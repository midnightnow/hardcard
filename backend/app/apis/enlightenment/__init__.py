from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import databutton as db
import re
from datetime import datetime

router = APIRouter()

# Schemas
class Book(BaseModel):
    id: str
    title: str
    author: str
    age_group: str
    description: str
    financial_concept: str
    difficulty: str = "Medium"
    image_url: Optional[str] = None
    amazon_url: Optional[str] = None

class BookStatus(BaseModel):
    is_completed: bool = False
    is_gifted: bool = False
    completion_date: Optional[str] = None
    gifted_date: Optional[str] = None
    notes: Optional[str] = None

class BookProgress(BaseModel):
    book_id: str
    status: BookStatus

class EnlightenmentJourney(BaseModel):
    profile_id: str
    books_progress: List[BookProgress] = []

class UpdateRequest(BaseModel):
    is_completed: Optional[bool] = None
    is_gifted: Optional[bool] = None
    notes: Optional[str] = None

# Helper functions
def sanitize_key(key):
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_books():
    try:
        data = db.storage.json.get("enlightenment_books", default=[])
        return [Book(**item) for item in data]
    except Exception as e:
        print(f"Error getting books: {e}")
        return []

def save_books(books):
    data = [book.dict() for book in books]
    db.storage.json.put(sanitize_key("enlightenment_books"), data)

def get_journey(profile_id):
    try:
        journeys = db.storage.json.get("enlightenment_journeys", default={})
        if profile_id in journeys:
            return EnlightenmentJourney(**journeys[profile_id])
        return None
    except Exception as e:
        print(f"Error getting journey: {e}")
        return None

def save_journey(journey):
    try:
        journeys = db.storage.json.get("enlightenment_journeys", default={})
        journeys[journey.profile_id] = journey.dict()
        db.storage.json.put(sanitize_key("enlightenment_journeys"), journeys)
    except Exception as e:
        print(f"Error saving journey: {e}")

# API Endpoints
@router.get("/enlightenment-journey/{profile_id}")
def get_enlightenment_journey(profile_id: str):
    """Get a profile's enlightenment journey"""
    # Get all books
    books = get_books()
    books_dict = {book.id: book for book in books}
    
    # Try to get existing journey
    journey = get_journey(profile_id)
    
    # If journey doesn't exist, create a new one with all books
    if not journey:
        books_progress = []
        for book in books:
            books_progress.append(BookProgress(
                book_id=book.id,
                status=BookStatus()
            ))
        
        journey = EnlightenmentJourney(
            profile_id=profile_id,
            books_progress=books_progress
        )
        save_journey(journey)
    
    # Create response with combined book details and progress
    result = {
        "profile_id": profile_id,
        "books": []
    }
    
    # Combine book details with progress status
    for progress in journey.books_progress:
        if progress.book_id in books_dict:
            book = books_dict[progress.book_id]
            result["books"].append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "age_group": book.age_group,
                "description": book.description,
                "financial_concept": book.financial_concept,
                "difficulty": book.difficulty,
                "image_url": book.image_url,
                "amazon_url": book.amazon_url,
                "status": progress.status.dict()
            })
    
    # Group books by age group
    books_by_age = {}
    for book in result["books"]:
        age_group = book["age_group"]
        if age_group not in books_by_age:
            books_by_age[age_group] = []
        books_by_age[age_group].append(book)
    
    result["by_age_group"] = books_by_age
    
    return result

@router.put("/enlightenment-journey/{profile_id}/book/{book_id}")
def update_book_progress_endpoint(profile_id: str, book_id: str, update_data: UpdateRequest):
    """Update reading progress for a book"""
    # Get journey for profile
    journey = get_journey(profile_id)
    if not journey:
        # Create new journey if it doesn't exist
        books = get_books()
        books_progress = []
        for book in books:
            books_progress.append(BookProgress(
                book_id=book.id,
                status=BookStatus()
            ))
        
        journey = EnlightenmentJourney(
            profile_id=profile_id,
            books_progress=books_progress
        )
    
    # Find and update the book progress
    book_found = False
    for progress in journey.books_progress:
        if progress.book_id == book_id:
            book_found = True
            
            # Update completed status if provided
            if update_data.is_completed is not None:
                progress.status.is_completed = update_data.is_completed
                if update_data.is_completed:
                    progress.status.completion_date = datetime.now().strftime("%Y-%m-%d")
            
            # Update gifted status if provided
            if update_data.is_gifted is not None:
                progress.status.is_gifted = update_data.is_gifted
                if update_data.is_gifted:
                    progress.status.gifted_date = datetime.now().strftime("%Y-%m-%d")
            
            # Update notes if provided
            if update_data.notes is not None:
                progress.status.notes = update_data.notes
            
            break
    
    # Save updated journey
    save_journey(journey)
    
    # Return updated journey
    return get_enlightenment_journey(profile_id)

# Initialize default books if none exist
def initialize_default_books():
    books = get_books()
    if books:
        return
    
    default_books = [
        Book(
            id="money-adventure",
            title="The Berenstain Bears Trouble with Money",
            author="Stan and Jan Berenstain",
            age_group="Ages 5-8",
            description="Brother and Sister Bear learn about earning and saving money.",
            financial_concept="Basic money concepts",
            difficulty="Easy",
            image_url="https://m.media-amazon.com/images/I/91MK0d+wMuL._AC_UF1000,1000_QL80_.jpg"
        ),
        Book(
            id="giving-book",
            title="The Giving Book",
            author="Ellen Sabin",
            age_group="Ages 5-8",
            description="Interactive lessons about giving and sharing wealth with others.",
            financial_concept="Philanthropy and sharing resources",
            difficulty="Easy"
        ),
        Book(
            id="richest-babylon",
            title="The Richest Man in Babylon",
            author="George S. Clason",
            age_group="Ages 9-12",
            description="Ancient parables offering timeless financial wisdom in simple stories.",
            financial_concept="Saving and investing",
            difficulty="Medium"
        ),
        Book(
            id="how-economy-works",
            title="How an Economy Grows and Why It Crashes",
            author="Peter Schiff and Andrew Schiff",
            age_group="Ages 9-12",
            description="Uses a simple story about fish to explain economic principles.",
            financial_concept="Economic principles",
            difficulty="Medium"
        ),
        Book(
            id="sophies-world",
            title="Sophies World",
            author="Jostein Gaarder",
            age_group="Ages 13-15",
            description="A novel that takes readers on a journey through philosophy.",
            financial_concept="Critical thinking",
            difficulty="Medium"
        ),
        Book(
            id="bitcoin-money",
            title="Bitcoin Money A Tale of Bitville",
            author="Michael Caras",
            age_group="Ages 13-15",
            description="An accessible introduction to Bitcoin through an allegorical tale.",
            financial_concept="Digital currency basics",
            difficulty="Medium"
        ),
        Book(
            id="psychology-of-money",
            title="The Psychology of Money",
            author="Morgan Housel",
            age_group="Ages 16-18",
            description="Timeless lessons on wealth, greed, and happiness through stories.",
            financial_concept="Behavioral finance",
            difficulty="Medium"
        ),
        Book(
            id="bitcoin-standard",
            title="The Bitcoin Standard",
            author="Saifedean Ammous",
            age_group="Ages 16-18",
            description="A comprehensive look at the history of money and Bitcoin.",
            financial_concept="Monetary history",
            difficulty="Hard"
        ),
        Book(
            id="intelligent-investor",
            title="The Intelligent Investor",
            author="Benjamin Graham",
            age_group="Ages 19-24",
            description="The definitive book on value investing strategy.",
            financial_concept="Value investing",
            difficulty="Hard"
        ),
        Book(
            id="antifragile",
            title="Antifragile",
            author="Nassim Nicholas Taleb",
            age_group="Ages 19-24",
            description="Explores systems that benefit from volatility and uncertainty.",
            financial_concept="Risk and uncertainty",
            difficulty="Hard"
        ),
        Book(
            id="almanack-ravikant",
            title="The Almanack of Naval Ravikant",
            author="Eric Jorgenson",
            age_group="Ages 25+",
            description="A guide to wealth and happiness from a philosopher-entrepreneur.",
            financial_concept="Wealth creation",
            difficulty="Medium"
        ),
        Book(
            id="meditations",
            title="Meditations",
            author="Marcus Aurelius",
            age_group="Ages 25+",
            description="Ancient Stoic wisdom on virtue, rationality, and inner peace.",
            financial_concept="Stoic philosophy",
            difficulty="Medium"
        )
    ]
    
    save_books(default_books)

# Initialize books on startup
initialize_default_books()