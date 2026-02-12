from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import date
import databutton as db
import uuid
from app.auth import AuthorizedUser

# Role definitions
class BeneficiaryRole:
    BUB = "BUB"  # 0-1
    BRAT = "BRAT"  # 1-18
    BXX = "BXX"  # 18+
    TRUST_CONTRIBUTOR = "TRUST_CONTRIBUTOR"

class BeneficiaryProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date_of_birth: date
    # Add other beneficiary details here as needed

class CreateBeneficiaryRequest(BaseModel):
    date_of_birth: date

router = APIRouter() # No prefix, to match existing pattern if any

BENEFICIARY_STORAGE_KEY = "beneficiary_profiles"

def get_all_beneficiaries() -> list[BeneficiaryProfile]:
    """Retrieve all beneficiary profiles from storage."""
    return db.storage.json.get(BENEFICIARY_STORAGE_KEY, default=[])

def save_all_beneficiaries(profiles: list[BeneficiaryProfile]):
    """Save all beneficiary profiles to storage."""
    # Pydantic models need to be converted to dicts for JSON serialization
    profiles_dict = [p.dict() for p in profiles]
    db.storage.json.put(BENEFICIARY_STORAGE_KEY, profiles_dict)

@router.post("/beneficiaries", response_model=BeneficiaryProfile)
def register_beneficiary(request: CreateBeneficiaryRequest, user: AuthorizedUser) -> BeneficiaryProfile:
    """Registers a new beneficiary."""
    all_profiles = get_all_beneficiaries()
    new_profile = BeneficiaryProfile(date_of_birth=request.date_of_birth)
    all_profiles.append(new_profile)
    save_all_beneficiaries(all_profiles)
    return new_profile


@router.get("/beneficiaries/{beneficiary_id}/role")
def get_beneficiary_role(beneficiary_id: str, user: AuthorizedUser) -> dict:
    """Determines and returns the current role of a beneficiary based on their age."""
    all_profiles_raw = db.storage.json.get(BENEFICIARY_STORAGE_KEY, default=[])
    # The data is stored as dicts, so we parse it back into Pydantic models
    all_profiles = [BeneficiaryProfile(**p) for p in all_profiles_raw]

    profile = next((p for p in all_profiles if p.id == beneficiary_id), None)

    if not profile:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    today = date.today()
    age = today.year - profile.date_of_birth.year - ((today.month, today.day) < (profile.date_of_birth.month, profile.date_of_birth.day))

    role = ""
    if age < 1:
        role = BeneficiaryRole.BUB
    elif 1 <= age < 18:
        role = BeneficiaryRole.BRAT
    else: # 18+
        role = BeneficiaryRole.BXX

    return {"beneficiary_id": beneficiary_id, "role": role, "age": age}

print("Beneficiary roles API loaded with initial models and endpoints.")
