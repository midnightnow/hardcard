from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import databutton as db
import firebase_admin
from firebase_admin import firestore
from datetime import datetime
import re
import math

router = APIRouter()

# Initialize Firestore DB
db_firestore = firestore.client()

# Collection constants
COLLECTIONS = {
    "ORDERS": "orders",
    "PRODUCTS": "products",
    "INVENTORY": "inventory"
}


class OrderItem(BaseModel):
    """An item in an order"""
    product_id: str
    product_name: str
    quantity: int
    price: int  # in cents
    subtotal: int  # in cents
    sku: Optional[str] = None
    image_url: Optional[str] = None
    variant: Optional[str] = None


class Address(BaseModel):
    """Shipping or billing address"""
    name: str
    street_address: str
    suburb: str  # city/suburb
    state: str
    postal_code: str
    country: str
    phone: Optional[str] = None


class ShippingDetails(BaseModel):
    """Shipping details for an order"""
    method: str
    cost: int  # in cents
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    tracking_url: Optional[str] = None
    estimated_delivery: Optional[str] = None  # ISO date string


class StatusHistoryEntry(BaseModel):
    """Entry in an order's status history"""
    status: str
    timestamp: str  # ISO date string
    note: Optional[str] = None


class CreateOrderRequest(BaseModel):
    """Request model for creating a new order"""
    user_id: Optional[str] = None
    email: str
    items: List[OrderItem]
    shipping_address: Address
    billing_address: Address
    shipping: ShippingDetails
    payment_method: str
    payment_id: str
    subtotal: int  # in cents
    tax: int  # in cents
    shipping_cost: int  # in cents
    total: int  # in cents
    notes: Optional[str] = None
    status: str = "pending_payment"  # Default initial status


class OrderResponse(BaseModel):
    """Response model for order-related operations"""
    success: bool
    message: str
    order_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@router.post("/create", response_model=OrderResponse)
def create_order(request: CreateOrderRequest) -> OrderResponse:
    """Create a new order in Firestore"""
    try:
        # Generate order ID (could be customized based on requirements)
        now = datetime.utcnow()
        # Generate a random ID since db.utils.generate_id is not available
        import random
        import string
        random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        order_id = f"ORD-{now.strftime('%Y%m%d')}-{random_id}"
        
        # Create the order object
        order_data = {
            "id": order_id,
            "user_id": request.user_id,
            "email": request.email,
            "items": [item.dict() for item in request.items],
            "shipping_address": request.shipping_address.dict(),
            "billing_address": request.billing_address.dict(),
            "shipping": request.shipping.dict(),
            "payment_method": request.payment_method,
            "payment_id": request.payment_id,
            "subtotal": request.subtotal,
            "tax": request.tax,
            "shipping_cost": request.shipping_cost,
            "total": request.total,
            "notes": request.notes,
            "status": request.status,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "status_history": [
                {
                    "status": request.status,
                    "timestamp": now.isoformat(),
                    "note": "Order created"
                }
            ]
        }
        
        # Save to Firestore
        db_firestore.collection(COLLECTIONS["ORDERS"]).document(order_id).set(order_data)
        
        # Update inventory (decrement stock for each item)
        for item in request.items:
            update_inventory(item.product_id, -item.quantity)
        
        # Process loyalty points if user is logged in
        if request.user_id:
            try:
                # Award loyalty points (1 point per $1 spent)
                points_earned = int(math.floor(request.total / 100))  # Convert cents to dollars and round down
                if points_earned > 0:
                    # Import here to avoid circular imports
                    from app.apis.loyalty import add_loyalty_points, get_customer_loyalty
                    
                    # Check if customer exists in loyalty program
                    loyalty_response = get_customer_loyalty(request.user_id)
                    
                    if loyalty_response.success and loyalty_response.data.get("is_enrolled", False):
                        # Customer exists in loyalty program, add points
                        add_loyalty_points(
                            customer_id=request.user_id,
                            request={
                                "points": points_earned,
                                "source": "order",
                                "source_id": order_id,
                                "description": f"Points earned from order {order_id}"
                            }
                        )
                    else:
                        # Customer not in loyalty program, skip points
                        print(f"Customer {request.user_id} not enrolled in loyalty program, skipping points")
            except Exception as loyalty_error:
                print(f"Error processing loyalty points for order {order_id}: {str(loyalty_error)}")
                # Continue processing - loyalty failure shouldn't block order creation
        
        # Send order confirmation email
        try:
            send_order_confirmation(order_id, order_data)
        except Exception as email_error:
            print(f"Error sending confirmation email for order {order_id}: {str(email_error)}")
            # Continue processing - email failure shouldn't block order creation
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} created successfully",
            order_id=order_id,
            data=order_data
        )
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create order: {str(e)}"
        )


@router.get("/get/{order_id}", response_model=OrderResponse)
def get_order(order_id: str) -> OrderResponse:
    """Get an order by ID"""
    try:
        order_ref = db_firestore.collection(COLLECTIONS["ORDERS"]).document(order_id)
        order = order_ref.get()
        
        if not order.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found"
            )
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} retrieved successfully",
            order_id=order_id,
            data=order.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve order: {str(e)}"
        )


class UpdateOrderStatusRequest(BaseModel):
    """Request model for updating an order's status"""
    status: str
    note: Optional[str] = None
    shipping_details: Optional[Dict[str, Any]] = None  # Optional shipping updates


@router.post("/update-status/{order_id}", response_model=OrderResponse)
def update_order_status(order_id: str, request: UpdateOrderStatusRequest) -> OrderResponse:
    """Update an order's status and optionally shipping details"""
    try:
        order_ref = db_firestore.collection(COLLECTIONS["ORDERS"]).document(order_id)
        order = order_ref.get()
        
        if not order.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found"
            )
        
        order_data = order.to_dict()
        now = datetime.utcnow()
        
        # Create status history entry
        status_entry = {
            "status": request.status,
            "timestamp": now.isoformat(),
            "note": request.note or f"Status updated to {request.status}"
        }
        
        # Update fields
        updates = {
            "status": request.status,
            "updated_at": now.isoformat(),
            "status_history": firestore.ArrayUnion([status_entry])
        }
        
        # Update shipping details if provided
        if request.shipping_details:
            # Merge with existing shipping details
            shipping = order_data.get("shipping", {})
            shipping.update(request.shipping_details)
            updates["shipping"] = shipping
        
        # Apply updates
        order_ref.update(updates)
        
        # Get updated order
        updated_order = order_ref.get().to_dict()
        
        # Send status notification email
        if request.status in ["processing", "shipped", "delivered", "cancelled", "refunded"]:
            try:
                send_order_status_notification(order_id, request.status, updated_order)
            except Exception as email_error:
                print(f"Error sending status notification email for order {order_id}: {str(email_error)}")
                # Continue processing - email failure shouldn't block status update
        
        return OrderResponse(
            success=True,
            message=f"Order {order_id} status updated to {request.status}",
            order_id=order_id,
            data=updated_order
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating order status for {order_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update order status: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=OrderResponse)
def get_user_orders(user_id: str) -> OrderResponse:
    """Get all orders for a specific user"""
    try:
        orders_ref = db_firestore.collection(COLLECTIONS["ORDERS"]).where("user_id", "==", user_id)
        orders = [doc.to_dict() for doc in orders_ref.get()]
        
        return OrderResponse(
            success=True,
            message=f"Retrieved {len(orders)} orders for user {user_id}",
            data={"orders": orders}
        )
    except Exception as e:
        print(f"Error retrieving orders for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user orders: {str(e)}"
        )


# Helper functions
def update_inventory(product_id: str, quantity_change: int) -> None:
    """Update inventory levels for a product"""
    inventory_ref = db_firestore.collection(COLLECTIONS["INVENTORY"]).document(product_id)
    inventory = inventory_ref.get()
    
    if inventory.exists:
        # Update existing inventory
        current_stock = inventory.to_dict().get("stock", 0)
        new_stock = max(0, current_stock + quantity_change)  # Prevent negative stock
        
        inventory_ref.update({
            "stock": new_stock,
            "updated_at": datetime.utcnow().isoformat(),
            "stock_history": firestore.ArrayUnion([{
                "change": quantity_change,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "order" if quantity_change < 0 else "restock"
            }])
        })
    else:
        # Create inventory record if it doesn't exist
        stock = max(0, quantity_change) if quantity_change > 0 else 0
        inventory_ref.set({
            "product_id": product_id,
            "stock": stock,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "stock_history": [{
                "change": quantity_change,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": "order" if quantity_change < 0 else "initial"
            }]
        })


def send_order_confirmation(order_id: str, order_data: dict) -> None:
    """Send order confirmation email"""
    # Call the notifications API
    import brain
    
    try:
        brain.send_order_notification({
            "order_id": order_id,
            "customer_email": order_data["email"],
            "notification_type": "confirmation",
            "order_data": order_data
        })
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        # Don't re-raise, just log


def send_order_status_notification(order_id: str, status: str, order_data: dict) -> None:
    """Send order status notification email"""
    # Map status to notification type
    notification_type_map = {
        "processing": "processing",
        "shipped": "shipped",
        "delivered": "delivered",
        "cancelled": "cancelled",
        "refunded": "refunded"
    }
    
    notification_type = notification_type_map.get(status, "status_update")
    
    # Call the notifications API
    import brain
    
    try:
        brain.send_order_notification({
            "order_id": order_id,
            "customer_email": order_data["email"],
            "notification_type": notification_type,
            "order_data": order_data
        })
    except Exception as e:
        print(f"Error sending status notification email: {e}")
        # Don't re-raise, just log
