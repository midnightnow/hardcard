from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union
from app.auth import AuthorizedUser
import databutton as db
import uuid
import json
import random
import math
from datetime import datetime

# Create a router
router = APIRouter(prefix="/nocturnal-elegy-preview")

# Models
class ParameterPreviewRequest(BaseModel):
    title: Optional[str] = "Untitled Preview"
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
    
    # Automation parameters if applicable
    automation_enabled: bool = False
    automation_parameter: Optional[str] = None
    automation_points: Optional[Dict[str, List[Dict[str, float]]]] = None
    
    # Preview options
    preview_duration_seconds: int = Field(5, ge=2, le=10)
    preview_section: str = Field("intro", description="Section of the composition to preview: intro, verse, chorus, etc.")

class ParameterPreviewResponse(BaseModel):
    preview_id: str
    audio_url: str
    waveform_data: List[float]
    preview_annotations: List[Dict[str, Union[float, str]]]
    spectral_signature: Dict[str, float]
    duration_seconds: int
    timestamp: str

# Helper functions
def generate_spectral_signature(params: ParameterPreviewRequest):
    """Generate a spectral signature based on the input parameters"""
    # Scale parameters to appropriate ranges
    base_darkness = 0.5 + (params.crypto_depth / 20.0)  # 0.55 to 1.0
    
    # Wave type influences
    mid_richness = 0.4
    if "Sine" in params.wave_types:
        mid_richness += 0.1
    if "Square" in params.wave_types:
        mid_richness += 0.2
    if "Sawtooth" in params.wave_types:
        mid_richness += 0.15
    if "Triangle" in params.wave_types:
        mid_richness += 0.1
    if "Noise" in params.wave_types:
        mid_richness += 0.25
    
    # Harmonic shift influences resonance
    harmonic_shift_factor = abs(params.harmonic_shift) / 12.0
    resonance = 0.6 + (harmonic_shift_factor * 0.3)
    
    # Reverb influences spatial characteristics
    reverb_factor = {
        "None": 0.1,
        "Small Room": 0.3,
        "Large Hall": 0.6,
        "Cathedral": 0.8,
        "Digital Canyon": 0.9
    }.get(params.reverb_style, 0.5)
    
    return {
        "bass_presence": 0.3 + (params.crypto_depth / 20.0) + random.uniform(-0.1, 0.1),
        "mid_richness": mid_richness + random.uniform(-0.05, 0.05),
        "high_shimmer": 0.2 + (params.resonance_depth / 20.0) + random.uniform(-0.05, 0.05),
        "harmonic_density": resonance + random.uniform(-0.05, 0.05),
        "tonal_darkness": base_darkness + random.uniform(-0.05, 0.05),
        "reverb_depth": reverb_factor + random.uniform(-0.05, 0.05),
        "spatial_width": 0.5 + (reverb_factor / 2.0) + random.uniform(-0.05, 0.05),
    }

def generate_preview_annotations(params: ParameterPreviewRequest):
    """Generate annotations for the waveform preview based on parameters"""
    annotations = []
    
    # Start with a few standard annotations
    annotations.append({
        "position": 5.0,  # Near the beginning
        "type": "cryptographic",
        "label": "Initialization Sequence"
    })
    
    # Crypto depth influences annotation density
    if params.crypto_depth > 7:
        crypto_annotations = 3
    elif params.crypto_depth > 4:
        crypto_annotations = 2
    else:
        crypto_annotations = 1
    
    # Add crypto-related annotations
    for i in range(crypto_annotations):
        position = 20.0 + (i * 20.0) + random.uniform(-5.0, 5.0)
        annotations.append({
            "position": min(95.0, position),  # Cap at 95% to avoid edge overflow
            "type": "cryptographic",
            "label": [
                "Hash Transition",
                "Cryptographic Modulation",
                "Encrypted Pattern",
                "Hexagonal Structure"
            ][random.randint(0, 3)]
        })
    
    # Wave types influence harmonic annotations
    if len(params.wave_types) > 1:
        annotations.append({
            "position": 30.0 + random.uniform(-10.0, 10.0),
            "type": "harmonic",
            "label": "Waveform Blend"
        })
    
    # Rhythm structure influences rhythmic annotations
    rhythm_position = 50.0
    if params.rhythm_structure == "Polyrhythmic" or params.rhythm_structure == "Euclidean":
        annotations.append({
            "position": rhythm_position + random.uniform(-5.0, 5.0),
            "type": "rhythmic",
            "label": f"{params.rhythm_structure} Pattern"
        })
    
    # Beat pattern annotation
    annotations.append({
        "position": 70.0 + random.uniform(-10.0, 10.0),
        "type": "rhythmic",
        "label": f"{params.beat_pattern} Beat"
    })
    
    # End marker
    annotations.append({
        "position": 95.0,
        "type": "harmonic",
        "label": "Resolution"
    })
    
    return annotations

def generate_waveform_data(params: ParameterPreviewRequest) -> List[float]:
    """Generate synthetic waveform data based on parameters"""
    sample_count = 1000  # Number of points in the waveform
    waveform = []
    
    # Base frequency adjusted by harmonic shift
    base_freq = 1.0 + (params.harmonic_shift / 24.0)  # -0.5 to +0.5 adjustment
    
    # Crypto depth affects complexity/density
    complexity = params.crypto_depth / 10.0  # 0.1 to 1.0
    
    # Resonance depth affects amplitude
    amplitude = 0.3 + (params.resonance_depth / 20.0)  # 0.35 to 0.8
    
    # Create a waveform that's influenced by parameters
    for i in range(sample_count):
        t = i / sample_count
        
        # Start with a base value
        value = 0.0
        
        # Add sine components if sine wave is selected
        if "Sine" in params.wave_types:
            value += amplitude * 0.8 * math.sin(2 * math.pi * base_freq * t * 2)
        
        # Add square components if square wave is selected
        if "Square" in params.wave_types:
            # Smooth square wave approximation
            square = math.sin(2 * math.pi * base_freq * t)
            square = math.copysign(1, square) if abs(square) > 0.1 else square * 10
            value += amplitude * 0.6 * square
        
        # Add sawtooth components if sawtooth wave is selected
        if "Sawtooth" in params.wave_types:
            sawtooth = ((t * base_freq * 2) % 1) * 2 - 1
            value += amplitude * 0.5 * sawtooth
        
        # Add triangle components if triangle wave is selected
        if "Triangle" in params.wave_types:
            triangle = 2 * abs(2 * ((t * base_freq * 2) % 1) - 1) - 1
            value += amplitude * 0.7 * triangle
        
        # Add noise if noise is selected
        if "Noise" in params.wave_types:
            noise = random.uniform(-1, 1) * amplitude * 0.4
            value += noise
        
        # Add effects from other parameters
        if params.use_hex_encoder:
            # Add hexagonal encoder effect (subtle interference pattern)
            hex_effect = 0.1 * amplitude * math.sin(2 * math.pi * 6 * t * base_freq)
            value += hex_effect
        
        # Beat pattern influences
        beat_factor = {
            "Four-on-floor": 4,
            "Breakbeat": 3.5,
            "Half-time": 2,
            "Double-time": 8,
            "Swing": 3
        }.get(params.beat_pattern, 4)
        
        # Add beat pulsing
        beat_pulse = 0.2 * amplitude * math.exp(-((t * beat_factor * 10) % 1) * 5)
        value += beat_pulse
        
        # Normalize to stay within bounds
        value = max(-1.0, min(1.0, value))
        
        # Convert to 0.0-1.0 range for easier visualization
        normalized = (value + 1) / 2
        waveform.append(normalized)
    
    return waveform

# Endpoints
@router.post("/preview")
def generate_nocturnal_parameter_preview(request: ParameterPreviewRequest, user: AuthorizedUser) -> ParameterPreviewResponse:
    """Generate a quick audio preview with current parameter settings"""
    try:
        # Create a preview ID
        preview_id = f"preview_{uuid.uuid4()}"
        
        # Generate spectral signature based on parameters
        spectral_signature = generate_spectral_signature(request)
        
        # Generate annotations for visualization
        preview_annotations = generate_preview_annotations(request)
        
        # Generate waveform data
        waveform_data = generate_waveform_data(request)
        
        # For development and testing, use placeholder audio URLs
        preview_audio_urls = [
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", # Ambient electronic
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", # More rhythmic
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", # Melodic
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3", # Dense
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3"  # Punchy
        ]
        
        # Choose a URL based on parameter settings
        index = (hash(str(request.crypto_depth) + str(request.influence_ratio)) % 5)
        preview_url = preview_audio_urls[index]
        
        # Create response
        response = ParameterPreviewResponse(
            preview_id=preview_id,
            audio_url=preview_url,
            waveform_data=waveform_data[:100],  # Limit data points for response
            preview_annotations=preview_annotations,
            spectral_signature=spectral_signature,
            duration_seconds=request.preview_duration_seconds,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the preview data
        db.storage.json.put(f"preview_{preview_id}", response.dict())
        
        return response
    
    except Exception as e:
        print(f"Error generating parameter preview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate parameter preview: {str(e)}")

@router.get("/preview/{preview_id}")
def get_preview(preview_id: str, user: AuthorizedUser) -> ParameterPreviewResponse:
    """Get a previously generated parameter preview by ID"""
    try:
        preview_data = db.storage.json.get(f"preview_{preview_id}")
        return ParameterPreviewResponse(**preview_data)
    except Exception as e:
        print(f"Error getting preview: {e}")
        raise HTTPException(status_code=404, detail=f"Preview with ID {preview_id} not found")
