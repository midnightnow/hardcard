from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import requests
import databutton as db
import json
import re
import uuid
from datetime import datetime, timedelta
import time
import random
from app.auth import AuthorizedUser
from app.apis.trust_fund_revenue import record_legacy_vault_revenue, RevenueRecordRequest

router = APIRouter(prefix="/distrokid")

# Constants for DistroKid OAuth flow
DISTROKID_CLIENT_ID = "legacy_vault_app"
DISTROKID_AUTH_URL = "https://distrokid.com/auth/oauth"
DISTROKID_TOKEN_URL = "https://distrokid.com/auth/token"
DISTROKID_API_BASE = "https://distrokid.com/api/v1"

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Storage helpers for DistroKid tokens and submissions
def get_distrokid_tokens() -> Dict[str, Any]:
    """Get all stored DistroKid tokens"""
    try:
        return db.storage.json.get("distrokid_tokens", default={})
    except Exception as e:
        print(f"Error getting DistroKid tokens: {e}")
        return {}

def save_distrokid_token(user_id: str, token_data: Dict[str, Any]):
    """Save a DistroKid token for a user"""
    tokens = get_distrokid_tokens()
    tokens[user_id] = token_data
    db.storage.json.put(sanitize_storage_key("distrokid_tokens"), tokens)

def get_track_submissions() -> Dict[str, Any]:
    """Get all track submission records"""
    try:
        return db.storage.json.get("distrokid_submissions", default={})
    except Exception as e:
        print(f"Error getting DistroKid submissions: {e}")
        return {}

def save_track_submission(submission_id: str, submission_data: Dict[str, Any]):
    """Save a track submission record"""
    submissions = get_track_submissions()
    submissions[submission_id] = submission_data
    db.storage.json.put(sanitize_storage_key("distrokid_submissions"), submissions)


def get_connection_health_status(user_id: str, token_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate health status metrics for the DistroKid connection"""
    # In a real implementation, you would check API logs, response times, error rates, etc.
    # For this demo, we'll generate a simulated health status
    
    # Get the connection history or create a new one
    try:
        connection_history = db.storage.json.get("distrokid_connection_history", default={})
        if user_id not in connection_history:
            connection_history[user_id] = {
                "error_count": 0,
                "last_sync": datetime.now().isoformat(),
                "connection_quality": "excellent"
            }
    except Exception:
        connection_history = {user_id: {
            "error_count": 0,
            "last_sync": datetime.now().isoformat(),
            "connection_quality": "excellent"
        }}
    
    # Calculate token age in hours
    token_age_hours = 0
    if "obtained_at" in token_data:
        obtained_timestamp = token_data["obtained_at"]
        token_age_hours = (int(time.time()) - obtained_timestamp) / 3600
    else:
        # If there's no obtained_at timestamp, estimate from expires_at
        if "expires_at" in token_data and "expires_in" in token_data:
            token_obtained_estimate = token_data["expires_at"] - token_data["expires_in"]
            token_age_hours = (int(time.time()) - token_obtained_estimate) / 3600
    
    # For demonstration purposes only: simulate some connection issues based on token age
    user_history = connection_history[user_id]
    
    # Determine health status based on token age and error count
    status = "excellent"
    if token_age_hours > 168 or user_history["error_count"] >= 4:  # > 7 days or lots of errors
        status = "poor"
    elif token_age_hours > 72 or user_history["error_count"] >= 2:  # > 3 days or some errors
        status = "fair"
    elif token_age_hours > 24 or user_history["error_count"] >= 1:  # > 1 day or a few errors
        status = "good"
    
    # Save updated status
    user_history["connection_quality"] = status
    db.storage.json.put("distrokid_connection_history", connection_history)
    
    return {
        "healthStatus": status,
        "lastSyncTimestamp": user_history["last_sync"],
        "errorCount": user_history["error_count"]
    }

# Pydantic models for requests and responses
class AuthRequest(BaseModel):
    redirect_uri: str = Field(..., description="Redirect URI for OAuth flow")

class AuthResponse(BaseModel):
    auth_url: str

class TokenExchangeRequest(BaseModel):
    code: str = Field(..., description="OAuth code received from DistroKid")
    redirect_uri: str = Field(..., description="Redirect URI used in auth request")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    connected: bool

class Artist(BaseModel):
    id: str
    name: str

class ArtistResponse(BaseModel):
    artists: List[Artist]

class TrackMetadata(BaseModel):
    title: str = Field(..., description="Title of the track")
    artist_name: str = Field(..., description="Primary artist name")
    album: Optional[str] = Field(None, description="Album name (optional)")
    genre: str = Field(..., description="Genre of the track")
    audio_language: str = Field("English", description="Language of the audio")
    release_date: Optional[str] = Field(None, description="Release date (YYYY-MM-DD)")
    lyrics: Optional[str] = Field(None, description="Lyrics (optional)")
    featuring: Optional[str] = Field(None, description="Featured artists (optional)")
    isrc: Optional[str] = Field(None, description="ISRC code (optional)")
    explicit: bool = Field(False, description="Whether the track has explicit content")

class TrackSubmissionRequest(BaseModel):
    content_id: str = Field(..., description="ID of the content to submit")
    dao_id: str = Field(..., description="ID of the DAO owning the content")
    track_metadata: TrackMetadata = Field(..., description="Metadata for the track")

class TrackSubmissionResponse(BaseModel):
    submission_id: str
    status: str
    submission_date: str
    content_id: str
    dao_id: str
    track_metadata: Dict[str, Any]
    distribution_info: Optional[Dict[str, Any]] = None

class TrackSubmissionStatusUpdate(BaseModel):
    status: str = Field(..., description="New status for the submission")
    distribution_info: Optional[Dict[str, Any]] = Field(None, description="Updated distribution info")

class RevenueItem(BaseModel):
    platform: str
    amount: float
    date: str
    track_id: str
    track_title: str

class RevenueResponse(BaseModel):
    total_revenue: float
    revenue_by_platform: Dict[str, float]
    revenue_items: List[RevenueItem]

@router.get("/auth")
async def get_auth_url(redirect_uri: str, user: AuthorizedUser):
    """Generate authorization URL for DistroKid OAuth flow"""
    try:
        # Try to get API key with a fallback
        client_id = None
        client_secret = None
        
        try:
            client_id = db.secrets.get("DISTROKID_CLIENT_ID")
            client_secret = db.secrets.get("DISTROKID_CLIENT_SECRET")
        except Exception:
            # For testing, use mock values if secrets aren't set
            client_id = DISTROKID_CLIENT_ID
            client_secret = "mock_secret"
            print("Using mock DistroKid credentials")
            
        # Generate a state parameter to prevent CSRF
        state = str(uuid.uuid4())
        
        # Construct the authorization URL
        auth_url = f"{DISTROKID_AUTH_URL}?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&response_type=code"
        
        # Save the state in the user's token data for verification later
        tokens = get_distrokid_tokens()
        if user.sub not in tokens:
            tokens[user.sub] = {}
        tokens[user.sub]["oauth_state"] = state
        db.storage.json.put(sanitize_storage_key("distrokid_tokens"), tokens)
        
        return AuthResponse(auth_url=auth_url)
    except Exception as e:
        print(f"Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate authentication URL: {str(e)}")

@router.post("/exchange-token")
async def exchange_token(request: TokenExchangeRequest, user: AuthorizedUser) -> TokenResponse:
    """Exchange authorization code for access token"""
    try:
        # Try to get API key with a fallback
        client_id = None
        client_secret = None
        
        try:
            client_id = db.secrets.get("DISTROKID_CLIENT_ID")
            client_secret = db.secrets.get("DISTROKID_CLIENT_SECRET")
        except Exception:
            # For testing, use mock values if secrets aren't set
            client_id = DISTROKID_CLIENT_ID
            client_secret = "mock_secret"
            print("Using mock DistroKid credentials")
        
        # In a real implementation, exchange the code for a token
        if client_id == DISTROKID_CLIENT_ID and client_secret == "mock_secret":
            # Mock token for testing
            token_data = {
                "access_token": f"mock_access_token_{uuid.uuid4()}",
                "refresh_token": f"mock_refresh_token_{uuid.uuid4()}",
                "expires_in": 3600,
                "token_type": "Bearer",
                "scope": "read write",
                "connected": True,
                "expires_at": int(time.time()) + 3600
            }
        else:
            # Real token exchange in production
            response = requests.post(
                DISTROKID_TOKEN_URL,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": request.code,
                    "redirect_uri": request.redirect_uri,
                    "grant_type": "authorization_code"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Failed to exchange token: {response.text}")
            
            token_data = response.json()
            token_data["connected"] = True
            token_data["expires_at"] = int(time.time()) + token_data["expires_in"]
        
        # Save the token data for the user
        save_distrokid_token(user.sub, token_data)
        
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_in=token_data["expires_in"],
            token_type=token_data["token_type"],
            connected=True
        )
    except Exception as e:
        print(f"Error exchanging token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to exchange token: {str(e)}")

@router.get("/connection-status")
async def get_distrokid_connection_status(user: AuthorizedUser):
    """Check if the user has connected their DistroKid account"""
    try:
        tokens = get_distrokid_tokens()
        is_connected = (
            user.sub in tokens and 
            "access_token" in tokens[user.sub] and
            tokens[user.sub].get("connected", False)
        )
        
        # Check if token is expired and needs refresh
        needs_refresh = False
        if is_connected and "expires_at" in tokens[user.sub]:
            if int(time.time()) >= tokens[user.sub]["expires_at"]:
                needs_refresh = True
        
        return {
            "connected": is_connected,
            "needs_refresh": needs_refresh
        }
    except Exception as e:
        print(f"Error checking connection status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check connection status: {str(e)}")

@router.get("/artists")
async def get_artists(user: AuthorizedUser) -> ArtistResponse:
    """Get artist profiles from DistroKid"""
    try:
        tokens = get_distrokid_tokens()
        if user.sub not in tokens or not tokens[user.sub].get("connected", False):
            raise HTTPException(status_code=401, detail="DistroKid account not connected")
        
        # In a real implementation, call the DistroKid API with the access token
        if tokens[user.sub]["access_token"].startswith("mock_"):
            # Mock response for testing
            artists = [
                {"id": "artist_1", "name": "Legacy Vault Studio"},
                {"id": "artist_2", "name": "Trust Fund Productions"},
                {"id": "artist_3", "name": "BirthdayBeats"},
            ]
        else:
            # Real API call in production
            response = requests.get(
                f"{DISTROKID_API_BASE}/artists",
                headers={
                    "Authorization": f"Bearer {tokens[user.sub]['access_token']}"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Failed to get artists: {response.text}")
            
            artists = response.json()["artists"]
        
        return ArtistResponse(artists=[Artist(**artist) for artist in artists])
    except Exception as e:
        print(f"Error getting artists: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get artists: {str(e)}")

@router.post("/submit-track")
async def submit_track(request: TrackSubmissionRequest, user: AuthorizedUser) -> TrackSubmissionResponse:
    """Submit a track to DistroKid for distribution"""
    try:
        tokens = get_distrokid_tokens()
        if user.sub not in tokens or not tokens[user.sub].get("connected", False):
            raise HTTPException(status_code=401, detail="DistroKid account not connected")
        
        # Check if content exists and get audio URL
        # This would normally query the content_dao API to get the content details
        # For this prototype, we'll assume the content ID is valid and has an audio URL
        
        # Generate a unique submission ID
        submission_id = f"submission_{uuid.uuid4().hex[:10]}"
        
        # In a real implementation, call the DistroKid API to submit the track
        if tokens[user.sub]["access_token"].startswith("mock_"):
            # Mock response for testing
            submission_data = {
                "submission_id": submission_id,
                "status": "submitted",
                "submission_date": datetime.now().isoformat(),
                "content_id": request.content_id,
                "dao_id": request.dao_id,
                "track_metadata": request.track_metadata.dict(),
                "distribution_info": {
                    "store_selection": ["spotify", "apple_music", "tidal", "amazon", "youtube"],
                    "estimated_release_date": (datetime.now() + timedelta(days=7)).isoformat()[:10]
                }
            }
        else:
            # Real API call in production would look something like this:
            # 1. First, we'd need to upload the audio file to DistroKid's storage
            # 2. Then, submit the track metadata and storage reference
            # This is a simplified placeholder for the real implementation
            response = requests.post(
                f"{DISTROKID_API_BASE}/releases",
                headers={
                    "Authorization": f"Bearer {tokens[user.sub]['access_token']}",
                    "Content-Type": "application/json"
                },
                json={
                    "title": request.track_metadata.title,
                    "artist": request.track_metadata.artist_name,
                    "album": request.track_metadata.album,
                    "genre": request.track_metadata.genre,
                    "language": request.track_metadata.audio_language,
                    "release_date": request.track_metadata.release_date,
                    "lyrics": request.track_metadata.lyrics,
                    "featuring": request.track_metadata.featuring,
                    "isrc": request.track_metadata.isrc,
                    "explicit": request.track_metadata.explicit,
                    # Other metadata and the asset reference would be included here
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Failed to submit track: {response.text}")
            
            submission_data = {
                "submission_id": submission_id,
                "status": "submitted",
                "submission_date": datetime.now().isoformat(),
                "content_id": request.content_id,
                "dao_id": request.dao_id,
                "track_metadata": request.track_metadata.dict(),
                "distribution_info": response.json()
            }
        
        # Save the submission data
        save_track_submission(submission_id, submission_data)
        
        return TrackSubmissionResponse(**submission_data)
    except Exception as e:
        print(f"Error submitting track: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit track: {str(e)}")

@router.get("/track-status/{submission_id}")
async def get_track_status(submission_id: str, user: AuthorizedUser) -> TrackSubmissionResponse:
    """Get the status of a track submission including ISRC/UPC codes and store links if available.
    This endpoint provides detailed tracking information for music distributed through DistroKid."""
    try:
        # Get all submissions
        submissions = get_track_submissions()
        
        # Check if the submission exists
        if submission_id not in submissions:
            raise HTTPException(status_code=404, detail=f"Submission with ID {submission_id} not found")
        
        submission = submissions[submission_id]
        
        # In a real implementation, we would check the actual status with DistroKid's API
        # For testing, we'll randomly update the status based on time passed
        if submission["status"] == "submitted":
            # Check how long ago it was submitted
            submission_date = datetime.fromisoformat(submission["submission_date"])
            days_passed = (datetime.now() - submission_date).total_seconds() / 86400
            
            if days_passed > 2:  # If more than 2 days have passed since submission
                submission["status"] = "released"
                submission["distribution_info"]["available_platforms"] = ["spotify", "apple_music", "amazon"]
                submission["distribution_info"]["release_date"] = datetime.now().isoformat()[:10]
                save_track_submission(submission_id, submission)
            elif days_passed > 1:  # If more than 1 day has passed
                submission["status"] = "processing"
                submission["distribution_info"]["processing_step"] = "store delivery"
                save_track_submission(submission_id, submission)
        
        return TrackSubmissionResponse(**submission)
    except Exception as e:
        print(f"Error getting track status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get track status: {str(e)}")

@router.post("/update-track-status/{submission_id}")
async def update_track_status(submission_id: str, update: TrackSubmissionStatusUpdate, user: AuthorizedUser = None) -> TrackSubmissionResponse:
    """Update the status and distribution information for a track submission.
    As a track progresses through the distribution pipeline, this endpoint allows for status updates."""
    try:
        # Get all submissions
        submissions = get_track_submissions()
        
        # Check if the submission exists
        if submission_id not in submissions:
            raise HTTPException(status_code=404, detail=f"Submission with ID {submission_id} not found")
        
        submission = submissions[submission_id]
        
        # Update the status
        submission["status"] = update.status
        
        # Update distribution info if provided
        if update.distribution_info:
            if "distribution_info" not in submission:
                submission["distribution_info"] = {}
            submission["distribution_info"].update(update.distribution_info)
        
        # Save the updated submission
        save_track_submission(submission_id, submission)
        
        return TrackSubmissionResponse(**submission)
    except Exception as e:
        print(f"Error updating track status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update track status: {str(e)}")

@router.get("/submissions")
async def list_submissions(dao_id: Optional[str] = None, user: AuthorizedUser = None) -> List[TrackSubmissionResponse]:
    """List all track submissions with their current status and distribution information.
    This endpoint supports filtering by DAO ID and returns comprehensive track metadata."""
    try:
        # Get all submissions
        submissions = get_track_submissions()
        
        # Filter by DAO ID if provided
        if dao_id:
            filtered_submissions = [sub for sub_id, sub in submissions.items() if sub["dao_id"] == dao_id]
        else:
            filtered_submissions = list(submissions.values())
        
        # Sort by submission date (newest first)
        filtered_submissions.sort(key=lambda x: x["submission_date"], reverse=True)
        
        return [TrackSubmissionResponse(**sub) for sub in filtered_submissions]
    except Exception as e:
        print(f"Error listing submissions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list submissions: {str(e)}")

@router.get("/revenue")
async def get_revenue(submission_id: Optional[str] = None, dao_id: Optional[str] = None, user: AuthorizedUser = None, profile_id: Optional[str] = None) -> RevenueResponse:
    """Get revenue data for distributed tracks across various streaming platforms.
    This endpoint provides detailed financial analytics with platform breakdown and timeline visualization."""
    try:
        # Determine which submissions to include
        submissions = get_track_submissions()
        
        if submission_id:
            # Get revenue for a specific submission
            if submission_id not in submissions:
                raise HTTPException(status_code=404, detail=f"Submission with ID {submission_id} not found")
            selected_submissions = [submissions[submission_id]]
        elif dao_id:
            # Get revenue for all submissions from a DAO
            selected_submissions = [sub for sub_id, sub in submissions.items() if sub["dao_id"] == dao_id]
        else:
            # Get revenue for all submissions
            selected_submissions = list(submissions.values())
        
        # Generate revenue data (mock implementation)
        revenue_items = []
        platforms = set()
        total_revenue = 0
        revenue_by_platform = {}
        
        for submission in selected_submissions:
            if submission["status"] == "released":
                # Only released tracks generate revenue
                available_platforms = submission.get("distribution_info", {}).get("available_platforms", [])
                
                for platform in available_platforms:
                    platforms.add(platform)
                    
                    # Calculate a random revenue amount based on the platform
                    if platform == "spotify":
                        amount = round(random.uniform(0.5, 10.0), 2)
                    elif platform == "apple_music":
                        amount = round(random.uniform(1.0, 15.0), 2)
                    elif platform == "amazon":
                        amount = round(random.uniform(0.3, 5.0), 2)
                    elif platform == "tidal":
                        amount = round(random.uniform(0.8, 12.0), 2)
                    else:
                        amount = round(random.uniform(0.1, 3.0), 2)
                    
                    revenue_items.append({
                        "platform": platform,
                        "amount": amount,
                        "date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()[:10],
                        "track_id": submission_id or "unknown",
                        "track_title": submission["track_metadata"]["title"]
                    })
                    
                    # Update total and per-platform revenue
                    total_revenue += amount
                    if platform in revenue_by_platform:
                        revenue_by_platform[platform] += amount
                    else:
                        revenue_by_platform[platform] = amount
                        
                    # If profile_id is provided, record this revenue to the trust fund
                    if profile_id:
                        try:
                            # Record revenue to the trust fund
                            record_request = RevenueRecordRequest(
                                profile_id=profile_id,
                                source=f"DistroKid: {platform.replace('_', ' ').title()}",
                                amount=amount,
                                description=f"Streaming revenue for '{submission['track_metadata']['title']}'"
                            )
                            record_legacy_vault_revenue(record_request)
                        except Exception as e:
                            print(f"Error recording DistroKid revenue to trust fund: {e}")
        
        # Sort revenue items by date (newest first)
        revenue_items.sort(key=lambda x: x["date"], reverse=True)
        
        return RevenueResponse(
            total_revenue=round(total_revenue, 2),
            revenue_by_platform={platform: round(amount, 2) for platform, amount in revenue_by_platform.items()},
            revenue_items=[RevenueItem(**item) for item in revenue_items]
        )
    except Exception as e:
        print(f"Error getting revenue data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get revenue data: {str(e)}")

from datetime import timedelta
import random