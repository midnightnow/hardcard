from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import uuid
import json
import datetime
import databutton as db
from openai import OpenAI
from app.auth import AuthorizedUser
import re

router = APIRouter()

# Initialize OpenAI client
def get_openai_client():
    api_key = db.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return OpenAI(api_key=api_key)

# Helper function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Enums for Hardcard elements
class Archetype(str, Enum):
    EXPLORER = "Explorer"
    CREATOR = "Creator"
    SAGE = "Sage"
    INNOCENT = "Innocent"
    RULER = "Ruler"
    CAREGIVER = "Caregiver"
    EVERYPERSON = "Everyperson"
    LOVER = "Lover"
    JESTER = "Jester"
    HERO = "Hero"
    OUTLAW = "Outlaw"
    MAGICIAN = "Magician"

class Element(str, Enum):
    FIRE = "Fire"
    WATER = "Water"
    EARTH = "Earth"
    AIR = "Air"
    VOID = "Void"
    AETHER = "Aether"

class SelfImprovementArea(str, Enum):
    PHYSICAL = "Physical"
    MENTAL = "Mental"
    EMOTIONAL = "Emotional"
    SPIRITUAL = "Spiritual"
    FINANCIAL = "Financial"
    SOCIAL = "Social"
    CREATIVE = "Creative"

# Pydantic Models
class ArchetypeTrio(BaseModel):
    primary: Archetype
    secondary: Archetype
    shadow: Archetype
    description: str

class ElementalAlignment(BaseModel):
    primary: Element
    secondary: Element
    description: str

class SoulSentence(BaseModel):
    text: str
    explanation: str

class Mythline(BaseModel):
    past: str
    present: str
    future: str
    description: str

class ImprovementGoal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    area: SelfImprovementArea
    title: str
    description: str
    metrics: List[str]
    target_date: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    completed: bool = False
    completion_date: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0

class ImprovementProgress(BaseModel):
    goal_id: str
    date: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    progress: float  # 0.0 to 1.0
    notes: Optional[str] = None

class HardcardCore(BaseModel):
    """The core elements that make up a Hardcard"""
    soul_sentence: SoulSentence
    archetype_trio: ArchetypeTrio
    elemental_alignment: ElementalAlignment
    mythline: Mythline

class Hardcard(BaseModel):
    """Complete Hardcard model including core elements and improvement tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    core: HardcardCore
    goals: List[ImprovementGoal] = []
    progress_history: List[Dict[str, Any]] = []
    version: int = 1

class HardcardGenerationRequest(BaseModel):
    """Request body for generating a new Hardcard"""
    name: str
    birth_date: Optional[str] = None
    values: List[str] = []
    strengths: List[str] = []
    challenges: List[str] = []
    aspirations: List[str] = []
    background: Optional[str] = None

class HardcardCustomizationRequest(BaseModel):
    """Request body for customizing an existing Hardcard"""
    hardcard_id: str
    name: Optional[str] = None
    soul_sentence: Optional[Dict[str, str]] = None
    archetype_trio: Optional[Dict[str, Any]] = None
    elemental_alignment: Optional[Dict[str, Any]] = None
    mythline: Optional[Dict[str, Any]] = None

class HardcardLightRequest(BaseModel):
    """Request body for the Hardcard Light generation from image analysis"""
    image_description: str
    person_name: Optional[str] = None
    guidance_prompt: Optional[str] = None

class ImprovementProgressRequest(BaseModel):
    """Request body for updating improvement goal progress"""
    goal_id: str
    progress: float  # 0.0 to 1.0
    notes: Optional[str] = None

class ImprovementGoalRequest(BaseModel):
    """Request body for adding a new improvement goal"""
    area: SelfImprovementArea
    title: str
    description: str
    metrics: List[str] = []
    target_date: Optional[str] = None

# Helper Functions
def get_user_hardcards(user_id: str) -> List[Hardcard]:
    """Get all Hardcards for a user"""
    storage_key = sanitize_storage_key(f"hardcards-{user_id}")
    try:
        hardcards_data = db.storage.json.get(storage_key, default=[])
        return [Hardcard(**h) for h in hardcards_data]
    except Exception as e:
        print(f"Error fetching user hardcards: {e}")
        return []

def get_hardcard_by_id(user_id: str, hardcard_id: str) -> Optional[Hardcard]:
    """Get a specific Hardcard by ID"""
    hardcards = get_user_hardcards(user_id)
    for card in hardcards:
        if card.id == hardcard_id:
            return card
    return None

def save_user_hardcards(user_id: str, hardcards: List[Hardcard]):
    """Save all Hardcards for a user"""
    storage_key = sanitize_storage_key(f"hardcards-{user_id}")
    hardcards_data = [h.dict() for h in hardcards]
    db.storage.json.put(storage_key, hardcards_data)

def generate_hardcard_with_ai(request: HardcardGenerationRequest, user_id: str) -> Hardcard:
    """Use OpenAI to generate a personalized Hardcard"""
    client = get_openai_client()
    
    # Create a prompt for the AI to generate the Hardcard elements
    prompt = f"""
    Create a personalized Hardcard for a person with the following information:
    Name: {request.name}
    {f'Birth Date: {request.birth_date}' if request.birth_date else ''}
    Values: {', '.join(request.values)}
    Strengths: {', '.join(request.strengths)}
    Challenges: {', '.join(request.challenges)}
    Aspirations: {', '.join(request.aspirations)}
    {f'Background: {request.background}' if request.background else ''}
    
    Based on this information, create the following elements in JSON format:
    
    1. Soul Sentence: A single powerful sentence that captures the essence of this person's unique purpose. Include an explanation.
    
    2. Archetype Trio:
       - Primary archetype (dominant personality trait)
       - Secondary archetype (supporting personality trait)
       - Shadow archetype (repressed or challenging aspect)
       Choose from: Explorer, Creator, Sage, Innocent, Ruler, Caregiver, Everyperson, Lover, Jester, Hero, Outlaw, Magician
       Include a description explaining this trio and how they interact.
    
    3. Elemental Alignment:
       - Primary element
       - Secondary element
       Choose from: Fire, Water, Earth, Air, Void, Aether
       Include a description explaining this elemental alignment and what it means.
    
    4. Mythline:
       - Past: A sentence about where they came from
       - Present: A sentence about where they are now
       - Future: A sentence about where they're going
       Include a description tying these together into a personal narrative.
    
    Return the response in structured JSON format only, without any introduction or explanation text.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a skilled creator of personalized Hardcards, which are deep insights into a person's core essence and potential. Respond only with structured JSON data of the Hardcard elements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        # Extract the JSON content from the response
        try:
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start != -1 and json_end != -1:
                json_content = content[json_start:json_end+1]
                data = json.loads(json_content)
            else:
                data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            raise HTTPException(status_code=500, detail="Error parsing AI response") 
        
        # Build the Hardcard from the AI response
        hardcard_core = HardcardCore(
            soul_sentence=SoulSentence(
                text=data.get("soul_sentence", {}).get("text", "Your journey unfolds in subtle layers of meaning."),
                explanation=data.get("soul_sentence", {}).get("explanation", "This represents your multifaceted path through life.")
            ),
            archetype_trio=ArchetypeTrio(
                primary=data.get("archetype_trio", {}).get("primary", Archetype.EXPLORER),
                secondary=data.get("archetype_trio", {}).get("secondary", Archetype.CREATOR),
                shadow=data.get("archetype_trio", {}).get("shadow", Archetype.JESTER),
                description=data.get("archetype_trio", {}).get("description", "Your archetypal nature blends exploration, creation, and hidden playfulness.")
            ),
            elemental_alignment=ElementalAlignment(
                primary=data.get("elemental_alignment", {}).get("primary", Element.FIRE),
                secondary=data.get("elemental_alignment", {}).get("secondary", Element.WATER),
                description=data.get("elemental_alignment", {}).get("description", "The passion of fire balanced by the depth of water creates a harmonious tension.")
            ),
            mythline=Mythline(
                past=data.get("mythline", {}).get("past", "Origins rooted in tradition yet seeking independence."),
                present=data.get("mythline", {}).get("present", "Standing at the crossroads of possibility and choice."),
                future=data.get("mythline", {}).get("future", "Destined to forge connections that transform landscapes."),
                description=data.get("mythline", {}).get("description", "Your personal journey weaves through time, connecting origins to destiny through present choices.")
            )
        )
        
        return Hardcard(
            user_id=user_id,
            name=request.name,
            core=hardcard_core
        )
        
    except Exception as e:
        print(f"Error generating hardcard with AI: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Hardcard: {str(e)}")

def generate_hardcard_light_with_ai(request: HardcardLightRequest, user_id: str) -> HardcardCore:
    """Generate a simplified Hardcard (Hardcard Light) based on image description"""
    client = get_openai_client()
    
    person_context = f"person named {request.person_name}" if request.person_name else "person"
    guidance = request.guidance_prompt or "Focus on the visual elements that reveal personality and essence"
    
    prompt = f"""
    Analyze this image description and create a Hardcard Light for the {person_context}:
    
    Image description: {request.image_description}
    
    Guidance: {guidance}
    
    Based on this visual information alone, create the following elements in JSON format:
    
    1. Soul Sentence: A single powerful sentence that captures the essence visible in this image.
    
    2. Archetype Trio:
       - Primary archetype (dominant visible trait)
       - Secondary archetype (supporting visible trait)
       - Shadow archetype (subtle or hidden aspect)
       Choose from: Explorer, Creator, Sage, Innocent, Ruler, Caregiver, Everyperson, Lover, Jester, Hero, Outlaw, Magician
    
    3. Elemental Alignment:
       - Primary element
       - Secondary element
       Choose from: Fire, Water, Earth, Air, Void, Aether
    
    4. Mythline:
       - A concise three-part story (past, present, future) based solely on what's visible
    
    Focus on what can be reasonably inferred from the visual information. Return in JSON format only.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at reading visual cues and creating personality insights. You respond only with structured JSON data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        # Extract the JSON content from the response
        try:
            json_start = content.find('{')
            json_end = content.rfind('}')
            if json_start != -1 and json_end != -1:
                json_content = content[json_start:json_end+1]
                data = json.loads(json_content)
            else:
                data = json.loads(content)
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            raise HTTPException(status_code=500, detail="Error parsing AI response")
        
        # Build the Hardcard core from the AI response
        return HardcardCore(
            soul_sentence=SoulSentence(
                text=data.get("soul_sentence", {}).get("text", "Visual essence captured in a moment of revelation."),
                explanation=data.get("soul_sentence", {}).get("explanation", "The image reveals deeper truths about the subject.")
            ),
            archetype_trio=ArchetypeTrio(
                primary=data.get("archetype_trio", {}).get("primary", Archetype.EXPLORER),
                secondary=data.get("archetype_trio", {}).get("secondary", Archetype.CREATOR),
                shadow=data.get("archetype_trio", {}).get("shadow", Archetype.JESTER),
                description=data.get("archetype_trio", {}).get("description", "The visual elements suggest a blend of exploration, creation, and hidden playfulness.")
            ),
            elemental_alignment=ElementalAlignment(
                primary=data.get("elemental_alignment", {}).get("primary", Element.FIRE),
                secondary=data.get("elemental_alignment", {}).get("secondary", Element.WATER),
                description=data.get("elemental_alignment", {}).get("description", "Visual cues indicate a dynamic tension between passion and depth.")
            ),
            mythline=Mythline(
                past=data.get("mythline", {}).get("past", "A journey from structured beginnings."),
                present=data.get("mythline", {}).get("present", "Standing at the threshold of transformation."),
                future=data.get("mythline", {}).get("future", "Moving toward authentic expression."),
                description=data.get("mythline", {}).get("description", "The visual narrative suggests an evolution from structure to authenticity.")
            )
        )
        
    except Exception as e:
        print(f"Error generating Hardcard Light with AI: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating Hardcard Light: {str(e)}")

# API Endpoints
@router.post("/generate-hardcard")
def create_personal_hardcard(request: HardcardGenerationRequest, user: AuthorizedUser) -> Hardcard:
    """Generate a new personalized Hardcard based on user details
    
    This endpoint creates a complete Hardcard profile with all core elements:
    - Soul Sentence™: Your essence captured in a powerful statement
    - Archetype Trio: Primary, Secondary and Shadow archetypes
    - Elemental Alignment: Your energetic composition
    - Mythline: Your personal journey through past, present and future
    
    The Hardcard becomes a foundation for your self-improvement journey
    and can be enhanced with specific goals and progress tracking.
    """
    # Generate the Hardcard using AI
    hardcard = generate_hardcard_with_ai(request, user.sub)
    
    # Save the new Hardcard
    user_hardcards = get_user_hardcards(user.sub)
    user_hardcards.append(hardcard)
    save_user_hardcards(user.sub, user_hardcards)
    
    return hardcard

@router.post("/hardcard-light")
def create_hardcard_light(request: HardcardLightRequest, user: AuthorizedUser) -> Hardcard:
    """Bootstrap a Hardcard from an image description (Hardcard Light)
    
    This endpoint creates a simplified Hardcard based on visual analysis of
    an image description. The Hardcard Light provides core elements:
    - Soul Sentence™: Visual essence captured in a statement
    - Archetype Trio: Visually-inferred character elements
    - Elemental Alignment: Energy composition based on visual cues
    - Mythline: A visual narrative inferred from the image
    
    The Hardcard Light can be used as a starting point for a full Hardcard
    or as a lightweight alternative for visual personality insights.
    """
    # Generate the Hardcard Light core using AI
    hardcard_core = generate_hardcard_light_with_ai(request, user.sub)
    
    # Create a complete Hardcard with the generated core
    name = request.person_name or "Hardcard Light"
    hardcard = Hardcard(
        user_id=user.sub,
        name=name,
        core=hardcard_core
    )
    
    # Save the new Hardcard
    user_hardcards = get_user_hardcards(user.sub)
    user_hardcards.append(hardcard)
    save_user_hardcards(user.sub, user_hardcards)
    
    return hardcard

@router.post("/customize-hardcard")
def customize_personal_hardcard(request: HardcardCustomizationRequest, user: AuthorizedUser) -> Hardcard:
    """Customize an existing Hardcard with updated elements
    
    This endpoint allows modification of any Hardcard core element:
    - Name: The identifier for this Hardcard
    - Soul Sentence™: Your essence statement
    - Archetype Trio: Your character archetype composition
    - Elemental Alignment: Your energetic nature
    - Mythline: Your personal narrative
    
    Only specified elements will be updated, leaving others unchanged.
    Each update increments the Hardcard version number for tracking.
    """
    # Get the existing Hardcard
    hardcard = get_hardcard_by_id(user.sub, request.hardcard_id)
    if not hardcard:
        raise HTTPException(status_code=404, detail="Hardcard not found")
    
    # Update the Hardcard with the requested changes
    if request.name:
        hardcard.name = request.name
    
    if request.soul_sentence:
        hardcard.core.soul_sentence.text = request.soul_sentence.get("text", hardcard.core.soul_sentence.text)
        hardcard.core.soul_sentence.explanation = request.soul_sentence.get("explanation", hardcard.core.soul_sentence.explanation)
    
    if request.archetype_trio:
        hardcard.core.archetype_trio.primary = request.archetype_trio.get("primary", hardcard.core.archetype_trio.primary)
        hardcard.core.archetype_trio.secondary = request.archetype_trio.get("secondary", hardcard.core.archetype_trio.secondary)
        hardcard.core.archetype_trio.shadow = request.archetype_trio.get("shadow", hardcard.core.archetype_trio.shadow)
        hardcard.core.archetype_trio.description = request.archetype_trio.get("description", hardcard.core.archetype_trio.description)
    
    if request.elemental_alignment:
        hardcard.core.elemental_alignment.primary = request.elemental_alignment.get("primary", hardcard.core.elemental_alignment.primary)
        hardcard.core.elemental_alignment.secondary = request.elemental_alignment.get("secondary", hardcard.core.elemental_alignment.secondary)
        hardcard.core.elemental_alignment.description = request.elemental_alignment.get("description", hardcard.core.elemental_alignment.description)
    
    if request.mythline:
        hardcard.core.mythline.past = request.mythline.get("past", hardcard.core.mythline.past)
        hardcard.core.mythline.present = request.mythline.get("present", hardcard.core.mythline.present)
        hardcard.core.mythline.future = request.mythline.get("future", hardcard.core.mythline.future)
        hardcard.core.mythline.description = request.mythline.get("description", hardcard.core.mythline.description)
    
    # Update the version and timestamp
    hardcard.version += 1
    hardcard.updated_at = datetime.datetime.now().isoformat()
    
    # Save the updated Hardcard
    user_hardcards = get_user_hardcards(user.sub)
    for i, card in enumerate(user_hardcards):
        if card.id == hardcard.id:
            user_hardcards[i] = hardcard
            break
    
    save_user_hardcards(user.sub, user_hardcards)
    
    return hardcard

@router.post("/hardcard/{hardcard_id}/add-goal")
def add_improvement_goal(hardcard_id: str, request: ImprovementGoalRequest, user: AuthorizedUser) -> Hardcard:
    """Add a new self-improvement goal to a Hardcard
    
    This endpoint allows adding personal development goals to your Hardcard
    in various areas:
    - Physical: Health, fitness, wellness goals
    - Mental: Learning, skills, cognitive development
    - Emotional: Emotional regulation, relationships
    - Spiritual: Purpose, meaning, connection
    - Financial: Wealth building, financial security
    - Social: Community, relationships, communication
    - Creative: Artistic expression, innovation
    
    Goals include metrics for tracking progress and optional target dates.
    """
    # Get the existing Hardcard
    hardcard = get_hardcard_by_id(user.sub, hardcard_id)
    if not hardcard:
        raise HTTPException(status_code=404, detail="Hardcard not found")
    
    # Create the new goal
    new_goal = ImprovementGoal(
        area=request.area,
        title=request.title,
        description=request.description,
        metrics=request.metrics,
        target_date=request.target_date
    )
    
    # Add the goal to the Hardcard
    hardcard.goals.append(new_goal)
    hardcard.updated_at = datetime.datetime.now().isoformat()
    
    # Save the updated Hardcard
    user_hardcards = get_user_hardcards(user.sub)
    for i, card in enumerate(user_hardcards):
        if card.id == hardcard.id:
            user_hardcards[i] = hardcard
            break
    
    save_user_hardcards(user.sub, user_hardcards)
    
    return hardcard

@router.post("/hardcard/{hardcard_id}/update-progress")
def update_goal_progress(hardcard_id: str, request: ImprovementProgressRequest, user: AuthorizedUser) -> Hardcard:
    """Update progress on a self-improvement goal
    
    This endpoint tracks your progress toward completing self-improvement goals.
    Each progress update includes:
    - A progress percentage (0.0 to 1.0)
    - Optional notes about what was accomplished
    - Automatic timestamp of the progress update
    
    Progress updates are stored in your Hardcard's history, allowing you to
    track your improvement journey over time and celebrate achievements.
    """
    # Get the existing Hardcard
    hardcard = get_hardcard_by_id(user.sub, hardcard_id)
    if not hardcard:
        raise HTTPException(status_code=404, detail="Hardcard not found")
    
    # Find the goal to update
    goal_found = False
    for goal in hardcard.goals:
        if goal.id == request.goal_id:
            # Update the goal progress
            goal.progress = request.progress
            goal_found = True
            
            # Mark as completed if progress is 100%
            if request.progress >= 1.0:
                goal.completed = True
                goal.completion_date = datetime.datetime.now().isoformat()
            break
    
    if not goal_found:
        raise HTTPException(status_code=404, detail="Goal not found in this Hardcard")
    
    # Record the progress update in the history
    progress_entry = {
        "goal_id": request.goal_id,
        "date": datetime.datetime.now().isoformat(),
        "progress": request.progress,
        "notes": request.notes
    }
    
    hardcard.progress_history.append(progress_entry)
    hardcard.updated_at = datetime.datetime.now().isoformat()
    
    # Save the updated Hardcard
    user_hardcards = get_user_hardcards(user.sub)
    for i, card in enumerate(user_hardcards):
        if card.id == hardcard.id:
            user_hardcards[i] = hardcard
            break
    
    save_user_hardcards(user.sub, user_hardcards)
    
    return hardcard

@router.get("/hardcards")
def list_personal_hardcards(user: AuthorizedUser) -> List[Hardcard]:
    """List all Hardcards belonging to the authenticated user
    
    Returns a complete list of all Hardcards created by or for the user,
    including both full Hardcards and Hardcard Light profiles. Each Hardcard
    contains its complete data including core elements and improvement goals.
    """
    return get_user_hardcards(user.sub)

@router.get("/hardcard/{hardcard_id}")
def get_personal_hardcard(hardcard_id: str, user: AuthorizedUser) -> Hardcard:
    """Get a specific Hardcard by ID
    
    Returns the complete Hardcard with all core elements, improvement goals,
    and progress history. Use this endpoint to retrieve all information about
    a specific Hardcard for detailed viewing or before making updates.
    """
    hardcard = get_hardcard_by_id(user.sub, hardcard_id)
    if not hardcard:
        raise HTTPException(status_code=404, detail="Hardcard not found")
    
    return hardcard
