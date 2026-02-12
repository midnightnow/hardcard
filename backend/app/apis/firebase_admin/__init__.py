import firebase_admin
from firebase_admin import credentials, firestore
import json
import databutton as db
from fastapi import APIRouter

router = APIRouter(prefix="/firebase-admin")

# Initialize Firebase Admin SDK
# Check if already initialized to avoid errors on app restart
if not firebase_admin._apps:
    # Try to get firebase credentials from secrets
    try:
        service_account_json = db.secrets.get("FIREBASE_SERVICE_ACCOUNT")
        if service_account_json:
            service_account = json.loads(service_account_json)
            cred = credentials.Certificate(service_account)
            firebase_admin.initialize_app(cred)
        else:
            # If no service account in secrets, initialize with default credentials
            # This assumes appropriate environment variables are set
            firebase_admin.initialize_app()
    except Exception as e:
        print(f"Error initializing Firebase Admin: {e}")
        # Initialize with default credentials as fallback
        firebase_admin.initialize_app()

# Get Firestore database
firestore_db = firestore.client()

@router.get("/health")
def check_health_firebase_admin():
    """Check if the Firebase Admin API is working"""
    return {"status": "ok", "message": "Firebase Admin API is operational"}