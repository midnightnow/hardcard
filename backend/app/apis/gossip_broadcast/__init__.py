from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth import AuthorizedUser
import asyncio # Added asyncio
from typing import List, Dict, Any
import json

router = APIRouter(
    prefix="/ws", 
    tags=["websockets"]
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, topic: str = "default_topic"):
        await websocket.accept(subprotocol="databutton.app")
        self.active_connections.append(websocket)
        print(f"New WebSocket connection: {websocket.client}")
        print(f"Total active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket connection closed: {websocket.client}")
            print(f"Total active connections: {len(self.active_connections)}")

    async def broadcast_json(self, data: Dict[str, Any]):
        print(f"Broadcasting JSON data: {data} to {len(self.active_connections)} connections")
        if not self.active_connections:
            print("No active WebSocket connections to broadcast to.")
            return
        
        message = json.dumps(data)
        send_tasks = [conn.send_text(message) for conn in self.active_connections]
        results = await asyncio.gather(*send_tasks, return_exceptions=True)
        
        # Store connections to remove to avoid modifying list while iterating indirectly
        connections_to_remove = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                # Attempt to get the connection associated with the failed task
                # This assumes active_connections hasn't changed order or size during await
                if idx < len(self.active_connections):
                    conn = self.active_connections[idx]
                    print(f"Error sending message to {conn.client}: {result}")
                    # Mark for removal instead of disconnecting immediately
                    if conn not in connections_to_remove:
                        connections_to_remove.append(conn)
                else:
                    print(f"Error sending message to a connection (index {idx} out of bounds for active_connections): {result}")
        
        # Remove problematic connections
        for conn_to_remove in connections_to_remove:
            self.disconnect(conn_to_remove) # Use existing disconnect logic

manager = ConnectionManager()

@router.websocket("/gossip")
async def gossip_endpoint(websocket: WebSocket, user: AuthorizedUser): # Added AuthorizedUser
    await manager.connect(websocket, topic=f"user_{user.sub}") # Use user.sub in the topic
    try:
        while True:
            data = await websocket.receive_text() 
            print(f"Received message from user {user.sub} ({websocket.client}): {data}")
    except WebSocketDisconnect:
        print(f"WebSocket for user {user.sub} ({websocket.client}) disconnected explicitly.")
    except Exception as e:
        print(f"Unexpected error with WebSocket for user {user.sub} ({websocket.client}): {e}")
    finally:
        manager.disconnect(websocket)

async def broadcast_json(data: Dict[str, Any]):
    await manager.broadcast_json(data)