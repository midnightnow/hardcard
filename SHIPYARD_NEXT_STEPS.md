# 🚢 Cursive Shipyard: Immediate Next Steps

## 🎯 Current Situation

The Cursive Shipyard exists as a proof-of-concept with mock data. Your mission is to transform it into a real-time command center for the Automated Application Factory.

## 🔥 Priority 1: WebSocket Infrastructure (DO THIS FIRST)

### Backend Tasks:

1. **Create WebSocket Endpoint**
   ```bash
   cd /Users/studio/hardcard/backend
   # Create new file: api/v1/shipyard_ws.py
   ```

2. **Implement This Code**:
   ```python
   from fastapi import APIRouter, WebSocket, WebSocketDisconnect
   from typing import List
   import asyncio
   import json
   from datetime import datetime
   from backend.services.factory_monitor import FactoryEfficiencyMonitor
   
   router = APIRouter()
   
   class ConnectionManager:
       def __init__(self):
           self.active_connections: List[WebSocket] = []
           self.monitor = FactoryEfficiencyMonitor()
           
       async def connect(self, websocket: WebSocket):
           await websocket.accept()
           self.active_connections.append(websocket)
           await self.send_personal_message({"type": "connection", "status": "connected"}, websocket)
           
       def disconnect(self, websocket: WebSocket):
           self.active_connections.remove(websocket)
           
       async def send_personal_message(self, message: dict, websocket: WebSocket):
           await websocket.send_json(message)
           
       async def broadcast(self, message: dict):
           for connection in self.active_connections:
               try:
                   await connection.send_json(message)
               except:
                   pass
   
   manager = ConnectionManager()
   
   async def stream_shipyard_updates():
       """Background task to stream updates to all connected clients"""
       while True:
           # Get current metrics
           metrics = manager.monitor.get_current_metrics()
           
           # Create shipyard update message
           update = {
               "type": "shipyard_update",
               "timestamp": datetime.now().isoformat(),
               "data": {
                   "fleet": [
                       {"id": "vetsorcery", "name": "VetSorcery", "status": "Launched", "progress": 100, "agentCount": 5},
                       {"id": "nexus", "name": "Nexus", "status": "Building", "progress": 65, "agentCount": 3},
                       {"id": "hempex", "name": "HEMPEX", "status": "Testing", "progress": 85, "agentCount": 4},
                   ],
                   "efficiency": {
                       "overall": metrics.overall_efficiency,
                       "bottlenecks": metrics.bottlenecks,
                       "suggestions": metrics.suggested_optimizations
                   }
               }
           }
           
           await manager.broadcast(update)
           await asyncio.sleep(2)  # Update every 2 seconds
   
   @router.websocket("/ws/shipyard-stream")
   async def websocket_endpoint(websocket: WebSocket):
       await manager.connect(websocket)
       
       # Start streaming updates if this is the first connection
       if len(manager.active_connections) == 1:
           asyncio.create_task(stream_shipyard_updates())
       
       try:
           while True:
               # Wait for any messages from client
               data = await websocket.receive_text()
               message = json.loads(data)
               
               # Handle different message types
               if message.get("type") == "ping":
                   await manager.send_personal_message({"type": "pong"}, websocket)
               elif message.get("type") == "request_update":
                   # Send immediate update
                   pass
                   
       except WebSocketDisconnect:
           manager.disconnect(websocket)
   ```

3. **Update main.py**:
   ```python
   # In /backend/main.py, add:
   from backend.api.v1 import shipyard_ws
   
   # After other route includes:
   app.include_router(shipyard_ws.router, prefix="/api/v1")
   ```

### Frontend Tasks:

1. **Update ShipyardContext.tsx**:
   ```typescript
   // Replace the mock WebSocket section with:
   
   const WEBSOCKET_URL = 'ws://localhost:8000/ws/shipyard-stream';
   
   useEffect(() => {
     let ws: WebSocket;
     let reconnectInterval: NodeJS.Timeout;
     
     const connect = () => {
       ws = new WebSocket(WEBSOCKET_URL);
       
       ws.onopen = () => {
         console.log('Connected to Shipyard WebSocket');
         setShipyardState(prev => ({ ...prev, isConnected: true }));
         
         // Send ping every 30 seconds to keep connection alive
         const pingInterval = setInterval(() => {
           if (ws.readyState === WebSocket.OPEN) {
             ws.send(JSON.stringify({ type: 'ping' }));
           }
         }, 30000);
       };
       
       ws.onmessage = (event) => {
         const message = JSON.parse(event.data);
         
         if (message.type === 'shipyard_update') {
           setShipyardState(prev => ({
             ...prev,
             fleet: message.data.fleet,
             lastUpdate: message.timestamp
           }));
         }
       };
       
       ws.onerror = (error) => {
         console.error('WebSocket error:', error);
       };
       
       ws.onclose = () => {
         console.log('Disconnected from Shipyard WebSocket');
         setShipyardState(prev => ({ ...prev, isConnected: false }));
         
         // Attempt to reconnect after 3 seconds
         reconnectInterval = setTimeout(connect, 3000);
       };
     };
     
     connect();
     
     return () => {
       ws?.close();
       clearTimeout(reconnectInterval);
     };
   }, []);
   ```

## 🔧 Testing Instructions

1. **Start Backend**:
   ```bash
   cd /Users/studio/hardcard/backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend**:
   ```bash
   cd /Users/studio/hardcard/frontend
   npm install  # If needed
   npm run dev
   ```

3. **Verify Connection**:
   - Open http://localhost:3000
   - Navigate to Shipyard dashboard
   - Check for green "Live" indicator
   - Watch for real-time updates every 2 seconds

4. **Test Connection Recovery**:
   - Stop backend (Ctrl+C)
   - Watch frontend show "Disconnected"
   - Restart backend
   - Verify automatic reconnection

## 📊 What Success Looks Like

When complete, you should see:
- ✅ Green "Live" indicator in dashboard
- ✅ Ship cards updating every 2 seconds
- ✅ Efficiency metrics displayed
- ✅ Automatic reconnection on disconnect
- ✅ Smooth, flicker-free updates

## 🚨 Common Issues & Solutions

1. **CORS Error**: Add WebSocket to CORS config in backend
2. **Connection Refused**: Ensure backend is running on port 8000
3. **No Updates**: Check browser console for WebSocket errors
4. **Type Errors**: Ensure TypeScript types match the data structure

## 🎯 Next After WebSocket Works

Once real-time updates are working:
1. Add real agent data instead of mock ships
2. Implement dynamic progress updates
3. Add task assignment functionality
4. Create efficiency visualizations
5. Build the blueprint system

---

**Remember**: The Cursive Shipyard is the nerve center of the Automated Application Factory. Every line of code brings us closer to the "1-Person Unicorn" vision!

Good luck! 🚀