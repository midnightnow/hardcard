from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.responses import StreamingResponse
from app.auth import AuthorizedUser
from app.libs.auth_utils import require_admin_user
from typing import Annotated
from enum import Enum
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict
from datetime import datetime, date
import uuid
import re # For sanitizing filenames

# Constants for DB storage keys
FAMILY_TRUSTS_DB_KEY = "family_trusts_data"
FAMILY_TRUST_DEPOSITS_DB_KEY = "family_trust_deposits_data"

# Initialize FastAPI router

# Main router - will be public-facing or mixed
router = APIRouter(prefix="/family-trusts", tags=["Family Trusts"])

# Admin router - will be prefixed and protected
admin_router = APIRouter(
    prefix="/admin", # This prefix will be added to the main router's prefix
    tags=["Family Trusts Admin"],
    dependencies=[Depends(require_admin_user)]
)


# --- Utility function to sanitize storage keys ---
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- characters."""
    # Remove potentially harmful characters, keep it simple for filenames
    key = re.sub(r'[^a-zA-Z0-9._-]', '_', key)
    # Prevent excessively long keys (optional, adjust as needed)
    return key[:255] 

from app.libs.family_trust_models import (
    TrustHandoverStatus,
    InitiateHandoverResponse,
    ClaimTrustRequest,
    ClaimTrustResponse,
    FamilyTrustCreateRequest,
    FamilyTrustData,
    FamilyTrustUpdateRequest,
    FamilyTrustResponse,
    DepositCreateRequest,
    DepositData,
    DepositResponse,
    TrustPolicy, # Added TrustPolicy as it's used in FamilyTrustData
    WithdrawalApprovalRequirement # Added WithdrawalApprovalRequirement as it's used in TrustPolicy
)


# --- Mock Database (using db.storage.json for simplicity in this step) ---
# In a real scenario, this would interact with Firestore or another DB.
# For now, we will use Databutton's db.storage.json to simulate persistence.
import databutton as db
import json


TRUST_ACCOUNTS_KEY = "family_trust_accounts.json"
DEPOSITS_KEY_PREFIX = "family_trust_deposits_" # deposits_TRUSTID.json

# Helper to ensure Pydantic models are fully JSON serializable with dates/datetimes as ISO strings
def _pydantic_to_json_serializable_dict(model_instance: BaseModel) -> dict:
    # Pydantic's .json() method correctly serializes datetime/date to ISO strings.
    # Then, json.loads() converts this JSON string back into a Python dict.
    return json.loads(model_instance.json())

def get_trust_accounts_store() -> Dict[str, Dict]:
    try:
        return db.storage.json.get(TRUST_ACCOUNTS_KEY)
    except FileNotFoundError:
        return {}

def save_trust_accounts_store(store: Dict[str, Dict]):
    # Ensure all FamilyTrustData instances within the store are JSON serializable dicts
    serializable_store = { 
        k: (_pydantic_to_json_serializable_dict(v) if isinstance(v, FamilyTrustData) else v) 
        for k, v in store.items() 
    }
    db.storage.json.put(TRUST_ACCOUNTS_KEY, serializable_store)

def get_deposits_store(trust_id: str) -> Dict[str, Dict]:
    try:
        return db.storage.json.get(f"{DEPOSITS_KEY_PREFIX}{trust_id}.json")
    except FileNotFoundError:
        return {}

def save_deposits_store(trust_id: str, store: Dict[str, Dict]):
    serializable_store = { 
        k: (_pydantic_to_json_serializable_dict(v) if isinstance(v, DepositData) else v) 
        for k, v in store.items() 
    }
    db.storage.json.put(f"{DEPOSITS_KEY_PREFIX}{trust_id}.json", serializable_store)


# --- API Endpoints ---


# --- Initiate Handover Process Endpoint (Parent/Guardian Authorized) ---
@router.post("/{trust_id}/initiate-handover", response_model=InitiateHandoverResponse, summary="Parent Initiates Handover for a Trust")
async def initiate_handover_process(
    trust_id: str, 
    current_user: AuthorizedUser 
):
    """
    Allows an authorized parent/guardian to initiate the handover process 
    for their child's trust once it's eligible.

    - Validates the trust belongs to the requesting parent/guardian.
    - Validates that the trust is in 'ELIGIBLE_FOR_HANDOVER' status.
    - Generates a secure handover token and sets an expiry.
    - Updates the trust status to 'HANDOVER_PENDING_BENEFICIARY_VERIFICATION'.
    - Sends an email notification to the beneficiary with the handover token and instructions.
    """
    trust_accounts = get_trust_accounts_store()
    trust_data_dict = trust_accounts.get(trust_id)

    if not trust_data_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family trust account not found")

    try:
        trust = FamilyTrustData(**trust_data_dict)
    except ValidationError as e:
        print(f"Validation error loading trust {trust_id} for handover: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error loading trust data.")

    # Authorization: Check if the current user is one of the parent/guardians for this trust
    if current_user.sub not in trust.parent_guardian_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to initiate handover for this trust."
        )

    if trust.status == TrustHandoverStatus.HANDOVER_COMPLETED_BENEFICIARY_CONTROL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Handover already completed and trust is under beneficiary control.")

    if trust.status != TrustHandoverStatus.ELIGIBLE_FOR_HANDOVER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Trust is not eligible for handover. Current status: {trust.status}")

    import secrets
    from datetime import timedelta
    trust.handover_token = secrets.token_urlsafe(32)
    trust.handover_token_expiry = datetime.utcnow() + timedelta(days=7) # Token valid for 7 days
    trust.status = TrustHandoverStatus.HANDOVER_PENDING_BENEFICIARY_VERIFICATION
    trust.last_updated = datetime.utcnow() # Record update time
    
    trust_accounts[trust_id] = _pydantic_to_json_serializable_dict(trust) # Ensure dict for JSON store
    save_trust_accounts_store(trust_accounts)

    print(f"Handover initiated for trust {trust_id} by parent {current_user.sub}. Token expires at {trust.handover_token_expiry}")
    
    # Attempt to send notification email
    try:
        PROFILES_STORAGE_KEY_FOR_NOTIFICATION = "family_profiles_data_v1" # Matches family_profiles API
        
        all_profiles_dict: Dict[str, Dict] = db.storage.json.get(PROFILES_STORAGE_KEY_FOR_NOTIFICATION, default={})
        beneficiary_profile_dict = all_profiles_dict.get(trust.child_id) # child_id from trust is the profile_id
        
        if beneficiary_profile_dict:
            # Directly access keys, assuming structure from FamilyMemberProfile (already added beneficiary_contact_email)
            beneficiary_email = beneficiary_profile_dict.get("beneficiary_contact_email")
            beneficiary_alias = beneficiary_profile_dict.get("alias", "Beneficiary") 

            if beneficiary_email and trust.handover_token:
                # Construct claim_trust_url - this should point to the frontend page
                # The frontend page will then call the /api/family-trusts/claim-trust endpoint
                # For now, this assumes a path on the deployed app.
                # Ensure APP_BASE_PATH is handled correctly if testing in dev workspace UI.
                # The host here is the *API* host. The UI might be different.
                # This URL construction might need refinement based on where the UI is hosted
                # and how APP_BASE_PATH is configured for deployed apps.
                
                # For deployed app:
                # claim_trust_ui_url = f"https://hardcard.ai/claim-trust?token={trust.handover_token}"
                # For development, it's more complex due to workspace UI paths.
                # A common pattern is to have a config for base UI URL.
                # Let's use a placeholder for now that's more generic.
                # This ideally comes from a config or env var accessible by the API.
                # For now, assuming the app is deployed at its custom domain or db.env.host.
                
                base_ui_url = f"https://{db.env.host}" # This gets the API host, UI could be elsewhere
                # If app is deployed, db.env.host might be hardcard.ai. If in workspace, it's the databutton internal host.
                # The client-side routing will handle /claim-trust path.
                claim_trust_url_for_email = f"{base_ui_url}/ClaimTrustPage?token={trust.handover_token}"


                email_subject = "Your Hardcard Legacy Trust is Ready for Handover"
                email_content_text = f"""Dear {beneficiary_alias},

Your Hardcard Legacy Trust, {trust.account_name}, is now eligible for you to take control.

To claim your trust, please use the following secure token: {trust.handover_token}

You can start the claim process by visiting: {claim_trust_url_for_email}

This token will expire on {trust.handover_token_expiry.strftime("%Y-%m-%d %H:%M UTC") if trust.handover_token_expiry else 'N/A'}.

If you have any questions, please contact your parent/guardian or Hardcard support.

Sincerely,
The Hardcard Team
"""
                email_content_html = f"""<p>Dear {beneficiary_alias},</p>
<p>Your Hardcard Legacy Trust, <strong>{trust.account_name}</strong>, is now eligible for you to take control.</p>
<p>To claim your trust, please use the following secure token: <strong>{trust.handover_token}</strong></p>
<p>You can start the claim process by visiting: <a href=\"{claim_trust_url_for_email}\">{claim_trust_url_for_email}</a></p>
<p>This token will expire on {trust.handover_token_expiry.strftime("%Y-%m-%d %H:%M UTC") if trust.handover_token_expiry else 'N/A'}.</p>
<p>If you have any questions, please contact your parent/guardian or Hardcard support.</p>
<p>Sincerely,<br>The Hardcard Team</p>
"""
                db.notify.email(
                    to=beneficiary_email,
                    subject=email_subject,
                    content_text=email_content_text,
                    content_html=email_content_html
                )
                print(f"Handover notification email sent to {beneficiary_email} for trust {trust_id}.")
            elif not beneficiary_email:
                print(f"Beneficiary contact email not found for child ID {trust.child_id} (Trust {trust_id}). Cannot send notification.")
        else:
            print(f"Beneficiary profile not found for child ID {trust.child_id} (Trust {trust_id}). Cannot send notification.")
    except Exception as e:
        print(f"Error sending handover notification email for trust {trust_id}: {e}")
        # Do not let email failure block the handover initiation process itself

    return InitiateHandoverResponse(
        trust_id=trust.trust_id,
        status=trust.status,
        handover_token_expiry=trust.handover_token_expiry,
        message="Handover process initiated. A token has been generated and sent to the beneficiary (if email available)."
    )

# --- Beneficiary Claim Trust Endpoint (on main public router) ---

@router.post("/claim-trust", response_model=ClaimTrustResponse, summary="Beneficiary Claims Control of a Trust")
async def beneficiary_claim_trust(request: ClaimTrustRequest, current_user: AuthorizedUser):
    """
    Allows a beneficiary to claim control of their trust using a handover token.

    - Validates the handover token, its expiry, and current trust status.
    - Verifies Date of Birth against the beneficiary's profile.
    - Verifies that the claiming user matches the intended beneficiary (if specified during initiation) or assigns the claiming user as beneficiary.
    - Updates trust status to HANDOVER_COMPLETED_BENEFICIARY_CONTROL.
    - Assigns beneficiary_user_id to the trust.
    """
    trust_accounts = get_trust_accounts_store()
    target_trust_id: Optional[str] = None
    trust_to_update_data: Optional[dict] = None

    for trust_id_iter, trust_data_dict in trust_accounts.items():
        if trust_data_dict.get("handover_token") == request.handover_token:
            target_trust_id = trust_id_iter
            trust_to_update_data = trust_data_dict
            break
    
    if not target_trust_id or not trust_to_update_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or expired handover token.")

    trust = FamilyTrustData(**trust_to_update_data)

    if trust.status != TrustHandoverStatus.HANDOVER_PENDING_BENEFICIARY_VERIFICATION:
        # Potentially allow claim if ELIGIBLE_FOR_HANDOVER and token matches (e.g. if notification failed but user got token)
        # For now, strictly require PENDING_BENEFICIARY_VERIFICATION
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Trust is not pending beneficiary verification. Current status: {trust.status}")

    if trust.handover_token_expiry and trust.handover_token_expiry < datetime.utcnow():
        trust.status = TrustHandoverStatus.HANDOVER_EXPIRED
        trust_accounts[target_trust_id] = trust.dict()
        save_trust_accounts_store(trust_accounts)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Handover token has expired.")

    # Verify the provided beneficiary_user_id against the authenticated user if it was set during initiation
    # If trust.beneficiary_user_id was pre-filled (e.g. parent knew future UID), it must match current_user.sub
    if trust.beneficiary_user_id and trust.beneficiary_user_id != current_user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated user does not match the pre-assigned beneficiary for this handover."
        )
    
    # If request.beneficiary_user_id is provided, it must match the authenticated user.
    if request.beneficiary_user_id and request.beneficiary_user_id != current_user.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provided beneficiary_user_id in request does not match authenticated user."
        )
    
    # Assign the current authenticated user as the beneficiary
    claimed_by_beneficiary_id = current_user.sub

    # Date of Birth Verification (if DOB provided in request)
    if request.date_of_birth_verification:
        if not trust.child_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Trust record is missing child_id for DOB verification.")

        PROFILES_STORAGE_KEY_FOR_VERIFICATION = "family_profiles_data_v1" # Consistent with initiation
        all_profiles_dict: Dict[str, Dict] = db.storage.json.get(PROFILES_STORAGE_KEY_FOR_VERIFICATION, default={})
        beneficiary_profile_dict = all_profiles_dict.get(trust.child_id)
        
        if not beneficiary_profile_dict:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary profile not found for DOB verification.")
        
        birthdate_str = beneficiary_profile_dict.get("birthdate") # Matches FamilyMemberProfile model
        if not birthdate_str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Beneficiary birthdate not found in profile.")
        
        try:
            beneficiary_dob = date.fromisoformat(birthdate_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid birthdate format in profile (expected YYYY-MM-DD).")

        if beneficiary_dob != request.date_of_birth_verification:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Date of birth verification failed.")
            
    # All checks passed, update the trust
    trust.status = TrustHandoverStatus.HANDOVER_COMPLETED_BENEFICIARY_CONTROL
    trust.beneficiary_user_id = claimed_by_beneficiary_id # Assign the UID of the user who successfully claimed
    trust.handover_token = None 
    trust.handover_token_expiry = None
    trust.last_updated = datetime.utcnow()

    # At this point, the beneficiary has gained sole control.
    # Future API operations to manage this trust should authorize based on trust.beneficiary_user_id.

    trust_accounts[target_trust_id] = trust.dict()
    save_trust_accounts_store(trust_accounts)

    print(f"Trust {target_trust_id} claimed by beneficiary. User ID: {claimed_by_beneficiary_id}")

    return ClaimTrustResponse(
        trust_id=target_trust_id,
        status=trust.status,
        beneficiary_user_id=trust.beneficiary_user_id,
        message="Trust successfully claimed by beneficiary."
    )


# --- API Endpoints Implementation (to be moved to admin_router) ---

# For simplicity, admin protection will be added in a later step.
# from app.auth import AuthorizedUser # Will be used later

@admin_router.post("/", response_model=FamilyTrustResponse, status_code=status.HTTP_201_CREATED)
def create_family_trust_account(
    payload: FamilyTrustCreateRequest,
    # current_user: AuthorizedUser # Add for admin protection
):
    # Basic admin check placeholder - replace with proper RBAC
    # if not current_user.is_admin: # Pseudocode for admin check
    #     raise HTTPException( # Applied to the one around line 200, the other one is fine as it's a direct validation failurestatus_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    trust_data = FamilyTrustData(
        child_id=payload.child_id,
        child_date_of_birth=payload.child_date_of_birth,
        parent_guardian_ids=payload.parent_guardian_ids,
        wallet_identifier=payload.wallet_identifier,
        account_name=payload.account_name,
        status=payload.initial_status,
        currency=payload.currency,
        metadata=payload.metadata,
    )
    
    store = get_trust_accounts_store()
    if trust_data.trust_id in store:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Trust ID already exists")
    
    store[trust_data.trust_id] = trust_data # Store the model instance directly
    save_trust_accounts_store(store)
    
    return FamilyTrustResponse(**_pydantic_to_json_serializable_dict(trust_data))

@admin_router.get("/{trust_id}", response_model=FamilyTrustResponse)
def get_family_trust_account(
    trust_id: str,
    # current_user: AuthorizedUser # Add for admin/user protection
):
    store = get_trust_accounts_store()
    # The get_trust_accounts_store already returns dicts, Pydantic will parse them.
    account_dict = store.get(trust_id)
    if not account_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family trust account not found") from None
    
    # Potentially check if current_user is parent/guardian or admin
    return FamilyTrustResponse(**account_dict)

@router.get("/sessions", response_model=List[FamilyTrustResponse], summary="List Trust Sessions for Current User")
def list_trust_sessions(
    current_user: AuthorizedUser,
    skip: int = 0,
    limit: int = 100
):
    """
    Lists all family trust accounts where the current authenticated user is either
    a parent/guardian or the assigned beneficiary. This provides a user-centric
    view of their associated trust sessions.
    """
    store = get_trust_accounts_store()
    user_id = current_user.sub
    
    user_trusts = []
    for account_id, account_dict in store.items():
        try:
            # Parse into the Pydantic model for safe attribute access
            trust = FamilyTrustData(**account_dict)
            # Check if user is a parent/guardian OR the beneficiary
            if user_id in trust.parent_guardian_ids or user_id == trust.beneficiary_user_id:
                user_trusts.append(FamilyTrustResponse(**account_dict))
        except ValidationError as e:
            # Log if a specific trust account in storage is malformed
            print(f"Skipping malformed trust account {account_id} during list_trust_sessions: {e}")
            continue
            
    return user_trusts[skip : skip + limit]

@admin_router.put("/{trust_id}", response_model=FamilyTrustResponse)
async def update_family_trust_account(
    trust_id: str,
    update_req: FamilyTrustUpdateRequest,
    # current_user: AuthorizedUser = Depends(require_admin)
):
    store = get_trust_accounts_store()
    if trust_id not in store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trust account not found")

    # Parse existing data into model
    try:
        existing = FamilyTrustData(**store[trust_id])
    except ValidationError as e:
        # This might happen if stored data is somehow corrupted or incomplete
        print(f"Validation error loading existing account {trust_id} from store: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error loading existing trust account data.") from e

    # Deep-copy and apply only the fields set in the request
    account_to_update = existing.copy(deep=True)
    update_values = update_req.dict(exclude_unset=True)
    
    for key, value in update_values.items():
        if hasattr(account_to_update, key):
            setattr(account_to_update, key, value)
        else:
            # This case should ideally not happen if FamilyTrustUpdateRequest only contains valid fields
            print(f"Warning: Attempted to update non-existent field '{key}' on FamilyTrustData")

    # Ensure creation_date is not altered by an update operation
    account_to_update.creation_date = existing.creation_date

    store[trust_id] = account_to_update # Store the updated Pydantic model instance
    save_trust_accounts_store(store) # This will handle serialization

    return FamilyTrustResponse(**_pydantic_to_json_serializable_dict(account_to_update))

@admin_router.post("/{trust_id}/deposits", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
def record_deposit_for_trust(
    trust_id: str,
    payload: DepositCreateRequest,
    # current_user: AuthorizedUser # Add for admin/system protection
):
    trust_store = get_trust_accounts_store()
    if trust_id not in trust_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family trust account not found")

    # Basic admin/system check placeholder
    # if not current_user.is_admin_or_system:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    deposit_data = DepositData(
        trust_id=trust_id,
        **payload.dict()
    )
    
    deposits_store = get_deposits_store(trust_id)
    if deposit_data.deposit_id in deposits_store:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Deposit ID already exists for this trust")
        
    deposits_store[deposit_data.deposit_id] = deposit_data # Store model instance
    save_deposits_store(trust_id, deposits_store)
    
    return DepositResponse(**_pydantic_to_json_serializable_dict(deposit_data))

@admin_router.get("/{trust_id}/deposits", response_model=List[DepositResponse])
def list_deposits_for_trust(
    trust_id: str,
    skip: int = 0,
    limit: int = 100,
    # current_user: AuthorizedUser # Add for admin/user protection
):
    trust_store = get_trust_accounts_store()
    if trust_id not in trust_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family trust account not found")

    # Potentially check if current_user is parent/guardian of this trust_id or admin

    deposits_store = get_deposits_store(trust_id)
    deposits_list = [DepositResponse(**data) for data in deposits_store.values()]
    return deposits_list[skip : skip + limit]

@router.post(
    "/{trust_id}/deposits/{deposit_id}/proof",
    response_model=DepositData,
    summary="Upload Proof of Deposit",
    tags=["stream"], # Added for StreamingResponse
    # dependencies=[Depends(require_admin_user)],
)
async def upload_proof_of_deposit(
    trust_id: str,
    deposit_id: str,
    proof_file: UploadFile = File(...),
    # current_user: AuthorizedUser # Placeholder for future auth
) -> DepositData:
    """
    Uploads a proof of deposit file (e.g., transaction screenshot) for a specific deposit
    associated with a family trust. The file is stored in db.storage.binary, and the
    deposit record is updated with the storage key using the per-trust deposit storage.
    """
    # Check if trust exists
    trust_store = get_trust_accounts_store()
    if trust_id not in trust_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family trust not found")

    # Get the specific trust's deposits
    deposits_store = get_deposits_store(trust_id)
    deposit_dict = deposits_store.get(deposit_id)

    if not deposit_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found for this trust")

    try:
        # Parse into DepositData model to ensure consistency and for easier manipulation
        deposit_to_update = DepositData(**deposit_dict)
    except ValidationError as e:
        print(f"Validation error loading deposit {deposit_id} for trust {trust_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error loading deposit data.")

    try:
        file_content = await proof_file.read()
        if not file_content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

        sanitized_filename = sanitize_storage_key(proof_file.filename if proof_file.filename else "unknown_proof_file")
        storage_key = f"trust_proofs/{trust_id}_{deposit_id}_{sanitized_filename}"
        
        db.storage.binary.put(storage_key, file_content)
        
        # Update the Pydantic model instance
        deposit_to_update.proof_storage_key = storage_key
        # If you have a URL field to be constructed, do it here:
        # deposit_to_update.proof_of_deposit_url = f"/api/family-trusts/{trust_id}/deposits/{deposit_id}/proof" # Example

        # Update the deposit record in the store by replacing the old dict with the new serialized model
        deposits_store[deposit_id] = _pydantic_to_json_serializable_dict(deposit_to_update)
        save_deposits_store(trust_id, deposits_store)
        
        return deposit_to_update # Return the Pydantic model instance directly

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        print(f"Error uploading proof of deposit for trust {trust_id}, deposit {deposit_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not upload proof of deposit: {str(e)}") from e

# Note: Proper error handling for db.storage.json operations (e.g., size limits, write failures)
# would be needed for a production system using this storage method.
# Firestore or a relational DB would offer more robust transactionality and querying.

@admin_router.delete("/{trust_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_family_trust_account(
    trust_id: str,
    admin_user: Annotated[AuthorizedUser, Depends(require_admin_user)]
):
    store = get_trust_accounts_store()
    if trust_id not in store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trust account not found")

    del store[trust_id]
    save_trust_accounts_store(store)
    return # For 204 No Content, FastAPI expects no return value or None

@router.get( # Moved from admin_router to main router
    "/{trust_id}/deposits/{deposit_id}/proof",
    summary="Get Proof of Deposit",
    tags=["stream"] # Important for Databutton to correctly handle streaming
    # dependencies will be handled by new auth logic
)
async def get_proof_of_deposit(
    trust_id: str,
    deposit_id: str,
    # current_user: AuthorizedUser, # Placeholder for future auth
    # admin_user: Annotated[AuthorizedUser, Depends(require_admin_user)] # Remove if moving to main router
):
    """
    Retrieves the proof of deposit file for a specific deposit using per-trust storage.
    """
    # Check if trust exists (optional, as deposit check implies trust)
    trust_store = get_trust_accounts_store()
    if trust_id not in trust_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family trust not found")

    # Get the specific trust's deposits
    deposits_store = get_deposits_store(trust_id)
    deposit_dict = deposits_store.get(deposit_id)

    if not deposit_dict:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deposit not found for this trust")
    
    try:
        # Parse to ensure it's valid, though we only need proof_storage_key
        deposit_data = DepositData(**deposit_dict)
    except ValidationError as e:
        print(f"Validation error loading deposit {deposit_id} for trust {trust_id} before proof retrieval: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error loading deposit data.")

    proof_storage_key = deposit_data.proof_storage_key # Access from Pydantic model
    if not proof_storage_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No proof of deposit found for this deposit")

    try:
        file_bytes = db.storage.binary.get(proof_storage_key)
        
        media_type = "application/octet-stream" # Generic, consider storing MIME type at upload
        filename = proof_storage_key.split('/')[-1] if '/' in proof_storage_key else "proof_of_deposit"

        return StreamingResponse(
            iter([file_bytes]), 
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
        )
    except FileNotFoundError:
        print(f"File not found in db.storage.binary for key: {proof_storage_key} (Trust {trust_id}, Deposit {deposit_id})")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proof of deposit file not found in storage")
    except Exception as e:
        print(f"Error retrieving proof of deposit file for trust {trust_id}, deposit {deposit_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve proof of deposit file")

# Include the admin_router into the main router
router.include_router(admin_router)

