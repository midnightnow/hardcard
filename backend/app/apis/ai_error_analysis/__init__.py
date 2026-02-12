from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import databutton as db
from datetime import datetime
import uuid
from openai import OpenAI

router = APIRouter()

# Request model for error analysis
class ErrorAnalysisRequest(BaseModel):
    message: str
    stack: Optional[str] = None
    component: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    error_id: Optional[str] = None

# Response model for error analysis
class ErrorAnalysisResponse(BaseModel):
    analysis_id: str
    insights: List[str]
    probable_causes: List[str]
    suggested_fixes: List[str]
    code_examples: Optional[List[Dict[str, str]]] = None

@router.post("/analyze-error")
def analyze_error(request: ErrorAnalysisRequest) -> ErrorAnalysisResponse:
    """
    Analyzes a JavaScript error using Claude AI to provide intelligent insights and fix suggestions.
    
    This endpoint uses AI to understand the error, identify potential causes, and suggest specific code fixes.
    The analysis considers the error message, stack trace, component context, and historical error patterns.
    """
    try:
        # Create a unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Check if we have an OpenAI API key
        openai_api_key = db.secrets.get("OPENAI_API_KEY")
        if not openai_api_key:
            # Fallback to simple analysis if no API key
            return fallback_error_analysis(request, analysis_id)
            
        # Get historical errors for context if available
        error_history = get_error_history(request.component)
        
        # Create prompt for Claude with error details and contextual info
        client = OpenAI(api_key=openai_api_key)
        
        # Build a detailed prompt with all available information
        prompt = build_error_analysis_prompt(request, error_history)
        
        # Get Claude's analysis
        completion = client.chat.completions.create(
            model="gpt-4o-mini",  # Using OpenAI as a stand-in for Claude in this implementation
            messages=[
                {"role": "system", "content": "You are an expert JavaScript and TypeScript developer specializing in React and modern frontend frameworks. Your task is to analyze errors and provide clear, actionable insights and fix suggestions. Be specific and practical in your advice."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse Claude's response
        analysis = parse_ai_response(completion.choices[0].message.content)
        
        # Store the analysis for future reference
        store_error_analysis(request, analysis, analysis_id)
        
        return ErrorAnalysisResponse(
            analysis_id=analysis_id,
            insights=analysis.get("insights", []),
            probable_causes=analysis.get("probable_causes", []),
            suggested_fixes=analysis.get("suggested_fixes", []),
            code_examples=analysis.get("code_examples", [])
        )
        
    except Exception as e:
        print(f"Error in analyze_error: {str(e)}")
        # Fall back to simple analysis if AI fails
        return fallback_error_analysis(request, str(uuid.uuid4()))

def build_error_analysis_prompt(request: ErrorAnalysisRequest, error_history: List[Dict[str, Any]]) -> str:
    """Build a detailed prompt for the AI with all available error information"""
    prompt = f"""Please analyze this JavaScript/TypeScript error and provide insights:

ERROR MESSAGE: {request.message}
"""
    
    if request.stack:
        prompt += f"\n\nSTACK TRACE: {request.stack}"
        
    if request.component:
        prompt += f"\n\nCOMPONENT: {request.component}"
        
    if request.context:
        prompt += f"\n\nCONTEXT: {str(request.context)}"
    
    if error_history:
        prompt += "\n\nRELATED HISTORICAL ERRORS:\n"
        for i, error in enumerate(error_history[:3]):  # Include up to 3 historical errors
            prompt += f"{i+1}. {error.get('message', 'Unknown')}\n"
    
    prompt += """\n\nPlease provide your analysis in this format:

1. INSIGHTS: List 2-3 key observations about what this error indicates
2. PROBABLE CAUSES: List 3-4 likely root causes
3. SUGGESTED FIXES: List 3-5 specific solutions with clear steps
4. CODE EXAMPLES: Provide 1-2 code snippets demonstrating the fix

Make your analysis specific to React and modern frontend development. Be practical and actionable."""
    
    return prompt

def parse_ai_response(response: str) -> Dict[str, Any]:
    """Parse the AI response into structured sections"""
    sections = {
        "insights": [],
        "probable_causes": [],
        "suggested_fixes": [],
        "code_examples": []
    }
    
    # Simple parsing - a more robust parser would be better in production
    current_section = None
    code_block = ""
    in_code_block = False
    
    for line in response.split('\n'):
        line = line.strip()
        
        # Check for section headers
        if "INSIGHTS:" in line.upper() or "INSIGHT:" in line.upper():
            current_section = "insights"
            continue
        elif "PROBABLE CAUSES:" in line.upper() or "CAUSE:" in line.upper():
            current_section = "probable_causes"
            continue
        elif "SUGGESTED FIXES:" in line.upper() or "SOLUTION:" in line.upper():
            current_section = "suggested_fixes"
            continue
        elif "CODE EXAMPLES:" in line.upper() or "CODE EXAMPLE:" in line.upper():
            current_section = "code_examples"
            continue
        
        # Skip empty lines
        if not line:
            continue
            
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End of code block
                in_code_block = False
                if current_section == "code_examples" and code_block:
                    sections["code_examples"].append({"code": code_block})
                    code_block = ""
            else:
                # Start of code block
                in_code_block = True
                code_block = ""
            continue
            
        if in_code_block:
            code_block += line + "\n"
            continue
        
        # Regular content lines
        if current_section and line:
            # Strip bullet points and numbers
            clean_line = line
            if clean_line.startswith(('-', '*', '+')) or (clean_line[0].isdigit() and clean_line[1:].startswith((')', '.', ':'))):
                clean_line = clean_line.split(' ', 1)[1] if ' ' in clean_line else clean_line
                
            if current_section != "code_examples":  # Code examples are handled separately
                sections[current_section].append(clean_line)
    
    return sections

def get_error_history(component: Optional[str]) -> List[Dict[str, Any]]:
    """Get historical errors for the same component"""
    try:
        all_errors = db.storage.json.get("client_errors", default={"errors": []})
        errors = all_errors.get("errors", [])
        
        if component:
            # Filter to errors from the same component
            filtered_errors = [e for e in errors if e.get("component") == component]
            return filtered_errors[:10]  # Return up to 10 related errors
        
        return errors[:10]  # Return the 10 most recent errors
    except Exception as e:
        print(f"Error getting error history: {str(e)}")
        return []

def store_error_analysis(request: ErrorAnalysisRequest, analysis: Dict[str, Any], analysis_id: str) -> None:
    """Store the error analysis for future reference"""
    try:
        # Get existing analyses or create new dictionary
        try:
            analyses = db.storage.json.get("error_analyses")
        except FileNotFoundError:
            analyses = {"analyses": []}
        
        # Create analysis record
        analysis_record = {
            "id": analysis_id,
            "timestamp": datetime.now().isoformat(),
            "error_message": request.message,
            "component": request.component,
            "error_id": request.error_id,
            "analysis": analysis
        }
        
        # Add new analysis and maintain last 100 analyses only
        analyses["analyses"] = [analysis_record] + analyses.get("analyses", [])[:99]
        
        # Save back to storage
        db.storage.json.put("error_analyses", analyses)
    except Exception as e:
        print(f"Error storing analysis: {str(e)}")

def fallback_error_analysis(request: ErrorAnalysisRequest, analysis_id: str) -> ErrorAnalysisResponse:
    """Provide a basic error analysis when AI is unavailable"""
    # Basic error type detection
    error_type = "unknown"
    message = request.message.lower()
    
    if "undefined" in message or "null" in message:
        error_type = "null_reference"
    elif "syntax" in message:
        error_type = "syntax"
    elif "type" in message or "typeerror" in message:
        error_type = "type"
    elif "network" in message or "fetch" in message or "request" in message:
        error_type = "network"
    elif "promise" in message or "async" in message:
        error_type = "async"
    elif "memory" in message or "heap" in message:
        error_type = "memory"
    
    # Return appropriate analysis based on error type
    if error_type == "null_reference":
        return ErrorAnalysisResponse(
            analysis_id=analysis_id,
            insights=[
                "This is a null/undefined reference error",
                "You're trying to access a property on an object that doesn't exist"
            ],
            probable_causes=[
                "The object hasn't been initialized yet",
                "An API response might be empty or in an unexpected format",
                "A component prop might be missing or undefined"
            ],
            suggested_fixes=[
                "Add null checks before accessing properties",
                "Use optional chaining (obj?.prop instead of obj.prop)",
                "Provide default values using || or ??",
                "Ensure data is loaded before rendering components that depend on it"
            ],
            code_examples=[
                {"code": "// Before\nconst value = data.user.name;\n\n// After\nconst value = data?.user?.name ?? 'Default Name';"}
            ]
        )
    elif error_type == "syntax":
        return ErrorAnalysisResponse(
            analysis_id=analysis_id,
            insights=[
                "This is a syntax error",
                "There's an issue with the structure of your code"
            ],
            probable_causes=[
                "Missing closing bracket, parenthesis, or curly brace",
                "Typo in a JavaScript keyword",
                "Using JSX without importing React"
            ],
            suggested_fixes=[
                "Check for balanced brackets and braces",
                "Verify all strings are properly closed",
                "Use a linter to catch syntax errors",
                "Ensure you're using correct JavaScript syntax"
            ],
            code_examples=[]
        )
    else:
        # Generic analysis for other error types
        return ErrorAnalysisResponse(
            analysis_id=analysis_id,
            insights=[
                "This appears to be a runtime error in your application",
                "The issue might be related to component state or data flow"
            ],
            probable_causes=[
                "Attempting to access properties on undefined objects",
                "Asynchronous operation timing issues",
                "Incorrect prop usage between components",
                "State updates on unmounted components"
            ],
            suggested_fixes=[
                "Add error boundaries around problematic components",
                "Implement proper loading states for async operations",
                "Add type checking for component props",
                "Check component lifecycle and cleanup functions",
                "Use console.log to track component rendering and state changes"
            ],
            code_examples=[]
        )

@router.get("/get-analyses/{component}")
def get_ai_error_analyses_for_component(component: str):
    """Get all error analyses for a specific component"""
    try:
        try:
            analyses = db.storage.json.get("error_analyses")
        except FileNotFoundError:
            return {"analyses": []}
        
        component_analyses = [
            analysis for analysis in analyses.get("analyses", [])
            if analysis.get("component") == component
        ]
        
        return {"analyses": component_analyses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list-analyses")
def list_error_analyses2():
    """List all error analyses with basic information"""
    try:
        try:
            analyses = db.storage.json.get("error_analyses")
        except FileNotFoundError:
            return {"analyses": []}
        
        # Return simplified analysis information
        simple_analyses = [
            {
                "id": a.get("id"),
                "timestamp": a.get("timestamp"),
                "error_message": a.get("error_message"),
                "component": a.get("component")
            }
            for a in analyses.get("analyses", [])
        ]
        
        return {"analyses": simple_analyses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-analysis/{analysis_id}")
def get_ai_error_analysis(analysis_id: str):
    """Get a specific error analysis by ID"""
    try:
        try:
            analyses = db.storage.json.get("error_analyses")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        for analysis in analyses.get("analyses", []):
            if analysis.get("id") == analysis_id:
                return analysis
        
        raise HTTPException(status_code=404, detail="Analysis not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
