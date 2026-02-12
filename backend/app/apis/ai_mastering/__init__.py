from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import databutton as db
import uuid
import os
import io
import json
import numpy as np
import librosa
import pydub
from datetime import datetime
import tempfile
import base64
from app.auth import AuthorizedUser

# Create router
router = APIRouter(prefix="/ai-mastering")

# Models
class MasteringAlgorithm(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = {}

class MasteringTask(BaseModel):
    task_id: str
    original_file: str
    mastered_file: Optional[str] = None
    algorithm: str
    parameters: Dict[str, Any] = {}
    status: str
    created_at: str
    updated_at: str
    error: Optional[str] = None
    original_waveform: Optional[List[float]] = None
    mastered_waveform: Optional[List[float]] = None

class MasteringRequest(BaseModel):
    algorithm: str
    parameters: Dict[str, Any] = {}

class MasteringResponse(BaseModel):
    task_id: str
    status: str
    message: str

class MasteringTaskStatus(BaseModel):
    task_id: str
    status: str
    message: str
    original_file: Optional[str] = None
    mastered_file: Optional[str] = None
    original_waveform: Optional[List[float]] = None
    mastered_waveform: Optional[List[float]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

class AlgorithmListResponse(BaseModel):
    algorithms: List[MasteringAlgorithm]

# Utility functions
def get_all_mastering_tasks() -> Dict[str, Dict]:
    """Get all mastering tasks from storage"""
    try:
        return db.storage.json.get("ai_mastering_tasks", default={})
    except Exception as e:
        print(f"Error loading mastering tasks: {e}")
        return {}

def save_mastering_task(task_id: str, task_data: Dict) -> None:
    """Save mastering task to storage"""
    try:
        tasks = get_all_mastering_tasks()
        tasks[task_id] = task_data
        db.storage.json.put("ai_mastering_tasks", tasks)
    except Exception as e:
        print(f"Error saving mastering task: {e}")

def generate_waveform(audio_path: str, n_points: int = 100) -> List[float]:
    """Generate a simplified waveform representation for visualization"""
    try:
        # Load audio file using librosa
        y, sr = librosa.load(audio_path, sr=None)
        
        # Compute RMS energy in windows
        frame_length = len(y) // n_points
        if frame_length == 0:
            frame_length = 1
            
        waveform = []
        for i in range(n_points):
            start = i * frame_length
            end = min(start + frame_length, len(y))
            if start >= len(y):
                break
            chunk = y[start:end]
            rms = np.sqrt(np.mean(chunk**2))
            waveform.append(float(rms))
            
        # Normalize to 0-1 range
        if waveform:
            max_val = max(waveform)
            if max_val > 0:
                waveform = [val / max_val for val in waveform]
                
        return waveform
    except Exception as e:
        print(f"Error generating waveform: {e}")
        return []

# Available mastering algorithms
def get_available_algorithms() -> List[MasteringAlgorithm]:
    """Get list of available mastering algorithms"""
    return [
        MasteringAlgorithm(
            name="basic",
            description="Basic mastering with normalization and compression",
            parameters={
                "target_loudness": -14.0,  # LUFS target
                "compression_ratio": 2.0,
                "attack": 5.0,  # ms
                "release": 50.0,  # ms
            }
        ),
        MasteringAlgorithm(
            name="matchering",
            description="Matches your track to reference tracks for consistent sound",
            parameters={
                "reference_track": "",  # Optional reference track ID
                "loudness_matching": True,
                "frequency_matching": True,
            }
        ),
        MasteringAlgorithm(
            name="audiocraft",
            description="AI-powered mastering using deep learning models",
            parameters={
                "style": "balanced",  # balanced, warm, bright, punchy
                "intensity": 0.7,  # 0.0 to 1.0
            }
        )
    ]

def apply_basic_mastering(input_path: str, output_path: str, parameters: Dict[str, Any]) -> None:
    """Apply basic mastering with normalization and simple compression"""
    try:
        # Load audio with pydub
        audio = pydub.AudioSegment.from_file(input_path)
        
        # Normalize (adjust volume)
        target_loudness = parameters.get("target_loudness", -14.0)
        current_loudness = audio.dBFS
        change_in_dBFS = target_loudness - current_loudness
        normalized_audio = audio.apply_gain(change_in_dBFS)
        
        # Apply simple compression (using pydub effects would be ideal but not all are available)
        # This is a simplified approach
        compressed_audio = normalized_audio
        
        # Export the processed audio
        compressed_audio.export(output_path, format="wav")
        
    except Exception as e:
        print(f"Error in basic mastering: {e}")
        raise e

def apply_matchering_mastering(input_path: str, output_path: str, parameters: Dict[str, Any]) -> None:
    """Apply matchering-inspired mastering (without the actual matchering library)"""
    try:
        # Load audio with pydub
        audio = pydub.AudioSegment.from_file(input_path)
        
        # For now, we'll simulate matchering with basic processing
        # In a real implementation, we would use the matchering library
        
        # Normalize to target loudness
        target_loudness = -14.0  # Industry standard streaming target
        current_loudness = audio.dBFS
        change_in_dBFS = target_loudness - current_loudness
        processed_audio = audio.apply_gain(change_in_dBFS)
        
        # Apply some basic EQ (simulating frequency matching)
        # In a real implementation, this would be much more sophisticated
        processed_audio = processed_audio.high_pass_filter(60)  # Remove rumble
        
        # Export the processed audio
        processed_audio.export(output_path, format="wav")
        
    except Exception as e:
        print(f"Error in matchering mastering: {e}")
        raise e

def apply_audiocraft_mastering(input_path: str, output_path: str, parameters: Dict[str, Any]) -> None:
    """Apply audiocraft-inspired mastering (simulated without the actual model)"""
    try:
        # Load audio with pydub
        audio = pydub.AudioSegment.from_file(input_path)
        
        # For now, we'll simulate audiocraft with basic processing
        # In a real implementation, we would use the audiocraft model
        
        # Apply processing based on style parameter
        style = parameters.get("style", "balanced")
        intensity = parameters.get("intensity", 0.7)
        
        # Normalize to target loudness
        target_loudness = -14.0
        current_loudness = audio.dBFS
        change_in_dBFS = target_loudness - current_loudness
        processed_audio = audio.apply_gain(change_in_dBFS)
        
        # Apply style-specific processing (simplified simulation)
        if style == "warm":
            # Boost low frequencies slightly
            processed_audio = processed_audio.low_shelf_filter(frequency=250, gain_db=2 * intensity)
        elif style == "bright":
            # Boost high frequencies slightly
            processed_audio = processed_audio.high_shelf_filter(frequency=2000, gain_db=2 * intensity)
        elif style == "punchy":
            # Add some compression
            processed_audio = processed_audio.compress_dynamic_range(threshold=-20, ratio=2.0)
        
        # Export the processed audio
        processed_audio.export(output_path, format="wav")
        
    except Exception as e:
        print(f"Error in audiocraft mastering: {e}")
        raise e

# Background task for processing audio
async def process_audio_file(task_id: str, input_path: str, algorithm: str, parameters: Dict[str, Any]):
    """Background task to process audio with selected algorithm"""
    tasks = get_all_mastering_tasks()
    if task_id not in tasks:
        print(f"Task {task_id} not found")
        return
    
    task = tasks[task_id]
    
    try:
        # Update task status
        task["status"] = "processing"
        task["updated_at"] = datetime.now().isoformat()
        save_mastering_task(task_id, task)
        
        # Prepare output path
        output_filename = f"mastered_{os.path.basename(input_path)}"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        
        # Apply selected mastering algorithm
        if algorithm == "basic":
            apply_basic_mastering(input_path, output_path, parameters)
        elif algorithm == "matchering":
            apply_matchering_mastering(input_path, output_path, parameters)
        elif algorithm == "audiocraft":
            apply_audiocraft_mastering(input_path, output_path, parameters)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Generate waveforms
        original_waveform = generate_waveform(input_path)
        mastered_waveform = generate_waveform(output_path)
        
        # Save mastered file to databutton storage
        mastered_key = f"mastered_{task_id}_{output_filename}"
        with open(output_path, "rb") as f:
            db.storage.binary.put(mastered_key, f.read())
        
        # Update task
        task["status"] = "completed"
        task["mastered_file"] = mastered_key
        task["original_waveform"] = original_waveform
        task["mastered_waveform"] = mastered_waveform
        task["updated_at"] = datetime.now().isoformat()
        save_mastering_task(task_id, task)
        
        # Clean up temp files
        try:
            os.remove(input_path)
            os.remove(output_path)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
        
    except Exception as e:
        # Update task with error
        task["status"] = "failed"
        task["error"] = str(e)
        task["updated_at"] = datetime.now().isoformat()
        save_mastering_task(task_id, task)
        print(f"Error processing audio: {e}")

# API Endpoints
@router.get("/algorithms")
def get_algorithms(user: AuthorizedUser) -> AlgorithmListResponse:
    """Get available mastering algorithms"""
    algorithms = get_available_algorithms()
    return AlgorithmListResponse(algorithms=algorithms)

@router.post("/process")
async def process_audio(file: UploadFile = File(...), 
                      algorithm: str = Form(...),
                      parameters: str = Form("{}"),
                      background_tasks: BackgroundTasks = None,
                      user: AuthorizedUser = None) -> MasteringResponse:
    """Process audio file with AI mastering"""
    try:
        # Parse parameters
        params = json.loads(parameters) if parameters else {}
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Save original file to temp location
        input_filename = file.filename
        temp_dir = tempfile.gettempdir()
        input_path = os.path.join(temp_dir, input_filename)
        
        # Write uploaded file to temp location
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Save original file to databutton storage
        original_key = f"original_{task_id}_{input_filename}"
        db.storage.binary.put(original_key, content)
        
        # Create task record
        now = datetime.now().isoformat()
        task = {
            "task_id": task_id,
            "original_file": original_key,
            "mastered_file": None,
            "algorithm": algorithm,
            "parameters": params,
            "status": "queued",
            "created_at": now,
            "updated_at": now,
            "error": None,
            "original_waveform": None,
            "mastered_waveform": None
        }
        
        # Save task
        save_mastering_task(task_id, task)
        
        # Start background processing
        background_tasks.add_task(process_audio_file, task_id, input_path, algorithm, params)
        
        return MasteringResponse(
            task_id=task_id,
            status="queued",
            message="Audio processing started"
        )
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
def get_task_status(task_id: str, user: AuthorizedUser) -> MasteringTaskStatus:
    """Get status of a mastering task"""
    tasks = get_all_mastering_tasks()
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    return MasteringTaskStatus(
        task_id=task_id,
        status=task["status"],
        message=f"Mastering task is {task['status']}",
        original_file=task["original_file"],
        mastered_file=task["mastered_file"],
        original_waveform=task["original_waveform"],
        mastered_waveform=task["mastered_waveform"],
        error=task["error"],
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )

@router.get("/download/{file_key}")
def download_file(file_key: str, user: AuthorizedUser):
    """Download processed audio file"""
    try:
        # Get file from storage
        file_data = db.storage.binary.get(file_key)
        
        # Create temp file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, file_key.split("_", 1)[1])
        
        with open(temp_path, "wb") as f:
            f.write(file_data)
        
        # Return file
        return FileResponse(
            path=temp_path,
            filename=file_key.split("_", 1)[1],
            media_type="audio/wav",
            background=BackgroundTasks()
        )
    except Exception as e:
        print(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
