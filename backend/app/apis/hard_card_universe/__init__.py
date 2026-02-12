from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class CorePrinciple(BaseModel):
    title: str
    description: str

class ManifestoResponse(BaseModel):
    vision: str
    core_principles: List[CorePrinciple]
    why_hardcard: str
    mission_statement: str

class Component(BaseModel):
    id: str
    name: str
    type: str
    description: str
    status: str
    parent: Optional[str] = None
    technical_stack: Optional[Dict[str, List[str]]] = None

class Connection(BaseModel):
    source: str
    target: str
    type: str
    description: str

class ArchitectureResponse(BaseModel):
    title: str
    description: str
    components: List[Component]
    connections: List[Connection]
    governance_model: Dict[str, Any]
    api_standards: Dict[str, str]

class Module(BaseModel):
    id: str
    name: str
    description: str
    status: str
    connections: List[Dict[str, str]]
    metadata: Dict[str, Any]

class ModulesResponse(BaseModel):
    modules: List[Module]

@router.get("/hcu-manifesto")
def get_hard_card_universe_manifesto() -> ManifestoResponse:
    """Returns the Hard Card Universe manifesto and vision statement.
    
    This endpoint provides the central philosophy, core principles, and mission
    statement for the Hard Card Universe ecosystem.
    """
    
    manifesto_data = {
        "vision": "The Hard Card Universe (HCU) exists to create an integrated ecosystem that preserves and enhances both financial wealth and intellectual wisdom across generations. By connecting distinct but harmonized modules through a coherent central architecture, HCU provides a framework for legacy-building that combines cutting-edge technology with time-tested principles of stewardship and growth.",
        
        "core_principles": [
            {
                "title": "Coherence Over Noise",
                "description": "In a world overwhelmed by fleeting information, HCU prioritizes coherent, interconnected knowledge systems that build upon themselves rather than fragmentary content that quickly becomes obsolete. Each project within the HCU ecosystem must contribute to this coherence rather than create more noise."
            },
            {
                "title": "Multi-Generational Perspective",
                "description": "HCU rejects short-termism in favor of planning and building across generational timelines. Investment strategies, knowledge acquisition, and platform development all operate on expanded time horizons that consider impact beyond immediate returns."
            },
            {
                "title": "Integrated Wisdom & Wealth",
                "description": "Financial assets and knowledge assets are treated as complementary and interconnected forms of wealth. HCU acknowledges that sustainable financial growth requires wisdom, while wisdom acquisition benefits from financial stability."
            },
            {
                "title": "Systematic Legacy-Building",
                "description": "Legacy creation is approached as a systematic, architectural process rather than an afterthought. HCU provides frameworks, tools, and methodologies for intentional legacy design rather than accidental legacy discovery."
            },
            {
                "title": "Harmonized Independence",
                "description": "Each module within the HCU ecosystem maintains operational independence while adhering to shared principles and integration standards. This balance allows for specialized excellence while preserving overall coherence and interoperability."
            },
            {
                "title": "Meta-Narrative Awareness",
                "description": "HCU embraces self-awareness about its own development and narrative. This meta-level perspective allows for continuous evolution, prevents dogmatic thinking, and encourages creative tension between earnest utility and playful exploration."
            }
        ],
        
        "why_hardcard": "The name 'Hard Card' evokes several interconnected concepts central to our mission. A physical hard card represents something durable, tangible, and resistant to corruption—qualities we seek in both financial and wisdom preservation. The term also suggests a playing card, acknowledging both the seriousness of legacy-building and the game-like, strategic thinking it requires. Additionally, 'hard' contrasts with the often soft, ephemeral nature of digital assets, reminding us to seek substantive value that persists even as technologies change.",
        
        "mission_statement": "To create an integrated ecosystem that enables families and organizations to build meaningful, multi-generational legacies combining financial wealth and intellectual wisdom through coherent, interconnected systems rather than fragmented tools and approaches."
    }
    
    return ManifestoResponse(**manifesto_data)

@router.get("/hcu-architecture")
def get_hard_card_universe_architecture() -> ArchitectureResponse:
    """Returns the Hard Card Universe architectural framework.
    
    This endpoint provides the high-level architecture, including the hub and spoke
    model, governance structure, API standards, and component relationships.
    """
    
    architecture_data = {
        "title": "Hard Card Universe Architectural Framework",
        "description": "The HCU follows a hub-and-spoke architecture with a central core connected to independent but harmonized modules. This structure allows for both specialized functionality in each module and coherent integration across the ecosystem.",
        
        "components": [
            {
                "id": "central-hub",
                "name": "HCU Central Hub",
                "type": "core",
                "description": "The coordination center of the HCU ecosystem, maintaining the shared standards, authentication, API gateway, and central data repositories.",
                "status": "active",
                "technical_stack": {
                    "frontend": ["React", "TypeScript", "Tailwind"],
                    "backend": ["Python", "FastAPI", "Firebase"],
                    "storage": ["Firestore", "DataButton Storage"]
                }
            },
            {
                "id": "legacy-vault",
                "name": "Legacy Vault",
                "type": "module",
                "description": "The financial cornerstone of HCU, handling multi-generational investment tracking, legacy gift management, and wealth preservation strategies.",
                "status": "active",
                "parent": "central-hub",
                "technical_stack": {
                    "frontend": ["React", "TypeScript", "Recharts"],
                    "backend": ["Python", "FastAPI"],
                    "storage": ["Firestore"]
                }
            },
            {
                "id": "enlightenment-journey",
                "name": "Enlightenment Journey",
                "type": "module",
                "description": "The wisdom acquisition arm of HCU, focused on structured knowledge building, book analysis, and intellectual legacy preservation.",
                "status": "active",
                "parent": "central-hub",
                "technical_stack": {
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Python", "FastAPI", "OpenAI"],
                    "storage": ["Firestore", "DataButton Storage"]
                }
            },
            {
                "id": "noir-mystery",
                "name": "Noir Mystery",
                "type": "module",
                "description": "Creative narrative project exploring themes of legacy and trust through an interactive noir murder mystery framework.",
                "status": "planned",
                "parent": "central-hub",
                "technical_stack": {
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Python", "FastAPI"],
                    "storage": ["Firestore"]
                }
            },
            {
                "id": "meta-narrative",
                "name": "Meta-Narrative",
                "type": "module",
                "description": "Multi-layered podcast and interactive media project documenting the creation and philosophy of the HCU itself.",
                "status": "planned",
                "parent": "central-hub",
                "technical_stack": {
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Python", "FastAPI"],
                    "storage": ["Firestore", "DataButton Storage"]
                }
            },
            {
                "id": "api-gateway",
                "name": "API Gateway & Integration Layer",
                "type": "infrastructure",
                "description": "Central API management system that handles routing, authentication, and data transformation between modules.",
                "status": "active",
                "parent": "central-hub",
                "technical_stack": {
                    "frontend": [],
                    "backend": ["Python", "FastAPI"],
                    "storage": []
                }
            },
            {
                "id": "identity-manager",
                "name": "Identity & Access Management",
                "type": "infrastructure",
                "description": "Centralized authentication and authorization system for all HCU modules.",
                "status": "active",
                "parent": "central-hub",
                "technical_stack": {
                    "frontend": ["React", "TypeScript"],
                    "backend": ["Firebase Auth"],
                    "storage": ["Firestore"]
                }
            }
        ],
        
        "connections": [
            {
                "source": "central-hub",
                "target": "legacy-vault",
                "type": "bi-directional",
                "description": "Core identity and financial data exchange"
            },
            {
                "source": "central-hub",
                "target": "enlightenment-journey",
                "type": "bi-directional",
                "description": "Knowledge repository integration and user preference sharing"
            },
            {
                "source": "central-hub",
                "target": "noir-mystery",
                "type": "planned",
                "description": "Creative content integration and user engagement metrics"
            },
            {
                "source": "central-hub",
                "target": "meta-narrative",
                "type": "planned",
                "description": "System-wide analytics and development narrative"
            },
            {
                "source": "legacy-vault",
                "target": "enlightenment-journey",
                "type": "bi-directional",
                "description": "Financial wisdom integration and legacy planning"
            },
            {
                "source": "noir-mystery",
                "target": "meta-narrative",
                "type": "planned",
                "description": "Narrative interconnection and creative element sharing"
            }
        ],
        
        "governance_model": {
            "structure": "The HCU follows a federated governance model with a central coordination team and specialized teams for each module.",
            "decision_making": {
                "strategic": "Central HCU Steering Committee",
                "tactical": "Module Leadership Teams",
                "operational": "Individual Development and Creative Teams"
            },
            "principles": [
                "Coherence preservation across all modules and initiatives",
                "Balanced autonomy with integration requirements",
                "Transparency in architectural decisions and roadmaps",
                "Multi-generational impact assessment for major decisions",
                "Regular architectural reviews and alignment sessions"
            ]
        },
        
        "api_standards": {
            "protocol": "REST with JSON",
            "authentication": "JWT with Firebase Auth",
            "versioning": "URI path versioning",
            "documentation": "OpenAPI/Swagger",
            "rate_limiting": "Token bucket per API key",
            "error_handling": "Standardized error responses with detailed codes",
            "data_exchange": "Standardized envelope format with metadata"
        }
    }
    
    return ArchitectureResponse(**architecture_data)

@router.get("/hcu-modules")
def list_hard_card_universe_modules() -> List[Module]:
    """Lists all modules in the Hard Card Universe ecosystem.
    
    This endpoint provides information about each module, including its status,
    description, connections to other modules, and metadata.
    """
    
    modules_data = [
        {
            "id": "legacy-vault",
            "name": "Legacy Vault",
            "description": "The financial cornerstone of the Hard Card Universe, the Legacy Vault module provides comprehensive tools for multi-generational investment tracking, legacy gift management, and wealth preservation strategies. It serves as the financial foundation that supports wisdom acquisition and legacy-building endeavors.",
            "status": "active",
            "connections": [
                {"target": "Central Hub", "type": "core integration"},
                {"target": "Enlightenment Journey", "type": "data exchange"}
            ],
            "metadata": {
                "key_features": [
                    "Multi-generational investment tracking and visualization",
                    "Legacy gift management system for Bitcoin and other assets",
                    "Performance tracking against philosophical principles",
                    "Family trust fund visualization and management",
                    "Automated reporting and inheritance planning tools"
                ],
                "technical_integration": "Directly integrated with HCU Central Hub via REST API with JWT authentication, shares investment philosophy tags with Enlightenment Journey."
            }
        },
        {
            "id": "enlightenment-journey",
            "name": "Enlightenment Journey",
            "description": "The wisdom acquisition arm of the Hard Card Universe, the Enlightenment Journey module provides structured approaches to knowledge building, book analysis, and intellectual legacy preservation. It transforms passive reading into active wisdom cultivation that can be preserved and transferred across generations.",
            "status": "active",
            "connections": [
                {"target": "Central Hub", "type": "core integration"},
                {"target": "Legacy Vault", "type": "data exchange"}
            ],
            "metadata": {
                "key_features": [
                    "Structured book analysis and wisdom extraction framework",
                    "Personal Canon development and curation tools",
                    "Multi-generational knowledge transfer system",
                    "Integration of financial concepts with philosophical wisdom",
                    "AI-assisted insight generation and connection"
                ],
                "technical_integration": "Connects to HCU Central Hub for identity and preference data, exchanges philosophical frameworks with Legacy Vault for investment alignment."
            }
        },
        {
            "id": "noir-mystery",
            "name": "Noir Mystery",
            "description": "A creative narrative project exploring themes of legacy, trust, and the value of long-term thinking through an interactive noir murder mystery framework. This module serves as both entertainment and allegory, embedding HCU philosophy in narrative form while critiquing short-term financial thinking.",
            "status": "planned",
            "connections": [
                {"target": "Central Hub", "type": "planned integration"},
                {"target": "Meta-Narrative", "type": "narrative overlap"}
            ],
            "metadata": {
                "key_features": [
                    "Interactive noir mystery storyline with legacy themes",
                    "Character-driven exploration of financial short-termism",
                    "Meta-commentary on insurance and financial services",
                    "Multiple narrative layers with varying levels of fiction",
                    "Potential ARG (Alternate Reality Game) elements"
                ],
                "technical_integration": "Planned integration with HCU Central Hub for user profiles and preferences, will share creative elements with Meta-Narrative module."
            }
        },
        {
            "id": "meta-narrative",
            "name": "Meta-Narrative",
            "description": "A multi-layered podcast and interactive media project documenting the creation, philosophy, and evolution of the Hard Card Universe itself. This self-reflective module creates a record of the development process while exploring the meta-concepts behind legacy-building in general.",
            "status": "planned",
            "connections": [
                {"target": "Central Hub", "type": "planned integration"},
                {"target": "Noir Mystery", "type": "narrative overlap"}
            ],
            "metadata": {
                "key_features": [
                    "Behind-the-scenes podcast series on HCU development",
                    "Multi-layered narrative with blending of fiction and reality",
                    "Documentation of architectural decisions and evolution",
                    "Business book analysis and application episodes",
                    "Interactive community engagement mechanisms"
                ],
                "technical_integration": "Planned integration with HCU Central Hub for development tracking and analytics, will incorporate narrative elements from Noir Mystery module."
            }
        }
    ]
    
    return modules_data

@router.get("/hcu-module/{module_id}")
def get_hard_card_universe_module(module_id: str) -> Module:
    """Returns details for a specific HCU module by ID.
    
    This endpoint provides comprehensive information about a single module in the
    Hard Card Universe ecosystem, including its connections, features, and status.
    """
    
    # A real implementation would fetch from a database based on module_id
    # This is a simplified example returning mock data
    
    modules = list_hard_card_universe_modules()
    for module in modules:
        if module.get("id") == module_id:
            return module
    
    # Handle case where module is not found
    # In a real implementation, this would raise an appropriate exception
    return None
