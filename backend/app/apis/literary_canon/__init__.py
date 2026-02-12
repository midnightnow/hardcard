from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import databutton as db
import re
from datetime import datetime
import uuid

# Create API router
router = APIRouter()

# Define models
class LiteraryWork(BaseModel):
    id: str
    title: str
    author: str
    year_published: int
    age_recommendation: int  # Age when appropriate to read
    description: str
    categories: List[str]  # e.g., "Classic", "Philosophy", "Economics", etc.
    difficulty: str  # "Easy", "Moderate", "Advanced"
    financial_concepts: List[str]  # Related financial concepts
    url: Optional[str] = None  # Optional link to purchase or more info
    cover_image: Optional[str] = None  # URL to book cover image

class FinancialConcept(BaseModel):
    id: str
    name: str
    description: str
    age_appropriate: int  # Age when this concept becomes relevant
    related_books: List[str]  # IDs of related literary works
    suggested_activities: List[str]  # Activities to understand the concept

class LiteraryProgressUpdate(BaseModel):
    profile_id: str
    book_id: str
    status: str  # "planned", "gifted", "completed", "skipped"
    completion_date: Optional[str] = None
    notes: Optional[str] = None

class LiteraryJourneyStatus(BaseModel):
    profile_id: str
    books_progress: Dict[str, dict]  # Map of book_id to progress status
    milestones_completed: List[int]  # List of age milestones completed
    last_updated: str

class AgeGroupLiterature(BaseModel):
    age: int
    title: str
    description: str
    books: List[LiteraryWork]
    financial_concepts: List[FinancialConcept]

class EnlightenmentJourneyResponse(BaseModel):
    age_groups: List[AgeGroupLiterature]
    profile_progress: Optional[LiteraryJourneyStatus] = None

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Initialize the literary canon and financial concepts if not already present
def initialize_default_literary_canon():
    """Initialize the default literary canon data if not already present"""
    try:
        # Check if data exists
        try:
            literary_works = db.storage.json.get("literary_canon_works")
            if literary_works and len(literary_works) > 0:
                return  # Data already exists
        except Exception:
            pass  # Continue to initialize
        
        # Literary works by age group
        literary_works = [
            # For Early Childhood (0-5)
            LiteraryWork(
                id="richest_man_babylon_kids",
                title="The Richest Man in Babylon for Kids",
                author="George S. Clason (Adapted)",
                year_published=2015,
                age_recommendation=5,
                description="A child-friendly adaptation of the classic financial wisdom, introducing basic concepts of saving and wealth.",
                categories=["Finance", "Children's"],
                difficulty="Easy",
                financial_concepts=["Saving", "Patience"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/richest_babylon_kids.jpg"
            ),
            
            # For Children (6-12)
            LiteraryWork(
                id="aesops_fables",
                title="Aesop's Fables",
                author="Aesop",
                year_published=-550,  # Approximate date
                age_recommendation=8,
                description="Ancient tales with moral lessons that teach responsibility, foresight, and wisdom.",
                categories=["Classic", "Fables"],
                difficulty="Easy",
                financial_concepts=["Planning", "Diligence"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/aesops_fables.jpg"
            ),
            LiteraryWork(
                id="little_house",
                title="Little House on the Prairie",
                author="Laura Ingalls Wilder",
                year_published=1935,
                age_recommendation=10,
                description="Stories of pioneer life teaching self-reliance, frugality, and the value of hard work.",
                categories=["Classic", "Historical"],
                difficulty="Easy",
                financial_concepts=["Self-Reliance", "Resourcefulness"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/little_house.jpg"
            ),
            
            # For Teenagers (13-17)
            LiteraryWork(
                id="richest_man_babylon",
                title="The Richest Man in Babylon",
                author="George S. Clason",
                year_published=1926,
                age_recommendation=14,
                description="Classic financial advice wrapped in parables from ancient Babylon, teaching fundamental principles of finance and wealth.",
                categories=["Finance", "Classic"],
                difficulty="Moderate",
                financial_concepts=["Saving", "Investment", "Debt Management"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/richest_babylon.jpg"
            ),
            LiteraryWork(
                id="benjamin_franklin_autobiography",
                title="The Autobiography of Benjamin Franklin",
                author="Benjamin Franklin",
                year_published=1791,
                age_recommendation=16,
                description="Franklin's own success story emphasizing industry, frugality, and continuous improvement.",
                categories=["Autobiography", "Classic"],
                difficulty="Moderate",
                financial_concepts=["Industry", "Frugality", "Personal Development"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/benjamin_franklin.jpg"
            ),
            
            # For Young Adults (18-21)
            LiteraryWork(
                id="intelligent_investor",
                title="The Intelligent Investor",
                author="Benjamin Graham",
                year_published=1949,
                age_recommendation=18,
                description="The definitive book on value investing, emphasizing long-term strategies and rational decision-making.",
                categories=["Finance", "Investment"],
                difficulty="Advanced",
                financial_concepts=["Value Investing", "Market Psychology", "Risk Management"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/intelligent_investor.jpg"
            ),
            LiteraryWork(
                id="wealth_of_nations",
                title="The Wealth of Nations",
                author="Adam Smith",
                year_published=1776,
                age_recommendation=20,
                description="Foundational text on economics and the functioning of markets, introducing concepts like division of labor and the 'invisible hand'.",
                categories=["Economics", "Classic"],
                difficulty="Advanced",
                financial_concepts=["Free Markets", "Division of Labor", "Economic Systems"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/wealth_nations.jpg"
            ),
            
            # For Adults (22-30)
            LiteraryWork(
                id="snowball",
                title="The Snowball: Warren Buffett and the Business of Life",
                author="Alice Schroeder",
                year_published=2008,
                age_recommendation=22,
                description="Biography of Warren Buffett revealing his investment philosophy and life principles.",
                categories=["Biography", "Finance"],
                difficulty="Moderate",
                financial_concepts=["Value Investing", "Long-term Thinking", "Business Analysis"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/snowball.jpg"
            ),
            LiteraryWork(
                id="fooled_by_randomness",
                title="Fooled by Randomness",
                author="Nassim Nicholas Taleb",
                year_published=2001,
                age_recommendation=25,
                description="Explores the role of chance in life and markets, helping readers understand risk and uncertainty.",
                categories=["Finance", "Psychology"],
                difficulty="Advanced",
                financial_concepts=["Risk Management", "Decision Making Under Uncertainty"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/fooled_randomness.jpg"
            ),
            
            # For Mature Adults (30+)
            LiteraryWork(
                id="essays_of_warren_buffett",
                title="The Essays of Warren Buffett",
                author="Warren Buffett (Lawrence Cunningham, ed.)",
                year_published=1997,
                age_recommendation=30,
                description="Compilation of Buffett's shareholder letters offering profound insights on investing, business, and life.",
                categories=["Finance", "Business"],
                difficulty="Advanced",
                financial_concepts=["Business Principles", "Corporate Governance", "Legacy Planning"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/essays_buffett.jpg"
            ),
            LiteraryWork(
                id="thinking_fast_slow",
                title="Thinking, Fast and Slow",
                author="Daniel Kahneman",
                year_published=2011,
                age_recommendation=30,
                description="Nobel Prize winner's exploration of cognitive biases affecting decision-making, including financial choices.",
                categories=["Psychology", "Economics"],
                difficulty="Advanced",
                financial_concepts=["Behavioral Economics", "Rational Decision Making"],
                cover_image="https://static.databutton.com/public/557509c6-1634-4d57-9b47-00fde8d73219/thinking_fast_slow.jpg"
            ),
        ]
        
        # Financial concepts
        financial_concepts = [
            FinancialConcept(
                id="saving",
                name="Saving",
                description="Setting aside money for future needs rather than spending it immediately.",
                age_appropriate=5,
                related_books=["richest_man_babylon_kids", "richest_man_babylon"],
                suggested_activities=["Start a piggy bank", "Open a savings account"]
            ),
            FinancialConcept(
                id="compound_interest",
                name="Compound Interest",
                description="How money grows over time when interest is earned on both principal and accumulated interest.",
                age_appropriate=12,
                related_books=["richest_man_babylon"],
                suggested_activities=["Calculate compound interest examples", "Compare simple vs. compound interest"]
            ),
            FinancialConcept(
                id="investing",
                name="Investing",
                description="Putting money to work to generate returns over time.",
                age_appropriate=16,
                related_books=["intelligent_investor", "essays_of_warren_buffett"],
                suggested_activities=["Research different investment vehicles", "Create a mock portfolio"]
            ),
            FinancialConcept(
                id="value_investing",
                name="Value Investing",
                description="Investment strategy focusing on buying securities that appear underpriced relative to their intrinsic value.",
                age_appropriate=18,
                related_books=["intelligent_investor", "snowball"],
                suggested_activities=["Analyze company financial statements", "Calculate intrinsic value of stocks"]
            ),
            FinancialConcept(
                id="risk_management",
                name="Risk Management",
                description="Identifying, analyzing, and accepting or mitigating uncertainty in investment decisions.",
                age_appropriate=20,
                related_books=["fooled_by_randomness", "intelligent_investor"],
                suggested_activities=["Create a diversified portfolio", "Learn about hedging strategies"]
            ),
            FinancialConcept(
                id="behavioral_finance",
                name="Behavioral Finance",
                description="Study of psychological influences on investors and financial markets.",
                age_appropriate=25,
                related_books=["thinking_fast_slow", "fooled_by_randomness"],
                suggested_activities=["Identify personal cognitive biases", "Journal investment decisions and emotions"]
            ),
            FinancialConcept(
                id="legacy_planning",
                name="Legacy Planning",
                description="Planning for wealth transfer across generations while instilling values and knowledge.",
                age_appropriate=30,
                related_books=["essays_of_warren_buffett"],
                suggested_activities=["Create a family mission statement", "Develop an educational plan for heirs"]
            ),
        ]
        
        # Create age groups structure
        age_groups = [
            {
                "age": 5,
                "title": "Early Foundations (Ages 5-7)",
                "description": "Simple stories that introduce basic concepts of saving, patience, and working for rewards."
            },
            {
                "age": 8,
                "title": "Building Blocks (Ages 8-12)",
                "description": "Tales that teach responsibility, planning, and the value of diligence through relatable narratives."
            },
            {
                "age": 13,
                "title": "Adolescent Insights (Ages 13-17)",
                "description": "Introduction to core financial principles through engaging stories and accessible guides."
            },
            {
                "age": 18,
                "title": "Early Adult Wisdom (Ages 18-21)",
                "description": "Foundational texts on economics and investment as young adults prepare for financial independence."
            },
            {
                "age": 22,
                "title": "Professional Growth (Ages 22-29)",
                "description": "Deeper exploration of investment strategies and psychological aspects of financial decision-making."
            },
            {
                "age": 30,
                "title": "Legacy Building (Ages 30+)",
                "description": "Advanced concepts for wealth preservation, family legacy, and teaching the next generation."
            },
        ]
        
        # Save to storage
        db.storage.json.put("literary_canon_works", [work.dict() for work in literary_works])
        db.storage.json.put("financial_concepts", [concept.dict() for concept in financial_concepts])
        db.storage.json.put("literary_age_groups", age_groups)
        
        print("Literary canon data initialized successfully")
    except Exception as e:
        print(f"Error initializing literary canon data: {str(e)}")

# Call initialization during module import
initialize_default_literary_canon()

@router.get("/journey/{profile_id}")
async def get_literary_journey_canon(profile_id: str) -> EnlightenmentJourneyResponse:
    """Get the enlightenment journey content with optional user progress"""
    try:
        # Sanitize profile ID
        sanitized_id = sanitize_storage_key(profile_id)
        
        # Get literary canon data
        literary_works = [LiteraryWork(**work) for work in db.storage.json.get("literary_canon_works", default=[])]
        financial_concepts = [FinancialConcept(**concept) for concept in db.storage.json.get("financial_concepts", default=[])]
        age_groups_data = db.storage.json.get("literary_age_groups", default=[])
        
        # Get user progress if available
        progress_key = f"literary_progress_{sanitized_id}"
        try:
            progress_data = db.storage.json.get(progress_key)
            progress = LiteraryJourneyStatus(**progress_data) if progress_data else None
        except Exception:
            progress = None
        
        # Build response structure by age group
        age_groups = []
        for group in age_groups_data:
            age = group["age"]
            group_books = [work for work in literary_works if work.age_recommendation >= age and 
                           (age == 30 or work.age_recommendation < next_age(age, age_groups_data))]
            
            group_concepts = [concept for concept in financial_concepts if concept.age_appropriate >= age and 
                              (age == 30 or concept.age_appropriate < next_age(age, age_groups_data))]
            
            age_groups.append(AgeGroupLiterature(
                age=age,
                title=group["title"],
                description=group["description"],
                books=group_books,
                financial_concepts=group_concepts
            ))
        
        return EnlightenmentJourneyResponse(
            age_groups=age_groups,
            profile_progress=progress
        )
    
    except Exception as e:
        print(f"Error getting enlightenment journey: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get enlightenment journey: {str(e)}")

def next_age(current_age: int, age_groups_data: List[dict]) -> int:
    """Get the next age group threshold after current_age"""
    ages = sorted([g["age"] for g in age_groups_data])
    for age in ages:
        if age > current_age:
            return age
    return 999  # No higher age group

@router.post("/progress/update")
async def update_book_progress2(update: LiteraryProgressUpdate) -> Dict[str, str]:
    """Update progress for a book in a user's journey"""
    try:
        # Sanitize profile ID
        sanitized_id = sanitize_storage_key(update.profile_id)
        progress_key = f"literary_progress_{sanitized_id}"
        
        # Get existing progress or create new
        try:
            progress_data = db.storage.json.get(progress_key)
            if progress_data:
                progress = progress_data
            else:
                progress = {
                    "profile_id": update.profile_id,
                    "books_progress": {},
                    "milestones_completed": [],
                    "last_updated": datetime.now().isoformat()
                }
        except Exception:
            progress = {
                "profile_id": update.profile_id,
                "books_progress": {},
                "milestones_completed": [],
                "last_updated": datetime.now().isoformat()
            }
        
        # Update book progress
        progress["books_progress"][update.book_id] = {
            "status": update.status,
            "completion_date": update.completion_date or datetime.now().isoformat() if update.status == "completed" else None,
            "notes": update.notes
        }
        
        # Update last updated timestamp
        progress["last_updated"] = datetime.now().isoformat()
        
        # Check if a new milestone should be added
        if update.status == "completed":
            # Get the book's age recommendation
            literary_works = db.storage.json.get("literary_canon_works", default=[])
            for work in literary_works:
                if work["id"] == update.book_id:
                    age = work["age_recommendation"]
                    if age not in progress["milestones_completed"]:
                        progress["milestones_completed"].append(age)
                        progress["milestones_completed"].sort()
                    break
        
        # Save updated progress
        db.storage.json.put(progress_key, progress)
        
        return {"message": "Progress updated successfully"}
    
    except Exception as e:
        print(f"Error updating book progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update book progress: {str(e)}")

@router.get("/book/{book_id}")
async def get_book_details_canon(book_id: str) -> LiteraryWork:
    """Get details for a specific book"""
    try:
        literary_works = db.storage.json.get("literary_canon_works", default=[])
        for work in literary_works:
            if work["id"] == book_id:
                return LiteraryWork(**work)
        
        raise HTTPException(status_code=404, detail="Book not found")
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting book details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get book details: {str(e)}")
