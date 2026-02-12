from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends, Header
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import databutton as db
import requests
from datetime import datetime
import json
import re
import hmac
import hashlib
import base64

# Main router for authenticated endpoints
router = APIRouter(prefix="/wordpress")

# Create a separate router for public endpoints that will be included without auth dependencies
public_webhook_router = APIRouter()

# Add the public router to exports
__all__ = ["router", "public_webhook_router"]

# Models
class WebhookEvent(BaseModel):
    topic: str
    resource: str
    id: Optional[str] = None
    action: Optional[str] = None
    data: Dict[str, Any]

class InventoryUpdate(BaseModel):
    sku: str
    inventory_quantity: int
    inventory_status: str

class BatchInventoryUpdate(BaseModel):
    updates: List[InventoryUpdate]

class WebhookResponse(BaseModel):
    success: bool
    message: str

class WebhookVerification(BaseModel):
    challenge: str

class WebhookVerificationResponse(BaseModel):
    challenge: str

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_webhook_secret() -> str:
    """Get the webhook secret from secrets"""
    try:
        return db.secrets.get("WORDPRESS_WEBHOOK_SECRET", "")
    except Exception:
        return ""

def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """Verify the webhook signature using HMAC"""
    if not signature:
        return False
        
    webhook_secret = get_webhook_secret()
    if not webhook_secret:
        print("Warning: WORDPRESS_WEBHOOK_SECRET not configured, skipping signature verification")
        return True
        
    try:
        # Create an HMAC-SHA256 signature of the request body using the secret
        computed_signature = hmac.new(
            webhook_secret.encode(),
            request_body,
            hashlib.sha256
        ).digest()
        
        # Base64 encode the digest
        computed_signature_base64 = base64.b64encode(computed_signature).decode()
        
        # Compare with the signature from the header
        return hmac.compare_digest(computed_signature_base64, signature)
    except Exception as e:
        print(f"Error verifying webhook signature: {e}")
        return False

default_woocommerce_config = {
    "store_url": "https://hempex.com",
    "api_url": "https://hempex.com/wp-json/wc/v3",
    "consumer_key": "",
    "consumer_secret": "",
    "enabled": True,
    "store_name": "Hempex"
}

def get_woocommerce_config(store_id: str = "hempex") -> Dict[str, Any]:
    """Get the WooCommerce API configuration for a specific store"""
    try:
        config = db.storage.json.get(f"woocommerce_config_{sanitize_storage_key(store_id)}", default=default_woocommerce_config)
        return config
    except Exception as e:
        print(f"Error getting WooCommerce config: {str(e)}")
        return default_woocommerce_config

def update_woocommerce_inventory(sku: str, quantity: int, status: str, store_id: str = "hempex") -> bool:
    """Update inventory in WooCommerce"""
    try:
        config = get_woocommerce_config(store_id)
        
        # Skip if not configured
        if not config.get("consumer_key") or not config.get("consumer_secret") or not config.get("enabled"):
            print(f"WooCommerce integration for {store_id} not properly configured or disabled")
            return False
            
        # First, we need to find the product ID in WooCommerce by SKU
        api_url = f"{config['api_url']}/products"
        params = {
            "consumer_key": config["consumer_key"],
            "consumer_secret": config["consumer_secret"],
            "sku": sku
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        products = response.json()
        if not products:
            print(f"Product with SKU {sku} not found in WooCommerce")
            return False
            
        # Use the first matching product
        woo_product = products[0]
        product_id = woo_product["id"]
        
        # Update the inventory in WooCommerce
        update_url = f"{config['api_url']}/products/{product_id}"
        update_data = {
            "stock_quantity": quantity,
            "stock_status": "instock" if status == "in_stock" else "outofstock"
        }
        
        update_response = requests.put(
            update_url, 
            params={
                "consumer_key": config["consumer_key"],
                "consumer_secret": config["consumer_secret"],
            },
            json=update_data
        )
        update_response.raise_for_status()
        
        return True
    except Exception as e:
        print(f"Error updating WooCommerce inventory for SKU {sku}: {str(e)}")
        return False

def batch_update_woocommerce_inventory(updates: List[InventoryUpdate], store_id: str = "hempex") -> Dict[str, Any]:
    """Update inventory for multiple products in WooCommerce"""
    results = []
    success_count = 0
    
    for update in updates:
        success = update_woocommerce_inventory(
            update.sku,
            update.inventory_quantity,
            update.inventory_status,
            store_id
        )
        
        results.append({
            "sku": update.sku,
            "success": success
        })
        
        if success:
            success_count += 1
    
    return {
        "success": len(updates) > 0 and success_count == len(updates),
        "results": results,
        "summary": {
            "total": len(updates),
            "success": success_count,
            "failed": len(updates) - success_count
        }
    }

# Endpoint routes
@router.get("/health")
def check_health_wordpress():
    """Check if the WordPress integration API is operational"""
    return {"status": "ok", "message": "WordPress integration API is operational"}

@public_webhook_router.post("/wordpress/webhook", response_model=WebhookResponse)
async def handle_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_wp_webhook_signature: Optional[str] = Header(None)
):
    """Handle webhook events from WordPress"""
    from app.apis.product import get_product, update_product_inventory
    
    # Get the raw request body for signature verification
    body_bytes = await request.body()
    
    # Skip signature verification in development/testing
    if x_wp_webhook_signature and not verify_webhook_signature(body_bytes, x_wp_webhook_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    try:
        event_data = await request.json()
        event = WebhookEvent(**event_data)
        
        # Handle different webhook topics
        if event.topic == "product" and event.action in ["updated", "created"]:
            # This is a product update/create event
            # Schedule a sync to pull in the product data
            from app.apis.woocommerce import sync_woocommerce_products
            background_tasks.add_task(sync_woocommerce_products)
            
            return WebhookResponse(
                success=True, 
                message=f"Scheduled product sync for {event.resource} with ID {event.id}"
            )
            
        elif event.topic == "order" and event.action == "created":
            # This is a new order event
            # We should update inventory for the ordered items
            order_data = event.data
            line_items = order_data.get("line_items", [])
            
            for item in line_items:
                sku = item.get("sku")
                quantity = item.get("quantity", 0)
                
                if sku and quantity > 0:
                    product = get_product(sku)
                    if product:
                        current_quantity = product.get("inventory_quantity", 0)
                        new_quantity = max(0, current_quantity - quantity)
                        new_status = "in_stock" if new_quantity > 0 else "out_of_stock"
                        
                        update_product_inventory(sku, new_quantity, new_status)
            
            return WebhookResponse(
                success=True, 
                message=f"Processed inventory updates from order {event.id}"
            )
            
        else:
            # Unhandled event type
            return WebhookResponse(
                success=True, 
                message=f"Received unhandled webhook event: {event.topic}/{event.action}"
            )
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        # Return 200 status code even for errors to prevent WordPress from retrying
        return WebhookResponse(
            success=False, 
            message=f"Error processing webhook: {str(e)}"
        )

@public_webhook_router.post("/wordpress/webhook/verification", response_model=WebhookVerificationResponse)
def verify_webhook(verification: WebhookVerification):
    """Verification endpoint for WordPress webhooks"""
    # Simply echo back the challenge for verification
    return WebhookVerificationResponse(challenge=verification.challenge)

@router.post("/inventory/update")
def update_inventory(update: InventoryUpdate, store_id: str = "hempex"):
    """Update inventory for a single product in WordPress"""
    # First update in our system
    from app.apis.product import update_product_inventory
    
    local_success = update_product_inventory(
        update.sku,
        update.inventory_quantity,
        update.inventory_status
    )
    
    if not local_success:
        return {
            "success": False,
            "message": f"Failed to update local inventory for SKU {update.sku}",
            "wordpress_update": False
        }
    
    # Then update in WordPress if local update was successful
    wp_success = update_woocommerce_inventory(
        update.sku,
        update.inventory_quantity,
        update.inventory_status,
        store_id
    )
    
    return {
        "success": local_success and wp_success,
        "message": f"Inventory updated for product {update.sku}",
        "local_update": local_success,
        "wordpress_update": wp_success
    }

@router.post("/inventory/batch-update")
def batch_update_wordpress_inventory(updates: BatchInventoryUpdate, store_id: str = "hempex") -> Dict[str, Any]:
    """Update inventory for multiple products in WordPress"""
    # First update in our system
    from app.apis.product import get_product, update_product_inventory
    
    local_results = []
    local_success_count = 0
    
    for update in updates.updates:
        success = update_product_inventory(
            update.sku,
            update.inventory_quantity,
            update.inventory_status
        )
        
        local_results.append({
            "sku": update.sku,
            "success": success
        })
        
        if success:
            local_success_count += 1
    
    # Then update in WordPress
    wp_results = batch_update_woocommerce_inventory(updates.updates, store_id)
    
    return {
        "success": local_success_count > 0 and wp_results["success"],
        "local_results": local_results,
        "wordpress_results": wp_results["results"],
        "summary": {
            "total": len(updates.updates),
            "local_success": local_success_count,
            "local_failed": len(updates.updates) - local_success_count,
            "wordpress_success": wp_results["summary"]["success"],
            "wordpress_failed": wp_results["summary"]["failed"]
        }
    }
