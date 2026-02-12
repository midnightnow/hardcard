from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import databutton as db
import re # For sanitizing keys
from datetime import datetime # For timestamp in keys

router = APIRouter(
    prefix="/investors",
    tags=["Investor Relations"],
)

class InterestFormPayload(BaseModel):
    interest_type: Optional[str] = None  # Added for Collector's Edition, etc.
    name: str
    email: EmailStr
    organization: str | None = None
    role: str | None = None # e.g., VC, Angel, Partner, Developer
    persona_interest: str | None = None # e.g., VC, Crypto, Gov, Default
    message: str | None = None

class InterestFormResponse(BaseModel):
    message: str
    # No longer returning data_received in the response for brevity and security
    submission_id: str | None = None 

def sanitize_storage_key_component(component: str) -> str:
    """Sanitize component of a storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', component)

@router.post("/interest", response_model=InterestFormResponse)
async def register_interest(payload: InterestFormPayload):
    """
    Receives an investor interest form submission.
    Logs the received data and stores it in db.storage.json.
    Returns a success message.
    """
    print(f"Received investor interest submission: {payload.json(indent=2)}")
    
    timestamp_str = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    sanitized_email = sanitize_storage_key_component(payload.email)
    sanitized_name = sanitize_storage_key_component(payload.name)
    
    sanitized_interest_type = sanitize_storage_key_component(payload.interest_type if payload.interest_type else "unknown")
    storage_key = f"investor_interest_{sanitized_email}_{sanitized_name}_{timestamp_str}_{sanitized_interest_type}.json"
    
    try:
        db.storage.json.put(storage_key, payload.dict(
        persona_interest=payload.persona_interest if payload.persona_interest else "general",
        interest_type=payload.interest_type if payload.interest_type else "unknown"
    ))
        print(f"Investor interest submission saved to: {storage_key}")
        submission_id = storage_key # Or a more abstract ID if needed later
    except Exception as e:
        print(f"ERROR: Failed to save investor interest to db.storage: {e}")
        # Optionally, re-raise or return a more specific error to the client
        # For now, we'll still return a generic success to the user not to expose backend issues,
        # but the error is logged.
        # Consider a separate notification mechanism for critical storage failures.
        # raise HTTPException(status_code=500, detail="Failed to store submission due to a server error.")
        # For now, we proceed to return a success message as per original design, but log the failure.
        submission_id = None # Indicate storage failure if we need to track it

    return InterestFormResponse(
        message="Thank you for your interest! We have received your submission.",
        submission_id=submission_id
    )

@router.get("/status")
async def get_investor_relations_status():
    return {"status": "Investor Relations API is active"}
