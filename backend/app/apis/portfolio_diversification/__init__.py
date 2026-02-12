from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Tuple
import databutton as db
import json
import random
import datetime
import numpy as np
from enum import Enum

# Create API router
router = APIRouter()

# Define enums and constants
class TimeHorizon(str, Enum):
    SHORT = "short"  # 0-5 years
    MEDIUM = "medium"  # 5-10 years
    LONG = "long"  # 10-20 years
    GENERATIONAL = "generational"  # 20+ years

class EconomicScenario(str, Enum):
    GROWTH = "growth"
    RECESSION = "recession"
    INFLATION = "inflation"
    DEFLATION = "deflation"
    STAGFLATION = "stagflation"

class RiskTolerance(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"

# Define asset classes with characteristics
ASSET_CLASSES = {
    "Bitcoin": {"type": "cryptocurrency", "timeframe": [TimeHorizon.MEDIUM, TimeHorizon.LONG, TimeHorizon.GENERATIONAL]},
    "US Stocks": {"type": "equity", "timeframe": [TimeHorizon.MEDIUM, TimeHorizon.LONG]},
    "International Stocks": {"type": "equity", "timeframe": [TimeHorizon.MEDIUM, TimeHorizon.LONG]},
    "Emerging Markets": {"type": "equity", "timeframe": [TimeHorizon.MEDIUM, TimeHorizon.LONG]},
    "US Bonds": {"type": "fixed_income", "timeframe": [TimeHorizon.SHORT, TimeHorizon.MEDIUM]},
    "TIPS": {"type": "fixed_income", "timeframe": [TimeHorizon.SHORT, TimeHorizon.MEDIUM]},
    "Corporate Bonds": {"type": "fixed_income", "timeframe": [TimeHorizon.SHORT, TimeHorizon.MEDIUM]},
    "Real Estate": {"type": "alternative", "timeframe": [TimeHorizon.MEDIUM, TimeHorizon.LONG, TimeHorizon.GENERATIONAL]},
    "Gold": {"type": "commodity", "timeframe": [TimeHorizon.MEDIUM, TimeHorizon.LONG, TimeHorizon.GENERATIONAL]},
    "Commodities": {"type": "commodity", "timeframe": [TimeHorizon.SHORT, TimeHorizon.MEDIUM]},
    "Private Equity": {"type": "alternative", "timeframe": [TimeHorizon.LONG, TimeHorizon.GENERATIONAL]},
    "Venture Capital": {"type": "alternative", "timeframe": [TimeHorizon.LONG, TimeHorizon.GENERATIONAL]},
    "Art & Collectibles": {"type": "alternative", "timeframe": [TimeHorizon.LONG, TimeHorizon.GENERATIONAL]},
    "Cash": {"type": "cash", "timeframe": [TimeHorizon.SHORT]},
    "Dividend Stocks": {"type": "equity", "timeframe": [TimeHorizon.MEDIUM, TimeHorizon.LONG]},
    "Alternative Cryptocurrencies": {"type": "cryptocurrency", "timeframe": [TimeHorizon.MEDIUM]},
}

# Define models
class AssetAllocation(BaseModel):
    asset_class: str
    allocation_percentage: float
    expected_return: float
    volatility: float
    description: Optional[str] = None

class AllocationStrategy(BaseModel):
    id: Optional[str] = None
    profile_id: str
    name: str
    description: str
    risk_tolerance: RiskTolerance
    time_horizon: TimeHorizon
    allocations: List[AssetAllocation]
    expected_annual_return: float
    expected_volatility: float
    sharpe_ratio: float
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    
    @validator('allocations')
    def validate_total_allocation(cls, v):
        total = sum(asset.allocation_percentage for asset in v)
        if not 99.0 <= total <= 101.0:  # Allow small rounding errors
            raise ValueError(f"Total allocation must be 100%, got {total}%")
        return v

class ScenarioResult(BaseModel):
    scenario: EconomicScenario
    description: str
    expected_return: float
    expected_volatility: float
    asset_impacts: Dict[str, float]  # How each asset class performs in this scenario

class AssetCorrelation(BaseModel):
    asset_class1: str
    asset_class2: str
    correlation: float  # -1.0 to 1.0

class DiversificationAnalysis(BaseModel):
    strategy_id: str
    profile_id: str
    asset_allocations: Dict[str, float]
    risk_concentration: Dict[str, float]  # Percentage of risk by asset type
    correlation_matrix: List[AssetCorrelation]
    diversification_score: float  # 0-100 score of how well diversified
    scenario_results: List[ScenarioResult]
    improvement_suggestions: Dict[str, float]  # Suggested rebalance

class DiversificationRequest(BaseModel):
    profile_id: str
    risk_tolerance: RiskTolerance
    time_horizon: TimeHorizon
    current_allocations: Optional[Dict[str, float]] = None  # Current portfolio allocations if any
    preferred_asset_classes: Optional[List[str]] = None  # Asset classes to focus on
    excluded_asset_classes: Optional[List[str]] = None  # Asset classes to exclude

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def generate_correlation_matrix(asset_classes: List[str]) -> List[AssetCorrelation]:
    """Generate a correlation matrix for the given asset classes"""
    # This would normally use historical data, but for simplicity we'll generate sensible values
    # In production, this would be based on real market data
    
    # Define some baseline correlations between asset types
    type_correlations = {
        ("equity", "equity"): 0.7,
        ("equity", "fixed_income"): -0.3,
        ("equity", "alternative"): 0.4,
        ("equity", "commodity"): 0.2,
        ("equity", "cryptocurrency"): 0.3,
        ("equity", "cash"): 0.0,
        
        ("fixed_income", "fixed_income"): 0.8,
        ("fixed_income", "alternative"): 0.1,
        ("fixed_income", "commodity"): 0.0,
        ("fixed_income", "cryptocurrency"): -0.1,
        ("fixed_income", "cash"): 0.2,
        
        ("alternative", "alternative"): 0.5,
        ("alternative", "commodity"): 0.3,
        ("alternative", "cryptocurrency"): 0.3,
        ("alternative", "cash"): 0.0,
        
        ("commodity", "commodity"): 0.6,
        ("commodity", "cryptocurrency"): 0.2,
        ("commodity", "cash"): 0.0,
        
        ("cryptocurrency", "cryptocurrency"): 0.8,
        ("cryptocurrency", "cash"): -0.1,
        
        ("cash", "cash"): 1.0,
    }
    
    # Symmetric matrix - add reversed pairs
    for (type1, type2), value in list(type_correlations.items()):
        if (type2, type1) not in type_correlations:
            type_correlations[(type2, type1)] = value
    
    correlations = []
    
    for i, asset1 in enumerate(asset_classes):
        asset1_type = ASSET_CLASSES.get(asset1, {}).get("type", "unknown")
        
        for j, asset2 in enumerate(asset_classes):
            if i <= j:  # Only compute half the matrix plus diagonal
                asset2_type = ASSET_CLASSES.get(asset2, {}).get("type", "unknown")
                
                if i == j:  # Same asset
                    correlation = 1.0
                else:
                    # Get base correlation between asset types
                    base_correlation = type_correlations.get((asset1_type, asset2_type), 0.0)
                    # Add some noise to make it more realistic
                    correlation = base_correlation + (random.random() - 0.5) * 0.2
                    # Keep within bounds
                    correlation = max(-1.0, min(1.0, correlation))
                    correlation = round(correlation, 2)
                
                correlations.append(AssetCorrelation(
                    asset_class1=asset1,
                    asset_class2=asset2,
                    correlation=correlation
                ))
    
    return correlations

# Global constants for asset return and volatility data
EXPECTED_RETURNS = {
    "Bitcoin": 20.0,
    "US Stocks": 10.0,
    "International Stocks": 9.0,
    "Emerging Markets": 11.0,
    "US Bonds": 4.0,
    "TIPS": 3.5,
    "Corporate Bonds": 5.0,
    "Real Estate": 8.0,
    "Gold": 5.0,
    "Commodities": 6.0,
    "Private Equity": 12.0,
    "Venture Capital": 15.0,
    "Art & Collectibles": 7.0,
    "Cash": 1.5,
    "Dividend Stocks": 8.0,
    "Alternative Cryptocurrencies": 25.0,
}

VOLATILITIES = {
    "Bitcoin": 60.0,
    "US Stocks": 18.0,
    "International Stocks": 20.0,
    "Emerging Markets": 25.0,
    "US Bonds": 5.0,
    "TIPS": 7.0,
    "Corporate Bonds": 8.0,
    "Real Estate": 15.0,
    "Gold": 15.0,
    "Commodities": 20.0,
    "Private Equity": 25.0,
    "Venture Capital": 35.0,
    "Art & Collectibles": 20.0,
    "Cash": 1.0,
    "Dividend Stocks": 15.0,
    "Alternative Cryptocurrencies": 75.0,
}

def calculate_portfolio_metrics(allocations: Dict[str, float]) -> Tuple[float, float, float]:
    """Calculate expected return, volatility, and Sharpe ratio"""
    # Simplified model - would be more sophisticated in production
    
    # Calculate weighted expected return
    expected_return = sum(allocations.get(asset, 0) * EXPECTED_RETURNS.get(asset, 0) / 100 for asset in allocations)
    
    # Calculate volatility (simplified without covariance)
    volatility = sum(allocations.get(asset, 0) * VOLATILITIES.get(asset, 0) / 100 for asset in allocations)
    
    # Calculate Sharpe ratio (assuming risk-free rate of 2%)
    risk_free_rate = 2.0
    sharpe_ratio = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    return expected_return, volatility, sharpe_ratio

def generate_scenario_results(allocations: Dict[str, float]) -> List[ScenarioResult]:
    # Use global expected returns and volatilities
    """Generate scenario analysis results for different economic conditions"""
    scenarios = [
        {
            "scenario": EconomicScenario.GROWTH,
            "description": "Economic expansion with strong GDP growth and low unemployment",
            "asset_impacts": {
                "Bitcoin": 1.5,
                "US Stocks": 1.3,
                "International Stocks": 1.2,
                "Emerging Markets": 1.4,
                "US Bonds": 0.9,
                "TIPS": 0.9,
                "Corporate Bonds": 1.0,
                "Real Estate": 1.2,
                "Gold": 0.8,
                "Commodities": 1.1,
                "Private Equity": 1.4,
                "Venture Capital": 1.6,
                "Art & Collectibles": 1.1,
                "Cash": 0.9,
                "Dividend Stocks": 1.1,
                "Alternative Cryptocurrencies": 1.3,
            }
        },
        {
            "scenario": EconomicScenario.RECESSION,
            "description": "Economic contraction with negative GDP growth and rising unemployment",
            "asset_impacts": {
                "Bitcoin": 0.6,
                "US Stocks": 0.7,
                "International Stocks": 0.7,
                "Emerging Markets": 0.6,
                "US Bonds": 1.1,
                "TIPS": 1.0,
                "Corporate Bonds": 0.8,
                "Real Estate": 0.8,
                "Gold": 1.2,
                "Commodities": 0.7,
                "Private Equity": 0.7,
                "Venture Capital": 0.6,
                "Art & Collectibles": 0.9,
                "Cash": 1.0,
                "Dividend Stocks": 0.8,
                "Alternative Cryptocurrencies": 0.5,
            }
        },
        {
            "scenario": EconomicScenario.INFLATION,
            "description": "Rising prices and eroding purchasing power",
            "asset_impacts": {
                "Bitcoin": 1.3,
                "US Stocks": 0.9,
                "International Stocks": 0.9,
                "Emerging Markets": 0.8,
                "US Bonds": 0.6,
                "TIPS": 1.1,
                "Corporate Bonds": 0.7,
                "Real Estate": 1.2,
                "Gold": 1.4,
                "Commodities": 1.3,
                "Private Equity": 0.9,
                "Venture Capital": 0.8,
                "Art & Collectibles": 1.1,
                "Cash": 0.6,
                "Dividend Stocks": 0.9,
                "Alternative Cryptocurrencies": 1.1,
            }
        },
        {
            "scenario": EconomicScenario.DEFLATION,
            "description": "Falling prices and increasing purchasing power",
            "asset_impacts": {
                "Bitcoin": 0.7,
                "US Stocks": 0.8,
                "International Stocks": 0.8,
                "Emerging Markets": 0.7,
                "US Bonds": 1.3,
                "TIPS": 0.8,
                "Corporate Bonds": 1.2,
                "Real Estate": 0.7,
                "Gold": 0.9,
                "Commodities": 0.6,
                "Private Equity": 0.7,
                "Venture Capital": 0.7,
                "Art & Collectibles": 0.8,
                "Cash": 1.2,
                "Dividend Stocks": 0.9,
                "Alternative Cryptocurrencies": 0.6,
            }
        },
        {
            "scenario": EconomicScenario.STAGFLATION,
            "description": "High inflation combined with high unemployment and stagnant demand",
            "asset_impacts": {
                "Bitcoin": 0.9,
                "US Stocks": 0.7,
                "International Stocks": 0.7,
                "Emerging Markets": 0.6,
                "US Bonds": 0.7,
                "TIPS": 1.0,
                "Corporate Bonds": 0.7,
                "Real Estate": 0.9,
                "Gold": 1.3,
                "Commodities": 1.2,
                "Private Equity": 0.7,
                "Venture Capital": 0.6,
                "Art & Collectibles": 0.9,
                "Cash": 0.8,
                "Dividend Stocks": 0.8,
                "Alternative Cryptocurrencies": 0.8,
            }
        },
    ]
    
    results = []
    for scenario in scenarios:
        # Calculate expected portfolio performance in this scenario
        expected_return = sum(
            allocations.get(asset, 0) * EXPECTED_RETURNS.get(asset, 0) * impact / 100
            for asset, impact in scenario["asset_impacts"].items()
        )
        
        expected_volatility = sum(
            allocations.get(asset, 0) * VOLATILITIES.get(asset, 0) * 
            (2.0 - scenario["asset_impacts"].get(asset, 1.0)) / 100  # Higher impact generally means lower volatility
            for asset in allocations
        )
        
        results.append(ScenarioResult(
            scenario=scenario["scenario"],
            description=scenario["description"],
            expected_return=round(expected_return, 2),
            expected_volatility=round(expected_volatility, 2),
            asset_impacts={asset: round(impact, 2) for asset, impact in scenario["asset_impacts"].items()}
        ))
    
    return results

def generate_improvement_suggestions(allocations: Dict[str, float], risk_tolerance: RiskTolerance, time_horizon: TimeHorizon) -> Dict[str, float]:
    """Generate suggestions to improve the portfolio"""
    # Target allocations based on risk tolerance and time horizon
    target_allocations = {}
    
    # Define allocation targets based on risk profile and time horizon
    if risk_tolerance == RiskTolerance.CONSERVATIVE:
        if time_horizon == TimeHorizon.SHORT:
            target_allocations = {
                "Cash": 30,
                "US Bonds": 40,
                "TIPS": 10,
                "US Stocks": 10,
                "Dividend Stocks": 5,
                "Gold": 5,
            }
        elif time_horizon == TimeHorizon.MEDIUM:
            target_allocations = {
                "Cash": 15,
                "US Bonds": 35,
                "Corporate Bonds": 10,
                "US Stocks": 20,
                "Dividend Stocks": 10,
                "Gold": 5,
                "Real Estate": 5,
            }
        else:  # LONG or GENERATIONAL
            target_allocations = {
                "Cash": 5,
                "US Bonds": 25,
                "Corporate Bonds": 10,
                "US Stocks": 25,
                "Dividend Stocks": 15,
                "International Stocks": 5,
                "Gold": 5,
                "Real Estate": 10,
            }
    
    elif risk_tolerance == RiskTolerance.MODERATE:
        if time_horizon == TimeHorizon.SHORT:
            target_allocations = {
                "Cash": 20,
                "US Bonds": 30,
                "US Stocks": 25,
                "International Stocks": 10,
                "Dividend Stocks": 10,
                "Gold": 5,
            }
        elif time_horizon == TimeHorizon.MEDIUM:
            target_allocations = {
                "Cash": 10,
                "US Bonds": 20,
                "Corporate Bonds": 10,
                "US Stocks": 30,
                "International Stocks": 10,
                "Emerging Markets": 5,
                "Dividend Stocks": 5,
                "Real Estate": 5,
                "Gold": 5,
            }
        else:  # LONG or GENERATIONAL
            target_allocations = {
                "Cash": 5,
                "US Bonds": 15,
                "US Stocks": 30,
                "International Stocks": 15,
                "Emerging Markets": 10,
                "Real Estate": 10,
                "Bitcoin": 5,
                "Gold": 5,
                "Private Equity": 5,
            }
    
    elif risk_tolerance == RiskTolerance.AGGRESSIVE:
        if time_horizon == TimeHorizon.SHORT:
            target_allocations = {
                "Cash": 10,
                "US Bonds": 15,
                "US Stocks": 40,
                "International Stocks": 20,
                "Emerging Markets": 10,
                "Bitcoin": 5,
            }
        elif time_horizon == TimeHorizon.MEDIUM:
            target_allocations = {
                "Cash": 5,
                "US Bonds": 10,
                "US Stocks": 35,
                "International Stocks": 15,
                "Emerging Markets": 15,
                "Real Estate": 5,
                "Bitcoin": 10,
                "Private Equity": 5,
            }
        else:  # LONG or GENERATIONAL
            target_allocations = {
                "Cash": 5,
                "US Stocks": 25,
                "International Stocks": 15,
                "Emerging Markets": 15,
                "Real Estate": 10,
                "Bitcoin": 15,
                "Private Equity": 10,
                "Venture Capital": 5,
            }
    
    else:  # VERY_AGGRESSIVE
        if time_horizon == TimeHorizon.SHORT:
            target_allocations = {
                "Cash": 5,
                "US Stocks": 35,
                "International Stocks": 20,
                "Emerging Markets": 20,
                "Bitcoin": 10,
                "Alternative Cryptocurrencies": 5,
                "Commodities": 5,
            }
        elif time_horizon == TimeHorizon.MEDIUM:
            target_allocations = {
                "US Stocks": 25,
                "International Stocks": 15,
                "Emerging Markets": 20,
                "Bitcoin": 15,
                "Alternative Cryptocurrencies": 5,
                "Private Equity": 10,
                "Venture Capital": 5,
                "Real Estate": 5,
            }
        else:  # LONG or GENERATIONAL
            target_allocations = {
                "US Stocks": 20,
                "International Stocks": 15,
                "Emerging Markets": 15,
                "Bitcoin": 20,
                "Alternative Cryptocurrencies": 5,
                "Venture Capital": 10,
                "Private Equity": 10,
                "Art & Collectibles": 5,
            }
    
    # Find differences between current and target allocations
    improvement_suggestions = {}
    for asset, target in target_allocations.items():
        current = allocations.get(asset, 0)
        if abs(current - target) >= 5:  # Only suggest significant changes
            improvement_suggestions[asset] = target
    
    return improvement_suggestions

# Endpoints
@router.post("/analyze")
async def analyze_portfolio_diversification(request: DiversificationRequest) -> DiversificationAnalysis:
    """Analyze a portfolio for diversification, risk assessment, and economic scenario planning.
    
    This endpoint provides sophisticated portfolio analysis to help Legacy Vault users understand
    their current asset allocation, identify potential diversification improvements, and
    forecast performance across different economic scenarios.
    
    It analyzes the portfolio's correlation structure, risk concentration, and diversification score,
    then provides targeted recommendations to optimize the portfolio based on the user's time horizon
    and risk tolerance.
    
    Args:
        request (DiversificationRequest): Portfolio analysis parameters including:
            - profile_id: The family member's profile ID
            - risk_tolerance: Conservative to very aggressive risk preference
            - time_horizon: Investment timeframe (short, medium, long, generational)
            - current_allocations: Current asset allocation percentages (optional)
            - preferred_asset_classes: Asset classes to prioritize (optional)
            - excluded_asset_classes: Asset classes to avoid (optional)
    
    Returns:
        DiversificationAnalysis: Comprehensive portfolio analysis including:
            - asset_allocations: Current portfolio allocation
            - risk_concentration: Risk breakdown by asset type
            - correlation_matrix: Asset correlation analysis
            - diversification_score: Overall diversification rating (0-100)
            - scenario_results: Performance projections in different economic scenarios
            - improvement_suggestions: Recommended allocation changes
    """
    try:
        # Handle case where no current allocations are provided
        current_allocations = request.current_allocations or {}
        
        # If allocations are empty, create a default allocation based on risk profile
        if not current_allocations:
            if request.risk_tolerance == RiskTolerance.CONSERVATIVE:
                current_allocations = {
                    "US Bonds": 40,
                    "US Stocks": 25,
                    "International Stocks": 10,
                    "Cash": 15,
                    "Gold": 5,
                    "Real Estate": 5,
                }
            elif request.risk_tolerance == RiskTolerance.MODERATE:
                current_allocations = {
                    "US Stocks": 40,
                    "International Stocks": 15,
                    "US Bonds": 25,
                    "Real Estate": 10,
                    "Bitcoin": 5,
                    "Cash": 5,
                }
            elif request.risk_tolerance == RiskTolerance.AGGRESSIVE:
                current_allocations = {
                    "US Stocks": 45,
                    "International Stocks": 20,
                    "Emerging Markets": 10,
                    "Bitcoin": 15,
                    "US Bonds": 5,
                    "Cash": 5,
                }
            else:  # VERY_AGGRESSIVE
                current_allocations = {
                    "US Stocks": 35,
                    "International Stocks": 15,
                    "Emerging Markets": 15,
                    "Bitcoin": 25,
                    "Alternative Cryptocurrencies": 5,
                    "Venture Capital": 5,
                }
        
        # Generate a correlation matrix for the assets in the portfolio
        asset_classes = list(current_allocations.keys())
        correlation_matrix = generate_correlation_matrix(asset_classes)
        
        # Calculate portfolio metrics
        expected_return, volatility, sharpe_ratio = calculate_portfolio_metrics(current_allocations)
        
        # Generate risk concentration by asset type
        risk_concentration = {}
        total_risk = sum(current_allocations.get(asset, 0) * VOLATILITIES.get(asset, 0) for asset in current_allocations)
        
        if total_risk > 0:
            for asset in current_allocations:
                asset_risk = current_allocations[asset] * VOLATILITIES.get(asset, 0)
                asset_type = ASSET_CLASSES.get(asset, {}).get("type", "unknown")
                risk_concentration[asset_type] = risk_concentration.get(asset_type, 0) + (asset_risk / total_risk * 100)
        
        # Calculate diversification score (simplified)
        # Higher is better - we reward broad allocation across uncorrelated asset classes
        num_asset_classes = len(current_allocations)
        avg_correlation = sum(c.correlation for c in correlation_matrix if c.correlation != 1.0) / max(1, len(correlation_matrix) - num_asset_classes)
        asset_type_count = len(set(ASSET_CLASSES.get(asset, {}).get("type", "unknown") for asset in current_allocations))
        
        diversification_score = (
            (100 - avg_correlation * 50) *  # Lower correlation is better
            (num_asset_classes / 10) *  # More asset classes is better (max 10)
            (asset_type_count / 5)  # More asset types is better (max 5)
        )
        diversification_score = min(100, max(0, diversification_score))
        
        # Generate scenario results
        scenario_results = generate_scenario_results(current_allocations)
        
        # Generate improvement suggestions
        improvement_suggestions = generate_improvement_suggestions(
            current_allocations, request.risk_tolerance, request.time_horizon
        )
        
        # Generate a unique ID for this analysis
        import uuid
        strategy_id = f"{sanitize_storage_key(request.profile_id)}_div_{uuid.uuid4().hex[:8]}"
        
        # Create the response
        analysis = DiversificationAnalysis(
            strategy_id=strategy_id,
            profile_id=request.profile_id,
            asset_allocations=current_allocations,
            risk_concentration={k: round(v, 2) for k, v in risk_concentration.items()},
            correlation_matrix=correlation_matrix,
            diversification_score=round(diversification_score, 2),
            scenario_results=scenario_results,
            improvement_suggestions=improvement_suggestions
        )
        
        # Store the analysis for future reference
        storage_key = f"diversification_analysis_{sanitize_storage_key(request.profile_id)}"
        
        try:
            analyses = db.storage.json.get(storage_key, default=[])
        except Exception:
            analyses = []
        
        # Add to list of analyses
        analyses.append(analysis.dict())
        
        # Keep only the most recent 10 analyses
        analyses = analyses[-10:]
        
        # Save to storage
        db.storage.json.put(storage_key, analyses)
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing portfolio diversification: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")

@router.post("/create-strategy")
async def create_allocation_strategy(allocation: AllocationStrategy) -> AllocationStrategy:
    """Create a custom investment allocation strategy for a family member.
    
    Allows Legacy Vault users to define and save customized asset allocation strategies
    for family members. These strategies can be used to guide investment decisions
    and track portfolio performance over time.
    
    Each strategy includes detailed allocation percentages for different asset classes,
    along with expected return, volatility, and risk metrics.
    
    Args:
        allocation (AllocationStrategy): The strategy details including:
            - profile_id: The family member's profile ID
            - name: Strategy name
            - description: Strategy description
            - risk_tolerance: Risk level (conservative to very aggressive)
            - time_horizon: Investment timeframe
            - allocations: List of asset allocations with percentages
            - expected_annual_return: Projected annual return
            - expected_volatility: Projected volatility
            - sharpe_ratio: Risk-adjusted return metric
    
    Returns:
        AllocationStrategy: The created strategy with all details
    """
    try:
        # Generate ID if not provided
        if not allocation.id:
            import uuid
            allocation.id = f"{sanitize_storage_key(allocation.profile_id)}_strategy_{uuid.uuid4().hex[:8]}"
        
        # Store the allocation strategy
        storage_key = f"allocation_strategies_{sanitize_storage_key(allocation.profile_id)}"
        
        try:
            strategies = db.storage.json.get(storage_key, default=[])
        except Exception:
            strategies = []
        
        # Add to list of strategies
        strategies.append(allocation.dict())
        
        # Save to storage
        db.storage.json.put(storage_key, strategies)
        
        return allocation
        
    except Exception as e:
        print(f"Error creating allocation strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create strategy: {str(e)}")

@router.get("/strategies/{profile_id}")
async def get_allocation_strategies(profile_id: str) -> List[AllocationStrategy]:
    """Get all investment allocation strategies for a family member.
    
    Retrieves all saved investment strategies associated with a specific family member profile.
    This allows users to view and manage their different investment approaches for each
    family member in the Legacy Vault system.
    
    Args:
        profile_id (str): The unique identifier of the family profile
    
    Returns:
        List[AllocationStrategy]: A list of all saved allocation strategies
    """
    try:
        # Get strategies from storage
        storage_key = f"allocation_strategies_{sanitize_storage_key(profile_id)}"
        
        try:
            strategies_data = db.storage.json.get(storage_key, default=[])
            return [AllocationStrategy(**strategy) for strategy in strategies_data]
        except Exception:
            return []
        
    except Exception as e:
        print(f"Error getting allocation strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategies: {str(e)}")

@router.get("/strategy/{strategy_id}")
async def get_allocation_strategy(strategy_id: str) -> AllocationStrategy:
    """Get a specific allocation strategy"""
    try:
        # Extract profile ID from strategy ID
        parts = strategy_id.split('_strategy_')
        if len(parts) != 2:
            parts = strategy_id.split('_div_')  # Try diversification ID format
            if len(parts) != 2:
                raise HTTPException(status_code=400, detail="Invalid strategy ID format")
        
        profile_id = parts[0]
        
        # Try allocation strategies first
        storage_key = f"allocation_strategies_{sanitize_storage_key(profile_id)}"
        try:
            strategies = db.storage.json.get(storage_key, default=[])
            for strategy in strategies:
                if strategy.get('id') == strategy_id:
                    return AllocationStrategy(**strategy)
        except Exception:
            pass
        
        # Try diversification analyses next
        storage_key = f"diversification_analysis_{sanitize_storage_key(profile_id)}"
        try:
            analyses = db.storage.json.get(storage_key, default=[])
            for analysis in analyses:
                if analysis.get('strategy_id') == strategy_id:
                    # Convert analysis to strategy format
                    allocations = []
                    for asset, percentage in analysis.get('asset_allocations', {}).items():
                        allocations.append({
                            "asset_class": asset,
                            "allocation_percentage": percentage,
                            "expected_return": EXPECTED_RETURNS.get(asset, 0),
                            "volatility": VOLATILITIES.get(asset, 0)
                        })
                    
                    return AllocationStrategy(
                        id=analysis.get('strategy_id'),
                        profile_id=analysis.get('profile_id'),
                        name=f"Analysis {strategy_id[-8:]}",
                        description="Generated from portfolio analysis",
                        risk_tolerance=RiskTolerance.MODERATE,  # Default
                        time_horizon=TimeHorizon.LONG,  # Default
                        allocations=allocations,
                        expected_annual_return=sum(alloc.get('allocation_percentage', 0) * alloc.get('expected_return', 0) / 100 for alloc in allocations),
                        expected_volatility=sum(alloc.get('allocation_percentage', 0) * alloc.get('volatility', 0) / 100 for alloc in allocations),
                        sharpe_ratio=0.0,  # Would need to calculate
                        created_at=datetime.datetime.now().isoformat()
                    )
        except Exception:
            pass
        
        # Not found
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting allocation strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategy: {str(e)}")

@router.delete("/strategy/{strategy_id}")
async def delete_allocation_strategy(strategy_id: str) -> Dict[str, str]:
    """Delete an allocation strategy"""
    try:
        # Extract profile ID from strategy ID
        parts = strategy_id.split('_strategy_')
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid strategy ID format")
        
        profile_id = parts[0]
        
        # Get strategies from storage
        storage_key = f"allocation_strategies_{sanitize_storage_key(profile_id)}"
        
        try:
            strategies = db.storage.json.get(storage_key, default=[])
        except Exception:
            strategies = []
        
        # Filter out the strategy to delete
        original_count = len(strategies)
        strategies = [s for s in strategies if s.get('id') != strategy_id]
        
        if len(strategies) == original_count:
            raise HTTPException(status_code=404, detail="Strategy not found")
        
        # Save updated strategies
        db.storage.json.put(storage_key, strategies)
        
        return {"message": "Strategy deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting allocation strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete strategy: {str(e)}")

@router.get("/asset-classes")
async def get_asset_classes() -> Dict[str, Dict]:
    """Get all available investment asset classes with detailed characteristics.
    
    Provides a comprehensive list of all available asset classes that can be included in
    investment portfolios in the Legacy Vault system. Each asset class includes information
    about its type (equity, fixed income, alternative, etc.) and appropriate time horizons.
    
    This endpoint is useful for building custom investment strategies and understanding
    the characteristics of different investment options.
    
    Returns:
        Dict[str, Dict]: A dictionary of asset classes with their characteristics
    """
    return ASSET_CLASSES

@router.get("/economic-scenarios")
async def get_economic_scenarios() -> List[Dict]:
    """Get all economic scenarios for long-term investment planning.
    
    Provides a list of potential economic scenarios (growth, recession, inflation, etc.)
    that are used in the portfolio analysis to simulate how investments might perform
    under different economic conditions.
    
    This data helps Legacy Vault users understand how their family investments might
    perform across different future economic environments, supporting generational
    planning with consideration for various market conditions.
    
    Returns:
        List[Dict]: A list of economic scenarios with descriptions and impact factors
    """
    return [
        {
            "scenario": EconomicScenario.GROWTH,
            "name": "Economic Growth",
            "description": "Economic expansion with strong GDP growth and low unemployment"
        },
        {
            "scenario": EconomicScenario.RECESSION,
            "name": "Recession",
            "description": "Economic contraction with negative GDP growth and rising unemployment"
        },
        {
            "scenario": EconomicScenario.INFLATION,
            "name": "High Inflation",
            "description": "Rising prices and eroding purchasing power"
        },
        {
            "scenario": EconomicScenario.DEFLATION,
            "name": "Deflation",
            "description": "Falling prices and increasing purchasing power"
        },
        {
            "scenario": EconomicScenario.STAGFLATION,
            "name": "Stagflation",
            "description": "High inflation combined with high unemployment and stagnant demand"
        }
    ]
