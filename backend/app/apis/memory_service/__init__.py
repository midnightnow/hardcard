from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.libs.memory_service import MemoryService, MemoryFrame, MemoryType

router = APIRouter()
memory_service = MemoryService()

class SearchQuery(BaseModel):
    agent_id: str
    query: str
    limit: Optional[int] = 5

class MemoryContextRequest(BaseModel):
    agent_id: str
    context_type: str = "all"
    limit: Optional[int] = 10

class EnhancedMemoryContextRequest(BaseModel):
    query: str

@router.post("/save-memory-frame", response_model=Dict[str, Any])
async def save_memory_frame_endpoint(memory_frame: MemoryFrame):
    """
    Saves a memory frame to the memory service.
    """
    new_memory = await memory_service.create_memory(memory_frame)
    return {"status": "success", "memory_id": new_memory.id}

@router.post("/get-memories-for-context", response_model=List[MemoryFrame])
def get_memories_for_context_endpoint(request: MemoryContextRequest):
    """
    Retrieves memories for a given agent and context type.
    """
    # This function needs to be implemented in the MemoryService class
    return []

@router.post("/get-enhanced-memory-context", response_model=Dict[str, Any])
def get_enhanced_memory_context_endpoint(request: EnhancedMemoryContextRequest):
    """
    Retrieves an enhanced memory context using vector search.
    """
    # This function needs to be implemented in the MemoryService class
    return {}

@router.post("/search-agent-memories", response_model=List[Dict[str, Any]])
def search_agent_memories_endpoint(query: SearchQuery):
    """
    Searches agent memories based on a query.
    """
    # This function needs to be implemented in the MemoryService class
    return []
