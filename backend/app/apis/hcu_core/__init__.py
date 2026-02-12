from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class PrincipleComponent(BaseModel):
    title: str
    description: str
    application: str

class ArchitectureComponent(BaseModel):
    name: str
    purpose: str
    description: str
    integration_points: List[str]

class HCUModule(BaseModel):
    id: str
    name: str
    description: str
    status: str
    integration_level: str
    primary_outcomes: List[str]

class HCUManifestoResponse(BaseModel):
    title: str
    vision_statement: str
    mission: str
    core_philosophy: str
    guiding_principles: List[PrincipleComponent]
    long_term_vision: str
    values: List[Dict[str, str]]

class HCUArchitectureResponse(BaseModel):
    title: str
    description: str
    architectural_approach: str
    hub_description: str
    api_integration_model: str
    components: List[ArchitectureComponent]
    design_principles: List[Dict[str, str]]
    governance_model: Dict[str, Any]

class HCUModulesResponse(BaseModel):
    module_count: int
    modules: List[HCUModule]
    integration_strategy: str
    expansion_approach: str

@router.get("/manifesto")
def get_hcu_manifesto() -> HCUManifestoResponse:
    """Returns the Hard Card Universe manifesto and vision statement.
    
    This endpoint provides the core philosophy, vision, mission and guiding
    principles of the Hard Card Universe ecosystem.
    """
    
    manifesto = {
        "title": "The Hard Card Universe: A Manifesto for Legacy Building",
        "vision_statement": "To create a comprehensive ecosystem that transforms how individuals and families build, preserve, and transfer both wealth and wisdom across generations.",
        "mission": "The Hard Card Universe exists to provide innovative tools, narratives, and frameworks that empower people to create meaningful, lasting legacies that transcend traditional financial planning.",
        "core_philosophy": "At the heart of the Hard Card Universe is the recognition that true legacy encompasses not just financial assets, but also wisdom, values, stories, and purpose. We believe that by integrating cutting-edge technology with timeless principles of intergenerational stewardship, we can create systems that preserve and enhance both material wealth and immaterial wisdom across generations. The Hard Card approach bridges the gap between the certainty of physical assets and the uncertainty of future needs, creating coherence amidst the noise of contemporary financial and technological landscapes.",
        
        "guiding_principles": [
            {
                "title": "Multigenerational Timeframes",
                "description": "All Hard Card Universe initiatives operate on genuinely long-term (50+ year) timelines, embracing the mathematics of compounding and the perspective shifts that occur when planning extends beyond a single lifetime.",
                "application": "Investment strategies, content planning, technology architecture, and narrative development all explicitly incorporate multi-decade perspectives and outcomes."
            },
            {
                "title": "Integration of Wisdom and Wealth",
                "description": "Financial assets without guiding wisdom deteriorate; wisdom without practical application remains theoretical. The Hard Card Universe explicitly connects these domains.",
                "application": "Every technology component and creative initiative includes mechanisms for capturing, preserving, and transferring both financial assets and the wisdom needed to steward them effectively."
            },
            {
                "title": "Narrative as Framework",
                "description": "Stories provide the cognitive scaffolding for complex ideas to be understood, remembered, and implemented. The Hard Card Universe employs narrative as a primary vehicle for transmitting core concepts.",
                "application": "Creative narratives like the noir mystery serve as accessible entry points to sophisticated legacy planning concepts, layered for different levels of engagement."
            },
            {
                "title": "Technological Amplification",
                "description": "Technology serves as a force multiplier for human intention, not a replacement for human judgment. The Hard Card Universe leverages advanced technology while maintaining human values at the center.",
                "application": "AI, automation, and algorithmic tools are deployed to extend human capability in legacy planning while preserving core human values and relationship elements."
            },
            {
                "title": "Coherence Across Components",
                "description": "While the Hard Card Universe comprises distinct modules with different functions, all maintain philosophical and practical coherence with the core vision and with each other.",
                "application": "A unified API architecture ensures that all modules share consistent data, terminology, and user experience, regardless of their specialized functions."
            },
            {
                "title": "Balanced Stewardship",
                "description": "Effective legacy planning balances capital preservation with calculated growth opportunities, conservative foundations with selective innovation, and individual autonomy with familial responsibility.",
                "application": "Portfolio structures, governance models, and decision frameworks all explicitly incorporate mechanisms for maintaining this balance across generations."
            }
        ],
        
        "long_term_vision": "The Hard Card Universe aims to become the definitive platform for holistic legacy building, recognized globally as the gold standard for integrating financial stewardship, wisdom transfer, and purposeful storytelling across generations. By 2030, we envision millions of families using Hard Card tools and frameworks to create legacies that combine financial security with meaningful purpose, ultimately reshaping how society thinks about inheritance, wealth, and generational impact.",
        
        "values": [
            {
                "name": "Integrity",
                "description": "Unwavering commitment to truth, transparency, and alignment between stated principles and actual practices."
            },
            {
                "name": "Foresight",
                "description": "Disciplined consideration of long-term consequences in all decisions, prioritizing multi-generational outcomes over short-term gains."
            },
            {
                "name": "Wisdom",
                "description": "Pursuit of deep understanding through both scholarly knowledge and practical experience, combined with ethical application."
            },
            {
                "name": "Stewardship",
                "description": "Recognition that wealth and knowledge are not merely possessed but held in trust for future generations and broader communities."
            },
            {
                "name": "Adaptability",
                "description": "Maintaining core principles while evolving methods and approaches as contexts change across generations and technological landscapes."
            },
            {
                "name": "Coherence",
                "description": "Creating alignment between values, actions, and outcomes that reinforces rather than fragments legacy intentions over time."
            }
        ]
    }
    
    return HCUManifestoResponse(**manifesto)

@router.get("/architecture")
def get_hcu_architecture() -> HCUArchitectureResponse:
    """Returns the Hard Card Universe architectural overview.
    
    This endpoint provides details about the high-level architecture of the
    Hard Card Universe ecosystem, including the hub and spoke model, API
    integration strategy, and governance approach.
    """
    
    architecture = {
        "title": "Hard Card Universe: Architectural Framework",
        "description": "The architectural design of the Hard Card Universe (HCU) reflects its philosophical foundations - creating coherence from complexity, balancing certainty with flexibility, and enabling multi-generational functionality. The architecture employs a hub-and-spoke model with a central core connected to specialized modules via standardized APIs, allowing for both consistency and adaptability as the ecosystem grows.",
        "architectural_approach": "The HCU employs a 'Federated Module' architecture where a strong central hub maintains core services, shared data models, and integration standards, while semi-autonomous modules provide specialized functionality. This approach allows for coordinated evolution while enabling innovation within individual domains.",
        
        "hub_description": "The HCU Core serves as the central hub of the ecosystem, providing foundational services including: identity management, value principle preservation, cross-module data harmonization, governance enforcement, and coherence monitoring. The hub maintains the philosophical integrity of the entire ecosystem while facilitating technical integration between modules.",
        
        "api_integration_model": "All HCU modules connect to the central hub and to each other through a standardized API framework that ensures data consistency, user experience coherence, and functional interoperability. This API-first approach enables both internal module communication and potential future integration with external services and platforms, ensuring the HCU remains adaptable to technological evolution.",
        
        "components": [
            {
                "name": "HCU Core",
                "purpose": "Central hub and foundational services",
                "description": "Provides identity management, value preservation, cross-module coordination, and maintains the philosophical and functional coherence of the ecosystem.",
                "integration_points": [
                    "All modules connect to the Core for authentication and authorization",
                    "Shared data models for cross-module consistency",
                    "Governance enforcement and coherence monitoring",
                    "Central event bus for cross-module communication"
                ]
            },
            {
                "name": "Creative Narrative Modules",
                "purpose": "Engaging story vehicles for concept introduction",
                "description": "Narrative experiences like the noir mystery that serve as accessible entry points to sophisticated legacy concepts, with varying levels of interactivity and meta-narrative layering.",
                "integration_points": [
                    "Connect to Core for user profile and progress tracking",
                    "API endpoints for narrative content and interactive elements",
                    "Event publication for user engagement tracking",
                    "Integration with Media modules for content delivery"
                ]
            },
            {
                "name": "Knowledge Repository Modules",
                "purpose": "Wisdom storage and transfer mechanisms",
                "description": "Structured frameworks for capturing, organizing, preserving, and transferring wisdom across generations, including business knowledge, personal values, and practical skills.",
                "integration_points": [
                    "Connect to Core for user identity and access management",
                    "API endpoints for knowledge retrieval and contribution",
                    "Integration with AI modules for knowledge processing",
                    "Integration with Legacy Planning modules for wisdom transfer"
                ]
            },
            {
                "name": "Financial Stewardship Modules",
                "purpose": "Multi-generational wealth management",
                "description": "Tools and frameworks for long-term financial planning, asset protection, growth strategy development, and generational wealth transfer with accompanying wisdom.",
                "integration_points": [
                    "Connect to Core for user authorization and value alignment",
                    "API endpoints for financial data and planning tools",
                    "Integration with Family Governance modules",
                    "Secure financial data exchange protocols"
                ]
            },
            {
                "name": "Family Governance Modules",
                "purpose": "Multi-generational decision frameworks",
                "description": "Structures and processes for family decision-making, conflict resolution, value preservation, and the balanced transfer of control across generations.",
                "integration_points": [
                    "Connect to Core for family identity and relationship mapping",
                    "API endpoints for governance tools and templates",
                    "Integration with Knowledge Repository for wisdom access",
                    "Integration with Financial Stewardship for aligned implementation"
                ]
            },
            {
                "name": "Media Distribution Modules",
                "purpose": "Content delivery and engagement",
                "description": "Platforms for distributing HCU content including podcasts, interactive narratives, educational materials, and community engagement tools.",
                "integration_points": [
                    "Connect to Core for content coherence validation",
                    "API endpoints for content access and engagement metrics",
                    "Integration with Creative Narrative modules",
                    "External platform integration capabilities"
                ]
            },
            {
                "name": "AI and Automation Modules",
                "purpose": "Technological amplification of human intention",
                "description": "Artificial intelligence and automation tools that extend human capability in legacy planning while preserving core human values and relationship elements.",
                "integration_points": [
                    "Connect to Core for value alignment and ethics enforcement",
                    "API endpoints for AI capabilities and decision support",
                    "Integration with Knowledge Repository for training data",
                    "Integration with Financial Stewardship for enhanced analysis"
                ]
            }
        ],
        
        "design_principles": [
            {
                "name": "API-First Development",
                "description": "All functionality is designed as API services before user interfaces, ensuring modularity, reusability, and future extensibility."
            },
            {
                "name": "Progressive Coherence",
                "description": "Modules can begin with minimal integration and progressively increase their coherence with the ecosystem over time, allowing for rapid initial development."
            },
            {
                "name": "Value-Aligned Data Models",
                "description": "Core data structures explicitly incorporate HCU values and principles, ensuring that technical implementation reinforces philosophical intentions."
            },
            {
                "name": "Multi-Generational Durability",
                "description": "Technical choices prioritize long-term stability and backwards compatibility, minimizing dependency on transient technologies or platforms."
            },
            {
                "name": "Graceful Adaptation",
                "description": "All systems are designed to evolve without disruption, with clear version management and transition paths as technologies and needs change."
            },
            {
                "name": "Human-Centered Automation",
                "description": "Technological systems amplify human intention and judgment rather than replacing them, with clear boundaries for algorithmic vs. human decision authority."
            }
        ],
        
        "governance_model": {
            "structure": "The HCU governance model operates at three levels: philosophical (maintaining alignment with core values), architectural (ensuring technical coherence), and operational (managing day-to-day development and growth).",
            
            "bodies": [
                {
                    "name": "Values Council",
                    "purpose": "Preserves and evolves the core philosophy and principles of the Hard Card Universe",
                    "responsibilities": [
                        "Maintaining and occasionally refining the HCU Manifesto",
                        "Evaluating new modules for philosophical alignment",
                        "Resolving value conflicts or ambiguities",
                        "Long-term vision stewardship"
                    ]
                },
                {
                    "name": "Architecture Board",
                    "purpose": "Ensures technical coherence and alignment across the ecosystem",
                    "responsibilities": [
                        "API standards development and enforcement",
                        "Cross-module integration oversight",
                        "Technical debt management",
                        "Security and privacy architecture"
                    ]
                },
                {
                    "name": "Module Teams",
                    "purpose": "Develop and maintain specific functional modules within the ecosystem",
                    "responsibilities": [
                        "Domain-specific innovation and development",
                        "User experience within module boundaries",
                        "Integration with Core and other modules",
                        "Feedback collection and implementation"
                    ]
                }
            ],
            
            "decision_framework": "HCU employs a 'distributed alignment' model where decisions are pushed to the lowest appropriate level while maintaining alignment through shared principles and clear escalation paths. Modules have high autonomy within their domains provided they maintain coherence with the ecosystem."
        }
    }
    
    return HCUArchitectureResponse(**architecture)

@router.get("/modules")
def get_hcu_modules() -> HCUModulesResponse:
    """Returns the list of Hard Card Universe modules.
    
    This endpoint provides information about the various modules that make up the
    Hard Card Universe ecosystem, including their descriptions, status, and integration levels.
    """
    
    modules_data = {
        "module_count": 5,
        "modules": [
            {
                "id": "hcu-core",
                "name": "HCU Core Hub",
                "description": "The central hub of the Hard Card Universe, providing the foundational services, manifesto, and architectural framework that connects all other modules. Includes identity management, value preservation, and cross-module coordination.",
                "status": "Active Development",
                "integration_level": "Central Hub",
                "primary_outcomes": [
                    "Unified philosophical foundation for all HCU modules",
                    "Coherent user experience across diverse functional areas",
                    "Standardized API framework for module interoperability",
                    "Centralized governance and alignment enforcement"
                ]
            },
            {
                "id": "noir-mystery",
                "name": "The Last Premium: Noir Mystery Experience",
                "description": "An interactive noir mystery narrative that serves as a creative vehicle for introducing key Hard Card Universe concepts. Follows insurance investigator Luigi Amato as he uncovers a conspiracy involving legacy algorithms and generational wealth transfer.",
                "status": "Active Development",
                "integration_level": "Creative Narrative Module",
                "primary_outcomes": [
                    "Engaging narrative introduction to HCU concepts",
                    "Exploration of insurance, legacy building and wealth preservation themes",
                    "Meta-narrative framework for broader HCU engagement",
                    "Interactive storytelling with practical application bridges"
                ]
            },
            {
                "id": "meta-narrative",
                "name": "The Hard Card Chronicles: Meta-Narrative Framework",
                "description": "A multi-layered narrative approach that blends fiction, documentary, and direct audience engagement to create a rich tapestry where stories and reality interweave to explore legacy concepts. Includes podcast series and ARG elements.",
                "status": "Active Development",
                "integration_level": "Media Distribution Module",
                "primary_outcomes": [
                    "Multi-layered engagement model for different audience depths",
                    "Reality-blurring approach that drives curiosity and exploration",
                    "Structured progression from entertainment to practical application",
                    "Community building around shared narrative experiences"
                ]
            },
            {
                "id": "podcast-strategy",
                "name": "Hard Card University: Podcast Knowledge Series",
                "description": "A strategic approach to podcast content creation focusing on key niches including Automation & AI, Storytelling, Business Literature Analysis, Multi-Generational Investment, Digital Assets, and Family Business Scaling.",
                "status": "Active Development",
                "integration_level": "Knowledge Repository Module",
                "primary_outcomes": [
                    "Authoritative content in high-value knowledge niches",
                    "Beachhead audience building in targeted segments",
                    "Practical wisdom capture and dissemination",
                    "Entry point for HCU platform exploration"
                ]
            },
            {
                "id": "family-trust",
                "name": "Legacy Vault: Family Trust Management",
                "description": "Tools and frameworks for establishing and managing multigenerational family trusts, with a focus on both financial growth and wisdom transfer. Includes Bitcoin allocation mechanisms, governance structures, and educational components.",
                "status": "Planning Phase",
                "integration_level": "Financial Stewardship Module",
                "primary_outcomes": [
                    "Structured approach to multigenerational wealth preservation",
                    "Integration of traditional and digital assets in trust structures",
                    "Educational frameworks for heir preparation and development",
                    "Governance models that balance growth and preservation"
                ]
            }
        ],
        "integration_strategy": "Modules are developed with progressive integration, beginning with core functionality and minimal connections to the HCU hub, then gradually increasing interoperability and ecosystem coherence. This approach allows for rapid initial development of functional capabilities while ensuring all modules ultimately create a unified experience.",
        "expansion_approach": "The Hard Card Universe follows a 'core and expand' development strategy. Initial modules establish the foundational architecture, philosophical framework, and narrative approach. Future expansion will proceed along two paths: deepening existing modules with enhanced functionality, and broadening with new modules that address additional aspects of comprehensive legacy building."
    }
    
    return HCUModulesResponse(**modules_data)
