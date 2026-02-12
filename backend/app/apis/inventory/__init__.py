from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import smtplib
from email.message import EmailMessage
import os
import uuid
import re
import json
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
import databutton as db

router = APIRouter()

# Helper function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize a storage key to only include alphanumeric characters, dots, hyphens and underscores"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Pydantic models
class InventoryUpdateRequest(BaseModel):
    stock: int = Field(..., description="The current stock count")
    low_stock_threshold: Optional[int] = Field(None, description="Threshold for low stock alerts")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit")
    reorder_quantity: Optional[int] = Field(None, description="Suggested quantity to reorder when low")
    cost_per_unit: Optional[float] = Field(None, description="Cost per unit")
    location: Optional[str] = Field(None, description="Physical storage location")
    notes: Optional[str] = Field(None, description="Additional notes about this inventory item")
    optimal_stock_level: Optional[int] = Field(None, description="Optimal stock level to maintain")
    batch_tracking: Optional[bool] = Field(None, description="Whether to track batch information")

class BatchUpdateRequest(BaseModel):
    batch_id: str = Field(..., description="Unique identifier for the batch")
    quantity: int = Field(..., description="Quantity in this batch")
    expiry_date: Optional[str] = Field(None, description="Expiration date in ISO format")
    received_date: Optional[str] = Field(None, description="Date received in ISO format")
    production_date: Optional[str] = Field(None, description="Production date in ISO format")
    supplier_id: Optional[str] = Field(None, description="ID of the supplier")
    supplier_batch_id: Optional[str] = Field(None, description="Supplier's batch identifier")
    quality_check_passed: Optional[bool] = Field(None, description="Whether quality check passed")
    quality_notes: Optional[str] = Field(None, description="Notes about quality")
    cost_per_unit: Optional[float] = Field(None, description="Cost per unit for this batch")
    
class InventoryResponse(BaseModel):
    product_id: str
    stock: int
    low_stock_threshold: Optional[int] = None
    sku: Optional[str] = None
    reorder_quantity: Optional[int] = None
    cost_per_unit: Optional[float] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    optimal_stock_level: Optional[int] = None
    batch_tracking: Optional[bool] = False
    updated_at: str
    last_checked: Optional[str] = None
    batch_info: Optional[Dict[str, Any]] = None

class BatchInventoryResponse(InventoryResponse):
    batch_info: Dict[str, Any]

class InventoryUpdateResponse(BaseModel):
    product_id: str
    success: bool
    message: str
    inventory: InventoryResponse

class InventoryBatchResponse(BaseModel):
    product_id: str
    batch_id: str
    success: bool
    message: str
    batch_info: Dict[str, Any]

class InventoryAlertModel(BaseModel):
    id: str
    product_id: str
    product_name: str
    type: str  # low_stock, out_of_stock, expiring, expired
    created_at: str
    updated_at: str
    acknowledged: bool
    status: str  # active, resolved
    threshold: int
    current_value: int
    description: str
    batch_id: Optional[str] = None
    task_id: Optional[str] = None

class InventoryAlertsResponse(BaseModel):
    alerts: List[InventoryAlertModel]
    count: int
    active_count: int

class ReorderSuggestion(BaseModel):
    product_id: str
    product_name: str
    current_stock: int
    low_stock_threshold: Optional[int] = None
    suggested_quantity: int
    estimated_cost: Optional[float] = None
    preferred_supplier_id: Optional[str] = None
    preferred_supplier_name: Optional[str] = None
    lead_time_days: Optional[int] = None
    alert_id: Optional[str] = None

class ReorderSuggestionsResponse(BaseModel):
    reorder_suggestions: List[ReorderSuggestion]
    count: int
    timestamp: str

# Endpoints
@router.get("/inventory/{product_id}", response_model=InventoryResponse)
def get_product_inventory(product_id: str, include_batches: bool = False) -> Dict[str, Any]:
    """Get inventory information for a specific product"""
    try:
        # Try to get the product inventory data
        inventory_data_key = f"inventory_{product_id}"
        
        try:
            inventory = db.storage.json.get(sanitize_storage_key(inventory_data_key))
        except FileNotFoundError:
            # Initialize empty inventory if not found
            inventory = {
                "product_id": product_id,
                "stock": 0,
                "updated_at": datetime.utcnow().isoformat(),
                "batch_tracking": False
            }
            
        # Update last checked timestamp
        inventory["last_checked"] = datetime.utcnow().isoformat()
        
        # Save updated timestamp
        db.storage.json.put(sanitize_storage_key(inventory_data_key), inventory)
        
        # Check if batch data should be included
        if include_batches and inventory.get("batch_tracking", False):
            try:
                batch_data_key = f"inventory_batches_{product_id}"
                batch_info = db.storage.json.get(sanitize_storage_key(batch_data_key))
                inventory["batch_info"] = batch_info
            except FileNotFoundError:
                inventory["batch_info"] = {}
        
        return inventory
        
    except Exception as e:
        print(f"Error retrieving inventory for product {product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving inventory information: {str(e)}"
        )

@router.post("/inventory/{product_id}", response_model=InventoryUpdateResponse)
def update_product_inventory(product_id: str, update: InventoryUpdateRequest) -> Dict[str, Any]:
    """Update inventory information for a specific product"""
    try:
        # Get current inventory data
        inventory_data_key = f"inventory_{product_id}"
        
        try:
            current_inventory = db.storage.json.get(sanitize_storage_key(inventory_data_key))
            was_existing = True
        except FileNotFoundError:
            # Initialize new inventory if not found
            current_inventory = {
                "product_id": product_id,
                "stock": 0,
                "updated_at": datetime.utcnow().isoformat()
            }
            was_existing = False
        
        # Get current stock to check for alerts
        previous_stock = current_inventory.get("stock", 0)
        
        # Update inventory data with provided values
        for field, value in update.dict(exclude_unset=True).items():
            current_inventory[field] = value
            
        # Always update timestamp
        current_inventory["updated_at"] = datetime.utcnow().isoformat()
        
        # Save updated inventory
        db.storage.json.put(sanitize_storage_key(inventory_data_key), current_inventory)
        
        # Check if we need to create alerts for stock changes
        new_stock = current_inventory.get("stock", 0)
        threshold = current_inventory.get("low_stock_threshold")
        
        # Only check for threshold alerts if a threshold is set
        if threshold is not None:
            # Check if stock has dropped below threshold
            if new_stock <= threshold and (previous_stock > threshold or not was_existing):
                # Get product name for the alert
                product_name = ""
                try:
                    from app.apis.product import get_product_by_id
                    product = get_product_by_id(product_id)
                    if product:
                        product_name = product.get("name", f"Product {product_id}")
                except Exception:
                    # If we can't get product info, use a generic name
                    product_name = f"Product {product_id}"
                
                # Create alert for low stock
                create_inventory_alert(
                    product_id=product_id, 
                    product_name=product_name,
                    alert_type="low_stock" if new_stock > 0 else "out_of_stock",
                    threshold=threshold,
                    current_value=new_stock
                )
        
        return {
            "product_id": product_id,
            "success": True,
            "message": "Inventory updated successfully",
            "inventory": current_inventory
        }
        
    except Exception as e:
        print(f"Error updating inventory for product {product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating inventory: {str(e)}"
        )

@router.post("/inventory/{product_id}/batch", response_model=InventoryBatchResponse)
def update_batch_inventory(product_id: str, batch: BatchUpdateRequest) -> Dict[str, Any]:
    """Update or add batch information for a product"""
    try:
        # Get current inventory data
        inventory_data_key = f"inventory_{product_id}"
        batch_data_key = f"inventory_batches_{product_id}"
        
        try:
            current_inventory = db.storage.json.get(sanitize_storage_key(inventory_data_key))
        except FileNotFoundError:
            # Initialize new inventory if not found
            current_inventory = {
                "product_id": product_id,
                "stock": 0,
                "batch_tracking": True,
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Enable batch tracking if not already enabled
        current_inventory["batch_tracking"] = True
        
        # Get existing batch data or create new
        try:
            batch_info = db.storage.json.get(sanitize_storage_key(batch_data_key))
        except FileNotFoundError:
            batch_info = {}
        
        # Get previous batch quantity if updating existing batch
        previous_quantity = 0
        if batch.batch_id in batch_info:
            previous_quantity = batch_info[batch.batch_id].get("quantity", 0)
        
        # Update batch info
        batch_data = batch_info.get(batch.batch_id, {})
        for field, value in batch.dict(exclude_unset=True).items():
            batch_data[field] = value
            
        # Add timestamp if new batch
        if batch.batch_id not in batch_info:
            batch_data["added_at"] = datetime.utcnow().isoformat()
            
        # Always update last modified
        batch_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Save the batch data back
        batch_info[batch.batch_id] = batch_data
        db.storage.json.put(sanitize_storage_key(batch_data_key), batch_info)
        
        # Update total inventory stock based on batch changes
        quantity_change = batch.quantity - previous_quantity
        current_inventory["stock"] = max(0, current_inventory.get("stock", 0) + quantity_change)
        current_inventory["updated_at"] = datetime.utcnow().isoformat()
        
        # Save updated inventory
        db.storage.json.put(sanitize_storage_key(inventory_data_key), current_inventory)
        
        # Check for alerts (expiry, low stock)
        if "expiry_date" in batch.dict(exclude_unset=True):
            check_batch_expiry_alerts(product_id, batch.batch_id, batch_info[batch.batch_id])
            
        # Check if total stock is below threshold after update
        threshold = current_inventory.get("low_stock_threshold")
        if threshold is not None and current_inventory["stock"] <= threshold:
            # Get product name for the alert
            product_name = ""
            try:
                from app.apis.product import get_product_by_id
                product = get_product_by_id(product_id)
                if product:
                    product_name = product.get("name", f"Product {product_id}")
            except Exception:
                # If we can't get product info, use a generic name
                product_name = f"Product {product_id}"
            
            # Create alert for low stock
            create_inventory_alert(
                product_id=product_id, 
                product_name=product_name,
                alert_type="low_stock" if current_inventory["stock"] > 0 else "out_of_stock",
                threshold=threshold,
                current_value=current_inventory["stock"]
            )
        
        return {
            "product_id": product_id,
            "batch_id": batch.batch_id,
            "success": True,
            "message": "Batch information updated successfully",
            "batch_info": batch_info[batch.batch_id]
        }
        
    except Exception as e:
        print(f"Error updating batch for product {product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating batch information: {str(e)}"
        )

@router.get("/inventory/alerts", response_model=InventoryAlertsResponse)
def get_inventory_alerts(status: Optional[str] = None, alert_type: Optional[str] = None, product_id: Optional[str] = None) -> Dict[str, Any]:
    """Get inventory alerts"""
    try:
        # Get all alerts
        alerts_key = "inventory_alerts"
        
        try:
            all_alerts = db.storage.json.get(sanitize_storage_key(alerts_key))
        except FileNotFoundError:
            all_alerts = []
        
        # Filter alerts based on parameters
        filtered_alerts = all_alerts
        
        if status:
            filtered_alerts = [alert for alert in filtered_alerts if alert.get("status") == status]
            
        if alert_type:
            filtered_alerts = [alert for alert in filtered_alerts if alert.get("type") == alert_type]
            
        if product_id:
            filtered_alerts = [alert for alert in filtered_alerts if alert.get("product_id") == product_id]
        
        # Count active alerts
        active_count = len([alert for alert in all_alerts if alert.get("status") == "active"])
        
        return {
            "alerts": filtered_alerts,
            "count": len(filtered_alerts),
            "active_count": active_count
        }
        
    except Exception as e:
        print(f"Error retrieving inventory alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving alerts: {str(e)}"
        )

@router.post("/inventory/alerts/{alert_id}/acknowledge")
def acknowledge_inventory_alert(alert_id: str) -> Dict[str, Any]:
    """Acknowledge an inventory alert"""
    try:
        # Get all alerts
        alerts_key = "inventory_alerts"
        
        try:
            all_alerts = db.storage.json.get(sanitize_storage_key(alerts_key))
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="No alerts found"
            )
        
        # Find the alert by ID
        alert_found = False
        for alert in all_alerts:
            if alert.get("id") == alert_id:
                alert["acknowledged"] = True
                alert["updated_at"] = datetime.utcnow().isoformat()
                alert_found = True
                break
                
        if not alert_found:
            raise HTTPException(
                status_code=404,
                detail=f"Alert with ID {alert_id} not found"
            )
        
        # Save updated alerts
        db.storage.json.put(sanitize_storage_key(alerts_key), all_alerts)
        
        return {
            "success": True,
            "message": "Alert acknowledged successfully",
            "alert_id": alert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error acknowledging alert: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error acknowledging alert: {str(e)}"
        )

@router.post("/inventory/alerts/{alert_id}/resolve")
def resolve_inventory_alert(alert_id: str) -> Dict[str, Any]:
    """Resolve an inventory alert"""
    try:
        # Get all alerts
        alerts_key = "inventory_alerts"
        
        try:
            all_alerts = db.storage.json.get(sanitize_storage_key(alerts_key))
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="No alerts found"
            )
        
        # Find the alert by ID
        alert_found = False
        for alert in all_alerts:
            if alert.get("id") == alert_id:
                alert["status"] = "resolved"
                alert["updated_at"] = datetime.utcnow().isoformat()
                alert_found = True
                break
                
        if not alert_found:
            raise HTTPException(
                status_code=404,
                detail=f"Alert with ID {alert_id} not found"
            )
        
        # Save updated alerts
        db.storage.json.put(sanitize_storage_key(alerts_key), all_alerts)
        
        return {
            "success": True,
            "message": "Alert resolved successfully",
            "alert_id": alert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resolving alert: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error resolving alert: {str(e)}"
        )

@router.get("/inventory/reorder-suggestions", response_model=ReorderSuggestionsResponse)
def get_reorder_suggestions() -> Dict[str, Any]:
    """Get suggestions for products that need reordering"""
    try:
        # Get active alerts
        alerts_response = get_inventory_alerts(status="active", alert_type="low_stock")
        low_stock_alerts = alerts_response.get("alerts", [])
        
        # Also get out of stock alerts
        out_of_stock_response = get_inventory_alerts(status="active", alert_type="out_of_stock")
        out_of_stock_alerts = out_of_stock_response.get("alerts", [])
        
        # Combine alerts
        all_relevant_alerts = low_stock_alerts + out_of_stock_alerts
        
        # Create suggestions
        suggestions = []
        
        # Get supplier information if available
        supplier_map = {}
        try:
            from app.apis.supplier import list_suppliers
            suppliers_response = list_suppliers()
            for supplier in suppliers_response.get("suppliers", []):
                supplier_map[supplier.get("id")] = supplier
        except Exception:
            # Continue without supplier info if not available
            pass
        
        # Create suggestion for each alert
        for alert in all_relevant_alerts:
            product_id = alert.get("product_id")
            product_name = alert.get("product_name")
            current_stock = alert.get("current_value", 0)
            threshold = alert.get("threshold", 0)
            
            # Skip if no product ID
            if not product_id:
                continue
                
            # Get inventory to check reorder details
            inventory = get_product_inventory(product_id)
            
            # Calculate reorder quantity
            reorder_qty = calculate_reorder_quantity(product_id)
            
            # Get supplier info if available
            supplier_id = None
            supplier_name = None
            
            # Try to get supplier from batch info
            try:
                inventory_with_batches = get_product_inventory(product_id, include_batches=True)
                
                # Find the most recent batch with supplier information
                for batch_data in inventory.get("batch_info", {}).values():
                    if batch_data.get("supplier_id"):
                        supplier_id = batch_data.get("supplier_id")
                        supplier = supplier_map.get(supplier_id, {})
                        supplier_name = supplier.get("name")
                        break
            except Exception as e:
                print(f"Error getting batch supplier info: {e}")
            
            suggestions.append({
                "product_id": product_id,
                "product_name": product_name, # Use the product_name from alert
                "current_stock": inventory.get("stock", 0),
                "low_stock_threshold": inventory.get("low_stock_threshold"),
                "suggested_quantity": reorder_qty,
                "estimated_cost": reorder_qty * inventory.get("cost_per_unit", 0) if inventory.get("cost_per_unit") else None,
                "preferred_supplier_id": supplier_id,
                "preferred_supplier_name": supplier_name,
                "lead_time_days": supplier_map.get(supplier_id, {}).get("lead_time_days") if supplier_id else None,
                "alert_id": alert.get("id")
            })
        
        # Sort by current stock level (lowest first)
        suggestions.sort(key=lambda x: x.get("current_stock", float('inf')))
        
        return {
            "reorder_suggestions": suggestions,
            "count": len(suggestions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"Error generating reorder suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate reorder suggestions: {str(e)}"
        )

# Helper functions for automation and notifications
def send_low_stock_notification(product_id: str, product_name: str, current_stock: int, threshold: int, alert_id: str) -> bool:
    """Send an email notification for low stock"""
    try:
        # Get email settings from db.secrets
        email_to = db.secrets.get("EMAIL_NOTIFICATION_RECIPIENT")
        email_from = db.secrets.get("EMAIL_NOTIFICATION_SENDER")
        smtp_server = db.secrets.get("SMTP_SERVER") 
        smtp_port = int(db.secrets.get("SMTP_PORT") or "587")
        smtp_username = db.secrets.get("SMTP_USERNAME")
        smtp_password = db.secrets.get("SMTP_PASSWORD")
        
        # Skip if email settings not available
        if not email_to or not smtp_server:
            print("Email notification settings not configured, skipping")
            return False
            
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f"Hempex Inventory Alert: {product_name}"
        msg['From'] = email_from or smtp_username
        msg['To'] = email_to
        
        # Determine alert severity
        severity = "Out of Stock" if current_stock == 0 else "Low Stock"
        
        # Create email content
        email_content = f"""
        <html>
        <body>
            <h2>Hempex Inventory Alert: {severity}</h2>
            <p>This is an automated notification from the Hempex inventory management system.</p>
            
            <div style="border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <h3>Alert Details</h3>
                <p><strong>Product:</strong> {product_name}</p>
                <p><strong>Product ID:</strong> {product_id}</p>
                <p><strong>Current Stock:</strong> {current_stock}</p>
                <p><strong>Threshold:</strong> {threshold}</p>
                <p><strong>Alert ID:</strong> {alert_id}</p>
                <p><strong>Status:</strong> Active</p>
            </div>
            
            <p>Please take appropriate action to replenish inventory for this product.</p>
            
            <p>You can view all current inventory alerts in the Hempex Inventory Management dashboard.</p>
            
            <p>This is an automated message. Please do not reply to this email.</p>
        </body>
        </html>
        """
        
        msg.set_content("Hempex Inventory Alert: Please check your inventory levels.")
        msg.add_alternative(email_content, subtype='html')
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_username and smtp_password:
                server.starttls()
                server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
        print(f"Sent low stock notification email for product {product_id}")
        return True
        
    except Exception as e:
        print(f"Error sending email notification: {e}")
        return False

# Helper functions for automation and notifications
def create_inventory_alert(product_id: str, product_name: str, alert_type: str, 
                           threshold: int, current_value: int, batch_id: str = None) -> str:
    """Create a new inventory alert"""
    try:
        # Generate alert ID
        alert_id = f"INV-{str(uuid.uuid4())[:8]}"
        
        # Create alert description
        if alert_type == "low_stock":
            description = f"Product has only {current_value} units remaining in stock, below the threshold of {threshold}."
        elif alert_type == "out_of_stock":
            description = f"Product is completely out of stock (0 units remaining). Threshold is {threshold}."
        elif alert_type == "expiring":
            description = f"Product batch is expiring soon."
        elif alert_type == "expired":
            description = f"Product batch has expired and should be removed from inventory."
        else:
            description = f"Inventory alert: {alert_type}"
            
        # Create alert object
        alert = {
            "id": alert_id,
            "product_id": product_id,
            "product_name": product_name,
            "type": alert_type,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "acknowledged": False,
            "status": "active",
            "threshold": threshold,
            "current_value": current_value,
            "description": description
        }
        
        # Add batch ID if provided
        if batch_id:
            alert["batch_id"] = batch_id
            
        # Get existing alerts
        alerts_key = "inventory_alerts"
        try:
            alerts = db.storage.json.get(sanitize_storage_key(alerts_key))
        except FileNotFoundError:
            alerts = []
            
        # Add the new alert
        alerts.append(alert)
        
        # Save the updated alerts
        db.storage.json.put(sanitize_storage_key(alerts_key), alerts)
        
        # Try to send notification
        try:
            # Create automatic task for this alert
            task_id = create_inventory_task(
                product_id=product_id, 
                product_name=product_name,
                current_stock=current_value,
                threshold=threshold,
                alert_id=alert_id
            )
            
            # Update alert with task ID if created
            if task_id:
                alert["task_id"] = task_id
                # Update alert in storage
                for idx, existing_alert in enumerate(alerts):
                    if existing_alert["id"] == alert_id:
                        alerts[idx] = alert
                        break
                db.storage.json.put(sanitize_storage_key(alerts_key), alerts)
        except Exception as task_error:
            print(f"Error creating inventory task: {task_error}")
        
        return alert_id
    except Exception as e:
        print(f"Error creating inventory alert: {e}")
        return None
        
def check_batch_expiry_alerts(product_id: str, batch_id: str, batch_data: Dict[str, Any]) -> None:
    """Check if batch is expiring soon and create alerts if needed"""
    try:
        if "expiry_date" not in batch_data:
            return  # No expiry date to check
            
        # Parse expiry date
        try:
            expiry_date = datetime.fromisoformat(batch_data["expiry_date"].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return  # Invalid date format
            
        # Current date for comparison
        now = datetime.utcnow()
        
        # Calculate days until expiry
        days_until_expiry = (expiry_date - now).days
        
        # Create alerts based on proximity to expiry
        product_name = ""
        try:
            from app.apis.product import get_product_by_id
            product = get_product_by_id(product_id)
            if product:
                product_name = product.get("name", f"Product {product_id}")
        except Exception:
            # If we can't get product info, use a generic name
            product_name = f"Product {product_id}"
        
        # Check if expired
        if days_until_expiry <= 0:
            # Create expired alert
            create_inventory_alert(
                product_id=product_id,
                product_name=product_name,
                alert_type="expired",
                threshold=0,  # Not relevant for expiry
                current_value=days_until_expiry,
                batch_id=batch_id
            )
        elif days_until_expiry <= 30:  # Alert for products expiring within 30 days
            # Create expiring alert
            create_inventory_alert(
                product_id=product_id,
                product_name=product_name,
                alert_type="expiring",
                threshold=30,  # 30 day threshold
                current_value=days_until_expiry,
                batch_id=batch_id
            )
    except Exception as e:
        print(f"Error checking batch expiry: {e}")

def create_inventory_task(product_id: str, product_name: str, current_stock: int, 
                           threshold: int, suggested_reorder: int = 0, alert_id: str = "") -> str:
    """Create an automation task for inventory alert"""
    try:
        # Create task ID
        task_id = f"T-{str(uuid.uuid4())[:8]}"
        
        # Set task properties based on stock status
        if current_stock == 0:
            title = f"Out of Stock: {product_name}"
            priority = "high"
            suggested_action = "Create a purchase order immediately or contact supplier for restock options."
        else:
            title = f"Low Stock Alert: {product_name}"
            priority = "medium"
            suggested_action = "Review current stock and consider reordering."
        
        # Create task object
        task = {
            "id": task_id,
            "title": title,
            "description": f"The inventory for {product_name} (ID: {product_id}) is {'out of stock' if current_stock == 0 else 'running low'}. Current stock: {current_stock}, Threshold: {threshold}.",
            "status": "pending",
            "category": "inventory",
            "source": "inventory_alert",
            "createdAt": datetime.utcnow().isoformat(),
            "priority": priority,
            "suggestedAction": suggested_action,
            "autoMatchConfidence": 100,
            "relatedRules": [],
            "metadata": {
                "alert_id": alert_id,
                "product_id": product_id,
                "current_stock": current_stock,
                "threshold": threshold,
                "suggested_reorder": suggested_reorder,
                "type": "stock_alert"
            }
        }
        
        # Get existing tasks
        try:
            tasks = db.storage.json.get(sanitize_storage_key("automation_tasks"))
        except FileNotFoundError:
            tasks = []
        
        # Add new task
        tasks.append(task)
        
        # Save updated tasks
        db.storage.json.put(sanitize_storage_key("automation_tasks"), tasks)
        
        # Check automation rules to see if we should trigger any automated actions
        try:
            from app.apis.automation import get_automation_rules
            
            # Get inventory automation rules
            rules = get_automation_rules("inventory")
            
            # Filter for enabled rules that match our conditions
            for rule in rules:
                if not rule.get("enabled", False):
                    continue
                    
                conditions = rule.get("conditions", {})
                
                # Check if this rule applies to our alert
                match = False
                
                # Rule for out of stock
                if conditions.get("type") == "inventory" and conditions.get("operator") == "equals" and conditions.get("value") == 0 and current_stock == 0:
                    match = True
                
                # Rule for below threshold
                elif conditions.get("type") == "inventory" and conditions.get("operator") == "below_threshold":
                    rule_threshold = conditions.get("threshold", 0)
                    if current_stock <= rule_threshold:
                        match = True
                
                if match:
                    # Record rule match
                    task["relatedRules"].append(rule.get("id"))
                    
                    # Process actions
                    for action in rule.get("actions", []):
                        action_type = action.get("type")
                        
                        # Send notification
                        if action_type == "send_notification":
                            try:
                                recipients = action.get("recipients", [])
                                for recipient in recipients:
                                    send_low_stock_notification(
                                        product_id=product_id,
                                        product_name=product_name,
                                        current_stock=current_stock,
                                        threshold=threshold,
                                        alert_id=alert_id
                                    )
                            except Exception as notify_error:
                                print(f"Error sending notification from rule: {notify_error}")
                        
                        # Create purchase order
                        elif action_type == "create_purchase_order":
                            # Get suggested reorder quantity
                            suggested_reorder = calculate_reorder_quantity(product_id)
                            if suggested_reorder > 0:
                                try:
                                    # Try to create a purchase order
                                    auto_create_purchase_order(
                                        product_id=product_id,
                                        product_name=product_name,
                                        quantity=suggested_reorder,
                                        alert_id=alert_id,
                                        task_id=task_id
                                    )
                                except Exception as po_error:
                                    print(f"Error auto-creating purchase order: {po_error}")
        except Exception as rules_error:
            print(f"Error processing automation rules: {rules_error}")
        
        return task_id
    
    except Exception as e:
        print(f"Error creating inventory task: {e}")
        return None

def auto_create_purchase_order(product_id: str, product_name: str, quantity: int, alert_id: str, task_id: str) -> bool:
    """Automatically create a purchase order based on inventory alert"""
    try:
        # Get supplier information
        supplier_id = None
        supplier_name = "Preferred Supplier"  # Default fallback
        
        try:
            # First check if we have batch info with supplier records
            inventory = get_product_inventory(product_id, include_batches=True)
            
            if inventory.get("batch_tracking", False) and inventory.get("batch_info"):
                # Find most recent batch with supplier info
                for batch_data in inventory.get("batch_info", {}).values():
                    if batch_data.get("supplier_id"):
                        supplier_id = batch_data.get("supplier_id")
                        break
                        
            # If we found a supplier ID, try to get supplier details
            if supplier_id:
                try:
                    from app.apis.supplier import get_supplier_by_id
                    supplier = get_supplier_by_id(supplier_id)
                    if supplier:
                        supplier_name = supplier.get("name", "Unknown Supplier")
                except Exception:
                    # Use fallback name if supplier API not available
                    pass
                    
        except Exception as inventory_error:
            print(f"Error getting supplier info: {inventory_error}")
        
        # Create a purchase order
        try:
            from app.apis.purchase_order import create_purchase_order
            
            order_data = {
                "supplier_id": supplier_id,
                "supplier_name": supplier_name if supplier_id else "Automatic Reorder",
                "status": "draft",
                "items": [
                    {
                        "product_id": product_id,
                        "product_name": product_name,
                        "quantity": quantity,
                        "notes": f"Auto-generated from inventory alert {alert_id}"
                    }
                ],
                "notes": f"Automatically created by inventory automation system. Related task: {task_id}",
                "metadata": {
                    "source": "inventory_automation",
                    "alert_id": alert_id,
                    "task_id": task_id
                }
            }
            
            # Create the order
            order_response = create_purchase_order(order_data)
            
            # Update the automation task with the order ID
            if order_response.get("success") and order_response.get("order_id"):
                # Get tasks
                tasks_key = "automation_tasks"
                try:
                    tasks = db.storage.json.get(sanitize_storage_key(tasks_key))
                    
                    # Find and update the task
                    for task in tasks:
                        if task.get("id") == task_id:
                            task["metadata"]["purchase_order_id"] = order_response.get("order_id")
                            task["metadata"]["purchase_order_status"] = "created"
                            break
                            
                    # Save updated tasks
                    db.storage.json.put(sanitize_storage_key(tasks_key), tasks)
                    
                except FileNotFoundError:
                    pass
                
            return order_response.get("success", False)
            
        except ImportError:
            # Purchase order API not available
            print("Purchase order module not available to create automatic orders")
            return False
            
    except Exception as e:
        print(f"Error auto-creating purchase order: {e}")
        return False

def send_low_stock_notification(product_id: str, product_name: str, current_stock: int, 
                               threshold: int, alert_id: str) -> bool:
    """Send email notification for low stock alert"""
    try:
        # Get notification settings from storage
        notification_settings_key = "notification_settings"
        try:
            settings = db.storage.json.get(sanitize_storage_key(notification_settings_key))
        except FileNotFoundError:
            # Default settings
            settings = {
                "inventory_notifications": {
                    "enabled": True,
                    "recipients": ["inventory@hempex.com"],
                    "low_stock_threshold": "all"  # all, critical, none
                }
            }
            db.storage.json.put(notification_settings_key, settings)
        
        # Check if notifications are enabled
        if not settings.get("inventory_notifications", {}).get("enabled", False):
            return False
            
        # Check threshold settings
        threshold_setting = settings.get("inventory_notifications", {}).get("low_stock_threshold", "all")
        if threshold_setting == "none":
            return False
        if threshold_setting == "critical" and current_stock > 0:
            return False
            
        # Get recipients
        recipients = settings.get("inventory_notifications", {}).get("recipients", [])
        if not recipients:
            return False
            
        # Build email content
        stock_status = "OUT OF STOCK" if current_stock == 0 else "LOW STOCK"
        subject = f"{stock_status} ALERT: {product_name}"
        
        # HTML content for email
        html_content = f"""<html>
            <body style="font-family: sans-serif; line-height: 1.5; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: {'#cc0000' if current_stock == 0 else '#ff9900'}; margin-bottom: 20px;">{stock_status} ALERT</h1>
                    <p>This is an automated notification from your inventory management system.</p>
                    <div style="background-color: #f8f8f8; border-left: 4px solid {'#cc0000' if current_stock == 0 else '#ff9900'}; padding: 15px; margin: 20px 0;">
                        <p><strong>Product:</strong> {product_name} ({product_id})</p>
                        <p><strong>Current Stock:</strong> {current_stock}</p>
                        <p><strong>Threshold Level:</strong> {threshold}</p>
                        <p><strong>Alert ID:</strong> {alert_id}</p>
                    </div>
                    <p>Please take appropriate action to replenish inventory.</p>
                    <p><a href="https://app.hempex.com/inventory-management" style="display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View in Inventory Management</a></p>
                </div>
            </body>
        </html>"""
        
        # Plain text content as fallback
        text_content = f"""{stock_status} ALERT

Product: {product_name} ({product_id})
Current Stock: {current_stock}
Threshold Level: {threshold}
Alert ID: {alert_id}

Please take appropriate action to replenish inventory.
View in Inventory Management: https://app.hempex.com/inventory-management
"""
        
        # Send the email
        for recipient in recipients:
            try:
                # Try to use the notifications API if available
                try:
                    from app.apis.notifications import send_email
                    email_notification = {
                        "customer_email": recipient,
                        "subject": subject,
                        "content_html": html_content,
                        "content_text": text_content
                    }
                    send_email(email_notification)
                except ImportError:
                    # Fall back to db.notify if notifications API not available
                    db.notify.email(
                        to=recipient,
                        subject=subject,
                        content_html=html_content,
                        content_text=text_content
                    )
            except Exception as email_error:
                print(f"Error sending email to {recipient}: {email_error}")
        
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False

def calculate_reorder_quantity(product_id: str) -> int:
    """Calculate the suggested reorder quantity for a product"""
    try:
        inventory = get_product_inventory(product_id)
        
        # Determine suggested reorder quantity
        if inventory.get("reorder_quantity"):
            reorder_qty = inventory.get("reorder_quantity")
        elif inventory.get("optimal_stock_level"):
            reorder_qty = inventory.get("optimal_stock_level") - inventory.get("stock", 0)
        else:
            # Default to twice the current stock or at least 10 units
            reorder_qty = max(inventory.get("stock", 0) * 2, 10)
            
        return max(0, reorder_qty)
    except Exception as e:
        print(f"Error calculating reorder quantity: {e}")
        return 10  # Default fallback value