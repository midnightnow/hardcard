from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

README_CONTENT = """
# VaultOS Core

VaultOS Core is the central backbone of the Legacy Vault system. It provides the fundamental services, architecture, and interfaces that power the entire VaultOS ecosystem.

## Overview

VaultOS is designed as a modular, extensible system for managing generational wealth and legacy planning. The Core module serves as the foundation upon which all other modules and services are built.

## Architecture

The VaultOS architecture follows these key principles:

1. **Modular Design**: Each capability is encapsulated in self-contained modules
2. **Layered Architecture**: Clear separation between storage, business logic, and presentation
3. **Secure by Default**: End-to-end encryption and granular access controls
4. **Future-Proof**: Designed to evolve with changing technology and needs
5. **User-Centric**: All design decisions prioritize user experience and control

## Directory Structure

The VaultOS structure is organized as follows:

```
vaultos_core/         # Core system services and interfaces
vaultos_config/       # Configuration management
vaultos_files/        # File system and storage management
vaultos_folder_structure/ # Folder hierarchy and organization
vaultos_documentation/ # System documentation
vaultos_connector/    # External system integrations
vaultos_launcher/     # System bootstrap and initialization
privacy_vault/        # Secure encrypted storage subsystem
```

## Module System

VaultOS uses a plugin-based architecture where modules can be enabled or disabled based on user needs. Each module provides specific functionality while adhering to the core system interfaces.

## Configuration

System configuration is managed through the vaultos_config API, which provides a consistent interface for reading and writing configuration values.

## Security Model

VaultOS implements a comprehensive security model with multiple layers of protection:

1. Authentication via Firebase Auth
2. Role-based access control
3. End-to-end encryption for sensitive data
4. Audit logging for all system changes
5. Secure key management through the privacy vault

## Development Guidelines

When extending VaultOS, follow these guidelines:

1. Maintain separation of concerns
2. Document all APIs and interfaces
3. Include comprehensive error handling
4. Write unit tests for all business logic
5. Follow the established naming conventions
6. Update this documentation when adding new core components
"""


class ReadmeResponse(BaseModel):
    content: str


@router.get("/vaultos-readme")
def get_vaultos_readme() -> ReadmeResponse:
    """Get the VaultOS Core readme document."""
    return ReadmeResponse(content=README_CONTENT)
