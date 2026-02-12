from fastapi import APIRouter, HTTPException
from typing import List, Tuple, Dict
from datetime import datetime, timedelta, timezone
import math

from app.libs.hardcard_spiral_dtos import (
    SpiralUnlocksRequest,
    SpiralUnlocksResponse,
    SpiralParameters,
    UnlockEventView
)
from app.libs.spiral_geometry import compute_spiral
from app.libs.spiral_events import overlay_unlock_events

router = APIRouter(
    prefix="/hardcard/spiral",
    tags=["Hardcard Spiral Visualizations"]
)

def get_default_spiral_parameters() -> SpiralParameters:
    """Returns default parameters for the spiral."""
    return SpiralParameters(
        start_angle_radians=0.0,
        end_angle_radians=8 * math.pi, # Roughly 4 full turns
        a_param=5.0, # Initial radius / scaling factor
        b_param=0.15, # Growth rate
        num_points=500
    )

# Mock data function - replace with actual data fetching logic later
def fetch_unlock_events_for_profile(profile_id: str) -> List[Dict]:
    """Mocks fetching unlock events for a given profile ID."""
    print(f"Fetching (mocked) unlock events for profile_id: {profile_id}")
    base_date = datetime.now(timezone.utc)
    return [
        {
            "event_id": "unlock_evt_1",
            "unlock_date": (base_date + timedelta(days=365 * 1)).isoformat(),
            "label": "Year 1 Unlock"
        },
        {
            "event_id": "unlock_evt_5",
            "unlock_date": (base_date + timedelta(days=365 * 5)).isoformat(),
            "label": "Year 5 Milestone"
        },
        {
            "event_id": "unlock_evt_10",
            "unlock_date": (base_date + timedelta(days=365 * 10)).isoformat(),
            "label": "Decade Check-in"
        },
        {
            "event_id": "unlock_evt_18",
            "unlock_date": (base_date + timedelta(days=365 * 18)).isoformat(),
            "label": "Age 18 Handover"
        }
    ]

def generate_svg_path_data(points: List[Tuple[float, float]]) -> str:
    """Converts a list of (x,y) points to an SVG path 'd' attribute string."""
    if not points:
        return ""
    return "M " + " L ".join([f"{p[0]:.2f},{p[1]:.2f}" for p in points])

@router.post("/unlocks", response_model=SpiralUnlocksResponse)
def spiral_unlocks_view(request: SpiralUnlocksRequest) -> SpiralUnlocksResponse:
    """Generates an SVG representation of a spiral timeline with unlock events."""
    try:
        spiral_params = request.parameters if request.parameters else get_default_spiral_parameters()
        
        center_x = request.view_width / 2
        center_y = request.view_height / 2

        # This computes the raw, unscaled spiral points centered around (center_x, center_y)
        # Scaling and full SVG generation will be handled by overlay_unlock_events
        spiral_path_points = compute_spiral(spiral_params, center_x, center_y)
        
        raw_unlock_events = fetch_unlock_events_for_profile(request.profile_id)
        
        # overlay_unlock_events now returns (svg_string, List[UnlockEventView])
        # It handles scaling, path generation, and event marker rendering internally.
        final_svg_markup, rendered_event_views = overlay_unlock_events(
            unlock_events_data=raw_unlock_events,
            spiral_path_points=spiral_path_points, # Pass raw points for it to scale
            svg_width=request.view_width,
            svg_height=request.view_height
        )

        return SpiralUnlocksResponse(
            svg_markup=final_svg_markup,
            unlock_events_rendered=rendered_event_views
        )
    except Exception as e:
        print(f"Error in spiral_unlocks_view: {e}")
        # Consider specific error types and more detailed responses
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

