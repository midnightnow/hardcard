"""VaultOS Configuration API

Provides API endpoints for managing VaultOS system configuration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import databutton as db
import json
from datetime import datetime

router = APIRouter()

# Constants
CONFIG_KEY = "vaultos_config"
THEME_KEY = "vaultos_theme"


def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


class ThemeConfig(BaseModel):
    """Theme configuration model"""
    primary_color: str = "#3E63DD"
    secondary_color: str = "#10B981"
    background_color: str = "#0F172A"
    text_color: str = "#F8FAFC"
    font_heading: str = "EB Garamond"
    font_body: str = "Inter"
    font_mono: str = "JetBrains Mono"


class ModuleConfig(BaseModel):
    """Module configuration model"""
    id: str
    name: str
    description: str
    enabled: bool = True
    path: str
    icon: str
    order: int
    requires_auth: bool = True


class SystemConfig(BaseModel):
    """System configuration model"""
    version: str = "0.1.0"
    environment: str = "development"
    name: str = "VaultOS"
    description: str = "VaultOS Wealth Management Platform"
    modules: List[ModuleConfig] = []
    updated_at: Optional[str] = None


# Helper functions for config management
def get_default_config() -> SystemConfig:
    """Get the default system configuration"""
    return SystemConfig(
        version="0.1.0",
        environment="development",
        name="VaultOS",
        description="VaultOS Wealth Management Platform",
        updated_at=datetime.now().isoformat(),
        modules=[
            ModuleConfig(
                id="dashboard",
                name="Dashboard",
                description="System overview and metrics",
                path="/vaultos",
                icon="layout-dashboard",
                order=0,
            ),
            ModuleConfig(
                id="portfolio",
                name="Portfolio Management",
                description="Manage investment portfolios and assets",
                path="/portfolio",
                icon="pie-chart",
                order=1,
            ),
            ModuleConfig(
                id="security",
                name="Security & Compliance",
                description="Manage security settings and compliance",
                path="/security",
                icon="shield",
                order=2,
            ),
            ModuleConfig(
                id="content",
                name="Content Management",
                description="Manage content and documents",
                path="/content",
                icon="file-text",
                order=3,
            ),
            ModuleConfig(
                id="legacy",
                name="Legacy Planning",
                description="Plan and manage legacy investments",
                path="/legacy",
                icon="gift",
                order=4,
            ),
            ModuleConfig(
                id="settings",
                name="Settings",
                description="System settings and configuration",
                path="/settings",
                icon="settings",
                order=5,
            ),
        ]
    )


def get_default_theme() -> ThemeConfig:
    """Get the default theme configuration"""
    return ThemeConfig()


def load_config() -> SystemConfig:
    """Load the system configuration from storage"""
    try:
        config_data = db.storage.json.get(sanitize_storage_key(CONFIG_KEY), default=None)
        if not config_data:
            default_config = get_default_config()
            save_config(default_config)
            return default_config
        return SystemConfig(**config_data)
    except Exception as e:
        print(f"Error loading config: {e}")
        default_config = get_default_config()
        save_config(default_config)
        return default_config


def save_config(config: SystemConfig) -> bool:
    """Save the system configuration to storage"""
    try:
        config.updated_at = datetime.now().isoformat()
        db.storage.json.put(sanitize_storage_key(CONFIG_KEY), config.dict())
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def load_theme() -> ThemeConfig:
    """Load the theme configuration from storage"""
    try:
        theme_data = db.storage.json.get(sanitize_storage_key(THEME_KEY), default=None)
        if not theme_data:
            default_theme = get_default_theme()
            save_theme(default_theme)
            return default_theme
        return ThemeConfig(**theme_data)
    except Exception as e:
        print(f"Error loading theme: {e}")
        default_theme = get_default_theme()
        save_theme(default_theme)
        return default_theme


def save_theme(theme: ThemeConfig) -> bool:
    """Save the theme configuration to storage"""
    try:
        db.storage.json.put(sanitize_storage_key(THEME_KEY), theme.dict())
        return True
    except Exception as e:
        print(f"Error saving theme: {e}")
        return False


# API endpoints
@router.get("/config")
def get_config() -> SystemConfig:
    """Get the system configuration"""
    return load_config()


@router.put("/config")
def update_config(config: SystemConfig) -> Dict[str, Any]:
    """Update the system configuration"""
    if save_config(config):
        return {"success": True, "message": "Configuration updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update configuration")


@router.get("/theme")
def get_theme() -> ThemeConfig:
    """Get the theme configuration"""
    return load_theme()


@router.put("/theme")
def update_theme(theme: ThemeConfig) -> Dict[str, Any]:
    """Update the theme configuration"""
    if save_theme(theme):
        return {"success": True, "message": "Theme updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update theme")


@router.get("/vaultos-status")
def get_vaultos_status() -> Dict[str, Any]:
    """Get the current status of the VaultOS system"""
    config = load_config()
    return {
        "status": "operational",
        "version": config.version,
        "environment": config.environment,
        "name": config.name,
        "module_count": len(config.modules),
        "enabled_modules": [m.id for m in config.modules if m.enabled],
        "updated_at": config.updated_at,
    }
