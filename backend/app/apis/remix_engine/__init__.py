import librosa
import numpy as np
import soundfile as sf
import tempfile
import os
import databutton as db
from typing import List, Dict, Any, Optional, Union
from fastapi import APIRouter
from pydantic import BaseModel

# Define models here to avoid circular imports
class TrackSource(BaseModel):
    id: str
    url: Optional[str] = None
    source_type: str  # "vault", "upload", "suno", "url"
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TrackAnalysis(BaseModel):
    id: str
    key: Optional[str] = None
    tempo: Optional[float] = None
    time_signature: Optional[str] = None
    mood: Optional[str] = None
    genre: Optional[List[str]] = None
    duration: Optional[float] = None
    compatibility_score: Optional[float] = None
    error: Optional[str] = None

class RemixSettings(BaseModel):
    auto_align: bool = True
    harmonize: bool = True
    fx_chain: Optional[List[Dict[str, Any]]] = None
    track_gains: Optional[Dict[str, float]] = None
    track_volumes: Optional[Dict[str, float]] = None
    track_pans: Optional[Dict[str, float]] = None
    target_key: Optional[str] = None
    target_tempo: Optional[float] = None
    use_stem_separation: bool = False
    style: Optional[str] = None

# Router Configuration
router = APIRouter()

# Import this after defining our models to avoid circular imports
# We'll use a function to conditionally import AudioAnalyzer when needed
def get_audio_analyzer():
    from app.apis.remix_analyzer import AudioAnalyzer
    return AudioAnalyzer()

class RemixEngine:
    """Engine for creating remixes from multiple audio tracks"""
    
    def __init__(self):
        """Initialize the remix engine"""
        self.analyzer = get_audio_analyzer()
        
    def remix(self, 
              track_sources: List[TrackSource], 
              track_analyses: List[Dict[str, Any]],
              settings: RemixSettings) -> Dict[str, Any]:
        """Create a remix from multiple audio tracks
        
        Args:
            track_sources: List of TrackSource objects
            track_analyses: List of track analysis dictionaries
            settings: RemixSettings object with remix parameters
            
        Returns:
            Dictionary with the remix result including audio data
        """
        result = {
            "success": False,
            "message": "",
            "audio_data": None,
            "metadata": {}
        }
        
        try:
            # 1. Load all audio tracks
            tracks_data = self._load_tracks(track_sources)
            if not tracks_data or len(tracks_data) == 0:
                result["message"] = "Failed to load any audio tracks"
                return result
                
            # Map the analyses to their track IDs for easier lookup
            analyses_by_id = {analysis.get("id"): analysis for analysis in track_analyses if "id" in analysis}
            
            # 2. Determine target tempo and key if not specified
            target_tempo, target_key = self._determine_target_parameters(
                tracks_data, analyses_by_id, settings)
                
            # 3. Process each track according to settings
            processed_tracks = []
            for track_id, (y, sr) in tracks_data.items():
                if track_id in analyses_by_id:
                    analysis = analyses_by_id[track_id]
                    processed_y = self._process_track(
                        y, sr, analysis, target_tempo, target_key, settings)
                    processed_tracks.append((processed_y, sr))
            
            # 4. Mix the processed tracks together
            mixed_audio = self._mix_tracks(processed_tracks, settings)
            
            # 5. Apply final master effects
            final_audio = self._apply_master_effects(mixed_audio[0], mixed_audio[1], settings)
            
            # 6. Export to WAV format
            audio_data = self._export_to_wav(final_audio[0], final_audio[1])
            
            # Prepare the result
            result["success"] = True
            result["message"] = "Remix created successfully"
            result["audio_data"] = audio_data
            result["metadata"] = {
                "target_tempo": target_tempo,
                "target_key": target_key,
                "track_count": len(tracks_data),
                "duration": len(final_audio[0]) / final_audio[1]
            }
            
            return result
            
        except Exception as e:
            result["message"] = f"Error creating remix: {str(e)}"
            return result
    
    def _load_tracks(self, track_sources: List[TrackSource]) -> Dict[str, tuple]:
        """Load audio tracks from various sources
        
        Returns a dictionary mapping track IDs to tuples of (audio_data, sample_rate)
        """
        tracks_data = {}
        
        for track in track_sources:
            try:
                # Get audio file path
                audio_path = self.analyzer._get_audio_data(track)
                if not audio_path:
                    print(f"Could not retrieve audio data for track {track.id}")
                    continue
                    
                # Load the audio file
                y, sr = librosa.load(audio_path, sr=None)
                
                # Store the loaded audio
                tracks_data[track.id] = (y, sr)
                
                # Clean up temporary file
                if audio_path and os.path.exists(audio_path) and track.source_type != "file":
                    os.remove(audio_path)
                    
            except Exception as e:
                print(f"Error loading track {track.id}: {str(e)}")
                continue
                
        return tracks_data
    
    def _determine_target_parameters(self, 
                                     tracks_data: Dict[str, tuple],
                                     analyses_by_id: Dict[str, Dict[str, Any]],
                                     settings: RemixSettings) -> tuple:
        """Determine the target tempo and key for the remix"""
        # Use settings if provided
        target_tempo = settings.target_tempo
        target_key = settings.target_key
        
        # If not provided, calculate from the tracks
        if not target_tempo:
            # Average the tempos of all tracks
            tempos = [analysis.get("tempo", 120) for analysis in analyses_by_id.values() 
                     if analysis.get("tempo") is not None]
            if tempos:
                target_tempo = sum(tempos) / len(tempos)
            else:
                target_tempo = 120  # Default tempo
        
        if not target_key:
            # Use the key of the first track or a default
            for analysis in analyses_by_id.values():
                if analysis.get("key") is not None:
                    target_key = analysis.get("key")
                    break
            if not target_key:
                target_key = "C major"  # Default key
        
        return target_tempo, target_key
    
    def _process_track(self, 
                       y: np.ndarray, 
                       sr: int, 
                       analysis: Dict[str, Any],
                       target_tempo: float, 
                       target_key: str,
                       settings: RemixSettings) -> np.ndarray:
        """Process a single track to match the target parameters"""
        # 1. Time-stretch to match target tempo
        if settings.auto_align and analysis.get("tempo") is not None:
            tempo_ratio = target_tempo / analysis.get("tempo")
            if 0.5 <= tempo_ratio <= 2.0:  # Reasonable range
                y = librosa.effects.time_stretch(y, rate=tempo_ratio)
        
        # 2. Pitch-shift to match target key (if harmonize is enabled)
        if settings.harmonize and analysis.get("key") is not None and target_key != analysis.get("key"):
            semitones = self._calculate_key_shift(analysis.get("key"), target_key)
            if semitones != 0:
                y = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)
        
        # 3. Apply track-specific effects from settings
        if settings.fx_chain:
            for fx in settings.fx_chain:
                fx_type = fx.get("type")
                fx_params = fx.get("params", {})
                
                if fx_type == "reverb":
                    # Simple reverb simulation
                    reverb_amount = fx_params.get("amount", 0.3)
                    decay = fx_params.get("decay", 2.0)
                    y = self._apply_reverb(y, sr, reverb_amount, decay)
                    
                elif fx_type == "delay":
                    # Simple delay effect
                    delay_amount = fx_params.get("amount", 0.3)
                    delay_time = fx_params.get("time", 0.25)  # in seconds
                    y = self._apply_delay(y, sr, delay_amount, delay_time)
                    
                elif fx_type == "eq":
                    # Simple EQ (just a high-pass filter for now)
                    cutoff = fx_params.get("cutoff", 200)  # in Hz
                    y = self._apply_highpass_filter(y, sr, cutoff)
        
        # 4. Apply volume adjustment
        track_id = analysis.get("id")
        if settings.track_volumes and track_id in settings.track_volumes:
            volume = settings.track_volumes[track_id]
            y = y * volume
        
        return y
    
    def _calculate_key_shift(self, source_key: str, target_key: str) -> int:
        """Calculate semitones to shift from source key to target key
        
        Args:
            source_key: Source key (e.g., "C major", "A minor")
            target_key: Target key (e.g., "G major", "E minor")
            
        Returns:
            Number of semitones to shift (positive or negative)
        """
        # Parse the keys
        source_note = source_key.split()[0]
        source_mode = "minor" if "minor" in source_key else "major"
        
        target_note = target_key.split()[0]
        target_mode = "minor" if "minor" in target_key else "major"
        
        # Define the chromatic scale
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Find the indices
        source_idx = notes.index(source_note)
        target_idx = notes.index(target_note)
        
        # Calculate the shift
        semitones = target_idx - source_idx
        
        # Adjust for mode change (major to minor or vice versa)
        # This is a simplification - in real music theory, this is more complex
        if source_mode != target_mode:
            if source_mode == "major" and target_mode == "minor":
                semitones -= 3  # Major to relative minor
            else:
                semitones += 3  # Minor to relative major
        
        # Ensure the shift is within -6 to 6 semitones for better quality
        while semitones > 6:
            semitones -= 12
        while semitones < -6:
            semitones += 12
            
        return semitones
    
    def _apply_reverb(self, y: np.ndarray, sr: int, amount: float, decay: float) -> np.ndarray:
        """Apply a simple reverb effect"""
        # This is a very simplified reverb simulation
        # Real reverb would use convolution with an impulse response
        
        # Create a decaying envelope for the reverb tail
        reverb_length = int(sr * decay)
        decay_envelope = np.exp(-np.linspace(0, 5, reverb_length))
        
        # Create the reverb tail
        reverb_tail = np.zeros(len(y) + reverb_length)
        for i in range(len(y)):
            reverb_tail[i:i+reverb_length] += y[i] * decay_envelope
        
        # Mix with the original signal
        y_reverb = np.zeros(len(y))
        y_reverb[:] = y * (1 - amount) + reverb_tail[:len(y)] * amount
        
        return y_reverb
    
    def _apply_delay(self, y: np.ndarray, sr: int, amount: float, delay_time: float) -> np.ndarray:
        """Apply a simple delay effect"""
        # Calculate the delay in samples
        delay_samples = int(sr * delay_time)
        
        # Create the delayed signal
        delayed = np.zeros_like(y)
        if delay_samples < len(y):
            delayed[delay_samples:] = y[:-delay_samples] * amount
        
        # Mix with the original signal
        y_delay = y + delayed
        
        # Normalize to avoid clipping
        max_val = np.max(np.abs(y_delay))
        if max_val > 1.0:
            y_delay = y_delay / max_val
        
        return y_delay
    
    def _apply_highpass_filter(self, y: np.ndarray, sr: int, cutoff: float) -> np.ndarray:
        """Apply a simple high-pass filter"""
        from scipy import signal
        
        # Design a high-pass filter
        nyquist = 0.5 * sr
        normal_cutoff = cutoff / nyquist
        b, a = signal.butter(4, normal_cutoff, btype='high', analog=False)
        
        # Apply the filter
        y_filtered = signal.filtfilt(b, a, y)
        
        return y_filtered
    
    def _mix_tracks(self, tracks: List[tuple], settings: RemixSettings) -> tuple:
        """Mix multiple processed tracks together
        
        Args:
            tracks: List of (audio_data, sample_rate) tuples
            settings: RemixSettings object
            
        Returns:
            Tuple of (mixed_audio, sample_rate)
        """
        if not tracks:
            return (np.zeros(0), 44100)
        
        # Ensure all tracks have the same sample rate
        sr = tracks[0][1]  # Use the first track's sample rate as reference
        resampled_tracks = []
        
        for y, track_sr in tracks:
            if track_sr != sr:
                y = librosa.resample(y, orig_sr=track_sr, target_sr=sr)
            resampled_tracks.append(y)
        
        # Determine the length of the longest track
        max_length = max(len(y) for y in resampled_tracks)
        
        # Extend shorter tracks with silence to match the longest track
        extended_tracks = []
        for y in resampled_tracks:
            if len(y) < max_length:
                extended = np.zeros(max_length)
                extended[:len(y)] = y
                extended_tracks.append(extended)
            else:
                extended_tracks.append(y)
        
        # Mix the tracks together with equal weight
        mix = np.zeros(max_length)
        for y in extended_tracks:
            mix += y
        
        # Normalize to avoid clipping
        max_val = np.max(np.abs(mix))
        if max_val > 1.0:
            mix = mix / max_val
        
        return (mix, sr)
    
    def _apply_master_effects(self, y: np.ndarray, sr: int, settings: RemixSettings) -> tuple:
        """Apply master effects to the final mix
        
        Args:
            y: Audio data
            sr: Sample rate
            settings: RemixSettings object
            
        Returns:
            Tuple of (processed_audio, sample_rate)
        """
        # For now, just apply a simple compression and normalization
        # This is a very simplified mastering process
        
        # Compression (very simple implementation)
        threshold = 0.5
        ratio = 4.0
        makeup_gain = 1.2
        
        # Apply compression
        y_compressed = y.copy()
        mask = np.abs(y) > threshold
        y_compressed[mask] = threshold + (np.abs(y[mask]) - threshold) / ratio * np.sign(y[mask])
        
        # Apply makeup gain
        y_compressed = y_compressed * makeup_gain
        
        # Ensure the signal doesn't clip
        max_val = np.max(np.abs(y_compressed))
        if max_val > 0.99:
            y_compressed = y_compressed / max_val * 0.99
        
        return (y_compressed, sr)
    
    def _export_to_wav(self, y: np.ndarray, sr: int) -> bytes:
        """Export audio data to WAV format
        
        Args:
            y: Audio data
            sr: Sample rate
            
        Returns:
            WAV file as bytes
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            # Write the audio data to the file
            sf.write(tmp_file.name, y, sr, format='wav')
            
            # Read the file as bytes
            tmp_file.close()
            with open(tmp_file.name, 'rb') as f:
                wav_bytes = f.read()
            
            # Clean up
            os.remove(tmp_file.name)
            
            return wav_bytes
