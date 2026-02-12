from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import databutton as db
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

router = APIRouter()

# Models
class SecurityEvent(BaseModel):
    event_type: str
    user_id: str
    timestamp: float
    severity: str
    details: Dict[str, Any]
    source_ip: Optional[str] = None
    geo_location: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None

class LearningModelState(BaseModel):
    last_updated: float
    training_iterations: int
    feature_weights: Dict[str, float]
    pattern_thresholds: Dict[str, float]
    risk_scores: Dict[str, float]  # Risk scores for different event patterns
    adaptive_rules: List[Dict[str, Any]]

class AdaptiveLearningResponse(BaseModel):
    success: bool
    message: str
    model_version: int
    adaptive_measures_applied: List[str]
    security_score_delta: float

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_learning_model():
    """Retrieve the current learning model or create default if none exists"""
    try:
        model_data = db.storage.json.get(sanitize_storage_key("security_learning_model"))
        return LearningModelState(**model_data)
    except:
        # Initialize default model with basic weights and thresholds
        return LearningModelState(
            last_updated=time.time(),
            training_iterations=0,
            feature_weights={
                "login_failure": 0.7,
                "unusual_location": 0.8,
                "api_abuse": 0.6,
                "data_access_rate": 0.5,
                "session_anomaly": 0.7,
                "time_pattern": 0.4
            },
            pattern_thresholds={
                "login_failure_rate": 3.0,  # failures per hour
                "location_distance": 1000.0,  # km
                "api_requests_rate": 30.0,  # requests per minute
                "data_access_volume": 50.0,  # MB per hour
                "session_duration": 8.0  # hours
            },
            risk_scores={
                "brute_force": 0.9,
                "account_takeover": 0.95,
                "data_exfiltration": 0.85,
                "api_abuse": 0.7,
                "session_hijacking": 0.8
            },
            adaptive_rules=[
                {
                    "pattern": "consecutive_failed_logins",
                    "threshold": 5,
                    "action": "increase_mfa_requirement",
                    "duration_hours": 24
                },
                {
                    "pattern": "unusual_location_access",
                    "threshold": 2,
                    "action": "require_additional_verification",
                    "duration_hours": 48
                },
                {
                    "pattern": "rapid_settings_changes",
                    "threshold": 3,
                    "action": "notify_user",
                    "duration_hours": 1
                }
            ]
        )

def save_learning_model(model: LearningModelState):
    """Save the updated learning model"""
    model.last_updated = time.time()
    db.storage.json.put(sanitize_storage_key("security_learning_model"), model.dict())

def get_recent_security_events(hours: int = 24) -> List[SecurityEvent]:
    """Get security events from the last n hours"""
    try:
        audit_log = db.storage.json.get(sanitize_storage_key("security_audit_log"), default=[])
        cutoff_time = time.time() - (hours * 3600)
        return [SecurityEvent(**event) for event in audit_log if event.get('timestamp', 0) > cutoff_time]
    except Exception as e:
        print(f"Error retrieving security events: {e}")
        return []

def update_user_security_settings(user_id: str, updates: Dict[str, Any]):
    """Update a user's security settings based on adaptive measures"""
    try:
        # Get all security settings
        all_settings = db.storage.json.get(sanitize_storage_key("user_security_settings"), default={})
        
        # Get user's settings or create defaults
        user_settings = all_settings.get(user_id, {
            "user_id": user_id,
            "security_level": "medium",
            "mfa_methods_enabled": [],
            "mfa_required": False,
            "location_verification": False,
            "unusual_activity_alerts": True,
            "last_security_update": time.time(),
            "security_score": 50,
            "adaptive_measures": []
        })
        
        # Apply updates
        for key, value in updates.items():
            if key == "adaptive_measures":
                # Add new measures without duplicates
                existing_measures = user_settings.get("adaptive_measures", [])
                for measure in value:
                    if measure not in existing_measures:
                        existing_measures.append(measure)
                user_settings["adaptive_measures"] = existing_measures
            else:
                user_settings[key] = value
        
        # Update timestamp
        user_settings["last_security_update"] = time.time()
        
        # Save back to storage
        all_settings[user_id] = user_settings
        db.storage.json.put(sanitize_storage_key("user_security_settings"), all_settings)
        
        return user_settings
    except Exception as e:
        print(f"Error updating security settings: {e}")
        return None

def apply_adaptive_measures(user_id: str, model: LearningModelState, events: List[SecurityEvent]):
    """Apply adaptive security measures based on detected patterns"""
    if not events:
        return [], 0  # No events to analyze
        
    applied_measures = []
    security_score_change = 0
    
    # Count and analyze patterns
    patterns = {
        "consecutive_failed_logins": 0,
        "unusual_location_access": 0,
        "rapid_settings_changes": 0,
        "suspicious_data_access": 0,
        "anomalous_behavior": 0
    }
    
    # Simple pattern detection for demo purposes
    for event in events:
        if event.event_type == "login_failure":
            patterns["consecutive_failed_logins"] += 1
        elif event.event_type == "unusual_location_detected":
            patterns["unusual_location_access"] += 1
        elif event.event_type == "settings_change":
            patterns["rapid_settings_changes"] += 1
        elif event.event_type == "data_access" and event.severity in ["warning", "critical"]:
            patterns["suspicious_data_access"] += 1
        
        # Simple anomaly detection based on event severity
        if event.severity == "critical":
            patterns["anomalous_behavior"] += 2
        elif event.severity == "warning":
            patterns["anomalous_behavior"] += 1
    
    # Apply adaptive rules based on detected patterns
    updates = {}
    for rule in model.adaptive_rules:
        pattern = rule["pattern"]
        if pattern in patterns and patterns[pattern] >= rule["threshold"]:
            action = rule["action"]
            
            # Apply the action
            if action == "increase_mfa_requirement":
                updates["mfa_required"] = True
                applied_measures.append("Enforced multi-factor authentication")
                security_score_change += 5
                
            elif action == "require_additional_verification":
                updates["location_verification"] = True
                applied_measures.append("Enabled location verification")
                security_score_change += 3
                
            elif action == "notify_user":
                # Would trigger a notification - log it for now
                applied_measures.append("Sent security alert notification")
                security_score_change += 1
                
            # Add record of this adaptive measure with expiration
            measure = {
                "type": action,
                "reason": pattern,
                "applied_at": time.time(),
                "expires_at": time.time() + (rule["duration_hours"] * 3600)
            }
            
            if "adaptive_measures" not in updates:
                updates["adaptive_measures"] = []
            updates["adaptive_measures"].append(measure)
    
    # Apply security level upgrade if needed
    if security_score_change >= 10:
        # Upgrade security level if multiple serious issues detected
        security_levels = ["low", "medium", "high", "maximum"]
        current_settings = db.storage.json.get(sanitize_storage_key("user_security_settings"), default={}).get(user_id, {})
        current_level = current_settings.get("security_level", "medium")
        
        try:
            current_index = security_levels.index(current_level)
            if current_index < len(security_levels) - 1:
                updates["security_level"] = security_levels[current_index + 1]
                applied_measures.append(f"Upgraded security level to {security_levels[current_index + 1]}")
        except ValueError:
            pass  # Invalid current security level
    
    # Apply the updates if any measures were taken
    if updates:
        # Update security score
        if "security_score" not in updates:
            current_settings = db.storage.json.get(sanitize_storage_key("user_security_settings"), default={}).get(user_id, {})
            current_score = current_settings.get("security_score", 50)
            updates["security_score"] = min(100, current_score + security_score_change)
        
        # Save updates
        update_user_security_settings(user_id, updates)
    
    return applied_measures, security_score_change

def update_learning_model(model: LearningModelState, events: List[SecurityEvent]):
    """Update the learning model based on recent security events"""
    if not events:
        return model  # No new data to learn from
    
    # Simulate learning by updating weights based on event frequencies
    event_types = {}
    severity_counts = {"info": 0, "warning": 0, "critical": 0}
    
    for event in events:
        # Count event types
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        # Count severity levels
        severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1
    
    # Update feature weights based on event frequency
    for event_type, count in event_types.items():
        if event_type.startswith("login_"):
            model.feature_weights["login_failure"] = min(1.0, model.feature_weights.get("login_failure", 0.5) + (count * 0.01))
        elif "location" in event_type:
            model.feature_weights["unusual_location"] = min(1.0, model.feature_weights.get("unusual_location", 0.5) + (count * 0.01))
        elif "api" in event_type:
            model.feature_weights["api_abuse"] = min(1.0, model.feature_weights.get("api_abuse", 0.5) + (count * 0.01))
    
    # Adjust thresholds based on severity distribution
    total_events = sum(severity_counts.values())
    if total_events > 0:
        critical_ratio = severity_counts.get("critical", 0) / total_events
        warning_ratio = severity_counts.get("warning", 0) / total_events
        
        # If we're seeing more critical events, lower thresholds to be more sensitive
        threshold_adjustment = -0.1 if critical_ratio > 0.1 else (0.1 if critical_ratio == 0 else 0)
        
        for key in model.pattern_thresholds:
            # Adjust threshold, ensuring it stays in reasonable range
            model.pattern_thresholds[key] = max(0.5, min(10.0, 
                model.pattern_thresholds[key] + threshold_adjustment))
    
    # Increment training iterations
    model.training_iterations += 1
    
    return model

# Endpoint for triggering adaptive learning
@router.post("/security_adaptive_learning")
async def security_adaptive_learning_main() -> AdaptiveLearningResponse:
    """Run the adaptive security learning system to analyze patterns and adapt security measures"""
    try:
        # Get current learning model
        model = get_learning_model()
        
        # Get recent security events (last 24 hours)
        events = get_recent_security_events(hours=24)
        
        # Process each user's events separately
        user_events = {}
        for event in events:
            if event.user_id not in user_events:
                user_events[event.user_id] = []
            user_events[event.user_id].append(event)
        
        # Track overall changes
        all_applied_measures = []
        total_score_delta = 0
        
        # Apply adaptive measures for each user
        for user_id, user_event_list in user_events.items():
            measures, score_delta = apply_adaptive_measures(user_id, model, user_event_list)
            all_applied_measures.extend(measures)
            total_score_delta += score_delta
        
        # Update the learning model with all recent events
        updated_model = update_learning_model(model, events)
        save_learning_model(updated_model)
        
        # Return results
        return AdaptiveLearningResponse(
            success=True,
            message="Adaptive security learning completed successfully",
            model_version=updated_model.training_iterations,
            adaptive_measures_applied=all_applied_measures,
            security_score_delta=total_score_delta / max(len(user_events), 1)  # Average score change
        )
    except Exception as e:
        print(f"Error in adaptive security learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))
