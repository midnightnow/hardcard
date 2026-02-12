# src/app/apis/jobs/__init__.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from app.apis.firebase_utils import get_firestore_client
from app.auth import AuthorizedUser

router = APIRouter(prefix="/jobs", tags=["Jobs"])

class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    budget: float
    skills: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    client_id: str

class JobInDB(Job):
    pass

@router.post("", response_model=Job)
async def create_job(job: Job, user: AuthorizedUser):
    """
    Creates a new job listing.
    """
    fs_client = get_firestore_client()
    if fs_client is None:
        raise HTTPException(status_code=503, detail="Job board service is temporarily unavailable.")

    job_data = job.dict()
    job_data["client_id"] = user.sub # Associate job with the authenticated user

    try:
        fs_client.collection("jobs").document(job.id).set(job_data)
        print(f"Successfully created job {job.id} for user {user.sub}")
    except Exception as e:
        print(f"CRITICAL: Failed to create job {job.id} in Firestore for user {user.sub}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

    return job

@router.get("", response_model=List[Job])
async def get_jobs():
    """
    Retrieves all job listings.
    """
    fs_client = get_firestore_client()
    if fs_client is None:
        raise HTTPException(status_code=503, detail="Job board service is temporarily unavailable.")

    try:
        jobs_ref = fs_client.collection("jobs").stream()
        jobs = [JobInDB(**job.to_dict()).dict() for job in jobs_ref]
        return jobs
    except Exception as e:
        print(f"Failed to retrieve jobs from Firestore: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs.")
