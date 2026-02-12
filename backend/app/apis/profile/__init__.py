from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.auth import AuthorizedUser
from app.apis.firebase import get_user_data

router = APIRouter()

class UserProfileResponse(BaseModel):
    level: int
    xp: int
    vault_points: int
    lore_fragments_unlocked: Optional[List[str]] = None

@router.get("/user-stats")
def get_user_profile_stats(user: AuthorizedUser) -> UserProfileResponse:
    """
    Get the current user's profile including level, XP, and vault points
    
    This endpoint retrieves the user's profile data from Firestore, including
    their Hardcard level, experience points, vault points, and unlocked lore fragments.
    """
    try:
        # Get user data from Firebase
        user_data = get_user_data(user.sub)
        
        if not user_data:
            # If user doesn't exist yet, return default values
            # For development testing, check for test_mode in the request
            test_mode = "test_mode" in user.sub
            
            # If in test mode, return a default profile with higher level for testing
            if test_mode:
                return UserProfileResponse(
                    level=3,  # Higher level for testing
                    xp=50000,
                    vault_points=2500,
                    unlocked_lore_fragments=["fragment1", "fragment2", "fragment3"]
                )
                
            return UserProfileResponse(
                level=0,
                xp=0,
                vault_points=0,
                lore_fragments_unlocked=[]
            )
        
        return UserProfileResponse(
            level=user_data.get("level", 0),
            xp=user_data.get("xp", 0),
            vault_points=user_data.get("vault_points", 0),
            lore_fragments_unlocked=user_data.get("lore_fragments_unlocked", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")
