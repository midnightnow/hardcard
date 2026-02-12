from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import requests
import databutton as db
from datetime import datetime, timedelta
import json
import random
import re
import uuid

# Import the improved Bitcoin price API functions
from app.apis.bitcoin_price import get_bitcoin_price, get_bitcoin_historical_price

# Import the formal investment model APIs for mathematical rigor
from app.apis.formal_investments import create_formal_investment, delete_formal_investment, get_formal_portfolio, verify_formal_portfolio
from app.apis.formal_investments import InvestmentRequest, InvestmentResponse, PortfolioResponse as FormalPortfolioResponse, VerifyPortfolioResponse

router = APIRouter()

class BitcoinInvestmentRequest(BaseModel):
    date: str
    amount_usd: float
    occasion: str = "Investment"
    notes: str = None

class BitcoinInvestmentResponse(BaseModel):
    date: str
    amount_usd: float
    btc_amount: float
    current_value: float
    id: str

class BitcoinPortfolioResponse(BaseModel):
    investments: list[dict]
    total_invested_usd: float
    total_btc_amount: float
    current_value_usd: float
    roi_percentage: float

class DeleteInvestmentResponse(BaseModel):
    success: bool
    message: str

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def save_investment(profile_id, investment_data):
    """Save a Bitcoin investment to storage"""
    try:
        # Get existing investments or create empty list
        investments_key = sanitize_storage_key(f"bitcoin_investments_{profile_id}")
        try:
            investments = db.storage.json.get(investments_key, default=[])
        except:
            investments = []
        
        # Add new investment
        investments.append(investment_data)
        
        # Save back to storage
        db.storage.json.put(investments_key, investments)
        
        return True
    except Exception as e:
        print(f"Error saving investment: {e}")
        return False

def get_investments(profile_id):
    """Get all Bitcoin investments for a profile
    
    For backward compatibility, this now pulls from the formal investment model
    and formats the data to match the legacy structure.
    """
    try:
        # Use the formal portfolio for retrieving investments
        formal_portfolio = get_formal_portfolio(profile_id)
        
        # Convert formal investments to legacy format
        legacy_investments = []
        for inv in formal_portfolio.investments:
            # Only include BTC investments
            if inv.acquired_currency != "BTC":
                continue
                
            # Format date for consistency
            date = inv.timestamp.split('T')[0] if 'T' in inv.timestamp else inv.timestamp
            
            legacy_investments.append({
                "id": inv.id,
                "date": date,
                "amount_usd": inv.invested_amount,
                "btc_price": inv.exchange_rate,
                "btc_amount": inv.acquired_amount,
                "occasion": inv.occasion or "Investment",
                "notes": inv.notes,
                "timestamp": inv.timestamp
            })
            
        return legacy_investments
    except:
        return []

@router.post("/bitcoin/investments/{profile_id}")
def add_investment(profile_id: str, investment: BitcoinInvestmentRequest) -> BitcoinInvestmentResponse:
    """Add a new Bitcoin investment to a family member's portfolio.
    
    Creates a new Bitcoin investment record for a specified family profile, calculating
    the equivalent BTC amount based on the Bitcoin price on the investment date.
    This is a core function of the Legacy Vault system, allowing long-term tracking
    of Bitcoin investments for children and family members.
    
    This implementation is now backed by the formal mathematical model from the
    formal_investments API, ensuring mathematical rigor and formal verification.
    
    Args:
        profile_id (str): The unique identifier of the family profile
        investment (BitcoinInvestmentRequest): The investment details including:
            - date: Investment date in YYYY-MM-DD format
            - amount_usd: Amount invested in USD
            - occasion: Reason for investment (e.g., "Birthday", "Holiday")
            - notes: Additional notes about the investment
            
    Returns:
        BitcoinInvestmentResponse: Details of the created investment including:
            - date: Investment date
            - amount_usd: Amount invested in USD
            - btc_amount: Amount of Bitcoin purchased
            - current_value: Current USD value of the Bitcoin
            - id: Unique identifier for the investment
            
    Raises:
        HTTPException: 500 error if historical Bitcoin price cannot be retrieved
        HTTPException: 500 error if investment cannot be saved
    """
    try:
        # Get Bitcoin price on the investment date for reference
        try:
            btc_price_response = get_bitcoin_historical_price(investment.date)
            btc_price = btc_price_response.price
        except Exception as e:
            print(f"Error getting historical price: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get Bitcoin price for {investment.date}")
            
        # Use the formal investment model for mathematical precision and verification
        formal_request = InvestmentRequest(
            profile_id=profile_id,
            amount=investment.amount_usd,
            currency="USD",
            asset_currency="BTC",
            date=investment.date,
            occasion=investment.occasion,
            notes=investment.notes
        )
        
        # Use the formal API to create the investment
        formal_response = create_formal_investment(formal_request)
        
        # For backward compatibility, compute the current value
        current_price_response = get_bitcoin_price()
        current_price = current_price_response.price
        current_value = formal_response.acquired_amount * current_price
        
        # Legacy format response for backward compatibility
        return BitcoinInvestmentResponse(
            date=formal_response.timestamp.split('T')[0] if 'T' in formal_response.timestamp else formal_response.timestamp,
            amount_usd=formal_response.invested_amount,
            btc_amount=formal_response.acquired_amount,
            current_value=current_value,
            id=formal_response.id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error adding investment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add investment: {str(e)}")

@router.delete("/bitcoin/investments/{profile_id}/{investment_id}")
def delete_investment(profile_id: str, investment_id: str) -> DeleteInvestmentResponse:
    """Delete a Bitcoin investment from a family member's portfolio.
    
    Removes a specific Bitcoin investment record from a family member's portfolio.
    This is useful for correcting errors or removing test data in the Legacy Vault system.
    
    This implementation is now backed by the formal mathematical model from the
    formal_investments API, ensuring mathematical rigor and formal verification.
    
    Args:
        profile_id (str): The unique identifier of the family profile
        investment_id (str): The unique identifier of the investment to delete
        
    Returns:
        DeleteInvestmentResponse: Object confirming successful deletion
            - success: Boolean indicating success
            - message: Description of the action taken
            
    Raises:
        HTTPException: 404 error if the investment with the specified ID is not found
        HTTPException: 500 error if the deletion operation fails
    """
    try:
        # Use the formal investment deletion for mathematical precision
        formal_response = delete_formal_investment(profile_id, investment_id)
        
        # Legacy response format for backward compatibility
        return DeleteInvestmentResponse(
            success=formal_response.success,
            message=formal_response.message
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error deleting investment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete investment: {str(e)}")

@router.get("/bitcoin/portfolio/{profile_id}")
def get_portfolio(profile_id: str) -> BitcoinPortfolioResponse:
    """Get the complete Bitcoin investment portfolio for a family member.
    
    Retrieves all Bitcoin investments for a specified family profile and calculates
    current values, total portfolio worth, and return on investment metrics. This endpoint
    is essential for tracking the growth of investments over time in the Legacy Vault system.
    
    This implementation is now backed by the formal mathematical model from the
    formal_investments API, ensuring mathematical rigor and formal verification.
    
    The portfolio includes detailed information about each investment including purchase date,
    amount invested, Bitcoin amount, current value, and ROI percentage. It also provides
    aggregate statistics for the entire portfolio.
    
    Args:
        profile_id (str): The unique identifier of the family profile
        
    Returns:
        BitcoinPortfolioResponse: Complete portfolio information including:
            - investments: List of all investments with current values
            - total_invested_usd: Total USD amount invested
            - total_btc_amount: Total Bitcoin owned
            - current_value_usd: Current total portfolio value in USD
            - roi_percentage: Overall return on investment percentage
            
    Raises:
        HTTPException: 500 error if the portfolio cannot be retrieved
        
    Note:
        Returns empty portfolio with zero values if no investments exist for the profile.
    """
    try:
        # Use the formal portfolio for mathematical precision
        formal_portfolio = get_formal_portfolio(profile_id)
        
        # For empty portfolios, return zero values
        if not formal_portfolio.investments:
            return BitcoinPortfolioResponse(
                investments=[],
                total_invested_usd=0,
                total_btc_amount=0,
                current_value_usd=0,
                roi_percentage=0
            )
        
        # Process investments for legacy format
        enhanced_investments = []
        total_btc_amount = 0
        
        for inv in formal_portfolio.investments:
            # Only include BTC investments
            if inv.acquired_currency != "BTC":
                continue
                
            # Format date for consistency
            date = inv.timestamp.split('T')[0] if 'T' in inv.timestamp else inv.timestamp
            
            # Calculate ROI for this investment
            investment_roi = ((inv.current_value - inv.invested_amount) / inv.invested_amount) * 100 if inv.invested_amount > 0 else 0
            
            # Track total BTC
            total_btc_amount += inv.acquired_amount
            
            # Create legacy format investment
            enhanced_investments.append({
                "id": inv.id,
                "date": date,
                "amount_usd": inv.invested_amount,
                "btc_price": inv.exchange_rate,
                "btc_amount": inv.acquired_amount,
                "occasion": inv.occasion or "Investment",
                "notes": inv.notes,
                "current_value": inv.current_value,
                "roi_percentage": investment_roi
            })
        
        # Build the response with the formal portfolio data
        return BitcoinPortfolioResponse(
            investments=enhanced_investments,
            total_invested_usd=formal_portfolio.total_invested.get("USD", 0),
            total_btc_amount=formal_portfolio.total_assets.get("BTC", 0),
            current_value_usd=formal_portfolio.current_value_usd,
            roi_percentage=formal_portfolio.roi_percentage
        )
    except Exception as e:
        print(f"Error retrieving portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve portfolio: {str(e)}")