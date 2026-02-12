"""PowerChat API Documentation

PowerChat is a context-aware AI assistant overlay system that provides real-time suggestions based 
on various data sources including clipboard content and API data.

Features:
- Real-time context monitoring (clipboard, API data)
- Context-aware suggestions
- Websocket-based real-time communication
- Transparent overlay UI
- Confidence-based transparency

API Endpoints:
- GET /powerchat/health - Check if the PowerChat API is running
- POST /powerchat/context/{client_id} - Update context for a specific client
- GET /powerchat/context/{client_id} - Get context for a specific client
- GET /powerchat/suggestions/{client_id} - Get suggestions for a specific client
- WebSocket /powerchat/ws/{client_id} - WebSocket endpoint for real-time communication
"""

from fastapi import APIRouter

router = APIRouter()

def get_documentation():
    """Return documentation string for PowerChat API"""
    return __doc__

@router.get("/readme-documentation")
def get_api_documentation():
    """Get PowerChat API documentation"""
    return {"documentation": get_documentation()}

@router.get("/readme/health")
def check_health_readme():
    """Check if the readme API is running"""
    return {"status": "ok", "message": "Readme API is operational"}
