from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import databutton as db
import re
from datetime import datetime
from app.auth import AuthorizedUser

router = APIRouter()

# Models for request and response
class DataCategory(BaseModel):
    id: str
    name: str
    description: str
    entry_count: int
    last_updated: Optional[datetime] = None

class DataUsagePolicy(BaseModel):
    storage_duration_days: int = 30
    allow_analytics: bool = False
    share_with_third_parties: bool = False

class UserDataSummary(BaseModel):
    categories: List[DataCategory]
    policy: DataUsagePolicy

class UpdatePolicyRequest(BaseModel):
    policy: DataUsagePolicy

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_default_data_policy() -> DataUsagePolicy:
    """Get the default data usage policy"""
    return DataUsagePolicy()

def get_user_data_categories(user_id: str) -> List[DataCategory]:
    """Get data categories for the user"""
    try:
        # This would normally scan storage for user data
        # For prototype, we'll return static examples
        return [
            DataCategory(
                id="conversations",
                name="Conversation History",
                description="Your chat conversations with philosophical personas",
                entry_count=3,
                last_updated=datetime.now()
            ),
            DataCategory(
                id="voice_recordings",
                name="Voice Recordings",
                description="Temporary voice recordings used for transcription",
                entry_count=5,
                last_updated=datetime.now()
            ),
            DataCategory(
                id="preferences",
                name="User Preferences",
                description="Your app settings and preferences",
                entry_count=1,
                last_updated=datetime.now()
            )
        ]
    except Exception as e:
        print(f"Error getting user data categories: {e}")
        return []

def get_user_data_policy(user_id: str) -> DataUsagePolicy:
    """Get data usage policy for the user"""
    try:
        storage_key = sanitize_storage_key(f"data_policy_{user_id}")
        try:
            policy_data = db.storage.json.get(storage_key)
            return DataUsagePolicy(**policy_data)
        except:
            # Create default policy if it doesn't exist
            default_policy = get_default_data_policy()
            db.storage.json.put(storage_key, default_policy.dict())
            return default_policy
    except Exception as e:
        print(f"Error getting user data policy: {e}")
        # Return default policy if storage fails
        return get_default_data_policy()

@router.get("/privacy-data-summary", response_model=UserDataSummary)
async def get_privacy_data_summary(user: AuthorizedUser):
    """Get a summary of user data and current privacy policy"""
    try:
        categories = get_user_data_categories(user.sub)
        policy = get_user_data_policy(user.sub)
        
        return UserDataSummary(
            categories=categories,
            policy=policy
        )
    except Exception as e:
        print(f"Error in get_privacy_data_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/policy", response_model=DataUsagePolicy)
async def update_data_policy(request: UpdatePolicyRequest, user: AuthorizedUser):
    """Update the user's data usage policy"""
    try:
        storage_key = sanitize_storage_key(f"data_policy_{user.sub}")
        
        # Save updated policy
        db.storage.json.put(storage_key, request.policy.dict())
        
        return request.policy
    except Exception as e:
        print(f"Error in update_data_policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/data/{category_id}")
async def delete_data_category(category_id: str, user: AuthorizedUser):
    """Delete all user data in a specific category"""
    try:
        # This would normally delete all data in the category
        # For prototype, we just acknowledge the request
        
        if category_id not in ["conversations", "voice_recordings", "preferences"]:
            raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")
            
        return {"status": "success", "message": f"All data in category '{category_id}' has been deleted"}
    except Exception as e:
        print(f"Error in delete_data_category: {e}")
        raise HTTPException(status_code=500, detail=str(e))
