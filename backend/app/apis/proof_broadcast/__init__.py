"""
API for broadcasting new anchoring proofs to subscribed clients via WebSockets.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth import AuthorizedUser # To protect the WebSocket endpoint
from typing import List, Dict, Any
import json

router = APIRouter(
    prefix="/ws/v1/proofs", 
    tags=["Proof Broadcast", "WebSocket"]
)

# In-memory store for active WebSocket connections. 
# For a multi-worker/multi-instance setup, a more robust solution like Redis Pub/Sub would be needed.
active_connections: List[WebSocket] = []

@router.websocket("/updates")
async def websocket_proof_updates(websocket: WebSocket, user: AuthorizedUser):
    """
    WebSocket endpoint for clients to subscribe to new anchoring proof updates.
    Requires authentication.
    The client must send 'databutton.app' and 'Authorization.Bearer.{token}' in Sec-WebSocket-Protocol header.
    """
    await websocket.accept(subprotocol="databutton.app")
    active_connections.append(websocket)
    print(f"Client {user.sub} connected to proof updates. Total clients: {len(active_connections)}")
    try:
        while True:
            # Keep the connection alive and listen for any client messages (optional)
            # For a pure broadcast, the server primarily sends, client receives.
            # If client can send messages, handle them here.
            # For now, we'll just wait for disconnect or server-side broadcast.
            data = await websocket.receive_text() 
            # Echo back or process client message if needed
            # await websocket.send_text(f"Message text was: {data}, from user {user.sub}")
            print(f"Received from {user.sub}: {data}") # Placeholder for potential client messages

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Client {user.sub} disconnected from proof updates. Total clients: {len(active_connections)}")
    except Exception as e:
        active_connections.remove(websocket)
        print(f"Error with client {user.sub}: {e}. Disconnected. Total clients: {len(active_connections)}")

async def broadcast_proof_to_subscribers(proof_payload: Dict[str, Any]):
    """
    Broadcasts a new proof payload to all connected WebSocket clients.
    """
    # Construct the message according to the defined format
    message = {
        "type": "NEW_ANCHOR_PROOF",
        "timestamp": proof_payload.get("timestamp", "N/A"), # Ensure timestamp is part of payload or generate here
        "proof": proof_payload
    }
    message_json = json.dumps(message)
    
    # Create a list of tasks to send messages concurrently
    # Iterate over a copy of the list in case of disconnections during broadcast
    disconnected_clients: List[WebSocket] = []
    for connection in active_connections[:]:
        try:
            await connection.send_text(message_json)
        except WebSocketDisconnect:
            print(f"Client disconnected during broadcast. Will remove.")
            disconnected_clients.append(connection)
        except Exception as e:
            print(f"Error sending to a client during broadcast: {e}. Will remove.")
            disconnected_clients.append(connection)
    
    # Remove clients that disconnected or errored out during broadcast
    for client_to_remove in disconnected_clients:
        if client_to_remove in active_connections:
            active_connections.remove(client_to_remove)
            print(f"Removed disconnected/errored client. Total clients: {len(active_connections)}")

    print(f"Broadcasted proof to {len(active_connections)} client(s).")

# Example usage (to be called from Merkle job completion logic):
# async def example_trigger_broadcast():
#     sample_proof = {
#         "merkle_root": "0xabcdef123456",
#         "transaction_hash": "0x789ghi",
#         "block_number": 1234567,
#         "timestamp": "2024-05-23T12:00:00Z"
#     }
#     await broadcast_proof_to_subscribers(sample_proof)

