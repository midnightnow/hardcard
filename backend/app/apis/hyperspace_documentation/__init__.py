from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

# Create router
router = APIRouter(prefix="/hyperspace-documentation")

"""
Hardcard Hyperspace Documentation API
----------------------------------

Comprehensive documentation for the Hardcard Hyperspace visualization, including
the mathematical model, usage guides, and API references.

This API provides detailed information about:
- The logarithmic spiral time model used in Hardcard
- How Bitcoin investments are mapped to the hyperspace
- Mathematical foundations and formulas
- Visualization and interaction guidelines
- Complete API endpoint documentation
"""

class MathematicalModel(BaseModel):
    title: str
    description: str
    spiral_equation: str
    time_mapping: str
    timestamp_algebra: str
    hyperspace_coordinates: Dict[str, str]
    parameters: Dict[str, str]
    invariants: Dict[str, str]
    unit_of_one: str

class VisualizationTip(BaseModel):
    title: str
    description: str

class ApiEndpointParam(BaseModel):
    name: str
    type: str
    description: str
    default: Optional[str] = None
    required: bool = False

class ApiEndpointResponse(BaseModel):
    status: int
    description: str
    schema_definition: Optional[str] = None

class ApiEndpoint(BaseModel):
    endpoint: str
    method: str
    description: str
    parameters: List[ApiEndpointParam] = []
    responses: List[ApiEndpointResponse] = []
    example_request: Optional[str] = None
    example_response: Optional[str] = None

class ApiUsage(BaseModel):
    title: str
    description: str
    get_spiral_parameters: ApiEndpoint
    update_spiral_parameters: ApiEndpoint
    get_spiral_coordinates: ApiEndpoint
    get_spiral_range: ApiEndpoint
    get_hyperspace_data_points: ApiEndpoint
    get_hyperspace_relationships: ApiEndpoint
    get_bitcoin_investments: ApiEndpoint
    get_bitcoin_hyperspace_data: ApiEndpoint

class HyperspaceDocumentation(BaseModel):
    title: str
    version: str
    description: str
    mathematical_model: MathematicalModel
    visualization_tips: List[VisualizationTip]
    usage: ApiUsage
    getting_started: str
    faq: Dict[str, str]

# Hardcard Hyperspace comprehensive documentation
HYPERSPACE_DOCUMENTATION = {
    "title": "Hardcard Hyperspace Documentation",
    "version": "1.0.0",
    "description": "Comprehensive documentation for the Hardcard Hyperspace visualization system",
    "mathematical_model": {
        "title": "Logarithmic Spiral Time Model",
        "description": "The Hardcard Hyperspace is based on a logarithmic spiral that maps time to spatial coordinates. This model provides an intuitive visualization of exponential growth over time, making it ideal for tracking Bitcoin investments and generational wealth.",
        "spiral_equation": "r(θ) = e^{θ} with r(0)=1",
        "time_mapping": "Time is mapped logarithmically, with t=1 representing the origin point ('Eye of the Storm')",
        "timestamp_algebra": "τₙ = t₀ + n·Δt, Δt = 1 year = 31 536 000 s",
        "hyperspace_coordinates": {
            "x": "x = r × cos(θ) = radius × cos(turns_per_log_unit × ln(time))",
            "y": "y = r × sin(θ) = radius × sin(turns_per_log_unit × ln(time))",
            "z": "z = pitch × ln(time)",
            "radius": "radius = initial_radius + z",
            "theta": "θ = turns_per_log_unit × ln(time)"
        },
        "parameters": {
            "turns_per_log_unit": "Controls the tightness of the spiral (how many turns per logarithmic unit)",
            "pitch": "Controls the vertical rise of the spiral (z-axis scaling)",
            "initial_radius": "The radius of the spiral at t=1 (the 'Eye of the Storm')"
        },
        "invariants": {
            "eye_of_storm": "The point at t=1 is the invariant reference point of the system",
            "logarithmic_spacing": "Equal multiplicative increases in time map to equal angular distances",
            "growth_visibility": "Exponential growth becomes visually apparent through the spiral's expansion"
        },
        "unit_of_one": "All quantities in the Hardcard system are traceable to a single invariant ≈ 1 (the 'unit-of-one' that anchors every quantity—BTC, time, proofs, entropy)."
    },
    "visualization_tips": [
        {
            "title": "Navigation",
            "description": "Use mouse/touch to rotate the view, scroll to zoom, and right-click/two-finger drag to pan."
        },
        {
            "title": "Time Markers",
            "description": "The spiral includes markers at logarithmically spaced time intervals to provide temporal context."
        },
        {
            "title": "Bitcoin Investments",
            "description": "Bitcoin investments appear as colored spheres on the spiral, positioned according to their timestamp."
        },
        {
            "title": "Color Coding",
            "description": "Green indicates positive growth, red indicates negative growth, with intensity reflecting magnitude."
        },
        {
            "title": "Size Scaling",
            "description": "The size of each Bitcoin investment sphere is proportional to the amount of Bitcoin."
        },
        {
            "title": "Eye of the Storm",
            "description": "The t=1 point (representing the Bitcoin genesis block time) is marked as the 'Eye of the Storm'."
        },
        {
            "title": "Performance Optimization",
            "description": "The visualization automatically adjusts quality during interaction to maintain smooth performance."
        }
    ],
    "usage": {
        "title": "API Reference",
        "description": "Comprehensive documentation for the Hardcard Hyperspace API endpoints",
        "get_spiral_parameters": {
            "endpoint": "/spiral-hyperspace/spiral-parameters",
            "method": "GET",
            "description": "Retrieve the current spiral parameters including pitch, turns per log unit, and initial radius",
            "parameters": [],
            "responses": [
                {
                    "status": 200,
                    "description": "Successful response with spiral parameters",
                    "schema_definition": "{pitch: number, turns_per_log_unit: number, initial_radius: number, default_start_time: number, default_end_time: number, wall_thickness: number}"
                }
            ],
            "example_response": "{\"pitch\": 1.0, \"turns_per_log_unit\": 1.0, \"initial_radius\": 1.0, \"default_start_time\": 1, \"default_end_time\": 100, \"wall_thickness\": 1.0}"
        },
        "update_spiral_parameters": {
            "endpoint": "/spiral-hyperspace/spiral-parameters",
            "method": "POST",
            "description": "Update the spiral parameters",
            "parameters": [
                {
                    "name": "pitch",
                    "type": "number",
                    "description": "Controls the vertical pitch of the spiral",
                    "default": "1.0",
                    "required": True
                },
                {
                    "name": "turns_per_log_unit",
                    "type": "number",
                    "description": "Controls the tightness of the spiral",
                    "default": "1.0",
                    "required": True
                },
                {
                    "name": "initial_radius",
                    "type": "number",
                    "description": "The radius of the spiral at t=1",
                    "default": "1.0",
                    "required": True
                }
            ],
            "responses": [
                {
                    "status": 200,
                    "description": "Parameters updated successfully",
                    "schema_definition": "{success: boolean, message: string}"
                }
            ],
            "example_request": "{\"pitch\": 1.0, \"turns_per_log_unit\": 1.0, \"initial_radius\": 1.0, \"wall_thickness\": 1.0, \"default_start_time\": 1, \"default_end_time\": 100}"
        },
        "get_spiral_coordinates": {
            "endpoint": "/spiral-hyperspace/spiral-coordinates",
            "method": "GET",
            "description": "Calculate coordinates on the hyperspace spiral for a given time value",
            "parameters": [
                {
                    "name": "time",
                    "type": "number",
                    "description": "The time value to calculate coordinates for",
                    "required": True
                },
                {
                    "name": "turns_per_log_unit",
                    "type": "number",
                    "description": "Controls the tightness of the spiral",
                    "default": "1.0",
                    "required": False
                },
                {
                    "name": "pitch",
                    "type": "number",
                    "description": "Controls the vertical pitch of the spiral",
                    "default": "1.0",
                    "required": False
                },
                {
                    "name": "initial_radius",
                    "type": "number",
                    "description": "The radius of the spiral at t=1",
                    "default": "1.0",
                    "required": False
                }
            ],
            "responses": [
                {
                    "status": 200,
                    "description": "Coordinates for the given time value",
                    "schema_definition": "{x: number, y: number, z: number, radius: number, theta: number, time: number}"
                }
            ],
            "example_response": "{\"x\": 1.0, \"y\": 0.0, \"z\": 0.0, \"radius\": 1.0, \"theta\": 0.0, \"time\": 1.0}"
        },
        "get_spiral_range": {
            "endpoint": "/spiral-hyperspace/spiral-range",
            "method": "GET",
            "description": "Calculate a range of points along the hyperspace spiral",
            "parameters": [
                {
                    "name": "start_time",
                    "type": "number",
                    "description": "The starting time value",
                    "default": "1.0",
                    "required": False
                },
                {
                    "name": "end_time",
                    "type": "number",
                    "description": "The ending time value",
                    "default": "100.0",
                    "required": False
                },
                {
                    "name": "step",
                    "type": "number",
                    "description": "The time step between points",
                    "default": "0.1",
                    "required": False
                },
                {
                    "name": "turns_per_log_unit",
                    "type": "number",
                    "description": "Controls the tightness of the spiral",
                    "default": "1.0",
                    "required": False
                },
                {
                    "name": "pitch",
                    "type": "number",
                    "description": "Controls the vertical pitch of the spiral",
                    "default": "1.0",
                    "required": False
                },
                {
                    "name": "initial_radius",
                    "type": "number",
                    "description": "The radius of the spiral at t=1",
                    "default": "1.0",
                    "required": False
                }
            ],
            "responses": [
                {
                    "status": 200,
                    "description": "Array of coordinates along the spiral",
                    "schema_definition": "[{x: number, y: number, z: number, t: number}, ...]"
                }
            ]
        },
        "get_hyperspace_data_points": {
            "endpoint": "/spiral-hyperspace/data-points",
            "method": "GET",
            "description": "Retrieve data points to be displayed in the hyperspace visualization",
            "parameters": [],
            "responses": [
                {
                    "status": 200,
                    "description": "Array of data points with their properties",
                    "schema_definition": "[{id: string, time: number, label: string, color: string, size: number}, ...]"
                }
            ]
        },
        "get_hyperspace_relationships": {
            "endpoint": "/spiral-hyperspace/relationships",
            "method": "GET",
            "description": "Retrieve relationships between data points in the hyperspace",
            "parameters": [],
            "responses": [
                {
                    "status": 200,
                    "description": "Array of relationships between data points",
                    "schema_definition": "[{source: string, target: string, label: string, color: string}, ...]"
                }
            ]
        },
        "get_bitcoin_investments": {
            "endpoint": "/hyperspace-bitcoin/investments",
            "method": "GET",
            "description": "Retrieve all Bitcoin investments",
            "parameters": [],
            "responses": [
                {
                    "status": 200,
                    "description": "Array of Bitcoin investments",
                    "schema_definition": "[{id: string, date: string, amount_usd: number, btc_price_usd: number, btc_amount: number, current_value_usd: number, growth_factor: number, label: string}, ...]"
                }
            ]
        },
        "get_bitcoin_hyperspace_data": {
            "endpoint": "/hyperspace-bitcoin/hyperspace-data",
            "method": "GET",
            "description": "Retrieve Bitcoin investments with hyperspace coordinates",
            "parameters": [
                {
                    "name": "pitch",
                    "type": "number",
                    "description": "Controls the vertical pitch of the spiral",
                    "default": "1.0",
                    "required": False
                },
                {
                    "name": "turns_per_log_unit",
                    "type": "number",
                    "description": "Controls the tightness of the spiral",
                    "default": "1.0",
                    "required": False
                },
                {
                    "name": "initial_radius",
                    "type": "number",
                    "description": "The radius of the spiral at t=1",
                    "default": "1.0",
                    "required": False
                }
            ],
            "responses": [
                {
                    "status": 200,
                    "description": "Array of Bitcoin investments with hyperspace coordinates",
                    "schema_definition": "[{investment: object, coordinates: object, time_value: number, visual_size: number, visual_color: string}, ...]"
                }
            ]
        }
    },
    "getting_started": """
## Getting Started with Hardcard Hyperspace

### Introduction
The Hardcard Hyperspace visualization is a 3D representation of the logarithmic time spiral that forms the mathematical foundation of Hardcard's Bitcoin legacy planning system.

### Understanding the visualization
1. **The Spiral**: The central logarithmic spiral represents time, with each point on the spiral mapping to a specific time value. The spiral expands outward as time increases, visually representing exponential growth.

2. **Time Markers**: Blue spheres along the spiral indicate specific time points, providing context for navigation.

3. **The Eye of the Storm**: The starting point of the spiral (t=1) is marked as the "Eye of the Storm", representing the origin point of the system.

4. **Bitcoin Investments**: Colored spheres positioned on the spiral represent Bitcoin investments. The size of each sphere is proportional to the amount of Bitcoin, while the color indicates growth (green) or loss (red).

5. **Adjustable Parameters**: You can adjust the mathematical parameters of the spiral to explore different visualizations of the same data.

### Interactive Controls
- **Rotate**: Click and drag to rotate the 3D view
- **Zoom**: Scroll to zoom in and out
- **Pan**: Right-click and drag to pan the view
- **Select**: Click on a Bitcoin investment to see detailed information

### Visualizing Bitcoin Growth
The Hardcard Hyperspace allows you to visualize the growth of Bitcoin investments over time. By mapping investments to their positions on the logarithmic spiral, you can see how early investments grow exponentially compared to later ones.

### Adjusting Parameters
You can customize the visualization by adjusting the following parameters:
- **Pitch**: Controls the vertical rise of the spiral
- **Turns Per Log Unit**: Controls how tightly the spiral is wound
- **Initial Radius**: Sets the starting radius at t=1

Experiment with these parameters to find the visualization that best helps you understand your Bitcoin legacy investments.
""",
    "faq": {
        "What is the Hardcard Hyperspace?": "The Hardcard Hyperspace is a 3D visualization of a logarithmic spiral that maps time to spatial coordinates, allowing for intuitive visualization of Bitcoin investments and their growth over time.",
        "What does the spiral represent?": "The spiral represents time, with each point on the spiral corresponding to a specific time value. The spiral expands exponentially, visually representing the potential for exponential growth of investments over time.",
        "How are Bitcoin investments displayed?": "Bitcoin investments appear as colored spheres positioned on the spiral according to their timestamp. The size of each sphere represents the amount of Bitcoin, while the color indicates the growth/loss.",
        "What are the key parameters?": "The key parameters are pitch (vertical scaling), turns per log unit (spiral tightness), and initial radius (starting radius at t=1). Adjusting these parameters changes the visual representation of the spiral.",
        "How is time mapped in the Hyperspace?": "Time is mapped logarithmically, with t=1 representing the origin point ('Eye of the Storm'). Equal multiplicative increases in time correspond to equal angular distances on the spiral.",
        "What is the 'Eye of the Storm'?": "The 'Eye of the Storm' is the point on the spiral where t=1, representing the baseline reference point of the system (analogous to the Bitcoin genesis block time).",
        "How do I interact with the visualization?": "You can rotate the view by clicking and dragging, zoom by scrolling, and pan by right-clicking and dragging. Clicking on a Bitcoin investment shows detailed information about that investment.",
        "Why is the spiral logarithmic?": "A logarithmic spiral is used because it naturally represents exponential growth, which aligns with the potential growth pattern of Bitcoin investments over time. Equal angular distances represent equal multiplicative increases in value.",
        "How do I read the visualization?": "The angular position on the spiral represents the time of the investment, while the distance from the center represents the logarithm of that time. Green points represent investments with positive returns, red points represent investments with negative returns.",
        "Can I add my own Bitcoin investments?": "Yes, you can add your own Bitcoin investments through the API, and they will automatically be positioned on the spiral according to their timestamp."
    }
}

@router.get("/", operation_id="get_hyperspace_documentation")
def get_hyperspace_documentation() -> Dict[str, Any]:
    """Get comprehensive documentation for the Hardcard Hyperspace
    
    This endpoint provides detailed documentation for the Hardcard Hyperspace visualization,
    including the mathematical model, usage guides, and API references.
    
    The documentation covers:
    - The logarithmic spiral time model
    - How Bitcoin investments are mapped to the hyperspace
    - Mathematical foundations and formulas
    - Visualization and interaction guidelines
    - Complete API endpoint documentation
    
    Returns:
        A comprehensive documentation object
    """
    return HYPERSPACE_DOCUMENTATION

@router.get("/mathematical-model", operation_id="get_mathematical_model")
def get_mathematical_model() -> Dict[str, Any]:
    """Get detailed documentation about the mathematical model
    
    This endpoint provides in-depth information about the mathematical foundations
    of the Hardcard Hyperspace, including the logarithmic spiral time model, formulas,
    and key parameters.
    
    Returns:
        Mathematical model documentation
    """
    return HYPERSPACE_DOCUMENTATION["mathematical_model"]

@router.get("/api-reference", operation_id="get_api_reference")
def get_api_reference() -> Dict[str, Any]:
    """Get API reference documentation
    
    This endpoint provides comprehensive documentation for all API endpoints
    related to the Hardcard Hyperspace, including parameters, responses,
    and example usage.
    
    Returns:
        API reference documentation
    """
    return HYPERSPACE_DOCUMENTATION["usage"]

@router.get("/user-guide", operation_id="get_user_guide")
def get_user_guide() -> Dict[str, str]:
    """Get user guide for the Hardcard Hyperspace
    
    This endpoint provides a user guide for the Hardcard Hyperspace visualization,
    including getting started information and frequently asked questions.
    
    Returns:
        User guide documentation
    """
    return {
        "getting_started": HYPERSPACE_DOCUMENTATION["getting_started"],
        "faq": HYPERSPACE_DOCUMENTATION["faq"]
    }
