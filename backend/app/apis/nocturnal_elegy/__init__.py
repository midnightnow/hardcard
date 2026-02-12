from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any
from app.auth import AuthorizedUser
import databutton as db
import uuid
import json
import random
from datetime import datetime
from app.env import mode, Mode

# Create a router
router = APIRouter(prefix="/nocturnal-elegy")

# Models
class SpectralDNARequest(BaseModel):
    reference_track_url: Optional[str] = None
    reference_artist: str = "Lana Del Rey"
    reference_mood: str = "melancholic"
    intensity: float = Field(0.7, ge=0.0, le=1.0)
    complexity: float = Field(0.6, ge=0.0, le=1.0)

class SpectralDNAResponse(BaseModel):
    spectral_dna_id: str
    harmonic_structure: Dict[str, float]
    rhythmic_patterns: List[Dict[str, Union[str, float]]]
    tonal_qualities: Dict[str, float]
    spectral_signature: Dict[str, float]
    timestamp: str

class CryptoSoundRequest(BaseModel):
    spectral_dna_id: str
    emotion_seed: str = "nostalgia"
    cryptographic_intensity: float = Field(0.5, ge=0.0, le=1.0)
    hash_algorithm: str = "sha256"
    temporal_structure: str = "flowing"

class CryptoSoundResponse(BaseModel):
    crypto_sound_id: str
    encrypted_patterns: List[Dict[str, Union[str, float, List[float]]]]
    emotion_mapping: Dict[str, float]
    harmonic_transformations: List[Dict[str, Union[str, float]]]
    signature_verification: bool
    timestamp: str

class LyricGenerationRequest(BaseModel):
    theme: str = "digital legacy"
    emotional_tone: str = "reflective"
    cryptographic_references: bool = True
    verse_count: int = Field(2, ge=1, le=5)
    chorus_repetitions: int = Field(2, ge=1, le=3)
    syllable_structure: Optional[List[int]] = None

class LyricGenerationResponse(BaseModel):
    lyric_id: str
    verses: List[str]
    chorus: str
    bridge: Optional[str] = None
    thematic_keywords: List[str]
    sentiment_analysis: Dict[str, float]
    cryptographic_elements: List[Dict[str, str]]
    timestamp: str

class VisualGenerationRequest(BaseModel):
    title: str
    themes: List[str] = ["nocturnal", "cyberpunk", "ethereal"]
    color_palette: str = "darkwave"
    symbolic_elements: List[str] = ["moon", "circuit", "geometric"]
    aspect_ratio: str = "square"

class VisualGenerationResponse(BaseModel):
    visual_id: str
    image_url: str
    color_analysis: Dict[str, str]
    symbolic_interpretations: Dict[str, str]
    timestamp: str

class NocturnalElegyGenerationRequest(BaseModel):
    title: str
    concept_description: str
    profile_id: Optional[str] = None
    reference_influences: Dict[str, float] = Field(
        default_factory=lambda: {"Lana Del Rey": 0.6, "ALEUS": 0.4}
    )
    emotional_seeds: List[str] = ["nostalgia", "transcendence", "digital melancholy"]
    cryptographic_elements: bool = True
    duration_seconds: int = Field(180, ge=30, le=300)
    include_lyrics: bool = True
    include_album_art: bool = True
    # New parameters for interactive controls
    crypto_depth: int = Field(5, ge=1, le=10)
    influence_ratio: float = Field(0.5, ge=0.0, le=1.0)
    crypto_source: str = "Algorithmic"
    use_hex_encoder: bool = False

class NocturnalElegyMetadata(BaseModel):
    title: str
    concept_description: str
    profile_id: Optional[str] = None
    spectral_dna_id: Optional[str] = None
    crypto_sound_id: Optional[str] = None
    lyric_id: Optional[str] = None
    visual_id: Optional[str] = None
    reference_influences: Dict[str, float]
    emotional_seeds: List[str]
    cryptographic_elements: bool
    duration_seconds: int
    include_lyrics: bool
    include_album_art: bool
    # New parameters for interactive controls
    crypto_depth: int = 5
    influence_ratio: float = 0.5
    crypto_source: str = "Algorithmic"
    use_hex_encoder: bool = False
    music_id: Optional[str] = None
    status: str = "pending"
    started_at: str
    completed_at: Optional[str] = None

class NocturnalElegyResponse(BaseModel):
    elegy_id: str
    title: str
    status: str
    creation_stage: str
    audio_url: Optional[str] = None
    lyrics: Optional[List[str]] = None
    album_art_url: Optional[str] = None
    spectral_analysis: Optional[Dict[str, Any]] = None
    crypto_elements: Optional[Dict[str, Any]] = None
    # Return parameters for UI feedback
    parameters: Optional[Dict[str, Any]] = None
    timestamp: str

# Helper functions
def get_all_elegies():
    """Get all nocturnal elegy records from storage"""
    try:
        records = db.storage.json.get("nocturnal_elegies", default={})
        return records
    except Exception as e:
        print(f"Error getting nocturnal elegy records: {e}")
        return {}

def save_elegy_record(elegy_id, record):
    """Save a nocturnal elegy record to storage"""
    try:
        records = get_all_elegies()
        records[elegy_id] = record
        db.storage.json.put("nocturnal_elegies", records)
    except Exception as e:
        print(f"Error saving nocturnal elegy record: {e}")

def generate_spectral_signature():
    """Generate a random spectral signature for development"""
    return {
        "bass_presence": random.uniform(0.3, 0.8),
        "mid_richness": random.uniform(0.4, 0.9),
        "high_shimmer": random.uniform(0.2, 0.7),
        "harmonic_density": random.uniform(0.5, 0.9),
        "tonal_darkness": random.uniform(0.6, 0.9),
        "reverb_depth": random.uniform(0.7, 0.95),
        "spatial_width": random.uniform(0.5, 0.8),
    }

def generate_rhythmic_patterns():
    """Generate random rhythmic patterns for development"""
    patterns = []
    for i in range(random.randint(2, 4)):
        patterns.append({
            "pattern_type": random.choice(["beat", "arpeggio", "drone", "pulse"]),
            "time_signature": random.choice(["4/4", "3/4", "6/8"]),
            "beat_emphasis": random.uniform(0.3, 0.9),
            "syncopation": random.uniform(0.2, 0.8),
            "variation_factor": random.uniform(0.1, 0.6),
        })
    return patterns

def generate_harmonic_structure():
    """Generate a random harmonic structure for development"""
    return {
        "minor_key_probability": random.uniform(0.7, 0.95),
        "modal_mixture": random.uniform(0.3, 0.8),
        "dissonance_factor": random.uniform(0.2, 0.6),
        "chord_complexity": random.uniform(0.4, 0.8),
        "progression_novelty": random.uniform(0.3, 0.7),
    }

def generate_emotional_mapping():
    """Generate emotional mapping for development"""
    return {
        "melancholy": random.uniform(0.6, 0.9),
        "nostalgia": random.uniform(0.5, 0.8),
        "tension": random.uniform(0.3, 0.7),
        "release": random.uniform(0.2, 0.6),
        "ethereality": random.uniform(0.5, 0.9),
        "darkness": random.uniform(0.6, 0.9),
        "transcendence": random.uniform(0.4, 0.8),
    }

def generate_cryptographic_elements():
    """Generate random cryptographic elements for development"""
    elements = []
    crypto_terms = ["entropy", "hash", "cipher", "quantum", "blockchain", "key", "signature"]
    poetic_terms = ["moonlight", "shadow", "eternal", "digital", "memory", "whisper", "echo"]
    
    for i in range(random.randint(3, 5)):
        elements.append({
            "crypto_term": random.choice(crypto_terms),
            "poetic_translation": random.choice(poetic_terms),
            "verse_placement": f"verse_{random.randint(1, 3)}"
        })
    return elements

def generate_lyrics():
    """Generate placeholder lyrics for development"""
    verses = [
        "Beneath digital moons and quantum haze\nYour legacy encoded in eternal phase\nEchoes of memory in cryptic arrays\nTime-locked whispers for future days",
        "Silent algorithms trace your shadow's form\nEntropy garden where emotions transform\nCipher the remnants of what we once knew\nBlockchain memories of a transcendent view"
    ]
    
    chorus = "In the darkness we find our light\nEncrypted echoes throughout the night\nNocturnal elegy, our digital rite\nPreserving forever what burns so bright"
    
    bridge = "Hash functions transform like tears in rain\nSignatures verifying what remains"
    
    return verses, chorus, bridge

# Endpoints
@router.post("/analyze-spectral-dna")
def analyze_spectral_dna(request: SpectralDNARequest, user: AuthorizedUser) -> SpectralDNAResponse:
    """Analyze reference tracks and extract spectral DNA signatures"""
    try:
        # Generate a spectral DNA analysis
        spectral_dna_id = f"spectral_{uuid.uuid4()}"
        
        # In development, generate random sample data
        harmonic_structure = generate_harmonic_structure()
        rhythmic_patterns = generate_rhythmic_patterns()
        spectral_signature = generate_spectral_signature()
        
        # Adjust based on intensity and complexity
        tonal_qualities = {
            "darkness": 0.5 + (request.intensity * 0.4),
            "richness": 0.3 + (request.complexity * 0.6),
            "clarity": 0.7 - (request.intensity * 0.3),
            "depth": 0.4 + (request.complexity * 0.4),
            "texture": 0.5 + (request.intensity * 0.3),
        }
        
        # Create response
        response = SpectralDNAResponse(
            spectral_dna_id=spectral_dna_id,
            harmonic_structure=harmonic_structure,
            rhythmic_patterns=rhythmic_patterns,
            tonal_qualities=tonal_qualities,
            spectral_signature=spectral_signature,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the analysis
        db.storage.json.put(f"spectral_dna_{spectral_dna_id}", response.dict())
        
        return response
    except Exception as e:
        print(f"Error analyzing spectral DNA: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze spectral DNA: {str(e)}")

@router.post("/design-crypto-sound")
def design_crypto_sound(request: CryptoSoundRequest, user: AuthorizedUser) -> CryptoSoundResponse:
    """Design sounds using cryptographic principles and emotional mapping"""
    try:
        # Retrieve the spectral DNA
        try:
            spectral_dna = db.storage.json.get(f"spectral_dna_{request.spectral_dna_id}")
        except Exception:
            raise HTTPException(status_code=404, detail=f"Spectral DNA with ID {request.spectral_dna_id} not found")
        
        # Generate a crypto sound design
        crypto_sound_id = f"crypto_sound_{uuid.uuid4()}"
        
        # Generate emotional mapping
        emotion_mapping = generate_emotional_mapping()
        
        # Create encrypted patterns
        encrypted_patterns = []
        for i in range(random.randint(3, 6)):
            encrypted_patterns.append({
                "pattern_name": f"pattern_{i+1}",
                "source_emotion": random.choice(list(emotion_mapping.keys())),
                "encryption_method": request.hash_algorithm,
                "time_signature": random.choice(["4/4", "3/4", "6/8"]),
                "pattern_sequence": [random.random() for _ in range(8)],
                "cryptographic_intensity": request.cryptographic_intensity
            })
        
        # Create harmonic transformations
        harmonic_transformations = []
        for i in range(random.randint(2, 4)):
            harmonic_transformations.append({
                "transform_type": random.choice(["modulation", "inversion", "retrograde", "augmentation"]),
                "source_chord": random.choice(["Am", "Fm", "Cm", "Gm"]),
                "target_chord": random.choice(["Em", "Dm", "Bm", "F#m"]),
                "transition_probability": random.uniform(0.3, 0.9)
            })
        
        # Create response
        response = CryptoSoundResponse(
            crypto_sound_id=crypto_sound_id,
            encrypted_patterns=encrypted_patterns,
            emotion_mapping=emotion_mapping,
            harmonic_transformations=harmonic_transformations,
            signature_verification=True,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the crypto sound design
        db.storage.json.put(f"crypto_sound_{crypto_sound_id}", response.dict())
        
        return response
    except Exception as e:
        print(f"Error designing crypto sound: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to design crypto sound: {str(e)}")

@router.post("/generate-lyrics")
def generate_lyrics_endpoint(request: LyricGenerationRequest, user: AuthorizedUser) -> LyricGenerationResponse:
    """Generate thematic lyrics for nocturnal elegy compositions"""
    try:
        # Generate a lyrics record
        lyric_id = f"lyrics_{uuid.uuid4()}"
        
        # Generate placeholder lyrics
        verses, chorus, bridge = generate_lyrics()
        
        # Generate crypto elements if requested
        cryptographic_elements = generate_cryptographic_elements() if request.cryptographic_references else []
        
        # Create sentiment analysis
        sentiment_analysis = {
            "melancholy": random.uniform(0.6, 0.9),
            "nostalgia": random.uniform(0.5, 0.8),
            "darkness": random.uniform(0.6, 0.9),
            "transcendence": random.uniform(0.4, 0.8),
            "cryptic": random.uniform(0.5, 0.9) if request.cryptographic_references else random.uniform(0.1, 0.4),
        }
        
        # Create response
        response = LyricGenerationResponse(
            lyric_id=lyric_id,
            verses=verses[:request.verse_count],
            chorus=chorus,
            bridge=bridge,
            thematic_keywords=["legacy", "digital", "nocturnal", "blockchain", "memory", "eternity"],
            sentiment_analysis=sentiment_analysis,
            cryptographic_elements=cryptographic_elements,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the lyrics
        db.storage.json.put(f"lyrics_{lyric_id}", response.dict())
        
        return response
    except Exception as e:
        print(f"Error generating lyrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate lyrics: {str(e)}")

@router.post("/generate-visual")
def generate_visual(request: VisualGenerationRequest, user: AuthorizedUser) -> VisualGenerationResponse:
    """Generate album art for nocturnal elegy compositions"""
    try:
        # Generate a visual record
        visual_id = f"visual_{uuid.uuid4()}"
        
        # For development, use placeholder imagery
        placeholder_images = [
            "https://images.unsplash.com/photo-1604076913837-52ab5629fba9", # Neon city
            "https://images.unsplash.com/photo-1581822261290-991b38693d1b", # Cyberpunk aesthetic
            "https://images.unsplash.com/photo-1526289034009-0240ddb68ce3", # Retrowave sunset
            "https://images.unsplash.com/photo-1558244661-d248897f7bc4", # Dark electronic mood
            "https://images.unsplash.com/photo-1554797589-7241bb691973"  # Dark abstract
        ]
        
        # Generate color analysis
        color_analysis = {
            "primary": "#1a0933", # deep purple
            "secondary": "#4b0082", # indigo
            "accent": "#800080", # purple
            "highlight": "#9400d3", # violet
            "shadow": "#120024", # near black
        }
        
        # Generate symbolic interpretations
        symbolic_interpretations = {}
        for element in request.symbolic_elements:
            if element == "moon":
                symbolic_interpretations["moon"] = "Represents the nocturnal essence and cyclical nature of legacy"
            elif element == "circuit":
                symbolic_interpretations["circuit"] = "Symbolizes the digital permanence and connectivity of inheritance"
            elif element == "geometric":
                symbolic_interpretations["geometric"] = "Represents mathematical precision and cryptographic structures"
        
        # Create response
        response = VisualGenerationResponse(
            visual_id=visual_id,
            image_url=random.choice(placeholder_images),
            color_analysis=color_analysis,
            symbolic_interpretations=symbolic_interpretations,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the visual
        db.storage.json.put(f"visual_{visual_id}", response.dict())
        
        return response
    except Exception as e:
        print(f"Error generating visual: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate visual: {str(e)}")

@router.post("/generate")
def generate_nocturnal_elegy(request: NocturnalElegyGenerationRequest, user: AuthorizedUser) -> NocturnalElegyResponse:
    """Generate a complete nocturnal elegy composition with all components"""
    try:
        # Create a new elegy record
        elegy_id = f"elegy_{uuid.uuid4()}"
        
        # Initialize metadata
        metadata = NocturnalElegyMetadata(
            title=request.title,
            concept_description=request.concept_description,
            profile_id=request.profile_id,
            reference_influences=request.reference_influences,
            emotional_seeds=request.emotional_seeds,
            cryptographic_elements=request.cryptographic_elements,
            duration_seconds=request.duration_seconds,
            include_lyrics=request.include_lyrics,
            include_album_art=request.include_album_art,
            # Include the new interactive parameters
            crypto_depth=request.crypto_depth,
            influence_ratio=request.influence_ratio,
            crypto_source=request.crypto_source,
            use_hex_encoder=request.use_hex_encoder,
            started_at=datetime.now().isoformat()
        )
        
        # Create initial response
        initial_response = NocturnalElegyResponse(
            elegy_id=elegy_id,
            title=request.title,
            status="processing",
            creation_stage="spectral_analysis",
            parameters={
                "influenceRatio": request.influence_ratio,
                "cryptoDepth": request.crypto_depth,
                "cryptoSource": request.crypto_source,
                "useHexEncoder": request.use_hex_encoder,
                "emotionalSeeds": request.emotional_seeds
            },
            timestamp=datetime.now().isoformat()
        )
        
        # Store the initial record
        db.storage.json.put(f"elegy_{elegy_id}", {
            "metadata": metadata.dict(),
            "response": initial_response.dict(),
            "components": {}
        })
        
        # For development, auto-complete the elegy generation
        is_dev_mode = mode == Mode.DEV
        
        if is_dev_mode:
            # 1. Spectral DNA Analysis
            spectral_request = SpectralDNARequest(
                reference_artist="Lana Del Rey" if request.reference_influences.get("Lana Del Rey", 0) > 0.5 else "ALEUS",
                intensity=0.4 + (request.influence_ratio * 0.6),  # Scale influence ratio to intensity
                complexity=0.3 + (request.crypto_depth / 10 * 0.7)  # Scale crypto depth to complexity
            )
            spectral_response = analyze_spectral_dna(spectral_request, user)
            
            # Update metadata with spectral DNA ID
            metadata.spectral_dna_id = spectral_response.spectral_dna_id
            
            # 2. Cryptographic Sound Design
            crypto_request = CryptoSoundRequest(
                spectral_dna_id=spectral_response.spectral_dna_id,
                emotion_seed=request.emotional_seeds[0] if request.emotional_seeds else "nostalgia",
                cryptographic_intensity=request.crypto_depth / 10,  # Scale crypto depth to intensity
                hash_algorithm="sha256" if request.crypto_source == "Bitcoin" else 
                             "keccak" if request.crypto_source == "Ethereum" else "hmac",
                temporal_structure="hexagonal" if request.use_hex_encoder else "flowing"
            )
            crypto_response = design_crypto_sound(crypto_request, user)
            
            # Update metadata with crypto sound ID
            metadata.crypto_sound_id = crypto_response.crypto_sound_id
            
            # 3. Lyric Generation (if requested)
            lyric_response = None
            if request.include_lyrics:
                lyric_request = LyricGenerationRequest(
                    theme="digital legacy",
                    emotional_tone=request.emotional_seeds[0] if request.emotional_seeds else "reflective",
                    cryptographic_references=request.cryptographic_elements
                )
                lyric_response = generate_lyrics_endpoint(lyric_request, user)
                
                # Update metadata with lyric ID
                metadata.lyric_id = lyric_response.lyric_id
            
            # 4. Visual Generation (if requested)
            visual_response = None
            if request.include_album_art:
                visual_request = VisualGenerationRequest(
                    title=request.title,
                    themes=["nocturnal", "cyberpunk", "ethereal"]
                )
                visual_response = generate_visual(visual_request, user)
                
                # Update metadata with visual ID
                metadata.visual_id = visual_response.visual_id
            
            # 5. Generate the actual music using existing suno_music API
            from app.apis.suno_music import generate_music, GenerateMusicRequest
            
            # Enhanced description with nocturnal/darksynthwave elements
            enhanced_description = f"A nocturnal elegy in darksynthwave style for '{request.title}': {request.concept_description}. Include heavy atmospheric synths, retro electronic elements, dark ambience, and cyberpunk influences."
            
            # Adjust description based on parameters
            if request.use_hex_encoder:
                enhanced_description += " Incorporate hexagonal harmonic patterns and geometric structured progressions."
                
            if request.crypto_source == "Bitcoin":
                enhanced_description += " Use Bitcoin-inspired hash patterns with digital minimalism."
            elif request.crypto_source == "Ethereum":
                enhanced_description += " Use Ethereum-inspired layered complexity and smart-contract-like transitions."
                
            # Adjust based on crypto depth
            if request.crypto_depth > 7:
                enhanced_description += " Maximize cryptographic elements with deep integration into the composition structure."
            elif request.crypto_depth < 3:
                enhanced_description += " Use subtle cryptographic influences that enhance without dominating the composition."
            
            
            music_request = GenerateMusicRequest(
                concept_id=f"darksynthwave_{elegy_id}",
                concept_name=f"Nocturnal Elegy: {request.title}",
                concept_description=enhanced_description,
                profile_id=request.profile_id,
                mood="melancholic", 
                genre="electronic",
                duration=min(request.duration_seconds, 60) # Cap at 60 seconds for demo
            )
            
            music_response = generate_music(music_request, user)
            
            # Update metadata with music ID
            metadata.music_id = music_response.music_id
            
            # Final response
            final_response = NocturnalElegyResponse(
                elegy_id=elegy_id,
                title=request.title,
                status="completed",
                creation_stage="completed",
                audio_url=music_response.audio_url,
                lyrics=lyric_response.verses + [lyric_response.chorus] if lyric_response else None,
                album_art_url=visual_response.image_url if visual_response else None,
                spectral_analysis={
                    "harmonic_structure": spectral_response.harmonic_structure,
                    "tonal_qualities": spectral_response.tonal_qualities
                },
                crypto_elements={
                    "emotion_mapping": crypto_response.emotion_mapping,
                    "encrypted_patterns": [p["pattern_name"] for p in crypto_response.encrypted_patterns]
                },
                parameters={
                    "influenceRatio": request.influence_ratio,
                    "cryptoDepth": request.crypto_depth,
                    "cryptoSource": request.crypto_source,
                    "useHexEncoder": request.use_hex_encoder,
                    "emotionalSeeds": request.emotional_seeds
                },
                timestamp=datetime.now().isoformat()
            )
            
            # Update status in metadata
            metadata.status = "completed"
            metadata.completed_at = datetime.now().isoformat()
            
            # Store the complete record
            db.storage.json.put(f"elegy_{elegy_id}", {
                "metadata": metadata.dict(),
                "response": final_response.dict(),
                "components": {
                    "spectral_dna": spectral_response.dict(),
                    "crypto_sound": crypto_response.dict(),
                    "lyrics": lyric_response.dict() if lyric_response else None,
                    "visual": visual_response.dict() if visual_response else None,
                    "music": music_response.dict() if music_response else None
                }
            })
            
            return final_response
        
        return initial_response
    except Exception as e:
        print(f"Error generating nocturnal elegy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate nocturnal elegy: {str(e)}")

@router.get("/{elegy_id}")
def get_nocturnal_elegy(elegy_id: str, user: AuthorizedUser) -> NocturnalElegyResponse:
    """Get the status and details of a nocturnal elegy generation"""
    try:
        try:
            elegy_data = db.storage.json.get(f"elegy_{elegy_id}")
        except Exception:
            raise HTTPException(status_code=404, detail=f"Nocturnal elegy with ID {elegy_id} not found")
        
        return NocturnalElegyResponse(**elegy_data["response"])
    except Exception as e:
        print(f"Error getting nocturnal elegy: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get nocturnal elegy: {str(e)}")

@router.get("/by-profile/{profile_id}")
def get_elegies_by_profile(profile_id: str, user: AuthorizedUser) -> List[NocturnalElegyResponse]:
    """Get all nocturnal elegies created by a specific profile"""
    try:
        # List all files in storage with 'elegy_' prefix
        all_files = db.storage.json.list()
        elegies = []
        
        for file in all_files:
            if file.name.startswith("elegy_"):
                try:
                    elegy_data = db.storage.json.get(file.name)
                    if elegy_data["metadata"].get("profile_id") == profile_id:
                        elegies.append(NocturnalElegyResponse(**elegy_data["response"]))
                except Exception as e:
                    print(f"Error processing elegy {file.name}: {e}")
        
        return elegies
    except Exception as e:
        print(f"Error getting elegies by profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get elegies by profile: {str(e)}")
