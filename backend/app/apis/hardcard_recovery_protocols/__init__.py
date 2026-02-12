from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict

router = APIRouter()

class RecoveryStep(BaseModel):
    step_number: int
    description: str
    time_estimate: str

class RecoveryProtocol(BaseModel):
    protocol_name: str
    activation_method: str
    recovery_steps: List[str]
    estimated_recovery_time: str
    required_tools: List[str]
    success_indicators: List[str]
    technological_level: str
    energy_source: str
    data_recovery_percentage: str
    card_integrity: str
    smartphone_compatibility: Optional[str] = None
    smartphone_instructions: Optional[List[str]] = None

class SmartphoneMethod(BaseModel):
    device_compatibility: List[str]
    app_requirements: Optional[str] = None
    connection_type: str
    power_delivery: str
    data_transfer_protocol: str
    initialization_steps: List[str]
    security_considerations: List[str]
    biometric_sensors: Optional[List[str]] = None
    form_factors: Optional[List[str]] = None

class HardcardRecoveryProtocolsResponse(BaseModel):
    primary_protocol: RecoveryProtocol
    alternate_protocols: List[RecoveryProtocol]
    emergency_recovery: RecoveryProtocol
    protocol_comparison: Optional[dict] = None
    smartphone_methods: Optional[List[SmartphoneMethod]] = None
    backup_mechanisms: Optional[Dict[str, str]] = None

@router.get("/hardcard/recovery-protocols")
def get_hardcard_recovery_protocols_detailed() -> HardcardRecoveryProtocolsResponse:
    """Retrieve detailed recovery protocols for the Civilization-Grade Hardcard."""
    
    # Define smartphone integration methods for the hardcard
    smartphone_methods = [
        SmartphoneMethod(
            device_compatibility=["iPhone 13 or later", "Samsung Galaxy S21 or later", "Google Pixel 6 or later"],
            app_requirements="Legacy Vault Companion App (available on App Store/Google Play)",
            connection_type="NFC with fallback to camera-based QR recognition",
            power_delivery="Wireless power transfer (Qi standard) with adaptive power regulation",
            data_transfer_protocol="Encrypted Bluetooth Low Energy with secondary optical verification",
            initialization_steps=[
                "Place Hardcard on flat surface with primary interface facing up",
                "Open Legacy Vault Companion App and select 'Connect to Hardcard'",
                "Place phone directly on Hardcard, centered over the NFC receptor area",
                "Maintain position for 5-8 seconds until confirmation tone",
                "Follow on-screen instructions for authentication sequence"
            ],
            security_considerations=[
                "Biometric authentication (FaceID/fingerprint) required on smartphone",
                "Geographic position verification may be required for high-security operations",
                "Connection is limited to 10 minutes before requiring re-authentication",
                "All data transfers are end-to-end encrypted with quantum-resistant algorithms"
            ],
            biometric_sensors=[
                "Facial recognition via front camera", 
                "Fingerprint via under-display sensor",
                "Voice pattern recognition via microphone array"
            ],
            form_factors=["Standard smartphone", "Credit card attachment", "Integrated smartwatch module"]
        ),
        SmartphoneMethod(
            device_compatibility=["Any smartphone with camera (reduced functionality)"],
            connection_type="Optical recognition via smartphone camera",
            power_delivery="No direct power transfer - passive optical scanning only",
            data_transfer_protocol="One-way visual encoding with multi-frame authentication",
            initialization_steps=[
                "Position Hardcard under bright, even lighting",
                "Open Legacy Vault Companion App or web interface via secure browser",
                "Position camera 20cm above Hardcard, ensuring all edges are visible",
                "Use app's stabilization guide to maintain optimal scanning position",
                "Perform slow 360° rotation of camera around card while maintaining distance"
            ],
            security_considerations=[
                "Limited data access - only public recovery instructions accessible",
                "No access to secured storage compartments or advanced functions",
                "Verification checksums prevent tampering or counterfeit cards",
                "Optical scanning creates temporary access token valid for 1 hour"
            ],
            form_factors=["Standard smartphone"]
        ),
        SmartphoneMethod(
            device_compatibility=["iPhone 15 Pro or later", "High-end Android with UWB"],
            app_requirements="Legacy Vault Pro with Biometric Enhancement Module",
            connection_type="Ultra-wideband spatial positioning with multi-point contact",
            power_delivery="Bi-directional power sharing with dynamic load balancing",
            data_transfer_protocol="Spatial mesh networking with distributed validation",
            initialization_steps=[
                "Insert special Legacy earbuds paired with iPhone",
                "Place iPhone in direct contact with Hardcard's primary interface",
                "Complete biometric validation sequence through earbuds sensors",
                "Maintain connection while spatial mesh is established (30-45 seconds)",
                "Follow interlinked guidance through earbuds audio and iPhone display"
            ],
            security_considerations=[
                "Multi-factor biometric authentication through specialized earbuds",
                "Continuous vitality verification ensures authorized user presence",
                "Spatial positioning confirms physical proximity to authorized locations",
                "Neurological pattern matching prevents unauthorized access attempts"
            ],
            biometric_sensors=[
                "In-ear EEG via specialized earbuds",
                "ECG via conductive surfaces on device and earbuds",
                "Micro-movement detection via spatial positioning sensors",
                "Pupillary response via front camera with iris tracking"
            ],
            form_factors=["Specialized earbuds", "AR glasses", "Standard smartphone"]
        )
    ]
    
    return HardcardRecoveryProtocolsResponse(
        backup_mechanisms={
            "physical_backup": "Durable crystalline storage matrix that remains viable even if the outer card is damaged",
            "digital_redundancy": "Multiple encrypted cloud backups synced at each authorized access",
            "distributed_storage": "Key data fragments stored across multiple family Legacy Vaults",
            "temporal_snapshots": "Automated versioning system stores key state changes with easy rollback",
            "quantum_resistant_encryption": "Forward-secure encryption protecting against future quantum attacks",
            "biometric_recovery": "Family biometric signatures can initiate emergency restoration protocols"
        },
        primary_protocol=RecoveryProtocol(
            protocol_name="Standard Illumination Protocol",
            activation_method="Expose solar collection surface to natural sunlight for minimum 30 minutes",
            recovery_steps=[
                "Place card on flat, clean surface with front side up",
                "Expose to direct sunlight for initial power generation (30-60 minutes)",
                "Observe activation pattern appearing on central display matrix",
                "When central pattern fully illuminates, apply gentle pressure to the center point",
                "Follow the sequential instructions displayed via holographic projection",
                "Connect to provided interface device or utilize the integrated projection system",
                "Authenticate using provided biometric key or cryptographic sequence",
                "Begin systematic data extraction and Legacy Vault reconstruction"
            ],
            estimated_recovery_time="6-12 hours for complete system recovery",
            required_tools=[
                "Natural sunlight or equivalent full-spectrum light source (5000K+)", 
                "Basic computing device for interaction (optional, not required)",
                "Clean environment free from extreme electromagnetic interference", 
                "Standard optical magnification device (10-100x) for verification steps"
            ],
            success_indicators=[
                "Holographic projection stabilizes and expands to full interactive display",
                "Sequential confirmation tones at 440Hz, 880Hz, and 1760Hz frequencies", 
                "Digital handshake with reconstruction system (visible data flow indicators)",
                "Self-verification of recovered data integrity with checksum confirmation"
            ],
            technological_level="Minimal",
            energy_source="Solar",
            data_recovery_percentage="100%",
            card_integrity="Fully Preserved",
            smartphone_compatibility="High - Compatible with all smartphone methods",
            smartphone_instructions=[
                "Use smartphone flashlight as alternative light source",
                "Follow app guidance for optimal positioning and illumination pattern",
                "Use camera for real-time feedback on activation progress"
            ]
        ),
        alternate_protocols=[
            RecoveryProtocol(
                protocol_name="Kinetic Activation Protocol",
                activation_method="Apply specific rhythmic tapping sequence to activate energy harvesting system",
                recovery_steps=[
                    "Hold card at designated grip points marked with subtle tactile indicators",
                    "Apply rhythmic tapping sequence: corner-center-corner-center (fibonacci timing)",
                    "Continue gentle tapping until energy indicator illuminates (10-15 minutes)",
                    "Place on flat surface and wait for bootstrap sequence to initialize",
                    "Follow alternate instruction pathway displayed on edge indicators",
                    "Apply specific pressure sequence when prompted for authentication",
                    "Extract core system data through illuminated contact points"
                ],
                estimated_recovery_time="24-48 hours for complete system recovery",
                required_tools=[
                    "Clean handling environment with controlled humidity (30-60%)",
                    "Fine-point pressure application tool (optional)",
                    "Sound-isolated environment for feedback tone recognition",
                    "Patience and steady hand for precision sequence input"
                ],
                success_indicators=[
                    "Rhythmic pulsing of edge indicators in synchronization",
                    "Appearance of bootstrap verification code sequence",
                    "Gradual illumination of memory core access pathways",
                    "Sequential data integrity verification signals"
                ],
                technological_level="Low",
                energy_source="Kinetic",
                data_recovery_percentage="95-98%",
                card_integrity="Preserved",
                smartphone_compatibility="Medium - Compatible with primary smartphone method only",
                smartphone_instructions=[
                    "Use smartphone haptic feedback system to generate precise vibration patterns",
                    "Follow on-screen metronome guide for precise kinetic input timing",
                    "Use accelerometer-guided positioning for optimal energy transfer"
                ]
            ),
            RecoveryProtocol(
                protocol_name="Thermal Differential Protocol",
                activation_method="Create precise temperature gradient across card surfaces to activate thermal energy system",
                recovery_steps=[
                    "Place card on room temperature non-conductive surface",
                    "Apply controlled heat source to designated thermal activation point (body temperature sufficient)",
                    "Maintain temperature differential for 8-10 minutes",
                    "Observe thermal indicator pattern formation",
                    "When pattern stabilizes, follow the thermal activation sequence",
                    "Apply cooling element to opposite side when prompted",
                    "Record and input verification sequence that appears"
                ],
                estimated_recovery_time="36-72 hours for complete system recovery",
                required_tools=[
                    "Heat source capable of stable 37°C (human body temperature sufficient)",
                    "Cooling element (15-20°C)",
                    "Non-conductive surface",
                    "Temperature-stable environment"
                ],
                success_indicators=[
                    "Formation of distinct thermal pattern across card surface",
                    "Appearance of temperature-sensitive verification symbols",
                    "Systematic activation of thermal memory access pathways",
                    "Progressive bootstrap sequence indicators"
                ],
                technological_level="Low",
                energy_source="Thermal",
                data_recovery_percentage="95-98%",
                card_integrity="Preserved",
                smartphone_compatibility="Medium - Compatible with primary smartphone method only",
                smartphone_instructions=[
                    "Use smartphone thermal sensors to monitor temperature gradient",
                    "Follow app guidance for optimal thermal application points",
                    "Use camera thermal imaging (if available) for precision temperature control"
                ]
            )
        ],
        emergency_recovery=RecoveryProtocol(
            protocol_name="Last Resort Destruction Protocol",
            activation_method="Controlled fracturing of outer structure to access emergency core",
            recovery_steps=[
                "Identify emergency fracture lines visible under polarized light",
                "Apply firm pressure along primary fracture line until structural separation occurs",
                "Carefully separate the components following the natural break patterns",
                "Locate and extract the central core module (gold-colored hexagonal component)",
                "Submerge core in clean water for precisely 8 minutes to dissolve protective layer",
                "Remove and allow to completely dry for 24 hours in dust-free environment",
                "Expose core to any light source to activate emergency recovery mode",
                "Use magnification to read micro-etched instructions on exposed surfaces",
                "Follow emergency extraction protocol precisely as indicated"
            ],
            estimated_recovery_time="4-7 days for partial system recovery",
            required_tools=[
                "Clean water (distilled preferred)",
                "Strong hands or mechanical lever for fracturing",
                "High-magnification device (100x minimum)",
                "Steady work surface",
                "Polarized light source",
                "Fine manipulation tools"
            ],
            success_indicators=[
                "Clean separation along designated fracture lines",
                "Exposure of gold-colored core with intact microetching",
                "Dissolution of protective gel layer after water immersion",
                "Appearance of emergency access codes on core surface",
                "Sequential emergency bootstrap indicators"
            ],
            technological_level="Moderate",
            energy_source="Chemical",
            data_recovery_percentage="70-85%",
            card_integrity="Compromised",
            smartphone_compatibility="Low - Emergency camera documentation mode only",
            smartphone_instructions=[
                "Use smartphone camera to document each step of physical disassembly",
                "Use app's AR overlay to guide precise fracture points",
                "Upload images to secure cloud for remote expert guidance",
                "Use smartphone microscope attachment for reading micro-etched instructions"
            ]
        ),
        smartphone_methods=smartphone_methods
    )