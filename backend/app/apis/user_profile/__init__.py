from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import databutton as db
import re
from datetime import datetime
from app.auth import AuthorizedUser

router = APIRouter()

# Models for request and response
class TrustSession(BaseModel):
    userId: str
    profileId: str
    trustName: str
    trustPurpose: str
    jurisdiction: str
    trustees: List[str]
    beneficiaries: List[str]
    founder: str
    duration: str
    strategy: str
    governanceRules: str
    createdAt: datetime = Field(default_factory=datetime.now)

class CreateSessionRequest(BaseModel):
    userId: str
    profileId: str
    trustName: str
    trustPurpose: str
    jurisdiction: str
    trustees: List[str]
    beneficiaries: List[str]
    founder: str
    duration: str
    strategy: str
    governanceRules: str

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_user_sessions_key(user_id: str) -> str:
    return sanitize_storage_key(f"user_trust_sessions_{user_id}")

@router.post("/sessions", response_model=TrustSession)
async def create_session(request: CreateSessionRequest, user: AuthorizedUser):
    """Create a new trust session"""
    if request.userId != user.sub:
        raise HTTPException(status_code=403, detail="User ID does not match authenticated user")
    
    try:
        sessions_key = get_user_sessions_key(user.sub)
        
        try:
            sessions = db.storage.json.get(sessions_key)
        except:
            sessions = []
            
        new_session = TrustSession(**request.dict())
        sessions.append(new_session.dict(by_alias=True))
        
        db.storage.json.put(sessions_key, sessions)
        
        return new_session
    except Exception as e:
        print(f"Error in create_session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=List[TrustSession])
async def list_sessions(user: AuthorizedUser):
    """List all trust sessions for the authenticated user"""
    try:
        sessions_key = get_user_sessions_key(user.sub)
        try:
            sessions_data = db.storage.json.get(sessions_key)
            return [TrustSession(**session) for session in sessions_data]
        except:
            # If no sessions are found, return an empty list
            return []
    except Exception as e:
        print(f"Error in list_sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

