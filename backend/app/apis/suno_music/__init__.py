from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.auth import AuthorizedUser
import databutton as db
import uuid
import json
import random
from datetime import datetime
from app.env import mode, Mode
import re
import traceback

# Import our own electronic music implementation
from app.apis.electronic_music import GenerateMusicRequest, MusicResponse, UpdateMusicStatusRequest

# We'll import the specific functions when needed, because the route names changed

# Create a router
router = APIRouter()

# Helper Functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_all_music_records():
    """Get all music records from storage"""
    try:
        records = db.storage.json.get("music_records", default={})
        return records
    except Exception as e:
        print(f"Error getting music records: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {}

def save_music_record(music_id, record):
    """Save a music record to storage"""
    try:
        # Validate and sanitize the music_id to prevent storage injection
        if music_id == "undefined" or not music_id:
            print(f"Invalid music_id received: '{music_id}'")
            raise HTTPException(status_code=400, detail="Invalid music ID provided")
            
        # Sanitize the music_id to prevent storage injection
        sanitized_id = sanitize_storage_key(music_id)
        print(f"Saving music record with ID: {sanitized_id}")
        records = get_all_music_records()
        records[sanitized_id] = record
        db.storage.json.put("music_records", records)
    except Exception as e:
        print(f"Error saving music record: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")

def generate_track_title(concept_name, mood, genre):
    """Generate a creative track title based on concept, mood and genre"""
    adjectives = [
        "Eternal", "Cosmic", "Ethereal", "Digital", "Quantum", "Solar", 
        "Lunar", "Celestial", "Infinite", "Timeless", "Crystalline", "Golden",
        "Sacred", "Ancient", "Future", "Mystic", "Dream", "Virtual"
    ]
    
    nouns = [
        "Legacy", "Horizon", "Journey", "Odyssey", "Voyage", "Ascension", 
        "Genesis", "Echo", "Pulse", "Wave", "Reflection", "Dimension",
        "Realm", "Vision", "Portal", "Matrix", "Nexus", "Singularity"
    ]
    
    formats = [
        f"{random.choice(adjectives)} {concept_name}",
        f"{concept_name} {random.choice(nouns)}",
        f"{random.choice(adjectives)} {random.choice(nouns)}",
        f"The {random.choice(adjectives)} {concept_name}",
        f"{concept_name}'s {random.choice(nouns)}",
        f"{random.choice(adjectives)} {mood.title()} in {genre.title()}"
    ]
    
    return random.choice(formats)

# Routes - delegate to our electronic_music implementation
@router.post("/generate-music")
async def generate_music(request: GenerateMusicRequest, user: AuthorizedUser) -> MusicResponse:
    """Generate music for a vault concept
    
    This endpoint has been updated to use our in-house electronic music generator
    instead of relying on the external Suno API.
    """
    # Forward the request to our electronic music implementation
    try:
        print(f"Received music generation request for concept: {request.concept_name}")
        
        # Import what we need from the electronic music API
        from fastapi import BackgroundTasks
        from app.apis.electronic_music import process_music_generation
        
        # Create a background tasks object
        background_tasks = BackgroundTasks()
        
        # Generate a unique ID for this music request
        music_id = str(uuid.uuid4())
        print(f"Generated unique music ID: {music_id}")
        
        # Generate a creative track title
        title = generate_track_title(request.concept_name, request.mood, request.genre)
        print(f"Generated track title: {title}")
        
        # Create initial record in our own storage
        record = {
            "music_id": music_id,
            "status": "pending",  # initial status
            "title": title,
            "description": f"Electronic {request.genre} music inspired by {request.concept_name}: {request.concept_description}",
            "concept_id": request.concept_id,
            "concept_name": request.concept_name,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "concept_name": request.concept_name,
                "mood": request.mood,
                "genre": request.genre,
                "prompt": request.concept_description,
                "generated_at": datetime.now().isoformat(),
                "duration": request.duration
            }
        }
        
        # Save the initial record to our storage
        save_music_record(music_id, record)
        
        # Also create a record in the electronic music storage for compatibility
        try:
            from app.apis.electronic_music import save_music_record as save_electronic_record
            save_electronic_record(music_id, record)
            print("Saved initial record to both storage locations")
        except Exception as e_err:
            print(f"Warning: Could not save to electronic storage: {str(e_err)}")
            # Continue anyway as we have our primary storage
        
        # Log the request details for debugging
        print(f"Starting music generation for concept '{request.concept_name}' with ID {music_id}")
        print(f"Parameters: genre={request.genre}, mood={request.mood}")
        
        # Start background processing
        background_tasks.add_task(process_music_generation, music_id, request)
        print("Added music generation task to background processing queue")
        
        print(f"Successfully initiated music generation with ID: {music_id}")
        return MusicResponse(**record)
    except Exception as e:
        print(f"Error in generate_music: {str(e)}")
        # Log detailed error for debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate music: {str(e)}") from e

@router.get("/status/{music_id}")
def get_music_status(music_id: str, user: AuthorizedUser) -> MusicResponse:
    """Get the status of a music generation request
    
    This endpoint checks both the original storage and the electronic music storage locations.
    """
    # Log the raw input for debugging
    print(f"Received music status request with ID: '{music_id}'")
    # First check our own records
    try:
        # Validate music_id parameter - check for undefined, null, empty string, whitespace only
        if not music_id or music_id == "undefined" or music_id.strip() == "" or music_id == "null":
            print(f"Invalid music_id received: '{music_id}'")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid music ID provided: '{music_id}'. Cannot be empty, 'undefined', or 'null'."
            )
        
        # Sanitize the music_id to prevent storage injection
        sanitized_id = sanitize_storage_key(music_id)
        print(f"Checking status for music ID: {sanitized_id}")
        
        records = get_all_music_records()
        if sanitized_id in records:
            print(f"Found music record in original storage: {sanitized_id}")
            return MusicResponse(**records[sanitized_id])
        
        # Check electronic music records
        try:
            from app.apis.electronic_music import get_all_music_records as get_electronic_records
            electronic_records = get_electronic_records()
            if sanitized_id in electronic_records:
                print(f"Found music record in electronic music storage: {sanitized_id}")
                return MusicResponse(**electronic_records[sanitized_id])
        except Exception as e_err:
            print(f"Error when checking electronic music storage: {str(e_err)}")
            import traceback
            print(f"Traceback from electronic check: {traceback.format_exc()}")
        
        # Not found in either location
        print(f"Music record not found in any storage location: {sanitized_id}")
        raise HTTPException(status_code=404, detail=f"Music with ID {sanitized_id} not found")
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        print(f"Error in get_music_status: {str(e)}")
        # Log detailed error for debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get music status: {str(e)}")

@router.post("/update-status/{music_id}")
def update_music_status(music_id: str, request: UpdateMusicStatusRequest, user: AuthorizedUser) -> MusicResponse:
    """Update the status of a music generation request (for testing)"""
    try:
        # Check if the record is in our storage
        records = get_all_music_records()
        if music_id in records:
            record = records[music_id]
            record["status"] = request.status
            if request.audio_url:
                record["audio_url"] = request.audio_url
            save_music_record(music_id, record)
            return MusicResponse(**record)
        
        # Otherwise check electronic music storage
        from app.apis.electronic_music import update_music_status as electronic_update_music_status
        return electronic_update_music_status(music_id, request, user)
    except Exception as e:
        print(f"Error in update_music_status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update music status: {str(e)}")

@router.get("/by-concept/{concept_id}")
def get_music_by_concept(concept_id: str, user: AuthorizedUser) -> list[MusicResponse]:
    """Get all music records for a specific concept"""
    try:
        # Get records from both storage locations and combine them
        records = get_all_music_records()
        concept_records = []
        
        # Get records from our storage
        for music_id, record in records.items():
            if record.get("concept_id") == concept_id:
                concept_records.append(MusicResponse(**record))
        
        # Get records from electronic music storage
        from app.apis.electronic_music import get_all_music_records as get_electronic_records
        electronic_records = get_electronic_records()
        for music_id, record in electronic_records.items():
            if record.get("concept_id") == concept_id:
                # Check if we already have this record
                if not any(r.music_id == music_id for r in concept_records):
                    concept_records.append(MusicResponse(**record))
        
        return concept_records
    except Exception as e:
        print(f"Error in get_music_by_concept: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get music by concept: {str(e)}")

@router.get("/by-profile/{profile_id}")
def get_music_by_profile(profile_id: str, user: AuthorizedUser) -> list[MusicResponse]:
    """Get all music records for a specific profile"""
    try:
        records = get_all_music_records()
        profile_records = []
        
        # Get records from our storage
        for music_id, record in records.items():
            concept_id = record.get("concept_id", "")
            if concept_id.startswith(f"{profile_id}:"):
                profile_records.append(MusicResponse(**record))
        
        # Get records from electronic music storage
        from app.apis.electronic_music import get_all_music_records as get_electronic_records
        electronic_records = get_electronic_records()
        for music_id, record in electronic_records.items():
            concept_id = record.get("concept_id", "")
            if concept_id.startswith(f"{profile_id}:"):
                # Check if we already have this record
                if not any(r.music_id == music_id for r in profile_records):
                    profile_records.append(MusicResponse(**record))
        
        return profile_records
    except Exception as e:
        print(f"Error in get_music_by_profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get music by profile: {str(e)}")