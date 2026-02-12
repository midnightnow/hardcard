
from fastapi import APIRouter, HTTPException
import json
from pathlib import Path
from typing import List, Dict, Any

router = APIRouter()

# Define the path to the system status file
# This assumes the script is run from the 'backend' directory's parent.
# A more robust solution would use environment variables or a config file.
STATUS_FILE = Path("./system-status.json")

# Placeholder for agent icons
AGENT_ICONS = {
    "Code Quality Agent": "🔬",
    "Code Fixing Agent": "🔧",
    "Strategic Alignment Agent": "🎯",
    "Performance Optimization Agent": "⚡️",
    "Learning Agent": "🧠",
    "Deployment Readiness Agent": "🚀",
    "Frontend Specialist": "🎨",
    "Backend Specialist": "⚙️",
    "Testing Specialist": "🧪",
    "Security Specialist": "🛡️",
    "Documentation Specialist": "📚",
    "default": "🤖"
}

@router.get("/api/shipyard/agents/status", response_model=List[Dict[str, Any]])
async def get_agents_status():
    """
    Provides the real-time status of all registered AI agents.
    """
    if not STATUS_FILE.is_file():
        raise HTTPException(status_code=404, detail="System status file not found.")

    try:
        with open(STATUS_FILE, "r") as f:
            status_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise HTTPException(status_code=500, detail=f"Error reading system status: {e}")

    agents_status = []
    agent_workload = status_data.get("agent_workload", {})

    for agent_id, workload in agent_workload.items():
        # Extracting more detailed status if available, otherwise providing defaults
        agent_details = status_data.get("agents", {}).get(agent_id, {})
        
        agents_status.append({
            "id": agent_id,
            "name": agent_id.replace("_", " ").title(),
            "icon": AGENT_ICONS.get(agent_id.replace("_", " ").title(), AGENT_ICONS["default"]),
            "status": agent_details.get("status", "idle"),
            "current_task": agent_details.get("current_task", "No active task"),
            "cpu_usage": agent_details.get("cpu_usage", 0),
            "memory_usage": agent_details.get("memory_usage", 0),
            "tasks_completed": workload.get("completed", 0),
            "tasks_pending": workload.get("pending", 0),
        })

    return agents_status

@router.post("/api/shipyard/agents/{agent_id}/control")
async def control_agent_action(agent_id: str, action: Dict[str, str]):
    """
    Placeholder for controlling an agent (e.g., pause, stop).
    In a real implementation, this would trigger a command to the agent process.
    """
    valid_actions = ["pause", "stop", "logs"]
    action_to_perform = action.get("action")

    if not action_to_perform or action_to_perform not in valid_actions:
        raise HTTPException(status_code=400, detail="Invalid action specified.")

    # Here you would implement the logic to send a signal or command
    # to the specified agent process.
    # For this demo, we'll just return a success message.
    
    print(f"Received action '{action_to_perform}' for agent '{agent_id}'")

    return {"message": f"Action '{action_to_perform}' sent to agent '{agent_id}' successfully."}

# You would need to include this router in your main FastAPI app
# Example in your main app file:
# from .apis import shipyard_api
# app.include_router(shipyard_api.router)
