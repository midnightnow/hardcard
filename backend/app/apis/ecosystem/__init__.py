from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends, Request
import json
import time
from datetime import datetime

router = APIRouter(prefix="/ecosystem")

# --- Module Identity Models ---

class ServiceStatus(BaseModel):
    database: str = "connected"
    apis: str = "operational"
    verification_system: str = "active"

class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    uptime: int = Field(default_factory=lambda: int(time.time() - START_TIME))
    services: ServiceStatus = Field(default_factory=ServiceStatus)

class ModuleInfo(BaseModel):
    name: str = "Hempex"
    version: str = "1.0.0"
    description: str = "Premium cannabinoid products platform"
    type: str = "business_venture"
    capabilities: List[str] = ["product_data", "verification", "education"]
    owner: str = "McMillan Family Trust"
    connections: List[str] = ["legacy_vault", "hardcard_hub"]

# --- Data Exchange Models ---

class SchemaField(BaseModel):
    name: str
    type: str
    description: str

class DataSchema(BaseModel):
    name: str
    fields: List[SchemaField]
    access: str

class SchemaResponse(BaseModel):
    schemas: List[DataSchema]

class Cannabinoid(BaseModel):
    type: str
    amount: int
    unit: str

class ProductMetadata(BaseModel):
    hcu_id: str
    creation_date: str
    verification_status: str

class Product(BaseModel):
    id: str
    name: str
    category: str
    cannabinoids: List[Cannabinoid]
    metadata: ProductMetadata

# --- Event System Models ---

class EventPublishRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    source: str = "hempex"
    target: List[str]
    priority: str = "normal"

class EventPublishResponse(BaseModel):
    event_id: str
    status: str = "published"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
    recipients: List[str]

class EventSubscribeRequest(BaseModel):
    subscriber: str
    event_types: List[str]
    callback_url: str
    secret: str

class EventSubscribeResponse(BaseModel):
    subscription_id: str
    status: str = "active"
    event_types: List[str]
    expires_at: str

# Initialize start time for uptime tracking
START_TIME = time.time()

# Sample data for demonstration
PRODUCT_DATA = {
    "cbd-oil-1000": Product(
        id="cbd-oil-1000",
        name="Premium CBD Oil 1000mg",
        category="oil",
        cannabinoids=[
            Cannabinoid(type="CBD", amount=1000, unit="mg"),
            Cannabinoid(type="CBG", amount=10, unit="mg")
        ],
        metadata=ProductMetadata(
            hcu_id="hempex:product:cbd-oil-1000",
            creation_date="2025-01-15T00:00:00Z",
            verification_status="verified"
        )
    )
}

# --- Hard Card Ecosystem API Endpoints ---

@router.get("/hardcard/info")
def get_module_info() -> ModuleInfo:
    """Provides information about this module within the Hard Card Universe ecosystem."""
    return ModuleInfo()

@router.get("/hardcard/health")
def check_ecosystem_health():
    """Health check endpoint to verify module availability and operational status."""
    return {"status": "ok", "message": "Ecosystem API is operational"}

@router.get("/hardcard/data/schema")
def get_data_schema() -> SchemaResponse:
    """Returns the module's data schema, describing available data types and formats."""
    return SchemaResponse(
        schemas=[
            DataSchema(
                name="product",
                fields=[
                    SchemaField(name="id", type="string", description="Unique product identifier"),
                    SchemaField(name="name", type="string", description="Product name"),
                    SchemaField(name="category", type="string", description="Product category"),
                    SchemaField(name="cannabinoids", type="array", description="Cannabinoid profile")
                ],
                access="read"
            ),
            DataSchema(
                name="verification",
                fields=[
                    SchemaField(name="product_id", type="string", description="Product reference"),
                    SchemaField(name="lab_id", type="string", description="Testing laboratory ID"),
                    SchemaField(name="results", type="object", description="Verification results")
                ],
                access="read"
            )
        ]
    )

@router.get("/hardcard/data/product/{product_id}")
def get_product(product_id: str) -> Product:
    """Retrieves product data for the specified product ID."""
    if product_id not in PRODUCT_DATA:
        raise HTTPException(status_code=404, detail="Product not found")
    return PRODUCT_DATA[product_id]

@router.post("/hardcard/events/publish")
def publish_event(event: EventPublishRequest) -> EventPublishResponse:
    """Publishes an event to the Hard Card ecosystem event bus."""
    # In a real implementation, this would connect to an event bus
    # For demo purposes, we'll generate a fake event ID and return success
    return EventPublishResponse(
        event_id=f"evt_{''.join(['8f7e6d5c4b3a2'])}",
        recipients=event.target
    )

@router.post("/hardcard/events/subscribe")
def subscribe_to_events(subscription: EventSubscribeRequest) -> EventSubscribeResponse:
    """Subscribes to specific event types from the Hard Card ecosystem."""
    # In a real implementation, this would register with an event subscription service
    # For demo purposes, we'll generate a fake subscription ID and return success
    return EventSubscribeResponse(
        subscription_id=f"sub_{''.join(['1a2b3c4d5e6f'])}",
        event_types=subscription.event_types,
        expires_at="2026-04-15T00:00:00Z"
    )
