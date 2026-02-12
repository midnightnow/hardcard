import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import databutton as db
from fastapi import APIRouter

# Import schemas from v6 API
from app.apis.v6 import TicketStatus, ProjectStatus, PushJobState, Ticket, Project, PushJob

# Define router
router = APIRouter()

# Constants
STORAGE_KEY = "buttonpusher_v6_data"

# Adapter for v6 Ticket to match legacy methods
class TicketAdapter:
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Ticket:
        # Convert legacy dict format to v6 Ticket model
        ticket_data = dict(data)
        if "depends_on" in ticket_data:
            ticket_data["dependsOn"] = ticket_data.pop("depends_on")
        if "est_cost_usd" in ticket_data:
            ticket_data["estCostUsd"] = ticket_data.pop("est_cost_usd")
        if "est_minutes" in ticket_data:
            ticket_data["estMinutes"] = ticket_data.pop("est_minutes")
        return Ticket.model_validate(ticket_data)
    
    @staticmethod
    def to_dict(ticket: Ticket) -> Dict[str, Any]:
        return ticket.model_dump()

# Adapter for v6 Project to match legacy methods
class ProjectAdapter:
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Project:
        # Convert legacy dict format to v6 Project model
        project_data = dict(data)
        if "tickets" in project_data and isinstance(project_data["tickets"], list):
            project_data["tickets"] = [TicketAdapter.from_dict(t) if isinstance(t, dict) else t for t in project_data["tickets"]]
        if "next_ticket_id" in project_data:
            project_data["nextTicketId"] = project_data.pop("next_ticket_id")
        return Project.model_validate(project_data)
    
    @staticmethod
    def to_dict(project: Project) -> Dict[str, Any]:
        return project.model_dump()

# Adapter for v6 PushJob to match legacy methods
class PushJobAdapter:
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> PushJob:
        # Convert legacy dict format to v6 PushJob model
        job_data = dict(data)
        if "project_ids" in job_data:
            job_data["projectIds"] = job_data.pop("project_ids")
        if "user_id" in job_data:
            job_data["userId"] = job_data.pop("user_id")
        if "created_at" in job_data:
            job_data["createdAt"] = job_data.pop("created_at")
        return PushJob.model_validate(job_data)
    
    @staticmethod
    def to_dict(job: PushJob) -> Dict[str, Any]:
        return job.model_dump()

# Data Store
class ButtonPusherStore:
    def __init__(self):
        self.projects: Dict[str, Project] = {}
        self.jobs: Dict[str, PushJob] = {}
        self.load()
        
    def save(self):
        """Save data to storage"""
        data = {
            "projects": [ProjectAdapter.to_dict(p) for p in self.projects.values()],
            "jobs": [PushJobAdapter.to_dict(j) for j in self.jobs.values()]
        }
        db.storage.json.put(STORAGE_KEY, data)
        
    def load(self):
        """Load data from storage"""
        try:
            data = db.storage.json.get(STORAGE_KEY)
            if data:
                self.projects = {p["id"]: ProjectAdapter.from_dict(p) for p in data.get("projects", [])}
                self.jobs = {j["id"]: PushJobAdapter.from_dict(j) for j in data.get("jobs", [])}
        except FileNotFoundError:
            self._seed_initial_data()
            self.save()
    
    def _seed_initial_data(self):
        """Seed with initial sample data"""
        # Create a few sample projects with tickets
        p1 = Project(
            title="Hardcard Core Refactor",
            status=ProjectStatus.READY,
            progress=20,
            tickets=[
                Ticket(
                    id="t1",
                    type="CODE_REFACTOR",
                    status=TicketStatus.READY,
                    executor="content-forge",
                    payload={"module": "hardcard", "action": "refactor"},
                    estMinutes=30
                )
            ],
            nextTicketId="t1"
        )
        
        p2 = Project(
            title="LegacyVault API Docs",
            status=ProjectStatus.READY,
            progress=55,
            tickets=[
                Ticket(
                    id="t2",
                    type="DOC_GEN",
                    status=TicketStatus.READY,
                    executor="content-forge",
                    payload={"module": "legacyvault", "action": "generate_docs"},
                    estMinutes=15
                )
            ],
            nextTicketId="t2"
        )
        
        p3 = Project(
            title="MacAgent Test Suite",
            status=ProjectStatus.READY,
            progress=0,
            tickets=[
                Ticket(
                    id="t3",
                    type="HEAVY_TEST_GEN",
                    status=TicketStatus.READY,
                    executor="test-forge",
                    payload={"module": "macagent", "action": "generate_tests"},
                    estMinutes=45,
                    estCostUsd=0.75
                )
            ],
            nextTicketId="t3"
        )
        
        # Add projects with IDs
        self.projects = {
            "p1": p1,
            "p2": p2,
            "p3": p3
        }

# Create a global instance for easy import
store = ButtonPusherStore()

# Utility functions
def initialize_data():
    """Initialize or reset data in storage"""
    store._seed_initial_data()
    store.save()
    return {"success": True, "message": "Data initialized successfully"}

def get_projects():
    """Get all projects"""
    store.load()  # Refresh from storage
    return [ProjectAdapter.to_dict(p) for p in store.projects.values()]

def get_jobs():
    """Get all jobs"""
    store.load()  # Refresh from storage
    return [PushJobAdapter.to_dict(j) for j in store.jobs.values()]

def create_job(project_ids: List[str], user_id: str = "anon"):
    """Create a new push job"""
    job = PushJob(
        projectIds=project_ids,
        userId=user_id,
        createdAt=datetime.utcnow().isoformat() + "Z",
        state=PushJobState.QUEUED,
        progress=0,
        logs=[]
    )
    store.jobs[job.id] = job
    store.save()
    return PushJobAdapter.to_dict(job)

def update_job_status(job_id: str, state: str, progress: int = None, log_message: str = None):
    """Update job status and progress"""
    if job_id not in store.jobs:
        return {"success": False, "error": "Job not found"}
    
    job = store.jobs[job_id]
    job.state = state
    
    if progress is not None:
        job.progress = progress
    
    if log_message:
        timestamp = datetime.utcnow().isoformat() + "Z"
        if job.logs is None:
            job.logs = []
        job.logs.append(f"[{timestamp}] {log_message}")
    
    store.save()
    return {"success": True}

def update_ticket_status(project_id: str, ticket_id: str, status: str):
    """Update a ticket's status"""
    if project_id not in store.projects:
        return {"success": False, "error": "Project not found"}
    
    project = store.projects[project_id]
    for ticket in project.tickets:
        if ticket.id == ticket_id:
            ticket.status = status
            
            # Update project status based on tickets
            if status == TicketStatus.DONE:
                all_done = all(t.status == TicketStatus.DONE for t in project.tickets)
                if all_done:
                    project.status = ProjectStatus.DONE
                    project.progress = 100
            elif status == TicketStatus.ERROR:
                project.status = ProjectStatus.BLOCKED
            
            store.save()
            return {"success": True}
    
    return {"success": False, "error": "Ticket not found"}

# Main execution for testing
if __name__ == "__main__":
    print("Initializing ButtonPusher v6 data...")
    result = initialize_data()
    print(result)
    
    print("\nProjects:")
    for project in get_projects():
        print(f"- {project['title']} ({project['id']}): {project['status']}")
        for ticket in project.get('tickets', []):
            print(f"  > {ticket['id']}: {ticket['type']} - {ticket['status']}")
            
    print("\nCreating test job...")
    job = create_job(["p1", "p2"])
    print(f"Job created: {job['id']}")
    
    print("\nUpdating job status...")
    update_job_status(job['id'], PushJobState.RUNNING, 10, "Job started")
    update_job_status(job['id'], PushJobState.RUNNING, 50, "Processing tickets")
    update_job_status(job['id'], PushJobState.COMPLETE, 100, "Job completed")
    
    print("\nUpdating ticket status...")
    update_ticket_status("p1", "t1", TicketStatus.RUNNING)
    update_ticket_status("p1", "t1", TicketStatus.DONE)
    
    print("\nFinal job status:")
    for job in get_jobs():
        print(f"- Job {job['id']}: {job['state']} - {job['progress']}%")
        for log in job.get('logs', []):
            print(f"  > {log}")