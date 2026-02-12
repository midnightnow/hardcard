from fastapi import APIRouter
router = APIRouter()

bitcoinlib_status = "Temporarily Disabled for Debugging"

@router.get("/test-bitcoinlib-import-status")
async def get_bitcoinlib_import_status():
    return {"import_status": bitcoinlib_status}