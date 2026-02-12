from fastapi import APIRouter, Depends
from app.auth import AuthorizedUser
from pydantic import BaseModel
from firebase_admin import firestore
from app.apis.firebase_init import initialize_firebase

# Initialize Firebase
initialize_firebase()

router = APIRouter()

class UserData(BaseModel):
    level: int = 0
    xp: int = 0
    vaultPoints: int = 0

@router.get("/me")
def get_user_data(user: AuthorizedUser) -> UserData:
    """
    Get the current user's data including level, XP, and vault points.
    """
    db = firestore.client()
    user_ref = db.collection("users").document(user.sub)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        # Create default user data if it doesn't exist
        default_data = {"level": 0, "xp": 0, "vault_points": 0}
        user_ref.set(default_data)
        return UserData(**default_data)
    
    user_data = user_doc.to_dict()
    return UserData(
        level=user_data.get("level", 0),
        xp=user_data.get("xp", 0),
        vaultPoints=user_data.get("vault_points", 0)  # Map from vault_points to vaultPoints
    )
