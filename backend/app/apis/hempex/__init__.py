from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from fastapi import APIRouter, UploadFile, HTTPException, Depends, BackgroundTasks, Query
import databutton as db
import re
import time
import json
import hashlib
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

router = APIRouter(prefix="/hempex")

# --- Domain Models ---

class Cannabinoid(BaseModel):
    name: str  # CBD, CBG, CBN, etc.
    amount: float
    unit: str  # mg, %, etc.

class ProductCategory(BaseModel):
    id: str
    name: str
    description: str
    parent_id: Optional[str] = None

class Product(BaseModel):
    sku: str
    name: str
    description: str
    category_id: str
    image_urls: List[str] = Field(default_factory=list)
    cannabinoids: List[Cannabinoid] = Field(default_factory=list)
    tga_approved: bool = False
    artg_number: Optional[str] = None
    sponsor_id: str
    price: float
    in_stock: bool = True
    stock_quantity: int = 0
    requires_prescription: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    inventory_status: str = "in_stock"  # Added field to match frontend expectations
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Patient(BaseModel):
    id: str
    dob: datetime
    verified_prescription_ids: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    consent_status: str = "pending"  # pending|granted|denied
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Prescription(BaseModel):
    id: str
    patient_id: str
    prescriber_id: str
    tga_sas_number: str  # SAS B approval reference
    product_sku: str
    quantity: int
    dosage_instructions: str = ""
    is_repeatable: bool = False
    repeats_remaining: int = 0
    expiry_date: Optional[datetime] = None
    verification_status: str = "pending"  # pending|verified|rejected
    verification_notes: str = ""
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class Order(BaseModel):
    id: str
    prescription_id: str
    patient_id: str
    product_sku: str
    quantity: int
    shipping_address: Dict[str, str] = Field(default_factory=dict)
    sponsor_release_id: str = ""  # populated once sponsor ships
    tracking_number: str = ""
    status: str = "pending"  # pending|approved|processing|shipped|delivered|cancelled
    payment_status: str = "pending"  # pending|paid|refunded
    compliance_verified: bool = False
    audit_trail: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# --- Helper Functions ---

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# --- Middleware for Compliance Audit Trail ---

class AuditTrail(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        t0 = time.time()
        response = await call_next(request)
        duration = time.time() - t0

        # Create audit entry
        entry = {
            "path": request.url.path,
            "method": request.method,
            "user": request.headers.get("X-User", "anon"),
            "status_code": response.status_code,
            "duration_ms": int(duration * 1000),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Create hash for immutability
        hash_str = hashlib.sha256(json.dumps(entry).encode()).hexdigest()
        entry["hash"] = hash_str

        # Store in audit log
        try:
            # Get existing audit log or create new one
            audit_log_key = f"audit_log_{datetime.utcnow().strftime('%Y%m%d')}"
            audit_log = db.storage.json.get(sanitize_storage_key(audit_log_key), default=[])
            audit_log.append(entry)
            db.storage.json.put(sanitize_storage_key(audit_log_key), audit_log)
        except Exception as e:
            print(f"Error saving audit log: {str(e)}")

        return response

# --- Storage Functions ---

def init_database():
    """Initialize database with sample data if empty"""
    try:
        # Check if patients collection exists
        patient_count = 0
        try:
            # List all patient keys
            patients = [k.name for k in db.storage.text.list() if k.name.startswith("patient_")]
            patient_count = len(patients)
        except Exception:
            pass
            
        if patient_count == 0:
            # Create sample patient
            sample_patient = Patient(
                id="patient123",
                dob=datetime(1980, 1, 1),
                verified_prescription_ids=[],
                preferences={"notifications": {"email": True, "sms": False}},
                consent_status="granted"
            )
            # Convert datetime objects to ISO format strings in the patient data
            patient_data = sample_patient.model_dump()
            patient_data["dob"] = patient_data["dob"].isoformat()
            patient_data["last_updated"] = patient_data["last_updated"].isoformat()
            
            # Save patient
            patient_key = f"patient_{sanitize_storage_key(sample_patient.id)}"
            db.storage.json.put(patient_key, patient_data)
            
            # Create sample product categories
            categories = [
                ProductCategory(
                    id="oils",
                    name="CBD Oils",
                    description="CBD oils in various concentrations"
                ),
                ProductCategory(
                    id="capsules",
                    name="CBD Capsules",
                    description="CBD in easy-to-dose capsule form"
                ),
                ProductCategory(
                    id="topicals",
                    name="Topical Products",
                    description="CBD creams, balms and lotions for topical application"
                )
            ]
            
            for category in categories:
                category_key = f"category_{sanitize_storage_key(category.id)}"
                db.storage.json.put(category_key, category.model_dump())
            
            # Create sample products
            products = [
                Product(
                    sku="cbd-oil-1000",
                    name="Premium CBD Oil 1000mg",
                    description="High-quality CBD oil with 1000mg of CBD per bottle",
                    category_id="oils",
                    image_urls=[
                        "https://images.unsplash.com/photo-1584486483122-af7d49cf2992?q=80&w=500",
                        "https://images.unsplash.com/photo-1559052582-10b5b9bf61b3?q=80&w=500"
                    ],
                    cannabinoids=[
                        Cannabinoid(name="CBD", amount=1000, unit="mg"),
                        Cannabinoid(name="CBG", amount=10, unit="mg")
                    ],
                    tga_approved=True,
                    artg_number="12345",
                    sponsor_id="sponsor123",
                    price=199.99,
                    in_stock=True,
                    stock_quantity=100,
                    inventory_status="in_stock"
                ),
                Product(
                    sku="cbd-capsules-25",
                    name="CBD Gel Capsules 25mg",
                    description="Convenient CBD capsules with 25mg per capsule",
                    category_id="capsules",
                    image_urls=[
                        "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?q=80&w=500",
                        "https://images.unsplash.com/photo-1549893072-4bc678117f45?q=80&w=500"
                    ],
                    cannabinoids=[
                        Cannabinoid(name="CBD", amount=25, unit="mg")
                    ],
                    tga_approved=True,
                    artg_number="12346",
                    sponsor_id="sponsor123",
                    price=89.99,
                    in_stock=True,
                    stock_quantity=75,
                    inventory_status="in_stock"
                ),
                Product(
                    sku="cbd-cream-500",
                    name="CBD Relief Cream 500mg",
                    description="Topical CBD cream for targeted relief",
                    category_id="topicals",
                    image_urls=[
                        "https://images.unsplash.com/photo-1608571423539-e951a50fc684?q=80&w=500",
                        "https://images.unsplash.com/photo-1608571423902-fb15d0856a3e?q=80&w=500"
                    ],
                    cannabinoids=[
                        Cannabinoid(name="CBD", amount=500, unit="mg"),
                        Cannabinoid(name="CBG", amount=50, unit="mg")
                    ],
                    tga_approved=False,
                    sponsor_id="sponsor123",
                    price=69.99,
                    in_stock=True,
                    stock_quantity=30,
                    inventory_status="in_stock"
                )
            ]
            
            for product in products:
                product_key = f"product_{sanitize_storage_key(product.sku)}"
                # Convert datetime objects to ISO format strings
                product_data = product.model_dump()
                product_data["created_at"] = product_data["created_at"].isoformat()
                product_data["updated_at"] = product_data["updated_at"].isoformat()
                db.storage.json.put(product_key, product_data)
                
            print("Initialized database with sample data")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

# Initialize database when module is loaded
init_database()

def get_patient(patient_id: str) -> Optional[Patient]:
    """Get patient by ID from storage"""
    try:
        patient_key = f"patient_{sanitize_storage_key(patient_id)}"
        patient_data = db.storage.json.get(patient_key)
        return Patient(**patient_data)
    except Exception:
        return None

def save_patient(patient: Patient) -> bool:
    """Save patient to storage"""
    try:
        patient_key = f"patient_{sanitize_storage_key(patient.id)}"
        db.storage.json.put(patient_key, patient.model_dump())
        return True
    except Exception as e:
        print(f"Error saving patient: {str(e)}")
        return False

def get_prescription(prescription_id: str) -> Optional[Prescription]:
    """Get prescription by ID from storage"""
    try:
        prescription_key = f"prescription_{sanitize_storage_key(prescription_id)}"
        prescription_data = db.storage.json.get(prescription_key)
        return Prescription(**prescription_data)
    except Exception:
        return None

def save_prescription(prescription: Prescription) -> bool:
    """Save prescription to storage"""
    try:
        prescription_key = f"prescription_{sanitize_storage_key(prescription.id)}"
        db.storage.json.put(prescription_key, prescription.model_dump())
        return True
    except Exception as e:
        print(f"Error saving prescription: {str(e)}")
        return False

def get_order(order_id: str) -> Optional[Order]:
    """Get order by ID from storage"""
    try:
        order_key = f"order_{sanitize_storage_key(order_id)}"
        order_data = db.storage.json.get(order_key)
        return Order(**order_data)
    except Exception:
        return None

def save_order(order: Order) -> bool:
    """Save order to storage"""
    try:
        order_key = f"order_{sanitize_storage_key(order.id)}"
        db.storage.json.put(order_key, order.model_dump())
        return True
    except Exception as e:
        print(f"Error saving order: {str(e)}")
        return False
        
def get_product(sku: str) -> Optional[Product]:
    """Get product by SKU from storage"""
    try:
        product_key = f"product_{sanitize_storage_key(sku)}"
        product_data = db.storage.json.get(product_key)
        return Product(**product_data)
    except Exception:
        return None

def get_all_products() -> List[Product]:
    """Get all products from storage"""
    products = []
    try:
        # List all product keys
        product_keys = [k.name for k in db.storage.json.list() if k.name.startswith("product_")]
        
        for key in product_keys:
            try:
                product_data = db.storage.json.get(key)
                products.append(Product(**product_data))
            except Exception as e:
                print(f"Error loading product {key}: {str(e)}")
    except Exception as e:
        print(f"Error listing products: {str(e)}")
    return products

def get_category(category_id: str) -> Optional[ProductCategory]:
    """Get category by ID from storage"""
    try:
        category_key = f"category_{sanitize_storage_key(category_id)}"
        category_data = db.storage.json.get(category_key)
        return ProductCategory(**category_data)
    except Exception:
        return None

def get_all_categories() -> List[ProductCategory]:
    """Get all categories from storage"""
    categories = []
    try:
        # List all category keys
        category_keys = [k.name for k in db.storage.json.list() if k.name.startswith("category_")]
        
        for key in category_keys:
            try:
                category_data = db.storage.json.get(key)
                categories.append(ProductCategory(**category_data))
            except Exception as e:
                print(f"Error loading category {key}: {str(e)}")
    except Exception as e:
        print(f"Error listing categories: {str(e)}")
    return categories

# --- Request/Response Models ---

class UploadPrescriptionResponse(BaseModel):
    message: str
    prescription_id: str

class TriggerShippingRequest(BaseModel):
    order_id: str

class TriggerShippingResponse(BaseModel):
    message: str
    order_id: str
    
class ProductResponse(BaseModel):
    sku: str
    name: str
    description: str
    category_id: str
    category_name: str = ""
    image_urls: List[str]
    cannabinoids: List[Cannabinoid]
    tga_approved: bool
    artg_number: Optional[str]
    price: float
    in_stock: bool
    requires_prescription: bool
    
class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str
    parent_id: Optional[str]
    
class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]

# --- Endpoints ---

@router.get("/health")
def check_health_hempex():
    """Check if the Hempex API is running"""
    return {"status": "ok", "message": "Hempex API is operational"}

@router.post("/prescriptions/upload", response_model=UploadPrescriptionResponse)
async def upload_prescription(file: UploadFile, patient_id: str):
    """Upload a prescription file for SAS B approval"""
    # Validate MIME type
    if file.content_type not in ("application/pdf", "image/png", "image/jpeg"):
        raise HTTPException(status_code=415, detail="Unsupported file format. Please upload PDF, PNG, or JPEG.")

    # Check file size (limit to 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")

    # Get patient or raise error
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Store the file
    file_id = f"prescription_{uuid4().hex}"
    db.storage.binary.put(sanitize_storage_key(file_id), contents)

    # OCR/parse SAS number (placeholder - would integrate with OCR service)
    # In a real implementation, this would extract the SAS number from the document
    sas_number = f"TGA-SASB-{uuid4().hex[:8].upper()}"

    # Create prescription record
    prescription_id = uuid4().hex
    prescription = Prescription(
        id=prescription_id,
        patient_id=patient_id,
        prescriber_id="unknown",  # Would be set based on authentication in real implementation
        tga_sas_number=sas_number,
        product_sku="default",  # Would be extracted from prescription
        quantity=1  # Would be extracted from prescription
    )

    # Save prescription
    if not save_prescription(prescription):
        raise HTTPException(status_code=500, detail="Failed to save prescription")

    # Update patient record
    patient.verified_prescription_ids.append(prescription_id)
    if not save_patient(patient):
        raise HTTPException(status_code=500, detail="Failed to update patient record")

    return UploadPrescriptionResponse(
        message="Prescription uploaded successfully",
        prescription_id=prescription_id
    )

@router.post("/shipping/trigger", response_model=TriggerShippingResponse)
def trigger_shipping(request: TriggerShippingRequest, background_tasks: BackgroundTasks):
    """Trigger shipping process with sponsor"""
    # Get the order
    order = get_order(request.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get the prescription
    prescription = get_prescription(order.prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    # Prepare sponsor payload
    sponsor_payload = {
        "order_id": order.id,
        "prescription_id": order.prescription_id,
        "tga_sas_number": prescription.tga_sas_number,
        "product_sku": prescription.product_sku,
        "quantity": prescription.quantity,
        "timestamp": datetime.utcnow().isoformat()
    }

    # In a real implementation, we would sign the payload and send to sponsor API or SFTP
    print(f"Would send payload to sponsor: {json.dumps(sponsor_payload)}")
    # For demo, we'll just simulate a successful response

    # Update order status
    order.status = "processing"
    order.updated_at = datetime.utcnow()

    # Generate mock sponsor release ID
    order.sponsor_release_id = f"SR-{uuid4().hex[:8].upper()}"

    # Save updated order
    if not save_order(order):
        raise HTTPException(status_code=500, detail="Failed to update order")

    # In background, we would poll for shipping status updates from sponsor
    background_tasks.add_task(lambda: print(f"Processing order {order.id} with sponsor"))

    return TriggerShippingResponse(
        message="Shipping process initiated with sponsor",
        order_id=order.id
    )

@router.get("/products", response_model=ProductListResponse)
def list_hempex_products(
    category_id: Optional[str] = None,
    tga_approved: Optional[bool] = None,
    requires_prescription: Optional[bool] = None,
    in_stock: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """List all products with optional filtering"""
    # Get all products
    all_products = get_all_products()
    
    # Filter products based on query parameters
    filtered_products = all_products
    
    if category_id is not None:
        filtered_products = [p for p in filtered_products if p.category_id == category_id]
        
    if tga_approved is not None:
        filtered_products = [p for p in filtered_products if p.tga_approved == tga_approved]
        
    if requires_prescription is not None:
        filtered_products = [p for p in filtered_products if p.requires_prescription == requires_prescription]
        
    if in_stock is not None:
        filtered_products = [p for p in filtered_products if p.in_stock == in_stock]
    
    # Calculate pagination
    total = len(filtered_products)
    total_pages = (total + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)
    
    # Get paginated products
    paginated_products = filtered_products[start_idx:end_idx]
    
    # Get category names for products
    product_responses = []
    for product in paginated_products:
        category = get_category(product.category_id)
        category_name = category.name if category else ""
        
        product_responses.append(ProductResponse(
            sku=product.sku,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            category_name=category_name,
            image_urls=product.image_urls,
            cannabinoids=product.cannabinoids,
            tga_approved=product.tga_approved,
            artg_number=product.artg_number,
            price=product.price,
            in_stock=product.in_stock,
            requires_prescription=product.requires_prescription
        ))
    
    return ProductListResponse(
        products=product_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/products/{sku}", response_model=ProductResponse)
def get_hempex_product_by_sku(sku: str):
    """Get a specific product by SKU"""
    product = get_product(sku)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with SKU '{sku}' not found")
    
    # Get category name
    category = get_category(product.category_id)
    category_name = category.name if category else ""
    
    return ProductResponse(
        sku=product.sku,
        name=product.name,
        description=product.description,
        category_id=product.category_id,
        category_name=category_name,
        image_urls=product.image_urls,
        cannabinoids=product.cannabinoids,
        tga_approved=product.tga_approved,
        artg_number=product.artg_number,
        price=product.price,
        in_stock=product.in_stock,
        requires_prescription=product.requires_prescription
    )

@router.get("/categories", response_model=CategoryListResponse)
def list_categories():
    """List all product categories"""
    categories = get_all_categories()
    
    # Convert ProductCategory objects to CategoryResponse objects
    category_responses = [
        CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id
        ) for category in categories
    ]
    
    return CategoryListResponse(categories=category_responses)
