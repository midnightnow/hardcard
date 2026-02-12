from fastapi import APIRouter, Depends
from pydantic import BaseModel
import databutton as db
import numpy as np
import math
import json
import time
import datetime
from typing import List, Dict, Any, Optional
from app.auth import AuthorizedUser

# Initialize router
router = APIRouter(prefix="/bitcoin-hyperspace")

# Model definitions
class BitcoinInvestment(BaseModel):
    """A Bitcoin investment data point for hyperspace visualization"""
    id: str
    timestamp: float  # Unix timestamp
    amount_btc: float  # Amount in BTC
    amount_usd: float  # Amount in USD at time of investment
    current_value_usd: Optional[float] = None  # Current value in USD
    label: Optional[str] = None
    notes: Optional[str] = None

class HyperspacePosition(BaseModel):
    """Position in hyperspace for a Bitcoin investment"""
    x: float
    y: float
    z: float
    time: float
    investment_id: str
    amount_btc: float
    amount_usd: float
    current_value_usd: Optional[float] = None
    growth_percentage: Optional[float] = None
    label: Optional[str] = None

class BitcoinHyperspaceResponse(BaseModel):
    """Response with hyperspace data for Bitcoin investments"""
    positions: List[HyperspacePosition]
    total_btc: float
    total_initial_usd: float
    total_current_usd: Optional[float] = None
    total_growth_percentage: Optional[float] = None

# Utility Functions for Hyperspace Transformations
def calculate_spiral_position(time_value: float, turns_per_log_unit: float = 1.0, 
                              pitch: float = 1.0, initial_radius: float = 1.0) -> Dict[str, float]:
    """
    Calculate the position on a logarithmic spiral in 3D space based on time.
    The spiral starts at (initial_radius, 0, 0) and grows exponentially.
    
    Args:
        time_value: The time value (t ≥ 1, where t=1 is the origin)
        turns_per_log_unit: How many turns per logarithmic unit
        pitch: The vertical pitch of the spiral
        initial_radius: The initial radius at t=1
    
    Returns:
        Dictionary with x, y, z coordinates
    """
    # Safety checks
    if time_value <= 0:
        time_value = 1.0  # Minimum allowed time
    
    # Convert to logarithmic scale (with t=1 as the origin)
    log_time = math.log(time_value)
    
    # Calculate angle based on logarithmic time and turns_per_log_unit
    theta = log_time * turns_per_log_unit * 2 * math.pi
    
    # Calculate radius based on exponential growth
    radius = initial_radius * math.exp(log_time)
    
    # Calculate 3D coordinates
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    z = log_time * pitch  # Height increases with log of time
    
    return {
        "x": x,
        "y": y,
        "z": z,
        "t": time_value
    }

def get_bitcoin_investments() -> List[BitcoinInvestment]:
    """
    Retrieve Bitcoin investments from storage or create sample data if none exists
    """
    # Define the storage key - matching the one used in hyperspace_bitcoin API
    BITCOIN_INVESTMENTS_KEY = "hyperspace_bitcoin_investments"
    
    try:
        # Try to load existing data
        investments_json = db.storage.json.get(BITCOIN_INVESTMENTS_KEY, default=None)
        if investments_json:
            # Convert to BitcoinInvestment objects with field mapping
            bitcoin_investments = []
            for inv in investments_json:
                # Convert date string to timestamp
                if "date" in inv and "timestamp" not in inv:
                    date_str = inv["date"]
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    timestamp = datetime.datetime.combine(date_obj, datetime.time.min).timestamp()
                    inv["timestamp"] = timestamp
                
                # Map btc_amount to amount_btc if needed
                if "btc_amount" in inv and "amount_btc" not in inv:
                    inv["amount_btc"] = inv["btc_amount"]
                
                # Create BitcoinInvestment object
                try:
                    bitcoin_investments.append(BitcoinInvestment(**inv))
                except Exception as e:
                    print(f"Error converting investment: {e}\nData: {inv}")
            
            return bitcoin_investments
    except Exception as e:
        print(f"Error loading Bitcoin investments: {e}")
    
    # If we reach here, either there's no data or there was an error
    # Return empty list - the front end can handle this case
    return []

@router.get("/investments", response_model=List[BitcoinInvestment], operation_id="get_bitcoin_hyperspace_investments_list")
def get_bitcoin_hyperspace_investments(user: AuthorizedUser):
    """Get all Bitcoin investments for the current user"""
    return get_bitcoin_investments()

@router.get("/data", operation_id="get_bitcoin_hyperspace_coordinates")
def get_bitcoin_hyperspace_coordinates(user: AuthorizedUser,
                               turns_per_log_unit: float = 1.0,
                               pitch: float = 1.0,
                               initial_radius: float = 1.0):
    """Get Bitcoin investment data mapped to hyperspace coordinates"""
    # Get all investments
    investments = get_bitcoin_investments()
    
    # Initialize response
    total_btc = 0
    total_initial_usd = 0
    total_current_usd = 0
    positions = []
    
    # Process each investment and map to hyperspace
    for inv in investments:
        # Calculate position in hyperspace based on timestamp
        # Convert Unix timestamp to "hyperspace time"
        # We use seconds since Jan 1, 2009 (Bitcoin genesis) divided by seconds in a year
        # This gives us a "year since Bitcoin" value
        genesis_timestamp = 1230768000  # Jan 1, 2009 timestamp
        seconds_per_year = 31536000
        years_since_genesis = (inv.timestamp - genesis_timestamp) / seconds_per_year
        
        # Ensure time is positive (minimum 0.1 years)
        hyperspace_time = max(0.1, years_since_genesis)
        
        # Calculate 3D position
        position = calculate_spiral_position(
            hyperspace_time,
            turns_per_log_unit=turns_per_log_unit,
            pitch=pitch,
            initial_radius=initial_radius
        )
        
        # Calculate growth if we have current value
        growth_percentage = None
        if inv.current_value_usd and inv.amount_usd > 0:
            growth_percentage = ((inv.current_value_usd - inv.amount_usd) / inv.amount_usd) * 100
        
        # Add to positions list
        positions.append(HyperspacePosition(
            x=position["x"],
            y=position["y"],
            z=position["z"],
            time=hyperspace_time,
            investment_id=inv.id,
            amount_btc=inv.amount_btc,
            amount_usd=inv.amount_usd,
            current_value_usd=inv.current_value_usd,
            growth_percentage=growth_percentage,
            label=inv.label or f"₿{inv.amount_btc:.4f}"
        ))
        
        # Update totals
        total_btc += inv.amount_btc
        total_initial_usd += inv.amount_usd
        if inv.current_value_usd:
            total_current_usd += inv.current_value_usd
    
    # Calculate total growth percentage
    total_growth_percentage = None
    if total_initial_usd > 0 and total_current_usd > 0:
        total_growth_percentage = ((total_current_usd - total_initial_usd) / total_initial_usd) * 100
    
    # Return the response
    return BitcoinHyperspaceResponse(
        positions=positions,
        total_btc=total_btc,
        total_initial_usd=total_initial_usd,
        total_current_usd=total_current_usd,
        total_growth_percentage=total_growth_percentage
    )

@router.get("/documentation", response_model=Dict[str, Any], operation_id="get_bitcoin_hyperspace_documentation_endpoint")
def get_bitcoin_hyperspace_documentation_endpoint():
    """Get documentation for the Bitcoin Hyperspace integration"""
    return {
        "title": "Bitcoin Hyperspace Integration",
        "description": "Maps Bitcoin investments to the Hardcard Hyperspace using logarithmic spiral mathematics.",
        "mathematical_model": {
            "spiral_equation": "r(θ) = e^{θ} with r(0)=1",
            "time_mapping": "τₙ = t₀ + n·Δt, where Δt = 1 year = 31,536,000 seconds",
            "hyperspace_coordinates": {
                "x": "radius * cos(theta)",
                "y": "radius * sin(theta)",
                "z": "log_time * pitch"
            },
            "parameters": {
                "turns_per_log_unit": "Controls how many spiral turns per logarithmic unit of time",
                "pitch": "Controls the vertical growth rate of the spiral",
                "initial_radius": "The starting radius at t=1 (origin)"
            }
        },
        "usage": {
            "get_investments": {
                "endpoint": "/bitcoin-hyperspace/investments",
                "description": "Returns all Bitcoin investments"
            },
            "get_hyperspace_data": {
                "endpoint": "/bitcoin-hyperspace/data",
                "description": "Returns Bitcoin investments mapped to hyperspace coordinates",
                "parameters": {
                    "turns_per_log_unit": "Default 1.0",
                    "pitch": "Default 1.0",
                    "initial_radius": "Default 1.0"
                }
            }
        },
        "visualization_tips": [
            "The origin (t=1) represents the Bitcoin genesis block",
            "Investments are positioned based on their timestamp relative to Bitcoin genesis",
            "Growth is visualized through color intensity and point size",
            "The spiral's growth represents the exponential potential of Bitcoin over time"
        ]
    }
