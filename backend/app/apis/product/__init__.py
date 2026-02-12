from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import databutton as db
import json
from datetime import datetime
import re

router = APIRouter(prefix="/product")

# Models
class ProductBase(BaseModel):
    sku: str
    name: str
    description: str
    short_description: Optional[str] = None
    category_id: str
    category_name: Optional[str] = None
    image_urls: List[str] = []
    cannabinoids: List[Dict[str, Any]] = []
    lab_results: List[str] = []
    tga_approved: bool = False
    price: float
    regular_price: Optional[float] = None
    sale_price: Optional[float] = None
    on_sale: Optional[bool] = False
    inventory_status: Optional[str] = "in_stock"  # in_stock, out_of_stock, backordered
    source: Optional[str] = None  # For products imported from external sources
    requires_prescription: bool = False
    featured: bool = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    image_urls: Optional[List[str]] = None
    cannabinoids: Optional[List[Dict[str, Any]]] = None
    lab_results: Optional[List[str]] = None
    tga_approved: Optional[bool] = None
    price: Optional[float] = None
    regular_price: Optional[float] = None
    sale_price: Optional[float] = None
    on_sale: Optional[bool] = None
    inventory_status: Optional[str] = None

class ProductResponse(ProductBase):
    pass

class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total_count: int

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    image_url: Optional[str] = None
    product_count: int = 0

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]

class ProductInventoryUpdate(BaseModel):
    sku: str
    inventory_quantity: int
    inventory_status: str

class BatchInventoryUpdate(BaseModel):
    updates: List[ProductInventoryUpdate]

# --- Helper Functions ---
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Get all products from storage
def get_all_products() -> List[Dict[str, Any]]:
    """Get all products from storage"""
    try:
        products_key = "products"
        products = db.storage.json.get(products_key, default=[])
        return products
    except Exception as e:
        print(f"Error getting products: {str(e)}")
        return []

# Get a single product from storage
def get_product(sku: str) -> Optional[Dict[str, Any]]:
    """Get product by SKU"""
    try:
        products = get_all_products()
        for product in products:
            if product.get("sku") == sku:
                return product
        return None
    except Exception as e:
        print(f"Error getting product: {str(e)}")
        return None

# Update or create a product in storage
def upsert_product(product: Dict[str, Any]) -> bool:
    """Update or create a product in storage"""
    try:
        products = get_all_products()
        
        # Check if product already exists
        found = False
        for i, existing in enumerate(products):
            if existing.get("sku") == product.get("sku"):
                # Update existing product
                products[i] = product
                found = True
                break
        
        # Add new product if not found
        if not found:
            products.append(product)
        
        # Save all products
        save_products(products)
        return True
    except Exception as e:
        print(f"Error upserting product: {str(e)}")
        return False
        
def save_products(products: List[Dict[str, Any]]) -> bool:
    """Save all products to storage"""
    try:
        db.storage.json.put("products", products)
        return True
    except Exception as e:
        print(f"Error saving products: {str(e)}")
        return False

# Update product inventory
def update_product_inventory(sku: str, quantity: int, status: str) -> bool:
    """Update product inventory"""
    try:
        product = get_product(sku)
        if not product:
            return False
        
        product["inventory_quantity"] = quantity
        product["inventory_status"] = status
        product["last_inventory_update"] = datetime.utcnow().isoformat()
        
        return upsert_product(product)
    except Exception as e:
        print(f"Error updating product inventory: {str(e)}")
        return False

# --- API Endpoints ---

@router.get("/health")
def check_health_product():
    """Check if the Product API is operational"""
    return {"status": "ok", "message": "Product API is operational"}

@router.get("/", response_model=ProductListResponse)
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    featured: Optional[bool] = None,
    source: Optional[str] = None,
    sort: Optional[str] = "name_asc",
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None
):
    """List products with optional filtering"""
    try:
        products = get_all_products()
        
        # Apply filters
        filtered_products = products
        
        if category:
            filtered_products = [p for p in filtered_products if p.get("category_name", "").lower() == category.lower()]
        
        if min_price is not None:
            filtered_products = [p for p in filtered_products if p.get("price", 0) >= min_price]
        
        if max_price is not None:
            filtered_products = [p for p in filtered_products if p.get("price", 0) <= max_price]
        
        if in_stock is not None:
            filtered_products = [p for p in filtered_products if (p.get("inventory_status", "") == "in_stock") == in_stock]
        
        if featured is not None:
            filtered_products = [p for p in filtered_products if p.get("featured", False) == featured]
            
        if source is not None:
            filtered_products = [p for p in filtered_products if p.get("source") == source]
        
        # Apply sorting
        if sort == "price_asc":
            filtered_products.sort(key=lambda x: x.get("price", 0))
        elif sort == "price_desc":
            filtered_products.sort(key=lambda x: x.get("price", 0), reverse=True)
        elif sort == "name_desc":
            filtered_products.sort(key=lambda x: x.get("name", ""), reverse=True)
        else:  # name_asc is default
            filtered_products.sort(key=lambda x: x.get("name", ""))
        
        # Apply pagination
        paginated = filtered_products[offset:offset + limit]
        
        return ProductListResponse(
            products=[ProductResponse(**p) for p in paginated],
            total_count=len(filtered_products)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing products: {str(e)}")

@router.get("/{sku}", response_model=ProductResponse)
async def get_product_by_sku(sku: str):
    """Get a single product by SKU"""
    product = get_product(sku)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with SKU {sku} not found")
    
    return ProductResponse(**product)

@router.post("/inventory/update")
async def update_inventory2(update: ProductInventoryUpdate):
    """Update inventory for a single product"""
    success = update_product_inventory(
        update.sku,
        update.inventory_quantity,
        update.inventory_status
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Product with SKU {update.sku} not found")
    
    return {"status": "success", "message": f"Inventory updated for product {update.sku}"}

@router.post("/inventory/batch-update")
async def batch_update_inventory_product(updates: BatchInventoryUpdate):
    """Update inventory for multiple products"""
    results = []
    for update in updates.updates:
        success = update_product_inventory(
            update.sku,
            update.inventory_quantity,
            update.inventory_status
        )
        results.append({
            "sku": update.sku,
            "success": success
        })
    
    return {
        "status": "success",
        "results": results,
        "success_count": len([r for r in results if r["success"]])
    }

@router.get("/inventory/{sku}")
async def get_product_inventory_by_sku(sku: str, source: Optional[str] = None):
    """Get product inventory status"""
    # In a real application, this would query inventory information
    # For now, we'll use our storage function
    product = get_product(sku)
    
    # If source is specified, only return product if it matches the source
    if source and product and product.get("source") != source:
        product = None
        
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with SKU {sku} not found")
    
    return {
        "sku": product["sku"],
        "inventory_quantity": product.get("inventory_quantity", 0),
        "inventory_status": product.get("inventory_status", "out_of_stock"),
        "last_updated": product.get("last_inventory_update")
    }

@router.get("/availability")
async def check_product_availability_by_sku(skus: str = Query(..., description="Comma-separated list of SKUs"), source: Optional[str] = None):
    """Check availability of multiple products"""
    sku_list = skus.split(",")
    results = {}
    
    for sku in sku_list:
        product = get_product(sku)
        # If source is specified, only return product if it matches the source
        if source and product and product.get("source") != source:
            product = None
            
        if not product:
            results[sku] = {"found": False, "available": False}
        else:
            results[sku] = {
                "found": True,
                "available": product.get("inventory_status") == "in_stock",
                "status": product.get("inventory_status", "out_of_stock"),
                "quantity": product.get("inventory_quantity", 0)
            }
    
    return results
