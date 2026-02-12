import math
import databutton as db
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

# Default spiral parameters
DEFAULT_PARAMETERS = {
    "pitch": 1.0,
    "turns_per_log_unit": 1.0,
    "initial_radius": 1.0,
    "wall_height": 1.0,
    "wall_thickness": 1.0,
    "intraluminal_diameter": 2.0,  # 2 * initial_radius
    "total_diameter": 4.0,         # 2 * wall_thickness + intraluminal_diameter
    "default_start_time": 1.0,
    "default_end_time": 100.0,
    "default_step": 0.1
}

# Storage keys
PARAMETERS_KEY = "spiral_hyperspace_parameters"
DATA_POINTS_KEY = "spiral_hyperspace_data_points"
RELATIONSHIPS_KEY = "spiral_hyperspace_relationships"

# Sample data points for initial visualization
SAMPLE_DATA_POINTS = [
    {
        "id": "birth",
        "time": 1.0,
        "label": "Birth",
        "color": "#4CAF50",
        "size": 0.3
    },
    {
        "id": "childhood",
        "time": 5.0,
        "label": "Childhood",
        "color": "#2196F3",
        "size": 0.25
    },
    {
        "id": "education",
        "time": 18.0,
        "label": "Education",
        "color": "#9C27B0",
        "size": 0.25
    },
    {
        "id": "career",
        "time": 25.0,
        "label": "Career",
        "color": "#FF9800",
        "size": 0.25
    },
    {
        "id": "family",
        "time": 30.0,
        "label": "Family",
        "color": "#E91E63",
        "size": 0.3
    },
    {
        "id": "retirement",
        "time": 65.0,
        "label": "Retirement",
        "color": "#795548",
        "size": 0.25
    }
]

# Sample relationships for initial visualization
SAMPLE_RELATIONSHIPS = [
    {
        "source": "birth",
        "target": "childhood",
        "label": "Growth",
        "color": "#4CAF50"
    },
    {
        "source": "childhood",
        "target": "education",
        "label": "Development",
        "color": "#2196F3"
    },
    {
        "source": "education",
        "target": "career",
        "label": "Advancement",
        "color": "#9C27B0"
    },
    {
        "source": "career",
        "target": "family",
        "label": "Balance",
        "color": "#FF9800"
    },
    {
        "source": "family",
        "target": "retirement",
        "label": "Legacy",
        "color": "#E91E63"
    }
]


def get_params_from_storage() -> Dict[str, Any]:
    """
    Get spiral parameters from storage or return defaults if not found
    """
    try:
        params = db.storage.json.get(PARAMETERS_KEY)
        
        # Update with any missing parameters from defaults
        for key, value in DEFAULT_PARAMETERS.items():
            if key not in params:
                params[key] = value
                
        # Ensure derived parameters are calculated
        params["intraluminal_diameter"] = 2 * params["initial_radius"]
        params["total_diameter"] = 2 * params["wall_thickness"] + params["intraluminal_diameter"]
        
        return params
    except:
        # Initialize parameters in storage
        db.storage.json.put(PARAMETERS_KEY, DEFAULT_PARAMETERS)
        return DEFAULT_PARAMETERS


def update_params_in_storage(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update spiral parameters in storage
    
    Args:
        updates: Dictionary of parameters to update
        
    Returns:
        Updated parameters dictionary
    """
    try:
        # Get current parameters
        params = get_params_from_storage()
        
        # Update with new values
        params.update(updates)
        
        # Recalculate derived parameters
        params["intraluminal_diameter"] = 2 * params["initial_radius"]
        params["total_diameter"] = 2 * params["wall_thickness"] + params["intraluminal_diameter"]
        
        # Save updated parameters
        db.storage.json.put(PARAMETERS_KEY, params)
        
        return params
    except Exception as e:
        print(f"Error updating parameters: {e}")
        return {}


def get_data_points() -> List[Dict[str, Any]]:
    """
    Get data points from storage or return sample data if not found
    """
    try:
        points = db.storage.json.get(DATA_POINTS_KEY)
        return points
    except:
        # Initialize with sample data
        db.storage.json.put(DATA_POINTS_KEY, SAMPLE_DATA_POINTS)
        return SAMPLE_DATA_POINTS


def get_relationships() -> List[Dict[str, Any]]:
    """
    Get relationships from storage or return sample data if not found
    """
    try:
        relationships = db.storage.json.get(RELATIONSHIPS_KEY)
        return relationships
    except:
        # Initialize with sample data
        db.storage.json.put(RELATIONSHIPS_KEY, SAMPLE_RELATIONSHIPS)
        return SAMPLE_RELATIONSHIPS

# Router Configuration
router = APIRouter(prefix="/spiral-hyperspace")

"""
Hardcard Hyperspace: Logarithmic Time Spiral
----------------------------------------------

This API provides mathematical models and calculations for the Hardcard Hyperspace representation,
which visualizes time as a 3D logarithmic spiral. The spiral's properties allow for intuitive
visualization of both near-term and far-future timeframes in a single continuous model.

Core Concept:
- Time is represented as a 3D spiral, with the origin (t=1) at the center and extending outwards
- The logarithmic scale compresses vast time spans into a manageable space
- The 3D spiral represents a "slice" of Hardcard Hyperspace, providing a visual and navigable
  representation of time and data relationships

Mathematical Model:
- Height (z-axis): z = pitch × ln(t)
- Angle (θ): θ = turnsPerLogUnit × ln(t)
- Radius: r = initialRadius + z 
- X-coordinate: x = r × cos(θ)
- Y-coordinate: y = r × sin(θ)

Geometric Properties:
- Wall Height: 1 unit (constant)
- Wall Thickness: 1 unit (constant, can be made variable)
- Intraluminal Diameter: Variable, defined by initialRadius
- Total Diameter: 2 × Wall Thickness + Intraluminal Diameter
"""

class SpiralCoordinates(BaseModel):
    """Coordinates for a point on the hyperspace spiral"""
    x: float
    y: float
    z: float
    radius: float
    theta: float
    time: float


class SpiralParametersResponse(BaseModel):
    """Parameters of the hyperspace spiral"""
    pitch: float = Field(..., description="Controls the vertical pitch of the spiral (z-axis scaling)")
    turns_per_log_unit: float = Field(..., description="Controls the tightness of the spiral (turns per logarithmic unit)")
    initial_radius: float = Field(..., description="The radius of the spiral at t=1 (the Eye of the Storm)")
    wall_height: float = Field(1.0, description="Height of the spiral walls (constant at 1 unit)")
    wall_thickness: float = Field(1.0, description="Thickness of the spiral walls (constant at 1 unit)")
    intraluminal_diameter: float = Field(..., description="Inner diameter defined by initialRadius")
    total_diameter: float = Field(..., description="2 × Wall Thickness + Intraluminal Diameter")
    default_start_time: float = Field(1.0, description="Default starting time value")
    default_end_time: float = Field(100.0, description="Default ending time value")
    default_step: float = Field(0.1, description="Default step size between points")


class DataPoint(BaseModel):
    """A data point on the hyperspace spiral"""
    id: str = Field(..., description="Unique identifier for the data point")
    time: float = Field(..., description="Time value for the data point")
    label: str = Field("", description="Label text for the data point")
    color: str = Field("#ff3e00", description="Color of the data point")
    size: float = Field(0.2, description="Size of the data point")


class Relationship(BaseModel):
    """A relationship between data points on the hyperspace spiral"""
    source: str = Field(..., description="ID of the source data point")
    target: str = Field(..., description="ID of the target data point")
    label: str = Field("", description="Label text for the relationship")
    color: str = Field("#ffffff", description="Color of the relationship line")


@router.get("/spiral-coordinates", operation_id="get_spiral_coordinates_hyperspace")
def get_spiral_coordinates_spiral_hyperspace(
    time: float = Query(1.0, gt=0, description="The time value to calculate coordinates for"),
    pitch: float = Query(1.0, gt=0, description="Controls the vertical pitch of the spiral"),
    turns_per_log_unit: float = Query(1.0, gt=0, description="Controls the tightness of the spiral"),
    initial_radius: float = Query(1.0, gt=0, description="The radius of the spiral at t=1")
) -> SpiralCoordinates:
    """Calculate coordinates on the hyperspace spiral for a given time point
    
    This endpoint calculates the exact 3D coordinates for a given time value on the logarithmic spiral.
    The resulting coordinates represent a precise position in the Hardcard Hyperspace model, allowing
    for placement of data points, events, or identities at specific temporal locations.
    
    The mathematical model uses these equations:
    - Height (z-axis): z = pitch × ln(t)
    - Angle (θ): θ = turnsPerLogUnit × ln(t)
    - Radius: r = initialRadius + z
    - X-coordinate: x = r × cos(θ)
    - Y-coordinate: y = r × sin(θ)
    
    Args:
        time: The time value (t > 0)
        pitch: Controls the vertical pitch of the spiral (z-axis scaling)
        turns_per_log_unit: How many turns per logarithmic unit (affects spiral tightness)
        initial_radius: The radius of the spiral at t=1 (the Eye of the Storm)
        
    Returns:
        The 3D coordinates and properties of the point on the spiral
    """
    if time <= 0:
        # Time must be positive for logarithmic calculations
        time = 0.001
        
    # Calculate the logarithmic height based on pitch parameter
    z = pitch * math.log(time)
    
    # Calculate the spiral angle (theta)
    theta = turns_per_log_unit * math.log(time)
    
    # Calculate the spiral radius with initial_radius parameter
    radius = initial_radius + z

    # Ensure radius is positive. If the calculated radius is non-positive,
    # cap it at a small epsilon to prevent math errors and represent a point near/at the XY origin for that Z.
    if radius <= 0:
        radius = 0.001  # Epsilon value
    
    # Calculate x and y coordinates using the (potentially capped) radius
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    
    return SpiralCoordinates(
        x=x,
        y=y,
        z=z,
        radius=radius,
        theta=theta,
        time=time
    )


@router.get("/spiral-range", operation_id="get_spiral_range_hyperspace")
def get_spiral_range_spiral_hyperspace(
    start_time: float = Query(1.0, gt=0, description="The starting time value"),
    end_time: float = Query(100.0, gt=0, description="The ending time value"),
    step: float = Query(0.1, gt=0, description="Step size between points"),
    pitch: float = Query(1.0, gt=0, description="Controls the vertical pitch of the spiral"),
    turns_per_log_unit: float = Query(1.0, gt=0, description="Controls the tightness of the spiral"),
    initial_radius: float = Query(1.0, gt=0, description="The radius of the spiral at t=1")
) -> List[SpiralCoordinates]:
    """Calculate a range of coordinates on the hyperspace spiral
    
    This endpoint generates a series of points along the logarithmic spiral between the specified start and end times.
    The resulting array forms a complete path through the Hardcard Hyperspace for the given time period, which
    can be used for visualization, animation, or analysis of temporal progressions.
    
    The step parameter controls the granularity of the generated points, with smaller steps producing
    smoother but more data-intensive results.
    
    Args:
        start_time: The starting time value (t > 0)
        end_time: The ending time value (t > start_time)
        step: Step size between points (smaller steps = smoother spiral)
        pitch: Controls the vertical pitch of the spiral (z-axis scaling)
        turns_per_log_unit: How many turns per logarithmic unit (affects spiral tightness)
        initial_radius: The radius of the spiral at t=1 (the Eye of the Storm)
        
    Returns:
        A list of 3D coordinates along the spiral
    """
    if start_time <= 0:
        start_time = 0.001
    if end_time <= start_time:
        end_time = start_time * 10
    
    points = []
    current_time = start_time
    
    while current_time <= end_time:
        points.append(get_spiral_coordinates_spiral_hyperspace(
            time=current_time,
            pitch=pitch,
            turns_per_log_unit=turns_per_log_unit,
            initial_radius=initial_radius
        ))
        current_time += step
        
    return points


@router.get("/data-points", operation_id="get_hyperspace_data_points_endpoint")
def get_hyperspace_data_points() -> List[DataPoint]:
    """Get data points mapped to the hyperspace spiral
    
    This endpoint returns a list of data points that are mapped to specific time values
    on the Hardcard Hyperspace spiral. These data points can represent milestones, events,
    investments, or other significant points in time.
    
    Each data point includes its position in time, visual properties like color and size,
    and an identifier that can be used to establish relationships between points.
    
    Returns:
        A list of data points on the spiral
    """
    return get_data_points()


@router.get("/relationships", operation_id="get_hyperspace_relationships_endpoint")
def get_hyperspace_relationships() -> List[Relationship]:
    """Get relationships between data points in hyperspace
    
    This endpoint returns a list of relationships between data points in the Hardcard Hyperspace.
    Relationships connect two data points and represent connections, flows, or progressions
    between events, milestones, or other temporal elements.
    
    Each relationship includes source and target point identifiers, optional label text,
    and visual properties like color.
    
    Returns:
        A list of relationships between data points
    """
    return get_relationships()


@router.get("/spiral-parameters", operation_id="get_spiral_parameters_unique_spiral_hyperspace")
def get_spiral_parameters_spiral_hyperspace() -> SpiralParametersResponse:
    """Get the parameters of the hyperspace spiral
    
    This endpoint returns the current configuration parameters for the Hardcard Hyperspace
    mathematical model, including the core mathematical parameters and derived geometric properties.
    
    The parameters define both the mathematical mapping of time to spatial coordinates and
    the physical representation of the spiral structure.
    
    Returns:
        The parameters defining the spiral
    """
    # Get parameters from storage
    params = get_params_from_storage()
    
    return SpiralParametersResponse(
        pitch=params["pitch"],
        turns_per_log_unit=params["turns_per_log_unit"],
        initial_radius=params["initial_radius"],
        wall_height=params["wall_height"],
        wall_thickness=params["wall_thickness"],
        intraluminal_diameter=params["intraluminal_diameter"],
        total_diameter=params["total_diameter"],
        default_start_time=params["default_start_time"],
        default_end_time=params["default_end_time"],
        default_step=params["default_step"]
    )


class SpiralParametersUpdateRequest(BaseModel):
    """Request body for updating spiral parameters"""
    pitch: Optional[float] = Field(None, gt=0, description="Controls the vertical pitch of the spiral")
    turns_per_log_unit: Optional[float] = Field(None, gt=0, description="Controls the tightness of the spiral")
    initial_radius: Optional[float] = Field(None, gt=0, description="The radius of the spiral at t=1")
    wall_height: Optional[float] = Field(None, gt=0, description="Height of the spiral walls")
    wall_thickness: Optional[float] = Field(None, gt=0, description="Thickness of the spiral walls")
    default_start_time: Optional[float] = Field(None, gt=0, description="Default starting time value")
    default_end_time: Optional[float] = Field(None, gt=0, description="Default ending time value")
    default_step: Optional[float] = Field(None, gt=0, description="Default step size between points")


@router.post("/spiral-parameters", operation_id="update_spiral_parameters_spiral_hyperspace")
async def update_spiral_parameters_spiral_hyperspace(request: SpiralParametersUpdateRequest) -> Dict[str, Any]:
    """Updates the spiral parameters.
    
    This endpoint allows customization of the Hardcard Hyperspace mathematical model by updating the core parameters
    that define the logarithmic spiral. The parameters control the shape, scale, and behavior of the spiral representation.
    
    The parameters are:
    - pitch: Controls the vertical pitch of the spiral (z-axis scaling)
    - turnsPerLogUnit: Controls the tightness of the spiral (number of turns per logarithmic unit)
    - initialRadius: The radius of the spiral at t=1 (the Eye of the Storm)
    - wallHeight: Height of the spiral walls
    - wallThickness: Thickness of the spiral walls
    - defaultStartTime: Default starting time value
    - defaultEndTime: Default ending time value
    - defaultStep: Default step size between points
    
    Changes to these parameters affect how time is visualized in the Hyperspace representation,
    allowing for different perspectives on temporal relationships and data visualization.
    """
    # Extract parameters from request, ignoring None values
    update_params = {k: v for k, v in request.dict().items() if v is not None}
    
    # Update parameters in storage
    updated_params = update_params_in_storage(update_params)
    
    if updated_params:
        return {
            "status": "success", 
            "message": "Parameters updated successfully",
            "parameters": updated_params
        }
    else:
        return {
            "status": "error", 
            "message": "Failed to update parameters"
        }


# Standard API paths as specified in the task (without hyphens)
# Legacy endpoint maintained for backward compatibility
@router.get("/spiral/coordinates")
def get_spiral_coordinates_without_hyphen(
    time: float = Query(1.0, gt=0, description="The time value to calculate coordinates for"),
    pitch: float = Query(1.0, gt=0, description="Controls the vertical pitch of the spiral"),
    turns_per_log_unit: float = Query(1.0, gt=0, description="Controls the tightness of the spiral"),
    initial_radius: float = Query(1.0, gt=0, description="The radius of the spiral at t=1")
) -> Dict[str, float]:
    """Retrieves the spiral coordinates for a specific time.
    
    This endpoint calculates the exact 3D coordinates for a given time value on the logarithmic spiral.
    The resulting coordinates represent a precise position in the Hardcard Hyperspace model, allowing
    for placement of data points, events, or identities at specific temporal locations.
    
    The mathematical model uses these equations:
    - Height (z-axis): z = pitch × ln(t)
    - Angle (θ): θ = turnsPerLogUnit × ln(t)
    - Radius: r = initialRadius + z
    - X-coordinate: x = r × cos(θ)
    - Y-coordinate: y = r × sin(θ)
    """
    # Forward to the standardized endpoint
    coordinates = get_spiral_coordinates_spiral_hyperspace(
        time=time,
        pitch=pitch,
        turns_per_log_unit=turns_per_log_unit,
        initial_radius=initial_radius
    )
    
    # Convert to the legacy format
    return {
        "x": coordinates.x,
        "y": coordinates.y,
        "z": coordinates.z,
        "t": coordinates.time
    }


# Legacy endpoint maintained for backward compatibility
@router.get("/spiral/range")
def get_spiral_range_without_hyphen(
    start_time: float = Query(1.0, gt=0, description="The starting time value"),
    end_time: float = Query(100.0, gt=0, description="The ending time value"),
    step: float = Query(0.1, gt=0, description="Step size between points"),
    pitch: float = Query(1.0, gt=0, description="Controls the vertical pitch of the spiral"),
    turns_per_log_unit: float = Query(1.0, gt=0, description="Controls the tightness of the spiral"),
    initial_radius: float = Query(1.0, gt=0, description="The radius of the spiral at t=1")
) -> List[Dict[str, float]]:
    """Retrieves an array of spiral coordinates for a time range.
    
    This endpoint generates a series of points along the logarithmic spiral between the specified start and end times.
    The resulting array forms a complete path through the Hardcard Hyperspace for the given time period, which
    can be used for visualization, animation, or analysis of temporal progressions.
    
    The step parameter controls the granularity of the generated points, with smaller steps producing
    smoother but more data-intensive results.
    
    Each point contains the complete coordinate data (x, y, z) along with the time value (t) it represents.
    """
    # Forward to the standardized endpoint
    points = get_spiral_range_spiral_hyperspace(
        start_time=start_time,
        end_time=end_time,
        step=step,
        pitch=pitch,
        turns_per_log_unit=turns_per_log_unit,
        initial_radius=initial_radius
    )
    
    # Convert to the legacy format
    return [
        {
            "x": point.x,
            "y": point.y,
            "z": point.z,
            "t": point.time
        } for point in points
    ]


# Legacy endpoint maintained for backward compatibility
@router.get("/spiral/parameters", operation_id="get_spiral_parameters_without_hyphen_legacy")
def get_spiral_parameters_without_hyphen() -> Dict[str, Any]:
    """Retrieves the current spiral parameters and geometric properties of the Hardcard Hyperspace model.
    
    Returns the mathematical and geometric parameters that define the logarithmic spiral representation
    of the Hardcard Hyperspace. This includes both the core mathematical parameters and the derived 
    geometric properties of the spiral model.
    
    The spiral parameters define how time is mapped to spatial coordinates, while the geometric properties
    define the physical characteristics of the spiral structure itself.
    """
    # Get parameters from storage
    params = get_params_from_storage()
    
    # Convert to camelCase for frontend
    return {
        # Mathematical model parameters
        "pitch": params["pitch"],
        "turnsPerLogUnit": params["turns_per_log_unit"],
        "initialRadius": params["initial_radius"],
        
        # Geometric properties
        "wallHeight": params["wall_height"],
        "wallThickness": params["wall_thickness"],
        "intraluminalDiameter": params["intraluminal_diameter"],
        "totalDiameter": params["total_diameter"],
        
        # Default visualization parameters
        "defaultStartTime": params["default_start_time"],
        "defaultEndTime": params["default_end_time"],
        "defaultStep": params["default_step"]
    }