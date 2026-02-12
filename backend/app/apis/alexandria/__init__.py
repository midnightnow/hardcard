from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import databutton as db
from datetime import datetime
import uuid
import json
from app.auth import AuthorizedUser

router = APIRouter(prefix="/alexandria")

# ---- Models ----

class Contributor(BaseModel):
    id: str
    name: str
    expertise: List[str] = []
    organization: Optional[str] = None

class ContentVersion(BaseModel):
    version_id: str
    content: str
    contributor_id: str
    timestamp: str
    change_description: Optional[str] = None

class MediaItem(BaseModel):
    id: str
    type: str  # image, video, audio, 3d-model, interactive
    url: str
    title: str
    description: Optional[str] = None
    contributor_id: Optional[str] = None
    timestamp: str

class Citation(BaseModel):
    id: str
    source: str
    authors: Optional[List[str]] = None
    year: Optional[int] = None
    url: Optional[str] = None
    doi: Optional[str] = None

class KnowledgeEntry(BaseModel):
    id: str
    title: str
    category: str
    subcategory: Optional[str] = None
    tags: List[str] = []
    current_version_id: str
    versions: List[ContentVersion] = []
    media: List[MediaItem] = []
    citations: List[Citation] = []
    contributors: List[str] = []  # Contributor IDs
    created_at: str
    updated_at: str
    curation_status: str = "pending"  # pending, reviewed, featured
    view_count: int = 0
    language: str = "en"

class KnowledgeEntryCreate(BaseModel):
    title: str = Field(..., description="Title of the knowledge entry")
    category: str = Field(..., description="Primary category for classification")
    subcategory: Optional[str] = Field(None, description="Optional subcategory for finer classification")
    tags: List[str] = Field([], description="Tags for improved searchability")
    content: str = Field(..., description="The main content of the knowledge entry")
    media: List[Dict[str, Any]] = Field([], description="Media items to include")
    citations: List[Dict[str, Any]] = Field([], description="Citations and references")
    change_description: Optional[str] = Field(None, description="Description of the initial version")
    language: str = Field("en", description="Language code")

class KnowledgeEntryUpdateVersion(BaseModel):
    content: str = Field(..., description="Updated content for the knowledge entry")
    change_description: str = Field(..., description="Description of changes made in this version")

class KnowledgeEntryUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = None

class CategoryModel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    icon: Optional[str] = None

class SearchResult(BaseModel):
    entries: List[KnowledgeEntry]
    total: int
    page: int
    page_size: int

# ---- Helper Functions ----

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_entries():
    """Get all knowledge entries"""
    try:
        entries = db.storage.json.get("alexandria_entries", default={})
        return entries
    except Exception as e:
        print(f"Error getting entries: {e}")
        return {}

def save_entries(entries):
    """Save all knowledge entries"""
    db.storage.json.put("alexandria_entries", entries)

def get_categories():
    """Get all categories"""
    try:
        categories = db.storage.json.get("alexandria_categories", default={})
        return categories
    except Exception as e:
        print(f"Error getting categories: {e}")
        return {}

def save_categories(categories):
    """Save all categories"""
    db.storage.json.put("alexandria_categories", categories)

# ---- Endpoints ----

@router.get("/entries", response_model=List[KnowledgeEntry])
def list_entries(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """List knowledge entries with optional filtering"""
    entries = get_entries()
    
    # Apply filters
    filtered_entries = []
    for entry_id, entry in entries.items():
        if category and entry["category"] != category:
            continue
        if subcategory and entry.get("subcategory") != subcategory:
            continue
        if tag and tag not in entry.get("tags", []):
            continue
        
        # Add ID to entry
        entry_with_id = {**entry, "id": entry_id}
        filtered_entries.append(entry_with_id)
    
    # Sort by updated_at (newest first)
    filtered_entries.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    # Apply pagination
    paginated_entries = filtered_entries[offset:offset+limit]
    
    return paginated_entries

@router.get("/entries/{entry_id}", response_model=KnowledgeEntry)
def get_entry(entry_id: str = Path(..., description="The ID of the knowledge entry")):
    """Get a specific knowledge entry by ID"""
    entries = get_entries()
    if entry_id not in entries:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Increment view count
    entries[entry_id]["view_count"] = entries[entry_id].get("view_count", 0) + 1
    save_entries(entries)
    
    # Add ID to entry
    entry = {**entries[entry_id], "id": entry_id}
    return entry

@router.post("/entries", response_model=KnowledgeEntry)
def create_entry(entry: KnowledgeEntryCreate, user: AuthorizedUser):
    """Create a new knowledge entry"""
    entries = get_entries()
    
    # Generate a new ID for the entry
    entry_id = str(uuid.uuid4())
    version_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    # Create the initial version
    initial_version = {
        "version_id": version_id,
        "content": entry.content,
        "contributor_id": user.sub,
        "timestamp": now,
        "change_description": entry.change_description or "Initial version"
    }
    
    # Create the entry
    new_entry = {
        "title": entry.title,
        "category": entry.category,
        "subcategory": entry.subcategory,
        "tags": entry.tags,
        "current_version_id": version_id,
        "versions": [initial_version],
        "media": entry.media,
        "citations": entry.citations,
        "contributors": [user.sub],
        "created_at": now,
        "updated_at": now,
        "curation_status": "pending",
        "view_count": 0,
        "language": entry.language
    }
    
    entries[entry_id] = new_entry
    save_entries(entries)
    
    # Add ID to the returned entry
    return {**new_entry, "id": entry_id}

@router.post("/entries/{entry_id}/versions", response_model=KnowledgeEntry)
def add_entry_version(
    entry_update: KnowledgeEntryUpdateVersion, 
    user: AuthorizedUser,
    entry_id: str = Path(..., description="The ID of the knowledge entry")
):
    """Add a new version to an existing knowledge entry"""
    entries = get_entries()
    if entry_id not in entries:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    entry = entries[entry_id]
    now = datetime.utcnow().isoformat()
    version_id = str(uuid.uuid4())
    
    # Create the new version
    new_version = {
        "version_id": version_id,
        "content": entry_update.content,
        "contributor_id": user.sub,
        "timestamp": now,
        "change_description": entry_update.change_description
    }
    
    # Add the new version to the entry
    entry["versions"].append(new_version)
    entry["current_version_id"] = version_id
    entry["updated_at"] = now
    
    # Add contributor if not already in the list
    if user.sub not in entry["contributors"]:
        entry["contributors"].append(user.sub)
    
    entries[entry_id] = entry
    save_entries(entries)
    
    # Add ID to the returned entry
    return {**entry, "id": entry_id}

@router.put("/entries/{entry_id}", response_model=KnowledgeEntry)
def update_entry(
    entry_update: KnowledgeEntryUpdate, 
    user: AuthorizedUser,
    entry_id: str = Path(..., description="The ID of the knowledge entry")
):
    """Update metadata for an existing knowledge entry"""
    entries = get_entries()
    if entry_id not in entries:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    entry = entries[entry_id]
    now = datetime.utcnow().isoformat()
    
    # Update fields if provided
    if entry_update.title is not None:
        entry["title"] = entry_update.title
    if entry_update.category is not None:
        entry["category"] = entry_update.category
    if entry_update.subcategory is not None:
        entry["subcategory"] = entry_update.subcategory
    if entry_update.tags is not None:
        entry["tags"] = entry_update.tags
    if entry_update.language is not None:
        entry["language"] = entry_update.language
    
    entry["updated_at"] = now
    
    # Add contributor if not already in the list
    if user.sub not in entry["contributors"]:
        entry["contributors"].append(user.sub)
    
    entries[entry_id] = entry
    save_entries(entries)
    
    # Add ID to the returned entry
    return {**entry, "id": entry_id}

@router.delete("/entries/{entry_id}")
def delete_entry(
    user: AuthorizedUser,
    entry_id: str = Path(..., description="The ID of the knowledge entry")
):
    """Delete a knowledge entry"""
    entries = get_entries()
    if entry_id not in entries:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Delete the entry
    del entries[entry_id]
    save_entries(entries)
    
    return {"message": f"Entry {entry_id} deleted successfully"}

@router.get("/categories", response_model=List[CategoryModel])
def list_categories():
    """List all categories"""
    categories = get_categories()
    
    # Convert dict to list with IDs, filtering out empty string IDs
    category_list = [
        {**category, "id": category_id}
        for category_id, category in categories.items()
        if category_id  # Ensures category_id is not an empty string
    ]
    
    return category_list

@router.post("/categories", response_model=CategoryModel)
def create_category(category: CategoryModel, user: AuthorizedUser):
    """Create a new category"""
    categories = get_categories()
    
    # Generate a new ID if not provided or if the provided ID is an empty string
    category_id = category.id if category.id else str(uuid.uuid4())
    
    # Create the category
    new_category = {
        "name": category.name,
        "description": category.description,
        "parent_id": category.parent_id,
        "icon": category.icon
    }
    
    categories[category_id] = new_category
    save_categories(categories)
    
    # Add ID to the returned category
    return {**new_category, "id": category_id}

@router.get("/search", response_model=SearchResult)
def search_entries(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Search for knowledge entries"""
    entries = get_entries()
    query = query.lower()
    
    # Simple search implementation
    matching_entries = []
    for entry_id, entry in entries.items():
        # Check if query matches title, content or tags
        title_match = query in entry["title"].lower()
        
        # Check content in current version
        content_match = False
        for version in entry["versions"]:
            if version["version_id"] == entry["current_version_id"]:
                content_match = query in version["content"].lower()
                break
        
        tag_match = any(query in tag.lower() for tag in entry.get("tags", []))
        
        # Filter by category if specified
        category_match = True
        if category:
            category_match = entry["category"] == category
        
        if (title_match or content_match or tag_match) and category_match:
            # Add ID to entry
            entry_with_id = {**entry, "id": entry_id}
            matching_entries.append(entry_with_id)
    
    # Sort by relevance (for now, just updated_at)
    matching_entries.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    # Calculate pagination
    total = len(matching_entries)
    offset = (page - 1) * page_size
    paginated_entries = matching_entries[offset:offset+page_size]
    
    return {
        "entries": paginated_entries,
        "total": total,
        "page": page,
        "page_size": page_size
    }

@router.get("/stats")
def get_stats():
    """Get statistics about the knowledge repository"""
    entries = get_entries()
    categories = get_categories()
    
    # Count entries by category
    entries_by_category = {}
    for entry in entries.values():
        category = entry["category"]
        if category in entries_by_category:
            entries_by_category[category] += 1
        else:
            entries_by_category[category] = 1
    
    # Count total contributors
    all_contributors = set()
    for entry in entries.values():
        all_contributors.update(entry.get("contributors", []))
    
    # Get top viewed entries
    sorted_entries = sorted(
        [{"id": entry_id, **entry} for entry_id, entry in entries.items()],
        key=lambda x: x.get("view_count", 0),
        reverse=True
    )[:5]  # Top 5
    
    top_viewed = [
        {"id": entry["id"], "title": entry["title"], "view_count": entry.get("view_count", 0)}
        for entry in sorted_entries
    ]
    
    return {
        "total_entries": len(entries),
        "total_categories": len(categories),
        "total_contributors": len(all_contributors),
        "entries_by_category": entries_by_category,
        "top_viewed": top_viewed
    }