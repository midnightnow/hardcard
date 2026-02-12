import librosa
import numpy as np
from typing import Dict, Any, List, Optional, Union
import requests
import tempfile
import os
import databutton as db
from fastapi import APIRouter
from pydantic import BaseModel

# Import models from remix_engine to avoid duplicate definitions
from app.apis.remix_engine import TrackSource, TrackAnalysis

# Router Configuration
router = APIRouter()

@router.post("/analyze-remix-track")
def analyze_remix_track(track: TrackSource) -> TrackAnalysis:
    """Analyze a track to extract musical properties for remixing"""
    analyzer = AudioAnalyzer()
    return analyzer.analyze_track(track)


class AudioAnalyzer:
    """Audio analysis class for extracting musical properties from audio files"""
    
    def __init__(self):
        """Initialize the audio analyzer"""
        self.supported_formats = [".mp3", ".wav", ".ogg", ".flac"]
    
    def analyze_track(self, track: TrackSource) -> TrackAnalysis:
        """Analyze a track to extract musical properties
        
        Args:
            track: The track source information
            
        Returns:
            TrackAnalysis object with extracted musical properties
        """
        # Initialize the analysis result with the track ID
        analysis = TrackAnalysis(id=track.id)
        
        try:
            # Get audio data based on source type
            audio_path = self._get_audio_data(track)
            if not audio_path:
                analysis.error = "Could not retrieve audio data"
                return analysis
                
            # Load the audio file with librosa
            try:
                y, sr = librosa.load(audio_path, sr=None)
            except Exception as e:
                analysis.error = f"Error loading audio file: {str(e)}"
                return analysis
                
            # Extract tempo
            try:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                analysis.tempo = round(float(tempo), 2)
            except Exception as e:
                print(f"Error detecting tempo: {str(e)}")
            
            # Extract key
            try:
                key = self._estimate_key(y, sr)
                analysis.key = key
            except Exception as e:
                print(f"Error detecting key: {str(e)}")
            
            # Extract time signature (simplified to 4/4 or 3/4)
            try:
                time_sig = self._estimate_time_signature(y, sr)
                analysis.time_signature = time_sig
            except Exception as e:
                print(f"Error detecting time signature: {str(e)}")
            
            # Calculate duration
            analysis.duration = float(len(y) / sr)
            
            # Estimate mood and genre (simplified implementation)
            try:
                mood, genre = self._estimate_mood_and_genre(y, sr)
                analysis.mood = mood
                analysis.genre = genre
            except Exception as e:
                print(f"Error estimating mood and genre: {str(e)}")
            
            # Remove the temporary file if it was created
            if audio_path and os.path.exists(audio_path) and track.source_type != "file":
                os.remove(audio_path)
            
            return analysis
            
        except Exception as e:
            analysis.error = f"Analysis failed: {str(e)}"
            return analysis
    
    def _get_audio_data(self, track: TrackSource) -> Optional[str]:
        """Get audio data from various sources and store to temp file if needed"""
        if track.source_type == "vault" and track.id:
            # Fetch from Vault storage
            try:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                audio_data = db.storage.binary.get(track.id)
                temp_file.write(audio_data)
                temp_file.close()
                return temp_file.name
            except Exception as e:
                print(f"Failed to retrieve audio from vault: {str(e)}")
                return None
        
        elif track.source_type == "url" and track.url:
            # Download from URL
            try:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                response = requests.get(track.url, stream=True)
                response.raise_for_status()
                
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                    
                temp_file.close()
                return temp_file.name
            except Exception as e:
                print(f"Failed to download audio from URL: {str(e)}")
                return None
        
        elif track.source_type == "suno" and track.id:
            # This would need to be implemented based on how Suno files are accessed
            # For now we'll return None
            return None
            
        elif track.source_type == "file" and track.id:
            # Local file path
            if os.path.exists(track.id):
                return track.id
            return None
            
        return None
    
    def _estimate_key(self, y: np.ndarray, sr: int) -> str:
        """Estimate the musical key of the audio
        
        Args:
            y: Audio time series
            sr: Sampling rate
            
        Returns:
            String representing the estimated key (e.g., "C major", "A minor")
        """
        # Extract harmonic content
        y_harmonic = librosa.effects.harmonic(y)
        
        # Compute chroma features
        chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
        
        # Average the chroma vectors
        chroma_avg = np.mean(chroma, axis=1)
        
        # Get the key with the highest energy
        key_idx = np.argmax(chroma_avg)
        
        # Map the index to a key name
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = key_names[key_idx]
        
        # Determine if it's major or minor
        # This is a simplified approach - in practice this requires more sophisticated analysis
        # For now, we'll use a heuristic based on the relative minor chroma values
        minor_idx = (key_idx + 9) % 12  # Relative minor is 9 semitones up
        is_minor = chroma_avg[minor_idx] > 0.7 * chroma_avg[key_idx]
        
        return f"{key} {'minor' if is_minor else 'major'}"
    
    def _estimate_time_signature(self, y: np.ndarray, sr: int) -> str:
        """Estimate the time signature of the audio
        
        Args:
            y: Audio time series
            sr: Sampling rate
            
        Returns:
            String representing the estimated time signature (e.g., "4/4", "3/4")
        """
        # This is a simplified implementation
        # In practice, time signature detection is complex and would require more advanced techniques
        
        # Extract onset envelope
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Get tempo and beats
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        # Compute beat intervals
        if len(beats) > 2:
            beat_intervals = np.diff(beats)
            
            # Analyze grouping patterns (simplified)
            # Count how many groups of 3 vs 4 beats fit better
            groups_of_3 = np.sum(beat_intervals[::3]) if len(beat_intervals) >= 3 else 0
            groups_of_4 = np.sum(beat_intervals[::4]) if len(beat_intervals) >= 4 else 0
            
            if groups_of_3 < groups_of_4:
                return "4/4"  # Most common time signature
            else:
                return "3/4"
        
        # Default to 4/4 if we can't determine
        return "4/4"
    
    def _estimate_mood_and_genre(self, y: np.ndarray, sr: int) -> tuple:
        """Estimate the mood and genre of the audio
        
        Args:
            y: Audio time series
            sr: Sampling rate
            
        Returns:
            Tuple of (mood, genres) where mood is a string and genres is a list of strings
        """
        # This is a simplified implementation
        # In practice, mood and genre detection would use machine learning models
        
        # Extract features
        spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr).mean()
        spec_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr).mean()
        zcr = librosa.feature.zero_crossing_rate(y).mean()
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Simplified mood detection based on features
        # High spectral centroid and ZCR often correlate with 'brightness'
        if spec_centroid > 2000 and zcr > 0.1:
            if tempo > 120:
                mood = "energetic"
            else:
                mood = "bright"
        else:
            if tempo < 90:
                mood = "melancholic"
            else:
                mood = "calm"
        
        # Simplified genre detection
        genres = []
        if tempo > 120:
            if spec_rolloff > 5000:
                genres.append("electronic")
            else:
                genres.append("rock")
        else:
            if spec_centroid < 1500:
                genres.append("ambient")
            else:
                genres.append("pop")
        
        return mood, genres
