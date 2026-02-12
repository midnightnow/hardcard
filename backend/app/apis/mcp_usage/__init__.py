from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import databutton as db
import json
import re

router = APIRouter()

class MickoUsageRequest(BaseModel):
    message: str
    child_id: str
    parental_controls: Dict[str, Any] = {}
    context: Optional[Dict[str, Any]] = None

class MickoUsageResponse(BaseModel):
    response: str
    memory_saved: bool = False
    badge_issued: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None

class MickoMemoryRequest(BaseModel):
    child_id: str
    content: str
    content_type: str = "text"
    metadata: Optional[Dict[str, Any]] = None

class MickoMemoryResponse(BaseModel):
    memory_id: str
    success: bool

class MickoBadgeRequest(BaseModel):
    child_id: str
    achievement: str
    details: Dict[str, Any] = {}

class MickoBadgeResponse(BaseModel):
    badge_id: str
    success: bool

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def filter_content_for_child(content: str, age_range: str, blocked_topics: List[str] = None) -> str:
    """Filter content to be appropriate for the given age range and blocked topics"""
    # In a real implementation, this would use more sophisticated content filtering
    # For this example, we'll just do a simple replacement of blocked words
    
    if blocked_topics:
        for topic in blocked_topics:
            content = re.sub(r'\\b' + re.escape(topic) + r'\\b', '[appropriate content]', content, flags=re.IGNORECASE)
    
    return content

@router.post("/micko/chat")
def process_child_chat(request: MickoUsageRequest) -> MickoUsageResponse:
    """Process a chat message from a child using the DevHelper MCP agent
    
    This endpoint demonstrates how the DevHelper MCP agent can be used to power
    the Micko.au "Jarvis for your son" kid-friendly AI companion. It processes
    the child's message, applying appropriate content filtering based on parental
    controls, and returns a response suitable for the child.
    """
    try:
        # Get child profile from storage
        child_profile_key = sanitize_storage_key(f"child-profile-{request.child_id}")
        try:
            child_profile = db.storage.json.get(child_profile_key, {})
        except:
            # Create default profile if not found
            child_profile = {
                "id": request.child_id,
                "age": 8,  # Default age
                "name": "Buddy",  # Default name
                "interests": [],
                "learning_level": "elementary"
            }
            db.storage.json.put(child_profile_key, child_profile)
        
        # Apply content filtering based on parental controls
        age_range = request.parental_controls.get("age_range", f"{child_profile['age']}-{child_profile['age']+2}")
        blocked_topics = request.parental_controls.get("blocked_topics", [])
        
        # Generate a child-appropriate response
        # In a real implementation, this would use the DevHelper MCP agent
        # For this example, we'll generate a simple response
        sample_responses = [
            f"That's a great question! I'd love to help you learn about that, {child_profile['name']}!",
            f"Hmm, let me think about that, {child_profile['name']}. Here's what I know:",
            f"That's interesting, {child_profile['name']}! Did you know...",
            f"I'm glad you asked, {child_profile['name']}! Here's something cool:"
        ]
        import random
        response_prefix = random.choice(sample_responses)
        
        # Build a response based on the child's message
        if "dinosaur" in request.message.lower():
            response = f"{response_prefix} Dinosaurs were amazing creatures that lived millions of years ago. T-Rex was one of the biggest meat-eaters with tiny arms but powerful jaws!"
            topic = "dinosaurs"
        elif "space" in request.message.lower() or "planet" in request.message.lower():
            response = f"{response_prefix} Space is incredible! Our solar system has 8 planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Jupiter is the biggest one!"
            topic = "space"
        elif "math" in request.message.lower() or "add" in request.message.lower() or "plus" in request.message.lower():
            response = f"{response_prefix} Math is like a puzzle game! When we add numbers together, we're combining quantities. For example, 5 + 3 = 8."
            topic = "math"
        else:
            response = f"{response_prefix} That's an interesting thought. Would you like to learn about dinosaurs, space, or maybe do some fun math games?"
            topic = "general"
        
        # Add appropriate emoji based on topic
        emoji_map = {
            "dinosaurs": "🦖",
            "space": "🚀",
            "math": "🔢",
            "general": "🌟"
        }
        response += f" {emoji_map.get(topic, '✨')}"
        
        # Filter content for appropriateness
        filtered_response = filter_content_for_child(response, age_range, blocked_topics)
        
        # Check if we should save this interaction to memory
        memory_saved = False
        if "remember" in request.message.lower():
            # Save to child's memory vault
            memory_key = sanitize_storage_key(f"child-memory-{request.child_id}")
            try:
                memories = db.storage.json.get(memory_key, [])
            except:
                memories = []
                
            memories.append({
                "timestamp": import_time(),
                "message": request.message,
                "response": filtered_response,
                "topic": topic
            })
            
            db.storage.json.put(memory_key, memories)
            memory_saved = True
            filtered_response += " I'll remember this conversation! 📝"
        
        # Check if we should issue a badge
        badge_issued = None
        if topic in ["dinosaurs", "space", "math"] and len(request.message) > 20:
            # This would integrate with Hardcard in a real implementation
            badge_issued = f"{topic.capitalize()} Explorer"
            filtered_response += f"\n\nCongratulations! You've earned the {badge_issued} badge! 🏆"
        
        return MickoUsageResponse(
            response=filtered_response,
            memory_saved=memory_saved,
            badge_issued=badge_issued,
            analysis={
                "topic": topic,
                "content_level": "G",
                "engagement_score": 0.8
            }
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/micko/save-memory")
def save_to_memory_vault(request: MickoMemoryRequest) -> MickoMemoryResponse:
    """Save content to a child's memory vault in Legacy Vault
    
    This endpoint demonstrates how the Micko.au application can save meaningful
    interactions and content to the Legacy Vault service, creating a growing 
    memory timeline for the child.
    """
    try:
        # Save to child's memory vault
        memory_key = sanitize_storage_key(f"child-memory-{request.child_id}")
        try:
            memories = db.storage.json.get(memory_key, [])
        except:
            memories = []
            
        import time
        memory_id = f"memory-{int(time.time())}"
        
        memory_entry = {
            "id": memory_id,
            "timestamp": int(time.time()),
            "content": request.content,
            "content_type": request.content_type,
            "metadata": request.metadata or {}
        }
        
        memories.append(memory_entry)
        db.storage.json.put(memory_key, memories)
        
        return MickoMemoryResponse(
            memory_id=memory_id,
            success=True
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/micko/issue-badge")
def issue_hardcard_credential(request: MickoBadgeRequest) -> MickoBadgeResponse:
    """Issue a credential for a child's achievement using Hardcard
    
    This endpoint demonstrates how the Micko.au application can issue digital
    credentials for a child's achievements, storing them securely using the
    Hardcard blockchain/DID registry.
    """
    try:
        # This would integrate with Hardcard in a real implementation
        # For this example, we'll just store the badge in our database
        badge_key = sanitize_storage_key(f"child-badges-{request.child_id}")
        try:
            badges = db.storage.json.get(badge_key, [])
        except:
            badges = []
            
        import time
        badge_id = f"badge-{int(time.time())}"
        
        badge_entry = {
            "id": badge_id,
            "timestamp": int(time.time()),
            "achievement": request.achievement,
            "details": request.details
        }
        
        badges.append(badge_entry)
        db.storage.json.put(badge_key, badges)
        
        return MickoBadgeResponse(
            badge_id=badge_id,
            success=True
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))