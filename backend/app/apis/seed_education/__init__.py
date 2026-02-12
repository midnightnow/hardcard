from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
import databutton as db
import json
from datetime import datetime, timedelta

# Initialize Firebase Admin SDK if not already initialized
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(json.loads(db.secrets.get("FIREBASE_SERVICE_ACCOUNT")))
    app = firebase_admin.initialize_app(cred)

router = APIRouter()
db = firestore.client()

class SeedEducationRequest(BaseModel):
    force_reset: bool = False

class SeedEducationResponse(BaseModel):
    message: str
    count: int
    categories_count: int
    tags_count: int
    authors_count: int

@router.post("/seed-education")
def seed_education(request: SeedEducationRequest) -> SeedEducationResponse:
    """
    Seeds the Firestore database with sample educational content about cannabinoids.
    If force_reset is True, it will delete existing documents before seeding.
    """
    # Check if we already have articles
    articles_ref = db.collection('articles')
    existing_articles = list(articles_ref.limit(1).stream())
    
    if existing_articles and not request.force_reset:
        return SeedEducationResponse(
            message="Articles already exist. Set force_reset to True to reseed.",
            count=len(list(articles_ref.stream())),
            categories_count=len(list(db.collection('article_categories').stream())),
            tags_count=len(list(db.collection('article_tags').stream())),
            authors_count=len(list(db.collection('article_authors').stream()))
        )
    
    # If force_reset, delete existing collections
    if request.force_reset:
        # Delete all documents in articles collection
        for doc in db.collection('articles').stream():
            doc.reference.delete()
        
        # Delete all documents in article_categories collection
        for doc in db.collection('article_categories').stream():
            doc.reference.delete()
            
        # Delete all documents in article_tags collection
        for doc in db.collection('article_tags').stream():
            doc.reference.delete()
            
        # Delete all documents in article_authors collection
        for doc in db.collection('article_authors').stream():
            doc.reference.delete()
    
    # SEED CATEGORIES
    categories = [
        {
            "id": "cbd-basics",
            "name": "CBD Basics",
            "description": "Essential information about CBD, what it is, and how it works.",
            "icon": "book-open",
            "order": 1,
            "slug": "cbd-basics",
            "active": True
        },
        {
            "id": "cbg-explained",
            "name": "CBG Explained",
            "description": "Learn about CBG, its potential benefits, and how it differs from CBD.",
            "icon": "microscope",
            "order": 2,
            "slug": "cbg-explained",
            "active": True
        },
        {
            "id": "wellness",
            "name": "Wellness Applications",
            "description": "How cannabinoids can support various aspects of your wellbeing.",
            "icon": "heart",
            "order": 3,
            "slug": "wellness",
            "active": True
        },
        {
            "id": "science",
            "name": "The Science",
            "description": "Scientific research and evidence behind cannabinoids and their effects.",
            "icon": "flask",
            "order": 4,
            "slug": "science",
            "active": True
        },
        {
            "id": "guides",
            "name": "How-to Guides",
            "description": "Practical guides on using cannabinoid products effectively.",
            "icon": "map",
            "order": 5,
            "slug": "guides",
            "active": True
        }
    ]
    
    # Add categories to Firestore
    for category in categories:
        cat_id = category.pop("id")
        db.collection('article_categories').document(cat_id).set(category)
    
    # SEED TAGS
    tags = [
        {"name": "Beginner", "slug": "beginner"},
        {"name": "Advanced", "slug": "advanced"},
        {"name": "Sleep", "slug": "sleep"},
        {"name": "Pain Management", "slug": "pain-management"},
        {"name": "Anxiety", "slug": "anxiety"},
        {"name": "Inflammation", "slug": "inflammation"},
        {"name": "Dosage", "slug": "dosage"},
        {"name": "Research", "slug": "research"},
        {"name": "Wellness", "slug": "wellness"},
        {"name": "Products", "slug": "products"}
    ]
    
    # Add tags to Firestore
    for tag in tags:
        db.collection('article_tags').document(tag["slug"]).set(tag)
    
    # SEED AUTHORS
    authors = [
        {
            "name": "Dr. Emily Johnson",
            "bio": "Dr. Emily Johnson has over 15 years of experience in phytocannabinoid research and has published numerous papers on the endocannabinoid system.",
            "avatar_url": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-4.0.3&auto=format&fit=crop&w=256&q=80",
            "credentials": "Ph.D in Neuroscience"
        },
        {
            "name": "Michael Chen",
            "bio": "Michael is a certified herbalist with special focus on cannabinoid therapies and plant-based wellness approaches.",
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=256&q=80",
            "credentials": "Certified Herbalist"
        },
        {
            "name": "Sarah Williams",
            "bio": "Sarah is a wellness coach specializing in holistic approaches to health, including cannabinoid integration for optimal wellbeing.",
            "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?ixlib=rb-4.0.3&auto=format&fit=crop&w=256&q=80",
            "credentials": "Wellness Specialist"
        }
    ]
    
    # Add authors to Firestore
    author_refs = []
    for author in authors:
        author_ref = db.collection('article_authors').add(author)
        author_refs.append(author_ref[1])
    
    # SEED ARTICLES
    articles = [
        {
            "slug": "what-is-cbd-beginners-guide",
            "title": "What is CBD? A Beginner's Guide to Cannabidiol",
            "subtitle": "Understanding the basics of this popular cannabinoid",
            "summary": "CBD has gained enormous popularity, but what exactly is it and how does it work? This beginner's guide explains everything you need to know about cannabidiol, its potential benefits, and how to get started.",
            "content": "<h2>Introduction to CBD</h2><p>Cannabidiol, commonly known as CBD, is one of over 100 chemical compounds called cannabinoids found in the cannabis plant. Unlike its cousin THC (tetrahydrocannabinol), CBD is non-intoxicating, meaning it won't get you 'high.'</p><h2>How CBD Works</h2><p>CBD interacts with your body's endocannabinoid system (ECS), a complex cell-signaling system that plays a role in regulating various functions and processes, including sleep, mood, appetite, memory, reproduction, and pain sensation.</p><p>Your body produces endocannabinoids, which are molecules similar to cannabinoids but produced by your body. These endocannabinoids bind to cannabinoid receptors in your nervous system. CBD doesn't bind directly to cannabinoid receptors but influences them indirectly, potentially helping your natural endocannabinoids work more effectively.</p>",
            "featured_image": "https://images.unsplash.com/photo-1598880773633-8a2d27b6a875?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1598880773633-8a2d27b6a875?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["cbd-basics"],
            "tag_ids": ["beginner", "wellness"],
            "author_id": author_refs[0],
            "published_date": datetime.now() - timedelta(days=30),
            "reading_time": 8,
            "featured": True,
            "status": "published"
        },
        {
            "slug": "cbd-vs-cbg-cannabinoids-compared",
            "title": "CBD vs. CBG: Understanding the Differences",
            "subtitle": "A comparison of two prominent non-intoxicating cannabinoids",
            "summary": "Both CBD and CBG are non-intoxicating cannabinoids with therapeutic potential, but they have distinct differences. This article compares their effects, benefits, and applications to help you understand which might be right for you.",
            "content": "<h2>Introduction to Cannabinoids</h2><p>The cannabis plant contains over 100 different cannabinoids, each with unique properties and potential effects on the human body. While THC and CBD have received the most attention, other cannabinoids like CBG (Cannabigerol) are gaining recognition for their distinctive properties.</p><h2>What is CBG?</h2><p>CBG is often referred to as the 'mother cannabinoid' because other cannabinoids are derived from its precursor form, CBGA (cannabigerolic acid). As the cannabis plant matures, enzymes convert CBGA into THCA, CBDA, and other cannabinoid acids, which is why CBG is typically found in lower concentrations in mature plants.</p>",
            "featured_image": "https://images.unsplash.com/photo-1579091372493-6616cf518f9b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1579091372493-6616cf518f9b?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["cbg-explained", "science"],
            "tag_ids": ["research", "advanced"],
            "author_id": author_refs[0],
            "published_date": datetime.now() - timedelta(days=15),
            "reading_time": 10,
            "featured": True,
            "status": "published"
        },
        {
            "slug": "cannabinoids-for-sleep-improvement",
            "title": "Using Cannabinoids for Better Sleep: A Comprehensive Guide",
            "subtitle": "How CBD, CBN, and other compounds may help improve sleep quality",
            "summary": "Sleep issues affect millions of people worldwide. This guide explores how cannabinoids like CBD and CBN may help address sleep problems, what the research says, and how to incorporate them into your sleep routine effectively.",
            "content": "<h2>The Importance of Quality Sleep</h2><p>Quality sleep is essential for physical health, cognitive function, emotional wellbeing, and overall quality of life. Unfortunately, sleep problems are increasingly common, with an estimated 50-70 million US adults suffering from sleep disorders.</p><p>While traditional sleep aids can be effective, many people experience unwanted side effects or prefer natural alternatives. This has led to growing interest in cannabinoids as potential sleep aids.</p>",
            "featured_image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["wellness", "guides"],
            "tag_ids": ["sleep", "research", "wellness"],
            "author_id": author_refs[2],
            "published_date": datetime.now() - timedelta(days=7),
            "reading_time": 12,
            "featured": True,
            "status": "published"
        },
        {
            "slug": "cannabinoids-for-pain-management",
            "title": "Cannabinoids for Pain Management: What the Science Says",
            "subtitle": "Exploring the evidence behind using cannabinoids for different types of pain",
            "summary": "Pain relief is one of the most common reasons people turn to cannabinoids. This article examines the scientific evidence behind using CBD, THC, and other cannabinoids for different types of pain, including chronic pain, neuropathic pain, and inflammatory pain.",
            "content": "<h2>Understanding Pain and the Endocannabinoid System</h2><p>Pain is a complex biological and psychological experience. It serves as an important warning system, but chronic pain can become debilitating and significantly impact quality of life. The endocannabinoid system (ECS) is involved in regulating pain sensation, making cannabinoids potentially valuable tools for pain management.</p>",
            "featured_image": "https://images.unsplash.com/photo-1595268746332-090e6b5fb9a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1595268746332-090e6b5fb9a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["science", "wellness"],
            "tag_ids": ["pain-management", "inflammation", "research"],
            "author_id": author_refs[0],
            "published_date": datetime.now() - timedelta(days=10),
            "reading_time": 15,
            "featured": False,
            "status": "published"
        }
    ]
    
    # Add articles to Firestore
    for article in articles:
        db.collection('articles').document(article["slug"]).set(article)
    
    # Return response with counts
    return SeedEducationResponse(
        message="Successfully seeded educational content",
        count=len(articles),
        categories_count=len(categories),
        tags_count=len(tags),
        authors_count=len(authors)
    )
