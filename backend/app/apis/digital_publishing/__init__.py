from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time
import uuid
from enum import Enum

router = APIRouter(prefix="/digital-publishing")

# Digital Publishing Dashboard API
# This API provides a comprehensive content management and distribution system
# with tamper-evident audit trails powered by the RealTBlock trust model

class ContentStatus(str, Enum):
    """Status of a content item"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ContentType(str, Enum):
    """Type of content"""
    ARTICLE = "article"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    COLLECTION = "collection"

class DistributionPlatform(str, Enum):
    """Distribution platform for content"""
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    PODCAST = "podcast"
    MUSIC_STREAMING = "music_streaming"
    VIDEO_STREAMING = "video_streaming"

class DistroKidStatus(str, Enum):
    """Status of a DistroKid submission"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"

class ContentItem(BaseModel):
    """A content item in the digital publishing system"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    content_type: ContentType
    status: ContentStatus = ContentStatus.DRAFT
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    author_id: str
    media_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    ledger_entries: List[str] = []  # References to RealTBlock ledger entries

class Campaign(BaseModel):
    """A campaign for distributing content"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    start_date: float
    end_date: Optional[float] = None
    platforms: List[DistributionPlatform] = []
    content_ids: List[str] = []
    metadata: Dict[str, Any] = {}
    status: str = "draft"
    ledger_entries: List[str] = []  # References to RealTBlock ledger entries

class DistroKidSubmission(BaseModel):
    """A submission to DistroKid"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str
    artist_name: str
    track_title: str
    album: Optional[str] = None
    genre: str
    release_date: float
    cover_art_url: Optional[str] = None
    audio_url: str
    pricing: Optional[Dict[str, Any]] = None
    platforms: List[str] = ["spotify", "apple_music", "amazon", "tidal"]
    status: DistroKidStatus = DistroKidStatus.PENDING
    submitted_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    external_id: Optional[str] = None
    ledger_entry_id: Optional[str] = None  # Reference to RealTBlock ledger entry

class CreateContentRequest(BaseModel):
    """Request to create a new content item"""
    title: str
    description: str
    content_type: ContentType
    author_id: str
    media_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tags: List[str] = []

class UpdateContentRequest(BaseModel):
    """Request to update a content item"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ContentStatus] = None
    media_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class CreateCampaignRequest(BaseModel):
    """Request to create a new campaign"""
    title: str
    description: str
    start_date: float
    end_date: Optional[float] = None
    platforms: List[DistributionPlatform] = []
    content_ids: List[str] = []
    metadata: Dict[str, Any] = {}

class UpdateCampaignRequest(BaseModel):
    """Request to update a campaign"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[float] = None
    end_date: Optional[float] = None
    platforms: Optional[List[DistributionPlatform]] = None
    content_ids: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class SubmitToDistroKidRequest(BaseModel):
    """Request to submit content to DistroKid"""
    content_id: str
    artist_name: str
    track_title: str
    album: Optional[str] = None
    genre: str
    release_date: float
    cover_art_url: Optional[str] = None
    pricing: Optional[Dict[str, Any]] = None
    platforms: List[str] = ["spotify", "apple_music", "amazon", "tidal"]

class AuditLogEntry(BaseModel):
    """An entry in the audit log"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any] = {}
    ledger_entry_id: Optional[str] = None  # Reference to RealTBlock ledger entry

# In-memory storage for the digital publishing system
content_items: Dict[str, ContentItem] = {}
campaigns: Dict[str, Campaign] = {}
distrokid_submissions: Dict[str, DistroKidSubmission] = {}
audit_log: List[AuditLogEntry] = []

@router.post("/content", response_model=ContentItem)
def create_content(request: CreateContentRequest) -> ContentItem:
    """Create a new content item"""
    content = ContentItem(
        title=request.title,
        description=request.description,
        content_type=request.content_type,
        author_id=request.author_id,
        media_url=request.media_url,
        metadata=request.metadata,
        tags=request.tags
    )
    
    content_items[content.id] = content
    
    # In a production implementation, we would add an entry to the RealTBlock ledger
    # content.ledger_entries.append(ledger_entry_id)
    
    return content

@router.get("/content/{content_id}", response_model=ContentItem)
def get_content(content_id: str) -> ContentItem:
    """Get a content item by ID"""
    if content_id not in content_items:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    return content_items[content_id]

@router.get("/content", response_model=List[ContentItem])
def list_content() -> List[ContentItem]:
    """List all content items"""
    return list(content_items.values())

@router.put("/content/{content_id}", response_model=ContentItem)
def update_content(content_id: str, request: UpdateContentRequest) -> ContentItem:
    """Update a content item"""
    if content_id not in content_items:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    content = content_items[content_id]
    
    # Update fields if provided
    if request.title is not None:
        content.title = request.title
    if request.description is not None:
        content.description = request.description
    if request.status is not None:
        content.status = request.status
    if request.media_url is not None:
        content.media_url = request.media_url
    if request.metadata is not None:
        content.metadata = request.metadata
    if request.tags is not None:
        content.tags = request.tags
    
    content.updated_at = time.time()
    
    # In a production implementation, we would add an entry to the RealTBlock ledger
    # content.ledger_entries.append(ledger_entry_id)
    
    return content

@router.post("/campaigns", response_model=Campaign)
def create_campaign(request: CreateCampaignRequest) -> Campaign:
    """Create a new campaign"""
    campaign = Campaign(
        title=request.title,
        description=request.description,
        start_date=request.start_date,
        end_date=request.end_date,
        platforms=request.platforms,
        content_ids=request.content_ids,
        metadata=request.metadata
    )
    
    campaigns[campaign.id] = campaign
    
    # In a production implementation, we would add an entry to the RealTBlock ledger
    # campaign.ledger_entries.append(ledger_entry_id)
    
    return campaign

@router.get("/campaigns/{campaign_id}", response_model=Campaign)
def get_campaign(campaign_id: str) -> Campaign:
    """Get a campaign by ID"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaigns[campaign_id]

@router.get("/campaigns", response_model=List[Campaign])
def list_campaigns() -> List[Campaign]:
    """List all campaigns"""
    return list(campaigns.values())

@router.put("/campaigns/{campaign_id}", response_model=Campaign)
def update_campaign(campaign_id: str, request: UpdateCampaignRequest) -> Campaign:
    """Update a campaign"""
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns[campaign_id]
    
    # Update fields if provided
    if request.title is not None:
        campaign.title = request.title
    if request.description is not None:
        campaign.description = request.description
    if request.start_date is not None:
        campaign.start_date = request.start_date
    if request.end_date is not None:
        campaign.end_date = request.end_date
    if request.platforms is not None:
        campaign.platforms = request.platforms
    if request.content_ids is not None:
        campaign.content_ids = request.content_ids
    if request.metadata is not None:
        campaign.metadata = request.metadata
    if request.status is not None:
        campaign.status = request.status
    
    campaign.updated_at = time.time()
    
    # In a production implementation, we would add an entry to the RealTBlock ledger
    # campaign.ledger_entries.append(ledger_entry_id)
    
    return campaign

@router.post("/distrokid/submit", response_model=DistroKidSubmission)
def submit_to_distrokid(request: SubmitToDistroKidRequest) -> DistroKidSubmission:
    """Submit content to DistroKid"""
    if request.content_id not in content_items:
        raise HTTPException(status_code=404, detail="Content item not found")
    
    # Verify content is audio type
    content = content_items[request.content_id]
    if content.content_type != ContentType.AUDIO:
        raise HTTPException(status_code=400, detail="Content must be audio type for DistroKid submission")
    
    # Create DistroKid submission
    submission = DistroKidSubmission(
        content_id=request.content_id,
        artist_name=request.artist_name,
        track_title=request.track_title,
        album=request.album,
        genre=request.genre,
        release_date=request.release_date,
        cover_art_url=request.cover_art_url,
        audio_url=content.media_url,  # Use the media URL from the content item
        pricing=request.pricing,
        platforms=request.platforms
    )
    
    distrokid_submissions[submission.id] = submission
    
    # In a real implementation, this would initiate the actual submission to DistroKid
    # and we would add an entry to the RealTBlock ledger
    # submission.ledger_entry_id = ledger_entry_id
    
    return submission

@router.get("/distrokid/submissions/{submission_id}", response_model=DistroKidSubmission)
def get_distrokid_submission(submission_id: str) -> DistroKidSubmission:
    """Get a DistroKid submission by ID"""
    if submission_id not in distrokid_submissions:
        raise HTTPException(status_code=404, detail="DistroKid submission not found")
    
    return distrokid_submissions[submission_id]

@router.get("/distrokid/submissions", response_model=List[DistroKidSubmission])
def list_distrokid_submissions() -> List[DistroKidSubmission]:
    """List all DistroKid submissions"""
    return list(distrokid_submissions.values())

@router.get("/audit-log", response_model=List[AuditLogEntry])
def get_digital_publishing_audit_log() -> List[AuditLogEntry]:
    """Get the audit log for digital publishing content"""
    return audit_log

@router.post("/audit-log", response_model=AuditLogEntry)
def add_audit_log_entry(entry: AuditLogEntry) -> AuditLogEntry:
    """Add an entry to the audit log"""
    audit_log.append(entry)
    
    # In a production implementation, we would add an entry to the RealTBlock ledger
    # entry.ledger_entry_id = ledger_entry_id
    
    return entry
