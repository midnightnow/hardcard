from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import databutton as db
from datetime import datetime
import uuid
import json
from app.auth import AuthorizedUser
import openai

router = APIRouter(prefix="/alexandria-ai")

# Initialize OpenAI client
openai_api_key = db.secrets.get("OPENAI_API_KEY")
openai_client = openai.OpenAI(api_key=openai_api_key)

# ---- Models ----

class GenerateContentRequest(BaseModel):
    topic: str = Field(..., description="The topic to generate content about")
    category: str = Field(..., description="Category for classification")
    depth: str = Field("standard", description="Depth of content: 'brief', 'standard', or 'comprehensive'")
    tone: str = Field("academic", description="Tone of content: 'conversational', 'academic', or 'technical'")
    audience: str = Field("general", description="Target audience: 'general', 'student', 'expert'")
    include_citations: bool = Field(True, description="Whether to include citations")

class ContentGenerationResponse(BaseModel):
    title: str
    content: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = []
    citations: List[Dict[str, Any]] = []

class KnowledgeEntryEnhanceRequest(BaseModel):
    entry_id: str = Field(..., description="ID of the knowledge entry to enhance")
    enhancement_type: str = Field(..., description="Type of enhancement: 'clarity', 'citations', 'connections', 'visuals'")

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's natural language query")
    context_ids: List[str] = Field([], description="IDs of knowledge entries to use as context")

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    related_entries: List[Dict[str, Any]] = []

# ---- Helper Functions ----

def get_entries_from_alexandria():
    """Get entries from the Alexandria API"""
    try:
        entries = db.storage.json.get("alexandria_entries", default={})
        return entries
    except Exception as e:
        print(f"Error getting entries: {e}")
        return {}

def get_entry_by_id(entry_id):
    """Get a specific entry by ID"""
    entries = get_entries_from_alexandria()
    if entry_id not in entries:
        return None
    return {**entries[entry_id], "id": entry_id}

def format_content_for_ai(entry):
    """Format entry content for AI processing"""
    # Find the current version
    current_content = ""
    for version in entry.get("versions", []):
        if version.get("version_id") == entry.get("current_version_id"):
            current_content = version.get("content", "")
            break
    
    return {
        "id": entry.get("id"),
        "title": entry.get("title"),
        "category": entry.get("category"),
        "subcategory": entry.get("subcategory"),
        "tags": entry.get("tags", []),
        "content": current_content
    }

# ---- Endpoints ----

@router.post("/generate", response_model=ContentGenerationResponse)
def generate_content(request: GenerateContentRequest, user: AuthorizedUser):
    """Generate AI content for a knowledge entry"""
    try:
        # Construct the prompt based on the request parameters
        prompt = f"""Generate educational content about '{request.topic}' for the Alexandria digital library.
        
        Parameters:
        - Category: {request.category}
        - Depth: {request.depth}
        - Tone: {request.tone}
        - Audience: {request.audience}
        - Include citations: {request.include_citations}
        
        Format your response as follows:
        1. A concise, engaging title
        2. Well-structured content with appropriate headings
        3. If requested, include 3-5 scholarly citations in a consistent format
        4. Suggest 5-10 relevant tags for classification
        
        The content should be factually accurate, well-organized, and appropriate for the specified audience.
        """
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Use appropriate model
            messages=[
                {"role": "system", "content": "You are a knowledgeable academic researcher creating content for the Library of Alexandria digital knowledge repository. Your goal is to create accurate, well-structured educational content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the content from the response
        generated_text = response.choices[0].message.content
        
        # Parse the generated content
        # This is a simple parser, could be more sophisticated in production
        lines = generated_text.strip().split("\n")
        title = lines[0].strip().replace("#", "").strip()
        
        # Extract tags from the content if they exist
        tags = []
        content = generated_text
        for line in lines:
            if "tags:" in line.lower() or "keywords:" in line.lower():
                tags_part = line.split(":", 1)[1].strip()
                tags = [tag.strip().lower() for tag in tags_part.split(",")]
                # Remove tags from content
                content = content.replace(line, "")
                break
        
        # Simple citation extraction
        citations = []
        citation_markers = ["references:", "citations:", "bibliography:"]
        for marker in citation_markers:
            if marker in content.lower():
                parts = content.lower().split(marker)
                if len(parts) > 1:
                    citation_text = parts[1].strip()
                    citation_lines = citation_text.split("\n")
                    for i, line in enumerate(citation_lines):
                        if line.strip():
                            citations.append({
                                "id": str(uuid.uuid4()),
                                "source": line.strip(),
                                "url": None
                            })
                    # Remove citations from content
                    content = content.lower().split(marker)[0]
                    break
        
        return {
            "title": title,
            "content": content.strip(),
            "category": request.category,
            "subcategory": None,  # Could be inferred from content in a more advanced implementation
            "tags": tags,
            "citations": citations
        }
    
    except Exception as e:
        print(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

@router.post("/enhance", response_model=Dict[str, Any])
def enhance_entry(request: KnowledgeEntryEnhanceRequest, user: AuthorizedUser):
    """Enhance an existing knowledge entry using AI"""
    # Get the entry
    entry = get_entry_by_id(request.entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Format entry for AI processing
    formatted_entry = format_content_for_ai(entry)
    
    try:
        # Construct the prompt based on the enhancement type
        prompt = f"""Enhance the following knowledge entry for the Alexandria digital library.
        
        Original Entry:
        Title: {formatted_entry['title']}
        Category: {formatted_entry['category']}
        Tags: {', '.join(formatted_entry['tags'])}
        
        Content:
        {formatted_entry['content']}
        
        Enhancement Type: {request.enhancement_type}
        
        """
        
        # Add specific instructions based on enhancement type
        if request.enhancement_type == "clarity":
            prompt += "Improve the clarity and readability while maintaining accuracy. Restructure if needed."
        elif request.enhancement_type == "citations":
            prompt += "Add or improve citations to support the content. Format them consistently."
        elif request.enhancement_type == "connections":
            prompt += "Suggest connections to related topics that would be valuable to link to this entry."
        elif request.enhancement_type == "visuals":
            prompt += "Suggest diagrams, charts, or other visual elements that would enhance understanding."
        else:
            raise HTTPException(status_code=400, detail="Invalid enhancement type")
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a knowledgeable academic editor improving content for the Library of Alexandria digital knowledge repository."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the enhanced content
        enhanced_content = response.choices[0].message.content
        
        return {
            "original_entry_id": request.entry_id,
            "enhancement_type": request.enhancement_type,
            "enhanced_content": enhanced_content,
            "instructions": "Review this AI-enhanced content before applying it to your knowledge entry."
        }
    
    except Exception as e:
        print(f"Error enhancing entry: {e}")
        raise HTTPException(status_code=500, detail=f"Error enhancing entry: {str(e)}")

@router.post("/query", response_model=QueryResponse)
def query_knowledge(request: QueryRequest, user: AuthorizedUser):
    """Query the knowledge base using natural language"""
    try:
        # Get relevant entries for context
        context = []
        
        # If specific context entries are provided, use those
        if request.context_ids:
            for entry_id in request.context_ids:
                entry = get_entry_by_id(entry_id)
                if entry:
                    context.append(format_content_for_ai(entry))
        
        # If no context is provided, perform a simple search to find relevant entries
        # This could be replaced with a more sophisticated vector search in production
        else:
            entries = get_entries_from_alexandria()
            query_terms = request.query.lower().split()
            
            for entry_id, entry in entries.items():
                entry_with_id = {**entry, "id": entry_id}
                
                # Check if query terms appear in title or content
                title = entry.get("title", "").lower()
                
                # Get content from current version
                content = ""
                for version in entry.get("versions", []):
                    if version.get("version_id") == entry.get("current_version_id"):
                        content = version.get("content", "").lower()
                        break
                
                match_score = 0
                for term in query_terms:
                    if term in title:
                        match_score += 2  # Higher weight for title matches
                    if term in content:
                        match_score += 1
                
                if match_score > 0:
                    context.append({
                        "id": entry_id,
                        "title": entry.get("title"),
                        "content": content,
                        "relevance": match_score
                    })
            
            # Sort by relevance and limit to top 3
            context.sort(key=lambda x: x.get("relevance", 0), reverse=True)
            context = context[:3]
        
        # Construct the context string for the AI
        context_str = ""
        sources = []
        for idx, entry in enumerate(context):
            context_str += f"\n[{idx+1}] {entry['title']}:\n{entry['content'][:500]}...\n"
            sources.append({
                "id": entry.get("id"),
                "title": entry.get("title")
            })
        
        # Construct the prompt
        prompt = f"""Answer the following question based on the provided knowledge entries.
        
        Knowledge Entries:
        {context_str}
        
        Question: {request.query}
        
        Provide a clear, accurate answer. If the information in the knowledge entries is insufficient, 
        say so rather than making up information. Cite sources using [1], [2], etc.
        """
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing answers based on the Library of Alexandria digital knowledge repository."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        # Extract the answer
        answer = response.choices[0].message.content
        
        # Find related entries beyond those used as sources
        related_entries = []
        entries = get_entries_from_alexandria()
        
        # Get IDs of entries already used as sources
        source_ids = [source["id"] for source in sources]
        
        # Find other potentially related entries
        for entry_id, entry in entries.items():
            if entry_id not in source_ids:  # Skip entries already used as sources
                # Simple check if the entry might be related
                title = entry.get("title", "").lower()
                tags = [tag.lower() for tag in entry.get("tags", [])]
                
                # Check if any query terms appear in title or tags
                for term in query_terms:
                    if term in title or any(term in tag for tag in tags):
                        related_entries.append({
                            "id": entry_id,
                            "title": entry.get("title")
                        })
                        break
        
        # Limit to top 3 related entries
        related_entries = related_entries[:3]
        
        return {
            "answer": answer,
            "sources": sources,
            "related_entries": related_entries
        }
    
    except Exception as e:
        print(f"Error querying knowledge: {e}")
        raise HTTPException(status_code=500, detail=f"Error querying knowledge: {str(e)}")