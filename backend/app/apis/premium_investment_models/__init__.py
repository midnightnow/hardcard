from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import databutton as db
import requests
import json
import uuid

# Create API router
router = APIRouter(prefix="/premium")

# Get Wise API key from secrets
try:
    WISE_API_KEY = db.secrets.get("WISE_API_KEY")
except KeyError:
    print("Wise API key not found, using mock responses only")
    WISE_API_KEY = ""
WISE_API_URL = "https://api.wise.com"

class CurrencyPair(BaseModel):
    source: str
    target: str

class QuoteRequest(BaseModel):
    source_currency: str
    target_currency: str
    source_amount: float
    profile_id: Optional[str] = None

class QuoteResponse(BaseModel):
    id: str
    source_currency: str
    target_currency: str
    source_amount: float
    target_amount: float
    rate: float
    fee: float
    estimated_delivery: str

class InvestmentModel(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    type: str  # "dollar-cost-average", "lump-sum", "value-averaging", "custom"
    schedule: str  # "weekly", "monthly", "quarterly", "annual", "custom"
    currencies: List[str]
    allocation: Dict[str, float]  # Currency to percentage allocation
    parameters: Dict[str, Any] = {}  # Model-specific parameters

class InvestmentModelList(BaseModel):
    models: List[InvestmentModel]

class TransferRequest(BaseModel):
    profile_id: str
    quote_id: str
    target_account_id: str
    reference: Optional[str] = None

class TransferResponse(BaseModel):
    id: str
    status: str
    source_currency: str
    target_currency: str
    source_amount: float
    target_amount: float
    created_at: str
    estimated_delivery: str

@router.get("/supported-currencies")
async def get_supported_currencies() -> List[Dict[str, str]]:
    """Get all currencies supported by Wise"""
    try:
        if not WISE_API_KEY:
            # Return mock data if API key is not available
            return [
                {"code": "USD", "name": "US Dollar"},
                {"code": "EUR", "name": "Euro"},
                {"code": "GBP", "name": "British Pound"},
                {"code": "AUD", "name": "Australian Dollar"},
                {"code": "CAD", "name": "Canadian Dollar"},
                {"code": "JPY", "name": "Japanese Yen"},
                {"code": "CHF", "name": "Swiss Franc"},
                {"code": "NZD", "name": "New Zealand Dollar"},
                {"code": "SGD", "name": "Singapore Dollar"},
                {"code": "HKD", "name": "Hong Kong Dollar"},
                {"code": "BTC", "name": "Bitcoin"}
            ]
            
        # Call Wise API to get supported currencies
        response = requests.get(
            f"{WISE_API_URL}/v1/currencies",
            headers={"Authorization": f"Bearer {WISE_API_KEY}"}
        )
        response.raise_for_status()
        currencies = response.json()
        
        # Add Bitcoin manually as it's not in Wise API
        currencies.append({"code": "BTC", "name": "Bitcoin"})
        
        return currencies
    except Exception as e:
        print(f"Error fetching supported currencies: {str(e)}")
        # Fallback to common currencies
        return [
            {"code": "USD", "name": "US Dollar"},
            {"code": "EUR", "name": "Euro"},
            {"code": "GBP", "name": "British Pound"},
            {"code": "AUD", "name": "Australian Dollar"},
            {"code": "CAD", "name": "Canadian Dollar"},
            {"code": "JPY", "name": "Japanese Yen"},
            {"code": "BTC", "name": "Bitcoin"}
        ]

@router.get("/currency-pairs")
async def get_currency_pairs() -> List[CurrencyPair]:
    """Get all available currency pairs for conversion"""
    try:
        if not WISE_API_KEY:
            # Return mock data if API key is not available
            return [
                {"source": "USD", "target": "EUR"},
                {"source": "USD", "target": "GBP"},
                {"source": "USD", "target": "AUD"},
                {"source": "USD", "target": "BTC"},
                {"source": "EUR", "target": "USD"},
                {"source": "EUR", "target": "GBP"},
                {"source": "EUR", "target": "BTC"},
                {"source": "GBP", "target": "USD"},
                {"source": "GBP", "target": "EUR"},
                {"source": "GBP", "target": "BTC"}
            ]
            
        # Call Wise API to get currency pairs
        response = requests.get(
            f"{WISE_API_URL}/v1/currency-pairs",
            headers={"Authorization": f"Bearer {WISE_API_KEY}"}
        )
        response.raise_for_status()
        pairs = response.json()
        
        # Add Bitcoin pairs manually
        for currency in ["USD", "EUR", "GBP"]:
            pairs.append({"source": currency, "target": "BTC"})
            pairs.append({"source": "BTC", "target": currency})
            
        return pairs
    except Exception as e:
        print(f"Error fetching currency pairs: {str(e)}")
        # Fallback to common pairs
        return [
            {"source": "USD", "target": "EUR"},
            {"source": "USD", "target": "GBP"},
            {"source": "USD", "target": "BTC"},
            {"source": "EUR", "target": "USD"},
            {"source": "EUR", "target": "BTC"},
            {"source": "GBP", "target": "USD"},
            {"source": "GBP", "target": "BTC"}
        ]

@router.post("/create-quote")
async def create_quote(request: QuoteRequest) -> QuoteResponse:
    """Create a quote for currency conversion"""
    try:
        # Handle special case for Bitcoin which is not in Wise API
        if request.source_currency == "BTC" or request.target_currency == "BTC":
            # Get Bitcoin price for simulation
            btc_price = 30000.0  # Default fallback price
            try:
                from app.apis.bitcoin_price import get_bitcoin_price
                btc_data = await get_bitcoin_price()
                btc_price = btc_data.price
            except Exception:
                pass
                
            # Simulate conversion
            if request.source_currency == "BTC":
                target_amount = request.source_amount * btc_price
                rate = btc_price
            else:
                target_amount = request.source_amount / btc_price
                rate = 1 / btc_price
                
            # Calculate mock fee (0.5%)
            fee = request.source_amount * 0.005
                
            return QuoteResponse(
                id=str(uuid.uuid4()),
                source_currency=request.source_currency,
                target_currency=request.target_currency,
                source_amount=request.source_amount,
                target_amount=target_amount,
                rate=rate,
                fee=fee,
                estimated_delivery="2-3 business days"
            )
            
        if not WISE_API_KEY:
            # Return mock data if API key is not available
            mock_rates = {
                "USD-EUR": 0.85,
                "USD-GBP": 0.75,
                "EUR-USD": 1.18,
                "EUR-GBP": 0.88,
                "GBP-USD": 1.33,
                "GBP-EUR": 1.14
            }
            
            pair_key = f"{request.source_currency}-{request.target_currency}"
            rate = mock_rates.get(pair_key, 1.0)
            target_amount = request.source_amount * rate
            fee = request.source_amount * 0.005  # 0.5% fee
            
            return QuoteResponse(
                id=str(uuid.uuid4()),
                source_currency=request.source_currency,
                target_currency=request.target_currency,
                source_amount=request.source_amount,
                target_amount=target_amount,
                rate=rate,
                fee=fee,
                estimated_delivery="2-3 business days"
            )
        
        # Create a profile if not provided
        profile_id = request.profile_id
        if not profile_id:
            profile_response = requests.get(
                f"{WISE_API_URL}/v1/profiles",
                headers={"Authorization": f"Bearer {WISE_API_KEY}"}
            )
            profile_response.raise_for_status()
            profiles = profile_response.json()
            if profiles:
                profile_id = profiles[0]["id"]
            else:
                raise HTTPException(status_code=400, detail="No profile found")
        
        # Call Wise API to create a quote
        payload = {
            "profile": profile_id,
            "source": request.source_currency,
            "target": request.target_currency,
            "sourceAmount": request.source_amount,
            "type": "REGULAR"
        }
        
        response = requests.post(
            f"{WISE_API_URL}/v1/quotes",
            headers={"Authorization": f"Bearer {WISE_API_KEY}", "Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        quote = response.json()
        
        return QuoteResponse(
            id=quote["id"],
            source_currency=quote["source"],
            target_currency=quote["target"],
            source_amount=quote["sourceAmount"],
            target_amount=quote["targetAmount"],
            rate=quote["rate"],
            fee=quote["fee"],
            estimated_delivery=quote["deliveryEstimate"]
        )
    except Exception as e:
        print(f"Error creating quote: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create quote: {str(e)}")

@router.post("/create-transfer")
async def create_transfer(request: TransferRequest) -> TransferResponse:
    """Create a transfer using a quote"""
    try:
        if not WISE_API_KEY:
            # Return mock data if API key is not available
            return TransferResponse(
                id=str(uuid.uuid4()),
                status="PENDING",
                source_currency="USD",
                target_currency="EUR",
                source_amount=1000.0,
                target_amount=850.0,
                created_at="2023-01-01T12:00:00Z",
                estimated_delivery="2023-01-04T12:00:00Z"
            )
        
        # Call Wise API to create a transfer
        payload = {
            "targetAccount": request.target_account_id,
            "quoteUuid": request.quote_id,
            "customerTransactionId": str(uuid.uuid4()),
            "details": {
                "reference": request.reference or "Investment Transfer"
            }
        }
        
        response = requests.post(
            f"{WISE_API_URL}/v1/transfers",
            headers={"Authorization": f"Bearer {WISE_API_KEY}", "Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()
        transfer = response.json()
        
        # Get transfer details
        details_response = requests.get(
            f"{WISE_API_URL}/v1/transfers/{transfer['id']}",
            headers={"Authorization": f"Bearer {WISE_API_KEY}"}
        )
        details_response.raise_for_status()
        details = details_response.json()
        
        return TransferResponse(
            id=details["id"],
            status=details["status"],
            source_currency=details["sourceCurrency"],
            target_currency=details["targetCurrency"],
            source_amount=details["sourceAmount"],
            target_amount=details["targetAmount"],
            created_at=details["created"],
            estimated_delivery=details["estimatedDeliveryDate"]
        )
    except Exception as e:
        print(f"Error creating transfer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create transfer: {str(e)}")

@router.get("/investment-models")
async def get_investment_models() -> InvestmentModelList:
    """Get available premium investment models"""
    # In a real app, these would be stored in a database
    models = [
        InvestmentModel(
            id="dca-premium",
            name="Premium Dollar-Cost Averaging",
            description="Enhanced DCA with multi-currency support and custom scheduling",
            type="dollar-cost-average",
            schedule="custom",
            currencies=["USD", "EUR", "GBP", "BTC"],
            allocation={"BTC": 60, "USD": 20, "EUR": 10, "GBP": 10},
            parameters={
                "frequency_days": 7,  # Weekly by default
                "rebalance_frequency": "quarterly"
            }
        ),
        InvestmentModel(
            id="value-avg",
            name="Value Averaging",
            description="Adjust contributions to maintain a steady growth curve",
            type="value-averaging",
            schedule="monthly",
            currencies=["USD", "BTC"],
            allocation={"BTC": 100},
            parameters={
                "target_growth_rate": 0.05,  # 5% monthly growth target
                "max_contribution": 5000
            }
        ),
        InvestmentModel(
            id="multi-asset",
            name="Multi-Asset Portfolio",
            description="Diversified portfolio across multiple asset classes and currencies",
            type="custom",
            schedule="monthly",
            currencies=["USD", "EUR", "GBP", "BTC"],
            allocation={"BTC": 30, "USD": 40, "EUR": 20, "GBP": 10},
            parameters={
                "rebalance_threshold": 0.05,  # Rebalance when allocation drifts by 5%
                "auto_currency_conversion": True
            }
        ),
        InvestmentModel(
            id="global-macro",
            name="Global Macro Strategy",
            description="Adjust allocations based on global economic trends",
            type="custom",
            schedule="quarterly",
            currencies=["USD", "EUR", "GBP", "JPY", "AUD", "BTC"],
            allocation={"BTC": 20, "USD": 30, "EUR": 20, "GBP": 10, "JPY": 10, "AUD": 10},
            parameters={
                "use_economic_indicators": True,
                "region_weights": {"north_america": 0.4, "europe": 0.3, "asia": 0.2, "oceania": 0.1}
            }
        )
    ]
    
    return InvestmentModelList(models=models)

@router.post("/create-custom-model")
async def create_custom_model(model: InvestmentModel) -> InvestmentModel:
    """Create a custom investment model"""
    # In a real app, this would be stored in a database
    # For now, we just return the model with a new ID
    model.id = str(uuid.uuid4())
    return model
