from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import databutton as db
import json

# --- Router Setup ---
router = APIRouter(prefix="/mcp-credential-types", tags=["MCP Credential Types"])

# --- Storage Configuration ---
STORAGE_KEY = "mcp_credential_types_store.json"

# --- Pydantic Models ---

class CredentialTypeBase(BaseModel):
    """Base model for a credential type, used for creation and updates."""
    name: str = Field(..., description="The unique name of the credential type.")
    description: str = Field(..., description="A short description of what this credential type represents.")
    schema_definition: Dict[str, Any] = Field(..., description="A JSON schema defining the structure of the credential data.")

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty.')
        return v

class CredentialType(CredentialTypeBase):
    """Full credential type model, including system-generated fields."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the credential type.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the credential type was created.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the last update.")

class CredentialTypeResponse(CredentialType):
    """Response model for a single credential type."""
    pass

class CredentialTypeCreate(CredentialTypeBase):
    """Model for creating a new credential type."""
    pass

# --- Storage Helper Functions ---

def get_credential_types_store() -> Dict[str, Dict]:
    """Retrieves the credential types store from db.storage.json."""
    try:
        return db.storage.json.get(STORAGE_KEY)
    except FileNotFoundError:
        return {}

def save_credential_types_store(store: Dict[str, Dict]):
    """Saves the credential types store to db.storage.json."""
    db.storage.json.put(STORAGE_KEY, store)

def _serialize_model(model_instance: BaseModel) -> Dict[str, Any]:
    """Helper to serialize Pydantic models with datetime objects to JSON-compatible dicts."""
    return json.loads(model_instance.json())

@router.post("/", response_model=CredentialTypeResponse, status_code=status.HTTP_201_CREATED)
def create_credential_type(payload: CredentialTypeCreate):
    """
    Creates a new MCP credential type.
    """
    store = get_credential_types_store()
    
    # Check for duplicate name
    for type_dict in store.values():
        if type_dict.get('name') == payload.name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A credential type with the name '{payload.name}' already exists."
            )
            
    new_credential_type = CredentialType(**payload.dict())
    
    store[new_credential_type.id] = _serialize_model(new_credential_type)
    save_credential_types_store(store)
    
    return new_credential_type




@router.get("/", response_model=List[CredentialTypeResponse])
def list_credential_types(skip: int = 0, limit: int = 100):
    """
    Retrieves a list of all MCP credential types.
    """
    store = get_credential_types_store()
    all_types = [CredentialTypeResponse(**data) for data in store.values()]
    return all_types[skip : skip + limit]

@router.get("/{credential_type_id}", response_model=CredentialTypeResponse)
def get_credential_type(credential_type_id: str):
    """
    Retrieves a single MCP credential type by its ID.
    """
    store = get_credential_types_store()
    if credential_type_id not in store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credential type with ID '{credential_type_id}' not found."
        )
    return CredentialTypeResponse(**store[credential_type_id])

@router.put("/{credential_type_id}", response_model=CredentialTypeResponse)
def update_credential_type(credential_type_id: str, payload: CredentialTypeCreate):
    """
    Updates an existing MCP credential type.
    """
    store = get_credential_types_store()
    if credential_type_id not in store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credential type with ID '{credential_type_id}' not found."
        )

    # Check for name collision on update
    for type_id, type_dict in store.items():
        if type_id != credential_type_id and type_dict.get('name') == payload.name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another credential type with the name '{payload.name}' already exists."
            )

    existing_data = store[credential_type_id]
    update_data = CredentialType(**existing_data).copy(update=payload.dict(exclude_unset=True))
    update_data.updated_at = datetime.utcnow()

    store[credential_type_id] = _serialize_model(update_data)
    save_credential_types_store(store)
    
    return update_data

@router.delete("/{credential_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_credential_type(credential_type_id: str):
    """
    Deletes an MCP credential type.
    """
    store = get_credential_types_store()
    if credential_type_id not in store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credential type with ID '{credential_type_id}' not found."
        )
    
    del store[credential_type_id]
    save_credential_types_store(store)
    
    return None # Return None for 204 No Content



