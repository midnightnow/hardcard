from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
import json
import openai
import databutton as db
import base64
from io import BytesIO
from PIL import Image
import re
import time
from datetime import datetime # Added for timestamping


from app.libs.memory_service import MemoryService, MemoryFrame

router = APIRouter(prefix="/visual-analysis")
memory_service = MemoryService()

# Models for request and response
class VisualElement(BaseModel):
    type: str = Field(..., description="Type of UI element (button, form, nav, text, image, etc.)")
    text: Optional[str] = Field(None, description="Text content of the element")
    location: Optional[str] = Field(None, description="Position information of the element")
    state: Optional[str] = Field(None, description="Current state of the element (focused, disabled, etc.)")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Additional attributes of the element")
    priority: Optional[int] = Field(None, description="Priority for attention (1-10, higher is more important)")
    accessibility_issues: Optional[List[str]] = Field(None, description="List of accessibility issues")
    interactions: Optional[List[str]] = Field(None, description="Possible user interactions with this element")

class VisualData(BaseModel):
    pageUrl: Optional[str] = Field(None, description="URL of the page being analyzed")
    screenshotBase64: Optional[str] = Field(None, description="Base64 encoded screenshot")
    elements: Optional[List[VisualElement]] = Field(None, description="List of visual elements on the page")
    viewportSize: Optional[Dict[str, int]] = Field(None, description="Size of the viewport")
    additionalContext: Optional[str] = Field(None, description="Additional context about the visual")
    taskContext: Optional[str] = Field(None, description="Context about the current task")
    userAction: Optional[str] = Field(None, description="What the user was doing")
    environmentContext: Optional[Dict[str, Any]] = Field(None, description="Information about the environment")

class VisualAnalysisRequest(BaseModel):
    visual: VisualData = Field(..., description="Visual data to analyze")
    analysisType: str = Field("comprehensive", description="Type of analysis to perform (basic, accessibility, semantic, layout, comprehensive, development, memory)")
    storeInMemory: bool = Field(True, description="Whether to store the analysis in memory")
    userId: Optional[str] = Field(None, description="User ID for memory storage")
    memoryTags: List[str] = Field(default_factory=lambda: ["visual", "screenshot"], description="Tags for memory storage")

class VisualAnalysisResponse(BaseModel):
    analysis: Dict[str, Any] = Field(..., description="Analysis results")
    enhancedElements: Optional[List[VisualElement]] = Field(None, description="Elements with additional analysis information")
    memoryId: Optional[str] = Field(None, description="ID of the stored memory")
    executionTime: Optional[float] = Field(None, description="Time taken to perform the analysis")
    elementCount: Optional[int] = Field(None, description="Number of elements analyzed")
    screenshotDimensions: Optional[Dict[str, int]] = Field(None, description="Dimensions of the analyzed screenshot")
    keyInsights: Optional[List[str]] = Field(None, description="Key insights from the analysis")

@router.post("/analyze", description="Analyze a visual using AI and store it in memory")
async def analyze_visual(request: VisualAnalysisRequest) -> VisualAnalysisResponse:
    """Analyze a visual using AI and store it in memory"""

    start_time = time.time()
    
    # Get the OpenAI API key
    api_key = db.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    client = openai.OpenAI(api_key=api_key)
    
    # Process the screenshot if provided
    screenshot_description = ""
    screenshot_dimensions = None
    if request.visual.screenshotBase64:
        try:
            # Extract image dimensions if possible
            try:
                # Remove the data URL prefix if present
                base64_data = request.visual.screenshotBase64
                if "," in base64_data:
                    base64_data = base64_data.split(",")[1]
                
                # Decode and get dimensions
                image_data = base64.b64decode(base64_data)
                image = Image.open(BytesIO(image_data))
                screenshot_dimensions = {"width": image.width, "height": image.height}
            except Exception as dim_error:
                print(f"Error extracting image dimensions: {dim_error}")
            
            # Save the screenshot and analyze it with vision model
            screenshot_description = await analyze_screenshot(client, request.visual.screenshotBase64, request.analysisType)
        except Exception as e:
            print(f"Error analyzing screenshot: {e}")
    
    # Prepare the context for analysis
    elements_text = ""
    element_count = 0
    if request.visual.elements:
        elements = [element.dict() for element in request.visual.elements]
        element_count = len(elements)
        elements_text = json.dumps(elements, indent=2)

    # Perform the analysis based on the type
    analysis_prompt = get_analysis_prompt(request.analysisType, elements_text, screenshot_description, request.visual.additionalContext)
    
    try:
        # Call OpenAI for analysis
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a visual analysis expert that specializes in UI/UX, accessibility, and semantic analysis of web interfaces."},
                {"role": "user", "content": analysis_prompt}
            ]
        )
        
        analysis_text = response.choices[0].message.content
        
        # Try to parse the analysis as JSON, fall back to text if not possible
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            analysis = {"textAnalysis": analysis_text}
        
        # Enhance elements with analysis insights if available
        enhanced_elements = request.visual.elements or []
        if "elements" in analysis and isinstance(analysis["elements"], list):
            # Try to match analysis elements with original elements
            updated_elements = []
            for element in enhanced_elements:
                element_dict = element.dict()
                # Try to find matching element in analysis
                for analysis_elem in analysis["elements"]:
                    if analysis_elem.get("type") == element.type and analysis_elem.get("text") == element.text:
                        # Update with analysis data
                        if "priority" in analysis_elem:
                            element_dict["priority"] = analysis_elem["priority"]
                        if "accessibility_issues" in analysis_elem:
                            element_dict["accessibility_issues"] = analysis_elem["accessibility_issues"]
                        if "interactions" in analysis_elem:
                            element_dict["interactions"] = analysis_elem["interactions"]
                        break
                updated_elements.append(VisualElement(**element_dict))
            enhanced_elements = updated_elements
        
        # Extract key insights if available
        key_insights = analysis.get("key_insights", [])
        if not key_insights and analysis.get("suggestions"):
            key_insights = analysis.get("suggestions")
        
        # Store in memory if requested
        memory_id = None
        if request.storeInMemory:
            try:
                # Prepare MemoryFrame payload
                # Note: We'll store the screenshot base64 directly in the MemoryFrame if provided,
                # rather than saving to db.storage.binary and linking by ID for simplicity with Firestore.
                # The frontend `memory-service.ts` uploads to Firebase Storage and stores a download URL.
                # For backend-initiated visual memories like this, we can store the base64 or a description.


                frame_payload = MemoryFrame(
                    timestamp=datetime.utcnow().isoformat() + "Z", 
                    pageUrl=request.visual.pageUrl,
                    # screenshotUrl will be None for now, as this backend path doesn't upload to Firebase Storage
                    detectedElements=[elem.dict() for elem in enhanced_elements],
                    taskContext=request.visual.taskContext,
                    userAction=request.visual.userAction or "visual_analysis_api_call",
                    outcome="success",
                    summary=f"Visual Analysis: {request.visual.pageUrl or 'Unnamed Page'} at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", # Brief summary
                    metadata={
                        "analysis_type": request.analysisType,
                        "environment_context": request.visual.environmentContext,
                        "original_user_id": request.userId,
                        "tags": request.memoryTags,
                        "screenshot_description": screenshot_description, # Storing as part of metadata
                        "analysis_raw_json": json.dumps(analysis) # Storing full analysis JSON in metadata
                    }
                )
                
                memory_response = await memory_service.create_memory(frame_payload)
                memory_id = memory_response.id
            except Exception as e:
                print(f"Error saving memory frame: {e}")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        return VisualAnalysisResponse(
            analysis=analysis,
            enhancedElements=enhanced_elements,
            memoryId=memory_id,
            executionTime=execution_time,
            elementCount=element_count,
            screenshotDimensions=screenshot_dimensions,
            keyInsights=key_insights,
            metrics={
                "execution_time": execution_time,
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        )
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        raise HTTPException(status_code=500, detail=f"Error in analysis: {str(e)}")

async def analyze_screenshot(client: openai.OpenAI, screenshot_base64: str, analysis_type: str = "comprehensive") -> str:
    """Analyze a screenshot using OpenAI Vision API"""
    try:
        # Remove the data URL prefix if present
        if "," in screenshot_base64:
            screenshot_base64 = screenshot_base64.split(",")[1]

        # Prepare prompt based on analysis type
        prompt = get_vision_prompt(analysis_type)
        
        # Call OpenAI vision model to analyze the screenshot
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_base64}"
                            }
                        }
                    ]
                }
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in vision analysis: {e}")
        return "Error analyzing screenshot"

def get_vision_prompt(analysis_type: str) -> str:
    """Generate an appropriate vision prompt based on the analysis type"""
    
    if analysis_type == "accessibility":
        return "Analyze this UI for accessibility issues. Focus on WCAG compliance, color contrast, keyboard navigation, screen reader compatibility, and overall accessibility for users with disabilities. Identify specific elements that have issues and suggest improvements."
    
    elif analysis_type == "semantic":
        return "Perform a semantic analysis of this UI. Identify the purpose and meaning of each element, information hierarchy, content structure, and overall information architecture. Focus on how well the UI communicates its purpose and functionality."
    
    elif analysis_type == "layout":
        return "Analyze this UI layout. Evaluate spacing, alignment, responsive design elements, visual balance, and overall composition. Identify any layout issues, inconsistencies, or areas that could be improved for better visual harmony."
    
    elif analysis_type == "development":
        return "Analyze this UI from a frontend developer's perspective. Identify UI component structure, likely HTML/CSS patterns, potential React component hierarchy, and implementation considerations. Suggest optimization approaches and note any technical challenges in implementing this UI."
    
    elif analysis_type == "memory":
        return "Describe this UI in detail for future reference. Create a comprehensive catalog of all visible UI elements, their states, positions, and relationships. Focus on details that would help reconstruct understanding of this interface later."
    
    elif analysis_type == "comprehensive":
        return "Perform a comprehensive analysis of this UI. Include: 1) General overview and purpose, 2) Layout structure and visual design quality, 3) Information hierarchy and content organization, 4) Usability and interaction design, 5) Accessibility considerations, 6) Technical implementation aspects, 7) Key strengths and weaknesses. Be thorough but prioritize insights that would be most valuable for improving this interface."
    
    else:  # basic analysis
        return "Describe this UI in detail. Identify key components, layout structure, and any potential usability or visual design issues."

def get_analysis_prompt(analysis_type: str, elements_text: str, screenshot_description: str, additional_context: Optional[str] = None) -> str:
    """Generate an appropriate prompt based on the analysis type"""
    
    base_prompt = f"""Analyze the following UI elements and screenshot description:

ELEMENTS:
{elements_text}

SCREENSHOT DESCRIPTION:
{screenshot_description}
"""
    
    if additional_context:
        base_prompt += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"
    
    # Add the response format instructions based on analysis type
    if analysis_type == "accessibility":
        return base_prompt + "\n\nPerform an accessibility analysis. Identify potential WCAG issues, color contrast problems, missing alt text, keyboard navigation issues, and suggest improvements. Return your analysis as a JSON object with these keys: issues (array), recommendations (array), complianceScore (number 0-100), keyInsights (array), elements (array with individual element assessments)."
    
    elif analysis_type == "semantic":
        return base_prompt + "\n\nPerform a semantic analysis. Identify the purpose of each UI element, their relationships, information hierarchy, and content structure. Return your analysis as a JSON object with these keys: purpose (string), hierarchy (object), keyElements (array), suggestions (array), keyInsights (array)."
    
    elif analysis_type == "layout":
        return base_prompt + "\n\nPerform a layout analysis. Evaluate spacing, alignment, responsive behavior, and visual balance. Identify any layout issues. Return your analysis as a JSON object with these keys: layoutAssessment (string), alignmentIssues (array), spacingIssues (array), responsiveIssues (array), visualBalance (string), keyInsights (array)."
    
    elif analysis_type == "development":
        return base_prompt + "\n\nAnalyze this UI from a frontend developer's perspective. Return your analysis as a JSON object with these keys: componentStructure (object), cssPatterns (array), reactComponentHierarchy (object), implementationNotes (array), technicalChallenges (array), optimizationTips (array), keyInsights (array)."
    
    elif analysis_type == "memory":
        return base_prompt + "\n\nCreate a comprehensive catalog of this UI for future reference. Return your analysis as a JSON object with these keys: catalogedElements (array with detailed element descriptions), pageStructure (object), interactionPoints (array), stateDescriptions (object), keyInsights (array)."
    
    elif analysis_type == "comprehensive":
        return base_prompt + "\n\nPerform a comprehensive analysis of this UI. Return your analysis as a JSON object with these keys: overview (string), layout (object), information_hierarchy (object), usability (object with findings), accessibility (object with issues), technical (object with implementation notes), strengths (array), weaknesses (array), key_insights (array of most important takeaways), elements (array with individual element assessments prioritized 1-10)."
    
    else:  # basic analysis
        return base_prompt + "\n\nPerform a basic UI analysis. Provide a general assessment of the interface, identifying strengths and potential improvements for usability and design. Return your analysis as a JSON object with these keys: overview (string), strengths (array), weaknesses (array), suggestions (array), keyInsights (array)."
