from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import asyncio
import time
from datetime import datetime
import databutton as db
import re

# Import the app's own apis
from app.apis.integrations import update_thinlayer_context

router = APIRouter(prefix="/thinlayer")

# Models for ThinLayerServiceAgent

class ContextEntry(BaseModel):
    value: str
    timestamp: str

class ContextData(BaseModel):
    context: Dict[str, ContextEntry]
    
class Suggestion(BaseModel):
    text: str
    confidence: float
    source: str
    
class SuggestionResponse(BaseModel):
    suggestions: List[Suggestion]
    confidence: float
    timestamp: str

class AgentLogEntry(BaseModel):
    timestamp: str
    context_keys: List[str]
    context_values: Dict[str, str]
    suggestions: List[str]
    confidence: float
    action_taken: Optional[str] = None

# Helper functions

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_agent_logs() -> List[AgentLogEntry]:
    """Get ThinLayerServiceAgent logs from storage"""
    try:
        logs = db.storage.json.get("thinlayer_agent_logs", default=[])
        return [AgentLogEntry(**log) for log in logs]
    except Exception as e:
        print(f"Error getting agent logs: {str(e)}")
        return []

def save_agent_log(log_entry: AgentLogEntry) -> bool:
    """Save a new log entry to storage"""
    try:
        logs = get_agent_logs()
        logs.append(log_entry)
        # Keep only the last 1000 logs
        if len(logs) > 1000:
            logs = logs[-1000:]
        logs_data = [log.model_dump() for log in logs]
        db.storage.json.put("thinlayer_agent_logs", logs_data)
        return True
    except Exception as e:
        print(f"Error saving agent log: {str(e)}")
        return False

def generate_suggestions(context: Dict[str, ContextEntry]) -> SuggestionResponse:
    """Generate suggestions based on context"""
    if not context:
        return SuggestionResponse(
            suggestions=[],
            confidence=0.0,
            timestamp=datetime.utcnow().isoformat()
        )
    
    # Calculate confidence based on context quantity and freshness
    max_sources = 5
    completeness = min(1.0, len(context) / max_sources)
    
    suggestions = []
    
    # Hempex-specific: show customer profile if API context exists
    if 'api' in context:
        suggestions.append(Suggestion(
            text=f"✔ Profile: {context['api'].value}",
            confidence=0.9,
            source="api"
        ))
    
    # Add clipboard-based suggestions if present
    if 'clipboard' in context:
        clipboard_text = context['clipboard'].value.lower()
        
        # Check for product mentions
        product_keywords = ['cbd', 'oil', 'tincture', 'capsule', 'topical', 'hemp']
        for keyword in product_keywords:
            if keyword in clipboard_text:
                suggestions.append(Suggestion(
                    text=f"🔍 Search products for '{keyword}'",
                    confidence=0.7,
                    source="clipboard"
                ))
                break
        
        # Check for customer service terms
        support_keywords = ['help', 'question', 'issue', 'problem', 'refund', 'return']
        for keyword in support_keywords:
            if keyword in clipboard_text:
                suggestions.append(Suggestion(
                    text=f"📧 Prepare customer service response",
                    confidence=0.8,
                    source="clipboard"
                ))
                break
    
    # Add integration-based suggestions
    # WooCommerce integration
    woo_product_key = 'woocommerce_products_count'
    woo_order_key = 'woocommerce_orders_count'
    if woo_product_key in context and woo_order_key in context:
        suggestions.append(Suggestion(
            text=f"📊 WooCommerce: {context[woo_product_key].value} products, {context[woo_order_key].value} orders",
            confidence=0.85,
            source="integration"
        ))
        
        # Add action suggestion if the context indicates sync is needed
        woo_sync_key = 'woocommerce_sync_status'
        if woo_sync_key in context and context[woo_sync_key].value != 'completed':
            suggestions.append(Suggestion(
                text="🔄 Sync WooCommerce data",
                confidence=0.9,
                source="integration"
            ))
    
    # DNS integration
    dns_domains_key = 'dns_domains'
    if dns_domains_key in context:
        domains = context[dns_domains_key].value
        suggestions.append(Suggestion(
            text=f"🌐 DNS: {domains} domain(s) configured",
            confidence=0.7,
            source="integration"
        ))
    
    # Marketing integration
    marketing_lists_key = 'marketing_lists_count'
    if marketing_lists_key in context:
        suggestions.append(Suggestion(
            text=f"📧 Marketing: {context[marketing_lists_key].value} subscriber lists",
            confidence=0.75,
            source="integration"
        ))
    
    # Fulfillment integration
    fulfillment_inventory_key = 'fulfillment_inventory_status'
    if fulfillment_inventory_key in context:
        status = context[fulfillment_inventory_key].value
        if status == 'low':
            suggestions.append(Suggestion(
                text="⚠️ Low inventory alert",
                confidence=0.95,
                source="integration"
            ))
    
    # Recommendation engine
    recommendation_key = 'recommendation_count'
    if recommendation_key in context:
        suggestions.append(Suggestion(
            text=f"🔍 {context[recommendation_key].value} product recommendations ready",
            confidence=0.8,
            source="integration"
        ))
    
    # Common actions
    suggestions.extend([
        Suggestion(text="🔍 Refine search", confidence=0.5, source="default"),
        Suggestion(text="✏️ Define a rule", confidence=0.4, source="default"),
        Suggestion(text="💬 Powerchat ritual", confidence=0.3 if completeness < 0.5 else 0.1, source="default"),
        Suggestion(text="❌ Hide overlay", confidence=0.2, source="default")
    ])
    
    return SuggestionResponse(
        suggestions=suggestions,
        confidence=completeness,
        timestamp=datetime.utcnow().isoformat()
    )

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.last_heartbeat: Dict[str, float] = {}
        self.background_task = None
    
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept("databutton.app")
        self.active_connections[client_id] = websocket
        self.last_heartbeat[client_id] = time.time()
        print(f"Client {client_id} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.last_heartbeat:
            del self.last_heartbeat[client_id]
        print(f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_suggestions(self, client_id: str, suggestions: SuggestionResponse):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(suggestions.model_dump())
            except Exception as e:
                print(f"Error sending suggestions to client {client_id}: {str(e)}")
                self.disconnect(client_id)
    
    async def heartbeat_monitor(self):
        while True:
            current_time = time.time()
            clients_to_disconnect = []
            
            for client_id, last_time in self.last_heartbeat.items():
                # If no heartbeat for 30 seconds, consider the connection dead
                if current_time - last_time > 30:
                    clients_to_disconnect.append(client_id)
            
            for client_id in clients_to_disconnect:
                print(f"Client {client_id} timed out (no heartbeat)")
                self.disconnect(client_id)
            
            await asyncio.sleep(10)  # Check every 10 seconds

manager = ConnectionManager()

# API Endpoints

@router.get("/health")
def check_health_thinlayer():
    """Check if the ThinLayerServiceAgent API is running"""
    return {"status": "ok", "message": "ThinLayerServiceAgent API is operational"}

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication with the ThinLayerServiceAgent"""
    await manager.connect(client_id, websocket)
    
    try:
        # Start the heartbeat monitor if not already running
        if manager.background_task is None:
            manager.background_task = asyncio.create_task(manager.heartbeat_monitor())
        
        while True:
            data = await websocket.receive_text()
            manager.last_heartbeat[client_id] = time.time()
            
            try:
                json_data = json.loads(data)
                
                # Handle heartbeat messages
                if "heartbeat" in json_data:
                    await websocket.send_json({"heartbeat_ack": time.time()})
                    continue
                
                # Process context updates
                if "context" in json_data:
                    context_data = {k: ContextEntry(**v) for k, v in json_data["context"].items()}
                    
                    # Generate suggestions based on context
                    response = generate_suggestions(context_data)
                    
                    # Log this interaction
                    log_entry = AgentLogEntry(
                        timestamp=datetime.utcnow().isoformat(),
                        context_keys=list(context_data.keys()),
                        context_values={k: v.value for k, v in context_data.items()},
                        suggestions=[s.text for s in response.suggestions],
                        confidence=response.confidence
                    )
                    save_agent_log(log_entry)
                    
                    # Send suggestions back to the client
                    await manager.send_suggestions(client_id, response)
            except json.JSONDecodeError:
                print(f"Received invalid JSON from client {client_id}")
            except Exception as e:
                print(f"Error processing message from client {client_id}: {str(e)}")
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
