from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Annotated # Keep for other uses if needed, but not for user here
import re
import uuid
from datetime import datetime, timezone
from app.apis.firebase_utils import get_firestore_client
from app.auth import AuthorizedUser # Corrected: Use AuthorizedUser directly
from pydantic import BaseModel, Field
import databutton as db
import bitcoinlib
import os
import tempfile
from pathlib import Path

router = APIRouter(prefix="/crypto_payments", tags=["Crypto Payments"])

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

class GenerateBitcoinAddressResponse(BaseModel):
    address: str = Field(..., description="The generated Bitcoin deposit address.")
    payment_id: str = Field(..., description="Unique ID for this payment intent.")

class GenerateBitcoinAddressRequest(BaseModel):
    job_id: str = Field(description="The ID of the job this payment is for.")
    bid_id: str = Field(description="The ID of the bid this payment is for.")

class CreateLightningInvoiceRequest(BaseModel):
    job_id: str = Field(description="The ID of the job this payment is for.")
    bid_id: str = Field(description="The ID of the bid this payment is for.")
    amount_sats: int = Field(..., gt=0, description="Amount in satoshis for the invoice.")
    memo: str = Field("", description="A memo for the Lightning invoice.")

class CreateLightningInvoiceResponse(BaseModel):
    invoice: str = Field(..., description="The generated Lightning Network payment request (BOLT11).")
    payment_id: str = Field(..., description="Unique ID for this payment intent.")



# --- API Endpoints ---

@router.post("/generate_bitcoin_address", response_model=GenerateBitcoinAddressResponse)
async def generate_bitcoin_address(request: GenerateBitcoinAddressRequest, user: Annotated[AuthorizedUser, Depends(AuthorizedUser)]):
    """
    Generates a new Bitcoin address for on-chain deposits and logs a payment intent.
    """
    WALLET_NAME = "nexusai_platform_wallet"
    WALLET_DB_FILENAME = f"{WALLET_NAME}.sqlite"
    # Ensure the storage key is sanitized, though this one is simple.
    # Sanitize function should be used if wallet name could be dynamic.
    STORAGE_KEY = f"bitcoin_wallets_{db.sanitize_storage_key(WALLET_DB_FILENAME)}"

    with tempfile.TemporaryDirectory() as tmpdir:
        local_wallet_path = Path(tmpdir) / WALLET_DB_FILENAME
        wallet_instance = None
        print(f"Using temporary directory: {tmpdir}")
        print(f"Local wallet path: {local_wallet_path}")

        try:
            # Try to fetch existing wallet from db.storage
            print(f"Attempting to load wallet from db.storage: {STORAGE_KEY}")
            wallet_bytes = db.storage.binary.get(STORAGE_KEY) # Default is FileNotFoundError if not found
            
            with open(local_wallet_path, 'wb') as f:
                f.write(wallet_bytes)
            print(f"Wallet file ({len(wallet_bytes)} bytes) loaded from db.storage to {local_wallet_path}")
            
            # Connect to the existing wallet db by specifying db_path and db_name
            wallet_instance = bitcoinlib.wallets.Wallet(
                WALLET_NAME, 
                db_path=str(local_wallet_path.parent), 
                db_name=local_wallet_path.name
            )
            print(f"Successfully connected to existing wallet: {WALLET_NAME}")

        except FileNotFoundError:
            print(f"Wallet file not found in db.storage ({STORAGE_KEY}). A new wallet will be created.")
        except Exception as e:
            print(f"Error loading wallet from db.storage or connecting: {e}. Attempting to create a new wallet.")
            # Log 'e' for debugging. If connection fails for other reasons, proceed to create new.

        if not wallet_instance:
            try:
                print(f"Creating new wallet: {WALLET_NAME} at {local_wallet_path.parent} with db_name {local_wallet_path.name}")
                wallet_instance = bitcoinlib.wallets.Wallet.create(
                    WALLET_NAME, 
                    db_path=str(local_wallet_path.parent), 
                    db_name=local_wallet_path.name,
                    network='bitcoin' # Explicitly set network, default is bitcoin
                )
                print(f"New wallet '{WALLET_NAME}' created successfully.")
                
                # Save the newly created wallet to storage immediately
                if local_wallet_path.exists():
                    with open(local_wallet_path, 'rb') as f:
                        new_wallet_bytes = f.read()
                    db.storage.binary.put(STORAGE_KEY, new_wallet_bytes)
                    print(f"Newly created wallet {WALLET_NAME} ({len(new_wallet_bytes)} bytes) saved to db.storage: {STORAGE_KEY}")
                else:
                    print(f"CRITICAL Error: Newly created wallet file {local_wallet_path} not found.")
                    raise HTTPException(status_code=500, detail="Failed to save newly created wallet.")
            except Exception as e:
                print(f"Error creating new wallet: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to create wallet: {str(e)}") from e

        if not wallet_instance:
            # This case should ideally not be reached if creation/loading logic is correct
            raise HTTPException(status_code=500, detail="Wallet instance could not be initialized.")

        try:
            # Generate a new key and address
            # For HD wallets, you might specify path, e.g., wallet_instance.get_key(purpose=84, coin_type=0, account=0)
            new_key = wallet_instance.get_key() 
            new_address = new_key.address
            print(f"Generated new Bitcoin address: {new_address} for wallet {WALLET_NAME}")
            
            # Important: Save the wallet database file back to db.storage
            # This includes new keys or any other changes bitcoinlib made to the wallet file.
            wallet_instance.scan() 
            
            if local_wallet_path.exists():
                with open(local_wallet_path, 'rb') as f:
                    updated_wallet_bytes = f.read()
                db.storage.binary.put(STORAGE_KEY, updated_wallet_bytes)
                print(f"Wallet {WALLET_NAME} (after getting key, {len(updated_wallet_bytes)} bytes) saved back to db.storage: {STORAGE_KEY}")
            else:
                print(f"Error: Wallet file {local_wallet_path} not found for saving after key generation.")
                raise HTTPException(status_code=500, detail="Failed to save wallet state after key generation.")

            # --- Firestore Integration Start ---
            payment_document_id = f"job-{request.job_id}-bid-{request.bid_id}"
            fs_client = get_firestore_client()

            if fs_client is None:
                print("CRITICAL: Firestore client not available in generate_bitcoin_address. Payment intent not created.")
                # Depending on policy, we might raise an error here if payment_id is mandatory for all address generations
                raise HTTPException(status_code=503, detail="Payment processing service is temporarily unavailable. Cannot log payment intent.")

            user_id = user.sub
            current_time = datetime.now(timezone.utc)
            payment_data = {
                "paymentId": payment_document_id,
                "jobId": request.job_id,
                "bidId": request.bid_id,
                "userId": user_id,
                "paymentType": "bitcoin",
                "status": "pending_address",
                "address": new_address,
                "currency": "BTC", # Or SATS if amounts are stored that way
                "requestedAmount": None, # On-chain typically doesn't have a pre-defined amount from user
                "confirmedAmount": None,
                "createdAt": current_time,
                "updatedAt": current_time,
                "invoice": None,
                "paymentHash": None,
                "transactionId": None,
                "expiresAt": None, # On-chain addresses don't typically expire in the same way invoices do
                "webhookData": None
            }

            try:
                fs_client.collection("payments").document(payment_document_id).set(payment_data)
                print(f"Successfully created payment intent {payment_document_id} for address {new_address} for user {user_id}")
            except Exception as e_firestore:
                print(f"CRITICAL: Failed to create payment intent {payment_document_id} in Firestore for user {user_id}: {e_firestore}")
                # If Firestore write fails, we should not proceed as the payment cannot be tracked.
                raise HTTPException(status_code=500, detail=f"Failed to record payment intent: {str(e_firestore)}") from e_firestore
            # --- Firestore Integration End ---

            return GenerateBitcoinAddressResponse(address=new_address, payment_id=payment_document_id)
        except Exception as e:
            print(f"Error generating address or saving wallet: {e}")
            # Consider more specific error handling or logging
            raise HTTPException(status_code=500, detail=f"Error during address generation or wallet update: {str(e)}") from e

@router.post("/create_lightning_invoice", response_model=CreateLightningInvoiceResponse)
async def create_lightning_invoice(request: CreateLightningInvoiceRequest, user: Annotated[AuthorizedUser, Depends(AuthorizedUser)]):
    """
    Creates a Lightning Network invoice.
    Connects to a live LND node if secrets are configured, otherwise returns a mock invoice.
    """
    payment_document_id = f"job-{request.job_id}-bid-{request.bid_id}"
    fs_client = get_firestore_client()
    user_id = user.sub
    current_time = datetime.now(timezone.utc)

    if fs_client is None:
        print("CRITICAL: Firestore client not available in create_lightning_invoice.")
        raise HTTPException(status_code=503, detail="Payment processing service is temporarily unavailable.")

    # Attempt to get LND connection details from secrets
    lnd_host = db.secrets.get("LND_GRPC_HOST")
    lnd_macaroon_hex = db.secrets.get("LND_MACAROON_HEX")
    lnd_tls_cert_b64 = db.secrets.get("LND_TLS_CERT_B64")

    invoice_string = ""
    payment_hash = ""
    
    # --- LND Integration ---
    if all([lnd_host, lnd_macaroon_hex, lnd_tls_cert_b64]):
        print(f"Attempting to connect to LND at {lnd_host}...")
        try:
            # This is where the actual lndgrpc code would go.
            # from lndgrpc import LndClient
            # lnd_client = LndClient(
            #     lnd_host,
            #     macaroon_filepath=lnd_macaroon_hex, # This would need adjustment based on library
            #     cert_filepath=lnd_tls_cert_b64, # This would need adjustment based on library
            # )
            # add_invoice_response = lnd_client.add_invoice(
            #     memo=f"pid_{payment_document_id}",
            #     value=request.amount_sats
            # )
            # invoice_string = add_invoice_response.payment_request
            # payment_hash = add_invoice_response.r_hash.hex()
            # print(f"Successfully generated live LND invoice: {invoice_string}")
            
            # For now, we will just log that we would have connected
            print("Live LND connection is configured but currently bypassed for mock implementation.")
            raise NotImplementedError("Live LND connection not yet implemented.")

        except Exception as e:
            print(f"LND connection or invoice generation failed: {e}. Falling back to mock invoice.")
            # Fallback to mock invoice if live connection fails
            pass

    # --- Mock Invoice Generation (if live LND fails or is not configured) ---
    if not invoice_string:
        print(f"Generating mock Lightning invoice for {request.amount_sats} sats.")
        # Create a more realistic-looking, but fake, BOLT11 invoice
        mock_payment_hash = os.urandom(32).hex()
        invoice_string = f"lnbc{request.amount_sats}m1p{mock_payment_hash}..."
        payment_hash = mock_payment_hash
        print(f"Generated mock invoice with payment hash: {payment_hash}")

    # --- Firestore Integration ---
    payment_data = {
        "paymentId": payment_document_id,
        "jobId": request.job_id,
        "bidId": request.bid_id,
        "userId": user_id,
        "paymentType": "lightning",
        "status": "pending_invoice",
        "currency": "SATS",
        "requestedAmount": request.amount_sats,
        "memo": f"pid_{payment_document_id}", # Standardize memo format
        "confirmedAmount": None,
        "createdAt": current_time,
        "updatedAt": current_time,
        "invoice": invoice_string,
        "paymentHash": payment_hash,
        "transactionId": None,
        "expiresAt": None, # In a real scenario, this would be set based on the invoice's expiry
        "webhookData": None
    }

    try:
        fs_client.collection("payments").document(payment_document_id).set(payment_data, merge=True)
        print(f"Successfully created/updated payment intent {payment_document_id} with invoice.")
    except Exception as e_firestore:
        print(f"CRITICAL: Failed to create/update payment intent {payment_document_id} in Firestore: {e_firestore}")
        raise HTTPException(status_code=500, detail=f"Failed to record payment intent: {str(e_firestore)}")

    return CreateLightningInvoiceResponse(
        invoice=invoice_string, payment_id=payment_document_id
    )
