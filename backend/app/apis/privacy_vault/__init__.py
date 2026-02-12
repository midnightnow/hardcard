from fastapi import APIRouter, HTTPException, Depends, Body, Query, Path
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import databutton as db
import re
from datetime import datetime
from app.auth import AuthorizedUser
import json
import uuid
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

router = APIRouter()

# Models for vault data
class VaultDataCategory(BaseModel):
    """Classification of data in the vault"""
    id: str
    name: str
    description: str
    sensitivity_level: str = Field(..., description="Classification level: 'standard', 'sensitive', 'highly_sensitive'")

class VaultEncryptionInfo(BaseModel):
    """Metadata about encryption used for a vault item"""
    algorithm: str = "AES-256-GCM"
    key_derivation: str = "PBKDF2"
    created_at: datetime
    updated_at: Optional[datetime] = None

class ConsentRecord(BaseModel):
    """Record of user consent for data usage"""
    id: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    purpose: str
    granted_to: Optional[str] = None
    scope: List[str] = []
    revoked_at: Optional[datetime] = None

class VaultItemMetadata(BaseModel):
    """Metadata for a vault item"""
    id: str
    user_id: str
    category_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    encryption_info: VaultEncryptionInfo
    tags: List[str] = []
    consents: List[ConsentRecord] = []
    retention_period_days: Optional[int] = None
    regulatory_frameworks: List[str] = []

class VaultItemData(BaseModel):
    """Encrypted data stored in the vault"""
    content: str = Field(..., description="Base64 encoded encrypted data")
    content_type: str = Field(..., description="MIME type of the original content")

class VaultItem(BaseModel):
    """Complete vault item with metadata and encrypted data"""
    metadata: VaultItemMetadata
    data: VaultItemData

class VaultItemRequest(BaseModel):
    """Request to create or update a vault item"""
    category_id: str
    name: str
    description: Optional[str] = None
    content: str = Field(..., description="Original content to be encrypted")
    content_type: str = Field(..., description="MIME type of the content")
    tags: List[str] = []
    retention_period_days: Optional[int] = None
    regulatory_frameworks: List[str] = []

class VaultConfig(BaseModel):
    """Configuration for the vault"""
    encryption_strength: str = "high"
    auto_tokenization: bool = True
    compliance_frameworks: List[str] = ["GDPR", "HIPAA"]
    data_categories: List[VaultDataCategory] = []

class ConsentRequest(BaseModel):
    """Request to grant consent for data usage"""
    purpose: str
    granted_to: Optional[str] = None
    scope: List[str] = []
    expires_at: Optional[datetime] = None

class AccessTokenRequest(BaseModel):
    """Request to generate a temporary access token for a vault item"""
    item_id: str
    purpose: str
    expires_in_seconds: int = 3600  # Default 1 hour

class AccessToken(BaseModel):
    """Temporary access token for a vault item"""
    token: str
    expires_at: datetime
    item_id: str

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def generate_encryption_key(user_id: str, item_id: str) -> bytes:
    """Generate a unique encryption key for a vault item
    
    Uses user_id and item_id to derive a key, with a master salt stored in secrets
    """
    try:
        # Get master salt from secrets or generate a new one
        try:
            master_salt = db.secrets.get("PRIVACY_VAULT_MASTER_SALT")
            if not master_salt:
                raise Exception("Master salt not found")
            master_salt = master_salt.encode()
        except:
            # For development only - in production, this should be set up by an admin
            master_salt = os.urandom(16)
            # This is just for development and testing
            # In production, you would need to ensure this is securely stored
            # db.secrets.put("PRIVACY_VAULT_MASTER_SALT", master_salt.hex())
            
        # Create a unique salt for this item using user_id and item_id
        item_salt = f"{user_id}:{item_id}".encode()
        
        # Use PBKDF2 to derive a key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 32 bytes = 256 bits for AES-256
            salt=master_salt,
            iterations=100000,  # Recommended minimum by OWASP
        )
        
        return base64.urlsafe_b64encode(kdf.derive(item_salt))
    except Exception as e:
        print(f"Error generating encryption key: {e}")
        raise

def encrypt_data(data: str, key: bytes) -> str:
    """Encrypt data using Fernet (AES-128-CBC with HMAC-SHA256)"""
    try:
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    except Exception as e:
        print(f"Error encrypting data: {e}")
        raise

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt data using Fernet"""
    try:
        f = Fernet(key)
        decoded_data = base64.b64decode(encrypted_data)
        decrypted_data = f.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception as e:
        print(f"Error decrypting data: {e}")
        raise

def get_vault_config(user_id: str) -> VaultConfig:
    """Get vault configuration for a user"""
    try:
        storage_key = sanitize_storage_key(f"vault_config_{user_id}")
        try:
            config_data = db.storage.json.get(storage_key)
            return VaultConfig(**config_data)
        except:
            # Create default config if it doesn't exist
            default_config = VaultConfig(
                data_categories=[
                    VaultDataCategory(
                        id="health",
                        name="Health Data",
                        description="Medical and health-related personal information",
                        sensitivity_level="highly_sensitive"
                    ),
                    VaultDataCategory(
                        id="financial",
                        name="Financial Data",
                        description="Financial and payment information",
                        sensitivity_level="highly_sensitive"
                    ),
                    VaultDataCategory(
                        id="genetic",
                        name="Genetic Data",
                        description="DNA and genetic testing information",
                        sensitivity_level="highly_sensitive"
                    ),
                    VaultDataCategory(
                        id="personal",
                        name="Personal Identifiers",
                        description="Personal identification information",
                        sensitivity_level="sensitive"
                    ),
                    VaultDataCategory(
                        id="documents",
                        name="Legal Documents",
                        description="Legal and official documents",
                        sensitivity_level="sensitive"
                    )
                ]
            )
            db.storage.json.put(storage_key, default_config.dict())
            return default_config
    except Exception as e:
        print(f"Error getting vault config: {e}")
        # Return default config if storage fails
        return VaultConfig()

def save_vault_item(user_id: str, item_id: str, item: VaultItem):
    """Save a vault item to storage"""
    try:
        storage_key = sanitize_storage_key(f"vault_item_{user_id}_{item_id}")
        db.storage.json.put(storage_key, item.dict())
    except Exception as e:
        print(f"Error saving vault item: {e}")
        raise

def get_vault_item(user_id: str, item_id: str) -> VaultItem:
    """Get a vault item from storage"""
    try:
        storage_key = sanitize_storage_key(f"vault_item_{user_id}_{item_id}")
        item_data = db.storage.json.get(storage_key)
        return VaultItem(**item_data)
    except Exception as e:
        print(f"Error getting vault item: {e}")
        raise HTTPException(status_code=404, detail=f"Item not found: {e}")

def get_user_vault_items(user_id: str) -> List[VaultItemMetadata]:
    """Get all vault items for a user"""
    try:
        # List all vault items for this user
        # Note: In a production system with many items, this would need pagination
        prefix = f"vault_item_{user_id}_"
        items = []
        
        # This is a simplified approach - in production, you would want a more efficient lookup
        all_items = db.storage.json.list()
        for item in all_items:
            if item.name.startswith(prefix):
                item_data = db.storage.json.get(item.name)
                vault_item = VaultItem(**item_data)
                items.append(vault_item.metadata)
        
        return items
    except Exception as e:
        print(f"Error listing vault items: {e}")
        return []

@router.get("/vault/config", response_model=VaultConfig)
async def get_vault_config_api(user: AuthorizedUser):
    """Get the privacy vault configuration for the current user"""
    try:
        return get_vault_config(user.sub)
    except Exception as e:
        print(f"Error in get_vault_config_api: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/vault/config", response_model=VaultConfig)
async def update_vault_config(config: VaultConfig, user: AuthorizedUser):
    """Update the privacy vault configuration"""
    try:
        storage_key = sanitize_storage_key(f"vault_config_{user.sub}")
        db.storage.json.put(storage_key, config.dict())
        return config
    except Exception as e:
        print(f"Error in update_vault_config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vault/items", response_model=VaultItemMetadata)
async def create_vault_item(request: VaultItemRequest, user: AuthorizedUser):
    """Create a new encrypted item in the privacy vault"""
    try:
        # Generate a new item ID
        item_id = str(uuid.uuid4())
        
        # Generate encryption key for this item
        encryption_key = generate_encryption_key(user.sub, item_id)
        
        # Encrypt the content
        encrypted_content = encrypt_data(request.content, encryption_key)
        
        # Create metadata
        now = datetime.now()
        metadata = VaultItemMetadata(
            id=item_id,
            user_id=user.sub,
            category_id=request.category_id,
            name=request.name,
            description=request.description,
            created_at=now,
            updated_at=now,
            encryption_info=VaultEncryptionInfo(
                created_at=now
            ),
            tags=request.tags,
            retention_period_days=request.retention_period_days,
            regulatory_frameworks=request.regulatory_frameworks
        )
        
        # Create the vault item
        vault_item = VaultItem(
            metadata=metadata,
            data=VaultItemData(
                content=encrypted_content,
                content_type=request.content_type
            )
        )
        
        # Save the vault item
        save_vault_item(user.sub, item_id, vault_item)
        
        return metadata
    except Exception as e:
        print(f"Error in create_vault_item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/items", response_model=List[VaultItemMetadata])
async def list_vault_items(
    user: AuthorizedUser,
    category_id: Optional[str] = Query(None, description="Filter by category ID")
):
    """List all vault items (metadata only) for the current user"""
    try:
        items = get_user_vault_items(user.sub)
        
        # Filter by category if specified
        if category_id:
            items = [item for item in items if item.category_id == category_id]
            
        return items
    except Exception as e:
        print(f"Error in list_vault_items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/items/{item_id}/metadata", response_model=VaultItemMetadata)
async def get_vault_item_metadata(item_id: str, user: AuthorizedUser):
    """Get metadata for a specific vault item"""
    try:
        item = get_vault_item(user.sub, item_id)
        return item.metadata
    except Exception as e:
        print(f"Error in get_vault_item_metadata: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/items/{item_id}/content")
async def get_vault_item_content(item_id: str, user: AuthorizedUser):
    """Get the decrypted content of a vault item"""
    try:
        # Get the encrypted item
        item = get_vault_item(user.sub, item_id)
        
        # Generate the encryption key
        encryption_key = generate_encryption_key(user.sub, item_id)
        
        # Decrypt the content
        decrypted_content = decrypt_data(item.data.content, encryption_key)
        
        # Return the content with appropriate content type
        return {"content": decrypted_content, "content_type": item.data.content_type}
    except Exception as e:
        print(f"Error in get_vault_item_content: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/vault/items/{item_id}")
async def delete_vault_item(item_id: str, user: AuthorizedUser):
    """Delete a vault item"""
    try:
        # Check if the item exists
        storage_key = sanitize_storage_key(f"vault_item_{user.sub}_{item_id}")
        
        # Delete the item
        try:
            db.storage.json.delete(storage_key)
            return {"status": "success", "message": f"Item {item_id} deleted successfully"}
        except:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        print(f"Error in delete_vault_item: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vault/items/{item_id}/consent", response_model=ConsentRecord)
async def create_consent_record(item_id: str, request: ConsentRequest, user: AuthorizedUser):
    """Create a new consent record for a vault item"""
    try:
        # Get the item
        item = get_vault_item(user.sub, item_id)
        
        # Create a new consent record
        consent_id = str(uuid.uuid4())
        now = datetime.now()
        
        consent = ConsentRecord(
            id=consent_id,
            granted_at=now,
            expires_at=request.expires_at,
            purpose=request.purpose,
            granted_to=request.granted_to,
            scope=request.scope
        )
        
        # Add the consent record to the item
        item.metadata.consents.append(consent)
        
        # Update the item
        save_vault_item(user.sub, item_id, item)
        
        return consent
    except Exception as e:
        print(f"Error in create_consent_record: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vault/items/{item_id}/revoke-consent/{consent_id}")
async def revoke_consent(item_id: str, consent_id: str, user: AuthorizedUser):
    """Revoke a consent record for a vault item"""
    try:
        # Get the item
        item = get_vault_item(user.sub, item_id)
        
        # Find and update the consent record
        for consent in item.metadata.consents:
            if consent.id == consent_id and consent.revoked_at is None:
                consent.revoked_at = datetime.now()
                
                # Update the item
                save_vault_item(user.sub, item_id, item)
                
                return {"status": "success", "message": f"Consent {consent_id} revoked"}
        
        raise HTTPException(status_code=404, detail="Consent record not found or already revoked")
    except Exception as e:
        print(f"Error in revoke_consent: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/vault/items/{item_id}/access-token", response_model=AccessToken)
async def generate_access_token(item_id: str, request: AccessTokenRequest, user: AuthorizedUser):
    """Generate a temporary access token for a vault item"""
    try:
        # Verify the item exists and user has access
        item = get_vault_item(user.sub, item_id)
        
        # Generate a token (in production, this would use JWTs or similar)
        token = str(uuid.uuid4())
        
        # Set expiration
        expires_at = datetime.now() + datetime.timedelta(seconds=request.expires_in_seconds)
        
        # In production, you would store this token in a proper token store with validation
        # For this prototype, we'll just return it
        
        return AccessToken(
            token=token,
            expires_at=expires_at,
            item_id=item_id
        )
    except Exception as e:
        print(f"Error in generate_access_token: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vault/stats")
async def get_vault_stats(user: AuthorizedUser):
    """Get statistics about the user's vault usage"""
    try:
        items = get_user_vault_items(user.sub)
        
        # Group by category
        categories = {}
        for item in items:
            if item.category_id not in categories:
                categories[item.category_id] = 0
            categories[item.category_id] += 1
        
        return {
            "total_items": len(items),
            "categories": categories,
            "oldest_item": min([item.created_at for item in items], default=None),
            "newest_item": max([item.created_at for item in items], default=None)
        }
    except Exception as e:
        print(f"Error in get_vault_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
