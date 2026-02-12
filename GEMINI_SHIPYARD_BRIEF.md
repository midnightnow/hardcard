# 🚢 Cursive Shipyard Project Brief for Gemini CLI

## 🎯 Executive Summary

The **Cursive Shipyard** is the command and control center for the HardCard Automated Application Factory - a sophisticated AI-driven system where 112+ AI agents collaboratively build, test, and deploy software applications. This brief provides Gemini CLI with comprehensive context to continue development of this critical infrastructure.

## 🏗️ Project Context

### The Three-Layer Architecture

1. **Layer 1: Cursive Shipyard (GUI Command Center)**
   - Visual dashboard for human operators
   - Real-time monitoring of all "ships" (applications being built)
   - Task assignment and agent coordination
   - Blueprint creation for new applications

2. **Layer 2: HardCard Platform (Execution Environment)**
   - Monorepo with Git worktrees for parallel development
   - Standardized infrastructure and services
   - CI/CD pipeline automation

3. **Layer 3: AI Workforce (112+ Agents)**
   - Frontend, Backend, Testing, Security, Documentation specialists
   - Self-organizing agents with emergent behaviors
   - Meta-agents that create specialized sub-agents
   - Novel patterns: Octopus, Antibody, Resonance, Harmonic models

### Strategic Vision
- **Goal**: Create a "1-Person Unicorn" - enabling a single operator to build and scale a portfolio of billion-dollar applications
- **Flagship Product**: VetSorcery (veterinary practice management system)
- **Revenue Target**: $100M+ ARR by 2027
- **Impact**: Save 170 million animal lives by 2035

## 📊 Current Implementation Status

### ✅ What Exists

#### Backend (`/Users/studio/hardcard/backend/`)
```python
# services/factory_monitor.py
- FactoryEfficiencyMonitor class (placeholder implementation)
- Basic metrics calculation structure
- Bottleneck identification framework

# api/v1/factory.py
- GET /factory/efficiency endpoint
- POST /factory/optimize endpoint
- Dependency injection setup
```

#### Frontend (`/Users/studio/hardcard/frontend/src/`)
```typescript
// contexts/shipyard/ShipyardContext.tsx
- Ship state management
- Mock WebSocket connection
- Fleet status tracking

// components/shipyard/FleetOverview.tsx
- Dashboard main view
- Connection status indicator
- Grid layout for ships

// components/shipyard/ShipCard.tsx
- Individual ship visualization
- Progress bars and status colors
- Agent count display
```

### ❌ What's Missing

1. **Real WebSocket Infrastructure**
   - Backend WebSocket server implementation
   - Bi-directional communication
   - Event streaming from agents
   - Connection management

2. **Agent Integration**
   - No connection to the 112-agent system
   - No real-time agent status
   - No task assignment mechanism
   - No workload visualization

3. **Blueprint System**
   - No UI for creating new applications
   - No template management
   - No configuration wizard

4. **Deployment Controls**
   - No environment management
   - No deployment triggers
   - No rollback mechanisms

5. **Real Metrics**
   - All metrics are hardcoded placeholders
   - No actual efficiency calculations
   - No real bottleneck detection

## 🚀 Development Roadmap

### Phase 1: Real-Time Infrastructure (IMMEDIATE PRIORITY)

**Epic 1: Backend WebSocket Implementation**
```python
# Tasks:
1. Create /ws/shipyard-stream endpoint in FastAPI
2. Implement WebSocket connection manager
3. Create event broadcasting system
4. Stream real metrics from FactoryEfficiencyMonitor
5. Handle connection lifecycle (connect/disconnect/reconnect)
```

**Epic 2: Frontend WebSocket Integration**
```typescript
// Tasks:
1. Replace mock WebSocket with real connection
2. Implement reconnection logic with exponential backoff
3. Add connection state management
4. Create real-time data synchronization
5. Add error handling and fallbacks
```

### Phase 2: Agent Coordination (Week 3-4)
- Agent registry and status tracking
- Task assignment interface
- Workload balancing visualization
- Performance metrics dashboard

### Phase 3: Blueprint Management (Week 5-6)
- Visual blueprint designer
- Template library
- Configuration management
- Build pipeline visualization

### Phase 4: Deployment Pipeline (Week 7-8)
- Environment management
- One-click deployment
- Rollback capabilities
- Production monitoring

### Phase 5: Advanced Analytics (Week 9-10)
- Real efficiency calculations
- Predictive analytics
- Auto-scaling workforce
- Self-healing capabilities

## 💻 Technical Implementation Details

### Backend WebSocket Server Structure
```python
# /Users/studio/hardcard/backend/api/v1/shipyard_ws.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Handle disconnected clients
                pass

manager = ConnectionManager()

@router.websocket("/ws/shipyard-stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Start background task to stream metrics
        asyncio.create_task(stream_metrics(websocket))
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Process commands from frontend
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### Frontend WebSocket Integration
```typescript
// /Users/studio/hardcard/frontend/src/hooks/useShipyardWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export const useShipyardWebSocket = (url: string) => {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  
  useEffect(() => {
    const connect = () => {
      ws.current = new WebSocket(url);
      
      ws.current.onopen = () => {
        setIsConnected(true);
        console.log('Shipyard WebSocket connected');
      };
      
      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      };
      
      ws.current.onclose = () => {
        setIsConnected(false);
        // Implement reconnection logic
        setTimeout(connect, 3000);
      };
    };
    
    connect();
    
    return () => {
      ws.current?.close();
    };
  }, [url]);
  
  return { isConnected, lastMessage, sendMessage: (msg: any) => ws.current?.send(JSON.stringify(msg)) };
};
```

## 🎯 Immediate Next Steps for Gemini

### Step 1: Create Backend WebSocket Endpoint
1. Navigate to `/Users/studio/hardcard/backend/`
2. Create new file `api/v1/shipyard_ws.py`
3. Implement WebSocket endpoint with connection management
4. Add route to main FastAPI application
5. Test with WebSocket client (e.g., `websocat`)

### Step 2: Stream Real Metrics
1. Modify `FactoryEfficiencyMonitor` to generate dynamic metrics
2. Create background task to calculate and broadcast metrics every 2 seconds
3. Include ship status updates in the broadcast
4. Add error handling for disconnected clients

### Step 3: Update Frontend Connection
1. Replace mock WebSocket in `ShipyardContext.tsx`
2. Point to real backend endpoint: `ws://localhost:8000/ws/shipyard-stream`
3. Handle connection states properly
4. Update UI to show real-time data

### Step 4: Test End-to-End
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Verify real-time updates in dashboard
4. Test connection recovery on backend restart

## 📝 Key Files to Modify

1. **Backend**:
   - Create: `/backend/api/v1/shipyard_ws.py`
   - Modify: `/backend/main.py` (add WebSocket route)
   - Enhance: `/backend/services/factory_monitor.py` (real metrics)

2. **Frontend**:
   - Modify: `/frontend/src/contexts/shipyard/ShipyardContext.tsx`
   - Create: `/frontend/src/hooks/useShipyardWebSocket.ts`
   - Update: `/frontend/src/components/shipyard/FleetOverview.tsx`

## 🔍 Testing Strategy

1. **Unit Tests**:
   - Test WebSocket connection manager
   - Test metric calculation logic
   - Test reconnection handling

2. **Integration Tests**:
   - Test full WebSocket flow
   - Test metric streaming
   - Test error scenarios

3. **E2E Tests**:
   - Test dashboard updates
   - Test connection recovery
   - Test multiple concurrent connections

## 🎨 UI/UX Considerations

- Show clear connection status (green/red indicator)
- Display "last updated" timestamp for each metric
- Smooth animations for progress updates
- Graceful degradation when disconnected
- Loading states during reconnection

## 🚦 Success Criteria

1. **Technical**:
   - WebSocket latency < 100ms
   - Supports 100+ concurrent connections
   - Automatic reconnection within 5 seconds
   - Zero message loss during normal operation

2. **Functional**:
   - Real-time fleet status updates
   - Live progress tracking for each ship
   - Accurate efficiency metrics
   - Responsive to backend changes

3. **User Experience**:
   - Intuitive connection status
   - Smooth, flicker-free updates
   - Clear error messages
   - Fast initial load time

## 🎯 The Big Picture

Remember, the Cursive Shipyard is the nerve center of an ambitious project to create an Automated Application Factory. Every feature we build should support the vision of enabling a single operator to orchestrate 112+ AI agents building multiple applications simultaneously.

The Enhanced Receptionist work in VetSorcery (achieving 98%+ success rate) demonstrates the power of this approach. Now we need the Shipyard to provide visibility and control over this entire ecosystem.

## 📞 Questions for Clarification

Before proceeding, Gemini should verify:
1. Is the backend running on port 8000?
2. Is the frontend running on port 3000?
3. Are there any specific WebSocket libraries preferred?
4. Should we use Socket.io or native WebSocket?
5. Any specific metrics to prioritize for Phase 1?

---

**Good luck, Gemini! You're building the command center for the future of automated software development. The foundation is laid - now let's make it real-time and powerful!**