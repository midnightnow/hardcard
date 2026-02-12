from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import databutton as db
import json
from datetime import datetime

router = APIRouter(prefix="/google-drive")

# Model definitions
class VaultOSConnectionStatus(BaseModel):
    status: str  # 'connected', 'disconnected', 'pending'
    last_sync: Optional[str] = None
    message: Optional[str] = None

class DataSummary(BaseModel):
    total_files: int
    total_folders: int
    total_size: int
    last_updated: str
    files: List[Dict[str, Any]]

class ExportRequest(BaseModel):
    folders: List[str] = []
    include_all: bool = True

class ExportResponse(BaseModel):
    status: str
    job_id: Optional[str] = None
    message: Optional[str] = None

class ExportStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    files_processed: int
    estimated_remaining_time: Optional[int] = None
    message: Optional[str] = None

# Mock data store
def get_mock_connection_status():
    return {
        "status": "connected",
        "last_sync": datetime.now().isoformat(),
        "message": None
    }

def get_mock_data_summary():
    return {
        "total_files": 148,
        "total_folders": 12,
        "total_size": 157286400,  # 150 MB
        "last_updated": datetime.now().isoformat(),
        "files": [
            {
                "id": "1",
                "name": "Family Documents",
                "type": "folder",
                "size": 0,
                "lastModified": "2023-12-10T14:30:00Z",
                "synced": True
            },
            {
                "id": "2",
                "name": "Legacy Investments",
                "type": "folder",
                "size": 0,
                "lastModified": "2023-12-15T09:45:00Z",
                "synced": True
            },
            {
                "id": "3",
                "name": "Trust Fund Documentation.pdf",
                "type": "file",
                "size": 1240000,
                "lastModified": "2024-02-20T11:20:00Z",
                "synced": True,
                "fileType": "pdf"
            },
            {
                "id": "4",
                "name": "Investment Strategy 2024.xlsx",
                "type": "file",
                "size": 3580000,
                "lastModified": "2024-03-05T16:10:00Z",
                "synced": False,
                "fileType": "spreadsheet"
            },
            {
                "id": "5",
                "name": "Family Trust Structure.png",
                "type": "file",
                "size": 840000,
                "lastModified": "2024-01-15T10:30:00Z",
                "synced": True,
                "fileType": "image"
            },
            {
                "id": "6",
                "name": "Legacy Portfolio Analysis.pptx",
                "type": "file",
                "size": 5240000,
                "lastModified": "2024-03-10T14:15:00Z",
                "synced": False,
                "fileType": "presentation"
            },
            {
                "id": "7",
                "name": "Bitcoin Purchase History.csv",
                "type": "file",
                "size": 350000,
                "lastModified": "2024-03-18T09:20:00Z",
                "synced": True,
                "fileType": "spreadsheet"
            }
        ]
    }

# Endpoints
@router.get("/vaultos-connection-status")
def get_google_drive_connection_status() -> VaultOSConnectionStatus:
    """
    Get the current connection status with Google Drive for VaultOS.
    Returns information about the connection state and last synchronization.
    """
    try:
        # Check if we have status in storage
        try:
            status_data = db.storage.json.get("google_drive_connection_status")
            return VaultOSConnectionStatus(**status_data)
        except:
            # Return mock data if not in storage or for demonstration
            mock_status = get_mock_connection_status()
            return VaultOSConnectionStatus(**mock_status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connection status: {str(e)}")

@router.get("/data-summary")
def get_google_drive_data_summary() -> DataSummary:
    """
    Get a summary of data stored in VaultOS and synchronized with Google Drive.
    Returns information about files, folders, sizes, and synchronization status.
    """
    try:
        # Check if we have data in storage
        try:
            data = db.storage.json.get("google_drive_data_summary")
            return DataSummary(**data)
        except:
            # Return mock data if not in storage or for demonstration
            mock_data = get_mock_data_summary()
            return DataSummary(**mock_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data summary: {str(e)}")

@router.post("/google-drive-export")
def export_to_google_drive(request: ExportRequest = None) -> ExportResponse:
    """
    Export data from VaultOS to Google Drive.
    Initiates a synchronization job that runs in the background.
    """
    try:
        # In a real implementation, this would start a background job
        # For demonstration, we'll just return a success response
        job_id = f"export-{datetime.now().strftime('%Y%m%d%H%M%S')}"  
        
        # Store the job status
        status = {
            "job_id": job_id,
            "status": "in_progress",
            "progress": 0,
            "files_processed": 0,
            "estimated_remaining_time": 120,  # 2 minutes
            "start_time": datetime.now().isoformat()
        }
        
        try:
            db.storage.json.put(f"export_job_{job_id}", status)
        except:
            # If storage fails, continue with mock response
            pass
            
        return ExportResponse(
            status="success",
            job_id=job_id,
            message="Export job started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start export: {str(e)}")

@router.get("/export-status/{job_id}")
def get_google_drive_export_status(job_id: str) -> ExportStatus:
    """
    Get the status of an export job.
    Returns information about the progress of a Google Drive synchronization job.
    """
    try:
        # Check if we have the job status in storage
        try:
            status = db.storage.json.get(f"export_job_{job_id}")
        except:
            # Create mock status for demonstration
            status = {
                "job_id": job_id,
                "status": "in_progress",
                "progress": 65,
                "files_processed": 96,
                "estimated_remaining_time": 45,  # 45 seconds
                "message": None
            }
            
        return ExportStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get export status: {str(e)}")
