from pydantic import BaseModel
from fastapi import APIRouter
import json
import databutton as db
import re

router = APIRouter()

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

class iPhoneAppPlan(BaseModel):
    """iPhone App Implementation Plan"""
    version: str = "1.0.0"
    app_name: str = "Legacy Vault"
    min_ios_version: str = "15.0"
    target_devices: list[str] = ["iPhone 13 or newer", "iPhone 12 or newer", "iPhone 11 or newer"]
    
    # Core features
    core_features: list[dict] = [
        {
            "name": "Authentication",
            "description": "Multi-factor authentication with biometrics, Google Sign-In and Hardcard verification",
            "priority": "Critical",
            "estimated_effort": "High",
            "dependencies": ["Firebase Authentication", "Google Sign-In SDK", "Local Authentication Framework"]
        },
        {
            "name": "Legacy Dashboard",
            "description": "Main dashboard showing investment progress, milestones, and trust fund activities",
            "priority": "High",
            "estimated_effort": "Medium",
            "dependencies": ["Firebase Firestore", "Charts Library"]
        },
        {
            "name": "Hardcard Integration",
            "description": "QR code and NFC scanning to link physical Hardcards with digital accounts",
            "priority": "Critical",
            "estimated_effort": "High",
            "dependencies": ["AVFoundation", "CoreNFC"]
        },
        {
            "name": "Investment Portfolio",
            "description": "View and manage investment portfolio with real-time data",
            "priority": "High",
            "estimated_effort": "Medium",
            "dependencies": ["Firebase Firestore", "Charts Library"]
        },
        {
            "name": "Starmap System",
            "description": "Cryptocurrency wallet and instant payment system",
            "priority": "Medium",
            "estimated_effort": "High",
            "dependencies": ["Blockchain SDK", "Secure Enclave"]
        },
        {
            "name": "Personal Assistant",
            "description": "AI-powered assistant for financial guidance and life planning",
            "priority": "Medium",
            "estimated_effort": "High",
            "dependencies": ["OpenAI SDK", "Speech Recognition"]
        },
        {
            "name": "Trust Fund Management",
            "description": "View and manage trust fund details, beneficiaries, and strategies",
            "priority": "High",
            "estimated_effort": "Medium",
            "dependencies": ["Firebase Firestore"]
        },
        {
            "name": "Security Settings",
            "description": "Configure security settings with adaptive security learning",
            "priority": "High",
            "estimated_effort": "Medium",
            "dependencies": ["Firebase Authentication", "Local Authentication Framework"]
        },
        {
            "name": "Notifications",
            "description": "Push notifications for investment updates, milestones, and security alerts",
            "priority": "Medium",
            "estimated_effort": "Low",
            "dependencies": ["Firebase Cloud Messaging"]
        },
        {
            "name": "Content DAOs",
            "description": "Browse and manage content DAOs for trust funding",
            "priority": "Low",
            "estimated_effort": "Medium",
            "dependencies": ["Firebase Firestore"]
        }
    ]
    
    # Technical architecture
    technical_architecture: dict = {
        "frontend": {
            "framework": "Swift UI",
            "design_system": "Custom Legacy Vault Design System",
            "state_management": "Combine Framework",
            "navigation": "SwiftUI Navigation Stack"
        },
        "backend": {
            "api_integration": "Same APIs as web platform",
            "real_time_data": "Firebase Firestore",
            "authentication": "Firebase Auth with custom claims",
            "local_storage": "Core Data with encryption"
        },
        "security": {
            "data_encryption": "AES-256 for stored data",
            "secure_communication": "TLS 1.3",
            "biometric_auth": "Face ID / Touch ID",
            "hardware_security": "Secure Enclave for sensitive operations",
            "certificate_pinning": "Enabled for API communications"
        },
        "dependencies": {
            "firebase": "Firebase iOS SDK",
            "authentication": "Google Sign-In SDK, LocalAuthentication framework",
            "networking": "URLSession with Combine",
            "crypto": "CryptoKit",
            "qr_scanning": "AVFoundation",
            "nfc": "CoreNFC",
            "charts": "Swift Charts or Charts library",
            "notifications": "UserNotifications framework + Firebase Cloud Messaging"
        }
    }
    
    # Integration strategy
    integration_strategy: dict = {
        "api_compatibility": "Use same API endpoints as web platform",
        "data_sync": "Firebase Firestore for real-time data synchronization",
        "authentication": "Shared Firebase Authentication with web platform",
        "offline_support": "Local caching with Core Data and sync when online",
        "feature_parity": "Core features match web platform with mobile-optimized UX",
        "deployment": "TestFlight for beta testing, App Store for public release"
    }
    
    # Development phases
    development_phases: list[dict] = [
        {
            "phase": "Planning and Design",
            "timeline": "2 weeks",
            "deliverables": ["Finalized wireframes", "Technical architecture document", "API requirements", "Sprint planning"]
        },
        {
            "phase": "Foundation Development",
            "timeline": "4 weeks",
            "deliverables": ["Project setup", "Authentication implementation", "Core API integration", "Basic navigation"]
        },
        {
            "phase": "Core Feature Development",
            "timeline": "8 weeks",
            "deliverables": ["Dashboard implementation", "Portfolio view", "Hardcard integration", "Security settings"]
        },
        {
            "phase": "Extended Feature Development",
            "timeline": "6 weeks",
            "deliverables": ["Personal assistant", "Trust fund management", "Starmap system", "Content DAOs"]
        },
        {
            "phase": "Testing and Refinement",
            "timeline": "4 weeks",
            "deliverables": ["Internal testing", "Bug fixes", "Performance optimization", "Security audit"]
        },
        {
            "phase": "Beta Testing",
            "timeline": "3 weeks",
            "deliverables": ["TestFlight release", "User feedback collection", "Final refinements"]
        },
        {
            "phase": "Launch",
            "timeline": "1 week",
            "deliverables": ["App Store submission", "Marketing materials", "Launch support"]
        }
    ]
    
    # User experience design principles
    design_principles: list[str] = [
        "Sophisticated futurism with timeless elegance",
        "Balance of wealth management tradition and forward-thinking strategy",
        "Time-centric visualization for investment growth across decades",
        "Inheritance-focused layouts prioritizing key milestones",
        "Nested hierarchy interfaces reflecting family structure",
        "Dual-mode viewing for conservative and aggressive investments",
        "Subtle blockchain integration visuals maintaining sophistication",
        "Dark mode as primary theme with architectural geometry inspired by legacy buildings",
        "Hexagonal patterns (blockchain) combined with classic arches (generational stability)",
        "Distinguished serif for headlines, geometric sans-serif for data",
        "Monospaced numbers for financial data alignment"
    ]
    
    # Physical Hardcard integration features
    hardcard_integration: dict = {
        "authentication_methods": [
            "QR code scanning via camera",
            "NFC tag reading (iPhone 7 and newer)",
            "Manual entry of Hardcard ID with additional verification"
        ],
        "verification_flow": [
            "1. Scan Hardcard via QR or NFC",
            "2. Verify with Google authentication",
            "3. Complete with Face ID/Touch ID confirmation"
        ],
        "security_features": [
            "One-time-use challenge codes for high-value transactions",
            "Proximity detection to prevent remote attacks",
            "Rate limiting for failed authentication attempts",
            "Device binding to prevent unauthorized devices"
        ],
        "physical_considerations": [
            "Metal and sapphire Hardcard optimal for NFC and durability",
            "Printable paper Hardcard option with QR code only",
            "QR code laser etching for premium Hardcards"
        ]
    }
    
    # Key wireframes
    wireframes: dict = {
        "authentication": {
            "screens": [
                "Welcome",
                "Google Sign-In",
                "Hardcard Scanning",
                "Biometric Verification",
                "Security Setup"
            ],
            "flow": "Linear with fallback options for each authentication method"
        },
        "dashboard": {
            "layout": "Card-based with scrollable sections",
            "primary_elements": [
                "Trust fund value graph (time-based)",
                "Investment milestone timeline",
                "Recent activities",
                "Security status",
                "Quick actions"
            ],
            "visualization": "Vertical growth charts with generational markers"
        },
        "portfolio": {
            "layout": "Tabbed interface with list and detail views",
            "primary_elements": [
                "Asset allocation chart",
                "Investment categories",
                "Performance metrics",
                "Bitcoin holdings",
                "Transaction history"
            ],
            "visualization": "Nested hexagonal patterns representing diversification"
        },
        "security": {
            "layout": "Multi-section scrollable view",
            "primary_elements": [
                "Security score",
                "Authentication methods",
                "Hardcard management",
                "Adaptive security settings",
                "Activity audit log"
            ],
            "visualization": "Shield-based security indicators with animation"
        },
        "hardcard": {
            "layout": "Interactive card visualization",
            "primary_elements": [
                "Card scanning interface",
                "Authentication progress",
                "Verification steps",
                "Success confirmation",
                "Physical card management"
            ],
            "visualization": "3D card rendering with scanning overlay"
        }
    }

@router.get("/get_iphone_app_plan")
def get_iphone_app_plan_endpoint() -> iPhoneAppPlan:
    """Get the iPhone App implementation plan"""
    # Create default plan
    plan = iPhoneAppPlan()
    
    # Try to load from storage if exists
    try:
        stored_plan = db.storage.json.get("iphone_app_plan")
        if stored_plan:
            return iPhoneAppPlan(**stored_plan)
    except Exception:
        # If not found or error, save the default plan
        db.storage.json.put("iphone_app_plan", plan.dict())
    
    return plan
