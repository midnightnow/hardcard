from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Body
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import databutton as db
import uuid
import json
import time
import re
from datetime import datetime

router = APIRouter()

# GemInstance status constants
GEM_STATUS = {
    "PENDING": "pending",
    "ACTIVE": "active",
    "PAUSED": "paused",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "TERMINATED": "terminated",
    "DESTROYED": "destroyed"
}

# GemInstance traceability level constants
TRACEABILITY_LEVEL = {
    "EPHEMERAL": "ephemeral",
    "PRIVATE": "private",
    "AUDITABLE": "auditable",
    "TRANSPARENT": "transparent"
}

# GemInstance task types
GEM_TASK_TYPES = {
    "FINE_TUNING": "fine-tuning",
    "DATA_PREPROCESSING": "data-preprocessing",
    "MODEL_EVALUATION": "model-evaluation",
    "CUSTOM_CODE": "custom-code",
    "DATA_ANNOTATION": "data-annotation"
}

# Helper function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Models for the API
class GemInstanceCreateRequest(BaseModel):
    jobId: str
    providerId: str
    name: Optional[str] = None
    description: Optional[str] = None
    traceability: str = TRACEABILITY_LEVEL["AUDITABLE"]
    taskType: Optional[str] = None

class GemInstanceStartRequest(BaseModel):
    gemId: str
    agentId: Optional[str] = None

class GemInstancePauseRequest(BaseModel):
    gemId: str

class GemInstanceResumeRequest(BaseModel):
    gemId: str

class GemInstanceCompleteRequest(BaseModel):
    gemId: str
    hash: Optional[str] = None
    outputRef: Optional[str] = None

class GemInstanceFailRequest(BaseModel):
    gemId: str
    reason: Optional[str] = None

class GemInstanceTerminateRequest(BaseModel):
    gemId: str
    reason: Optional[str] = None

class GemInstanceAddLogRequest(BaseModel):
    gemId: str
    logEntry: str

class GemInstanceUpdateProgressRequest(BaseModel):
    gemId: str
    progressPercentage: int
    currentStep: Optional[str] = None

class GemInstanceResponse(BaseModel):
    id: str
    status: str
    message: str
    timestamp: str

# Helper function to store GemInstance in Databutton storage
def store_gem_instance(gem_instance: Dict[str, Any]) -> None:
    """Store GemInstance data in Databutton storage"""
    try:
        gem_id = gem_instance["id"]
        # Ensure storage key is sanitized and does not contain slashes
        storage_key = f"gem_instances_{sanitize_storage_key(gem_id)}"
        print(f"DEBUG - Storing gem instance with key: {storage_key}")
        db.storage.json.put(storage_key, gem_instance)
        
        # Also update the list of gem instances for the job
        job_id = gem_instance.get("jobId")
        if job_id:
            job_gems_key = f"job_gems_{sanitize_storage_key(job_id)}"
            print(f"DEBUG - Updating job gems list with key: {job_gems_key}")
            try:
                job_gems = db.storage.json.get(job_gems_key, default=[])
                if gem_id not in job_gems:
                    job_gems.append(gem_id)
                    db.storage.json.put(job_gems_key, job_gems)
            except Exception as e:
                print(f"Error updating job gems list: {str(e)}")
    except Exception as e:
        print(f"ERROR storing gem instance: {str(e)}")
        raise

# Helper function to retrieve GemInstance from Databutton storage
def get_gem_instance(gem_id: str) -> Dict[str, Any]:
    """Retrieve GemInstance data from Databutton storage"""
    sanitized_id = sanitize_storage_key(gem_id)
    storage_key = f"gem_instances_{sanitized_id}"
    try:
        return db.storage.json.get(storage_key)
    except:
        raise HTTPException(status_code=404, detail=f"GemInstance with ID {gem_id} not found")

# Helper function to add an audit log entry for GemInstance actions
def add_audit_log(gem_id: str, action: str, details: Dict[str, Any] = None) -> None:
    """Add an audit log entry for GemInstance actions"""
    try:
        sanitized_id = sanitize_storage_key(gem_id)
        audit_entry = {
            "gemId": gem_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        # Generate a unique audit log ID
        audit_log_id = str(uuid.uuid4())
        sanitized_audit_log_id = sanitize_storage_key(audit_log_id)
        
        # Store in audit log collection - use underscore instead of slashes
        audit_key = f"gem_audit_logs_{sanitized_id}_{sanitized_audit_log_id}"
        print(f"DEBUG - Adding audit log with key: {audit_key}")
        db.storage.json.put(audit_key, audit_entry)
    except Exception as e:
        print(f"ERROR adding audit log: {str(e)}")
        # Don't raise the exception to prevent breaking the main flow
        # Just log it instead

# Background task for handling the complete lifecycle of a GemInstance
def handle_gem_lifecycle(gem_id: str) -> None:
    """Background task for managing the complete lifecycle of a GemInstance"""
    try:
        sanitized_id = sanitize_storage_key(gem_id)
        gem_instance = get_gem_instance(sanitized_id)
        
        # In a real implementation, this would handle different lifecycle stages
        # For this demo, we'll just add a log entry
        current_time = datetime.utcnow().isoformat()
        log_entry = f"[{current_time}] Lifecycle manager initialized for GemInstance {gem_id}"
        
        if "logs" not in gem_instance:
            gem_instance["logs"] = []
            
        gem_instance["logs"].append(log_entry)
        store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(sanitized_id, "lifecycle_manager_initialized")
        
    except Exception as e:
        print(f"Error in GemInstance lifecycle handler: {str(e)}")

# Endpoint to create a new GemInstance
@router.post("/create-gem-instance")
def create_gem_instance(request: GemInstanceCreateRequest, background_tasks: BackgroundTasks) -> GemInstanceResponse:
    """Create a new GemInstance and initialize its lifecycle"""
    try:
        # Print debug info
        print(f"DEBUG - Request data: jobId={request.jobId}, providerId={request.providerId}")
        
        # Generate a unique ID for the GemInstance - use this first because we need it for error messages
        gem_id = f"gem-{uuid.uuid4()}"
        current_time = datetime.utcnow().isoformat()
        
        # First, sanitize the keys to ensure they are valid for storage
        sanitized_job_id = sanitize_storage_key(request.jobId)
        sanitized_provider_id = sanitize_storage_key(request.providerId)
        
        # Log the sanitized values
        print(f"DEBUG - Sanitized values: jobId={sanitized_job_id}, providerId={sanitized_provider_id}")
        
        # Create GemInstance object
        gem_instance = {
            "id": gem_id,
            "jobId": sanitized_job_id,
            "providerId": sanitized_provider_id,
            "name": request.name or f"GemInstance {gem_id}",
            "description": request.description or f"GemInstance for job {sanitized_job_id}",
            "status": GEM_STATUS["PENDING"],
            "traceability": request.traceability,
            "createdAt": current_time,
            "logs": [f"[{current_time}] GemInstance created and initialized"],
            "progressPercentage": 0,
            "taskType": request.taskType or GEM_TASK_TYPES["CUSTOM_CODE"]
        }
        
        # Store the GemInstance
        store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(gem_id, "created", {"jobId": request.jobId, "providerId": request.providerId})
        
        # Start background task for lifecycle management
        background_tasks.add_task(handle_gem_lifecycle, gem_id)
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance created successfully",
            timestamp=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating GemInstance: {str(e)}")

# Endpoint to start a GemInstance
@router.post("/start-gem-instance")
def start_gem_instance(request: GemInstanceStartRequest) -> GemInstanceResponse:
    """Start a GemInstance and update its status"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        # Validate current status
        if gem_instance["status"] != GEM_STATUS["PENDING"] and gem_instance["status"] != GEM_STATUS["PAUSED"]:
            raise HTTPException(status_code=400, detail=f"Cannot start GemInstance in state {gem_instance['status']}")
        
        current_time = datetime.utcnow().isoformat()
        agent_id = request.agentId or f"agent-{uuid.uuid4()}"
        
        # Update GemInstance
        gem_instance["status"] = GEM_STATUS["ACTIVE"]
        gem_instance["startedAt"] = current_time
        gem_instance["agentId"] = agent_id
        gem_instance["currentStep"] = "Initialization"
        gem_instance["logs"].append(f"[{current_time}] GemInstance started with agent {agent_id}")
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(gem_id, "started", {"agentId": agent_id})
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance started successfully",
            timestamp=current_time
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting GemInstance: {str(e)}")

# Endpoint to pause a GemInstance
@router.post("/pause-gem-instance")
def pause_gem_instance(request: GemInstancePauseRequest) -> GemInstanceResponse:
    """Pause a running GemInstance"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        # Validate current status
        if gem_instance["status"] != GEM_STATUS["ACTIVE"]:
            raise HTTPException(status_code=400, detail=f"Cannot pause GemInstance in state {gem_instance['status']}")
        
        current_time = datetime.utcnow().isoformat()
        
        # Update GemInstance
        gem_instance["status"] = GEM_STATUS["PAUSED"]
        gem_instance["pausedAt"] = current_time
        gem_instance["currentStep"] = "Paused"
        gem_instance["logs"].append(f"[{current_time}] GemInstance paused")
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(gem_id, "paused")
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance paused successfully",
            timestamp=current_time
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error pausing GemInstance: {str(e)}")

# Endpoint to resume a GemInstance
@router.post("/resume-gem-instance")
def resume_gem_instance(request: GemInstanceResumeRequest) -> GemInstanceResponse:
    """Resume a paused GemInstance"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        # Validate current status
        if gem_instance["status"] != GEM_STATUS["PAUSED"]:
            raise HTTPException(status_code=400, detail=f"Cannot resume GemInstance in state {gem_instance['status']}")
        
        current_time = datetime.utcnow().isoformat()
        
        # Update GemInstance
        gem_instance["status"] = GEM_STATUS["ACTIVE"]
        gem_instance["resumedAt"] = current_time
        gem_instance["currentStep"] = "Resumed execution"
        gem_instance["logs"].append(f"[{current_time}] GemInstance resumed")
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(gem_id, "resumed")
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance resumed successfully",
            timestamp=current_time
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resuming GemInstance: {str(e)}")

# Endpoint to complete a GemInstance
@router.post("/complete-gem-instance")
def complete_gem_instance(request: GemInstanceCompleteRequest) -> GemInstanceResponse:
    """Mark a GemInstance as completed"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        # Validate current status
        if gem_instance["status"] != GEM_STATUS["ACTIVE"]:
            raise HTTPException(status_code=400, detail=f"Cannot complete GemInstance in state {gem_instance['status']}")
        
        current_time = datetime.utcnow().isoformat()
        
        # Update GemInstance
        gem_instance["status"] = GEM_STATUS["COMPLETED"]
        gem_instance["completedAt"] = current_time
        gem_instance["progressPercentage"] = 100
        gem_instance["currentStep"] = "Completed"
        
        # Add hash and output reference if provided
        if request.hash:
            gem_instance["hash"] = request.hash
        if request.outputRef:
            # Sanitize the output reference
            sanitized_output_ref = sanitize_storage_key(request.outputRef)
            gem_instance["outputRef"] = sanitized_output_ref
            
        gem_instance["logs"].append(f"[{current_time}] GemInstance completed successfully")
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        # Handle archiving based on traceability level
        if gem_instance["traceability"] == TRACEABILITY_LEVEL["EPHEMERAL"]:
            # For ephemeral instances, archive minimal data and remove logs
            archive_data = {
                "id": gem_id,
                "jobId": gem_instance["jobId"],
                "providerId": gem_instance["providerId"],
                "status": GEM_STATUS["COMPLETED"],
                "createdAt": gem_instance["createdAt"],
                "completedAt": current_time,
                "hash": gem_instance.get("hash", ""),
                "traceability": TRACEABILITY_LEVEL["EPHEMERAL"]
            }
            
            # Store minimal archive data
            archive_key = f"gem_archives/{gem_id}"
            db.storage.json.put(archive_key, archive_data)
            
            # Set the gem instance to only contain minimal data
            gem_instance = archive_data
            store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(gem_id, "completed", {
            "hash": request.hash,
            "outputRef": request.outputRef
        })
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance completed successfully",
            timestamp=current_time
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing GemInstance: {str(e)}")

# Endpoint to mark a GemInstance as failed
@router.post("/fail-gem-instance")
def fail_gem_instance(request: GemInstanceFailRequest) -> GemInstanceResponse:
    """Mark a GemInstance as failed"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        current_time = datetime.utcnow().isoformat()
        reason = request.reason or "Unspecified failure"
        
        # Update GemInstance
        gem_instance["status"] = GEM_STATUS["FAILED"]
        gem_instance["completedAt"] = current_time
        gem_instance["failureReason"] = reason
        gem_instance["currentStep"] = f"Failed: {reason}"
        gem_instance["logs"].append(f"[{current_time}] GemInstance failed: {reason}")
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(gem_id, "failed", {"reason": reason})
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance marked as failed",
            timestamp=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking GemInstance as failed: {str(e)}")

# Endpoint to terminate a GemInstance
@router.post("/terminate-gem-instance")
def terminate_gem_instance(request: GemInstanceTerminateRequest) -> GemInstanceResponse:
    """Terminate a GemInstance"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        current_time = datetime.utcnow().isoformat()
        reason = request.reason or "Terminated by user"
        
        # Update GemInstance
        gem_instance["status"] = GEM_STATUS["TERMINATED"]
        gem_instance["completedAt"] = current_time
        gem_instance["terminationReason"] = reason
        gem_instance["currentStep"] = f"Terminated: {reason}"
        gem_instance["logs"].append(f"[{current_time}] GemInstance terminated: {reason}")
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        # Add audit log entry
        add_audit_log(gem_id, "terminated", {"reason": reason})
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance terminated",
            timestamp=current_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error terminating GemInstance: {str(e)}")

# Endpoint to add a log entry to a GemInstance
@router.post("/add-gem-log")
def add_gem_log(request: GemInstanceAddLogRequest) -> GemInstanceResponse:
    """Add a log entry to a GemInstance"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        # Validate the instance is not in a terminal state
        terminal_states = [GEM_STATUS["COMPLETED"], GEM_STATUS["FAILED"], 
                          GEM_STATUS["TERMINATED"], GEM_STATUS["DESTROYED"]]
        
        if gem_instance["status"] in terminal_states:
            raise HTTPException(status_code=400, 
                               detail=f"Cannot add logs to GemInstance in terminal state {gem_instance['status']}")
        
        # Add the log entry
        if "logs" not in gem_instance:
            gem_instance["logs"] = []
            
        gem_instance["logs"].append(request.logEntry)
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="Log entry added successfully",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding log entry: {str(e)}")

# Endpoint to update GemInstance progress
@router.post("/update-gem-progress")
def update_gem_progress(request: GemInstanceUpdateProgressRequest) -> GemInstanceResponse:
    """Update the progress percentage and current step of a GemInstance"""
    try:
        gem_id = sanitize_storage_key(request.gemId)
        gem_instance = get_gem_instance(gem_id)
        
        # Validate the instance is active
        if gem_instance["status"] != GEM_STATUS["ACTIVE"]:
            raise HTTPException(status_code=400, 
                               detail=f"Cannot update progress for GemInstance in state {gem_instance['status']}")
        
        # Validate progress percentage
        if request.progressPercentage < 0 or request.progressPercentage > 100:
            raise HTTPException(status_code=400, 
                               detail=f"Progress percentage must be between 0 and 100")
        
        current_time = datetime.utcnow().isoformat()
        
        # Update progress
        gem_instance["progressPercentage"] = request.progressPercentage
        if request.currentStep:
            gem_instance["currentStep"] = request.currentStep
            # Add a log entry for the step change
            gem_instance["logs"].append(f"[{current_time}] {request.currentStep} - {request.progressPercentage}%")
        
        # Store updated GemInstance
        store_gem_instance(gem_instance)
        
        return GemInstanceResponse(
            id=gem_id,
            status="success",
            message="GemInstance progress updated",
            timestamp=current_time
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")

# Endpoint to retrieve GemInstance information
@router.get("/get-gem-instance/{gem_id}")
def get_gem_instance_endpoint(gem_id: str) -> Dict[str, Any]:
    """Retrieve information about a GemInstance"""
    try:
        sanitized_id = sanitize_storage_key(gem_id)
        return get_gem_instance(sanitized_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving GemInstance: {str(e)}")

# Endpoint to list GemInstances for a job
@router.get("/list-job-gems/{job_id}")
def list_job_gems_endpoint(job_id: str) -> List[Dict[str, Any]]:
    """List all GemInstances for a specific job"""
    try:
        # Sanitize job ID
        sanitized_job_id = sanitize_storage_key(job_id)
        
        # Get the list of gem IDs for this job
        job_gems_key = f"job_gems_{sanitized_job_id}"
        gem_ids = db.storage.json.get(job_gems_key, default=[])
        
        # Retrieve each GemInstance
        gems = []
        for gem_id in gem_ids:
            try:
                gem = get_gem_instance(sanitize_storage_key(gem_id))
                gems.append(gem)
            except Exception as e:
                print(f"Error retrieving gem {gem_id}: {str(e)}")
        
        return gems
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing GemInstances: {str(e)}")
