"""
Coaching Authentication & Authorization

Role-based access control system for the coaching platform with
granular permissions for coaches, clients, teams, and administrators.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Optional, Set
from enum import Enum
import jwt
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import auth as firebase_auth, firestore

# Security scheme
security = HTTPBearer()

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    COACH = "coach"
    SENIOR_COACH = "senior_coach"
    CLIENT = "client"
    TEAM_MEMBER = "team_member"
    TEAM_LEAD = "team_lead"
    OBSERVER = "observer"

class Permission(str, Enum):
    # Coaching Sessions
    CREATE_SESSION = "create_session"
    VIEW_SESSION = "view_session"
    EDIT_SESSION = "edit_session"
    DELETE_SESSION = "delete_session"
    
    # Client Management
    CREATE_CLIENT = "create_client"
    VIEW_CLIENT = "view_client"
    EDIT_CLIENT = "edit_client"
    DELETE_CLIENT = "delete_client"
    
    # Analytics & Insights
    VIEW_ANALYTICS = "view_analytics"
    VIEW_AI_INSIGHTS = "view_ai_insights"
    EXPORT_DATA = "export_data"
    
    # Framework Management
    MANAGE_FRAMEWORKS = "manage_frameworks"
    VIEW_FRAMEWORK_PROGRESS = "view_framework_progress"
    
    # Team Collaboration
    CREATE_TEAM = "create_team"
    MANAGE_TEAM = "manage_team"
    VIEW_TEAM = "view_team"
    
    # Administrative
    MANAGE_USERS = "manage_users"
    VIEW_SYSTEM_ANALYTICS = "view_system_analytics"
    CONFIGURE_SYSTEM = "configure_system"

class CoachingUser(BaseModel):
    uid: str
    email: str
    role: UserRole
    display_name: Optional[str] = None
    organization_id: Optional[str] = None
    assigned_clients: List[str] = []
    team_memberships: List[str] = []
    permissions: Set[Permission] = set()
    created_at: datetime
    last_active: datetime
    is_active: bool = True

class RolePermissions:
    """Define permissions for each role"""
    
    ROLE_PERMISSION_MAP = {
        UserRole.SUPER_ADMIN: {
            Permission.CREATE_SESSION, Permission.VIEW_SESSION, Permission.EDIT_SESSION, Permission.DELETE_SESSION,
            Permission.CREATE_CLIENT, Permission.VIEW_CLIENT, Permission.EDIT_CLIENT, Permission.DELETE_CLIENT,
            Permission.VIEW_ANALYTICS, Permission.VIEW_AI_INSIGHTS, Permission.EXPORT_DATA,
            Permission.MANAGE_FRAMEWORKS, Permission.VIEW_FRAMEWORK_PROGRESS,
            Permission.CREATE_TEAM, Permission.MANAGE_TEAM, Permission.VIEW_TEAM,
            Permission.MANAGE_USERS, Permission.VIEW_SYSTEM_ANALYTICS, Permission.CONFIGURE_SYSTEM
        },
        
        UserRole.SENIOR_COACH: {
            Permission.CREATE_SESSION, Permission.VIEW_SESSION, Permission.EDIT_SESSION, Permission.DELETE_SESSION,
            Permission.CREATE_CLIENT, Permission.VIEW_CLIENT, Permission.EDIT_CLIENT,
            Permission.VIEW_ANALYTICS, Permission.VIEW_AI_INSIGHTS, Permission.EXPORT_DATA,
            Permission.MANAGE_FRAMEWORKS, Permission.VIEW_FRAMEWORK_PROGRESS,
            Permission.CREATE_TEAM, Permission.MANAGE_TEAM, Permission.VIEW_TEAM,
            Permission.VIEW_SYSTEM_ANALYTICS
        },
        
        UserRole.COACH: {
            Permission.CREATE_SESSION, Permission.VIEW_SESSION, Permission.EDIT_SESSION,
            Permission.VIEW_CLIENT, Permission.EDIT_CLIENT,
            Permission.VIEW_ANALYTICS, Permission.VIEW_AI_INSIGHTS, Permission.EXPORT_DATA,
            Permission.VIEW_FRAMEWORK_PROGRESS,
            Permission.VIEW_TEAM
        },
        
        UserRole.CLIENT: {
            Permission.VIEW_SESSION, Permission.VIEW_ANALYTICS, Permission.VIEW_AI_INSIGHTS,
            Permission.VIEW_FRAMEWORK_PROGRESS, Permission.VIEW_TEAM
        },
        
        UserRole.TEAM_LEAD: {
            Permission.VIEW_SESSION, Permission.VIEW_CLIENT,
            Permission.VIEW_ANALYTICS, Permission.VIEW_AI_INSIGHTS,
            Permission.VIEW_FRAMEWORK_PROGRESS, Permission.MANAGE_TEAM, Permission.VIEW_TEAM
        },
        
        UserRole.TEAM_MEMBER: {
            Permission.VIEW_SESSION, Permission.VIEW_ANALYTICS,
            Permission.VIEW_FRAMEWORK_PROGRESS, Permission.VIEW_TEAM
        },
        
        UserRole.OBSERVER: {
            Permission.VIEW_SESSION, Permission.VIEW_ANALYTICS, Permission.VIEW_FRAMEWORK_PROGRESS
        }
    }
    
    @classmethod
    def get_permissions_for_role(cls, role: UserRole) -> Set[Permission]:
        """Get permissions for a specific role"""
        return cls.ROLE_PERMISSION_MAP.get(role, set())

class CoachingAuthService:
    """Authentication and authorization service for coaching platform"""
    
    def __init__(self):
        self.db = firestore.client()
    
    async def verify_firebase_token(self, token: str) -> Dict:
        """Verify Firebase JWT token"""
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(e)}"
            )
    
    async def get_user_from_token(self, token: str) -> CoachingUser:
        """Get user information from Firebase token"""
        decoded_token = await self.verify_firebase_token(token)
        uid = decoded_token['uid']
        
        # Fetch user details from Firestore
        user_doc = self.db.collection('coaching_users').document(uid).get()
        
        if not user_doc.exists:
            # Create new user if doesn't exist
            return await self.create_new_user(decoded_token)
        
        user_data = user_doc.to_dict()
        
        # Get role permissions
        role = UserRole(user_data.get('role', UserRole.CLIENT))
        permissions = RolePermissions.get_permissions_for_role(role)
        
        return CoachingUser(
            uid=uid,
            email=decoded_token.get('email', ''),
            role=role,
            display_name=user_data.get('display_name'),
            organization_id=user_data.get('organization_id'),
            assigned_clients=user_data.get('assigned_clients', []),
            team_memberships=user_data.get('team_memberships', []),
            permissions=permissions,
            created_at=datetime.fromisoformat(user_data.get('created_at', datetime.utcnow().isoformat())),
            last_active=datetime.utcnow(),
            is_active=user_data.get('is_active', True)
        )
    
    async def create_new_user(self, decoded_token: Dict) -> CoachingUser:
        """Create new user with default role"""
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Default role is CLIENT unless specified otherwise
        default_role = UserRole.CLIENT
        permissions = RolePermissions.get_permissions_for_role(default_role)
        
        user_data = {
            'uid': uid,
            'email': email,
            'role': default_role.value,
            'display_name': decoded_token.get('name'),
            'organization_id': None,
            'assigned_clients': [],
            'team_memberships': [],
            'created_at': datetime.utcnow().isoformat(),
            'last_active': datetime.utcnow().isoformat(),
            'is_active': True
        }
        
        # Save to Firestore
        self.db.collection('coaching_users').document(uid).set(user_data)
        
        return CoachingUser(
            **user_data,
            permissions=permissions,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
    
    async def check_permission(
        self, 
        user: CoachingUser, 
        permission: Permission,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if user has specific permission"""
        
        # Super admin has all permissions
        if user.role == UserRole.SUPER_ADMIN:
            return True
        
        # Check if user has the required permission
        if permission not in user.permissions:
            return False
        
        # Additional context-based checks
        if resource_id:
            return await self.check_resource_access(user, permission, resource_id)
        
        return True
    
    async def check_resource_access(
        self,
        user: CoachingUser,
        permission: Permission,
        resource_id: str
    ) -> bool:
        """Check if user has access to specific resource"""
        
        # For client-specific resources, check if user is assigned to client
        if permission in [Permission.VIEW_CLIENT, Permission.EDIT_CLIENT]:
            if user.role in [UserRole.COACH, UserRole.SENIOR_COACH]:
                return resource_id in user.assigned_clients
            elif user.role == UserRole.CLIENT:
                return user.uid == resource_id
        
        # For session-specific resources, check session ownership/assignment
        if permission in [Permission.VIEW_SESSION, Permission.EDIT_SESSION]:
            session_doc = self.db.collection('coaching_sessions').document(resource_id).get()
            if session_doc.exists:
                session_data = session_doc.to_dict()
                
                # Coaches can access sessions they created or are assigned to
                if user.role in [UserRole.COACH, UserRole.SENIOR_COACH]:
                    return (session_data.get('coach_id') == user.uid or 
                           session_data.get('client_id') in user.assigned_clients)
                
                # Clients can access their own sessions
                if user.role == UserRole.CLIENT:
                    return session_data.get('client_id') == user.uid
        
        # For team resources, check team membership
        if permission in [Permission.VIEW_TEAM, Permission.MANAGE_TEAM]:
            return resource_id in user.team_memberships or user.role in [UserRole.TEAM_LEAD, UserRole.SENIOR_COACH]
        
        return False
    
    async def update_user_role(
        self,
        admin_user: CoachingUser,
        target_uid: str,
        new_role: UserRole
    ) -> bool:
        """Update user role (admin only)"""
        
        if not await self.check_permission(admin_user, Permission.MANAGE_USERS):
            return False
        
        # Update role in Firestore
        self.db.collection('coaching_users').document(target_uid).update({
            'role': new_role.value,
            'updated_at': datetime.utcnow().isoformat(),
            'updated_by': admin_user.uid
        })
        
        return True
    
    async def assign_client_to_coach(
        self,
        admin_user: CoachingUser,
        coach_uid: str,
        client_uid: str
    ) -> bool:
        """Assign client to coach"""
        
        if not await self.check_permission(admin_user, Permission.MANAGE_USERS):
            return False
        
        # Add client to coach's assigned clients
        coach_ref = self.db.collection('coaching_users').document(coach_uid)
        coach_doc = coach_ref.get()
        
        if coach_doc.exists:
            coach_data = coach_doc.to_dict()
            assigned_clients = coach_data.get('assigned_clients', [])
            
            if client_uid not in assigned_clients:
                assigned_clients.append(client_uid)
                coach_ref.update({
                    'assigned_clients': assigned_clients,
                    'updated_at': datetime.utcnow().isoformat()
                })
        
        return True

# Global auth service instance
auth_service = CoachingAuthService()

# Dependency functions for FastAPI

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CoachingUser:
    """Get current authenticated user"""
    token = credentials.credentials
    user = await auth_service.get_user_from_token(token)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last active timestamp
    auth_service.db.collection('coaching_users').document(user.uid).update({
        'last_active': datetime.utcnow().isoformat()
    })
    
    return user

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def permission_checker(
        current_user: CoachingUser = Depends(get_current_user)
    ) -> CoachingUser:
        if not auth_service.check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission.value} required"
            )
        return current_user
    
    return permission_checker

def require_role(required_roles: List[UserRole]):
    """Decorator to require specific role(s)"""
    def role_checker(
        current_user: CoachingUser = Depends(get_current_user)
    ) -> CoachingUser:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role {current_user.role.value} not authorized"
            )
        return current_user
    
    return role_checker

async def require_resource_access(
    permission: Permission,
    resource_id: str,
    current_user: CoachingUser = Depends(get_current_user)
) -> CoachingUser:
    """Check if user has access to specific resource"""
    
    has_access = await auth_service.check_resource_access(
        current_user, permission, resource_id
    )
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to resource {resource_id}"
        )
    
    return current_user

# Role-based access decorators for common use cases

def coaches_only():
    """Decorator for coach-only endpoints"""
    return require_role([UserRole.COACH, UserRole.SENIOR_COACH, UserRole.SUPER_ADMIN])

def admins_only():
    """Decorator for admin-only endpoints"""
    return require_role([UserRole.SUPER_ADMIN])

def clients_and_coaches():
    """Decorator for endpoints accessible to clients and coaches"""
    return require_role([
        UserRole.CLIENT, UserRole.COACH, UserRole.SENIOR_COACH, 
        UserRole.TEAM_LEAD, UserRole.SUPER_ADMIN
    ])

def team_members():
    """Decorator for team member endpoints"""
    return require_role([
        UserRole.TEAM_MEMBER, UserRole.TEAM_LEAD, UserRole.COACH,
        UserRole.SENIOR_COACH, UserRole.SUPER_ADMIN
    ])

# Permission constants for easy access
class CoachingPermissions:
    """Easy access to coaching permissions"""
    
    # Session permissions
    CREATE_SESSION = require_permission(Permission.CREATE_SESSION)
    VIEW_SESSION = require_permission(Permission.VIEW_SESSION)
    EDIT_SESSION = require_permission(Permission.EDIT_SESSION)
    DELETE_SESSION = require_permission(Permission.DELETE_SESSION)
    
    # Client permissions
    VIEW_CLIENT = require_permission(Permission.VIEW_CLIENT)
    EDIT_CLIENT = require_permission(Permission.EDIT_CLIENT)
    
    # Analytics permissions
    VIEW_ANALYTICS = require_permission(Permission.VIEW_ANALYTICS)
    EXPORT_DATA = require_permission(Permission.EXPORT_DATA)
    
    # Team permissions
    MANAGE_TEAM = require_permission(Permission.MANAGE_TEAM)
    VIEW_TEAM = require_permission(Permission.VIEW_TEAM)
    
    # Admin permissions
    MANAGE_USERS = require_permission(Permission.MANAGE_USERS)
    CONFIGURE_SYSTEM = require_permission(Permission.CONFIGURE_SYSTEM)