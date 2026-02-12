from fastapi import APIRouter, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
import databutton as db
from datetime import datetime, timedelta
import re

router = APIRouter(prefix="/purchase-order")

# Models
class POLineItem(BaseModel):
    """Model for purchase order line item"""
    product_id: str
    product_name: str
    sku: Optional[str] = None
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    unit_of_measure: str = "ea"  # ea, kg, liter, etc.
    notes: Optional[str] = None
    supplier_product_code: Optional[str] = None

    @property
    def total_price(self) -> float:
        return self.quantity * self.unit_price

class PurchaseOrderStatus(str):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    PLACED = "placed"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"

class PurchaseOrderBase(BaseModel):
    """Base model for purchase order"""
    supplier_id: str
    supplier_name: str
    order_date: Optional[str] = None
    expected_delivery_date: Optional[str] = None
    status: str = PurchaseOrderStatus.DRAFT
    items: List[POLineItem]
    shipping_address: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None  # External reference number

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = [
            PurchaseOrderStatus.DRAFT,
            PurchaseOrderStatus.PENDING,
            PurchaseOrderStatus.APPROVED,
            PurchaseOrderStatus.PLACED,
            PurchaseOrderStatus.PARTIALLY_RECEIVED,
            PurchaseOrderStatus.RECEIVED,
            PurchaseOrderStatus.CANCELLED
        ]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @property
    def total_amount(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)

class ReceiveItemRequest(BaseModel):
    """Model for receiving line items"""
    line_item_index: int
    quantity_received: int = Field(..., gt=0)
    batch_lot_number: Optional[str] = None
    expiry_date: Optional[str] = None
    quality_check_passed: bool = True
    quality_notes: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    """Model for creating a purchase order"""
    pass

class PurchaseOrderUpdate(BaseModel):
    """Model for updating a purchase order"""
    supplier_id: Optional[str] = None
    supplier_name: Optional[str] = None
    order_date: Optional[str] = None
    expected_delivery_date: Optional[str] = None
    status: Optional[str] = None
    items: Optional[List[POLineItem]] = None
    shipping_address: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    reference_number: Optional[str] = None

class ReceiptRecord(BaseModel):
    """Model for tracking receipt of items"""
    receipt_date: str
    line_item_index: int
    product_id: str
    product_name: str
    quantity_received: int
    batch_lot_number: Optional[str] = None
    expiry_date: Optional[str] = None
    quality_check_passed: bool
    quality_notes: Optional[str] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    """Response model for purchase order information"""
    id: str
    po_number: str
    created_at: str
    updated_at: str
    receipts: List[ReceiptRecord] = []

class PurchaseOrderListResponse(BaseModel):
    """Response model for listing purchase orders"""
    orders: List[PurchaseOrderResponse]
    total_count: int

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_all_purchase_orders() -> List[Dict[str, Any]]:
    """Get all purchase orders from storage"""
    try:
        po_key = "purchase_orders"
        orders = db.storage.json.get(po_key, default=[])
        return orders
    except Exception as e:
        print(f"Error getting purchase orders: {str(e)}")
        return []

def get_purchase_order(order_id: str) -> Optional[Dict[str, Any]]:
    """Get purchase order by ID"""
    try:
        orders = get_all_purchase_orders()
        for order in orders:
            if order.get("id") == order_id:
                return order
        return None
    except Exception as e:
        print(f"Error getting purchase order: {str(e)}")
        return None

def save_purchase_orders(orders: List[Dict[str, Any]]) -> bool:
    """Save all purchase orders to storage"""
    try:
        po_key = "purchase_orders"
        db.storage.json.put(po_key, orders)
        return True
    except Exception as e:
        print(f"Error saving purchase orders: {str(e)}")
        return False

def generate_po_number() -> str:
    """Generate a new purchase order number"""
    try:
        orders = get_all_purchase_orders()
        # Format: PO-YYYY-MM-XXXX where XXXX is sequential
        now = datetime.utcnow()
        year_month = now.strftime("%Y-%m")
        
        # Count orders from this year-month
        count = sum(1 for o in orders if o.get("po_number", "").startswith(f"PO-{year_month}"))
        
        return f"PO-{year_month}-{count+1:04d}"
    except Exception as e:
        print(f"Error generating PO number: {str(e)}")
        # Fallback format
        return f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"      

def create_or_update_purchase_order(order_data: Dict[str, Any], order_id: Optional[str] = None) -> Dict[str, Any]:
    """Create or update a purchase order"""
    try:
        orders = get_all_purchase_orders()
        now = datetime.utcnow().isoformat()
        
        # Calculate total amount
        total = 0
        for item in order_data.get("items", []):
            total += item.get("quantity", 0) * item.get("unit_price", 0)
        
        # If updating existing order
        if order_id:
            for i, order in enumerate(orders):
                if order.get("id") == order_id:
                    # Update existing order
                    for key, value in order_data.items():
                        orders[i][key] = value
                    
                    orders[i]["updated_at"] = now
                    orders[i]["total_amount"] = total
                    save_purchase_orders(orders)
                    return orders[i]
            raise ValueError(f"Purchase order with ID {order_id} not found")
        
        # Create new order
        new_order = {
            **order_data,
            "id": f"po_{len(orders) + 1}",
            "po_number": generate_po_number(),
            "created_at": now,
            "updated_at": now,
            "receipts": [],
            "total_amount": total
        }
        
        # Set order date if not provided
        if "order_date" not in new_order or not new_order["order_date"]:
            new_order["order_date"] = now
        
        orders.append(new_order)
        save_purchase_orders(orders)
        return new_order
    except Exception as e:
        print(f"Error creating/updating purchase order: {str(e)}")
        raise

def record_item_receipt(order_id: str, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Record receipt of items for a purchase order"""
    try:
        orders = get_all_purchase_orders()
        now = datetime.utcnow().isoformat()
        
        for i, order in enumerate(orders):
            if order.get("id") == order_id:
                # Validate line item index
                line_item_index = receipt_data.get("line_item_index")
                if line_item_index < 0 or line_item_index >= len(order.get("items", [])):
                    raise ValueError(f"Invalid line item index: {line_item_index}")
                
                # Get the line item
                line_item = order["items"][line_item_index]
                
                # Create receipt record
                receipt = {
                    "receipt_date": now,
                    "line_item_index": line_item_index,
                    "product_id": line_item["product_id"],
                    "product_name": line_item["product_name"],
                    "quantity_received": receipt_data["quantity_received"],
                    "batch_lot_number": receipt_data.get("batch_lot_number"),
                    "expiry_date": receipt_data.get("expiry_date"),
                    "quality_check_passed": receipt_data.get("quality_check_passed", True),
                    "quality_notes": receipt_data.get("quality_notes")
                }
                
                # Initialize receipts array if it doesn't exist
                if "receipts" not in order:
                    order["receipts"] = []
                
                # Add receipt record
                order["receipts"].append(receipt)
                
                # Update inventory if quality check passed
                if receipt["quality_check_passed"]:
                    try:
                        from app.apis.inventory import inventory_update_item, InventoryUpdate
                        
                        # Create inventory update request
                        inventory_request = InventoryUpdate(
                            product_id=line_item["product_id"],
                            quantity_change=receipt["quantity_received"],
                            reason="purchase_order",
                            reference_id=order["po_number"]
                        )
                        
                        # Update inventory
                        inventory_update_item(inventory_request)
                    except Exception as inv_error:
                        print(f"Error updating inventory: {str(inv_error)}")
                
                # Update order status based on received items
                update_order_status_after_receipt(order)
                
                # Save changes
                order["updated_at"] = now
                save_purchase_orders(orders)
                return order
        
        raise ValueError(f"Purchase order with ID {order_id} not found")
    except Exception as e:
        print(f"Error recording item receipt: {str(e)}")
        raise

def update_order_status_after_receipt(order: Dict[str, Any]):
    """Update order status based on received items"""
    # If order is already marked as received or cancelled, don't change it
    if order["status"] in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CANCELLED]:
        return
    
    # Calculate total ordered and received quantities
    ordered_quantities = {}
    for i, item in enumerate(order.get("items", [])):
        product_id = item["product_id"]
        if product_id not in ordered_quantities:
            ordered_quantities[product_id] = 0
        ordered_quantities[product_id] += item["quantity"]
    
    received_quantities = {}
    for receipt in order.get("receipts", []):
        if not receipt.get("quality_check_passed", True):
            continue  # Skip items that failed quality check
        
        product_id = receipt["product_id"]
        if product_id not in received_quantities:
            received_quantities[product_id] = 0
        received_quantities[product_id] += receipt["quantity_received"]
    
    # Check if all items are fully received
    all_received = True
    any_received = False
    
    for product_id, ordered in ordered_quantities.items():
        received = received_quantities.get(product_id, 0)
        if received > 0:
            any_received = True
        if received < ordered:
            all_received = False
    
    # Update status
    if all_received:
        order["status"] = PurchaseOrderStatus.RECEIVED
    elif any_received:
        order["status"] = PurchaseOrderStatus.PARTIALLY_RECEIVED

# API Endpoints
@router.get("/health")
def check_purchase_order_health():
    """Check if the Purchase Order API is operational"""
    return {"status": "ok", "message": "Purchase Order API is operational"}

@router.get("/", response_model=PurchaseOrderListResponse)
async def list_purchase_orders(
    supplier_id: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List purchase orders with optional filtering"""
    try:
        orders = get_all_purchase_orders()
        
        # Apply filters
        if supplier_id:
            orders = [o for o in orders if o.get("supplier_id") == supplier_id]
        
        if status:
            orders = [o for o in orders if o.get("status") == status]
        
        if date_from:
            orders = [o for o in orders if o.get("order_date", "") >= date_from]
        
        if date_to:
            orders = [o for o in orders if o.get("order_date", "") <= date_to]
        
        # Sort by created_at desc
        orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        total_count = len(orders)
        paginated = orders[offset:offset + limit]
        
        return PurchaseOrderListResponse(
            orders=[PurchaseOrderResponse(**o) for o in paginated],
            total_count=total_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing purchase orders: {str(e)}")

@router.post("/", response_model=PurchaseOrderResponse)
async def create_purchase_order(order: PurchaseOrderCreate):
    """Create a new purchase order"""
    try:
        order_data = order.dict()
        new_order = create_or_update_purchase_order(order_data)
        
        return PurchaseOrderResponse(**new_order)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating purchase order: {str(e)}")

@router.get("/{order_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order_by_id(order_id: str = Path(..., description="The ID of the purchase order")):
    """Get a purchase order by ID"""
    order = get_purchase_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Purchase order with ID {order_id} not found")
    
    return PurchaseOrderResponse(**order)

@router.put("/{order_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(order_id: str, update_data: PurchaseOrderUpdate):
    """Update an existing purchase order"""
    try:
        # Check if order exists
        existing = get_purchase_order(order_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Purchase order with ID {order_id} not found")
        
        # Only allow updates to draft or pending orders
        if existing.get("status") not in [PurchaseOrderStatus.DRAFT, PurchaseOrderStatus.PENDING]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot update purchase order with status {existing.get('status')}"
            )
        
        # Update order
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        updated_order = create_or_update_purchase_order(update_dict, order_id)
        
        return PurchaseOrderResponse(**updated_order)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating purchase order: {str(e)}")

@router.patch("/{order_id}/status", response_model=PurchaseOrderResponse)
async def update_purchase_order_status(order_id: str, status: str = Body(..., embed=True)):
    """Update the status of a purchase order"""
    try:
        # Validate status
        valid_statuses = [
            PurchaseOrderStatus.DRAFT,
            PurchaseOrderStatus.PENDING,
            PurchaseOrderStatus.APPROVED,
            PurchaseOrderStatus.PLACED,
            PurchaseOrderStatus.PARTIALLY_RECEIVED,
            PurchaseOrderStatus.RECEIVED,
            PurchaseOrderStatus.CANCELLED
        ]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Check if order exists
        existing = get_purchase_order(order_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Purchase order with ID {order_id} not found")
        
        # Update status
        updated_order = create_or_update_purchase_order({"status": status}, order_id)
        
        return PurchaseOrderResponse(**updated_order)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating purchase order status: {str(e)}")

@router.post("/{order_id}/receive", response_model=PurchaseOrderResponse)
async def receive_order_items(order_id: str, receipt_data: ReceiveItemRequest):
    """Record receipt of items for a purchase order"""
    try:
        # Check if order exists
        existing = get_purchase_order(order_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Purchase order with ID {order_id} not found")
        
        # Only allow receiving items for placed or partially received orders
        if existing.get("status") not in [PurchaseOrderStatus.PLACED, PurchaseOrderStatus.PARTIALLY_RECEIVED]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot receive items for purchase order with status {existing.get('status')}"
            )
        
        # Record receipt
        updated_order = record_item_receipt(order_id, receipt_data.dict())
        
        return PurchaseOrderResponse(**updated_order)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error receiving order items: {str(e)}")
