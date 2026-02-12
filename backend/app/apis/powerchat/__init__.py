from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Set, Tuple
import json
import asyncio
import time
from datetime import datetime
import databutton as db
import re
import uuid
import os

# Create router
router = APIRouter()

# Models
class ContextEntry(BaseModel):
    value: str
    timestamp: float = None
    
    def __init__(self, **data):
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = time.time()
        super().__init__(**data)

class Suggestion(BaseModel):
    text: str
    confidence: float
    source: str

class SuggestionsResponse(BaseModel):
    suggestions: List[Suggestion]
    confidence: float
    timestamp: str

class ContextRequest(BaseModel):
    context: Dict[str, ContextEntry]

class ContextResponse(BaseModel):
    status: str
    message: str

# Context storage
context_store: Dict[str, Dict[str, ContextEntry]] = {}

# Persist context to storage
def _persist_context(client_id: str):
    """Persist context to storage"""
    if client_id in context_store:
        try:
            sanitized_id = re.sub(r'[^a-zA-Z0-9._-]', '', client_id)
            db.storage.json.put(f"powerchat_context_{sanitized_id}", context_store[client_id])
        except Exception as e:
            print(f"Error persisting context for {client_id}: {e}")

# Load context from storage
def _load_context(client_id: str) -> Dict[str, ContextEntry]:
    """Load context from storage"""
    try:
        sanitized_id = re.sub(r'[^a-zA-Z0-9._-]', '', client_id)
        context = db.storage.json.get(f"powerchat_context_{sanitized_id}", default={})
        # Convert dict to ContextEntry objects
        return {k: ContextEntry(**v) for k, v in context.items()}
    except Exception as e:
        print(f"Error loading context for {client_id}: {e}")
        return {}

# Generate suggestions based on context
def generate_suggestions(context: Dict[str, ContextEntry]) -> Tuple[List[Suggestion], float]:
    """Generate suggestions based on context"""
    suggestions = []
    max_sources = 5  # Maximum number of context sources for confidence calculation
    
    # Process clipboard data if available
    if 'clipboard' in context:
        text = context['clipboard'].value
        if text and len(text.strip()) > 0:
            # Simple suggestion based on clipboard content
            suggestions.append(
                Suggestion(
                    text=f"Use this from clipboard: {text[:50]}{'...' if len(text) > 50 else ''}",
                    confidence=0.8,
                    source="clipboard"
                )
            )
            
            # If it looks like a product ID or SKU, create a related suggestion
            if re.match(r'^[A-Z0-9]{4,12}$', text.strip()):
                suggestions.append(
                    Suggestion(
                        text=f"Search for product with ID: {text.strip()}",
                        confidence=0.9,
                        source="clipboard_sku"
                    )
                )
    
    # Process API data if available
    for key, entry in context.items():
        if key.startswith('api_'):
            try:
                data = json.loads(entry.value)
                category = key.replace('api_', '')
                
                if category == 'products' and isinstance(data, list) and len(data) > 0:
                    # Suggest first few products
                    for i, product in enumerate(data[:3]):
                        if 'name' in product and 'sku' in product:
                            suggestions.append(
                                Suggestion(
                                    text=f"Product: {product['name']} (SKU: {product['sku']})",
                                    confidence=0.85,
                                    source=f"api_products"
                                )
                            )
                
                elif category == 'categories' and isinstance(data, list) and len(data) > 0:
                    # Suggest first few categories
                    for i, category_data in enumerate(data[:3]):
                        if 'name' in category_data:
                            suggestions.append(
                                Suggestion(
                                    text=f"Category: {category_data['name']}",
                                    confidence=0.75,
                                    source=f"api_categories"
                                )
                            )
            except Exception as e:
                print(f"Error processing API data for {key}: {e}")
    
    # Calculate overall confidence as ratio of non-empty sources to max sources
    sources_count = sum(1 for entry in context.values() if entry.value.strip())
    completeness = min(1.0, sources_count / max_sources)
    
    return suggestions, completeness

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.last_heartbeat: Dict[str, float] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept("databutton.app")
        self.active_connections[client_id] = websocket
        self.last_heartbeat[client_id] = time.time()
        print(f"PowerChat client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.last_heartbeat:
            del self.last_heartbeat[client_id]
        print(f"PowerChat client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_suggestions(self, client_id: str, suggestions: List[Suggestion], confidence: float):
        if client_id in self.active_connections:
            message = SuggestionsResponse(
                suggestions=suggestions,
                confidence=confidence,
                timestamp=datetime.utcnow().isoformat()
            )
            await self.active_connections[client_id].send_json(message.dict())
    
    async def heartbeat_monitor(self):
        """Monitor client connections and disconnect inactive ones"""
        while True:
            try:
                current_time = time.time()
                to_remove = []
                
                for client_id, last_time in self.last_heartbeat.items():
                    # If no heartbeat for 60 seconds, disconnect
                    if current_time - last_time > 60:
                        to_remove.append(client_id)
                
                for client_id in to_remove:
                    print(f"Client {client_id} timed out due to inactivity")
                    # Close WebSocket if still active
                    if client_id in self.active_connections:
                        try:
                            await self.active_connections[client_id].close(code=1000, reason="Inactivity timeout")
                        except Exception:
                            pass  # Connection might already be closed
                    self.disconnect(client_id)
                
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(10)  # Continue monitoring despite errors

# Create connection manager
manager = ConnectionManager()

# Start the heartbeat monitor in the background
bg_task = None
@router.on_event("startup")
async def startup_event():
    global bg_task
    bg_task = asyncio.create_task(manager.heartbeat_monitor())

@router.on_event("shutdown")
async def shutdown_event():
    if bg_task:
        bg_task.cancel()

# API endpoints
@router.get("/powerchat-health")
def check_powerchat_health():
    """Check if the PowerChat API is running"""
    return {"status": "ok", "message": "PowerChat API is operational"}

@router.post("/context/{client_id}")
async def update_context(client_id: str, request: ContextRequest, background_tasks: BackgroundTasks):
    """Update context for a specific client"""
    # Initialize client context if not exists
    if client_id not in context_store:
        # Try to load from storage first
        context_store[client_id] = _load_context(client_id)
    
    # Update context with new entries
    context_store[client_id].update(request.context)
    
    # Persist context in background
    background_tasks.add_task(_persist_context, client_id)
    
    # Generate suggestions based on updated context
    suggestions, confidence = generate_suggestions(context_store[client_id])
    
    # If client is connected via WebSocket, send suggestions
    if client_id in manager.active_connections:
        background_tasks.add_task(manager.send_suggestions, client_id, suggestions, confidence)
    
    return ContextResponse(status="success", message="Context updated")

@router.get("/context/{client_id}")
async def get_context(client_id: str):
    """Get context for a specific client"""
    # Initialize client context if not exists
    if client_id not in context_store:
        # Try to load from storage
        context_store[client_id] = _load_context(client_id)
    
    return context_store[client_id]

@router.get("/suggestions/{client_id}")
async def get_suggestions(client_id: str):
    """Get suggestions for a specific client"""
    # Initialize client context if not exists
    if client_id not in context_store:
        # Try to load from storage
        context_store[client_id] = _load_context(client_id)
    
    # Generate suggestions based on context
    suggestions, confidence = generate_suggestions(context_store[client_id])
    
    return SuggestionsResponse(
        suggestions=suggestions,
        confidence=confidence,
        timestamp=datetime.utcnow().isoformat()
    )

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication with PowerChat clients"""
    await manager.connect(client_id, websocket)
    
    # Load context for this client
    if client_id not in context_store:
        context_store[client_id] = _load_context(client_id)
    
    try:
        while True:
            # Wait for message from client
            message_text = await websocket.receive_text()
            try:
                message = json.loads(message_text)
                
                # Handle heartbeat
                if "heartbeat" in message:
                    manager.last_heartbeat[client_id] = time.time()
                    await websocket.send_json({"heartbeat_ack": message["heartbeat"]})
                    continue
                
                # Handle context update
                if "context" in message:
                    # Update context with new entries
                    new_context = {k: ContextEntry(**v) for k, v in message["context"].items()}
                    context_store[client_id].update(new_context)
                    
                    # Persist context
                    _persist_context(client_id)
                    
                    # Generate and send suggestions
                    suggestions, confidence = generate_suggestions(context_store[client_id])
                    await manager.send_suggestions(client_id, suggestions, confidence)
            except json.JSONDecodeError:
                print(f"Received invalid JSON from client {client_id}: {message_text}")
            except Exception as e:
                print(f"Error processing message from client {client_id}: {e}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"Unexpected error in WebSocket connection for client {client_id}: {e}")
        manager.disconnect(client_id)