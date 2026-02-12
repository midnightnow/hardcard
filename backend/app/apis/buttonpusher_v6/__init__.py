from fastapi import APIRouter, Depends
from pydantic import BaseModel
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
import databutton as db

# Router for ButtonPusher v6 API
router = APIRouter()

# Ticket status enum
class TicketStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"

from app.libs.ticket_schema import Ticket

# Project status enum
class ProjectStatus(str, Enum):
    BACKLOG = "BACKLOG"
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    BLOCKED = "BLOCKED"

# Project model
class Project(BaseModel):
    id: str
    title: str
    status: ProjectStatus
    nextTicketId: Optional[str] = None
    tickets: List[Ticket]

# PushJob state enum
class PushJobState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PAUSED = "PAUSED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"

# PushJob model
class PushJob(BaseModel):
    id: str
    projectIds: List[str]
    userId: str
    createdAt: datetime
    state: PushJobState
    progress: float
    logs: Optional[List[str]] = None

# Storage keys
PROJECTS_KEY = "buttonpusher_v6_projects"
JOBS_KEY = "buttonpusher_v6_jobs"

# Helper to get projects from storage
def get_projects() -> List[Project]:
    try:
        projects_data = db.storage.json.get(PROJECTS_KEY, default={})
        return [
            Project(
                id=project_id,
                **project_data
            ) for project_id, project_data in projects_data.items()
        ]
    except Exception as e:
        print(f"Error getting projects: {e}")
        return []

# Helper to get jobs from storage
def get_jobs() -> List[PushJob]:
    try:
        jobs_data = db.storage.json.get(JOBS_KEY, default={})
        return [
            PushJob(
                id=job_id,
                **job_data
            ) for job_id, job_data in jobs_data.items()
        ]
    except Exception as e:
        print(f"Error getting jobs: {e}")
        return []


# Get all projects
@router.get("/buttonpusher_v6/projects")
def list_projects():
    """
    List all projects in the ButtonPusher v6 system.
    """
    return get_projects()

# Get all jobs
@router.get("/buttonpusher_v6/jobs")
def list_v6_jobs():
    """
    List all push jobs in the ButtonPusher v6 system.
    """
    return get_jobs()

# Get a specific job
@router.get("/buttonpusher_v6/jobs/{job_id}")
def get_v6_job(job_id: str):
    """
    Get details of a specific push job by ID.
    """
    jobs_data = db.storage.json.get(JOBS_KEY, default={})
    if job_id not in jobs_data:
        return {"error": "Job not found"}, 404
    
    return PushJob(id=job_id, **jobs_data[job_id])

# Run a single project
@router.post("/buttonpusher_v6/projects/{project_id}/run")
def start_project_job(project_id: str):
    """
    Start a push job for a single project.
    """
    # Check if project exists
    projects_data = db.storage.json.get(PROJECTS_KEY, default={})
    if project_id not in projects_data:
        return {"error": "Project not found"}, 404
    
    # Create a new job
    job_id = f"job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    new_job = {
        "projectIds": [project_id],
        "userId": "user-1",  # In production this would be the authenticated user
        "createdAt": datetime.now(),
        "state": PushJobState.QUEUED,
        "progress": 0,
        "logs": [f"[{datetime.now().isoformat()}] 🚀 Job created for project {project_id}"]
    }
    
    # Save job to storage
    jobs_data = db.storage.json.get(JOBS_KEY, default={})
    jobs_data[job_id] = new_job
    db.storage.json.put(JOBS_KEY, jobs_data)
    
    return {"job_id": job_id}

# Run multiple projects as a batch
@router.post("/buttonpusher_v6/run-batch")
def run_v6_batch(request: dict):
    """
    Start a push job for multiple projects.
    """
    project_ids = request.get("project_ids", [])
    if not project_ids:
        return {"error": "No project IDs provided"}, 400
    
    # Verify all projects exist
    projects_data = db.storage.json.get(PROJECTS_KEY, default={})
    for project_id in project_ids:
        if project_id not in projects_data:
            return {"error": f"Project {project_id} not found"}, 404
    
    # Create a new job
    job_id = f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    new_job = {
        "projectIds": project_ids,
        "userId": "user-1",  # In production this would be the authenticated user
        "createdAt": datetime.now(),
        "state": PushJobState.QUEUED,
        "progress": 0,
        "logs": [f"[{datetime.now().isoformat()}] 🚀 Batch job created for {len(project_ids)} projects"]
    }
    
    # Save job to storage
    jobs_data = db.storage.json.get(JOBS_KEY, default={})
    jobs_data[job_id] = new_job
    db.storage.json.put(JOBS_KEY, jobs_data)
    
    return {"job_id": job_id}

# Initialize test data
@router.post("/buttonpusher_v6/initialize")
def initialize_v6_test_data():
    """
    Initialize test data for the ButtonPusher v6 system.
    Creates sample projects with tickets.
    """
    # Clear existing data
    db.storage.json.put(PROJECTS_KEY, {})
    db.storage.json.put(JOBS_KEY, {})
    
    # Create sample projects
    projects_data = {}
    
    # Project 1: Simple content project
    projects_data["p1"] = {
        "title": "Content Generation",
        "status": ProjectStatus.READY,
        "nextTicketId": "t1-setup",
        "tickets": [
            {
                "id": "t1-setup",
                "type": "SETUP",
                "status": TicketStatus.READY,
                "executor": "content-forge",
                "payload": {
                    "prompt": "Initialize content generation pipeline"
                }
            },
            {
                "id": "t1-generate",
                "type": "HEAVY_GENERATION",
                "status": TicketStatus.BLOCKED,
                "executor": "content-forge",
                "payload": {
                    "prompt": "Generate 10 blog posts about AI"
                },
                "dependsOn": ["t1-setup"],
                "estCostUsd": 2.50,
                "estMinutes": 5
            },
            {
                "id": "t1-publish",
                "type": "PUBLISH",
                "status": TicketStatus.BLOCKED,
                "executor": "publisher",
                "payload": {
                    "target": "blog"
                },
                "dependsOn": ["t1-generate"]
            }
        ]
    }
    
    # Project 2: Code analysis
    projects_data["p2"] = {
        "title": "Code Analysis",
        "status": ProjectStatus.READY,
        "nextTicketId": "t2-analyze",
        "tickets": [
            {
                "id": "t2-analyze",
                "type": "CODE_ANALYSIS",
                "status": TicketStatus.READY,
                "executor": "code-analyzer",
                "payload": {
                    "repo": "https://github.com/example/repo",
                    "branch": "main"
                },
                "estCostUsd": 0.75,
                "estMinutes": 2
            },
            {
                "id": "t2-report",
                "type": "REPORT",
                "status": TicketStatus.BLOCKED,
                "executor": "reporter",
                "payload": {
                    "format": "markdown"
                },
                "dependsOn": ["t2-analyze"]
            }
        ]
    }
    
    # Project 3: Test suite
    projects_data["p3"] = {
        "title": "Test Suite",
        "status": ProjectStatus.READY,
        "nextTicketId": "t3-setup",
        "tickets": [
            {
                "id": "t3-setup",
                "type": "SETUP",
                "status": TicketStatus.READY,
                "executor": "test-runner",
                "payload": {
                    "framework": "jest"
                }
            },
            {
                "id": "t3-generate",
                "type": "TEST_GENERATION",
                "status": TicketStatus.BLOCKED,
                "executor": "test-generator",
                "payload": {
                    "coverage": 80
                },
                "dependsOn": ["t3-setup"]
            },
            {
                "id": "t3-run",
                "type": "TEST_EXECUTION",
                "status": TicketStatus.BLOCKED,
                "executor": "test-runner",
                "payload": {
                    "timeout": 30
                },
                "dependsOn": ["t3-generate"]
            }
        ]
    }
    
    # Save to storage
    db.storage.json.put(PROJECTS_KEY, projects_data)
    
    return {
        "success": True,
        "message": "Test data initialized with 3 projects and 9 tickets"
    }
