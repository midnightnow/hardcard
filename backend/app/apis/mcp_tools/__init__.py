from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import databutton as db
import json
from datetime import datetime

router = APIRouter(prefix="/api/v1/tools")

# Request/Response Models
class MemorySaveParams(BaseModel):
    content: str
    type: str = "knowledge"
    tags: List[str] = []

class MemoryContextParams(BaseModel):
    taskId: Optional[str] = None
    limit: int = 10

class MemorySearchParams(BaseModel):
    query: str
    types: List[str] = ["knowledge"]

class ScreenshotParams(BaseModel):
    selector: str = "body"
    analysisType: str = "basic"

# Wrapper for client requests
class MCPToolRequest(BaseModel):
    params: Dict[str, Any]

class MCPToolResponse(BaseModel):
    success: bool
    data: Any
    message: Optional[str] = None

class MemoryEntry(BaseModel):
    id: str
    content: str
    type: str
    tags: List[str]
    timestamp: str
    relevance_score: Optional[float] = None

# Authentication helper
def verify_api_key(authorization: str = Header(None)):
    """Verify API key from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    # For now, we'll use a simple validation - in production you'd want proper key management
    if len(api_key) < 10:  # Basic validation
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

@router.post("/memory/save")
def save_memory_tool(
    request: MCPToolRequest,
    api_key: str = Header(None, alias="Authorization")
) -> MCPToolResponse:
    """Save a memory entry to the DevHelper memory system"""
    try:
        verify_api_key(api_key)
        
        # Parse params
        save_params = MemorySaveParams(**request.params)
        
        # Create memory entry
        memory_entry = {
            "id": f"mem_{datetime.now().timestamp()}",
            "content": save_params.content,
            "type": save_params.type,
            "tags": save_params.tags,
            "timestamp": datetime.now().isoformat(),
            "source": "mcp_client"
        }
        
        # Store in databutton storage
        existing_memories = db.storage.json.get("mcp_memories", default=[])
        existing_memories.append(memory_entry)
        db.storage.json.put("mcp_memories", existing_memories)
        
        return MCPToolResponse(
            success=True,
            data=memory_entry,
            message="Memory saved successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/getContext")
def get_memory_context_tool(
    request: MCPToolRequest,
    api_key: str = Header(None, alias="Authorization")
) -> MCPToolResponse:
    """Get memory context for a task or general context"""
    try:
        verify_api_key(api_key)
        
        # Parse params
        context_params = MemoryContextParams(**request.params)
        
        # Retrieve memories from storage
        memories = db.storage.json.get("mcp_memories", default=[])
        
        # Filter by taskId if provided
        if context_params.taskId:
            filtered_memories = [
                mem for mem in memories 
                if context_params.taskId in mem.get("tags", []) or context_params.taskId in mem.get("content", "")
            ]
        else:
            filtered_memories = memories
        
        # Sort by timestamp (newest first) and limit
        sorted_memories = sorted(
            filtered_memories, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )[:context_params.limit]
        
        return MCPToolResponse(
            success=True,
            data={
                "memories": sorted_memories,
                "total_count": len(filtered_memories)
            },
            message=f"Retrieved {len(sorted_memories)} memory entries"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/search")
def search_memory_tool(
    request: MCPToolRequest,
    api_key: str = Header(None, alias="Authorization")
) -> MCPToolResponse:
    """Search memories by query and types"""
    try:
        verify_api_key(api_key)
        
        # Parse params
        search_params = MemorySearchParams(**request.params)
        
        # Retrieve memories from storage
        memories = db.storage.json.get("mcp_memories", default=[])
        
        # Simple text search (in production, you'd use vector search)
        query_lower = search_params.query.lower()
        matching_memories = []
        
        for memory in memories:
            # Check if memory type matches requested types
            if memory.get("type") not in search_params.types:
                continue
                
            # Check if query matches content or tags
            content_match = query_lower in memory.get("content", "").lower()
            tag_match = any(query_lower in tag.lower() for tag in memory.get("tags", []))
            
            if content_match or tag_match:
                # Add relevance score (simple implementation)
                relevance = 1.0
                if content_match:
                    relevance += 0.5
                if tag_match:
                    relevance += 0.3
                    
                memory_copy = memory.copy()
                memory_copy["relevance_score"] = relevance
                matching_memories.append(memory_copy)
        
        # Sort by relevance score
        matching_memories.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return MCPToolResponse(
            success=True,
            data={
                "memories": matching_memories,
                "total_count": len(matching_memories),
                "query": search_params.query
            },
            message=f"Found {len(matching_memories)} matching memories"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vision/captureScreenshot")
def capture_screenshot_tool(
    request: MCPToolRequest,
    api_key: str = Header(None, alias="Authorization")
) -> MCPToolResponse:
    """Capture and analyze a screenshot (placeholder implementation)"""
    try:
        verify_api_key(api_key)
        
        # Parse params
        screenshot_params = ScreenshotParams(**request.params)
        
        # This is a placeholder - in a real implementation, you'd:
        # 1. Capture screenshot using browser automation
        # 2. Analyze with vision models
        # 3. Return structured analysis
        
        analysis_result = {
            "selector": screenshot_params.selector,
            "analysisType": screenshot_params.analysisType,
            "timestamp": datetime.now().isoformat(),
            "analysis": {
                "elements_detected": [],
                "layout_assessment": "Screenshot analysis not yet implemented",
                "accessibility_issues": [],
                "suggestions": [
                    "Implement browser automation for screenshot capture",
                    "Integrate vision model for analysis"
                ]
            },
            "status": "placeholder"
        }
        
        return MCPToolResponse(
            success=True,
            data=analysis_result,
            message="Screenshot analysis placeholder - implementation needed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check() -> MCPToolResponse:
    """Health check endpoint for the MCP tools API"""
    return MCPToolResponse(
        success=True,
        data={"status": "healthy", "timestamp": datetime.now().isoformat()},
        message="MCP Tools API is running"
    )
