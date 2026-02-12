from fastapi import APIRouter

router = APIRouter()
# This API group is intended to house shared Pydantic models.
# It does not expose any endpoints itself.
# Models can be imported from app.apis.models.role_definitions
