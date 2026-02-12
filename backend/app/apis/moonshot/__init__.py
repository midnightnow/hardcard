from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import json
import databutton as db

def get_firestore_client():
    """Initializes and returns a Firestore client."""
    try:
        # Check if the default app is already initialized
        firebase_admin.get_app()
    except ValueError:
        # If not, initialize it
        service_account_info = json.loads(db.secrets.get("FIREBASE_SERVICE_ACCOUNT"))
        creds = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(creds)
    return firestore.client()

# Pydantic Models

class MoonshotTheme(BaseModel):
    """Defines a single investment theme for the moonshot fund."""
    name: str = Field(..., description="Name of the investment theme (e.g., 'AI & Robotics', 'Longevity').")
    allocation: float = Field(..., gt=0, le=100, description="Percentage of the fund to allocate to this theme.")

class MoonshotConfig(BaseModel):
    """Configuration for the AI-curated moonshot fund."""
    strategy_name: str = Field(default="Default Moonshot", description="A user-defined name for the strategy.")
    themes: List[MoonshotTheme] = Field(..., description="List of investment themes and their allocations.")
    rebalancing_frequency_days: int = Field(default=30, description="How often the fund should be rebalanced, in days.")
    risk_tolerance: str = Field(default="moderate", description="User's risk tolerance (e.g., 'conservative', 'moderate', 'aggressive').")

class Asset(BaseModel):
    """Represents a single asset within the moonshot portfolio."""
    symbol: str = Field(..., description="The ticker symbol of the asset.")
    quantity: float = Field(..., description="The number of units held.")
    current_value_usd: float = Field(..., description="The current market value of the holdings in USD.")
    theme: str = Field(..., description="The investment theme this asset belongs to.")

class MoonshotPortfolio(BaseModel):
    """Represents the current state of the moonshot portfolio."""
    assets: List[Asset] = Field(..., description="List of assets currently held in the portfolio.")
    total_value_usd: float = Field(..., description="The total current value of the portfolio in USD.")
    last_rebalanced_at: Optional[datetime.datetime] = Field(default=None, description="Timestamp of the last rebalancing event.")
    performance_history: Dict[str, float] = Field(default={}, description="Historical performance data (e.g., daily value over time).")


# FastAPI Router
router = APIRouter(
    prefix="/moonshot",
    tags=["Moonshot Fund"]
)

@router.post("/{user_id}/configure", response_model=MoonshotConfig)
async def configure_moonshot_fund(user_id: str, config: MoonshotConfig):
    """
    Set up or update the strategy for the AI-curated moonshot fund.
    This includes defining investment themes, allocations, and rebalancing rules.
    """
    db = get_firestore_client()
    doc_ref = db.collection('moonshot_configs').document(user_id)
    doc_ref.set(config.dict())
    
    # Initialize a placeholder portfolio if one doesn't exist
    portfolio_ref = db.collection('moonshot_portfolios').document(user_id)
    if not portfolio_ref.get().exists:
        placeholder_portfolio = MoonshotPortfolio(
            assets=[],
            total_value_usd=0.0,
            last_rebalanced_at=None,
        )
        portfolio_ref.set(placeholder_portfolio.dict())

    return config

@router.get("/{user_id}/portfolio", response_model=MoonshotPortfolio)
async def get_moonshot_portfolio(user_id: str):
    """
    Retrieve the current assets, performance, and configuration of the moonshot fund.
    """
    firestore_client = get_firestore_client()
    portfolio_ref = firestore_client.collection('moonshot_portfolios').document(user_id)
    portfolio_doc = portfolio_ref.get()
    
    if not portfolio_doc.exists:
        raise HTTPException(status_code=404, detail="Moonshot portfolio not found. Please configure the fund first.")
    
    portfolio_data = portfolio_doc.to_dict()
    
    # Manually parse the datetime string from Firestore
    if portfolio_data.get('last_rebalanced_at') and isinstance(portfolio_data['last_rebalanced_at'], str):
        portfolio_data['last_rebalanced_at'] = datetime.datetime.fromisoformat(portfolio_data['last_rebalanced_at'])

    portfolio = MoonshotPortfolio(**portfolio_data)
        
    # Mock data for demonstration if portfolio is empty
    if not portfolio.assets:
        portfolio.assets = [
            Asset(symbol="TSLA", quantity=10, current_value_usd=2000.0, theme="AI & Robotics"),
            Asset(symbol="NVDA", quantity=5, current_value_usd=2500.0, theme="AI & Robotics"),
            Asset(symbol="CRSP", quantity=50, current_value_usd=3000.0, theme="Longevity"),
        ]
        portfolio.total_value_usd = 7500.0

    return portfolio

@router.post("/{user_id}/rebalance")
async def trigger_rebalancing(user_id: str):
    """
    Trigger the AI-driven rebalancing process for the moonshot fund based on the current configuration.
    This would involve complex logic to analyze markets and execute trades.
    """
    db = get_firestore_client()
    config_ref = db.collection('moonshot_configs').document(user_id)
    portfolio_ref = db.collection('moonshot_portfolios').document(user_id)

    config_doc = config_ref.get()
    portfolio_doc = portfolio_ref.get()

    if not config_doc.exists or not portfolio_doc.exists:
        raise HTTPException(status_code=404, detail="Portfolio or configuration not found.")

    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Update Firestore with ISO string for datetime
    portfolio_ref.update({"last_rebalanced_at": now.isoformat()})

    # In a real scenario, assets would be updated here.
    
    return {"status": "success", "message": "Rebalancing process initiated.", "rebalanced_at": now}
