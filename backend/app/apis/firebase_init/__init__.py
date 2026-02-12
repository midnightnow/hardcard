import firebase_admin
from firebase_admin import credentials, firestore, auth
import databutton as db
import json
import os
from fastapi import APIRouter
from pydantic import BaseModel
import re

# Create router required for APIs
router = APIRouter()

# Global variable to track initialization status
firebase_initialized = False
firebase_app = None

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account if available"""
    global firebase_initialized, firebase_app
    
    if firebase_initialized and firebase_app:
        return True
    
    try:
        # Check if already initialized
        firebase_app = firebase_admin.get_app()
        firebase_initialized = True
        print("Firebase already initialized")
        return True
    except ValueError:
        # Not initialized yet, continue
        pass
    
    # Try to initialize with service account
    try:
        # Try to get service account - catch specific exception if not exists
        try:
            firebase_service_account = db.secrets.get("FIREBASE_SERVICE_ACCOUNT")
        except Exception as e:
            print(f"Firebase service account not found: {str(e)}")
            firebase_service_account = None
            
        if firebase_service_account and firebase_service_account.strip():
            # Parse JSON string to dict
            try:
                # Clean the service account string to handle potential formatting issues
                cleaned_service_account = firebase_service_account.strip()
                # Check if the string is valid before parsing
                if cleaned_service_account and cleaned_service_account[0] in ('{', '['):
                    # Attempt to parse as JSON
                    service_account_dict = json.loads(cleaned_service_account)
                    if isinstance(service_account_dict, dict) and service_account_dict.get("type") == "service_account":
                        cred = credentials.Certificate(service_account_dict)
                        firebase_app = firebase_admin.initialize_app(cred)
                        firebase_initialized = True
                        print("Firebase Admin SDK initialized with service account")
                        return True
                    else:
                        print("Invalid Firebase service account format: missing required fields")
                else:
                    print("Firebase service account JSON appears malformed (doesn't start with '{' or '[')")
            except json.JSONDecodeError as e:
                print(f"Error parsing Firebase service account JSON: {str(e)}")
            except Exception as e:
                print(f"Unexpected error initializing Firebase with service account: {str(e)}")
    except Exception as e:
        print(f"Error initializing Firebase with service account: {str(e)}")
    
    # Fallback to default config if service account didn't work
    try:
        firebase_app = firebase_admin.initialize_app()
        firebase_initialized = True
        print("Firebase Admin SDK initialized with default configuration")
        return True
    except Exception as e:
        print(f"Error initializing Firebase with default config: {str(e)}")
        firebase_initialized = False
        return False

# Initialize Firebase on module import
initialize_firebase()


class FirebaseStatusResponse(BaseModel):
    initialized: bool
    message: str
    service_account_present: bool = False
    auth_available: bool = False
    firestore_available: bool = False


@router.get("/firebase/status")
def get_firebase_status() -> FirebaseStatusResponse:
    """Check if Firebase is properly initialized and return the status"""
    # Re-attempt initialization if not already done
    if not firebase_initialized:
        initialize_firebase()
    
    # Check if service account is present
    service_account_present = False
    try:
        firebase_service_account = db.secrets.get("FIREBASE_SERVICE_ACCOUNT") or ""
        service_account_present = bool(firebase_service_account.strip())
    except Exception:
        service_account_present = False
    
    # Check if auth is available
    auth_available = False
    try:
        auth.get_user_by_email("test@example.com")
        auth_available = True
    except auth.UserNotFoundError:
        # This is expected - just testing if the auth service works
        auth_available = True
    except Exception:
        auth_available = False
    
    # Check if Firestore is available
    firestore_available = False
    try:
        # Create a client for this check only
        db_client = firestore.client()
        # Just check if we can access Firestore
        db_client.collection("test").limit(1).get()
        firestore_available = True
    except Exception:
        firestore_available = False
    
    if firebase_initialized:
        if auth_available and firestore_available:
            message = "Firebase is fully initialized and operational"
        elif auth_available:
            message = "Firebase Auth is operational, but Firestore has issues"
        elif firestore_available:
            message = "Firebase Firestore is operational, but Auth has issues"
        else:
            message = "Firebase is initialized but services are not fully operational"
    else:
        message = "Firebase failed to initialize"
    
    return FirebaseStatusResponse(
        initialized=firebase_initialized,
        message=message,
        service_account_present=service_account_present,
        auth_available=auth_available,
        firestore_available=firestore_available
    )

@router.get("/firebase/health-check")
def check_firebase_health_init() -> dict:
    """Perform a comprehensive health check of Firebase services"""
    # Check various Firebase components
    health_check = {
        "status": "operational" if firebase_initialized else "failed",
        "firestore": {
            "status": "unknown",
            "error": None
        },
        "authentication": {
            "status": "unknown",
            "error": None
        }
    }
    
    # Check Firestore health
    try:
        # Create a client for this check only
        db_client = firestore.client()
        db_client.collection("test").limit(1).get()
        health_check["firestore"]["status"] = "operational"
    except Exception as e:
        health_check["firestore"]["status"] = "error"
        health_check["firestore"]["error"] = str(e)
    
    # Check Authentication health
    try:
        # This will fail with UserNotFoundError which is expected
        auth.get_user_by_email("test@example.com")
        health_check["authentication"]["status"] = "operational"
    except auth.UserNotFoundError:
        # This is expected - email doesn't exist but auth is working
        health_check["authentication"]["status"] = "operational"
    except Exception as e:
        health_check["authentication"]["status"] = "error"
        health_check["authentication"]["error"] = str(e)
    
    # Update overall status based on components
    if health_check["firestore"]["status"] == "operational" and health_check["authentication"]["status"] == "operational":
        health_check["status"] = "fully_operational"
    elif health_check["firestore"]["status"] != "operational" and health_check["authentication"]["status"] != "operational":
        health_check["status"] = "critical"
    else:
        health_check["status"] = "partially_operational"
    
    return health_check