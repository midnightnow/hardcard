from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from typing import Optional
import re
from datetime import datetime, timezone
from app.apis.firebase_utils import get_firestore_client
from pydantic import BaseModel, Field
import databutton as db

# This router is NOT automatically included in the app.
# It is intended to be included manually in src/main.py WITHOUT an auth dependency,
# allowing it to be a public-facing but secret-protected webhook.
#
# To enable this webhook:
# 1. Add this import to src/main.py:
#    from app.apis.payment_webhooks import router as payment_webhooks_router
# 2. Add this line in the create_app function in src/main.py:
#    app.include_router(payment_webhooks_router)

router = APIRouter(prefix="/payment_webhooks", tags=["Payment Webhooks"])

# --- SECURITY ---
API_KEY_NAME = "X-Webhook-Secret"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key():
    """
    Retrieves the webhook secret from Databutton secrets.
    A secret named PAYMENT_WEBHOOK_SECRET must be set.
    """
    webhook_secret = db.secrets.get("PAYMENT_WEBHOOK_SECRET")
    if not webhook_secret:
        print("CRITICAL: PAYMENT_WEBHOOK_SECRET is not set in Databutton secrets.")
        raise HTTPException(status_code=500, detail="Webhook secret is not configured on the server.")
    return webhook_secret

async def verify_api_key(api_key: str = Security(api_key_header), expected_key: str = Depends(get_api_key)):
    """
    Verifies that the provided API key matches the one stored in secrets.
    """
    if api_key != expected_key:
        print("Webhook authentication failed: Invalid webhook secret provided.")
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# --- Helper Functions ---
def _get_job_and_update_status(fs_client, job_id: str, new_status: str):
    """
    Fetches a job from Firestore and updates its status.
    """
    if not job_id:
        print("No job_id provided to _get_job_and_update_status.")
        return None
    
    job_ref = fs_client.collection("jobs").document(job_id)
    try:
        job_doc = job_ref.get()
        if not job_doc.exists:
            print(f"Job with ID {job_id} not found in Firestore.")
            return None
        
        job_ref.update({"status": new_status})
        print(f"Successfully updated job {job_id} to status {new_status}.")
        return job_doc.to_dict()
    except Exception as e:
        print(f"Error accessing or updating job {job_id}: {e}")
        return None

def _parse_payment_id_from_memo(memo: str) -> Optional[str]:
    """
    Parses a payment ID from a Lightning invoice memo string.
    Expected format in memo: 'pid_job-...'
    """
    if not memo:
        return None
    
    match = re.search(r'pid_(job-[a-zA-Z0-9\-]+)', memo)
    if match:
        payment_id = match.group(1)
        print(f"Extracted payment_id '{payment_id}' from memo: '{memo}'")
        return payment_id
    
    return None

# --- Pydantic Models ---
class PaymentWebhookRequest(BaseModel):
    type: str = Field(..., description="Type of payment notification (e.g., 'onchain_btc', 'lightning').")
    data: dict = Field(..., description="Payload of the payment notification.")

class PaymentWebhookResponse(BaseModel):
    status: str = Field(default="received", description="Status of webhook processing.")

@router.post("/btc_ln_webhook", response_model=PaymentWebhookResponse, dependencies=[Depends(verify_api_key)])
async def payment_webhook(request: PaymentWebhookRequest):
    """
    Receives payment notifications (e.g., from a Bitcoin node watcher or Lightning node).
    This endpoint will process incoming payment data and update relevant records.
    """
    
    
    try:
        fs_client = get_firestore_client()
        if fs_client is None:
            print("CRITICAL: Firestore client not available in payment_webhook.")
            raise HTTPException(status_code=503, detail="Payment processing service is temporarily unavailable.")

        if request.type == "onchain_btc":
            print(f"Processing on-chain Bitcoin payment: {request.data}")
            tx_id = request.data.get("transaction_id")
            address = request.data.get("address")
            amount_satoshi = request.data.get("value_satoshi")
            confirmations = int(request.data.get("confirmations", 0))

            if not all([tx_id, address, amount_satoshi is not None]):
                raise HTTPException(status_code=400, detail="Missing data for on-chain BTC notification.")

            payments_ref = fs_client.collection("payments").where("address", "==", address).limit(1)
            payment_docs = list(payments_ref.stream())

            if not payment_docs:
                print(f"No active payment intent found for address {address}. Ignoring.")
                return PaymentWebhookResponse(status="received_ignored_unknown_address")
            
            payment_doc = payment_docs[0]
            payment_data = payment_doc.to_dict()
            job_id = payment_data.get("jobId")
            
            if not job_id:
                print(f"CRITICAL: Job ID missing in payment record {payment_doc.id}.")
                raise HTTPException(status_code=500, detail="Job ID missing in payment record.")

            new_status = payment_data.get('status')
            MIN_CONFIRMATIONS_FOR_COMPLETION = 1 

            if confirmations >= MIN_CONFIRMATIONS_FOR_COMPLETION and new_status != "confirmed":
                new_status = "confirmed"
                _get_job_and_update_status(fs_client, job_id, "FUNDED")
            elif 0 < confirmations < MIN_CONFIRMATIONS_FOR_COMPLETION and new_status not in ["confirmed", "confirming"]:
                new_status = "confirming"

            update_data = {
                "status": new_status,
                "transactionId": tx_id,
                "confirmedAmount": amount_satoshi,
                "confirmations": confirmations,
                "webhookData": request.data,
                "updatedAt": datetime.now(timezone.utc)
            }
            payment_doc.reference.update(update_data)
            print(f"Payment intent {payment_doc.id} updated to status '{new_status}'.")

        elif request.type == "lightning":
            print(f"Processing Lightning Network payment: {request.data}")
            settled = request.data.get("settled", False)
            memo = request.data.get("memo", "")
            
            if not settled:
                print("Lightning payment notification received but not settled. Ignoring.")
                return PaymentWebhookResponse(status="received_unsettled")

            payment_id = _parse_payment_id_from_memo(memo)
            if not payment_id:
                print(f"Could not parse a valid payment_id from memo: '{memo}'. Ignoring.")
                return PaymentWebhookResponse(status="received_ignored_no_payment_id")

            payment_ref = fs_client.collection("payments").document(payment_id)
            payment_doc = payment_ref.get()

            if not payment_doc.exists:
                print(f"No payment record found for payment_id '{payment_id}'. Ignoring.")
                return PaymentWebhookResponse(status="received_ignored_unknown_payment_id")

            payment_data = payment_doc.to_dict()
            job_id = payment_data.get("jobId")

            if not job_id:
                print(f"CRITICAL: Job ID missing in payment record {payment_id}.")
                raise HTTPException(status_code=500, detail="Job ID missing in payment record.")
            
            if payment_data.get("status") == "confirmed":
                print(f"Payment {payment_id} has already been confirmed. Ignoring webhook.")
                return PaymentWebhookResponse(status="received_already_confirmed")

            update_data = {
                "status": "confirmed",
                "paymentHash": request.data.get("payment_hash"),
                "confirmedAmount": request.data.get("amt_paid_sat"),
                "webhookData": request.data,
                "updatedAt": datetime.now(timezone.utc)
            }
            payment_ref.update(update_data)
            print(f"Payment {payment_id} updated to confirmed status.")
            _get_job_and_update_status(fs_client, job_id, "FUNDED")
            
        else:
            print(f"Received webhook for unknown payment type: {request.type}")
            return PaymentWebhookResponse(status="received_unknown_type")

        return PaymentWebhookResponse(status=f"received_and_processed_type_{request.type}")

    except Exception as e:
        print(f"An unexpected error occurred in payment_webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the webhook.",
        ) from e
    finally:
        print("Webhook processing finished.")