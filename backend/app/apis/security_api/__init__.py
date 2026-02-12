from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
import time
import random
from datetime import datetime, timedelta
from app.auth import AuthorizedUser
import uuid
import json

router = APIRouter()

# Models
class SecuritySettingsUpdate(BaseModel):
    security_level: Optional[Literal["low", "medium", "high", "maximum"]] = None
    mfa_methods_enabled: Optional[List[str]] = None
    mfa_required: Optional[bool] = None
    location_verification: Optional[bool] = None
    unusual_activity_alerts: Optional[bool] = None

class SecuritySettings(BaseModel):
    user_id: str
    security_level: Literal["low", "medium", "high", "maximum"]
    mfa_methods_enabled: List[str]
    mfa_required: bool
    location_verification: bool
    unusual_activity_alerts: bool
    last_security_update: int
    security_score: int

class AuditEvent(BaseModel):
    user_id: str
    timestamp: int
    event_type: str
    details: Dict[str, Any]
    severity: str
    source_ip: Optional[str] = None
    geo_location: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None

class SecurityThreat(BaseModel):
    threat_id: str
    detection_time: int
    threat_type: str
    threat_level: str
    description: str
    affected_users: List[str]
    recommended_actions: List[str]
    auto_mitigated: bool

class SecurityRiskAnalysis(BaseModel):
    security_score: int
    risk_level: Literal["low", "medium", "high"]
    recommendations: List[str]

class HardcardAuthRequest(BaseModel):
    hardcard_id: str
    auth_challenge: str
    google_auth_token: Optional[str] = None
    device_verification: Optional[Dict[str, Any]] = None
    biometric_data: Optional[Dict[str, Any]] = None

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None

class ResetResponse(BaseModel):
    success: bool
    message: str
    
class AdaptiveLearningResponse(BaseModel):
    success: bool
    message: str
    improved_areas: List[str]
    adaptive_measures_applied: Optional[List[str]] = None
    new_security_score: Optional[int] = None

# Mock data store (in a real app, this would be a database)
_security_settings = {}
_audit_logs = {}
_security_threats = {}
_learning_patterns = {}
_detected_anomalies = {}

# Helper functions

class AdaptiveSecurityLearningSystem:
    """A self-learning security system that adapts to new threats and user behavior"""
    
    @staticmethod
    def analyze_audit_log(user_id: str) -> Dict[str, Any]:
        """Analyze audit logs to identify patterns and potential security improvements"""
        if user_id not in _audit_logs or len(_audit_logs[user_id]) < 5:
            return {
                "patterns": [],
                "recommendations": ["Continue using the system to generate more security data for analysis"],
                "anomalies": [],
            }
        
        logs = _audit_logs[user_id]
        patterns = []
        anomalies = []
        access_times = []
        access_locations = []
        event_frequencies = {}
        
        # Analyze login times, locations, and event frequencies
        for event in logs:
            # Collect timestamps for time pattern analysis
            if event.event_type == "login_success":
                access_times.append(event.timestamp)
                if event.geo_location:
                    access_locations.append(event.geo_location)
            
            # Track event frequencies
            if event.event_type in event_frequencies:
                event_frequencies[event.event_type] += 1
            else:
                event_frequencies[event.event_type] = 1
        
        # Find time patterns (e.g., user typically logs in during certain hours)
        if access_times:
            # Convert timestamps to hours and find most common login hours
            hours = [datetime.fromtimestamp(ts).hour for ts in access_times]
            hour_counts = {}
            for hour in hours:
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
            # Find the most common login hour
            most_common_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
            common_hour_range = f"{most_common_hour}:00 to {most_common_hour+1}:00"
            patterns.append({"type": "login_time", "pattern": common_hour_range})
        
        # Find location patterns
        if access_locations:
            location_counts = {}
            for loc in access_locations:
                loc_str = f"{loc.get('city', 'Unknown')}, {loc.get('country', 'Unknown')}"
                location_counts[loc_str] = location_counts.get(loc_str, 0) + 1
            
            # Find the most common location
            if location_counts:
                most_common_location = max(location_counts.items(), key=lambda x: x[1])[0]
                patterns.append({"type": "login_location", "pattern": most_common_location})
        
        # Generate recommendations based on patterns
        recommendations = []
        
        # Check if there are any failed login attempts
        failed_logins = event_frequencies.get("login_failure", 0)
        if failed_logins > 3:
            recommendations.append("Consider enabling location verification for additional security")
            anomalies.append({"type": "multiple_failed_logins", "count": failed_logins})
        
        # Check if security settings have been updated recently
        settings_updates = event_frequencies.get("security_settings_updated", 0)
        if settings_updates < 1:
            recommendations.append("Review and update your security settings regularly")
        
        # Check if threat analysis has been performed
        threat_analyses = event_frequencies.get("security_risk_analysis", 0)
        if threat_analyses < 2:
            recommendations.append("Perform security risk analysis regularly to identify potential threats")
        
        return {
            "patterns": patterns,
            "recommendations": recommendations,
            "anomalies": anomalies,
        }
    
    @staticmethod
    def learn_from_threats(user_id: str, threats: List[SecurityThreat]) -> List[str]:
        """Learn from detected threats to improve security posture"""
        if not threats:
            return ["No threats to learn from"]
        
        improved_areas = []
        if user_id not in _learning_patterns:
            _learning_patterns[user_id] = {
                "threat_types": {},
                "mitigation_tactics": [],
                "vulnerability_scores": {}
            }
        
        user_patterns = _learning_patterns[user_id]
        
        # Analyze threats by type
        for threat in threats:
            # Update threat type frequency
            if threat.threat_type in user_patterns["threat_types"]:
                user_patterns["threat_types"][threat.threat_type] += 1
            else:
                user_patterns["threat_types"][threat.threat_type] = 1
            
            # Add mitigation tactics
            for action in threat.recommended_actions:
                if action not in user_patterns["mitigation_tactics"]:
                    user_patterns["mitigation_tactics"].append(action)
        
        # Determine most common threat type
        if user_patterns["threat_types"]:
            most_common_threat = max(user_patterns["threat_types"].items(), key=lambda x: x[1])
            improved_areas.append(f"Enhanced protection against {most_common_threat[0].replace('_', ' ')}")
        
        # Implement specific improvements based on threat types
        threat_types = set(threat.threat_type for threat in threats)
        
        if "suspicious_login_attempt" in threat_types:
            improved_areas.append("Improved login attempt analysis algorithms")
        
        if "brute_force_attack" in threat_types:
            improved_areas.append("Enhanced password security measures")
        
        if "session_hijacking_attempt" in threat_types:
            improved_areas.append("Strengthened session security and validation")
        
        if "unusual_access_pattern" in threat_types:
            improved_areas.append("Refined user behavior analytics")
        
        if "potential_data_exfiltration" in threat_types:
            improved_areas.append("Upgraded data access monitoring")
        
        return improved_areas
    
    @staticmethod
    def detect_anomalies(user_id: str, event: AuditEvent) -> Optional[Dict[str, Any]]:
        """Detect anomalies in user behavior in real-time"""
        # Skip if we don't have enough history for this user
        if user_id not in _audit_logs or len(_audit_logs[user_id]) < 10:
            return None
        
        # Initialize user's anomaly detection patterns if they don't exist
        if user_id not in _detected_anomalies:
            _detected_anomalies[user_id] = []
        
        anomaly = None
        logs = _audit_logs[user_id]
        
        # Check for login time anomalies
        if event.event_type == "login_success":
            # Get historical login times
            login_times = [log.timestamp for log in logs if log.event_type == "login_success"]
            if login_times:
                # Convert to hours of day
                login_hours = [datetime.fromtimestamp(ts).hour for ts in login_times]
                # Get most common login hours
                hour_counts = {}
                for hour in login_hours:
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                
                common_hours = [hour for hour, count in hour_counts.items() if count > 1]
                current_hour = datetime.fromtimestamp(event.timestamp).hour
                
                # If user is logging in at an unusual time
                if common_hours and current_hour not in common_hours:
                    anomaly = {
                        "type": "unusual_login_time",
                        "description": f"Login at unusual hour: {current_hour}:00",
                        "severity": "medium",
                        "timestamp": event.timestamp
                    }
        
        # Check for location anomalies
        if event.event_type == "login_success" and event.geo_location:
            # Get historical login locations
            locations = [log.geo_location for log in logs 
                       if log.event_type == "login_success" and log.geo_location]
            
            if locations:
                # Check if current location has been seen before
                current_location = f"{event.geo_location.get('country', '')}, {event.geo_location.get('city', '')}"
                location_matches = [f"{loc.get('country', '')}, {loc.get('city', '')}" == current_location for loc in locations]
                
                if not any(location_matches):
                    anomaly = {
                        "type": "new_login_location",
                        "description": f"Login from new location: {current_location}",
                        "severity": "high",
                        "timestamp": event.timestamp
                    }
        
        # If we found an anomaly, add it to the user's history
        if anomaly:
            _detected_anomalies[user_id].append(anomaly)
        
        return anomaly
def get_default_security_settings(user_id: str) -> SecuritySettings:
    """Create default security settings for a new user"""
    return SecuritySettings(
        user_id=user_id,
        security_level="medium",
        mfa_methods_enabled=["email"],
        mfa_required=True,
        location_verification=True,
        unusual_activity_alerts=True,
        last_security_update=int(time.time()),
        security_score=65
    )

def calculate_security_score(settings: SecuritySettings) -> int:
    """Calculate a security score based on the settings"""
    score = 0
    
    # Base score from security level
    if settings.security_level == "low":
        score += 20
    elif settings.security_level == "medium":
        score += 40
    elif settings.security_level == "high":
        score += 70
    elif settings.security_level == "maximum":
        score += 85
    
    # MFA methods
    mfa_count = len(settings.mfa_methods_enabled)
    if mfa_count > 0:
        score += min(25, 5 * mfa_count)  # Up to 25 points for MFA
        
        # Extra points for requiring MFA
        if settings.mfa_required:
            score += 10
    
    # Other security features
    if settings.location_verification:
        score += 5
    if settings.unusual_activity_alerts:
        score += 5
    
    # Cap at 100
    return min(100, score)

def add_audit_event(user_id: str, event_type: str, severity: str, details: Dict[str, Any]):
    """Add an audit event to the log and check for anomalies"""
    # Create the event
    """Add an audit event to the log"""
    if user_id not in _audit_logs:
        _audit_logs[user_id] = []
    
    event = AuditEvent(
        user_id=user_id,
        timestamp=int(time.time()),
        event_type=event_type,
        details=details,
        severity=severity,
        source_ip="192.168.0.1",  # Mock IP
        geo_location={"country": "United States", "city": "San Francisco"},  # Mock location
        device_info={"browser": "Chrome", "os": "Windows"}  # Mock device info
    )
    
    _audit_logs[user_id].insert(0, event)  # Add to the beginning for reverse chronological order
    
    # Keep only the most recent 100 events
    if len(_audit_logs[user_id]) > 100:
        _audit_logs[user_id] = _audit_logs[user_id][:100]
    
    # Check for anomalies using the adaptive security system
    anomaly = AdaptiveSecurityLearningSystem.detect_anomalies(user_id, event)
    if anomaly:
        # Create a security threat if it's a high severity anomaly
        if anomaly["severity"] == "high":
            threat = SecurityThreat(
                threat_id=str(uuid.uuid4()),
                detection_time=int(time.time()),
                threat_type="anomalous_behavior",
                threat_level="medium",
                description=f"Unusual activity detected: {anomaly['description']}",
                affected_users=[user_id],
                recommended_actions=[
                    "Review recent account activity",
                    "Change your password if you don't recognize this activity",
                    "Enable additional security features"
                ],
                auto_mitigated=False
            )
            
            # Add to global threats
            _security_threats[threat.threat_id] = threat
            
            # Add a separate audit event for the anomaly
            _audit_logs[user_id].insert(0, AuditEvent(
                user_id=user_id,
                timestamp=int(time.time()),
                event_type="security_anomaly_detected",
                details=anomaly,
                severity="warning",
                source_ip=event.source_ip,
                geo_location=event.geo_location,
                device_info=event.device_info
            ))
    
    return event

def generate_risk_analysis(user_id: str) -> SecurityRiskAnalysis:
    """Generate a risk analysis report based on security settings"""
    if user_id not in _security_settings:
        return SecurityRiskAnalysis(
            security_score=0,
            risk_level="high",
            recommendations=["Set up your security settings"]
        )
    
    settings = _security_settings[user_id]
    score = settings.security_score
    
    recommendations = []
    
    # Determine risk level based on score
    if score >= 80:
        risk_level = "low"
    elif score >= 50:
        risk_level = "medium"
    else:
        risk_level = "high"
    
    # Generate recommendations based on settings
    if not settings.mfa_required or len(settings.mfa_methods_enabled) == 0:
        recommendations.append("Enable multi-factor authentication for stronger account protection")
    
    if len(settings.mfa_methods_enabled) < 2:
        recommendations.append("Add additional authentication methods as backup")
    
    if settings.security_level in ["low", "medium"]:
        recommendations.append("Increase your security level for better protection")
    
    if not settings.location_verification:
        recommendations.append("Enable location verification to prevent unauthorized access from unknown locations")
    
    if not settings.unusual_activity_alerts:
        recommendations.append("Turn on unusual activity alerts to be notified of suspicious behavior")
    
    # If we have threats, add recommendations about them
    threats = [t for t in _security_threats.values() if user_id in t.affected_users]
    if threats:
        recommendations.append(f"Address {len(threats)} active security threats detected on your account")
    
    # If we have perfect security, acknowledge it
    if score >= 95 and not recommendations:
        recommendations.append("Your security setup is excellent. Continue monitoring your security settings regularly.")
    
    return SecurityRiskAnalysis(
        security_score=score,
        risk_level=risk_level,
        recommendations=recommendations
    )

# Endpoints
@router.get("/security/api/settings")
async def get_security_api_settings(user: AuthorizedUser) -> SecuritySettings:
    user_id = user.sub
    
    # If user doesn't have settings yet, create defaults
    if user_id not in _security_settings:
        _security_settings[user_id] = get_default_security_settings(user_id)
        add_audit_event(
            user_id=user_id,
            event_type="security_settings_initialized",
            severity="info",
            details={"initial_settings": json.loads(_security_settings[user_id].json())}
        )
    
    return _security_settings[user_id]

@router.post("/security/api/settings")
async def update_security_api_settings(updates: SecuritySettingsUpdate, user: AuthorizedUser) -> SecuritySettings:
    user_id = user.sub
    
    # Ensure user has settings
    if user_id not in _security_settings:
        _security_settings[user_id] = get_default_security_settings(user_id)
    
    current_settings = _security_settings[user_id]
    updated = False
    update_details = {}
    
    # Apply updates
    if updates.security_level is not None and updates.security_level != current_settings.security_level:
        current_settings.security_level = updates.security_level
        updated = True
        update_details["security_level"] = updates.security_level
    
    if updates.mfa_methods_enabled is not None and updates.mfa_methods_enabled != current_settings.mfa_methods_enabled:
        current_settings.mfa_methods_enabled = updates.mfa_methods_enabled
        updated = True
        update_details["mfa_methods_enabled"] = updates.mfa_methods_enabled
    
    if updates.mfa_required is not None and updates.mfa_required != current_settings.mfa_required:
        current_settings.mfa_required = updates.mfa_required
        updated = True
        update_details["mfa_required"] = updates.mfa_required
    
    if updates.location_verification is not None and updates.location_verification != current_settings.location_verification:
        current_settings.location_verification = updates.location_verification
        updated = True
        update_details["location_verification"] = updates.location_verification
    
    if updates.unusual_activity_alerts is not None and updates.unusual_activity_alerts != current_settings.unusual_activity_alerts:
        current_settings.unusual_activity_alerts = updates.unusual_activity_alerts
        updated = True
        update_details["unusual_activity_alerts"] = updates.unusual_activity_alerts
    
    if updated:
        # Update the security score and timestamp
        current_settings.security_score = calculate_security_score(current_settings)
        current_settings.last_security_update = int(time.time())
        
        # Add audit log entry
        add_audit_event(
            user_id=user_id,
            event_type="security_settings_updated",
            severity="info",
            details=update_details
        )
    
    return current_settings

@router.get("/security/api/audit-log")
async def get_security_api_audit_log(user: AuthorizedUser) -> List[AuditEvent]:
    user_id = user.sub
    
    # Return empty list if no logs
    if user_id not in _audit_logs:
        return []
    
    return _audit_logs[user_id]

@router.get("/security/api/threats")
async def get_active_security_api_threats(user: AuthorizedUser) -> List[SecurityThreat]:
    user_id = user.sub
    
    # Filter threats that affect this user
    user_threats = [threat for threat in _security_threats.values() if user_id in threat.affected_users]
    return user_threats

@router.get("/security/risk-analysis")
async def analyze_security_risks2(user: AuthorizedUser) -> SecurityRiskAnalysis:
    user_id = user.sub
    
    # Add an audit event
    add_audit_event(
        user_id=user_id,
        event_type="security_risk_analysis",
        severity="info",
        details={"timestamp": int(time.time())}
    )
    
    return generate_risk_analysis(user_id)

@router.post("/security/reset-auth-factors")
async def reset_authentication_factors2(user: AuthorizedUser) -> ResetResponse:
    user_id = user.sub
    
    if user_id not in _security_settings:
        return ResetResponse(success=False, message="No security settings found")
    
    # Reset MFA methods
    previous_methods = _security_settings[user_id].mfa_methods_enabled.copy()
    _security_settings[user_id].mfa_methods_enabled = []
    _security_settings[user_id].mfa_required = False
    
    # Update security score
    _security_settings[user_id].security_score = calculate_security_score(_security_settings[user_id])
    _security_settings[user_id].last_security_update = int(time.time())
    
    # Add audit log entry
    add_audit_event(
        user_id=user_id,
        event_type="auth_factors_reset",
        severity="critical",
        details={"previous_methods": previous_methods}
    )
    
    return ResetResponse(success=True, message="Authentication factors have been reset")

@router.post("/security/simulate-threat")
async def simulate_threat_detection2(user: AuthorizedUser) -> SecurityThreat:
    user_id = user.sub
    
    # Create a simulated threat
    threat_types = [
        "suspicious_login_attempt",
        "brute_force_attack",
        "session_hijacking_attempt",
        "unusual_access_pattern",
        "potential_data_exfiltration"
    ]
    
    threat_levels = ["low", "medium", "high"]
    
    descriptions = {
        "suspicious_login_attempt": "Multiple failed login attempts detected from an unusual location",
        "brute_force_attack": "Systematic password guessing attempts detected on your account",
        "session_hijacking_attempt": "Unusual session activity detected suggesting potential session theft",
        "unusual_access_pattern": "Access patterns indicating automated or scripted behavior detected",
        "potential_data_exfiltration": "Unusual data access patterns detected suggesting potential data theft"
    }
    
    recommendations = {
        "low": [
            "Review recent login activity",
            "No immediate action required"
        ],
        "medium": [
            "Change your password",
            "Enable additional security features",
            "Review recent account activity"
        ],
        "high": [
            "Change your password immediately",
            "Enable multi-factor authentication",
            "Contact security team",
            "Check for unauthorized changes to your account"
        ]
    }
    
    threat_type = random.choice(threat_types)
    threat_level = random.choice(threat_levels)
    
    threat = SecurityThreat(
        threat_id=str(uuid.uuid4()),
        detection_time=int(time.time()),
        threat_type=threat_type,
        threat_level=threat_level,
        description=descriptions[threat_type],
        affected_users=[user_id],
        recommended_actions=recommendations[threat_level],
        auto_mitigated=False
    )
    
    # Add to global threats
    _security_threats[threat.threat_id] = threat
    
    # Add audit log entry
    add_audit_event(
        user_id=user_id,
        event_type="security_threat_detected",
        severity="warning" if threat_level == "low" else "critical",
        details={
            "threat_id": threat.threat_id,
            "threat_type": threat_type,
            "threat_level": threat_level
        }
    )
    
    return threat

@router.post("/security/api/adaptive-learning")
async def security_adaptive_learning_api(user: AuthorizedUser) -> AdaptiveLearningResponse:
    """Apply adaptive learning to improve security based on patterns and threats"""
    user_id = user.sub
    
    # Initialize response
    improved_areas = []
    
    # Step 1: Analyze audit logs to detect patterns
    log_analysis = AdaptiveSecurityLearningSystem.analyze_audit_log(user_id)
    
    # Step 2: Learn from detected threats
    threats = [t for t in _security_threats.values() if user_id in t.affected_users]
    threat_learnings = AdaptiveSecurityLearningSystem.learn_from_threats(user_id, threats)
    
    # Step 3: Apply adaptive measures
    adaptive_measures_applied = []
    
    # If we have patterns, apply some adaptive measures
    if log_analysis["patterns"]:
        # If we detected login time patterns, enhance monitoring during non-standard hours
        time_patterns = [p for p in log_analysis["patterns"] if p["type"] == "login_time"]
        if time_patterns:
            improved_areas.append("Enhanced monitoring during unusual access hours")
            adaptive_measures_applied.append("Time-based access monitoring")
        
        # If we detected location patterns, enhance location verification
        location_patterns = [p for p in log_analysis["patterns"] if p["type"] == "login_location"]
        if location_patterns and not _security_settings.get(user_id, {}).location_verification:
            # Auto-enable location verification if we have location patterns
            if user_id in _security_settings:
                _security_settings[user_id].location_verification = True
                _security_settings[user_id].security_score = calculate_security_score(_security_settings[user_id])
                adaptive_measures_applied.append("Enabled location verification")
                improved_areas.append("Automated location-based security")
    
    # If we have anomalies, apply defensive measures
    if log_analysis["anomalies"]:
        # If we detected multiple failed logins, increase security level
        failed_login_anomalies = [a for a in log_analysis["anomalies"] if a["type"] == "multiple_failed_logins"]
        if failed_login_anomalies and user_id in _security_settings:
            # Only increase if not already at maximum
            if _security_settings[user_id].security_level != "maximum":
                # Determine new security level (increase by one level)
                current_level = _security_settings[user_id].security_level
                new_level = {
                    "low": "medium",
                    "medium": "high",
                    "high": "maximum"
                }.get(current_level, "maximum")
                
                _security_settings[user_id].security_level = new_level
                _security_settings[user_id].security_score = calculate_security_score(_security_settings[user_id])
                adaptive_measures_applied.append(f"Increased security level to {new_level}")
                improved_areas.append("Proactive security level adjustment")
    
    # Add learnings from threats
    improved_areas.extend(threat_learnings)
    
    # Step 4: Update security score if needed
    new_security_score = None
    if user_id in _security_settings and adaptive_measures_applied:
        _security_settings[user_id].last_security_update = int(time.time())
        new_security_score = _security_settings[user_id].security_score
    
    # Log the adaptive learning event
    add_audit_event(
        user_id=user_id,
        event_type="adaptive_security_applied",
        severity="info",
        details={
            "improved_areas": improved_areas,
            "adaptive_measures_applied": adaptive_measures_applied,
            "new_security_score": new_security_score
        }
    )
    
    return AdaptiveLearningResponse(
        success=True,
        message="Adaptive security measures applied",
        improved_areas=improved_areas,
        new_security_score=new_security_score,
        adaptive_measures_applied=adaptive_measures_applied if adaptive_measures_applied else None
    )

@router.post("/security/authenticate-with-hardcard")
async def authenticate_with_hardcard2(auth_request: HardcardAuthRequest, user: AuthorizedUser = None) -> AuthResponse:
    """Authenticate a user with a physical hardcard credential"""
    
    # This would integrate with a real hardcard authentication system
    # The implementation follows the Hardcard MVP authentication flow
    
    # Step 1: Validate the Hardcard ID from QR code
    if not auth_request.hardcard_id or not auth_request.auth_challenge:
        return AuthResponse(
            success=False,
            message="Missing required Hardcard identification parameters"
        )
    
    # Step 2: Verify Google authentication (if provided)
    # In a real implementation, this would validate the Google auth token
    google_auth_valid = True
    if auth_request.google_auth_token:
        # Simulate token validation
        google_auth_valid = len(auth_request.google_auth_token) > 10
        if not google_auth_valid:
            return AuthResponse(
                success=False,
                message="Invalid Google authentication credentials"
            )
    
    # Step 3: Verify device-specific authentication (Face ID/Touch ID)
    device_verified = True
    if auth_request.device_verification:
        # Check if it's an iPhone
        is_iphone = auth_request.device_verification.get("device_type") == "iphone"
        # Check if biometric auth was used
        biometric_used = auth_request.device_verification.get("biometric_used") in ["face_id", "touch_id"]
        
        device_verified = is_iphone and biometric_used
        if not device_verified:
            return AuthResponse(
                success=False,
                message="Device verification failed - iPhone with Face ID or Touch ID required"
            )
    
    # Step 4: Link the Hardcard to the user account if not already linked
    user_id = user.sub if user else "anonymous_user"
    
    # In a real implementation, this would create or update the association
    # between the user account and the hardcard in a database
    
    # Step 5: Generate encrypted response
    # In a real implementation, this would use proper encryption
    
    # Record the authentication in the audit log if we have a user
    if user:
        add_audit_event(
            user_id=user_id,
            event_type="hardcard_authentication",
            severity="info",
            details={
                "hardcard_id": auth_request.hardcard_id[:5] + "...",  # Only log partial ID for security
                "authentication_method": "google_auth" if auth_request.google_auth_token else "direct",
                "device_verification": "biometric" if auth_request.device_verification else "none"
            }
        )
        
        # Update the user's security settings to include Hardcard as an MFA method
        if user_id in _security_settings:
            if "hardcard" not in _security_settings[user_id].mfa_methods_enabled:
                _security_settings[user_id].mfa_methods_enabled.append("hardcard")
                _security_settings[user_id].security_score = calculate_security_score(_security_settings[user_id])
                _security_settings[user_id].last_security_update = int(time.time())
    
    return AuthResponse(
        success=True,
        message="Hardcard authentication successful",
        token="hardcard_auth_token_" + str(int(time.time()))
    )
