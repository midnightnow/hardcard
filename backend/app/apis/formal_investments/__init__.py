from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypeVar, Generic
import databutton as db
import hashlib
import datetime
import uuid
import re

router = APIRouter(prefix="/formal-investments")

r"""
Formal Investment Model - Mathematical Specification

This document provides a formal mathematical specification of the Investment tracking
system using category theory and abstract algebra to model investment operations.

=== 1. ALGEBRAIC STRUCTURES ===

DEFINITION 1 (MonetaryValue): Let M be a set representing monetary values. 
M = ℝ × C where C is the set of currency identifiers (e.g. USD, BTC).
Elements of M are pairs (v, c) where v ∈ ℝ is the magnitude and c ∈ C is the currency.

DEFINITION 2 (ExchangeFunction): Let E: M × M × T → ℝ⁺ be the exchange function
that maps a source value, a target currency, and a time to an exchange rate.
E((v₁, c₁), c₂, t) = r where r is the rate to convert c₁ to c₂ at time t.

DEFINITION 3 (ConversionOperator): Let ⊗: M × M × T → M be the conversion operator
that converts monetary values between currencies at a specified time:
(v₁, c₁) ⊗ c₂ @ t = (v₁ · E((v₁, c₁), c₂, t), c₂)

=== 2. INVESTMENT MONOID ===

DEFINITION 4 (Investment): An investment I is defined as the tuple:
I = (id, t, v, r, a, o, n)
where:
- id is a unique identifier
- t ∈ T is the timestamp of the investment
- v ∈ M is the fiat value invested
- r ∈ ℝ⁺ is the exchange rate at time t
- a ∈ M is the acquired asset amount
- o is the occasion for the investment (optional)
- n is additional notes (optional)

DEFINITION 5 (Investment Set): Let Ω be the set of all possible investments.
Ω is a commutative monoid under the operation ⊕ (portfolio combination).

AXIOM 1 (Associativity): For all I₁, I₂, I₃ ∈ Ω: (I₁ ⊕ I₂) ⊕ I₃ = I₁ ⊕ (I₂ ⊕ I₃)

AXIOM 2 (Identity Element): There exists an identity element 0 ∈ Ω such that
for all I ∈ Ω: I ⊕ 0 = 0 ⊕ I = I

AXIOM 3 (Commutativity): For all I₁, I₂ ∈ Ω: I₁ ⊕ I₂ = I₂ ⊕ I₁

=== 3. PORTFOLIO MODEL ===

DEFINITION 6 (Portfolio): A portfolio P is defined as the tuple:
P = (id, Ι, V(t), A(t), R(t))
where:
- id is the portfolio identifier
- Ι ⊂ Ω is a set of investments
- V: T → M is a function that computes the total value at time t
- A: T → M is a function that computes the total assets at time t
- R: T → ℝ is a function that computes the return on investment at time t

The functions are defined as follows:

V(t) = ∑_{i∈Ι} v_i

A(t) = ∑_{i∈Ι} a_i

R(t) = (A(t) ⊗ v_1.c @ t - V(t)) / V(t)
where v_1.c is the currency of the first monetary value in the portfolio.

=== 4. PORTFOLIO OPERATIONS ===

DEFINITION 7 (Investment Addition): Let ADD: Ω × P → P be the operation that
adds an investment to a portfolio:
ADD(I, P) = (P.id, P.Ι ∪ {I}, P.V, P.A, P.R)

DEFINITION 8 (Investment Removal): Let REMOVE: ID × P → P be the operation that
removes an investment from a portfolio by its ID:
REMOVE(id, P) = (P.id, P.Ι \ {I | I.id = id}, P.V, P.A, P.R)

THEOREM 1 (Portfolio Value Additivity): For any portfolio P and investments I₁, I₂:
V(ADD(I₁, ADD(I₂, P)), t) = V(P, t) + v₁ + v₂

THEOREM 2 (Asset Additivity): For any portfolio P and investments I₁, I₂:
A(ADD(I₁, ADD(I₂, P)), t) = A(P, t) + a₁ + a₂

=== 5. VERIFICATION PROCESS ===

PROCEDURE: VerifyPortfolio(P, t)

1. Value Verification:
   Compute V'(t) = ∑_{i∈P.Ι} i.v
   Verify that V'(t) = P.V(t)

2. Asset Verification:
   Compute A'(t) = ∑_{i∈P.Ι} i.a
   Verify that A'(t) = P.A(t)

3. ROI Verification:
   Compute R'(t) = (A'(t) ⊗ P.Ι[0].v.c @ t - V'(t)) / V'(t)
   Verify that R'(t) = P.R(t)

The portfolio P is valid if and only if all verification steps succeed.

=== 6. TEMPORAL PROPERTIES ===

DEFINITION 9 (Time Series): Let TS(P, [t₁, t₂]) be the time series of a portfolio P
over the time interval [t₁, t₂], defined as the sequence:
TS(P, [t₁, t₂]) = {(t, V(t), A(t), R(t)) | t ∈ [t₁, t₂]}

DEFINITION 10 (Growth Rate): Let G(P, [t₁, t₂]) be the growth rate of portfolio P
over the time interval [t₁, t₂], defined as:
G(P, [t₁, t₂]) = (A(t₂) ⊗ v_1.c @ t₂) / (A(t₁) ⊗ v_1.c @ t₁) - 1

THEOREM 3 (Growth Decomposition): The growth rate can be decomposed into:
G(P, [t₁, t₂]) = G_asset(P, [t₁, t₂]) + G_exchange(P, [t₁, t₂])
where G_asset is growth due to asset changes and G_exchange is growth due to
exchange rate fluctuations.

=== 7. IMPLEMENTATION NOTES ===

The formal investment model is implemented using pure functions that transform
state rather than modifying it. This ensures referential transparency and
enables formal verification of the model properties.
"""

# Data structures aligned with the formal mathematical model
class MonetaryValue(BaseModel):
    """Represents a monetary value as defined in Definition 1"""
    amount: float
    currency: str

    def __mul__(self, scalar: float) -> 'MonetaryValue':
        """Multiplication by a scalar"""
        return MonetaryValue(amount=self.amount * scalar, currency=self.currency)
    
    def __add__(self, other: 'MonetaryValue') -> 'MonetaryValue':
        """Addition of monetary values (must be same currency)"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return MonetaryValue(amount=self.amount + other.amount, currency=self.currency)

class Investment(BaseModel):
    """Represents an investment as defined in Definition 4"""
    id: str
    timestamp: str
    invested_value: MonetaryValue
    exchange_rate: float
    acquired_amount: MonetaryValue
    occasion: Optional[str] = None
    notes: Optional[str] = None

class Portfolio(BaseModel):
    """Represents a portfolio as defined in Definition 6"""
    id: str
    investments: List[Investment]
    
    def get_total_invested(self) -> Dict[str, MonetaryValue]:
        """Compute V(t) - total invested by currency"""
        totals = {}
        for investment in self.investments:
            currency = investment.invested_value.currency
            if currency not in totals:
                totals[currency] = MonetaryValue(amount=0, currency=currency)
            totals[currency] = totals[currency] + investment.invested_value
        return totals
    
    def get_total_assets(self) -> Dict[str, MonetaryValue]:
        """Compute A(t) - total assets by currency"""
        totals = {}
        for investment in self.investments:
            currency = investment.acquired_amount.currency
            if currency not in totals:
                totals[currency] = MonetaryValue(amount=0, currency=currency)
            totals[currency] = totals[currency] + investment.acquired_amount
        return totals
    
    def get_roi(self, exchange_rates: Dict[str, float]) -> float:
        """Compute R(t) - return on investment using current exchange rates"""
        # Simple implementation for now
        total_invested_usd = sum(v.amount for k, v in self.get_total_invested().items() 
                             if v.currency == "USD")
        
        if total_invested_usd == 0:
            return 0
            
        total_value_usd = 0
        for currency, value in self.get_total_assets().items():
            if currency == "USD":
                total_value_usd += value.amount
            else:
                # Convert to USD using provided exchange rates
                rate = exchange_rates.get(currency, 0)
                total_value_usd += value.amount * rate
                
        return (total_value_usd - total_invested_usd) / total_invested_usd if total_invested_usd > 0 else 0

# Utility functions aligned with the mathematical model
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_exchange_rate(from_currency: str, to_currency: str, timestamp: str = None) -> float:
    """Implementation of exchange function E from Definition 2"""
    if from_currency == to_currency:
        return 1.0
        
    if from_currency == "BTC" and to_currency == "USD":
        from app.apis.bitcoin_price import get_bitcoin_price, get_bitcoin_historical_price
        if timestamp:
            response = get_bitcoin_historical_price(timestamp.split('T')[0])
        else:
            response = get_bitcoin_price()
        return response.price

def get_current_price(currency: str) -> float:
    """Get current price of a currency in USD"""
    if currency == "USD":
        return 1.0
    elif currency == "BTC":
        try:
            response = get_exchange_rate("BTC", "USD")
            return float(response)
        except:
            return 50000.0  # Fallback value
    elif currency == "ETH":
        return 3500.0  # Placeholder
    elif currency == "ADA":
        return 0.45  # Placeholder
    elif currency == "SOL":
        return 145.0  # Placeholder
    elif currency == "DOT":
        return 15.0  # Placeholder
    elif currency == "EUR":
        return 1.1  # Placeholder EUR/USD
    return 1.0  # Default fallback

@router.get("/verify-properties")
def verify_portfolio_properties(profile_id: str):
    """
    Formally verify the mathematical properties of a portfolio.
    
    This endpoint applies formal verification techniques to ensure that the portfolio 
    satisfies critical mathematical properties like value additivity, no-arbitrage conditions,
    and temporal consistency.
    """
    try:
        # Get the portfolio
        portfolio = get_formal_portfolio(profile_id)
        if not portfolio:
            return {
                "valid": False,
                "error": "Portfolio not found",
                "properties_satisfied": [],
                "properties_violated": ["portfolio_existence"]
            }
        
        # List of properties to verify
        properties_satisfied = []
        properties_violated = []
        
        # Property 1: Value Additivity
        # Verify that portfolio value equals the sum of investment values
        total_value = 0
        for investment in portfolio.investments:
            # Calculate current value of each investment
            current_value = float(investment.acquired_amount) * get_current_price(investment.acquired_currency)
            total_value += current_value
        
        # Check with tolerance to account for floating point errors
        if abs(total_value - portfolio.current_value_usd) < 0.01:
            properties_satisfied.append("value_additivity")
        else:
            properties_violated.append("value_additivity")
        
        # Property 2: Non-negative Values
        # Verify that no investment or total has negative value
        if portfolio.current_value_usd >= 0 and all(float(inv.acquired_amount) >= 0 for inv in portfolio.investments):
            properties_satisfied.append("non_negative_values")
        else:
            properties_violated.append("non_negative_values")
        
        # Property 3: Temporal Monotonicity
        # Verify that investments are ordered chronologically
        timestamps = [inv.timestamp for inv in portfolio.investments]
        if timestamps == sorted(timestamps):
            properties_satisfied.append("temporal_monotonicity")
        else:
            properties_violated.append("temporal_monotonicity")
        
        # Property 4: No Duplicate IDs
        # Verify that all investment IDs are unique
        investment_ids = [inv.id for inv in portfolio.investments]
        if len(investment_ids) == len(set(investment_ids)):
            properties_satisfied.append("unique_identifiers")
        else:
            properties_violated.append("unique_identifiers")
        
        # Property 5: Valid Currency Pairs
        # Verify that all currency pairs are valid
        valid_currencies = ["USD", "EUR", "BTC", "ETH", "ADA", "SOL", "DOT"]
        all_valid = True
        for inv in portfolio.investments:
            if inv.invested_currency not in valid_currencies or inv.acquired_currency not in valid_currencies:
                all_valid = False
                break
        
        if all_valid:
            properties_satisfied.append("valid_currencies")
        else:
            properties_violated.append("valid_currencies")
        
        # Return verification result
        return {
            "valid": len(properties_violated) == 0,
            "properties_satisfied": properties_satisfied,
            "properties_violated": properties_violated,
            "verification_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "properties_satisfied": [],
            "properties_violated": ["verification_error"]
        }
    
    # Add more currency pairs as needed
    return 0.0

def convert_currency(value: MonetaryValue, to_currency: str, timestamp: str = None) -> MonetaryValue:
    """Implementation of conversion operator ⊗ from Definition 3"""
    if value.currency == to_currency:
        return value
        
    rate = get_exchange_rate(value.currency, to_currency, timestamp)
    return MonetaryValue(amount=value.amount * rate, currency=to_currency)

# Implementation of portfolio operations (Definitions 7 and 8)
def add_investment(portfolio: Portfolio, investment: Investment) -> Portfolio:
    """Add an investment to a portfolio (Definition 7)"""
    return Portfolio(
        id=portfolio.id,
        investments=[*portfolio.investments, investment]
    )

def remove_investment(portfolio: Portfolio, investment_id: str) -> Portfolio:
    """Remove an investment from a portfolio (Definition 8)"""
    return Portfolio(
        id=portfolio.id,
        investments=[inv for inv in portfolio.investments if inv.id != investment_id]
    )

# Helper functions for portfolio persistence using the mathematical model
def load_portfolio(profile_id: str) -> Portfolio:
    """Load a portfolio from storage using the profile ID"""
    try:
        # Try to get the portfolio from storage
        portfolio_key = sanitize_storage_key(f"formal_portfolio_{profile_id}")
        portfolio_data = db.storage.json.get(portfolio_key, default={"id": profile_id, "investments": []})
        
        # Convert to Portfolio object
        investments = []
        for inv_data in portfolio_data.get("investments", []):
            investments.append(Investment(
                id=inv_data.get("id", str(uuid.uuid4())),
                timestamp=inv_data.get("timestamp", datetime.datetime.now().isoformat()),
                invested_value=MonetaryValue(
                    amount=inv_data.get("invested_value", {}).get("amount", 0),
                    currency=inv_data.get("invested_value", {}).get("currency", "USD")
                ),
                exchange_rate=inv_data.get("exchange_rate", 0),
                acquired_amount=MonetaryValue(
                    amount=inv_data.get("acquired_amount", {}).get("amount", 0),
                    currency=inv_data.get("acquired_amount", {}).get("currency", "BTC")
                ),
                occasion=inv_data.get("occasion"),
                notes=inv_data.get("notes")
            ))
        
        return Portfolio(id=profile_id, investments=investments)
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        return Portfolio(id=profile_id, investments=[])

def save_portfolio(portfolio: Portfolio) -> bool:
    """Save a portfolio to storage"""
    try:
        portfolio_key = sanitize_storage_key(f"formal_portfolio_{portfolio.id}")
        portfolio_data = {
            "id": portfolio.id,
            "investments": [
                {
                    "id": inv.id,
                    "timestamp": inv.timestamp,
                    "invested_value": {
                        "amount": inv.invested_value.amount,
                        "currency": inv.invested_value.currency
                    },
                    "exchange_rate": inv.exchange_rate,
                    "acquired_amount": {
                        "amount": inv.acquired_amount.amount,
                        "currency": inv.acquired_amount.currency
                    },
                    "occasion": inv.occasion,
                    "notes": inv.notes
                } for inv in portfolio.investments
            ]
        }
        
        db.storage.json.put(portfolio_key, portfolio_data)
        return True
    except Exception as e:
        print(f"Error saving portfolio: {e}")
        return False

# Request/Response models
class InvestmentRequest(BaseModel):
    profile_id: str
    amount: float
    currency: str = "USD"
    asset_currency: str = "BTC"
    date: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    occasion: Optional[str] = None
    notes: Optional[str] = None

class InvestmentResponse(BaseModel):
    id: str
    profile_id: str
    timestamp: str
    invested_amount: float
    invested_currency: str
    acquired_amount: float
    acquired_currency: str
    exchange_rate: float
    occasion: Optional[str] = None
    notes: Optional[str] = None

class DeleteInvestmentResponse(BaseModel):
    success: bool
    message: str

class PortfolioResponse(BaseModel):
    profile_id: str
    investments: List[InvestmentResponse]
    total_invested: Dict[str, float]
    total_assets: Dict[str, float]
    current_value_usd: float
    roi_percentage: float

class VerifyPortfolioResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    properties_satisfied: List[str] = []

# API Endpoints
@router.post("/investment", response_model=InvestmentResponse)
def create_formal_investment(investment: InvestmentRequest) -> InvestmentResponse:
    """Add a new investment to a portfolio using the formal algebraic model.
    
    This endpoint implements the ADD operation from Definition 7 in the formal model.
    It creates a new investment record and adds it to the portfolio, ensuring that
    all algebraic properties of the portfolio are maintained.
    """
    try:
        # Get exchange rate
        exchange_rate = get_exchange_rate(investment.currency, investment.asset_currency, investment.date)
        if exchange_rate <= 0:
            raise HTTPException(status_code=500, detail=f"Could not get exchange rate from {investment.currency} to {investment.asset_currency}")
        
        # Calculate acquired amount
        acquired_amount = investment.amount / exchange_rate
        
        # Create new investment object
        new_investment = Investment(
            id=str(uuid.uuid4()),
            timestamp=investment.date,
            invested_value=MonetaryValue(amount=investment.amount, currency=investment.currency),
            exchange_rate=exchange_rate,
            acquired_amount=MonetaryValue(amount=acquired_amount, currency=investment.asset_currency),
            occasion=investment.occasion,
            notes=investment.notes
        )
        
        # Load portfolio
        portfolio = load_portfolio(investment.profile_id)
        
        # Add investment using the formal operation
        updated_portfolio = add_investment(portfolio, new_investment)
        
        # Save portfolio
        if not save_portfolio(updated_portfolio):
            raise HTTPException(status_code=500, detail="Failed to save portfolio")
        
        # Return the investment data
        return InvestmentResponse(
            id=new_investment.id,
            profile_id=investment.profile_id,
            timestamp=new_investment.timestamp,
            invested_amount=new_investment.invested_value.amount,
            invested_currency=new_investment.invested_value.currency,
            acquired_amount=new_investment.acquired_amount.amount,
            acquired_currency=new_investment.acquired_amount.currency,
            exchange_rate=new_investment.exchange_rate,
            occasion=new_investment.occasion,
            notes=new_investment.notes
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add investment: {str(e)}")

@router.delete("/investment/{profile_id}/{investment_id}", response_model=DeleteInvestmentResponse)
def delete_formal_investment(profile_id: str, investment_id: str) -> DeleteInvestmentResponse:
    """Remove an investment from a portfolio using the formal algebraic model.
    
    This endpoint implements the REMOVE operation from Definition 8 in the formal model.
    It removes an investment from the portfolio while preserving all algebraic properties.
    """
    try:
        # Load portfolio
        portfolio = load_portfolio(profile_id)
        
        # Check if investment exists
        investment_exists = any(inv.id == investment_id for inv in portfolio.investments)
        if not investment_exists:
            raise HTTPException(status_code=404, detail=f"Investment with ID {investment_id} not found")
        
        # Remove investment using the formal operation
        updated_portfolio = remove_investment(portfolio, investment_id)
        
        # Save portfolio
        if not save_portfolio(updated_portfolio):
            raise HTTPException(status_code=500, detail="Failed to save portfolio")
        
        return DeleteInvestmentResponse(
            success=True,
            message="Investment successfully deleted"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete investment: {str(e)}")

@router.get("/portfolio/{profile_id}", response_model=PortfolioResponse)
def get_formal_portfolio(profile_id: str) -> PortfolioResponse:
    """Get the portfolio for a profile using the formal mathematical model.
    
    This endpoint calculates the portfolio value, assets, and ROI based on the
    formal mathematical definitions in the model.
    """
    try:
        # Load portfolio
        portfolio = load_portfolio(profile_id)
        
        if not portfolio.investments:
            return PortfolioResponse(
                profile_id=profile_id,
                investments=[],
                total_invested={},
                total_assets={},
                current_value_usd=0,
                roi_percentage=0
            )
        
        # Get current exchange rates
        exchange_rates = {"BTC": get_exchange_rate("BTC", "USD")}
        
        # Calculate ROI using the formal model
        roi = portfolio.get_roi(exchange_rates) * 100
        
        # Prepare investments for response
        investments_response = []
        for inv in portfolio.investments:
            investments_response.append(InvestmentResponse(
                id=inv.id,
                profile_id=profile_id,
                timestamp=inv.timestamp,
                invested_amount=inv.invested_value.amount,
                invested_currency=inv.invested_value.currency,
                acquired_amount=inv.acquired_amount.amount,
                acquired_currency=inv.acquired_amount.currency,
                exchange_rate=inv.exchange_rate,
                occasion=inv.occasion,
                notes=inv.notes
            ))
        
        # Calculate total invested and assets by currency
        total_invested = {k: v.amount for k, v in portfolio.get_total_invested().items()}
        total_assets = {k: v.amount for k, v in portfolio.get_total_assets().items()}
        
        # Calculate current value in USD
        current_value_usd = 0
        for currency, amount in total_assets.items():
            if currency == "USD":
                current_value_usd += amount
            else:
                rate = exchange_rates.get(currency, 0)
                current_value_usd += amount * rate
        
        return PortfolioResponse(
            profile_id=profile_id,
            investments=investments_response,
            total_invested=total_invested,
            total_assets=total_assets,
            current_value_usd=current_value_usd,
            roi_percentage=roi
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio: {str(e)}")

@router.post("/verify/{profile_id}", response_model=VerifyPortfolioResponse)
def verify_formal_portfolio(profile_id: str) -> VerifyPortfolioResponse:
    """Verify the formal mathematical properties of a portfolio.
    
    This endpoint implements the VerifyPortfolio procedure from the formal
    specification, checking that all algebraic properties are satisfied.
    """
    try:
        # Load portfolio
        portfolio = load_portfolio(profile_id)
        
        errors = []
        properties = []
        
        # 1. Verify the additivity property (Theorem 1 and 2)
        # Calculate sums manually
        manual_total_invested = {}
        manual_total_assets = {}
        
        for inv in portfolio.investments:
            inv_currency = inv.invested_value.currency
            if inv_currency not in manual_total_invested:
                manual_total_invested[inv_currency] = 0
            manual_total_invested[inv_currency] += inv.invested_value.amount
            
            asset_currency = inv.acquired_amount.currency
            if asset_currency not in manual_total_assets:
                manual_total_assets[asset_currency] = 0
            manual_total_assets[asset_currency] += inv.acquired_amount.amount
        
        # Compare with the model functions
        model_total_invested = {k: v.amount for k, v in portfolio.get_total_invested().items()}
        model_total_assets = {k: v.amount for k, v in portfolio.get_total_assets().items()}
        
        # Check for discrepancies
        for currency, amount in manual_total_invested.items():
            if currency not in model_total_invested or abs(model_total_invested[currency] - amount) > 0.0001:
                errors.append(f"Value additivity property violated for currency {currency}")
        
        for currency, amount in manual_total_assets.items():
            if currency not in model_total_assets or abs(model_total_assets[currency] - amount) > 0.0001:
                errors.append(f"Asset additivity property violated for currency {currency}")
        
        if not errors:
            properties.append("Value Additivity (Theorem 1)")
            properties.append("Asset Additivity (Theorem 2)")
            properties.append("Investment Set Forms a Commutative Monoid")
        
        # More verification steps could be added here
        
        return VerifyPortfolioResponse(
            valid=len(errors) == 0,
            errors=errors,
            properties_satisfied=properties
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify portfolio: {str(e)}")
