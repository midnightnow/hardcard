from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Set, Tuple, Any
from enum import Enum
import databutton as db
from app.auth import AuthorizedUser
import time
import json
import uuid
import re
import hashlib

router = APIRouter(prefix="/security-formal")

"""
Formal Mathematical Model for Security System
===================================================

1. AXIOMS AND DEFINITIONS
-------------------------

DEFINITION 1 (Security State): The security state S of a user u is defined as an ordered tuple:
S_u = (L, M, B, V, A)
where:
- L ∈ {LOW, MEDIUM, HIGH, MAXIMUM} is the security level
- M ⊆ {SMS, EMAIL, AUTHENTICATOR, SECURITY_KEY, BIOMETRIC, HARDCARD} is the set of enabled MFA methods
- B ∈ {true, false} is the MFA requirement boolean
- V ∈ {true, false} is the location verification boolean
- A ∈ {true, false} is the unusual activity alerts boolean

DEFINITION 2 (Security Score): The security score σ(S) is a function that maps a security state to a real number in [0, 100]:
σ(S_u) = λ(L) + μ(M) + β(B) + ν(V) + α(A)
where:
- λ(L) represents the base score for security level
- μ(M) represents the score for MFA methods
- β(B) represents the score for MFA requirement
- ν(V) represents the score for location verification
- α(A) represents the score for unusual activity alerts

DEFINITION 3 (Security Event): A security event E is defined as a tuple:
E = (u, t, τ, D, ρ)
where:
- u is the user identifier
- t ∈ ℝ⁺ is the timestamp
- τ is the event type
- D is a dictionary of event details
- ρ ∈ {INFO, WARN, ERROR, CRITICAL} is the severity level

AXIOM 1 (Security Monotonicity): For any two security states S_1 and S_2 where S_2 is derived from S_1 by enabling additional security features, the security score must increase: S_1 ⊂ S_2 ⟹ σ(S_1) < σ(S_2)

AXIOM 2 (Event Immutability): Once recorded, a security event cannot be modified or deleted. ∀E ∈ Events: E remains unchanged after creation.

2. SECURITY STATE ALGEBRA
-------------------------

Theorem 1 (Security State Composition): Security states can be combined using an operator ⊕ such that:
S_u ⊕ ΔS = S'_u
where ΔS represents a partial security state update.

Let ΔS = (L', M', B', V', A') where any component might be undefined (∅).
Then S_u ⊕ ΔS = (L ⊕ L', M ⊕ M', B ⊕ B', V ⊕ V', A ⊕ A')
where:
- L ⊕ L' = L' if L' ≠ ∅, otherwise L
- M ⊕ M' = M ∪ M' if M' ≠ ∅, otherwise M
- B ⊕ B' = B' if B' ≠ ∅, otherwise B
- V ⊕ V' = V' if V' ≠ ∅, otherwise V
- A ⊕ A' = A' if A' ≠ ∅, otherwise A

Property 1 (State Transition): Any security state transition S_u → S'_u must ensure σ(S'_u) ≥ σ(S_u) unless explicitly authorized as a security reset operation.

3. EVENT SEQUENCE ALGEBRA
-------------------------

Let Ω_u be the sequence of security events for user u ordered by timestamp.

Definition 4 (Event Sequence): Ω_u = (E_1, E_2, ..., E_n) where t_i < t_j for all i < j.

Theorem 2 (Event Projection): Given an event sequence Ω and a predicate p, the filtered sequence Ω|_p = (E ∈ Ω | p(E)) preserves the temporal ordering of the original sequence.

Definition 5 (Threat Detection): A threat is detected when an anomaly function α(Ω_u, E_new) exceeds a threshold θ, indicating the new event is significantly different from the established pattern in Ω_u.

4. FORMAL VERIFICATION METHODS
-----------------------------

Verification Procedure: VerifySecurity(S_u, Ω_u)

1. State Property Verification:
   - Verify that σ(S_u) ≥ min_score(S_u.L) where min_score is the minimum security score required for a given security level
   - Verify that |S_u.M| ≥ min_methods(S_u.L) where min_methods is the minimum number of MFA methods required for a given security level

2. Event Integrity Verification:
   - Verify that ∀i,j: i < j ⟹ Ω_u[i].t < Ω_u[j].t (strict temporal ordering)
   - Verify that events involving security state changes are consistent with the current security state

3. Anomaly Detection:
   - For any new event E, compute anomaly score α(Ω_u, E)
   - If α(Ω_u, E) > θ, generate a security threat alert
"""

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

class SecurityEventSeverity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    CRITICAL = "critical"

class FormalSecurityState(BaseModel):
    """Formal representation of user security state"""
    user_id: str
    security_level: SecurityLevel
    mfa_methods: Set[MFAMethod]
    mfa_required: bool
    location_verification: bool
    unusual_activity_alerts: bool
    security_score: float
    last_update_timestamp: int

class FormalSecurityEvent(BaseModel):
    """Formal representation of a security event"""
    user_id: str
    timestamp: int
    event_type: str
    details: Dict[str, Any]
    severity: SecurityEventSeverity
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)

class SecurityStateUpdate(BaseModel):
    """Partial update to security state"""
    security_level: Optional[SecurityLevel] = None
    mfa_methods_to_add: Optional[Set[MFAMethod]] = None
    mfa_methods_to_remove: Optional[Set[MFAMethod]] = None
    mfa_required: Optional[bool] = None
    location_verification: Optional[bool] = None
    unusual_activity_alerts: Optional[bool] = None

class SecurityVerificationResult(BaseModel):
    """Result of a formal security verification"""
    valid: bool
    security_score: float
    verification_errors: List[str] = []
    satisfied_properties: List[str] = []

# Helper functions
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_user_formal_security_state(user_id: str) -> FormalSecurityState:
    """Get or create user's formal security state"""
    key = sanitize_storage_key(f"formal_security_state_{user_id}")
    try:
        data = db.storage.json.get(key)
        # Convert mfa_methods list to set
        if "mfa_methods" in data and isinstance(data["mfa_methods"], list):
            data["mfa_methods"] = set(data["mfa_methods"])
        return FormalSecurityState(**data)
    except:
        # Create default security state with formal properties
        default_state = FormalSecurityState(
            user_id=user_id,
            security_level=SecurityLevel.MEDIUM,
            mfa_methods=set(),
            mfa_required=False,
            location_verification=False,
            unusual_activity_alerts=True,
            security_score=calculate_formal_security_score(
                SecurityLevel.MEDIUM, set(), False, False, True
            ),
            last_update_timestamp=int(time.time())
        )
        # Convert the set to list for storage
        state_dict = default_state.dict()
        state_dict["mfa_methods"] = list(state_dict["mfa_methods"])
        db.storage.json.put(key, state_dict)
        return default_state

def save_user_formal_security_state(state: FormalSecurityState):
    """Save user's formal security state"""
    key = sanitize_storage_key(f"formal_security_state_{state.user_id}")
    # Convert the set to list for storage
    state_dict = state.dict()
    state_dict["mfa_methods"] = list(state_dict["mfa_methods"])
    db.storage.json.put(key, state_dict)

def append_security_event(event: FormalSecurityEvent):
    """Append a security event to the user's event sequence"""
    # Save the individual event
    event_key = sanitize_storage_key(f"formal_security_event_{event.user_id}_{event.event_id}")
    db.storage.json.put(event_key, event.dict())
    
    # Append to the user's event sequence
    sequence_key = sanitize_storage_key(f"formal_security_events_{event.user_id}")
    try:
        events = db.storage.json.get(sequence_key) or []
    except:
        events = []
    
    # Add new event and maintain temporal ordering
    events.append(event.dict())
    events.sort(key=lambda e: e["timestamp"])
    
    # Keep only the most recent 100 events
    if len(events) > 100:
        events = events[-100:]
    
    db.storage.json.put(sequence_key, events)

def get_user_security_events(user_id: str) -> List[FormalSecurityEvent]:
    """Get user's security event sequence"""
    sequence_key = sanitize_storage_key(f"formal_security_events_{user_id}")
    try:
        events_data = db.storage.json.get(sequence_key) or []
        return [FormalSecurityEvent(**event) for event in events_data]
    except:
        return []

def calculate_formal_security_score(
    security_level: SecurityLevel, 
    mfa_methods: Set[MFAMethod],
    mfa_required: bool,
    location_verification: bool,
    unusual_activity_alerts: bool
) -> float:
    """Calculate security score based on formal definitions"""
    # Base scores by security level (λ function)
    level_scores = {
        SecurityLevel.LOW: 10.0,
        SecurityLevel.MEDIUM: 30.0,
        SecurityLevel.HIGH: 60.0,
        SecurityLevel.MAXIMUM: 70.0
    }
    
    # μ(M) - Score for MFA methods
    mfa_score = min(len(mfa_methods) * 10.0, 30.0)
    
    # Extra for Hardcard (formal weight for premium method)
    if MFAMethod.HARDCARD in mfa_methods:
        mfa_score += 15.0
    
    # β(B) - Score for MFA requirement
    mfa_required_score = 10.0 if mfa_required else 0.0
    
    # ν(V) - Score for location verification
    location_score = 10.0 if location_verification else 0.0
    
    # α(A) - Score for unusual activity alerts
    alerts_score = 5.0 if unusual_activity_alerts else 0.0
    
    # Total score - σ(S_u) function
    total_score = (
        level_scores[security_level] + 
        mfa_score + 
        mfa_required_score + 
        location_score + 
        alerts_score
    )
    
    # Apply formal cap at 100
    return min(total_score, 100.0)

def compose_security_states(current: FormalSecurityState, update: SecurityStateUpdate) -> FormalSecurityState:
    """Compose current state with update using formal ⊕ operator"""
    # Start with the current state
    new_state = FormalSecurityState(
        user_id=current.user_id,
        security_level=current.security_level,
        mfa_methods=current.mfa_methods.copy(),
        mfa_required=current.mfa_required,
        location_verification=current.location_verification,
        unusual_activity_alerts=current.unusual_activity_alerts,
        security_score=current.security_score,
        last_update_timestamp=int(time.time())
    )
    
    # Apply updates using the formal composition rules
    if update.security_level is not None:
        new_state.security_level = update.security_level
    
    if update.mfa_methods_to_add is not None:
        new_state.mfa_methods.update(update.mfa_methods_to_add)
    
    if update.mfa_methods_to_remove is not None:
        new_state.mfa_methods.difference_update(update.mfa_methods_to_remove)
    
    if update.mfa_required is not None:
        new_state.mfa_required = update.mfa_required
    
    if update.location_verification is not None:
        new_state.location_verification = update.location_verification
    
    if update.unusual_activity_alerts is not None:
        new_state.unusual_activity_alerts = update.unusual_activity_alerts
    
    # Recalculate security score based on formal definition
    new_state.security_score = calculate_formal_security_score(
        new_state.security_level,
        new_state.mfa_methods,
        new_state.mfa_required,
        new_state.location_verification,
        new_state.unusual_activity_alerts
    )
    
    return new_state

def verify_security_state(state: FormalSecurityState) -> Tuple[bool, List[str], List[str]]:
    """Formally verify a security state against security axioms"""
    errors = []
    satisfied_properties = []
    
    # Verify minimum security score for each level
    min_scores = {
        SecurityLevel.LOW: 0.0,
        SecurityLevel.MEDIUM: 25.0,
        SecurityLevel.HIGH: 50.0,
        SecurityLevel.MAXIMUM: 75.0
    }
    
    if state.security_score < min_scores[state.security_level]:
        errors.append(f"Security score {state.security_score} is below minimum threshold {min_scores[state.security_level]} for level {state.security_level}")
    else:
        satisfied_properties.append("Minimum Security Score")
    
    # Verify minimum MFA methods for each level
    min_methods = {
        SecurityLevel.LOW: 0,
        SecurityLevel.MEDIUM: 1,
        SecurityLevel.HIGH: 2,
        SecurityLevel.MAXIMUM: 3
    }
    
    if len(state.mfa_methods) < min_methods[state.security_level]:
        errors.append(f"Number of MFA methods {len(state.mfa_methods)} is below minimum requirement {min_methods[state.security_level]} for level {state.security_level}")
    else:
        satisfied_properties.append("Minimum MFA Methods")
    
    # Verify MFA requirement for HIGH and MAXIMUM levels
    if state.security_level in [SecurityLevel.HIGH, SecurityLevel.MAXIMUM] and not state.mfa_required:
        errors.append(f"MFA must be required for security level {state.security_level}")
    else:
        satisfied_properties.append("MFA Requirement Consistency")
    
    # Verify location verification for MAXIMUM level
    if state.security_level == SecurityLevel.MAXIMUM and not state.location_verification:
        errors.append("Location verification must be enabled for MAXIMUM security level")
    else:
        satisfied_properties.append("Location Verification Consistency")
    
    # Verify calculated security score matches definition
    expected_score = calculate_formal_security_score(
        state.security_level,
        state.mfa_methods,
        state.mfa_required,
        state.location_verification,
        state.unusual_activity_alerts
    )
    
    if abs(state.security_score - expected_score) > 0.001:
        errors.append(f"Security score {state.security_score} does not match calculated score {expected_score}")
    else:
        satisfied_properties.append("Security Score Consistency")
    
    return len(errors) == 0, errors, satisfied_properties

# Endpoints
@router.get("/state")
async def get_formal_security_state(user: AuthorizedUser) -> FormalSecurityState:
    """Get user's formal security state"""
    state = get_user_formal_security_state(user.sub)
    
    # Record a formal security event
    append_security_event(FormalSecurityEvent(
        user_id=user.sub,
        timestamp=int(time.time()),
        event_type="security_state_accessed",
        details={},
        severity=SecurityEventSeverity.INFO
    ))
    
    return state

@router.put("/state")
async def update_formal_security_state(update: SecurityStateUpdate, user: AuthorizedUser) -> FormalSecurityState:
    """Update user's formal security state using state composition"""
    current_state = get_user_formal_security_state(user.sub)
    
    # Apply the formal composition operation
    new_state = compose_security_states(current_state, update)
    
    # Verify the new state
    valid, errors, properties = verify_security_state(new_state)
    
    if not valid:
        # Record verification failure
        append_security_event(FormalSecurityEvent(
            user_id=user.sub,
            timestamp=int(time.time()),
            event_type="security_state_update_failed",
            details={
                "errors": errors,
                "update": update.dict(exclude_unset=True)
            },
            severity=SecurityEventSeverity.ERROR
        ))
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid security state", "errors": errors}
        )
    
    # Record successful update
    append_security_event(FormalSecurityEvent(
        user_id=user.sub,
        timestamp=int(time.time()),
        event_type="security_state_updated",
        details={
            "previous_state": {
                "security_level": current_state.security_level,
                "mfa_methods": list(current_state.mfa_methods),
                "security_score": current_state.security_score
            },
            "new_state": {
                "security_level": new_state.security_level,
                "mfa_methods": list(new_state.mfa_methods),
                "security_score": new_state.security_score
            },
            "properties_satisfied": properties
        },
        severity=SecurityEventSeverity.INFO
    ))
    
    # Save the new state
    save_user_formal_security_state(new_state)
    
    return new_state

@router.get("/events")
async def get_formal_security_events(user: AuthorizedUser) -> List[FormalSecurityEvent]:
    """Get user's formal security event sequence"""
    return get_user_security_events(user.sub)

@router.post("/verify")
async def verify_formal_security(user: AuthorizedUser) -> SecurityVerificationResult:
    """Perform formal verification of security state"""
    state = get_user_formal_security_state(user.sub)
    
    # Verify the state
    valid, errors, properties = verify_security_state(state)
    
    # Record verification event
    append_security_event(FormalSecurityEvent(
        user_id=user.sub,
        timestamp=int(time.time()),
        event_type="security_verification_performed",
        details={
            "valid": valid,
            "errors": errors,
            "properties_satisfied": properties
        },
        severity=SecurityEventSeverity.INFO if valid else SecurityEventSeverity.WARN
    ))
    
    return SecurityVerificationResult(
        valid=valid,
        security_score=state.security_score,
        verification_errors=errors,
        satisfied_properties=properties
    )

@router.post("/detect-anomalies")
async def detect_security_anomalies(user: AuthorizedUser) -> Dict[str, Any]:
    """Detect anomalies in the security event sequence using formal criteria"""
    events = get_user_security_events(user.sub)
    
    if len(events) < 5:
        return {
            "anomalies_detected": [],
            "confidence": 0.0,
            "message": "Insufficient events for anomaly detection"
        }
    
    # In a real implementation, this would use sophisticated anomaly detection algorithms
    # based on the formal definition of anomalies
    
    # For demonstration, we'll use a simplified formal approach:
    # 1. Calculate the average time between events (temporal pattern)
    # 2. Flag events that deviate significantly from this pattern
    
    # Calculate average time between events
    time_diffs = [events[i+1].timestamp - events[i].timestamp for i in range(len(events)-1)]
    avg_time_diff = sum(time_diffs) / len(time_diffs) if time_diffs else 0
    std_dev = (
        (sum((t - avg_time_diff) ** 2 for t in time_diffs) / len(time_diffs)) ** 0.5
        if time_diffs else 0
    )
    
    # Flag anomalies (events with timestamp differences > 2 standard deviations)
    threshold = avg_time_diff + (2 * std_dev)
    
    anomalies = []
    for i in range(1, len(events)):
        time_diff = events[i].timestamp - events[i-1].timestamp
        if time_diff > threshold:
            anomalies.append({
                "event_id": events[i].event_id,
                "timestamp": events[i].timestamp,
                "event_type": events[i].event_type,
                "anomaly_type": "temporal_deviation",
                "expected_max_time": threshold,
                "actual_time": time_diff,
                "confidence": min(1.0, (time_diff - threshold) / threshold)
            })
    
    # Record the anomaly detection event
    append_security_event(FormalSecurityEvent(
        user_id=user.sub,
        timestamp=int(time.time()),
        event_type="anomaly_detection_performed",
        details={
            "anomalies_found": len(anomalies),
            "total_events_analyzed": len(events),
            "temporal_threshold": threshold
        },
        severity=SecurityEventSeverity.INFO if not anomalies else SecurityEventSeverity.WARN
    ))
    
    return {
        "anomalies_detected": anomalies,
        "confidence": 0.7 if anomalies else 0.8,  # Confidence in the analysis
        "message": f"Detected {len(anomalies)} anomalies in {len(events)} events"
    }
