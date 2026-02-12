from fastapi import APIRouter, Depends
from pydantic import BaseModel
import databutton as db
import uuid
import time
import random
import json
from typing import List, Dict, Any, Optional
from app.auth import AuthorizedUser

# Initialize router
router = APIRouter(prefix="/bitcoin-sample-data")

class GenerateDataResponse(BaseModel):
    """Response from sample data generation"""
    success: bool
    message: str
    investment_count: int
    total_btc: float
    total_usd_invested: float
    total_current_value_usd: float

@router.post("/generate", response_model=GenerateDataResponse)
def generate_sample_bitcoin_data(user: AuthorizedUser):
    """Generate sample Bitcoin investment data for testing"""
    # Sample Bitcoin investment data for testing
    sample_investments = [
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1350105600,  # October 2012
            "amount_btc": 10.0,
            "amount_usd": 120.0,  # $12 per BTC
            "current_value_usd": 550000.0,  # $55,000 per BTC
            "label": "Genesis Investment",
            "notes": "First Bitcoin purchase"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1392508800,  # February 2014
            "amount_btc": 5.0,
            "amount_usd": 3250.0,  # $650 per BTC
            "current_value_usd": 275000.0,  # $55,000 per BTC
            "label": "Pre-Bull Run",
            "notes": "Additional purchase before 2017 bull run"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1451606400,  # January 2016
            "amount_btc": 8.0,
            "amount_usd": 3360.0,  # $420 per BTC
            "current_value_usd": 440000.0,  # $55,000 per BTC
            "label": "2016 Accumulation",
            "notes": "Accumulation phase"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1498867200,  # July 2017
            "amount_btc": 2.0,
            "amount_usd": 5000.0,  # $2,500 per BTC
            "current_value_usd": 110000.0,  # $55,000 per BTC
            "label": "2017 Bull Run",
            "notes": "Bought during 2017 bull market"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1577836800,  # January 2020 
            "amount_btc": 1.5,
            "amount_usd": 11250.0,  # $7,500 per BTC
            "current_value_usd": 82500.0,  # $55,000 per BTC
            "label": "Pre-COVID",
            "notes": "Investment before COVID-19 pandemic"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1600128000,  # September 2020
            "amount_btc": 0.5,
            "amount_usd": 5500.0,  # $11,000 per BTC
            "current_value_usd": 27500.0,  # $55,000 per BTC
            "label": "2020 DCA",
            "notes": "Dollar-cost averaging during recovery"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1640995200,  # January 2022
            "amount_btc": 0.25,
            "amount_usd": 11875.0,  # $47,500 per BTC
            "current_value_usd": 13750.0,  # $55,000 per BTC
            "label": "2022 Bear Market",
            "notes": "Purchased during bear market"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1693526400,  # September 2023
            "amount_btc": 0.75,
            "amount_usd": 19875.0,  # $26,500 per BTC
            "current_value_usd": 41250.0,  # $55,000 per BTC
            "label": "Pre-ETF Approval",
            "notes": "Purchase before Bitcoin ETF approval"
        },
        {
            "id": str(uuid.uuid4()),
            "timestamp": 1714176000,  # April 2024
            "amount_btc": 0.2,
            "amount_usd": 13000.0,  # $65,000 per BTC
            "current_value_usd": 11000.0,  # $55,000 per BTC
            "label": "Post-Halving",
            "notes": "Purchase after fourth Bitcoin halving"
        }
    ]
    
    # Calculate totals
    total_btc = sum(inv["amount_btc"] for inv in sample_investments)
    total_usd_invested = sum(inv["amount_usd"] for inv in sample_investments)
    total_current_value = sum(inv["current_value_usd"] for inv in sample_investments)
    
    # Save sample data to storage
    try:
        db.storage.json.put("bitcoin_investments", sample_investments)
        return GenerateDataResponse(
            success=True,
            message=f"Successfully generated {len(sample_investments)} sample Bitcoin investments",
            investment_count=len(sample_investments),
            total_btc=total_btc,
            total_usd_invested=total_usd_invested,
            total_current_value_usd=total_current_value
        )
    except Exception as e:
        return GenerateDataResponse(
            success=False,
            message=f"Error generating sample data: {str(e)}",
            investment_count=0,
            total_btc=0.0,
            total_usd_invested=0.0,
            total_current_value_usd=0.0
        )
