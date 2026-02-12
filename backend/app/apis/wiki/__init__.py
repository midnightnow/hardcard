from fastapi import APIRouter, HTTPException, Query
from firebase_admin import firestore
import databutton as db
import firebase_admin
from firebase_admin import credentials
import json
import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import re
from openai import OpenAI

# Initialize Firebase Admin SDK if not already initialized
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(json.loads(db.secrets.get("FIREBASE_SERVICE_ACCOUNT")))
    app = firebase_admin.initialize_app(cred)

# Create router with prefix
router = APIRouter(prefix="/wiki")
firestoredb = firestore.client()

# Initialize OpenAI client if API key exists
try:
    openai_api_key = db.secrets.get("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
        print("OpenAI client initialized successfully")
    else:
        print("Warning: OPENAI_API_KEY not found. Auto-generation features will be disabled.")
        openai_client = None
except Exception as e:
    print(f"Error initializing OpenAI client: {str(e)}")
    openai_client = None

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

class WikiTermBase(BaseModel):
    """Base model for wiki terms"""
    term: str
    slug: str
    category: str
    summary: str

class WikiTerm(WikiTermBase):
    """Model for wiki term with additional fields"""
    id: Optional[str] = None
    content: str
    molecular_structure_url: Optional[str] = None
    references: List[str] = []
    related_terms: List[str] = []
    updated_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None
    auto_generated: bool = False

class WikiTermResponse(BaseModel):
    """Response model for wiki term"""
    success: bool
    data: Optional[WikiTerm] = None
    message: Optional[str] = None

class WikiTermsResponse(BaseModel):
    """Response model for wiki terms list"""
    success: bool
    data: List[WikiTerm] = []
    message: Optional[str] = None

@router.get("/health")
async def check_wiki_health():
    """Check the health of the wiki API"""
    return {"status": "ok", "message": "Wiki API is working"}

@router.get("/term/{slug}")
async def get_wiki_term(slug: str) -> WikiTermResponse:
    """Get a wiki term by slug"""
    try:
        # Check if the term exists in Firestore
        doc_ref = firestoredb.collection("wiki_terms").document(slug)
        doc = doc_ref.get()
        
        if doc.exists:
            # Term exists, return it
            term_data = doc.to_dict()
            term = WikiTerm(**term_data)
            return WikiTermResponse(success=True, data=term)
        else:
            # Term doesn't exist, try to generate it
            return await generate_wiki_term(slug)
    except Exception as e:
        print(f"Error getting wiki term: {str(e)}")
        return WikiTermResponse(success=False, message=f"Error: {str(e)}")

async def generate_wiki_term(slug: str) -> WikiTermResponse:
    """Generate a wiki term using AI"""
    try:
        # Convert slug to readable term (e.g., "cbd" to "CBD")
        if slug.lower() in ['cbd', 'cbg', 'cbn', 'cbc', 'thc', 'thcv']:
            term = slug.upper()
        else:
            term = slug.replace('-', ' ').title()
        
        # Make a guess at the category based on the term
        if any(x in slug.lower() for x in ["cbd", "thc", "cbn", "cbg", "cannabinoid"]):
            category = "cannabinoids"
        elif any(x in slug.lower() for x in ["terpene", "myrcene", "limonene", "pinene", "linalool"]):
            category = "terpenes"
        elif any(x in slug.lower() for x in ["extract", "distillate", "isolate", "oil", "tincture"]):
            category = "methods"
        else:
            category = "terminology"  # Default category
        
        # Check if OpenAI is available
        if not openai_client:
            # Create a minimal wiki entry without AI
            wiki_term = WikiTerm(
                term=term,
                slug=slug,
                category=category,
                summary=f"Information about {term}.",
                content=f"<h2>About {term}</h2><p>This is a placeholder entry for {term}. Full content will be available soon.</p>",
                references=[],
                related_terms=[],
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                auto_generated=True
            )
            
            # Save to Firestore
            doc_ref = firestoredb.collection("wiki_terms").document(slug)
            doc_ref.set(wiki_term.dict())
            
            return WikiTermResponse(success=True, data=wiki_term)
        
        # Generate content with OpenAI
        prompt = f"""Generate a comprehensive wiki entry about {term}. Format the response as JSON with the following properties: 
        {{
            "term": "string", 
            "category": "string (one of: cannabinoids, terpenes, methods, terminology, research)", 
            "summary": "string (2-3 sentences)", 
            "content": "string (HTML with h2, h3 headings and proper paragraphs)", 
            "references": ["academic citation 1", "academic citation 2"], 
            "molecular_formula": "string (for cannabinoids/terpenes only)", 
            "molecular_structure_url": "string (URL to molecular structure image, for cannabinoids/terpenes)"
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a scientific expert on cannabis, cannabinoids, and terpenes. Generate a detailed, scientifically accurate wiki entry about {term}. Your response will be presented on a cannabis knowledge wiki. Include molecular formula and structure URL if relevant (for cannabinoids and terpenes). Make content scientifically accurate but accessible to educated consumers."}, 
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract and parse the generated content
        generated_text = response.choices[0].message.content.strip()
        # Extract the JSON part from the response
        json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
        if not json_match:
            return WikiTermResponse(success=False, message="Failed to generate valid content")
            
        json_content = json_match.group(0)
        generated_data = json.loads(json_content)
        
        # Create wiki term object
        wiki_term = WikiTerm(
            term=generated_data.get("term", term),
            slug=slug,
            category=generated_data.get("category", category),
            summary=generated_data.get("summary", ""),
            content=generated_data.get("content", ""),
            molecular_structure_url=generated_data.get("molecular_structure_url"),
            references=generated_data.get("references", []),
            related_terms=generated_data.get("related_terms", []),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            auto_generated=True
        )
        
        # Save to Firestore
        doc_ref = firestoredb.collection("wiki_terms").document(slug)
        doc_ref.set(wiki_term.dict())
        
        return WikiTermResponse(success=True, data=wiki_term)
    except Exception as e:
        print(f"Error generating wiki term: {str(e)}")
        return WikiTermResponse(success=False, message=f"Error generating content: {str(e)}")

@router.get("/search")
async def search_wiki_terms(query: str = Query(...), category: Optional[str] = None, limit: int = 10) -> WikiTermsResponse:
    """Search wiki terms"""
    try:
        query = query.lower()
        terms_ref = firestoredb.collection("wiki_terms")
        
        # Apply category filter if provided
        if category and category != "all":
            terms_ref = terms_ref.where("category", "==", category)
        
        # Get all terms (we'll filter client-side for better search)
        terms = []
        for doc in terms_ref.stream():
            term_data = doc.to_dict()
            term_data["id"] = doc.id
            
            # Simple search in term, summary and content
            if (query in term_data.get("term", "").lower() or 
                query in term_data.get("summary", "").lower() or 
                query in term_data.get("content", "").lower()):
                
                terms.append(WikiTerm(**term_data))
                if len(terms) >= limit:
                    break
                    
        return WikiTermsResponse(success=True, data=terms)
    except Exception as e:
        print(f"Error searching wiki terms: {str(e)}")
        return WikiTermsResponse(success=False, message=f"Error: {str(e)}")

@router.get("/list/{category}")
async def list_wiki_terms(category: Optional[str] = None, limit: int = 20) -> WikiTermsResponse:
    """List wiki terms by category"""
    try:
        terms_ref = firestoredb.collection("wiki_terms")
        
        # Apply category filter if provided
        if category and category != "all":
            terms_ref = terms_ref.where("category", "==", category)
        
        # Get terms with limit
        terms = []
        for doc in terms_ref.limit(limit).stream():
            term_data = doc.to_dict()
            term_data["id"] = doc.id
            terms.append(WikiTerm(**term_data))
                    
        return WikiTermsResponse(success=True, data=terms)
    except Exception as e:
        print(f"Error listing wiki terms: {str(e)}")
        return WikiTermsResponse(success=False, message=f"Error: {str(e)}")

@router.post("/wiki/seed")
async def seed_wiki_terms():
    """Seed the wiki with initial terms"""
    try:
        # Check if OpenAI is available
        if not openai_client:
            return {
                "success": False,
                "message": "OpenAI API key not configured. Seeding requires OpenAI for content generation."
            }
            
        # Common cannabinoids and terpenes to pre-generate
        terms_to_generate = [
            # Cannabinoids
            "CBD", "CBG", "CBN", "CBC", "THCV", "CBDA", "CBGA", "Delta-8-THC", "THCA", "CBDV",
            # Terpenes
            "Myrcene", "Limonene", "Pinene", "Linalool", "Caryophyllene", "Humulene", "Terpinolene", "Ocimene", "Terpineol", "Valencene",
            # Terminology
            "Entourage Effect", "Full Spectrum", "Broad Spectrum", "Isolate", "Endocannabinoid System"
        ]
        
        generated_count = 0
        for term in terms_to_generate:
            # Check if already exists
            doc_ref = firestoredb.collection("wiki_terms").document(sanitize_storage_key(term.lower()))
            if not doc_ref.get().exists:
                # Generate and save term
                try:
                    await generate_wiki_term(sanitize_storage_key(term.lower()))
                    generated_count += 1
                    print(f"Generated term: {term}")
                except Exception as e:
                    print(f"Error generating {term}: {str(e)}")
        
        return {
            "success": True, 
            "message": f"Successfully generated {generated_count} wiki terms out of {len(terms_to_generate)} requested."
        }
    except Exception as err:
        print(f"Error seeding wiki terms: {str(err)}")
        raise HTTPException(status_code=500, detail=f"Error seeding wiki terms: {str(err)}")
