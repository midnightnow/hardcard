
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import APIRouter, HTTPException, Body, Path, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import datetime
import uuid

import databutton as db
from google.oauth2 import service_account # Added for Google Drive
from googleapiclient.discovery import build # Added for Google Drive
from googleapiclient.http import MediaIoBaseUpload # Added for Google Drive
import json # Added for Google Drive secret parsing
import io # Added for file upload

# Initialize Firebase Admin
try:
    if not firebase_admin._apps:
        service_account_info = db.secrets.get("FIREBASE_SERVICE_ACCOUNT")
        if not service_account_info:
            print("FIREBASE_SERVICE_ACCOUNT secret not found. Firestore integration will not work.")
            db_firestore = None
        else:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
            db_firestore = firestore.client()
            print("Firebase Admin SDK initialized successfully.")
    else:
        db_firestore = firestore.client()
        print("Firebase Admin SDK already initialized.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    db_firestore = None

router = APIRouter(prefix="/project-management", tags=["Project Management"])

# --- Pydantic Models ---

# Project Models
class ProjectBase(BaseModel):
    name: str = Field(..., example="New Website Launch")
    description: Optional[str] = Field(None, example="Launch the new company website by Q3.")
    owner: Optional[str] = Field(None, example="user@example.com")
    startDate: Optional[datetime.date] = Field(None, example="2024-06-01")
    endDate: Optional[datetime.date] = Field(None, example="2024-09-30")
    status: str = Field("Not Started", example="In Progress")  # "Not Started", "In Progress", "Completed", "On Hold", "Cancelled"
    priority: str = Field("Medium", example="High")  # "Low", "Medium", "High", "Urgent"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    startDate: Optional[datetime.date] = None
    endDate: Optional[datetime.date] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class ProjectInDB(ProjectBase):
    projectId: str = Field(..., example="proj_123xyz")
    createdAt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updatedAt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class ProjectResponse(ProjectInDB):
    pass

# Report Models
class TaskReportItem(BaseModel):
    taskId: str
    title: str
    status: str
    assignee: Optional[str] = None
    dueDate: Optional[datetime.date] = None

class ProjectReportItem(BaseModel):
    projectId: str
    name: str
    status: str
    owner: Optional[str] = None
    tasks: List[TaskReportItem] = []

class ProjectStatusReportResponse(BaseModel):
    reportGeneratedAt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    projects: List[ProjectReportItem] = []

# Task Models
class TaskBase(BaseModel):
    title: str = Field(..., example="Design Homepage Mockup")
    description: Optional[str] = Field(None, example="Create detailed mockups for the homepage.")
    assignee: Optional[str] = Field(None, example="designer@example.com")
    assigneeEmail: Optional[str] = Field(None, example="designer@example.com")  # Added for email notifications
    dueDate: Optional[datetime.date] = Field(None, example="2024-07-15")
    status: str = Field("To Do", example="In Progress")  # "To Do", "In Progress", "Done", "Blocked"

class TaskCreate(TaskBase):
    projectId: str = Field(..., example="proj_123xyz")

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    assigneeEmail: Optional[str] = None  # Added for email notifications
    dueDate: Optional[datetime.date] = None
    status: Optional[str] = None

class TaskInDB(TaskBase):
    taskId: str = Field(..., example="task_abc789")
    projectId: str
    createdAt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updatedAt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class TaskResponse(TaskInDB):
    pass

class DueDateReminderResponse(BaseModel):
    total_tasks_checked: int
    reminders_sent: int
    details: List[str]

class UploadReportResponse(BaseModel):
    message: str
    file_id: Optional[str] = None
    web_view_link: Optional[str] = None
    file_name: Optional[str] = None

# --- API Endpoints ---

# Project Endpoints
@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(project_data: ProjectCreate):
    """
    Create a new project.
    - **projectId**: Auto-generated UUID.
    - **createdAt, updatedAt**: Auto-generated timestamps.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available. Cannot create project.")
    
    project_id = f"proj_{uuid.uuid4()}"
    now = datetime.datetime.utcnow()
    
    new_project_data = project_data.model_dump()
    new_project_data["projectId"] = project_id
    new_project_data["createdAt"] = now
    new_project_data["updatedAt"] = now

    try:
        project_doc = ProjectInDB(**new_project_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating project data model: {e}") from e

    try:
        db_firestore.collection("projects").document(project_id).set(project_doc.model_dump())
        print(f"Project {project_id} created successfully in Firestore.")
        return project_doc
    except Exception as e:
        print(f"Error saving project {project_id} to Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not create project in database: {e}") from e

@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    status: Optional[str] = Query(None, description="Filter projects by status", example="In Progress"),
    priority: Optional[str] = Query(None, description="Filter projects by priority", example="High"),
    owner: Optional[str] = Query(None, description="Filter projects by owner's email", example="user@example.com")
):
    """
    List all projects. Supports filtering by status, priority, and owner.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available. Cannot list projects.")
    
    try:
        projects_ref = db_firestore.collection("projects")
        query = projects_ref

        if status:
            query = query.where("status", "==", status)
        if priority:
            query = query.where("priority", "==", priority)
        if owner:
            query = query.where("owner", "==", owner)
        
        query = query.order_by("createdAt", direction=firestore.Query.DESCENDING)

        project_docs = query.stream()
        projects_list = []
        for doc in project_docs:
            try:
                project_data = doc.to_dict()
                if 'startDate' in project_data and isinstance(project_data['startDate'], str):
                    project_data['startDate'] = datetime.datetime.fromisoformat(project_data['startDate'].replace('Z', '+00:00')).date()
                elif 'startDate' in project_data and isinstance(project_data['startDate'], datetime.datetime):
                    project_data['startDate'] = project_data['startDate'].date() 
                
                if 'endDate' in project_data and isinstance(project_data['endDate'], str):
                    project_data['endDate'] = datetime.datetime.fromisoformat(project_data['endDate'].replace('Z', '+00:00')).date()
                elif 'endDate' in project_data and isinstance(project_data['endDate'], datetime.datetime):
                    project_data['endDate'] = project_data['endDate'].date()

                if 'createdAt' in project_data and not isinstance(project_data['createdAt'], datetime.datetime):
                     project_data['createdAt'] = project_data['createdAt'].to_datetime().replace(tzinfo=None)
                if 'updatedAt' in project_data and not isinstance(project_data['updatedAt'], datetime.datetime):
                     project_data['updatedAt'] = project_data['updatedAt'].to_datetime().replace(tzinfo=None)

                projects_list.append(ProjectResponse(**project_data))
            except Exception as e:
                print(f"Error processing project document {doc.id}: {e}. Data: {doc.to_dict()}")
                continue 
        
        return projects_list
    except Exception as e:
        print(f"Error listing projects from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not list projects: {e}") from e

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str = Path(..., example="proj_123xyz")):
    """
    Get a single project by its ID.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        project_ref = db_firestore.collection("projects").document(project_id)
        project_doc = project_ref.get()

        if not project_doc.exists:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        project_data = project_doc.to_dict()
        
        if 'startDate' in project_data and isinstance(project_data['startDate'], str):
            project_data['startDate'] = datetime.datetime.fromisoformat(project_data['startDate'].replace('Z', '+00:00')).date()
        elif 'startDate' in project_data and isinstance(project_data['startDate'], datetime.datetime):
            project_data['startDate'] = project_data['startDate'].date()
        
        if 'endDate' in project_data and isinstance(project_data['endDate'], str):
            project_data['endDate'] = datetime.datetime.fromisoformat(project_data['endDate'].replace('Z', '+00:00')).date()
        elif 'endDate' in project_data and isinstance(project_data['endDate'], datetime.datetime):
            project_data['endDate'] = project_data['endDate'].date()

        if 'createdAt' in project_data and not isinstance(project_data['createdAt'], datetime.datetime):
            project_data['createdAt'] = project_data['createdAt'].to_datetime().replace(tzinfo=None)
        if 'updatedAt' in project_data and not isinstance(project_data['updatedAt'], datetime.datetime):
            project_data['updatedAt'] = project_data['updatedAt'].to_datetime().replace(tzinfo=None)
            
        return ProjectResponse(**project_data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error getting project {project_id} from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve project: {e}") from e

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str = Path(..., example="proj_123xyz"),
    project_update: ProjectUpdate = Body(...)
):
    """
    Update an existing project.
    Only provided fields will be updated.
    `updatedAt` timestamp will be automatically set.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        project_ref = db_firestore.collection("projects").document(project_id)
        project_doc = project_ref.get()

        if not project_doc.exists:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        existing_project_data = project_doc.to_dict()
        update_data = project_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided.")

        update_data["updatedAt"] = datetime.datetime.utcnow()
        
        project_ref.update(update_data)
        
        updated_project_data = {**existing_project_data, **update_data}

        if 'startDate' in updated_project_data and isinstance(updated_project_data['startDate'], str):
            updated_project_data['startDate'] = datetime.datetime.fromisoformat(updated_project_data['startDate'].replace('Z', '+00:00')).date()
        elif 'startDate' in updated_project_data and isinstance(updated_project_data['startDate'], datetime.datetime):
            updated_project_data['startDate'] = updated_project_data['startDate'].date()
        
        if 'endDate' in updated_project_data and isinstance(updated_project_data['endDate'], str):
            updated_project_data['endDate'] = datetime.datetime.fromisoformat(updated_project_data['endDate'].replace('Z', '+00:00')).date()
        elif 'endDate' in updated_project_data and isinstance(updated_project_data['endDate'], datetime.datetime):
            updated_project_data['endDate'] = updated_project_data['endDate'].date()
        
        if 'createdAt' in updated_project_data and not isinstance(updated_project_data['createdAt'], datetime.datetime):
             updated_project_data['createdAt'] = updated_project_data['createdAt'].to_datetime().replace(tzinfo=None) 
        if 'updatedAt' in updated_project_data and not isinstance(updated_project_data['updatedAt'], datetime.datetime):
            updated_project_data['updatedAt'] = updated_project_data['updatedAt'].to_datetime().replace(tzinfo=None) 

        return ProjectResponse(**updated_project_data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error updating project {project_id} in Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not update project: {e}") from e

@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str = Path(..., example="proj_123xyz")):
    """
    Delete a project by its ID.
    (Note: Consider soft delete vs hard delete. This is a hard delete.)
    Also, consider deleting associated tasks or handling them.
    For now, this only deletes the project document itself.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        project_ref = db_firestore.collection("projects").document(project_id)
        project_doc = project_ref.get()

        if not project_doc.exists:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")

        project_ref.delete()
        print(f"Project {project_id} deleted successfully from Firestore.")
        return None
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error deleting project {project_id} from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not delete project: {e}") from e


# Task Endpoints
@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate):
    """
    Create a new task for a specific project.
    - **taskId**: Auto-generated UUID.
    - **projectId**: Must be a valid existing project ID.
    - **createdAt, updatedAt**: Auto-generated timestamps.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        project_ref = db_firestore.collection("projects").document(task_data.projectId)
        project_doc = project_ref.get()
        if not project_doc.exists:
            raise HTTPException(status_code=404, detail=f"Project with ID {task_data.projectId} not found. Cannot create task.")

        task_id = f"task_{uuid.uuid4()}"
        now = datetime.datetime.utcnow()
        
        new_task_data = task_data.model_dump()
        new_task_data["taskId"] = task_id
        new_task_data["createdAt"] = now
        new_task_data["updatedAt"] = now
        
        task_doc_model = TaskInDB(**new_task_data)
        
        db_firestore.collection("tasks").document(task_id).set(task_doc_model.model_dump())
        print(f"Task {task_id} for project {task_data.projectId} created successfully.")
        return task_doc_model
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error creating task for project {task_data.projectId}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not create task: {e}") from e

@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_tasks_for_project(
    project_id: str = Path(..., description="ID of the project to list tasks for", example="proj_123xyz"),
    status: Optional[str] = Query(None, description="Filter tasks by status", example="In Progress"),
    assignee: Optional[str] = Query(None, description="Filter tasks by assignee's name/ID", example="user@example.com"),
    assigneeEmail: Optional[str] = Query(None, description="Filter tasks by assignee's email", example="user@example.com")
):
    """
    List all tasks for a specific project. Supports filtering by status and assignee.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        project_ref = db_firestore.collection("projects").document(project_id)
        project_doc = project_ref.get()
        if not project_doc.exists:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found.")

        tasks_query = db_firestore.collection("tasks").where("projectId", "==", project_id)

        if status is not None:
            tasks_query = tasks_query.where("status", "==", status)
        if assignee is not None:
            tasks_query = tasks_query.where("assignee", "==", assignee)
        if assigneeEmail is not None:
            tasks_query = tasks_query.where("assigneeEmail", "==", assigneeEmail)
        
        tasks_query = tasks_query.order_by("createdAt", direction=firestore.Query.DESCENDING)

        task_docs = tasks_query.stream()
        tasks_list = []
        for doc in task_docs:
            try:
                task_data = doc.to_dict()
                if 'dueDate' in task_data and isinstance(task_data['dueDate'], str):
                    task_data['dueDate'] = datetime.datetime.fromisoformat(task_data['dueDate'].replace('Z', '+00:00')).date()
                elif 'dueDate' in task_data and isinstance(task_data['dueDate'], datetime.datetime):
                     task_data['dueDate'] = task_data['dueDate'].date()
                
                if 'createdAt' in task_data and not isinstance(task_data['createdAt'], datetime.datetime):
                     task_data['createdAt'] = task_data['createdAt'].to_datetime().replace(tzinfo=None)
                if 'updatedAt' in task_data and not isinstance(task_data['updatedAt'], datetime.datetime):
                     task_data['updatedAt'] = task_data['updatedAt'].to_datetime().replace(tzinfo=None)

                tasks_list.append(TaskResponse(**task_data))
            except Exception as e:
                print(f"Error processing task document {doc.id} for project {project_id}: {e}. Data: {doc.to_dict()}")
                continue
        
        return tasks_list
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error listing tasks for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not list tasks: {e}") from e

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str = Path(..., example="task_abc789")):
    """
    Get a single task by its ID.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        task_ref = db_firestore.collection("tasks").document(task_id)
        task_doc = task_ref.get()

        if not task_doc.exists:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        task_data = task_doc.to_dict()
        
        if 'dueDate' in task_data and isinstance(task_data['dueDate'], str):
            task_data['dueDate'] = datetime.datetime.fromisoformat(task_data['dueDate'].replace('Z', '+00:00')).date()
        elif 'dueDate' in task_data and isinstance(task_data['dueDate'], datetime.datetime):
            task_data['dueDate'] = task_data['dueDate'].date()
        
        if 'createdAt' in task_data and not isinstance(task_data['createdAt'], datetime.datetime):
            task_data['createdAt'] = task_data['createdAt'].to_datetime().replace(tzinfo=None)
        if 'updatedAt' in task_data and not isinstance(task_data['updatedAt'], datetime.datetime):
            task_data['updatedAt'] = task_data['updatedAt'].to_datetime().replace(tzinfo=None)
            
        return TaskResponse(**task_data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error getting task {task_id} from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve task: {e}") from e

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str = Path(..., example="task_abc789"),
    task_update: TaskUpdate = Body(...)
):
    """
    Update an existing task.
    Only provided fields will be updated.
    `updatedAt` timestamp will be automatically set.
    `projectId` cannot be changed.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        task_ref = db_firestore.collection("tasks").document(task_id)
        task_doc = task_ref.get()

        if not task_doc.exists:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        existing_task_data = task_doc.to_dict()
        update_data = task_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided.")

        if "projectId" in update_data and update_data["projectId"] != existing_task_data.get("projectId"):
            raise HTTPException(status_code=400, detail="Cannot change the project ID of a task.")
        
        update_data["updatedAt"] = datetime.datetime.utcnow()
        
        task_ref.update(update_data)
        
        updated_task_data = {**existing_task_data, **update_data}

        if 'dueDate' in updated_task_data and isinstance(updated_task_data['dueDate'], str):
            updated_task_data['dueDate'] = datetime.datetime.fromisoformat(updated_task_data['dueDate'].replace('Z', '+00:00')).date()
        elif 'dueDate' in updated_task_data and isinstance(updated_task_data['dueDate'], datetime.datetime):
            updated_task_data['dueDate'] = updated_task_data['dueDate'].date()

        if 'createdAt' in updated_task_data and not isinstance(updated_task_data['createdAt'], datetime.datetime):
            updated_task_data['createdAt'] = updated_task_data['createdAt'].to_datetime().replace(tzinfo=None)
        if 'updatedAt' in updated_task_data and not isinstance(updated_task_data['updatedAt'], datetime.datetime):
            updated_task_data['updatedAt'] = updated_task_data['updatedAt'].to_datetime().replace(tzinfo=None) 

        return TaskResponse(**updated_task_data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error updating task {task_id} in Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not update task: {e}") from e

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str = Path(..., example="task_abc789")):
    """
    Delete a task by its ID.
    (Note: Consider soft delete vs hard delete. This is a hard delete.)
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    try:
        task_ref = db_firestore.collection("tasks").document(task_id)
        task_doc = task_ref.get()

        if not task_doc.exists:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")

        task_ref.delete()
        print(f"Task {task_id} deleted successfully from Firestore.")
        return None
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error deleting task {task_id} from Firestore: {e}")
        raise HTTPException(status_code=500, detail=f"Could not delete task: {e}") from e


@router.post("/tasks/trigger-due-date-reminders", response_model=DueDateReminderResponse)
async def trigger_due_date_reminders():
    """
    Scans for tasks due soon (within 24 hours or today) and sends email reminders
    to assignees who have an email address specified.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    now = datetime.datetime.utcnow()
    today_date = now.date()
    tomorrow_date = today_date + datetime.timedelta(days=1)

    reminders_sent_count = 0
    tasks_checked_count = 0
    reminder_details = []

    try:
        tasks_ref = db_firestore.collection("tasks")
        
        query1 = tasks_ref.where("status", "not-in", ["Done"]).where("dueDate", "==", today_date)
        query2 = tasks_ref.where("status", "not-in", ["Done"]).where("dueDate", "==", tomorrow_date)
        
        task_docs_today = list(query1.stream())
        task_docs_tomorrow = list(query2.stream())
        
        all_relevant_task_docs_map = {doc.id: doc for doc in task_docs_today}
        for doc in task_docs_tomorrow:
            if doc.id not in all_relevant_task_docs_map:
                all_relevant_task_docs_map[doc.id] = doc
        
        all_relevant_task_docs = list(all_relevant_task_docs_map.values())
        tasks_checked_count = len(all_relevant_task_docs)

        for task_doc in all_relevant_task_docs:
            task_data = task_doc.to_dict()
            task_title = task_data.get("title", "N/A")
            assignee_email = task_data.get("assigneeEmail")
            due_date_obj = task_data.get("dueDate")

            if isinstance(due_date_obj, str):
                try:
                    due_date_obj = datetime.datetime.fromisoformat(due_date_obj.replace('Z', '+00:00')).date()
                except ValueError:
                    due_date_obj = None
            elif isinstance(due_date_obj, datetime.datetime):
                due_date_obj = due_date_obj.date()
            
            if assignee_email and due_date_obj:
                try:
                    email_subject = f"Task Reminder: '{task_title}' is due soon"
                    email_content_text = f"Hello,\n\nThis is a friendly reminder that your task \"{task_title}\" is due on {due_date_obj.strftime('%Y-%m-%d')}.\n\nPlease update its status in the project management system.\n\nThank you,\nHempex Project System"
                    email_content_html = f"<p>Hello,</p><p>This is a friendly reminder that your task <strong>\"{task_title}\"</strong> is due on <strong>{due_date_obj.strftime('%Y-%m-%d')}</strong>.</p><p>Please update its status in the project management system.</p><p>Thank you,<br/>Hempex Project System</p>"
                    
                    db.notify.email(
                        to=[assignee_email],
                        subject=email_subject,
                        content_text=email_content_text,
                        content_html=email_content_html
                    )
                    reminders_sent_count += 1
                    reminder_details.append(f"Sent reminder for task '{task_title}' (ID: {task_doc.id}) to {assignee_email}.")
                except Exception as mail_e:
                    print(f"Error sending email for task {task_doc.id} to {assignee_email}: {mail_e}")
                    reminder_details.append(f"Failed to send reminder for task '{task_title}' (ID: {task_doc.id}) to {assignee_email}: {mail_e}")
            elif not assignee_email:
                 reminder_details.append(f"Skipped task '{task_title}' (ID: {task_doc.id}) - no assignee email.")
            elif not due_date_obj:
                 reminder_details.append(f"Skipped task '{task_title}' (ID: {task_doc.id}) - invalid or missing due date.")
        
        return DueDateReminderResponse(
            total_tasks_checked=tasks_checked_count,
            reminders_sent=reminders_sent_count,
            details=reminder_details
        )
    except Exception as e:
        print(f"Error in trigger_due_date_reminders: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing due date reminders: {e}") from e

@router.get("/reports/status", response_model=ProjectStatusReportResponse)
async def get_project_status_report(
    include_archived: bool = Query(False, description="Whether to include projects marked as 'Archived'.")
):
    """Generate a status report for all projects, including their tasks.
    By default, 'Archived' projects are excluded unless `include_archived` is true.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    report_items: List[ProjectReportItem] = []
    try:
        projects_query = db_firestore.collection("projects")
        # Order by creation date for consistency, can be changed or made configurable
        project_docs_stream = projects_query.order_by("createdAt", direction=firestore.Query.DESCENDING).stream()

        for project_doc in project_docs_stream:
            project_data = project_doc.to_dict()
            project_id = project_data.get("projectId")
            project_name = project_data.get("name", "N/A")
            project_status = project_data.get("status")
            project_owner = project_data.get("owner")

            if not include_archived and project_status == "Archived":
                continue  # Skip archived projects if not requested

            task_report_items: List[TaskReportItem] = []
            if project_id:  # Ensure project_id is valid before querying tasks
                tasks_query = (
                    db_firestore.collection("tasks")
                    .where("projectId", "==", project_id)
                    .order_by("createdAt", direction=firestore.Query.DESCENDING)
                )
                task_docs_stream = tasks_query.stream()
                for task_doc_item in task_docs_stream:
                    task_data = task_doc_item.to_dict()
                    
                    due_date_val = task_data.get("dueDate")
                    if isinstance(due_date_val, str):
                        try:
                            # Attempt to parse ISO format string date
                            due_date_val = datetime.datetime.fromisoformat(due_date_val.replace('Z', '+00:00')).date()
                        except ValueError:
                            due_date_val = None # Or handle error as appropriate
                    elif isinstance(due_date_val, datetime.datetime): # If it's already a datetime object (e.g. from Firestore Timestamp conversion)
                        due_date_val = due_date_val.date()
                    # If it's already a date object, no conversion needed.
                    # If None or other type, it remains as is (will be None if not a date/datetime/parsable string)

                    task_report_items.append(
                        TaskReportItem(
                            taskId=task_data.get("taskId", "N/A"),
                            title=task_data.get("title", "N/A"),
                            status=task_data.get("status", "N/A"),
                            assignee=task_data.get("assignee"),
                            dueDate=due_date_val
                        )
                    )
            
            report_items.append(
                ProjectReportItem(
                    projectId=project_id,
                    name=project_name,
                    status=project_status,
                    owner=project_owner,
                    tasks=task_report_items
                )
            )
        
        return ProjectStatusReportResponse(projects=report_items, reportGeneratedAt=datetime.datetime.utcnow())
    except Exception as e:
        print(f"Error generating project status report: {e}")
        raise HTTPException(status_code=500, detail=f"Could not generate project status report: {e}") from e

# Define constants for Google Drive
DRIVE_FOLDER_ID = "1o-qmHk9GKXlES3tAlfIpfFKOgzyP4s_w" # Hempex Project Reports

@router.post("/projects/{project_id}/upload_report_to_drive", response_model=UploadReportResponse)
async def upload_project_report_to_drive(project_id: str = Path(..., description="ID of the project to upload report for")):
    """
    Generates a status report for a specific project and uploads it to Google Drive.
    """
    if not db_firestore:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    google_drive_secret_json = db.secrets.get("GOOGLE_DRIVE_OAUTH_JSON")
    if not google_drive_secret_json:
        raise HTTPException(status_code=500, detail="GOOGLE_DRIVE_OAUTH_JSON secret not found.")

    try:
        # 1. Fetch project details
        project = await get_project(project_id) # Reuses existing endpoint logic
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found.")
        print(f"HTTPException fetching project {project_id}: {e.detail}")
        raise e # Re-raise other HTTPExceptions from get_project
    except Exception as e:
        print(f"Error fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve project details: {e}")

    try:
        # 2. Fetch tasks for the project
        tasks = await list_tasks_for_project(project_id=project_id) # Reuses existing endpoint logic
    except Exception as e:
        print(f"Error fetching tasks for project {project_id}: {e}")
        # Allow report generation even if tasks fail to load, but note it.
        tasks = [] 

    # 3. Format report content
    report_lines = []
    report_lines.append(f"Project Name: {project.name}")
    report_lines.append(f"Project ID: {project.projectId}")
    report_lines.append(f"Status: {project.status}")
    if project.owner:
        report_lines.append(f"Owner: {project.owner}")
    if project.startDate:
        report_lines.append(f"Start Date: {project.startDate.strftime('%Y-%m-%d') if isinstance(project.startDate, (datetime.date, datetime.datetime)) else project.startDate}")
    if project.endDate:
        report_lines.append(f"End Date: {project.endDate.strftime('%Y-%m-%d') if isinstance(project.endDate, (datetime.date, datetime.datetime)) else project.endDate}")
    report_lines.append(f"Report Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report_lines.append("\nTasks:")
    if tasks:
        for task_item in tasks: # tasks is List[TaskResponse]
            task_line = f"- Task: {task_item.title} (ID: {task_item.taskId})"
            task_line += f", Status: {task_item.status}"
            if task_item.assignee:
                task_line += f", Assignee: {task_item.assignee}"
            if task_item.dueDate:
                task_line += f", Due: {task_item.dueDate.strftime('%Y-%m-%d') if isinstance(task_item.dueDate, (datetime.date, datetime.datetime)) else task_item.dueDate}"
            report_lines.append(task_line)
    else:
        report_lines.append("  No tasks found for this project or tasks could not be retrieved.")
    report_content_str = "\n".join(report_lines)
    report_content_bytes = report_content_str.encode('utf-8')

    # 4. Upload to Google Drive
    try:
        credentials_info = json.loads(google_drive_secret_json)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/drive.file'] 
        )
        drive_service = build('drive', 'v3', credentials=credentials)

        file_name = f"{project.projectId}_report_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.txt"
        file_metadata = {
            'name': file_name,
            'parents': [DRIVE_FOLDER_ID]
        }
        
        media = MediaIoBaseUpload(io.BytesIO(report_content_bytes), mimetype='text/plain', resumable=True)
        
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, name'
        ).execute()

        print(f"Report for project {project_id} uploaded to Google Drive. File ID: {uploaded_file.get('id')}")
        return UploadReportResponse(
            message="Report uploaded successfully to Google Drive.",
            file_id=uploaded_file.get('id'),
            web_view_link=uploaded_file.get('webViewLink'),
            file_name=uploaded_file.get('name')
        )

    except Exception as e:
        print(f"Error uploading report to Google Drive for project {project_id}: {e}")
        # Consider if more specific error messages can be returned to the client
        raise HTTPException(status_code=500, detail=f"Could not upload report to Google Drive: {str(e)}")



