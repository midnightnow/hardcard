from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
# No need for import databutton here yet

router = APIRouter()


class HardwareComponent(BaseModel):
    id: str
    name: str
    description: str
    verification_status: str  # "verified", "in_progress", "planned"
    formal_properties: List[str]
    interfaces: List[str]  # IDs of interfaces this component exposes


class SoftwareComponent(BaseModel):
    id: str
    name: str
    description: str
    verification_status: str
    formal_properties: List[str]
    interfaces: List[str]  # IDs of interfaces this component uses
    language: str
    verification_approach: str


class Interface(BaseModel):
    id: str
    name: str
    description: str
    type: str  # "hw_to_sw", "sw_to_hw", "sw_to_sw", "hw_to_hw"
    verification_status: str
    formal_specification: str
    properties: List[str]


class VerificationResult(BaseModel):
    interface_id: str
    status: str
    proof_summary: str
    assumptions: List[str]
    constraints: List[Dict[str, str]]


class HardwareSwInterfaceResponse(BaseModel):
    hardware_components: List[HardwareComponent]
    software_components: List[SoftwareComponent]
    interfaces: List[Interface]
    verification_results: List[VerificationResult]
    verification_summary: Dict[str, Union[str, int]]


@router.get("/hw-sw-interface")
def get_hardcard_hardware_software_interface() -> HardwareSwInterfaceResponse:
    """
    Retrieve the formal specification of the hardware-software interface for the Hardcard system.
    This includes hardware components, software components, their interfaces,
    and verification results that ensure the correctness of their interaction.
    """
    # Define the hardware components
    hardware_components = [
        HardwareComponent(
            id="secure_element",
            name="Secure Element",
            description="Hardware-isolated cryptographic processor with secure key storage",
            verification_status="verified",
            formal_properties=[
                "Isolation from main processor",
                "Side-channel attack resistance",
                "Tamper-evidence mechanisms"
            ],
            interfaces=["crypto_ops_interface", "secure_storage_interface"]
        ),
        HardwareComponent(
            id="energy_harvesting",
            name="Energy Harvesting System",
            description="Passive energy collection from RF and light sources",
            verification_status="in_progress",
            formal_properties=[
                "Power stability under variable conditions",
                "Minimum energy throughput guarantees"
            ],
            interfaces=["power_management_interface"]
        ),
        HardwareComponent(
            id="storage_array",
            name="Permanent Storage Array",
            description="Ultra-long-term data storage using specialized materials",
            verification_status="verified",
            formal_properties=[
                "Data retention >100 years",
                "Error correction capabilities",
                "Read-only after initialization"
            ],
            interfaces=["storage_access_interface"]
        ),
        HardwareComponent(
            id="qr_matrix",
            name="Visual QR Matrix",
            description="Physical QR code embedded in card structure for optical recovery",
            verification_status="verified",
            formal_properties=[
                "Optical readability under various lighting",
                "Redundant encoding for damage resistance"
            ],
            interfaces=["recovery_interface"]
        ),
        HardwareComponent(
            id="microcontroller",
            name="Low-Power Microcontroller",
            description="Central processing unit controlling card operations",
            verification_status="in_progress",
            formal_properties=[
                "Defined instruction set semantics",
                "Memory protection",
                "Secure boot process"
            ],
            interfaces=["system_control_interface", "crypto_ops_interface", "storage_access_interface"]
        )
    ]

    # Define the software components
    software_components = [
        SoftwareComponent(
            id="firmware_core",
            name="Firmware Core",
            description="Minimal trusted software handling core card operations",
            verification_status="verified",
            formal_properties=[
                "Memory safety",
                "Control flow integrity",
                "Information flow control"
            ],
            interfaces=["system_control_interface"],
            language="Rust & formally verified assembly",
            verification_approach="Deductive verification with F*"
        ),
        SoftwareComponent(
            id="crypto_module",
            name="Cryptographic Module",
            description="Handles all cryptographic operations including signatures and verification",
            verification_status="verified",
            formal_properties=[
                "Constant-time operations",
                "Formal correspondence to cryptographic specifications",
                "Side-channel resistance"
            ],
            interfaces=["crypto_ops_interface"],
            language="Rust with HACL* verified primitives",
            verification_approach="Model checking & symbolic execution"
        ),
        SoftwareComponent(
            id="storage_manager",
            name="Storage Manager",
            description="Manages access to long-term storage with integrity checks",
            verification_status="in_progress",
            formal_properties=[
                "Atomic write operations",
                "Data integrity verification",
                "Hierarchical access control"
            ],
            interfaces=["storage_access_interface"],
            language="Rust",
            verification_approach="Interactive theorem proving with Coq"
        ),
        SoftwareComponent(
            id="legacy_executor",
            name="Legacy Rule Executor",
            description="Evaluates and executes legacy rules when conditions are met",
            verification_status="planned",
            formal_properties=[
                "Rule evaluation correctness",
                "Temporal consistency",
                "Deadlock freedom"
            ],
            interfaces=["system_control_interface", "crypto_ops_interface", "storage_access_interface"],
            language="Rust with custom DSL",
            verification_approach="Temporal logic model checking"
        ),
        SoftwareComponent(
            id="recovery_module",
            name="Recovery Module",
            description="Handles data recovery protocols and key reconstruction",
            verification_status="in_progress",
            formal_properties=[
                "Information-theoretic security properties",
                "Threshold recovery guarantees",
                "Forward secrecy"
            ],
            interfaces=["recovery_interface", "crypto_ops_interface"],
            language="Rust",
            verification_approach="Protocol verification with Tamarin"
        )
    ]

    # Define the interfaces between components
    interfaces = [
        Interface(
            id="crypto_ops_interface",
            name="Cryptographic Operations Interface",
            description="Interface for secure cryptographic operations between hardware secure element and software",
            type="hw_to_sw",
            verification_status="verified",
            formal_specification="Formally defined with state transitions and invariants in F*",
            properties=[
                "Non-extractability of key material",
                "Complete mediation of all crypto operations",
                "Audit logging of sensitive operations"
            ]
        ),
        Interface(
            id="secure_storage_interface",
            name="Secure Storage Interface",
            description="Interface for accessing key storage in the secure element",
            type="hw_to_sw",
            verification_status="verified",
            formal_specification="Access control model formalized in Coq",
            properties=[
                "Hierarchical access control",
                "Monotonic counters for freshness",
                "Tamper-evident logging"
            ]
        ),
        Interface(
            id="power_management_interface",
            name="Power Management Interface",
            description="Interface between energy harvesting system and microcontroller",
            type="hw_to_hw",
            verification_status="in_progress",
            formal_specification="Timed automata model of power states and transitions",
            properties=[
                "Graceful degradation under low power",
                "Prioritization of critical operations",
                "Safe state persistence across power cycles"
            ]
        ),
        Interface(
            id="storage_access_interface",
            name="Storage Access Interface",
            description="Interface for reading from and writing to the permanent storage array",
            type="hw_to_sw",
            verification_status="in_progress",
            formal_specification="I/O automata with failure models",
            properties=[
                "Atomic write guarantees",
                "Wear leveling",
                "Error detection and correction"
            ]
        ),
        Interface(
            id="recovery_interface",
            name="Recovery Interface",
            description="Interface for external data recovery operations",
            type="hw_to_sw",
            verification_status="verified",
            formal_specification="Zero-knowledge protocol formalized in the applied pi calculus",
            properties=[
                "Authentication of recovery attempts",
                "Rate limiting and progressive difficulty",
                "Partial recovery capabilities"
            ]
        ),
        Interface(
            id="system_control_interface",
            name="System Control Interface",
            description="Core interface between firmware and microcontroller hardware",
            type="hw_to_sw",
            verification_status="verified",
            formal_specification="ISA-level formal semantics with security annotations",
            properties=[
                "Memory protection enforcement",
                "Privilege separation",
                "Secure interrupt handling"
            ]
        )
    ]

    # Define the verification results
    verification_results = [
        VerificationResult(
            interface_id="crypto_ops_interface",
            status="complete",
            proof_summary="Formal verification of all security properties using F* and ProVerif",
            assumptions=[
                "Physical side-channel protection is adequate",
                "Hardware RNG meets entropy requirements"
            ],
            constraints=[
                {"name": "Maximum key usage", "value": "10,000 operations per key"}
            ]
        ),
        VerificationResult(
            interface_id="secure_storage_interface",
            status="complete",
            proof_summary="Access control policy proven with Coq, implementation verified with symbolic execution",
            assumptions=[
                "Secure element maintains integrity under specified physical attacks"
            ],
            constraints=[
                {"name": "Maximum credentials", "value": "32 per domain"}
            ]
        ),
        VerificationResult(
            interface_id="power_management_interface",
            status="in_progress",
            proof_summary="Timing and resource models verified, physical testing ongoing",
            assumptions=[
                "Minimum ambient energy availability",
                "Maximum operational temperature range" 
            ],
            constraints=[
                {"name": "Power transition latency", "value": "< 500μs"}
            ]
        ),
        VerificationResult(
            interface_id="storage_access_interface",
            status="in_progress",
            proof_summary="Atomicity properties proven, wear-leveling algorithm verification in progress",
            assumptions=[
                "Storage cells meet minimum retention specifications"
            ],
            constraints=[
                {"name": "Write cycle limit", "value": "100 per sector before reallocation"}
            ]
        ),
        VerificationResult(
            interface_id="recovery_interface",
            status="complete",
            proof_summary="Zero-knowledge properties formally verified with CryptoVerif",
            assumptions=[
                "Visual scanning hardware meets minimum resolution requirements"
            ],
            constraints=[
                {"name": "Recovery attempts", "value": "Maximum 3 per 24h period"}
            ]
        ),
        VerificationResult(
            interface_id="system_control_interface",
            status="complete",
            proof_summary="ISA model formally verified, implementation correspondence proven via binary analysis",
            assumptions=[
                "Compiler correctly implements verified transformations"
            ],
            constraints=[
                {"name": "Interrupt latency", "value": "< 100μs for critical events"}
            ]
        )
    ]

    # Create the summary statistics
    total_interfaces = len(interfaces)
    verified_interfaces = sum(1 for i in interfaces if i.verification_status == "verified")
    in_progress_interfaces = sum(1 for i in interfaces if i.verification_status == "in_progress")
    planned_interfaces = sum(1 for i in interfaces if i.verification_status == "planned")
    
    verification_summary = {
        "total_components": len(hardware_components) + len(software_components),
        "total_interfaces": total_interfaces,
        "verified_interfaces": verified_interfaces,
        "verification_coverage": f"{(verified_interfaces / total_interfaces) * 100:.1f}%",
        "in_progress": in_progress_interfaces,
        "planned": planned_interfaces,
        "tcb_size": "4,327 SLOC",
        "verification_status": "Phase 2 of 3"
    }
    
    return HardwareSwInterfaceResponse(
        hardware_components=hardware_components,
        software_components=software_components,
        interfaces=interfaces,
        verification_results=verification_results,
        verification_summary=verification_summary
    )
