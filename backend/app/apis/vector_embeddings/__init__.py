from fastapi import APIRouter, HTTPException, Depends
from app.auth import AuthorizedUser
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import databutton as db
import numpy as np
import openai
from datetime import datetime
from app.libs.memory_service import MemoryType, MemoryFrame
from app.apis.vector_utils import (
    sanitize_storage_key, cosine_similarity, get_vector_store, save_vector_store,
    create_memory_index, get_memory_index, generate_optimized_embeddings,
    search_with_relevance_scoring
)

router = APIRouter(prefix="/vector-embeddings")

# OpenAI API client
api_key = db.secrets.get("OPENAI_API_KEY")
if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    client = None

# Models for embedding generation and search
class TextEmbeddingRequest(BaseModel):
    text: str = Field(..., description="Text to generate embeddings for")
    model: str = Field("text-embedding-3-small", description="Embedding model to use")

class EmbeddingResponse(BaseModel):
    embedding: List[float] = Field(..., description="Vector embedding of the input text")
    model: str = Field(..., description="Model used to generate the embedding")
    dimensions: int = Field(..., description="Number of dimensions in the embedding")
    text_hash: str = Field(..., description="Hash of the input text for reference")

# Forward declare the index_memory function for importing in agent_memory

class VectorMemory(BaseModel):
    id: str = Field(..., description="Unique identifier for this memory")
    memory_type: MemoryType = Field(..., description="Type of memory (state, task, etc)")
    embedding: List[float] = Field(..., description="Vector embedding of the memory content")
    content: str = Field(..., description="Text content that was embedded")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    memory_id: str = Field(..., description="Reference to the original memory ID")

class VectorSearchRequest(BaseModel):
    query: str = Field(..., description="Query text to search for similar memories")
    memory_types: Optional[List[MemoryType]] = Field(None, description="Types of memories to search")
    limit: int = Field(5, description="Maximum number of results to return")
    threshold: float = Field(0.7, description="Similarity threshold (0-1)")

class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Search results with similarity scores")
    query_embedding: Optional[List[float]] = Field(None, description="Embedding of the query text")

@router.post("/embed", response_model=EmbeddingResponse)
async def generate_embedding(request: TextEmbeddingRequest) -> EmbeddingResponse:
    """Generate a vector embedding for the input text"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        # Generate optimized embedding
        embedding = generate_optimized_embeddings(request.text, request.model)
        if not embedding:
            raise ValueError("Failed to generate embedding")
        
        # Generate text hash
        import hashlib
        text_hash = hashlib.md5(request.text.encode()).hexdigest()
        
        return EmbeddingResponse(
            embedding=embedding,
            model=request.model,
            dimensions=len(embedding),
            text_hash=text_hash
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")



@router.post("/index-memory")
async def index_memory(memory_frame: MemoryFrame) -> Dict[str, Any]:
    """Index a memory item in the vector store"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        # Extract text content from memory based on type
        content = ""
        
        try:
            # Extract content based on memory type with better error handling
            if memory_frame.memory_type == MemoryType.STATE:
                content = f"Current state: {memory_frame.payload}"
            elif memory_frame.memory_type == MemoryType.TASK:
                task_data = memory_frame.payload
                content = f"Task: {task_data.get('task_title', '')}. Description: {task_data.get('task_description', '')}. Status: {task_data.get('task_status', '')}"
            elif memory_frame.memory_type == MemoryType.COMMAND:
                cmd_data = memory_frame.payload
                content = f"Command: {cmd_data.get('action', '')} on {cmd_data.get('target', '')}. Result: {cmd_data.get('result', '')}"
            elif memory_frame.memory_type == MemoryType.KNOWLEDGE:
                knowledge_data = memory_frame.payload
                if not isinstance(knowledge_data, dict):
                    knowledge_data = {}
                content = f"Knowledge: {knowledge_data.get('knowledge_type', '')}. Content: {knowledge_data.get('knowledge_content', '')}"
            elif memory_frame.memory_type == MemoryType.VISUAL:
                visual_data = memory_frame.payload
                content = f"Visual: {visual_data.get('page_url', '')}. Description: {visual_data.get('screenshot_description', '')}"
            else:
                content = str(memory_frame.payload)
        except Exception as content_error:
            print(f"Error extracting content from {memory_frame.memory_type} memory: {content_error}")
            # Provide fallback content with error info
            content = f"Memory of type {memory_frame.memory_type}. Error processing content."
        
        # Generate embedding
        embedding_request = TextEmbeddingRequest(text=content)
        embedding_response = await generate_embedding(embedding_request)
        
        # Create vector memory
        vector_memory = VectorMemory(
            id=f"vm_{memory_frame.id}",
            memory_type=memory_frame.memory_type,
            embedding=embedding_response.embedding,
            content=content,
            metadata={
                "timestamp": memory_frame.timestamp,
                "user_id": memory_frame.user_id,
                "project_id": memory_frame.project_id,
                "tags": memory_frame.tags if hasattr(memory_frame, 'tags') and memory_frame.tags else []
            },
            memory_id=memory_frame.id
        )
        
        # Add to vector store
        store = get_vector_store()
        store["vectors"].append(vector_memory.dict())
        save_vector_store(store)
        
        return {"status": "success", "id": vector_memory.id}
    except Exception as e:
        error_msg = f"Error indexing memory of type {memory_frame.memory_type}: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/search", response_model=VectorSearchResponse)
async def search_similar_memories(request: VectorSearchRequest) -> VectorSearchResponse:
    """Search for memories similar to the query text using vector embeddings"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        # Generate query embedding
        query_embedding = generate_optimized_embeddings(request.query)
        if not query_embedding:
            raise ValueError("Failed to generate query embedding")
        
        # Get vector store
        store = get_vector_store()
        vectors = store.get("vectors", [])
        
        # Search with relevance scoring
        results, _ = search_with_relevance_scoring(
            query_text=request.query,
            vectors=vectors,
            memory_types=request.memory_types,
            threshold=request.threshold,
            limit=request.limit
        )
        
        return VectorSearchResponse(
            results=results,
            query_embedding=query_embedding
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching memories: {str(e)}")

@router.post("/generate-rag-context")
async def generate_smart_rag_context(request: dict) -> dict:
    """Generate a smart RAG context for enhancing AI responses
    
    This endpoint uses vector search to find the most relevant memories based on a query
    and formats them into a context string for use in RAG systems.
    """
    try:
        query = request.get("query", "")
        memory_types = request.get("memory_types")
        limit = request.get("limit", 5)
        threshold = request.get("threshold", 0.7)
        advanced_features = request.get("advanced_features", True)
        include_embeddings = request.get("include_embeddings", False)
        
        if not query:
            return {"context": "", "error": "No query provided", "status": "error"}
        
        # Convert memory_types to enum values if provided as strings
        typed_memory_types = None
        if memory_types:
            typed_memory_types = []
            for memory_type in memory_types:
                if isinstance(memory_type, str) and memory_type.upper() in MemoryType.__members__:
                    typed_memory_types.append(MemoryType[memory_type.upper()])
                elif isinstance(memory_type, MemoryType):
                    typed_memory_types.append(memory_type)
        
        # Search for relevant memories
        search_request = VectorSearchRequest(
            query=query,
            memory_types=typed_memory_types,
            limit=limit,
            threshold=threshold
        )
        
        search_response = await search_similar_memories(search_request)
        
        # Format the context for more advanced RAG
        context_string = ""
        
        # Group results by memory type for better organization
        memory_types_present = set(r["memory_type"] for r in search_response.results)
        
        if not search_response.results:
            context_string = "### NO RELEVANT MEMORIES FOUND ###\n\nNo memories match your query with sufficient relevance."
        else:
            context_string = "### RELEVANT MEMORY CONTEXT ###\n\n"
            
            # Add a summary section first
            memory_count = len(search_response.results)
            types_count = len(memory_types_present)
            avg_relevance = sum(r["similarity"] for r in search_response.results) / memory_count if memory_count > 0 else 0
            context_string += f"Found {memory_count} relevant memories across {types_count} categories "
            context_string += f"with average relevance of {int(avg_relevance * 100)}%.\n\n"
            
            # Add memories by type for better organization
            for memory_type in memory_types_present:
                type_memories = [r for r in search_response.results if r["memory_type"] == memory_type]
                if not type_memories:
                    continue
                
                # Add section for this memory type
                context_string += f"## {memory_type.upper()} MEMORIES ({len(type_memories)})\n\n"
                
                for memory in type_memories:
                    # Format with relevance scoring
                    relevance = int(memory["similarity"] * 100)
                    context_string += f"• **{relevance}% relevant**: {memory['content']}\n"
                    
                    # Add metadata if advanced features enabled
                    if advanced_features and memory.get("metadata"):
                        metadata = memory["metadata"]
                        meta_parts = []
                        
                        if "timestamp" in metadata:
                            try:
                                timestamp = datetime.fromisoformat(metadata["timestamp"])
                                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                                meta_parts.append(f"Time: {formatted_time}")
                            except:
                                pass
                                
                        if "tags" in metadata and metadata["tags"]:
                            meta_parts.append(f"Tags: {', '.join(metadata['tags'])}")
                            
                        if meta_parts:
                            context_string += f"  *({' | '.join(meta_parts)})*\n"
                    
                    context_string += "\n"
                
                context_string += "\n"
            
            # Add a divider
            context_string += "### END MEMORY CONTEXT ###"
        
        response = {
            "context": context_string,
            "memories_used": len(search_response.results),
            "status": "success",
            "memories": search_response.results
        }
        
        # Include embeddings if requested
        if include_embeddings and search_response.query_embedding:
            response["query_embedding"] = search_response.query_embedding
        
        return response
    except Exception as e:
        return {"context": "", "error": str(e), "status": "error"}

@router.get("/store")
async def get_vector_store_data() -> Dict[str, Any]:
    """Get the current vector store data"""
    try:
        # Get vector store
        store = get_vector_store()
        return store
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting vector store: {str(e)}")

@router.post("/rebuild")
async def rebuild_vector_index() -> Dict[str, Any]:
    """Rebuild the vector index from all stored memories"""
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        # Clear existing vector store
        store = {
            "vectors": [],
            "metadata": {
                "model": "text-embedding-3-small",
                "dimensions": 1536,
                "count": 0,
                "last_updated": db.utils.now().isoformat()
            }
        }
        
        # Get all memories from storage
        try:
            all_memories = db.storage.json.get("agent_memory")
        except FileNotFoundError:
            # No memories yet
            save_vector_store(store)
            return {"status": "success", "count": 0, "message": "No memories found to index"}
        
        if not all_memories or not isinstance(all_memories, list):
            save_vector_store(store)
            return {"status": "success", "count": 0, "message": "No valid memories found to index"}
        
        # Convert to MemoryFrame objects and index each one
        count = 0
        for memory_data in all_memories:
            try:
                memory_frame = MemoryFrame(**memory_data)
                await index_memory(memory_frame)
                count += 1
            except Exception as e:
                print(f"Error indexing memory: {e}")
                continue
        
        # After indexing all memories, create an optimized index
        store = get_vector_store()
        create_memory_index(store["vectors"])
        
        return {
            "status": "success", 
            "count": count, 
            "message": f"Successfully indexed {count} memories and created optimized index"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding vector index: {str(e)}")
