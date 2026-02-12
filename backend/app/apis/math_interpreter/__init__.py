from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import databutton as db
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import os
import re
import json
from openai import OpenAI
from datetime import datetime

# Initialize the OpenAI client
client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))

# Path to the interpreter mapping file
INTERPRETER_MAP_PATH = "src/data/interpreter_map.json"

# Function to load the interpreter map
def load_interpreter_map():
    """Load the interpreter map from JSON"""
    try:
        # First try to load from db.storage
        try:
            return db.storage.json.get("interpreter_map", {})
        except Exception:
            # If not in storage, try to read from file
            if os.path.exists(INTERPRETER_MAP_PATH):
                with open(INTERPRETER_MAP_PATH, 'r') as f:
                    return json.load(f)
            return {}
    except Exception as e:
        print(f"Error loading interpreter map: {e}")
        return {}

router = APIRouter(prefix="/math_interpreter")

# Supported formal systems
SUPPORTED_FORMAL_SYSTEMS = ["lean4", "tla+", "coq", "isabelle"]

class ExplainMathRequest(BaseModel):
    formal_expression: str = Field(..., description="Mathematical expression, theorem, or definition to explain")
    detail_level: str = Field("medium", description="Level of detail for the explanation: 'basic', 'medium', or 'advanced'")
    target_audience: Optional[str] = Field("general", description="Target audience, e.g., 'technical', 'general', 'financial'")
    formal_system: Optional[str] = Field("lean4", description="Formal system to use for code examples: 'lean4', 'tla+', 'coq', 'isabelle'")
    
    @property
    def validated_formal_system(self) -> str:
        """Validate and return the formal system"""
        if not self.formal_system or self.formal_system.lower() not in SUPPORTED_FORMAL_SYSTEMS:
            return "lean4"  # Default to Lean 4 for unsupported systems
        return self.formal_system.lower()

class ExplainMathResponse(BaseModel):
    explanation: str
    key_concepts: List[str]
    simplified_notation: Optional[str] = None
    formal_system_snippet: Optional[dict] = None

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

@router.post("/explain-math")
async def explain_math(request: ExplainMathRequest) -> ExplainMathResponse:
    """
    Explain a mathematical formalism in natural language. This endpoint translates formal 
    mathematical expressions, definitions, and theorems into natural language explanations 
    at the requested level of detail.
    """
    try:
        cache_key = sanitize_storage_key(f"math_explanation_{request.formal_expression}_{request.detail_level}")
        
        # Try to get from cache first
        try:
            cached_explanation = db.storage.json.get(cache_key)
            if cached_explanation:
                return ExplainMathResponse(**cached_explanation)
        except Exception:
            pass  # Continue if no cache hit
        
        # Setup OpenAI client with API key
        client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
        
        # Prepare prompt based on detail level and audience
        audience_instruction = {
            "technical": "Use precise mathematical terminology suitable for domain experts.",
            "general": "Use clear language accessible to educated non-specialists.",
            "financial": "Focus on financial implications and examples in the explanation."
        }.get(request.target_audience, "Use clear language accessible to educated non-specialists.")
        
        detail_instruction = {
            "basic": "Provide a simple, intuitive explanation with minimal formalism.",
            "medium": "Balance formal precision with intuitive understanding.",
            "advanced": "Include deeper insights and connections to related mathematical concepts."
        }.get(request.detail_level, "Balance formal precision with intuitive understanding.")
        
        # Add formal system instructions
        formal_system = request.validated_formal_system
        formal_system_instruction = {
            "lean4": "Include a Lean 4 formalization of the mathematics using dependent type theory.",
            "tla+": "Include a TLA+ specification of the concept using temporal logic.",
            "coq": "Include a Coq formalization using the Calculus of Inductive Constructions.",
            "isabelle": "Include an Isabelle/HOL formalization using Higher-Order Logic."
        }.get(formal_system, "Include a Lean 4 formalization of the mathematics using dependent type theory.")
        
        # Generate explanation using GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a mathematical interpreter that explains formal mathematical concepts in natural language. {audience_instruction} {detail_instruction} {formal_system_instruction}"}, 
                {"role": "user", "content": f"Explain the following mathematical formalism:\n\n{request.formal_expression}\n\nProvide:"
                                         f"\n1. A clear explanation"
                                         f"\n2. A list of key concepts involved"
                                         f"\n3. If appropriate, a simplified notation or representation"
                                         f"\n4. A formalization in {formal_system} with a brief explanation of the code"}
            ]
        )
        
        # Extract explanation, key concepts, and simplified notation
        explanation_text = response.choices[0].message.content
        
        # Parse the response (simple approach)
        sections = explanation_text.split("\n\n")
        
        explanation = sections[0] if sections else explanation_text
        key_concepts = []
        simplified_notation = None
        formal_system_code = None
        
        for section in sections[1:]:
            if section.startswith("Key concepts") or section.startswith("2."):
                # Extract concepts listed after a colon or numbered list
                concept_text = section.split(":", 1)[1] if ":" in section else section
                key_concepts = [c.strip() for c in concept_text.split("-") if c.strip()]
                # Clean up any numbering
                key_concepts = [c.lstrip("123456789. ") for c in key_concepts]
            
            elif section.startswith("Simplified") or section.startswith("3."):
                # Extract the simplified notation part
                simplified_notation = section.split(":", 1)[1].strip() if ":" in section else section.strip()
            
            elif section.startswith(f"{formal_system} formalization") or section.startswith("4.") or "```" in section.lower():
                # Extract formal system code
                code_parts = section.split("```")
                code = code_parts[1].strip() if len(code_parts) > 1 else section
                
                # Extract the explanation that might come after the code block
                explanation_text = ""
                if len(code_parts) > 2 and code_parts[2].strip():
                    explanation_text = code_parts[2].strip()
                
                formal_system_code = {
                    "system": formal_system.upper() if formal_system.lower() != "tla+" else "TLA+",
                    "code": code,
                    "explanation": explanation_text or f"Formalization of the concept in {formal_system}."
                }
        
        # Ensure we have some key concepts if parsing failed
        if not key_concepts:
            key_concepts = ["Mathematical formalism", "Formal verification"]
        
        return ExplainMathResponse(
            explanation=explanation,
            key_concepts=key_concepts,
            simplified_notation=simplified_notation,
            formal_system_snippet=formal_system_code
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining mathematical expression: {str(e)}") from e

class InterpretOperationRequest(BaseModel):
    operation: str = Field(..., description="Mathematical operation or transformation to interpret")
    context: Optional[str] = Field(None, description="Context for the operation (e.g., portfolio, security)")

class InterpretOperationResponse(BaseModel):
    interpretation: str
    implications: List[str]
    verification_status: str

@router.post("/interpret-operation")
async def interpret_operation(request: InterpretOperationRequest) -> InterpretOperationResponse:
    """
    Interpret a mathematical operation or transformation in the context of finance or security.
    This endpoint translates formal operations into understandable explanations with practical implications.
    """
    try:
        # Setup OpenAI client with API key
        client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
        
        context = request.context or "general financial context"
        
        # Generate interpretation using GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial mathematics interpreter that explains formal operations in practical terms."}, 
                {"role": "user", "content": f"Interpret the following mathematical operation in the context of {context}:\n\n{request.operation}\n\nProvide:"
                                         f"\n1. A clear interpretation of what this operation means"
                                         f"\n2. Practical implications of this operation"
                                         f"\n3. Verification status (e.g., 'Verified', 'Partially Verified', 'Theoretical')"}
            ]
        )
        
        # Extract response
        interpretation_text = response.choices[0].message.content
        
        # Simple parsing of the response
        sections = interpretation_text.split("\n\n")
        
        interpretation = sections[0] if sections else interpretation_text
        implications = []
        verification_status = "Theoretical"  # Default
        
        for section in sections[1:]:
            if section.lower().startswith("implication") or section.startswith("2."):
                # Extract implications
                implication_text = section.split(":", 1)[1] if ":" in section else section
                implications = [imp.strip() for imp in implication_text.split("-") if imp.strip()]
                implications = [imp.lstrip("123456789. ") for imp in implications]
            
            elif section.lower().startswith("verification") or section.startswith("3."):
                # Extract verification status
                for status in ["Verified", "Partially Verified", "Theoretical", "Unverified"]:
                    if status.lower() in section.lower():
                        verification_status = status
                        break
        
        # Ensure we have some implications if parsing failed
        if not implications:
            implications = ["Affects financial calculations", "May impact investment decisions"]
        
        return InterpretOperationResponse(
            interpretation=interpretation,
            implications=implications,
            verification_status=verification_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interpreting operation: {str(e)}") from e

class InterpretVerificationRequest(BaseModel):
    verification_statement: str = Field(..., description="Formal verification statement or theorem to interpret")
    domain: Optional[str] = Field("financial", description="Domain of verification (e.g., 'financial', 'security')")

class InterpretVerificationResponse(BaseModel):
    interpretation: str
    practical_meaning: str
    confidence_level: str
    assumptions: List[str]

class TranslateToFormalRequest(BaseModel):
    description: str = Field(..., description="Natural language description to translate to formal specification")
    domain: str = Field(..., description="Domain of the specification (e.g., 'portfolio', 'security')")
    format: str = Field("lean4", description="Target formalism format (e.g., 'lean4', 'tla+', 'coq', 'isabelle')")

    @property
    def formal_system(self) -> str:
        """Validate and return the formal system format"""
        format_lower = self.format.lower()
        if format_lower not in SUPPORTED_FORMAL_SYSTEMS:
            return "lean4"  # Default to Lean 4 for unsupported formats
        return format_lower

class TranslateToFormalResponse(BaseModel):
    formal_specification: str
    verification_hints: List[str]
    confidence: float  # 0.0 to 1.0 indicating confidence in the translation

class TranslateFromFormalRequest(BaseModel):
    formal_code: str = Field(..., description="Formal system code to translate to natural language")
    formal_system: str = Field("lean4", description="Source formal system: 'lean4', 'tla+', 'coq', 'isabelle'")
    detail_level: str = Field("medium", description="Level of detail for the explanation: 'basic', 'medium', or 'advanced'")
    domain: Optional[str] = Field("general", description="Domain context for the translation, e.g., 'financial', 'security'")
    
    @property
    def validated_formal_system(self) -> str:
        """Validate and return the formal system"""
        if not self.formal_system or self.formal_system.lower() not in SUPPORTED_FORMAL_SYSTEMS:
            return "lean4"  # Default to Lean 4 for unsupported systems
        return self.formal_system.lower()

class TranslateFromFormalResponse(BaseModel):
    explanation: str
    key_concepts: List[str]
    example_applications: List[str] = Field(default_factory=list, description="Example applications of the formal code")
    confidence: float  # 0.0 to 1.0 indicating confidence in the translation

class TranslateToNaturalRequest(BaseModel):
    formalism: str = Field(..., description="Formal specification to translate to natural language")
    domain: str = Field(..., description="Domain of the specification (e.g., 'portfolio', 'security')")
    detail_level: str = Field("medium", description="Level of detail for the explanation: 'basic', 'medium', or 'advanced'")
    formal_system: Optional[str] = Field("lean4", description="Source formal system: 'lean4', 'tla+', 'coq', 'isabelle'")
    
    @property
    def validated_formal_system(self) -> str:
        """Validate and return the formal system"""
        if not self.formal_system or self.formal_system.lower() not in SUPPORTED_FORMAL_SYSTEMS:
            return "lean4"  # Default to Lean 4 for unsupported systems
        return self.formal_system.lower()

class TranslateToNaturalResponse(BaseModel):
    explanation: str
    key_concepts: List[str]

@router.post("/interpret-verification")
async def interpret_verification(request: InterpretVerificationRequest) -> InterpretVerificationResponse:
    """
    Interpret a formal verification statement or theorem and explain its practical significance.
    This endpoint makes formal verification results accessible to non-specialists.
    """
    try:
        # Setup OpenAI client with API key
        client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
        
        domain = request.domain or "financial"
        
        # Generate interpretation using GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a formal verification interpreter specializing in {domain} systems. Explain verification results clearly for non-specialists."}, 
                {"role": "user", "content": f"Interpret the following formal verification statement:\n\n{request.verification_statement}\n\nProvide:"
                                         f"\n1. A clear interpretation of what this verification means"
                                         f"\n2. The practical significance for users or stakeholders"
                                         f"\n3. A confidence assessment (e.g., 'Mathematical certainty', 'High confidence', 'Theoretical')"
                                         f"\n4. Key assumptions underlying this verification"}
            ]
        )
        
        # Extract response
        interpretation_text = response.choices[0].message.content
        
        # Simple parsing
        sections = interpretation_text.split("\n\n")
        
        interpretation = sections[0] if sections else interpretation_text
        practical_meaning = ""
        confidence_level = "Theoretical" 
        assumptions = []
        
        for section in sections[1:]:
            if section.lower().startswith("practical") or section.startswith("2."):
                practical_meaning = section.split(":", 1)[1].strip() if ":" in section else section.strip()
            
            elif section.lower().startswith("confidence") or section.startswith("3."):
                confidence_text = section.lower()
                if "mathematical certainty" in confidence_text:
                    confidence_level = "Mathematical certainty"
                elif "high confidence" in confidence_text:
                    confidence_level = "High confidence"
                elif "medium confidence" in confidence_text:
                    confidence_level = "Medium confidence"
                elif "low confidence" in confidence_text:
                    confidence_level = "Low confidence"
                else:
                    confidence_level = "Theoretical"
            
            elif section.lower().startswith("assumption") or section.startswith("4."):
                # Extract assumptions
                assumption_text = section.split(":", 1)[1] if ":" in section else section
                assumptions = [a.strip() for a in assumption_text.split("-") if a.strip()]
                assumptions = [a.lstrip("123456789. ") for a in assumptions]
        
        # Ensure we have some assumptions if parsing failed
        if not assumptions:
            assumptions = ["System operates as specified", "Input data is valid"]
        
        return InterpretVerificationResponse(
            interpretation=interpretation,
            practical_meaning=practical_meaning or "This verification ensures system integrity and correctness.",
            confidence_level=confidence_level,
            assumptions=assumptions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interpreting verification: {str(e)}") from e

# Helper function to extract JSON from possibly text-wrapped response
def extract_json(text: str) -> Dict:
    """Extract JSON from text, handling potential text wrapping"""
    try:
        # Try to parse the entire text as JSON first
        return json.loads(text)
    except json.JSONDecodeError:
        # Look for JSON-like structure in the text
        try:
            # Find content between curly braces
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return json.loads(match.group(0))
            else:
                # Fall back to creating a simple structure
                lines = text.split('\n')
                result = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        result[key.strip()] = value.strip()
                return result
        except Exception:
            # If all parsing fails, return a minimal valid structure
            return {"explanation": text, "key_concepts": [], "related_concepts": [], "examples": [], "confidence": 0.5}

class SimpleTextRequest(BaseModel):
    text: str = Field(..., description="Natural language text to translate")

class FormalMatchResponse(BaseModel):
    mapping_id: str
    formal_code: str
    symbol: str
    confidence: float = 1.0

@router.post("/translate-to-formal")
async def translate_to_formal(request: SimpleTextRequest) -> FormalMatchResponse:
    """Translate natural language to formal specification using the mapping file
    
    This is a simpler version for the vertical slice that matches text against known mappings.
    """
    # Load the interpreter map
    interpreter_map = load_interpreter_map()
    
    # Initialize variables
    best_match = None
    best_confidence = 0.0
    
    # Get natural language mappings
    nl_to_formal = interpreter_map.get("natural_to_formal", {})
    
    # Simple matching algorithm - in a real implementation, this would use embeddings or LLM
    for mapping_id, mapping in nl_to_formal.items():
        nl_text = mapping.get("nl", "").lower()
        
        # Simple keyword matching - replace with proper NLP in production
        if any(keyword in request.text.lower() for keyword in nl_text.split()):
            confidence = 1.0  # Simplified confidence score
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = mapping_id
    
    # If no match found
    if not best_match:
        raise HTTPException(status_code=404, detail="No matching formal specification found")
    
    # Get the mapping
    mapping = nl_to_formal[best_match]
    
    # Try to load the Lean file
    lean_file_path = f"src/lean/{mapping.get('lean_file', '')}"
    lean_code = ""
    if os.path.exists(lean_file_path):
        try:
            with open(lean_file_path, 'r') as f:
                lean_code = f.read()
        except Exception as e:
            print(f"Error reading Lean file: {e}")
    
    return FormalMatchResponse(
        mapping_id=best_match,
        formal_code=lean_code,
        symbol=mapping.get("symbol", ""),
        confidence=best_confidence
    )

@router.post("/translate-to-natural")
async def translate_to_natural(request: dict) -> dict:
    """Translate formal to natural language using the mapping file
    
    This is a simpler version for the vertical slice that returns the natural language from the mapping.
    """
    # Load the interpreter map
    interpreter_map = load_interpreter_map()
    
    # Get natural language mappings
    nl_to_formal = interpreter_map.get("natural_to_formal", {})
    
    # Get the mapping
    mapping_id = request.get("mapping_id")
    if not mapping_id or mapping_id not in nl_to_formal:
        raise HTTPException(status_code=404, detail="Mapping ID not found")
    
    mapping = nl_to_formal[mapping_id]
    
    return {
        "nl": mapping.get("nl", ""),
        "symbol": mapping.get("symbol", ""),
        "lean_file": mapping.get("lean_file", "")
    }

# Original endpoints with detailed implementations
@router.post("/translate-from-formal-complex", response_model=TranslateFromFormalResponse)
async def translate_from_formal_complex(request: TranslateFromFormalRequest) -> TranslateFromFormalResponse:
    """Translate natural language to a formal mathematical specification
    
    This endpoint takes a natural language description and translates it into a
    formal mathematical specification in the requested format (e.g., Lean 4).
    """
    # Check cache first
    cache_key = sanitize_storage_key(f"to_formal_{request.description[:50]}_{request.domain}_{request.format}")
    
    # Try to get from cache first
    try:
        cached_result = db.storage.json.get(cache_key)
        if cached_result:
            return TranslateToFormalResponse(**cached_result)
    except Exception:
        pass  # Continue if no cache hit
    
    # Domain-specific instructions
    domain_instructions = {
        "portfolio": "focus on financial invariants, balance preservation, and portfolio value additivity",
        "security": "focus on tamper-evidence, non-repudiation, and cryptographic properties",
        "trust_fund": "focus on temporal integrity, fund allocation rules, and beneficiary constraints",
        "legacy": "focus on inheritance rules, temporal constraints, and generational transfers",
        "hardcard": "focus on physical security, hardware interfaces, and authentication protocols",
        "ledger": "focus on hash chain integrity, transaction validity, and consistency properties"
    }
    
    # Format-specific templates
    format_templates = {
        "lean4": "Use Lean 4 syntax with proper theorem, axiom, and definition declarations. Lean 4 uses dependent type theory and is the primary verification language for the Hardcard system.",
        "tla+": "Use TLA+ syntax with proper module structure and temporal logic operators. TLA+ is used for protocol verification and state machine modeling.",
        "coq": "Use Coq syntax with appropriate tactics and proof structures. Coq is used for mathematical theory development.",
        "isabelle": "Use Isabelle/HOL syntax with Isar proof style. Isabelle/HOL is used for hardware modeling and protocol verification."
    }
    
    # Get instructions for the requested domain and format
    domain_instruction = domain_instructions.get(request.domain.lower(), "")
    format_instruction = format_templates.get(request.formal_system, format_templates["lean4"])
    
    try:
        # Setup OpenAI client with API key
        client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
        
        prompt = f"""
        You are a mathematical formalizer specialized in translating natural language descriptions 
        into precise formal mathematical specifications.
        
        Translate the following description into a formal specification using {request.formal_system}:
        ```
        {request.description}
        ```
        
        Domain instructions: {domain_instruction}
        Format instructions: {format_instruction}
        
        Return your response as a valid JSON object with these fields:
        1. formal_specification: The formal mathematical specification in {request.formal_system} syntax
        2. verification_hints: A list of hints or suggestions for verifying this specification
        3. confidence: A number between 0.0 and 1.0 indicating your confidence in this translation
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a mathematical formalizer specialized in translating natural language descriptions into precise formal mathematical specifications."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        # Extract JSON from response
        response_text = response.choices[0].message.content.strip()
        json_content = extract_json(response_text)
        
        translation_data = TranslateToFormalResponse(
            formal_specification=json_content.get("formal_specification", "No formal specification provided"),
            verification_hints=json_content.get("verification_hints", []),
            confidence=json_content.get("confidence", 0.5)
        )
        
        # Cache the result
        try:
            db.storage.json.put(cache_key, translation_data.dict())
        except Exception as cache_error:
            print(f"Cache storage error: {cache_error}")
        
        return translation_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating to formal specification: {str(e)}") from e

@router.post("/translate-to-natural-complex", response_model=TranslateToNaturalResponse)
async def translate_to_natural_complex(request: TranslateToNaturalRequest) -> TranslateToNaturalResponse:
    """Translate a formal mathematical specification to natural language
    
    This endpoint takes a formal mathematical specification and translates it
    into a natural language explanation at the requested detail level.
    """
    # Check cache first
    cache_key = sanitize_storage_key(f"to_natural_{request.formalism[:50]}_{request.domain}_{request.detail_level}_{request.validated_formal_system}")
    
    # Try to get from cache first
    try:
        cached_result = db.storage.json.get(cache_key)
        if cached_result:
            return TranslateToNaturalResponse(**cached_result)
    except Exception:
        pass  # Continue if no cache hit
    
    # Domain-specific context
    domain_context = {
        "portfolio": "This formalism relates to financial portfolio management within the Hardcard system.",
        "security": "This formalism relates to security properties of the Hardcard system.",
        "trust_fund": "This formalism relates to trust fund management in the Hardcard system.",
        "legacy": "This formalism relates to legacy and inheritance rules in the Hardcard system.",
        "hardcard": "This formalism relates to the physical Hardcard device specifications.",
        "ledger": "This formalism relates to the ledger data structure in the Hardcard system."
    }
    
    # Detail level adjustments
    detail_instructions = {
        "basic": "Explain in simple terms that a high school student could understand. Avoid technical jargon.",
        "medium": "Explain at an undergraduate level with some technical terms but clear explanations.",
        "advanced": "Explain at a graduate level with appropriate technical terminology and depth."
    }
    
    # Formal system context
    formal_system_context = {
        "lean4": "This is written in Lean 4, a dependent type theory based proof assistant that is the primary verification language for Hardcard.",
        "tla+": "This is written in TLA+, a specification language based on temporal logic used for modeling concurrent and distributed systems.",
        "coq": "This is written in Coq, a proof assistant based on the Calculus of Inductive Constructions.",
        "isabelle": "This is written in Isabelle/HOL, a higher-order logic proof assistant often used for hardware verification."
    }
    
    context = domain_context.get(request.domain.lower(), "")
    detail = detail_instructions.get(request.detail_level.lower(), detail_instructions["medium"])
    system_context = formal_system_context.get(request.validated_formal_system, formal_system_context["lean4"])
    
    try:
        # Setup OpenAI client with API key
        client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
        
        prompt = f"""
        You are a mathematical interpreter specialized in explaining formal mathematical specifications in natural language.
        
        Translate the following formal specification into natural language:
        ```
        {request.formalism}
        ```
        
        Context: {context}
        Formal system context: {system_context}
        Detail level: {detail}
        
        Return your response as a valid JSON object with these fields:
        1. explanation: A clear explanation in natural language at the requested detail level
        2. key_concepts: A list of key mathematical concepts referenced in the formalism
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a mathematical interpreter specialized in explaining formal mathematical specifications in natural language."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Extract JSON from response
        response_text = response.choices[0].message.content.strip()
        json_content = extract_json(response_text)
        
        translation_data = TranslateToNaturalResponse(
            explanation=json_content.get("explanation", "No explanation provided"),
            key_concepts=json_content.get("key_concepts", [])
        )
        
        # Cache the result
        try:
            db.storage.json.put(cache_key, translation_data.dict())
        except Exception as cache_error:
            print(f"Cache storage error: {cache_error}")
        
        return translation_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating to natural language: {str(e)}") from e

@router.post("/translate-from-formal", response_model=TranslateFromFormalResponse)
async def translate_from_formal(request: TranslateFromFormalRequest) -> TranslateFromFormalResponse:
    """Translate formal system code to natural language
    
    This endpoint takes code written in a formal verification system (e.g., Lean 4, TLA+)
    and translates it into a natural language explanation at the requested detail level.
    This is the counterpart to the translate-to-formal endpoint.
    """
    # Check cache first
    cache_key = sanitize_storage_key(f"from_formal_{request.formal_code[:50]}_{request.validated_formal_system}_{request.detail_level}")
    
    # Try to get from cache first
    try:
        cached_result = db.storage.json.get(cache_key)
        if cached_result:
            return TranslateFromFormalResponse(**cached_result)
    except Exception:
        pass  # Continue if no cache hit
    
    # Formal system context - providing information about each system's features
    formal_system_context = {
        "lean4": "Lean 4 is a dependently typed theorem prover based on dependent type theory and is the primary verification language for the Hardcard system.",
        "tla+": "TLA+ is a formal specification language based on temporal logic that excels at describing state machines and concurrent systems.",
        "coq": "Coq is a proof assistant based on the Calculus of Inductive Constructions, with sophisticated proof automation capabilities.",
        "isabelle": "Isabelle/HOL is a generic proof assistant that implements higher-order logic, used extensively in hardware verification."
    }
    
    # Domain-specific context
    domain_context = {
        "financial": "This formalism relates to financial systems such as portfolio management, budget constraints, or accounting invariants.",
        "security": "This formalism relates to security properties such as authentication, authorization, and data protection.",
        "hardcard": "This formalism relates to the Hardcard system's physical and logical security features.",
        "ledger": "This formalism relates to distributed ledger properties such as integrity, consistency, and immutability.",
        "general": "This formalism represents mathematical properties without domain-specific context."
    }
    
    # Detail level adjustments
    detail_instructions = {
        "basic": "Explain in simple terms that a high school student could understand. Avoid technical jargon.",
        "medium": "Explain at an undergraduate level with some technical terms but clear explanations.",
        "advanced": "Explain at a graduate level with appropriate technical terminology and depth."
    }
    
    system_context = formal_system_context.get(request.validated_formal_system, formal_system_context["lean4"])
    context = domain_context.get(request.domain.lower(), domain_context["general"])
    detail = detail_instructions.get(request.detail_level.lower(), detail_instructions["medium"])
    
    try:
        # Setup OpenAI client with API key
        client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
        
        prompt = f"""
        You are a formal methods expert specialized in translating formal verification code into natural language explanations. 
        You understand multiple formal systems including Lean 4, TLA+, Coq, and Isabelle/HOL.
        
        Translate the following {request.validated_formal_system.upper()} code into natural language:
        ```
        {request.formal_code}
        ```
        
        Formal system: {system_context}
        Domain context: {context}
        Detail level: {detail}
        
        Return your response as a valid JSON object with these fields:
        1. explanation: A clear explanation in natural language at the requested detail level
        2. key_concepts: A list of key mathematical and logical concepts used in the code
        3. example_applications: A list of example applications or implications of this code
        4. confidence: A number between 0.0 and 1.0 indicating your confidence in this translation
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a formal methods expert specialized in translating formal verification code into natural language explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Extract JSON from response
        response_text = response.choices[0].message.content.strip()
        json_content = extract_json(response_text)
        
        translation_data = TranslateFromFormalResponse(
            explanation=json_content.get("explanation", "No explanation provided"),
            key_concepts=json_content.get("key_concepts", []),
            example_applications=json_content.get("example_applications", []),
            confidence=json_content.get("confidence", 0.5)
        )
        
        # Cache the result
        try:
            db.storage.json.put(cache_key, translation_data.dict())
        except Exception as cache_error:
            print(f"Cache storage error: {cache_error}")
        
        return translation_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating from formal system: {str(e)}") from e