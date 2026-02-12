"""VaultOS Architecture API

Defines the comprehensive architecture for the VaultOS system, including
the distributed Family Vault structure with hybrid storage, modular frontends,
and secure data management.

This module provides:
1. Complete folder structure definition
2. Configuration templates for each component
3. Guidelines for distributed development
4. Component interaction specifications
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter()

class ComponentTemplate(BaseModel):
    """Template for configuration of a system component"""
    name: str
    description: str
    config_schema: Dict[str, Any]
    default_config: Dict[str, Any]

class FolderComponent(BaseModel):
    """Component in the VaultOS folder structure"""
    id: str
    name: str
    description: str
    path: str
    parent: Optional[str] = None
    children: List[str] = []
    files: List[str] = []
    readme: Optional[str] = None
    config_template: Optional[ComponentTemplate] = None

class VaultOSArchitecture(BaseModel):
    """Complete VaultOS architecture definition"""
    components: Dict[str, FolderComponent]
    root_component: str

@router.get("/vaultos-architecture")
def get_vaultos_architecture() -> VaultOSArchitecture:
    """Get the complete VaultOS architecture definition"""
    # Define the comprehensive architecture
    architecture = VaultOSArchitecture(
        root_component="root",
        components={
            # Root level
            "root": FolderComponent(
                id="root",
                name="VaultOS",
                description="Root directory for the VaultOS system",
                path="/",
                children=["core", "storage", "security", "frontend", "api_gateway", "auth", "audit", "config"],
                readme="# VaultOS\n\nDistributed Family Trust Vault System\n\n## Overview\n\nVaultOS is a comprehensive system for managing family trust assets, documents, and digital legacy, with a focus on long-term inheritance planning. The system is built with a modular architecture that separates concerns between storage, security, frontend interfaces, and backend services."
            ),
            # Core system components
            "core": FolderComponent(
                id="core",
                name="Core",
                description="Core system services and components",
                path="/core",
                parent="root",
                children=["orchestration", "scheduler", "events", "registry"],
                readme="# VaultOS Core\n\nCore system services and components for VaultOS.\n\n## Components\n\n- Orchestration: Manages the lifecycle of system components\n- Scheduler: Handles scheduled tasks and periodic operations\n- Events: Provides an event bus for system-wide communication\n- Registry: Central registry of all system components and services"
            ),
            "orchestration": FolderComponent(
                id="orchestration",
                name="Orchestration",
                description="Component lifecycle management",
                path="/core/orchestration",
                parent="core",
                readme="# Orchestration\n\nManages the lifecycle of system components, including initialization, startup, shutdown, and updates.\n\n## Responsibilities\n\n- Component dependency resolution\n- Initialization order management\n- Health monitoring\n- Graceful shutdown coordination"
            ),
            "scheduler": FolderComponent(
                id="scheduler",
                name="Scheduler",
                description="Task scheduling and execution",
                path="/core/scheduler",
                parent="core",
                readme="# Scheduler\n\nHandles scheduled tasks and periodic operations.\n\n## Responsibilities\n\n- Timed task execution\n- Recurring job management\n- Task prioritization\n- Execution history tracking"
            ),
            "events": FolderComponent(
                id="events",
                name="Events",
                description="Event bus and messaging system",
                path="/core/events",
                parent="core",
                readme="# Events\n\nProvides an event bus for system-wide communication.\n\n## Responsibilities\n\n- Event publication and subscription\n- Event routing\n- Event persistence\n- Event replay and recovery"
            ),
            "registry": FolderComponent(
                id="registry",
                name="Registry",
                description="Component and service registry",
                path="/core/registry",
                parent="core",
                readme="# Registry\n\nCentral registry of all system components and services.\n\n## Responsibilities\n\n- Service discovery\n- Component metadata management\n- Version tracking\n- Health status aggregation"
            ),
            # Storage system
            "storage": FolderComponent(
                id="storage",
                name="Storage",
                description="Hybrid storage management for vault data",
                path="/storage",
                parent="root",
                children=["encrypted_vault", "document_store", "asset_storage", "metadata_db", "sync"],
                readme="# Storage System\n\nHybrid storage management for Family Vault data.\n\n## Components\n\n- Encrypted Vault: End-to-end encrypted storage for sensitive data\n- Document Store: Structured storage for family documents\n- Asset Storage: Binary asset storage for multimedia content\n- Metadata DB: Metadata and indexing service\n- Sync: Data synchronization between local and cloud storage"
            ),
            "encrypted_vault": FolderComponent(
                id="encrypted_vault",
                name="Encrypted Vault",
                description="End-to-end encrypted storage",
                path="/storage/encrypted_vault",
                parent="storage",
                config_template=ComponentTemplate(
                    name="Encrypted Vault Configuration",
                    description="Configuration for the encrypted vault storage",
                    config_schema={
                        "encryption_algorithm": {"type": "string"},
                        "key_length": {"type": "integer"},
                        "rotation_period_days": {"type": "integer"}
                    },
                    default_config={
                        "encryption_algorithm": "AES-256-GCM",
                        "key_length": 256,
                        "rotation_period_days": 90
                    }
                ),
                readme="# Encrypted Vault\n\nEnd-to-end encrypted storage for sensitive family data.\n\n## Security Features\n\n- Client-side encryption\n- Zero-knowledge architecture\n- Key rotation and recovery protocols\n- Quantum-resistant encryption options"
            ),
            "document_store": FolderComponent(
                id="document_store",
                name="Document Store",
                description="Structured document storage",
                path="/storage/document_store",
                parent="storage",
                readme="# Document Store\n\nStructured storage for family documents and records.\n\n## Features\n\n- Version control and history\n- Document classification\n- Full-text search\n- Automated metadata extraction"
            ),
            "asset_storage": FolderComponent(
                id="asset_storage",
                name="Asset Storage",
                description="Binary asset storage",
                path="/storage/asset_storage",
                parent="storage",
                readme="# Asset Storage\n\nBinary asset storage for multimedia content.\n\n## Features\n\n- Large file handling\n- Content-aware compression\n- Multimedia previews\n- Auto-tagging and classification"
            ),
            "metadata_db": FolderComponent(
                id="metadata_db",
                name="Metadata DB",
                description="Metadata and indexing service",
                path="/storage/metadata_db",
                parent="storage",
                readme="# Metadata DB\n\nMetadata and indexing service for vault content.\n\n## Features\n\n- Fast retrieval optimizations\n- Relationship tracking\n- Graph-based data modeling\n- Timeline-oriented views"
            ),
            "sync": FolderComponent(
                id="sync",
                name="Sync",
                description="Data synchronization service",
                path="/storage/sync",
                parent="storage",
                readme="# Sync Service\n\nData synchronization between local and cloud storage.\n\n## Features\n\n- Differential sync\n- Conflict resolution\n- Bandwidth optimization\n- Offline capabilities"
            )
        }
    )
    
    return architecture

@router.get("/folder-architecture")
def get_folder_architecture() -> Dict[str, Any]:
    """Get a simplified view of the folder architecture"""
    architecture = get_vaultos_architecture()
    
    # Convert to a tree structure
    tree = {}
    
    # First pass - create all nodes
    for component_id, component in architecture.components.items():
        tree[component_id] = {
            "id": component_id,
            "name": component.name,
            "description": component.description,
            "path": component.path,
            "children": []
        }
    
    # Second pass - connect children
    for component_id, component in architecture.components.items():
        if component.parent and component.parent in tree:
            tree[component.parent]["children"].append(component_id)
    
    return tree[architecture.root_component]

@router.get("/architecture-components/{component_id}")
def get_architecture_component(component_id: str) -> FolderComponent:
    """Get details for a specific architecture component"""
    architecture = get_vaultos_architecture()
    
    if component_id not in architecture.components:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    return architecture.components[component_id]

@router.get("/architecture-readme/{component_id}")
def get_architecture_readme(component_id: str) -> Dict[str, str]:
    """Get the README for a specific architecture component"""
    architecture = get_vaultos_architecture()
    
    if component_id not in architecture.components:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    component = architecture.components[component_id]
    
    if not component.readme:
        return {"readme": f"No README available for {component.name}"}
    
    return {"readme": component.readme}

@router.get("/config-template/{component_id}")
def get_config_template(component_id: str) -> Dict[str, Any]:
    """Get the configuration template for a specific component"""
    architecture = get_vaultos_architecture()
    
    if component_id not in architecture.components:
        raise HTTPException(status_code=404, detail=f"Component {component_id} not found")
    
    component = architecture.components[component_id]
    
    if not component.config_template:
        return {
            "name": f"{component.name} Configuration",
            "description": f"Configuration for {component.name}",
            "message": "No specific configuration template available for this component",
            "config_schema": {},
            "default_config": {}
        }
    
    return {
        "name": component.config_template.name,
        "description": component.config_template.description,
        "config_schema": component.config_template.config_schema,
        "default_config": component.config_template.default_config
    }

@router.get("/development-guidelines")
def get_development_guidelines() -> Dict[str, Any]:
    """Get development guidelines for working with the VaultOS architecture"""
    return {
        "title": "VaultOS Development Guidelines",
        "summary": "Guidelines for developing within the VaultOS architecture",
        "sections": [
            {
                "title": "Component Development",
                "content": "When developing a new component for VaultOS, follow these practices:\n\n1. One component per folder\n2. Create a README.md in each component folder\n3. Follow the configuration template pattern\n4. Include unit tests for all code\n5. Document all public interfaces"
            },
            {
                "title": "Security Considerations",
                "content": "All VaultOS components must adhere to these security principles:\n\n1. Encrypt all sensitive data at rest and in transit\n2. Validate all inputs, even from trusted sources\n3. Implement proper access controls for all operations\n4. Log security events for audit purposes\n5. Follow the principle of least privilege"
            },
            {
                "title": "Integration Guidelines",
                "content": "When integrating components:\n\n1. Use the API Gateway for all service-to-service communication\n2. Follow the event-driven architecture pattern for asynchronous operations\n3. Implement circuit breakers for external dependencies\n4. Version all APIs\n5. Include comprehensive error handling and fallbacks"
            },
            {
                "title": "Storage Guidelines",
                "content": "When working with the storage system:\n\n1. Use the appropriate storage type for each data category\n2. Include metadata for all stored objects\n3. Implement proper backup and recovery mechanisms\n4. Structure data for efficient retrieval\n5. Follow data retention policies"
            }
        ]
    }
