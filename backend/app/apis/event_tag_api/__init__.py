from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import datetime
import uuid

router = APIRouter(tags=["Event Tags"])

class GeoCoordinates(BaseModel):
    latitude: float
    longitude: float

class EventTagCreate(BaseModel):
    name: str
    event_type: str
    actor: str
    timestamp: str  # Expecting ISO 8601 format string
    description: Optional[str] = None
    coordinates: Optional[GeoCoordinates] = None
    reference_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class EventTagRead(EventTagCreate):
    id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

@router.post("/event-tags", response_model=EventTagRead, status_code=status.HTTP_201_CREATED)
async def create_event_tag(payload: EventTagCreate) -> EventTagRead:
    """
    Create a new Event Tag.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    # In a real application, this data would be saved to a database.
    # For now, we just return it with an ID and timestamps.
    
    # Validate timestamp format (basic check)
    try:
        datetime.datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid timestamp format. Expected ISO 8601 string.",
        ) from e

    # Validate coordinates if provided
    if payload.coordinates:
        if not (-90 <= payload.coordinates.latitude <= 90):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid latitude. Must be between -90 and 90.",
            ) # No specific error to chain here for simple validation
        if not (-180 <= payload.coordinates.longitude <= 180):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid longitude. Must be between -180 and 180.",
            ) # No specific error to chain here for simple validation
            
    new_id = str(uuid.uuid4())
    
    event_tag_data = payload.dict()
    
    # Ensure all optional fields that are None are handled correctly
    # Pydantic models handle this by excluding None values from the model dict by default if exclude_none=True,
    # but here we are creating EventTagRead from EventTagCreate's data.

    response_data = {
        "id": new_id,
        **event_tag_data,
        "created_at": now,
        "updated_at": now,
    }
    
    # Ensure coordinates is correctly passed if it exists
    if payload.coordinates:
        response_data["coordinates"] = payload.coordinates.dict()
    else:
        response_data["coordinates"] = None

    return EventTagRead(**response_data)

# Example usage (for testing, not part of the API itself)
# async def main():
#     test_payload = EventTagCreate(
#         name="Test Event",
#         event_type="Test",
#         actor="Test Actor",
#         timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
#         description="A test event.",
#         coordinates=GeoCoordinates(latitude=0.0, longitude=0.0),
#         reference_ids=["ref1", "ref2"],
#         metadata={"key": "value"}
#     )
#     created_tag = await create_event_tag_endpoint(test_payload)
#     print(created_tag)

