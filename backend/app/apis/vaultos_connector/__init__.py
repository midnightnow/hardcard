from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import databutton as db
from datetime import datetime
from app.auth import AuthorizedUser

router = APIRouter()

# Models for request and response
class VaultOSConnectionStatus(BaseModel):
    connected: bool
    last_sync: Optional[datetime] = None
    vault_id: Optional[str] = None

class VaultOSDataSummary(BaseModel):
    session_count: int
    insight_count: int
    philosophical_paths: List[str]

class ExportRequest(BaseModel):
    session_ids: List[str] = []  # Empty list means all sessions
    include_voice_data: bool = False

class ExportResponse(BaseModel):
    export_id: str
    status: str = "processing"
    estimated_completion_time: datetime

@router.get("/connection-status", response_model=VaultOSConnectionStatus)
async def get_vaultos_connection_status(user: AuthorizedUser):
    """Get the current VaultOS connection status"""
    try:
        # This would normally check if the user has connected their VaultOS account
        # For prototype, we'll return a dummy status
        return VaultOSConnectionStatus(
            connected=True,
            last_sync=datetime.now(),
            vault_id="legacy-vault-123"
        )
    except Exception as e:
        print(f"Error in get_vaultos_connection_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data-summary", response_model=VaultOSDataSummary)
async def get_data_summary(user: AuthorizedUser):
    """Get a summary of the user's data in VaultOS"""
    try:
        # This would normally fetch data from VaultOS
        # For prototype, we'll return dummy data
        return VaultOSDataSummary(
            session_count=15,
            insight_count=42,
            philosophical_paths=["Stoicism", "Socratic Method", "Existentialism"]
        )
    except Exception as e:
        print(f"Error in get_data_summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vaultos-export-data", response_model=ExportResponse)
async def export_to_vaultos(request: ExportRequest, user: AuthorizedUser):
    """Export conversation data to VaultOS for long-term storage"""
    try:
        # This would normally initiate an export process to VaultOS
        # For prototype, we'll return a dummy response
        export_id = f"export_{datetime.now().timestamp()}"
        completion_time = datetime.now()
        
        return ExportResponse(
            export_id=export_id,
            status="processing",
            estimated_completion_time=completion_time
        )
    except Exception as e:
        print(f"Error in export_to_vaultos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-status/{export_id}", response_model=ExportResponse)
async def get_export_status(export_id: str, user: AuthorizedUser):
    """Check the status of a VaultOS export"""
    try:
        # This would normally check the status of an export
        # For prototype, we'll return a dummy response
        return ExportResponse(
            export_id=export_id,
            status="completed",
            estimated_completion_time=datetime.now()
        )
    except Exception as e:
        print(f"Error in get_export_status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
