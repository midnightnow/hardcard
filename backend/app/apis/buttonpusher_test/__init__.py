from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import databutton as db
import json
import uuid
from datetime import datetime

from app.apis.v6 import (
    Project, ProjectStatus, Ticket, TicketStatus, sanitize_storage_key, save_project
)
from app.apis.buttonpusher_v6 import initialize_v6_test_data as v6_init_test_data

router = APIRouter(prefix="/testutil")

class CreateTestProjectRequest(BaseModel):
    title: str
    ticketCount: Optional[int] = 3

class TestProjectResponse(BaseModel):
    id: str
    title: str
    status: str
    tickets: List[dict]

@router.post("/create-project", tags=["ButtonPusher", "Testing"])
async def create_buttonpusher_test_project(request: CreateTestProjectRequest) -> TestProjectResponse:
    """Create a test project with sample tickets for ButtonPusher v6"""
    # Create ticket list
    tickets = []
    
    for i in range(request.ticketCount or 3):
        ticket_type = "HEAVY_PROCESS" if i % 2 == 0 else "LIGHT_PROCESS"
        ticket = Ticket(
            id=f"ticket-{i+1}",
            type=ticket_type,
            status=TicketStatus.READY,
            executor="content-forge" if i % 3 == 0 else "code-analyzer",
            payload={
                "task": f"Task {i+1} for {request.title}",
                "complexity": (i % 3) + 1,
                "params": {"param1": f"value{i+1}"}
            },
            dependsOn=[f"ticket-{i}"] if i > 0 else None,
            estCostUsd=0.05 * (i + 1),
            estMinutes=2 * (i + 1)
        )
        tickets.append(ticket)
    
    # Create project
    project = Project(
        title=request.title,
        status=ProjectStatus.READY,
        tickets=tickets,
        nextTicketId=tickets[0].id if tickets else None
    )
    
    # Generate ID and save
    project_id = str(uuid.uuid4())
    save_project(project_id, project)
    
    # Return response
    return TestProjectResponse(
        id=project_id,
        title=project.title,
        status=project.status.value,
        tickets=json.loads(json.dumps([ticket.model_dump() for ticket in project.tickets]))
    )

@router.delete("/clear-all", tags=["ButtonPusher", "Testing"])
async def clear_buttonpusher_test_data():
    """Clear all test projects and jobs for ButtonPusher v6"""
    try:
        # List all project files
        project_files = db.storage.json.list()
        for file in project_files:
            if file.name.startswith("bp_v6_"):
                db.storage.json.delete(file.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}") from e
    
    return {"message": "All v6 test data cleared successfully"}

@router.post("/init-v6-data", tags=["ButtonPusher", "Testing"])
async def initialize_v6_test_data2():
    """Initialize test data for ButtonPusher v6 with predefined projects and tickets"""
    try:
        result = v6_init_test_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing test data: {str(e)}") from e