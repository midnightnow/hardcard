from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
import databutton as db
from app.libs.event_processor_service import run_event_processor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cron", tags=["Cron"])

# --- SECURITY ---
API_KEY_NAME = "X-Cron-Secret"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key():
    """
    Retrieves the cron secret from Databutton secrets.
    It's recommended to set a secret named CRON_SECRET.
    """
    cron_secret = db.secrets.get("CRON_SECRET")
    if not cron_secret:
        logger.error("CRON_SECRET is not set in Databutton secrets.")
        raise HTTPException(status_code=500, detail="Cron secret is not configured on the server.")
    return cron_secret

async def verify_api_key(api_key: str = Security(api_key_header), expected_key: str = Depends(get_api_key)):
    """
    Verifies that the provided API key matches the one stored in secrets.
    """
    if api_key != expected_key:
        logger.warning("Invalid cron secret provided.")
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# --- ENDPOINTS ---
@router.post("/process-escrow-events", dependencies=[Depends(verify_api_key)])
async def process_escrow_events():
    """
    A secure endpoint to trigger the smart contract event processing service.
    This should be called by a scheduled job (cron).
    
    Requires a valid secret token in the 'X-Cron-Secret' header.
    """
    logger.info("Cron job triggered: Processing escrow events.")
    try:
        result = run_event_processor()
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))
        return {"status": "success", "detail": result}
    except Exception as e:
        logger.error(f"Error in process_escrow_events endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

