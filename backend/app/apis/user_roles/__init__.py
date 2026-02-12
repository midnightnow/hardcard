from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the unified Role enum
from app.apis.auth import Role  # Assuming Role enum is in auth/__init__.py
from app.auth import AuthorizedUser # For current user dependency
from firebase_admin import firestore
from app.apis.firebase_init import initialize_firebase

# Initialize Firebase
initialize_firebase()

router = APIRouter(prefix="/user-roles", tags=["User Roles & Permissions"])

def get_firestore_db():
    """Dependency to get a Firestore client."""
    return firestore.client()


# --- Pydantic Models ---
# ALLOWED_ROLES_LITERAL is now replaced by the Role enum

class UserRoleBase(BaseModel):
    role: Role = Field(..., description="The role assigned to the user.")
    did: Optional[str] = Field(None, description="Decentralized Identifier for the user, if applicable.")

class UserRoleDB(UserRoleBase):
    uid: str # UID is part of the document ID in Firestore, but good to have in the model

class UserRoleResponse(UserRoleBase):
    uid: str = Field(..., description="The Firebase UID of the user.")

class SetRoleRequest(BaseModel): # Renamed from UserRoleData to be more specific
    role: Role # Use the Role enum
    did: Optional[str] = None

class UserRoleListResponse(BaseModel):
    roles: List[UserRoleResponse]

# --- Role Checking Dependencies ---

async def get_actor_role_from_firestore(
    current_user: AuthorizedUser, 
    db_client: firestore.Client = Depends(get_firestore_db)
) -> str:
    """
    Retrieves the user's role from Firestore. Defaults to 'user' if not found or error.
    """
    print(f"Attempting to get role for UID: {current_user.sub} from Firestore.")
    try:
        user_role_ref = db_client.collection("user_roles").document(current_user.sub)
        doc = user_role_ref.get()
        if doc.exists:
            role_data = doc.to_dict()
            role_value = role_data.get("role")
            print(f"Role data found for UID {current_user.sub}: {role_value}")
            # Ensure the role value from DB is a valid Role enum member string
            if role_value in Role._value2member_map_:
                return role_value # Return the string value directly
            else:
                print(f"Warning: Role '{role_value}' from Firestore for UID {current_user.sub} is not in defined Role enum. Defaulting to '{Role.USER.value}'.")
                return Role.USER.value
        else:
            print(f"No role document found for UID: {current_user.sub}. Defaulting to '{Role.USER.value}'.")
            return Role.USER.value # Default role if no specific role is assigned
    except Exception as e:
        print(f"Error fetching role for UID {current_user.sub} from Firestore: {e}. Defaulting to '{Role.USER.value}'.")
        return Role.USER.value # Default role on error

async def require_admin_role(actor_role: str = Depends(get_actor_role_from_firestore)):
    """Dependency that raises HTTPException if the current actor is not a GLOBAL_ADMIN."""
    print(f"require_admin_role: Checking if actor_role '{actor_role}' is GLOBAL_ADMIN.")
    # Use .value to compare with the string role from Firestore
    if actor_role != Role.GLOBAL_ADMIN.value: # Check against GLOBAL_ADMIN
        print(f"Access denied: Actor role '{actor_role}' is not {Role.GLOBAL_ADMIN.value}.")
        raise HTTPException(status_code=403, detail="Global Administrator privileges required.")
    print(f"Access granted: Actor role is {Role.GLOBAL_ADMIN.value}.")
    return True

# --- API Endpoints ---

@router.post(
    "/{uid_to_set}", # Changed path parameter name to avoid conflict with uid in UserRoleResponse
    response_model=UserRoleResponse, 
    summary="Set or Update User Role (Admin Only)",
    dependencies=[Depends(require_admin_role)] # Enforce admin role for this endpoint
)
async def set_user_role(
    uid_to_set: str = Path(..., description="Firebase UID of the user whose role is to be set."),
    role_request: SetRoleRequest = Body(...), # Changed variable name
    db_client: firestore.Client = Depends(get_firestore_db),
    actor_role: str = Depends(get_actor_role_from_firestore) # Added to get the admin's role for logging
):
    # Actual Firestore logic to set the role
    print(f"Admin '{actor_role}' setting role for UID: {uid_to_set} to role: {role_request.role}")
    try:
        user_role_ref = db_client.collection("user_roles").document(uid_to_set)
        user_role_ref.set({
            "role": role_request.role.value, # Store the enum's value (string)
            "did": role_request.did
        })
        print(f"Successfully set role for {uid_to_set} to {role_request.role} in Firestore.")
        return UserRoleResponse(uid=uid_to_set, role=role_request.role, did=role_request.did) # role_request.role is already a Role enum member
    except Exception as e:
        print(f"Error setting role for {uid_to_set} in Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not set user role: {str(e)}")

@router.get(
    "/{uid_to_get}", # Changed path parameter name
    response_model=UserRoleResponse, 
    summary="Get User Role (Admin or Self)"
)
async def get_user_role(
    current_user: AuthorizedUser,
    uid_to_get: str = Path(..., description="Firebase UID of the user whose role is to be retrieved."),
    actor_role: str = Depends(get_actor_role_from_firestore), # Role of the user making the request
    db_client: firestore.Client = Depends(get_firestore_db)
):
    print(f"User {current_user.sub} (role: {actor_role}) attempting to get role for UID: {uid_to_get}.")
    if actor_role != "admin" and current_user.sub != uid_to_get:
        print(f"Access denied for {current_user.sub} to get role of {uid_to_get}.")
        raise HTTPException(status_code=403, detail="Forbidden: You can only view your own role or you must be an admin.")

    # Actual Firestore logic to get the role
    try:
        user_role_ref = db_client.collection("user_roles").document(uid_to_get)
        doc = user_role_ref.get()
        if doc.exists:
            role_data = doc.to_dict()
            role_value = role_data.get("role", Role.USER.value)
            # Ensure the role value from DB is a valid Role enum member string before constructing UserRoleResponse
            if role_value not in Role._value2member_map_:
                print(f"Warning: Role '{role_value}' from Firestore for UID {uid_to_get} not in defined Role enum. Defaulting for response.")
                role_value = Role.USER.value
            return UserRoleResponse(uid=uid_to_get, role=Role(role_value), did=role_data.get("did"))
        else:
            # If the document does not exist, return a default 'user' role.
            # The frontend RoleStore can also default, but this makes the API more robust.
            print(f"No role document found for UID: {uid_to_get}. Returning default '{Role.USER.value}' role.")
            return UserRoleResponse(uid=uid_to_get, role=Role.USER, did=None)
    except Exception as e:
        print(f"Error getting role for {uid_to_get} from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve user role: {str(e)}")


@router.get(
    "/", 
    response_model=UserRoleListResponse, 
    summary="List All User Roles (Admin Only)",
    dependencies=[Depends(require_admin_role)] # Enforce admin role
)
async def list_user_roles(db_client: firestore.Client = Depends(get_firestore_db)):
    print("Admin (verified) attempting to list all user roles.")
    roles_list = []
    try:
        users_roles_ref = db_client.collection("user_roles").stream()
        for doc in users_roles_ref:
            data = doc.to_dict()
            role_value = data.get("role", Role.USER.value)
            # Ensure the role value from DB is a valid Role enum member string
            if role_value not in Role._value2member_map_:
                print(f"Warning: Role '{role_value}' from Firestore for UID {doc.id} not in defined Role enum during list. Defaulting for response.")
                role_value = Role.USER.value
            roles_list.append(UserRoleResponse(uid=doc.id, role=Role(role_value), did=data.get("did")))
        return UserRoleListResponse(roles=roles_list)
    except Exception as e:
        print(f"Error listing user roles from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not list user roles: {str(e)}")


@router.delete(
    "/{uid_to_delete}", # Changed path parameter name
    status_code=204, # No content response
    summary="Delete User Role (Admin Only)",
    dependencies=[Depends(require_admin_role)] # Enforce admin role
)
async def delete_user_role(
    uid_to_delete: str = Path(..., description="Firebase UID of the user whose role is to be deleted."),
    db_client: firestore.Client = Depends(get_firestore_db)
):
    print(f"Admin (verified) attempting to delete role for UID: {uid_to_delete}")
    try:
        user_role_ref = db_client.collection("user_roles").document(uid_to_delete)
        # Check if document exists before deleting (optional, delete is idempotent)
        doc = user_role_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Role for user {uid_to_delete} not found, cannot delete.")
        
        user_role_ref.delete()
        print(f"Successfully deleted role for {uid_to_delete} from Firestore.")
        return # Returns 204 No Content
    except HTTPException: # Re-raise specific HTTP exceptions
        raise
    except Exception as e:
        print(f"Error deleting role for {uid_to_delete} from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not delete user role: {str(e)}")

# Example of how to use the role in another protected endpoint (conceptual)
# from app.auth import AuthorizedUser # Already imported
# @router.get("/some-admin-action", summary="Example Admin-Only Action")
# async def some_admin_action(
#     current_user: AuthorizedUser = Depends(AuthorizedUser), # Get current authenticated user
#     is_admin: bool = Depends(require_admin_role) # Enforce admin role
# ):
#     # If we reach here, require_admin_role did not raise an exception, so user is admin
#     return {"message": f"Admin action performed by {current_user.email} (UID: {current_user.sub})"}

print("User Roles API router defined.")

