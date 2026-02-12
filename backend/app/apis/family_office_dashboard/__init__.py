from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import databutton as db
import json
import re

router = APIRouter()

# Models
class TrusteeData(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    role: str = "Trustee"
    created_at: Optional[datetime] = None

class PortfolioData(BaseModel):
    trustee_id: str
    real_estate: float
    infrastructure: float
    equities: float
    crypto: float
    precious_metals: float
    solar_systems: float
    bunkers: float
    updated_at: Optional[datetime] = None

class InvestmentData(BaseModel):
    trustee_id: str
    roi: float
    yearly_growth: List[Dict[str, float]]
    allocation: Dict[str, float]
    risk_level: str
    updated_at: Optional[datetime] = None

# Utility function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Routes
@router.get("/trustee/{trustee_id}", response_model=TrusteeData)
async def get_trustee_data(trustee_id: str):
    """Get trustee information"""
    try:
        # Check if we have the trustee in storage
        storage_key = sanitize_storage_key(f"trustee_{trustee_id}")
        try:
            trustee_data = db.storage.json.get(storage_key)
            return TrusteeData(**trustee_data)
        except FileNotFoundError:
            # For demo, return sample data if not found
            sample_data = {
                "id": trustee_id,
                "name": "McMillan Family Trust",
                "email": "trustee@mcmillanfamily.com",
                "role": "Primary Trustee",
                "created_at": datetime.now().isoformat()
            }
            # Store the sample data for future use
            db.storage.json.put(storage_key, sample_data)
            return TrusteeData(**sample_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trustee data: {str(e)}")

@router.get("/portfolio/{trustee_id}", response_model=PortfolioData)
async def get_portfolio_data(trustee_id: str):
    """Get portfolio information for a trustee"""
    try:
        # Check if we have the portfolio in storage
        storage_key = sanitize_storage_key(f"portfolio_{trustee_id}")
        try:
            portfolio_data = db.storage.json.get(storage_key)
            return PortfolioData(**portfolio_data)
        except FileNotFoundError:
            # For demo, return sample data if not found
            sample_data = {
                "trustee_id": trustee_id,
                "real_estate": 1250000.0,
                "infrastructure": 750000.0,
                "equities": 2000000.0,
                "crypto": 500000.0,
                "precious_metals": 300000.0,
                "solar_systems": 75.0,  # percentage complete
                "bunkers": 60.0,  # percentage complete
                "updated_at": datetime.now().isoformat()
            }
            # Store the sample data for future use
            db.storage.json.put(storage_key, sample_data)
            return PortfolioData(**sample_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio data: {str(e)}")

@router.get("/investment/{trustee_id}", response_model=InvestmentData)
async def get_investment_data(trustee_id: str):
    """Get investment growth and performance data"""
    try:
        # Check if we have the investment data in storage
        storage_key = sanitize_storage_key(f"investment_{trustee_id}")
        try:
            investment_data = db.storage.json.get(storage_key)
            return InvestmentData(**investment_data)
        except FileNotFoundError:
            # For demo, return sample data if not found
            sample_data = {
                "trustee_id": trustee_id,
                "roi": 12.8,  # percentage
                "yearly_growth": [
                    {"year": 2020, "growth": 8.5},
                    {"year": 2021, "growth": 10.2},
                    {"year": 2022, "growth": 9.7},
                    {"year": 2023, "growth": 11.3},
                    {"year": 2024, "growth": 12.8}
                ],
                "allocation": {
                    "real_estate": 25.0,
                    "infrastructure": 15.0,
                    "equities": 40.0,
                    "crypto": 10.0,
                    "precious_metals": 10.0
                },
                "risk_level": "Moderate",
                "updated_at": datetime.now().isoformat()
            }
            # Store the sample data for future use
            db.storage.json.put(storage_key, sample_data)
            return InvestmentData(**sample_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get investment data: {str(e)}")
