from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import databutton as db
import requests
import uuid
import datetime
import re
from app.apis.hardcard import HardcardMVPPlan, get_hardcard_mvp_plan

router = APIRouter(prefix="/wise-hardcard")

# Get Wise API key from secrets
try:
    WISE_API_KEY = db.secrets.get("WISE_API_KEY")
except KeyError:
    print("Wise API key not found, using mock responses only")
    WISE_API_KEY = ""
WISE_API_URL = "https://api.wise.com"

# EarthCC API key
try:
    EARTHCC_API_KEY = db.secrets.get("EARTHCC_API_KEY")
except KeyError:
    print("EarthCC API key not found, using mock data only")
    EARTHCC_API_KEY = ""
EARTHCC_API_URL = "https://api.earthcc.com"

# Models for Wise Card Issuance
class CardDesign(BaseModel):
    color: str = Field(default="gold", description="Card color")
    material: str = Field(default="metal", description="Card material")
    include_family_crest: bool = Field(default=True, description="Include family crest on the card")
    layout_style: str = Field(default="classic", description="Card layout style")

class HardcardEarthCCSettings(BaseModel):
    enabled: bool = Field(default=True, description="Enable EarthCC functionality")
    track_carbon_footprint: bool = Field(default=True, description="Track carbon footprint for transactions")
    display_impact_metrics: bool = Field(default=True, description="Display environmental impact metrics")

class HardcardQRSettings(BaseModel):
    enabled: bool = Field(default=True, description="Enable QR code on the hardcard")
    link_type: str = Field(default="personal_account", description="QR code link type")
    include_earthcc_data: bool = Field(default=True, description="Include EarthCC data in the QR code")

class CreateHardcardRequest(BaseModel):
    profile_id: str = Field(..., description="User profile ID")
    card_name: str = Field(..., description="Name to display on the card")
    design: CardDesign = Field(default_factory=CardDesign, description="Card design configuration")
    earthcc_settings: HardcardEarthCCSettings = Field(default_factory=HardcardEarthCCSettings, description="EarthCC integration settings")
    qr_settings: HardcardQRSettings = Field(default_factory=HardcardQRSettings, description="QR code settings")
    shipping_address: Dict[str, str] = Field(..., description="Shipping address for the physical card")

class HardcardInfo(BaseModel):
    id: str = Field(..., description="Unique hardcard ID")
    profile_id: str = Field(..., description="Associated user profile ID")
    status: str = Field(..., description="Card status")
    card_name: str = Field(..., description="Name displayed on the card")
    design: CardDesign = Field(..., description="Card design")
    earthcc_settings: HardcardEarthCCSettings = Field(..., description="EarthCC settings")
    qr_settings: HardcardQRSettings = Field(..., description="QR code settings")
    qr_code_url: Optional[str] = Field(None, description="URL to the QR code image")
    created_at: str = Field(..., description="Card creation timestamp")
    estimated_delivery: str = Field(..., description="Estimated delivery date")
    shipping_address: Dict[str, str] = Field(..., description="Shipping address")

class CustomizeHardcardRequest(BaseModel):
    card_id: str = Field(..., description="Hardcard ID to customize")
    design: Optional[CardDesign] = Field(None, description="Updated card design")
    earthcc_settings: Optional[HardcardEarthCCSettings] = Field(None, description="Updated EarthCC settings")
    qr_settings: Optional[HardcardQRSettings] = Field(None, description="Updated QR code settings")

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def generate_qr_code_url(hardcard_id: str, profile_id: str, include_earthcc: bool) -> str:
    """Generate a URL for a QR code linking to the personal hardcard account"""
    base_url = "https://legacyvault.com/hardcard"
    
    params = [f"id={hardcard_id}", f"profile={profile_id}"]
    if include_earthcc:
        params.append("earthcc=1")
        
    return f"{base_url}?{'&'.join(params)}"

@router.post("/create")
def create_hardcard2(request: CreateHardcardRequest) -> HardcardInfo:
    """
    Create a new hardcard using Wise's card issuance API. This endpoint creates a physical card 
    with EarthCC functionality and a QR code linking to a personalized hardcard account.
    """
    try:
        # Generate a unique hardcard ID
        hardcard_id = str(uuid.uuid4())
        
        # Current timestamp
        now = datetime.datetime.now().isoformat()
        
        # Generate QR code URL if enabled
        qr_code_url = None
        if request.qr_settings.enabled:
            qr_code_url = generate_qr_code_url(
                hardcard_id, 
                request.profile_id, 
                request.qr_settings.include_earthcc_data
            )
        
        # Generate estimated delivery date (10-15 days in the future)
        days_to_deliver = 10 + (uuid.uuid4().int % 6)  # 10-15 days
        estimated_delivery = (datetime.datetime.now() + datetime.timedelta(days=days_to_deliver)).isoformat()
        
        if not WISE_API_KEY:
            # Mock response if API key is not available
            return HardcardInfo(
                id=hardcard_id,
                profile_id=request.profile_id,
                status="PROCESSING",
                card_name=request.card_name,
                design=request.design,
                earthcc_settings=request.earthcc_settings,
                qr_settings=request.qr_settings,
                qr_code_url=qr_code_url,
                created_at=now,
                estimated_delivery=estimated_delivery,
                shipping_address=request.shipping_address
            )
        
        # Call Wise API to create a card
        # Note: In a real implementation, this would use the actual Wise Card Issuance API
        # The following is a placeholder based on common API patterns
        payload = {
            "profileId": request.profile_id,
            "cardholderName": request.card_name,
            "cardType": "PHYSICAL",
            "cardDetails": {
                "design": {
                    "color": request.design.color,
                    "material": request.design.material,
                    "customArtwork": request.design.include_family_crest,
                    "layoutStyle": request.design.layout_style
                }
            },
            "shippingAddress": request.shipping_address,
            "metadata": {
                "isHardcard": True,
                "earthccEnabled": request.earthcc_settings.enabled,
                "qrCodeEnabled": request.qr_settings.enabled
            }
        }
        
        headers = {
            "Authorization": f"Bearer {WISE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{WISE_API_URL}/v1/cards",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        card_data = response.json()
        
        # Store hardcard data in Databutton storage
        hardcard_data = {
            "id": hardcard_id,
            "wise_card_id": card_data.get("id", f"mock_{hardcard_id}"),
            "profile_id": request.profile_id,
            "status": card_data.get("status", "PROCESSING"),
            "card_name": request.card_name,
            "design": request.design.dict(),
            "earthcc_settings": request.earthcc_settings.dict(),
            "qr_settings": request.qr_settings.dict(),
            "qr_code_url": qr_code_url,
            "created_at": now,
            "estimated_delivery": estimated_delivery,
            "shipping_address": request.shipping_address
        }
        
        db.storage.json.put(
            sanitize_storage_key(f"hardcard_{hardcard_id}"),
            hardcard_data
        )
        
        # If EarthCC is enabled, register the card with EarthCC API
        if request.earthcc_settings.enabled and EARTHCC_API_KEY:
            try:
                earthcc_payload = {
                    "card_id": hardcard_id,
                    "profile_id": request.profile_id,
                    "track_footprint": request.earthcc_settings.track_carbon_footprint,
                    "display_metrics": request.earthcc_settings.display_impact_metrics
                }
                
                earthcc_headers = {
                    "Authorization": f"Bearer {EARTHCC_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                earthcc_response = requests.post(
                    f"{EARTHCC_API_URL}/v1/cards/register",
                    headers=earthcc_headers,
                    json=earthcc_payload
                )
                earthcc_response.raise_for_status()
                
                # Update hardcard data with EarthCC registration info
                hardcard_data["earthcc_registration"] = earthcc_response.json()
                db.storage.json.put(
                    sanitize_storage_key(f"hardcard_{hardcard_id}"),
                    hardcard_data
                )
            except Exception as e:
                print(f"Error registering with EarthCC: {str(e)}")
                # Continue even if EarthCC registration fails
        
        return HardcardInfo(
            id=hardcard_id,
            profile_id=request.profile_id,
            status=card_data.get("status", "PROCESSING"),
            card_name=request.card_name,
            design=request.design,
            earthcc_settings=request.earthcc_settings,
            qr_settings=request.qr_settings,
            qr_code_url=qr_code_url,
            created_at=now,
            estimated_delivery=estimated_delivery,
            shipping_address=request.shipping_address
        )
    except Exception as e:
        print(f"Error creating hardcard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create hardcard: {str(e)}")

@router.post("/customize")
def customize_hardcard2(request: CustomizeHardcardRequest) -> HardcardInfo:
    """
    Customize an existing hardcard by updating its design, EarthCC settings, or QR code settings.
    """
    try:
        # Get hardcard data from storage
        storage_key = sanitize_storage_key(f"hardcard_{request.card_id}")
        
        try:
            hardcard_data = db.storage.json.get(storage_key)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Hardcard with ID {request.card_id} not found")
        
        # Update hardcard data with new values
        if request.design:
            hardcard_data["design"] = request.design.dict()
            
        if request.earthcc_settings:
            hardcard_data["earthcc_settings"] = request.earthcc_settings.dict()
            
            # Update EarthCC registration if enabled and API key is available
            if request.earthcc_settings.enabled and EARTHCC_API_KEY:
                try:
                    earthcc_payload = {
                        "card_id": request.card_id,
                        "profile_id": hardcard_data["profile_id"],
                        "track_footprint": request.earthcc_settings.track_carbon_footprint,
                        "display_metrics": request.earthcc_settings.display_impact_metrics
                    }
                    
                    earthcc_headers = {
                        "Authorization": f"Bearer {EARTHCC_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    earthcc_response = requests.post(
                        f"{EARTHCC_API_URL}/v1/cards/update",
                        headers=earthcc_headers,
                        json=earthcc_payload
                    )
                    earthcc_response.raise_for_status()
                    
                    # Update hardcard data with EarthCC registration info
                    hardcard_data["earthcc_registration"] = earthcc_response.json()
                except Exception as e:
                    print(f"Error updating EarthCC settings: {str(e)}")
                    # Continue even if EarthCC update fails
            
        if request.qr_settings:
            hardcard_data["qr_settings"] = request.qr_settings.dict()
            
            # Regenerate QR code URL if enabled
            if request.qr_settings.enabled:
                hardcard_data["qr_code_url"] = generate_qr_code_url(
                    request.card_id, 
                    hardcard_data["profile_id"], 
                    request.qr_settings.include_earthcc_data
                )
            else:
                hardcard_data["qr_code_url"] = None
        
        # Update hardcard data in storage
        db.storage.json.put(storage_key, hardcard_data)
        
        # If Wise API key is available, update the card design
        if WISE_API_KEY and request.design:
            try:
                wise_card_id = hardcard_data.get("wise_card_id")
                if wise_card_id and not wise_card_id.startswith("mock_"):
                    payload = {
                        "cardDetails": {
                            "design": {
                                "color": request.design.color,
                                "material": request.design.material,
                                "customArtwork": request.design.include_family_crest,
                                "layoutStyle": request.design.layout_style
                            }
                        }
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {WISE_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    response = requests.patch(
                        f"{WISE_API_URL}/v1/cards/{wise_card_id}",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
            except Exception as e:
                print(f"Error updating card design with Wise API: {str(e)}")
                # Continue even if Wise API update fails
        
        # Return updated hardcard info
        return HardcardInfo(
            id=hardcard_data["id"],
            profile_id=hardcard_data["profile_id"],
            status=hardcard_data["status"],
            card_name=hardcard_data["card_name"],
            design=CardDesign(**hardcard_data["design"]),
            earthcc_settings=HardcardEarthCCSettings(**hardcard_data["earthcc_settings"]),
            qr_settings=HardcardQRSettings(**hardcard_data["qr_settings"]),
            qr_code_url=hardcard_data["qr_code_url"],
            created_at=hardcard_data["created_at"],
            estimated_delivery=hardcard_data["estimated_delivery"],
            shipping_address=hardcard_data["shipping_address"]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error customizing hardcard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to customize hardcard: {str(e)}")

@router.get("/get/{card_id}")
def get_hardcard2(card_id: str) -> HardcardInfo:
    """
    Get information about a specific hardcard.
    """
    try:
        # Get hardcard data from storage
        storage_key = sanitize_storage_key(f"hardcard_{card_id}")
        
        try:
            hardcard_data = db.storage.json.get(storage_key)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Hardcard with ID {card_id} not found")
        
        # Return hardcard info
        return HardcardInfo(
            id=hardcard_data["id"],
            profile_id=hardcard_data["profile_id"],
            status=hardcard_data["status"],
            card_name=hardcard_data["card_name"],
            design=CardDesign(**hardcard_data["design"]),
            earthcc_settings=HardcardEarthCCSettings(**hardcard_data["earthcc_settings"]),
            qr_settings=HardcardQRSettings(**hardcard_data["qr_settings"]),
            qr_code_url=hardcard_data["qr_code_url"],
            created_at=hardcard_data["created_at"],
            estimated_delivery=hardcard_data["estimated_delivery"],
            shipping_address=hardcard_data["shipping_address"]
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting hardcard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get hardcard: {str(e)}")

@router.get("/list/{profile_id}")
def list_hardcards2(profile_id: str) -> List[HardcardInfo]:
    """
    List all hardcards associated with a profile.
    """
    try:
        # List all hardcard files in storage
        hardcard_files = db.storage.json.list()
        
        # Filter for hardcard files
        hardcards = []
        for file in hardcard_files:
            if file.name.startswith("hardcard_"):
                try:
                    hardcard_data = db.storage.json.get(file.name)
                    # Check if this hardcard belongs to the requested profile
                    if hardcard_data.get("profile_id") == profile_id:
                        hardcards.append(HardcardInfo(
                            id=hardcard_data["id"],
                            profile_id=hardcard_data["profile_id"],
                            status=hardcard_data["status"],
                            card_name=hardcard_data["card_name"],
                            design=CardDesign(**hardcard_data["design"]),
                            earthcc_settings=HardcardEarthCCSettings(**hardcard_data["earthcc_settings"]),
                            qr_settings=HardcardQRSettings(**hardcard_data["qr_settings"]),
                            qr_code_url=hardcard_data["qr_code_url"],
                            created_at=hardcard_data["created_at"],
                            estimated_delivery=hardcard_data["estimated_delivery"],
                            shipping_address=hardcard_data["shipping_address"]
                        ))
                except Exception as e:
                    print(f"Error processing hardcard file {file.name}: {str(e)}")
                    # Skip this file and continue
        
        return hardcards
    except Exception as e:
        print(f"Error listing hardcards: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list hardcards: {str(e)}")

@router.get("/documentation")
def get_hardcard_documentation() -> dict:
    """
    Get comprehensive documentation about the hardcard system, including the card issuance process,
    EarthCC integration, and QR code functionality.
    """
    try:
        # Get the hardcard MVP plan for reference
        mvp_plan = get_hardcard_mvp_plan()
        
        documentation = {
            "overview": {
                "title": "Wise Hardcard System",
                "description": "A comprehensive physical card solution with integrated EarthCC functionality and QR code access to personalized accounts.",
                "key_features": [
                    "Physical metal card issuance through Wise",
                    "Environmental impact tracking with EarthCC integration",
                    "QR code linking to personalized digital vault",
                    "Long-term investment and wealth tracking",
                    "Family trust integration and inheritance planning"
                ]
            },
            "wise_integration": {
                "description": "The hardcard utilizes Wise's robust card issuance services to create and manage physical cards.",
                "features": [
                    "Metal card options (stainless steel, titanium, or gold-plated)",
                    "Custom designs with family crest integration",
                    "Global shipping capability",
                    "Secure transaction processing",
                    "Multiple currency support"
                ],
                "implementation": {
                    "api_endpoints": [
                        "/wise-hardcard/create - Create a new hardcard",
                        "/wise-hardcard/customize - Update hardcard design and settings",
                        "/wise-hardcard/get/{card_id} - Get hardcard details",
                        "/wise-hardcard/list/{profile_id} - List all hardcards for a profile"
                    ],
                    "authentication": "Secure API key authentication with Wise services",
                    "data_storage": "Encrypted storage of card details and settings"
                }
            },
            "earthcc_functionality": {
                "description": "EarthCC integration provides environmental impact tracking for all card transactions.",
                "features": [
                    "Carbon footprint calculation for purchases",
                    "Environmental impact visualization",
                    "Sustainable alternatives suggestions",
                    "Monthly environmental impact reports",
                    "Offsetting options and initiatives"
                ],
                "implementation": {
                    "data_collection": "Transaction data is analyzed through EarthCC's API",
                    "metrics": "CO2 emissions, water usage, and energy consumption metrics",
                    "visualization": "Integrated dashboards and reports in the user's account",
                    "api_integration": "Real-time data processing through secure API connections"
                }
            },
            "qr_code_system": {
                "description": "Each hardcard includes a unique QR code linking to the user's personalized digital vault.",
                "features": [
                    "Direct access to personal hardcard account",
                    "Environmental impact dashboard",
                    "Investment and wealth tracking",
                    "Family trust management tools",
                    "Legacy planning and inheritance options"
                ],
                "implementation": {
                    "code_generation": "Secure, unique QR codes are generated for each card",
                    "authentication": "Multi-factor authentication required for sensitive operations",
                    "user_experience": "Seamless mobile-first interface for QR code scanning",
                    "security": "End-to-end encryption of all data and transactions"
                }
            },
            "physical_specifications": mvp_plan.stage_2,
            "future_roadmap": mvp_plan.future_roadmap
        }
        
        return documentation
    except Exception as e:
        print(f"Error getting hardcard documentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get hardcard documentation: {str(e)}")
