from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import databutton as db
import re

router = APIRouter(prefix="/legacy-points")

class PointGiftRequest(BaseModel):
    sender_id: str = Field(..., description="Profile ID of the sender")
    recipient_id: str = Field(..., description="Profile ID of the recipient")
    points: int = Field(..., gt=0, description="Number of points to gift (must be positive)")
    message: Optional[str] = Field(None, description="Personal message from sender")
    category: Optional[str] = Field("contribution", description="Category of the gift (e.g., contribution, milestone, recognition)")

class PointGiftResponse(BaseModel):
    gift_id: str = Field(..., description="Unique identifier for this gift")
    sender_id: str = Field(..., description="Profile ID of the sender")
    sender_name: str = Field(..., description="Display name of the sender")
    recipient_id: str = Field(..., description="Profile ID of the recipient")
    recipient_name: str = Field(..., description="Display name of the recipient")
    points: int = Field(..., description="Number of points gifted")
    message: Optional[str] = Field(None, description="Personal message from sender")
    category: str = Field(..., description="Category of the gift")
    timestamp: str = Field(..., description="ISO format timestamp of when the gift was sent")
    read: bool = Field(False, description="Whether the recipient has seen this gift")

class PointGiftListResponse(BaseModel):
    gifts: List[PointGiftResponse] = Field(..., description="List of point gifts")

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_profile_name(profile_id: str) -> str:
    """Get the name of a profile based on profile_id"""
    try:
        from app.apis.family_profiles import get_family_profile
        profile = get_family_profile(profile_id)
        return profile.alias or profile.full_name or f"Profile {profile_id}"
    except Exception as e:
        print(f"Error getting profile name: {e}")
        return f"Profile {profile_id}"

def get_all_gifts() -> List[Dict[str, Any]]:
    """Get all point gifts from storage"""
    try:
        gifts_data = db.storage.json.get("legacy_points_gifts", default=[])
        return gifts_data
    except Exception as e:
        print(f"Error getting gifts: {e}")
        return []

def get_gifts_for_profile(profile_id: str) -> List[Dict[str, Any]]:
    """Get all point gifts for a specific profile (sent or received)"""
    all_gifts = get_all_gifts()
    return [gift for gift in all_gifts if gift["sender_id"] == profile_id or gift["recipient_id"] == profile_id]

def save_all_gifts(gifts: List[Dict[str, Any]]):
    """Save all gifts to storage"""
    db.storage.json.put(sanitize_storage_key("legacy_points_gifts"), gifts)

@router.post("/gift", response_model=PointGiftResponse)
def create_point_gift(gift_request: PointGiftRequest) -> PointGiftResponse:
    """Create a new point gift between family members
    
    This endpoint allows family members to gift Legacy Points to each other,
    recognizing contributions to the family's legacy and fostering a sense of community.
    
    Args:
        gift_request (PointGiftRequest): The details of the point gift, including:
            - sender_id: Profile ID of the sender
            - recipient_id: Profile ID of the recipient
            - points: Number of points to gift (must be positive)
            - message: Optional personal message from sender
            - category: Optional category of the gift
            
    Returns:
        PointGiftResponse: The created point gift with all information
        
    Raises:
        HTTPException: 400 error if profiles don't exist or other validation issues
    """
    # Validate that both sender and recipient exist
    try:
        from app.apis.family_profiles import get_family_profile
        sender = get_family_profile(gift_request.sender_id)
        recipient = get_family_profile(gift_request.recipient_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error validating profiles: {str(e)}")
    
    # Ensure sender and recipient are different
    if gift_request.sender_id == gift_request.recipient_id:
        raise HTTPException(status_code=400, detail="Cannot gift points to yourself")
    
    # Create the gift record
    import uuid
    gift_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    new_gift = {
        "gift_id": gift_id,
        "sender_id": gift_request.sender_id,
        "sender_name": sender.alias or sender.full_name or f"Profile {sender.id}",
        "recipient_id": gift_request.recipient_id,
        "recipient_name": recipient.alias or recipient.full_name or f"Profile {recipient.id}",
        "points": gift_request.points,
        "message": gift_request.message,
        "category": gift_request.category or "contribution",
        "timestamp": timestamp,
        "read": False
    }
    
    # Save the gift
    all_gifts = get_all_gifts()
    all_gifts.append(new_gift)
    save_all_gifts(all_gifts)
    
    # Update legacy score
    try:
        from app.apis.legacy_score import recalculate_legacy_score
        # Recalculate for both sender and recipient
        if hasattr(sender, 'vault_id'):
            recalculate_legacy_score(sender.vault_id)
        if hasattr(recipient, 'vault_id'):
            recalculate_legacy_score(recipient.vault_id)
    except Exception as e:
        print(f"Error updating legacy score: {e}")
    
    return PointGiftResponse(**new_gift)

@router.get("/profile/{profile_id}", response_model=PointGiftListResponse)
def get_profile_gifts(profile_id: str) -> PointGiftListResponse:
    """Get all point gifts for a specific profile
    
    This endpoint retrieves all point gifts that a profile has sent or received,
    providing a complete history of all gifting activity for the profile.
    
    Args:
        profile_id (str): The unique identifier for the family member profile
        
    Returns:
        PointGiftListResponse: Object containing the list of all point gifts
        
    Raises:
        HTTPException: 404 error if no profile with the specified ID exists
    """
    # Validate that profile exists
    try:
        from app.apis.family_profiles import get_family_profile
        profile = get_family_profile(profile_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Profile not found: {str(e)}")
    
    # Get all gifts for this profile
    profile_gifts = get_gifts_for_profile(profile_id)
    
    return PointGiftListResponse(gifts=[PointGiftResponse(**gift) for gift in profile_gifts])

@router.get("/received/{profile_id}", response_model=PointGiftListResponse)
def get_received_gifts(profile_id: str) -> PointGiftListResponse:
    """Get all point gifts received by a specific profile
    
    This endpoint retrieves all point gifts that a profile has received,
    allowing the profile to see all the points other family members have gifted them.
    
    Args:
        profile_id (str): The unique identifier for the family member profile
        
    Returns:
        PointGiftListResponse: Object containing the list of received point gifts
        
    Raises:
        HTTPException: 404 error if no profile with the specified ID exists
    """
    # Validate that profile exists
    try:
        from app.apis.family_profiles import get_family_profile
        profile = get_family_profile(profile_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Profile not found: {str(e)}")
    
    # Get all gifts for this profile
    all_gifts = get_all_gifts()
    received_gifts = [gift for gift in all_gifts if gift["recipient_id"] == profile_id]
    
    return PointGiftListResponse(gifts=[PointGiftResponse(**gift) for gift in received_gifts])

@router.get("/sent/{profile_id}", response_model=PointGiftListResponse)
def get_sent_gifts(profile_id: str) -> PointGiftListResponse:
    """Get all point gifts sent by a specific profile
    
    This endpoint retrieves all point gifts that a profile has sent to others,
    allowing the profile to see all the points they have gifted to other family members.
    
    Args:
        profile_id (str): The unique identifier for the family member profile
        
    Returns:
        PointGiftListResponse: Object containing the list of sent point gifts
        
    Raises:
        HTTPException: 404 error if no profile with the specified ID exists
    """
    # Validate that profile exists
    try:
        from app.apis.family_profiles import get_family_profile
        profile = get_family_profile(profile_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Profile not found: {str(e)}")
    
    # Get all gifts for this profile
    all_gifts = get_all_gifts()
    sent_gifts = [gift for gift in all_gifts if gift["sender_id"] == profile_id]
    
    return PointGiftListResponse(gifts=[PointGiftResponse(**gift) for gift in sent_gifts])

@router.post("/mark-read/{gift_id}")
def mark_gift_as_read(gift_id: str) -> Dict[str, Any]:
    """Mark a point gift as read by the recipient
    
    This endpoint updates a specific point gift to indicate that the recipient has seen it,
    allowing the UI to show which gifts are new or unread.
    
    Args:
        gift_id (str): The unique identifier for the point gift
        
    Returns:
        Dict[str, Any]: Success message and updated gift information
        
    Raises:
        HTTPException: 404 error if no gift with the specified ID exists
    """
    all_gifts = get_all_gifts()
    gift_found = False
    
    for gift in all_gifts:
        if gift["gift_id"] == gift_id:
            gift["read"] = True
            gift_found = True
            break
    
    if not gift_found:
        raise HTTPException(status_code=404, detail=f"Gift with ID {gift_id} not found")
    
    save_all_gifts(all_gifts)
    
    return {"status": "success", "message": f"Gift {gift_id} marked as read"}
