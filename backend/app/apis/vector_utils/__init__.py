from typing import List, Dict, Any, Optional
import numpy as np
import databutton as db
import re
import openai
from datetime import datetime
from fastapi import APIRouter

# Add router to make this a valid API module (expected by the framework)
router = APIRouter()

# OpenAI API client
api_key = db.secrets.get("OPENAI_API_KEY")
if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    client = None

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_vector_store():
    """Get the vector store from storage or create it if it doesn't exist"""
    try:
        return db.storage.json.get("vector_memory_store")
    except FileNotFoundError:
        # Initialize an empty vector store
        initial_store = {
            "vectors": [],
            "metadata": {
                "model": "text-embedding-3-small",
                "dimensions": 1536,
                "count": 0,
                "last_updated": ""
            }
        }
        db.storage.json.put("vector_memory_store", initial_store)
        return initial_store

def save_vector_store(store):
    """Save the vector store to storage"""
    # Update metadata
    store["metadata"]["count"] = len(store["vectors"])
    store["metadata"]["last_updated"] = datetime.now().isoformat()
    
    db.storage.json.put("vector_memory_store", store)

def create_memory_index(vectors: List[Dict[str, Any]], index_name: str = "memory_index"):
    """Create an optimized index for faster memory retrieval"""
    # This is a simplified version - in a real system, you'd use a more sophisticated index
    # But for our purposes, we'll create a simple index structure
    
    # Group vectors by memory type for faster filtering
    index_by_type = {}
    
    for i, vector in enumerate(vectors):
        memory_type = vector.get("memory_type")
        if memory_type not in index_by_type:
            index_by_type[memory_type] = []
        
        # Store position in the original vectors list for retrieval
        index_by_type[memory_type].append(i)
    
    # Create a simple index structure
    index = {
        "by_type": index_by_type,
        "created_at": datetime.now().isoformat(),
        "vector_count": len(vectors)
    }
    
    # Save the index
    db.storage.json.put(f"{sanitize_storage_key(index_name)}", index)
    
    return index

def get_memory_index(index_name: str = "memory_index"):
    """Get the memory index"""
    try:
        return db.storage.json.get(sanitize_storage_key(index_name))
    except FileNotFoundError:
        # No index exists yet
        return None

def generate_optimized_embeddings(text: str, model: str = "text-embedding-3-small"):
    """Generate optimized embeddings for text"""
    if not client:
        raise ValueError("OpenAI API key not configured")
    
    try:
        # Preprocess text to improve embedding quality
        # Remove extra whitespace and normalize
        processed_text = " ".join(text.split())
        
        # Use OpenAI API to generate embeddings
        response = client.embeddings.create(
            input=processed_text,
            model=model
        )
        
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None

def search_with_relevance_scoring(query_text: str = None, query_embedding: List[float] = None, vectors: List[Dict[str, Any]] = None, 
                                  limit: int = 5, threshold: float = 0.7, 
                                  memory_types: Optional[List[str]] = None):
    """Search with advanced relevance scoring
    
    This function accepts either a query text or a pre-computed embedding.
    If query_text is provided but query_embedding is not, it will generate the embedding.
    """
    if not vectors:
        store = get_vector_store()
        vectors = store.get("vectors", [])
    
    if not vectors:
        return [], None
    
    # Generate query embedding if needed
    if not query_embedding and query_text:
        query_embedding = generate_optimized_embeddings(query_text)
    
    if not query_embedding:
        raise ValueError("Must provide either query_text or query_embedding")
    
    # Filter by memory type if specified
    if memory_types:
        filtered_vectors = [v for v in vectors if v["memory_type"] in memory_types]
    else:
        filtered_vectors = vectors
    
    # Calculate similarity scores
    results = []
    for vector in filtered_vectors:
        # Get embedding from vector
        vector_embedding = vector.get("embedding")
        if not vector_embedding:
            continue
        
        # Calculate cosine similarity
        similarity = cosine_similarity(query_embedding, vector_embedding)
        
        # Calculate recency score (more recent = higher score)
        timestamp = vector.get("metadata", {}).get("timestamp")
        recency_score = 0.0
        if timestamp:
            try:
                # Parse timestamp
                dt = datetime.fromisoformat(timestamp)
                # Calculate how recent (0-1 scale, newer is closer to 1)
                now = datetime.now()
                age_days = (now - dt).total_seconds() / (60 * 60 * 24)  # Convert to days
                recency_score = max(0, 1 - min(age_days / 30, 1))  # Linear decay over 30 days
            except Exception:
                pass
        
        # Calculate relevance based on memory type
        # This allows us to prioritize certain memory types for certain queries
        type_relevance = 1.0
        memory_type = vector.get("memory_type", "")
        
        # Keywords in content boost relevance
        content_boost = 0.0
        if query_text and vector.get("content"):
            # Simple keyword matching for boost
            content = vector["content"].lower()
            keywords = [k.lower() for k in query_text.split() if len(k) > 3]
            matches = sum(1 for k in keywords if k in content)
            content_boost = min(matches * 0.05, 0.25)  # Up to 0.25 boost for keyword matches
        
        # Combine scores (similarity is most important)
        combined_score = (similarity * 0.7) + (recency_score * 0.1) + (type_relevance * 0.05) + content_boost
        
        # Add to results if above threshold
        if similarity >= threshold:
            results.append({
                "id": vector.get("id", "unknown"),
                "memory_type": memory_type,
                "content": vector.get("content", ""),
                "similarity": float(similarity),
                "relevance_score": float(combined_score),
                "metadata": vector.get("metadata", {}),
                "memory_id": vector.get("memory_id", vector.get("id", "unknown"))
            })
    
    # Sort by combined relevance score (descending)
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    # Apply limit
    results = results[:limit]
    
    return results, query_embedding
