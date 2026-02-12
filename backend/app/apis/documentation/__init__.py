from fastapi import APIRouter
from typing import Dict, List, Any
from pydantic import BaseModel
from app.auth import AuthorizedUser

# Create a router for the documentation API
router = APIRouter()

class ModuleInfo(BaseModel):
    name: str
    description: str
    endpoints: List[Dict[str, str]]

class SystemDocumentation(BaseModel):
    modules: List[ModuleInfo]
    overview: str

HARDCARD_DOCUMENTATION = """
Hardcard™ System Documentation

This module provides comprehensive documentation for the Hardcard™ system,
which offers personalized identity cards that capture a user's essence and
support their self-improvement journey.

## Core Concepts

### Hardcard Components

1. **Soul Sentence™** - A powerful statement that captures the essence of a person's unique purpose
2. **Archetype Trio** - Three archetypal energies (Primary, Secondary, Shadow) that define character
3. **Elemental Alignment** - Primary and secondary elemental energies that define temperament
4. **Mythline** - A personal narrative connecting past, present, and future
5. **Self-Improvement Goals** - Trackable development objectives across different life areas

### Hardcard Types

1. **Full Hardcard** - Complete identity profile with all core components
2. **Hardcard Light** - Simplified version generated from visual analysis
"""

@router.get("/hardcard-documentation")
def get_hardcard_documentation_docs(user: AuthorizedUser) -> Dict[str, str]:
    """Retrieve documentation for the Hardcard system"""
    return {"documentation": HARDCARD_DOCUMENTATION}

@router.get("/documentation-modules")
def get_documentation_modules(user: AuthorizedUser) -> SystemDocumentation:
    """Retrieve an overview of all system modules"""
    modules = [
        ModuleInfo(
            name="Hardcard System",
            description="Personalized identity cards with self-improvement tracking",
            endpoints=[
                {"path": "/hardcard-documentation", "method": "GET", "description": "Get Hardcard system documentation"},
                {"path": "/hardcard/{hardcard_id}", "method": "GET", "description": "Get a specific Hardcard"},
                {"path": "/hardcards", "method": "GET", "description": "List all Hardcards for user"}
            ]
        ),
        ModuleInfo(
            name="Legacy Vault",
            description="Bitcoin investment tracking for inheritance purposes",
            endpoints=[
                {"path": "/legacy-portfolio", "method": "GET", "description": "View legacy investment portfolio"},
                {"path": "/bitcoin/price", "method": "GET", "description": "Get current Bitcoin price"},
                {"path": "/bitcoin/historical-prices", "method": "GET", "description": "Get historical Bitcoin prices"}
            ]
        ),
        ModuleInfo(
            name="Family Profiles",
            description="Management of family member profiles and trusts",
            endpoints=[
                {"path": "/family-profiles/", "method": "GET", "description": "List all family profiles"},
                {"path": "/family-profiles/{profile_id}", "method": "GET", "description": "Get specific family profile"},
                {"path": "/family-stories/", "method": "GET", "description": "Get family stories"}
            ]
        )
    ]
    
    return SystemDocumentation(
        modules=modules,
        overview="Legacy Vault is a comprehensive family trust fund management platform focused on "
                 "long-term wealth preservation and growth across generations."
    )

@router.get("/architecture-documentation")
def get_architecture_documentation(user: AuthorizedUser) -> Dict[str, Any]:
    """Retrieve documentation about the system architecture"""
    return {
        "name": "Legacy Vault",
        "version": "1.0.0",
        "architecture": {
            "frontend": "React with TypeScript",
            "backend": "FastAPI with Python",
            "storage": "Databutton storage and Firebase",
            "authentication": "Firebase Authentication"
        },
        "core_systems": [
            {
                "name": "Legacy Investment Tracking",
                "description": "Monitors Bitcoin investments for children's trust funds"
            },
            {
                "name": "Family Trust Management",
                "description": "Manages family member profiles and investment allocations"
            },
            {
                "name": "Hardcard Personal Development",
                "description": "Tracks personal growth objectives tied to identity profiles"
            }
        ]
    }
    