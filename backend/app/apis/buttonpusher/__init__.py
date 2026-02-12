import json
import time
import uuid
import os
import threading
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.libs.ticket_schema import Ticket, TicketComment, TicketUpdate
from app.libs.serena_schemas import SerenaTask, SerenaPlan
from fastapi import APIRouter, HTTPException
import databutton as db

router = APIRouter()

# Project model definitions
class ProjectStatus(str):
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    REVIEW = "review"
    PUBLISHING = "publishing"
    COMPLETE = "complete"
    ERROR = "error"

class Project(BaseModel):
    id: str
    name: str
    status: str
    progress: int  # 0-100
    lastUpdated: str

class ProjectRunRequest(BaseModel):
    pass

class ProjectRulesRequest(BaseModel):
    rules: str

# In-memory project store (reset on server restart)
projects_store: Dict[str, Project] = {}

# Threading locks and controls
project_locks: Dict[str, threading.Lock] = {}
project_stop_events: Dict[str, threading.Event] = {}

# Rules directory
RULES_DIR = "rules"
os.makedirs(RULES_DIR, exist_ok=True)

# Helper functions
def get_current_time() -> str:
    """Get current time in ISO format"""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def save_rules_to_storage(project_id: str, rules: str) -> None:
    """Save rules to db.storage"""
    key = f"buttonpusher_rules_{project_id}"
    db.storage.text.put(key, rules)

def get_rules_from_storage(project_id: str) -> str:
    """Get rules from db.storage"""
    key = f"buttonpusher_rules_{project_id}"
    try:
        return db.storage.text.get(key)
    except FileNotFoundError:
        return ""

def run_project_background(project_id: str):
    """
    Background task to simulate project execution
    Moves through states and updates progress automatically
    """
    if project_id not in projects_store:
        return
    
    project = projects_store[project_id]
    stop_event = project_stop_events[project_id]
    lock = project_locks[project_id]
    
    # Predefined status flow
    status_flow = [
        ProjectStatus.QUEUED,
        ProjectStatus.RUNNING,
        ProjectStatus.REVIEW,
        ProjectStatus.PUBLISHING,
        ProjectStatus.COMPLETE
    ]
    
    current_status_idx = 0
    
    try:
        # Update to first status (queued)
        with lock:
            project.status = status_flow[current_status_idx]
            project.lastUpdated = get_current_time()
            projects_store[project_id] = project
        
        current_status_idx += 1
        
        # Run through statuses
        while current_status_idx < len(status_flow):
            status = status_flow[current_status_idx]
            
            # Determine how long to stay in this status (simulated)
            steps = 5 if status == ProjectStatus.RUNNING else 3
            progress_per_step = (100 - project.progress) / steps if status == ProjectStatus.RUNNING else 0
            
            for _ in range(steps):
                if stop_event.is_set():
                    return
                
                with lock:
                    project.status = status
                    if status == ProjectStatus.RUNNING:
                        project.progress = min(project.progress + int(progress_per_step), 100)
                    project.lastUpdated = get_current_time()
                    projects_store[project_id] = project
                
                # Wait a bit
                time.sleep(5)  # Poll interval matches frontend
                
                if stop_event.is_set():
                    return
            
            current_status_idx += 1
    
    except Exception as e:
        with lock:
            project.status = ProjectStatus.ERROR
            project.lastUpdated = get_current_time()
            projects_store[project_id] = project
        print(f"Error in project run: {e}")

# Seed initial projects on module load
def seed_initial_projects():
    """Seed initial projects for demonstration"""
    # Using fixed IDs for testing and development
    seed_projects = [
        {"id": "a1b2c3d4-e5f6-7890-1234-567890abcdef", "name": "Hardcard Core Refactor", "status": ProjectStatus.IDLE, "progress": 20, "lastUpdated": get_current_time()},
        {"id": "b2c3d4e5-f6a7-8901-2345-67890abcdef1", "name": "LegacyVault API Docs", "status": ProjectStatus.IDLE, "progress": 55, "lastUpdated": get_current_time()},
        {"id": "c3d4e5f6-a7b8-9012-3456-7890abcdef12", "name": "MacAgent Test Suite", "status": ProjectStatus.IDLE, "progress": 0, "lastUpdated": get_current_time()}
    ]
    
    for project_data in seed_projects:
        project = Project(**project_data)
        projects_store[project.id] = project
        project_locks[project.id] = threading.Lock()
        project_stop_events[project.id] = threading.Event()

# Seed on module initialization
seed_initial_projects()

# API endpoints
@router.get("/projects", response_model=List[Project])
def get_legacy_projects():
    """
    Get all projects for the ButtonPusher dashboard
    """
    return list(projects_store.values())

@router.post("/projects/{project_id}/run")
def run_legacy_project(project_id: str, request: ProjectRunRequest):
    """
    Start or continue running a project
    Triggers progression through status states and progress updates
    """
    if project_id not in projects_store:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_store[project_id]
    
    # Check if already running
    if project.status in [ProjectStatus.QUEUED, ProjectStatus.RUNNING, ProjectStatus.REVIEW, ProjectStatus.PUBLISHING]:
        return {"message": "Project already in progress"}
    
    # Reset stop event if it exists
    if project_id in project_stop_events:
        project_stop_events[project_id].clear()
    else:
        project_stop_events[project_id] = threading.Event()
    
    # Start background task
    thread = threading.Thread(target=run_project_background, args=(project_id,))
    thread.daemon = True
    thread.start()
    
    return {"message": "Project run started"}

@router.post("/projects/{project_id}/rules")
def save_project_rules(project_id: str, request: ProjectRulesRequest):
    """
    Save intervention rules for a project
    Rules are stored in db.storage and can be retrieved later
    """
    if project_id not in projects_store:
        raise HTTPException(status_code=404, detail="Project not found")
    
    save_rules_to_storage(project_id, request.rules)
    
    return {"message": "Rules saved successfully"}

@router.get("/projects/{project_id}/rules")
def get_project_rules(project_id: str):
    """
    Get intervention rules for a project
    """
    if project_id not in projects_store:
        raise HTTPException(status_code=404, detail="Project not found")
    
    rules = get_rules_from_storage(project_id)
    
    return {"rules": rules}
