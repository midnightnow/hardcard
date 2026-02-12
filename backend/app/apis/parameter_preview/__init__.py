from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from app.auth import AuthorizedUser
import databutton as db
import numpy as np
import uuid
import random
from datetime import datetime
import time

# Create a router
router = APIRouter(prefix="/parameter-preview")

# Models
class ParameterPreviewRequest(BaseModel):
    """Request model for generating a quick audio preview based on parameter settings"""
    title: str = "Untitled Preview"
    profile_id: Optional[str] = None
    
    # Basic parameters
    influence_ratio: float = Field(0.5, ge=0.0, le=1.0)
    crypto_depth: int = Field(5, ge=1, le=10)
    emotional_seeds: List[str] = ["nostalgia", "transcendence"]
    crypto_source: str = "Algorithmic"
    use_hex_encoder: bool = False
    
    # Advanced parameters
    resonance_depth: int = Field(5, ge=1, le=10)
    wave_types: List[str] = ["Sine"]
    rhythm_structure: str = "Binary"
    beat_pattern: str = "Four-on-floor"
    harmonic_shift: int = Field(0, ge=-12, le=12)
    reverb_style: str = "None"
    
    # Automation parameters
    automation_enabled: bool = False
    automation_parameter: Optional[str] = None
    automation_points: Optional[Dict[str, List[Dict[str, float]]]] = None
    
    # Preview options
    preview_duration_seconds: int = Field(5, ge=2, le=10)
    preview_section: str = "intro"

class ParameterPreviewResponse(BaseModel):
    """Response model with real-time audio preview and waveform data"""
    preview_id: str
    audio_url: str
    waveform_data: List[float]
    previewAnnotations: List[Dict[str, Any]]
    spectralSignature: Dict[str, float]
    durationSeconds: int
    timestamp: str

# Helper functions
def generate_waveform_data(params: ParameterPreviewRequest) -> List[float]:
    """Generate synthetic waveform data based on parameters"""
    # Number of points in waveform visualization
    num_points = 128
    
    # Base waveform (sine wave)
    t = np.linspace(0, 4*np.pi, num_points)
    base_wave = np.sin(t)
    
    # Adjust based on wave types
    wave_components = []
    for wave_type in params.wave_types:
        if wave_type == "Sine":
            wave_components.append(np.sin(t))
        elif wave_type == "Square":
            wave_components.append(np.sign(np.sin(t)))
        elif wave_type == "Sawtooth":
            wave_components.append(((t / np.pi) % 2) - 1)
        elif wave_type == "Triangle":
            wave_components.append(2 * np.abs(((t / np.pi) % 2) - 1) - 1)
        elif wave_type == "Noise":
            wave_components.append(np.random.random(num_points) * 2 - 1)
    
    # Combine wave components
    if wave_components:
        combined_wave = np.zeros(num_points)
        for wave in wave_components:
            combined_wave += wave
        combined_wave /= len(wave_components)  # Normalize
    else:
        combined_wave = base_wave
    
    # Apply harmonic shift
    if params.harmonic_shift != 0:
        # Shift frequency
        t_shifted = np.linspace(0, 4*np.pi * (1 + params.harmonic_shift/12), num_points)
        harmonic_component = np.sin(t_shifted) * 0.3
        combined_wave = combined_wave * 0.7 + harmonic_component
    
    # Apply crypto depth (more complexity and modulation with higher depth)
    if params.crypto_depth > 5:
        modulation = np.sin(t * (params.crypto_depth / 5)) * ((params.crypto_depth - 5) / 10)
        combined_wave = combined_wave * (1 - modulation) + modulation
    
    # Apply resonance (more peaks and valleys with higher resonance)
    if params.resonance_depth > 5:
        resonance_factor = (params.resonance_depth - 5) / 10
        combined_wave = combined_wave + resonance_factor * np.sin(t * 3) * combined_wave
    
    # Apply hex encoder effects (more geometric patterns)
    if params.use_hex_encoder:
        hex_pattern = np.sin(t * 6) * 0.3
        combined_wave = combined_wave * 0.7 + hex_pattern
    
    # Apply influence ratio (more variability with lower influence)
    noise_level = (1 - params.influence_ratio) * 0.3
    combined_wave = combined_wave * (1 - noise_level) + np.random.random(num_points) * noise_level * 2 - noise_level
    
    # Normalize between 0 and 1 for visualization
    normalized_wave = (combined_wave - combined_wave.min()) / (combined_wave.max() - combined_wave.min())
    
    return normalized_wave.tolist()

def generate_spectral_signature(params: ParameterPreviewRequest) -> Dict[str, float]:
    """Generate spectral signature based on parameters"""
    bass_presence = 0.3 + params.crypto_depth / 20
    mid_richness = 0.3 + params.influence_ratio / 2
    high_shimmer = 0.3 + (1 if "Noise" in params.wave_types else 0) / 5
    harmonic_density = 0.3 + len(params.wave_types) / 10
    tonal_darkness = 0.3 + (0.6 if params.crypto_source == "Bitcoin" else 0.3)
    reverb_depth = 0.3 + (0.8 if params.reverb_style == "Cathedral" else 
                        0.6 if params.reverb_style == "Large Hall" else
                        0.4 if params.reverb_style == "Small Room" else
                        0.2 if params.reverb_style == "Digital Canyon" else 0.1)
    spatial_width = 0.3 + params.resonance_depth / 20
    
    # Ensure values are between 0 and 1
    return {
        "bass_presence": min(max(bass_presence, 0), 1),
        "mid_richness": min(max(mid_richness, 0), 1),
        "high_shimmer": min(max(high_shimmer, 0), 1),
        "harmonic_density": min(max(harmonic_density, 0), 1),
        "tonal_darkness": min(max(tonal_darkness, 0), 1),
        "reverb_depth": min(max(reverb_depth, 0), 1),
        "spatial_width": min(max(spatial_width, 0), 1),
    }

def generate_preview_annotations(params: ParameterPreviewRequest) -> List[Dict[str, Any]]:
    """Generate annotations for the preview based on parameters"""
    annotations = []
    
    # Add harmonic structure annotations
    for wave_type in params.wave_types:
        annotations.append({
            "position": random.random(),
            "type": "harmonic",
            "label": wave_type
        })
    
    # Add rhythm annotations
    annotations.append({
        "position": random.random(),
        "type": "rhythmic",
        "label": params.rhythm_structure
    })
    
    annotations.append({
        "position": random.random(),
        "type": "rhythmic",
        "label": params.beat_pattern
    })
    
    # Add cryptographic annotations
    if params.use_hex_encoder:
        annotations.append({
            "position": random.random(),
            "type": "cryptographic",
            "label": "Hex Encoder"
        })
    annotations.append({
        "position": random.random(),
        "type": "cryptographic",
        "label": params.crypto_source
    })
    
    # Add emotional seed annotations
    for seed in params.emotional_seeds[:2]:  # Just add a couple
        annotations.append({
            "position": random.random(),
            "type": "emotional",
            "label": seed
        })
    return annotations

def generate_preview_audio_url(params: ParameterPreviewRequest, preview_id: str) -> str:
    """Generate a mock audio URL for the preview
    In a real implementation, this would create actual audio"""
    # For development purposes, we're using a placeholder URL
    # In production, this would generate actual audio based on parameters
    audio_types = [
        "https://actions.google.com/sounds/v1/science_fiction/alien_beam.ogg",
        "https://actions.google.com/sounds/v1/science_fiction/alien_time_machine.ogg",
        "https://actions.google.com/sounds/v1/science_fiction/alien_time_machine_2.ogg",
        "https://actions.google.com/sounds/v1/science_fiction/laser_retro_gun.ogg",
        "https://actions.google.com/sounds/v1/science_fiction/space_station_computer_interface.ogg"
    ]
    
    # Select an audio based on crypto depth and use hexagonal encoder
    index = int(params.crypto_depth / 2) % len(audio_types)
    if params.use_hex_encoder:
        index = (index + 1) % len(audio_types)
    
    return audio_types[index]

# Endpoints
@router.post("/generate")
def generate_parameter_preview(request: ParameterPreviewRequest, user: AuthorizedUser) -> ParameterPreviewResponse:
    """Generate a quick audio preview based on current parameter settings"""
    try:
        # Generate a unique ID for this preview
        preview_id = f"preview_{uuid.uuid4()}"
        
        # Add a slight delay to simulate processing
        time.sleep(0.5)
        
        # Generate waveform data
        waveform_data = generate_waveform_data(request)
        
        # Generate spectral signature
        spectral_signature = generate_spectral_signature(request)
        
        # Generate preview annotations
        preview_annotations = generate_preview_annotations(request)
        
        # Get audio URL for the preview
        audio_url = generate_preview_audio_url(request, preview_id)
        
        # Create response
        response = ParameterPreviewResponse(
            preview_id=preview_id,
            audio_url=audio_url,
            waveform_data=waveform_data,
            previewAnnotations=preview_annotations,
            spectralSignature=spectral_signature,
            durationSeconds=request.preview_duration_seconds,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the preview data for potential later reference
        db.storage.json.put(f"parameter_preview_{preview_id}", {
            "request": request.dict(),
            "response": response.dict(),
            "created_at": datetime.now().isoformat()
        })
        
        return response
    except Exception as e:
        print(f"Error generating parameter preview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate parameter preview: {str(e)}")
