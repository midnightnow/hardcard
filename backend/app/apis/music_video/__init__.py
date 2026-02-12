from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from app.auth import AuthorizedUser
import databutton as db
import uuid
import json
from datetime import datetime
import time
import re
from typing import List, Optional, Dict, Any
from app.env import mode, Mode

# Import existing APIs we'll leverage
try:
    from app.apis.suno_music import generate_music, GenerateMusicRequest
except ImportError:
    print("Warning: suno_music API not found. Music generation will be mocked.")
    generate_music = None
    
# Create a router
router = APIRouter()

# Models
class GenerationStep(BaseModel):
    """Represents a step in the music video generation process"""
    name: str
    status: str = "pending"  # pending, in_progress, completed, failed
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class MusicVideoRequest(BaseModel):
    """Request model for generating a music video"""
    prompt: str = Field(..., description="The creative prompt for generating the music video")
    title: Optional[str] = Field(None, description="Optional title for the music video")
    duration: int = Field(30, description="Desired duration in seconds (max 60)")
    style: Optional[str] = Field(None, description="Optional style direction")
    profile_id: Optional[str] = Field(None, description="Optional profile ID for tracking")
    optimize_for_m4: bool = Field(True, description="Whether to optimize memory usage for M4 Mac")
    mode: str = Field("autonomous", description="Generation mode: autonomous, human-in-loop, or supervised")

class MusicVideoResponse(BaseModel):
    """Response model for music video generation"""
    video_id: str
    title: str
    status: str  # overall status: pending, in_progress, completed, failed
    prompt: str
    created_at: str
    steps: List[GenerationStep]
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    lyrics: Optional[str] = None
    music_id: Optional[str] = None
    assets: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MusicVideoStatusRequest(BaseModel):
    """Request model for updating music video status"""
    status: str
    step_name: Optional[str] = None
    step_status: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    assets: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AssetUsageReport(BaseModel):
    """Report on creative asset usage and costs"""
    profile_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    asset_types: List[str] = ["music", "visuals", "animation", "video"]

class AssetUsageResponse(BaseModel):
    """Response with asset usage data"""
    report_id: str
    profile_id: Optional[str]
    period: Dict[str, str]
    summary: Dict[str, Any]
    details: Dict[str, List[Dict[str, Any]]]
    estimated_costs: Dict[str, float]
    report_url: Optional[str] = None

# Helper Functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_all_music_videos():
    """Get all music video records from storage"""
    try:
        records = db.storage.json.get("music_video_records", default={})
        return records
    except Exception as e:
        print(f"Error getting music video records: {e}")
        return {}

def save_music_video_record(video_id, record):
    """Save a music video record to storage"""
    try:
        records = get_all_music_videos()
        records[video_id] = record
        db.storage.json.put("music_video_records", records)
    except Exception as e:
        print(f"Error saving music video record: {e}")

def generate_title_from_prompt(prompt: str) -> str:
    """Generate a title from the prompt if none is provided"""
    if len(prompt) <= 40:
        return prompt
    
    # Extract first sentence or first 40 chars
    first_sentence = prompt.split(".")[0].strip()
    if len(first_sentence) <= 40:
        return first_sentence
    return first_sentence[:37] + "..."

# Background task for music video generation pipeline
async def generate_music_video_pipeline(video_id: str, request: MusicVideoRequest):
    """Background task to run the full music video generation pipeline"""
    try:
        records = get_all_music_videos()
        if video_id not in records:
            print(f"Video ID {video_id} not found in records")
            return
            
        record = records[video_id]
        steps = record["steps"]
        
        # Update overall status to in_progress
        record["status"] = "in_progress"
        save_music_video_record(video_id, record)
        
        # Step 1: Lyrics Generation with Claude
        lyrics_step = next((s for s in steps if s["name"] == "lyrics_generation"), None)
        if lyrics_step:
            lyrics_step["status"] = "in_progress"
            lyrics_step["start_time"] = datetime.now().isoformat()
            save_music_video_record(video_id, record)
            
            try:
                # In a real implementation, call Claude API here
                # For now, mock the lyrics generation
                time.sleep(2)  # Simulate API call time
                
                # Mock lyrics based on prompt
                words = request.prompt.split()
                chorus = " ".join(words[:min(len(words), 6)])
                mock_lyrics = f"Verse 1:\n{request.prompt}\n\nChorus:\n{chorus}, {chorus}\n\nVerse 2:\nContinuing the journey through time\nBuilding a legacy that will shine"
                
                lyrics_step["status"] = "completed"
                lyrics_step["end_time"] = datetime.now().isoformat()
                lyrics_step["result"] = {"lyrics": mock_lyrics}
                record["lyrics"] = mock_lyrics
                save_music_video_record(video_id, record)
            except Exception as e:
                lyrics_step["status"] = "failed"
                lyrics_step["end_time"] = datetime.now().isoformat()
                lyrics_step["error"] = str(e)
                save_music_video_record(video_id, record)
                raise e
        
        # Step 2: Music Generation with Suno
        music_step = next((s for s in steps if s["name"] == "music_generation"), None)
        if music_step:
            music_step["status"] = "in_progress"
            music_step["start_time"] = datetime.now().isoformat()
            save_music_video_record(video_id, record)
            
            try:
                if generate_music:
                    # Use real Suno API if available
                    music_request = GenerateMusicRequest(
                        concept_id=f"musicvideo_{video_id}",
                        concept_name=record["title"],
                        concept_description=f"Music video soundtrack for: {request.prompt}",
                        profile_id=request.profile_id,
                        mood=determine_mood_from_prompt(request.prompt),
                        genre=determine_genre_from_prompt(request.prompt),
                        duration=min(request.duration, 60)
                    )
                    
                    # Generate music
                    music_response = generate_music(music_request, None)  # Pass None as user for testing
                    
                    music_step["status"] = "completed"
                    music_step["end_time"] = datetime.now().isoformat()
                    music_step["result"] = {"music_id": music_response.music_id, "audio_url": music_response.audio_url}
                    record["music_id"] = music_response.music_id
                    if record.get("assets") is None:
                        record["assets"] = {}
                    record["assets"]["music"] = {"id": music_response.music_id, "url": music_response.audio_url}
                else:
                    # Mock music generation
                    time.sleep(3)  # Simulate API call time
                    mock_music_id = f"mock-music-{video_id}"
                    mock_audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
                    
                    music_step["status"] = "completed"
                    music_step["end_time"] = datetime.now().isoformat()
                    music_step["result"] = {"music_id": mock_music_id, "audio_url": mock_audio_url}
                    record["music_id"] = mock_music_id
                    if record.get("assets") is None:
                        record["assets"] = {}
                    record["assets"]["music"] = {"id": mock_music_id, "url": mock_audio_url}
                
                save_music_video_record(video_id, record)
            except Exception as e:
                music_step["status"] = "failed"
                music_step["end_time"] = datetime.now().isoformat()
                music_step["error"] = str(e)
                save_music_video_record(video_id, record)
                raise e
        
        # Step 3: Visual Generation with Flux AI
        visual_step = next((s for s in steps if s["name"] == "visual_generation"), None)
        if visual_step:
            visual_step["status"] = "in_progress"
            visual_step["start_time"] = datetime.now().isoformat()
            save_music_video_record(video_id, record)
            
            try:
                # In a real implementation, call Flux AI API here
                # For now, mock the visual generation
                time.sleep(4)  # Simulate API call time
                
                # Mock visuals based on prompt
                mock_visual_id = f"flux-{video_id}"
                mock_images = [
                    f"https://source.unsplash.com/random/1280x720/?{request.prompt.split()[0]},abstract",
                    f"https://source.unsplash.com/random/1280x720/?{request.prompt.split()[1] if len(request.prompt.split()) > 1 else 'music'},visual"
                ]
                
                visual_step["status"] = "completed"
                visual_step["end_time"] = datetime.now().isoformat()
                visual_step["result"] = {"visual_id": mock_visual_id, "images": mock_images}
                if record.get("assets") is None:
                    record["assets"] = {}
                record["assets"]["visuals"] = {"id": mock_visual_id, "urls": mock_images}
                record["thumbnail_url"] = mock_images[0]  # Use first image as thumbnail
                save_music_video_record(video_id, record)
            except Exception as e:
                visual_step["status"] = "failed"
                visual_step["end_time"] = datetime.now().isoformat()
                visual_step["error"] = str(e)
                save_music_video_record(video_id, record)
                raise e
        
        # Step 4: Animation Creation with Kling AI
        animation_step = next((s for s in steps if s["name"] == "animation_creation"), None)
        if animation_step:
            animation_step["status"] = "in_progress"
            animation_step["start_time"] = datetime.now().isoformat()
            save_music_video_record(video_id, record)
            
            try:
                # In a real implementation, call Kling AI API here
                # For now, mock the animation creation
                time.sleep(5)  # Simulate API call time
                
                # Mock animation based on prompt and visuals
                mock_animation_id = f"kling-{video_id}"
                mock_animation_url = f"https://example.com/mock-animation-{video_id}.mp4"
                
                animation_step["status"] = "completed"
                animation_step["end_time"] = datetime.now().isoformat()
                animation_step["result"] = {"animation_id": mock_animation_id, "animation_url": mock_animation_url}
                if record.get("assets") is None:
                    record["assets"] = {}
                record["assets"]["animation"] = {"id": mock_animation_id, "url": mock_animation_url}
                save_music_video_record(video_id, record)
            except Exception as e:
                animation_step["status"] = "failed"
                animation_step["end_time"] = datetime.now().isoformat()
                animation_step["error"] = str(e)
                save_music_video_record(video_id, record)
                raise e
        
        # Step 5: Video Editing and Composition with Veed
        video_step = next((s for s in steps if s["name"] == "video_editing"), None)
        if video_step:
            video_step["status"] = "in_progress"
            video_step["start_time"] = datetime.now().isoformat()
            save_music_video_record(video_id, record)
            
            try:
                # In a real implementation, call Veed API here
                # For now, mock the video editing
                time.sleep(6)  # Simulate API call time
                
                # Mock video editing and composition
                mock_video_id = f"veed-{video_id}"
                mock_video_url = f"https://example.com/mock-video-{video_id}.mp4"
                
                video_step["status"] = "completed"
                video_step["end_time"] = datetime.now().isoformat()
                video_step["result"] = {"video_id": mock_video_id, "video_url": mock_video_url}
                if record.get("assets") is None:
                    record["assets"] = {}
                record["assets"]["video"] = {"id": mock_video_id, "url": mock_video_url}
                record["video_url"] = mock_video_url
                save_music_video_record(video_id, record)
            except Exception as e:
                video_step["status"] = "failed"
                video_step["end_time"] = datetime.now().isoformat()
                video_step["error"] = str(e)
                save_music_video_record(video_id, record)
                raise e
        
        # Final status update
        record["status"] = "completed"
        save_music_video_record(video_id, record)
        
        # Track asset usage for reporting
        try:
            asset_usage = db.storage.json.get("music_video_asset_usage", default=[])
            asset_usage.append({
                "video_id": video_id,
                "profile_id": request.profile_id,
                "created_at": datetime.now().isoformat(),
                "assets": record.get("assets", {}),
                "metadata": {
                    "title": record["title"],
                    "prompt": record["prompt"],
                    "duration": request.duration,
                    "optimize_for_m4": request.optimize_for_m4,
                    "mode": request.mode
                }
            })
            db.storage.json.put("music_video_asset_usage", asset_usage)
        except Exception as e:
            print(f"Error tracking asset usage: {e}")
    
    except Exception as e:
        print(f"Error in music video generation pipeline: {e}")
        # Update record with failure status
        try:
            records = get_all_music_videos()
            if video_id in records:
                record = records[video_id]
                record["status"] = "failed"
                # Update the current step if any is in progress
                for step in record["steps"]:
                    if step["status"] == "in_progress":
                        step["status"] = "failed"
                        step["end_time"] = datetime.now().isoformat()
                        step["error"] = str(e)
                save_music_video_record(video_id, record)
        except Exception as inner_e:
            print(f"Error updating failure status: {inner_e}")

def determine_mood_from_prompt(prompt: str) -> str:
    """Determine appropriate mood from prompt"""
    # Simplified mood detection based on keywords
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["happy", "joyful", "celebrat", "excit", "fun"]):
        return "joyful"
    elif any(word in prompt_lower for word in ["sad", "melanchol", "depress", "sorrow"]):
        return "melancholic"
    elif any(word in prompt_lower for word in ["intense", "power", "epic", "drama"]):
        return "intense"
    elif any(word in prompt_lower for word in ["relax", "calm", "peace", "tranquil"]):
        return "relaxed"
    elif any(word in prompt_lower for word in ["mystic", "wonder", "magic", "fantasy"]):
        return "mystical"
    return "contemplative"  # Default mood

def determine_genre_from_prompt(prompt: str) -> str:
    """Determine appropriate genre from prompt"""
    # Simplified genre detection based on keywords
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["rock", "guitar", "band", "electric"]):
        return "rock"
    elif any(word in prompt_lower for word in ["pop", "mainstream", "catchy"]):
        return "pop"
    elif any(word in prompt_lower for word in ["classic", "orchestra", "symphony", "piano"]):
        return "classical"
    elif any(word in prompt_lower for word in ["electronic", "techno", "synth", "beat"]):
        return "electronic"
    elif any(word in prompt_lower for word in ["ambient", "atmosphere", "background"]):
        return "ambient"
    elif any(word in prompt_lower for word in ["cinematic", "film", "movie", "score"]):
        return "cinematic"
    return "pop"  # Default genre

# Routes
@router.post("/generate")
def generate_music_video(request: MusicVideoRequest, background_tasks: BackgroundTasks, user: AuthorizedUser) -> MusicVideoResponse:
    """Generate a music video from a text prompt using multiple AI services"""
    try:
        # Generate a unique ID for this music video
        video_id = str(uuid.uuid4())
        
        # Use provided title or generate one from the prompt
        title = request.title if request.title else generate_title_from_prompt(request.prompt)
        
        # Define the generation steps
        steps = [
            GenerationStep(name="lyrics_generation", status="pending"),
            GenerationStep(name="music_generation", status="pending"),
            GenerationStep(name="visual_generation", status="pending"),
            GenerationStep(name="animation_creation", status="pending"),
            GenerationStep(name="video_editing", status="pending")
        ]
        
        # Create initial record
        record = {
            "video_id": video_id,
            "title": title,
            "status": "pending",
            "prompt": request.prompt,
            "created_at": datetime.now().isoformat(),
            "steps": [step.dict() for step in steps],
            "mode": request.mode,
            "metadata": {
                "optimization": {
                    "for_m4": request.optimize_for_m4,
                    "memory_target": "16GB" if request.optimize_for_m4 else "32GB+"
                },
                "requested_duration": request.duration,
                "style": request.style,
                "profile_id": request.profile_id
            }
        }
        
        # Save the initial record
        save_music_video_record(video_id, record)
        
        # Start the background generation pipeline
        background_tasks.add_task(generate_music_video_pipeline, video_id, request)
        
        return MusicVideoResponse(**record)
    except Exception as e:
        print(f"Error initiating music video generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate music video generation: {str(e)}")

@router.get("/status/{video_id}")
def get_music_video_status(video_id: str, user: AuthorizedUser) -> MusicVideoResponse:
    """Get the status of a music video generation request"""
    records = get_all_music_videos()
    if video_id not in records:
        raise HTTPException(status_code=404, detail=f"Music video with ID {video_id} not found")
    
    record = records[video_id]
    return MusicVideoResponse(**record)

@router.post("/update-status/{video_id}")
def update_music_video_status(video_id: str, request: MusicVideoStatusRequest, user: AuthorizedUser) -> MusicVideoResponse:
    """Update the status of a music video generation request
    
    This endpoint is primarily for testing and manual updates.
    """
    records = get_all_music_videos()
    if video_id not in records:
        raise HTTPException(status_code=404, detail=f"Music video with ID {video_id} not found")
    
    record = records[video_id]
    
    # Update overall status if provided
    if request.status:
        record["status"] = request.status
    
    # Update specific step if provided
    if request.step_name and request.step_status:
        for step in record["steps"]:
            if step["name"] == request.step_name:
                step["status"] = request.step_status
                if request.step_status == "in_progress" and not step.get("start_time"):
                    step["start_time"] = datetime.now().isoformat()
                elif request.step_status in ["completed", "failed"] and not step.get("end_time"):
                    step["end_time"] = datetime.now().isoformat()
    
    # Update video URL if provided
    if request.video_url:
        record["video_url"] = request.video_url
    
    # Update thumbnail URL if provided
    if request.thumbnail_url:
        record["thumbnail_url"] = request.thumbnail_url
    
    # Update assets if provided
    if request.assets:
        if record.get("assets") is None:
            record["assets"] = {}
        record["assets"].update(request.assets)
    
    # Update metadata if provided
    if request.metadata:
        if record.get("metadata") is None:
            record["metadata"] = {}
        record["metadata"].update(request.metadata)
    
    # Save the updated record
    save_music_video_record(video_id, record)
    
    return MusicVideoResponse(**record)

@router.get("/videos-by-profile/{profile_id}")
def get_music_videos_by_profile(profile_id: str, user: AuthorizedUser) -> list[MusicVideoResponse]:
    """Get all music videos for a specific profile"""
    records = get_all_music_videos()
    
    # Filter records by profile ID
    profile_records = []
    for video_id, record in records.items():
        metadata = record.get("metadata", {})
        if metadata.get("profile_id") == profile_id:
            profile_records.append(MusicVideoResponse(**record))
    
    return profile_records

@router.post("/asset-report")
def generate_asset_report(request: AssetUsageReport, user: AuthorizedUser) -> AssetUsageResponse:
    """Generate a report on creative asset usage and costs"""
    try:
        report_id = str(uuid.uuid4())
        
        # Get all music video asset usage records
        try:
            asset_usage = db.storage.json.get("music_video_asset_usage", default=[])
        except Exception:
            asset_usage = []
        
        # Filter by profile ID if provided
        if request.profile_id:
            asset_usage = [record for record in asset_usage if record.get("profile_id") == request.profile_id]
        
        # Filter by date range if provided
        if request.start_date and request.end_date:
            asset_usage = [
                record for record in asset_usage 
                if record.get("created_at", "") >= request.start_date and record.get("created_at", "") <= request.end_date
            ]
        
        # Calculate summary statistics
        summary = {
            "total_videos": len(asset_usage),
            "total_duration": sum(record.get("metadata", {}).get("duration", 0) for record in asset_usage),
            "asset_counts": {
                "music": sum(1 for record in asset_usage if record.get("assets", {}).get("music")),
                "visuals": sum(1 for record in asset_usage if record.get("assets", {}).get("visuals")),
                "animation": sum(1 for record in asset_usage if record.get("assets", {}).get("animation")),
                "video": sum(1 for record in asset_usage if record.get("assets", {}).get("video"))
            }
        }
        
        # Compile details for each asset type
        details = {
            "music": [
                {
                    "video_id": record.get("video_id"),
                    "title": record.get("metadata", {}).get("title"),
                    "created_at": record.get("created_at"),
                    "asset_id": record.get("assets", {}).get("music", {}).get("id")
                }
                for record in asset_usage if record.get("assets", {}).get("music")
            ],
            "visuals": [
                {
                    "video_id": record.get("video_id"),
                    "title": record.get("metadata", {}).get("title"),
                    "created_at": record.get("created_at"),
                    "asset_id": record.get("assets", {}).get("visuals", {}).get("id")
                }
                for record in asset_usage if record.get("assets", {}).get("visuals")
            ],
            "animation": [
                {
                    "video_id": record.get("video_id"),
                    "title": record.get("metadata", {}).get("title"),
                    "created_at": record.get("created_at"),
                    "asset_id": record.get("assets", {}).get("animation", {}).get("id")
                }
                for record in asset_usage if record.get("assets", {}).get("animation")
            ],
            "video": [
                {
                    "video_id": record.get("video_id"),
                    "title": record.get("metadata", {}).get("title"),
                    "created_at": record.get("created_at"),
                    "asset_id": record.get("assets", {}).get("video", {}).get("id")
                }
                for record in asset_usage if record.get("assets", {}).get("video")
            ]
        }
        
        # Estimate costs based on usage
        # These are placeholder values; real implementation would use actual pricing
        estimated_costs = {
            "music": summary["asset_counts"]["music"] * 0.10,  # $0.10 per music generation
            "visuals": summary["asset_counts"]["visuals"] * 0.05,  # $0.05 per visual generation
            "animation": summary["asset_counts"]["animation"] * 0.15,  # $0.15 per animation
            "video": summary["asset_counts"]["video"] * 0.20,  # $0.20 per video editing
            "total": sum([
                summary["asset_counts"]["music"] * 0.10,
                summary["asset_counts"]["visuals"] * 0.05,
                summary["asset_counts"]["animation"] * 0.15,
                summary["asset_counts"]["video"] * 0.20
            ])
        }
        
        # Generate and store a PDF report (in a real implementation)
        # For now, we'll just return the report data
        response = {
            "report_id": report_id,
            "profile_id": request.profile_id,
            "period": {
                "start": request.start_date or "all",
                "end": request.end_date or "all"
            },
            "summary": summary,
            "details": details,
            "estimated_costs": estimated_costs,
            "report_url": None  # In a real implementation, this would be a URL to a PDF report
        }
        
        return AssetUsageResponse(**response)
    except Exception as e:
        print(f"Error generating asset report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate asset report: {str(e)}")
