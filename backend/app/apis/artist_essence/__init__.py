from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.auth import AuthorizedUser
import databutton as db
import uuid
import json
from datetime import datetime
from app.env import mode, Mode
from openai import OpenAI

# Create a router
router = APIRouter()

# Models
class ArtistEssenceRequest(BaseModel):
    artist_name: str = Field(..., description="Name of the artist to analyze")
    reference_details: Optional[str] = Field(None, description="Additional details to help with artist analysis")

class ArtistEssence(BaseModel):
    artist_name: str = Field(..., description="Name of the artist")
    genre: str = Field(..., description="Primary genre of the artist")
    mood: str = Field(..., description="Overall mood or emotional quality of the artist's work")
    instrumentation: List[str] = Field(..., description="Primary instruments used by the artist")
    vocal_style: str = Field(..., description="Description of the vocal style of the artist")
    tempo: int = Field(..., description="Typical BPM (beats per minute) range")
    production_style: str = Field(..., description="Production style characteristics")
    influences: Optional[List[str]] = Field(None, description="Key musical influences")
    lyrical_themes: Optional[List[str]] = Field(None, description="Common themes in lyrics")
    visual_aesthetic: Optional[str] = Field(None, description="Visual and brand identity")
    additional_notes: Optional[str] = Field(None, description="Additional notes about the artist's style")
    created_at: str = Field(..., description="When this analysis was created")

class ArtistEssenceResponse(BaseModel):
    essence_id: str
    essence: ArtistEssence

# Reference artist database - real implementation would use a proper database or API
REFERENCE_ARTISTS = {
    "daft punk": {
        "artist_name": "Daft Punk",
        "genre": "Electronic, French House",
        "mood": "Futuristic, Energetic, Nostalgic",
        "instrumentation": ["Synthesizers", "Drum Machines", "Vocoders", "Samplers"],
        "vocal_style": "Heavily Processed, Robotic, Vocoded",
        "tempo": 120,
        "production_style": "Clean, Polished, Meticulous, Retro-Futuristic",
        "additional_notes": "Known for robot personas and fusion of disco, funk, and electronic music"
    },
    "kavinsky": {
        "artist_name": "Kavinsky",
        "genre": "Synthwave, Darksynth, Electronic",
        "mood": "Nocturnal, Brooding, Cinematic",
        "instrumentation": ["Synthesizers", "Electronic Drums", "Vintage Keyboards"],
        "vocal_style": "Deep, Processed, Sparse",
        "tempo": 100,
        "production_style": "Retro-Futuristic, 80s-Inspired, Film Noir",
        "additional_notes": "Heavily influenced by 80s film soundtracks and driving music"
    },
    "radiohead": {
        "artist_name": "Radiohead",
        "genre": "Alternative Rock, Art Rock, Experimental",
        "mood": "Melancholic, Introspective, Anxious",
        "instrumentation": ["Electric Guitar", "Bass", "Drums", "Synthesizers", "Ondes Martenot"],
        "vocal_style": "Falsetto, Emotive, Versatile",
        "tempo": 95,
        "production_style": "Layered, Atmospheric, Innovative",
        "additional_notes": "Known for constantly evolving sound and experimental approaches"
    },
    "taylor swift": {
        "artist_name": "Taylor Swift",
        "genre": "Pop, Country-Pop, Alternative",
        "mood": "Emotional, Narrative, Personal",
        "instrumentation": ["Acoustic Guitar", "Piano", "Synth-Pop Elements", "Orchestra"],
        "vocal_style": "Clear, Storytelling, Versatile Range",
        "tempo": 125,
        "production_style": "Polished, Era-Defined, Evolving",
        "additional_notes": "Known for narrative songwriting and evolution from country to pop"
    },
    "kendrick lamar": {
        "artist_name": "Kendrick Lamar",
        "genre": "Hip-Hop, Conscious Rap, Jazz Rap",
        "mood": "Introspective, Political, Storytelling",
        "instrumentation": ["Jazz Samples", "Live Instruments", "Experimental Beats"],
        "vocal_style": "Dynamic Flow, Varied Voices, Technical",
        "tempo": 90,
        "production_style": "Innovative, Layered, Jazz-Influenced",
        "additional_notes": "Known for complex narratives and social commentary"
    }
}

# Storage functions
def get_all_artist_essences():
    """Get all artist essence records from storage"""
    try:
        records = db.storage.json.get("artist_essence_records", default={})
        return records
    except Exception as e:
        print(f"Error getting artist essence records: {e}")
        return {}

def save_artist_essence(essence_id, record):
    """Save an artist essence record to storage"""
    try:
        records = get_all_artist_essences()
        records[essence_id] = record
        db.storage.json.put("artist_essence_records", records)
    except Exception as e:
        print(f"Error saving artist essence record: {e}")

# Helper functions
def extract_artist_essence_with_ai(artist_name, reference_details=None):
    """Extract the essence of an artist using OpenAI's GPT-4o-mini"""
    # Get the OpenAI API key
    api_key = db.secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    # Create a prompt for GPT-4
    system_prompt = """
    You are an expert music analyst with deep knowledge of music theory, production techniques, and artist styles across all genres and eras.
    Your task is to analyze musical artists and extract their signature style characteristics.
    Focus on extracting objective, detailed, and accurate stylistic information.
    Provide a comprehensive analysis that could guide content creation in the artist's style.
    """

    user_prompt = f"""
    I need you to analyze the musical style and essence of the artist: {artist_name}

    {f"Additional context about the artist: {reference_details}" if reference_details else ""}

    Extract the following details about the artist's signature style:
    1. Primary genre(s)
    2. Emotional mood of their work
    3. Characteristic instrumentation
    4. Vocal style (if applicable)
    5. Typical tempo range (in BPM)
    6. Production style and sonic characteristics 
    7. Key musical influences and similar artists
    8. Notable themes in their lyrical content (if applicable)
    9. Visual aesthetic and brand identity

    Format your response as a structured JSON object with the following keys:
    - artist_name: The name of the artist
    - genre: Primary genre description
    - mood: Overall mood/emotional quality
    - instrumentation: Array of primary instruments
    - vocal_style: Description of vocal approach
    - tempo: Average BPM (as a number)
    - production_style: Production characteristics
    - influences: Array of key musical influences
    - lyrical_themes: Array of common themes in lyrics
    - visual_aesthetic: Their visual/fashion style
    - additional_notes: Any other distinctive elements

    Make sure your response is valid JSON and focuses on musical characteristics that would be useful for generating content in their style.
    DO NOT INCLUDE ANY OTHER TEXT - JUST RETURN THE JSON OBJECT
    """

    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Lower temperature for more consistent results
            response_format={"type": "json_object"}  # Request JSON response
        )
        
        # Parse the response
        content = response.choices[0].message.content
        parsed_response = json.loads(content)
        
        # Add created_at timestamp
        parsed_response["created_at"] = datetime.now().isoformat()
        
        return parsed_response
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        # Check if we have a predefined reference as fallback
        normalized_name = artist_name.lower().strip()
        if normalized_name in REFERENCE_ARTISTS:
            artist_data = REFERENCE_ARTISTS[normalized_name]
            return {
                **artist_data,
                "created_at": datetime.now().isoformat()
            }
        
        # Return a fallback response
        return {
            "artist_name": artist_name,
            "genre": "Unknown",
            "mood": "Mysterious, Undefined",
            "instrumentation": ["Unknown"],
            "vocal_style": "Unknown",
            "tempo": 110,
            "production_style": "Unknown",
            "influences": ["Unknown"],
            "lyrical_themes": ["Unknown"],
            "visual_aesthetic": "Unknown",
            "additional_notes": f"Analysis failed. Using fallback. {reference_details if reference_details else ''}",
            "created_at": datetime.now().isoformat()
        }

def extract_artist_essence(artist_name, reference_details=None):
    """Extract the essence of an artist based on their name
    
    Uses AI to analyze the artist, with a fallback to reference database.
    """
    if mode == Mode.DEV and False:  # Only use reference database in development mode when testing
        # Normalize the artist name for lookup
        normalized_name = artist_name.lower().strip()
        
        # Check if we have a predefined reference
        if normalized_name in REFERENCE_ARTISTS:
            artist_data = REFERENCE_ARTISTS[normalized_name]
            return {
                **artist_data,
                "created_at": datetime.now().isoformat()
            }
        
        # For unknown artists, generate a mock essence
        return {
            "artist_name": artist_name,
            "genre": "Unknown",
            "mood": "Mysterious, Undefined",
            "instrumentation": ["Synthesizers", "Digital Instruments"],
            "vocal_style": "Unknown",
            "tempo": 110,
            "production_style": "Experimental",
            "influences": ["Unknown"],
            "lyrical_themes": ["Unknown"],
            "visual_aesthetic": "Unknown",
            "additional_notes": f"This is a generated profile for an unknown artist. {reference_details if reference_details else ''}",
            "created_at": datetime.now().isoformat()
        }
    else:
        # Use AI to extract artist essence
        return extract_artist_essence_with_ai(artist_name, reference_details)

# Routes
@router.post("/extract", summary="Extract the essence of an artist", response_model=ArtistEssenceResponse)
def extract_essence(request: ArtistEssenceRequest, user: AuthorizedUser) -> ArtistEssenceResponse:
    """Extract the musical and stylistic essence of an artist.
    
    This endpoint analyzes artist references using AI and extracts key stylistic elements
    that can be used to improve AI prompts for content generation. The analysis includes
    genre, mood, instrumentation, vocal style, tempo, production characteristics,
    influences, lyrical themes, and visual aesthetic.
    """
    try:
        # Generate a unique ID for this essence extraction
        essence_id = str(uuid.uuid4())
        
        # Extract the artist essence
        essence = extract_artist_essence(request.artist_name, request.reference_details)
        
        # Create the record
        record = {
            "essence_id": essence_id,
            "essence": essence,
            "created_at": datetime.now().isoformat(),
            "user_id": user.sub  # Store the user ID who requested this
        }
        
        # Save the record
        save_artist_essence(essence_id, record)
        
        # Return the response
        return ArtistEssenceResponse(
            essence_id=essence_id,
            essence=essence
        )
    except Exception as e:
        print(f"Error extracting artist essence: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract artist essence: {str(e)}")

@router.get("/get/{essence_id}", summary="Get a specific artist essence", response_model=ArtistEssenceResponse)
def get_artist_essence(essence_id: str, user: AuthorizedUser) -> ArtistEssenceResponse:
    """Get a specific artist essence by ID"""
    records = get_all_artist_essences()
    if essence_id not in records:
        raise HTTPException(status_code=404, detail=f"Artist essence with ID {essence_id} not found")
    
    record = records[essence_id]
    
    return ArtistEssenceResponse(
        essence_id=essence_id,
        essence=record["essence"]
    )

@router.get("/prompt/{essence_id}", summary="Get formatted prompt for Claude")
def get_prompt_format(essence_id: str, user: AuthorizedUser) -> dict:
    """Get a formatted prompt string for Claude based on the artist essence"""
    records = get_all_artist_essences()
    if essence_id not in records:
        raise HTTPException(status_code=404, detail=f"Artist essence with ID {essence_id} not found")
    
    record = records[essence_id]
    essence = record["essence"]
    
    # Format the prompt for Claude
    prompt = f"""
Artist: {essence['artist_name']}
Genre: {essence['genre']}
Mood: {essence['mood']}
Instrumentation: {', '.join(essence['instrumentation'])}
Vocal Style: {essence['vocal_style']}
Tempo: {essence['tempo']} BPM
Production Style: {essence['production_style']}
{f"Influences: {', '.join(essence['influences'])}" if essence.get('influences') else ""}
{f"Lyrical Themes: {', '.join(essence['lyrical_themes'])}" if essence.get('lyrical_themes') else ""}
{f"Visual Aesthetic: {essence['visual_aesthetic']}" if essence.get('visual_aesthetic') else ""}
{f"Notes: {essence['additional_notes']}" if essence.get('additional_notes') else ""}
    """.strip()
    
    return {
        "essence_id": essence_id,
        "formatted_prompt": prompt
    }

@router.get("/artist-essences", summary="List recent artist essences", response_model=List[ArtistEssenceResponse])
def list_artist_essences(user: AuthorizedUser) -> List[ArtistEssenceResponse]:
    """List recently created artist essences"""
    records = get_all_artist_essences()
    
    # Convert records to response model format
    essences = [
        ArtistEssenceResponse(
            essence_id=essence_id,
            essence=record["essence"]
        )
        for essence_id, record in records.items()
    ]
    
    # Sort by creation date (most recent first)
    sorted_essences = sorted(
        essences,
        key=lambda x: x.essence.created_at,
        reverse=True
    )
    
    # Return at most 10 items
    return sorted_essences[:10]
