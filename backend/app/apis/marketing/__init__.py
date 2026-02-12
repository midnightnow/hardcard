from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import databutton as db
import json

router = APIRouter(prefix="/marketing")

# Models for marketing content
class MarketingPage(BaseModel):
    slug: str
    title: str
    content: str
    metadata: Optional[dict] = None

class BlogPost(BaseModel):
    id: str
    title: str
    summary: str
    author: str
    published_date: str
    content: Optional[str] = None
    tags: List[str] = []

class BlogPostsList(BaseModel):
    posts: List[BlogPost]
    total: int
    offset: int
    limit: int

class LeadCapture(BaseModel):
    email: Optional[str] = None
    page_slug: str
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

# Mock data storage - would be replaced by actual LegacyVault API calls
def get_mock_page(slug: str) -> MarketingPage:
    # In production, this would make a request to LegacyVault's Marketing CMS API
    pages = {
        "about": MarketingPage(
            slug="about",
            title="About NexusAI",
            content="# About NexusAI\n\nNexusAI is a decentralized marketplace for AI services, connecting clients with top AI providers.",
            metadata={"seo_description": "Learn about NexusAI's mission and vision."}
        ),
        "how-it-works": MarketingPage(
            slug="how-it-works",
            title="How NexusAI Works",
            content="# How It Works\n\nNexusAI uses blockchain technology to secure transactions between clients and AI service providers.",
            metadata={"seo_description": "Learn how NexusAI's blockchain escrow system works."}
        )
    }
    return pages.get(slug)

def get_mock_blog_posts(limit: int, offset: int) -> BlogPostsList:
    # In production, this would make a request to LegacyVault's Marketing CMS API
    all_posts = [
        BlogPost(
            id="1",
            title="The Future of AI Services",
            summary="How decentralized marketplaces are changing the AI landscape",
            author="John Doe",
            published_date="2025-03-15",
            tags=["AI", "blockchain", "future"]
        ),
        BlogPost(
            id="2",
            title="Smart Contracts for AI Services",
            summary="How blockchain ensures fair compensation for AI work",
            author="Jane Smith",
            published_date="2025-03-20",
            tags=["smart contracts", "blockchain", "payments"]
        )
    ]
    
    # Apply pagination
    paginated_posts = all_posts[offset:offset+limit]
    
    return BlogPostsList(
        posts=paginated_posts,
        total=len(all_posts),
        offset=offset,
        limit=limit
    )

def get_mock_post(post_id: str) -> BlogPost:
    # In production, this would make a request to LegacyVault's Marketing CMS API
    posts = {
        "1": BlogPost(
            id="1",
            title="The Future of AI Services",
            summary="How decentralized marketplaces are changing the AI landscape",
            author="John Doe",
            published_date="2025-03-15",
            content="# The Future of AI Services\n\nIn this article, we explore how decentralized marketplaces are revolutionizing the AI landscape...",
            tags=["AI", "blockchain", "future"]
        ),
        "2": BlogPost(
            id="2",
            title="Smart Contracts for AI Services",
            summary="How blockchain ensures fair compensation for AI work",
            author="Jane Smith",
            published_date="2025-03-20",
            content="# Smart Contracts for AI Services\n\nSmart contracts are self-executing contracts with the terms of the agreement directly written into code...",
            tags=["smart contracts", "blockchain", "payments"]
        )
    }
    return posts.get(post_id)

# API Endpoints
@router.get("/pages/{slug}", response_model=MarketingPage)
async def get_marketing_page(slug: str):
    """Get marketing page content by slug"""
    page = get_mock_page(slug)
    if not page:
        raise HTTPException(status_code=404, detail=f"Page with slug '{slug}' not found")
    return page

@router.get("/blog", response_model=BlogPostsList)
async def get_blog_posts(limit: int = 10, offset: int = 0):
    """Get a list of blog posts with pagination"""
    return get_mock_blog_posts(limit, offset)

@router.get("/posts/{post_id}", response_model=BlogPost)
async def get_blog_post(post_id: str):
    """Get a specific blog post by ID"""
    post = get_mock_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with ID '{post_id}' not found")
    return post

@router.post("/leads")
async def capture_lead(lead: LeadCapture):
    """Capture lead information from marketing pages"""
    # In production, this would make a request to LegacyVault's lead capture API
    # For now, we'll just log the lead
    print(f"Lead captured: {lead}")
    
    # Store the lead in Databutton storage for demo purposes
    try:
        # Get existing leads or initialize empty list
        leads_key = "marketing_leads"
        try:
            leads = json.loads(db.storage.text.get(leads_key))
        except:
            leads = []
        
        # Add new lead
        leads.append(lead.dict())
        
        # Save updated leads
        db.storage.text.put(leads_key, json.dumps(leads))
        
        return {"status": "success", "message": "Lead captured successfully"}
    except Exception as e:
        print(f"Error storing lead: {e}")
        return {"status": "error", "message": str(e)}
