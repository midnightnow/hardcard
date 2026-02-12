from datetime import datetime
import uuid
import random
import time
from typing import List, Dict, Optional, Any, Union

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.auth import AuthorizedUser
import databutton as db
from app.env import Mode, mode


# Define the router
router = APIRouter(prefix="/enlightened-dj")


# --- Data Models ---

class TrackSegment(BaseModel):
    """Represents a segment of a track with musical characteristics"""
    start_time: float  # in seconds
    end_time: float  # in seconds
    energy: float = Field(0.5, ge=0.0, le=1.0)  # normalized energy level
    key: str  # musical key (e.g., "C#m")
    tempo: float  # in BPM
    dominant_frequencies: List[float] = []  # in Hz
    spectral_centroid: float = 0.0  # in Hz
    beat_positions: List[float] = []  # positions of beats in seconds
    lyrics: Optional[str] = None  # lyrics in this segment if available
    mood_vector: Optional[Dict[str, float]] = None  # emotional mood analysis


class Track(BaseModel):
    """Represents a track for the DJ system"""
    id: str
    title: str
    artist: Optional[str] = None
    audio_url: str
    waveform_data: Optional[List[float]] = None  # visualization data
    duration: float  # in seconds
    segments: List[TrackSegment] = []  # analysis segments
    bpm: Optional[float] = None  # overall track BPM
    key: Optional[str] = None  # overall track key
    energy_profile: Optional[List[float]] = None  # energy over time
    lyrical_themes: Optional[Dict[str, float]] = None  # theme analysis results
    timestamp: str


class DJTransition(BaseModel):
    """Represents a transition between two tracks"""
    id: str
    source_track_id: str
    target_track_id: str
    transition_type: str  # e.g., "beatmatch", "harmonic", "energy", "lyrical"
    start_time_source: float  # seconds into source track
    end_time_source: float
    start_time_target: float  # seconds into target track
    end_time_target: float
    transition_duration: float  # in seconds
    crossfade_curve: str = "linear"  # crossfade type
    harmonic_compatibility: float = Field(0.0, ge=0.0, le=1.0)  # how well the keys match
    rhythmic_compatibility: float = Field(0.0, ge=0.0, le=1.0)  # how well the beats align
    lyrical_compatibility: float = Field(0.0, ge=0.0, le=1.0)  # how well the lyrics flow
    timestamp: str


class AnalyzeTrackRequest(BaseModel):
    """Request to analyze a track for DJ features"""
    track_id: str
    audio_url: str
    title: str
    artist: Optional[str] = None
    include_waveform: bool = True
    include_beat_detection: bool = True
    include_key_detection: bool = True
    include_spectral_analysis: bool = True
    include_lyrical_analysis: bool = True
    segment_duration: float = 5.0  # analyze in segments of this duration


class AnalyzeTrackResponse(BaseModel):
    """Results of track analysis"""
    track_id: str
    status: str  # "completed", "processing", "failed"
    track: Optional[Track] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None  # in seconds
    timestamp: str


class CreateTransitionRequest(BaseModel):
    """Request to create a transition between two tracks"""
    source_track_id: str
    target_track_id: str
    transition_type: str = "auto"  # "auto", "beatmatch", "harmonic", "energy", "lyrical"
    preferred_duration: Optional[float] = None  # in seconds
    source_start_at: Optional[float] = None  # seconds into source, None = auto
    target_start_at: Optional[float] = None  # seconds into target, None = auto
    energy_trajectory: Optional[str] = "maintain"  # "maintain", "increase", "decrease"
    lyrical_continuity: bool = True  # try to maintain lyrical continuity


class CreateTransitionResponse(BaseModel):
    """Results of transition creation"""
    transition_id: str
    status: str  # "completed", "processing", "failed"
    transition: Optional[DJTransition] = None
    error: Optional[str] = None
    audio_preview_url: Optional[str] = None  # URL to hear transition preview
    waveform_preview: Optional[Dict[str, Any]] = None  # visual preview data
    timestamp: str


class MixRequest(BaseModel):
    """Request to mix multiple tracks in sequence"""
    track_ids: List[str]
    mix_name: str
    transition_duration: Optional[float] = None  # in seconds, None = auto
    energy_profile: Optional[str] = "dynamic"  # "dynamic", "building", "constant"
    theme_continuity: Optional[bool] = True  # maintain thematic continuity
    target_duration: Optional[float] = None  # desired duration in seconds
    include_visualization: bool = True


class MixResponse(BaseModel):
    """Results of mix creation"""
    mix_id: str
    status: str  # "completed", "processing", "failed"
    audio_url: Optional[str] = None
    tracks: List[str] = []  # track IDs in order
    transitions: List[str] = []  # transition IDs in order
    duration: Optional[float] = None  # total duration in seconds
    waveform_data: Optional[Dict[str, Any]] = None
    visualization_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str


class LyricalThemeAnalysisRequest(BaseModel):
    """Request to analyze lyrical themes and flow"""
    track_id: str
    lyrics: Optional[str] = None  # Supply lyrics directly or use track_id to fetch


class LyricalThemeAnalysisResponse(BaseModel):
    """Results of lyrical analysis"""
    track_id: str
    themes: Dict[str, float] = {}  # theme name -> strength
    semantic_flow: List[Dict[str, Any]] = []  # semantic evolution over time
    key_phrases: List[str] = []
    emotional_trajectory: Dict[str, List[float]] = {}  # emotion -> values over time
    narrative_connections: List[Dict[str, Any]] = []  # potential connections to other tracks
    timestamp: str


# --- Mock functions for development ---

def mock_analyze_audio(audio_url: str, include_beat_detection: bool = True, 
                      include_key_detection: bool = True) -> Dict[str, Any]:
    """Mock audio analysis function for development"""
    # In a real implementation, this would use a DSP library like librosa
    analysis = {
        "duration": random.uniform(180, 360),
        "waveform_data": [random.uniform(0, 1) for _ in range(100)],  # Simplified
        "segments": []
    }
    
    if include_beat_detection:
        bpm = random.uniform(80, 140)
        analysis["bpm"] = bpm
        # Generate fake beat positions
        beat_interval = 60 / bpm  # seconds per beat
        num_beats = int(analysis["duration"] / beat_interval)
        analysis["beat_positions"] = [i * beat_interval for i in range(num_beats)]
    
    if include_key_detection:
        keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        modes = ["maj", "min"]
        analysis["key"] = random.choice(keys) + random.choice(modes)
    
    # Create segments
    segment_duration = 5.0
    num_segments = int(analysis["duration"] / segment_duration)
    
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = min((i + 1) * segment_duration, analysis["duration"])
        
        segment = {
            "start_time": start_time,
            "end_time": end_time,
            "energy": random.uniform(0.3, 0.9),
            "key": analysis.get("key", random.choice(["Am", "C", "Gm", "F"])),
            "tempo": analysis.get("bpm", random.uniform(80, 140)),
            "dominant_frequencies": [random.uniform(80, 2000) for _ in range(3)],
            "spectral_centroid": random.uniform(500, 3000),
            "beat_positions": [p for p in analysis.get("beat_positions", []) 
                             if p >= start_time and p < end_time]
        }
        analysis["segments"].append(segment)
    
    # Generate an energy profile (simplified)
    num_points = 50
    analysis["energy_profile"] = [random.uniform(0.2, 0.9) for _ in range(num_points)]
    
    return analysis


def mock_analyze_lyrics(lyrics: str) -> Dict[str, Any]:
    """Mock lyrical analysis function for development"""
    # In a real implementation, this would use NLP and sentiment analysis
    themes = {
        "love": random.uniform(0, 1),
        "nostalgia": random.uniform(0, 1),
        "hope": random.uniform(0, 1),
        "loss": random.uniform(0, 1),
        "introspection": random.uniform(0, 1),
        "transcendence": random.uniform(0, 1),
        "awakening": random.uniform(0, 1),
        "enlightenment": random.uniform(0, 1),
        "timelessness": random.uniform(0, 1),
        "cosmic": random.uniform(0, 1)
    }
    
    # Normalize to sum to 1.0
    total = sum(themes.values())
    if total > 0:
        themes = {k: v/total for k, v in themes.items()}
    
    # Mock semantic flow and emotional trajectory
    flow_length = 10  # number of semantic points in the flow
    semantic_flow = [
        {
            "position": i / flow_length,
            "themes": {k: random.uniform(0, v*1.5) for k, v in themes.items()},
            "intensity": random.uniform(0.2, 0.9)
        } 
        for i in range(flow_length)
    ]
    
    # Generate mock key phrases
    potential_phrases = [
        "eternal night", "digital dawn", "memory fragments", 
        "neon reflections", "synthetic dreams", "fractured time",
        "cybernetic pulse", "quantum echoes", "harmonic convergence",
        "temporal displacement", "stellar resonance", "cosmic harmony"
    ]
    key_phrases = random.sample(potential_phrases, k=min(5, len(potential_phrases)))
    
    # Emotional trajectory
    emotions = ["joy", "sadness", "anticipation", "contemplation", "transcendence", "revelation", "epiphany", "wonder"]
    trajectory_length = 20
    emotional_trajectory = {
        emotion: [random.uniform(0, 1) for _ in range(trajectory_length)]
        for emotion in emotions
    }
    
    # Generate potential narrative connections
    narrative_connections = [
        {
            "theme": theme,
            "strength": strength,
            "connection_types": [
                {"type": "contrast", "probability": random.uniform(0, 1)},
                {"type": "continuation", "probability": random.uniform(0, 1)},
                {"type": "expansion", "probability": random.uniform(0, 1)},
                {"type": "transformation", "probability": random.uniform(0, 1)}
            ]
        }
        for theme, strength in sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]  # Top 3 themes
    ]
    
    return {
        "themes": themes,
        "semantic_flow": semantic_flow,
        "key_phrases": key_phrases,
        "emotional_trajectory": emotional_trajectory,
        "narrative_connections": narrative_connections
    }


# --- API Endpoints ---

@router.post("/analyze-track")
def analyze_track(request: AnalyzeTrackRequest, user: AuthorizedUser) -> AnalyzeTrackResponse:
    """Analyze a track for DJ features including tempo, key, spectrum, and lyrics"""
    try:
        track_id = request.track_id
        start_time = time.time()
        
        # Check if analysis already exists
        try:
            existing = db.storage.json.get(f"enlightened_dj_track_{track_id}")
            if existing:
                return AnalyzeTrackResponse(
                    track_id=track_id,
                    status="completed",
                    track=Track(**existing),
                    processing_time=0.0,
                    timestamp=datetime.now().isoformat()
                )
        except:
            pass  # Continue with analysis if not found
        
        # Perform audio analysis (mock for development)
        audio_analysis = mock_analyze_audio(
            request.audio_url,
            include_beat_detection=request.include_beat_detection,
            include_key_detection=request.include_key_detection
        )
        
        # For development, simulate processing time
        if mode == Mode.DEV:
            time.sleep(0.5)  # Simulate processing time
        
        # Create track object
        track = Track(
            id=track_id,
            title=request.title,
            artist=request.artist,
            audio_url=request.audio_url,
            duration=audio_analysis["duration"],
            waveform_data=audio_analysis["waveform_data"] if request.include_waveform else None,
            bpm=audio_analysis.get("bpm"),
            key=audio_analysis.get("key"),
            energy_profile=audio_analysis.get("energy_profile"),
            segments=[TrackSegment(**segment) for segment in audio_analysis["segments"]],
            timestamp=datetime.now().isoformat()
        )
        
        # Add lyrical analysis if requested
        if request.include_lyrical_analysis:
            # In a real implementation, lyrics would be fetched from a service or provided
            mock_lyrics = "In the glow of night, digital dreams take flight. Neon reflections guide our way through endless city lights."
            lyrical_analysis = mock_analyze_lyrics(mock_lyrics)
            
            # Update segments with lyrics (simplified)
            segment_count = len(track.segments)
            if segment_count > 0:
                # Split lyrics evenly among segments for mock purposes
                words = mock_lyrics.split()
                words_per_segment = max(1, len(words) // segment_count)
                
                for i, segment in enumerate(track.segments):
                    start_word = i * words_per_segment
                    end_word = min(start_word + words_per_segment, len(words))
                    if start_word < len(words):
                        segment_words = words[start_word:end_word]
                        segment.lyrics = " ".join(segment_words)
                        
                        # Also add mood vector from lyrical analysis
                        if i < len(lyrical_analysis["semantic_flow"]):
                            segment.mood_vector = lyrical_analysis["semantic_flow"][i]["themes"]
            
            # Add overall lyrical themes
            track.lyrical_themes = lyrical_analysis["themes"]
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Store the track analysis
        db.storage.json.put(f"enlightened_dj_track_{track_id}", track.dict())
        
        return AnalyzeTrackResponse(
            track_id=track_id,
            status="completed",
            track=track,
            processing_time=processing_time,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"Error analyzing track: {str(e)}")
        return AnalyzeTrackResponse(
            track_id=request.track_id,
            status="failed",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )


@router.post("/create-transition")
def create_transition(request: CreateTransitionRequest, user: AuthorizedUser) -> CreateTransitionResponse:
    """Create a transition between two tracks"""
    try:
        transition_id = f"transition_{uuid.uuid4()}"
        
        # Retrieve the source and target tracks
        try:
            source_track_dict = db.storage.json.get(f"enlightened_dj_track_{request.source_track_id}")
            target_track_dict = db.storage.json.get(f"enlightened_dj_track_{request.target_track_id}")
            
            if not source_track_dict or not target_track_dict:
                raise ValueError("Source or target track not found. Please analyze tracks first.")
                
            source_track = Track(**source_track_dict)
            target_track = Track(**target_track_dict)
        except Exception as e:
            raise ValueError(f"Error retrieving tracks: {str(e)}")
        
        # For development, simulate processing time
        if mode == Mode.DEV:
            time.sleep(0.8)  # Simulate processing time
        
        # Calculate transition parameters
        # In a real implementation, this would use sophisticated algorithms
        # to find the best transition points and methods
        
        # Set defaults and calculate compatibilities
        source_duration = source_track.duration
        target_duration = target_track.duration
        
        # Default to source track end if not specified
        source_start = request.source_start_at or max(0, source_duration - 30)
        
        # Default transition duration based on BPM compatibility
        source_bpm = source_track.bpm or 120
        target_bpm = target_track.bpm or 120
        bpm_diff = abs(source_bpm - target_bpm)
        
        transition_duration = request.preferred_duration or (
            8 if bpm_diff < 10 else  # Short transition for similar BPM
            16 if bpm_diff < 30 else  # Medium transition for moderate difference
            24  # Longer transition for large BPM difference
        )
        
        # Calculate end time of source track in transition
        source_end = min(source_start + transition_duration, source_duration)
        
        # Target track should start at beginning if not specified
        target_start = request.target_start_at or 0
        target_end = min(target_start + transition_duration, target_duration)
        
        # Calculate compatibilities
        source_key = source_track.key or "C"
        target_key = target_track.key or "C"
        
        # Simple harmonic compatibility (would be more sophisticated in real implementation)
        # This checks if keys are identical or closely related
        harmonic_compatibility = 1.0 if source_key == target_key else (
            0.7 if source_key[0] == target_key[0] else  # Same root note
            0.5  # Different keys
        )
        
        # Rhythmic compatibility based on BPM
        max_bpm_diff = 50  # Maximum expected BPM difference
        rhythmic_compatibility = max(0, 1 - (bpm_diff / max_bpm_diff))
        
        # Lyrical compatibility (mock implementation)
        lyrical_compatibility = random.uniform(0.3, 0.9) if request.lyrical_continuity else 0.5
        
        # Create the transition
        transition = DJTransition(
            id=transition_id,
            source_track_id=request.source_track_id,
            target_track_id=request.target_track_id,
            transition_type=request.transition_type,
            start_time_source=source_start,
            end_time_source=source_end,
            start_time_target=target_start,
            end_time_target=target_end,
            transition_duration=transition_duration,
            crossfade_curve="linear",  # Could vary based on genre/mood
            harmonic_compatibility=harmonic_compatibility,
            rhythmic_compatibility=rhythmic_compatibility,
            lyrical_compatibility=lyrical_compatibility,
            timestamp=datetime.now().isoformat()
        )
        
        # Store the transition
        db.storage.json.put(f"enlightened_dj_transition_{transition_id}", transition.dict())
        
        # Generate a mock waveform preview
        source_wave = source_track.waveform_data or [random.uniform(0, 1) for _ in range(100)]
        target_wave = target_track.waveform_data or [random.uniform(0, 1) for _ in range(100)]
        
        # Create a simple visualization of the transition
        waveform_preview = {
            "source": source_wave[-30:],  # Last 30 points of source
            "target": target_wave[:30],  # First 30 points of target
            "crossfade": [max(source_wave[-30:][i] * (1 - i/30), target_wave[:30][i] * (i/30)) 
                          for i in range(30)],
            "markers": [
                {"position": 0, "label": "Transition Start"},
                {"position": 0.5, "label": "Mid-Transition"},
                {"position": 1, "label": "Transition End"}
            ]
        }
        
        return CreateTransitionResponse(
            transition_id=transition_id,
            status="completed",
            transition=transition,
            audio_preview_url=None,  # Would require server-side audio processing
            waveform_preview=waveform_preview,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"Error creating transition: {str(e)}")
        return CreateTransitionResponse(
            transition_id=f"failed_{uuid.uuid4()}",
            status="failed",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )


@router.post("/create-mix")
def create_mix(request: MixRequest, user: AuthorizedUser) -> MixResponse:
    """Create a mix from multiple tracks"""
    try:
        mix_id = f"mix_{uuid.uuid4()}"
        
        # Validate that we have at least 2 tracks
        if len(request.track_ids) < 2:
            raise ValueError("A mix requires at least 2 tracks")
        
        # Retrieve all the tracks
        tracks = []
        for track_id in request.track_ids:
            try:
                track_dict = db.storage.json.get(f"enlightened_dj_track_{track_id}")
                if not track_dict:
                    raise ValueError(f"Track {track_id} not found. Please analyze it first.")
                tracks.append(Track(**track_dict))
            except Exception as e:
                print(f"Error loading track {track_id}: {str(e)}")
                raise ValueError(f"Error loading track {track_id}: {str(e)}")
        
        # For development, simulate processing time
        if mode == Mode.DEV:
            time.sleep(len(request.track_ids) * 0.5)  # Longer for more tracks
        
        # Create transitions between tracks
        transitions = []
        for i in range(len(tracks) - 1):
            source_track = tracks[i]
            target_track = tracks[i + 1]
            
            # Create a transition request
            transition_request = CreateTransitionRequest(
                source_track_id=source_track.id,
                target_track_id=target_track.id,
                transition_type="auto",
                preferred_duration=request.transition_duration,
                energy_trajectory=request.energy_profile,
                lyrical_continuity=request.theme_continuity,
            )
            
            # Call the transition creation function
            transition_response = create_transition(transition_request, user)
            
            if transition_response.status == "failed":
                raise ValueError(f"Failed to create transition between tracks {i} and {i+1}: "
                                f"{transition_response.error}")
                
            transitions.append(transition_response.transition)
        
        # Calculate total duration of the mix
        total_duration = 0
        
        # Add first track's full duration
        total_duration += tracks[0].duration
        
        # For each transition, add target track duration minus overlap
        for i, transition in enumerate(transitions):
            # Add target track's duration
            total_duration += tracks[i+1].duration
            # Subtract the overlap in the transition
            overlap = transition.end_time_source - transition.start_time_source
            total_duration -= overlap
        
        # Generate visualization data (simplified)
        if request.include_visualization:
            visualization_data = {
                "tracks": [{
                    "id": track.id,
                    "title": track.title,
                    "artist": track.artist,
                    "duration": track.duration,
                    "waveform": track.waveform_data,
                    "key": track.key,
                    "bpm": track.bpm
                } for track in tracks],
                "transitions": [{
                    "id": t.id,
                    "source_id": t.source_track_id,
                    "target_id": t.target_track_id,
                    "type": t.transition_type,
                    "duration": t.transition_duration,
                    "harmonic_compatibility": t.harmonic_compatibility,
                    "rhythmic_compatibility": t.rhythmic_compatibility,
                    "lyrical_compatibility": t.lyrical_compatibility
                } for t in transitions],
                "timeline": {
                    "total_duration": total_duration,
                    "segments": []
                }
            }
            
            # Build a timeline representation
            current_time = 0
            timeline_segments = []
            
            # First track
            if transitions:
                first_transition = transitions[0]
                timeline_segments.append({
                    "type": "track",
                    "track_id": tracks[0].id,
                    "start_time": 0,
                    "end_time": first_transition.start_time_source,
                    "duration": first_transition.start_time_source
                })
                current_time += first_transition.start_time_source
            else:
                # Only one track, no transitions
                timeline_segments.append({
                    "type": "track",
                    "track_id": tracks[0].id,
                    "start_time": 0,
                    "end_time": tracks[0].duration,
                    "duration": tracks[0].duration
                })
                current_time += tracks[0].duration
            
            # Add transitions and subsequent tracks
            for i, transition in enumerate(transitions):
                # Add transition
                transition_duration = transition.end_time_source - transition.start_time_source
                timeline_segments.append({
                    "type": "transition",
                    "transition_id": transition.id,
                    "start_time": current_time,
                    "end_time": current_time + transition_duration,
                    "duration": transition_duration,
                    "source_track_id": transition.source_track_id,
                    "target_track_id": transition.target_track_id
                })
                current_time += transition_duration
                
                # Add next track (if not the last transition)
                if i < len(transitions) - 1:
                    next_transition = transitions[i + 1]
                    track_duration = next_transition.start_time_source
                    timeline_segments.append({
                        "type": "track",
                        "track_id": next_transition.source_track_id,
                        "start_time": current_time,
                        "end_time": current_time + track_duration,
                        "duration": track_duration
                    })
                    current_time += track_duration
                else:
                    # Last track after last transition
                    last_track = tracks[-1]
                    remaining_duration = last_track.duration - transition.end_time_target
                    timeline_segments.append({
                        "type": "track",
                        "track_id": last_track.id,
                        "start_time": current_time,
                        "end_time": current_time + remaining_duration,
                        "duration": remaining_duration
                    })
                    current_time += remaining_duration
            
            visualization_data["timeline"]["segments"] = timeline_segments
        else:
            visualization_data = None
            
        # Create the mix response
        mix_response = MixResponse(
            mix_id=mix_id,
            status="completed",
            tracks=[t.id for t in tracks],
            transitions=[t.id for t in transitions],
            duration=total_duration,
            visualization_data=visualization_data,
            # These would be created through audio processing in a real implementation
            audio_url=None,  # Would require server-side audio processing
            waveform_data=None,  # Would require processing the full mix
            timestamp=datetime.now().isoformat()
        )
        
        # Store the mix data
        db.storage.json.put(f"enlightened_dj_mix_{mix_id}", mix_response.dict())
        
        return mix_response
    except Exception as e:
        print(f"Error creating mix: {str(e)}")
        return MixResponse(
            mix_id=f"failed_{uuid.uuid4()}",
            status="failed",
            error=str(e),
            timestamp=datetime.now().isoformat()
        )


@router.post("/analyze-lyrics")
def analyze_lyrics(request: LyricalThemeAnalysisRequest, user: AuthorizedUser) -> LyricalThemeAnalysisResponse:
    """Analyze the lyrical themes and flow of a track"""
    try:
        # If lyrics not provided, try to find them from the track
        lyrics = request.lyrics
        if not lyrics:
            try:
                track_dict = db.storage.json.get(f"enlightened_dj_track_{request.track_id}")
                if track_dict:
                    track = Track(**track_dict)
                    # Extract lyrics from segments
                    segment_lyrics = [s.lyrics for s in track.segments if s.lyrics]
                    lyrics = " ".join(segment_lyrics)
            except:
                pass
        
        # If still no lyrics, use placeholder text
        if not lyrics:
            lyrics = "In the glow of night, digital dreams take flight. Neon reflections guide our way through endless city lights."
        
        # Perform lyrical analysis
        analysis = mock_analyze_lyrics(lyrics)
        
        # For development, simulate processing time
        if mode == Mode.DEV:
            time.sleep(0.3)  # Simulate processing time
        
        # Create and return response
        response = LyricalThemeAnalysisResponse(
            track_id=request.track_id,
            themes=analysis["themes"],
            semantic_flow=analysis["semantic_flow"],
            key_phrases=analysis["key_phrases"],
            emotional_trajectory=analysis["emotional_trajectory"],
            narrative_connections=analysis.get("narrative_connections", []),
            timestamp=datetime.now().isoformat()
        )
        
        # Store the analysis
        db.storage.json.put(f"enlightened_dj_lyrics_{request.track_id}", response.dict())
        
        return response
    except Exception as e:
        print(f"Error analyzing lyrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze lyrics: {str(e)}")


@router.get("/track/{track_id}")
def get_track(track_id: str, user: AuthorizedUser) -> Track:
    """Get a track by ID"""
    try:
        track_dict = db.storage.json.get(f"enlightened_dj_track_{track_id}")
        if not track_dict:
            raise HTTPException(status_code=404, detail=f"Track {track_id} not found")
        
        return Track(**track_dict)
    except Exception as e:
        print(f"Error retrieving track {track_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve track: {str(e)}")


@router.get("/transition/{transition_id}")
def get_transition(transition_id: str, user: AuthorizedUser) -> DJTransition:
    """Get a transition by ID"""
    try:
        transition_dict = db.storage.json.get(f"enlightened_dj_transition_{transition_id}")
        if not transition_dict:
            raise HTTPException(status_code=404, detail=f"Transition {transition_id} not found")
        
        return DJTransition(**transition_dict)
    except Exception as e:
        print(f"Error retrieving transition {transition_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve transition: {str(e)}")


@router.get("/mix/{mix_id}")
def get_mix(mix_id: str, user: AuthorizedUser) -> MixResponse:
    """Get a mix by ID"""
    try:
        mix_dict = db.storage.json.get(f"enlightened_dj_mix_{mix_id}")
        if not mix_dict:
            raise HTTPException(status_code=404, detail=f"Mix {mix_id} not found")
        
        return MixResponse(**mix_dict)
    except Exception as e:
        print(f"Error retrieving mix {mix_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve mix: {str(e)}")
