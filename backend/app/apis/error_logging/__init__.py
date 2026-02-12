from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import databutton as db
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timedelta

router = APIRouter()

# Error severity levels
class ErrorSeverity(str):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

# Input model for logging errors
class ErrorLogRequest(BaseModel):
    message: str
    stack: Optional[str] = None
    component: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    severity: str = ErrorSeverity.ERROR
    tags: Optional[List[str]] = None
    
# Output model for error statistics
class ErrorStats(BaseModel):
    total_errors: int
    unique_errors: int
    most_common: List[Dict[str, Any]]
    last_24h: int
    last_7d: int

# Helper function to store error logs
def store_error_log(error_data: dict):
    """
    Store an error log in the storage system
    """
    try:
        # Get existing logs
        try:
            logs = db.storage.json.get("error_logs", default=[])
        except:
            logs = []
            
        # Add timestamp if not present
        if "timestamp" not in error_data:
            error_data["timestamp"] = datetime.now().isoformat()
            
        # Add the new log
        logs.append(error_data)
        
        # Keep only the last 1000 logs to avoid storage issues
        if len(logs) > 1000:
            logs = logs[-1000:]
            
        # Save back to storage
        db.storage.json.put("error_logs", logs)
        return True
    except Exception as e:
        print(f"Failed to store error log: {e}")
        return False

@router.post("/log-client-error-logging")
def log_client_error_logging(error_data: ErrorLogRequest):
    """
    Log a client-side error from the frontend application
    """
    # Convert to dict and store
    error_dict = error_data.dict()
    success = store_error_log(error_dict)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to log error")
        
    return {"status": "success"}

@router.get("/error-logging-stats", response_model=ErrorStats)
def get_error_stats_logging():
    """
    Get error statistics for system monitoring and dashboard display
    """
    try:
        # Get logs
        try:
            logs = db.storage.json.get("error_logs", default=[])
        except:
            logs = []
            
        # Calculate stats
        now = datetime.now()
        day_ago = (now - timedelta(days=1)).isoformat()
        week_ago = (now - timedelta(days=7)).isoformat()
        
        # Filter for recent errors
        last_24h_errors = [log for log in logs if log.get("timestamp", "") >= day_ago]
        last_7d_errors = [log for log in logs if log.get("timestamp", "") >= week_ago]
        
        # Count unique errors by message
        error_counts = {}
        for log in logs:
            message = log.get("message", "Unknown error")
            error_counts[message] = error_counts.get(message, 0) + 1
            
        # Sort by count descending
        most_common = [
            {"message": message, "count": count}
            for message, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]  # Top 5 errors
        
        return ErrorStats(
            total_errors=len(logs),
            unique_errors=len(error_counts),
            most_common=most_common,
            last_24h=len(last_24h_errors),
            last_7d=len(last_7d_errors)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error stats: {str(e)}")
