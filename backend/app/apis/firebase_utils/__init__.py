# src/app/apis/firebase_utils/__init__.py
import logging
import firebase_admin
from firebase_admin import credentials, firestore
import databutton as db
import json
import os
from fastapi import APIRouter

# Suppress INFO logs from httpx client, which are otherwise shown as errors
logging.getLogger("httpx").setLevel(logging.WARNING)

# This router won't have endpoints but is needed for the file to be treated as an API module
router = APIRouter()

_firestore_db_client = None
_firebase_app_initialized_flag = False

FIREBASE_SERVICE_ACCOUNT_SECRET_KEY = "FIREBASE_SERVICE_ACCOUNT_JSON"

def _initialize_firebase_admin_sdk():
    global _firestore_db_client, _firebase_app_initialized_flag

    if _firebase_app_initialized_flag:
        return

    try:
        print("Attempting to initialize Firebase Admin SDK from firebase_utils...")
        service_account_json_str = db.secrets.get(FIREBASE_SERVICE_ACCOUNT_SECRET_KEY)
        
        if not service_account_json_str:
            print(f"Firebase secret '{FIREBASE_SERVICE_ACCOUNT_SECRET_KEY}' not found. Attempting default credentials.")
            try:
                # Try to use default credentials (e.g., when running in Google Cloud Environment)
                cred_object = firebase_admin.credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred_object)
                _firestore_db_client = firestore.client()
                _firebase_app_initialized_flag = True
                print("Firebase Admin SDK initialized successfully with default Google credentials.")
                return
            except Exception as e_default:
                print(f"Failed to initialize Firebase Admin with default credentials: {e_default}. Firestore will not be available.")
                _firebase_app_initialized_flag = False # Explicitly mark as not initialized
                return

        service_account_dict = json.loads(service_account_json_str)
        cred = credentials.Certificate(service_account_dict)
        firebase_admin.initialize_app(cred)
        _firestore_db_client = firestore.client()
        _firebase_app_initialized_flag = True
        print("Firebase Admin SDK initialized successfully using secret from firebase_utils.")

    except json.JSONDecodeError as e_json:
        print(f"Error decoding Firebase service account JSON: {e_json}. Firestore will not be available.")
        _firebase_app_initialized_flag = False
    except ValueError as e_value:
        print(f"Error initializing Firebase Admin SDK (ValueError): {e_value}. Ensure '{FIREBASE_SERVICE_ACCOUNT_SECRET_KEY}' is set. Firestore will not be available.")
        _firebase_app_initialized_flag = False
    except Exception as e_general:
        print(f"Unexpected error during Firebase Admin SDK initialization: {e_general}. Firestore will not be available.")
        _firebase_app_initialized_flag = False

def get_firestore_client():
    """Provides a Firestore client instance. Initializes SDK on first call."""
    global _firestore_db_client, _firebase_app_initialized_flag
    if not _firebase_app_initialized_flag:
        _initialize_firebase_admin_sdk()
    
    if not _firebase_app_initialized_flag or _firestore_db_client is None:
        print(
            f"CRITICAL: Firestore client is not available. "
            f"Ensure Firebase Admin SDK initialized correctly (check '{FIREBASE_SERVICE_ACCOUNT_SECRET_KEY}' secret) or default credentials are working."
        )
        return None
        
    return _firestore_db_client

# Perform initialization when this module is loaded
_initialize_firebase_admin_sdk()
