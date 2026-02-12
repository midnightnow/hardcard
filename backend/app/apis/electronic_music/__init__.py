from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.auth import AuthorizedUser
import databutton as db
import uuid
import json
import random
from datetime import datetime
from app.env import mode, Mode
import re

# Create a router
router = APIRouter()

# Models - keep compatible with the existing suno_music API
class GenerateMusicRequest(BaseModel):
    concept_id: str
    concept_name: str
    concept_description: str
    profile_id: str = None
    photo_description: str = None
    mood: str = "contemplative"
    genre: str = "ambient"
    duration: int = 30

class MusicResponse(BaseModel):
    music_id: str
    status: str
    title: str = None
    description: str = None
    concept_id: str = None
    concept_name: str = None
    audio_url: str = None
    created_at: str = None
    metadata: dict = None

class UpdateMusicStatusRequest(BaseModel):
    status: str
    audio_url: str = None

# Helper Functions
def get_all_music_records():
    """Get all music records from storage"""
    try:
        records = db.storage.json.get("electronic_music_records", default={})
        return records
    except Exception as e:
        print(f"Error getting electronic music records: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {}
        
def get_music_record(music_id: str | None) -> dict:
    """Get an electronic music record from storage with improved validation
    
    Validates the music_id, then checks the electronic_music_records collection first,
    then tries individual record lookup as a fallback.
    """
    try:
        # Enhanced validation for the music_id parameter to prevent errors
        # Handle extreme edge cases where music_id might not be a string type or be None
        if music_id is None:
            error_msg = "Invalid music_id received in electronic_music API: None"
            print(error_msg)
            raise HTTPException(
                status_code=400, 
                detail="Invalid music ID: None provided. Must be a valid non-empty string."
            )
            
        # Safety conversion to string (important for UUID objects or non-string inputs)
        music_id_str = str(music_id)
        
        # Check for undefined, null, empty string, or whitespace
        if not music_id_str or music_id_str == "undefined" or music_id_str == "null" or music_id_str.strip() == "":
            error_msg = f"Invalid music_id received in electronic_music API: '{music_id_str}'"
            print(error_msg)
            print(f"Type of music_id: {type(music_id)}")
            print(f"Source of request: get_music_record function")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid music ID provided: '{music_id_str}'. Must be a valid non-empty string."
            )
            
        # Sanitize the music_id to prevent storage injection with improved error handling
        try:
            sanitized_id = sanitize_storage_key(music_id)
            print(f"Processing electronic music status for sanitized ID: '{sanitized_id}'")
            print(f"Looking up electronic music record: {sanitized_id}")
        except ValueError as ve:
            error_msg = f"Storage key sanitization error in get_music_record: {str(ve)}"
            print(error_msg)
            print(f"Original music_id: '{music_id}'")
            raise HTTPException(status_code=400, detail=f"Invalid music ID format: {str(ve)}") from ve
        
        # First check in the collection with detailed logging
        records = get_all_music_records()
        record_count = len(records)
        print(f"Retrieved {record_count} electronic music records for lookup")
        print(f"Checking if ID '{sanitized_id}' exists in records collection")
        
        if sanitized_id in records:
            print(f"Found electronic music record in main storage: {sanitized_id}")
            return records[sanitized_id]
        
        # Check if we have a standalone record (legacy format)
        try:
            key = f"electronic_music_{sanitized_id}"
            print(f"Checking for standalone record with key: {key}")
            record = db.storage.json.get(key)
            if record:
                print(f"Found standalone electronic music record: {sanitized_id}")
                return record
        except FileNotFoundError:
            print(f"No standalone record found: {sanitized_id}")
            pass
        
        # Not found in any location
        print(f"Electronic music record not found: {sanitized_id}")
        return None
    except Exception as e:
        print(f"Error retrieving electronic music record: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def save_music_record(music_id, record):
    """Save a music record to storage"""
    try:
        # Sanitize the music_id to prevent storage injection
        sanitized_id = sanitize_storage_key(music_id)
        print(f"Saving electronic music record with ID: {sanitized_id}")
        records = get_all_music_records()
        records[sanitized_id] = record
        db.storage.json.put("electronic_music_records", records)
    except Exception as e:
        print(f"Error saving electronic music record: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols
    
    Also validates the key is a non-empty string before sanitizing.
    """
    # Validate key is a proper string before sanitizing
    if key is None or not isinstance(key, str):
        print(f"Warning: Non-string key provided to sanitize_storage_key: {key} (type: {type(key)})")
        if key is None:
            raise ValueError("Cannot sanitize None value as storage key")
        # Try to convert to string if possible
        key = str(key)
    
    # Check for empty string after conversion
    if key.strip() == "":
        print("Warning: Empty string provided as storage key")
        raise ValueError("Cannot use empty string as storage key")
        
    # Sanitize by removing invalid characters
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', key)
    
    # Log if sanitization changed the key
    if sanitized != key:
        print(f"Sanitized storage key: '{key}' -> '{sanitized}'")
    
    return sanitized

def generate_track_title(concept_name, mood, genre):
    """Generate a creative track title based on concept, mood and genre"""
    adjectives = [
        "Eternal", "Cosmic", "Ethereal", "Digital", "Quantum", "Solar", 
        "Lunar", "Celestial", "Infinite", "Timeless", "Crystalline", "Golden",
        "Sacred", "Ancient", "Future", "Mystic", "Dream", "Virtual",
        "Neon", "Cyber", "Analog", "Synthetic", "Pulse", "Wave", "Glitch", "Vapor"
    ]
    
    nouns = [
        "Legacy", "Horizon", "Journey", "Odyssey", "Voyage", "Ascension", 
        "Genesis", "Echo", "Pulse", "Wave", "Reflection", "Dimension",
        "Realm", "Vision", "Portal", "Matrix", "Nexus", "Singularity",
        "Circuit", "Grid", "Frequency", "Transmission", "Signal", "Waveform", "Synth", "Beat"
    ]
    
    electronic_formats = [
        f"{random.choice(adjectives)} {concept_name}",
        f"{concept_name} {random.choice(nouns)}",
        f"{random.choice(adjectives)} {random.choice(nouns)}",
        f"The {random.choice(adjectives)} {concept_name}",
        f"{concept_name}'s {random.choice(nouns)}",
        f"{random.choice(adjectives)} {mood.title()} in {genre.title()}",
        f"{random.choice(adjectives)} {random.choice(nouns)} ({genre.title()})",
        f"{mood.title()} {random.choice(nouns)}",
        f"[{concept_name}] {random.choice(adjectives)} {random.choice(nouns)}"
    ]
    
    # Use different formats based on genre
    if genre.lower() in ["electronic", "techno", "ambient", "synth", "edm", "house"]:
        return random.choice(electronic_formats)
    
    # Default formats if genre is not electronic
    return f"{random.choice(adjectives)} {concept_name} ({genre.title()})"

# High-quality electronic instrumental music tracks
ELECTRONIC_MUSIC_TRACKS = {
    "ambient": [
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/ambient_01.mp3",
            "name": "Ambient Journey"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/ambient_02.mp3",
            "name": "Floating Dimensions"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/ambient_03.mp3",
            "name": "Ethereal Waves"
        }
    ],
    "electronic": [
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/electronic_01.mp3",
            "name": "Digital Pulse"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/electronic_02.mp3",
            "name": "Circuit Dreams"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/electronic_03.mp3",
            "name": "Neon Synthesis"
        }
    ],
    "techno": [
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/techno_01.mp3",
            "name": "Techno Vision"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/techno_02.mp3",
            "name": "Quantum Beats"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/techno_03.mp3",
            "name": "Hyperdrive"
        }
    ],
    "synth": [
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/synth_01.mp3",
            "name": "Synth Odyssey"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/synth_02.mp3",
            "name": "Analog Dreams"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/electronic_music/synth_03.mp3",
            "name": "Retrowave"
        }
    ],
    "default": [
        # Fallback tracks for any genre not explicitly listed
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/mcm1-Hardcard1.mp3",
            "name": "Legacy Vault Theme"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/mcm2-Legacy2.mp3",
            "name": "Digital Legacy"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/mcm3-Bitcoin3.mp3",
            "name": "Crypto Symphony"
        },
        {
            "url": "https://storage.googleapis.com/aae-dialogue-production/mcm4-Trust4.mp3",
            "name": "Trust Dynamics"
        }
    ],
}

# Map moods to musical characteristics
MOOD_CHARACTERISTICS = {
    "contemplative": "slow, ethereal, deep, thoughtful",
    "inspirational": "uplifting, building, emotional, soaring",
    "joyful": "bright, energetic, upbeat, positive",
    "melancholic": "minor key, emotional, nostalgic, introspective",
    "tense": "dissonant, suspenseful, dark, unpredictable",
    "relaxed": "smooth, flowing, gentle, calming",
    "energetic": "fast-paced, dynamic, powerful, driving",
    "mysterious": "intriguing, unusual harmonies, unexpected elements",
    "epic": "grand, orchestral elements, dramatic, powerful",
    "futuristic": "modern synthesis, innovative sounds, cutting-edge"
}

# Select an appropriate track based on genre and mood
def select_track(genre, mood):
    """Select an appropriate track based on genre and mood"""
    # Normalize genre and mood
    genre_lower = genre.lower()
    # Mood will be used in future enhancements for track selection
    # Currently only using genre for track selection
    
    # Select the track list based on genre
    if genre_lower in ELECTRONIC_MUSIC_TRACKS:
        track_list = ELECTRONIC_MUSIC_TRACKS[genre_lower]
    else:
        # Use default tracks if genre not found
        track_list = ELECTRONIC_MUSIC_TRACKS["default"]
    
    # Randomly select a track from the appropriate list
    track = random.choice(track_list)
    
    return track

# Create an enhanced music description using OpenAI if available
async def create_enhanced_description(concept_description, genre, mood, background_tasks):
    """Create an enhanced music description using OpenAI if available"""
    try:
        # Try to get the OpenAI API key
        try:
            openai_api_key = db.secrets.get("OPENAI_API_KEY")
            if not openai_api_key or openai_api_key in ["test-key", "example-key", ""]:
                return concept_description
                
            # Import OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            # Get mood characteristics
            mood_chars = MOOD_CHARACTERISTICS.get(mood.lower(), mood)
            
            # Create the prompt
            prompt = f"""Describe a {genre} instrumental music track with a {mood} ({mood_chars}) mood 
            inspired by this concept: '{concept_description}'. Include musical elements like 
            instrumentation, rhythm, melody, and progression. Keep it under a paragraph, maximum 3 sentences."""
            
            # Call OpenAI
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a music producer specializing in electronic instrumental music."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract and return the enhanced description
            enhanced_description = completion.choices[0].message.content
            return enhanced_description
            
        except Exception as e:
            print(f"Error getting OpenAI key or generating description: {e}")
            return concept_description
            
    except Exception as e:
        print(f"Error in create_enhanced_description: {e}")
        return concept_description

# Background task to process music generation asynchronously
async def process_music_generation(music_id, request):
    """Process music generation in the background
    
    This function handles the actual generation of electronic music based on
    the requested parameters and concept. It updates the status throughout the process.
    """
    try:
        # Get the record
        records = get_all_music_records()
        if music_id not in records:
            print(f"Music record {music_id} not found during background processing")
            return
            
        record = records[music_id]
        
        # Update status to processing
        record["status"] = "processing"
        save_music_record(music_id, record)
        
        # Simulate processing time (1-2 seconds)
        import asyncio
        await asyncio.sleep(random.uniform(1, 2))
        
        # Select an appropriate track based on genre and mood
        track = select_track(request.genre, request.mood)
        
        # Create an enhanced description with OpenAI if available
        enhanced_description = await create_enhanced_description(
            request.concept_description, 
            request.genre, 
            request.mood,
            None
        )
        
        # Update the record with the track and description
        record["status"] = "completed"
        record["audio_url"] = track["url"]
        record["description"] = enhanced_description
        record["completed_at"] = datetime.now().isoformat()
        record["metadata"]["track_name"] = track["name"]
        record["metadata"]["enhanced_description"] = enhanced_description
        
        # Save the updated record
        save_music_record(music_id, record)
        print(f"Music generation completed for {music_id}")
            
    except Exception as e:
        print(f"Error in process_music_generation: {e}")
        # Update record to failed status
        try:
            record = records.get(music_id)
            if record:
                record["status"] = "failed"
                record["error"] = str(e)
                save_music_record(music_id, record)
        except Exception as inner_e:
            print(f"Error updating failed record: {inner_e}")

# Routes
@router.post("/electronic/generate-music")
async def generate_electronic_music(request: GenerateMusicRequest, background_tasks: BackgroundTasks, user: AuthorizedUser) -> MusicResponse:
    """Generate electronic instrumental music for a vault concept
    
    This endpoint generates high-quality electronic instrumental music based on concept, 
    mood, and genre parameters. It selects from a curated library of professionally produced
    tracks and enhances the description using AI to match the requested characteristics.
    """
    try:
        # Generate a unique ID for this music request
        music_id = str(uuid.uuid4())
        
        # Generate a creative track title
        title = generate_track_title(request.concept_name, request.mood, request.genre)
        
        # Create initial record
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
        
        # Save the initial record
        save_music_record(music_id, record)
        
        # Start background processing
        background_tasks.add_task(process_music_generation, music_id, request)
        
        print(f"Started music generation task for {music_id}")
        return MusicResponse(**record)
    
    except Exception as e:
        print(f"Error generating music: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate music: {str(e)}")

@router.get("/electronic/status/{music_id}")
def get_music_status2(music_id: str | None, user: AuthorizedUser) -> MusicResponse:
    """Get the status of a music generation request
    
    This endpoint checks both storage locations for the requested music record.
    """
    # First validate the input - with comprehensive checks
    print(f"Received electronic music status request with ID: '{music_id}'")
    print(f"User ID: {user.sub}")
    print(f"Request path parameter type: {type(music_id)}")
    
    # Handle edge case where music_id might be None
    if music_id is None:
        error_msg = "Invalid music_id received in get_music_status: None"
        print(error_msg)
        raise HTTPException(
            status_code=400, 
            detail="Invalid music ID: None provided. Must be a valid non-empty string."
        )
        
    # Safety conversion to string for non-string inputs
    music_id_str = str(music_id)
    
    # Explicit validation before any processing
    if not music_id_str or music_id_str == "undefined" or music_id_str == "null" or music_id_str.strip() == "":
        error_msg = f"Invalid music_id received in get_music_status: '{music_id_str}'"
        print(error_msg)
        print(f"Type of original music_id: {type(music_id)}")
        print(f"Source of request: get_music_status endpoint")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid music ID provided: '{music_id_str}'. Must be a valid non-empty string."
        )
    
    try:
        # Sanitize the music_id to prevent storage injection - with enhanced error handling
        try:
            sanitized_id = sanitize_storage_key(music_id)
            print(f"Checking status for electronic music ID: {sanitized_id}")
        except ValueError as ve:
            print(f"Storage key sanitization error: {str(ve)}")
            raise HTTPException(status_code=400, detail=f"Invalid music ID format: {str(ve)}") from ve
        
        # Try to get the record from our storage
        record = get_music_record(sanitized_id)
        
        if not record:
            # Also check the suno_music storage as a fallback
            try:
                from app.apis.suno_music import get_all_music_records as get_suno_records
                suno_records = get_suno_records()
                if sanitized_id in suno_records:
                    print(f"Found music record in suno storage: {sanitized_id}")
                    record = suno_records[sanitized_id]
            except Exception as e_err:
                print(f"Error when checking suno_music storage: {str(e_err)}")
                # Continue with normal flow rather than raising an exception here
        
        # If record is still not found in either location, return 404
        if not record:
            print(f"Music record not found in any storage location: {sanitized_id}")
            raise HTTPException(status_code=404, detail=f"Music with ID {sanitized_id} not found")
        
        print(f"Returning music record with status: {record.get('status')}")
        return MusicResponse(**record)
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        print(f"Error in get_music_status: {str(e)}")
        # Log detailed error for debugging
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to get music status: {str(e)}") from e

@router.post("/electronic/update-status/{music_id}")
def update_music_status2(music_id: str | None, request: UpdateMusicStatusRequest, user: AuthorizedUser) -> MusicResponse:
    """Update the status of a music generation request (for testing)
    
    This endpoint is primarily for testing and manual updates.
    """
    # Log the request details with enhanced logging
    print(f"Received update status request for music ID: '{music_id}'")
    print(f"New status: {request.status}")
    print(f"Audio URL provided: {True if request.audio_url else False}")
    print(f"Request path parameter type: {type(music_id)}")
    
    # Handle edge case where music_id might be None (shouldn't happen with FastAPI but being thorough)
    if music_id is None:
        error_msg = "Invalid music_id received in update_music_status: None"
        print(error_msg)
        raise HTTPException(
            status_code=400, 
            detail="Invalid music ID: None provided. Must be a valid non-empty string."
        )
        
    # Safety conversion to string for non-string inputs
    music_id_str = str(music_id)
    
    # Comprehensive validation before any processing
    if not music_id_str or music_id_str == "undefined" or music_id_str == "null" or music_id_str.strip() == "":
        error_msg = f"Invalid music_id received in update_music_status: '{music_id_str}'"
        print(error_msg)
        print(f"Type of original music_id: {type(music_id)}")
        print(f"Source of request: update_music_status endpoint")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid music ID provided: '{music_id_str}'. Must be a valid non-empty string."
        )
    
    try:
        # Sanitize the music_id to prevent storage injection - with enhanced error handling
        try:
            sanitized_id = sanitize_storage_key(music_id)
            print(f"Using sanitized music ID: '{sanitized_id}'")
        except ValueError as ve:
            print(f"Storage key sanitization error: {str(ve)}")
            raise HTTPException(status_code=400, detail=f"Invalid music ID format: {str(ve)}") from ve
        
        # Keep track if sanitization changed the ID
        if sanitized_id != music_id:
            print(f"Sanitized music_id in update_music_status: '{music_id}' -> '{sanitized_id}'")
            music_id = sanitized_id
        
        # Get all records
        records = get_all_music_records()
        
        # Check if the record exists
        if music_id not in records:
            print(f"Music record not found in update_music_status: '{music_id}'")
            raise HTTPException(status_code=404, detail=f"Music with ID {music_id} not found")
        
        record = records[music_id]
        print(f"Found music record with current status: {record.get('status')}")
        
        # Update the status
        record["status"] = request.status
        print(f"Updated status to: {request.status}")
        
        # If audio URL is provided, update it
        if request.audio_url:
            record["audio_url"] = request.audio_url
            print(f"Updated audio URL to: {request.audio_url}")
        
        # Add timestamp for the update
        record["updated_at"] = datetime.now().isoformat()
        
        # Save the updated record
        print("Saving updated record")
        save_music_record(music_id, record)
        
        print("Successfully updated music record status")
        return MusicResponse(**record)
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        print(f"Error in update_music_status: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to update music status: {str(e)}") from e

@router.get("/electronic/by-concept/{concept_id}")
def get_music_by_concept2(concept_id: str, user: AuthorizedUser) -> list[MusicResponse]:
    """Get all music records for a specific concept"""
    records = get_all_music_records()
    
    # Filter records by concept ID
    concept_records = []
    for music_id, record in records.items():
        if record.get("concept_id") == concept_id:
            concept_records.append(MusicResponse(**record))
    
    return concept_records

@router.get("/electronic/by-profile/{profile_id}")
def get_music_by_profile2(profile_id: str, user: AuthorizedUser) -> list[MusicResponse]:
    """Get all music records for a specific profile"""
    records = get_all_music_records()
    
    # Filter records by profile ID (match by prefix in the concept_id)
    profile_records = []
    for music_id, record in records.items():
        concept_id = record.get("concept_id", "")
        if concept_id.startswith(f"{profile_id}:"):
            profile_records.append(MusicResponse(**record))
    
    return profile_records
