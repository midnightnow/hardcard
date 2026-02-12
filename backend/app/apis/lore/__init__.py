from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.auth import AuthorizedUser
from app.apis.firebase import get_user_lore
import databutton as db

router = APIRouter()

class LoreFragment(BaseModel):
    id: str
    title: str
    content: str
    level_required: int
    category: str
    order: int
    image_url: Optional[str] = None

class LoreResponse(BaseModel):
    unlocked: List[LoreFragment]
    locked_count: int

@router.get("/user-lore")
def get_user_lore_data(user: AuthorizedUser) -> LoreResponse:
    """Get lore fragments that have been unlocked by the user
    
    This endpoint returns all lore fragments that the user has unlocked,
    as well as the count of locked fragments still available to discover.
    """
    try:
        # Get user's unlocked lore fragments from Firestore
        lore_data = get_user_lore(user.sub)
        
        # Convert to proper response format
        unlocked_fragments = []
        for fragment in lore_data.get('unlocked', []):
            unlocked_fragments.append(LoreFragment(
                id=fragment.get('id', ''),
                title=fragment.get('title', 'Untitled Fragment'),
                content=fragment.get('content', ''),
                level_required=fragment.get('level_required', 0),
                category=fragment.get('category', 'general'),
                order=fragment.get('order', 0),
                image_url=fragment.get('image_url')
            ))
        
        return LoreResponse(
            unlocked=unlocked_fragments,
            locked_count=lore_data.get('locked_count', 0)
        )
        
    except Exception as e:
        print(f"Error retrieving lore: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving lore: {str(e)}")