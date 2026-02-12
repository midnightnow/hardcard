from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class ScreenSection(BaseModel):
    title: str
    description: str
    components: List[str]

class ScreenWireframe(BaseModel):
    screen_name: str
    purpose: str
    sections: List[ScreenSection]
    interactions: List[str]

class TechnicalComponent(BaseModel):
    name: str
    purpose: str
    implementation_details: str
    dependencies: List[str]

class SecurityFeature(BaseModel):
    name: str
    description: str
    implementation_approach: str

class IPhoneAppPlan(BaseModel):
    app_name: str
    version: str
    description: str
    key_features: List[str]
    target_audience: List[str]
    wireframes: List[ScreenWireframe]
    technical_architecture: List[TechnicalComponent]
    security_features: List[SecurityFeature]
    implementation_phases: Dict[str, List[str]]
    integration_points: List[Dict[str, str]]

@router.get("/iphone-app-plan", response_model=IPhoneAppPlan)
def get_iphone_app_plan():
    """
    Returns the implementation plan for the Legacy Vault iPhone app with Hardcard authentication
    """
    return IPhoneAppPlan(
        app_name="Legacy Vault - Project Unicorn",
        version="1.0.0-MVP",
        description="A secure iOS application enabling Legacy Vault users to authenticate using physical Hardcards through QR code scanning, biometrics, and Google authentication.",
        key_features=[
            "QR code scanning for physical Hardcard authentication",
            "Google account authentication for quick onboarding",
            "Face ID/Touch ID biometric verification",
            "Personalized dashboard with legacy-building activities",
            "Secure account creation linking to physical Hardcards",
            "Encrypted communication and data storage",
            "Offline authentication capabilities",
            "Multi-factor authentication options"
        ],
        target_audience=[
            "Legacy Vault family account holders",
            "Parents building generational wealth",
            "Trust fund administrators",
            "Financial advisors managing family accounts",
            "Children with Legacy Vault accounts (monitored access)"
        ],
        wireframes=[
            ScreenWireframe(
                screen_name="Onboarding Screen",
                purpose="Introduce users to the app and provide authentication options",
                sections=[
                    ScreenSection(
                        title="Welcome Section",
                        description="Animated logo and welcome message",
                        components=["Legacy Vault logo animation", "Welcome to Legacy Vault Secure Access headline", "Subtitle explaining app purpose"]
                    ),
                    ScreenSection(
                        title="Authentication Options",
                        description="Buttons for different authentication methods",
                        components=["Sign in with Google button", "Scan Hardcard QR Code button", "Enter Hardcard ID manually (small text link)"]
                    ),
                    ScreenSection(
                        title="Legal Information",
                        description="Privacy policy and terms of service links",
                        components=["Privacy Policy link", "Terms of Service link"]
                    )
                ],
                interactions=["Tap 'Sign in with Google' to initiate Google OAuth flow", "Tap 'Scan Hardcard' to open camera for QR scanning", "Tap 'Enter manually' to navigate to manual entry screen"]
            ),
            ScreenWireframe(
                screen_name="QR Code Scanner",
                purpose="Allow users to authenticate via Hardcard QR code scan",
                sections=[
                    ScreenSection(
                        title="Camera View",
                        description="Live camera feed with QR code detection",
                        components=["Camera viewfinder", "QR code targeting rectangle", "Scan instructions overlay", "Cancel button"]
                    ),
                    ScreenSection(
                        title="Scanning Status",
                        description="Visual feedback during scanning process",
                        components=["Scanning animation", "Status text ('Searching for Hardcard...')", "Cancel button"]
                    )
                ],
                interactions=["Camera automatically detects QR code", "After successful scan, proceeds to verification screen", "Tap 'Cancel' to return to onboarding screen"]
            ),
            ScreenWireframe(
                screen_name="Biometric Verification",
                purpose="Verify user identity using Face ID or Touch ID",
                sections=[
                    ScreenSection(
                        title="Verification Prompt",
                        description="Request for biometric verification",
                        components=["Large Face ID or Touch ID icon", "'Verify Your Identity' headline", "'Use Face ID/Touch ID to authenticate' instruction text", "'Use alternative method' link"]
                    ),
                    ScreenSection(
                        title="Status Feedback",
                        description="Visual feedback during verification",
                        components=["Verification status animation", "Status text"]
                    )
                ],
                interactions=["System automatically triggers Face ID/Touch ID prompt", "After successful verification, proceeds to dashboard", "Tap 'Use alternative method' for fallback authentication options"]
            ),
            ScreenWireframe(
                screen_name="Dashboard",
                purpose="Provide overview of legacy-building activities and account status",
                sections=[
                    ScreenSection(
                        title="Header",
                        description="User and account information",
                        components=["User profile photo/avatar", "Welcome message with user name", "Account security status indicator", "Quick action buttons (settings, notifications)"]
                    ),
                    ScreenSection(
                        title="Legacy Summary",
                        description="Overview of legacy investments and growth",
                        components=["Current valuation card", "Growth percentage indicator", "Time-based visualization toggle (1Y, 5Y, 18Y, 30Y)", "Last update timestamp"]
                    ),
                    ScreenSection(
                        title="Legacy-Building Activities",
                        description="List of actions and symbolic tasks",
                        components=["Activity cards with icons", "Completion status indicators", "'View all' button"]
                    ),
                    ScreenSection(
                        title="Navigation Bar",
                        description="Bottom navigation to other sections",
                        components=["Dashboard icon (active)", "Investments icon", "Family icon", "Security icon", "Profile icon"]
                    )
                ],
                interactions=["Tap activity card to view details", "Tap security status to view security settings", "Use bottom navigation to switch between main sections", "Tap time toggle to change investment visualization timeframe"]
            ),
            ScreenWireframe(
                screen_name="Security Center",
                purpose="Manage security settings and view authentication history",
                sections=[
                    ScreenSection(
                        title="Header",
                        description="Security overview information",
                        components=["Security score indicator", "Last security check timestamp", "Security level badge"]
                    ),
                    ScreenSection(
                        title="Hardcard Management",
                        description="Manage connected Hardcards",
                        components=["Active Hardcard display", "Hardcard status indicator", "'Add new Hardcard' button", "'Revoke Hardcard' option"]
                    ),
                    ScreenSection(
                        title="Authentication Methods",
                        description="Manage authentication options",
                        components=["Google account status", "Biometric authentication toggle", "PIN/Password management", "Two-factor authentication settings"]
                    ),
                    ScreenSection(
                        title="Authentication History",
                        description="Recent authentication attempts",
                        components=["List of recent authentication events", "Date/time stamps", "Success/failure indicators", "Device information"]
                    )
                ],
                interactions=["Toggle biometric authentication on/off", "Tap 'Add new Hardcard' to start pairing process", "Tap authentication event to see details", "Tap 'Revoke Hardcard' to remove a Hardcard"]
            )
        ],
        technical_architecture=[
            TechnicalComponent(
                name="Authentication Module",
                purpose="Handle all authentication flows (QR, Google, Biometric)",
                implementation_details="Uses Apple's LocalAuthentication framework for biometrics, Google Sign-In SDK for Google authentication, and AVFoundation for QR code scanning. Implements OAuth 2.0 flow for secure token exchange with Legacy Vault backend.",
                dependencies=["Google Sign-In SDK", "LocalAuthentication framework", "AVFoundation", "Legacy Vault Authentication API"]
            ),
            TechnicalComponent(
                name="Secure Storage Module",
                purpose="Safely store authentication tokens and user data",
                implementation_details="Utilizes Apple's Keychain Services API for secure credential storage. Sensitive data is encrypted using AES-256 before storage. Implements automatic data purging on multiple failed authentication attempts.",
                dependencies=["Keychain Services API", "CryptoKit framework"]
            ),
            TechnicalComponent(
                name="QR Code Scanner",
                purpose="Scan and process Hardcard QR codes",
                implementation_details="Built on AVFoundation to access camera and process QR codes in real-time. Implements custom QR code validation to verify Hardcard authenticity. Includes adaptive scanning for various lighting conditions.",
                dependencies=["AVFoundation", "Core Image", "Legacy Vault Hardcard Verification API"]
            ),
            TechnicalComponent(
                name="Secure Networking Layer",
                purpose="Handle all API communications with end-to-end encryption",
                implementation_details="Custom networking layer built on URLSession with certificate pinning to prevent MITM attacks. Implements request signing for API authentication. All network traffic is encrypted using TLS 1.3 with strong cipher suites.",
                dependencies=["URLSession", "CryptoKit", "Legacy Vault API Gateway"]
            ),
            TechnicalComponent(
                name="Biometric Authentication Manager",
                purpose="Handle Face ID and Touch ID integration",
                implementation_details="Wrapper around LocalAuthentication framework that provides simplified API for biometric verification. Includes fallback mechanisms for devices without biometric capabilities or when biometric authentication fails.",
                dependencies=["LocalAuthentication framework"]
            ),
            TechnicalComponent(
                name="Dashboard Data Manager",
                purpose="Fetch and manage data displayed on the dashboard",
                implementation_details="Responsible for retrieving user-specific data from the Legacy Vault API, including investment summaries, growth projections, and legacy-building activities. Implements caching for offline access and data synchronization when connectivity is restored.",
                dependencies=["Secure Networking Layer", "Secure Storage Module", "Legacy Vault Data API"]
            ),
            TechnicalComponent(
                name="Encryption Service",
                purpose="Provide app-wide encryption capabilities",
                implementation_details="Centralized service for handling all encryption/decryption operations. Uses Apple's CryptoKit for modern cryptographic operations. Implements key rotation policies and secure key derivation from user credentials.",
                dependencies=["CryptoKit framework", "Secure Storage Module"]
            )
        ],
        security_features=[
            SecurityFeature(
                name="End-to-End Encryption",
                description="All communications between the app and backend are encrypted",
                implementation_approach="Implement TLS 1.3 with certificate pinning and custom application-layer encryption using CryptoKit for sensitive data fields."
            ),
            SecurityFeature(
                name="Secure Local Storage",
                description="All sensitive data stored on the device is encrypted",
                implementation_approach="Use Keychain Services for credentials and CryptoKit for file-level encryption with keys derived from user authentication."
            ),
            SecurityFeature(
                name="Biometric Authentication",
                description="Use Face ID or Touch ID to verify user identity",
                implementation_approach="Integrate LocalAuthentication framework with security policies that require re-authentication after app background or timeout."
            ),
            SecurityFeature(
                name="Jailbreak Detection",
                description="Detect if device is jailbroken and take appropriate action",
                implementation_approach="Implement multiple jailbreak detection techniques and block app usage or limit functionality on compromised devices."
            ),
            SecurityFeature(
                name="Secure QR Code Processing",
                description="Ensure QR codes are valid Hardcards and cannot be spoofed",
                implementation_approach="Implement digital signature verification on QR code data and time-based validation to prevent replay attacks."
            ),
            SecurityFeature(
                name="App Transport Security",
                description="Enforce secure connections to all external services",
                implementation_approach="Configure ATS settings to require HTTPS connections with strong TLS protocols and cipher suites."
            ),
            SecurityFeature(
                name="Tamper Detection",
                description="Detect if app binary has been modified",
                implementation_approach="Implement code signature verification and runtime integrity checks to detect unauthorized modifications."
            )
        ],
        implementation_phases={
            "Phase 1: Core Authentication": [
                "Implement QR code scanning functionality",
                "Integrate Google Sign-In",
                "Implement biometric authentication",
                "Develop secure storage for authentication tokens",
                "Create basic authentication flow"
            ],
            "Phase 2: Dashboard & User Experience": [
                "Develop dashboard UI",
                "Implement data fetching for legacy investments",
                "Create legacy-building activities display",
                "Design and implement navigation system",
                "Add basic offline support"
            ],
            "Phase 3: Security Enhancements": [
                "Implement end-to-end encryption",
                "Add jailbreak detection",
                "Implement certificate pinning",
                "Add tamper detection",
                "Create security activity logging"
            ],
            "Phase 4: Polish & Final Integration": [
                "Optimize performance",
                "Enhance offline capabilities",
                "Add animations and visual polish",
                "Conduct security audit",
                "Prepare for App Store submission"
            ]
        },
        integration_points=[
            {
                "name": "Legacy Vault Authentication API",
                "description": "Authenticates users and validates Hardcards"
            },
            {
                "name": "Legacy Vault Data API",
                "description": "Provides investment data and activity information"
            },
            {
                "name": "Google Identity Services",
                "description": "Handles Google authentication"
            },
            {
                "name": "Apple Push Notification Service",
                "description": "Delivers secure notifications"
            },
            {
                "name": "Legacy Vault Sync Service",
                "description": "Synchronizes offline changes with backend"
            }
        ]
    )
