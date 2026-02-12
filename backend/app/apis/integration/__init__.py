from fastapi import APIRouter, HTTPException, Depends
import requests
import time
import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.apis.product import get_product_by_sku as get_local_product, get_all_products as get_all_local_products, save_products
import databutton as db
import json
import re

router = APIRouter()

# Models
class WooCommerceConfig(BaseModel):
    url: str
    consumer_key: str
    consumer_secret: str
    sync_products: bool = True
    sync_orders: bool = False
    sync_customers: bool = False
    enabled: bool = True
    last_sync: Optional[str] = None
    last_error: Optional[str] = None
    error_count: int = 0

class IntegrationBase(BaseModel):
    name: str
    type: str
    
class IntegrationCreate(IntegrationBase):
    config: WooCommerceConfig
    
class Integration(IntegrationBase):
    id: str
    status: str = "disconnected"
    created_at: str
    updated_at: str
    config: WooCommerceConfig
    
class IntegrationListResponse(BaseModel):
    integrations: List[Integration]
    
class IntegrationResponse(BaseModel):
    integration: Integration
    message: str

class MessageResponse(BaseModel):
    message: str
    success: bool

class SyncOptions(BaseModel):
    force: bool = False

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_all_integrations() -> List[Integration]:
    try:
        integrations = db.storage.json.get("integrations", default=[])
        return integrations
    except Exception as e:
        print(f"Error getting integrations: {str(e)}")
        return []

def save_integrations(integrations: List[Dict]):
    db.storage.json.put("integrations", integrations)

def get_integration_by_id(integration_id: str) -> Optional[Dict]:
    integrations = get_all_integrations()
    for integration in integrations:
        if integration.get("id") == integration_id:
            return integration
    return None

def map_woocommerce_to_product(product: Dict, source: str = "hempex.com") -> Dict:
    """Map WooCommerce product data to our internal product format"""
    # Extract categories
    categories = product.get("categories", [])
    category_name = categories[0].get("name") if categories else "Uncategorized"
    category_id = str(categories[0].get("id")) if categories else "uncategorized"
    
    # Get the price
    price = 0
    try:
        price = float(product.get("price", "0"))
    except (ValueError, TypeError):
        price = 0
    
    # Determine if product is on sale
    regular_price = 0
    sale_price = 0
    on_sale = False
    
    try:
        regular_price = float(product.get("regular_price", "0"))
        if product.get("sale_price"):
            sale_price = float(product.get("sale_price", "0"))
            on_sale = True
    except (ValueError, TypeError):
        pass
    
    # Get stock status
    in_stock = product.get("stock_status", "") == "instock"
    inventory_status = "in_stock" if in_stock else "out_of_stock"
    
    # Map images
    images = []
    for image in product.get("images", []):
        if "src" in image:
            images.append(image["src"])
    
    # Create our product object
    mapped_product = {
        "id": str(product.get("id", "")),
        "sku": product.get("sku", f"wc-{product.get('id')}"),
        "name": product.get("name", ""),
        "description": product.get("description", ""),
        "short_description": product.get("short_description", ""),
        "category_id": category_id,
        "category_name": category_name,
        "image_urls": images,
        "cannabinoids": [],  # WooCommerce doesn't have this directly
        "tga_approved": False,  # Default, adjust if metadata indicates otherwise
        "price": price,
        "regular_price": regular_price if regular_price > 0 else price,
        "sale_price": sale_price if on_sale else None,
        "on_sale": on_sale,
        "inventory_status": inventory_status,
        "source": source,  # Indicate this came from hempex.com
    }
    
    # Check if TGA approved in attributes or metadata
    for attribute in product.get("attributes", []):
        if attribute.get("name", "").lower() in ["tga approved", "tga compliance"]:
            options = attribute.get("options", [])
            if options and options[0].lower() in ["yes", "true", "approved", "compliant"]:
                mapped_product["tga_approved"] = True
    
    # Look for cannabinoid data in attributes
    for attribute in product.get("attributes", []):
        name = attribute.get("name", "").lower()
        if name in ["cbd", "cbd content", "cbd percentage"]:
            try:
                options = attribute.get("options", [])
                if options:
                    value = options[0].replace("%", "").strip()
                    if value and float(value) > 0:
                        mapped_product["cannabinoids"].append({
                            "type": "CBD",
                            "amount": float(value),
                            "unit": "%"
                        })
            except (ValueError, TypeError):
                pass
        elif name in ["cbg", "cbg content", "cbg percentage"]:
            try:
                options = attribute.get("options", [])
                if options:
                    value = options[0].replace("%", "").strip()
                    if value and float(value) > 0:
                        mapped_product["cannabinoids"].append({
                            "type": "CBG",
                            "amount": float(value),
                            "unit": "%"
                        })
            except (ValueError, TypeError):
                pass
    
    return mapped_product

def fetch_woocommerce_products(integration: Dict) -> List[Dict]:
    """Fetch products from a WooCommerce store"""
    config = integration.get("config", {})
    url = config.get("url", "").rstrip("/")
    consumer_key = config.get("consumer_key", "")
    consumer_secret = config.get("consumer_secret", "")
    
    if not url or not consumer_key or not consumer_secret:
        raise ValueError("Missing required WooCommerce configuration")
    
    products = []
    page = 1
    per_page = 50
    
    while True:
        api_url = f"{url}/wp-json/wc/v3/products"
        params = {
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "per_page": per_page,
            "page": page,
            "status": "publish"
        }
        
        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            
            batch = response.json()
            if not batch:
                break
                
            products.extend(batch)
            
            # Check if we have more pages
            if len(batch) < per_page:
                break
                
            page += 1
            
        except requests.RequestException as e:
            raise ValueError(f"Error fetching WooCommerce products: {str(e)}")
    
    return products

# Endpoints
@router.get("/integration/health")
async def check_health_integration():
    """Check if the integrations system is working"""
    return {"status": "ok", "message": "Integration API is operational"}

@router.get("/", response_model=IntegrationListResponse)
async def list_all_integrations2():
    """List all available integrations"""
    integrations = get_all_integrations()
    return IntegrationListResponse(integrations=integrations)

@router.post("/", response_model=IntegrationResponse)
async def create_integration2(integration: IntegrationCreate):
    """Create a new integration"""
    integrations = get_all_integrations()
    
    # Generate a simple ID
    import uuid
    new_id = str(uuid.uuid4())
    
    # Get current timestamp
    now = datetime.datetime.now().isoformat()
    
    # Create new integration
    new_integration = {
        "id": new_id,
        "name": integration.name,
        "type": integration.type,
        "status": "disconnected",
        "created_at": now,
        "updated_at": now,
        "config": integration.config.dict()
    }
    
    # Test the connection
    if integration.type == "woocommerce":
        try:
            # Attempt to connect
            fetch_woocommerce_products(new_integration)
            new_integration["status"] = "connected"
        except Exception as e:
            new_integration["config"]["last_error"] = str(e)
            new_integration["config"]["error_count"] = 1
    
    integrations.append(new_integration)
    save_integrations(integrations)
    
    return IntegrationResponse(
        integration=new_integration,
        message="Integration created successfully"
    )

@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_single_integration2(integration_id: str):
    """Get a single integration by ID"""
    integration = get_integration_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return IntegrationResponse(
        integration=integration,
        message="Integration retrieved successfully"
    )

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_single_integration2(integration_id: str, update_data: Dict[str, Any]):
    """Update a single integration"""
    integrations = get_all_integrations()
    
    found = False
    for i, integration in enumerate(integrations):
        if integration.get("id") == integration_id:
            # Update only the fields that are provided
            for key, value in update_data.items():
                if key == "config":
                    # Update config fields individually
                    for config_key, config_value in value.items():
                        integration["config"][config_key] = config_value
                else:
                    integration[key] = value
            
            # Update the timestamp
            integration["updated_at"] = datetime.datetime.now().isoformat()
            
            # If enabled status changed, update the status
            if "config" in update_data and "enabled" in update_data["config"]:
                if update_data["config"]["enabled"]:
                    integration["status"] = "connected" if integration["status"] != "syncing" else "syncing"
                else:
                    integration["status"] = "disconnected"
            
            integrations[i] = integration
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    save_integrations(integrations)
    
    return IntegrationResponse(
        integration=integrations[i],
        message="Integration updated successfully"
    )

@router.delete("/{integration_id}", response_model=MessageResponse)
async def delete_integration2(integration_id: str):
    """Delete an integration"""
    integrations = get_all_integrations()
    
    found = False
    for i, integration in enumerate(integrations):
        if integration.get("id") == integration_id:
            integrations.pop(i)
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    save_integrations(integrations)
    
    return MessageResponse(
        message="Integration deleted successfully",
        success=True
    )

@router.post("/{integration_id}/test", response_model=MessageResponse)
async def test_integration2(integration_id: str):
    """Test an integration connection"""
    integration = get_integration_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    if integration["type"] == "woocommerce":
        try:
            # Test the connection by getting a single product
            url = integration["config"]["url"].rstrip("/")
            consumer_key = integration["config"]["consumer_key"]
            consumer_secret = integration["config"]["consumer_secret"]
            
            api_url = f"{url}/wp-json/wc/v3/products"
            params = {
                "consumer_key": consumer_key,
                "consumer_secret": consumer_secret,
                "per_page": 1
            }
            
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            
            return MessageResponse(
                message="WooCommerce connection successful",
                success=True
            )
            
        except Exception as e:
            # Update the integration with the error
            integration["config"]["last_error"] = str(e)
            integration["config"]["error_count"] = integration["config"].get("error_count", 0) + 1
            integration["status"] = "error"
            
            # Save the updated integration
            integrations = get_all_integrations()
            for i, integ in enumerate(integrations):
                if integ.get("id") == integration_id:
                    integrations[i] = integration
                    break
            save_integrations(integrations)
            
            return MessageResponse(
                message=f"WooCommerce connection failed: {str(e)}",
                success=False
            )
    
    return MessageResponse(
        message=f"Testing {integration['type']} integration is not supported",
        success=False
    )

@router.post("/{integration_id}/sync", response_model=MessageResponse)
async def trigger_sync2(integration_id: str, options: SyncOptions):
    """Trigger a sync for an integration"""
    integration = get_integration_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Check if the integration is enabled
    if not integration["config"].get("enabled", True) and not options.force:
        return MessageResponse(
            message="Integration is disabled. Enable it or use force=true to sync anyway.",
            success=False
        )
    
    # Update status to syncing
    integration["status"] = "syncing"
    integration["updated_at"] = datetime.datetime.now().isoformat()
    
    # Update the integration status
    integrations = get_all_integrations()
    for i, integ in enumerate(integrations):
        if integ.get("id") == integration_id:
            integrations[i] = integration
            break
    save_integrations(integrations)
    
    # Start a background task for sync (we'll simulate with a delay)
    # In a production environment, this would use a proper background task system
    try:
        if integration["type"] == "woocommerce":
            # Only proceed if sync_products is enabled
            if not integration["config"].get("sync_products", True) and not options.force:
                return MessageResponse(
                    message="Product sync is disabled for this integration",
                    success=False
                )
            
            # Fetch products from WooCommerce
            woo_products = fetch_woocommerce_products(integration)
            
            # Convert to our product format
            mapped_products = [map_woocommerce_to_product(p) for p in woo_products]
            
            # Get existing products
            existing_products = get_all_local_products()
            
            # Create a dictionary of existing products by SKU
            existing_by_sku = {p["sku"]: p for p in existing_products}
            
            # Merge products - update existing ones and add new ones
            for product in mapped_products:
                if product["sku"] in existing_by_sku:
                    # This is an existing product - update selected fields
                    for key in ["name", "description", "short_description", "price", 
                                "regular_price", "sale_price", "on_sale", "inventory_status", 
                                "image_urls", "source"]:
                        existing_by_sku[product["sku"]][key] = product[key]
                else:
                    # This is a new product - add it
                    existing_by_sku[product["sku"]] = product
            
            # Convert back to list
            updated_products = list(existing_by_sku.values())
            
            # Save the updated products
            save_products(updated_products)
            
            # Update the integration with success
            integration["status"] = "connected"
            integration["config"]["last_sync"] = datetime.datetime.now().isoformat()
            integration["config"]["last_error"] = None
            
            if integration["config"].get("error_count", 0) > 0:
                integration["config"]["error_count"] = 0
            
            # Save the updated integration
            for i, integ in enumerate(integrations):
                if integ.get("id") == integration_id:
                    integrations[i] = integration
                    break
            save_integrations(integrations)
            
            return MessageResponse(
                message=f"Synchronized {len(mapped_products)} products from WooCommerce",
                success=True
            )
        
        # Other integration types would be handled here
        return MessageResponse(
            message=f"Syncing {integration['type']} is not supported yet",
            success=False
        )
        
    except Exception as e:
        # Update the integration with the error
        integration["status"] = "error"
        integration["config"]["last_error"] = str(e)
        integration["config"]["error_count"] = integration["config"].get("error_count", 0) + 1
        
        # Save the updated integration
        for i, integ in enumerate(integrations):
            if integ.get("id") == integration_id:
                integrations[i] = integration
                break
        save_integrations(integrations)
        
        return MessageResponse(
            message=f"Sync failed: {str(e)}",
            success=False
        )

@router.get("/{integration_id}/context", response_model=Dict[str, Any])
async def get_integration_context2(integration_id: str):
    """Get context data for an integration"""
    integration = get_integration_by_id(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Extract context based on integration type
    context = {}
    
    if integration["type"] == "woocommerce":
        # Include relevant WooCommerce context
        context = {
            "store_url": integration["config"].get("url", ""),
            "sync_status": integration["status"],
            "last_sync": integration["config"].get("last_sync"),
            "product_sync_enabled": integration["config"].get("sync_products", True),
            "orders_sync_enabled": integration["config"].get("sync_orders", False),
            "customers_sync_enabled": integration["config"].get("sync_customers", False),
        }
    
    return context
