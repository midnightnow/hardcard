from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime, timedelta
import uuid
from firebase_admin import firestore
from firebase_admin.firestore import client as FirestoreClient # For type hinting
from app.auth import AuthorizedUser
from app.apis.firebase_init import initialize_firebase

# Initialize Firebase
initialize_firebase()

def get_db() -> FirestoreClient:
    """Dependency to get a Firestore client."""
    return firestore.client()

router = APIRouter(prefix="/waitlist", tags=["Waitlist & Invites"])

# --- Data Models ---
class WaitlistEntryBase(BaseModel):
    email: EmailStr
    notes: Optional[str] = None

class WaitlistEntryCreate(WaitlistEntryBase):
    # invited_by_user_id is determined by the server based on invite_code_used
    invite_code_used: Optional[str] = None

class WaitlistEntry(WaitlistEntryBase):
    granted_access_level: Optional[Literal["minipreview", "full_vault"]] = None
    admin_grant_notes: Optional[str] = None
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None # Firebase UID, if user signs up later
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by_user_id: Optional[str] = None
    invite_code_used: Optional[str] = None
    friends_invited_count: int = 0
    status: Literal["pending", "invited", "accepted_invite", "access_granted", "user_registered"] = "pending"
    queue_position: Optional[int] = None # For future use
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class InviteBase(BaseModel):
    invite_type: Literal["admin_direct", "waitlist_referral"]
    created_by_user_id: str # Firebase UID of the creator (admin or waitlist user)
    target_email: Optional[EmailStr] = None # For admin direct invites

class InviteCreate(InviteBase):
    pass

class Invite(InviteBase):
    invite_code: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None # e.g., datetime.utcnow() + timedelta(days=7)
    status: Literal["pending", "accepted", "expired", "revoked"] = "pending"
    accepted_by_user_id: Optional[str] = None # Firebase UID of the acceptor
    accepted_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class UserProfileData(BaseModel):
    user_id: str # Firebase UID, primary key
    email: EmailStr
    display_name: Optional[str] = None
    access_level: Literal["none", "minipreview", "full_vault"] = "none"
    waitlist_entry_id: Optional[str] = None
    joined_via_invite_code: Optional[str] = None
    personal_referral_code: str = Field(default_factory=lambda: str(uuid.uuid4().hex[:10])) # Shorter, hex
    last_login_at: Optional[datetime] = None
    roles: list[str] = [] # e.g., ['admin', 'waitlist_user', 'vault_member']
    referred_users_count: int = 0

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# --- Firestore Collection Names (constants) ---
WAITLIST_COLLECTION = "waitlist_entries"
INVITES_COLLECTION = "invites"
USERS_COLLECTION = "user_profiles"

\
class AdminGrantAccessRequest(BaseModel):
    target_user_email: EmailStr # To verify against the waitlist entry
    access_level_to_grant: Literal["minipreview", "full_vault"]
    admin_notes: Optional[str] = None




# --- Helper Functions ---
async def get_admin_user(user: AuthorizedUser, db_client: FirestoreClient = Depends(get_db)) -> UserProfileData:  # noqa: B008
    """Dependency to check if the user is an admin."""
    user_profile_doc = db_client.collection(USERS_COLLECTION).document(user.sub).get()
    if not user_profile_doc.exists:
        # If profile doesn't exist, they can't be an admin. Create a basic one for consistency?
        # For now, strict: no profile, no admin rights.
        print(f"Admin check failed: User profile not found for user_id {user.sub}.")
        raise HTTPException(status_code=403, detail="User profile not found. Cannot verify admin privileges.")
    profile_data = UserProfileData(**user_profile_doc.to_dict())
    if "admin" not in profile_data.roles:
        print(f"Admin check failed: User {user.sub} does not have 'admin' role. Roles: {profile_data.roles}")
        raise HTTPException(status_code=403, detail="User does not have admin privileges.")
    return profile_data

class AdminCreateInviteRequest(BaseModel):
    target_email: EmailStr
    expires_in_days: Optional[int] = 7 # Default 7 days

# --- API Endpoints ---

@router.post("/admin/invites/create", response_model=Invite, status_code=201)
async def create_admin_invite(invite_data: AdminCreateInviteRequest, admin_user: UserProfileData = Depends(get_admin_user), db_client: FirestoreClient = Depends(get_db)):  # noqa: B008 (admin_user) # noqa: B008 (db_client)
    """
    Allows an admin to create a direct invite for a specific email.
    This invite grants 'full_vault' access upon acceptance.
    """
    new_invite_code = str(uuid.uuid4())
    expires_at = None
    if invite_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=invite_data.expires_in_days)

    invite = Invite(
        invite_code=new_invite_code,
        invite_type="admin_direct",
        created_by_user_id=admin_user.user_id,
        target_email=invite_data.target_email,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        status="pending"
    )

    try:
        db_client.collection(INVITES_COLLECTION).document(invite.invite_code).set(invite.dict())
    except Exception as e:
        print(f"Error creating admin invite in Firestore: {e}")
        raise HTTPException(status_code=500, detail="Could not create admin invite.") from e
        
    return invite

@router.post("/join", response_model=WaitlistEntry, status_code=201)
async def join_waitlist(entry_data: WaitlistEntryCreate, db_client: FirestoreClient = Depends(get_db)):  # noqa: B008
    """
    Allows a new user to join the waitlist.
    If an invite_code_used is provided, it attempts to link to an inviter.
    This can be a standard Invite object or a user's personal_referral_code.
    """
    existing_entries_query = db_client.collection(WAITLIST_COLLECTION).where(filter=firestore.FieldFilter("email", "==", entry_data.email)).limit(1).stream()
    if any(doc.exists for doc in existing_entries_query):
        raise HTTPException(status_code=409, detail=f"Email {entry_data.email} is already on the waitlist.")

    new_entry_id = str(uuid.uuid4())
    new_entry_dict = entry_data.dict()
    new_entry_dict["id"] = new_entry_id
    new_entry_dict["joined_at"] = datetime.utcnow()
    new_entry_dict["status"] = "pending"
    new_entry_dict["friends_invited_count"] = 0
    new_entry_dict["invited_by_user_id"] = None # Initialize

    if entry_data.invite_code_used:
        code_is_standard_invite = False
        # 1. Check if it's a standard Invite (from INVITES_COLLECTION)
        invite_docs = list(db_client.collection(INVITES_COLLECTION).where(filter=firestore.FieldFilter("invite_code", "==", entry_data.invite_code_used)).where(filter=firestore.FieldFilter("status", "==", "pending")).limit(1).stream())
        
        if invite_docs and invite_docs[0].exists:
            valid_invite_doc = invite_docs[0]
            invite_obj = Invite(**valid_invite_doc.to_dict())
            new_entry_dict["invited_by_user_id"] = invite_obj.created_by_user_id
            code_is_standard_invite = True
            print(f"Standard invite code {entry_data.invite_code_used} used by {entry_data.email}, inviter: {invite_obj.created_by_user_id}")

        # 2. If not a standard invite, check if it's a personal_referral_code (from USERS_COLLECTION)
        if not code_is_standard_invite:
            referring_user_docs = list(db_client.collection(USERS_COLLECTION).where(filter=firestore.FieldFilter("personal_referral_code", "==", entry_data.invite_code_used)).limit(1).stream())
            
            if referring_user_docs and referring_user_docs[0].exists:
                referring_user_profile_doc = referring_user_docs[0]
                referring_user_profile = UserProfileData(**referring_user_profile_doc.to_dict())
                referring_user_id = referring_user_profile.user_id
                new_entry_dict["invited_by_user_id"] = referring_user_id
                
                try:
                    referring_user_profile_doc.reference.update({"referred_users_count": firestore.Increment(1)})
                    print(f"Personal referral code {entry_data.invite_code_used} used by {entry_data.email}, referrer: {referring_user_id}. Incremented their referred_users_count.")

                    if referring_user_profile.waitlist_entry_id:
                        waitlist_entry_ref = db_client.collection(WAITLIST_COLLECTION).document(referring_user_profile.waitlist_entry_id)
                        waitlist_entry_doc = waitlist_entry_ref.get()
                        if waitlist_entry_doc.exists:
                            waitlist_entry_ref.update({"friends_invited_count": firestore.Increment(1)})
                            print(f"Incremented friends_invited_count for waitlist entry {referring_user_profile.waitlist_entry_id} of user {referring_user_id}")
                        else:
                            print(f"Warning: Waitlist entry ID {referring_user_profile.waitlist_entry_id} for user {referring_user_id} not found, cannot increment friends_invited_count.")
                except Exception as e:
                    print(f"Error updating referrer counts for {referring_user_id} due to code {entry_data.invite_code_used}: {e}") # Log error but proceed
            else:
                print(f"Warning: Invite code {entry_data.invite_code_used} provided by {entry_data.email} is not a valid standard invite or personal referral code.")
                new_entry_dict["invite_code_used"] = None # Clear invalid code
    
    waitlist_entry = WaitlistEntry(**new_entry_dict)

    try:
        db_client.collection(WAITLIST_COLLECTION).document(waitlist_entry.id).set(waitlist_entry.dict())
    except Exception as e:
        print(f"Error saving to Firestore: {e}")
        raise HTTPException(status_code=500, detail="Could not add entry to waitlist.") from e
        
    return waitlist_entry

@router.post("/invite/accept/{invite_code}", response_model=UserProfileData)
async def accept_invite(invite_code: str, user: AuthorizedUser, db_client: FirestoreClient = Depends(get_db)):  # noqa: B008
    """
    Allows an authenticated user to accept an invite using an invite code.
    This will update their access level and mark the invite as used.
    It also attempts to link the user's profile with any existing waitlist entry.
    """
    user_uid = user.sub
    user_email = user.email # Assuming email is available in AuthorizedUser
    if not user_email:
        # This case should ideally not happen if Firebase Auth provides email.
        # If it can, we need a way to fetch it or handle it.
        print(f"Warning: User {user_uid} accepting invite {invite_code} has no email in token.")
        raise HTTPException(status_code=400, detail="User email not available, cannot process invite acceptance fully.")

    invite_doc_ref = None
    invite_data_dict = None
    invites_query = db_client.collection(INVITES_COLLECTION).where(filter=firestore.FieldFilter("invite_code", "==", invite_code)).limit(1).stream()
    for doc in invites_query:
        if doc.exists:
            invite_doc_ref = doc.reference
            invite_data_dict = doc.to_dict()
            break

    if not invite_doc_ref or not invite_data_dict:
        raise HTTPException(status_code=404, detail="Invite code not found.")

    invite = Invite(**invite_data_dict)

    if invite.status != "pending":
        raise HTTPException(status_code=400, detail=f"Invite code has already been {invite.status}.")

    if invite.expires_at and invite.expires_at < datetime.utcnow():
        try:
            invite_doc_ref.update({"status": "expired"})
        except Exception as e_update:
            print(f"Error updating expired invite {invite_code} status: {e_update}")
        raise HTTPException(status_code=410, detail="Invite code has expired.")

    # Update invite
    try:
        invite_doc_ref.update({
            "status": "accepted",
            "accepted_by_user_id": user_uid,
            "accepted_at": datetime.utcnow()
        })
    except Exception as e:
        print(f"Error updating invite {invite_code} to accepted: {e}")
        raise HTTPException(status_code=500, detail="Could not update invite status.") from e

    # Determine access level based on invite type
    access_level_granted = "minipreview" # Default for waitlist referrals (though they don't use this endpoint typically)
    if invite.invite_type == "admin_direct":
        access_level_granted = "full_vault"

    # Update or create user profile
    user_profile_ref = db_client.collection(USERS_COLLECTION).document(user_uid)
    user_profile_doc = user_profile_ref.get()
    profile_data_dict = {}

    if user_profile_doc.exists:
        profile_data_dict = user_profile_doc.to_dict()
        profile_data_dict["access_level"] = access_level_granted
        profile_data_dict["joined_via_invite_code"] = invite_code
        profile_data_dict["last_login_at"] = datetime.utcnow()
        if 'vault_member' not in profile_data_dict.get("roles", []):
             profile_data_dict.setdefault("roles", []).append('vault_member')
    else:
        profile_data_dict = {
            "user_id": user_uid,
            "email": user_email,
            "access_level": access_level_granted,
            "joined_via_invite_code": invite_code,
            "last_login_at": datetime.utcnow(),
            "roles": ['vault_member'],
            "personal_referral_code": str(uuid.uuid4().hex[:10]), # Ensure new profiles get one
            "referred_users_count": 0
        }
    
    # Link with Waitlist Entry if applicable
    if not profile_data_dict.get("waitlist_entry_id") and user_email:
        wl_query = db_client.collection(WAITLIST_COLLECTION).where(filter=firestore.FieldFilter("email", "==", user_email)).where(filter=firestore.FieldFilter("user_id", "==", None)).limit(1).stream()
        for wl_doc in wl_query:
            if wl_doc.exists:
                profile_data_dict["waitlist_entry_id"] = wl_doc.id
                try:
                    wl_doc.reference.update({"user_id": user_uid, "status": "accepted_invite"})
                    print(f"Linked user {user_uid} with waitlist entry {wl_doc.id}")
                except Exception as e_wl_update:
                    print(f"Error updating waitlist entry {wl_doc.id} for user {user_uid}: {e_wl_update}")
                break
    
    final_profile_data = UserProfileData(**profile_data_dict)
    try:
        user_profile_ref.set(final_profile_data.dict(exclude_none=True), merge=True) # Use merge=True for safety
    except Exception as e:
        print(f"Error updating/creating user profile for {user_uid}: {e}")
        raise HTTPException(status_code=500, detail="Could not update user profile.") from e
    
    # If waitlist referral invite was accepted (though this flow is more for admin_direct)
    # and inviter needs their counts updated (this is mostly handled by join_waitlist for personal codes)
    if invite.invite_type == "waitlist_referral" and invite.created_by_user_id:
        inviter_profile_ref = db_client.collection(USERS_COLLECTION).document(invite.created_by_user_id)
        inviter_profile_doc = inviter_profile_ref.get()
        if inviter_profile_doc.exists:
            try:
                inviter_profile_ref.update({"referred_users_count": firestore.Increment(1)})
                # Also update the original waitlist entry for the inviter if they are still on it
                inviter_profile = UserProfileData(**inviter_profile_doc.to_dict())
                if inviter_profile.waitlist_entry_id:
                    wl_entry_ref = db_client.collection(WAITLIST_COLLECTION).document(inviter_profile.waitlist_entry_id)
                    wl_entry_ref.update({"friends_invited_count": firestore.Increment(1)})
            except Exception as e_inviter:
                print(f"Error incrementing referral count for inviter {invite.created_by_user_id} during accept_invite: {e_inviter}")

    return final_profile_data

\
@router.post("/admin/waitlist/{waitlist_entry_id}/grant_access", response_model=WaitlistEntry, tags=["Admin"])
async def admin_grant_access_to_waitlist_entry(
    waitlist_entry_id: str,
    request_data: AdminGrantAccessRequest,
    admin_user: UserProfileData = Depends(get_admin_user),  # noqa: B008
    db_client: FirestoreClient = Depends(get_db)  # noqa: B008
):
    """
    Allows an admin to grant a specific access level to a user on the waitlist.
    This updates the waitlist entry and potentially the user's profile if they exist.
    """
    waitlist_entry_ref = db_client.collection(WAITLIST_COLLECTION).document(waitlist_entry_id)
    waitlist_entry_doc = waitlist_entry_ref.get()

    if not waitlist_entry_doc.exists:
        raise HTTPException(status_code=404, detail="Waitlist entry not found.")

    waitlist_entry_data = waitlist_entry_doc.to_dict()
    
    if waitlist_entry_data.get("email") != request_data.target_user_email:
        raise HTTPException(status_code=400, detail="Target email does not match waitlist entry email.")

    updated_fields = {
        "status": "access_granted",
        "granted_access_level": request_data.access_level_to_grant
    }
    if request_data.admin_notes:
        updated_fields["admin_grant_notes"] = request_data.admin_notes
    
    try:
        waitlist_entry_ref.update(updated_fields)
        print(f"Admin {admin_user.user_id} granted {request_data.access_level_to_grant} access to waitlist entry {waitlist_entry_id} for {request_data.target_user_email}.")
    except Exception as e:
        print(f"Error updating waitlist entry {waitlist_entry_id} for admin grant: {e}")
        raise HTTPException(status_code=500, detail="Could not update waitlist entry for access grant.") from e

    # If the user already has a profile (i.e., waitlist_entry_data['user_id'] is populated),
    # update their UserProfileData directly.
    user_id_on_waitlist = waitlist_entry_data.get("user_id")
    if user_id_on_waitlist:
        user_profile_ref = db_client.collection(USERS_COLLECTION).document(user_id_on_waitlist)
        user_profile_doc = user_profile_ref.get()
        if user_profile_doc.exists:
            try:
                user_profile_ref.update({
                    "access_level": request_data.access_level_to_grant,
                    "roles": firestore.ArrayUnion(['vault_member']) # Ensure vault_member role
                })
                print(f"Updated UserProfileData for user {user_id_on_waitlist} with granted access level {request_data.access_level_to_grant}.")
            except Exception as e_profile:
                print(f"Error updating UserProfileData for {user_id_on_waitlist} during admin grant: {e_profile}")
                # Continue, as waitlist entry was updated. Log this for monitoring.
        else:
            print(f"Warning: User ID {user_id_on_waitlist} on waitlist entry {waitlist_entry_id} but no matching UserProfileData found to update access level directly.")


    # Fetch the updated waitlist entry to return
    updated_waitlist_entry_doc = waitlist_entry_ref.get()
    return WaitlistEntry(**updated_waitlist_entry_doc.to_dict())




@router.get("/user/access_status", response_model=UserProfileData)
async def get_user_access_status(user: AuthorizedUser, db_client: FirestoreClient = Depends(get_db)):  # noqa: B008
    """
    Retrieves the access status and profile data for the currently authenticated user.
    Creates a basic profile if one doesn't exist and links to waitlist if applicable.
    """
    user_uid = user.sub
    user_email = user.email # Assuming email is available in AuthorizedUser
    if not user_email:
        print(f"Warning: User {user_uid} in get_user_access_status has no email in token.")
        # Depending on strictness, could raise error or proceed with limited functionality
        # For now, let's assume email is usually present for profile creation.
        raise HTTPException(status_code=400, detail="User email not available, cannot ensure profile integrity.")

    user_profile_ref = db_client.collection(USERS_COLLECTION).document(user_uid)
    user_profile_doc = user_profile_ref.get()

    if user_profile_doc.exists:
        profile_data = UserProfileData(**user_profile_doc.to_dict())
        # Ensure last_login_at is updated
        if profile_data.last_login_at is None or (datetime.utcnow() - profile_data.last_login_at > timedelta(minutes=5)):
            try:
                user_profile_ref.update({"last_login_at": datetime.utcnow()})
                profile_data.last_login_at = datetime.utcnow()
            except Exception as e_login_update:
                print(f"Error updating last_login_at for user {user_uid}: {e_login_update}")
        return profile_data
    else:
        print(f"No profile found for user {user_uid} ({user_email}). Creating default profile.")
        default_profile_dict = {
            "user_id": user_uid,
            "email": user_email,
            "access_level": "none",
            "last_login_at": datetime.utcnow(),
            "personal_referral_code": str(uuid.uuid4().hex[:10]),
            "roles": [],
            "referred_users_count": 0
        }

        # Attempt to link with an existing waitlist entry
        wl_entries_query = db_client.collection(WAITLIST_COLLECTION).where(filter=firestore.FieldFilter("email", "==", user_email)).limit(1).stream()
        waitlist_doc_snapshot = next(wl_entries_query, None)

        if waitlist_doc_snapshot and waitlist_doc_snapshot.exists:
            wl_doc_id = waitlist_doc_snapshot.id
            wl_data = waitlist_doc_snapshot.to_dict()
            default_profile_dict["waitlist_entry_id"] = wl_doc_id
            
            updated_wl_fields = {}
            if not wl_data.get("user_id"):
                updated_wl_fields["user_id"] = user_uid
            
            # Check if access was granted via admin action on waitlist
            if wl_data.get("status") == "access_granted" and wl_data.get("granted_access_level"):
                default_profile_dict["access_level"] = wl_data["granted_access_level"]
                if 'vault_member' not in default_profile_dict.get("roles", []):
                    default_profile_dict.setdefault("roles", []).append('vault_member')
                print(f"User {user_uid} ({user_email}) granted access level '{wl_data['granted_access_level']}' from waitlist entry {wl_doc_id}.")
                if wl_data.get("status") != "user_registered": # Avoid overwriting if already registered from accept_invite
                    updated_wl_fields["status"] = "user_registered" # Or "accepted_invite" if more appropriate
            elif wl_data.get("status") == "pending": # Or any other status that implies they haven't fully onboarded yet
                 updated_wl_fields["status"] = "user_registered"

            if updated_wl_fields:
                try:
                    waitlist_doc_snapshot.reference.update(updated_wl_fields)
                    print(f"Updated waitlist entry {wl_doc_id} for user {user_uid}: {updated_wl_fields}")
                except Exception as e_wl_link:
                    print(f"Error updating waitlist entry {wl_doc_id} during profile creation for {user_uid}: {e_wl_link}")
            
            # If they joined via a referral code on the waitlist entry, consider copying it
            if wl_data.get("invite_code_used") and not default_profile_dict.get("joined_via_invite_code"):
                default_profile_dict["joined_via_invite_code"] = wl_data.get("invite_code_used")
            # Note: invited_by_user_id from waitlist is not currently copied to user profile directly.
            # if wl_data.get("invited_by_user_id") and not default_profile_dict.get("invited_by_user_id_on_waitlist"): 
            #     pass
        
        final_default_profile = UserProfileData(**default_profile_dict)
        try:
            user_profile_ref.set(final_default_profile.dict())
            return final_default_profile
        except Exception as e:
            print(f"Error creating default profile for {user_uid}: {e}")
            raise HTTPException(status_code=500, detail="Could not retrieve or create user profile.") from e

print("Waitlist API router defined with endpoints for joining, admin invites, accepting invites, and checking access status.")
