"""
HardCard Mathematical Engine - Core Allocation Algorithms
Systematic wealth building through mathematically validated strategies
"""

import math
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AllocationStrategy(Enum):
    """HardCard allocation strategy types"""
    CONSERVATIVE_80_20 = "80:20"
    AGGRESSIVE_90_10 = "90:10"
    CUSTOM = "custom"

@dataclass
class RiskProfile:
    """Client risk assessment profile"""
    age: int
    annual_income: Decimal
    net_worth: Decimal
    investment_experience: str  # 'novice', 'intermediate', 'expert'
    time_horizon: int  # years
    risk_tolerance: int  # 1-10 scale
    liquidity_needs: Decimal  # percentage of portfolio
    emotional_tolerance: int  # 1-10 scale for market volatility

@dataclass
class AllocationTarget:
    """Target portfolio allocation"""
    equity_percentage: Decimal
    bond_percentage: Decimal
    cash_percentage: Decimal
    equity_amount: Decimal
    bond_amount: Decimal
    cash_amount: Decimal
    rebalance_threshold: Decimal
    strategy_name: str

@dataclass
class PortfolioAnalysis:
    """Portfolio analysis results"""
    current_allocation: Dict[str, Decimal]
    target_allocation: AllocationTarget
    drift_analysis: Dict[str, Decimal]
    rebalance_needed: bool
    rebalance_trades: List[Dict]
    risk_score: Decimal
    mathematical_score: int  # 0-100 HardCard validation score

class HardCardMathEngine:
    """
    Core HardCard mathematical engine for systematic wealth building
    
    Implements proven 80:20 and 90:10 allocation strategies with
    mathematical precision and risk management protocols.
    """
    
    def __init__(self):
        """Initialize the mathematical engine"""
        self.strategies = {
            AllocationStrategy.CONSERVATIVE_80_20: {
                'equity': Decimal('0.8000'),
                'bonds': Decimal('0.2000'),
                'cash': Decimal('0.0000'),
                'rebalance_threshold': Decimal('0.0500'),  # 5% drift
                'name': 'Conservative 80:20 Strategy',
                'description': 'Systematic wealth building with 80% growth, 20% stability'
            },
            AllocationStrategy.AGGRESSIVE_90_10: {
                'equity': Decimal('0.9000'),
                'bonds': Decimal('0.1000'),
                'cash': Decimal('0.0000'),
                'rebalance_threshold': Decimal('0.0300'),  # 3% drift (tighter for aggressive)
                'name': 'Aggressive 90:10 Strategy',
                'description': 'Accelerated wealth building with 90% growth, 10% stability'
            }
        }
        
        # Mathematical constants for risk calculations
        self.RISK_MULTIPLIERS = {
            'age_factor': Decimal('0.20'),
            'income_stability': Decimal('0.15'),
            'net_worth_factor': Decimal('0.10'),
            'experience_factor': Decimal('0.15'),
            'time_horizon_factor': Decimal('0.25'),
            'risk_tolerance_factor': Decimal('0.15')
        }
        
    def assess_risk_profile(self, profile: RiskProfile) -> Tuple[Decimal, AllocationStrategy]:
        """
        Mathematical risk assessment to determine optimal strategy
        
        Returns:
            Tuple of (risk_score, recommended_strategy)
        """
        logger.info(f"Assessing risk profile for client age {profile.age}")
        
        # Age-based risk calculation (younger = higher risk capacity)
        age_score = max(0, (65 - profile.age) / 40) * 10
        
        # Income stability assessment
        income_score = min(10, float(profile.annual_income) / 20000)
        
        # Net worth factor (higher wealth = more risk capacity)
        net_worth_score = min(10, math.log10(max(1, float(profile.net_worth))) / 2)
        
        # Experience factor
        experience_scores = {'novice': 3, 'intermediate': 6, 'expert': 9}
        experience_score = experience_scores.get(profile.investment_experience, 5)
        
        # Time horizon (longer = more aggressive)
        time_horizon_score = min(10, profile.time_horizon / 3)
        
        # Subjective risk tolerance
        risk_tolerance_score = profile.risk_tolerance
        
        # Calculate composite risk score
        composite_score = (
            age_score * self.RISK_MULTIPLIERS['age_factor'] +
            income_score * self.RISK_MULTIPLIERS['income_stability'] +
            net_worth_score * self.RISK_MULTIPLIERS['net_worth_factor'] +
            experience_score * self.RISK_MULTIPLIERS['experience_factor'] +
            time_horizon_score * self.RISK_MULTIPLIERS['time_horizon_factor'] +
            risk_tolerance_score * self.RISK_MULTIPLIERS['risk_tolerance_factor']
        )
        
        risk_score = Decimal(str(round(composite_score, 2)))
        
        # Strategy recommendation based on risk score
        if risk_score >= Decimal('7.5'):
            recommended_strategy = AllocationStrategy.AGGRESSIVE_90_10
        else:
            recommended_strategy = AllocationStrategy.CONSERVATIVE_80_20
            
        logger.info(f"Risk score: {risk_score}, Recommended: {recommended_strategy.value}")
        return risk_score, recommended_strategy
    
    def calculate_allocation(
        self, 
        portfolio_value: Decimal, 
        strategy: AllocationStrategy = AllocationStrategy.CONSERVATIVE_80_20,
        custom_equity_ratio: Optional[Decimal] = None
    ) -> AllocationTarget:
        """
        Calculate target portfolio allocation based on strategy
        
        Args:
            portfolio_value: Total portfolio value
            strategy: Allocation strategy to use
            custom_equity_ratio: Custom equity percentage (for advanced users)
            
        Returns:
            AllocationTarget with precise allocations
        """
        if strategy == AllocationStrategy.CUSTOM and custom_equity_ratio:
            equity_ratio = custom_equity_ratio
            bond_ratio = Decimal('1.0') - equity_ratio
            cash_ratio = Decimal('0.0')
            rebalance_threshold = Decimal('0.0400')  # 4% for custom
            strategy_name = f"Custom {int(equity_ratio * 100)}:{int(bond_ratio * 100)} Strategy"
        else:
            strategy_config = self.strategies[strategy]
            equity_ratio = strategy_config['equity']
            bond_ratio = strategy_config['bonds']
            cash_ratio = strategy_config['cash']
            rebalance_threshold = strategy_config['rebalance_threshold']
            strategy_name = strategy_config['name']
        
        # Calculate precise allocations using Decimal for financial accuracy
        equity_amount = (portfolio_value * equity_ratio).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        bond_amount = (portfolio_value * bond_ratio).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        cash_amount = (portfolio_value * cash_ratio).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        # Ensure allocations sum to total (adjust cash for rounding)
        total_allocated = equity_amount + bond_amount + cash_amount
        if total_allocated != portfolio_value:
            cash_amount += portfolio_value - total_allocated
            
        return AllocationTarget(
            equity_percentage=equity_ratio,
            bond_percentage=bond_ratio,
            cash_percentage=cash_ratio,
            equity_amount=equity_amount,
            bond_amount=bond_amount,
            cash_amount=cash_amount,
            rebalance_threshold=rebalance_threshold,
            strategy_name=strategy_name
        )
    
    def analyze_portfolio_drift(
        self, 
        current_holdings: Dict[str, Decimal],
        target_allocation: AllocationTarget
    ) -> Dict[str, Decimal]:
        """
        Analyze how far current portfolio has drifted from target
        
        Args:
            current_holdings: {'equity': amount, 'bonds': amount, 'cash': amount}
            target_allocation: Target allocation to compare against
            
        Returns:
            Dictionary of drift percentages by asset class
        """
        total_value = sum(current_holdings.values())
        
        if total_value == 0:
            return {'equity': Decimal('0'), 'bonds': Decimal('0'), 'cash': Decimal('0')}
        
        current_equity_pct = current_holdings.get('equity', Decimal('0')) / total_value
        current_bond_pct = current_holdings.get('bonds', Decimal('0')) / total_value
        current_cash_pct = current_holdings.get('cash', Decimal('0')) / total_value
        
        equity_drift = abs(current_equity_pct - target_allocation.equity_percentage)
        bond_drift = abs(current_bond_pct - target_allocation.bond_percentage)
        cash_drift = abs(current_cash_pct - target_allocation.cash_percentage)
        
        return {
            'equity': equity_drift,
            'bonds': bond_drift,
            'cash': cash_drift
        }
    
    def calculate_rebalance_trades(
        self,
        current_holdings: Dict[str, Decimal],
        target_allocation: AllocationTarget
    ) -> List[Dict]:
        """
        Calculate specific trades needed to rebalance portfolio
        
        Returns:
            List of trade instructions
        """
        total_value = sum(current_holdings.values())
        trades = []
        
        # Calculate current vs target amounts
        current_equity = current_holdings.get('equity', Decimal('0'))
        current_bonds = current_holdings.get('bonds', Decimal('0'))
        current_cash = current_holdings.get('cash', Decimal('0'))
        
        # Calculate new target amounts based on current total value
        new_target = self.calculate_allocation(total_value, strategy=AllocationStrategy.CONSERVATIVE_80_20)
        
        equity_diff = new_target.equity_amount - current_equity
        bond_diff = new_target.bond_amount - current_bonds
        
        # Generate trade instructions
        if abs(equity_diff) > Decimal('1.00'):  # Only trade if difference > $1
            action = 'BUY' if equity_diff > 0 else 'SELL'
            trades.append({
                'asset_class': 'equity',
                'action': action,
                'amount': abs(equity_diff),
                'current': current_equity,
                'target': new_target.equity_amount
            })
        
        if abs(bond_diff) > Decimal('1.00'):
            action = 'BUY' if bond_diff > 0 else 'SELL'
            trades.append({
                'asset_class': 'bonds',
                'action': action,
                'amount': abs(bond_diff),
                'current': current_bonds,
                'target': new_target.bond_amount
            })
            
        return trades
    
    def calculate_mathematical_score(
        self,
        current_holdings: Dict[str, Decimal],
        target_allocation: AllocationTarget,
        time_since_rebalance: int  # days
    ) -> int:
        """
        Calculate HardCard mathematical validation score (0-100)
        
        Factors:
        - Allocation accuracy (40 points)
        - Rebalancing discipline (30 points)
        - Strategy consistency (30 points)
        """
        score = 0
        
        # Allocation accuracy (40 points max)
        drift = self.analyze_portfolio_drift(current_holdings, target_allocation)
        max_drift = max(drift.values())
        accuracy_score = max(0, 40 - (float(max_drift) * 1000))  # Penalize drift
        score += int(accuracy_score)
        
        # Rebalancing discipline (30 points max)
        if max_drift <= target_allocation.rebalance_threshold:
            rebalance_score = 30  # Perfect score for staying within threshold
        elif time_since_rebalance <= 90:  # Rebalanced within 90 days
            rebalance_score = 20
        elif time_since_rebalance <= 180:
            rebalance_score = 10
        else:
            rebalance_score = 0
        score += rebalance_score
        
        # Strategy consistency (30 points max)
        # Bonus points for following HardCard systematic approach
        total_value = sum(current_holdings.values())
        if total_value > 0:
            equity_pct = current_holdings.get('equity', Decimal('0')) / total_value
            # Check if close to 80:20 or 90:10 ratios
            close_to_80_20 = abs(equity_pct - Decimal('0.80')) <= Decimal('0.10')
            close_to_90_10 = abs(equity_pct - Decimal('0.90')) <= Decimal('0.10')
            
            if close_to_80_20 or close_to_90_10:
                consistency_score = 30
            else:
                consistency_score = 15  # Partial credit for any systematic approach
        else:
            consistency_score = 0
            
        score += consistency_score
        
        return min(100, max(0, score))  # Ensure score is between 0-100
    
    def generate_portfolio_analysis(
        self,
        current_holdings: Dict[str, Decimal],
        risk_profile: RiskProfile,
        time_since_rebalance: int = 0
    ) -> PortfolioAnalysis:
        """
        Generate comprehensive portfolio analysis
        
        Returns:
            Complete PortfolioAnalysis with recommendations
        """
        # Assess risk and get strategy recommendation
        risk_score, recommended_strategy = self.assess_risk_profile(risk_profile)
        
        # Calculate target allocation
        total_value = sum(current_holdings.values())
        target_allocation = self.calculate_allocation(total_value, recommended_strategy)
        
        # Analyze drift
        drift_analysis = self.analyze_portfolio_drift(current_holdings, target_allocation)
        
        # Check if rebalance needed
        max_drift = max(drift_analysis.values())
        rebalance_needed = max_drift > target_allocation.rebalance_threshold
        
        # Calculate rebalance trades if needed
        rebalance_trades = []
        if rebalance_needed:
            rebalance_trades = self.calculate_rebalance_trades(current_holdings, target_allocation)
        
        # Calculate mathematical validation score
        math_score = self.calculate_mathematical_score(
            current_holdings, target_allocation, time_since_rebalance
        )
        
        # Calculate current allocation percentages
        if total_value > 0:
            current_allocation = {
                'equity': current_holdings.get('equity', Decimal('0')) / total_value,
                'bonds': current_holdings.get('bonds', Decimal('0')) / total_value,
                'cash': current_holdings.get('cash', Decimal('0')) / total_value
            }
        else:
            current_allocation = {'equity': Decimal('0'), 'bonds': Decimal('0'), 'cash': Decimal('0')}
        
        return PortfolioAnalysis(
            current_allocation=current_allocation,
            target_allocation=target_allocation,
            drift_analysis=drift_analysis,
            rebalance_needed=rebalance_needed,
            rebalance_trades=rebalance_trades,
            risk_score=risk_score,
            mathematical_score=math_score
        )

# Performance projection utilities
class PerformanceProjector:
    """Project portfolio performance based on HardCard strategies"""
    
    def __init__(self):
        # Historical market return assumptions (conservative estimates)
        self.EQUITY_ANNUAL_RETURN = Decimal('0.07')  # 7% equity return
        self.BOND_ANNUAL_RETURN = Decimal('0.03')   # 3% bond return
        self.INFLATION_RATE = Decimal('0.025')      # 2.5% inflation
        
    def project_wealth_accumulation(
        self,
        initial_amount: Decimal,
        monthly_contribution: Decimal,
        strategy: AllocationStrategy,
        years: int
    ) -> Dict[str, Decimal]:
        """
        Project wealth accumulation over time
        
        Returns:
            Dictionary with year-by-year projections
        """
        engine = HardCardMathEngine()
        allocation = engine.calculate_allocation(Decimal('100000'), strategy)  # Use percentage allocation
        
        # Calculate blended return rate
        blended_return = (
            allocation.equity_percentage * self.EQUITY_ANNUAL_RETURN +
            allocation.bond_percentage * self.BOND_ANNUAL_RETURN
        )
        
        monthly_return = blended_return / 12
        
        projections = {}
        balance = initial_amount
        
        for year in range(1, years + 1):
            for month in range(12):
                # Add monthly contribution
                balance += monthly_contribution
                # Apply monthly return
                balance *= (1 + monthly_return)
            
            projections[f"year_{year}"] = balance.quantize(Decimal('0.01'))
            
        return {
            'final_balance': balance.quantize(Decimal('0.01')),
            'total_contributions': (initial_amount + (monthly_contribution * 12 * years)).quantize(Decimal('0.01')),
            'total_growth': (balance - initial_amount - (monthly_contribution * 12 * years)).quantize(Decimal('0.01')),
            'annual_projections': projections,
            'strategy_used': strategy.value,
            'blended_return_rate': blended_return
        }

if __name__ == "__main__":
    # Example usage and testing
    engine = HardCardMathEngine()
    
    # Example risk profile
    profile = RiskProfile(
        age=35,
        annual_income=Decimal('120000'),
        net_worth=Decimal('300000'),
        investment_experience='intermediate',
        time_horizon=25,
        risk_tolerance=7,
        liquidity_needs=Decimal('0.05'),
        emotional_tolerance=6
    )
    
    # Example current holdings
    holdings = {
        'equity': Decimal('75000'),
        'bonds': Decimal('20000'),
        'cash': Decimal('5000')
    }
    
    # Generate analysis
    analysis = engine.generate_portfolio_analysis(holdings, profile)
    
    print(f"Risk Score: {analysis.risk_score}")
    print(f"Mathematical Score: {analysis.mathematical_score}/100")
    print(f"Strategy: {analysis.target_allocation.strategy_name}")
    print(f"Rebalance Needed: {analysis.rebalance_needed}")
    
    if analysis.rebalance_trades:
        print("Recommended Trades:")
        for trade in analysis.rebalance_trades:
            print(f"  {trade['action']} ${trade['amount']} of {trade['asset_class']}")
    
    # Performance projection
    projector = PerformanceProjector()
    projection = projector.project_wealth_accumulation(
        Decimal('100000'),
        Decimal('2000'),
        AllocationStrategy.CONSERVATIVE_80_20,
        20
    )
    
    print(f"\n20-Year Projection:")
    print(f"Final Balance: ${projection['final_balance']}")
    print(f"Total Growth: ${projection['total_growth']}")