from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import random
import uuid
import json
from datetime import datetime, timedelta
import databutton as db
import openai
from app.auth import AuthorizedUser

router = APIRouter(prefix="/ai-service")

# Initialize OpenAI client
try:
    client = openai.OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"OpenAI API key error: {str(e)}")
    client = None

class InvestmentRecommendationRequest(BaseModel):
    profile_id: str
    query: str
    context: Optional[str] = None

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

class ActionItem(BaseModel):
    action: str
    description: str
    priority: str = Field(..., description="Priority level: high, medium, or low")

class Resource(BaseModel):
    title: str
    url: Optional[str] = None
    description: Optional[str] = None

class AIServiceResponse(BaseModel):
    type: str
    response: str
    suggestions: Optional[List[str]] = None
    resources: Optional[List[Resource]] = None
    actionItems: Optional[List[ActionItem]] = None

class ContentRequest(BaseModel):
    profile_id: str
    query: str
    context: Optional[str] = None

class CustomStrategyRequest(BaseModel):
    profileId: str
    strategy: Dict[str, Any]

@router.post("/generate-investment-recommendations")
async def generate_investment_recommendations(request: InvestmentRecommendationRequest) -> AIServiceResponse:
    """Generate AI-powered investment recommendations based on profile data and query.
    
    Provides personalized investment advice and recommendations by analyzing the user's query
    and their family profile context. The system detects key investment themes in the query and
    generates targeted advice on topics like Bitcoin investments, equity strategies, real estate,
    fixed income, and timeframe-specific planning.
    
    Particularly useful for Legacy Vault users seeking contextual investment guidance related to
    specific asset classes or investment timeframes for their family trust planning.
    
    Args:
        request (InvestmentRecommendationRequest): Contains profile ID, query text, and optional context
        
    Returns:
        AIServiceResponse: Structured response containing:
            - Main recommendation text
            - Follow-up question suggestions
            - Relevant resources with descriptions
            - Actionable next steps with priority levels
    """
    # In a production environment, this would use a real AI model
    # with access to the profile data to generate personalized recommendations
    
    # Extract context if provided
    context_data = {}
    if request.context:
        try:
            context_data = json.loads(request.context)
        except Exception as e:
            print(f"Error parsing context: {e}")
    
    # Get previous messages for context if available
    previous_messages = context_data.get("previousMessages", [])
    
    # Sample investment-related keywords to detect in the query
    bitcoin_keywords = ["bitcoin", "btc", "cryptocurrency", "crypto"]
    stocks_keywords = ["stocks", "equities", "market", "shares"]
    estate_keywords = ["estate", "property", "real estate", "land"]
    bonds_keywords = ["bonds", "fixed income", "treasury"]
    timeframe_keywords = ["long-term", "short-term", "generations", "years", "decades", "century"]
    
    query_lower = request.query.lower()
    
    # Generate response based on detected keywords
    if any(keyword in query_lower for keyword in bitcoin_keywords):
        response = "Based on your family profile and legacy goals, I recommend allocating 5-10% of your portfolio to Bitcoin and other digital assets as a long-term store of value. Consider dollar-cost averaging with regular purchases on your child's birthday to build a significant position over time. This approach balances the speculative nature of cryptocurrency with the potential for substantial long-term growth."
        
        suggestions = [
            "What's the optimal Bitcoin allocation for generational wealth?",
            "How should I secure Bitcoin investments for family inheritance?",
            "What are the tax implications of Bitcoin investments?"
        ]
        
        resources = [
            Resource(
                title="Bitcoin Security Best Practices",
                description="Comprehensive guide to securing Bitcoin for long-term family wealth"
            ),
            Resource(
                title="Generational Bitcoin Investing Strategy",
                description="Framework for Bitcoin investments spanning multiple generations"
            )
        ]
        
        action_items = [
            ActionItem(
                action="Set up cold storage wallet",
                description="Purchase a hardware wallet for secure long-term Bitcoin storage",
                priority="high"
            ),
            ActionItem(
                action="Create Bitcoin inheritance documentation",
                description="Document private key recovery procedures for heirs",
                priority="medium"
            )
        ]
        
    elif any(keyword in query_lower for keyword in stocks_keywords):
        response = "For your family's generational wealth strategy, I recommend a core equity portfolio focused on dividend aristocrats and companies with strong moats. Allocate approximately 40-50% to these stable companies, 20-30% to growth stocks in emerging industries, and 10-15% to international equities. This balanced approach provides stable income while capturing innovation-driven growth over multiple decades."
        
        suggestions = [
            "What dividend strategies work best for generational wealth?",
            "How should I balance growth vs. value in a family portfolio?",
            "What sectors should I focus on for the next decade?"
        ]
        
        resources = [
            Resource(
                title="Dividend Aristocrats Analysis",
                description="Performance review of companies with 25+ years of dividend increases"
            ),
            Resource(
                title="Moat-Focused Investment Strategy",
                description="Long-term investment approach focused on companies with sustainable competitive advantages"
            )
        ]
        
        action_items = [
            ActionItem(
                action="Optimize tax structure",
                description="Set up appropriate account structures to minimize long-term tax implications",
                priority="medium"
            ),
            ActionItem(
                action="Schedule portfolio review",
                description="Conduct a comprehensive review of current equity holdings and allocation",
                priority="high"
            )
        ]
        
    elif any(keyword in query_lower for keyword in estate_keywords):
        response = "Real estate remains a foundational component of generational wealth. For your family's legacy strategy, I recommend diversifying across residential, commercial, and land holdings. Consider investing 20-30% in residential income properties, 15-20% in commercial real estate investment trusts (REITs), and 5-10% in undeveloped land with long-term appreciation potential. Real estate provides both income and inflation protection across generations."
        
        suggestions = [
            "What real estate markets show the best long-term potential?",
            "How should I structure real estate holdings for tax efficiency?",
            "What are the best vehicles for investing in commercial real estate?"
        ]
        
        resources = [
            Resource(
                title="Intergenerational Real Estate Transfer Strategies",
                description="Tax-efficient approaches to transferring property across generations"
            ),
            Resource(
                title="Commercial vs. Residential Real Estate Analysis",
                description="Comparative analysis for legacy-focused portfolios"
            )
        ]
        
        action_items = [
            ActionItem(
                action="Establish real estate LLC",
                description="Create a limited liability company for holding family real estate assets",
                priority="high"
            ),
            ActionItem(
                action="Develop property maintenance fund",
                description="Establish a dedicated fund for long-term maintenance of real estate holdings",
                priority="medium"
            )
        ]
        
    elif any(keyword in query_lower for keyword in bonds_keywords):
        response = "For the wealth preservation component of your family legacy strategy, I recommend a laddered bond approach. Allocate 15-25% of your portfolio to a mix of Treasury bonds, municipal bonds (for tax advantages), and high-quality corporate bonds. Structure these with staggered maturities from 2-30 years to provide liquidity while capturing higher yields on longer-term instruments. This provides portfolio stability and predictable income streams."
        
        suggestions = [
            "What bond duration is optimal in the current rate environment?",
            "How can I use municipal bonds for tax-efficient income?",
            "Should I consider international bonds in my portfolio?"
        ]
        
        resources = [
            Resource(
                title="Bond Ladder Strategy Guide",
                description="Step-by-step approach to creating effective bond ladders for family portfolios"
            ),
            Resource(
                title="Tax-Equivalent Yield Calculator",
                description="Tool for comparing taxable and tax-exempt bond returns"
            )
        ]
        
        action_items = [
            ActionItem(
                action="Assess current bond holdings",
                description="Review existing fixed income investments for yield and duration",
                priority="medium"
            ),
            ActionItem(
                action="Establish bond ladder",
                description="Structure new bond purchases with staggered maturities from 2-30 years",
                priority="high"
            )
        ]
        
    elif any(keyword in query_lower for keyword in timeframe_keywords):
        response = "Your focus on multi-generational wealth requires a time-layered approach to investing. I recommend structuring your portfolio in distinct timeframe tranches: 10% in highly liquid assets for near-term needs, 25% in growth assets for 10-20 year horizons, 40% in core wealth builders for 20-50 year horizons, and 25% in legacy assets with century-long perspectives. This approach aligns investment vehicles with their intended time of utilization."
        
        suggestions = [
            "What investments work best for century-long horizons?",
            "How should I balance different timeframes in my portfolio?",
            "What rebalancing strategy works for multi-generational investing?"
        ]
        
        resources = [
            Resource(
                title="Time-Horizon Investment Framework",
                description="Comprehensive approach to aligning investments with different time horizons"
            ),
            Resource(
                title="Century-Scale Investment Vehicles",
                description="Analysis of investment vehicles designed for extremely long-term horizons"
            )
        ]
        
        action_items = [
            ActionItem(
                action="Create time-horizon investment map",
                description="Document which assets are aligned with specific future time periods and goals",
                priority="high"
            ),
            ActionItem(
                action="Establish century fund",
                description="Create a dedicated investment vehicle for assets with 100+ year horizons",
                priority="medium"
            )
        ]
        
    else:
        # Generic financial advice if no specific keywords detected
        response = "Based on your family profile, I recommend a balanced approach to generational wealth building. Consider allocating assets across multiple categories including 30-40% in equities for growth, 20-25% in real estate for inflation protection, 15-20% in bonds for stability, 10-15% in alternative investments including Bitcoin for potential asymmetric returns, and 5-10% in cash equivalents for opportunities and liquidity. This diversified approach balances wealth preservation with growth potential across generations."
        
        suggestions = [
            "What allocation is best for my family's specific situation?",
            "How should I adapt my investment strategy as my children age?",
            "What are the best wealth preservation strategies?"
        ]
        
        resources = [
            Resource(
                title="Modern Portfolio Theory for Family Wealth",
                description="Adaptation of MPT principles for multi-generational investing"
            ),
            Resource(
                title="Family Investment Policy Statement Template",
                description="Framework for documenting your family's investment philosophy and rules"
            )
        ]
        
        action_items = [
            ActionItem(
                action="Create Investment Policy Statement",
                description="Document your family's investment philosophy, goals, and guardrails",
                priority="high"
            ),
            ActionItem(
                action="Schedule quarterly portfolio review",
                description="Set up regular reviews to ensure alignment with long-term goals",
                priority="medium"
            )
        ]
    
    return AIServiceResponse(
        type="financial",
        response=response,
        suggestions=suggestions,
        resources=resources,
        actionItems=action_items
    )

@router.post("/generate-content")
async def generate_ai_content(request: ContentRequest) -> AIServiceResponse:
    """
    Generate AI-powered content based on profile data and specifications
    """
    # In a production environment, this would use a real AI model
    # with access to the profile data to generate personalized content
    
    query_lower = request.query.lower()
    
    # Content types that might be detected in the query
    newsletter_keywords = ["newsletter", "update", "family news"]
    education_keywords = ["education", "tutorial", "learn", "guide"]
    report_keywords = ["report", "analysis", "portfolio", "performance"]
    legacy_keywords = ["legacy", "statement", "values", "mission"]
    
    if any(keyword in query_lower for keyword in newsletter_keywords):
        response = "# McMillan Family Quarterly Update\n\n## Investment Highlights\n\nThis quarter has shown remarkable growth in our long-term holdings, with our Bitcoin allocation appreciating 15% and dividend income increasing by 7% year-over-year. Our real estate properties have maintained stable occupancy rates of 97%.\n\n## Family Milestones\n\nWe're excited to celebrate Sophia's 10th birthday this month! Her Bitcoin trust has now been active for a decade and has grown substantially. We've also completed the renovation of the family cabin, which will host our summer reunion.\n\n## Legacy Planning Update\n\nThe family council has finalized the updated investment policy statement, emphasizing our commitment to ethical investing and long-term wealth preservation. We've also established a new educational trust for future generations.\n\n## Looking Ahead\n\nIn the coming quarter, we'll be reviewing our estate plan and tax strategy. We're also exploring new investment opportunities in emerging technologies that align with our multi-generational perspective."
        
        suggestions = [
            "Generate a monthly investment update",
            "Create a family milestone announcement",
            "Draft a legacy planning update"
        ]
        
    elif any(keyword in query_lower for keyword in education_keywords):
        response = "# Understanding Bitcoin as a Family Legacy Asset\n\n## What is Bitcoin?\n\nBitcoin is a decentralized digital currency that operates without a central authority. It's often described as 'digital gold' because of its scarcity (only 21 million will ever exist) and its potential as a store of value across generations.\n\n## Why Bitcoin for Legacy Planning?\n\n1. **Scarcity**: The limited supply creates potential for long-term appreciation\n2. **Seizure resistance**: Assets can be secured in a way that's resistant to confiscation\n3. **Borderless**: Can be accessed anywhere in the world regardless of geopolitical changes\n4. **Divisible**: Can be transferred in exact amounts across generations\n5. **Non-sovereign**: Not tied to any particular government or currency system\n\n## Risks to Consider\n\n- **Volatility**: Prices can fluctuate dramatically in the short term\n- **Regulatory uncertainty**: Government policies toward digital assets continue to evolve\n- **Security challenges**: Proper storage is essential to prevent loss\n\n## Family Strategy Recommendations\n\n- Allocate a modest percentage (5-10%) of family assets to Bitcoin\n- Use dollar-cost averaging to build positions over time\n- Focus on secure, long-term storage solutions\n- Document access methods for future generations\n- Review and adjust allocation based on family goals and market conditions"
        
        suggestions = [
            "Create a guide to estate planning",
            "Generate a tutorial on investment diversification",
            "Create an educational resource about taxes and wealth"
        ]
        
    elif any(keyword in query_lower for keyword in report_keywords):
        response = "# McMillan Family Trust: Investment Performance Analysis\n\n## Portfolio Overview\n\nAs of this quarter, the family portfolio is allocated across the following asset classes:\n\n- Equities: 42% (US: 30%, International: 12%)\n- Real Estate: 23% (Residential: 15%, Commercial: 8%)\n- Fixed Income: 18% (Government: 10%, Corporate: 8%)\n- Alternative Investments: 12% (Bitcoin: 7%, Private Equity: 5%)\n- Cash & Equivalents: 5%\n\n## Performance Highlights\n\n- **Overall Performance**: +8.2% trailing 12 months (benchmark: +6.5%)\n- **Top Performing Category**: Alternative Investments (+15.7%)\n- **Most Improved**: International Equities (from +2.1% to +7.3% YoY)\n- **Underperforming**: Commercial Real Estate (+2.1% vs benchmark +4.5%)\n\n## Generational Metrics\n\n- **Short-term liquidity**: 175% of target (exceeding 1-year emergency requirements)\n- **Education funding**: 92% of projected needs (on track for milestone dates)\n- **Retirement adequacy**: 115% of required rate (exceeding long-term projections)\n- **Legacy growth rate**: 7.3% annualized (10-year average)\n\n## Recommendations\n\n1. Rebalance equity allocation to increase exposure to emerging markets\n2. Evaluate commercial real estate holdings for potential repositioning\n3. Increase Bitcoin allocation by 1% on the next significant market correction\n4. Review insurance coverage to ensure alignment with current asset values"
        
        suggestions = [
            "Generate a quarterly investment report",
            "Create a Bitcoin performance analysis",
            "Draft a real estate holdings summary"
        ]
        
    elif any(keyword in query_lower for keyword in legacy_keywords):
        response = "# McMillan Family Legacy Statement\n\n## Our Family Purpose\n\nThe McMillan Family Trust exists to nurture the growth, education, and well-being of current and future generations while making a positive impact on our communities and the world. We believe in the power of long-term thinking, continuous learning, and principled action.\n\n## Core Values\n\n1. **Stewardship**: We are temporary custodians of our resources, responsible for growing and protecting them for future generations\n\n2. **Education**: We value lifelong learning and believe in investing in the intellectual development of each family member\n\n3. **Independence**: We strive to provide opportunities for each family member to develop self-reliance while maintaining strong family connections\n\n4. **Innovation**: We embrace thoughtful risk-taking and new ideas that can create extraordinary outcomes over time\n\n5. **Integrity**: We conduct ourselves with honesty, transparency, and ethical behavior in all endeavors\n\n## Multi-Generational Vision\n\nOur hundred-year vision is to build a family legacy that:\n\n- Provides educational opportunities for every descendant\n- Maintains financial independence across market cycles and geopolitical changes\n- Preserves and transmits our core values and family history\n- Creates positive impact through strategic philanthropy\n- Adapts and innovates while maintaining principled foundations\n\n## Governance Principles\n\nThe family's resources will be governed by:\n\n- A clear investment policy statement reviewed annually\n- Inclusive family meetings with age-appropriate participation\n- Transparent communication about assets, opportunities, and responsibilities\n- Educational programs for financial literacy at all ages\n- Professional management balanced with family oversight"
        
        suggestions = [
            "Generate a family mission statement",
            "Create a values declaration for the trust",
            "Draft a letter to future generations"
        ]
        
    else:
        # Generic content if no specific keywords detected
        response = "# McMillan Family Wealth Strategy\n\nThe McMillan Family Wealth Strategy is designed to build, preserve, and transfer wealth across multiple generations. This document outlines our approach to investment management, governance, education, and legacy planning.\n\n## Investment Philosophy\n\nWe take a long-term, diversified approach that balances wealth preservation with growth potential. Our strategy incorporates time-layered investing with distinct allocations for different time horizons ranging from immediate needs to century-long growth.\n\n## Governance Structure\n\nOur family employs a collaborative governance model with a family council that meets quarterly to review investments, discuss major decisions, and ensure alignment with our values and long-term vision.\n\n## Education Commitment\n\nWe are dedicated to the financial education of all family members. Age-appropriate learning begins in childhood and continues throughout life, ensuring each generation has the knowledge to be effective stewards.\n\n## Legacy Planning\n\nBeyond financial assets, we are committed to transmitting our family values, history, and purpose. We maintain a family archive, create regular family communications, and organize events that strengthen family bonds.\n\n## Technological Innovation\n\nWe embrace technological innovation in our investment approach, including allocations to emerging digital assets like Bitcoin that offer potential for asymmetric returns over multi-decade time horizons."
        
        suggestions = [
            "Generate a wealth management overview",
            "Create a family communication template",
            "Draft a strategic investment outline"
        ]
    
    return AIServiceResponse(
        type="content",
        response=response,
        suggestions=suggestions,
    )

@router.get("/default-strategies")
async def get_default_strategies() -> List[Dict[str, Any]]:
    """
    Get default investment strategies for different risk profiles and time horizons
    """
    return [
        {
            "id": "conservative-generational",
            "name": "Conservative Generational",
            "description": "A low-risk strategy focused on wealth preservation across generations",
            "riskLevel": "low",
            "timeHorizon": "generational",
            "allocation": {
                "equities": 25,
                "bonds": 40,
                "realEstate": 20,
                "commodities": 5,
                "digitalAssets": 5,
                "cash": 5
            },
            "expectedReturn": 5.2,
            "principles": [
                "Capital preservation",
                "Income generation",
                "Inflation protection",
                "Tax efficiency"
            ]
        },
        {
            "id": "balanced-generational",
            "name": "Balanced Generational",
            "description": "A moderate-risk strategy balancing growth and preservation across generations",
            "riskLevel": "medium",
            "timeHorizon": "generational",
            "allocation": {
                "equities": 40,
                "bonds": 25,
                "realEstate": 15,
                "commodities": 5,
                "digitalAssets": 10,
                "cash": 5
            },
            "expectedReturn": 7.5,
            "principles": [
                "Balanced growth",
                "Diversification",
                "Moderate volatility",
                "Tax-aware investing"
            ]
        },
        {
            "id": "growth-generational",
            "name": "Growth Generational",
            "description": "A higher-risk strategy focused on long-term growth across generations",
            "riskLevel": "high",
            "timeHorizon": "generational",
            "allocation": {
                "equities": 55,
                "bonds": 10,
                "realEstate": 15,
                "commodities": 5,
                "digitalAssets": 12,
                "cash": 3
            },
            "expectedReturn": 9.8,
            "principles": [
                "Long-term capital appreciation",
                "Innovation exposure",
                "Strategic rebalancing",
                "Alternative asset inclusion"
            ]
        },
        {
            "id": "aggressive-generational",
            "name": "Aggressive Generational",
            "description": "A very high-risk strategy maximizing long-term growth potential across generations",
            "riskLevel": "very-high",
            "timeHorizon": "generational",
            "allocation": {
                "equities": 60,
                "bonds": 5,
                "realEstate": 10,
                "commodities": 5,
                "digitalAssets": 18,
                "cash": 2
            },
            "expectedReturn": 12.3,
            "principles": [
                "Maximum growth potential",
                "Emerging technology focus",
                "High conviction positions",
                "Opportunistic rebalancing"
            ]
        }
    ]

@router.post("/save-custom-strategy")
async def save_custom_strategy(request: CustomStrategyRequest) -> Dict[str, Any]:
    """
    Save a custom investment strategy for a family profile
    """
    # In a production environment, this would save to a database
    # Here we'll just return the strategy with an ID
    
    strategy = request.strategy
    strategy["id"] = f"custom-{uuid.uuid4().hex[:8]}"  # Generate a unique ID
    strategy["createdAt"] = datetime.now().isoformat()
    
    return strategy

@router.get("/custom-strategies")
async def list_custom_strategies(profileId: str) -> List[Dict[str, Any]]:
    """
    List all custom investment strategies for a family profile
    """
    # In a production environment, this would query a database
    # Here we'll return mock data
    
    # Generate 1-3 random strategies
    num_strategies = random.randint(1, 3)
    strategies = []
    
    for i in range(num_strategies):
        creation_date = datetime.now() - timedelta(days=random.randint(10, 100))
        
        strategy = {
            "id": f"custom-{uuid.uuid4().hex[:8]}",
            "name": f"Custom Strategy {i+1}",
            "description": "Personalized investment strategy for long-term family wealth",
            "riskLevel": random.choice(["low", "medium", "high", "very-high"]),
            "timeHorizon": "generational",
            "allocation": {
                "equities": random.randint(20, 60),
                "bonds": random.randint(5, 40),
                "realEstate": random.randint(10, 25),
                "commodities": random.randint(0, 10),
                "digitalAssets": random.randint(5, 20),
                "cash": random.randint(2, 10)
            },
            "expectedReturn": round(random.uniform(5.0, 12.0), 1),
            "createdAt": creation_date.isoformat(),
            "principles": [
                "Personalized allocation",
                "Family-specific requirements",
                "Tax optimization",
                "Legacy-focused"
            ]
        }
        
        strategies.append(strategy)
    
    return strategies

@router.get("/custom-strategy/{strategy_id}")
async def get_custom_strategy(strategy_id: str) -> Dict[str, Any]:
    """
    Get a specific custom investment strategy by ID
    """
    # In a production environment, this would query a database
    # Here we'll return mock data
    
    creation_date = datetime.now() - timedelta(days=random.randint(10, 100))
    
    return {
        "id": strategy_id,
        "name": "Premium Growth Strategy",
        "description": "A personalized strategy focusing on growth while maintaining generational wealth transfer capability",
        "riskLevel": "high",
        "timeHorizon": "generational",
        "allocation": {
            "equities": 52,
            "bonds": 13,
            "realEstate": 15,
            "commodities": 5,
            "digitalAssets": 12,
            "cash": 3
        },
        "expectedReturn": 9.4,
        "createdAt": creation_date.isoformat(),
        "lastModified": datetime.now().isoformat(),
        "principles": [
            "Focused growth",
            "Tax-efficient transfers",
            "Inflation protection",
            "Innovation exposure"
        ],
        "notes": "This strategy was created with a focus on technological innovation while maintaining sufficient conservative allocation for legacy preservation."
    }

@router.delete("/custom-strategy/{strategy_id}")
async def delete_custom_strategy(strategy_id: str) -> Dict[str, str]:
    """
    Delete a custom investment strategy
    """
    # In a production environment, this would delete from a database
    # Here we'll just return a success message
    
    return {"status": "success", "message": f"Strategy {strategy_id} deleted successfully"}

@router.post("/generate-recommendations")
async def generate_advanced_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Generate detailed investment recommendations based on risk profile and time horizon
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
