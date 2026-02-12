from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import datetime
import databutton as db
import json
import random
from typing import List, Optional, Dict, Any

router = APIRouter()

# Models
class BitcoinPriceResponse(BaseModel):
    price: float
    timestamp: str

class HistoricalPricePoint(BaseModel):
    date: str
    price: float

class HistoricalPriceResponse(BaseModel):
    prices: List[HistoricalPricePoint]

# API key and endpoint for CoinGecko (free tier doesn't require API key but has rate limits)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
COINGECKO_PRO_API_URL = "https://pro-api.coingecko.com/api/v3"

# Try to get API key from environment or secrets if available
try:
    import databutton as db
    try:
        COINGECKO_API_KEY = db.secrets.get("COINGECKO_API_KEY")
        print(f"Using CoinGecko API key: Available")
    except KeyError:
        COINGECKO_API_KEY = None
        # print("CoinGecko API key not found, using free tier API")
except Exception as e:
    print(f"Error loading CoinGecko API key: {e}")
    COINGECKO_API_KEY = None

# Cache duration in seconds
CACHE_DURATION = 60 * 60  # 1 hour due to API rate limits

# Bitcoin historical price estimate (for fallback when API fails)
BITCOIN_HISTORICAL_ESTIMATES = {
    # Average prices for different years
    "2010": 0.10,        # Early Bitcoin
    "2011": 5.00,       # Early growth
    "2012": 10.00,
    "2013": 100.00,     # First major growth
    "2014": 500.00,
    "2015": 300.00,
    "2016": 600.00,
    "2017": 5000.00,    # Early bull run
    "2018": 8000.00,
    "2019": 7000.00,
    "2020": 10000.00,
    "2021": 40000.00,   # COVID bull run
    "2022": 30000.00,
    "2023": 25000.00,
    "2024": 60000.00,
    "2025": 65000.00,
}

# Use this to add some variation when generating fallback prices
def get_price_variation(base_price):
    """Returns a price with some random variation to make it more realistic"""
    variation_percentage = random.uniform(-0.10, 0.10)  # 10% variation
    return base_price * (1 + variation_percentage)

# Helper to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Function to get current Bitcoin price
def get_current_bitcoin_price() -> float:
    """Get current Bitcoin price from cache or API"""
    # Try to get from cache first
    try:
        cache_data = db.storage.json.get("bitcoin_price_cache", default={})
        if cache_data and "timestamp" in cache_data:
            cache_time = datetime.datetime.fromisoformat(cache_data["timestamp"])
            now = datetime.datetime.now()
            # If cache is fresh (less than CACHE_DURATION seconds old)
            if (now - cache_time).total_seconds() < CACHE_DURATION:
                print("Using cached Bitcoin price")
                return cache_data["price"]
    except Exception as e:
        print(f"Cache read error: {e}")
        pass  # If cache fails, continue to API call
    
    # Cache miss or expired, call API
    try:
        # Determine which API URL to use based on whether we have an API key
        api_url = COINGECKO_PRO_API_URL if COINGECKO_API_KEY else COINGECKO_API_URL
        headers = {}
        
        # Add API key if available
        if COINGECKO_API_KEY:
            headers["x-cg-pro-api-key"] = COINGECKO_API_KEY
        
        print(f"Fetching Bitcoin price from CoinGecko {'Pro' if COINGECKO_API_KEY else 'Free'} API...")
        response = requests.get(
            f"{api_url}/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            headers=headers,
            timeout=5  # Add timeout to prevent hanging requests
        )
        
        # Check response status
        if response.status_code == 401:
            print("CoinGecko API returned 401 Unauthorized - API key may be required")
            raise Exception("API authorization failed")
            
        response.raise_for_status()
        data = response.json()
        price = data["bitcoin"]["usd"]
        
        print(f"Successfully fetched Bitcoin price: ${price}")
        
        # Update cache
        db.storage.json.put("bitcoin_price_cache", {
            "price": price,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        return price
    except Exception as e:
        print(f"Error fetching Bitcoin price from API: {e}")
        
        # Fall back to last cached value if it exists
        try:
            print("Attempting to use last cached Bitcoin price...")
            cache_data = db.storage.json.get("bitcoin_price_cache", default={})
            if "price" in cache_data:
                print(f"Using last cached price: ${cache_data['price']}")
                return cache_data["price"]
        except Exception as cache_err:
            print(f"Cache fallback failed: {cache_err}")
        
        # Final fallback to a reasonable estimate
        print("Using estimated Bitcoin price fallback")
        current_year = str(datetime.datetime.now().year)
        base_price = BITCOIN_HISTORICAL_ESTIMATES.get(current_year, 65000.0)
        estimated_price = get_price_variation(base_price)
        
        # Update cache with our estimate so we're consistent
        try:
            db.storage.json.put("bitcoin_price_cache", {
                "price": estimated_price,
                "timestamp": datetime.datetime.now().isoformat(),
                "is_estimate": True
            })
        except Exception as e:
            print(f"Failed to update cache with estimate: {e}")
            
        return estimated_price

# Endpoint to get current Bitcoin price - no authentication required
@router.get("/bitcoin/price", tags=["public"])
def get_bitcoin_price() -> BitcoinPriceResponse:
    """Get the current Bitcoin price in USD.
    
    Returns the latest Bitcoin price in USD from CoinGecko API or from cache.
    This endpoint is rate-limited and uses a 1-hour cache to avoid exceeding API limits.
    If the API request fails, it will return cached data or an estimated price.
    
    This endpoint is useful for calculating the current value of Bitcoin investments
    and for making purchase decisions in the Legacy Vault system.
    
    Returns:
        BitcoinPriceResponse: Object containing the current price and timestamp
            - price: Current Bitcoin price in USD
            - timestamp: ISO timestamp of when the price was retrieved
    """
    price = get_current_bitcoin_price()
    return BitcoinPriceResponse(
        price=price,
        timestamp=datetime.datetime.now().isoformat()
    )

# Endpoint to get historical Bitcoin price for a specific date - no authentication required
@router.get("/bitcoin/historical/{date}", tags=["public"])
def get_bitcoin_historical_price(date: str) -> BitcoinPriceResponse:
    """Get the Bitcoin price for a specific historical date.
    
    Retrieves the Bitcoin price in USD for a given date, using the CoinGecko API
    or fallback estimation if the API is unavailable. This is useful for calculating
    the historical performance of investments and analyzing past investment decisions.
    
    The endpoint caches results to minimize API calls and provide consistent data.
    Dates must be in YYYY-MM-DD format and cannot be in the future.
    
    Args:
        date (str): The date to get price for in YYYY-MM-DD format
        
    Returns:
        BitcoinPriceResponse: Object containing the historical price and timestamp
            - price: Bitcoin price in USD on the specified date
            - timestamp: ISO timestamp of the requested date
            
    Raises:
        HTTPException: 400 error if date is in the future or in invalid format
        HTTPException: 500 error if price retrieval failed completely
    """
    try:
        # Parse the date
        target_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        
        # Ensure the date is not in the future
        if target_date > datetime.datetime.now():
            raise HTTPException(status_code=400, detail="Date cannot be in the future")
        
        print(f"Getting Bitcoin price for {date}")
        
        # Check if we have the price cached
        cache_key = sanitize_storage_key(f"bitcoin_price_{date}")
        try:
            cached_price = db.storage.json.get(cache_key, default=None)
            if cached_price is not None:
                print(f"Using cached price for {date}: ${cached_price}")
                return BitcoinPriceResponse(
                    price=cached_price,
                    timestamp=target_date.isoformat()
                )
        except Exception as e:
            print(f"Cache read error: {e}")
        
        # Try to get from API
        try:
            # Determine which API URL to use based on whether we have an API key
            api_url = COINGECKO_PRO_API_URL if COINGECKO_API_KEY else COINGECKO_API_URL
            headers = {}
            
            # Add API key if available
            if COINGECKO_API_KEY:
                headers["x-cg-pro-api-key"] = COINGECKO_API_KEY
                
            print(f"Fetching historical price from CoinGecko {'Pro' if COINGECKO_API_KEY else 'Free'} API for {date}...")
            # Get historical data
            response = requests.get(
                f"{api_url}/coins/bitcoin/history",
                params={"date": target_date.strftime("%d-%m-%Y"), "localization": "false"},
                headers=headers,
                timeout=5  # Add timeout to prevent hanging requests
            )
            
            # Check for authorization issues
            if response.status_code == 401:
                print("CoinGecko API returned 401 Unauthorized - API key may be required")
                raise Exception("API authorization failed")
                
            response.raise_for_status()
            data = response.json()
            
            # Extract the price
            price = data["market_data"]["current_price"]["usd"]
            print(f"Successfully fetched historical price: ${price}")
            
            # Cache the result
            db.storage.json.put(cache_key, price)
            
            return BitcoinPriceResponse(
                price=price,
                timestamp=target_date.isoformat()
            )
        except Exception as e:
            print(f"CoinGecko API error: {e}")
            print("Falling back to estimated historical price")
            
            # Fall back to estimated price
            year = str(target_date.year)
            if year in BITCOIN_HISTORICAL_ESTIMATES:
                # Get base price for that year
                base_price = BITCOIN_HISTORICAL_ESTIMATES[year]
                # Add some variation based on day/month
                day_of_year = target_date.timetuple().tm_yday
                yearly_progress = day_of_year / 365.0
                # Adjust price based on time of year and add random variation
                adjusted_price = base_price * (1 + (yearly_progress * 0.2) - 0.1)
                estimated_price = get_price_variation(adjusted_price)
                
                print(f"Using estimated price for {year}: ${estimated_price}")
                
                # Cache the estimated price
                db.storage.json.put(cache_key, estimated_price)
                
                return BitcoinPriceResponse(
                    price=estimated_price,
                    timestamp=target_date.isoformat()
                )
            else:
                # If we don't have an estimate for this year, use current price with a discount
                print(f"No estimate available for {year}, calculating based on current price")
                current_price = get_current_bitcoin_price()
                years_ago = datetime.datetime.now().year - target_date.year
                if years_ago > 0:
                    # Reduce price by 40% for each year in the past (very approximate)
                    estimated_price = current_price * (0.6 ** years_ago)
                else:
                    estimated_price = current_price
                
                print(f"Calculated historical price: ${estimated_price}")
                
                # Cache the estimated price
                db.storage.json.put(cache_key, estimated_price)
                
                return BitcoinPriceResponse(
                    price=estimated_price,
                    timestamp=target_date.isoformat()
                )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_bitcoin_historical_price: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical Bitcoin price")

# Endpoint to get historical Bitcoin prices for a date range - no authentication required
@router.get("/bitcoin/historical", tags=["public"])
def get_bitcoin_historical_prices(start_date: str, end_date: Optional[str] = None) -> HistoricalPriceResponse:
    """Get Bitcoin prices for a date range, useful for trend analysis.
    
    Retrieves Bitcoin prices in USD for a specified time period, with a maximum
    range of 90 days due to API limitations. This endpoint is valuable for
    generating charts, analyzing trends, and calculating investment performance
    over time in the Legacy Vault system.
    
    Results are cached to provide consistent data and reduce API calls.
    
    Args:
        start_date (str): The start date in YYYY-MM-DD format
        end_date (str, optional): The end date in YYYY-MM-DD format. Defaults to current date.
        
    Returns:
        HistoricalPriceResponse: Object containing a list of daily price points
            - prices: List of objects with date and price properties
            
    Raises:
        HTTPException: 400 error if date range is invalid
        HTTPException: 500 error if price retrieval failed completely
        
    Note:
        If the date range exceeds 90 days, it will be automatically limited to 90 days
        from the start date for API compatibility.
    """
    try:
        # Parse the start date
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        
        # Parse the end date or default to today
        if end_date:
            end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.datetime.now()
        
        # Ensure dates are valid
        if start > end:
            raise HTTPException(status_code=400, detail="Start date cannot be after end date")
        if end > datetime.datetime.now():
            end = datetime.datetime.now()
        
        print(f"Getting Bitcoin historical prices from {start_date} to {end_date or 'today'}")
        
        # Calculate days difference (CoinGecko limits to 90 days for free tier)
        days_diff = (end - start).days
        if days_diff > 90:
            print("Warning: Date range exceeds 90 days, limiting to 90 days for API compatibility")
            # Just limit to 90 days instead of throwing an error
            end = start + datetime.timedelta(days=90)
        
        # Try to get from cache first
        cache_key = sanitize_storage_key(f"bitcoin_prices_{start_date}_to_{end_date or 'today'}")
        try:
            cached_data = db.storage.json.get(cache_key, default=None)
            if cached_data is not None:
                print(f"Using cached historical prices")
                prices = [HistoricalPricePoint(**point) for point in cached_data]
                return HistoricalPriceResponse(prices=prices)
        except Exception as e:
            print(f"Cache read error: {e}")
        
        # Get historical data from CoinGecko
        try:
            print("Fetching historical prices from CoinGecko API...")
            # Determine which API URL to use based on whether we have an API key
            api_url = COINGECKO_PRO_API_URL if COINGECKO_API_KEY else COINGECKO_API_URL
            headers = {}
            
            # Add API key if available
            if COINGECKO_API_KEY:
                headers["x-cg-pro-api-key"] = COINGECKO_API_KEY
                
            unix_start = int(start.timestamp())
            unix_end = int(end.timestamp())
            
            print(f"Fetching historical prices from CoinGecko {'Pro' if COINGECKO_API_KEY else 'Free'} API...")
            response = requests.get(
                f"{api_url}/coins/bitcoin/market_chart/range",
                params={
                    "vs_currency": "usd",
                    "from": unix_start,
                    "to": unix_end
                },
                headers=headers,
                timeout=10  # Longer timeout for larger data requests
            )
            
            # Check for authorization issues
            if response.status_code == 401:
                print("CoinGecko API returned 401 Unauthorized - API key may be required")
                raise Exception("API authorization failed")
                
            response.raise_for_status()
            data = response.json()
            
            # Process the data
            # CoinGecko returns prices as [timestamp, price] arrays
            prices = []
            for price_point in data["prices"]:
                timestamp, price = price_point
                date_str = datetime.datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
                prices.append(HistoricalPricePoint(date=date_str, price=price))
            
            print(f"Successfully fetched {len(prices)} historical price points")
            
            # Cache the results
            cache_data = [point.dict() for point in prices]
            db.storage.json.put(cache_key, cache_data)
            
            return HistoricalPriceResponse(prices=prices)
        except Exception as e:
            print(f"Error fetching from CoinGecko: {e}")
            # Generate mock data for the date range as fallback
            print("Generating synthetic historical prices as fallback")
            current_date = start
            prices = []
            
            while current_date <= end:
                date_str = current_date.strftime("%Y-%m-%d")
                # Get price for this individual date using our other function
                # which already has fallbacks built in
                try:
                    price_response = get_bitcoin_historical_price(date_str)
                    prices.append(HistoricalPricePoint(
                        date=date_str,
                        price=price_response.price
                    ))
                except Exception as e:
                    print(f"Error getting price for {date_str}: {e}")
                    # Even if one date fails, continue with others
                    pass
                
                # Move to next day
                current_date += datetime.timedelta(days=1)
            
            # Only cache if we got some data
            if prices:
                print(f"Generated {len(prices)} fallback price points")
                cache_data = [point.dict() for point in prices]
                db.storage.json.put(cache_key, cache_data)
                return HistoricalPriceResponse(prices=prices)
            else:
                # Complete failure - return empty list with error message
                print("Failed to generate any price data")
                raise HTTPException(
                    status_code=500, 
                    detail="Could not fetch or generate Bitcoin historical prices"
                )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_bitcoin_historical_prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical Bitcoin prices")
