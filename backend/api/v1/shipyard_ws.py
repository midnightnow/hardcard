from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Set
import asyncio
import json
import uuid
from datetime import datetime
import random
import hashlib

from ...services.code_analyzer import CodeAnalyzer

router = APIRouter()

# Initialize code analyzer
code_analyzer = CodeAnalyzer()

class AnalyzeRepoRequest(BaseModel):
    repo_path: str
    ship_name: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ships: Dict[str, Ship] = {}  # In-memory ship storage
        self.events: List[Dict] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        await websocket.send_json(message)
        
    def add_event(self, ship_id: str, event_type: str, message: str, severity: str = "info"):
        """Add event to history and broadcast"""
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "shipId": ship_id,
            "type": event_type,
            "message": message,
            "severity": severity
        }
        self.events.append(event)
        # Keep only last 1000 events
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
        return event

manager = ConnectionManager()

# Initialize with some demo ships
def create_demo_ships():
    """Create some demo ships for visualization"""
    ships = []
    
    # VetSorcery - The flagship
    ships.append({
        "id": "ship-vetsorcery",
        "name": "VetSorcery Flagship",
        "class": "galleon",
        "stage": "rigging",
        "health": "pristine",
        "progress": 75,
        "hullColor": "#2C3E50",
        "sailColor": "#3498DB",
        "flagDesign": "VS",
        "size": "large",
        "blueprint": {
            "architect": "Shipyard AI",
            "createdAt": datetime.now().isoformat(),
            "framework": "React",
            "database": "Firebase",
            "features": ["AI Phone Agents", "CRM Integration", "Real-time Analytics"]
        },
        "components": [
            {"id": "c1", "name": "Phone Agent Core", "type": "hull", "status": "complete", "progress": 100, "agents": ["backend-1", "backend-2"]},
            {"id": "c2", "name": "Voice Processing", "type": "sail", "status": "building", "progress": 85, "agents": ["ai-1", "ai-2"]},
            {"id": "c3", "name": "CRM Integration", "type": "mast", "status": "building", "progress": 70, "agents": ["frontend-1"]},
            {"id": "c4", "name": "Analytics Dashboard", "type": "deck", "status": "planned", "progress": 30, "agents": []}
        ],
        "crew": [
            {"id": "crew1", "name": "Captain Claude", "role": "captain", "agentType": "backend", "status": "working", "currentTask": "Coordinating voice integration", "efficiency": 95, "tasksCompleted": 142},
            {"id": "crew2", "name": "Navigator Nova", "role": "navigator", "agentType": "frontend", "status": "working", "currentTask": "Building UI components", "efficiency": 88, "tasksCompleted": 89},
            {"id": "crew3", "name": "Engineer Echo", "role": "engineer", "agentType": "testing", "status": "idle", "efficiency": 92, "tasksCompleted": 156}
        ],
        "cargo": {"features": 24, "bugs": 3, "techDebt": 12},
        "metrics": {
            "linesOfCode": 45892,
            "filesCreated": 287,
            "testsWritten": 156,
            "testsPassing": 148,
            "coveragePercent": 87,
            "buildTime": 145,
            "deployTime": 89,
            "errors": 3,
            "warnings": 12
        },
        "destination": {"port": "production", "eta": None, "route": ["design", "build", "test", "deploy"]},
        "armament": {"security": 92, "performance": 85, "scalability": 78}
    })
    
    # HardCard Platform
    ships.append({
        "id": "ship-hardcard",
        "name": "HardCard Armada",
        "class": "carrier",
        "stage": "sailing",
        "health": "seaworthy",
        "progress": 100,
        "hullColor": "#8B4513",
        "sailColor": "#FFD700",
        "flagDesign": "HC",
        "size": "massive",
        "blueprint": {
            "architect": "Shipyard AI",
            "createdAt": datetime.now().isoformat(),
            "framework": "React",
            "database": "Firebase",
            "features": ["Domain Portfolio", "Payment Processing", "Multi-tenant"]
        },
        "components": [
            {"id": "hc1", "name": "Domain Management", "type": "hull", "status": "complete", "progress": 100, "agents": ["backend-3"]},
            {"id": "hc2", "name": "Payment Gateway", "type": "cargo", "status": "complete", "progress": 100, "agents": ["backend-4"]},
            {"id": "hc3", "name": "Admin Dashboard", "type": "cabin", "status": "complete", "progress": 100, "agents": ["frontend-2"]}
        ],
        "crew": [
            {"id": "hcrew1", "name": "Admiral Azure", "role": "captain", "agentType": "devops", "status": "working", "currentTask": "Monitoring deployments", "efficiency": 98, "tasksCompleted": 423}
        ],
        "cargo": {"features": 72, "bugs": 5, "techDebt": 28},
        "metrics": {
            "linesOfCode": 125000,
            "filesCreated": 892,
            "testsWritten": 456,
            "testsPassing": 445,
            "coveragePercent": 91,
            "buildTime": 240,
            "deployTime": 120,
            "errors": 5,
            "warnings": 23
        },
        "destination": {"port": "production", "eta": None, "route": ["deployed"]},
        "armament": {"security": 95, "performance": 90, "scalability": 88}
    })
    
    # New AI Dashboard project
    ships.append({
        "id": "ship-ai-dash",
        "name": "AI Control Center",
        "class": "frigate",
        "stage": "framework",
        "health": "pristine",
        "progress": 35,
        "hullColor": "#1E3A8A",
        "sailColor": "#60A5FA",
        "flagDesign": "AI",
        "size": "medium",
        "blueprint": {
            "architect": "Shipyard AI",
            "createdAt": datetime.now().isoformat(),
            "framework": "React",
            "database": "Supabase",
            "features": ["Real-time Monitoring", "Agent Control", "Analytics"]
        },
        "components": [
            {"id": "ai1", "name": "Database Schema", "type": "hull", "status": "complete", "progress": 100, "agents": ["backend-5"]},
            {"id": "ai2", "name": "API Layer", "type": "framework", "status": "building", "progress": 60, "agents": ["backend-6", "backend-7"]},
            {"id": "ai3", "name": "UI Components", "type": "sail", "status": "planned", "progress": 10, "agents": []}
        ],
        "crew": [
            {"id": "aicrew1", "name": "Builder Bot", "role": "engineer", "agentType": "backend", "status": "working", "currentTask": "Creating API endpoints", "efficiency": 85, "tasksCompleted": 34}
        ],
        "cargo": {"features": 8, "bugs": 1, "techDebt": 2},
        "metrics": {
            "linesOfCode": 8234,
            "filesCreated": 45,
            "testsWritten": 28,
            "testsPassing": 27,
            "coveragePercent": 72,
            "buildTime": 45,
            "deployTime": 0,
            "errors": 1,
            "warnings": 4
        },
        "destination": {"port": "staging", "eta": datetime(2024, 2, 15).isoformat(), "route": ["design", "build", "test", "deploy"]},
        "armament": {"security": 70, "performance": 65, "scalability": 60}
    })
    
    return ships

# Initialize demo ships
demo_ships = create_demo_ships()
for ship in demo_ships:
    manager.ships[ship["id"]] = ship

@router.websocket("/ws/shipyard-stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        # Send initial fleet status
        fleet_data = {
            "type": "fleet_update",
            "fleet": {
                "ships": list(manager.ships.values()),
                "admiral": {
                    "name": "Claude Navigator",
                    "experience": 100,
                    "victories": 42
                },
                "homePort": "production-harbor",
                "totalCrew": 112,
                "supplies": {
                    "cpu": 85,
                    "memory": 72,
                    "storage": 68
                }
            }
        }
        await manager.send_personal_message(fleet_data, websocket)
        
        # Send current conditions
        conditions_data = {
            "type": "conditions_update",
            "windConditions": {
                "favorable": True,
                "speed": 1.2,
                "direction": "tailwind",
                "forecast": "Strong winds favor rapid development"
            },
            "seaState": {
                "calm": True,
                "waves": "choppy",
                "visibility": "clear",
                "threats": []
            }
        }
        await manager.send_personal_message(conditions_data, websocket)
        
        # Start background tasks
        metric_task = asyncio.create_task(stream_metrics(websocket))
        event_task = asyncio.create_task(generate_events())
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "get_fleet_status":
                await manager.send_personal_message(fleet_data, websocket)
                
            elif message["type"] == "create_ship":
                ship = message["ship"]
                ship["id"] = f"ship-{uuid.uuid4().hex[:8]}"
                manager.ships[ship["id"]] = ship
                
                # Add creation event
                event = manager.add_event(
                    ship["id"],
                    "ship_created",
                    f"New {ship['class']} '{ship['name']}' launched from shipyard",
                    "success"
                )
                
                # Broadcast ship creation
                await manager.broadcast({
                    "type": "ship_update",
                    "ship": ship
                })
                await manager.broadcast({
                    "type": "event",
                    "event": event
                })
                
            elif message["type"] == "update_ship_stage":
                ship_id = message["shipId"]
                new_stage = message["stage"]
                
                if ship_id in manager.ships:
                    manager.ships[ship_id]["stage"] = new_stage
                    manager.ships[ship_id]["progress"] = get_stage_progress(new_stage)
                    
                    event = manager.add_event(
                        ship_id,
                        "stage_change",
                        f"Ship advanced to {new_stage} stage",
                        "info"
                    )
                    
                    await manager.broadcast({
                        "type": "ship_update",
                        "ship": manager.ships[ship_id]
                    })
                    await manager.broadcast({
                        "type": "event",
                        "event": event
                    })
                    
            elif message["type"] == "assign_crew":
                ship_id = message["shipId"]
                crew = message["crew"]
                
                if ship_id in manager.ships:
                    manager.ships[ship_id]["crew"].extend(crew)
                    
                    event = manager.add_event(
                        ship_id,
                        "crew_assigned",
                        f"{len(crew)} crew members assigned to ship",
                        "info"
                    )
                    
                    await manager.broadcast({
                        "type": "ship_update",
                        "ship": manager.ships[ship_id]
                    })
                    await manager.broadcast({
                        "type": "event",
                        "event": event
                    })
                    
            elif message["type"] == "launch_ship":
                ship_id = message["shipId"]
                
                if ship_id in manager.ships:
                    manager.ships[ship_id]["stage"] = "launching"
                    manager.ships[ship_id]["progress"] = 95
                    
                    event = manager.add_event(
                        ship_id,
                        "ship_launching",
                        f"{manager.ships[ship_id]['name']} is launching!",
                        "success"
                    )
                    
                    await manager.broadcast({
                        "type": "ship_update",
                        "ship": manager.ships[ship_id]
                    })
                    await manager.broadcast({
                        "type": "event",
                        "event": event
                    })
                    
                    # Simulate launch completion after 5 seconds
                    asyncio.create_task(complete_launch(ship_id))
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        metric_task.cancel()
        event_task.cancel()

async def stream_metrics(websocket: WebSocket):
    """Stream real-time metrics updates"""
    while True:
        try:
            # Update metrics for all ships
            for ship_id, ship in manager.ships.items():
                if ship["stage"] not in ["sailing", "blueprint"]:
                    # Simulate progress
                    ship["progress"] = min(100, ship["progress"] + random.uniform(0.1, 0.5))
                    
                    # Update metrics
                    ship["metrics"]["linesOfCode"] += random.randint(10, 100)
                    ship["metrics"]["filesCreated"] += random.randint(0, 2)
                    
                    if random.random() > 0.7:
                        ship["metrics"]["testsWritten"] += 1
                        ship["metrics"]["testsPassing"] = min(
                            ship["metrics"]["testsWritten"],
                            ship["metrics"]["testsPassing"] + random.randint(0, 1)
                        )
                    
                    # Update crew status
                    for crew in ship["crew"]:
                        if crew["status"] == "idle" and random.random() > 0.8:
                            crew["status"] = "working"
                            crew["currentTask"] = random.choice([
                                "Writing code",
                                "Running tests",
                                "Reviewing PRs",
                                "Fixing bugs",
                                "Optimizing performance"
                            ])
                        elif crew["status"] == "working" and random.random() > 0.9:
                            crew["status"] = "idle"
                            crew["currentTask"] = None
                            crew["tasksCompleted"] += 1
                    
                    # Broadcast update
                    await manager.broadcast({
                        "type": "ship_update",
                        "ship": ship
                    })
            
            await asyncio.sleep(2)  # Update every 2 seconds
            
        except Exception as e:
            print(f"Error in metrics stream: {e}")
            break

async def generate_events():
    """Generate random events for ships"""
    event_templates = [
        ("component_complete", "{component} construction complete", "success"),
        ("crew_assigned", "New crew member joined the ship", "info"),
        ("warning", "Supply shortage detected", "warning"),
        ("milestone", "Reached {progress}% completion", "success"),
        ("error", "Build error in {component}", "error")
    ]
    
    while True:
        try:
            await asyncio.sleep(random.uniform(5, 15))  # Random interval
            
            # Pick a random ship that's being built
            active_ships = [s for s in manager.ships.values() 
                          if s["stage"] not in ["sailing", "blueprint"]]
            
            if active_ships:
                ship = random.choice(active_ships)
                event_type, message_template, severity = random.choice(event_templates)
                
                # Customize message
                message = message_template.format(
                    component=random.choice(["Navigation System", "Cargo Hold", "Engine Room", "Command Bridge"]),
                    progress=int(ship["progress"])
                )
                
                event = manager.add_event(ship["id"], event_type, message, severity)
                
                await manager.broadcast({
                    "type": "event",
                    "event": event
                })
                
        except Exception as e:
            print(f"Error generating events: {e}")
            break

async def complete_launch(ship_id: str):
    """Complete ship launch after delay"""
    await asyncio.sleep(5)
    
    if ship_id in manager.ships:
        manager.ships[ship_id]["stage"] = "sailing"
        manager.ships[ship_id]["progress"] = 100
        manager.ships[ship_id]["destination"]["port"] = "production"
        
        event = manager.add_event(
            ship_id,
            "ship_deployed",
            f"{manager.ships[ship_id]['name']} successfully deployed to production!",
            "success"
        )
        
        await manager.broadcast({
            "type": "ship_update",
            "ship": manager.ships[ship_id]
        })
        await manager.broadcast({
            "type": "event",
            "event": event
        })

def get_stage_progress(stage: str) -> int:
    """Get default progress for a stage"""
    progress_map = {
        "blueprint": 5,
        "drydock": 15,
        "hull": 25,
        "framework": 40,
        "outfitting": 55,
        "rigging": 70,
        "testing": 85,
        "launching": 95,
        "sailing": 100,
        "maintenance": 100
    }
    return progress_map.get(stage, 0)

@router.post("/api/v1/shipyard/analyze-repo")
async def analyze_repository(request: AnalyzeRepoRequest):
    """
    Analyze a code repository and transform it into a ship
    """
    try:
        # Analyze the repository
        analysis = code_analyzer.analyze_repository(request.repo_path)
        
        # Create ship object from analysis
        ship = {
            "id": f"ship-{uuid.uuid4().hex[:8]}",
            "name": request.ship_name,
            "class": analysis["class"],
            "stage": analysis["stage"],
            "health": analysis["health"],
            "progress": analysis["progress"],
            "hullColor": "#" + hashlib.md5(request.ship_name.encode()).hexdigest()[:6],
            "sailColor": "#FFFFFF",
            "flagDesign": request.ship_name[:2].upper(),
            "size": {
                "dinghy": "small",
                "sloop": "small",
                "frigate": "medium",
                "galleon": "large",
                "carrier": "massive",
                "armada": "massive"
            }.get(analysis["class"], "medium"),
            "blueprint": analysis["blueprint"],
            "components": analysis["components"],
            "crew": analysis["crew"],
            "cargo": analysis["cargo"],
            "metrics": analysis["metrics"],
            "destination": {
                "port": "production",
                "eta": None,
                "route": ["design", "build", "test", "deploy"]
            },
            "armament": analysis["armament"]
        }
        
        # Store the ship
        manager.ships[ship["id"]] = ship
        
        # Create event
        event = manager.add_event(
            ship["id"],
            "ship_analyzed",
            f"Repository '{request.ship_name}' analyzed and transformed into {ship['class']}",
            "success"
        )
        
        # Broadcast to all connected clients
        await manager.broadcast({
            "type": "ship_update",
            "ship": ship
        })
        await manager.broadcast({
            "type": "event",
            "event": event
        })
        
        return {
            "success": True,
            "ship": ship,
            "message": f"Repository analyzed successfully. Created {ship['class']} class ship."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze repository: {str(e)}")

