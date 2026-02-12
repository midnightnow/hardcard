import databutton as db
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

router = APIRouter()

# Storage key for spiral parameters
SPIRAL_PARAMS_KEY = "hardcard_hyperspace_spiral_params"

# Default spiral parameters
DEFAULT_SPIRAL_PARAMS = {
    "pitch": 1.0,
    "turns_per_log_unit": 1.0,
    "initial_radius": 1.0,
    "wall_height": 1.0,
    "wall_thickness": 1.0,
    "intraluminal_diameter": 1.0,
    "total_diameter": 3.0,
    "default_start_time": 1.0,
    "default_end_time": 100.0,
    "default_step": 0.1
}

# Sample data points for demonstration
DEFAULT_DATA_POINTS = [
    {"id": "milestone-1", "time": 1.0, "label": "Birth", "color": "#ff3e00", "size": 0.3},
    {"id": "milestone-2", "time": 18.0, "label": "Age 18", "color": "#ffaa00", "size": 0.3},
    {"id": "milestone-3", "time": 30.0, "label": "Age 30", "color": "#00aaff", "size": 0.3},
    {"id": "milestone-4", "time": 60.0, "label": "Age 60", "color": "#aa00ff", "size": 0.3},
    {"id": "investment-1", "time": 1.5, "label": "First Investment", "color": "#00ff00", "size": 0.2}
]

# Sample relationships between data points
DEFAULT_RELATIONSHIPS = [
    {"source": "milestone-1", "target": "milestone-2", "label": "Childhood", "color": "#ffffff"},
    {"source": "milestone-2", "target": "milestone-3", "label": "Early Adult", "color": "#00ffaa"},
    {"source": "milestone-3", "target": "milestone-4", "label": "Mid Life", "color": "#aaaaff"},
    {"source": "milestone-1", "target": "investment-1", "label": "Initial Gift", "color": "#ffff00"}
]

def get_spiral_parameters():
    """Get the current spiral parameters from storage"""
    try:
        params_json = db.storage.text.get(SPIRAL_PARAMS_KEY, default=json.dumps(DEFAULT_SPIRAL_PARAMS))
        return json.loads(params_json)
    except Exception as e:
        print(f"Error reading spiral parameters: {e}")
        return DEFAULT_SPIRAL_PARAMS

def update_spiral_parameters(params):
    """Update the spiral parameters in storage"""
    current_params = get_spiral_parameters()
    
    # Update only the provided parameters
    for key, value in params.items():
        if key in current_params:
            current_params[key] = value
    
    # Calculate derived parameters
    current_params["intraluminal_diameter"] = current_params["initial_radius"]
    current_params["total_diameter"] = current_params["intraluminal_diameter"] + (2 * current_params["wall_thickness"])
    
    try:
        db.storage.text.put(SPIRAL_PARAMS_KEY, json.dumps(current_params))
        return current_params
    except Exception as e:
        print(f"Error updating spiral parameters: {e}")
        return None

def get_data_points():
    """Get data points from storage or return defaults"""
    try:
        data_key = "hardcard_hyperspace_data_points"
        data_json = db.storage.text.get(data_key, default=json.dumps(DEFAULT_DATA_POINTS))
        return json.loads(data_json)
    except Exception as e:
        print(f"Error reading data points: {e}")
        return DEFAULT_DATA_POINTS

def get_relationships():
    """Get relationships from storage or return defaults"""
    try:
        rel_key = "hardcard_hyperspace_relationships"
        rel_json = db.storage.text.get(rel_key, default=json.dumps(DEFAULT_RELATIONSHIPS))
        return json.loads(rel_json)
    except Exception as e:
        print(f"Error reading relationships: {e}")
        return DEFAULT_RELATIONSHIPS


# Pydantic models for API request/response validation
class SpiralParameters(BaseModel):
    pitch: Optional[float] = None
    turns_per_log_unit: Optional[float] = None
    initial_radius: Optional[float] = None
    wall_height: Optional[float] = None
    wall_thickness: Optional[float] = None
    intraluminal_diameter: Optional[float] = None
    total_diameter: Optional[float] = None
    default_start_time: Optional[float] = None
    default_end_time: Optional[float] = None
    default_step: Optional[float] = None


class DataPoint(BaseModel):
    id: str
    time: float
    label: str
    color: str
    size: float


class Relationship(BaseModel):
    source: str
    target: str
    label: str
    color: str


@router.get("/spiral-parameters", operation_id="get_spiral_parameters_endpoint_data_storage")
def get_spiral_parameters_data_storage_endpoint():
    """Endpoint to get the current spiral parameters"""
    params = get_spiral_parameters()
    return params


@router.post("/spiral-parameters", operation_id="update_spiral_parameters_endpoint_data_storage")
def update_spiral_parameters_data_storage_endpoint(params: SpiralParameters):
    """Endpoint to update the spiral parameters"""
    updated_params = update_spiral_parameters(params.dict(exclude_unset=True))
    if updated_params is None:
        raise HTTPException(status_code=500, detail="Failed to update spiral parameters")
    return updated_params


@router.get("/data-points", operation_id="get_data_points_data_storage")
def get_data_points_endpoint():
    """Endpoint to get the data points"""
    return get_data_points()


@router.get("/relationships", operation_id="get_relationships_data_storage")
def get_relationships_endpoint():
    """Endpoint to get the relationships between data points"""
    return get_relationships()
