from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
import json
import asyncio
import time
import hashlib
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

# Create router
router = APIRouter()

# Models for hardcard event streams
class HardcardEvent(BaseModel):
    event_id: str
    timestamp: str
    event_type: str
    hardcard_id: str
    data: Dict[str, Any]
    signature: Optional[str] = None

class HardcardStreamResponse(BaseModel):
    events: List[HardcardEvent]
    next_cursor: Optional[str] = None

# Connected clients tracking
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, hardcard_id: str):
        await websocket.accept("databutton.app")  # Accept with the protocol
        if hardcard_id not in self.active_connections:
            self.active_connections[hardcard_id] = []
        self.active_connections[hardcard_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, hardcard_id: str):
        if hardcard_id in self.active_connections:
            if websocket in self.active_connections[hardcard_id]:
                self.active_connections[hardcard_id].remove(websocket)
            if not self.active_connections[hardcard_id]:
                del self.active_connections[hardcard_id]
                
    async def broadcast(self, hardcard_id: str, event: HardcardEvent):
        if hardcard_id in self.active_connections:
            for connection in self.active_connections[hardcard_id]:
                await connection.send_json(event.dict())

manager = ConnectionManager()

# Helper functions
def generate_event_id():
    """Generate a unique event ID"""
    return str(uuid.uuid4())

def get_current_timestamp():
    """Get current ISO timestamp"""
    return datetime.utcnow().isoformat() + "Z"

def compute_signature(event_data: dict) -> str:
    """Compute a signature for an event using SHA-256"""
    # In a real implementation, this would use a proper signing mechanism
    # For demo purposes, we'll just hash the JSON representation
    serialized = json.dumps(event_data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()

# Security events simulation
async def generate_hardcard_events(hardcard_id: str):
    """Generate simulated hardcard security events"""
    event_types = [
        "authentication_attempt",
        "key_rotation",
        "integrity_check",
        "access_granted",
        "access_denied",
        "signature_verification",
        "firmware_update",
        "quantum_key_exchange"
    ]
    
    status_options = ["success", "pending", "failed"]
    risk_levels = ["low", "medium", "high", "critical"]
    
    while True:
        # Random interval between events (1-5 seconds)
        await asyncio.sleep(1 + 4 * asyncio.get_event_loop().time() % 1)
        
        # Determine event type (with weighted probabilities for more common events)
        weights = [0.3, 0.1, 0.2, 0.15, 0.05, 0.1, 0.05, 0.05]
        choice = sum(asyncio.get_event_loop().time() * 10 % 1 for _ in range(3)) % 1
        cumulative = 0
        selected_event_type = event_types[0]
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if choice <= cumulative:
                selected_event_type = event_types[i]
                break
        
        # Generate event data based on type
        timestamp = get_current_timestamp()
        event_id = generate_event_id()
        
        # Base data all events have
        data = {
            "status": status_options[int(asyncio.get_event_loop().time() * 10) % 3],
            "location": "Legacy Vault Security System"
        }
        
        # Add event-specific data
        if selected_event_type == "authentication_attempt":
            data.update({
                "auth_method": "biometric" if asyncio.get_event_loop().time() % 2 > 1 else "hardcard",
                "ip_address": f"192.168.1.{int(asyncio.get_event_loop().time() * 100) % 255}",
                "user_agent": "Legacy Vault Client 1.0"
            })
        elif selected_event_type == "key_rotation":
            data.update({
                "key_type": "quantum_resistant",
                "rotation_reason": "scheduled",
                "key_id": f"key-{uuid.uuid4().hex[:8]}"
            })
        elif selected_event_type == "integrity_check":
            data.update({
                "check_type": "full_scan",
                "blocks_verified": int(asyncio.get_event_loop().time() * 1000) % 1000 + 1000,
                "verification_method": "cryptographic_hash"
            })
        elif selected_event_type == "access_granted":
            data.update({
                "resource": f"vault/{uuid.uuid4().hex[:8]}",
                "access_level": "read" if asyncio.get_event_loop().time() % 3 > 2 else "write",
                "session_id": f"session-{uuid.uuid4().hex[:10]}"
            })
        elif selected_event_type == "access_denied":
            data.update({
                "resource": f"vault/{uuid.uuid4().hex[:8]}",
                "reason": "insufficient_permissions",
                "risk_level": risk_levels[int(asyncio.get_event_loop().time() * 10) % 4]
            })
        elif selected_event_type == "signature_verification":
            data.update({
                "document_id": f"doc-{uuid.uuid4().hex[:8]}",
                "verification_method": "ecdsa",
                "valid": asyncio.get_event_loop().time() % 10 > 1  # 90% valid signatures
            })
        elif selected_event_type == "firmware_update":
            data.update({
                "version": f"1.{int(asyncio.get_event_loop().time() * 10) % 10}.{int(asyncio.get_event_loop().time() * 100) % 100}",
                "update_type": "security_patch",
                "components": ["encryption_module", "authentication_controller"]
            })
        elif selected_event_type == "quantum_key_exchange":
            data.update({
                "protocol": "BB84",
                "qubits_exchanged": int(asyncio.get_event_loop().time() * 1000) % 1000 + 2000,
                "entropy_estimate": f"{(asyncio.get_event_loop().time() * 10) % 1 + 99:.2f}%"
            })
        
        # Create event object
        event_obj = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": selected_event_type,
            "hardcard_id": hardcard_id,
            "data": data
        }
        
        # Compute signature and add to event
        signature = compute_signature(event_obj)
        event_obj["signature"] = signature
        
        # Create proper event object and broadcast
        event = HardcardEvent(**event_obj)
        await manager.broadcast(hardcard_id, event)

# Background tasks for each hardcard
async_tasks = {}

@router.websocket("/events/{hardcard_id}")
async def hardcard_events_stream(websocket: WebSocket, hardcard_id: str):
    """WebSocket endpoint for streaming hardcard security events
    
    Provides a real-time stream of security events for a specific hardcard,
    including authentication attempts, integrity checks, and other security-related activities.
    """
    await manager.connect(websocket, hardcard_id)
    
    # Start event generator for this hardcard if not already running
    if hardcard_id not in async_tasks or async_tasks[hardcard_id].done():
        task = asyncio.create_task(generate_hardcard_events(hardcard_id))
        async_tasks[hardcard_id] = task
    
    try:
        # Keep connection alive and handle client messages
        while True:
            # Wait for messages (client can send filters or commands)
            data = await websocket.receive_text()
            try:
                # Process client message (if needed)
                message = json.loads(data)
                if message.get("command") == "ping":
                    await websocket.send_json({"command": "pong", "timestamp": get_current_timestamp()})
            except json.JSONDecodeError:
                # Invalid message format
                await websocket.send_json({"error": "Invalid message format"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, hardcard_id)
        
        # If no more connections for this hardcard, cancel the task
        if hardcard_id not in manager.active_connections and hardcard_id in async_tasks:
            async_tasks[hardcard_id].cancel()
            del async_tasks[hardcard_id]

@router.get("/hardcard-events-summary")
async def get_hardcard_events_summary():
    """Get the current status of all hardcard event streams
    
    Returns information about active connections and event generation tasks.
    Provides monitoring data for the hardcard events streaming system.
    """
    active_hardcards = list(manager.active_connections.keys())
    connection_count = sum(len(connections) for connections in manager.active_connections.values())
    
    return {
        "active_hardcards": active_hardcards,
        "active_connections": connection_count,
        "running_tasks": len(async_tasks)
    }