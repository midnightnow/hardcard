from fastapi import APIRouter, HTTPException
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
    details: dict


@router.post("/seed-education-content-basic")
def seed_education_content_basic() -> SeedResponse:
    """
    Seeds the Firestore database with initial educational content for the Hempex education hub.
    Creates categories, tags, authors, and articles.
    """
    try:
        # Count existing data before seeding
        existing_counts = {
            "article_categories": len(db.collection("article_categories").get()),
            "article_tags": len(db.collection("article_tags").get()),
            "article_authors": len(db.collection("article_authors").get()),
            "articles": len(db.collection("articles").get()),
        }

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

        # Seed tags
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

        # Seed authors
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

        # Seed articles
        articles = [
            {
                "slug": "what-is-cbd-beginners-guide",
                "title": "What is CBD? A Beginner's Guide",
                "subtitle": "Understanding the basics of cannabidiol and its potential benefits",
                "summary": "This comprehensive guide explains what CBD is, how it works in the body, and what potential benefits it may offer for wellness.",
                "content": """<p>Cannabidiol, commonly known as CBD, is one of over 100 chemical compounds called cannabinoids found in the cannabis plant. Unlike its cousin tetrahydrocannabinol (THC), CBD is non-intoxicating, meaning it doesn't produce the "high" associated with cannabis use.</p>

<h2>How CBD Works in the Body</h2>

<p>CBD interacts with your body's endocannabinoid system (ECS), a complex cell-signaling system that plays a role in regulating various functions and processes, including:</p>

<ul>
    <li>Sleep</li>
    <li>Mood</li>
    <li>Appetite</li>
    <li>Memory</li>
    <li>Reproduction and fertility</li>
    <li>Inflammation and immune response</li>
</ul>

<p>The ECS consists of endocannabinoids (molecules produced by your body), receptors that endocannabinoids and cannabinoids bond with, and enzymes that break down endocannabinoids and cannabinoids.</p>""",
                "featured_image": "https://images.unsplash.com/photo-1598963233122-778f8285a2c9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "category_ids": ["cbd-basics"],
                "tag_ids": ["beginner", "endocannabinoid-system"],
                "author_id": "author-1",
                "reading_time": 8,
                "featured": True,
                "status": "published",
                "references": [
                    "Russo EB. (2019). The Case for the Entourage Effect and Conventional Breeding of Clinical Cannabis: No \"Strain,\" No Gain. Front Plant Sci. 9:1969.",
                    "Kaur R, et al. (2016). Endocannabinoid System: A Multi-Facet Therapeutic Target. Curr Clin Pharmacol. 11(2):110-7.",
                ],
            },
            {
                "slug": "introduction-to-cbg-mother-cannabinoid",
                "title": "Introduction to CBG: The Mother of All Cannabinoids",
                "subtitle": "Exploring cannabigerol and its unique properties in the hemp plant",
                "summary": "Discover CBG (cannabigerol), a lesser-known but potentially powerful cannabinoid that serves as the precursor to other cannabinoids like CBD and THC.",
                "content": """<p>While CBD and THC often dominate the conversation about cannabinoids, cannabigerol (CBG) is emerging as a compound of significant interest in the scientific community. Often referred to as the "mother" or "stem cell" of cannabinoids, CBG plays a crucial role in the cannabis plant's biochemistry.</p>

<h2>What is CBG?</h2>

<p>Cannabigerol (CBG) is a non-intoxicating cannabinoid typically present in low levels (&lt;1%) in most cannabis strains. Its significance stems from its role as the precursor from which other cannabinoids are synthesized.</p>""",
                "featured_image": "https://images.unsplash.com/photo-1503262028195-93c528f03218?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2071&q=80",
                "category_ids": ["cbg-explained"],
                "tag_ids": ["beginner", "research"],
                "author_id": "author-1",
                "reading_time": 7,
                "featured": True,
                "status": "published",
                "references": [
                    "Nachnani R, et al. (2021). The pharmacological case for cannabigerol. J Pharmacol Exp Ther. 376(2):204-212.",
                ],
            },
            {
                "slug": "using-cbd-for-better-sleep",
                "title": "Using CBD for Better Sleep: What the Research Says",
                "subtitle": "A science-based look at how cannabidiol may help improve sleep quality",
                "summary": "Explore the potential of CBD for improving sleep quality, addressing insomnia, and establishing healthy sleep patterns based on current scientific understanding.",
                "content": """<p>Sleep difficulties affect millions of people worldwide, with consequences ranging from daytime fatigue to serious health problems. As conventional sleep medications often come with significant side effects and dependency risks, many are turning to cannabidiol (CBD) as a potential natural sleep aid. But what does the science actually say about CBD and sleep?</p>

<h2>How CBD Might Affect Sleep</h2>

<p>CBD may influence sleep through several mechanisms:</p>

<h3>Anxiety Reduction</h3>

<p>One of the most well-documented effects of CBD is its ability to reduce anxiety. Since anxiety and racing thoughts are common causes of insomnia, CBD's calming effect on the mind may help people fall asleep more easily.</p>""",
                "featured_image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2060&q=80",
                "category_ids": ["wellness", "science"],
                "tag_ids": ["sleep", "research", "dosage"],
                "author_id": "author-3",
                "reading_time": 10,
                "featured": True,
                "status": "published",
                "references": [
                    "Shannon S, et al. (2019). Cannabidiol in Anxiety and Sleep: A Large Case Series. Perm J. 23:18-041.",
                ],
            },
            {
                "slug": "understanding-cannabinoid-dosage",
                "title": "Understanding Cannabinoid Dosage: Finding Your Optimal Dose",
                "subtitle": "A practical guide to determining the right CBD or CBG dosage for your needs",
                "summary": "Learn about the factors that influence cannabinoid dosing, the concept of the biphasic effect, and practical strategies for finding your personal optimal dose.",
                "content": """<p>One of the most common questions people have when beginning their cannabinoid journey is: "How much should I take?" Unlike many conventional medications with standardized dosing, cannabinoid dosing is highly individualized, with the optimal amount varying widely from person to person.</p>

<h2>Why There's No Universal Dosage</h2>

<p>Cannabinoid dosing is influenced by numerous factors:</p>

<ul>
    <li><strong>Body weight and composition:</strong> Generally, higher body weight may require higher doses</li>
    <li><strong>Metabolism:</strong> Faster metabolizers may process cannabinoids more quickly</li>
    <li><strong>Endocannabinoid tone:</strong> Your body's baseline endocannabinoid activity</li>
</ul>""",
                "featured_image": "https://images.unsplash.com/photo-1579621970795-87facc2f976d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80",
                "category_ids": ["guides"],
                "tag_ids": ["dosage", "beginner"],
                "author_id": "author-2",
                "reading_time": 9,
                "featured": False,
                "status": "published",
                "references": [
                    "Millar SA, et al. (2019). A systematic review of cannabidiol dosing in clinical populations. Br J Clin Pharmacol. 85(9):1888-1900.",
                ],
            },
            {
                "slug": "the-endocannabinoid-system-explained",
                "title": "The Endocannabinoid System Explained",
                "subtitle": "Understanding the body's natural cannabinoid network and how plant cannabinoids interact with it",
                "summary": "A comprehensive look at the endocannabinoid system, its components, functions, and how plant-derived cannabinoids like CBD and CBG work within this system.",
                "content": """<p>Discovered only in the early 1990s, the endocannabinoid system (ECS) represents one of the most important physiological systems involved in establishing and maintaining human health. Despite its critical role in nearly every aspect of our physiology, the ECS isn't commonly discussed in medical education, leaving many healthcare providers and patients unaware of its significance.</p>

<h2>What is the Endocannabinoid System?</h2>

<p>The endocannabinoid system is a complex cell-signaling system that plays a role in regulating a wide range of functions and processes, including:</p>

<ul>
    <li>Mood and stress response</li>
    <li>Sleep</li>
    <li>Appetite and digestion</li>
    <li>Metabolism</li>
</ul>""",
                "featured_image": "https://images.unsplash.com/photo-1559757175-7cb057cecfc9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2073&q=80",
                "category_ids": ["science"],
                "tag_ids": ["endocannabinoid-system", "research", "advanced"],
                "author_id": "author-1",
                "reading_time": 12,
                "featured": False,
                "status": "published",
                "references": [
                    "Pacher P, et al. (2006). The endocannabinoid system as an emerging target of pharmacotherapy. Pharmacol Rev. 58(3):389-462.",
                ],
            },
        ]

        # Add articles to Firestore
        for article in articles:
            # Set timestamps for published_date
            article["published_date"] = firestore.SERVER_TIMESTAMP
                
            doc_ref = db.collection("articles").document(article["slug"])
            doc_ref.set(article)

        # Count data after seeding
        final_counts = {
            "article_categories": len(db.collection("article_categories").get()),
            "article_tags": len(db.collection("article_tags").get()),
            "article_authors": len(db.collection("article_authors").get()),
            "articles": len(db.collection("articles").get()),
        }

        # Calculate new records added
        added_counts = {
            k: final_counts[k] - existing_counts.get(k, 0) for k in final_counts
        }

        return SeedResponse(
            success=True,
            message="Educational content successfully seeded!",
            details={
                "added": added_counts,
                "final": final_counts,
            },
        )

    except Exception as e:
        print(f"Error seeding data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error seeding data: {str(e)}")
