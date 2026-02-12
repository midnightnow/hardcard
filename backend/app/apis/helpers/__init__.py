from fastapi import APIRouter

router = APIRouter(prefix="/helpers", tags=["Helpers"])

@router.get("/health")
async def helpers_health_check():
    return {"message": "Helpers API is up and running!"} # Forcing a save
