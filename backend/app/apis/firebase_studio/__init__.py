from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
import databutton as db
import requests
import time
import uuid
from enum import Enum
from firebase_admin import auth, firestore
from app.apis.firebase_init import initialize_firebase

# Initialize Firebase
initialize_firebase()

# Create a FastAPI router
router = APIRouter()

# Define Pydantic models for request/response validation

class DeploymentType(str, Enum):
    CODE = "code"
    DATA = "data"
    CONFIG = "config"

class DeploymentDirection(str, Enum):
    TO_FIREBASE = "to-firebase"
    FROM_FIREBASE = "from-firebase"

class DeploymentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DeploymentRequest(BaseModel):
    """Request model for deploying to/from Firebase"""
    type: DeploymentType
    direction: DeploymentDirection
    project_id: str = Field(..., description="Firebase project ID")
    environment: str = Field("development", description="Environment (development, staging, production)")
    auto_sync: bool = Field(False, description="Whether to enable auto-sync")

class DeploymentResponse(BaseModel):
    """Response model for deployment operations"""
    deployment_id: str
    status: DeploymentStatus
    message: str

class DeploymentStatusRequest(BaseModel):
    """Request model for checking deployment status"""
    deployment_id: str

class DeploymentStatusResponse(BaseModel):
    """Response model for deployment status"""
    deployment_id: str
    status: DeploymentStatus
    progress: int
    error: str = None
class FirebaseStatsResponse(BaseModel):
    """Firebase Statistics Response model"""
    users_count: int
    collections_count: int
    documents_count: Dict[str, int]
    storage_usage: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]

class FirebaseUserResponse(BaseModel):
    """Firebase User Information Response model"""
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    disabled: bool
    email_verified: bool
    creation_time: str
    last_sign_in_time: Optional[str] = None
    custom_claims: Optional[Dict[str, Any]] = None
    provider_data: List[Dict[str, Any]]

class CollectionDataResponse(BaseModel):
    """Collection Data Response model"""
    collection_id: str
    document_count: int
    sample_documents: List[Dict[str, Any]]
    collection_schema: Dict[str, str] = Field(..., alias="schema")

class FirebaseExportRequest(BaseModel):
    """Firebase Export Request model"""
    collections: List[str] = Field(..., description="List of collection names to export")
    destination: str = Field(..., description="Destination for the exported data")

class FirebaseImportRequest(BaseModel):
    """Firebase Import Request model"""
    source: str = Field(..., description="Source of the data to import")
    merge: bool = Field(False, description="Whether to merge with existing data or overwrite")

class GeminiCodeRequest(BaseModel):
    """Gemini Code Request model"""
    prompt: str = Field(..., description="Prompt for Gemini to generate code")
    context: Optional[Dict[str, Any]] = Field(None, description="Context information for Gemini")
    target_platform: str = Field("firebase", description="Target platform for the generated code")

class GeminiCodeResponse(BaseModel):
    """Gemini Code Response model"""
    code: str
    explanation: str
    suggested_filename: str
    language: str

# Ensure Firebase is initialized
initialize_firebase()

@router.get("/stats", response_model=FirebaseStatsResponse)
def get_firebase_stats():
    """Get statistics about Firebase usage and performance."""
    try:
        # Get user count
        users_count = 0
        users_iter = auth.list_users()
        for _ in users_iter.iterate_all():
            users_count += 1
        
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # Get collections
        collections = db_client.collections()
        collections_list = [collection.id for collection in collections]
        collections_count = len(collections_list)
        
        # Get document counts per collection
        documents_count = {}
        for collection_id in collections_list:
            docs = db_client.collection(collection_id).get()
            documents_count[collection_id] = len(docs)
        
        # Storage usage is mocked for now (would require Google Cloud API)
        storage_usage = {
            "total_bytes": 1024 * 1024 * 10,  # Example: 10 MB
            "files_count": 25
        }
        
        # Recent activity (would be pulled from logs in production)
        recent_activity = [
            {
                "timestamp": time.time() - 3600,
                "operation": "document_write",
                "collection": "users",
                "document_id": "example_id"
            },
            {
                "timestamp": time.time() - 7200,
                "operation": "authentication",
                "user_id": "auth_user_id",
                "success": True
            }
        ]
        
        return FirebaseStatsResponse(
            users_count=users_count,
            collections_count=collections_count,
            documents_count=documents_count,
            storage_usage=storage_usage,
            recent_activity=recent_activity
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Firebase stats: {str(e)}")

@router.get("/users", response_model=List[FirebaseUserResponse])
def list_firebase_users():
    """List all users in Firebase Authentication."""
    try:
        users_list = []
        users_iter = auth.list_users()
        for user in users_iter.iterate_all():
            user_dict = {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "disabled": user.disabled,
                "email_verified": user.email_verified,
                "creation_time": user.user_metadata.creation_timestamp,
                "last_sign_in_time": user.user_metadata.last_sign_in_timestamp,
                "custom_claims": user.custom_claims,
                "provider_data": [dict(provider.to_dict()) for provider in user.provider_data]
            }
            users_list.append(user_dict)
        
        return users_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Firebase users: {str(e)}")

@router.get("/collections", response_model=List[str])
def list_collections():
    """List all collections in Firestore."""
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        collections = db_client.collections()
        collections_list = [collection.id for collection in collections]
        return collections_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")

@router.get("/collections/{collection_id}", response_model=CollectionDataResponse)
def get_collection_data(collection_id: str):
    """Get data and schema information about a specific collection."""
    try:
        # Create a local Firestore client for this function
        db_client = firestore.client()
        # Get collection documents
        docs = db_client.collection(collection_id).limit(10).get()
        document_count = len(list(db_client.collection(collection_id).get()))
        
        # Get sample documents
        sample_documents = []
        schema = {}
        for doc in docs:
            doc_dict = doc.to_dict()
            sample_documents.append({
                "id": doc.id,
                "data": doc_dict
            })
            
            # Extract schema from the first document
            if not schema and doc_dict:
                for key, value in doc_dict.items():
                    schema[key] = type(value).__name__
        
        return CollectionDataResponse(
            collection_id=collection_id,
            document_count=document_count,
            sample_documents=sample_documents,
            schema=schema
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collection data: {str(e)}")

@router.post("/export")
def export_firebase_data(request: FirebaseExportRequest):
    """Export selected collections from Firebase to a specified destination."""
    try:
        # In a real implementation, this would use Firebase Admin SDK
        # or Google Cloud Storage to export the data
        
        # Create a local Firestore client for this function
        db_client = firestore.client()
        
        # For our example, we'll just fetch the collections and save to Databutton storage
        export_data = {}
        
        for collection_id in request.collections:
            docs = db_client.collection(collection_id).get()
            collection_data = {doc.id: doc.to_dict() for doc in docs}
            export_data[collection_id] = collection_data
        
        # Save to Databutton storage with the specified destination as key
        storage_key = f"firebase_export_{request.destination}"
        db.storage.json.put(storage_key, export_data)
        
        return {
            "status": "success",
            "message": f"Exported {len(request.collections)} collections to {request.destination}",
            "export_id": storage_key
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export Firebase data: {str(e)}")

@router.post("/import")
def import_firebase_data(request: FirebaseImportRequest):
    """Import data from a specified source into Firebase."""
    try:
        # In a real implementation, this would use Firebase Admin SDK
        # to import data from Google Cloud Storage
        
        # For our example, we'll get data from Databutton storage
        storage_key = f"firebase_export_{request.source}"
        import_data = db.storage.json.get(storage_key)
        
        if not import_data:
            raise HTTPException(status_code=404, detail=f"Export data not found: {request.source}")
        
        # Import the collections
        # Create a local Firestore client for this function
        db_client = firestore.client()
        for collection_id, documents in import_data.items():
            collection_ref = db_client.collection(collection_id)
            
            for doc_id, doc_data in documents.items():
                if request.merge:
                    collection_ref.document(doc_id).set(doc_data, merge=True)
                else:
                    collection_ref.document(doc_id).set(doc_data)
        
        return {
            "status": "success",
            "message": f"Imported {len(import_data)} collections from {request.source}",
            "collections_imported": list(import_data.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import Firebase data: {str(e)}")

@router.post("/gemini-code", response_model=GeminiCodeResponse)
def generate_code_with_gemini(request: GeminiCodeRequest):
    """Generate code using Google's Gemini AI for Firebase integration."""
    try:
        # This is a mock implementation
        # In a real implementation, this would call the Gemini API
        
        # For demonstration purposes, return a mock response
        language = "javascript"
        if "python" in request.prompt.lower():
            language = "python"
        
        code_snippets = {
            "javascript": "// Firebase Authentication example\n\nconst signInWithEmailAndPassword = async (email, password) => {\n  try {\n    const userCredential = await firebase.auth().signInWithEmailAndPassword(email, password);\n    const user = userCredential.user;\n    console.log('Signed in user:', user);\n    return user;\n  } catch (error) {\n    console.error('Error signing in:', error);\n    throw error;\n  }\n};",
            "python": "# Firebase Authentication example\n\ndef sign_in_with_email_and_password(email, password):\n    try:\n        user = auth.get_user_by_email(email)\n        # In a real app, you would verify the password here\n        # This is just for demonstration\n        print(f'Signed in user: {user.uid}')\n        return user\n    except Exception as e:\n        print(f'Error signing in: {str(e)}')\n        raise e"
        }
        
        explanations = {
            "javascript": "This code provides a function to sign in users with email and password using Firebase Authentication. It returns the user object on success and throws an error on failure.",
            "python": "This code provides a function to sign in users with email and password using Firebase Admin SDK. It returns the user object on success and raises an exception on failure."
        }
        
        filenames = {
            "javascript": "auth.js",
            "python": "auth.py"
        }
        
        return GeminiCodeResponse(
            code=code_snippets[language],
            explanation=explanations[language],
            suggested_filename=filenames[language],
            language=language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate code with Gemini: {str(e)}")

@router.post("/run-query")
def run_firestore_query(query: Dict[str, Any] = Body(...)):
    """Run a Firestore query and return the results."""
    try:
        collection_id = query.get("collection")
        if not collection_id:
            raise HTTPException(status_code=400, detail="Collection ID is required")
        
        # Start with the collection reference
        # Create a local Firestore client for this function
        db_client = firestore.client()
        ref = db_client.collection(collection_id)
        
        # Apply filters if present
        filters = query.get("filters", [])
        for filter_item in filters:
            field = filter_item.get("field")
            op = filter_item.get("operator")
            value = filter_item.get("value")
            
            if field and op and value is not None:
                ref = ref.where(filter=firestore.FieldFilter(field, op, value))
        
        # Apply order if present
        order = query.get("order")
        if order:
            field = order.get("field")
            direction = order.get("direction", "asc")
            
            if field:
                if direction == "desc":
                    ref = ref.order_by(field, direction=firestore.Query.DESCENDING)
                else:
                    ref = ref.order_by(field)
        
        # Apply limit if present
        limit = query.get("limit")
        if limit and isinstance(limit, int):
            ref = ref.limit(limit)
        
        # Execute the query
        docs = ref.get()
        
        # Format the results
        results = []
        for doc in docs:
            results.append({
                "id": doc.id,
                "data": doc.to_dict()
            })
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run Firestore query: {str(e)}")

@router.get("/performance")
def get_firebase_performance():
    """Get performance metrics for Firebase services."""
    # In a real implementation, this would use Firebase Performance Monitoring API
    # Here we return mock data
    return {
        "authentication": {
            "success_rate": 98.5,
            "average_latency_ms": 120,
            "requests_per_minute": 2.3
        },
        "firestore": {
            "reads_per_minute": 15.2,
            "writes_per_minute": 3.8,
            "average_query_time_ms": 85
        },
        "storage": {
            "downloads_per_minute": 0.5,
            "uploads_per_minute": 0.1,
            "average_download_time_ms": 350
        }
    }


@router.get("/resources")
def get_firebase_resources():
    """Get real-time resource metrics for Firebase infrastructure."""
    import random
    import time
    
    # Generate mock data for demonstration purposes
    # In a real implementation, this would fetch actual metrics from Firebase Admin SDK
    
    cpu_usage = random.uniform(30, 75)
    memory_usage = random.uniform(35, 70)
    disk_usage = random.uniform(40, 70)
    
    # Create alerts based on thresholds
    high_cpu = cpu_usage > 70
    high_memory = memory_usage > 70
    high_disk = disk_usage > 80
    scaling_needed = (cpu_usage > 65 and memory_usage > 65)
    
    # Generate historical data
    historical_data = []
    now = int(time.time() * 1000)
    for i in range(24):
        historical_data.append({
            "timestamp": now - (23 - i) * 15 * 60 * 1000,  # 15 minute intervals
            "cpu_usage": 25 + random.random() * 40,
            "memory_usage": 30 + random.random() * 45,
            "requests_per_minute": 80 + random.random() * 120,
            "active_users": 15 + random.random() * 35
        })
    
    response_data = {
        "metrics": {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage,
            "network": {
                "requests_per_minute": random.uniform(80, 200),
                "bandwidth_usage_kbps": random.uniform(500, 1500)
            },
            "instances": {
                "total": random.randint(3, 10),
                "active": random.randint(1, 3)
            },
            "historical_data": historical_data
        },
        "alerts": {
            "high_cpu_usage": high_cpu,
            "high_memory_usage": high_memory,
            "high_disk_usage": high_disk,
            "instance_scaling_needed": scaling_needed,
            "message": "Resource utilization is high, consider scaling up" if (high_cpu or high_memory or high_disk) else None
        }
    }
    
    return response_data

@router.get("/firebase-health-check")
def check_firebase_health_endpoint():
    """Check the health status of Firebase connection."""
    return check_firebase_health()

@router.post("/deploy", response_model=DeploymentResponse)
def deploy_to_firebase(request: DeploymentRequest):
    """Deploy code, data, or configuration between Databutton and Firebase."""
    try:
        # Generate a unique deployment ID
        deployment_id = str(uuid.uuid4())
        
        # Store the deployment information in Databutton storage
        deployment_info = {
            "id": deployment_id,
            "type": request.type,
            "direction": request.direction,
            "project_id": request.project_id,
            "environment": request.environment,
            "auto_sync": request.auto_sync,
            "status": DeploymentStatus.PENDING,
            "progress": 0,
            "created_at": time.time(),
            "updated_at": time.time(),
            "message": "Deployment initialized",
            "error": None
        }
        
        # Store the deployment in Databutton storage
        storage_key = f"firebase_deployment_{deployment_id}"
        db.storage.json.put(storage_key, deployment_info)
        
        # In a real implementation, we would start a background task to handle the deployment
        # For now, we'll just return the deployment ID
        
        return DeploymentResponse(
            deployment_id=deployment_id,
            status=DeploymentStatus.PENDING,
            message="Deployment initiated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate deployment: {str(e)}")

@router.get("/deployment/{deployment_id}/status", response_model=DeploymentStatusResponse)
def get_deployment_status(deployment_id: str):
    """Get the status of a deployment operation."""
    try:
        # Retrieve the deployment information from Databutton storage
        storage_key = f"firebase_deployment_{deployment_id}"
        deployment_info = db.storage.json.get(storage_key, None)
        
        if not deployment_info:
            raise HTTPException(status_code=404, detail=f"Deployment {deployment_id} not found")
        
        # In a real implementation, we would check the actual status of the deployment
        # For demo purposes, we'll simulate progress
        progress = deployment_info.get("progress", 0)
        status = deployment_info.get("status", DeploymentStatus.PENDING)
        
        # Simulate progress for demo purposes
        if status == DeploymentStatus.PENDING:
            # Change to in-progress
            status = DeploymentStatus.IN_PROGRESS
            progress = 10
        elif status == DeploymentStatus.IN_PROGRESS:
            # Increase progress
            progress += 20
            if progress >= 100:
                progress = 100
                status = DeploymentStatus.COMPLETED
        
        # Update the deployment info
        deployment_info["status"] = status
        deployment_info["progress"] = progress
        deployment_info["updated_at"] = time.time()
        
        # Store the updated info
        db.storage.json.put(storage_key, deployment_info)
        
        return DeploymentStatusResponse(
            deployment_id=deployment_id,
            status=status,
            progress=progress,
            error=deployment_info.get("error")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deployment status: {str(e)}")

@router.get("/deployments", response_model=list)
def get_deployment_history():
    """Get the history of deployments."""
    try:
        # List all deployment files in storage
        # In a real implementation, we would use a database to store and query deployments
        deployments = []
        
        # Mock implementation for demo purposes
        # Return some sample deployment history
        return [
            {
                "id": "dep-001",
                "timestamp": time.time() - 3600,
                "status": "completed",
                "source": "databutton",
                "target": "firebase",
                "type": "code",
                "details": "Authentication and user management components"
            },
            {
                "id": "dep-002",
                "timestamp": time.time() - 7200,
                "status": "failed",
                "source": "databutton",
                "target": "firebase",
                "type": "data",
                "details": "User profile data migration failed: schema mismatch"
            },
            {
                "id": "dep-003",
                "timestamp": time.time() - 10800,
                "status": "completed",
                "source": "firebase",
                "target": "databutton",
                "type": "config",
                "details": "Firebase authentication settings"
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deployment history: {str(e)}")

@router.get("/deployment-config")
def get_deployment_config():
    """Get deployment configuration."""
    try:
        # In a real implementation, we would retrieve this from a database or configuration file
        return {
            "project_id": "legacy-vault-firebase",
            "environment": "development",
            "auto_sync": False,
            "firebase_region": "us-central1",
            "supported_features": {
                "code_deployment": True,
                "data_migration": True,
                "config_sync": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get deployment config: {str(e)}")

@router.post("/deployment-config")
def update_deployment_config(config: dict = Body(...)):
    """Update deployment configuration."""
    try:
        # In a real implementation, we would update the configuration in a database or file
        # For demo purposes, we'll just echo back the config with a success message
        return {
            "status": "success",
            "message": "Deployment configuration updated successfully",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update deployment config: {str(e)}")

@router.get("/firebase-health")
def check_firebase_health():
    """Check the health of Firebase services."""
    try:
        # Check Firestore connection
        firestore_healthy = True
        try:
            # Create a local Firestore client for this function
            db_client = firestore.client()
            db_client.collection("__health_check__").document("test").set({"timestamp": firestore.SERVER_TIMESTAMP})
            db_client.collection("__health_check__").document("test").delete()
        except Exception as e:
            firestore_healthy = False
            firestore_error = str(e)
        
        # Check Authentication
        auth_healthy = True
        try:
            auth.list_users(limit=1)
        except Exception as e:
            auth_healthy = False
            auth_error = str(e)
        
        # Return health status
        return {
            "status": "healthy" if (firestore_healthy and auth_healthy) else "unhealthy",
            "firestore": {
                "status": "healthy" if firestore_healthy else "unhealthy",
                "error": None if firestore_healthy else firestore_error
            },
            "authentication": {
                "status": "healthy" if auth_healthy else "unhealthy",
                "error": None if auth_healthy else auth_error
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
