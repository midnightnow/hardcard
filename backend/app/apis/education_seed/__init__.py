from fastapi import APIRouter, HTTPException, Query
from firebase_admin import firestore
import databutton as db
import firebase_admin
from firebase_admin import credentials
import json
import datetime
from pydantic import BaseModel

# Initialize Firebase Admin SDK if not already initialized
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(json.loads(db.secrets.get("FIREBASE_SERVICE_ACCOUNT")))
    app = firebase_admin.initialize_app(cred)

router = APIRouter()
db = firestore.client()


class SeedResponse(BaseModel):
    success: bool
    message: str
    count: int
    categories_count: int
    tags_count: int
    authors_count: int


@router.post("/seed-education-content")
def seed_education_content(force_reset: bool = False) -> SeedResponse:
    """
    Seeds the Firestore database with initial educational content for the Hempex education hub.
    Creates categories, tags, authors, and articles.
    """
    try:
        # If force_reset is True, delete existing data
        if force_reset:
            # Delete all collections
            for collection_name in ["article_categories", "article_tags", "article_authors", "articles"]:
                docs = db.collection(collection_name).stream()
                for doc in docs:
                    doc.reference.delete()
            
        # Count existing data before seeding
        categories_count = len(list(db.collection("article_categories").stream()))
        tags_count = len(list(db.collection("article_tags").stream()))
        authors_count = len(list(db.collection("article_authors").stream()))
        articles_count = len(list(db.collection("articles").stream()))

        # Only seed if collections are empty or force_reset is True
        if categories_count == 0 or force_reset:
            # Seed categories
            categories = [
                {
                    "name": "CBD Basics",
                    "description": "Fundamental information about CBD, what it is, and how it works.",
                    "icon": "book-open",
                    "order": 1,
                    "slug": "cbd-basics",
                    "active": True,
                },
                {
                    "name": "CBG Explained",
                    "description": "Learn about CBG, the 'mother cannabinoid' and its potential benefits.",
                    "icon": "flask",
                    "order": 2,
                    "slug": "cbg-explained",
                    "active": True,
                },
                {
                    "name": "Wellness Applications",
                    "description": "How cannabinoids can be used to support overall wellness and health.",
                    "icon": "heart",
                    "order": 3,
                    "slug": "wellness",
                    "active": True,
                },
                {
                    "name": "The Science",
                    "description": "Scientific research and studies on cannabinoids and the endocannabinoid system.",
                    "icon": "microscope",
                    "order": 4,
                    "slug": "science",
                    "active": True,
                },
                {
                    "name": "How-to Guides",
                    "description": "Practical guides on using cannabinoid products effectively.",
                    "icon": "map",
                    "order": 5,
                    "slug": "guides",
                    "active": True,
                },
            ]

            category_refs = {}
            for category in categories:
                doc_ref = db.collection("article_categories").document(category["slug"])
                doc_ref.set(category)
                category_refs[category["slug"]] = doc_ref
            
            categories_count = len(categories)
        else:
            category_refs = {}
            for doc in db.collection("article_categories").stream():
                category_data = doc.to_dict()
                category_refs[category_data.get("slug", doc.id)] = doc.reference

        # Seed tags only if empty or force reset
        if tags_count == 0 or force_reset:
            tags = [
                {"name": "Beginner", "slug": "beginner"},
                {"name": "Advanced", "slug": "advanced"},
                {"name": "Pain Management", "slug": "pain-management"},
                {"name": "Sleep", "slug": "sleep"},
                {"name": "Anxiety", "slug": "anxiety"},
                {"name": "Dosage", "slug": "dosage"},
                {"name": "Research", "slug": "research"},
                {"name": "Products", "slug": "products"},
                {"name": "Endocannabinoid System", "slug": "endocannabinoid-system"},
                {"name": "Legal", "slug": "legal"},
            ]

            tag_refs = {}
            for tag in tags:
                doc_ref = db.collection("article_tags").document(tag["slug"])
                doc_ref.set(tag)
                tag_refs[tag["slug"]] = doc_ref
                
            tags_count = len(tags)
        else:
            tag_refs = {}
            for doc in db.collection("article_tags").stream():
                tag_data = doc.to_dict()
                tag_refs[tag_data.get("slug", doc.id)] = doc.reference

        # Seed authors only if empty or force reset
        if authors_count == 0 or force_reset:
            authors = [
                {
                    "name": "Dr. Sarah Mitchell",
                    "bio": "Pharmacologist with a focus on cannabinoid research and clinical applications.",
                    "avatar_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                    "credentials": "Ph.D. in Pharmacology",
                },
                {
                    "name": "James Wilson",
                    "bio": "Certified herbalist and wellness consultant specializing in plant-based remedies.",
                    "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                    "credentials": "Certified Herbalist",
                },
                {
                    "name": "Emily Chen",
                    "bio": "Naturopathic doctor focused on integrative approaches to chronic pain and inflammation.",
                    "avatar_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1061&q=80",
                    "credentials": "N.D.",
                },
            ]

            author_refs = {}
            for i, author in enumerate(authors):
                doc_ref = db.collection("article_authors").document(f"author-{i+1}")
                doc_ref.set(author)
                author_refs[f"author-{i+1}"] = doc_ref
                
            authors_count = len(authors)
        else:
            author_refs = {}
            for doc in db.collection("article_authors").stream():
                author_refs[doc.id] = doc.reference

        # Seed articles only if empty or force reset
        articles_created = 0
        if articles_count == 0 or force_reset:
            articles = [{"author_id": "author-1", "category_ids": ["cbd-basics"], "content": "<p>Cannabidiol, commonly known as CBD, is one of over 100 chemical compounds called cannabinoids found in the cannabis plant. Unlike its cousin tetrahydrocannabinol (THC), CBD is non-intoxicating, meaning it doesn't produce the \"high\" associated with cannabis use.</p>\n\n<h2>How CBD Works in the Body</h2>\n\n<p>CBD interacts with your body's endocannabinoid system (ECS), a complex cell-signaling system that plays a role in regulating various functions and processes, including:</p>\n\n<ul>\n<li>Sleep</li>\n<li>Mood</li>\n<li>Appetite</li>\n<li>Memory</li>\n<li>Reproduction and fertility</li>\n<li>Inflammation and immune response</li>\n</ul>\n\n<p>The ECS consists of endocannabinoids (molecules produced by your body), receptors that endocannabinoids and cannabinoids bond with, and enzymes that break down endocannabinoids and cannabinoids.</p>\n\n<p>CBD doesn't bind directly to cannabinoid receptors but instead influences the ECS indirectly, potentially enhancing your body's use of its own endocannabinoids.</p>\n\n<h2>Potential Benefits of CBD</h2>\n\n<p>Research into CBD is still evolving, but early studies and anecdotal evidence suggest it may offer benefits for:</p>\n\n<ul>\n<li><strong>Pain management:</strong> CBD may help reduce chronic pain by influencing endocannabinoid receptor activity, reducing inflammation, and interacting with neurotransmitters.</li>\n<li><strong>Anxiety and depression:</strong> CBD has shown promise in treating anxiety and depression, potentially related to its ability to act on brain receptors for serotonin.</li>\n<li><strong>Sleep improvement:</strong> By addressing causes of sleeplessness like anxiety, pain, and restlessness, CBD may help improve sleep quality.</li>\n<li><strong>Neuroprotection:</strong> CBD's anti-inflammatory and antioxidant properties might protect against neurological diseases.</li>\n</ul>\n\n<h2>Common CBD Products</h2>\n\n<p>CBD is available in various forms, each with different onset times, durations, and use cases:</p>\n\n<ul>\n<li><strong>Oils and tinctures:</strong> Taken sublingually (under the tongue) for faster absorption or added to food and drinks.</li>\n<li><strong>Capsules and softgels:</strong> Convenient, pre-measured doses that are swallowed like traditional supplements.</li>\n<li><strong>Edibles:</strong> CBD-infused gummies, chocolates, and other food products offer a tasty way to consume CBD.</li>\n<li><strong>Topicals:</strong> Creams, balms, and lotions applied directly to the skin for localized relief.</li>\n<li><strong>Vape products:</strong> Inhalation delivers CBD quickly to the bloodstream, though this method raises health concerns.</li>\n</ul>\n\n<h2>Tips for CBD Beginners</h2>\n\n<ol>\n<li><strong>Start low and go slow:</strong> Begin with a low dose and gradually increase until you find your optimal dose.</li>\n<li><strong>Be patient:</strong> CBD effects can be subtle and may take time to become noticeable, especially for chronic conditions.</li>\n<li><strong>Consult healthcare providers:</strong> Discuss CBD use with your doctor, especially if you take other medications, due to potential interactions.</li>\n<li><strong>Choose quality products:</strong> Look for CBD from reputable manufacturers that provide third-party lab tests verifying content and purity.</li>\n<li><strong>Consider full-spectrum vs. isolate:</strong> Full-spectrum products contain other beneficial cannabis compounds, while isolates contain only CBD.</li>\n</ol>\n\n<p>As research continues to expand our understanding of CBD, its potential role in wellness routines becomes increasingly promising. Remember that individual experiences with CBD can vary significantly, and finding the right product and dosage for your needs may require some experimentation.</p>\n", "featured": True, "featured_image": "https://images.unsplash.com/photo-1598963233122-778f8285a2c9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80", "published_date": datetime.datetime.now() - datetime.timedelta(days=30), "reading_time": 8, "references": ["Russo EB. (2019). The Case for the Entourage Effect and Conventional Breeding of Clinical Cannabis: No \"Strain,\" No Gain. Front Plant Sci. 9:1969.", "Kaur R, et al. (2016). Endocannabinoid System: A Multi-Facet Therapeutic Target. Curr Clin Pharmacol. 11(2):110-7.", "Corroon J, Phillips JA. (2018). A Cross-Sectional Study of Cannabidiol Users. Cannabis Cannabinoid Res. 3(1):152-161."], "slug": "what-is-cbd-beginners-guide", "status": "published", "subtitle": "Understanding the basics of cannabidiol and its potential benefits", "summary": "This comprehensive guide explains what CBD is, how it works in the body, and what potential benefits it may offer for wellness.", "tag_ids": ["beginner", "endocannabinoid-system"], "title": "What is CBD? A Beginner's Guide"}]

            for article in articles:
                doc_ref = db.collection("articles").document(article["slug"])
                doc_ref.set(article)

            articles_created = len(articles)
        
        return SeedResponse(
            success=True,
            message=f"Successfully seeded education content with {articles_created} articles.",
            count=articles_created,
            categories_count=categories_count,
            tags_count=tags_count,
            authors_count=authors_count,
        )
        
    except Exception as e:
        return SeedResponse(
            success=False,
            message=f"Error seeding education content: {str(e)}",
            count=0,
            categories_count=0,
            tags_count=0,
            authors_count=0,
        )


@router.post("/seed-education-simple")
def seed_education_simple() -> SeedResponse:
    """
    Seeds sample educational content. This is a simplified version of seed-education-content endpoint.
    """
    return seed_education_content(force_reset=True)
