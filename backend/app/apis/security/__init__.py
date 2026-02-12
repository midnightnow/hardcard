from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import databutton as db
from app.auth import AuthorizedUser
import time
import json
import uuid
import re
import hashlib
from app.apis.security_formal import get_user_formal_security_state, append_security_event, FormalSecurityEvent, SecurityEventSeverity

# Import visual encryption system
try:
    from hardcard.HARDCARDSUITE.vetsorcery_extracted.backend.security.visual_encryption import (
        visual_encryption, visual_api
    )
    VISUAL_ENCRYPTION_AVAILABLE = True
except ImportError:
    VISUAL_ENCRYPTION_AVAILABLE = False
    print("Warning: Visual encryption module not available")

router = APIRouter()

# Models for security system
class SecurityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"

class MFAMethod(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    AUTHENTICATOR = "authenticator"
    SECURITY_KEY = "security_key"
    BIOMETRIC = "biometric"
    HARDCARD = "hardcard"

class UserSecuritySettings(BaseModel):
    user_id: str
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    mfa_methods_enabled: List[MFAMethod] = []
    mfa_required: bool = False
    location_verification: bool = False
    unusual_activity_alerts: bool = True
    last_security_update: Optional[int] = None
    security_score: int = 50 # 0-100

class SecuritySettingsUpdate(BaseModel):
    security_level: Optional[SecurityLevel] = None
    mfa_methods_enabled: Optional[List[MFAMethod]] = None
    mfa_required: Optional[bool] = None
    location_verification: Optional[bool] = None
    unusual_activity_alerts: Optional[bool] = None

class SecurityAuditEvent(BaseModel):
    user_id: str
    timestamp: int
    event_type: str
    details: dict
    severity: str
    source_ip: Optional[str] = None
    geo_location: Optional[dict] = None
    device_info: Optional[dict] = None

class SecurityThreatResponse(BaseModel):
    threat_id: str
    detection_time: int
    threat_type: str
    threat_level: str
    description: str
    affected_users: List[str]
    recommended_actions: List[str]
    auto_mitigated: bool

class SecurityResponse(BaseModel):
    success: bool
    message: str

class SecurityLearningData(BaseModel):
    user_id: str
    learning_patterns: dict
    last_updated: int
    anomalies_detected: List[dict]
    security_improvements: List[dict]
    confidence_score: float  # 0.0 to 1.0

class SecurityLearningResult(BaseModel):
    success: bool
    message: str
    learning_data: SecurityLearningData

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_user_security_settings(user_id: str) -> UserSecuritySettings:
    """Get user security settings or create default if not exists"""
    key = sanitize_storage_key(f"security_settings_{user_id}")
    try:
        data = db.storage.json.get(key)
        return UserSecuritySettings(**data)
    except:
        # Create default settings
        settings = UserSecuritySettings(
            user_id=user_id,
            last_security_update=int(time.time())
        )
        db.storage.json.put(key, settings.dict())
        return settings

def save_user_security_settings(settings: UserSecuritySettings):
    """Save user security settings"""
    key = sanitize_storage_key(f"security_settings_{settings.user_id}")
    db.storage.json.put(key, settings.dict())

def log_security_event(event: SecurityAuditEvent):
    """Log security event to audit trail"""
    # Create a unique ID for the event based on timestamp and user
    event_id = sanitize_storage_key(f"{event.timestamp}_{event.user_id}_{uuid.uuid4().hex[:8]}")
    db.storage.json.put(f"security_audit_{event_id}", event.dict())
    
    # Also maintain a user-specific recent events log
    user_events_key = sanitize_storage_key(f"security_events_{event.user_id}")
    try:
        user_events = db.storage.json.get(user_events_key)
    except:
        user_events = []
    
    # Add new event and keep only last 50 events
    user_events.append(event.dict())
    if len(user_events) > 50:
        user_events = user_events[-50:]
    
    db.storage.json.put(user_events_key, user_events)

def calculate_security_score(settings: UserSecuritySettings) -> int:
    """Calculate a security score (0-100) based on current settings"""
    score = 0
    
    # Base score from security level
    if settings.security_level == SecurityLevel.LOW:
        score += 10
    elif settings.security_level == SecurityLevel.MEDIUM:
        score += 30
    elif settings.security_level == SecurityLevel.HIGH:
        score += 60
    elif settings.security_level == SecurityLevel.MAXIMUM:
        score += 70
    
    # MFA methods
    score += min(len(settings.mfa_methods_enabled) * 10, 30)
    
    # Extra points for Hardcard as it's more secure
    if MFAMethod.HARDCARD in settings.mfa_methods_enabled:
        score += 15
    
    # MFA required
    if settings.mfa_required:
        score += 10
    
    # Location verification
    if settings.location_verification:
        score += 10
    
    # Alerts enabled
    if settings.unusual_activity_alerts:
        score += 5
    
    # Cap at 100
    return min(score, 100)

# Endpoints
@router.get("/security/core/settings")
async def get_security_core_settings(user: AuthorizedUser) -> UserSecuritySettings:
    """Get current security settings for the user"""
    settings = get_user_security_settings(user.sub)
    
    # Log access to security settings
    log_security_event(
        SecurityAuditEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="security_settings_accessed",
            details={},
            severity="info"
        )
    )
    
    # Also log in the formal security event system
    try:
        append_security_event(FormalSecurityEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="security_settings_accessed",
            details={},
            severity=SecurityEventSeverity.INFO
        ))
    except Exception as e:
        print(f"Warning: Failed to record formal security event: {e}")
    
    return settings

@router.put("/security/core/settings")
async def update_security_settings(settings_update: SecuritySettingsUpdate, user: AuthorizedUser) -> UserSecuritySettings:
    """Update security settings for the user"""
    current_settings = get_user_security_settings(user.sub)
    
    # Update only the fields that are provided
    update_data = {k: v for k, v in settings_update.dict().items() if v is not None}
    for key, value in update_data.items():
        setattr(current_settings, key, value)
    
    # Update timestamp and recalculate security score
    current_settings.last_security_update = int(time.time())
    current_settings.security_score = calculate_security_score(current_settings)
    
    # Save updated settings
    save_user_security_settings(current_settings)
    
    # Log settings update
    log_security_event(
        SecurityAuditEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="security_settings_updated",
            details=update_data,
            severity="info"
        )
    )
    
    return current_settings

@router.get("/security/audit-log")
async def get_security_audit_log(user: AuthorizedUser) -> List[SecurityAuditEvent]:
    """Get security audit log for the user"""
    user_events_key = sanitize_storage_key(f"security_events_{user.sub}")
    try:
        events = db.storage.json.get(user_events_key)
        return [SecurityAuditEvent(**event) for event in events]
    except:
        return []

@router.get("/security/threats")
async def get_active_security_threats(user: AuthorizedUser) -> List[SecurityThreatResponse]:
    """Get active security threats for the user"""
    # In a real implementation, this would query a threat detection system
    # For now, we'll return an empty list
    return []

@router.post("/security/analyze-risks")
async def analyze_security_risks(user: AuthorizedUser) -> dict:
    """Analyze security risks and provide recommendations"""
    settings = get_user_security_settings(user.sub)
    
    recommendations = []
    
    # Analyze security settings and generate recommendations
    if settings.security_level == SecurityLevel.LOW:
        recommendations.append("Increase your security level to at least Medium for better protection")
    
    if len(settings.mfa_methods_enabled) == 0:
        recommendations.append("Enable at least one multi-factor authentication method")
    elif len(settings.mfa_methods_enabled) == 1:
        recommendations.append("Add a second authentication method as backup")
    
    if not settings.mfa_required:
        recommendations.append("Require multi-factor authentication for all logins")
    
    if not settings.location_verification:
        recommendations.append("Enable location verification to prevent unauthorized access from unusual locations")
    
    # Log this security analysis
    log_security_event(
        SecurityAuditEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="security_risk_analysis",
            details={"security_score": settings.security_score},
            severity="info"
        )
    )
    
    return {
        "security_score": settings.security_score,
        "risk_level": "high" if settings.security_score < 40 else "medium" if settings.security_score < 70 else "low",
        "recommendations": recommendations
    }

class HardcardAuthRequest(BaseModel):
    """Request model for Hardcard authentication"""
    hardcard_id: str
    auth_challenge: str

class HardcardAuthResponse(BaseModel):
    """Response model for Hardcard authentication"""
    success: bool
    message: str
    auth_token: Optional[str] = None

@router.post("/security/hardcard-auth")
async def authenticate_with_hardcard(request: HardcardAuthRequest, user: AuthorizedUser) -> HardcardAuthResponse:
    """Authenticate using the Legacy Vault Hardcard"""
    # In a real implementation, this would verify the hardcard's cryptographic challenge
    # For now, we'll simulate a successful authentication
    
    # Get user settings
    settings = get_user_security_settings(user.sub)
    
    # Check if hardcard is enabled as an MFA method
    if MFAMethod.HARDCARD not in settings.mfa_methods_enabled:
        # Add it to their methods if they're authenticating with it
        settings.mfa_methods_enabled.append(MFAMethod.HARDCARD)
        settings.security_score = calculate_security_score(settings)
        settings.last_security_update = int(time.time())
        save_user_security_settings(settings)
    
    # Log this authentication event
    log_security_event(
        SecurityAuditEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="hardcard_authentication",
            details={"hardcard_id": request.hardcard_id},
            severity="info"
        )
    )
    
    # Generate a simulated auth token
    auth_token = hashlib.sha256(f"{user.sub}:{time.time()}:{request.hardcard_id}".encode()).hexdigest()
    
    return HardcardAuthResponse(
        success=True,
        message="Successfully authenticated with Legacy Vault Hardcard",
        auth_token=auth_token
    )

@router.post("/security/reset-authentication-factors")
async def reset_authentication_factors(user: AuthorizedUser) -> SecurityResponse:
    """Reset all authentication factors for a user in case of compromise"""
    settings = get_user_security_settings(user.sub)
    
    # In a real implementation, this would invalidate all MFA methods and force re-enrollment
    # For demonstration, we'll just clear the list
    settings.mfa_methods_enabled = []
    settings.security_score = calculate_security_score(settings)
    settings.last_security_update = int(time.time())
    
    save_user_security_settings(settings)
    
    # Log this critical security event
    log_security_event(
        SecurityAuditEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="authentication_factors_reset",
            details={},
            severity="critical"
        )
    )
    
    return SecurityResponse(
        success=True,
        message="All authentication factors have been reset. Please set up new authentication methods."
    )

def get_user_learning_data(user_id: str) -> SecurityLearningData:
    """Get or create security learning data for a user"""
    key = sanitize_storage_key(f"security_learning_{user_id}")
    try:
        data = db.storage.json.get(key)
        return SecurityLearningData(**data)
    except:
        # Create default learning data
        learning_data = SecurityLearningData(
            user_id=user_id,
            learning_patterns={
                "login_times": [],
                "login_locations": [],
                "device_types": [],
                "access_patterns": []
            },
            last_updated=int(time.time()),
            anomalies_detected=[],
            security_improvements=[],
            confidence_score=0.3  # Initial confidence is low
        )
        db.storage.json.put(key, learning_data.dict())
        return learning_data

def save_user_learning_data(learning_data: SecurityLearningData):
    """Save user security learning data"""
    key = sanitize_storage_key(f"security_learning_{learning_data.user_id}")
    db.storage.json.put(key, learning_data.dict())

@router.post("/security/adaptive-learning")
async def security_adaptive_learning(user: AuthorizedUser) -> SecurityLearningResult:
    """Run adaptive security learning to improve recommendations"""
    # Get current learning data
    learning_data = get_user_learning_data(user.sub)
    
    # Get recent events for analysis
    user_events_key = sanitize_storage_key(f"security_events_{user.sub}")
    recent_events = []
    try:
        events_data = db.storage.json.get(user_events_key)
        recent_events = events_data[-20:] if len(events_data) > 20 else events_data
    except:
        pass
    
    # Get current security settings
    settings = get_user_security_settings(user.sub)
    
    # Simulate machine learning analysis
    # In a real implementation, this would use actual ML models
    
    # Example: Extract login times patterns
    login_times = []
    for event in recent_events:
        if event.get("event_type") in ["login", "login_failed"]:
            hour_of_day = time.localtime(event.get("timestamp")).tm_hour
            login_times.append(hour_of_day)
    
    # Update learning patterns
    if login_times:
        learning_data.learning_patterns["login_times"] = login_times
    
    # Detect anomalies (simplified simulation)
    anomalies = []
    if len(recent_events) >= 5:
        # For demo, just pick a random event and flag it as an anomaly
        import random
        if random.random() < 0.3:  # 30% chance
            random_event = random.choice(recent_events)
            anomalies.append({
                "event_id": f"event_{random_event.get('timestamp')}",
                "event_type": random_event.get("event_type"),
                "timestamp": random_event.get("timestamp"),
                "anomaly_type": "unusual_pattern",
                "confidence": 0.7 + (random.random() * 0.3),
                "description": "Activity detected outside normal patterns"
            })
    
    # Add anomalies to learning data
    if anomalies:
        learning_data.anomalies_detected.extend(anomalies)
        # Cap the list at 10 items
        learning_data.anomalies_detected = learning_data.anomalies_detected[-10:]
    
    # Generate security improvements based on analysis
    improvements = []
    
    # Check if MFA should be required based on patterns
    if not settings.mfa_required and len(recent_events) > 10:
        improvements.append({
            "id": "require_mfa",
            "timestamp": int(time.time()),
            "description": "Enable mandatory multi-factor authentication",
            "reasoning": "Based on account activity patterns, enabling MFA would significantly improve security",
            "impact_score": 0.8,
            "auto_applied": False
        })
    
    # Suggest location verification if not enabled and we detect multiple locations
    if not settings.location_verification and len(learning_data.learning_patterns.get("login_locations", [])) > 1:
        improvements.append({
            "id": "enable_location_verification",
            "timestamp": int(time.time()),
            "description": "Enable location verification for logins",
            "reasoning": "Multiple login locations detected, enabling verification would protect against unauthorized access",
            "impact_score": 0.7,
            "auto_applied": False
        })
    
    # Add Hardcard if high value account and not enabled
    if settings.security_score > 70 and "hardcard" not in settings.mfa_methods_enabled:
        improvements.append({
            "id": "add_hardcard",
            "timestamp": int(time.time()),
            "description": "Add Legacy Vault Hardcard as authentication method",
            "reasoning": "Your high-value assets would benefit from the strongest physical security option",
            "impact_score": 0.9,
            "auto_applied": False
        })
    
    # Update improvements in learning data
    if improvements:
        learning_data.security_improvements.extend(improvements)
        # Keep only the most recent 10 improvements
        learning_data.security_improvements = learning_data.security_improvements[-10:]
    
    # Update confidence score - it increases as we collect more data
    # In a real implementation, this would be based on model confidence metrics
    events_analyzed = len(recent_events)
    if events_analyzed > 0:
        # Confidence grows with more data, up to a maximum of 0.95
        learning_data.confidence_score = min(0.3 + (events_analyzed * 0.05), 0.95)
    
    # Update timestamp
    learning_data.last_updated = int(time.time())
    
    # Save updated learning data
    save_user_learning_data(learning_data)
    
    # Log this learning event
    log_security_event(
        SecurityAuditEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="adaptive_security_learning",
            details={
                "confidence_score": learning_data.confidence_score,
                "anomalies_detected": len(anomalies),
                "improvements_suggested": len(improvements)
            },
            severity="info"
        )
    )
    
    return SecurityLearningResult(
        success=True,
        message=f"Adaptive security learning completed with {learning_data.confidence_score:.2f} confidence score",
        learning_data=learning_data
    )

@router.post("/security/simulate-threat-detection")
async def simulate_threat_detection(user: AuthorizedUser) -> SecurityThreatResponse:
    """Simulate threat detection for testing"""
    # This is for demonstration purposes only
    # In a real implementation, this would be an internal endpoint or not exist at all
    
    # Log this simulation
    log_security_event(
        SecurityAuditEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="threat_detection_simulation",
            details={},
            severity="info"
        )
    )
    
    # Return a simulated threat
    return SecurityThreatResponse(
        threat_id=uuid.uuid4().hex,
        detection_time=int(time.time()),
        threat_type="suspicious_login_attempt",
        threat_level="medium",
        description="Unusual login attempt detected from an unrecognized location",
        affected_users=[user.sub],
        recommended_actions=[
            "Verify recent account activity",
            "Enable location verification",
            "Change password if you don't recognize this activity"
        ],
        auto_mitigated=False
    )


# Visual Encryption Endpoints
class VisualEncodeRequest(BaseModel):
    """Request model for visual encoding"""
    data: str
    columns: int = 8
    encoding_type: str = "standard"  # standard, medical, signature

class VisualEncodeResponse(BaseModel):
    """Response model for visual encoding"""
    success: bool
    encoded_image: str  # Base64 encoded image
    encoding_id: str
    verification_hash: Optional[str] = None
    metadata: dict

class VisualDecodeRequest(BaseModel):
    """Request model for visual decoding"""
    encoded_image: str  # Base64 encoded image or file path
    columns: int = 8

class VisualDecodeResponse(BaseModel):
    """Response model for visual decoding"""
    success: bool
    decoded_data: Optional[str] = None
    error: Optional[str] = None

class HardCardVisualRequest(BaseModel):
    """Request for HardCard visual pattern generation"""
    hardcard_id: str
    security_level: SecurityLevel = SecurityLevel.MAXIMUM

class HardCardVisualResponse(BaseModel):
    """Response for HardCard visual pattern"""
    success: bool
    hardcard_id: str
    visual_pattern: str  # Base64 encoded image
    pattern_type: str
    created: int

@router.post("/security/visual/encode")
async def encode_to_visual(request: VisualEncodeRequest, user: AuthorizedUser) -> VisualEncodeResponse:
    """Encode sensitive data into visual steganographic format"""
    if not VISUAL_ENCRYPTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visual encryption service unavailable")
    
    try:
        # Generate encoding ID
        encoding_id = f"vis_{user.sub}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Handle different encoding types
        if request.encoding_type == "medical":
            # Use medical-grade encryption for PHI data
            result = await visual_api.encode_sensitive_data(
                data=request.data,
                user_id=user.sub
            )
            
            # Create medical verification stamp
            verification_hash = hashlib.sha256(
                f"medical:{request.data}:{user.sub}".encode()
            ).hexdigest()[:16]
            
        elif request.encoding_type == "signature":
            # Create visual signature
            image_b64, verification_hash = visual_encryption.create_visual_signature(
                user_id=user.sub,
                auth_data={"timestamp": int(time.time())}
            )
            result = {
                'success': True,
                'encoded_image': image_b64
            }
            
        else:
            # Standard encoding
            result = await visual_api.encode_sensitive_data(
                data=request.data,
                user_id=user.sub
            )
            verification_hash = None
        
        # Log encoding event
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="visual_data_encoded",
                details={
                    "encoding_id": encoding_id,
                    "encoding_type": request.encoding_type,
                    "columns": request.columns
                },
                severity="info"
            )
        )
        
        return VisualEncodeResponse(
            success=True,
            encoded_image=result['encoded_image'],
            encoding_id=encoding_id,
            verification_hash=verification_hash,
            metadata={
                "encoding_type": request.encoding_type,
                "columns": request.columns,
                "timestamp": int(time.time()),
                "user_id": user.sub
            }
        )
        
    except Exception as e:
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="visual_encoding_failed",
                details={"error": str(e)},
                severity="warning"
            )
        )
        raise HTTPException(status_code=500, detail=f"Visual encoding failed: {str(e)}")

@router.post("/security/visual/decode")
async def decode_from_visual(request: VisualDecodeRequest, user: AuthorizedUser) -> VisualDecodeResponse:
    """Decode data from visual steganographic format"""
    if not VISUAL_ENCRYPTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visual encryption service unavailable")
    
    try:
        result = await visual_api.decode_visual_data(
            image_data=request.encoded_image,
            user_id=user.sub
        )
        
        # Log decoding event
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="visual_data_decoded",
                details={
                    "success": result['success'],
                    "columns": request.columns
                },
                severity="info"
            )
        )
        
        if result['success']:
            return VisualDecodeResponse(
                success=True,
                decoded_data=result['decoded_data']
            )
        else:
            return VisualDecodeResponse(
                success=False,
                error=result.get('error', 'Decoding failed')
            )
            
    except Exception as e:
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="visual_decoding_failed",
                details={"error": str(e)},
                severity="warning"
            )
        )
        return VisualDecodeResponse(
            success=False,
            error=f"Visual decoding failed: {str(e)}"
        )

@router.post("/security/hardcard/generate-visual")
async def generate_hardcard_visual(request: HardCardVisualRequest, user: AuthorizedUser) -> HardCardVisualResponse:
    """Generate unique visual pattern for HardCard"""
    if not VISUAL_ENCRYPTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visual encryption service unavailable")
    
    try:
        # Check if user has permission to generate HardCard visuals
        settings = get_user_security_settings(user.sub)
        if MFAMethod.HARDCARD not in settings.mfa_methods_enabled and settings.security_level != SecurityLevel.MAXIMUM:
            raise HTTPException(
                status_code=403, 
                detail="HardCard visual generation requires HardCard MFA or maximum security level"
            )
        
        # Generate visual pattern
        result = await visual_api.generate_hardcard_visual(request.hardcard_id)
        
        # Log generation event
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="hardcard_visual_generated",
                details={
                    "hardcard_id": request.hardcard_id,
                    "security_level": request.security_level
                },
                severity="info"
            )
        )
        
        return HardCardVisualResponse(
            success=True,
            hardcard_id=request.hardcard_id,
            visual_pattern=result['visual_pattern'],
            pattern_type=result['pattern_type'],
            created=result['created']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="hardcard_visual_generation_failed",
                details={"error": str(e)},
                severity="error"
            )
        )
        raise HTTPException(status_code=500, detail=f"HardCard visual generation failed: {str(e)}")

@router.post("/security/visual/verify-signature")
async def verify_visual_signature(
    signature_image: str,
    verification_hash: str,
    user: AuthorizedUser
) -> dict:
    """Verify a visual signature"""
    if not VISUAL_ENCRYPTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visual encryption service unavailable")
    
    try:
        # Verify the visual signature
        is_valid = visual_encryption.verify_visual_signature(
            signature_image=signature_image,
            user_id=user.sub,
            verification_hash=verification_hash
        )
        
        # Log verification attempt
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="visual_signature_verification",
                details={
                    "valid": is_valid,
                    "hash": verification_hash[:8] + "..."  # Log partial hash only
                },
                severity="info" if is_valid else "warning"
            )
        )
        
        return {
            "success": True,
            "valid": is_valid,
            "message": "Signature verified successfully" if is_valid else "Invalid signature"
        }
        
    except Exception as e:
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="visual_signature_verification_failed",
                details={"error": str(e)},
                severity="error"
            )
        )
        raise HTTPException(status_code=500, detail=f"Signature verification failed: {str(e)}")

@router.post("/security/visual/create-qr-alternative")
async def create_secure_qr_alternative(
    data: str,
    max_width: int = 512,
    max_height: int = 512,
    user: AuthorizedUser
) -> dict:
    """Create a visual encoding as a secure alternative to QR codes"""
    if not VISUAL_ENCRYPTION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Visual encryption service unavailable")
    
    try:
        # Create secure QR alternative
        qr_image = visual_encryption.create_secure_qr_alternative(
            data=data,
            max_size=(max_width, max_height)
        )
        
        # Convert to base64
        import io
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Log creation
        log_security_event(
            SecurityAuditEvent(
                user_id=user.sub,
                timestamp=int(time.time()),
                event_type="secure_qr_alternative_created",
                details={
                    "data_length": len(data),
                    "image_size": f"{max_width}x{max_height}"
                },
                severity="info"
            )
        )
        
        return {
            "success": True,
            "encoded_image": image_b64,
            "encoding_type": "visual_steganographic_qr",
            "data_capacity": f"{len(data)} bytes encoded",
            "security_level": "maximum"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR alternative creation failed: {str(e)}")
