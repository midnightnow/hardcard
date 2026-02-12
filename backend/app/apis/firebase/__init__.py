import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import databutton as db
from firebase_admin import firestore
# Import Firebase modules
from app.apis.firebase_init import initialize_firebase

# Initialize Firebase
initialize_firebase()

# Create a FastAPI router
router = APIRouter()

# Define Pydantic models for request/response validation
class UserDataResponse(BaseModel):
    level: int
    xp: int
    vault_points: int
    lore_fragments_unlocked: list[str]

class UpdateUserRequest(BaseModel):
    level: int
    xp_to_add: int
    points_to_add: int

class LoreFragmentRequest(BaseModel):
    fragment_id: str

class StripeEventRequest(BaseModel):
    event_id: str
    event_type: str
    data: dict

class StripeErrorRequest(BaseModel):
    event_id: str
    error_message: str
    payload: dict

# API endpoints
@router.get("/users/{user_id}")
def get_user_data_endpoint(user_id: str) -> UserDataResponse:
    """Get user data from Firestore."""
    user_data = get_user_data(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDataResponse(**user_data)

@router.post("/users/{user_id}/update")
def update_user_data(user_id: str, request: UpdateUserRequest) -> UserDataResponse:
    """Update user level, XP, and vault points."""
    updated_data = update_user_level_xp_points(
        user_id, 
        request.level, 
        request.xp_to_add, 
        request.points_to_add
    )
    if not updated_data:
        raise HTTPException(status_code=500, detail="Failed to update user data")
    return UserDataResponse(**updated_data)

@router.post("/users/{user_id}/unlock-lore")
def unlock_lore_endpoint(user_id: str, request: LoreFragmentRequest) -> UserDataResponse:
    """Unlock a lore fragment for a user."""
    updated_data = unlock_lore_fragment(user_id, request.fragment_id)
    if not updated_data:
        raise HTTPException(status_code=500, detail="Failed to unlock lore fragment")
    return UserDataResponse(**updated_data)

@router.get("/lore/level/{level}")
def get_lore_fragments_endpoint(level: int) -> list[str]:
    """Get lore fragments that should be unlocked at a specific level."""
    return get_lore_fragments_for_level(level)

@router.post("/stripe/log-event/{user_id}")
def log_stripe_event_endpoint(user_id: str, request: StripeEventRequest) -> dict:
    """Log a Stripe event to Firestore."""
    log_data = log_stripe_event(
        request.event_id,
        request.event_type,
        user_id,
        request.data
    )
    if not log_data:
        raise HTTPException(status_code=500, detail="Failed to log Stripe event")
    return log_data

@router.post("/stripe/log-error")
def log_stripe_error_endpoint(request: StripeErrorRequest) -> dict:
    """Log a Stripe error to Firestore."""
    log_data = log_stripe_error(
        request.event_id,
        request.error_message,
        request.payload
    )
    if not log_data:
        raise HTTPException(status_code=500, detail="Failed to log Stripe error")
    return log_data

# Ensure Firebase is initialized
initialize_firebase()

def get_user_data(user_id):
    """
    Get user data from Firestore
    
    Args:
        user_id (str): The user ID
        
    Returns:
        dict: The user data
    """
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # Try to get user data from Firestore
        user_doc = db_client.collection('users').document(user_id).get()
        
        if user_doc.exists:
            return user_doc.to_dict()
        
        # If user document doesn't exist, create it with default values
        default_data = {
            "level": 0,
            "xp": 0,
            "vault_points": 0,
            "lore_fragments_unlocked": []
        }
        
        db_client.collection('users').document(user_id).set(default_data)
        return default_data
    except Exception as e:
        print(f"Error getting user data from Firestore: {str(e)}")
        # Fallback to Databutton storage for development/testing
        try:
            user_data_key = f"user_profile_{user_id}"
            user_data = db.storage.json.get(user_data_key, default={})
            
            # If no data exists, initialize with defaults
            if not user_data:
                user_data = {
                    "level": 0,
                    "xp": 0,
                    "vault_points": 0,
                    "lore_fragments_unlocked": []
                }
                db.storage.json.put(user_data_key, user_data)
                
            return user_data
        except Exception as e2:
            print(f"Error getting user data from Databutton storage: {str(e2)}")
            return {
                "level": 0,
                "xp": 0,
                "vault_points": 0,
                "lore_fragments_unlocked": []
            }

def update_user_level_xp_points(user_id, level, xp_to_add, points_to_add):
    """
    Update user level, XP, and vault points in Firestore
    
    Args:
        user_id (str): The user ID
        level (int): The new level
        xp_to_add (int): The XP to add
        points_to_add (int): The vault points to add
        
    Returns:
        dict: The updated user data
    """
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # Try to update user data in Firestore
        user_ref = db_client.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
        else:
            user_data = {
                "level": 0,
                "xp": 0,
                "vault_points": 0,
                "lore_fragments_unlocked": []
            }
        
        # Get current values
        current_level = user_data.get('level', 0)
        current_xp = user_data.get('xp', 0)
        current_points = user_data.get('vault_points', 0)
        
        # Only update level if the new level is higher
        if level > current_level:
            user_data['level'] = level
        
        # Always add XP and points
        user_data['xp'] = current_xp + xp_to_add
        user_data['vault_points'] = current_points + points_to_add
        
        # Save the updated data
        user_ref.set(user_data)
        
        return user_data
    except Exception as e:
        print(f"Error updating user data in Firestore: {str(e)}")
        # Fallback to Databutton storage for development/testing
        try:
            user_data_key = f"user_profile_{user_id}"
            user_data = db.storage.json.get(user_data_key, default={})
            
            # Get current values or set defaults
            current_level = user_data.get('level', 0)
            current_xp = user_data.get('xp', 0)
            current_points = user_data.get('vault_points', 0)
            
            # Only update level if the new level is higher
            if level > current_level:
                user_data['level'] = level
            
            # Always add XP and points
            user_data['xp'] = current_xp + xp_to_add
            user_data['vault_points'] = current_points + points_to_add
            
            # Save the updated data
            db.storage.json.put(user_data_key, user_data)
            
            return user_data
        except Exception as e2:
            print(f"Error updating user data in Databutton storage: {str(e2)}")
            return None

def unlock_lore_fragment(user_id, fragment_id):
    """
    Unlock a lore fragment for a user
    
    Args:
        user_id (str): The user ID
        fragment_id (str): The lore fragment ID
        
    Returns:
        dict: The updated user data
    """
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # Try to update user data in Firestore
        user_ref = db_client.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
        else:
            user_data = {
                "level": 0,
                "xp": 0,
                "vault_points": 0,
                "lore_fragments_unlocked": []
            }
        
        # Get current unlocked fragments
        unlocked_fragments = user_data.get('lore_fragments_unlocked', [])
        
        # Only add if not already unlocked
        if fragment_id not in unlocked_fragments:
            unlocked_fragments.append(fragment_id)
            user_data['lore_fragments_unlocked'] = unlocked_fragments
            
            # Save the updated data
            user_ref.set(user_data)
        
        return user_data
    except Exception as e:
        print(f"Error unlocking lore fragment in Firestore: {str(e)}")
        # Fallback to Databutton storage for development/testing
        try:
            user_data_key = f"user_profile_{user_id}"
            user_data = db.storage.json.get(user_data_key, default={})
            
            # Get current unlocked fragments
            unlocked_fragments = user_data.get('lore_fragments_unlocked', [])
            
            # Only add if not already unlocked
            if fragment_id not in unlocked_fragments:
                unlocked_fragments.append(fragment_id)
                user_data['lore_fragments_unlocked'] = unlocked_fragments
                
                # Save the updated data
                db.storage.json.put(user_data_key, user_data)
            
            return user_data
        except Exception as e2:
            print(f"Error unlocking lore fragment in Databutton storage: {str(e2)}")
            return None

def get_lore_fragments_for_level(level):
    """
    Get lore fragments that should be unlocked at a specific level
    
    Args:
        level (int): The level to get fragments for
        
    Returns:
        list: List of lore fragment IDs
    """
    # This mapping defines which fragments are unlocked at each level
    level_to_fragments = {
        0: ["origins-1", "security-1"],
        1: ["guardian-secrets-1"],
        2: ["sentinel-archives-1"],
        3: ["custodian-codex-1"],
        4: ["sovereign-principles-1"],
        5: ["oracle-vision-1"],
        6: ["ascendant-wisdom-1"],
        7: ["architect-paradigm-1"],
        8: ["chronos-secrets-1"],
        9: ["genesis-codex-1"],
    }
    
    return level_to_fragments.get(level, [])

def log_stripe_event(event_id, event_type, user_id, data):
    """
    Log a Stripe event to Firestore
    
    Args:
        event_id (str): The Stripe event ID
        event_type (str): The Stripe event type
        user_id (str): The user ID
        data (dict): Additional data to log
        
    Returns:
        dict: The created log entry
    """
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # Create log entry in Firestore
        log_ref = db_client.collection('stripe_events').document(event_id)
        
        log_data = {
            "event_id": event_id,
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "data": data
        }
        
        log_ref.set(log_data)
        return log_data
    except Exception as e:
        print(f"Error logging Stripe event to Firestore: {str(e)}")
        # Fallback to Databutton storage for development/testing
        try:
            log_key = f"stripe_event_{event_id}"
            log_data = {
                "event_id": event_id,
                "event_type": event_type,
                "user_id": user_id,
                "timestamp": str(firestore.SERVER_TIMESTAMP),  # Convert to string for JSON storage
                "data": data
            }
            
            db.storage.json.put(log_key, log_data)
            return log_data
        except Exception as e2:
            print(f"Error logging Stripe event to Databutton storage: {str(e2)}")
            return None

def log_stripe_error(event_id, error_message, payload):
    """
    Log a Stripe error to Firestore
    
    Args:
        event_id (str): The Stripe event ID
        error_message (str): The error message
        payload (dict): Additional data about the error
        
    Returns:
        dict: The created error log entry
    """
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # Create error log entry in Firestore
        log_id = f"error_{event_id}_{str(int(time.time()))}"
        log_ref = db_client.collection('stripe_errors').document(log_id)
        
        log_data = {
            "event_id": event_id,
            "error_message": error_message,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "payload": payload
        }
        
        log_ref.set(log_data)
        return log_data
    except Exception as e:
        print(f"Error logging Stripe error to Firestore: {str(e)}")
        # Fallback to Databutton storage for development/testing
        try:
            log_key = f"stripe_error_{event_id}_{int(time.time())}"
            log_data = {
                "event_id": event_id,
                "error_message": error_message,
                "timestamp": str(firestore.SERVER_TIMESTAMP),  # Convert to string for JSON storage
                "payload": payload
            }
            
            db.storage.json.put(log_key, log_data)
            return log_data
        except Exception as e2:
            print(f"Error logging Stripe error to Databutton storage: {str(e2)}")
            return None

def get_user_lore(user_id: str) -> Dict[str, Any]:
    """
    Retrieve a user's lore data from Firestore
    
    Args:
        user_id: The Firebase user ID
        
    Returns:
        Dict containing unlocked lore fragments and count of locked fragments
    """
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # Try to get lore data from Firestore
        lore_ref = db_client.collection('users').document(user_id).collection('lore').document('status')
        lore_doc = lore_ref.get()
        
        if lore_doc.exists:
            return lore_doc.to_dict() or {}
        
        # If lore document doesn't exist, create it with default values
        default_data = {
            "unlocked": [],
            "locked_count": 5  # Default number of locked fragments
        }
        
        lore_ref.set(default_data)
        return default_data
    except Exception as e:
        print(f"Error getting user lore data from Firestore: {str(e)}")
        # Fallback to Databutton storage for development/testing
        try:
            lore_data_key = f"user_lore_{user_id}"
            lore_data = db.storage.json.get(lore_data_key, default={})
            
            # If no data exists, initialize with defaults
            if not lore_data:
                lore_data = {
                    "unlocked": [],
                    "locked_count": 5  # Default number of locked fragments
                }
                db.storage.json.put(lore_data_key, lore_data)
                
            return lore_data
        except Exception as e2:
            print(f"Error getting user lore data from Databutton storage: {str(e2)}")
            return {
                "unlocked": [],
                "locked_count": 0
            }
