from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import databutton as db
import json
import re
import datetime
from enum import Enum

router = APIRouter(prefix="/content-dao")

# Helper function for storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Enum for content types
class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CONCEPT = "concept"

# Enum for content status
class ContentStatus(str, Enum):
    GENERATED = "generated"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# Models
class ContentMetrics(BaseModel):
    views: int = Field(default=0)
    engagement_rate: float = Field(default=0.0)
    revenue_generated: float = Field(default=0.0)
    
class ContentItem(BaseModel):
    id: str = Field(..., description="Unique identifier for the content item")
    dao_id: str = Field(..., description="ID of the content DAO that created this item")
    title: str = Field(..., description="Title of the content")
    description: str = Field(..., description="Description of the content")
    content_type: ContentType = Field(..., description="Type of content (text, image, etc)")
    created_at: str = Field(..., description="Creation timestamp")
    status: ContentStatus = Field(default=ContentStatus.GENERATED)
    metrics: ContentMetrics = Field(default_factory=ContentMetrics)
    content_url: Optional[str] = Field(None, description="URL to the content if applicable")
    content_text: Optional[str] = Field(None, description="Text content if applicable")
    tags: List[str] = Field(default_factory=list, description="Tags for the content")

class RevenueRecord(BaseModel):
    id: str = Field(..., description="Unique identifier for the revenue record")
    dao_id: str = Field(..., description="ID of the content DAO")
    amount: float = Field(..., description="Amount of revenue in USD")
    source: str = Field(..., description="Source of the revenue")
    content_id: Optional[str] = Field(None, description="ID of the content that generated the revenue")
    date: str = Field(..., description="Date of the revenue record")
    
class ContentDAO(BaseModel):
    id: str = Field(..., description="Unique identifier for the content DAO")
    profile_id: str = Field(..., description="ID of the associated family profile")
    name: str = Field(..., description="Name of the content DAO")
    description: str = Field(..., description="Description of the content DAO")
    created_at: str = Field(..., description="Creation timestamp")
    avatar_url: Optional[str] = Field(None, description="Avatar URL for the DAO")
    interests: List[str] = Field(default_factory=list, description="Interests/themes for content generation")
    governance_rules: Dict[str, Any] = Field(default_factory=dict, description="Governance rules for the DAO")
    total_revenue: float = Field(default=0.0, description="Total revenue generated to date")
    content_count: int = Field(default=0, description="Total count of generated content")
    trust_contribution: float = Field(default=0.0, description="Total contribution to the family trust")

# Storage helper functions
def get_all_daos() -> List[ContentDAO]:
    """Get all content DAOs from storage"""
    try:
        daos_data = db.storage.json.get("content_daos", default={})
        daos = [ContentDAO(**dao_data) for dao_id, dao_data in daos_data.items()]
        return daos
    except Exception as e:
        print(f"Error getting content DAOs: {e}")
        return []

def save_all_daos(daos: List[ContentDAO]):
    """Save all content DAOs to storage"""
    daos_dict = {dao.id: dao.dict() for dao in daos}
    db.storage.json.put(sanitize_storage_key("content_daos"), daos_dict)

def get_dao_content(dao_id: str) -> List[ContentItem]:
    """Get all content items for a specific DAO"""
    try:
        content_data = db.storage.json.get(f"content_items_{dao_id}", default={})
        content_items = [ContentItem(**item_data) for item_id, item_data in content_data.items()]
        return content_items
    except Exception as e:
        print(f"Error getting content for DAO {dao_id}: {e}")
        return []

def save_dao_content(dao_id: str, content_items: List[ContentItem]):
    """Save all content items for a specific DAO"""
    content_dict = {item.id: item.dict() for item in content_items}
    db.storage.json.put(sanitize_storage_key(f"content_items_{dao_id}"), content_dict)

def get_dao_revenue(dao_id: str) -> List[RevenueRecord]:
    """Get all revenue records for a specific DAO"""
    try:
        revenue_data = db.storage.json.get(f"revenue_records_{dao_id}", default={})
        revenue_records = [RevenueRecord(**record_data) for record_id, record_data in revenue_data.items()]
        return revenue_records
    except Exception as e:
        print(f"Error getting revenue for DAO {dao_id}: {e}")
        return []

def save_dao_revenue(dao_id: str, revenue_records: List[RevenueRecord]):
    """Save all revenue records for a specific DAO"""
    revenue_dict = {record.id: record.dict() for record in revenue_records}
    db.storage.json.put(sanitize_storage_key(f"revenue_records_{dao_id}"), revenue_dict)

# Request/Response models
class ContentDAOCreate(BaseModel):
    profile_id: str = Field(..., description="ID of the associated family profile")
    name: str = Field(..., description="Name of the content DAO")
    description: str = Field(..., description="Description of the content DAO")
    interests: List[str] = Field(default_factory=list, description="Interests/themes for content generation")
    avatar_url: Optional[str] = Field(None, description="Avatar URL for the DAO")
    governance_rules: Dict[str, Any] = Field(default_factory=dict, description="Governance rules for the DAO")

class ContentItemCreate(BaseModel):
    dao_id: str = Field(..., description="ID of the content DAO that created this item")
    title: str = Field(..., description="Title of the content")
    description: str = Field(..., description="Description of the content")
    content_type: ContentType = Field(..., description="Type of content (text, image, etc)")
    content_url: Optional[str] = Field(None, description="URL to the content if applicable")
    content_text: Optional[str] = Field(None, description="Text content if applicable")
    tags: List[str] = Field(default_factory=list, description="Tags for the content")

class RevenueRecordCreate(BaseModel):
    dao_id: str = Field(..., description="ID of the content DAO")
    amount: float = Field(..., description="Amount of revenue in USD")
    source: str = Field(..., description="Source of the revenue")
    content_id: Optional[str] = Field(None, description="ID of the content that generated the revenue")

class ContentDAOSummary(BaseModel):
    id: str
    profile_id: str
    name: str
    description: str
    created_at: str
    avatar_url: Optional[str]
    interests: List[str]
    total_revenue: float
    content_count: int
    trust_contribution: float

# Endpoints
@router.get("/daos")
def list_content_daos() -> List[ContentDAOSummary]:
    """List all content DAOs with summary information"""
    daos = get_all_daos()
    return [ContentDAOSummary(**dao.dict()) for dao in daos]

@router.get("/daos/profile/{profile_id}")
def get_content_daos_for_profile(profile_id: str) -> List[ContentDAOSummary]:
    """Get all content DAOs for a specific family profile"""
    daos = get_all_daos()
    profile_daos = [dao for dao in daos if dao.profile_id == profile_id]
    return [ContentDAOSummary(**dao.dict()) for dao in profile_daos]

@router.get("/daos/{dao_id}")
def get_content_dao(dao_id: str) -> ContentDAO:
    """Get a specific content DAO by ID"""
    daos = get_all_daos()
    for dao in daos:
        if dao.id == dao_id:
            return dao
    raise HTTPException(status_code=404, detail=f"Content DAO with ID {dao_id} not found")

@router.post("/daos")
def create_content_dao(dao_request: ContentDAOCreate) -> ContentDAO:
    """Create a new content DAO"""
    daos = get_all_daos()
    
    # Generate a unique ID
    dao_id = f"dao_{uuid.uuid4().hex[:8]}"
    
    # Create the new DAO
    new_dao = ContentDAO(
        id=dao_id,
        profile_id=dao_request.profile_id,
        name=dao_request.name,
        description=dao_request.description,
        created_at=datetime.datetime.now().isoformat(),
        avatar_url=dao_request.avatar_url,
        interests=dao_request.interests,
        governance_rules=dao_request.governance_rules,
        total_revenue=0.0,
        content_count=0,
        trust_contribution=0.0
    )
    
    # Add the new DAO
    daos.append(new_dao)
    save_all_daos(daos)
    
    return new_dao

@router.put("/daos/{dao_id}")
def update_content_dao(dao_id: str, dao_request: ContentDAOCreate) -> ContentDAO:
    """Update an existing content DAO"""
    daos = get_all_daos()
    dao_found = False
    
    # Find and update the DAO
    for i, dao in enumerate(daos):
        if dao.id == dao_id:
            # Preserve metrics and timestamps
            updated_dao = ContentDAO(
                id=dao_id,
                profile_id=dao_request.profile_id,
                name=dao_request.name,
                description=dao_request.description,
                created_at=dao.created_at,  # Preserve creation time
                avatar_url=dao_request.avatar_url,
                interests=dao_request.interests,
                governance_rules=dao_request.governance_rules,
                total_revenue=dao.total_revenue,
                content_count=dao.content_count,
                trust_contribution=dao.trust_contribution
            )
            daos[i] = updated_dao
            dao_found = True
            break
    
    if not dao_found:
        raise HTTPException(status_code=404, detail=f"Content DAO with ID {dao_id} not found")
    
    save_all_daos(daos)
    return daos[i]

@router.delete("/daos/{dao_id}")
def delete_content_dao(dao_id: str) -> Dict[str, str]:
    """Delete a content DAO"""
    daos = get_all_daos()
    initial_count = len(daos)
    
    # Filter out the DAO to delete
    daos = [dao for dao in daos if dao.id != dao_id]
    
    if len(daos) == initial_count:
        raise HTTPException(status_code=404, detail=f"Content DAO with ID {dao_id} not found")
    
    save_all_daos(daos)
    return {"status": "success", "message": f"Content DAO with ID {dao_id} deleted successfully"}

@router.get("/content/{dao_id}")
def list_dao_content(dao_id: str) -> List[ContentItem]:
    """List all content items for a specific DAO"""
    return get_dao_content(dao_id)

@router.post("/content")
def create_content_item(content_request: ContentItemCreate) -> ContentItem:
    """Create a new content item for a DAO"""
    # Check if the DAO exists
    daos = get_all_daos()
    dao_exists = any(dao.id == content_request.dao_id for dao in daos)
    if not dao_exists:
        raise HTTPException(status_code=404, detail=f"Content DAO with ID {content_request.dao_id} not found")
    
    # Get existing content items
    content_items = get_dao_content(content_request.dao_id)
    
    # Generate a unique ID
    content_id = f"content_{uuid.uuid4().hex[:8]}"
    
    # Create the new content item
    new_item = ContentItem(
        id=content_id,
        dao_id=content_request.dao_id,
        title=content_request.title,
        description=content_request.description,
        content_type=content_request.content_type,
        created_at=datetime.datetime.now().isoformat(),
        status=ContentStatus.GENERATED,
        metrics=ContentMetrics(),
        content_url=content_request.content_url,
        content_text=content_request.content_text,
        tags=content_request.tags
    )
    
    # Add the new content item
    content_items.append(new_item)
    save_dao_content(content_request.dao_id, content_items)
    
    # Update the DAO's content count
    for i, dao in enumerate(daos):
        if dao.id == content_request.dao_id:
            dao.content_count += 1
            daos[i] = dao
            break
    save_all_daos(daos)
    
    return new_item

@router.put("/content/{content_id}")
def update_content_status(content_id: str, status: ContentStatus) -> ContentItem:
    """Update the status of a content item"""
    # Find which DAO contains this content
    all_daos = get_all_daos()
    content_item = None
    dao_id = None
    
    for dao in all_daos:
        content_items = get_dao_content(dao.id)
        for item in content_items:
            if item.id == content_id:
                content_item = item
                dao_id = dao.id
                break
        if content_item:
            break
    
    if not content_item or not dao_id:
        raise HTTPException(status_code=404, detail=f"Content item with ID {content_id} not found")
    
    # Update the content status
    content_items = get_dao_content(dao_id)
    for i, item in enumerate(content_items):
        if item.id == content_id:
            item.status = status
            content_items[i] = item
            break
    
    save_dao_content(dao_id, content_items)
    return item

@router.post("/revenue")
def record_revenue(revenue_request: RevenueRecordCreate) -> RevenueRecord:
    """Record new revenue for a DAO"""
    # Check if the DAO exists
    daos = get_all_daos()
    dao_found = False
    dao_index = -1
    
    for i, dao in enumerate(daos):
        if dao.id == revenue_request.dao_id:
            dao_found = True
            dao_index = i
            break
    
    if not dao_found:
        raise HTTPException(status_code=404, detail=f"Content DAO with ID {revenue_request.dao_id} not found")
    
    # Get existing revenue records
    revenue_records = get_dao_revenue(revenue_request.dao_id)
    
    # Generate a unique ID
    revenue_id = f"revenue_{uuid.uuid4().hex[:8]}"
    
    # Create the new revenue record
    new_record = RevenueRecord(
        id=revenue_id,
        dao_id=revenue_request.dao_id,
        amount=revenue_request.amount,
        source=revenue_request.source,
        content_id=revenue_request.content_id,
        date=datetime.datetime.now().isoformat()
    )
    
    # Add the new revenue record
    revenue_records.append(new_record)
    save_dao_revenue(revenue_request.dao_id, revenue_records)
    
    # Update the DAO's total revenue and trust contribution
    dao = daos[dao_index]
    dao.total_revenue += revenue_request.amount
    dao.trust_contribution += revenue_request.amount * 0.75  # 75% goes to trust by default
    daos[dao_index] = dao
    save_all_daos(daos)
    
    # If the revenue is associated with a content item, update its metrics
    if revenue_request.content_id:
        content_items = get_dao_content(revenue_request.dao_id)
        for i, item in enumerate(content_items):
            if item.id == revenue_request.content_id:
                item.metrics.revenue_generated += revenue_request.amount
                content_items[i] = item
                break
        save_dao_content(revenue_request.dao_id, content_items)
    
    return new_record

@router.get("/revenue/{dao_id}")
def get_revenue_history(dao_id: str) -> List[RevenueRecord]:
    """Get revenue history for a specific DAO"""
    # Check if the DAO exists
    daos = get_all_daos()
    dao_exists = any(dao.id == dao_id for dao in daos)
    if not dao_exists:
        raise HTTPException(status_code=404, detail=f"Content DAO with ID {dao_id} not found")
    
    return get_dao_revenue(dao_id)

# AI content generation simulation endpoint
@router.post("/generate-content/{dao_id}")
def generate_content_dao(dao_id: str) -> ContentItem:
    """Simulate AI generating content for a DAO"""
    # Check if the DAO exists
    daos = get_all_daos()
    dao = None
    
    for d in daos:
        if d.id == dao_id:
            dao = d
            break
    
    if not dao:
        raise HTTPException(status_code=404, detail=f"Content DAO with ID {dao_id} not found")
    
    # Simple content generation based on DAO interests
    content_types = [ContentType.TEXT, ContentType.IMAGE, ContentType.CONCEPT]
    selected_type = content_types[uuid.uuid4().int % len(content_types)]
    
    interests = dao.interests if dao.interests else ["creativity", "innovation", "technology"]
    selected_interest = interests[uuid.uuid4().int % len(interests)]
    
    # Generate content title based on interest
    title_templates = [
        f"The Future of {selected_interest}",
        f"5 Ways {selected_interest} Will Change the World",
        f"Understanding {selected_interest} Through Data",
        f"A New Perspective on {selected_interest}",
        f"The Hidden Potential of {selected_interest}",
    ]
    title = title_templates[uuid.uuid4().int % len(title_templates)]
    
    # Generate content description
    description_templates = [
        f"An exploration of how {selected_interest} is shaping our future and creating new opportunities.",
        f"A deep dive into the transformative potential of {selected_interest} across industries.",
        f"Analyzing current trends in {selected_interest} and their implications for society.",
        f"Uncovering hidden patterns and insights in the world of {selected_interest}.",
        f"A visionary look at how {selected_interest} will evolve over the next decade.",
    ]
    description = description_templates[uuid.uuid4().int % len(description_templates)]
    
    # For text content, generate a sample paragraph
    content_text = None
    if selected_type == ContentType.TEXT:
        text_templates = [
            f"The evolution of {selected_interest} represents one of the most significant paradigm shifts of our time. As we move forward into an increasingly digital and interconnected world, the principles and applications of {selected_interest} continue to reshape how we think about value, ownership, and trust in our global society. This article explores the multifaceted implications of these changes.",
            f"In recent years, {selected_interest} has emerged as a powerful force for innovation across industries. By challenging conventional wisdom and established practices, it creates new possibilities for solving complex problems that have long plagued our society. This piece examines the transformative potential of {selected_interest} through various case studies and expert insights.",
            f"The intersection of {selected_interest} and emerging technologies presents unprecedented opportunities for growth and development. As these fields continue to evolve and converge, we're witnessing the birth of entirely new ecosystems and value networks that transcend traditional boundaries and limitations.",
        ]
        content_text = text_templates[uuid.uuid4().int % len(text_templates)]
    
    # Generate tags from interests
    tags = [selected_interest] + interests[:2]
    
    # Create a content item request
    content_request = ContentItemCreate(
        dao_id=dao_id,
        title=title,
        description=description,
        content_type=selected_type,
        content_url=None,  # In a real implementation, this might be a generated image URL
        content_text=content_text,
        tags=tags
    )
    
    # Use the existing endpoint to create the content item
    return create_content_item(content_request)

# Endpoint to simulate audience engagement with content
@router.post("/simulate-engagement/{content_id}")
def simulate_engagement(content_id: str) -> ContentItem:
    """Simulate audience engagement with a piece of content"""
    # Find which DAO contains this content
    all_daos = get_all_daos()
    content_item = None
    dao_id = None
    
    for dao in all_daos:
        content_items = get_dao_content(dao.id)
        for item in content_items:
            if item.id == content_id:
                content_item = item
                dao_id = dao.id
                break
        if content_item:
            break
    
    if not content_item or not dao_id:
        raise HTTPException(status_code=404, detail=f"Content item with ID {content_id} not found")
    
    # Simulate engagement metrics
    views_increase = uuid.uuid4().int % 100 + 10  # 10-109 new views
    engagement_rate = (uuid.uuid4().int % 30) / 100 + 0.05  # 5%-35% engagement rate
    revenue = (views_increase * engagement_rate) * (uuid.uuid4().int % 5 + 1) / 10  # Some revenue based on engagement
    
    # Update the content metrics
    content_items = get_dao_content(dao_id)
    for i, item in enumerate(content_items):
        if item.id == content_id:
            item.metrics.views += views_increase
            item.metrics.engagement_rate = engagement_rate
            item.metrics.revenue_generated += revenue
            content_items[i] = item
            content_item = item  # Update the return value
            break
    
    save_dao_content(dao_id, content_items)
    
    # If revenue was generated, create a revenue record
    if revenue > 0:
        revenue_request = RevenueRecordCreate(
            dao_id=dao_id,
            amount=revenue,
            source="Content engagement",
            content_id=content_id
        )
        record_revenue(revenue_request)
    
    return content_item

# Dashboard analytics endpoint
@router.get("/analytics/{dao_id}")
def get_dao_analytics(dao_id: str) -> Dict[str, Any]:
    """Get analytics data for a specific content DAO"""
    # Check if the DAO exists
    daos = get_all_daos()
    dao = None
    
    for d in daos:
        if d.id == dao_id:
            dao = d
            break
    
    if not dao:
        raise HTTPException(status_code=404, detail=f"Content DAO with ID {dao_id} not found")
    
    # Get all content and revenue data
    content_items = get_dao_content(dao_id)
    revenue_records = get_dao_revenue(dao_id)
    
    # Calculate analytics
    total_views = sum(item.metrics.views for item in content_items)
    avg_engagement = sum(item.metrics.engagement_rate for item in content_items) / len(content_items) if content_items else 0
    revenue_by_type = {}
    for item in content_items:
        content_type = item.content_type
        if content_type not in revenue_by_type:
            revenue_by_type[content_type] = 0
        revenue_by_type[content_type] += item.metrics.revenue_generated
    
    # Get revenue over time (last 30 days by default)
    now = datetime.datetime.now()
    thirty_days_ago = now - datetime.timedelta(days=30)
    daily_revenue = {}
    
    for record in revenue_records:
        record_date = datetime.datetime.fromisoformat(record.date.split('T')[0])
        if record_date >= thirty_days_ago:
            date_str = record_date.strftime('%Y-%m-%d')
            if date_str not in daily_revenue:
                daily_revenue[date_str] = 0
            daily_revenue[date_str] += record.amount
    
    # Format revenue time series
    revenue_time_series = [
        {"date": date, "amount": amount}
        for date, amount in daily_revenue.items()
    ]
    
    # Get top performing content
    top_content = sorted(
        content_items, 
        key=lambda item: item.metrics.revenue_generated, 
        reverse=True
    )[:5]
    
    return {
        "dao": dao.dict(),
        "total_views": total_views,
        "average_engagement_rate": avg_engagement,
        "revenue_by_content_type": revenue_by_type,
        "revenue_time_series": revenue_time_series,
        "top_performing_content": [item.dict() for item in top_content],
        "content_count": len(content_items),
        "trust_contribution_percentage": (dao.trust_contribution / dao.total_revenue) * 100 if dao.total_revenue > 0 else 0
    }

# Educational endpoint
@router.get("/education/dao-concept")
def get_dao_educational_content() -> Dict[str, Any]:
    """Get educational content about Content DAOs and their role in trust funding"""
    return {
        "title": "Understanding AI-Powered Content DAOs for Trust Funding",
        "sections": [
            {
                "title": "What is a Content DAO?",
                "content": "A Content DAO (Decentralized Autonomous Organization) is a self-managing entity that produces creative work and generates value through content creation and distribution. In the Legacy Vault context, each family member can have their own AI-powered Content DAO that automatically generates media and other creative assets aligned with their interests, with revenue flowing directly into their trust."
            },
            {
                "title": "How Content DAOs Generate Value",
                "content": "Content DAOs leverage artificial intelligence to create various types of content - articles, images, concepts, audio, and potentially video. This content is then distributed through appropriate channels where it can generate revenue through views, engagement, licensing, or direct sales. The AI continuously improves its content strategy based on performance metrics."
            },
            {
                "title": "Governance and Revenue Distribution",
                "content": "Each Content DAO operates according to predefined governance rules that determine how content is approved, published, and monetized. By default, 75% of all revenue generated flows directly into the family member's trust portfolio, with the remaining funds used to sustain and grow the DAO's operations."
            },
            {
                "title": "Benefits for Long-Term Wealth Building",
                "content": "Content DAOs provide a unique advantage for generational wealth building: they create a perpetual value-generation mechanism that operates independently of market conditions. Unlike traditional investments that may be subject to market volatility, these DAOs produce value through human attention and engagement - a resource that continues to grow in the digital economy."
            },
            {
                "title": "Creating a Personal Media Empire",
                "content": "Think of each Content DAO as a personal media company that works 24/7 to create value aligned with the family member's interests and identity. Over decades, these DAOs can evolve into substantial digital estates that generate significant ongoing revenue streams for trust beneficiaries."
            }
        ],
        "recommendations": [
            "Start with clear interest areas that have market potential",
            "Monitor performance metrics and adjust DAO governance parameters accordingly",
            "Diversify content types to maximize reach and engagement",
            "Consider the ethical implications of content creation and set appropriate guidelines",
            "View Content DAOs as complementary to traditional investments, not replacements"
        ]
    }
