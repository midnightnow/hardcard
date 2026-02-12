from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import databutton as db
import uuid
import json
import os
import time
import re
from fastapi import File, Form, UploadFile

# Import models from remix_engine to avoid circular imports
from app.apis.remix_engine import TrackSource, RemixSettings, TrackAnalysis

# Router Configuration
router = APIRouter(prefix="/remix-node")

# Additional models we still need - remove TrackAnalysis since we now import it

class RemixRequest(BaseModel):
    track_sources: List[TrackSource]
    settings: RemixSettings
    project_name: Optional[str] = None

class RemixResponse(BaseModel):
    remix_id: str
    status: str
    message: Optional[str] = None

class RemixStatusResponse(BaseModel):
    remix_id: str
    status: str  # "processing", "complete", "failed"
    progress: Optional[float] = None
    error: Optional[str] = None
    result_url: Optional[str] = None
    track_analysis: Optional[List[TrackAnalysis]] = None

# Utility Functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_remix_storage_key(remix_id: str) -> str:
    """Get the sanitized storage key for a remix"""
    return f"remix_{sanitize_storage_key(remix_id)}"

# Import AudioAnalyzer instance conditionally to avoid circular imports
def get_audio_analyzer():
    from app.apis.remix_analyzer import AudioAnalyzer
    return AudioAnalyzer()

@router.post("/analyze-tracks")
async def analyze_tracks(request: List[TrackSource]) -> List[TrackAnalysis]:
    """Analyze multiple audio tracks to determine key, tempo, and compatibility"""
    # This endpoint is now deprecated - use analyze_multiple_tracks instead
    return await analyze_multiple_tracks(request)

@router.post("/analyze-multiple-tracks")
async def analyze_multiple_tracks(request: List[TrackSource]) -> List[TrackAnalysis]:
    """Analyze multiple audio tracks to determine key, tempo, and compatibility"""
    analyzer = get_audio_analyzer()
    results = []
    
    for track in request:
        try:
            # Get audio file from the source
            if track.source_type == "vault" and track.id:
                # Fetch from Vault storage
                try:
                    # Just validate it exists, analyzer will handle retrieval
                    db.storage.binary.get(track.id)
                except Exception as e:
                    results.append(TrackAnalysis(
                        id=track.id,
                        error=f"Failed to retrieve audio from vault: {str(e)}"
                    ))
                    continue
            elif track.source_type == "url" and track.url:
                # We'll implement URL fetching in the analyzer
                pass
            elif track.source_type == "suno" and track.id:
                # Fetch from Suno via brain client 
                # (This would be implemented separately)
                pass
            
            # Analyze the track
            analysis = analyzer.analyze_track(track)
            results.append(analysis)
            
        except Exception as e:
            # Log the error and return it in the response
            print(f"Error analyzing track {track.id}: {str(e)}")
            results.append(TrackAnalysis(
                id=track.id,
                error=f"Analysis failed: {str(e)}"
            ))
    
    return results

@router.post("/upload-audio")
async def upload_audio_file(file: UploadFile, filename: str = Form()):
    """Upload an audio file for remixing
    
    This endpoint accepts audio files and stores them in the Databutton binary storage.
    Returns a file ID that can be used with the remix API endpoints.
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Generate a unique ID for this file
        file_id = f"remix_audio_{sanitize_storage_key(str(uuid.uuid4()))}"
        
        # Store the file in DB storage
        db.storage.binary.put(file_id, file_content)
        
        # Return the file ID to be used with the remix API
        return {
            "file_id": file_id,
            "filename": filename,
            "size": len(file_content),
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/remix", response_model=RemixResponse)
async def create_remix(request: RemixRequest, background_tasks: BackgroundTasks) -> RemixResponse:
    """Create a remix from multiple audio tracks with specified settings"""
    # Generate a unique ID for this remix
    remix_id = str(uuid.uuid4())

    # Store the request in DB storage for background processing
    storage_key = get_remix_storage_key(remix_id)

    # Initialize the remix record with 'processing' status
    remix_data = {
        "remix_id": remix_id,
        "status": "processing",
        "created_at": time.time(),
        "track_sources": [source.dict() for source in request.track_sources],
        "settings": request.settings.dict(),
        "project_name": request.project_name or f"Remix {remix_id[:8]}"
    }

    # Save to DB storage
    db.storage.json.put(storage_key, remix_data)

    # Add task to background queue
    background_tasks.add_task(process_remix, remix_id, request)

    return RemixResponse(
        remix_id=remix_id,
        status="processing",
        message="Remix creation started in the background."
    )

@router.get("/status/{remix_id}", response_model=RemixStatusResponse)
async def get_remix_status(remix_id: str) -> RemixStatusResponse:
    """Get the status of a remix in progress or completed"""
    try:
        storage_key = get_remix_storage_key(remix_id)
        remix_data = db.storage.json.get(storage_key)

        if not remix_data:
            raise HTTPException(status_code=404, detail=f"Remix with ID {remix_id} not found")

        return RemixStatusResponse(
            remix_id=remix_id,
            status=remix_data.get("status", "unknown"),
            progress=remix_data.get("progress"),
            error=remix_data.get("error"),
            result_url=remix_data.get("result_url"),
            track_analysis=remix_data.get("track_analysis")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving remix status: {str(e)}")

@router.get("/download/{remix_id}")
async def download_remix(remix_id: str):
    """Get the result file of a completed remix"""
    try:
        storage_key = get_remix_storage_key(remix_id)
        remix_data = db.storage.json.get(storage_key)

        if not remix_data or remix_data.get("status") != "complete":
            raise HTTPException(status_code=404, detail=f"Completed remix with ID {remix_id} not found")

        # Get the audio file binary data
        audio_key = f"remix_audio_{sanitize_storage_key(remix_id)}"
        try:
            audio_data = db.storage.binary.get(audio_key)
            # Return the audio file
            return audio_data
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Remix audio file not found: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving remix audio: {str(e)}")

@router.get("/list")
async def list_remixes():
    """List all remixes created by the user"""
    try:
        # List all remix files in the storage
        all_files = db.storage.json.list()
        remix_files = [file for file in all_files if file.name.startswith("remix_")]  

        results = []
        for file in remix_files:
            try:
                remix_data = db.storage.json.get(file.name)
                if remix_data and isinstance(remix_data, dict):
                    results.append({
                        "remix_id": remix_data.get("remix_id"),
                        "project_name": remix_data.get("project_name"),
                        "status": remix_data.get("status"),
                        "created_at": remix_data.get("created_at"),
                        "result_url": remix_data.get("result_url") if remix_data.get("status") == "complete" else None
                    })
            except Exception as e:
                # Skip files that cannot be read
                print(f"Error reading remix file {file.name}: {str(e)}")
                continue

        # Sort by created_at (newest first)
        results.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing remixes: {str(e)}")

# Background Processing Function (called by FastAPI background tasks)
async def process_remix(remix_id: str, request: RemixRequest):
    """Process a remix in the background"""
    # Import RemixEngine conditionally to avoid circular imports
    def get_remix_engine():
        from app.apis.remix_engine import RemixEngine
        return RemixEngine()

    storage_key = get_remix_storage_key(remix_id)

    try:
        # Load the remix data
        remix_data = db.storage.json.get(storage_key)
        if not remix_data:
            print(f"Remix data not found for {remix_id}")
            return

        # Update status to show we're working on it
        remix_data["status"] = "processing"
        remix_data["progress"] = 0.1
        db.storage.json.put(storage_key, remix_data)

        # Step 1: Analyze tracks if not already analyzed
        analyzer = get_audio_analyzer()

        track_analysis = []
        for track in request.track_sources:
            analysis = analyzer.analyze_track(track)
            track_analysis.append(analysis.dict())

        # Update the remix data with track analysis
        remix_data["track_analysis"] = track_analysis
        remix_data["progress"] = 0.3
        db.storage.json.put(storage_key, remix_data)

        # Step 2: Create the remix engine and process
        engine = get_remix_engine()
        result = engine.remix(request.track_sources, track_analysis, request.settings)

        # Step 3: Save the result audio file
        if result and result.get("audio_data"):
            audio_key = f"remix_audio_{sanitize_storage_key(remix_id)}"
            db.storage.binary.put(audio_key, result["audio_data"])

            # Update the remix data with the result
            remix_data["status"] = "complete"
            remix_data["progress"] = 1.0
            remix_data["result_url"] = f"/remix-node/download/{remix_id}"
            db.storage.json.put(storage_key, remix_data)
        else:
            # Something went wrong
            remix_data["status"] = "failed"
            remix_data["error"] = "Failed to generate remix audio"
            db.storage.json.put(storage_key, remix_data)

    except Exception as e:
        # Update the remix data with the error
        try:
            remix_data = db.storage.json.get(storage_key)
            if remix_data:
                remix_data["status"] = "failed"
                remix_data["error"] = f"Error processing remix: {str(e)}"
                db.storage.json.put(storage_key, remix_data)
        except Exception:
            pass
        print(f"Error processing remix {remix_id}: {str(e)}")
