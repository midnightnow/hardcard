# identity_events API is intentionally left minimal as this feature has moved.
from fastapi import APIRouter

router = APIRouter(prefix="/identity_events", tags=["IdentityEvents"])

# No automatic endpoints here; identity event handling moved to core event_tags API.
