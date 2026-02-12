from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import databutton as db
import requests
from datetime import datetime
import json
import re

router = APIRouter(prefix="/woocommerce")

# Models
class SyncRequest(BaseModel):
    store_url: str
    consumer_key: str
    consumer_secret: str
    force: bool = False

class SyncResponse(BaseModel):
    success: bool
    message: str
    products_synced: int = 0

class WooCommerceConfig(BaseModel):
    store_url: str
    api_url: str
    consumer_key: str
    consumer_secret: str
    last_sync: Optional[str] = None
    enabled: bool = True
    error_count: int = 0
    last_error: Optional[str] = None
    store_name: str = "Hempex"

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_woocommerce_config(store_id: str = "hempex") -> WooCommerceConfig:
    """Get the WooCommerce API configuration for a specific store"""
    try:
        config = db.storage.json.get(f"woocommerce_config_{sanitize_storage_key(store_id)}", default={})
        if not config:
            # Create default config if it doesn't exist
            config = WooCommerceConfig(
                store_url="https://hempex.com",
                api_url="https://hempex.com/wp-json/wc/v3",
                consumer_key="",
                consumer_secret=""
            ).dict()
            db.storage.json.put(f"woocommerce_config_{sanitize_storage_key(store_id)}", config)
        return WooCommerceConfig(**config)
    except Exception as e:
        print(f"Error getting WooCommerce config: {str(e)}")
        return WooCommerceConfig(
            store_url="https://hempex.com",
            api_url="https://hempex.com/wp-json/wc/v3",
            consumer_key="",
            consumer_secret=""
        )

def save_woocommerce_config(config: WooCommerceConfig, store_id: str = "hempex") -> bool:
    """Save the WooCommerce API configuration"""
    try:
        db.storage.json.put(f"woocommerce_config_{sanitize_storage_key(store_id)}", config.dict())
        return True
    except Exception as e:
        print(f"Error saving WooCommerce config: {str(e)}")
        return False

def fetch_woocommerce_products(store_id: str = "hempex") -> List[Dict]:
    """Fetch products from WooCommerce API"""
    config = get_woocommerce_config(store_id)
    
    if not config.consumer_key or not config.consumer_secret:
        raise ValueError(f"Missing API credentials for {store_id} WooCommerce integration")
    
    products = []
    page = 1
    per_page = 50
    
    while True:
        api_url = f"{config.api_url}/products"
        params = {
            "consumer_key": config.consumer_key,
            "consumer_secret": config.consumer_secret,
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
            raise ValueError(f"Error fetching {store_id} products: {str(e)}")
    
    return products

def map_woocommerce_product(product: Dict, store_id: str = "hempex") -> Dict:
    """Map WooCommerce product to our internal format"""
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
    
    # Get inventory quantity
    inventory_quantity = 0
    try:
        inventory_quantity = int(product.get("stock_quantity", 0))
    except (ValueError, TypeError):
        inventory_quantity = 0
    
    # Map images
    images = []
    for image in product.get("images", []):
        if "src" in image:
            images.append(image["src"])
    
    # Extract attributes for cannabinoid content
    cannabinoids = []
    for attribute in product.get("attributes", []):
        name = attribute.get("name", "").lower()
        if name in ["cbd", "cbd content", "cbd percentage"]:
            try:
                options = attribute.get("options", [])
                if options:
                    value = options[0].replace("%", "").strip()
                    if value and float(value) > 0:
                        cannabinoids.append({
                            "name": "CBD",
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
                        cannabinoids.append({
                            "name": "CBG",
                            "amount": float(value),
                            "unit": "%"
                        })
            except (ValueError, TypeError):
                pass
    
    # Create our product object
    mapped_product = {
        "sku": product.get("sku", f"{store_id}-{product.get('id')}"),
        "name": product.get("name", ""),
        "description": product.get("description", ""),
        "short_description": product.get("short_description", ""),
        "category_id": category_id,
        "category_name": category_name,
        "image_urls": images,
        "cannabinoids": cannabinoids,
        "tga_approved": False,  # Default assumption
        "price": price,
        "regular_price": regular_price if regular_price > 0 else price,
        "sale_price": sale_price if on_sale else None,
        "on_sale": on_sale,
        "inventory_status": inventory_status,
        "inventory_quantity": inventory_quantity,
        "requires_prescription": False,  # Assuming consumer products don't require prescription
        "source": f"{store_id}.com",  # Mark source
        "external_id": str(product.get("id")),
        "external_url": product.get("permalink", "")
    }
    
    # Check if TGA approved in attributes
    for attribute in product.get("attributes", []):
        if attribute.get("name", "").lower() in ["tga approved", "tga compliance"]:
            options = attribute.get("options", [])
            if options and options[0].lower() in ["yes", "true", "approved", "compliant"]:
                mapped_product["tga_approved"] = True
    
    return mapped_product

def sync_woocommerce_products(store_id: str = "hempex") -> Dict[str, Any]:
    """Synchronize products from WooCommerce to local database"""
    from app.apis.product import get_all_products, upsert_product, save_products
    
    config = get_woocommerce_config(store_id)
    try:
        # Fetch products from WooCommerce API
        woo_products = fetch_woocommerce_products(store_id)
        
        # Map to our internal product format
        mapped_products = [map_woocommerce_product(p, store_id) for p in woo_products]
        
        # Get existing products
        existing_products = get_all_products()
        
        # Create dictionary of existing products by SKU
        existing_by_sku = {p.get("sku"): p for p in existing_products}
        
        # Track changes
        added = 0
        updated = 0
        
        # Process each product from WooCommerce
        for product in mapped_products:
            if product["sku"] in existing_by_sku:
                # Update existing product
                update_product = existing_by_sku[product["sku"]].copy()
                
                # Update fields from WooCommerce product
                for key, value in product.items():
                    update_product[key] = value
                
                # Save the updated product
                upsert_product(update_product)
                updated += 1
            else:
                # Add new product
                upsert_product(product)
                added += 1
        
        # Update config with successful sync
        config.last_sync = datetime.utcnow().isoformat()
        config.last_error = None
        config.error_count = 0
        save_woocommerce_config(config, store_id)
        
        return {
            "success": True,
            "message": f"Successfully synchronized products from {config.store_name}. Added: {added}, Updated: {updated}",
            "products_synced": added + updated,
            "added": added,
            "updated": updated
        }
    except Exception as e:
        # Update config with error
        config.last_error = str(e)
        config.error_count += 1
        save_woocommerce_config(config, store_id)
        
        return {
            "success": False,
            "message": f"Error synchronizing products from {config.store_name}: {str(e)}",
            "products_synced": 0
        }

# API Endpoints
@router.get("/health")
def check_health_woocommerce():
    """Check if the WooCommerce integration API is operational"""
    return {"status": "ok", "message": "WooCommerce API is operational"}

@router.get("/config/{store_id}")
def get_config(store_id: str = "hempex"):
    """Get current WooCommerce integration configuration"""
    config = get_woocommerce_config(store_id)
    # Hide sensitive data
    config_data = config.dict()
    if config_data.get("consumer_key"):
        config_data["consumer_key"] = "*" * 8
    if config_data.get("consumer_secret"):
        config_data["consumer_secret"] = "*" * 8
    return config_data

@router.post("/config/{store_id}")
def update_config(config_update: Dict[str, Any], store_id: str = "hempex"):
    """Update WooCommerce integration configuration"""
    current_config = get_woocommerce_config(store_id)
    
    # Update fields that were provided
    for key, value in config_update.items():
        if hasattr(current_config, key):
            setattr(current_config, key, value)
    
    # Save updated config
    success = save_woocommerce_config(current_config, store_id)
    
    return {
        "success": success,
        "message": "Configuration updated successfully" if success else "Failed to update configuration"
    }

@router.post("/sync/{store_id}", response_model=SyncResponse)
def trigger_sync(request: SyncRequest, background_tasks: BackgroundTasks, store_id: str = "hempex"):
    """Trigger synchronization of products from WooCommerce"""
    config = get_woocommerce_config(store_id)
    
    # Check if we have new credentials
    if request.consumer_key and request.consumer_secret:
        config.consumer_key = request.consumer_key
        config.consumer_secret = request.consumer_secret
        
        # Update the store URL if provided
        if request.store_url:
            config.store_url = request.store_url
            # Update the API URL based on the store URL
            if not config.store_url.endswith("/"):
                config.store_url += "/"
            config.api_url = f"{config.store_url}wp-json/wc/v3"
        
        # Save the updated config
        save_woocommerce_config(config, store_id)
    
    # Check if enabled
    if not config.enabled and not request.force:
        return SyncResponse(
            success=False,
            message=f"{config.store_name} integration is disabled. Enable it or use force=true to sync anyway."
        )
    
    # Check if we have credentials
    if not config.consumer_key or not config.consumer_secret:
        return SyncResponse(
            success=False,
            message=f"Missing API credentials for {config.store_name} integration. Please configure the integration first."
        )
    
    # Run sync in background
    background_tasks.add_task(sync_woocommerce_products, store_id)
    
    return SyncResponse(
        success=True,
        message=f"Synchronization with {config.store_name} started in the background. Check logs for progress."
    )

@router.get("/products/{store_id}")
def list_woocommerce_products(store_id: str = "hempex"):
    """List products imported from a specific WooCommerce store"""
    from app.apis.product import get_all_products
    
    all_products = get_all_products()
    store_products = [p for p in all_products if p.get("source") == f"{store_id}.com"]
    
    return {
        "products": store_products,
        "count": len(store_products)
    }

@router.get("/status/{store_id}")
def get_sync_status(store_id: str = "hempex"):
    """Get the current status of the WooCommerce integration"""
    config = get_woocommerce_config(store_id)
    from app.apis.product import get_all_products
    
    all_products = get_all_products()
    store_products = [p for p in all_products if p.get("source") == f"{store_id}.com"]
    
    return {
        "store_name": config.store_name,
        "enabled": config.enabled,
        "last_sync": config.last_sync,
        "products_count": len(store_products),
        "has_error": config.error_count > 0,
        "last_error": config.last_error,
        "connection_status": "error" if config.error_count > 0 else "connected" if config.last_sync else "disconnected"
    }
