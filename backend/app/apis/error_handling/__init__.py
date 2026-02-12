from fastapi import APIRouter, HTTPException, status, Request
from typing import Dict, Any, Optional, List, Union, Type, Callable
import traceback
import json
import time
import uuid
from datetime import datetime
from pydantic import BaseModel, ValidationError
import databutton as db

router = APIRouter()

# Common HTTP error status codes
class ErrorCodes:
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

# Error response model
class ClientErrorResponse(BaseModel):
    status_code: int
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        super().__init__(**data)

# Client-friendly API exceptions
class APIError(HTTPException):
    def __init__(
        self, 
        status_code: int, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail={
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

# Common exception types
class BadRequestError(APIError):
    def __init__(self, message: str = "Invalid request", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=ErrorCodes.BAD_REQUEST, message=message, details=details)

class UnauthorizedError(APIError):
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=ErrorCodes.UNAUTHORIZED, message=message, details=details)

class ForbiddenError(APIError):
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=ErrorCodes.FORBIDDEN, message=message, details=details)

class NotFoundError(APIError):
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=ErrorCodes.NOT_FOUND, message=message, details=details)

class ConflictError(APIError):
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=ErrorCodes.CONFLICT, message=message, details=details)

class InternalServerError(APIError):
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=ErrorCodes.INTERNAL_SERVER_ERROR, message=message, details=details)

# Helper function to format validation errors
def format_validation_errors(errors: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Format validation errors into a more user-friendly structure"""
    formatted_errors: Dict[str, List[str]] = {}
    
    for error in errors:
        location = error.get("loc", [])
        field_name = location[-1] if location else "_general"
        field_name = str(field_name)  # Convert to string for consistency
        
        if field_name not in formatted_errors:
            formatted_errors[field_name] = []
            
        formatted_errors[field_name].append(error.get("msg", "Unknown validation error"))
        
    return formatted_errors

# Error handling for pydantic validation errors
def handle_validation_error(error: ValidationError) -> Dict[str, Any]:
    """Convert a Pydantic ValidationError into a structured error response"""
    errors = json.loads(error.json())
    formatted_errors = format_validation_errors(errors)
    
    return {
        "message": "Validation error",
        "details": {
            "validation_errors": formatted_errors
        }
    }

# Function to catch and handle API errors
def safe_execution(func, *args, **kwargs):
    """Safely execute a function and handle exceptions consistently"""
    try:
        return func(*args, **kwargs)
    except ValidationError as e:
        error_details = handle_validation_error(e)
        raise BadRequestError(message=error_details["message"], details=error_details["details"])
    except APIError:
        # Already formatted, just re-raise
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise InternalServerError(message="An unexpected error occurred", details={
            "error_type": type(e).__name__,
            "error_message": str(e)
        })

# Utility endpoint to log errors from frontend
class ErrorPayload(BaseModel):
    message: str
    stack: Optional[str] = None
    component: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None
    userId: Optional[str] = None
    severity: Optional[str] = "error"  # 'error', 'warning', 'info'
    tags: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    id: str
    stored: bool
    suggestion: Optional[str] = None


@router.post("/log-client-error")
async def log_client_error(error: ErrorPayload) -> ClientErrorResponse:
    """
    Logs client-side errors for analysis and self-improvement. 
    This endpoint collects error data from the frontend to enable 
    automated error detection, pattern recognition, and self-correcting behaviors.
    """
    error_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Construct the error record
    error_record = {
        "id": error_id,
        "timestamp": error.timestamp or timestamp,
        "message": error.message,
        "stack": error.stack,
        "component": error.component,
        "context": error.context or {},
        "url": error.url,
        "userId": error.userId,
        "severity": error.severity,
        "tags": error.tags or [],
    }
    
    # Store error in DB storage for analysis
    try:
        # Get existing errors or create new array
        try:
            all_errors = db.storage.json.get("client_errors")
        except FileNotFoundError:
            all_errors = {"errors": []}
        
        # Add new error and maintain last 1000 errors only
        all_errors["errors"] = [error_record] + all_errors.get("errors", [])[:999]
        
        # Save back to storage
        db.storage.json.put("client_errors", all_errors)
        
        # Simple analysis for suggestion
        suggestion = _analyze_error(error_record, all_errors["errors"])
        
        return ClientErrorResponse(
            id=error_id,
            stored=True,
            suggestion=suggestion
        )
    except Exception as e:
        print(f"Error storing client error: {str(e)}")
        return ClientErrorResponse(
            status_code=500,
            message="Failed to store client error",
            id=error_id,
            stored=False
        )


def _analyze_error(current_error: Dict[str, Any], all_errors: List[Dict[str, Any]]) -> Optional[str]:
    """
    Simple error analysis to identify patterns and provide suggestions.
    This is where self-improvement logic would be expanded.
    """
    # Count similar errors by component
    if current_error.get("component"):
        similar_errors = [e for e in all_errors 
                         if e.get("component") == current_error.get("component") 
                         and e.get("id") != current_error.get("id")]
        
        if len(similar_errors) >= 3:
            return f"Multiple errors detected in {current_error.get('component')}. Consider reviewing this component's error handling."
    
    # Check for repeated errors with same message
    similar_message_errors = [e for e in all_errors 
                              if e.get("message") == current_error.get("message")
                              and e.get("id") != current_error.get("id")]
    
    if len(similar_message_errors) >= 5:
        return "This error is occurring frequently. Consider implementing a specific error handler for this case."
    
    return None

# Health check endpoint with error simulation capability
class PerformanceMetric(BaseModel):
    component: str
    operation: str  # e.g., 'render', 'api_call', 'calculation'
    duration_ms: int
    timestamp: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    userId: Optional[str] = None


class PerformanceResponse(BaseModel):
    stored: bool
    threshold_exceeded: bool
    suggestion: Optional[str] = None


@router.post("/log-performance")
async def log_performance(metric: PerformanceMetric) -> PerformanceResponse:
    """
    Logs performance metrics for analysis and optimization suggestions.
    This enables the app to identify slow components and operations for self-improvement.
    """
    timestamp = datetime.now().isoformat()
    
    # Construct the metric record
    metric_record = {
        "timestamp": metric.timestamp or timestamp,
        "component": metric.component,
        "operation": metric.operation,
        "duration_ms": metric.duration_ms,
        "context": metric.context or {},
        "userId": metric.userId
    }
    
    # Performance thresholds for different operation types
    thresholds = {
        "render": 500,  # 500ms for rendering
        "api_call": 2000,  # 2 seconds for API calls
        "calculation": 1000,  # 1 second for calculations
        "default": 1000  # Default threshold
    }
    
    threshold = thresholds.get(metric.operation, thresholds["default"])
    threshold_exceeded = metric.duration_ms > threshold
    
    # Store performance metric
    try:
        # Get existing metrics or create new array
        try:
            all_metrics = db.storage.json.get("performance_metrics")
        except FileNotFoundError:
            all_metrics = {"metrics": []}
        
        # Add new metric and maintain last 1000 metrics only
        all_metrics["metrics"] = [metric_record] + all_metrics.get("metrics", [])[:999]
        
        # Save back to storage
        db.storage.json.put("performance_metrics", all_metrics)
        
        # Generate optimization suggestion if threshold exceeded
        suggestion = None
        if threshold_exceeded:
            suggestion = f"Performance threshold exceeded for {metric.component} ({metric.operation}). Consider optimization."
        
        return PerformanceResponse(
            stored=True,
            threshold_exceeded=threshold_exceeded,
            suggestion=suggestion
        )
    except Exception as e:
        print(f"Error storing performance metric: {str(e)}")
        return PerformanceResponse(
            stored=False,
            threshold_exceeded=threshold_exceeded
        )


class AnalyticsRequest(BaseModel):
    timeframe: Optional[str] = "24h"  # '1h', '24h', '7d', '30d'


class ErrorSummary(BaseModel):
    total_count: int
    by_component: Dict[str, int]
    by_severity: Dict[str, int]
    most_frequent: List[Dict[str, Any]]
    trend: str  # 'improving', 'stable', 'degrading'
    suggestions: List[str]


@router.post("/analyze-errors")
async def analyze_errors(request: AnalyticsRequest) -> ErrorSummary:
    """
    Analyzes collected errors to identify patterns and provide intelligent suggestions for improvement.
    This endpoint powers the self-improving aspect of the error handling system.
    """
    try:
        # Get stored errors
        try:
            all_errors = db.storage.json.get("client_errors")
            errors = all_errors.get("errors", [])
        except FileNotFoundError:
            errors = []
        
        # Basic analysis
        by_component = {}
        by_severity = {"error": 0, "warning": 0, "info": 0}
        message_count = {}
        
        for error in errors:
            # Count by component
            component = error.get("component", "unknown")
            by_component[component] = by_component.get(component, 0) + 1
            
            # Count by severity
            severity = error.get("severity", "error")
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # Count by message
            message = error.get("message", "")
            if message:
                message_count[message] = message_count.get(message, 0) + 1
        
        # Get most frequent errors
        most_frequent = [
            {"message": msg, "count": count}
            for msg, count in sorted(message_count.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Generate improvement suggestions
        suggestions = []
        
        # Suggest improvements for components with many errors
        for component, count in sorted(by_component.items(), key=lambda x: x[1], reverse=True):
            if count >= 5 and component != "unknown":
                suggestions.append(f"Consider improving error handling in '{component}' component ({count} errors)")
        
        # Suggest improvements based on error patterns
        for error in most_frequent:
            if error["count"] >= 3:
                suggestions.append(f"Frequently occurring error: '{error['message']}' ({error['count']} occurrences)")
        
        # Determine trend (simplified for now)
        trend = "stable"
        
        return ErrorSummary(
            total_count=len(errors),
            by_component=by_component,
            by_severity=by_severity,
            most_frequent=most_frequent,
            trend=trend,
            suggestions=suggestions[:5]  # Limit to top 5 suggestions
        )
    except Exception as e:
        print(f"Error analyzing errors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/error-handling/health-check")
def check_health_api(simulate_error: bool = False):
    """Health check endpoint that can also be used to test error handling"""
    if simulate_error:
        raise InternalServerError(message="Simulated server error", details={"simulated": True})
    
    return {"status": "healthy", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
