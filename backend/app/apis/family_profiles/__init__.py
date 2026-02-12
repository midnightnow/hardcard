from fastapi import APIRouter, HTTPException, Depends
from app.auth import AuthorizedUser
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import databutton as db
import json
import re
import random # Added import

router = APIRouter(prefix="/family-profiles", tags=["Family Profiles"])

# Storage key for family profiles
PROFILES_STORAGE_KEY = "family_profiles_data_v1" # Defined constant

# Lists for generating memorable IDs (can be expanded)
ADJECTIVES = [ # Defined constant
    "golden", "crystal", "eternal", "sacred", "radiant",
    "sovereign", "noble", "valiant", "serene", "wise"
]
NOUNS = [ # Defined constant
    "leaf", "chalice", "star", "oak", "spring",
    "legacy", "scroll", "pillar", "haven", "cipher"
]

# Schema for family member profiles
class GuardianReference(BaseModel):
    id: str = Field(..., description="Guardian identifier (wallet address or reference)", example="wallet_0x123abc")
    name: str = Field(..., description="Name of the guardian", example="Alice Wonderland")
    relationship: str = Field(..., description="Relationship to the family member", example="Mother")

class FamilyMemberProfile(BaseModel):
    id: str = Field(..., description="Unique identifier for the family member", example="golden_leaf_007")
    user_id: Optional[str] = Field(None, description="Firebase UID of the user this profile belongs to.")
    vault_id: Optional[str] = Field(None, description="Reference to associated vault config", example="vault_stellar_nebula_42")
    alias: Optional[str] = Field(None, description="Friendly alias or nickname", example="Jamie")
    full_name: Optional[str] = Field(None, description="Full name of the family member", example="James Tiberius Kirk Jr.")
    birthdate: str = Field(..., description="Birthdate in YYYY-MM-DD format", example="2010-07-15")
    beneficiary_contact_email: Optional[str] = Field(None, description="Contact email for the beneficiary, used for handover notifications.", example="beneficiary@example.com")
    profile_image: Optional[str] = Field(None, description="Profile image URL or reference", example="https://static.databutton.com/public/example_project_id/example_profile.png")
    vault_start_date: Optional[str] = Field(None, description="Date when the vault was started in YYYY-MM-DD format", example="2010-07-16")
    guardians: List[GuardianReference] = Field(
        default_factory=list,
        description="List of guardians for this family member",
        example=[GuardianReference(id="wallet_0x123abc", name="Alice Wonderland", relationship="Mother")]
    )
    notes: Optional[str] = Field(None, description="Additional notes about this family member", example="Loves space exploration and has a knack for leadership.")
    beneficiary_email: Optional[str] = Field(None, description="Email address of the beneficiary, for handover notifications")

class GenerateProfileIdResponse(BaseModel):
    profile_id: str = Field(..., description="The uniquely generated profile identifier.", example="golden_leaf_123")

class DeleteProfileResponse(BaseModel):
    status: str = Field(..., description="The status of the deletion operation.", example="success")
    message: str = Field(..., description="A message confirming the deletion.", example="Profile with ID golden_leaf_007 deleted successfully")


def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_all_profiles(user_id: Optional[str] = None) -> List[FamilyMemberProfile]:
    """Get family member profiles from storage, optionally filtered by user_id."""
    try:
        profiles_data_dict = db.storage.json.get(PROFILES_STORAGE_KEY, default={})
        valid_profiles = []
        for profile_id, profile_data in profiles_data_dict.items():
            try:
                # Ensure profile_data is a dict, as it comes from JSON storage
                if not isinstance(profile_data, dict):
                    print(f"Skipping malformed profile entry (not a dict) with id {profile_id if profile_id else 'Unknown ID'}")
                    continue
                valid_profiles.append(FamilyMemberProfile(**profile_data))
            except Exception as e: # Catch Pydantic validation errors and other issues
                profile_identifier = profile_data.get('id', profile_id) # Try to get an id for logging
                print(f"Skipping profile due to validation error for id '{profile_identifier}': {e}")
        
        if user_id:
            # Filter the valid profiles by user_id
            # getattr is still good here in case a profile somehow got validated without user_id (should not happen with Pydantic model)
            filtered_profiles = [
                profile for profile in valid_profiles
                if getattr(profile, 'user_id', None) == user_id
            ]
            return filtered_profiles
        return valid_profiles # Return all valid profiles if no user_id is provided for filtering
    except Exception as e:
        # This outer exception would catch errors like issues with db.storage.json.get itself
        print(f"Critical error getting profiles: {e}")
        return []

def save_all_profiles(profiles: List[FamilyMemberProfile]):
    """Save all profiles to storage"""
    profiles_dict = {profile.id: profile.dict() for profile in profiles}
    db.storage.json.put(sanitize_storage_key("family_profiles"), profiles_dict)

@router.get("/", response_model=List[FamilyMemberProfile])
def list_family_profiles(current_user: AuthorizedUser) -> List[FamilyMemberProfile]:
    """Retrieve a list of family member profiles for the authenticated user.

    This endpoint provides family members managed by the authenticated user
    within the Hardcard system. Requires authentication.

    Returns:
        List[FamilyMemberProfile]: A list of family member profile objects for the user.
                                     Returns an empty list if no profiles exist for the user.
    """
    return get_all_profiles(user_id=current_user.sub)

@router.get("/{profile_id}", response_model=FamilyMemberProfile)
def get_family_profile(profile_id: str, current_user: AuthorizedUser) -> FamilyMemberProfile:
    """Retrieve a specific family member profile by its unique ID.

    Requires authentication.

    Args:
        profile_id (str): The unique identifier of the family member profile to retrieve.
                          Example: `golden_leaf_007`

    Returns:
        FamilyMemberProfile: The requested family member profile object.

    Raises:
        HTTPException: 404 Not Found if no profile with the given ID exists.
    """
    profiles_data = db.storage.json.get(PROFILES_STORAGE_KEY, default={})
    profile_data = profiles_data.get(profile_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail=f"Profile with ID {profile_id} not found.")
    return FamilyMemberProfile(**profile_data)

@router.post("", response_model=FamilyMemberProfile, status_code=201)
def create_family_profile(profile_create_data: FamilyMemberProfile, current_user: AuthorizedUser) -> FamilyMemberProfile:
    """Create a new family member profile in the Legacy Vault for the authenticated user.

    This endpoint allows for the addition of a new family member to the Hardcard system.
    The `user_id` field will be automatically populated with the authenticated user\'s ID.
    A unique profile ID should ideally be generated and assigned to the `id` field
    of the `profile` object before calling this endpoint, for instance, by using
    the `/generate-id` endpoint first. Requires authentication.

    If a profile with the same ID already exists, this endpoint will raise an HTTPException
    with a 409 Conflict status code.

    Args:
        profile_create_data (FamilyMemberProfile): The family member profile data to create. 
                                       The `user_id` field will be ignored if present and overwritten.

    Returns:
        FamilyMemberProfile: The created family member profile object.

    Raises:
        HTTPException: 409 Conflict if a profile with the same ID already exists.
    """
    profiles_data = db.storage.json.get(PROFILES_STORAGE_KEY, default={})
    if profile_create_data.id in profiles_data:
        raise HTTPException(status_code=409, detail=f"Profile with ID {profile_create_data.id} already exists.") 
    
    # Create a new profile object, ensuring user_id is set from the authenticated user
    # This also makes sure that all fields are present as per model, using defaults if not provided by client for optional ones
    # and raising validation error if required ones are missing.
    
    profile_dict_from_request = profile_create_data.dict(exclude_unset=True) # Get only fields set by client
    profile_dict_from_request['user_id'] = current_user.sub # Set/overwrite user_id

    # Re-validate with Pydantic to ensure all required fields are present after merging user_id
    # and to apply defaults for any other non-provided optional fields.
    try:
        # Note: Pydantic will use the values from profile_dict_from_request.
        # If profile_create_data was already a valid FamilyMemberProfile instance,
        # we can simply assign user_id and then .dict() it.
        # However, to be safe and handle if client omits some optional fields,
        # re-constructing like this (or a more careful merge + validation) is better.
        # For simplicity, assuming profile_create_data has required fields id, vault_id, alias, birthdate, vault_start_date.
        # The user_id is now guaranteed.
        
        # Safer way: Create an instance, then set user_id, then save.
        # The input 'profile_create_data' might not have user_id, or have a wrong one.
        # We want to ensure the stored one is the current_user.sub
        
        # Create a dictionary from the input, overriding user_id
        final_profile_data_dict = profile_create_data.dict()
        final_profile_data_dict['user_id'] = current_user.sub

        # Create the final model instance from this dict
        # This ensures validation with the correct user_id
        profile_to_save = FamilyMemberProfile(**final_profile_data_dict)

    except Exception as e: # Catch Pydantic validation errors if any required fields are missing
        raise HTTPException(status_code=422, detail=f"Invalid profile data: {e}")

    profiles_data[profile_to_save.id] = profile_to_save.dict()
    db.storage.json.put(PROFILES_STORAGE_KEY, profiles_data)
    return profile_to_save

@router.put("/{profile_id}", response_model=FamilyMemberProfile)
def update_family_profile(profile_id: str, updated_profile_data: FamilyMemberProfile, current_user: AuthorizedUser) -> FamilyMemberProfile:
    """Update an existing family member profile.

    This endpoint allows modification of an existing family member's details.
    The `profile_id` in the path must match the `id` field within the `updated_profile_data`.
    Requires authentication.

    Args:
        profile_id (str): The ID of the profile to update. Example: `golden_leaf_007`
        updated_profile_data (FamilyMemberProfile): The new data for the profile.

    Returns:
        FamilyMemberProfile: The updated family member profile object.

    Raises:
        HTTPException: 404 Not Found if the profile ID does not exist.
        HTTPException: 400 Bad Request if path `profile_id` and `updated_profile_data.id` mismatch.
    """
    if profile_id != updated_profile_data.id:
        raise HTTPException(
            status_code=400,
            detail=f"Profile ID in path ({profile_id}) does not match ID in body ({updated_profile_data.id})"
        )
    profiles_data = db.storage.json.get(PROFILES_STORAGE_KEY, default={})
    if profile_id not in profiles_data:
        raise HTTPException(status_code=404, detail=f"Profile with ID {profile_id} not found to update.")
    
    profiles_data[profile_id] = updated_profile_data.dict()
    db.storage.json.put(PROFILES_STORAGE_KEY, profiles_data)
    return updated_profile_data

@router.delete("/{profile_id}", response_model=DeleteProfileResponse)
def delete_family_profile(profile_id: str, current_user: AuthorizedUser) -> DeleteProfileResponse:
    """Delete a family member profile from the Legacy Vault system.

    This operation permanently removes the profile associated with the given ID.
    Requires authentication.

    Args:
        profile_id (str): The unique identifier of the profile to delete. Example: `golden_leaf_007`

    Returns:
        DeleteProfileResponse: An object confirming the status of the deletion.

    Raises:
        HTTPException: 404 Not Found if the profile ID does not exist.
    """
    profiles_data = db.storage.json.get(PROFILES_STORAGE_KEY, default={})
    if profile_id not in profiles_data:
        raise HTTPException(status_code=404, detail=f"Profile with ID {profile_id} not found to delete.")
    
    del profiles_data[profile_id]
    db.storage.json.put(PROFILES_STORAGE_KEY, profiles_data)
    
    return DeleteProfileResponse(status="success", message=f"Profile with ID {profile_id} deleted successfully")

@router.post("/generate-id", response_model=GenerateProfileIdResponse)
def generate_profile_id(current_user: AuthorizedUser) -> GenerateProfileIdResponse:
    """Generate a unique, human-readable profile ID for a new family member.

    This endpoint creates a memorable ID combining a positive adjective and a noun,
    followed by a short random number (e.g., "golden_leaf_123"). It ensures the generated
    ID does not already exist in the system. Requires authentication.

    Returns:
        GenerateProfileIdResponse: An object containing the new unique `profile_id`.
    """
    profiles_data = db.storage.json.get(PROFILES_STORAGE_KEY, default={})
    while True:
        adjective = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        number = random.randint(100, 999)
        new_id = f"{adjective}_{noun}_{number}"
        if new_id not in profiles_data:
            return GenerateProfileIdResponse(profile_id=new_id)