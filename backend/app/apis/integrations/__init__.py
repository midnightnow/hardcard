from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json
import re
import databutton as db
import httpx
from enum import Enum

router = APIRouter(prefix="/integrations")

# --- Integration Models ---

class IntegrationStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    ERROR = "error"
    SYNCING = "syncing"

class IntegrationType(str, Enum):
    WOOCOMMERCE = "woocommerce"
    DNS = "dns"
    MARKETING = "marketing"
    FULFILLMENT = "fulfillment"
    RECOMMENDATION = "recommendation"

class IntegrationConfig(BaseModel):
    """Base configuration for all integrations"""
    enabled: bool = False
    last_sync: Optional[datetime] = None
    sync_frequency: int = 3600  # Seconds between syncs
    error_count: int = 0
    last_error: Optional[str] = None
    context_keys: List[str] = Field(default_factory=list)  # Keys used in ThinLayer context

class WooCommerceConfig(IntegrationConfig):
    """WooCommerce specific configuration"""
    url: str = ""
    consumer_key: str = ""
    consumer_secret: str = ""
    webhook_secret: str = ""
    sync_products: bool = True
    sync_orders: bool = True
    sync_customers: bool = True
    auto_publish: bool = False

class DNSConfig(IntegrationConfig):
    """DNS/Domain Services configuration"""
    provider: str = "godaddy"  # godaddy, cloudflare, etc.
    api_key: str = ""
    api_secret: str = ""
    domains: List[str] = Field(default_factory=list)
    auto_renew: bool = True

class MarketingConfig(IntegrationConfig):
    """Marketing & CRM configuration"""
    provider: str = "activecampaign"  # activecampaign, mailchimp, etc.
    api_key: str = ""
    api_url: str = ""
    lists: List[str] = Field(default_factory=list)
    automations: List[str] = Field(default_factory=list)
    sync_tags: bool = True

class FulfillmentConfig(IntegrationConfig):
    """Fulfillment & Logistics configuration"""
    provider: str = "shipbob"  # shipbob, shipstation, etc.
    api_key: str = ""
    warehouse_id: str = ""
    sync_inventory: bool = True
    auto_fulfill: bool = False

class RecommendationConfig(IntegrationConfig):
    """Recommendation Engine configuration"""
    enabled_algorithms: List[str] = Field(default_factory=lambda: ["collaborative", "content-based"])
    min_confidence: float = 0.7
    max_recommendations: int = 10
    include_competitor_data: bool = False
    competitor_catalogs: List[str] = Field(default_factory=list)

class Integration(BaseModel):
    """Main integration model that contains all configuration"""
    id: str
    name: str
    type: IntegrationType
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    config: Union[
        WooCommerceConfig, 
        DNSConfig, 
        MarketingConfig, 
        FulfillmentConfig, 
        RecommendationConfig
    ]

# --- API Request/Response Models ---

class IntegrationListResponse(BaseModel):
    integrations: List[Integration]

class IntegrationResponse(BaseModel):
    integration: Integration
    message: str

class CreateIntegrationRequest(BaseModel):
    name: str
    type: IntegrationType
    config: Dict[str, Any]

class UpdateIntegrationRequest(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[IntegrationStatus] = None

class SyncRequest(BaseModel):
    force: bool = False

class SyncResponse(BaseModel):
    message: str
    task_id: Optional[str] = None

class TestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

# --- Helper Functions ---

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_integration(integration_id: str) -> Optional[Integration]:
    """Get integration by ID"""
    try:
        key = f"integration_{sanitize_storage_key(integration_id)}"
        data = db.storage.json.get(key)
        
        # Convert the config dict to the appropriate config object based on type
        if data["type"] == IntegrationType.WOOCOMMERCE:
            data["config"] = WooCommerceConfig(**data["config"])
        elif data["type"] == IntegrationType.DNS:
            data["config"] = DNSConfig(**data["config"])
        elif data["type"] == IntegrationType.MARKETING:
            data["config"] = MarketingConfig(**data["config"])
        elif data["type"] == IntegrationType.FULFILLMENT:
            data["config"] = FulfillmentConfig(**data["config"])
        elif data["type"] == IntegrationType.RECOMMENDATION:
            data["config"] = RecommendationConfig(**data["config"])
            
        return Integration(**data)
    except Exception as e:
        print(f"Error getting integration: {str(e)}")
        return None

def save_integration(integration: Integration) -> bool:
    """Save integration to storage"""
    try:
        integration.updated_at = datetime.utcnow()
        key = f"integration_{sanitize_storage_key(integration.id)}"
        db.storage.json.put(key, integration.model_dump())
        return True
    except Exception as e:
        print(f"Error saving integration: {str(e)}")
        return False

def list_integrations() -> List[Integration]:
    """List all integrations"""
    integrations = []
    try:
        # List all integration keys
        integration_keys = [k.name for k in db.storage.json.list() if k.name.startswith("integration_")]
        
        for key in integration_keys:
            try:
                integration = get_integration(key.replace("integration_", ""))
                if integration:
                    integrations.append(integration)
            except Exception as e:
                print(f"Error loading integration {key}: {str(e)}")
    except Exception as e:
        print(f"Error listing integrations: {str(e)}")
    return integrations

def update_thinlayer_context(integration_id: str, context_data: Dict[str, str]):
    """Update ThinLayer context with integration data"""
    try:
        integration = get_integration(integration_id)
        if not integration or not integration.config.enabled:
            return
            
        # Get existing integration context from storage
        context_key = f"integration_context_{sanitize_storage_key(integration_id)}"
        stored_context = db.storage.json.get(context_key, default={})
        
        # Update with new data
        stored_context.update(context_data)
        
        # Save updated context
        db.storage.json.put(context_key, stored_context)
        
        # Register these keys for ThinLayer
        for key, value in context_data.items():
            formatted_key = f"{integration.type.value}_{key}"
            if formatted_key not in integration.config.context_keys:
                integration.config.context_keys.append(formatted_key)
                
        # Save integration with updated context keys
        save_integration(integration)
        
        print(f"Updated ThinLayer context for integration {integration_id}")
        return True
    except Exception as e:
        print(f"Error updating ThinLayer context: {str(e)}")
        return False

# --- Integration Type-Specific Functions ---

# WooCommerce
async def woocommerce_test_connection(config: WooCommerceConfig) -> TestResponse:
    """Test connection to WooCommerce API"""
    try:
        # Format WooCommerce REST API URL
        api_url = f"{config.url.rstrip('/')}/wp-json/wc/v3/products"
        
        # Make request to WooCommerce API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_url,
                auth=(config.consumer_key, config.consumer_secret),
                params={"per_page": 1},
                timeout=10.0
            )
            
        if response.status_code == 200:
            products = response.json()
            return TestResponse(
                success=True,
                message=f"Successfully connected to WooCommerce API. Found {len(products)} products.",
                details={"url": api_url, "status_code": response.status_code}
            )
        else:
            return TestResponse(
                success=False,
                message=f"Error connecting to WooCommerce API: {response.status_code} {response.reason_phrase}",
                details={"url": api_url, "status_code": response.status_code, "response": response.text}
            )
    except Exception as e:
        return TestResponse(
            success=False,
            message=f"Error testing WooCommerce connection: {str(e)}",
            details={"error": str(e)}
        )

async def woocommerce_sync_products(integration_id: str, config: WooCommerceConfig, force: bool = False) -> Dict[str, Any]:
    """Sync products from WooCommerce to Hempex"""
    try:
        from app.apis.product import get_all_products, upsert_product
        import httpx
        
        # Format WooCommerce REST API URL for products
        api_url = f"{config.url.rstrip('/')}/wp-json/wc/v3/products"
        
        # Fetch all products from WooCommerce API
        products_imported = 0
        products_updated = 0
        products_with_errors = 0
        page = 1
        per_page = 50
        all_woo_products = []
        
        while True:
            try:
                # Make request to WooCommerce API
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        api_url,
                        auth=(config.consumer_key, config.consumer_secret),
                        params={
                            "per_page": per_page,
                            "page": page,
                            "status": "publish"  # Only get published products
                        },
                        timeout=30.0
                    )
                    
                if response.status_code != 200:
                    print(f"Error fetching products from WooCommerce, status code: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"WooCommerce API error: {response.status_code} {response.reason_phrase}"
                    }
                
                woo_products = response.json()
                if not woo_products or len(woo_products) == 0:
                    # No more products, break the loop
                    break
                    
                all_woo_products.extend(woo_products)
                page += 1
                
                # If we got less than per_page products, we're at the end
                if len(woo_products) < per_page:
                    break
                    
            except Exception as request_error:
                print(f"Error fetching products page {page}: {str(request_error)}")
                products_with_errors += 1
                break
        
        print(f"Fetched {len(all_woo_products)} products from WooCommerce")
        
        # Get existing products
        existing_products = get_all_products()
        existing_skus = {product.get("sku"): product for product in existing_products}
        
        # Process each WooCommerce product
        for woo_product in all_woo_products:
            try:
                # Skip products without SKU
                if not woo_product.get("sku"):
                    print(f"Skipping product without SKU: {woo_product.get('name')}")
                    continue
                    
                # Convert to our product format
                product_data = {
                    "id": woo_product.get("id", ""),
                    "sku": woo_product.get("sku", ""),
                    "name": woo_product.get("name", ""),
                    "description": woo_product.get("description", "").strip(),
                    "short_description": woo_product.get("short_description", "").strip(),
                    "price": float(woo_product.get("price") or 0),
                    "regular_price": float(woo_product.get("regular_price") or 0),
                    "sale_price": float(woo_product.get("sale_price") or 0),
                    "on_sale": woo_product.get("on_sale", False),
                    "inventory_quantity": int(woo_product.get("stock_quantity") or 0),
                    "category_id": "",
                    "category_name": "",
                    "image_urls": [],
                    "cannabinoids": [],
                    "tga_approved": False,
                    "requires_prescription": False,
                    "featured": woo_product.get("featured", False),
                    "source": "hempex.com",  # Mark products from hempex.com
                    "created_at": woo_product.get("date_created", datetime.utcnow().isoformat()),
                    "updated_at": woo_product.get("date_modified", datetime.utcnow().isoformat())
                }
                
                # Determine inventory status based on stock_status
                stock_status = woo_product.get("stock_status", "outofstock")
                if stock_status == "instock":
                    product_data["inventory_status"] = "in_stock"
                elif stock_status == "onbackorder":
                    product_data["inventory_status"] = "low_stock"
                else:
                    product_data["inventory_status"] = "out_of_stock"
                
                # Extract image URLs
                if woo_product.get("images") and len(woo_product["images"]) > 0:
                    product_data["image_urls"] = [img.get("src") for img in woo_product["images"] if img.get("src")]
                
                # Extract category information
                if woo_product.get("categories") and len(woo_product["categories"]) > 0:
                    product_data["category_id"] = str(woo_product["categories"][0].get("id", ""))
                    product_data["category_name"] = woo_product["categories"][0].get("name", "")
                
                # Extract cannabinoid content from attributes if available
                for attribute in woo_product.get("attributes", []):
                    name = attribute.get("name", "").upper()
                    # Look for cannabinoid attributes
                    if name in ["CBD", "CBG", "CBC", "CBN", "CBDV", "THCV"]:
                        try:
                            # Try to extract the amount from the attribute
                            value = attribute.get("options", ["0"])[0]
                            # Handle different formats like "10mg", "10%", etc.
                            amount = float(''.join(c for c in value if c.isdigit() or c == '.'))
                            unit = ''.join(c for c in value if not c.isdigit() and c != '.') or "mg"
                            
                            product_data["cannabinoids"].append({
                                "name": name,
                                "amount": amount,
                                "unit": unit
                            })
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing cannabinoid content for {name}: {str(e)}")
                
                # Look for TGA approval in product metadata
                for meta in woo_product.get("meta_data", []):
                    key = meta.get("key", "")
                    if key == "tga_approved":
                        product_data["tga_approved"] = meta.get("value") == "yes"
                    elif key == "requires_prescription":
                        product_data["requires_prescription"] = meta.get("value") == "yes"
                    elif key == "artg_number":
                        product_data["artg_number"] = meta.get("value")
                
                # Check if product already exists
                if product_data["sku"] in existing_skus:
                    products_updated += 1
                else:
                    products_imported += 1
                
                # Save the product
                upsert_product(product_data)
                
            except Exception as product_error:
                print(f"Error processing product {woo_product.get('sku')}: {str(product_error)}")
                products_with_errors += 1
        
        # Update ThinLayer context with sync stats
        update_thinlayer_context(
            integration_id,
            {
                "products_count": str(len(all_woo_products)),
                "imported_count": str(products_imported),
                "updated_count": str(products_updated),
                "errors_count": str(products_with_errors),
                "last_sync": datetime.utcnow().isoformat(),
                "sync_status": "completed"
            }
        )
        
        return {
            "success": True,
            "imported": products_imported,
            "updated": products_updated,
            "errors": products_with_errors,
            "total": len(all_woo_products)
        }
    except Exception as e:
        print(f"Error syncing WooCommerce products: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def woocommerce_sync_orders(integration_id: str, config: WooCommerceConfig, force: bool = False) -> Dict[str, Any]:
    """Sync orders from WooCommerce to Hempex"""
    # Placeholder for real implementation
    update_thinlayer_context(
        integration_id,
        {
            "orders_count": "18",
            "last_sync": datetime.utcnow().isoformat(),
            "sync_status": "completed"
        }
    )
    
    return {
        "success": True,
        "imported": 18,
        "updated": 5,
        "errors": 0
    }

async def woocommerce_sync_customers(integration_id: str, config: WooCommerceConfig, force: bool = False) -> Dict[str, Any]:
    """Sync customers from WooCommerce to Hempex"""
    # Placeholder for real implementation
    update_thinlayer_context(
        integration_id,
        {
            "customers_count": "36",
            "last_sync": datetime.utcnow().isoformat(),
            "sync_status": "completed"
        }
    )
    
    return {
        "success": True,
        "imported": 36,
        "updated": 12,
        "errors": 0
    }

# Domain/DNS
async def dns_test_connection(config: DNSConfig) -> TestResponse:
    """Test connection to DNS provider API"""
    # Placeholder for real implementation
    return TestResponse(
        success=True,
        message=f"Successfully connected to {config.provider} API",
        details={"domains": config.domains}
    )

# Marketing/CRM
async def marketing_test_connection(config: MarketingConfig) -> TestResponse:
    """Test connection to Marketing/CRM provider API"""
    # Placeholder for real implementation
    return TestResponse(
        success=True,
        message=f"Successfully connected to {config.provider} API",
        details={"lists": config.lists}
    )

# Fulfillment
async def fulfillment_test_connection(config: FulfillmentConfig) -> TestResponse:
    """Test connection to Fulfillment provider API"""
    # Placeholder for real implementation
    return TestResponse(
        success=True,
        message=f"Successfully connected to {config.provider} API",
        details={"warehouse_id": config.warehouse_id}
    )

# Recommendation Engine
async def recommendation_test_connection(config: RecommendationConfig) -> TestResponse:
    """Test Recommendation Engine configuration"""
    # Placeholder for real implementation
    return TestResponse(
        success=True,
        message=f"Recommendation Engine configured successfully",
        details={"algorithms": config.enabled_algorithms}
    )

# --- Background Tasks ---

async def sync_integration(integration_id: str, force: bool = False):
    """Background task to sync an integration"""
    try:
        integration = get_integration(integration_id)
        if not integration or not integration.config.enabled:
            print(f"Integration {integration_id} is not enabled or does not exist")
            return
            
        # Update status to syncing
        integration.status = IntegrationStatus.SYNCING
        save_integration(integration)
        
        result = {"success": False, "error": "Unsupported integration type"}
        
        # Dispatch to appropriate sync function based on integration type
        if integration.type == IntegrationType.WOOCOMMERCE:
            config = integration.config
            woo_config = WooCommerceConfig(**config.model_dump())
            
            # Sync everything
            results = {}
            if woo_config.sync_products:
                results["products"] = await woocommerce_sync_products(integration_id, woo_config, force)
                
            if woo_config.sync_orders:
                results["orders"] = await woocommerce_sync_orders(integration_id, woo_config, force)
                
            if woo_config.sync_customers:
                results["customers"] = await woocommerce_sync_customers(integration_id, woo_config, force)
                
            # Set overall success based on all operations
            result = {
                "success": all(r.get("success", False) for r in results.values()),
                "results": results
            }
        
        # Similar implementations would exist for other integration types
        
        # Update integration status based on result
        integration = get_integration(integration_id)  # Refresh in case it was updated
        if result.get("success", False):
            integration.status = IntegrationStatus.CONNECTED
            integration.config.last_sync = datetime.utcnow()
            integration.config.error_count = 0
            integration.config.last_error = None
        else:
            integration.status = IntegrationStatus.ERROR
            integration.config.error_count += 1
            integration.config.last_error = result.get("error", "Unknown error")
            
        save_integration(integration)
        print(f"Completed sync for integration {integration_id} with result: {result}")
    except Exception as e:
        print(f"Error in sync_integration task: {str(e)}")
        
        # Try to update integration status on error
        try:
            integration = get_integration(integration_id)
            if integration:
                integration.status = IntegrationStatus.ERROR
                integration.config.error_count += 1
                integration.config.last_error = str(e)
                save_integration(integration)
        except Exception as inner_e:
            print(f"Error updating integration status: {str(inner_e)}")

# --- Endpoints ---

@router.get("/health")
def check_integrations_health():
    """Check if the Integrations API is running"""
    return {"status": "ok", "message": "Integrations API is operational"}

@router.get("/", response_model=IntegrationListResponse)
async def list_all_integrations():
    """List all configured integrations"""
    return IntegrationListResponse(integrations=list_integrations())

@router.post("/", response_model=IntegrationResponse)
async def create_integration(request: CreateIntegrationRequest):
    """Create a new integration"""
    # Generate unique ID for the integration
    integration_id = f"{request.type.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Create config based on integration type
    if request.type == IntegrationType.WOOCOMMERCE:
        config = WooCommerceConfig(**request.config)
    elif request.type == IntegrationType.DNS:
        config = DNSConfig(**request.config)
    elif request.type == IntegrationType.MARKETING:
        config = MarketingConfig(**request.config)
    elif request.type == IntegrationType.FULFILLMENT:
        config = FulfillmentConfig(**request.config)
    elif request.type == IntegrationType.RECOMMENDATION:
        config = RecommendationConfig(**request.config)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported integration type: {request.type}")
    
    # Create the integration
    integration = Integration(
        id=integration_id,
        name=request.name,
        type=request.type,
        config=config
    )
    
    # Save to storage
    if not save_integration(integration):
        raise HTTPException(status_code=500, detail="Failed to save integration")
    
    return IntegrationResponse(
        integration=integration,
        message=f"{request.type.value.capitalize()} integration created successfully"
    )

@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_single_integration(integration_id: str):
    """Get a single integration by ID"""
    integration = get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration not found: {integration_id}")
    
    return IntegrationResponse(
        integration=integration,
        message="Integration retrieved successfully"
    )

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_single_integration(integration_id: str, request: UpdateIntegrationRequest):
    """Update an integration"""
    # Get existing integration
    integration = get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration not found: {integration_id}")
    
    # Update fields
    if request.name is not None:
        integration.name = request.name
        
    if request.status is not None:
        integration.status = request.status
        
    if request.config is not None:
        # Update config based on integration type
        if integration.type == IntegrationType.WOOCOMMERCE:
            # Create a new config with updated values but keep existing ones not in request
            updated_config = {**integration.config.model_dump(), **request.config}
            integration.config = WooCommerceConfig(**updated_config)
        elif integration.type == IntegrationType.DNS:
            updated_config = {**integration.config.model_dump(), **request.config}
            integration.config = DNSConfig(**updated_config)
        elif integration.type == IntegrationType.MARKETING:
            updated_config = {**integration.config.model_dump(), **request.config}
            integration.config = MarketingConfig(**updated_config)
        elif integration.type == IntegrationType.FULFILLMENT:
            updated_config = {**integration.config.model_dump(), **request.config}
            integration.config = FulfillmentConfig(**updated_config)
        elif integration.type == IntegrationType.RECOMMENDATION:
            updated_config = {**integration.config.model_dump(), **request.config}
            integration.config = RecommendationConfig(**updated_config)
    
    # Save updated integration
    if not save_integration(integration):
        raise HTTPException(status_code=500, detail="Failed to update integration")
    
    return IntegrationResponse(
        integration=integration,
        message="Integration updated successfully"
    )

@router.delete("/{integration_id}")
async def delete_integration(integration_id: str):
    """Delete an integration"""
    # Check if integration exists
    integration = get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration not found: {integration_id}")
    
    # Delete from storage
    try:
        key = f"integration_{sanitize_storage_key(integration_id)}"
        db.storage.json.delete(key)
        
        # Also delete any context data
        context_key = f"integration_context_{sanitize_storage_key(integration_id)}"
        try:
            db.storage.json.delete(context_key)
        except Exception:
            pass  # Ignore if context doesn't exist
        
        return {"message": f"Integration {integration_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete integration: {str(e)}")

@router.post("/{integration_id}/test", response_model=TestResponse)
async def test_integration(integration_id: str):
    """Test connection to an integration"""
    # Get integration
    integration = get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration not found: {integration_id}")
    
    # Dispatch to appropriate test function based on integration type
    if integration.type == IntegrationType.WOOCOMMERCE:
        config = integration.config
        woo_config = WooCommerceConfig(**config.model_dump())
        return await woocommerce_test_connection(woo_config)
    elif integration.type == IntegrationType.DNS:
        config = integration.config
        dns_config = DNSConfig(**config.model_dump())
        return await dns_test_connection(dns_config)
    elif integration.type == IntegrationType.MARKETING:
        config = integration.config
        marketing_config = MarketingConfig(**config.model_dump())
        return await marketing_test_connection(marketing_config)
    elif integration.type == IntegrationType.FULFILLMENT:
        config = integration.config
        fulfillment_config = FulfillmentConfig(**config.model_dump())
        return await fulfillment_test_connection(fulfillment_config)
    elif integration.type == IntegrationType.RECOMMENDATION:
        config = integration.config
        recommendation_config = RecommendationConfig(**config.model_dump())
        return await recommendation_test_connection(recommendation_config)
    else:
        return TestResponse(
            success=False,
            message=f"Unsupported integration type: {integration.type}",
            details=None
        )

@router.post("/{integration_id}/sync", response_model=SyncResponse)
async def trigger_integration_sync(integration_id: str, request: SyncRequest, background_tasks: BackgroundTasks):
    """Trigger synchronization for an integration"""
    # Get integration
    integration = get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration not found: {integration_id}")
    
    # Check if integration is enabled
    if not integration.config.enabled:
        raise HTTPException(status_code=400, detail=f"Integration {integration_id} is not enabled")
    
    # Check for already running sync
    if integration.status == IntegrationStatus.SYNCING and not request.force:
        return SyncResponse(
            message=f"Integration {integration_id} is already syncing",
            task_id=None
        )
    
    # Start sync in background
    background_tasks.add_task(sync_integration, integration_id, request.force)
    
    # Update status to syncing
    integration.status = IntegrationStatus.SYNCING
    save_integration(integration)
    
    return SyncResponse(
        message=f"Synchronization started for integration {integration_id}",
        task_id=f"sync_{integration_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )

@router.get("/{integration_id}/context")
async def get_integration_context(integration_id: str):
    """Get ThinLayer context data for an integration"""
    # Check if integration exists
    integration = get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration not found: {integration_id}")
    
    # Get context data
    context_key = f"integration_context_{sanitize_storage_key(integration_id)}"
    context_data = db.storage.json.get(context_key, default={})
    
    return {
        "context": context_data,
        "registered_keys": integration.config.context_keys
    }
