"""
HardCard API Endpoints - Mathematical Validation Services
RESTful API for the Workplace Best Friend Ecosystem
"""

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import Dict, List, Optional
from decimal import Decimal
import logging
from datetime import datetime, timedelta
import json

from ..core.mathematical_engine import (
    HardCardMathEngine, 
    PerformanceProjector,
    AllocationStrategy, 
    RiskProfile, 
    PortfolioAnalysis
)

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Pydantic models for API validation
class RiskProfileRequest(BaseModel):
    """Risk profile assessment request"""
    age: int
    annual_income: float
    net_worth: float
    investment_experience: str
    time_horizon: int
    risk_tolerance: int
    liquidity_needs: float = 0.05
    emotional_tolerance: int = 5
    
    @validator('age')
    def validate_age(cls, v):
        if not 18 <= v <= 100:
            raise ValueError('Age must be between 18 and 100')
        return v
    
    @validator('risk_tolerance', 'emotional_tolerance')
    def validate_tolerance(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Tolerance must be between 1 and 10')
        return v
    
    @validator('investment_experience')
    def validate_experience(cls, v):
        if v not in ['novice', 'intermediate', 'expert']:
            raise ValueError('Experience must be novice, intermediate, or expert')
        return v

class PortfolioHoldingsRequest(BaseModel):
    """Current portfolio holdings"""
    equity: float
    bonds: float
    cash: float = 0.0
    
    @validator('equity', 'bonds', 'cash')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError('Holdings must be non-negative')
        return v

class AllocationRequest(BaseModel):
    """Portfolio allocation calculation request"""
    portfolio_value: float
    strategy: str = "80:20"
    custom_equity_ratio: Optional[float] = None
    
    @validator('portfolio_value')
    def validate_portfolio_value(cls, v):
        if v <= 0:
            raise ValueError('Portfolio value must be positive')
        return v
    
    @validator('strategy')
    def validate_strategy(cls, v):
        if v not in ["80:20", "90:10", "custom"]:
            raise ValueError('Strategy must be 80:20, 90:10, or custom')
        return v

class PerformanceProjectionRequest(BaseModel):
    """Performance projection request"""
    initial_amount: float
    monthly_contribution: float
    strategy: str = "80:20"
    years: int = 20
    
    @validator('years')
    def validate_years(cls, v):
        if not 1 <= v <= 50:
            raise ValueError('Years must be between 1 and 50')
        return v

class PortfolioAnalysisRequest(BaseModel):
    """Comprehensive portfolio analysis request"""
    current_holdings: PortfolioHoldingsRequest
    risk_profile: RiskProfileRequest
    time_since_rebalance: int = 0

# Response models
class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    risk_score: float
    recommended_strategy: str
    strategy_description: str
    risk_factors: Dict[str, float]

class AllocationResponse(BaseModel):
    """Allocation calculation response"""
    strategy_name: str
    equity_percentage: float
    bond_percentage: float
    cash_percentage: float
    equity_amount: float
    bond_amount: float
    cash_amount: float
    rebalance_threshold: float

class MathematicalValidationResponse(BaseModel):
    """Mathematical validation score response"""
    mathematical_score: int
    score_breakdown: Dict[str, int]
    validation_message: str
    recommendations: List[str]

class PortfolioAnalysisResponse(BaseModel):
    """Complete portfolio analysis response"""
    current_allocation: Dict[str, float]
    target_allocation: AllocationResponse
    drift_analysis: Dict[str, float]
    rebalance_needed: bool
    rebalance_trades: List[Dict]
    risk_assessment: RiskAssessmentResponse
    mathematical_validation: MathematicalValidationResponse
    next_rebalance_date: str

# Initialize FastAPI app
app = FastAPI(
    title="HardCard Mathematical Engine API",
    description="Systematic wealth building through mathematical precision",
    version="1.0.0"
)

# Initialize engines
math_engine = HardCardMathEngine()
performance_projector = PerformanceProjector()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token (placeholder for actual auth)"""
    # In production, verify JWT token against user database
    token = credentials.credentials
    if not token or len(token) < 10:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token

@app.post("/api/hardcard/analyze-risk-profile", response_model=RiskAssessmentResponse)
async def analyze_risk_profile(
    request: RiskProfileRequest,
    token: str = Depends(verify_token)
):
    """
    Analyze client risk profile and recommend strategy
    
    **Free Tier Feature** - Available to all Trusted Advisors
    """
    try:
        # Convert to engine format
        profile = RiskProfile(
            age=request.age,
            annual_income=Decimal(str(request.annual_income)),
            net_worth=Decimal(str(request.net_worth)),
            investment_experience=request.investment_experience,
            time_horizon=request.time_horizon,
            risk_tolerance=request.risk_tolerance,
            liquidity_needs=Decimal(str(request.liquidity_needs)),
            emotional_tolerance=request.emotional_tolerance
        )
        
        # Perform risk assessment
        risk_score, recommended_strategy = math_engine.assess_risk_profile(profile)
        
        # Get strategy description
        strategy_config = math_engine.strategies[recommended_strategy]
        
        # Calculate risk factor breakdown
        risk_factors = {
            "age_factor": min(10, (65 - request.age) / 4),
            "income_stability": min(10, request.annual_income / 20000),
            "experience_level": {"novice": 3, "intermediate": 6, "expert": 9}[request.investment_experience],
            "time_horizon": min(10, request.time_horizon / 3),
            "risk_tolerance": request.risk_tolerance
        }
        
        logger.info(f"Risk assessment completed: {risk_score} -> {recommended_strategy.value}")
        
        return RiskAssessmentResponse(
            risk_score=float(risk_score),
            recommended_strategy=recommended_strategy.value,
            strategy_description=strategy_config['description'],
            risk_factors=risk_factors
        )
        
    except Exception as e:
        logger.error(f"Risk assessment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Risk assessment failed")

@app.post("/api/hardcard/calculate-allocation", response_model=AllocationResponse)
async def calculate_allocation(
    request: AllocationRequest,
    token: str = Depends(verify_token)
):
    """
    Calculate optimal portfolio allocation
    
    **Core HardCard Feature** - Mathematical precision for wealth building
    """
    try:
        # Parse strategy
        if request.strategy == "80:20":
            strategy = AllocationStrategy.CONSERVATIVE_80_20
        elif request.strategy == "90:10":
            strategy = AllocationStrategy.AGGRESSIVE_90_10
        elif request.strategy == "custom":
            strategy = AllocationStrategy.CUSTOM
        else:
            raise ValueError("Invalid strategy")
        
        # Calculate allocation
        allocation = math_engine.calculate_allocation(
            Decimal(str(request.portfolio_value)),
            strategy,
            Decimal(str(request.custom_equity_ratio)) if request.custom_equity_ratio else None
        )
        
        logger.info(f"Allocation calculated: {allocation.strategy_name}")
        
        return AllocationResponse(
            strategy_name=allocation.strategy_name,
            equity_percentage=float(allocation.equity_percentage),
            bond_percentage=float(allocation.bond_percentage),
            cash_percentage=float(allocation.cash_percentage),
            equity_amount=float(allocation.equity_amount),
            bond_amount=float(allocation.bond_amount),
            cash_amount=float(allocation.cash_amount),
            rebalance_threshold=float(allocation.rebalance_threshold)
        )
        
    except Exception as e:
        logger.error(f"Allocation calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Allocation calculation failed")

@app.post("/api/hardcard/validate-allocation", response_model=MathematicalValidationResponse)
async def validate_allocation(
    holdings: PortfolioHoldingsRequest,
    allocation: AllocationRequest,
    token: str = Depends(verify_token)
):
    """
    Validate portfolio allocation and provide mathematical score
    
    **Premium Feature** - Advanced mathematical validation
    """
    try:
        # Convert holdings to engine format
        current_holdings = {
            'equity': Decimal(str(holdings.equity)),
            'bonds': Decimal(str(holdings.bonds)),
            'cash': Decimal(str(holdings.cash))
        }
        
        # Get target allocation
        strategy = AllocationStrategy.CONSERVATIVE_80_20 if allocation.strategy == "80:20" else AllocationStrategy.AGGRESSIVE_90_10
        target_allocation = math_engine.calculate_allocation(Decimal(str(allocation.portfolio_value)), strategy)
        
        # Calculate mathematical score
        math_score = math_engine.calculate_mathematical_score(current_holdings, target_allocation, 30)
        
        # Generate score breakdown
        drift = math_engine.analyze_portfolio_drift(current_holdings, target_allocation)
        max_drift = max(drift.values())
        
        score_breakdown = {
            "allocation_accuracy": max(0, 40 - int(float(max_drift) * 1000)),
            "rebalancing_discipline": 30 if max_drift <= target_allocation.rebalance_threshold else 15,
            "strategy_consistency": 30 if math_score >= 80 else 15
        }
        
        # Generate validation message
        if math_score >= 90:
            validation_message = "Excellent! Your portfolio follows HardCard mathematical precision."
        elif math_score >= 70:
            validation_message = "Good allocation. Minor adjustments recommended for optimization."
        elif math_score >= 50:
            validation_message = "Moderate alignment. Rebalancing recommended to improve systematic approach."
        else:
            validation_message = "Significant drift detected. Immediate rebalancing strongly recommended."
        
        # Generate recommendations
        recommendations = []
        if max_drift > target_allocation.rebalance_threshold:
            recommendations.append("Portfolio has drifted beyond threshold - rebalancing recommended")
        if math_score < 80:
            recommendations.append("Consider adopting HardCard systematic approach for better results")
        if len(recommendations) == 0:
            recommendations.append("Portfolio is well-aligned with mathematical principles")
        
        logger.info(f"Validation completed: Score {math_score}/100")
        
        return MathematicalValidationResponse(
            mathematical_score=math_score,
            score_breakdown=score_breakdown,
            validation_message=validation_message,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Portfolio validation failed")

@app.post("/api/hardcard/portfolio-analysis", response_model=PortfolioAnalysisResponse)
async def comprehensive_portfolio_analysis(
    request: PortfolioAnalysisRequest,
    token: str = Depends(verify_token)
):
    """
    Comprehensive portfolio analysis combining all HardCard features
    
    **Complete HardCard Experience** - Full mathematical analysis
    """
    try:
        # Convert request to engine formats
        profile = RiskProfile(
            age=request.risk_profile.age,
            annual_income=Decimal(str(request.risk_profile.annual_income)),
            net_worth=Decimal(str(request.risk_profile.net_worth)),
            investment_experience=request.risk_profile.investment_experience,
            time_horizon=request.risk_profile.time_horizon,
            risk_tolerance=request.risk_profile.risk_tolerance,
            liquidity_needs=Decimal(str(request.risk_profile.liquidity_needs)),
            emotional_tolerance=request.risk_profile.emotional_tolerance
        )
        
        current_holdings = {
            'equity': Decimal(str(request.current_holdings.equity)),
            'bonds': Decimal(str(request.current_holdings.bonds)),
            'cash': Decimal(str(request.current_holdings.cash))
        }
        
        # Generate comprehensive analysis
        analysis = math_engine.generate_portfolio_analysis(
            current_holdings, profile, request.time_since_rebalance
        )
        
        # Convert to response format
        target_allocation_response = AllocationResponse(
            strategy_name=analysis.target_allocation.strategy_name,
            equity_percentage=float(analysis.target_allocation.equity_percentage),
            bond_percentage=float(analysis.target_allocation.bond_percentage),
            cash_percentage=float(analysis.target_allocation.cash_percentage),
            equity_amount=float(analysis.target_allocation.equity_amount),
            bond_amount=float(analysis.target_allocation.bond_amount),
            cash_amount=float(analysis.target_allocation.cash_amount),
            rebalance_threshold=float(analysis.target_allocation.rebalance_threshold)
        )
        
        # Risk assessment response
        risk_score, recommended_strategy = math_engine.assess_risk_profile(profile)
        strategy_config = math_engine.strategies[recommended_strategy]
        
        risk_assessment_response = RiskAssessmentResponse(
            risk_score=float(analysis.risk_score),
            recommended_strategy=recommended_strategy.value,
            strategy_description=strategy_config['description'],
            risk_factors={
                "composite_score": float(analysis.risk_score),
                "strategy_alignment": 10 if recommended_strategy.value in analysis.target_allocation.strategy_name else 5
            }
        )
        
        # Mathematical validation response
        math_validation_response = MathematicalValidationResponse(
            mathematical_score=analysis.mathematical_score,
            score_breakdown={
                "allocation_accuracy": 40 if analysis.mathematical_score >= 80 else 20,
                "rebalancing_discipline": 30 if not analysis.rebalance_needed else 15,
                "strategy_consistency": 30 if analysis.mathematical_score >= 70 else 15
            },
            validation_message="Portfolio analysis complete" if analysis.mathematical_score >= 80 else "Optimization opportunities identified",
            recommendations=["Maintain systematic approach"] if analysis.mathematical_score >= 80 else ["Consider rebalancing"]
        )
        
        # Calculate next rebalance date (quarterly for systematic approach)
        next_rebalance = datetime.now() + timedelta(days=90 - request.time_since_rebalance)
        
        logger.info(f"Comprehensive analysis completed: Score {analysis.mathematical_score}/100")
        
        return PortfolioAnalysisResponse(
            current_allocation={k: float(v) for k, v in analysis.current_allocation.items()},
            target_allocation=target_allocation_response,
            drift_analysis={k: float(v) for k, v in analysis.drift_analysis.items()},
            rebalance_needed=analysis.rebalance_needed,
            rebalance_trades=analysis.rebalance_trades,
            risk_assessment=risk_assessment_response,
            mathematical_validation=math_validation_response,
            next_rebalance_date=next_rebalance.strftime("%Y-%m-%d")
        )
        
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Portfolio analysis failed")

@app.post("/api/hardcard/performance-projection")
async def project_performance(
    request: PerformanceProjectionRequest,
    token: str = Depends(verify_token)
):
    """
    Project portfolio performance based on HardCard strategies
    
    **Planning Feature** - Long-term wealth building projections
    """
    try:
        # Parse strategy
        strategy = AllocationStrategy.CONSERVATIVE_80_20 if request.strategy == "80:20" else AllocationStrategy.AGGRESSIVE_90_10
        
        # Generate projection
        projection = performance_projector.project_wealth_accumulation(
            Decimal(str(request.initial_amount)),
            Decimal(str(request.monthly_contribution)),
            strategy,
            request.years
        )
        
        # Convert Decimal values to float for JSON serialization
        response_data = {
            'final_balance': float(projection['final_balance']),
            'total_contributions': float(projection['total_contributions']),
            'total_growth': float(projection['total_growth']),
            'annual_projections': {k: float(v) for k, v in projection['annual_projections'].items()},
            'strategy_used': projection['strategy_used'],
            'blended_return_rate': float(projection['blended_return_rate']),
            'years_projected': request.years,
            'monthly_contribution': request.monthly_contribution
        }
        
        logger.info(f"Performance projection: {request.years} years, final: ${projection['final_balance']}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Performance projection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Performance projection failed")

# Health check endpoint
@app.get("/api/hardcard/health")
async def health_check():
    """Health check for HardCard mathematical engine"""
    return {
        "status": "healthy",
        "engine": "HardCard Mathematical Engine v1.0",
        "features": ["risk_assessment", "allocation_calculation", "mathematical_validation", "performance_projection"],
        "strategies": ["80:20 Conservative", "90:10 Aggressive", "Custom Allocation"],
        "timestamp": datetime.now().isoformat()
    }

# API documentation endpoint
@app.get("/api/hardcard/info")
async def api_info():
    """HardCard API information and capabilities"""
    return {
        "name": "HardCard Mathematical Engine API",
        "version": "1.0.0",
        "description": "Systematic wealth building through mathematical precision",
        "capabilities": {
            "risk_assessment": "Comprehensive client risk profiling with mathematical scoring",
            "allocation_calculation": "Precise 80:20 and 90:10 portfolio allocation strategies",
            "mathematical_validation": "Portfolio validation with 0-100 precision scoring",
            "performance_projection": "Long-term wealth accumulation forecasting",
            "comprehensive_analysis": "Complete portfolio analysis combining all features"
        },
        "free_tier": ["risk_assessment", "basic_allocation"],
        "premium_tier": ["mathematical_validation", "custom_allocation", "advanced_analysis"],
        "enterprise_tier": ["white_label", "bulk_analysis", "custom_strategies"],
        "documentation": "/docs",
        "ecosystem": "Workplace Best Friend - Your Plastic Pal Who's Fun to Be With"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)