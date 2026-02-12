"""VaultOS Folder Structure API

Provides endpoints for retrieving and managing the logical folder structure
for the VaultOS system. The folder structure serves as the organizational
framework for the distributed family vault.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()

class FileNode(BaseModel):
    name: str
    description: str
    type: str
    size: Optional[int] = None
    modified: Optional[str] = None
    created: Optional[str] = None

class FolderNode(BaseModel):
    name: str
    description: str
    children: Optional[List['FolderNode']] = []
    files: Optional[List[FileNode]] = []

@router.get("/get-folder-structure")
def get_folder_structure() -> FolderNode:
    """Retrieve the logical folder structure for VaultOS.
    
    This endpoint provides a recommended organizational hierarchy for user data
    in the Legacy Vault system. The structure includes predefined folders and
    sample files that demonstrate the intended organization of different
    types of family and financial data.
    
    Returns:
        FolderNode: A hierarchical tree structure representing the recommended
            folder organization, including folder descriptions and sample files
    """
    # Define the base folder structure for the VaultOS system
    folder_structure = FolderNode(
        name="Legacy Vault",
        description="Root folder for all your legacy data",
        children=[
            FolderNode(
                name="Family Documents",
                description="Essential family documentation and records",
                children=[
                    FolderNode(
                        name="Legal Documents",
                        description="Wills, trusts, and legal agreements",
                        files=[
                            FileNode(
                                name="Family Trust Agreement.pdf", 
                                description="Master trust document",
                                type="pdf"
                            ),
                            FileNode(
                                name="Will Template.docx", 
                                description="Template for creating wills",
                                type="document"
                            )
                        ]
                    ),
                    FolderNode(
                        name="Identity Documents",
                        description="Birth certificates, passports, and identification"
                    ),
                    FolderNode(
                        name="Educational Records",
                        description="Academic achievements and certifications"
                    )
                ]
            ),
            FolderNode(
                name="Financial Assets",
                description="Investment and financial records",
                children=[
                    FolderNode(
                        name="Bitcoin Investments",
                        description="Bitcoin purchase records and certificates",
                        files=[
                            FileNode(
                                name="Annual Bitcoin Statement.pdf", 
                                description="Summary of annual Bitcoin investments",
                                type="pdf"
                            )
                        ]
                    ),
                    FolderNode(
                        name="Traditional Investments",
                        description="Stocks, bonds, and traditional investment vehicles"
                    ),
                    FolderNode(
                        name="Real Estate",
                        description="Property deeds and related documentation"
                    ),
                    FolderNode(
                        name="Tax Documents",
                        description="Tax returns and related financial records"
                    )
                ]
            ),
            FolderNode(
                name="Inheritance Planning",
                description="Long-term inheritance and legacy planning",
                children=[
                    FolderNode(
                        name="Succession Plans",
                        description="Instructions for asset transfer and succession"
                    ),
                    FolderNode(
                        name="Letters to Heirs",
                        description="Personal messages to future generations"
                    ),
                    FolderNode(
                        name="Key Events",
                        description="Timeline of important life milestones",
                        files=[
                            FileNode(
                                name="18th Birthday Instructions.pdf", 
                                description="Instructions for 18th birthday Bitcoin delivery",
                                type="pdf"
                            )
                        ]
                    )
                ]
            ),
            FolderNode(
                name="Digital Legacy",
                description="Digital assets and online presence management",
                children=[
                    FolderNode(
                        name="Online Accounts",
                        description="Inventory of online accounts and access information"
                    ),
                    FolderNode(
                        name="Digital Assets",
                        description="Cryptocurrency, NFTs, and other digital property"
                    ),
                    FolderNode(
                        name="Content Archive",
                        description="Personal digital content with lasting value"
                    )
                ]
            ),
            FolderNode(
                name="Family History",
                description="Family stories, photos, and historical records",
                children=[
                    FolderNode(
                        name="Photos",
                        description="Family photo collections"
                    ),
                    FolderNode(
                        name="Stories",
                        description="Written and recorded family narratives"
                    ),
                    FolderNode(
                        name="Genealogy",
                        description="Family tree and ancestry information"
                    )
                ]
            ),
            FolderNode(
                name="Privacy Vault",
                description="End-to-end encrypted secure storage for sensitive documents",
                children=[
                    FolderNode(
                        name="Private Keys",
                        description="Cryptocurrency and encryption key backups"
                    ),
                    FolderNode(
                        name="Passwords",
                        description="Password recovery information"
                    )
                ]
            ),
            FolderNode(
                name="System",
                description="VaultOS system files and configuration",
                children=[
                    FolderNode(
                        name="Logs",
                        description="System logs and access records"
                    ),
                    FolderNode(
                        name="Backups",
                        description="System backups and recovery points"
                    ),
                    FolderNode(
                        name="Configuration",
                        description="System settings and configuration files"
                    )
                ]
            )
        ]
    )
    
    return folder_structure

@router.get("/file-system-architecture")
def get_file_system_architecture() -> dict:
    """Retrieve the VaultOS file system architecture overview.
    
    Provides a high-level description of the design principles and components
    of the VaultOS file system. This endpoint documents the architectural
    concepts that guide the folder structure design and implementation.
    
    Returns:
        dict: A structured description of the file system architecture, including
            design principles and key components
    """
    architecture = {
        "name": "VaultOS File System Architecture",
        "description": "The structural design of the VaultOS hierarchical file system",
        "principles": [
            {
                "name": "Hierarchical Organization",
                "description": "Data organized in a logical tree structure from general to specific"
            },
            {
                "name": "Separation of Concerns",
                "description": "Different data types segregated into appropriate categories"
            },
            {
                "name": "Future-Proof Structure",
                "description": "Categories designed to remain relevant across technological changes"
            },
            {
                "name": "Access Control Integration",
                "description": "Structure supports granular permission controls"
            },
            {
                "name": "Versioning Support",
                "description": "Built-in support for file versioning and history tracking"
            }
        ],
        "components": [
            {
                "name": "Root Structure",
                "description": "Top-level organization of the entire vault"
            },
            {
                "name": "Category System",
                "description": "Logical grouping of related data types"
            },
            {
                "name": "Metadata Framework",
                "description": "Rich descriptive data attached to files and folders"
            },
            {
                "name": "Encryption Layer",
                "description": "Selective end-to-end encryption for sensitive content"
            },
            {
                "name": "Access Control Mechanism",
                "description": "Permission system for controlling data access"
            }
        ]
    }
    
    return architecture

@router.get("/get-folder-tree2")
def get_folder_tree_view() -> dict:
    """Retrieve a simplified tree representation of the folder structure.
    
    Provides a lightweight hierarchical view of the VaultOS folder structure,
    optimized for navigation components like sidebars, breadcrumbs, and folder trees.
    This is more efficient than the full folder structure when only basic
    navigation information is needed.
    
    Returns:
        dict: A tree structure with folder IDs and names suitable for UI navigation
    """
    tree = {
        "id": "root",
        "name": "Legacy Vault",
        "children": [
            {
                "id": "family-documents",
                "name": "Family Documents",
                "children": [
                    {"id": "legal-documents", "name": "Legal Documents"},
                    {"id": "identity-documents", "name": "Identity Documents"},
                    {"id": "educational-records", "name": "Educational Records"}
                ]
            },
            {
                "id": "financial-assets",
                "name": "Financial Assets",
                "children": [
                    {"id": "bitcoin-investments", "name": "Bitcoin Investments"},
                    {"id": "traditional-investments", "name": "Traditional Investments"},
                    {"id": "real-estate", "name": "Real Estate"},
                    {"id": "tax-documents", "name": "Tax Documents"}
                ]
            },
            {
                "id": "inheritance-planning",
                "name": "Inheritance Planning",
                "children": [
                    {"id": "succession-plans", "name": "Succession Plans"},
                    {"id": "letters-to-heirs", "name": "Letters to Heirs"},
                    {"id": "key-events", "name": "Key Events"}
                ]
            },
            {
                "id": "digital-legacy",
                "name": "Digital Legacy",
                "children": [
                    {"id": "online-accounts", "name": "Online Accounts"},
                    {"id": "digital-assets", "name": "Digital Assets"},
                    {"id": "content-archive", "name": "Content Archive"}
                ]
            },
            {
                "id": "family-history",
                "name": "Family History",
                "children": [
                    {"id": "photos", "name": "Photos"},
                    {"id": "stories", "name": "Stories"},
                    {"id": "genealogy", "name": "Genealogy"}
                ]
            },
            {
                "id": "privacy-vault",
                "name": "Privacy Vault",
                "children": [
                    {"id": "private-keys", "name": "Private Keys"},
                    {"id": "passwords", "name": "Passwords"}
                ]
            },
            {
                "id": "system",
                "name": "System",
                "children": [
                    {"id": "logs", "name": "Logs"},
                    {"id": "backups", "name": "Backups"},
                    {"id": "configuration", "name": "Configuration"}
                ]
            }
        ]
    }
    
    return tree