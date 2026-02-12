from fastapi import Header, HTTPException, Depends, APIRouter
from enum import Enum
from typing import Optional
from jose import jwt, JWTError
import os
from pydantic import BaseModel

# Create a router
router = APIRouter()

# Define roles for the application
class Role(str, Enum):
    ADMIN = "admin" # Retained for general admin, maps to GLOBAL_ADMIN if needed or can be distinct
    REGISTRAR = "registrar"
    MIDWIFE = "midwife"
    USER = "user"
    ANONYMOUS = "anonymous"

    # Roles from user_roles API
    GLOBAL_ADMIN = "GLOBAL_ADMIN"  # Full control over entire system
    VAULT_MANAGER = "VAULT_MANAGER"  # Manages specific vaults
    SECURITY_AUDIT = "SECURITY_AUDIT"  # Security & audit role
    FINANCE_MANAGER = "FINANCE_MANAGER"  # Manages financial tools
    COMMS_MANAGER = "COMMS_MANAGER"  # Manages communications
    CONTENT_MANAGER = "CONTENT_MANAGER"  # Manages content and media
    FAMILY_ADMIN = "FAMILY_ADMIN"  # Manages family profiles and trusts
    # USER role is already present

    # Beneficiary roles from user_roles API
    BUB = "BUB"  # Passive accumulation role (ages 0-16)
    BRAT = "BRAT"  # Receiving transfers role (ages 16-18/19)
    BXX = "BXX"  # Active beneficiary role (ages 18+)
    TRUST_CONTRIBUTOR = "TRUST_CONTRIBUTOR"  # Trust contributors

# Simple JWT secret (in production, store this securely)
JWT_SECRET = os.environ.get("JWT_SECRET", "hardcard-development-secret")
JWT_ALGORITHM = "HS256"

class JWTPayload(BaseModel):
    """JWT payload structure"""
    sub: str  # Subject (user ID)
    role: Role  # User role
    exp: Optional[int] = None  # Expiration time

class AuthActor(BaseModel):
    """Actor with role information"""
    id: str
    role: Role

# Role-based access control matrix for event tag operations
role_permissions = {
    # Format: {endpoint_name: {http_method: [allowed_roles]}}
    "create_identity_event_tag": {
        "POST": [Role.ADMIN, Role.REGISTRAR, Role.MIDWIFE]
    },
    "get_identity_events": {
        "GET": [Role.ADMIN, Role.REGISTRAR, Role.MIDWIFE, Role.USER]
    },
    "get_event_tag": {
        "GET": [Role.ADMIN, Role.REGISTRAR, Role.MIDWIFE, Role.USER]
    },
    "verify_event_tag": {
        "GET": [Role.ADMIN, Role.REGISTRAR, Role.MIDWIFE, Role.USER]
    },
    "get_event_provenance": {
        "GET": [Role.ADMIN, Role.REGISTRAR, Role.USER]
    }
}

def get_actor_from_token(authorization: Optional[str] = Header(None)) -> AuthActor:
    """Extract actor information from JWT token"""
    if not authorization:
        return AuthActor(id="anonymous", role=Role.ANONYMOUS)
        
    try:
        # Extract token from the Authorization header
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return AuthActor(id="anonymous", role=Role.ANONYMOUS)
            
        # Decode and validate the token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        jwt_payload = JWTPayload(**payload)
        
        return AuthActor(id=jwt_payload.sub, role=jwt_payload.role)
    except (JWTError, ValueError):
        return AuthActor(id="anonymous", role=Role.ANONYMOUS)

def check_role_permission(endpoint_name: str, method: str, actor_role: Role) -> bool:
    """Check if a role has permission for an operation"""
    if endpoint_name not in role_permissions:
        return False
        
    if method not in role_permissions[endpoint_name]:
        return False
        
    return actor_role in role_permissions[endpoint_name][method]

async def require_role(endpoint_name: str, method: str, actor: AuthActor = Depends(get_actor_from_token)) -> AuthActor:
    """Dependency that enforces role-based access control"""
    if not check_role_permission(endpoint_name, method, actor.role):
        raise HTTPException(
            status_code=403,
            detail=f"Actor with role {actor.role} is not authorized for this operation"
        )
    return actor
