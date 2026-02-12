from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import databutton as db
import uuid
from typing import List

# Assuming the models are in a library file as per previous task
from app.libs.formal_trust_office_models import FormalTrustOffice

router = APIRouter()

TRUST_OFFICE_KEY_PREFIX = "formal_trust_office"


def get_trust_office_key(trust_office_id: str) -> str:
    """Generates a sanitized storage key for a trust office."""
    return f"{TRUST_OFFICE_KEY_PREFIX}_{trust_office_id}"


@router.post("/formal-trust-offices", response_model=FormalTrustOffice, tags=["Formal Trust Office"])
async def create_trust_office(trust_office_data: FormalTrustOffice) -> FormalTrustOffice:
    """
    Creates a new Formal Trust Office.
    A unique ID is generated for the office, and the data is stored.
    """
    if not trust_office_data.trustOfficeId:
        trust_office_data.trustOfficeId = str(uuid.uuid4())
    
    storage_key = get_trust_office_key(trust_office_data.trustOfficeId)
    
    try:
        db.storage.json.put(storage_key, trust_office_data.dict())
        return trust_office_data
    except Exception as e:
        print(f"Error creating trust office: {e}")
        raise HTTPException(status_code=500, detail="Failed to create trust office.")


@router.get("/formal-trust-offices/{trust_office_id}", response_model=FormalTrustOffice, tags=["Formal Trust Office"])
async def get_trust_office(trust_office_id: str) -> FormalTrustOffice:
    """
    Retrieves the details of a specific Formal Trust Office by its ID.
    """
    storage_key = get_trust_office_key(trust_office_id)
    
    try:
        trust_office_data = db.storage.json.get(storage_key)
        if trust_office_data is None:
            raise HTTPException(status_code=404, detail="Trust office not found.")
        return FormalTrustOffice(**trust_office_data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Trust office not found.")
    except Exception as e:
        print(f"Error retrieving trust office: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trust office.")
