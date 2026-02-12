from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional
import databutton as db
from datetime import datetime
import re

router = APIRouter(prefix="/supplier")

# Models
class SupplierContact(BaseModel):
    """Model for supplier contact information"""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None

class SupplierPerformanceMetrics(BaseModel):
    """Model for tracking supplier performance"""
    on_time_delivery_rate: Optional[float] = Field(None, ge=0, le=100)
    quality_rating: Optional[float] = Field(None, ge=0, le=10)
    response_time_avg: Optional[int] = None  # Average response time in hours
    fulfillment_rate: Optional[float] = Field(None, ge=0, le=100)  # Percentage of orders fulfilled completely

class SupplierBase(BaseModel):
    """Base model for supplier information"""
    name: str
    code: str  # Unique supplier code/ID
    contact_info: SupplierContact
    address: Optional[str] = None
    product_categories: List[str] = []
    active: bool = True
    lead_time_days: Optional[int] = None  # Typical lead time for orders in days
    payment_terms: Optional[str] = None  # e.g., "Net 30", "Net 60"
    minimum_order_value: Optional[float] = None
    notes: Optional[str] = None

class SupplierCreate(SupplierBase):
    """Model for creating a new supplier"""
    pass

class SupplierUpdate(BaseModel):
    """Model for updating supplier information"""
    name: Optional[str] = None
    contact_info: Optional[SupplierContact] = None
    address: Optional[str] = None
    product_categories: Optional[List[str]] = None
    active: Optional[bool] = None
    lead_time_days: Optional[int] = None
    payment_terms: Optional[str] = None
    minimum_order_value: Optional[float] = None
    notes: Optional[str] = None

class SupplierResponse(SupplierBase):
    """Response model for supplier information"""
    id: str
    created_at: str
    updated_at: str
    performance_metrics: Optional[SupplierPerformanceMetrics] = None

class SupplierListResponse(BaseModel):
    """Response model for listing suppliers"""
    suppliers: List[SupplierResponse]
    total_count: int

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_all_suppliers() -> List[Dict[str, Any]]:
    """Get all suppliers from storage"""
    try:
        suppliers_key = "suppliers"
        suppliers = db.storage.json.get(suppliers_key, default=[])
        return suppliers
    except Exception as e:
        print(f"Error getting suppliers: {str(e)}")
        return []

def get_supplier(supplier_id: str) -> Optional[Dict[str, Any]]:
    """Get supplier by ID"""
    try:
        suppliers = get_all_suppliers()
        for supplier in suppliers:
            if supplier.get("id") == supplier_id:
                return supplier
        return None
    except Exception as e:
        print(f"Error getting supplier: {str(e)}")
        return None

def get_supplier_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Get supplier by code"""
    try:
        suppliers = get_all_suppliers()
        for supplier in suppliers:
            if supplier.get("code") == code:
                return supplier
        return None
    except Exception as e:
        print(f"Error getting supplier by code: {str(e)}")
        return None

def save_suppliers(suppliers: List[Dict[str, Any]]) -> bool:
    """Save all suppliers to storage"""
    try:
        suppliers_key = "suppliers"
        db.storage.json.put(suppliers_key, suppliers)
        return True
    except Exception as e:
        print(f"Error saving suppliers: {str(e)}")
        return False

def create_or_update_supplier(supplier_data: Dict[str, Any], supplier_id: Optional[str] = None) -> Dict[str, Any]:
    """Create or update a supplier"""
    try:
        suppliers = get_all_suppliers()
        now = datetime.utcnow().isoformat()
        
        # If updating existing supplier
        if supplier_id:
            for i, supplier in enumerate(suppliers):
                if supplier.get("id") == supplier_id:
                    # Update existing supplier
                    suppliers[i].update(supplier_data)
                    suppliers[i]["updated_at"] = now
                    save_suppliers(suppliers)
                    return suppliers[i]
            raise ValueError(f"Supplier with ID {supplier_id} not found")
        
        # Check if code already exists
        if any(s.get("code") == supplier_data.get("code") for s in suppliers):
            raise ValueError(f"Supplier with code {supplier_data.get('code')} already exists")
        
        # Create new supplier
        new_supplier = {
            **supplier_data,
            "id": f"sup_{len(suppliers) + 1}",
            "created_at": now,
            "updated_at": now
        }
        suppliers.append(new_supplier)
        save_suppliers(suppliers)
        return new_supplier
    except Exception as e:
        print(f"Error creating/updating supplier: {str(e)}")
        raise

def update_supplier_performance(supplier_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Update performance metrics for a supplier"""
    try:
        suppliers = get_all_suppliers()
        for i, supplier in enumerate(suppliers):
            if supplier.get("id") == supplier_id:
                # Initialize performance_metrics if it doesn't exist
                if "performance_metrics" not in supplier:
                    supplier["performance_metrics"] = {}
                
                # Update only provided metrics
                for key, value in metrics.items():
                    supplier["performance_metrics"][key] = value
                
                supplier["updated_at"] = datetime.utcnow().isoformat()
                save_suppliers(suppliers)
                return supplier
        raise ValueError(f"Supplier with ID {supplier_id} not found")
    except Exception as e:
        print(f"Error updating supplier performance: {str(e)}")
        raise

# API Endpoints
@router.get("/health")
def check_supplier_health():
    """Check if the Supplier API is operational"""
    return {"status": "ok", "message": "Supplier API is operational"}

@router.get("/", response_model=SupplierListResponse)
async def list_suppliers(
    active: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List suppliers with optional filtering"""
    try:
        suppliers = get_all_suppliers()
        
        # Apply filters
        if active is not None:
            suppliers = [s for s in suppliers if s.get("active") == active]
        
        if category:
            suppliers = [
                s for s in suppliers 
                if "product_categories" in s and category in s["product_categories"]
            ]
        
        if search:
            search_lower = search.lower()
            suppliers = [
                s for s in suppliers 
                if search_lower in s.get("name", "").lower() or 
                   search_lower in s.get("code", "").lower()
            ]
        
        # Apply pagination
        total_count = len(suppliers)
        paginated = suppliers[offset:offset + limit]
        
        return SupplierListResponse(
            suppliers=[SupplierResponse(**s) for s in paginated],
            total_count=total_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing suppliers: {str(e)}")

@router.post("/", response_model=SupplierResponse)
async def create_supplier(supplier: SupplierCreate):
    """Create a new supplier"""
    try:
        # Check if supplier with this code already exists
        existing = get_supplier_by_code(supplier.code)
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Supplier with code {supplier.code} already exists"
            )
        
        # Create new supplier
        supplier_data = supplier.dict()
        new_supplier = create_or_update_supplier(supplier_data)
        
        return SupplierResponse(**new_supplier)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating supplier: {str(e)}")

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier_by_id(supplier_id: str = Path(..., description="The ID of the supplier")):
    """Get a supplier by ID"""
    supplier = get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier with ID {supplier_id} not found")
    
    return SupplierResponse(**supplier)

@router.get("/code/{code}", response_model=SupplierResponse)
async def get_supplier_by_supplier_code(code: str = Path(..., description="The code of the supplier")):
    """Get a supplier by code"""
    supplier = get_supplier_by_code(code)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier with code {code} not found")
    
    return SupplierResponse(**supplier)

@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(supplier_id: str, update_data: SupplierUpdate):
    """Update an existing supplier"""
    try:
        # Check if supplier exists
        existing = get_supplier(supplier_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Supplier with ID {supplier_id} not found")
        
        # Update supplier
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        updated_supplier = create_or_update_supplier(update_dict, supplier_id)
        
        return SupplierResponse(**updated_supplier)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating supplier: {str(e)}")

@router.patch("/{supplier_id}/performance", response_model=SupplierResponse)
async def update_supplier_performance_metrics(supplier_id: str, metrics: SupplierPerformanceMetrics):
    """Update performance metrics for a supplier"""
    try:
        # Check if supplier exists
        existing = get_supplier(supplier_id)
        if not existing:
            raise HTTPException(status_code=404, detail=f"Supplier with ID {supplier_id} not found")
        
        # Update only provided metrics
        metrics_dict = {k: v for k, v in metrics.dict().items() if v is not None}
        updated_supplier = update_supplier_performance(supplier_id, metrics_dict)
        
        return SupplierResponse(**updated_supplier)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating supplier performance: {str(e)}")
