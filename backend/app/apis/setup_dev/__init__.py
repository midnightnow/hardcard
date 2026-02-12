"""VaultOS Development Environment Setup API

This API provides endpoints to initialize and manage the VaultOS development environment,
including directory structure validation, configuration management, and environment setup.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import databutton as db
import re
import os
import json
from typing import Dict, List, Any, Optional

router = APIRouter()

# Constants
VAULTOS_VERSION = "0.1.0"

# Core VaultOS configuration
VAULTOS_CONFIG = {
    "version": VAULTOS_VERSION,
    "name": "Legacy Vault",
    "theme": "sophisticated-future",
    "modules": [
        "core",
        "bitcoin",
        "investments",
        "family-profiles",
        "security"
    ],
    "features": {
        "hardcard": True,
        "enlightenment-journey": True,
        "content-dao": True,
        "tax-management": True
    }
}

# Default theme configuration
DEFAULT_THEME = {
    "name": "sophisticated-future",
    "colors": {
        "primary": "#1E3A8A",  # Deep blue
        "secondary": "#6B7280",  # Subtle gray
        "accent": "#FBBF24",  # Gold accent
        "background": {
            "primary": "#0F172A",  # Deep navy
            "secondary": "#1E293B"  # Lighter navy
        },
        "text": {
            "primary": "#F8FAFC",  # Almost white
            "secondary": "#CBD5E1",  # Light gray
            "muted": "#94A3B8"  # Muted blue gray
        },
        "success": "#10B981",  # Emerald green
        "warning": "#F59E0B",  # Amber
        "error": "#EF4444",  # Red
        "info": "#3B82F6"  # Blue
    },
    "typography": {
        "heading": {
            "family": "Playfair Display, serif",  # Distinguished serif
            "weight": 600
        },
        "body": {
            "family": "Inter, sans-serif",  # Clean, legible sans-serif
            "weight": 400
        },
        "monospace": {
            "family": "JetBrains Mono, monospace",  # Modern monospace for financial data
            "weight": 400
        }
    },
    "spacing": {
        "base": 4,
        "scale": [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96]
    },
    "borderRadius": {
        "small": "0.125rem",
        "medium": "0.25rem",
        "large": "0.5rem",
        "full": "9999px"
    },
    "shadows": {
        "small": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "medium": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "large": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    },
    "animations": {
        "fast": "150ms",
        "normal": "300ms",
        "slow": "500ms"
    }
}

# Models
class SetupRequest(BaseModel):
    """Request model for setup initiation"""
    force_reset: bool = False
    setup_directories: bool = True
    setup_config: bool = True
    setup_theme: bool = True

class SetupResponse(BaseModel):
    """Response model for setup operations"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

class ConfigUpdateRequest(BaseModel):
    """Request model for updating VaultOS configuration"""
    config: Dict[str, Any]

class ThemeUpdateRequest(BaseModel):
    """Request model for updating VaultOS theme"""
    theme: Dict[str, Any]
    theme_name: str

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

@router.post("/setup")
def setup_environment(request: SetupRequest) -> SetupResponse:
    """Initialize the VaultOS development environment"""
    results = {}
    
    try:
        # Set up configuration
        if request.setup_config:
            config_key = sanitize_storage_key("vaultos_config")
            
            # Check if config already exists
            try:
                existing_config = db.storage.json.get(config_key)
                if request.force_reset or not existing_config:
                    db.storage.json.put(config_key, VAULTOS_CONFIG)
                    results["config"] = "Created new configuration"
                else:
                    results["config"] = "Configuration already exists"
            except Exception:
                db.storage.json.put(config_key, VAULTOS_CONFIG)
                results["config"] = "Created new configuration"
        
        # Set up theme
        if request.setup_theme:
            theme_key = sanitize_storage_key("vaultos_theme_sophisticated-future")
            
            # Check if theme already exists
            try:
                existing_theme = db.storage.json.get(theme_key)
                if request.force_reset or not existing_theme:
                    db.storage.json.put(theme_key, DEFAULT_THEME)
                    results["theme"] = "Created default theme"
                else:
                    results["theme"] = "Theme already exists"
            except Exception:
                db.storage.json.put(theme_key, DEFAULT_THEME)
                results["theme"] = "Created default theme"
        
        return SetupResponse(
            success=True,
            message="VaultOS development environment setup completed successfully",
            details=results
        )
    
    except Exception as e:
        return SetupResponse(
            success=False,
            message=f"Setup failed: {str(e)}",
            details=results
        )

@router.get("/setup-config")
def get_setup_config() -> Dict[str, Any]:
    """Get the current VaultOS setup configuration"""
    try:
        config_key = sanitize_storage_key("vaultos_config")
        config = db.storage.json.get(config_key)
        return config
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Configuration not found: {str(e)}") from e

@router.post("/setup-config")
def update_dev_config(request: ConfigUpdateRequest) -> SetupResponse:
    """Update the VaultOS setup configuration"""
    try:
        config_key = sanitize_storage_key("vaultos_config")
        db.storage.json.put(config_key, request.config)
        return SetupResponse(
            success=True,
            message="Configuration updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}") from e

@router.get("/theme/{theme_name}")
def get_setup_theme_by_name(theme_name: str) -> Dict[str, Any]:
    """Get a specific theme by name"""
    try:
        theme_key = sanitize_storage_key(f"vaultos_theme_{theme_name}")
        theme = db.storage.json.get(theme_key)
        return theme
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Theme not found: {str(e)}") from e

@router.post("/setup-theme")
def update_setup_theme(request: ThemeUpdateRequest) -> SetupResponse:
    """Update or create a development theme"""
    try:
        theme_key = sanitize_storage_key(f"vaultos_theme_{request.theme_name}")
        db.storage.json.put(theme_key, request.theme)
        return SetupResponse(
            success=True,
            message=f"Theme '{request.theme_name}' updated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update theme: {str(e)}") from e

@router.get("/setup-status")
def get_setup_status() -> Dict[str, Any]:
    """Get the current status of the VaultOS development environment"""
    status = {
        "version": VAULTOS_VERSION,
        "config_exists": False,
        "themes": [],
    }
    
    # Check config
    try:
        config_key = sanitize_storage_key("vaultos_config")
        config = db.storage.json.get(config_key)
        status["config_exists"] = True
        status["config"] = config
    except Exception:
        pass
    
    # Find themes
    themes = []
    for file in db.storage.json.list():
        if file.name.startswith("vaultos_theme_"):
            theme_name = file.name.replace("vaultos_theme_", "")
            themes.append(theme_name)
    
    status["themes"] = themes
    
    return status
