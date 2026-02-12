"""VaultOS Core API Module

Provides foundational APIs for the VaultOS system, including configuration,
system status, and environment management.

The VaultOS architecture follows these key principles:

1. Modular Design: Each capability is encapsulated in self-contained modules
2. Layered Architecture: Clear separation between storage, business logic, and presentation
3. Secure by Default: End-to-end encryption and granular access controls
4. Future-Proof: Designed to evolve with changing technology and needs
5. User-Centric: All design decisions prioritize user experience and control

VaultOS Module Structure:
- vaultos_core: Core system services and interfaces
- vaultos_config: Configuration management
- vaultos_files: File system and storage management
- vaultos_folder_structure: Folder hierarchy and organization
- vaultos_documentation: System documentation
- vaultos_connector: External system integrations
- vaultos_launcher: System bootstrap and initialization
- privacy_vault: Secure encrypted storage subsystem
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import databutton as db
import json
from datetime import datetime

router = APIRouter()

# Constants
SYSTEM_VERSION = "1.0.0"
SYSTEM_NAME = "Legacy Vault"
SYSTEM_STATUS_KEY = "vaultos_system_status"


def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


class VaultOSModule(BaseModel):
    """Base model for VaultOS module information"""
    id: str
    name: str
    description: str
    version: str
    status: str = "active"  # active, inactive, deprecated
    dependencies: List[str] = []


class SystemStatus(BaseModel):
    """System status information"""
    version: str = SYSTEM_VERSION
    name: str = SYSTEM_NAME
    status: str = "operational"  # operational, degraded, maintenance, offline
    last_start: Optional[str] = None
    uptime: Optional[int] = None
    active_modules: List[str] = []
    environment: str = "production"


def get_modules_list() -> List[VaultOSModule]:
    """Get the list of all registered VaultOS modules"""
    # This would typically be dynamically discovered, but for simplicity we'll hardcode
    return [
        VaultOSModule(
            id="vaultos_core",
            name="VaultOS Core",
            description="Core system services and interfaces",
            version="1.0.0",
            dependencies=[]
        ),
        VaultOSModule(
            id="vaultos_config",
            name="VaultOS Configuration",
            description="Configuration management system",
            version="1.0.0",
            dependencies=["vaultos_core"]
        ),
        VaultOSModule(
            id="vaultos_files",
            name="VaultOS Files",
            description="File system and storage management",
            version="1.0.0",
            dependencies=["vaultos_core", "vaultos_config"]
        ),
        VaultOSModule(
            id="vaultos_folder_structure",
            name="VaultOS Folder Structure",
            description="Folder hierarchy and organization",
            version="1.0.0",
            dependencies=["vaultos_core", "vaultos_files"]
        ),
        VaultOSModule(
            id="privacy_vault",
            name="Privacy Vault",
            description="Secure encrypted storage subsystem",
            version="1.0.0",
            dependencies=["vaultos_core", "vaultos_files"]
        ),
        VaultOSModule(
            id="vaultos_documentation",
            name="VaultOS Documentation",
            description="System documentation and guides",
            version="1.0.0",
            dependencies=["vaultos_core"]
        )
    ]


def get_system_status() -> SystemStatus:
    """Get the current system status"""
    try:
        status_data = db.storage.json.get(sanitize_storage_key(SYSTEM_STATUS_KEY), default=None)
        if not status_data:
            status = SystemStatus(
                last_start=datetime.now().isoformat(),
                active_modules=[module.id for module in get_modules_list()]
            )
            save_system_status(status)
            return status
        return SystemStatus(**status_data)
    except Exception as e:
        print(f"Error getting system status: {e}")
        # Return default if there's an error
        return SystemStatus(
            last_start=datetime.now().isoformat(),
            active_modules=[module.id for module in get_modules_list()]
        )


def save_system_status(status: SystemStatus) -> bool:
    """Save the current system status"""
    try:
        db.storage.json.put(sanitize_storage_key(SYSTEM_STATUS_KEY), status.dict())
        return True
    except Exception as e:
        print(f"Error saving system status: {e}")
        return False


@router.get("/core-status")
def get_core_status() -> Dict[str, Any]:
    """Get the current operational status of the VaultOS core system.
    
    Provides essential system information including operational status,
    version, uptime, and active modules. This endpoint is used for system
    monitoring and health checks.
    
    Returns:
        Dict[str, Any]: Comprehensive system status information including:
            - status: Current operational state (operational, degraded, etc.)
            - version: System version number
            - name: System name
            - last_start: Timestamp of last system start
            - modules: Information about system modules
    """
    status = get_system_status()
    modules = get_modules_list()
    
    return {
        "status": status.status,
        "version": status.version,
        "name": status.name,
        "last_start": status.last_start,
        "environment": status.environment,
        "modules": {
            "total": len(modules),
            "active": len(status.active_modules),
            "list": [m.dict() for m in modules]
        }
    }


@router.get("/modules-overview")
def get_modules_overview() -> Dict[str, Any]:
    """Get an overview of all VaultOS modules with their status and dependencies.
    
    Provides a complete list of all modules in the VaultOS system along with their
    status (active/inactive), version information, and dependency relationships.
    This endpoint is essential for system monitoring and troubleshooting.
    
    Returns:
        Dict[str, Any]: Overview of all modules including status and dependencies
    """
    modules = get_modules_list()
    status = get_system_status()
    
    return {
        "total_modules": len(modules),
        "active_modules": len(status.active_modules),
        "modules": [{
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "version": m.version,
            "status": "active" if m.id in status.active_modules else "inactive",
            "dependencies": m.dependencies
        } for m in modules]
    }
