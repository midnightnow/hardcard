from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
import math
from typing import List, Dict, Any, Optional

# This router is explicitly open to allow public access to the hyperspace visualization
router = APIRouter(tags=["open"])

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

class SpiralCoordinatesRequest(BaseModel):
    time: float = Field(..., description="The time value to compute coordinates for")
    pitch: float = Field(1.0, description="Controls the vertical pitch of the spiral (z-axis scaling)")
    turns_per_log_unit: float = Field(1.0, description="Controls the tightness of the spiral (turns per logarithmic unit)")
    initial_radius: float = Field(1.0, description="The radius of the spiral at t=1 (the Eye of the Storm)")
    
    class Config:
        schema_extra = {
            "example": {
                "time": 10.0,
                "pitch": 1.0,
                "turns_per_log_unit": 1.0,
                "initial_radius": 1.0
            }
        }

class SpiralCoordinatesResponse(BaseModel):
    x: float = Field(..., description="X-coordinate (horizontal position, east-west)")
    y: float = Field(..., description="Y-coordinate (horizontal position, north-south)")
    z: float = Field(..., description="Z-coordinate (vertical position, height)")
    radius: float = Field(..., description="Distance from center axis")
    theta: float = Field(..., description="Angular position around the spiral (in radians)")
    time: float = Field(..., description="The time value these coordinates represent")
    
    class Config:
        schema_extra = {
            "example": {
                "x": 2.214,
                "y": 0.767,
                "z": 2.303,
                "radius": 3.303,
                "theta": 2.303,
                "time": 10.0
            }
        }

class SpiralRangeRequest(BaseModel):
    start_time: float = Field(..., description="The starting time value for the range")
    end_time: float = Field(..., description="The ending time value for the range")
    step: float = Field(0.1, description="The step size for the time range (smaller values create smoother but more data-intensive results)")
    pitch: float = Field(1.0, description="Controls the vertical pitch of the spiral (z-axis scaling)")
    turns_per_log_unit: float = Field(1.0, description="Controls the tightness of the spiral (turns per logarithmic unit)")
    initial_radius: float = Field(1.0, description="The radius of the spiral at t=1 (the Eye of the Storm)")
    
    class Config:
        schema_extra = {
            "example": {
                "start_time": 1.0,
                "end_time": 100.0,
                "step": 0.1,
                "pitch": 1.0,
                "turns_per_log_unit": 1.0,
                "initial_radius": 1.0
            }
        }

class SpiralRangeResponse(BaseModel):
    points: List[Dict[str, float]] = Field(..., description="Array of points along the spiral, each with x, y, z coordinates and time value")
    
    class Config:
        schema_extra = {
            "example": {
                "points": [
                    {
                        "time": 1.0,
                        "x": 1.0,
                        "y": 0.0,
                        "z": 0.0,
                        "radius": 1.0,
                        "theta": 0.0
                    },
                    {
                        "time": 10.0,
                        "x": 2.214,
                        "y": 0.767,
                        "z": 2.303,
                        "radius": 3.303,
                        "theta": 2.303
                    }
                ]
            }
        }
    
class SpiralParametersResponse(BaseModel):
    pitch: float = Field(..., description="Controls the vertical pitch of the spiral (z-axis scaling)")
    turns_per_log_unit: float = Field(..., description="Controls the tightness of the spiral (turns per logarithmic unit)")
    initial_radius: float = Field(..., description="The radius of the spiral at t=1 (the Eye of the Storm)")
    
    class Config:
        schema_extra = {
            "example": {
                "pitch": 1.0,
                "turns_per_log_unit": 1.0,
                "initial_radius": 1.0
            }
        }

# Original endpoints with /hyperspace prefix
@router.post("/hyperspace/coordinates")
def get_spiral_coordinates(request: SpiralCoordinatesRequest) -> SpiralCoordinatesResponse:
    """Generate the coordinates for a single point on the Hardcard Hyperspace spiral."""
    time = request.time
    pitch = request.pitch
    turns_per_log_unit = request.turns_per_log_unit
    initial_radius = request.initial_radius
    
    # Ensure time is positive
    if time <= 0:
        time = 0.001
    
    # Calculate coordinates based on logarithmic spiral equations
    z = pitch * math.log(time)
    theta = turns_per_log_unit * math.log(time)
    radius = initial_radius + z
    
    # Convert to Cartesian coordinates
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    
    return SpiralCoordinatesResponse(
        x=x,
        y=y,
        z=z,
        radius=radius,
        theta=theta,
        time=time
    )

@router.post("/hyperspace/range")
def get_spiral_range(request: SpiralRangeRequest) -> SpiralRangeResponse:
    """Generate coordinates for a range of points on the Hardcard Hyperspace spiral."""
    points = []
    
    current_time = request.start_time
    while current_time <= request.end_time:
        # Ensure time is positive
        if current_time <= 0:
            current_time = 0.001
        
        # Calculate coordinates based on logarithmic spiral equations
        z = request.pitch * math.log(current_time)
        theta = request.turns_per_log_unit * math.log(current_time)
        radius = request.initial_radius + z
        
        # Convert to Cartesian coordinates
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        
        points.append({
            "time": current_time,
            "x": x,
            "y": y,
            "z": z,
            "radius": radius,
            "theta": theta
        })
        
        current_time += request.step
    
    return SpiralRangeResponse(points=points)

@router.get("/hyperspace/parameters")
def get_spiral_parameters() -> Dict[str, Any]:
    """Return the default parameters for the Hardcard Hyperspace spiral."""
    return {
        "wallHeight": 1.0,
        "wallThickness": 1.0,
        "internalRadius": 1.0,
        "pitch": 1.0,  # Controls the vertical pitch of the spiral
        "turnsPerLogUnit": 1.0,  # Controls the tightness of the spiral
        "initialRadius": 1.0,  # The radius of the spiral at t=1
        "defaultStartTime": 1.0,
        "defaultEndTime": 100.0,
        "defaultStep": 0.1
    }

# New endpoints for the Hyperspace spiral (exact paths from the task specification)
@router.get("/spiral/coordinates")
def get_spiral_coordinates_query(
    time: float,
    pitch: float = 1.0,
    turns_per_log_unit: float = 1.0,
    initial_radius: float = 1.0
) -> Dict[str, float]:
    """Retrieves the spiral coordinates for a specific time point.
    
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
    """Retrieves the spiral coordinates for a specific time."""
    # Ensure time is positive
    if time <= 0:
        time = 0.001
    
    # Calculate coordinates based on logarithmic spiral equations
    z = pitch * math.log(time)
    theta = turns_per_log_unit * math.log(time)
    radius = initial_radius + z
    
    # Convert to Cartesian coordinates
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    
    return {
        "x": x,
        "y": y,
        "z": z,
        "t": time
    }

@router.get("/spiral/range")
def get_spiral_range_query(
    start_time: float,
    end_time: float,
    step: float = 0.1,
    pitch: float = 1.0,
    turns_per_log_unit: float = 1.0,
    initial_radius: float = 1.0
) -> List[Dict[str, float]]:
    """Retrieves an array of spiral coordinates for a time range.
    
    This endpoint generates a series of points along the logarithmic spiral between the specified start and end times.
    The resulting array forms a complete path through the Hardcard Hyperspace for the given time period, which
    can be used for visualization, animation, or analysis of temporal progressions.
    
    The step parameter controls the granularity of the generated points, with smaller steps producing
    smoother but more data-intensive results.
    
    Each point contains the complete coordinate data (x, y, z) along with the time value (t) it represents.
    """
    """Retrieves an array of spiral coordinates for a time range."""
    points = []
    
    current_time = start_time
    while current_time <= end_time:
        # Ensure time is positive
        if current_time <= 0:
            current_time = 0.001
        
        # Calculate coordinates based on logarithmic spiral equations
        z = pitch * math.log(current_time)
        theta = turns_per_log_unit * math.log(current_time)
        radius = initial_radius + z
        
        # Convert to Cartesian coordinates
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        
        points.append({
            "x": x,
            "y": y,
            "z": z,
            "t": current_time
        })
        
        current_time += step
    
    return points

@router.get("/spiral/parameters", operation_id="get_spiral_parameters_main_hyperspace")
def get_spiral_parameters_hyperspace_endpoint() -> Dict[str, Any]:
    """Retrieves the current spiral parameters and geometric properties of the Hardcard Hyperspace model.
    
    Returns the mathematical and geometric parameters that define the logarithmic spiral representation
    of the Hardcard Hyperspace. This includes both the core mathematical parameters and the derived 
    geometric properties of the spiral model.
    
    The spiral parameters define how time is mapped to spatial coordinates, while the geometric properties
    define the physical characteristics of the spiral structure itself.
    """
    return {
        # Mathematical model parameters
        "pitch": 1.0,  # Controls the vertical pitch of the spiral
        "turnsPerLogUnit": 1.0,  # Controls the tightness of the spiral
        "initialRadius": 1.0,  # The radius of the spiral at t=1
        
        # Geometric properties
        "wallHeight": 1.0,  # Constant at 1 unit
        "wallThickness": 1.0,  # Constant at 1 unit, but can be variable
        "intraluminalDiameter": 1.0,  # Variable, defined by initialRadius
        "totalDiameter": 3.0,  # 2*Wall Thickness + Intraluminal Diameter
        
        # Default visualization parameters
        "defaultStartTime": 1.0,
        "defaultEndTime": 100.0,
        "defaultStep": 0.1
    }

@router.post("/spiral/parameters")
def update_spiral_parameters(
    parameters: SpiralParametersResponse
) -> Dict[str, str]:
    """Updates the spiral parameters.
    
    This endpoint allows customization of the Hardcard Hyperspace mathematical model by updating the core parameters
    that define the logarithmic spiral. The parameters control the shape, scale, and behavior of the spiral representation.
    
    The parameters are:
    - pitch: Controls the vertical pitch of the spiral (z-axis scaling)
    - turnsPerLogUnit: Controls the tightness of the spiral (number of turns per logarithmic unit)
    - initialRadius: The radius of the spiral at t=1 (the Eye of the Storm)
    
    Changes to these parameters affect how time is visualized in the Hyperspace representation,
    allowing for different perspectives on temporal relationships and data visualization.
    """
    # In a real implementation, this would store the parameters in a database
    # For the MVP, we're returning success as parameters are managed client-side
    # Future implementation will store these in a user settings profile
    return {"status": "success", "message": "Parameters updated successfully"}