from fastapi import APIRouter, HTTPException, Depends
from app.auth import AuthorizedUser # Use AuthorizedUser from app.auth for Firebase Auth
from app.libs.scheduler_models import Job, JobCreateRequest, JobStatus,JobListResponse # Placeholder
from typing import Dict, List, Any
import databutton as db
import uuid
from datetime import datetime

# Import the birthday checker
from app.libs.birthday_checker import check_and_process_birthdays
# Import the new handover utility
from app.apis.handover_management import check_beneficiary_ages_and_update_status

router = APIRouter(
    prefix="/scheduler",
    tags=["Scheduler"]
)

# In-memory store for jobs (for simplicity, replace with persistent storage e.g. db.storage.json)
JOBS_DB_KEY = "scheduler_jobs_store"

def get_jobs_store() -> Dict[str, Dict]:
    return db.storage.json.get(JOBS_DB_KEY, default={})

def save_jobs_store(jobs: Dict[str, Dict]):
    db.storage.json.put(JOBS_DB_KEY, jobs)

@router.post("/jobs", response_model=Job)
async def create_job(job_request: JobCreateRequest, current_user: AuthorizedUser): # Assuming protected
    """
    Create a new scheduled job.
    (Example endpoint, adapt as needed for specific job types)
    """
    job_id = str(uuid.uuid4())
    job_data = job_request.dict()
    job_data.update({
        "id": job_id,
        "created_by": current_user.email, # or user_id
        "created_at": datetime.utcnow().isoformat(),
        "status": JobStatus.PENDING
    })
    
    jobs_store = get_jobs_store()
    jobs_store[job_id] = job_data
    save_jobs_store(jobs_store)
    
    return Job(**job_data)

@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(current_user: AuthorizedUser): # Assuming protected
    """
    List all scheduled jobs.
    """
    jobs_store = get_jobs_store()
    job_list = [Job(**job_data) for job_data in jobs_store.values()]
    return JobListResponse(jobs=job_list, total=len(job_list))

@router.get("/jobs/{job_id}", response_model=Job, operation_id="scheduler_get_job")
async def get_job(job_id: str, current_user: AuthorizedUser): # Assuming protected
    """
    Get details of a specific job.
    """
    jobs_store = get_jobs_store()
    job_data = jobs_store.get(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**job_data)

@router.post("/jobs/{job_id}/run") # Could be PUT for status change
async def run_job_manually(job_id: str, current_user: AuthorizedUser): # Assuming protected
    """
    Manually trigger a specific job to run (for admin/testing purposes).
    Actual job execution logic would be here or called from here.
    """
    jobs_store = get_jobs_store()
    job_data = jobs_store.get(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")

    # Example: Mark as running, then completed (actual logic would be more complex)
    job_data["status"] = JobStatus.RUNNING
    job_data["last_run_at"] = datetime.utcnow().isoformat()
    save_jobs_store(jobs_store)

    print(f"Job {job_id} (type: {job_data.get('job_type')}) triggered manually by {current_user.email}")
    # Simulate work
    # Here you would call the actual function for the job_data.get('job_type')
    
    job_data["status"] = JobStatus.COMPLETED # Or FAILED
    job_data["updated_at"] = datetime.utcnow().isoformat()
    save_jobs_store(jobs_store)
    
    return {"message": f"Job {job_id} run attempt finished.", "status": job_data["status"]}

@router.post("/trigger-birthday-checks", summary="Trigger Daily Birthday Check and Deposit Process")
async def trigger_birthday_check_and_deposit_process() -> Dict[str, Any]:
    """
    This endpoint is designed to be called by an automated scheduler (e.g., cron job)
    to initiate the daily process of checking for children's birthdays and
    attempting to make the automated Bitcoin deposits.

    It calls the `check_and_process_birthdays` function which handles:
    - Identifying children with birthdays today.
    - Simulating Bitcoin purchases.
    - Attempting to record these deposits via an internal API call.
    - Sending email notifications to parents regarding the outcome.

    **Note:** This endpoint should be secured to prevent unauthorized execution.
    Authentication/Authorization is currently a placeholder.
    """
    print("[SchedulerAPI] Received request to trigger birthday checks.")
    try:
        result_summary = check_and_process_birthdays()
        print(f"[SchedulerAPI] Birthday check process completed. Summary: {result_summary}")
        return result_summary
    except Exception as e:
        print(f"[SchedulerAPI] Critical error during scheduled birthday check process: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"A critical error occurred in the birthday check process: {str(e)}"
        ) from e

# New endpoint to trigger the beneficiary age check
@router.post("/trigger-beneficiary-age-check", status_code=202)
async def trigger_beneficiary_age_check_endpoint(current_user: AuthorizedUser): # Corrected for Firebase Auth
    """
    Manually triggers the process to check beneficiary ages and update trust statuses 
    to ELIGIBLE_FOR_HANDOVER if they are 18 or older.
    This is intended for admin use or scheduled invocation.
    """
    print(f"Beneficiary age check triggered by: {current_user.email}")
    try:
        check_beneficiary_ages_and_update_status()
        return {"message": "Beneficiary age check process initiated successfully."}
    except Exception as e:
        print(f"Error during beneficiary age check process: {e}")
        # Log the exception details for debugging
        # import traceback
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred during the age check process: {str(e)}") from e
