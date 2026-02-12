from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import databutton as db
import openai
import json
import random

# Create API router
router = APIRouter()

# Initialize OpenAI client
try:
    client = openai.OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
except KeyError:
    print("OpenAI API key not found, using mock responses only")
    client = None

class RecommendationRequest(BaseModel):
    profile_id: Optional[str] = None
    time_horizon_years: int = 10
    risk_profile: str = "balanced"  # conservative, balanced, aggressive
    focus_areas: Optional[List[str]] = None
    current_portfolio_value: Optional[float] = None

class InvestmentRecommendation(BaseModel):
    category: str
    allocation_percentage: float
    description: str
    reasoning: str
    time_horizon: str
    risk_level: str

class RecommendationResponse(BaseModel):
    recommendations: List[InvestmentRecommendation]
    strategy_summary: str
    long_term_outlook: str
    conservative_allocation: Dict[str, float]
    aggressive_allocation: Dict[str, float]

@router.post("/generate-recommendations")
async def generate_investment_recommendations_rec(request: RecommendationRequest) -> RecommendationResponse:
    """Generate detailed investment recommendations based on risk profile and time horizon.
    
    Creates a comprehensive investment strategy tailored to the user's risk tolerance, time horizon,
    and specific investment interests. This endpoint provides sophisticated, generational wealth-building
    recommendations with both conservative and aggressive allocation options.
    
    The recommendations include specific asset categories, allocation percentages, rationales, and
    time horizons, making this ideal for long-term family trust planning and wealth transfer strategies.
    
    Args:
        request (RecommendationRequest): Contains risk profile, time horizon, focus areas, and portfolio value
    
    Returns:
        RecommendationResponse: Comprehensive investment strategy with:
            - Specific asset allocation recommendations with rationales
            - Strategy summary and long-term outlook
            - Both conservative and aggressive allocation models
    """
    # Determine the right prompt based on risk profile
    risk_descriptions = {
        "conservative": "preservation of capital with modest growth",
        "balanced": "moderate growth with reasonable risk management",
        "aggressive": "maximum long-term growth accepting higher volatility"
    }
    
    risk_description = risk_descriptions.get(request.risk_profile, risk_descriptions["balanced"])
    
    # Generate focus areas if not provided
    focus_areas = request.focus_areas or ["technology", "sustainable energy", "healthcare", "blockchain"]
    focus_areas_str = ", ".join(focus_areas)
    
    # Build the prompt for OpenAI
    prompt = f"""
    Act as a sophisticated financial advisor specializing in multi-generational wealth building with a focus on emerging industries.
    
    Generate investment recommendations for a family trust with the following parameters:
    - Time Horizon: {request.time_horizon_years} years
    - Risk Profile: {request.risk_profile} ({risk_description})
    - Areas of Interest: {focus_areas_str}
    
    Provide the following information structured as JSON:
    1. A list of 5 specific investment category recommendations with:
       - category (asset class or industry)
       - allocation_percentage (what percentage of portfolio)
       - description (brief description of what this category includes)
       - reasoning (why this is a good long-term investment)
       - time_horizon (when this investment is expected to mature/pay off)
       - risk_level (low, medium, high)
       
    2. A strategy_summary (2-3 sentences summarizing the overall approach)
    3. A long_term_outlook (2-3 sentences on how this strategy builds generational wealth)
    4. conservative_allocation (a dictionary mapping asset classes to percentages, must sum to 100%)
    5. aggressive_allocation (a dictionary mapping asset classes to percentages, must sum to 100%)
    
    Structure your response as properly formatted JSON matching the schema of RecommendationResponse in the code.
    Focus on options suitable for long-term generational wealth building, not short-term gains.
    """
    
    # Call OpenAI API
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a sophisticated financial advisor specializing in intergenerational wealth planning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            response_content = response.choices[0].message.content
            recommendations_data = json.loads(response_content)
            
            # Return structured recommendations
            return RecommendationResponse(**recommendations_data)
        except Exception as e:
            # Log error and fall back to default recommendations
            print(f"Error generating AI recommendations: {str(e)}")
    
    # Fallback to default recommendations if API fails or client is None
    print("Using fallback investment recommendations")
    
    # Return a pre-defined fallback response
    fallback_response = {
        "recommendations": [
            {
                "category": "Bitcoin",
                "allocation_percentage": 20.0,
                "description": "Digital gold and inflation hedge",
                "reasoning": "Limited supply and growing institutional adoption make Bitcoin a cornerstone for long-term wealth preservation.",
                "time_horizon": "10+ years",
                "risk_level": "medium"
            },
            {
                "category": "Index Funds",
                "allocation_percentage": 30.0,
                "description": "Broad market exposure through low-cost funds",
                "reasoning": "Historically reliable returns with minimum management requirements.",
                "time_horizon": "5-30 years",
                "risk_level": "low"
            },
            {
                "category": "AI & Automation",
                "allocation_percentage": 15.0,
                "description": "Companies leading in artificial intelligence and automation technologies",
                "reasoning": "Transformative technologies reshaping every industry with exponential growth potential.",
                "time_horizon": "7-15 years",
                "risk_level": "high"
            },
            {
                "category": "Sustainable Energy",
                "allocation_percentage": 15.0,
                "description": "Clean energy producers and infrastructure",
                "reasoning": "Global transition to renewable energy creates multi-decade growth opportunity.",
                "time_horizon": "10-20 years",
                "risk_level": "medium"
            },
            {
                "category": "Real Estate",
                "allocation_percentage": 20.0,
                "description": "Property and REITs in strategic locations",
                "reasoning": "Tangible assets that provide income and appreciation over generations.",
                "time_horizon": "15-30 years",
                "risk_level": "medium"
            }
        ],
        "strategy_summary": "This strategy balances digital and traditional assets for multi-generational growth, with strategic allocation to emerging technologies that will shape the future economy.",
        "long_term_outlook": "Building wealth across generations requires patience and positioning capital in innovations that solve humanity's biggest challenges while maintaining anchor positions in proven stores of value.",
        "conservative_allocation": {
            "Bitcoin": 10.0,
            "Fixed Income": 40.0,
            "Blue Chip Stocks": 25.0,
            "Real Estate": 20.0,
            "Cash": 5.0
        },
        "aggressive_allocation": {
            "Bitcoin": 30.0,
            "Growth Stocks": 35.0,
            "Emerging Tech": 20.0,
            "Real Estate": 10.0,
            "Alternatives": 5.0
        }
    }
    
    return RecommendationResponse(**fallback_response)

@router.get("/default-strategies")
async def get_default_strategies_rec() -> List[Dict[str, Any]]:
    """Return predefined investment strategies with allocations"""
    return {
        "conservative": {
            "name": "Conservative Foundation",
            "description": "Focus on capital preservation with modest growth expectations",
            "allocation": {
                "Bitcoin": 10.0,
                "Fixed Income": 40.0,
                "Blue Chip Stocks": 25.0,
                "Real Estate": 20.0,
                "Cash": 5.0
            },
            "annual_return": 6.0,
            "volatility": "Low",
            "risk_score": 3
        },
        "balanced": {
            "name": "Balanced Growth",
            "description": "Mix of growth and stability for medium-term horizons",
            "allocation": {
                "Bitcoin": 20.0,
                "Index Funds": 30.0,
                "Growth Stocks": 25.0,
                "Real Estate": 15.0,
                "Fixed Income": 10.0
            },
            "annual_return": 9.0,
            "volatility": "Medium",
            "risk_score": 5
        },
        "aggressive": {
            "name": "Future Focused Growth",
            "description": "Maximum growth potential accepting higher volatility",
            "allocation": {
                "Bitcoin": 30.0,
                "Growth Stocks": 35.0,
                "Emerging Tech": 20.0,
                "Real Estate": 10.0,
                "Alternatives": 5.0
            },
            "annual_return": 12.0,
            "volatility": "High",
            "risk_score": 8
        },
        "bitcoin_maximalist": {
            "name": "Bitcoin Maximalist",
            "description": "Heavy focus on Bitcoin as the primary investment vehicle",
            "allocation": {
                "Bitcoin": 80.0,
                "Gold": 10.0,
                "Cash": 5.0, 
                "Bitcoin Mining": 5.0
            },
            "annual_return": 20.0,
            "volatility": "Very High",
            "risk_score": 9
        },
        "legacy_builder": {
            "name": "Legacy Builder",
            "description": "Designed for multi-generational wealth transfer with intellectual assets",
            "allocation": {
                "Bitcoin": 25.0,
                "Productive Land": 20.0,
                "Dividend Aristocrats": 20.0,
                "Education": 15.0,
                "Value Stocks": 15.0,
                "Physical Gold": 5.0
            },
            "annual_return": 8.0,
            "volatility": "Medium-Low",
            "risk_score": 4
        }
    }
