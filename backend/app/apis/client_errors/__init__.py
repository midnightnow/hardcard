from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import databutton as db
import json

router = APIRouter()


class ClientErrorRequest(BaseModel):
    """
    Model for logging client errors from the frontend application.
    """
    message: str
    source: str
    stackTrace: Optional[str] = None
    componentName: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ClientErrorResponse(BaseModel):
    """
    Response model for client error logging.
    """
    success: bool
    errorId: Optional[str] = None
    message: str


class ErrorAnalysisRequest(BaseModel):
    """
    Model for requesting error analysis.
    """
    componentName: Optional[str] = None
    timeframe: Optional[str] = "7d"  # Options: 24h, 7d, 30d, all


class ErrorSummary(BaseModel):
    """
    Summary of errors for a specific component or error type.
    """
    errorType: str
    count: int
    lastOccurred: str
    affectedComponents: List[str]
    possibleSolutions: Optional[List[str]] = None


class ErrorAnalysisResponse(BaseModel):
    """
    Response model for error analysis.
    """
    totalErrors: int
    timeframe: str
    summaries: List[ErrorSummary]
    recommendations: Optional[List[str]] = None


class ErrorStats(BaseModel):
    """
    Error statistics response model.
    """
    totalErrors: int
    errorsByComponent: Dict[str, int]
    errorsByType: Dict[str, int]
    errorTrend: List[Dict[str, Any]]


def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


def get_error_store():
    """Get the error store from storage or create a new one if it doesn't exist"""
    try:
        error_store = db.storage.json.get("client_errors")
    except FileNotFoundError:
        error_store = {"errors": []}
        db.storage.json.put("client_errors", error_store)
    
    return error_store


def save_error_store(error_store):
    """Save the error store to storage"""
    db.storage.json.put("client_errors", error_store)


@router.post("/client-errors/log-error")
def log_client_error_main(request: ClientErrorRequest) -> ClientErrorResponse:
    """Log client errors from the frontend application for monitoring and debugging purposes."""
    try:
        # Generate error ID
        error_id = f"err-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create error entry
        error_entry = {
            "id": error_id,
            "message": request.message,
            "source": request.source,
            "stackTrace": request.stackTrace,
            "componentName": request.componentName,
            "url": request.url,
            "timestamp": request.timestamp or datetime.now().isoformat(),
            "metadata": request.metadata or {}
        }
        
        # Get error store
        error_store = get_error_store()
        
        # Add error to store
        error_store["errors"].append(error_entry)
        
        # Keep only the last 1000 errors
        if len(error_store["errors"]) > 1000:
            error_store["errors"] = error_store["errors"][-1000:]
        
        # Save updated error store
        save_error_store(error_store)
        
        return ClientErrorResponse(
            success=True,
            errorId=error_id,
            message="Error logged successfully"
        )
    
    except Exception as e:
        return ClientErrorResponse(
            success=False,
            message=f"Failed to log error: {str(e)}"
        )


@router.get("/client-errors/error-stats")
def get_client_error_stats() -> ErrorStats:
    """Get statistics about client errors for monitoring and debugging."""
    try:
        error_store = get_error_store()
        errors = error_store.get("errors", [])
        
        total_errors = len(errors)
        errors_by_component = {}
        errors_by_type = {}
        error_trend = []
        
        # Process errors
        for error in errors:
            # Count by component
            component = error.get("componentName") or "unknown"
            errors_by_component[component] = errors_by_component.get(component, 0) + 1
            
            # Count by error type/message
            # Simplify message to use as a type
            error_type = error.get("message", "")[:50]  # First 50 chars as type
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
        
        # Create a simple trend (could be expanded to group by day/hour)
        # For now, just return the last 20 errors with timestamps
        for error in errors[-20:]:
            error_trend.append({
                "timestamp": error.get("timestamp"),
                "component": error.get("componentName") or "unknown"
            })
        
        return ErrorStats(
            totalErrors=total_errors,
            errorsByComponent=errors_by_component,
            errorsByType=errors_by_type,
            errorTrend=error_trend
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error stats: {str(e)}")


@router.post("/client-errors/analyze")
def analyze_client_errors(request: ErrorAnalysisRequest) -> ErrorAnalysisResponse:
    """Analyze client errors and provide insights and potential solutions."""
    try:
        error_store = get_error_store()
        errors = error_store.get("errors", [])
        
        # Filter by component if specified
        if request.componentName:
            errors = [e for e in errors if e.get("componentName") == request.componentName]
        
        # Filter by timeframe
        current_time = datetime.now()
        filtered_errors = []
        
        for error in errors:
            try:
                error_time = datetime.fromisoformat(error.get("timestamp").replace('Z', '+00:00'))
                
                if request.timeframe == "24h":
                    if (current_time - error_time).days < 1:
                        filtered_errors.append(error)
                elif request.timeframe == "7d":
                    if (current_time - error_time).days < 7:
                        filtered_errors.append(error)
                elif request.timeframe == "30d":
                    if (current_time - error_time).days < 30:
                        filtered_errors.append(error)
                else:  # "all"
                    filtered_errors.append(error)
            except (ValueError, AttributeError):
                # If timestamp parsing fails, include the error anyway
                filtered_errors.append(error)
        
        # Group errors by type (using message as type)
        error_types = {}
        
        for error in filtered_errors:
            error_type = error.get("message", "")[:100]  # Use first 100 chars of message as type
            if error_type not in error_types:
                error_types[error_type] = {
                    "count": 0,
                    "lastOccurred": error.get("timestamp", ""),
                    "components": set()
                }
            
            error_types[error_type]["count"] += 1
            if error.get("componentName"):
                error_types[error_type]["components"].add(error.get("componentName"))
        
        # Generate summaries
        summaries = []
        
        for error_type, data in error_types.items():
            summaries.append(ErrorSummary(
                errorType=error_type,
                count=data["count"],
                lastOccurred=data["lastOccurred"],
                affectedComponents=list(data["components"]),
                # Simple placeholder for possible solutions
                possibleSolutions=["Check component for null references", "Verify API responses", "Check data formatting"]
            ))
        
        # Sort summaries by count (descending)
        summaries.sort(key=lambda x: x.count, reverse=True)
        
        # Generate recommendations
        recommendations = [
            "Focus on fixing errors in the most affected components first",
            "Consider adding additional error boundaries around problematic components",
            "Review recent code changes that might have introduced these errors"
        ]
        
        return ErrorAnalysisResponse(
            totalErrors=len(filtered_errors),
            timeframe=request.timeframe,
            summaries=summaries,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze errors: {str(e)}")


@router.get("/get-error-analyses-for-component/{component_name}")
def get_component_error_analyses(component_name: str) -> List[Dict[str, Any]]:
    """Get error analyses specific to a component."""
    try:
        # Create request with the component name
        request = ErrorAnalysisRequest(componentName=component_name)
        
        # Get analyses for different timeframes
        analyses = []
        
        for timeframe in ["24h", "7d", "30d", "all"]:
            request.timeframe = timeframe
            analysis = analyze_client_errors(request)
            analyses.append({
                "timeframe": timeframe,
                "analysis": analysis.dict()
            })
        
        return analyses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error analyses: {str(e)}")


@router.get("/list-error-analyses")
def list_error_analyses() -> List[Dict[str, Any]]:
    """List all component error analyses."""
    try:
        error_store = get_error_store()
        errors = error_store.get("errors", [])
        
        # Get unique components
        components = set()
        for error in errors:
            if error.get("componentName"):
                components.add(error.get("componentName"))
        
        # Get analyses for each component
        component_analyses = []
        
        for component in components:
            # Get 7-day analysis for the component
            request = ErrorAnalysisRequest(componentName=component, timeframe="7d")
            analysis = analyze_client_errors(request)
            
            component_analyses.append({
                "component": component,
                "totalErrors": analysis.totalErrors,
                "topIssue": analysis.summaries[0].errorType if analysis.summaries else "No issues",
                "analysis": analysis.dict()
            })
        
        # Sort by total errors (descending)
        component_analyses.sort(key=lambda x: x["totalErrors"], reverse=True)
        
        return component_analyses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list error analyses: {str(e)}")


@router.get("/get-error-analysis/{error_id}")
def get_error_analysis(error_id: str) -> Dict[str, Any]:
    """Get detailed analysis for a specific error."""
    try:
        error_store = get_error_store()
        errors = error_store.get("errors", [])
        
        # Find the error with the given ID
        error = next((e for e in errors if e.get("id") == error_id), None)
        
        if not error:
            raise HTTPException(status_code=404, detail=f"Error with ID {error_id} not found")
        
        # Get similar errors (if any)
        similar_errors = []
        error_message = error.get("message", "")
        
        for e in errors:
            if e.get("id") != error_id and e.get("message") == error_message:
                similar_errors.append(e)
        
        # Limit to 10 similar errors
        similar_errors = similar_errors[:10]
        
        return {
            "error": error,
            "similarErrors": similar_errors,
            "potentialSolutions": [
                "Check for null or undefined values",
                "Verify API responses",
                "Add error boundary to component",
                "Check recent code changes"
            ]
        }
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get error analysis: {str(e)}")
