from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import databutton as db
import json
from datetime import datetime, timedelta

router = APIRouter()

class ErrorEntry(BaseModel):
    message: str
    stack: Optional[str] = None
    component: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    severity: str
    timestamp: str
    tags: Optional[List[str]] = None

class MostCommonError(BaseModel):
    message: str
    count: int

class ErrorStats(BaseModel):
    total_errors: int
    unique_errors: int
    most_common: List[MostCommonError]
    last_24h: int
    last_7d: int

@router.get("/error-stats")
def get_error_stats() -> ErrorStats:
    """
    Get statistics about client-side errors logged in the system.
    This endpoint provides aggregated error metrics for monitoring and troubleshooting.
    """
    try:
        # Get stored errors or initialize empty list
        stored_errors = db.storage.json.get("client_errors", default=[])
        
        if not stored_errors:
            return ErrorStats(
                total_errors=0,
                unique_errors=0,
                most_common=[],
                last_24h=0,
                last_7d=0
            )
        
        # Parse timestamps
        for error in stored_errors:
            if isinstance(error.get("timestamp"), str):
                error["_timestamp_obj"] = datetime.fromisoformat(error["timestamp"].replace("Z", "+00:00"))
            else:
                error["_timestamp_obj"] = datetime.now() - timedelta(days=30)  # Default old date
        
        # Calculate statistics
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        # Count errors in time periods
        last_24h_count = sum(1 for e in stored_errors if e["_timestamp_obj"] >= day_ago)
        last_7d_count = sum(1 for e in stored_errors if e["_timestamp_obj"] >= week_ago)
        
        # Find unique error messages and count occurrences
        error_counts = {}
        for error in stored_errors:
            message = error.get("message", "Unknown error")
            error_counts[message] = error_counts.get(message, 0) + 1
        
        # Sort by count descending and take top 10
        most_common = [
            MostCommonError(message=msg, count=count)
            for msg, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        return ErrorStats(
            total_errors=len(stored_errors),
            unique_errors=len(error_counts),
            most_common=most_common,
            last_24h=last_24h_count,
            last_7d=last_7d_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving error statistics: {str(e)}")

@router.post("/log-client-error-stats")
def log_client_error_stats(error: ErrorEntry):
    """
    Log a client-side error to the system.
    Errors are stored for analysis and monitoring purposes.
    """
    try:
        # Get existing errors or initialize empty list
        stored_errors = db.storage.json.get("client_errors", default=[])
        
        # Add new error to the list (convert to dict for storage)
        error_dict = error.model_dump()
        
        # Ensure timestamp exists
        if not error_dict.get("timestamp"):
            error_dict["timestamp"] = datetime.now().isoformat()
            
        # Add to storage
        stored_errors.append(error_dict)
        
        # Keep only the last 1000 errors to prevent excessive storage
        if len(stored_errors) > 1000:
            stored_errors = stored_errors[-1000:]
            
        # Save back to storage
        db.storage.json.put("client_errors", stored_errors)
        
        return {"status": "success", "message": "Error logged successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging client error: {str(e)}")

@router.post("/client-error-analysis")
def analyze_errors_stats() -> Dict[str, Any]:
    """
    Analyze stored client errors to find patterns and potential solutions.
    This endpoint uses simple heuristics to group errors and suggest fixes.
    """
    try:
        # Get stored errors
        stored_errors = db.storage.json.get("client_errors", default=[])
        
        if not stored_errors:
            return {
                "status": "success", 
                "message": "No errors to analyze",
                "analysis": {}
            }
        
        # Group errors by component
        components = {}
        for error in stored_errors:
            component = error.get("component", "unknown")
            if component not in components:
                components[component] = []
            components[component].append(error)
        
        # Simple analysis of each component
        analysis = {}
        for component, errors in components.items():
            # Count by severity
            severity_counts = {}
            for error in errors:
                severity = error.get("severity", "error")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Find most common error message
            message_counts = {}
            for error in errors:
                message = error.get("message", "Unknown error")
                message_counts[message] = message_counts.get(message, 0) + 1
            
            most_common_message = max(message_counts.items(), key=lambda x: x[1])[0] if message_counts else ""
            
            # Add to analysis
            analysis[component] = {
                "total_errors": len(errors),
                "severity_distribution": severity_counts,
                "most_common_error": most_common_message,
                "potential_fix": generate_fix_suggestion(most_common_message)
            }
        
        return {
            "status": "success",
            "analysis": analysis,
            "total_components_with_errors": len(components)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing errors: {str(e)}")

def generate_fix_suggestion(error_message: str) -> str:
    """Generate a simple fix suggestion based on common error patterns"""
    # This could be enhanced with AI or more sophisticated pattern matching
    if not error_message:
        return "Insufficient data to suggest a fix"
    
    # Common React errors
    if "is not defined" in error_message.lower():
        return "Check for undefined variables or import missing components"
    elif "cannot read property" in error_message.lower() or "cannot read properties" in error_message.lower():
        return "Add null/undefined checks before accessing object properties"
    elif "expected a react node" in error_message.lower():
        return "Ensure you're returning valid JSX from your component"
    elif "invalid hook call" in error_message.lower():
        return "Ensure hooks are only called from function components and at the top level"
    elif "memory leak" in error_message.lower():
        return "Clean up subscriptions or async operations in useEffect cleanup function"
    elif "maximum update depth exceeded" in error_message.lower():
        return "Check for infinite render loops in useEffect dependencies or state updates"
    elif "promise" in error_message.lower() and "rejected" in error_message.lower():
        return "Add proper error handling to Promise chains or async/await blocks"
    elif "network error" in error_message.lower() or "failed to fetch" in error_message.lower():
        return "Check network connectivity and API endpoint configuration"
    elif "authentication" in error_message.lower() or "auth" in error_message.lower():
        return "Verify authentication credentials and token validity"
    
    # Default suggestion
    return "Review the component code and add error boundaries for better resilience"
