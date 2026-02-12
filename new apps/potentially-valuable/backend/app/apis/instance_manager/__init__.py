import uuid
import time
from enum import Enum
from typing import List, Optional, Dict, Literal # Added Literal
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status, Body
import databutton as db
import re

router = APIRouter(prefix="/api/instances", tags=["Instance Management"])

# --- Pydantic Models ---

class InstanceStatus(str, Enum):
    PENDING = "PENDING"
    PROVISIONING = "PROVISIONING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    DELETING = "DELETING"
    ERROR = "ERROR"
    DELETED = "DELETED" # Added for completeness

class InstanceResourceConfig(BaseModel):
    cpu: int = Field(1, description="Number of CPU cores")
    ram_mb: int = Field(512, description="RAM in MB")
    storage_gb: int = Field(10, description="Storage in GB")
    # In the future, this could include modules, kernel versions, etc.

class InstanceBase(BaseModel):
    name: str = Field(..., description="User-defined name for the instance", min_length=3, max_length=50)
    resource_config: InstanceResourceConfig = Field(default_factory=InstanceResourceConfig)
    modules: List[str] = Field(default=None, description="Optional list of modules to install")
    # Potentially: user_id: str when auth is integrated

class InstanceCreate(InstanceBase):
    pass

class Instance(InstanceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique instance ID")
    status: InstanceStatus = Field(InstanceStatus.PENDING, description="Current status of the instance")
    created_at: float = Field(default_factory=time.time, description="Timestamp of creation")
    updated_at: float = Field(default_factory=time.time, description="Timestamp of last update")
    status_message: Optional[str] = Field(None, description="Optional message related to the current status, e.g., error details")
    # internal_ip: Optional[str] = None # For later when simulation is more detailed
    # public_ip: Optional[str] = None

class InstanceStatusUpdate(BaseModel):
    status: Literal[InstanceStatus.RUNNING, InstanceStatus.STOPPED] # For now, only allow starting/stopping via this
    # Potentially 'RESTART' could map to STOP then START logic

# --- Helper Functions ---

INSTANCES_DB_KEY = "os1000_instances_data" # Key for db.storage.json

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_all_instances_from_storage() -> Dict[str, Instance]:
    """Placeholder for Firestore: Retrieves all instances from db.storage.json"""
    # NOTE: This is a placeholder. Replace with actual Firestore logic.
    # For Firebase/Firestore, this would involve querying a collection.
    # Ensure FIREBASE_ADMIN_SDK is set up and initialized.
    # from firebase_admin import firestore
    # firestore_db = firestore.client()
    # instances_ref = firestore_db.collection('os1000_instances')
    # docs = instances_ref.stream()
    # return {doc.id: Instance(**doc.to_dict()) for doc in docs}
    
    raw_instances = db.storage.json.get(INSTANCES_DB_KEY, default={})
    return {instance_id: Instance(**data) for instance_id, data in raw_instances.items()}

def save_instance_to_storage(instance: Instance):
    """Placeholder for Firestore: Saves a single instance to db.storage.json"""
    # NOTE: This is a placeholder. Replace with actual Firestore logic.
    # firestore_db.collection('os1000_instances').document(instance.id).set(instance.model_dump())
    
    all_instances = get_all_instances_from_storage()
    all_instances[instance.id] = instance
    db.storage.json.put(INSTANCES_DB_KEY, {k: v.model_dump() for k, v in all_instances.items()})

def delete_instance_from_storage(instance_id: str):
    """Placeholder for Firestore: Deletes an instance from db.storage.json"""
    # NOTE: This is a placeholder. Replace with actual Firestore logic.
    # firestore_db.collection('os1000_instances').document(instance_id).delete()

    all_instances = get_all_instances_from_storage()
    if instance_id in all_instances:
        del all_instances[instance_id]
        db.storage.json.put(INSTANCES_DB_KEY, {k: v.model_dump() for k, v in all_instances.items()})

# --- Authentication Placeholder ---

async def get_current_user_placeholder():
    """
    Placeholder for Firebase Authentication.
    In a real scenario, this would verify the Firebase ID token from the Authorization header.
    Example:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import OAuth2PasswordBearer
    # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # if you had a token URL
    # async def get_current_user(token: str = Depends(oauth2_scheme)):
    #   try:
    #     decoded_token = firebase_admin.auth.verify_id_token(token)
    #     return decoded_token['uid']
    #   except firebase_admin.auth.FirebaseAuthError as e:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    """
    # print("WARNING: Authentication is currently disabled/placeholder.")
    # return "test_user_id" # Simulate a user ID
    # For now, no auth for easier initial development as per plan
    pass


# --- API Endpoints ---

@router.post("", response_model=Instance, status_code=status.HTTP_201_CREATED)
async def create_instance(
    instance_data: InstanceCreate = Body(...),
    # current_user_id: str = Depends(get_current_user_placeholder) # TODO: Enable when auth ready
):
    """
    Create a new simulated OS instance.
    Simulates provisioning time.
    Placeholder for authentication and Firestore integration.
    """
    print(f"Received request to create instance: {instance_data.name}")
    
    # Check for duplicate names (basic check for now)
    existing_instances = get_all_instances_from_storage()
    if any(inst.name == instance_data.name for inst in existing_instances.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An instance with the name '{instance_data.name}' already exists."
        )

    new_instance = Instance(
        **instance_data.model_dump(),
        # id will be auto-generated by pydantic default_factory
        status=InstanceStatus.PENDING,
        created_at=time.time(),
        updated_at=time.time(),
        status_message="Instance creation initiated."
    )
    print(f"New instance {new_instance.id} ({new_instance.name}) created with PENDING status.")
    save_instance_to_storage(new_instance)

    # Simulate provisioning delay
    try:
        # Stage 1: Provisioning
        new_instance.status = InstanceStatus.PROVISIONING
        new_instance.status_message = "Resources are being provisioned..."
        new_instance.updated_at = time.time()
        save_instance_to_storage(new_instance)
        print(f"Instance {new_instance.id} status: PROVISIONING")
        time.sleep(3)  # Simulate provisioning time (e.g., 3-8 seconds)

        # Stage 2: Running
        new_instance.status = InstanceStatus.RUNNING
        new_instance.status_message = "Instance is now running."
        # new_instance.internal_ip = f"10.0.1.{len(existing_instances) + 1}" # Example internal IP
        new_instance.updated_at = time.time()
        save_instance_to_storage(new_instance)
        print(f"Instance {new_instance.id} status: RUNNING. Provisioning complete.")

    except Exception as e:
        print(f"Error during provisioning for instance {new_instance.id}: {str(e)}")
        new_instance.status = InstanceStatus.ERROR
        new_instance.status_message = f"Failed during provisioning: {str(e)}"
        new_instance.updated_at = time.time()
        save_instance_to_storage(new_instance)
        # Depending on desired behavior, we might re-raise or return the error state
        # For now, the instance will be in ERROR state and client will get it upon next GET
        # Or we can raise an HTTPException here as well if creation itself is considered failed

    return new_instance


@router.get("", response_model=List[Instance])
async def list_instances(
    # current_user_id: str = Depends(get_current_user_placeholder) # TODO: Enable when auth ready
):
    """
    List all simulated OS instances.
    Placeholder for authentication (would filter by user_id).
    """
    print("Received request to list all instances.")
    all_instances = get_all_instances_from_storage()
    # When auth is integrated, this would filter by user_id:
    # user_instances = [inst for inst in all_instances.values() if inst.user_id == current_user_id]
    # For now, returning all:
    return list(all_instances.values())


@router.get("/{instance_id}", response_model=Instance)
async def get_instance(
    instance_id: str,
    # current_user_id: str = Depends(get_current_user_placeholder) # TODO: Enable when auth ready
):
    """
    Get details for a specific simulated OS instance.
    Placeholder for authentication (would check if user owns instance).
    """
    print(f"Received request to get instance: {instance_id}")
    all_instances = get_all_instances_from_storage()
    instance = all_instances.get(instance_id)

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance with ID '{instance_id}' not found."
        )
    
    # TODO: When auth is integrated, check if current_user_id matches instance.user_id
    # if instance.user_id != current_user_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="User does not have permission to access this instance."
    #     )
        
    return instance


@router.put("/{instance_id}/status", response_model=Instance)
async def update_instance_status(
    instance_id: str,
    status_update: InstanceStatusUpdate = Body(...),
    # current_user_id: str = Depends(get_current_user_placeholder) # TODO: Enable when auth ready
):
    """
    Update the status of a simulated OS instance (e.g., start, stop).
    Simulates operation time.
    Placeholder for authentication.
    """
    print(f"Received request to update status for instance {instance_id} to {status_update.status.value}")
    all_instances = get_all_instances_from_storage()
    instance = all_instances.get(instance_id)

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance with ID '{instance_id}' not found."
        )

    # TODO: When auth is integrated, check ownership
    # if instance.user_id != current_user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    current_status = instance.status
    target_status = status_update.status

    if current_status == target_status:
        instance.status_message = f"Instance is already {current_status.value}."
        instance.updated_at = time.time()
        save_instance_to_storage(instance) # Save even if just message change
        return instance

    # Simulate operation delay and update status
    try:
        if target_status == InstanceStatus.RUNNING:
            if current_status not in [InstanceStatus.STOPPED, InstanceStatus.PENDING, InstanceStatus.ERROR]: # Can start from STOPPED, PENDING or ERROR
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot start instance from {current_status.value} state.")
            instance.status = InstanceStatus.PROVISIONING # Or "STARTING"
            instance.status_message = "Instance is starting..."
            print(f"Instance {instance.id} status: STARTING/PROVISIONING")
            instance.updated_at = time.time()
            save_instance_to_storage(instance)
            time.sleep(2)  # Simulate start-up time
            instance.status = InstanceStatus.RUNNING
            instance.status_message = "Instance is now running."
            print(f"Instance {instance.id} status: RUNNING")
        
        elif target_status == InstanceStatus.STOPPED:
            if current_status != InstanceStatus.RUNNING:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cannot stop instance from {current_status.value} state. Must be RUNNING.")
            instance.status = InstanceStatus.STOPPING
            instance.status_message = "Instance is stopping..."
            print(f"Instance {instance.id} status: STOPPING")
            instance.updated_at = time.time()
            save_instance_to_storage(instance)
            time.sleep(2)  # Simulate stopping time
            instance.status = InstanceStatus.STOPPED
            instance.status_message = "Instance is stopped."
            print(f"Instance {instance.id} status: STOPPED")
        
        else:
            # This else block should ideally not be reached due to InstanceStatusUpdate model restriction
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported status transition to {target_status.value}.")

        instance.updated_at = time.time()
        save_instance_to_storage(instance)

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        print(f"Error during status update for instance {instance.id}: {str(e)}")
        instance.status = InstanceStatus.ERROR
        instance.status_message = f"Failed during status update: {str(e)}"
        instance.updated_at = time.time()
        save_instance_to_storage(instance)
        # Optionally raise an HTTPException here if the operation itself is considered failed
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}") from e

    return instance


@router.delete("/{instance_id}", response_model=Instance, status_code=status.HTTP_200_OK)
async def delete_instance(
    instance_id: str,
    # current_user_id: str = Depends(get_current_user_placeholder) # TODO: Enable when auth ready
):
    """
    Delete a simulated OS instance.
    Simulates deletion time and sets status to DELETED.
    Placeholder for authentication.
    """
    print(f"Received request to delete instance: {instance_id}")
    all_instances = get_all_instances_from_storage()
    instance = all_instances.get(instance_id)

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instance with ID '{instance_id}' not found."
        )

    # TODO: When auth is integrated, check ownership
    # if instance.user_id != current_user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if instance.status == InstanceStatus.DELETED:
        instance.status_message = "Instance is already deleted."
        # No need to save again if already marked deleted in a persistent way
        # but with current db.storage.json, re-saving is harmless
        save_instance_to_storage(instance)
        return instance
        
    if instance.status == InstanceStatus.DELETING:
        instance.status_message = "Instance is already being deleted."
        save_instance_to_storage(instance)
        return instance # Or perhaps a 202 Accepted if it's a long async process

    # original_status_before_delete = instance.status # Kept for reference if complex rollback needed later
    instance.status = InstanceStatus.DELETING
    instance.status_message = "Instance is being deleted..."
    instance.updated_at = time.time()
    save_instance_to_storage(instance)
    print(f"Instance {instance.id} status: DELETING")

    # Simulate deletion time
    try:
        time.sleep(2)  # Simulate time it takes to delete resources
        
        # Option 1: Actually remove from our db.storage.json
        # delete_instance_from_storage(instance_id)
        # print(f"Instance {instance.id} physically deleted from storage.")
        # return Response(status_code=status.HTTP_204_NO_CONTENT) # If actually deleting

        # Option 2: Mark as DELETED (as per task description for later state checks)
        instance.status = InstanceStatus.DELETED
        instance.status_message = "Instance has been deleted."
        instance.updated_at = time.time()
        save_instance_to_storage(instance)
        print(f"Instance {instance.id} status: DELETED (marked as deleted)")
        return instance

    except Exception as e:
        print(f"Error during deletion for instance {instance.id}: {str(e)}")
        # Revert to a consistent error state if deletion fails mid-way
        instance.status = InstanceStatus.ERROR # Or the original status before attempting delete
        instance.status_message = f"Failed during deletion: {str(e)}"
        instance.updated_at = time.time()
        save_instance_to_storage(instance)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during deletion: {str(e)}") from e


# TODO: Implement all other endpoints:
# (All core endpoints for this task are now implemented)

