from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
import databutton as db
import json
import re
import hmac
import hashlib
import base64
from datetime import datetime

# This router is deliberately NOT prefixed to maintain path consistency
router = APIRouter()

# Models
class WebhookVerification(BaseModel):
    """Model for WordPress webhook verification challenge"""
    challenge: str

class WebhookVerificationResponse(BaseModel):
    """Response model for webhook verification"""
    challenge: str

class WebhookResponse(BaseModel):
    """Response model for webhook processing"""
    success: bool
    message: str

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify the webhook signature from WordPress"""
    if not signature:
        return False
        
    try:
        # Get the secret from Databutton secrets
        secret = db.secrets.get("WORDPRESS_WEBHOOK_SECRET")
        if not secret:
            print("WordPress webhook secret not configured")
            return False
            
        # Calculate expected signature
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare with provided signature
        return hmac.compare_digest(expected_sig, signature)
    except Exception as e:
        print(f"Error verifying webhook signature: {str(e)}")
        return False

@router.post("/wordpress/webhook", response_model=WebhookResponse)
async def handle_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_wp_webhook_signature: Optional[str] = Header(None)
):
    """Handle incoming webhook from WordPress"""
    # Get raw payload
    payload = await request.body()
    
    # Verify signature if present
    if x_wp_webhook_signature and not verify_webhook_signature(payload, x_wp_webhook_signature):
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid webhook signature"}
        )
    
    try:
        # Parse the payload
        data = json.loads(payload)
        topic = data.get("topic", "")
        
        # Handle based on topic
        if "product" in topic:
            # Handle product update
            product_id = data.get("id", "")
            if not product_id:
                return {"success": False, "message": "Missing product ID"}
                
            # Store the webhook data for processing
            webhook_key = f"wordpress_webhook_{sanitize_storage_key(str(product_id))}"
            webhook_data = {
                "id": product_id,
                "type": topic,
                "data": data,
                "received_at": datetime.utcnow().isoformat(),
                "processed": False
            }
            
            # Store webhook data
            db.storage.json.put(webhook_key, webhook_data)
            
            # Process in background to avoid webhook timeout
            background_tasks.add_task(process_product_webhook, data)
            
            return {"success": True, "message": f"Received {topic} webhook for product {product_id}"}
            
        elif "order" in topic:
            # Handle order update
            order_id = data.get("id", "")
            if not order_id:
                return {"success": False, "message": "Missing order ID"}
                
            # Store the webhook data
            webhook_key = f"wordpress_webhook_order_{sanitize_storage_key(str(order_id))}"
            webhook_data = {
                "id": order_id,
                "type": topic,
                "data": data,
                "received_at": datetime.utcnow().isoformat(),
                "processed": False
            }
            
            # Store webhook data
            db.storage.json.put(webhook_key, webhook_data)
            
            # Process in background
            background_tasks.add_task(process_order_webhook, data)
            
            return {"success": True, "message": f"Received {topic} webhook for order {order_id}"}
            
        else:
            # Unsupported topic
            return {"success": False, "message": f"Unsupported webhook topic: {topic}"}
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return {
            "success": False,
            "message": f"Error processing webhook: {str(e)}"
        }

def process_product_webhook(product_data: Dict[str, Any]):
    """Process product webhook data (runs in background)"""
    try:
        # Get product ID
        product_id = product_data.get("id", "")
        if not product_id:
            print("Missing product ID in webhook data")
            return
            
        # Get the full product data from WordPress API
        # (In a real implementation, you would call the WP API here)
        
        # For now, just update our inventory
        from app.apis.product import get_product, update_product_inventory
        
        # Get stock information
        stock_quantity = product_data.get("stock_quantity", 0)
        stock_status = product_data.get("stock_status", "")
        
        # Map stock status
        inventory_status = "in_stock" if stock_status == "instock" else "out_of_stock"
        
        # Update inventory
        sku = product_data.get("sku", f"wp-{product_id}")
        success = update_product_inventory(sku, stock_quantity, inventory_status)
        
        print(f"Product webhook processed for {sku}: {success}")
        
        # Mark as processed
        webhook_key = f"wordpress_webhook_{sanitize_storage_key(str(product_id))}"
        try:
            webhook_data = db.storage.json.get(webhook_key)
            webhook_data["processed"] = True
            webhook_data["processed_at"] = datetime.utcnow().isoformat()
            webhook_data["success"] = success
            db.storage.json.put(webhook_key, webhook_data)
        except Exception as e:
            print(f"Error updating webhook status: {str(e)}")
            
    except Exception as e:
        print(f"Error processing product webhook: {str(e)}")

def process_order_webhook(order_data: Dict[str, Any]):
    """Process order webhook data (runs in background)"""
    try:
        # Get order ID
        order_id = order_data.get("id", "")
        if not order_id:
            print("Missing order ID in webhook data")
            return
            
        # Get the order items
        line_items = order_data.get("line_items", [])
        
        # Update inventory for each item
        from app.apis.inventory import inventory_update_item
        from app.apis.product import get_product
        
        for item in line_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)
            if not product_id or not quantity:
                continue
                
            # Get SKU
            sku = item.get("sku")
            if not sku:
                # Try to get from our product database
                product = get_product(f"wp-{product_id}")
                if product:
                    sku = product.get("sku")
                else:
                    continue
            
            # Update inventory
            try:
                inventory_update_item({
                    "product_id": sku,
                    "quantity_change": -quantity,  # Reduce inventory
                    "reason": "order",
                    "reference_id": f"wp-order-{order_id}"
                })
            except Exception as e:
                print(f"Error updating inventory for {sku}: {str(e)}")
        
        # Mark as processed
        webhook_key = f"wordpress_webhook_order_{sanitize_storage_key(str(order_id))}"
        try:
            webhook_data = db.storage.json.get(webhook_key)
            webhook_data["processed"] = True
            webhook_data["processed_at"] = datetime.utcnow().isoformat()
            webhook_data["success"] = True
            db.storage.json.put(webhook_key, webhook_data)
        except Exception as e:
            print(f"Error updating webhook status: {str(e)}")
            
    except Exception as e:
        print(f"Error processing order webhook: {str(e)}")

@router.post("/wordpress/webhook/verification", response_model=WebhookVerificationResponse)
def verify_webhook(verification: WebhookVerification):
    """Verification endpoint for WordPress webhooks"""
    # Simply echo back the challenge
    return {"challenge": verification.challenge}
