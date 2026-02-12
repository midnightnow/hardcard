from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import openai
import databutton as db
from app.auth import AuthorizedUser

router = APIRouter()

class EmotionAnalysisRequest(BaseModel):
    text: str

class EmotionAnalysisResponse(BaseModel):
    primary_emotion: str
    emotion_scores: Dict[str, float]
    intensity: float
    analysis: str

def get_openai_client():
    """Get OpenAI client with API key"""
    api_key = db.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return openai.OpenAI(api_key=api_key)

@router.post("/emotions/analyze", response_model=EmotionAnalysisResponse)
async def analyze_emotion(request: EmotionAnalysisRequest, user: AuthorizedUser):
    """Analyze text for emotional content using LLM"""
    try:
        client = get_openai_client()
        
        # Use OpenAI to analyze emotional content
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json"},
            messages=[
                {"role": "system", "content": """
                    You are an emotional analysis expert. Analyze the emotional content of the text and return a JSON object with the following structure:
                    {
                        "primary_emotion": "the dominant emotion in the text",
                        "emotion_scores": {"emotion1": score, "emotion2": score, ...},
                        "intensity": a number from 0 to 1 indicating the intensity of emotion,
                        "analysis": "a brief explanation of your analysis"
                    }
                    
                    The emotions to consider are: joy, sadness, anger, fear, disgust, surprise, trust, anticipation, neutral.
                    Each emotion score should be between 0 and 1.
                """}, 
                {"role": "user", "content": request.text}
            ]
        )
        
        # Parse the response
        result = response.choices[0].message.content
        # In a real system we'd need more robust JSON parsing with error handling
        try:
            import json
            result_json = json.loads(result)
            return EmotionAnalysisResponse(**result_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse emotion analysis result")
        
    except Exception as e:
        print(f"Error in analyze_emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
