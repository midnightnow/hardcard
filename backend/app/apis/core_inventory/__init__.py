# Hardcard Core Inventory
# This file defines which components are considered part of the Hardcard core
# and which should be deprecated as part of the MYA-105 refactoring effort.

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Core Backend APIs
CORE_BACKEND_APIS = [
    # Identity & Lineage
    "hardcard_identity", 
    "hardcard_lineage",
    "identity",
    
    # Vault Kernel
    "hardcard_vault",
    "data_storage",  # Note: only core components should be kept
    
    # HWX Compression
    "hwx_compression",
    
    # Anchoring
    "anchoring",
    
    # Hyperspace
    "hyperspace",
    "spiral_hyperspace",
    "spiral_hyperspace_annotations",
    "spiral_transforms",
    "spiral_coordinates",
    
    # BTC Bridge
    "bitcoin_bridge",
    "bitcoin_wallet",
    "bitcoin_price",
    "bitcoin",
    
    # Supporting Core Modules
    "cryptographic_verification",
    "crypto_agility",
    "security",
    
    # System essentials
    "utils",
    "system_health",
    "error_handling",
    "client_errors",
]

# All other APIs should be considered deprecated and eventually removed

# Core Frontend Pages (these should be kept)
CORE_FRONTEND_PAGES = [
    "Hardcard",  # Any page starting with Hardcard
    "HardcardBrochure", 
    "HardcardConcept", 
    "HardcardCreator", 
    "HardcardFabricationPage", 
    "HardcardFirmwareAPI", 
    "HardcardHyperspace", 
    "HardcardKnowledgeSystem", 
    "HardcardLore", 
    "HardcardMvpDocs", 
    "HardcardRepositorySetupGuide", 
    "HardcardVisualization",
    
    # Hyperspace pages
    "Hyperspace", 
    "HyperspaceDemo", 
    "HyperspaceDemoPage",
    
    # Bitcoin/wallet pages
    "BitcoinWallet",
    "BitcoinManager",
    "BitcoinPortfolio",
    
    # Principles & foundations
    "CypherpunkPrinciples",
    
    # Auth pages
    "Login",
    "Logout",
    
    # Home page
    "App",  # Home page
]

# Core Frontend Components (these should be kept)
CORE_FRONTEND_COMPONENTS = [
    # Hardcard components
    "Hardcard",  # Base Hardcard component
    "HardcardAuthentication",
    "HardcardBrochure",
    "HardcardCrossSectionView",
    "HardcardDesignViewer",
    "HardcardDigitalTwin",
    "HardcardEventStream",
    "HardcardFirmwareDocumentation",
    "HardcardHostCommunication",
    "HardcardLandingPage",
    "HardcardLevelPurchase",
    "HardcardLore",
    "HardcardPrinter",
    "HardcardSecurity",
    "HardcardTechnicalSpecs",
    
    # Hyperspace components
    "HyperspaceViewer",
    "HyperspaceAnnotation",
    "HyperspaceAnnotationTools",
    "HyperspaceSliceManager",
    "HyperspaceTransformTools",
    "SpiralVisualization",
    
    # Core components
    "QRSeedCard",
    "CryptoVerificationAPI",
    "SelfSovereignIdentity",
    
    # Bitcoin components
    "BitcoinPriceTicker",
    "BitcoinPurchaseForm",
    "BitcoinStrategy",
    "BitcoinWalletBalance",
    "CreateWalletForm",
    "ImportWalletForm",
    "SendBitcoinForm",
    "TransactionHistory",
    
    # Supporting UI components
    "Layout",
    "GlobalNavigation",
    "Navbar",
    "SimpleNavBar",
    "ErrorBoundary",
    "ErrorDisplay",
    "ErrorFallback",
    "LoadingScreen",
    "ProgressCircle",
    "HWXVisualizer",
    "ThemeProvider",
]

# All other components should be considered deprecated and eventually removed

def is_core_api(api_name):
    """Check if the given API is part of the core."""
    # Direct match
    if api_name in CORE_BACKEND_APIS:
        return True
    
    # Check for prefixes
    for core_api in CORE_BACKEND_APIS:
        if api_name.startswith(core_api + "_"):
            return True
    
    return False

def is_core_page(page_name):
    """Check if the given page is part of the core."""
    # Direct match
    if page_name in CORE_FRONTEND_PAGES:
        return True
    
    # Check for prefixes
    for core_page in CORE_FRONTEND_PAGES:
        if page_name.startswith(core_page + "_"):
            return True
    
    return False

def is_core_component(component_name):
    """Check if the given component is part of the core."""
    # Direct match
    if component_name in CORE_FRONTEND_COMPONENTS:
        return True
    
    # Check for prefixes
    for core_component in CORE_FRONTEND_COMPONENTS:
        if component_name.startswith(core_component):
            return True
    
    return False


class CoreComponentsResponse(BaseModel):
    """Response model for core components listing"""
    core_apis: List[str]
    core_pages: List[str]
    core_components: List[str]


@router.get("/core-components")
def get_core_components() -> CoreComponentsResponse:
    """Get all core components that are part of the Hardcard system."""
    return CoreComponentsResponse(
        core_apis=CORE_BACKEND_APIS,
        core_pages=CORE_FRONTEND_PAGES,
        core_components=CORE_FRONTEND_COMPONENTS
    )


class ComponentCheckResponse(BaseModel):
    """Response model for component check"""
    name: str
    is_core: bool
    type: str


@router.get("/check/{component_type}/{component_name}")
def check_component(component_type: str, component_name: str) -> ComponentCheckResponse:
    """Check if a specific component is part of the core"""
    is_core = False
    
    if component_type == "api":
        is_core = is_core_api(component_name)
    elif component_type == "page":
        is_core = is_core_page(component_name)
    elif component_type == "component":
        is_core = is_core_component(component_name)
    
    return ComponentCheckResponse(
        name=component_name,
        is_core=is_core,
        type=component_type
    )
