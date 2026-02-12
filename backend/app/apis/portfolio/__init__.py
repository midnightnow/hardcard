# This API is deprecated in favor of bitcoin_price and bitcoin_tracker
# Keeping for backward compatibility but will be removed in the future

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import databutton as db
import uuid
import datetime
import json

# Import the better implementations
from app.apis.bitcoin_tracker import get_portfolio as get_bitcoin_portfolio
from app.apis.bitcoin_tracker import add_investment as add_bitcoin_investment
from app.apis.bitcoin_tracker import BitcoinInvestmentRequest

router = APIRouter()

# Models
class Investment(BaseModel):
    id: str
    profile_id: str
    amount_usd: float
    bitcoin_price_at_purchase: float
    bitcoin_amount: float
    date: str
    occasion: Optional[str] = None
    notes: Optional[str] = None

class InvestmentCreate(BaseModel):
    profile_id: str
    amount_usd: float
    bitcoin_price_at_purchase: float
    date: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    occasion: Optional[str] = None
    notes: Optional[str] = None

class Portfolio(BaseModel):
    profile_id: str
    investments: List[Investment]
    total_invested_usd: float
    total_bitcoin: float
    current_value_usd: Optional[float] = None

# Endpoints - These are now just wrappers for the bitcoin_tracker API
@router.post("/investment")
def create_legacy_investment(investment: InvestmentCreate) -> Investment:
    """Add a new Bitcoin investment for a profile (Legacy API)"""
    try:
        # Forward to the bitcoin_tracker API
        result = add_bitcoin_investment(
            profile_id=investment.profile_id,
            investment=BitcoinInvestmentRequest(
                date=investment.date,
                amount_usd=investment.amount_usd,
                occasion=investment.occasion or "Investment",
                notes=investment.notes
            )
        )
        
        # Map the response to the legacy format
        return Investment(
            id=str(uuid.uuid4()),
            profile_id=investment.profile_id,
            amount_usd=investment.amount_usd,
            bitcoin_price_at_purchase=investment.bitcoin_price_at_purchase,
            bitcoin_amount=result.btc_amount,
            date=investment.date,
            occasion=investment.occasion,
            notes=investment.notes
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add investment: {str(e)}")

@router.get("/portfolio/{profile_id}")
def get_legacy_portfolio(profile_id: str) -> Portfolio:
    """Get the investment portfolio for a profile (Legacy API)"""
    try:
        # Forward to the bitcoin_tracker API
        result = get_bitcoin_portfolio(profile_id=profile_id)
        
        # Map the response to the legacy format
        investments = []
        for inv in result.investments:
            investments.append(Investment(
                id=inv.get("id", str(uuid.uuid4())),
                profile_id=profile_id,
                amount_usd=inv["amount_usd"],
                bitcoin_price_at_purchase=inv["btc_price"],
                bitcoin_amount=inv["btc_amount"],
                date=inv["date"],
                occasion=inv.get("occasion", "Investment"),
                notes=inv.get("notes")
            ))
        
        return Portfolio(
            profile_id=profile_id,
            investments=investments,
            total_invested_usd=result.total_invested_usd,
            total_bitcoin=result.total_btc_amount,
            current_value_usd=result.current_value_usd
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio: {str(e)}")