from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import databutton as db
from datetime import datetime, date
import json
import uuid

router = APIRouter()

# Models for Literary Journey
class BookProgress(BaseModel):
    status: str = Field(description="Status of the book - 'not_started', 'in_progress', 'completed'")
    completion_date: Optional[str] = None
    notes: Optional[str] = None
    is_gifted: bool = False
    gifted_date: Optional[str] = None

class FinancialConcept(BaseModel):
    name: str
    description: str
    difficulty: str
    examples: List[str]

class LiteraryWork(BaseModel):
    id: str
    title: str
    author: str
    description: str
    publication_year: Optional[int] = None
    age_recommendation: int
    financial_concept: Optional[FinancialConcept] = None
    image_url: Optional[str] = None
    amazon_url: Optional[str] = None

class AgeGroupLiterature(BaseModel):
    age: int
    description: str
    books: List[LiteraryWork]

class LiteraryJourneyStatus(BaseModel):
    profile_id: str
    books_progress: Dict[str, BookProgress] = {}
    last_updated: str

class EnlightenmentJourneyResponse(BaseModel):
    profile_id: str
    age_groups: List[AgeGroupLiterature]
    profile_progress: Optional[LiteraryJourneyStatus] = None

# Book details response model
class BookDetailsResponse(BaseModel):
    id: str
    title: str
    author: str
    description: str
    full_summary: str
    publication_year: Optional[int] = None
    age_recommendation: int
    financial_concept: Optional[FinancialConcept] = None
    image_url: Optional[str] = None
    amazon_url: Optional[str] = None
    key_takeaways: List[str]
    discussion_questions: List[str]
    related_books: List[str]

# Update book progress request model
class UpdateBookProgressRequest(BaseModel):
    profile_id: str
    book_id: str
    status: Optional[str] = None
    completion_date: Optional[str] = None
    notes: Optional[str] = None
    is_gifted: Optional[bool] = None

# Sample data for the literary journey
AGE_GROUPS_DATA = [
    {
        "age": 5,
        "description": "Early foundations of financial literacy and value.",
        "books": [
            {
                "id": "money-adventure",
                "title": "The Money Adventure",
                "author": "Sarah Green",
                "description": "A colorful introduction to the basics of money for young children.",
                "publication_year": 2019,
                "age_recommendation": 5,
                "financial_concept": {
                    "name": "Basic Value",
                    "description": "Understanding that money represents value and can be exchanged for goods.",
                    "difficulty": "Beginner",
                    "examples": ["Trading coins for candy", "Earning money for simple chores"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?children,money",
                "amazon_url": "https://www.amazon.com"
            },
            {
                "id": "giving-book",
                "title": "The Giving Book",
                "author": "Ellen Sabin",
                "description": "A book that teaches children about the importance of generosity and sharing resources.",
                "publication_year": 2015,
                "age_recommendation": 6,
                "financial_concept": {
                    "name": "Generosity",
                    "description": "Understanding that we can use money to help others.",
                    "difficulty": "Beginner",
                    "examples": ["Donating to charity", "Buying gifts for others"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?giving,charity",
                "amazon_url": "https://www.amazon.com"
            }
        ]
    },
    {
        "age": 9,
        "description": "Building core financial understanding and historical context.",
        "books": [
            {
                "id": "how-economy-works",
                "title": "How the Economy Works",
                "author": "James Robinson",
                "description": "A child-friendly introduction to basic economic principles.",
                "publication_year": 2017,
                "age_recommendation": 9,
                "financial_concept": {
                    "name": "Economic Systems",
                    "description": "Understanding how goods and services are created and exchanged in society.",
                    "difficulty": "Intermediate",
                    "examples": ["Markets and trade", "Jobs and businesses"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?economy,market",
                "amazon_url": "https://www.amazon.com"
            },
            {
                "id": "richest-babylon",
                "title": "The Richest Man in Babylon (Young Reader's Edition)",
                "author": "George S. Clason (adapted)",
                "description": "Ancient wisdom about money management adapted for young readers.",
                "publication_year": 2018,
                "age_recommendation": 10,
                "financial_concept": {
                    "name": "Saving",
                    "description": "The principle of paying yourself first and building wealth gradually.",
                    "difficulty": "Intermediate",
                    "examples": ["Saving a portion of all income", "The power of consistency"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?ancient,wealth",
                "amazon_url": "https://www.amazon.com"
            }
        ]
    },
    {
        "age": 13,
        "description": "Introduction to philosophy and deeper financial concepts.",
        "books": [
            {
                "id": "sophies-world",
                "title": "Sophie's World",
                "author": "Jostein Gaarder",
                "description": "A novel about the history of philosophy, presented through the eyes of a young girl.",
                "publication_year": 1991,
                "age_recommendation": 13,
                "financial_concept": {
                    "name": "Value Philosophy",
                    "description": "Philosophical perspectives on what creates value in society.",
                    "difficulty": "Intermediate",
                    "examples": ["Subjective vs. objective value", "Intrinsic vs. instrumental value"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?philosophy,thinking",
                "amazon_url": "https://www.amazon.com"
            },
            {
                "id": "bitcoin-money",
                "title": "Bitcoin Money: A Tale of Bitville",
                "author": "Michael Caras",
                "description": "An introduction to Bitcoin concepts through storytelling.",
                "publication_year": 2019,
                "age_recommendation": 13,
                "financial_concept": {
                    "name": "Digital Scarcity",
                    "description": "Understanding how Bitcoin creates digital scarcity and acts as money.",
                    "difficulty": "Intermediate",
                    "examples": ["Limited supply", "Digital ownership"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?bitcoin,digital",
                "amazon_url": "https://www.amazon.com"
            }
        ]
    },
    {
        "age": 16,
        "description": "Advanced financial concepts and deeper philosophical exploration.",
        "books": [
            {
                "id": "psychology-of-money",
                "title": "The Psychology of Money",
                "author": "Morgan Housel",
                "description": "Timeless lessons on wealth, greed, and happiness.",
                "publication_year": 2020,
                "age_recommendation": 16,
                "financial_concept": {
                    "name": "Behavioral Finance",
                    "description": "How psychology affects our financial decisions.",
                    "difficulty": "Advanced",
                    "examples": ["Status seeking vs. wealth building", "Long-term vs. short-term thinking"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?psychology,finance",
                "amazon_url": "https://www.amazon.com"
            },
            {
                "id": "bitcoin-standard",
                "title": "The Bitcoin Standard",
                "author": "Saifedean Ammous",
                "description": "The decentralized alternative to central banking and its implications.",
                "publication_year": 2018,
                "age_recommendation": 17,
                "financial_concept": {
                    "name": "Sound Money",
                    "description": "The historical evolution of money and Bitcoin's place in monetary history.",
                    "difficulty": "Advanced",
                    "examples": ["Monetary inflation", "Store of value properties"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?bitcoin,gold",
                "amazon_url": "https://www.amazon.com"
            }
        ]
    },
    {
        "age": 18,
        "description": "Adult financial wisdom and investment philosophy.",
        "books": [
            {
                "id": "intelligent-investor",
                "title": "The Intelligent Investor",
                "author": "Benjamin Graham",
                "description": "The definitive book on value investing.",
                "publication_year": 1949,
                "age_recommendation": 18,
                "financial_concept": {
                    "name": "Value Investing",
                    "description": "The disciplined approach to finding undervalued investments.",
                    "difficulty": "Advanced",
                    "examples": ["Margin of safety", "Mr. Market analogy"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?investment,stocks",
                "amazon_url": "https://www.amazon.com"
            },
            {
                "id": "almanack-ravikant",
                "title": "The Almanack of Naval Ravikant",
                "author": "Eric Jorgenson",
                "description": "A guide to wealth and happiness from a modern philosopher.",
                "publication_year": 2020,
                "age_recommendation": 18,
                "financial_concept": {
                    "name": "Leverage and Specific Knowledge",
                    "description": "How to create wealth by applying unique skills with leverage.",
                    "difficulty": "Advanced",
                    "examples": ["Code and media as leverage", "Building specific knowledge"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?wisdom,future",
                "amazon_url": "https://www.amazon.com"
            }
        ]
    },
    {
        "age": 25,
        "description": "Legacy thinking and philosophical maturity.",
        "books": [
            {
                "id": "meditations",
                "title": "Meditations",
                "author": "Marcus Aurelius",
                "description": "Stoic philosophy from the Roman Emperor, teaching resilience and virtue.",
                "publication_year": 180,
                "age_recommendation": 25,
                "financial_concept": {
                    "name": "Stoic Wealth Philosophy",
                    "description": "The proper relationship between wealth and virtue.",
                    "difficulty": "Advanced",
                    "examples": ["Wealth as preferred indifferent", "Internal vs. external value"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?stoicism,roman",
                "amazon_url": "https://www.amazon.com"
            },
            {
                "id": "skin-in-game",
                "title": "Skin in the Game",
                "author": "Nassim Nicholas Taleb",
                "description": "The asymmetries of risk and reward in life, markets, and human affairs.",
                "publication_year": 2018,
                "age_recommendation": 25,
                "financial_concept": {
                    "name": "Risk Asymmetry",
                    "description": "How having personal risk exposure creates better systems and decisions.",
                    "difficulty": "Advanced",
                    "examples": ["Transferring vs. bearing risk", "Ergodicity in financial decisions"]
                },
                "image_url": "https://source.unsplash.com/featured/300x500/?risk,game",
                "amazon_url": "https://www.amazon.com"
            }
        ]
    }
]

# Book details data
BOOK_DETAILS = {
    "money-adventure": {
        "id": "money-adventure",
        "title": "The Money Adventure",
        "author": "Sarah Green",
        "description": "A colorful introduction to the basics of money for young children.",
        "full_summary": "The Money Adventure follows twins Alex and Ava as they discover the world of money through a magical adventure. When they find an old coin in their grandmother's attic, it transports them to Coinsville, a place where every object has a clear value and people trade with golden tokens. Through their journey, the twins learn about earning, saving, spending, and sharing money. They meet wise characters like Penny the owl who teaches them about patience and saving, and Generous George who shows them the joy of giving. By the end of their adventure, Alex and Ava understand that money is a tool that can help them achieve goals and help others.",
        "publication_year": 2019,
        "age_recommendation": 5,
        "financial_concept": {
            "name": "Basic Value",
            "description": "Understanding that money represents value and can be exchanged for goods.",
            "difficulty": "Beginner",
            "examples": ["Trading coins for candy", "Earning money for simple chores"]
        },
        "image_url": "https://source.unsplash.com/featured/300x500/?children,money",
        "amazon_url": "https://www.amazon.com",
        "key_takeaways": [
            "Money represents value and helps us trade",
            "We can earn money by helping others",
            "Saving means keeping money for later",
            "We can use money to help others through sharing"
        ],
        "discussion_questions": [
            "What's something you would like to save money for?",
            "How could you earn money by helping others?",
            "If you had $10, how would you divide it between spending, saving, and sharing?",
            "Why do you think different things cost different amounts of money?"
        ],
        "related_books": ["giving-book"]
    },
    "sophies-world": {
        "id": "sophies-world",
        "title": "Sophie's World",
        "author": "Jostein Gaarder",
        "description": "A novel about the history of philosophy, presented through the eyes of a young girl.",
        "full_summary": "Sophie's World tells the story of 14-year-old Sophie Amundsen, who begins receiving mysterious letters asking deep philosophical questions like 'Who are you?' and 'Where does the world come from?' These letters turn out to be from Alberto Knox, an enigmatic philosopher who begins giving Sophie a comprehensive course on the history of Western philosophy, from the pre-Socratics through Socrates, Plato, Aristotle, medieval Christian philosophy, the Renaissance, Enlightenment thinkers like Descartes, Spinoza and Locke, the Romantics, Hegel, Marx, Darwin, Freud and Sartre. As Sophie learns about these philosophical traditions, she discovers that she and Alberto may actually be characters in a book written by a man named Albert Knag for his daughter Hilde. The novel weaves together Sophie's education in philosophy with a meta-narrative that raises questions about reality, consciousness, and free will.",
        "publication_year": 1991,
        "age_recommendation": 13,
        "financial_concept": {
            "name": "Value Philosophy",
            "description": "Philosophical perspectives on what creates value in society.",
            "difficulty": "Intermediate",
            "examples": ["Subjective vs. objective value", "Intrinsic vs. instrumental value"]
        },
        "image_url": "https://source.unsplash.com/featured/300x500/?philosophy,thinking",
        "amazon_url": "https://www.amazon.com",
        "key_takeaways": [
            "Philosophy helps us question our assumptions about reality",
            "Different philosophical traditions offer diverse perspectives on value and meaning",
            "Critical thinking allows us to evaluate claims about what matters",
            "Our understanding of the world shapes how we interact with it"
        ],
        "discussion_questions": [
            "How does understanding philosophy help us make better decisions about money and value?",
            "Do you think value is something objective in the world or created by people's minds?",
            "Which philosopher from the book do you most agree with about what makes a good life?",
            "How might different philosophical perspectives view something like Bitcoin differently?"
        ],
        "related_books": ["meditations", "bitcoin-money"]
    }
    # Additional book details would be defined similarly
}

def get_storage_key(profile_id):
    """Create a sanitized storage key for the profile's journey data"""
    return f"literary_journey_{profile_id.replace('-', '_')}"

def get_profile_progress(profile_id):
    """Retrieve the profile's reading progress from storage"""
    try:
        key = get_storage_key(profile_id)
        data = db.storage.json.get(key, default=None)
        if data:
            return LiteraryJourneyStatus(**data)
        return None
    except Exception as e:
        print(f"Error retrieving profile progress: {e}")
        return None

def save_profile_progress(profile_id, progress_data):
    """Save the profile's reading progress to storage"""
    try:
        key = get_storage_key(profile_id)
        db.storage.json.put(key, progress_data.dict())
        return True
    except Exception as e:
        print(f"Error saving profile progress: {e}")
        return False

@router.get("/get-literary-journey")
def get_literary_journey_endpoint(profileId: str):
    """Get the literary journey data for a profile"""
    try:
        # Convert data to Pydantic models
        age_groups = [AgeGroupLiterature(**group) for group in AGE_GROUPS_DATA]
        
        # Get profile progress from storage
        profile_progress = get_profile_progress(profileId)
        
        # If no progress exists yet, initialize it
        if not profile_progress:
            profile_progress = LiteraryJourneyStatus(
                profile_id=profileId,
                books_progress={},
                last_updated=datetime.now().isoformat()
            )
            save_profile_progress(profileId, profile_progress)
        
        return EnlightenmentJourneyResponse(
            profile_id=profileId,
            age_groups=age_groups,
            profile_progress=profile_progress
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving literary journey: {str(e)}")

@router.get("/get-book-details")
def get_book_details_endpoint(bookId: str):
    """Get detailed information about a specific book"""
    if bookId not in BOOK_DETAILS:
        # If we don't have detailed info, try to find basic info
        for group in AGE_GROUPS_DATA:
            for book in group["books"]:
                if book["id"] == bookId:
                    # Create a response with available data and placeholders
                    return BookDetailsResponse(
                        **book,
                        full_summary=book["description"],
                        key_takeaways=["Information not available"],
                        discussion_questions=["Information not available"],
                        related_books=[]
                    )
        raise HTTPException(status_code=404, detail=f"Book with ID {bookId} not found")
    
    return BookDetailsResponse(**BOOK_DETAILS[bookId])

@router.post("/update-book-progress")
def update_book_progress_journey(request: UpdateBookProgressRequest):
    """Update a profile's progress on a specific book"""
    try:
        profile_id = request.profile_id
        book_id = request.book_id
        
        # Get current progress
        profile_progress = get_profile_progress(profile_id)
        if not profile_progress:
            profile_progress = LiteraryJourneyStatus(
                profile_id=profile_id,
                books_progress={},
                last_updated=datetime.now().isoformat()
            )
        
        # Update book progress
        if book_id not in profile_progress.books_progress:
            profile_progress.books_progress[book_id] = BookProgress(
                status="not_started",
                is_gifted=False
            )
        
        # Update fields if provided
        current_progress = profile_progress.books_progress[book_id]
        
        if request.status is not None:
            current_progress.status = request.status
            if request.status == "completed" and not current_progress.completion_date:
                current_progress.completion_date = request.completion_date or datetime.now().isoformat()
        
        if request.notes is not None:
            current_progress.notes = request.notes
            
        if request.is_gifted is not None and request.is_gifted != current_progress.is_gifted:
            current_progress.is_gifted = request.is_gifted
            if request.is_gifted and not current_progress.gifted_date:
                current_progress.gifted_date = datetime.now().isoformat()
        
        # Update progress in storage
        profile_progress.last_updated = datetime.now().isoformat()
        profile_progress.books_progress[book_id] = current_progress
        save_profile_progress(profile_id, profile_progress)
        
        # Return updated journey data
        return get_literary_journey(profile_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating book progress: {str(e)}")
