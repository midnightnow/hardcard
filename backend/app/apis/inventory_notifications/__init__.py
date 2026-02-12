from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import databutton as db
from datetime import datetime
import json
import re

router = APIRouter()

# Model definitions
class NotificationSettingsUpdate(BaseModel):
    email_recipients: List[str] = Field(..., description="Email addresses to receive notifications")
    low_stock_threshold_percentage: int = Field(..., description="Threshold percentage for low stock alerts", ge=1, le=100)
    out_of_stock_enabled: bool = Field(..., description="Enable notifications for out of stock items")
    daily_summary_enabled: bool = Field(..., description="Enable daily inventory summary")
    daily_summary_time: str = Field(..., description="Time to send daily summary (24h format HH:MM)")

class NotificationSettings(NotificationSettingsUpdate):
    category: str = Field(..., description="Category of notification settings")
    updated_at: str = Field(..., description="Last update timestamp")

class EmailNotificationRequest(BaseModel):
    to: List[str] = Field(..., description="Recipients of the email")
    subject: str = Field(..., description="Email subject")
    content_html: str = Field(..., description="HTML content of the email")
    content_text: str = Field(..., description="Plain text content of the email")

class EmailNotificationResponse(BaseModel):
    success: bool = Field(..., description="Whether the email was sent successfully")
    message: str = Field(None, description="Additional information")

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_notification_settings(category: str) -> NotificationSettings:
    """Get notification settings from storage"""
    try:
        data = db.storage.json.get(f"notification_settings_{sanitize_storage_key(category)}")
        return NotificationSettings(**data)
    except FileNotFoundError:
        # Default settings
        default_settings = {
            "category": category,
            "email_recipients": [],
            "low_stock_threshold_percentage": 20,
            "out_of_stock_enabled": True,
            "daily_summary_enabled": False,
            "daily_summary_time": "08:00",
            "updated_at": datetime.now().isoformat()
        }
        db.storage.json.put(f"notification_settings_{sanitize_storage_key(category)}", default_settings)
        return NotificationSettings(**default_settings)

@router.get("/notification-settings")
def get_notification_settings_endpoint() -> Dict[str, Any]:
    """Get notification settings for inventory category"""
    settings = get_notification_settings("inventory")
    return settings.dict()

@router.put("/notification-settings/{category}")
def update_notification_settings(category: str, settings: NotificationSettingsUpdate) -> Dict[str, Any]:
    """Update notification settings for a specific category"""
    if category not in ["inventory", "orders", "marketing"]:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
    
    # Update settings with new values and current timestamp
    updated_settings = NotificationSettings(
        **settings.dict(),
        category=category,
        updated_at=datetime.now().isoformat()
    )
    
    # Save to storage
    db.storage.json.put(f"notification_settings_{sanitize_storage_key(category)}", updated_settings.dict())
    
    return {"success": True, "settings": updated_settings.dict()}

@router.post("/send-inventory-notification")
async def send_inventory_notification(notification_type: str, product_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Send inventory notification email based on notification type"""
    settings = get_notification_settings("inventory")
    
    if not settings.email_recipients:
        return {"success": False, "message": "No email recipients configured"}
    
    subject = ""
    content_html = ""
    content_text = ""
    
    product_name = context.get("product_name", "Unknown Product")
    current_stock = context.get("current_stock", 0)
    threshold = context.get("threshold", 0)
    
    if notification_type == "low_stock":
        subject = f"🟠 Low Stock Alert: {product_name}"
        content_html = f"""
        <h2>Low Stock Alert</h2>
        <p>The following product is running low on inventory:</p>
        <table border="0" cellpadding="8" cellspacing="0" style="border:1px solid #ddd; border-radius:4px;">
            <tr>
                <td><strong>Product:</strong></td>
                <td>{product_name}</td>
            </tr>
            <tr>
                <td><strong>Current Stock:</strong></td>
                <td>{current_stock}</td>
            </tr>
            <tr>
                <td><strong>Threshold:</strong></td>
                <td>{threshold}</td>
            </tr>
        </table>
        <p>Please consider reordering this item soon.</p>
        <p><a href="#" style="display:inline-block; background:#007bff; color:white; padding:10px 15px; text-decoration:none; border-radius:4px;">View Inventory</a></p>
        """
        content_text = f"""Low Stock Alert
        
The following product is running low on inventory:

Product: {product_name}
Current Stock: {current_stock}
Threshold: {threshold}

Please consider reordering this item soon.
"""
    
    elif notification_type == "out_of_stock":
        subject = f"🔴 Out of Stock Alert: {product_name}"
        content_html = f"""
        <h2>Out of Stock Alert</h2>
        <p>The following product is now out of stock:</p>
        <table border="0" cellpadding="8" cellspacing="0" style="border:1px solid #ddd; border-radius:4px;">
            <tr>
                <td><strong>Product:</strong></td>
                <td>{product_name}</td>
            </tr>
            <tr>
                <td><strong>Status:</strong></td>
                <td>Out of Stock (0 items remaining)</td>
            </tr>
        </table>
        <p>Immediate action is required. Please reorder this item.</p>
        <p><a href="#" style="display:inline-block; background:#dc3545; color:white; padding:10px 15px; text-decoration:none; border-radius:4px;">Order Now</a></p>
        """
        content_text = f"""Out of Stock Alert
        
The following product is now out of stock:

Product: {product_name}
Status: Out of Stock (0 items remaining)

Immediate action is required. Please reorder this item.
"""
    
    elif notification_type == "daily_summary":
        products_summary = context.get("products_summary", [])
        low_stock_count = context.get("low_stock_count", 0)
        out_of_stock_count = context.get("out_of_stock_count", 0)
        date = datetime.now().strftime("%Y-%m-%d")
        
        subject = f"📊 Daily Inventory Summary - {date}"
        
        # Build HTML table of low stock items
        products_html = ""
        products_text = ""
        
        if products_summary:
            products_html = "<table border='0' cellpadding='8' cellspacing='0' style='border:1px solid #ddd; border-radius:4px; width:100%;'>"
            products_html += "<tr style='background-color:#f8f9fa;'><th>Product</th><th>Current Stock</th><th>Status</th></tr>"
            
            for product in products_summary:
                status_color = "#dc3545" if product.get("stock_level", 0) == 0 else "#ffc107"
                status_text = "Out of Stock" if product.get("stock_level", 0) == 0 else "Low Stock"
                
                products_html += f"""<tr>
                    <td>{product.get('name', 'Unknown')}</td>
                    <td>{product.get('stock_level', 0)}</td>
                    <td style='color:{status_color};'>{status_text}</td>
                </tr>"""
                
                products_text += f"{product.get('name', 'Unknown')} - {product.get('stock_level', 0)} - {status_text}\n"
            
            products_html += "</table>"
        
        content_html = f"""
        <h2>Daily Inventory Summary - {date}</h2>
        <div style="margin-bottom:20px;">
            <p>Here's a summary of your current inventory status:</p>
            
            <div style="display:flex; margin-bottom:20px;">
                <div style="flex:1; padding:15px; background-color:#fff3cd; border-radius:4px; margin-right:10px; text-align:center;">
                    <h3 style="margin-top:0;">{low_stock_count}</h3>
                    <p style="margin-bottom:0;">Low Stock Items</p>
                </div>
                <div style="flex:1; padding:15px; background-color:#f8d7da; border-radius:4px; text-align:center;">
                    <h3 style="margin-top:0;">{out_of_stock_count}</h3>
                    <p style="margin-bottom:0;">Out of Stock Items</p>
                </div>
            </div>
            
            <h3>Items Requiring Attention:</h3>
            {products_html}
        </div>
        <p><a href="#" style="display:inline-block; background:#007bff; color:white; padding:10px 15px; text-decoration:none; border-radius:4px;">View Full Inventory</a></p>
        """
        
        content_text = f"""Daily Inventory Summary - {date}
        
Here's a summary of your current inventory status:

Low Stock Items: {low_stock_count}
Out of Stock Items: {out_of_stock_count}

Items Requiring Attention:
{products_text}
"""
    
    else:
        return {"success": False, "message": f"Unknown notification type: {notification_type}"}
    
    # Send email notification
    try:
        db.notify.email(
            to=settings.email_recipients,
            subject=subject,
            content_html=content_html,
            content_text=content_text
        )
        return {"success": True, "message": f"Sent {notification_type} notification for product {product_id}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {str(e)}"}

@router.post("/send-test-notification")
async def send_test_notification(notification_type: str) -> Dict[str, Any]:
    """Send a test notification to verify email configuration"""
    settings = get_notification_settings("inventory")
    
    if not settings.email_recipients:
        return {"success": False, "message": "No email recipients configured"}
    
    context = {
        "product_name": "Test Product",
        "current_stock": 5,
        "threshold": 10,
        "products_summary": [
            {"name": "Test Product 1", "stock_level": 5, "threshold": 10},
            {"name": "Test Product 2", "stock_level": 0, "threshold": 5}
        ],
        "low_stock_count": 1,
        "out_of_stock_count": 1
    }
    
    return await send_inventory_notification(notification_type, "test-product-id", context)