from fastapi import APIRouter, Depends
from pydantic import BaseModel
import databutton as db
from typing import List, Dict, Any, Optional

router = APIRouter()

class CorePrinciple(BaseModel):
    """A core principle of the HCU manifesto"""
    title: str
    description: str


class ManifestoResponse(BaseModel):
    """Response model for the HCU Manifesto/Vision Statement"""
    title: str
    subtitle: str
    vision: str
    core_principles: List[CorePrinciple]
    why_hardcard: str
    mission_statement: str
    legacy_statement: str

class GovernanceRole(BaseModel):
    """A governance role in the HCU ecosystem"""
    title: str
    description: str
    rights: List[str]
    responsibilities: List[str]


class ArchitectureComponent(BaseModel):
    """A component in the HCU architecture"""
    id: str
    name: str
    type: str
    description: str
    status: str
    responsibilities: List[str]
    connections: List[str]
    parent: Optional[str] = None
    technical_stack: Optional[Dict[str, List[str]]] = None


class APIContract(BaseModel):
    """An API contract in the HCU architecture"""
    name: str
    description: str
    endpoints: List[Dict[str, str]]
    access_control: str


class UpdateProtocol(BaseModel):
    """An update protocol in the HCU architecture"""
    name: str
    description: str
    steps: str


class ArchitectureResponse(BaseModel):
    """Response model for the HCU Architecture"""
    title: str
    description: str
    hub_spoke_model: Dict[str, str]
    components: List[ArchitectureComponent]
    connections: List[Dict[str, Any]]
    governance_model: Dict[str, Any]
    api_contracts: List[APIContract]
    update_protocols: List[UpdateProtocol]
    api_standards: Dict[str, Any]

class ModuleResponse(BaseModel):
    """Response model for a HCU Module"""
    id: str
    name: str
    description: str
    status: str
    connections: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@router.get("/hardcard-manifesto")
def get_hardcard_manifesto() -> ManifestoResponse:
    """Provides the Hard Card Universe Manifesto and Core Vision
    
    This endpoint returns the foundational vision and principles of the
    Hard Card Universe ecosystem, explaining its philosophy and mission.
    """
    manifesto = {
        "title": "Hard Card Universe Manifesto",
        "subtitle": "Legacy + Certainty in an Uncertain World",
        "vision": "The Hard Card Universe (HCU) represents a paradigm shift in the approach to legacy building, wealth preservation, and knowledge transfer. It integrates sophisticated financial mechanisms with immersive storytelling and educational frameworks to create a cohesive ecosystem that spans generations, ensuring that values, knowledge, and assets are preserved and grown over time.",
        
        "core_principles": [
            CorePrinciple(
                title="Intergenerational Value Transfer",
                description="Creating systems that allow wealth, knowledge, and values to transcend generations, preserved through robust technologies and governance frameworks."
            ),
            CorePrinciple(
                title="Technical Certainty",
                description="Employing cryptographic principles, distributed systems, and formal verification to ensure that digital assets and knowledge remain accessible and intact over decades."
            ),
            CorePrinciple(
                title="Narrative Integration",
                description="Weaving compelling stories that connect family history, values, and aspirations with technological systems, making abstract concepts tangible and meaningful."
            ),
            CorePrinciple(
                title="Adaptability with Preservation",
                description="Building systems that can evolve with changing technologies while maintaining core data integrity and accessibility across technological shifts."
            ),
            CorePrinciple(
                title="Ethical Speculation",
                description="Balancing conservative preservation with strategic risk-taking, always guided by long-term thinking and intergenerational benefit."
            ),
            CorePrinciple(
                title="Legacy Over Transactions",
                description="Prioritizing multi-generational impact over short-term gains. Every component is designed with longevity and meaningful inheritance in mind."
            ),
            CorePrinciple(
                title="Wisdom Alongside Wealth",
                description="Financial growth is complemented by philosophical and educational depth, creating a balanced inheritance that includes both material and intellectual prosperity."
            )
        ],
        
        "why_hardcard": "The Hard Card represents the physical manifestation of certainty and trust in an increasingly digital and ephemeral world. It embodies the tangible commitment to preserving value, identity, and legacy across generations, serving as both a technological tool and a philosophical symbol of our commitment to future generations.",
        
        "mission_statement": "To forge an integrated ecosystem that empowers families to build, preserve, and transfer both wealth and wisdom across generations through coherent frameworks that balance certainty with strategic growth, utilizing cutting-edge technology alongside timeless principles of stewardship.",
        
        "legacy_statement": "The Hard Card Universe is more than a collection of technologies or investment strategies—it is a framework for thinking about time differently. We measure success not in quarters or years, but in generations. Every decision, protocol, and narrative is designed with the future in mind, creating an enduring legacy that transcends individual lifespans."
    }
    
    return ManifestoResponse(**manifesto)

@router.get("/hardcard-architecture")
def get_hardcard_architecture() -> ArchitectureResponse:
    """Provides the Hard Card Universe Architecture
    
    This endpoint returns the high-level architectural design of the HCU ecosystem,
    including its hub-and-spoke model, component relationships, and governance framework.
    """
    architecture = {
        "title": "Hard Card Universe - System Architecture Blueprint",
        "description": "The HCU utilizes a hub-and-spoke architecture with modular components connected through well-defined API contracts. This design enables independent evolution of components while maintaining system cohesion through centralized governance and data flow management.",
        
        "hub_spoke_model": {
            "hub": "Central HCU Core - Manages identity, governance, and cross-module data flow",
            "spokes": "Specialized modules for different aspects of legacy management and growth",
            "connectors": "Standardized API contracts that define how modules interact with the core and each other"
        },
        
        "components": [
            ArchitectureComponent(
                id="central-hub",
                name="HCU Central Hub",
                type="core",
                description="The primary coordination platform that manages authentication, data synchronization, event publishing, and cross-module integration. Maintains the cohesive narrative and governance model across all modules.",
                status="in-development",
                responsibilities=[
                    "Identity and access management",
                    "Cross-module data synchronization",
                    "Event publishing and subscription",
                    "Governance enforcement",
                    "System-wide logging and monitoring"
                ],
                connections=[
                    "legacy-vault",
                    "enlightenment-journey",
                    "noir-mystery",
                    "meta-narrative"
                ],
                technical_stack={
                    "frontend": ["React", "TypeScript", "TailwindCSS"],
                    "backend": ["FastAPI", "Firebase"],
                    "storage": ["Firestore", "Databutton Storage"]
                }
            ),
            ArchitectureComponent(
                id="legacy-vault",
                name="Legacy Vault",
                type="module",
                description="The foundational financial module that manages Bitcoin investments, trust structures, and long-term wealth preservation strategies.",
                status="active",
                responsibilities=[
                    "Bitcoin and cryptocurrency management",
                    "Trust fund administration",
                    "Long-term investment strategy execution",
                    "Regular reporting and performance tracking",
                    "Inheritance planning and execution"
                ],
                connections=[
                    "central-hub",
                    "familial-trust",
                    "formal-verification"
                ],
                parent="central-hub",
                technical_stack={
                    "frontend": ["React", "TailwindCSS", "recharts"],
                    "backend": ["FastAPI", "Python Crypto Libraries"],
                    "storage": ["Firestore", "Secure Storage Solutions"]
                }
            ),
            ArchitectureComponent(
                id="enlightenment-journey",
                name="Enlightenment Journey",
                type="module",
                description="Educational module that curates wisdom literature, philosophical works, and learning pathways tied to life stages and asset growth.",
                status="active",
                responsibilities=[
                    "Curation of business and financial knowledge",
                    "Age-appropriate learning paths",
                    "Progress tracking and knowledge verification",
                    "Integration with real-world educational resources",
                    "Personalized recommendations"
                ],
                connections=[
                    "central-hub",
                    "business-books",
                    "family-profiles"
                ],
                parent="central-hub",
                technical_stack={
                    "frontend": ["React", "TailwindCSS"],
                    "backend": ["FastAPI", "OpenAI Integration"],
                    "storage": ["Firestore", "Document Database"]
                }
            ),
            ArchitectureComponent(
                id="noir-mystery",
                name="Noir Mystery Narrative",
                type="module",
                description="Storytelling module delivering the noir murder mystery concept as a creative vehicle for exploring themes of insurance, legacy building, and trust.",
                status="planned",
                responsibilities=[
                    "Story development and episode creation",
                    "Character and plot management",
                    "Integration of real-world principles into fictional scenarios",
                    "Cross-module thematic connections",
                    "Interactive narrative elements"
                ],
                connections=[
                    "central-hub",
                    "meta-narrative",
                    "arg-components"
                ],
                parent="central-hub"
            ),
            ArchitectureComponent(
                id="meta-narrative",
                name="Meta-Narrative Framework",
                type="module",
                description="Executes the multidimensional storytelling approach through podcasts, interactive elements, and meta-commentary that bridges fiction and reality.",
                status="planned",
                responsibilities=[
                    "Narrative arc management",
                    "Thematic mapping across modules",
                    "Cross-media coordination",
                    "User participation framework",
                    "Podcast production and distribution"
                ],
                connections=[
                    "central-hub",
                    "noir-mystery",
                    "podcast-series",
                    "arg-components"
                ],
                parent="central-hub"
            ),
            ArchitectureComponent(
                id="business-books",
                name="Top 100 Business Books",
                type="module",
                description="Detailed analysis and synthesis of business literature, providing intellectual foundations for wealth building and management.",
                status="active",
                responsibilities=[
                    "Book curation and selection",
                    "Principle extraction and categorization",
                    "Learning level adaptations",
                    "Content relationship mapping",
                    "Application case studies"
                ],
                connections=[
                    "enlightenment-journey",
                    "podcast-series",
                    "content-daos"
                ],
                parent="enlightenment-journey"
            ),
            ArchitectureComponent(
                id="familial-trust",
                name="Familial Stewardship Structure",
                type="module",
                description="Governance and distribution framework for managing legacy assets based on contribution and relation.",
                status="planned",
                responsibilities=[
                    "Relation-based profit distribution",
                    "Contribution-based incentives",
                    "Multi-generational governance",
                    "Ethical frameworks for expansion",
                    "Conflict resolution mechanisms"
                ],
                connections=[
                    "legacy-vault",
                    "family-profiles",
                    "formal-verification"
                ],
                parent="legacy-vault"
            ),
            ArchitectureComponent(
                id="formal-verification",
                name="Formal Verification Engine",
                type="module",
                description="Mathematical proof system for ensuring security and correctness of critical protocols and smart contracts used throughout the HCU ecosystem.",
                status="in-development",
                responsibilities=[
                    "Formal specification of security properties",
                    "Automated verification of critical protocols",
                    "Security audit logging and reporting",
                    "Cryptographic agility maintenance",
                    "Theorem proving for financial contracts"
                ],
                connections=[
                    "legacy-vault",
                    "familial-trust",
                    "hardcard-hardware"
                ]
            ),
            ArchitectureComponent(
                id="family-profiles",
                name="Family Profiles",
                type="module",
                description="Management of family member identities, preferences, and access rights within the HCU ecosystem.",
                status="active",
                responsibilities=[
                    "Profile creation and management",
                    "Role-based access control",
                    "Age-appropriate revealing of assets and information",
                    "Legacy transfer protocols",
                    "Family relationship mapping"
                ],
                connections=[
                    "central-hub",
                    "familial-trust",
                    "enlightenment-journey",
                    "family-stories"
                ]
            ),
            ArchitectureComponent(
                id="podcast-series",
                name="Podcast Series",
                type="module",
                description="Audio content production and distribution platform for both narrative and educational content, featuring interviews, discussions, and storytelling.",
                status="in-development",
                responsibilities=[
                    "Episode production workflow",
                    "Guest management system",
                    "Distribution channel integration",
                    "Audience analytics",
                    "Content repurposing tools"
                ],
                connections=[
                    "meta-narrative",
                    "business-books",
                    "arg-components"
                ]
            ),
            ArchitectureComponent(
                id="hardcard-hardware",
                name="Hardcard Hardware",
                type="module",
                description="Physical security devices for authentication, key management, and asset protection, bridging the digital and physical worlds.",
                status="in-development",
                responsibilities=[
                    "Cryptographic key management",
                    "Multi-factor authentication",
                    "Physical durability and longevity",
                    "Offline transaction signing",
                    "Recovery mechanisms"
                ],
                connections=[
                    "formal-verification",
                    "legacy-vault",
                    "vaultos"
                ]
            ),
            ArchitectureComponent(
                id="family-stories",
                name="Family Stories",
                type="module",
                description="Personal and family narrative preservation system for capturing, organizing, and sharing stories, memories, and media across generations.",
                status="active",
                responsibilities=[
                    "Story collection tools",
                    "Media archiving and tagging",
                    "Timeline visualization",
                    "Relationship mapping",
                    "Privacy and sharing controls"
                ],
                connections=[
                    "family-profiles",
                    "content-daos",
                    "meta-narrative"
                ]
            ),
            ArchitectureComponent(
                id="content-daos",
                name="Content DAOs",
                type="module",
                description="Decentralized autonomous organizations for collaborative content creation, curation, and governance within specific knowledge domains.",
                status="planned",
                responsibilities=[
                    "Governance and voting mechanisms",
                    "Contribution tracking and rewards",
                    "Quality control processes",
                    "Cross-DAO coordination",
                    "Content licensing management"
                ],
                connections=[
                    "business-books",
                    "family-stories",
                    "enlightenment-journey"
                ]
            ),
            ArchitectureComponent(
                id="arg-components",
                name="ARG Components",
                type="module",
                description="Alternate Reality Game elements that blend the fictional world with real-world interactions, creating immersive experiences and learning opportunities.",
                status="planned",
                responsibilities=[
                    "Puzzle and challenge design",
                    "Real-world integration points",
                    "Player progress tracking",
                    "Narrative advancement triggers",
                    "Community collaboration tools"
                ],
                connections=[
                    "meta-narrative",
                    "noir-mystery",
                    "podcast-series"
                ]
            ),
            ArchitectureComponent(
                id="vaultos",
                name="VaultOS",
                type="module",
                description="Operating system for secure asset management and access, providing a consistent interface across platforms and ensuring long-term accessibility.",
                status="in-development",
                responsibilities=[
                    "Secure boot sequence",
                    "Cross-platform runtime environment",
                    "API gateway and access control",
                    "Version compatibility layer",
                    "Backup and recovery systems"
                ],
                connections=[
                    "hardcard-hardware",
                    "formal-verification",
                    "legacy-vault"
                ]
            )
        ],
        
        "connections": [
            {
                "source": "central-hub",
                "target": "legacy-vault",
                "type": "bidirectional-api",
                "description": "Data synchronization for financial assets and investment strategies"
            },
            {
                "source": "central-hub",
                "target": "enlightenment-journey",
                "type": "bidirectional-api",
                "description": "Coordination of educational milestones with financial growth stages"
            },
            {
                "source": "central-hub",
                "target": "noir-mystery",
                "type": "content-api",
                "description": "Integration of narrative elements with the core platform"
            },
            {
                "source": "central-hub",
                "target": "meta-narrative",
                "type": "content-api",
                "description": "Framework for podcast and meta-commentary distribution"
            },
            {
                "source": "enlightenment-journey",
                "target": "business-books",
                "type": "content-api",
                "description": "Incorporation of business literature into broader educational pathways"
            },
            {
                "source": "legacy-vault",
                "target": "familial-trust",
                "type": "governance-api",
                "description": "Application of stewardship rules to financial assets"
            },
            {
                "source": "meta-narrative",
                "target": "podcast-series",
                "type": "content-production",
                "description": "Podcast content alignment with overarching narrative"
            },
            {
                "source": "family-profiles",
                "target": "familial-trust",
                "type": "governance-api",
                "description": "Identity verification and role-based access to trust management"
            },
            {
                "source": "formal-verification",
                "target": "legacy-vault",
                "type": "security-verification",
                "description": "Formal verification of financial contracts and protocols"
            },
            {
                "source": "hardcard-hardware",
                "target": "vaultos",
                "type": "device-integration",
                "description": "Secure hardware interface to VaultOS environment"
            },
            {
                "source": "family-stories",
                "target": "family-profiles",
                "type": "content-management",
                "description": "Association of family stories with appropriate profiles"
            },
            {
                "source": "content-daos",
                "target": "business-books",
                "type": "collaborative-curation",
                "description": "Community involvement in business book analysis and curation"
            }
        ],
        
        "governance_model": {
            "structure": "Federated with central oversight",
            "decision_making": {
                "strategic": "Central governance board",
                "tactical": "Module-level autonomy",
                "operational": "Distributed across modules"
            },
            "roles": [
                GovernanceRole(
                    title="System Architect",
                    description="Responsible for overall system design and evolution",
                    rights=[
                        "Propose architectural changes",
                        "Review and approve technical implementations",
                        "Define API contracts and standards"
                    ],
                    responsibilities=[
                        "Maintain system coherence and alignment",
                        "Ensure technical scalability and adaptability",
                        "Document architectural decisions and rationales"
                    ]
                ),
                GovernanceRole(
                    title="Content Steward",
                    description="Oversees narrative and educational content quality and alignment",
                    rights=[
                        "Approve content additions and changes",
                        "Define content standards and guidelines",
                        "Manage content categorization and organization"
                    ],
                    responsibilities=[
                        "Ensure content quality and relevance",
                        "Maintain thematic consistency across modules",
                        "Facilitate cross-module content integration"
                    ]
                ),
                GovernanceRole(
                    title="Security Guardian",
                    description="Ensures system security and data integrity",
                    rights=[
                        "Conduct security audits and assessments",
                        "Approve security-related changes",
                        "Define security policies and procedures"
                    ],
                    responsibilities=[
                        "Monitor system for security vulnerabilities",
                        "Implement and maintain security controls",
                        "Develop and test disaster recovery procedures"
                    ]
                ),
                GovernanceRole(
                    title="Family Trustee",
                    description="Represents family interests and ensures alignment with legacy goals",
                    rights=[
                        "Approve changes to core principles and goals",
                        "Override decisions that conflict with family interests",
                        "Define legacy transfer and succession policies"
                    ],
                    responsibilities=[
                        "Represent the interests of current and future family members",
                        "Ensure system evolution aligns with family values",
                        "Facilitate resolution of governance conflicts"
                    ]
                ),
                GovernanceRole(
                    title="Module Owner",
                    description="Responsible for specific module implementation and operation",
                    rights=[
                        "Define module-specific implementation details",
                        "Manage module resources and priorities",
                        "Implement approved changes within their module"
                    ],
                    responsibilities=[
                        "Ensure module fulfills its defined responsibilities",
                        "Maintain compatibility with API contracts",
                        "Report on module status and issues"
                    ]
                )
            ],
            "principles": [
                "Central coherence with module autonomy",
                "Consistent user experience across touchpoints",
                "Data integration with privacy preservation",
                "Cross-pollination of insights between modules",
                "Scalable architecture for future expansion",
                "Long-term stability with capability for evolution",
                "Ethical alignment across all components"
            ]
        },
        
        "api_contracts": [
            APIContract(
                name="Identity and Access API",
                description="Manages user authentication, authorization, and profile information",
                endpoints=[
                    {"path": "/authenticate", "purpose": "User authentication and session management"},
                    {"path": "/profiles", "purpose": "Profile CRUD operations"},
                    {"path": "/roles", "purpose": "Role and permission management"}
                ],
                access_control="Role-based with age-appropriate restrictions"
            ),
            APIContract(
                name="Asset Management API",
                description="Interfaces for managing and viewing legacy assets",
                endpoints=[
                    {"path": "/assets", "purpose": "Asset CRUD operations"},
                    {"path": "/transactions", "purpose": "Transaction history and execution"},
                    {"path": "/reports", "purpose": "Performance and status reporting"}
                ],
                access_control="Role-based with multi-signature requirements for critical operations"
            ),
            APIContract(
                name="Knowledge Graph API",
                description="Access to educational content and learning paths",
                endpoints=[
                    {"path": "/content", "purpose": "Educational content access"},
                    {"path": "/progress", "purpose": "Learning progress tracking"},
                    {"path": "/recommendations", "purpose": "Personalized learning recommendations"}
                ],
                access_control="Profile-based with age-appropriate content filtering"
            ),
            APIContract(
                name="Narrative API",
                description="Interface for story elements and interactive components",
                endpoints=[
                    {"path": "/stories", "purpose": "Narrative content access"},
                    {"path": "/interactions", "purpose": "User participation and choices"},
                    {"path": "/media", "purpose": "Multimedia content delivery"}
                ],
                access_control="Public with progressive unlocking based on user participation"
            ),
            APIContract(
                name="Governance API",
                description="System for module coordination and policy enforcement",
                endpoints=[
                    {"path": "/policies", "purpose": "Policy definition and retrieval"},
                    {"path": "/audits", "purpose": "Compliance logging and reporting"},
                    {"path": "/votes", "purpose": "Governance decision recording"}
                ],
                access_control="Role-based with multi-party consensus requirements"
            )
        ],
        
        "update_protocols": [
            UpdateProtocol(
                name="Minor Update Protocol",
                description="For changes that don't affect API contracts or core functionality",
                steps="1. Module Owner proposes change\n2. Technical review if needed\n3. Implementation\n4. Testing\n5. Deployment\n6. Documentation update"
            ),
            UpdateProtocol(
                name="Major Update Protocol",
                description="For changes that affect API contracts or core functionality",
                steps="1. Module Owner proposes change\n2. Review by System Architect\n3. Change Advisory Board approval\n4. Implementation plan development\n5. Technical Review Committee approval\n6. Implementation\n7. Testing\n8. Coordinated deployment\n9. Documentation update\n10. Post-deployment review"
            ),
            UpdateProtocol(
                name="Emergency Update Protocol",
                description="For critical security fixes or issue resolution",
                steps="1. Issue identification\n2. Security Guardian assessment\n3. Emergency fix development\n4. Expedited technical review\n5. Deployment\n6. Post-deployment documentation\n7. Root cause analysis\n8. Preventative measure implementation"
            ),
            UpdateProtocol(
                name="Evolution Protocol",
                description="For long-term strategic changes to the system architecture",
                steps="1. System Architect proposes evolution\n2. Stakeholder consultation\n3. Family Trustee review\n4. Ethics Council review\n5. Evolution roadmap development\n6. Phased implementation planning\n7. Change Advisory Board approval of phases\n8. Implementation of phases\n9. Continuous review and adjustment\n10. Final integration and documentation"
            )
        ],
        
        "api_standards": {
            "protocol": "REST with GraphQL for complex queries",
            "authentication": "OAuth 2.0 with central identity",
            "data_format": "JSON with standardized schemas",
            "versioning": "Semantic versioning with backwards compatibility",
            "documentation": "OpenAPI/Swagger with contextual examples",
            "event_model": "Publish/subscribe for cross-module coordination",
            "error_handling": "Consistent error codes and descriptive messages",
            "rate_limiting": "Module-specific with dynamic adjustment based on load",
            "caching": "Multi-level with invalidation protocols"
        }
    }
    
    return ArchitectureResponse(**architecture)

@router.get("/hardcard-modules")
def list_hardcard_modules() -> List[ModuleResponse]:
    """Lists all active and planned modules in the HCU ecosystem
    
    This endpoint provides details about all the modules that make up the
    Hard Card Universe ecosystem, their status, and connections.
    """
    # This would typically be stored in a database
    # For now, we're hardcoding the data for the initial implementation
    modules = [
        {
            "id": "legacy-vault",
            "name": "Legacy Vault",
            "description": "The foundational financial module that manages Bitcoin investments, trust structures, and long-term wealth preservation strategies.",
            "status": "active",
            "connections": [
                {"target": "central-hub", "type": "primary"},
                {"target": "familial-trust", "type": "parent"}
            ],
            "metadata": {
                "key_features": [
                    "Bitcoin birthday investments",
                    "Trust fund management",
                    "Long-term growth projections",
                    "Inheritance planning"
                ],
                "technical_integration": "Direct API access to financial data and investment strategies"
            }
        },
        {
            "id": "enlightenment-journey",
            "name": "Enlightenment Journey",
            "description": "Educational module that curates wisdom literature, philosophical works, and learning pathways tied to life stages and asset growth.",
            "status": "active",
            "connections": [
                {"target": "central-hub", "type": "primary"},
                {"target": "business-books", "type": "parent"}
            ],
            "metadata": {
                "key_features": [
                    "Age-appropriate reading lists",
                    "Philosophy and economics education",
                    "Milestone-based content unlocking",
                    "Personal development tracking"
                ],
                "technical_integration": "Content API with age and milestone triggers"
            }
        },
        {
            "id": "noir-mystery",
            "name": "Noir Mystery Narrative",
            "description": "Storytelling module delivering the noir murder mystery concept as a creative vehicle for exploring themes of insurance, legacy building, and trust.",
            "status": "planned",
            "connections": [
                {"target": "central-hub", "type": "primary"},
                {"target": "meta-narrative", "type": "related"}
            ],
            "metadata": {
                "key_features": [
                    "Interactive noir storyline",
                    "Character development (Luigi)",
                    "Insurance and legacy themes",
                    "Fourth-wall breaking elements"
                ],
                "technical_integration": "Narrative engine API with event triggers"
            }
        },
        {
            "id": "meta-narrative",
            "name": "Meta-Narrative Framework",
            "description": "Executes the multidimensional storytelling approach through podcasts, interactive elements, and meta-commentary that bridges fiction and reality.",
            "status": "planned",
            "connections": [
                {"target": "central-hub", "type": "primary"},
                {"target": "noir-mystery", "type": "related"}
            ],
            "metadata": {
                "key_features": [
                    "Podcast series production",
                    "Behind-the-scenes commentary",
                    "Fiction-reality blending",
                    "Alternate reality game elements"
                ],
                "technical_integration": "Content delivery API with interactive components"
            }
        },
        {
            "id": "business-books",
            "name": "Top 100 Business Books",
            "description": "Detailed analysis and synthesis of business literature, providing intellectual foundations for wealth building and management.",
            "status": "active",
            "connections": [
                {"target": "enlightenment-journey", "type": "child"}
            ],
            "metadata": {
                "key_features": [
                    "Curated business book collection",
                    "In-depth analysis and summaries",
                    "Expert commentary and interviews",
                    "Practical application frameworks"
                ],
                "technical_integration": "Content API with structured book data"
            }
        },
        {
            "id": "familial-trust",
            "name": "Familial Stewardship Structure",
            "description": "Governance and distribution framework for managing legacy assets based on contribution and relation.",
            "status": "planned",
            "connections": [
                {"target": "legacy-vault", "type": "child"}
            ],
            "metadata": {
                "key_features": [
                    "Relation-based profit distribution",
                    "Contribution-based incentives",
                    "Multi-generational governance",
                    "Ethical frameworks for expansion"
                ],
                "technical_integration": "Governance API with rule enforcement"
            }
        }
    ]
    
    return [ModuleResponse(**module) for module in modules]

@router.get("/module/{module_id}")
def get_hcu_module(module_id: str) -> ModuleResponse:
    """Get details for a specific HCU module
    
    This endpoint returns detailed information about a specific module
    in the Hard Card Universe ecosystem.
    """
    # This would typically fetch from a database
    # For now, we'll reuse the hardcoded module data and filter
    modules = list_hardcard_modules()
    
    for module in modules:
        if module.id == module_id:
            return module
    
    # If module not found, return 404
    raise ValueError(f"Module with ID {module_id} not found")
