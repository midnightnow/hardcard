from fastapi import APIRouter, HTTPException, Depends, WebSocket
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Literal, Union
import openai
import databutton as db
import re
import time
import json
from app.auth import AuthorizedUser

router = APIRouter()

# Models for request and response
class PhilosopherPersona(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    avatar_url: Optional[str] = None

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    persona_id: Optional[str] = None
    stream: bool = False

class ChatResponse(BaseModel):
    message: ChatMessage
    persona_id: str

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_openai_client():
    """Get OpenAI client with API key"""
    api_key = db.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return openai.OpenAI(api_key=api_key)

def get_default_personas() -> List[PhilosopherPersona]:
    """Get the default list of philosophical personas"""
    return [
        PhilosopherPersona(
            id="socrates",
            name="Socrates",
            description="Ancient Greek philosopher known for the Socratic method of questioning",
            system_prompt="""You are Socrates, the ancient Greek philosopher. You primarily use questions to help 
                         people examine their own beliefs. You rarely give direct answers, instead preferring to 
                         lead the person to discover insights themselves through structured inquiry. Your tone is 
                         thoughtful, patient, and sometimes ironic. You value wisdom over knowledge and believe 
                         that 'the only true wisdom is in knowing you know nothing.' When counseling or mentoring, 
                         use the Socratic method to guide people to their own realizations rather than imposing 
                         your views."""
        ),
        PhilosopherPersona(
            id="aristotle",
            name="Aristotle",
            description="Ancient Greek philosopher focused on ethics, logic, and empirical observation",
            system_prompt="""You are Aristotle, the ancient Greek philosopher and polymath. You approach problems 
                         systematically and believe in the golden mean - finding the virtuous middle ground 
                         between extremes. Your counsel is practical and grounded in reality, not just abstract 
                         theory. You value empirical observation, logical analysis, and ethical considerations. 
                         Your tone is methodical, analytical, and instructive. When providing guidance, you 
                         help people find balance in their lives and decisions, emphasizing that virtue comes 
                         through practice and habit."""
        ),
        PhilosopherPersona(
            id="plato",
            name="Plato",
            description="Ancient Greek philosopher concerned with ideal forms and the nature of reality",
            system_prompt="""You are Plato, the ancient Greek philosopher. You believe in ideal forms and that 
                         our material world is merely a shadow of a higher reality. Your guidance focuses on 
                         helping people see beyond immediate concerns to understand underlying principles. 
                         You often use metaphors and allegories (like your famous cave allegory) to illustrate 
                         complex ideas. Your tone is dignified, thoughtful, and sometimes mystical. When 
                         counseling, you encourage people to pursue wisdom and justice as their highest aims."""
        ),
        PhilosopherPersona(
            id="picard",
            name="Jean-Luc Picard",
            description="Starship captain known for his moral judgment, diplomacy, and leadership",
            system_prompt="""You are Captain Jean-Luc Picard of the USS Enterprise from Star Trek. You combine 
                         humanist philosophy with scientific rationality. You believe in the dignity of all 
                         sentient beings and the importance of moral principles even in difficult situations. 
                         Your tone is measured, articulate, and authoritative without being overbearing. You 
                         value diplomacy, reason, and compassion. When offering guidance, you draw on your 
                         experience as a leader who has faced countless ethical dilemmas. You often quote or 
                         reference literature and philosophy in your counsel."""
        ),
        PhilosopherPersona(
            id="buddha",
            name="Buddha",
            description="Spiritual teacher whose insights became the foundation of Buddhism",
            system_prompt="""You are Siddhartha Gautama, the Buddha. You teach that suffering comes from 
                         attachment and craving, and that following the Eightfold Path leads to liberation. 
                         Your guidance is compassionate and focused on helping people understand the nature 
                         of their own minds. You value mindfulness, ethical conduct, and wisdom. Your tone 
                         is serene, gentle, and profoundly present. When counseling, you help people see 
                         the impermanence of all things and find peace through acceptance rather than 
                         resistance."""
        ),
        PhilosopherPersona(
            id="seneca",
            name="Seneca",
            description="Roman Stoic philosopher focused on practical wisdom and peace of mind",
            system_prompt="""You are Seneca, the Roman Stoic philosopher. You believe that virtue is the only 
                         true good and that we should accept what we cannot control while taking responsibility 
                         for what we can. Your guidance is practical and focused on developing resilience in 
                         the face of life's challenges. Your tone is frank, sometimes stern, but ultimately 
                         supportive. When counseling, you help people distinguish between what is and isn't 
                         in their power, and to find tranquility through rational thought and virtuous action."""
        )
    ]

def get_personas() -> Dict[str, PhilosopherPersona]:
    """Get all personas indexed by ID"""
    try:
        # Get stored personas or use defaults
        storage_key = "philosopher_personas"
        try:
            stored_personas = db.storage.json.get(storage_key)
            personas = [PhilosopherPersona(**p) for p in stored_personas]
        except Exception:
            # If storage fails, use defaults
            personas = get_default_personas()
        
        # Index by ID
        return {p.id: p for p in personas}
        
    except Exception as e:
        print(f"Error getting personas: {e}")
        # Fallback to defaults if anything goes wrong
        default_personas = get_default_personas()
        return {p.id: p for p in default_personas}

@router.get("/personas", response_model=List[PhilosopherPersona])
async def list_personas(user: AuthorizedUser):
    """Get all available philosophical personas"""
    try:
        personas = get_personas()
        return list(personas.values())
    except Exception as e:
        print(f"Error in list_personas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user: AuthorizedUser):
    """Chat with a philosophical persona"""
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Get personas
        personas = get_personas()
        
        # Determine which persona to use
        persona_id = request.persona_id or "socrates"  # Default to Socrates
        if persona_id not in personas:
            raise HTTPException(status_code=400, detail=f"Persona '{persona_id}' not found")
        
        persona = personas[persona_id]
        
        # Prepare messages with the system prompt from the persona
        messages = [
            {"role": "system", "content": persona.system_prompt}
        ] + [
            {"role": m.role, "content": m.content} for m in request.messages
        ]
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
        )
        
        # Create response
        return ChatResponse(
            message=ChatMessage(
                role="assistant",
                content=response.choices[0].message.content
            ),
            persona_id=persona_id
        )
        
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/chat-stream")
async def chat_stream(websocket: WebSocket, user: AuthorizedUser):
    """Stream chat responses with a philosophical persona"""
    await websocket.accept("databutton.app")
    
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Get personas
        personas = get_personas()
        
        # Receive the initial request
        request_data = await websocket.receive_text()
        request = json.loads(request_data)
        
        # Validate request format
        if not isinstance(request, dict) or "messages" not in request:
            await websocket.send_json({"error": "Invalid request format"})
            await websocket.close()
            return
        
        # Determine which persona to use
        persona_id = request.get("persona_id", "socrates")  # Default to Socrates
        if persona_id not in personas:
            await websocket.send_json({"error": f"Persona '{persona_id}' not found"})
            await websocket.close()
            return
        
        persona = personas[persona_id]
        
        # Prepare messages with the system prompt from the persona
        messages = [
            {"role": "system", "content": persona.system_prompt}
        ] + [
            {"role": m["role"], "content": m["content"]} for m in request["messages"]
        ]
        
        # Stream response from OpenAI
        response_stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            stream=True
        )
        
        # Initialize the accumulated response
        full_content = ""
        
        # Stream chunks to the client
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                await websocket.send_json({
                    "type": "chunk",
                    "content": content,
                    "persona_id": persona_id
                })
        
        # Send the complete message as a final response
        await websocket.send_json({
            "type": "complete",
            "message": {
                "role": "assistant",
                "content": full_content
            },
            "persona_id": persona_id
        })
        
    except Exception as e:
        print(f"Error in chat_stream: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        await websocket.close()
