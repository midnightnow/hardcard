from pydantic import BaseModel
from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()

class IPhoneAppPlan(BaseModel):
    app_name: str = "Legacy Vault Authenticator"
    version: str = "1.0.0"
    description: str = "Secure authentication app for Legacy Vault using Hardcard technology"
    features: List[dict] = [
        {
            "id": "qr_scanning",
            "name": "QR Code Scanning",
            "description": "Scan physical Hardcards (paper or metal) via the device camera",
            "implementation_details": [
                "Utilize AVFoundation for camera access and QR recognition",
                "Support multiple QR code formats for backward compatibility",
                "Process encoded data with cryptographic verification",
                "Haptic feedback on successful scan"
            ],
            "status": "planned"
        },
        {
            "id": "google_auth",
            "name": "Google Authentication",
            "description": "Fast and secure onboarding using Google Sign-In",
            "implementation_details": [
                "Implement Google Sign-In SDK",
                "Verify authentication tokens on server",
                "Securely store authentication credentials",
                "Link Google accounts to Legacy Vault profiles"
            ],
            "status": "planned"
        },
        {
            "id": "biometric_verification",
            "name": "Biometric Verification",
            "description": "Use Face ID/Touch ID for secure access",
            "implementation_details": [
                "Integrate LocalAuthentication framework",
                "Support both Face ID and Touch ID based on device capability",
                "Implement secure enclave for biometric key storage",
                "Fallback mechanism for devices without biometric capabilities"
            ],
            "status": "planned"
        },
        {
            "id": "personal_dashboard",
            "name": "Personalized Dashboard",
            "description": "View legacy-building activities and symbolic tasks",
            "implementation_details": [
                "Real-time synchronization with Legacy Vault",
                "Visual representation of trust growth",
                "Task completion tracking",
                "Timeline of legacy-building activities"
            ],
            "status": "planned"
        },
        {
            "id": "account_creation",
            "name": "Secure Account Creation",
            "description": "Create accounts linked to physical Hardcards",
            "implementation_details": [
                "Secure registration flow with email verification",
                "Hardcard linking during initial setup",
                "Hierarchical account structure for family members",
                "Recovery options and backup procedures"
            ],
            "status": "planned"
        },
        {
            "id": "encrypted_communication",
            "name": "Encrypted Communication",
            "description": "Secure data transfer between app and server",
            "implementation_details": [
                "End-to-end encryption for all communications",
                "TLS 1.3 for transport security",
                "Certificate pinning to prevent MITM attacks",
                "Local encryption for stored data using AES-256"
            ],
            "status": "planned"
        }
    ],
    technical_architecture: dict = {
        "frontend": {
            "framework": "Swift UI",
            "minimum_ios_version": "15.0",
            "key_components": [
                "AVFoundation for camera and QR scanning",
                "LocalAuthentication for biometrics",
                "GoogleSignIn SDK for authentication",
                "Keychain for secure credential storage",
                "SwiftUI for modern, declarative UI"
            ]
        },
        "backend_integration": {
            "api_endpoints": [
                "/authenticate-with-hardcard",
                "/verify-device",
                "/link-account",
                "/get-dashboard-data",
                "/update-security-settings"
            ],
            "authentication": "JWT with refresh tokens",
            "data_sync": "Real-time with offline capabilities"
        },
        "security_measures": [
            "App Transport Security (ATS) enforced",
            "Certificate pinning for API communication",
            "Secure Enclave for biometric and cryptographic operations",
            "Jailbreak detection",
            "Anti-tampering measures",
            "Hardcard cryptographic verification"
        ]
    },
    user_flow: List[dict] = [
        {
            "step": 1,
            "name": "Onboarding",
            "description": "Initial app introduction and setup",
            "screens": [
                "Welcome screen with app explanation",
                "Authentication options (Google/Email)",
                "Permission requests (Camera, Notifications)",
                "Biometric setup"
            ]
        },
        {
            "step": 2,
            "name": "Hardcard Linking",
            "description": "Connect physical Hardcard to digital account",
            "screens": [
                "QR code scanning interface",
                "Hardcard verification status",
                "Successful connection confirmation"
            ]
        },
        {
            "step": 3,
            "name": "Dashboard Access",
            "description": "View personal Legacy Vault dashboard",
            "screens": [
                "Legacy building overview",
                "Trust fund growth visualization",
                "Recent activities and tasks",
                "Family member connections"
            ]
        },
        {
            "step": 4,
            "name": "Authentication Process",
            "description": "Authenticate for sensitive operations",
            "screens": [
                "Biometric prompt",
                "Hardcard QR re-scan if needed",
                "Multi-factor confirmation",
                "Success confirmation"
            ]
        }
    ],
    timeline: dict = {
        "phase_1": {
            "name": "Core Authentication",
            "duration": "4 weeks",
            "deliverables": [
                "QR scanning functionality",
                "Google authentication",
                "Biometric verification",
                "Basic dashboard"
            ]
        },
        "phase_2": {
            "name": "Enhanced Features",
            "duration": "3 weeks",
            "deliverables": [
                "Full dashboard implementation",
                "Family account linking",
                "Offline capabilities",
                "Enhanced security measures"
            ]
        },
        "phase_3": {
            "name": "Polishing & Testing",
            "duration": "3 weeks",
            "deliverables": [
                "UI refinement",
                "Security auditing",
                "Performance optimization",
                "App Store submission preparation"
            ]
        }
    }

@router.get("/iphone-app-plan-legacy")
def get_iphone_app_plan_detail() -> IPhoneAppPlan:
    """Get the implementation plan for the iPhone app MVP"""
    return IPhoneAppPlan()
