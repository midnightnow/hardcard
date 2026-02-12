from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import databutton as db
import json
import time
import uuid
import re
from datetime import datetime

# Schema definition for ButtonPusher v6
from enum import Enum
from pydantic import Field

class TicketStatus(str, Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"

class Ticket(BaseModel):
    id: str
    type: str
    status: TicketStatus
    executor: str
    payload: Dict[str, Any]
    dependsOn: Optional[List[str]] = None
    estCostUsd: Optional[float] = None
    estMinutes: Optional[int] = None

class ProjectStatus(str, Enum):
    BACKLOG = "BACKLOG"
    READY = "READY"
    RUNNING = "RUNNING"
    DONE = "DONE"
    BLOCKED = "BLOCKED"

class Project(BaseModel):
    title: str
    status: ProjectStatus
    nextTicketId: Optional[str] = None
    tickets: List[Ticket]

class PushJobState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"
    PAUSED = "PAUSED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"

class PushJob(BaseModel):
    projectIds: List[str]
    userId: str
    createdAt: datetime
    state: PushJobState
    progress: float = Field(ge=0, le=100)
    logs: Optional[List[str]] = None

# End Schema definition

router = APIRouter(prefix="/v6")

# In-memory semaphore for heavy tasks
MAX_CONCURRENT_HEAVY = 3
active_heavy = 0

# Storage helpers
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_project(project_id: str) -> Optional[Project]:
    """Get a project from storage"""
    try:
        project_data = db.storage.json.get(sanitize_storage_key(f"bp_v6_project_{project_id}"))
        if isinstance(project_data, dict):
            return Project.model_validate(project_data)
        return None
    except Exception:
        return None

def save_project(project_id: str, project: Project) -> None:
    """Save a project to storage"""
    db.storage.json.put(sanitize_storage_key(f"bp_v6_project_{project_id}"), 
                        json.loads(project.model_dump_json()))

def get_push_job(job_id: str) -> Optional[PushJob]:
    """Get a push job from storage"""
    try:
        job_data = db.storage.json.get(sanitize_storage_key(f"bp_v6_job_{job_id}"))
        if isinstance(job_data, dict):
            if isinstance(job_data.get('createdAt'), str):
                job_data['createdAt'] = datetime.fromisoformat(job_data['createdAt'])
            return PushJob.model_validate(job_data)
        return None
    except Exception:
        return None

def save_push_job(job_id: str, job: PushJob) -> None:
    """Save a push job to storage"""
    job_dict = json.loads(job.model_dump_json())
    # Convert datetime to ISO string for storage
    if isinstance(job_dict.get('createdAt'), datetime):
        job_dict['createdAt'] = job_dict['createdAt'].isoformat()
    db.storage.json.put(sanitize_storage_key(f"bp_v6_job_{job_id}"), job_dict)

def list_projects() -> List[Dict[str, Any]]:
    """List all projects"""
    projects = []
    try:
        # List all project files
        project_files = db.storage.json.list()
        for file in project_files:
            if file.name.startswith("bp_v6_project_"):
                project_id = file.name[14:]  # Remove 'bp_v6_project_' prefix
                project_data = db.storage.json.get(file.name)
                projects.append({"id": project_id, **project_data})
    except Exception as e:
        print(f"Error listing projects: {e}")
    return projects

# API models
class RunProjectRequest(BaseModel):
    project_id: str

class RunBatchRequest(BaseModel):
    project_ids: List[str]

class JobResponse(BaseModel):
    job_id: str

# Migration model
class MigrateProjectRequest(BaseModel):
    project_id: str
    name: str

# API routes
@router.get("/projects", tags=["ButtonPusher"])
async def get_projects():
    """Get all v6 projects for ButtonPusher"""
    return list_projects()

@router.post("/migrate", tags=["ButtonPusher"])
async def migrate_legacy_project(request: MigrateProjectRequest):
    """Migrate a legacy project to ButtonPusher v6 format"""
    # Create a new V6 project with a single legacy ticket
    project = Project(
        title=request.name,
        status=ProjectStatus.READY,
        tickets=[
            Ticket(
                id="legacy-all",
                type="LEGACY_PROJECT",
                status=TicketStatus.READY,
                executor="legacy-runner",
                payload={"legacyId": request.project_id}
            )
        ],
        nextTicketId="legacy-all"
    )
    
    # Generate a new UUID for the v6 project
    new_id = str(uuid.uuid4())
    save_project(new_id, project)
    
    return {"id": new_id, **json.loads(project.model_dump_json())}

@router.post("/projects/{project_id}/run", tags=["ButtonPusher"])
async def run_project(project_id: str, background_tasks: BackgroundTasks) -> JobResponse:
    """Run a single project"""
    # Check if project exists
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Create push job
    job_id = str(uuid.uuid4())
    job = PushJob(
        projectIds=[project_id],
        userId="anon",  # TODO: Add auth
        createdAt=datetime.now(),
        state=PushJobState.QUEUED,
        progress=0,
        logs=[]
    )
    save_push_job(job_id, job)
    
    # Start worker in background
    background_tasks.add_task(process_push_job, job_id)
    
    return JobResponse(job_id=job_id)

@router.post("/run-batch", tags=["ButtonPusher"])
async def run_batch(request: RunBatchRequest, background_tasks: BackgroundTasks) -> JobResponse:
    """Run multiple projects as a batch"""
    if not request.project_ids:
        raise HTTPException(status_code=400, detail="No project IDs provided")
    
    # Create push job
    job_id = str(uuid.uuid4())
    job = PushJob(
        projectIds=request.project_ids,
        userId="anon",  # TODO: Add auth
        createdAt=datetime.now(),
        state=PushJobState.QUEUED,
        progress=0,
        logs=[]
    )
    save_push_job(job_id, job)
    
    # Start worker in background
    background_tasks.add_task(process_push_job, job_id)
    
    return JobResponse(job_id=job_id)

@router.get("/jobs/{job_id}", tags=["ButtonPusher"])
async def get_job(job_id: str):
    """Get status of a push job"""
    job = get_push_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job

@router.get("/jobs", tags=["ButtonPusher"])
async def list_jobs():
    """List all push jobs"""
    jobs = []
    try:
        # List all job files
        job_files = db.storage.json.list()
        for file in job_files:
            if file.name.startswith("bp_v6_job_"):
                job_id = file.name[10:]  # Remove 'bp_v6_job_' prefix
                job_data = db.storage.json.get(file.name)
                if isinstance(job_data, dict):
                    if isinstance(job_data.get('createdAt'), str):
                        job_data['createdAt'] = datetime.fromisoformat(job_data['createdAt'])
                    jobs.append({"id": job_id, **job_data})
    except Exception as e:
        print(f"Error listing jobs: {e}")
    
    # Sort by creation date (newest first)
    jobs.sort(key=lambda j: j.get('createdAt', ''), reverse=True)
    return jobs

@router.post("/initialize", tags=["ButtonPusher"])
async def initialize_test_data():
    """Initialize test data for ButtonPusher v6"""
    try:
        # Create test projects
        projects = [
            {
                "id": "demo-project-1",
                "project": Project(
                    title="Content Generation Pipeline",
                    status=ProjectStatus.READY,
                    tickets=[
                        Ticket(
                            id="t1",
                            type="DATA_PREPARATION",
                            status=TicketStatus.READY,
                            executor="data-preprocessor",
                            payload={"source": "blog-content", "format": "markdown"},
                            estMinutes=5
                        ),
                        Ticket(
                            id="t2",
                            type="HEAVY_ML_PROCESSING",
                            status=TicketStatus.READY,
                            executor="content-forge",
                            payload={"template": "blog-post", "topic": "AI trends"},
                            dependsOn=["t1"],
                            estMinutes=15,
                            estCostUsd=0.85
                        ),
                        Ticket(
                            id="t3",
                            type="POST_PROCESSING",
                            status=TicketStatus.READY,
                            executor="content-publisher",
                            payload={"channels": ["blog", "social"]},
                            dependsOn=["t2"],
                            estMinutes=3
                        )
                    ],
                    nextTicketId="t1"
                )
            },
            {
                "id": "demo-project-2",
                "project": Project(
                    title="Data Analysis Report",
                    status=ProjectStatus.READY,
                    tickets=[
                        Ticket(
                            id="extract",
                            type="DATA_EXTRACTION",
                            status=TicketStatus.READY,
                            executor="data-extractor",
                            payload={"source": "sales-db", "timeframe": "Q2-2025"},
                            estMinutes=8
                        ),
                        Ticket(
                            id="analyze",
                            type="HEAVY_ANALYSIS",
                            status=TicketStatus.READY,
                            executor="data-analyzer",
                            payload={"metrics": ["conversion", "retention"]},
                            dependsOn=["extract"],
                            estMinutes=12,
                            estCostUsd=1.25
                        ),
                        Ticket(
                            id="visualize",
                            type="VISUALIZATION",
                            status=TicketStatus.READY,
                            executor="chart-generator",
                            payload={"type": "dashboard", "theme": "executive"},
                            dependsOn=["analyze"],
                            estMinutes=6
                        )
                    ],
                    nextTicketId="extract"
                )
            },
            {
                "id": "demo-project-3",
                "project": Project(
                    title="Code Review & Testing",
                    status=ProjectStatus.READY,
                    tickets=[
                        Ticket(
                            id="test-1",
                            type="CODE_TEST",
                            status=TicketStatus.READY,
                            executor="test-runner",
                            payload={"repo": "main", "suite": "unit-tests"},
                            estMinutes=6
                        ),
                        Ticket(
                            id="test-2",
                            type="CODE_TEST",
                            status=TicketStatus.READY,
                            executor="test-runner",
                            payload={"repo": "main", "suite": "integration-tests"},
                            dependsOn=["test-1"],
                            estMinutes=10
                        ),
                        Ticket(
                            id="review",
                            type="CODE_REVIEW",
                            status=TicketStatus.READY,
                            executor="code-reviewer",
                            payload={"repo": "main", "pr": "123"},
                            dependsOn=["test-2"],
                            estMinutes=15,
                            estCostUsd=0.50
                        )
                    ],
                    nextTicketId="test-1"
                )
            }
        ]
        
        # Save test projects
        for project_data in projects:
            save_project(project_data["id"], project_data["project"])
        
        # Create a completed job and an in-progress job
        job1_id = str(uuid.uuid4())
        job1 = PushJob(
            projectIds=["demo-project-3"],
            userId="demo-user",
            createdAt=datetime.now(),
            state=PushJobState.COMPLETE,
            progress=100,
            logs=[
                "🚀 Starting job execution",
                "▶️ Running test-1 for demo-project-3",
                "✅ test-1 DONE",
                "▶️ Running test-2 for demo-project-3",
                "✅ test-2 DONE",
                "▶️ Running review for demo-project-3",
                "✅ review DONE",
                "🎉 Job complete"
            ]
        )
        save_push_job(job1_id, job1)
        
        job2_id = str(uuid.uuid4())
        job2 = PushJob(
            projectIds=["demo-project-1"],
            userId="demo-user",
            createdAt=datetime.now(),
            state=PushJobState.RUNNING,
            progress=33,
            logs=[
                "🚀 Starting job execution",
                "▶️ Running t1 for demo-project-1",
                "✅ t1 DONE",
                "▶️ Running t2 for demo-project-1"
            ]
        )
        save_push_job(job2_id, job2)
        
        return {"success": True, "message": "Test data initialized successfully"}
    except Exception as e:
        print(f"Error initializing test data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize test data: {str(e)}")

# Worker implementation
async def append_log(job_id: str, line: str) -> None:
    """Append a log line to a push job"""
    job = get_push_job(job_id)
    if not job:
        return
    
    if job.logs is None:
        job.logs = []
    
    job.logs.append(f"[{datetime.now().isoformat()}] {line}")
    save_push_job(job_id, job)

async def mark_error(job_id: str, msg: str) -> None:
    """Mark a job as error with message"""
    job = get_push_job(job_id)
    if not job:
        return
    
    job.state = PushJobState.ERROR
    await append_log(job_id, f"❌ {msg}")
    save_push_job(job_id, job)

async def mark_ticket_done(project_id: str, ticket_id: str) -> None:
    """Mark a ticket as done in a project"""
    project = get_project(project_id)
    if not project:
        return
    
    # Update ticket status
    for ticket in project.tickets:
        if ticket.id == ticket_id:
            ticket.status = TicketStatus.DONE
    
    # Update project status
    project.status = ProjectStatus.DONE
    save_project(project_id, project)

async def call_executor(executor: str, payload: Dict[str, Any]) -> bool:
    """Call an executor service (stub implementation)"""
    print(f"EXEC {executor} with payload: {payload}")
    # Simulate execution time
    time.sleep(1)
    # In a real implementation, this would call a service or run code to execute the task
    return True

import asyncio
import httpx
from fastapi import BackgroundTasks, HTTPException

# Add a helper to call the executor
async def call_executor(executor: str, payload: Dict[str, Any]) -> bool:
    """Call an executor service to process a task"""
    print(f"EXEC {executor} with payload: {payload}")
    # Simulate execution time
    time.sleep(1)
    # In a real implementation, this would call a service or run code to execute the task
    return True

async def update_job_state(job_id: str, state: PushJobState) -> None:
    """Update the state of a push job"""
    job = get_push_job(job_id)
    if not job:
        return
    
    job.state = state
    save_push_job(job_id, job)

async def update_job_progress(job_id: str, progress: float) -> None:
    """Update the progress of a push job"""
    job = get_push_job(job_id)
    if not job:
        return
    
    job.progress = progress
    save_push_job(job_id, job)

async def update_ticket_status(project_id: str, ticket_id: str, status: TicketStatus) -> None:
    """Update a ticket's status in a project"""
    project = get_project(project_id)
    if not project:
        return
    
    for ticket in project.tickets:
        if ticket.id == ticket_id:
            ticket.status = status
            break
    
    save_project(project_id, project)

async def update_project_status(project_id: str, status: ProjectStatus) -> None:
    """Update a project's status"""
    project = get_project(project_id)
    if not project:
        return
    
    project.status = status
    save_project(project_id, project)

# --- Worker Process ---
async def process_push_job(job_id: str) -> None:
    """Process a push job (worker implementation)"""
    global active_heavy
    
    job = get_push_job(job_id)
    if not job or job.state not in [PushJobState.QUEUED, PushJobState.RUNNING]:
        return
    
    # Update job state
    await update_job_state(job_id, PushJobState.RUNNING)
    await append_log(job_id, "🚀 Starting job execution")
    
    total = len(job.projectIds)
    completed = 0
    
    for project_id in job.projectIds:
        project = get_project(project_id)
        if not project or project.status != ProjectStatus.READY:
            await append_log(job_id, f"⚠️ Project {project_id} not READY, skipping")
            continue
        
        # Find the next ticket to process
        next_ticket = None
        if project.nextTicketId:
            for ticket in project.tickets:
                if ticket.id == project.nextTicketId:
                    next_ticket = ticket
                    break
        
        if not next_ticket:
            await append_log(job_id, f"❌ No next ticket for {project_id}")
            await mark_error(job_id, f"No ticket for {project_id}")
            return
        
        # Throttle heavy tasks
        if next_ticket.type.startswith("HEAVY"):
            while active_heavy >= MAX_CONCURRENT_HEAVY:
                time.sleep(1)
            active_heavy += 1
        
        await append_log(job_id, f"▶️ Running {next_ticket.id} for {project_id}")
        try:
            success = await call_executor(next_ticket.executor, next_ticket.payload)
        except Exception as e:
            success = False
            print(f"Executor error: {e}")
        
        # Release semaphore
        if next_ticket.type.startswith("HEAVY"):
            active_heavy -= 1
        
        if success:
            await mark_ticket_done(project_id, next_ticket.id)
            await append_log(job_id, f"✅ {next_ticket.id} DONE")
            completed += 1
            job.progress = (completed / total) * 100
            save_push_job(job_id, job)
        else:
            await mark_error(job_id, f"Executor failed on {project_id}/{next_ticket.id}")
            return
    
    # All projects completed
    await update_job_state(job_id, PushJobState.COMPLETE)
    await update_job_progress(job_id, 100)
    await append_log(job_id, "🎉 Job complete")