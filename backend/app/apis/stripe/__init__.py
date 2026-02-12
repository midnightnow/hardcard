from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
import databutton as db
# Make sure stripe is installed using pip install stripe
import stripe
from typing import Dict, Any, Optional, List, Union
import uuid
import json
from datetime import datetime

# Initialize Stripe with API key from secrets (requires stripe package)
# try:
#     stripe.api_key = db.secrets.get("STRIPE_SECRET_KEY")
# except Exception as e:
#     print(f"Warning: Could not load Stripe secret key: {e}")
#     # Use a placeholder key for development. Will be replaced in production.
stripe.api_key = "sk_test_placeholder"

# Create router
router = APIRouter(prefix="/stripe")

# Models for API
class CheckoutSessionRequest(BaseModel):
    priceId: str
    quantity: int = 1
    successUrl: str
    cancelUrl: str
    metadata: Dict[str, str] = {}
    customerId: Optional[str] = None

class CheckoutSessionResponse(BaseModel):
    sessionId: str
    url: str

class VerifySessionResponse(BaseModel):
    id: str
    payment_status: str
    payment_intent: Optional[str]
    customer: Optional[str]
    amount_total: int
    currency: str
    metadata: Dict[str, str]

# Models for Escrow Payment
class MilestonePaymentIntent(BaseModel):
    jobId: str
    milestoneId: str
    amount: float
    currency: str = "USD"
    providerId: str
    clientId: str
    description: str
    metadata: Dict[str, str] = {}

class PaymentIntentResponse(BaseModel):
    paymentIntentId: str
    clientSecret: str
    amount: float
    currency: str
    status: str
    transactionId: str

class CapturePaymentRequest(BaseModel):
    paymentIntentId: str
    amount: Optional[float] = None  # If not provided, capture the entire amount

class CapturePaymentResponse(BaseModel):
    paymentIntentId: str
    amount: float
    currency: str
    status: str
    transactionId: str

class EscrowTransaction(BaseModel):
    id: str = Field(default_factory=lambda: f"txn_{uuid.uuid4().hex}")
    jobId: str
    milestoneId: str
    amount: float
    fee: float
    providerId: str
    clientId: str
    type: str  # "deposit", "release", "refund"
    status: str  # "pending", "completed", "failed"
    paymentMethod: str  # "stripe", "bitcoin"
    paymentId: str  # External payment reference (Stripe payment intent ID)
    description: str
    metadata: Dict[str, Any] = {}
    createdAt: str = Field(default_factory=lambda: datetime.now().isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now().isoformat())

@router.post("/create-checkout-session")
def create_checkout_session(request: CheckoutSessionRequest) -> CheckoutSessionResponse:
    """Create a Stripe checkout session"""
    try:
        # Create the checkout session
        checkout_params = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price": request.priceId,
                    "quantity": request.quantity,
                },
            ],
            "mode": "payment",
            "success_url": request.successUrl,
            "cancel_url": request.cancelUrl,
            "metadata": request.metadata,
        }
        
        # Add customer if provided
        if request.customerId:
            checkout_params["customer"] = request.customerId
        
        # Create the session
        session = stripe.checkout.Session.create(**checkout_params)
        
        return CheckoutSessionResponse(
            sessionId=session.id,
            url=session.url,
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify-checkout-session")
def verify_checkout_session(sessionId: str) -> VerifySessionResponse:
    """Verify a Stripe checkout session"""
    try:
        # Retrieve the session
        session = stripe.checkout.Session.retrieve(sessionId)
        
        return VerifySessionResponse(
            id=session.id,
            payment_status=session.payment_status,
            payment_intent=session.payment_intent,
            customer=session.customer,
            amount_total=session.amount_total,
            currency=session.currency,
            metadata=session.metadata,
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Escrow payment endpoints
@router.post("/create-payment-intent")
def create_payment_intent(payment: MilestonePaymentIntent) -> PaymentIntentResponse:
    """Create a payment intent for funding a milestone"""
    try:
        # Calculate platform fee (10%)
        fee = calculate_platform_fee(payment.amount)
        total_amount = payment.amount + fee
        
        # Convert to cents for Stripe
        amount_cents = int(total_amount * 100)
        
        # Create a payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=payment.currency.lower(),
            payment_method_types=["card"],
            capture_method="manual",  # We'll capture the payment later when we know it's successful
            metadata={
                "jobId": payment.jobId,
                "milestoneId": payment.milestoneId,
                "providerId": payment.providerId,
                "clientId": payment.clientId,
                "fee": str(fee),
                "type": "escrow_deposit",
                **payment.metadata
            },
            description=f"Escrow deposit for job {payment.jobId}, milestone {payment.milestoneId}"
        )
        
        # Create and store transaction
        transaction = EscrowTransaction(
            jobId=payment.jobId,
            milestoneId=payment.milestoneId,
            amount=payment.amount,
            fee=fee,
            providerId=payment.providerId,
            clientId=payment.clientId,
            type="deposit",
            status="pending",
            paymentMethod="stripe",
            paymentId=intent.id,
            description=payment.description or f"Escrow deposit for milestone {payment.milestoneId}",
            metadata=payment.metadata
        )
        
        store_transaction(transaction)
        
        # Return response
        return PaymentIntentResponse(
            paymentIntentId=intent.id,
            clientSecret=intent.client_secret,
            amount=payment.amount,
            currency=payment.currency,
            status=intent.status,
            transactionId=transaction.id
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/capture-payment")
def capture_payment(request: CapturePaymentRequest) -> CapturePaymentResponse:
    """Capture a previously authorized payment intent"""
    try:
        # Retrieve the payment intent
        intent = stripe.PaymentIntent.retrieve(request.paymentIntentId)
        
        # Ensure it's in a state that can be captured
        if intent.status != "requires_capture":
            raise HTTPException(
                status_code=400, 
                detail=f"Payment cannot be captured. Current status: {intent.status}"
            )
        
        # Capture parameters
        capture_params = {}
        if request.amount is not None:
            # Convert to cents for Stripe
            capture_params["amount_to_capture"] = int(request.amount * 100)
        
        # Capture the payment
        intent = stripe.PaymentIntent.capture(request.paymentIntentId, **capture_params)
        
        # Update transaction status
        try:
            transactions_data = db.storage.json.get("escrow_transactions")
            
            # Find the transaction for this payment intent
            transaction_id = None
            for tid, txn in transactions_data.items():
                if txn["paymentId"] == request.paymentIntentId:
                    transaction_id = tid
                    break
            
            if transaction_id:
                transactions_data[transaction_id]["status"] = "completed"
                transactions_data[transaction_id]["updatedAt"] = datetime.now().isoformat()
                
                # Store updated transaction
                db.storage.json.put("escrow_transactions", transactions_data)
                
                # Also update in the job transactions
                job_id = transactions_data[transaction_id]["jobId"]
                job_key = f"job_{job_id}_transactions"
                job_transactions = db.storage.json.get(job_key)
                
                if transaction_id in job_transactions:
                    job_transactions[transaction_id]["status"] = "completed"
                    job_transactions[transaction_id]["updatedAt"] = datetime.now().isoformat()
                    db.storage.json.put(job_key, job_transactions)
        except Exception as e:
            print(f"Error updating transaction status: {str(e)}")
        
        # Return response
        return CapturePaymentResponse(
            paymentIntentId=intent.id,
            amount=intent.amount / 100,  # Convert back from cents
            currency=intent.currency,
            status=intent.status,
            transactionId=transaction_id or "unknown"
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Get the webhook signature
        signature = request.headers.get("stripe-signature")
        if not signature:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
            
        # Get the webhook secret from secrets
        webhook_secret = db.secrets.get("STRIPE_WEBHOOK_SECRET")
        
        # Get the raw body
        payload = await request.body()
        
        # Verify the event
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
            
        # Handle the event
        event_type = event["type"]
        event_data = event["data"]["object"]
        
        # Process different event types
        if event_type == "checkout.session.completed":
            handle_completed_checkout(event_data)
        elif event_type == "payment_intent.succeeded":
            handle_payment_intent_succeeded(event_data)
        elif event_type == "payment_intent.payment_failed":
            handle_payment_intent_failed(event_data)
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def handle_payment_intent_succeeded(payment_intent_data):
    """Handle payment intent succeeded event"""
    try:
        # Get payment intent data
        payment_intent_id = payment_intent_data["id"]
        metadata = payment_intent_data.get("metadata", {})
        job_id = metadata.get("jobId")
        milestone_id = metadata.get("milestoneId")
        
        if not job_id or not milestone_id:
            print(f"Warning: No job or milestone ID found for payment intent {payment_intent_id}")
            return
        
        print(f"Payment intent succeeded for job {job_id}, milestone {milestone_id}")
        print(f"Payment intent data: {payment_intent_data}")
        
        # Update transaction status if not already updated
        try:
            transactions_data = db.storage.json.get("escrow_transactions")
            
            # Find the transaction for this payment intent
            transaction_id = None
            for tid, txn in transactions_data.items():
                if txn["paymentId"] == payment_intent_id:
                    transaction_id = tid
                    break
            
            if transaction_id and transactions_data[transaction_id]["status"] != "completed":
                transactions_data[transaction_id]["status"] = "completed"
                transactions_data[transaction_id]["updatedAt"] = datetime.now().isoformat()
                
                # Store updated transaction
                db.storage.json.put("escrow_transactions", transactions_data)
                
                # Also update in the job transactions
                job_key = f"job_{job_id}_transactions"
                job_transactions = db.storage.json.get(job_key)
                
                if transaction_id in job_transactions:
                    job_transactions[transaction_id]["status"] = "completed"
                    job_transactions[transaction_id]["updatedAt"] = datetime.now().isoformat()
                    db.storage.json.put(job_key, job_transactions)
        except Exception as e:
            print(f"Error updating transaction status: {str(e)}")
    except Exception as e:
        print(f"Error handling payment intent succeeded: {str(e)}")

def handle_payment_intent_failed(payment_intent_data):
    """Handle payment intent failed event"""
    try:
        # Get payment intent data
        payment_intent_id = payment_intent_data["id"]
        metadata = payment_intent_data.get("metadata", {})
        job_id = metadata.get("jobId")
        milestone_id = metadata.get("milestoneId")
        
        if not job_id or not milestone_id:
            print(f"Warning: No job or milestone ID found for payment intent {payment_intent_id}")
            return
        
        print(f"Payment intent failed for job {job_id}, milestone {milestone_id}")
        print(f"Payment intent data: {payment_intent_data}")
        
        # Update transaction status
        try:
            transactions_data = db.storage.json.get("escrow_transactions")
            
            # Find the transaction for this payment intent
            transaction_id = None
            for tid, txn in transactions_data.items():
                if txn["paymentId"] == payment_intent_id:
                    transaction_id = tid
                    break
            
            if transaction_id:
                transactions_data[transaction_id]["status"] = "failed"
                transactions_data[transaction_id]["updatedAt"] = datetime.now().isoformat()
                
                # Store updated transaction
                db.storage.json.put("escrow_transactions", transactions_data)
                
                # Also update in the job transactions
                job_key = f"job_{job_id}_transactions"
                job_transactions = db.storage.json.get(job_key)
                
                if transaction_id in job_transactions:
                    job_transactions[transaction_id]["status"] = "failed"
                    job_transactions[transaction_id]["updatedAt"] = datetime.now().isoformat()
                    db.storage.json.put(job_key, job_transactions)
        except Exception as e:
            print(f"Error updating transaction status: {str(e)}")
    except Exception as e:
        print(f"Error handling payment intent failed: {str(e)}")

def handle_completed_checkout(session_data):
    """Handle completed checkout session"""
    try:
        # Get session data
        session_id = session_data["id"]
        metadata = session_data.get("metadata", {})
        user_id = metadata.get("userId")
        
        if not user_id:
            print(f"Warning: No user ID found for session {session_id}")
            return
            
        # Update order in Firestore (would be done via Cloud Function in production)
        # For now, we'll just log the data
        print(f"Checkout completed for session {session_id} by user {user_id}")
        print(f"Session data: {session_data}")
    except Exception as e:
        print(f"Error handling completed checkout: {str(e)}")

# Function to store transaction data
def store_transaction(transaction: EscrowTransaction):
    """Store transaction data in Databutton storage"""
    try:
        # Get existing transactions
        try:
            transactions_data = db.storage.json.get("escrow_transactions")
        except:
            transactions_data = {}
        
        # Add new transaction
        transactions_data[transaction.id] = transaction.dict()
        
        # Store updated transactions
        db.storage.json.put("escrow_transactions", transactions_data)
        
        # Also store in a separate key for the job for easier retrieval
        job_key = f"job_{transaction.jobId}_transactions"
        try:
            job_transactions = db.storage.json.get(job_key)
        except:
            job_transactions = {}
        
        job_transactions[transaction.id] = transaction.dict()
        db.storage.json.put(job_key, job_transactions)
        
        return transaction
    except Exception as e:
        print(f"Error storing transaction: {str(e)}")
        raise

# Calculate platform fee (10%)
def calculate_platform_fee(amount: float) -> float:
    return round(amount * 0.1, 2)  # 10% fee rounded to 2 decimal places
