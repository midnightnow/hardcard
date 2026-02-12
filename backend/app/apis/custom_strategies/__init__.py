from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import databutton as db
import json
import re

# Create API router
router = APIRouter()

# Define models
class CustomStrategyRequest(BaseModel):
    profile_id: str
    strategy_name: str
    description: str
    allocation: Dict[str, float]
    annual_return: float
    volatility: str
    risk_score: int
    based_on_ai: bool = True
    time_horizon: int = 18

class StrategyResponse(BaseModel):
    id: str
    strategy_name: str
    description: str
    allocation: Dict[str, float]
    annual_return: float
    volatility: str
    risk_score: int
    based_on_ai: bool
    time_horizon: int
    creation_date: str

class StrategiesListResponse(BaseModel):
    strategies: List[StrategyResponse]

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

@router.post("/save-strategy")
async def save_custom_strategy_endpoint(request: CustomStrategyRequest) -> StrategyResponse:
    """Save a custom investment strategy"""
    try:
        # Create a unique ID for the strategy
        from datetime import datetime
        import uuid
        
        strategy_id = f"{sanitize_storage_key(request.profile_id)}_strategy_{uuid.uuid4().hex[:8]}"
        creation_date = datetime.now().isoformat()
        
        # Create the strategy object
        strategy = {
            "id": strategy_id,
            "strategy_name": request.strategy_name,
            "description": request.description,
            "allocation": request.allocation,
            "annual_return": request.annual_return,
            "volatility": request.volatility,
            "risk_score": request.risk_score,
            "based_on_ai": request.based_on_ai,
            "time_horizon": request.time_horizon,
            "creation_date": creation_date,
            "profile_id": request.profile_id
        }
        
        # Get existing strategies or create empty list
        storage_key = f"custom_strategies_{sanitize_storage_key(request.profile_id)}"
        
        try:
            strategies = db.storage.json.get(storage_key, default=[])
        except Exception:
            strategies = []
        
        # Add new strategy
        strategies.append(strategy)
        
        # Save updated strategies
        db.storage.json.put(storage_key, strategies)
        
        # Return the created strategy
        return StrategyResponse(**strategy)
        
    except Exception as e:
        print(f"Error saving custom strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save custom strategy: {str(e)}")

@router.get("/list-strategies/{profile_id}")
async def list_custom_strategies_endpoint(profile_id: str) -> StrategiesListResponse:
    """List all custom strategies for a profile"""
    try:
        # Sanitize the profile ID
        sanitized_id = sanitize_storage_key(profile_id)
        
        # Get strategies from storage
        storage_key = f"custom_strategies_{sanitized_id}"
        
        try:
            strategies = db.storage.json.get(storage_key, default=[])
        except Exception:
            strategies = []
        
        # Convert to response model
        response_strategies = [StrategyResponse(**strategy) for strategy in strategies]
        
        return StrategiesListResponse(strategies=response_strategies)
        
    except Exception as e:
        print(f"Error listing custom strategies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list custom strategies: {str(e)}")

@router.get("/get-strategy/{strategy_id}")
async def get_custom_strategy_endpoint(strategy_id: str) -> StrategyResponse:
    """Get a specific custom strategy by ID"""
    try:
        # Extract profile ID from strategy ID (assuming format: profile_id_strategy_uuid)
        parts = strategy_id.split('_strategy_')
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid strategy ID format")
            
        profile_id = parts[0]
        
        # Get strategies from storage
        storage_key = f"custom_strategies_{sanitize_storage_key(profile_id)}"
        
        try:
            strategies = db.storage.json.get(storage_key, default=[])
        except Exception:
            strategies = []
        
        # Find the strategy
        for strategy in strategies:
            if strategy.get('id') == strategy_id:
                return StrategyResponse(**strategy)
        
        # If not found
        raise HTTPException(status_code=404, detail="Strategy not found")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting custom strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get custom strategy: {str(e)}")

@router.delete("/delete-strategy/{strategy_id}")
async def delete_custom_strategy_endpoint(strategy_id: str) -> Dict[str, str]:

    """Delete a custom strategy by ID"""
    try:
        # Extract profile ID from strategy ID
        parts = strategy_id.split('_strategy_')
        if len(parts) != 2:
            raise HTTPException(status_code=400, detail="Invalid strategy ID format")
            
        profile_id = parts[0]
        
        # Get strategies from storage
        storage_key = f"custom_strategies_{sanitize_storage_key(profile_id)}"
        
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
        print(f"Error deleting custom strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete custom strategy: {str(e)}")
