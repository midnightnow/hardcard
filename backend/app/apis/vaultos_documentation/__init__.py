"""VaultOS Documentation API

This module serves as the central documentation hub for the VaultOS system architecture.
It provides structured information about the system's design, components, and organization.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()


class FolderStructure(BaseModel):
    """Model representing the VaultOS folder structure"""
    name: str
    description: str
    children: List[Dict[str, Any]] = []


@router.get("/folder-structure")
def get_folder_structure_documentation() -> Dict[str, Any]:
    """Get the VaultOS folder structure documentation"""
    return {
        "name": "vaultos",
        "description": "VaultOS system root",
        "children": [
            {
                "name": "personal",
                "description": "Personal data and documents",
                "children": [
                    {"name": "documents", "description": "Personal documents, contracts, and legal papers", "children": [
                        {"name": "legal", "description": "Legal documents and contracts"},
                        {"name": "financial", "description": "Financial records and statements"},
                        {"name": "identity", "description": "Identity documents and certificates"}
                    ]},
                    {"name": "media", "description": "Personal photos, videos, and recordings", "children": [
                        {"name": "photos", "description": "Personal photographs"},
                        {"name": "videos", "description": "Personal video recordings"},
                        {"name": "audio", "description": "Personal audio recordings"}
                    ]},
                    {"name": "health", "description": "Health records and information", "children": [
                        {"name": "medical", "description": "Medical records and reports"},
                        {"name": "insurance", "description": "Health insurance documents"}
                    ]}
                ]
            },
            {
                "name": "family",
                "description": "Family trust management",
                "children": [
                    {"name": "profiles", "description": "Family member profiles"},
                    {"name": "trust", "description": "Trust documents and records", "children": [
                        {"name": "legal", "description": "Trust legal documents"},
                        {"name": "financial", "description": "Trust financial records"}
                    ]},
                    {"name": "inheritance", "description": "Inheritance planning documents", "children": [
                        {"name": "assets", "description": "Asset distribution plans"},
                        {"name": "instructions", "description": "Personal instructions and wishes"}
                    ]},
                    {"name": "shared", "description": "Shared family documents and media"}
                ]
            },
            {
                "name": "investments",
                "description": "Investment portfolios and assets",
                "children": [
                    {"name": "bitcoin", "description": "Bitcoin investments and transactions"},
                    {"name": "stocks", "description": "Stock market investments"},
                    {"name": "real_estate", "description": "Real estate investments"},
                    {"name": "strategies", "description": "Investment strategies and models"},
                    {"name": "reports", "description": "Investment reports and analysis"}
                ]
            },
            {
                "name": "legacy",
                "description": "Legacy planning and generational wealth",
                "children": [
                    {"name": "vision", "description": "Family vision and mission statements"},
                    {"name": "education", "description": "Educational resources and plans", "children": [
                        {"name": "enlightenment", "description": "Enlightenment journey resources"},
                        {"name": "financial_literacy", "description": "Financial education materials"}
                    ]},
                    {"name": "gifts", "description": "Birthday and milestone investment gifts"},
                    {"name": "timeline", "description": "Long-term legacy planning timeline"}
                ]
            },
            {
                "name": "core",
                "description": "Core system functionality",
                "children": [
                    {"name": "auth", "description": "Authentication and authorization", "children": [
                        {"name": "keys.json", "description": "Authentication keys", "type": "json"},
                        {"name": "permissions.json", "description": "User permissions", "type": "json"}
                    ]},
                    {"name": "config", "description": "Configuration management", "children": [
                        {"name": "system.json", "description": "System configuration", "type": "json"},
                        {"name": "user.json", "description": "User preferences", "type": "json"}
                    ]},
                    {"name": "storage", "description": "Storage utilities"},
                    {"name": "utils", "description": "Common utilities"}
                ]
            },
            {
                "name": "api",
                "description": "API endpoints by domain",
                "children": [
                    {"name": "portfolios", "description": "Portfolio management APIs", "children": [
                        {"name": "bitcoin.py", "description": "Bitcoin API endpoints", "type": "code"},
                        {"name": "investments.py", "description": "Investment API endpoints", "type": "code"}
                    ]},
                    {"name": "reporting", "description": "Reporting and analytics APIs", "children": [
                        {"name": "performance.py", "description": "Performance reporting endpoints", "type": "code"},
                        {"name": "forecasts.py", "description": "Forecasting endpoints", "type": "code"}
                    ]},
                    {"name": "security", "description": "Security and compliance APIs"},
                    {"name": "content", "description": "Content management APIs"},
                    {"name": "integrations", "description": "Third-party integration APIs"}
                ]
            },
            {
                "name": "modules",
                "description": "UI modules by domain",
                "children": [
                    {"name": "portfolio", "description": "Portfolio management UI components", "children": [
                        {"name": "BitcoinWidget.tsx", "description": "Bitcoin tracking widget", "type": "code"},
                        {"name": "PortfolioChart.tsx", "description": "Portfolio visualization component", "type": "code"}
                    ]},
                    {"name": "reporting", "description": "Reporting and analytics UI components"},
                    {"name": "security", "description": "Security and compliance UI components"},
                    {"name": "content", "description": "Content management UI components"},
                    {"name": "settings", "description": "User settings UI components"}
                ]
            },
            {
                "name": "components",
                "description": "Shared UI components",
                "children": [
                    {"name": "data-display", "description": "Data visualization components"},
                    {"name": "inputs", "description": "Form input components"},
                    {"name": "feedback", "description": "User feedback components"},
                    {"name": "navigation", "description": "Navigation components"}
                ]
            },
            {
                "name": "user",
                "description": "User documents and files",
                "children": [
                    {"name": "documents", "description": "User documents", "children": [
                        {"name": "welcome.md", "description": "Welcome document", "type": "document"},
                        {"name": "getting-started.md", "description": "Getting started guide", "type": "document"}
                    ]},
                    {"name": "investments", "description": "Investment documents", "children": [
                        {"name": "bitcoin-strategy.md", "description": "Bitcoin investment strategy", "type": "document"},
                        {"name": "annual-report-2025.xlsx", "description": "Annual investment report", "type": "spreadsheet"}
                    ]},
                    {"name": "media", "description": "Media files", "children": [
                        {"name": "family-photo.jpg", "description": "Family photo", "type": "image"},
                        {"name": "birthday-message.mp3", "description": "Birthday audio message", "type": "audio"}
                    ]},
                    {"name": "legacy", "description": "Legacy planning documents"}
                ]
            }
        ]
    }


class ArchitectureOverview(BaseModel):
    """Model representing the VaultOS architecture overview"""
    title: str
    description: str
    layers: List[Dict[str, Any]]


@router.get("/architecture-overview")
def get_architecture_overview() -> ArchitectureOverview:
    """Get the VaultOS architecture overview"""
    return ArchitectureOverview(
        title="VaultOS Architecture Overview",
        description="A comprehensive view of the VaultOS system architecture",
        layers=[
            {
                "name": "Presentation Layer",
                "description": "User interface components and pages",
                "components": [
                    "React components",
                    "ShadCN UI",
                    "Zustand stores",
                    "React Router"
                ]
            },
            {
                "name": "Application Layer",
                "description": "Business logic and services",
                "components": [
                    "FastAPI controllers",
                    "Business services",
                    "Integration services",
                    "Authentication services"
                ]
            },
            {
                "name": "Data Layer",
                "description": "Data access and storage",
                "components": [
                    "Firebase/Firestore",
                    "Databutton storage",
                    "External APIs",
                    "In-memory caching"
                ]
            },
            {
                "name": "Infrastructure Layer",
                "description": "Deployment and infrastructure",
                "components": [
                    "Databutton hosting",
                    "Firebase services",
                    "API integrations",
                    "Serverless functions"
                ]
            }
        ]
    )


class ModulesOverview(BaseModel):
    """Model representing the VaultOS modules overview"""
    modules: List[Dict[str, Any]]


@router.get("/modules-features")
def get_modules_features() -> ModulesOverview:
    """Get detailed features for each VaultOS module.
    
    Provides an overview of the functionality available in each module of the VaultOS system,
    including key features and associated APIs. This helps users understand the capabilities
    of each module and how they relate to each other.
    
    Returns:
        ModulesOverview: A complete overview of all modules with their features and APIs
    """
    return ModulesOverview(
        modules=[
            {
                "id": "portfolio",
                "name": "Portfolio Management",
                "description": "Manage investment portfolios and assets",
                "features": [
                    "Portfolio creation and management",
                    "Asset allocation",
                    "Performance tracking",
                    "Investment recommendations"
                ],
                "apis": [
                    "portfolio",
                    "bitcoin_tracker",
                    "portfolio_diversification"
                ]
            },
            {
                "id": "security",
                "name": "Security & Compliance",
                "description": "Manage security settings and compliance",
                "features": [
                    "Authentication management",
                    "Access control",
                    "Audit logging",
                    "Compliance reporting"
                ],
                "apis": [
                    "security",
                    "security_api",
                    "security_adaptive_learning"
                ]
            },
            {
                "id": "content",
                "name": "Content Management",
                "description": "Manage content and documents",
                "features": [
                    "Document management",
                    "Media library",
                    "Content generation",
                    "Content sharing"
                ],
                "apis": [
                    "content_dao",
                    "family_stories",
                    "enlightenment_journey"
                ]
            },
            {
                "id": "legacy",
                "name": "Legacy Planning",
                "description": "Plan and manage legacy investments",
                "features": [
                    "Beneficiary management",
                    "Milestone planning",
                    "Legacy scoring",
                    "Trust fund management"
                ],
                "apis": [
                    "legacy_score",
                    "trust_fund_revenue",
                    "family_profiles"
                ]
            }
        ]
    )
