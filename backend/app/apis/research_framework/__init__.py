from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import databutton as db

router = APIRouter()

# Models for the Research Framework
class ResearchTrack(BaseModel):
    id: str
    name: str
    description: str
    status: str  # "not-started", "in-progress", "completed"
    progress: float  # 0-100
    key_tools: List[str] = []
    formalism: Optional[str] = None
    related_tracks: List[str] = []
    milestones: List[Dict[str, Any]] = []

class ResearchFramework(BaseModel):
    tracks: List[ResearchTrack]
    framework_version: str
    last_updated: str

def get_default_framework() -> Dict[str, Any]:
    """
    Returns the default research framework structure with the 8 key research tracks
    for civilisation-grade mathematical assurance in the Hardcard system.
    
    This framework defines the mathematical foundation for creating a device that
    stores, communicates, and manages digital legacy for centuries, backed by
    provable mathematics instead of best-effort engineering.
    """
    
    # Define phased roadmap
    phased_roadmap = [
        {
            "name": "Phase 1",
            "timeframe": "0-18 months",
            "focus": "Formalism & toolchain development",
            "milestones": [
                "Formal specification v1 (Q3 2025)",
                "Core abstraction libraries",
                "Verification toolchain integration",
                "Initial proof-of-concepts"
            ]
        },
        {
            "name": "Phase 2",
            "timeframe": "12-36 months",
            "focus": "Core component proofs & first hardware",
            "milestones": [
                "Verified storage subsystem",
                "Secure communications protocol verification",
                "Legacy engine formal model",
                "First hardware reference implementation"
            ]
        },
        {
            "name": "Phase 3",
            "timeframe": "30-48 months",
            "focus": "Integration, full CI, governance tests",
            "milestones": [
                "End-to-end proof including HW slice",
                "Post-quantum migration demonstration",
                "Long-term governance framework",
                "Full regression-verification CI pipeline"
            ]
        }
    ]
    
    # Define key takeaways
    key_takeaways = [
        "Hardcard's credibility **hinges on maths**; anything un-proved is a liability.",
        "AI front-end must be sandboxed by a verified checker.",
        "Data immortality is active work: errors, crypto breaks, media decay demand scheduled, provable maintenance.",
        "HW verification & governance integrity are likely cost bottlenecks—budget and talent planning must start now."
    ]
    return {
        "phased_roadmap": phased_roadmap,
        "key_takeaways": key_takeaways,
        "tracks": [
            {
                "id": "unified-formalism",
                "name": "Unified Mathematical Foundation",
                "description": "Select or design a logic expressive enough for state, concurrency, time, and economics yet still verifiable. Candidates include Higher-Order Logic, Dependent Types (Lean 4), Process Algebras, and Category abstractions.",
                "status": "in-progress",
                "progress": 35.0,
                "key_tools": ["Lean 4", "Coq", "Isabelle/HOL", "Pi-calculus", "Categorical Semantics"],
                "formalism": "Higher-Order Logic",
                "related_tracks": ["system-verification", "nl-interpreter", "legacy-calculus"],
                "milestones": [
                    {
                        "name": "Formalism Selection",
                        "due_date": "2025-Q2",
                        "status": "completed"
                    },
                    {
                        "name": "Core Abstractions Definition",
                        "due_date": "2025-Q3",
                        "status": "in-progress"
                    },
                    {
                        "name": "Interface Standardization",
                        "due_date": "2025-Q4",
                        "status": "not-started"
                    },
                    {
                        "name": "Legacy Specification Translation",
                        "due_date": "2026-Q1",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "goal": "Pick (or design) a logic expressive enough for state, concurrency, time & economics yet still verifiable.",
                    "candidate_formalisms": [
                        {
                            "name": "Higher-Order Logic",
                            "strengths": ["Expressive", "Well-established", "Strong tool support"],
                            "weaknesses": ["Complex automation", "Steeper learning curve"]
                        },
                        {
                            "name": "Dependent Types (Lean 4)",
                            "strengths": ["Code extraction", "Modern tooling", "Growing community"],
                            "weaknesses": ["Evolving ecosystem", "Potentially longer proof terms"]
                        },
                        {
                            "name": "Process Algebras",
                            "strengths": ["Natural for concurrency", "Compositional reasoning"],
                            "weaknesses": ["Less expressivity for data", "Smaller verification ecosystem"]
                        },
                        {
                            "name": "Category Abstractions",
                            "strengths": ["Mathematical elegance", "Compositional", "High-level abstractions"],
                            "weaknesses": ["Abstraction gap to implementation", "Fewer verification tools"]
                        }
                    ],
                    "key_tasks": [
                        "Modular interfaces with well-defined contracts",
                        "Cross-cutting security annotations at formalism level",
                        "Translation layers for legacy specifications",
                        "Compositional verification approach"
                    ],
                    "selection_criteria": {
                        "expressivity": "Must handle state, time, concurrency, and economic models",
                        "verifiability": "Automated/interactive proof support",
                        "compositionality": "Support for modular verification",
                        "tool_support": "Mature proof assistants and libraries",
                        "learnability": "Reasonable learning curve for team"
                    }
                }
            },
            {
                "id": "system-verification",
                "name": "System-Wide Verification",
                "description": "Implement functional correctness, safety, and cryptographic security verification using Lean for interactive proofs, SMT (Z3/CVC5) for automated proofs, and model-checking where finite. Define a risk-based TCB for maximum rigor.",
                "status": "in-progress",
                "progress": 25.0,
                "key_tools": ["Lean", "Z3", "CVC5", "Model Checking", "Abstract Interpretation"],
                "formalism": "Compositional Verification",
                "related_tracks": ["unified-formalism", "hw-sw-verification", "governance"],
                "milestones": [
                    {
                        "name": "Verification Toolchain Integration",
                        "due_date": "2025-Q3",
                        "status": "in-progress"
                    },
                    {
                        "name": "Risk-based TCB Definition",
                        "due_date": "2025-Q4",
                        "status": "not-started"
                    },
                    {
                        "name": "Core Component Proofs",
                        "due_date": "2026-Q2",
                        "status": "not-started"
                    },
                    {
                        "name": "CI Integration for Regression Verification",
                        "due_date": "2026-Q3",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "scope": {
                        "functional_correctness": "Ensure implementation correctly implements specification",
                        "safety": "Prevent crashes, memory corruption, undefined behavior",
                        "cryptographic_security": "Prove security properties of cryptographic protocols"
                    },
                    "toolchain": [
                        {
                            "name": "Lean",
                            "purpose": "Interactive theorem proving for core correctness properties"
                        },
                        {
                            "name": "SMT (Z3/CVC5)",
                            "purpose": "Automated proving for decidable subproblems"
                        },
                        {
                            "name": "Model checking",
                            "purpose": "Verification of finite-state components and protocols"
                        },
                        {
                            "name": "Abstract interpretation",
                            "purpose": "Static analysis for baseline safety properties"
                        }
                    ],
                    "strategy": {
                        "risk_based_tcb": "Highest rigorous verification for boot, crypto, and legacy engine components",
                        "compositional_proofs": "Modular verification based on contracts between components",
                        "continuous_verification": "CI pipeline with proof caching; fail build if proofs break"
                    },
                    "verification_levels": [
                        {
                            "level": "L1 - Critical",
                            "components": ["Secure boot", "Crypto core", "Legacy executor"],
                            "verification": "Full formal verification, manual proof review"
                        },
                        {
                            "level": "L2 - High",
                            "components": ["Key management", "Update mechanisms", "Recovery protocols"],
                            "verification": "Formal verification with automated tools"
                        },
                        {
                            "level": "L3 - Medium",
                            "components": ["Storage subsystems", "User interfaces", "Network stack"],
                            "verification": "Property-based testing, model checking"
                        },
                        {
                            "level": "L4 - Low",
                            "components": ["Analytics", "Logging", "Non-critical UI elements"],
                            "verification": "Conventional testing, static analysis"
                        }
                    ]
                }
            },
            {
                "id": "math-interpreter",
                "name": "Math-Interpreter",
                "description": "Create a safe natural language to formal mathematics bridge for users with semantic grounding to avoid hallucinations and robust prompt-injection defenses. Implement an architecture where LLM proposals are validated by a formally-verified checker.",
                "status": "in-progress",
                "progress": 40.0,
                "key_tools": ["Large Language Models", "Formal Verification", "Semantic Parsing", "Natural Language Processing", "Proof Assistants"],
                "formalism": "LLM-to-Formal Bridge Architecture",
                "related_tracks": ["unified-formalism", "system-verification", "legacy-calculus"],
                "milestones": [
                    {
                        "name": "Math-Interpreter Architecture Specification",
                        "due_date": "2025-Q4",
                        "status": "completed"
                    },
                    {
                        "name": "Semantic Grounding Framework",
                        "due_date": "2026-Q1",
                        "status": "in-progress"
                    },
                    {
                        "name": "Formal Verification of NL Translation",
                        "due_date": "2026-Q3",
                        "status": "not-started"
                    },
                    {
                        "name": "Human-Readable Proof Explanation System",
                        "due_date": "2027-Q1",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "role": ["translate", "validate", "explain"],
                    "architecture": {
                        "layers": [
                            {
                                "name": "LLM Proposal Layer",
                                "description": "Generate candidate translations and explanations",
                                "components": ["Context management", "Prompt engineering", "Response generation"]
                            },
                            {
                                "name": "Formally-verified Checker",
                                "description": "Validate mathematical correctness of LLM outputs",
                                "components": ["Type checking", "Proof verification", "Syntax validation"]
                            },
                            {
                                "name": "Core Integration",
                                "description": "Bridge validated translations to Hardcard core systems",
                                "components": ["API integration", "Legacy rule translation", "Audit logging"]
                            }
                        ]
                    },
                    "research_areas": [
                        {
                            "name": "Semantic grounding",
                            "goal": "Ensure translations maintain semantic meaning, avoid hallucinations",
                            "approaches": ["Knowledge graphs", "Term disambiguation", "Ontology mapping"]
                        },
                        {
                            "name": "Prompt-injection defense",
                            "goal": "Prevent attacks that manipulate the translation process",
                            "approaches": ["Input sanitization", "Constraint enforcement", "Adversarial testing"]
                        },
                        {
                            "name": "NL explanation generation",
                            "goal": "Generate clear, accurate explanations of formal mathematical steps",
                            "approaches": ["Template-based generation", "Proof tree visualization", "Progressive disclosure"]
                        }
                    ],
                    "security_model": {
                        "principle": "LLM outputs are untrusted until verified",
                        "verification_pipeline": "Natural language → formal representation → verification → execution",
                        "isolation": "LLM components contained in separate security domain from verified core"
                    }
                }
            },
            {
                "id": "ultra-long-storage",
                "name": "Ultra-Long-Term Storage",
                "description": "Develop civilisation-grade permanence with targets of 1000+ years data survival with P(loss) < 10⁻¹⁵ and crypto agility. Implement regenerating codes, PQ-safe signatures, and formal maintenance loops for data preservation.",
                "status": "in-progress",
                "progress": 30.0,
                "key_tools": ["Raptor Codes", "Authenticated Data Structures", "Post-Quantum Cryptography", "Media Refresh Protocols", "Formal Maintenance Cycles"],
                "formalism": "Long-Term Data Survival Framework",
                "related_tracks": ["crypto-comms", "governance"],
                "milestones": [
                    {
                        "name": "Storage Architectural Design",
                        "due_date": "2025-Q4",
                        "status": "completed"
                    },
                    {
                        "name": "PQ-Safe Signature Selection",
                        "due_date": "2026-Q1",
                        "status": "in-progress"
                    },
                    {
                        "name": "Erasure Coding Implementation & Verification",
                        "due_date": "2026-Q3",
                        "status": "not-started"
                    },
                    {
                        "name": "Formal Maintenance Loop Verification",
                        "due_date": "2027-Q1",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "targets": {
                        "data_survival": "≥ 1000 years",
                        "loss_probability": "< 10⁻¹⁵",
                        "crypto_agility": "Ability to smoothly transition between cryptographic algorithms"
                    },
                    "mechanisms": [
                        {
                            "name": "Erasure Coding",
                            "type": "Regenerating/raptor codes",
                            "properties": ["Self-healing", "Optimal repair bandwidth", "Resilient to mass node failures"],
                            "implementation": "Fountain codes with feedback mechanism for verification"
                        },
                        {
                            "name": "Authenticated Data Structures",
                            "type": "Merkle trees with vector commitments",
                            "properties": ["Efficient verification", "Tamper evidence", "Succinct proofs"],
                            "implementation": "Hybrid approach combining hash-based and polynomial commitments"
                        },
                        {
                            "name": "PQ-Safe Signatures",
                            "type": "Dilithium and SPHINCS+",
                            "properties": ["Post-quantum security", "Conservative parameter selection", "Multiple algorithm support"],
                            "implementation": "Dual-signature approach during transition periods"
                        },
                        {
                            "name": "Key Rotation Protocol",
                            "type": "Threshold signing with time-based rotation",
                            "properties": ["No single point of failure", "Graceful key compromise recovery", "Formal verification"],
                            "implementation": "M-of-N threshold scheme with tamper-evident history"
                        }
                    ],
                    "maintenance_cycles": [
                        {
                            "name": "Data scrubbing",
                            "frequency": "Quarterly",
                            "description": "Verify integrity and repair corruptions using redundant data"
                        },
                        {
                            "name": "Media refresh",
                            "frequency": "Biennial",
                            "description": "Copy data to fresh media before degradation reaches critical levels"
                        },
                        {
                            "name": "Format migration",
                            "frequency": "Decennial",
                            "description": "Convert data to new formats as standards evolve"
                        },
                        {
                            "name": "Cryptographic refresh",
                            "frequency": "As needed (at least once per decade)",
                            "description": "Re-sign and re-encrypt data with new algorithms before existing ones are compromised"
                        }
                    ],
                    "formal_properties": [
                        "All maintenance operations provably preserve integrity",
                        "Recovery possible with any k of n shards available",
                        "System remains secure even if signature scheme is broken, assuming replacement within window"
                    ]
                }
            },
            {
                "id": "crypto-comms",
                "name": "Verified Comms",
                "description": "Design secure communication protocols for device-to-device clustering, device-to-user control, and minimal external oracle gateways. Use formal methods like CSP/Pi-calculus with ProVerif and Tamarin to prove confidentiality, integrity, and other security properties.",
                "status": "in-progress",
                "progress": 20.0,
                "key_tools": ["ProVerif", "Tamarin", "CSP", "Pi-calculus", "Protocol Verification"],
                "formalism": "Communicating Sequential Processes (CSP)",
                "related_tracks": ["ultra-long-storage", "hw-sw-verification", "system-verification"],
                "milestones": [
                    {
                        "name": "Communication Protocol Specification",
                        "due_date": "2026-Q1",
                        "status": "in-progress"
                    },
                    {
                        "name": "Formal Properties Definition",
                        "due_date": "2026-Q2",
                        "status": "not-started"
                    },
                    {
                        "name": "Protocol Verification",
                        "due_date": "2026-Q4",
                        "status": "not-started"
                    },
                    {
                        "name": "Cross-Protocol Composition Proofs",
                        "due_date": "2027-Q2",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "protocols": [
                        {
                            "name": "Device-to-device clustering",
                            "purpose": "Establish secure communication and coordination between multiple Hardcard devices",
                            "properties": ["Mutual authentication", "Byzantine fault tolerance", "Dynamic membership"],
                            "verification_tool": "Tamarin"
                        },
                        {
                            "name": "Device-to-user control",
                            "purpose": "Secure interface between users and their Hardcard devices",
                            "properties": ["User authentication", "Authorization enforcement", "Usable security"],
                            "verification_tool": "ProVerif"
                        },
                        {
                            "name": "External oracle gateway",
                            "purpose": "Minimal, secure interface to external data sources and services",
                            "properties": ["Data validation", "Source authentication", "Strict access control"],
                            "verification_tool": "CSP/FDR"
                        }
                    ],
                    "formalisms_and_tools": [
                        {
                            "name": "CSP / Pi-calculus",
                            "application": "Formal modeling of protocol message flows and process interactions"
                        },
                        {
                            "name": "ProVerif",
                            "application": "Automated symbolic verification of security protocols"
                        },
                        {
                            "name": "Tamarin",
                            "application": "Verification of protocols with complex state machines and equational theories"
                        },
                        {
                            "name": "FDR",
                            "application": "Refinement checking for CSP models"
                        }
                    ],
                    "properties_to_prove": [
                        {
                            "name": "Confidentiality",
                            "description": "Sensitive data remains secret from unauthorized parties"
                        },
                        {
                            "name": "Integrity",
                            "description": "Messages cannot be tampered with without detection"
                        },
                        {
                            "name": "Forward secrecy",
                            "description": "Compromise of long-term keys does not compromise past session keys"
                        },
                        {
                            "name": "Replay resistance",
                            "description": "Captured valid messages cannot be reused in another context"
                        },
                        {
                            "name": "Identity binding",
                            "description": "Actions are provably linked to authenticated identities"
                        }
                    ],
                    "composition": {
                        "approach": "Embed protocol proofs into the global formal model",
                        "benefits": "Avoid cross-protocol attack vulnerabilities",
                        "challenges": "Integration of different formal methods and verification tools",
                        "strategy": "Abstract protocol guarantees into invariants for the global model"
                    }
                }
            },
            {
                "id": "legacy-calculus",
                "name": "Legacy Calculus",
                "description": "Create a temporal logic with rich state predicates to model legacy management rules with formal operational semantics. Ensure rule consistency, termination, and asset-transfer correctness with mechanisms for resolving ambiguity.",
                "status": "in-progress",
                "progress": 45.0,
                "key_tools": ["Temporal Logic (LTL/CTL*)", "State Predicates", "Declarative Rules", "Guardian Quorum Logic", "Dispute Resolution Framework"],
                "formalism": "Temporal Logic (LTL) with State Predicates",
                "related_tracks": ["unified-formalism", "math-interpreter", "governance"],
                "milestones": [
                    {
                        "name": "Legacy Calculus Language Definition",
                        "due_date": "2026-Q2",
                        "status": "completed"
                    },
                    {
                        "name": "Formal Operational Semantics",
                        "due_date": "2026-Q3",
                        "status": "in-progress"
                    },
                    {
                        "name": "Rule Consistency & Termination Proofs",
                        "due_date": "2027-Q1",
                        "status": "not-started"
                    },
                    {
                        "name": "Dispute Resolution Implementation",
                        "due_date": "2027-Q3",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "language_requirements": {
                        "temporal_constructs": "Express conditions and actions over time periods",
                        "rich_state_predicates": "Complex conditions on system and asset states",
                        "declarative_syntax": "Rules expressed as logical statements, not procedures",
                        "formal_semantics": "Precise mathematical meaning for all constructs"
                    },
                    "language_features": [
                        {
                            "name": "Temporal operators",
                            "examples": ["always", "eventually", "until", "before", "after"],
                            "purpose": "Express conditions and effects across time"
                        },
                        {
                            "name": "Asset transfer directives",
                            "examples": ["allocate", "distribute", "vest", "restrict"],
                            "purpose": "Specify asset movement between entities"
                        },
                        {
                            "name": "Conditional clauses",
                            "examples": ["when", "unless", "if_all", "if_any"],
                            "purpose": "Define triggering conditions for rules"
                        },
                        {
                            "name": "Entity quantifiers",
                            "examples": ["for_all", "exists", "exactly_n"],
                            "purpose": "Express conditions across groups of entities"
                        }
                    ],
                    "guarantees": [
                        {
                            "name": "Rule consistency",
                            "verification": "Static analysis to detect contradictory rules",
                            "importance": "Prevents impossible or ambiguous states"
                        },
                        {
                            "name": "Termination",
                            "verification": "Proof that rule execution always reaches final state",
                            "importance": "Ensures no infinite loops or deadlocks"
                        },
                        {
                            "name": "Asset-transfer correctness",
                            "verification": "Conservation of value, authorization rules, temporal constraints",
                            "importance": "Maintains system integrity and trustworthiness"
                        }
                    ],
                    "ambiguity_controls": [
                        {
                            "mechanism": "Underspecification hooks",
                            "purpose": "Explicit identification of areas requiring human judgment"
                        },
                        {
                            "mechanism": "Dispute resolution clauses",
                            "purpose": "Formalized processes for resolving interpretation conflicts"
                        },
                        {
                            "mechanism": "Guardian quorum logic",
                            "purpose": "Rules for multi-party decision making when automation is insufficient"
                        }
                    ]
                }
            },
            {
                "id": "hw-sw-verification",
                "name": "Hardware + Software Co-Verification",
                "description": "Specify and verify hardware interfaces (ISA, MMU, crypto engines, secure elements) and prove software correctness against these specifications. Focus on critical blocks like boot ROM and crypto first.",
                "status": "not-started",
                "progress": 0.0,
                "key_tools": ["Model Checking", "Equivalence Checking", "OS Verification", "Side-Channel Mitigation"],
                "formalism": "Hardware-Software Interface Models",
                "related_tracks": ["unified-formalism", "system-verification", "governance"],
                "milestones": [
                    {
                        "name": "Interface Specification",
                        "due_date": "2026-Q2",
                        "status": "not-started"
                    },
                    {
                        "name": "RTL-Spec Verification (Critical Blocks)",
                        "due_date": "2026-Q3",
                        "status": "not-started"
                    },
                    {
                        "name": "OS Driver Verification",
                        "due_date": "2026-Q4",
                        "status": "not-started"
                    },
                    {
                        "name": "Side-Channel Mitigation Modeling",
                        "due_date": "2027-Q1",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "interface_specifications": [
                        {
                            "name": "ISA (Instruction Set Architecture)",
                            "formalization": "Formal semantics for each instruction",
                            "verification": "Prove processor implementation matches ISA specification"
                        },
                        {
                            "name": "MMU (Memory Management Unit)",
                            "formalization": "Address translation and protection model",
                            "verification": "Prove isolation and permission enforcement properties"
                        },
                        {
                            "name": "Crypto engines",
                            "formalization": "Functional behavior and side-channel characteristics",
                            "verification": "Prove functional correctness and resistance to specified attacks"
                        },
                        {
                            "name": "Secure elements",
                            "formalization": "Key management and secure storage properties",
                            "verification": "Prove tamper resistance and non-extractability guarantees"
                        }
                    ],
                    "verification_plan": [
                        {
                            "step": "RTL ↔ spec equivalence",
                            "methods": ["Model checking", "Equivalence checking"],
                            "tools": ["JasperGold", "Questa Formal", "CoSA"]
                        },
                        {
                            "step": "OS/driver correctness against HW spec",
                            "methods": ["Assume-guarantee reasoning", "Refinement checking"],
                            "tools": ["seL4 verification framework", "CertiKOS", "Custom Lean proofs"]
                        },
                        {
                            "step": "Side-channel mitigation modeling",
                            "methods": ["Information flow analysis", "Constant-time verification"],
                            "tools": ["ct-verif", "FlowTracker", "Custom formal models"]
                        }
                    ],
                    "priority_blocks": [
                        {
                            "name": "Boot ROM",
                            "criticality": "Highest",
                            "justification": "Root of trust for entire system",
                            "verification_depth": "Full formal verification, including side-channels"
                        },
                        {
                            "name": "Crypto blocks",
                            "criticality": "Highest",
                            "justification": "Security foundation for all operations",
                            "verification_depth": "Full formal verification, including side-channels"
                        },
                        {
                            "name": "Memory protection",
                            "criticality": "High",
                            "justification": "Enforces isolation between components",
                            "verification_depth": "Full functional verification"
                        },
                        {
                            "name": "I/O controllers",
                            "criticality": "Medium",
                            "justification": "External attack surface",
                            "verification_depth": "Interface verification, security properties"
                        }
                    ],
                    "reality_check": {
                        "constraints": "Start with critical blocks (boot ROM, crypto) and expand incrementally",
                        "documentation": "Clearly document abstraction boundaries and assumptions",
                        "verification_gaps": "Identify areas where full verification is not feasible",
                        "mitigation": "Use defense-in-depth where full verification is impractical"
                    }
                }
            },
            {
                "id": "governance",
                "name": "Governance & Evolution",
                "description": "Develop a framework for balancing immutable proofs with inevitable change through layered trust: immutable core invariants, formally-verified update protocol, and governance logic with threshold voting and audited history.",
                "status": "in-progress",
                "progress": 15.0,
                "key_tools": ["Layered Trust Architecture", "Threshold Voting", "Formal Update Protocol", "Audited History"],
                "formalism": "Layered Trust Model",
                "related_tracks": ["unified-formalism", "system-verification", "hw-sw-verification"],
                "milestones": [
                    {
                        "name": "Layered Trust Architecture Design",
                        "due_date": "2026-Q4",
                        "status": "in-progress"
                    },
                    {
                        "name": "Formal Update Protocol Specification",
                        "due_date": "2027-Q1",
                        "status": "not-started"
                    },
                    {
                        "name": "Governance Logic Implementation",
                        "due_date": "2027-Q2",
                        "status": "not-started"
                    },
                    {
                        "name": "Cryptographic Agility Drills",
                        "due_date": "2027-Q4",
                        "status": "not-started"
                    }
                ],
                "detailed_implementation": {
                    "secure_update_mechanisms": {
                        "objective": "Formally specify, implement and verify an over-the-air (OTA) update protocol that guarantees authenticity, integrity, freshness, atomicity and rollback protection, anchored in secure-boot.",
                        "formal_model": {
                            "protocol_flow_manifests": "Lean 4 state machines or Isabelle/HOL",
                            "cryptographic_hand_shake": "Tamarin / ProVerif models",
                            "state_and_atomicity": "Event-B refinements to Lean implementation"
                        },
                        "properties_to_prove": [
                            "Authenticity & integrity – only vendor-signed artefacts install",
                            "Freshness – version N + 1 prevents downgrade to ≤ N",
                            "Atomicity – commit or rollback, never partial",
                            "Confidentiality – (optional) encrypted payloads"
                        ],
                        "implementation_path": [
                            "Lean verified client ↠ direct compilation",
                            "Verified build/signing pipeline",
                            "Integration test on secure-boot board; prove root-of-trust chain unbroken"
                        ],
                        "metrics": {
                            "proof_build_time": "< 5 min/module",
                            "update_failure_rate": "< 10⁻⁶ per device-year"
                        }
                    },
                    "regression_verification_pipelines": {
                        "objective": "CI/CD jobs that re-check only the proofs impacted by a code change, blocking merges on failure.",
                        "architecture": {
                            "trigger": "nightly (alt: per-commit for small modules)",
                            "selection": "dep-graph (Lean lake + custom slicer)",
                            "tools": [
                                {
                                    "solver": "Z3",
                                    "invariant_tool": "IC3Synth"
                                }
                            ],
                            "thresholds": {
                                "proof_time_sec": 300,
                                "manual_fixes": 5
                            },
                            "dashboard": "proofHealth"
                        },
                        "pipeline_steps": [
                            "Delta analysis via Lean dependency graph",
                            "Generate VCs → Z3/CVC5",
                            "Attempt auto-repair (LLM-guided) if proof fails",
                            "Post results to Grafana dashboard; Slack alert if thresholds breached"
                        ]
                    },
                    "proof_maintenance_infrastructure": {
                        "objective": "Prevent 'proof rot' as the codebase evolves.",
                        "practices": [
                            {
                                "name": "Modular Lean design",
                                "description": "Type-classes + namespaces = localised proofs"
                            },
                            {
                                "name": "Style guide & lint",
                                "description": "Enforce readable structured proofs (Isar-style)"
                            },
                            {
                                "name": "Dependency visualiser",
                                "description": "lake-json → D3 graph"
                            },
                            {
                                "name": "Automated refactor/repair",
                                "description": "metaprogram tactics + LLM PRISM model"
                            }
                        ],
                        "metrics": {
                            "avg_proof_check_time": "> 500 ms",
                            "broken_proofs_per_sprint": "> 5",
                            "dependency_depth": "> 10 levels"
                        },
                        "audit": "Quarterly Proof Audit revisits hotspots & schedules refactors"
                    },
                    "cryptographic_agility_framework": {
                        "objective": "Swap algorithms (e.g., ECDSA → ML-DSA) or keys without violating proofs.",
                        "components": [
                            {
                                "name": "Crypto Inventory",
                                "format": "YAML/JSON",
                                "description": "Records algorithm, key size, lifespan, and status information"
                            },
                            {
                                "name": "CryptoLayer abstraction",
                                "language": "Lean",
                                "description": "Type-class that defines core cryptographic operations",
                                "code_sample": "class CryptoLayer (σ : Type) :=\n  (sign      : σ → ByteString → Signature)\n  (verify    : σ → ByteString → Signature → Prop)\n  (encrypt   : σ → ByteString → ByteString)\n  (decrypt   : σ → ByteString → Option ByteString)\n  -- ∀ m, decrypt k (encrypt k m) = some m ∧ verify k m (sign k m)",
                                "properties": "Each concrete impl proven to satisfy CryptoLayer"
                            },
                            {
                                "name": "Verified modules",
                                "description": "Each implementation (HACL*, PQC candidate) with proofs of correctness",
                                "verification": "Formal proof that implementation satisfies CryptoLayer"
                            },
                            {
                                "name": "Key-rotation & algorithm-migration protocols",
                                "description": "Secure processes for updating cryptographic components",
                                "verification": "Lean proofs + Tamarin for handshake security"
                            }
                        ],
                        "roadmap": {
                            "inventory_complete": {
                                "date": "Q2 2025",
                                "notes": "Including PQC options"
                            },
                            "crypto_layer_spec_stable": {
                                "date": "Q3 2025",
                                "notes": "Code ⇄ spec round-tripped"
                            },
                            "first_pq_algorithm_in_prod": {
                                "date": "Q4 2025",
                                "notes": "ML-KEM-768 dual-run"
                            }
                        }
                    },
                    "next_steps": [
                        "Adopt doc as canonical Section 2.7 in Master Plan",
                        "Stand-up proof-health dashboard (Grafana + Prometheus)",
                        "Prototype update-client model → Lean proof of authenticity",
                        "Finish CryptoLayer skeleton + ECDSA module proof",
                        "Schedule first Proof Audit (end of next sprint)"
                    ]
                }
            }
        ],
        "framework_version": "1.0",
        "last_updated": "2025-04-19"
    }

@router.get("/framework")
async def get_research_framework():
    """Get the current research framework with all tracks, phased roadmap, and key takeaways.
    
    The research framework defines the eight research tracks that must converge to build
    a civilisation-grade device that stores, communicates and manages digital legacy for
    centuries, backed by provable maths instead of best-effort engineering.
    
    This includes detailed implementations for all tracks, with special focus on Section 2.7's
    governance and cryptographic agility framework, covering secure update mechanisms,
    regression-verification pipelines, proof-maintenance infrastructure, and the cryptographic
    agility framework designed for long-term evolution of the system.
    """
    try:
        # Try to load the saved framework first
        framework = db.storage.json.get("research_framework", default=None)
        if not framework:
            # If no saved framework exists, return the default
            framework = get_default_framework()
        return framework
    except Exception as err:
        print(f"Error getting research framework: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@router.post("/research/framework/update")
def update_research_framework(framework: dict):
    """Update the entire research framework with new data."""
    try:
        db.storage.json.put("research_framework", framework)
        return {"status": "success", "message": "Research framework updated successfully"}
    except Exception as err:
        print(f"Error updating research framework: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@router.post("/research/track/{track_id}/update")
def update_research_track_status(track_id: str, status: str, progress: float):
    """Update the status and progress of a specific research track.
    
    Args:
        track_id: Unique identifier of the track to update
        status: New status (not-started, in-progress, or completed)
        progress: New progress percentage (0-100)
        
    Returns:
        Updated track information
    """
    try:
        # Load current framework
        framework = db.storage.json.get("research_framework", default=get_default_framework())
        
        # Find and update the track
        track_updated = False
        for track in framework["tracks"]:
            if track["id"] == track_id:
                track["status"] = status
                track["progress"] = progress
                track_updated = True
                break
        
        if not track_updated:
            raise HTTPException(status_code=404, detail=f"Track with ID {track_id} not found")
        
        # Save the updated framework
        db.storage.json.put("research_framework", framework)
        
        # Return the updated track
        updated_track = next((t for t in framework["tracks"] if t["id"] == track_id), None)
        return updated_track
    except HTTPException:
        raise
    except Exception as err:
        print(f"Error updating track status: {err}")
        raise HTTPException(status_code=500, detail=str(err))
