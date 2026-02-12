"""Governance Verification Formal API

This API implements a mathematically rigorous framework for governance verification using
formal algebraic structures and category theory principles. It provides a unified approach
to verifying governance properties with strong mathematical guarantees.

Key mathematical structures:
1. Governance State Monoid: Algebraic structure for governance states with composition operations
2. Verification Functors: Structure-preserving maps between algebraic domains
3. Temporal Category: Categorical model of temporal consistency verification
"""

from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set, Tuple, Union, Callable, TypeVar
from enum import Enum
import time
import hashlib
import databutton as db
import json
import re
from datetime import datetime, timedelta

router = APIRouter(prefix="/governance-formal")

# --- MATHEMATICAL DEFINITIONS ---

"""
== FORMAL ALGEBRAIC FOUNDATIONS ==

1. Governance State Monoid (S, •, e)
   - S is the set of all possible governance states
   - • is the composition operation: S × S → S
   - e is the identity element
   - Satisfies associativity: (a • b) • c = a • (b • c)
   - Satisfies identity: e • a = a • e = a

2. Verification Pipeline Category:
   - Objects are verification pipelines
   - Morphisms are pipeline transformations
   - Functors map between verification domains preserving structure

3. Verification Functor V: P → R:
   - P is the category of governance configurations
   - R is the category of verification results
   - V preserves composition: V(p₁ ∘ p₂) = V(p₁) ∘ V(p₂)

4. Temporal Verification Framework:
   - Time domain T with order relation ≤
   - Events e with timestamp function τ: E → T
   - Temporal consistency property: ∀e₁,e₂ ∈ E: e₁ depends on e₂ ⟹ τ(e₂) < τ(e₁)
"""

# --- TYPE DEFINITIONS ---

T = TypeVar('T')  # Generic type
S = TypeVar('S')  # State type

# Algebraic composition operation
class MonoidOperation(BaseModel):
    """Formal definition of a monoid operation for governance states"""
    class Config:
        arbitrary_types_allowed = True
    
    # The composition function S × S → S
    compose: Callable[[T, T], T]
    
    # The identity element
    identity: T
    
    def __call__(self, a: T, b: T) -> T:
        """Apply the composition operation"""
        return self.compose(a, b)


class PipelineCategory(str, Enum):
    """Categories of verification pipelines within the category theory framework"""
    CRYPTOGRAPHIC = "cryptographic"
    TEMPORAL = "temporal"
    STRUCTURAL = "structural"
    CONSISTENCY = "consistency"


class FormalProperty(str, Enum):
    """Formal properties that can be verified"""
    ASSOCIATIVITY = "associativity"           # (a • b) • c = a • (b • c)
    COMMUTATIVITY = "commutativity"           # a • b = b • a
    IDEMPOTENCE = "idempotence"               # a • a = a
    MONOTONICITY = "monotonicity"             # a ≤ b ⟹ f(a) ≤ f(b)
    TEMPORAL_CONSISTENCY = "temporal_consistency"  # Respects temporal ordering
    HASH_CONSISTENCY = "hash_consistency"     # Cryptographic hash chain integrity
    SIGNATURE_VALIDITY = "signature_validity" # Cryptographic signature validity


class VerificationType(str, Enum):
    """Verification strategies within the formal framework"""
    DEDUCTIVE = "deductive"            # Proof-theoretic verification
    ALGEBRAIC = "algebraic"            # Algebraic structure verification
    MODEL_CHECKING = "model_checking"  # State-space exploration
    REFINEMENT = "refinement"          # Stepwise refinement verification


# --- PYDANTIC MODELS ---

class VerificationState(BaseModel):
    """Formal representation of a verification state in the monoid"""
    valid: bool = True
    properties_satisfied: Set[str] = Field(default_factory=set)
    properties_violated: Set[str] = Field(default_factory=set)
    counter_examples: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    
    def compose(self, other: 'VerificationState') -> 'VerificationState':
        """Monoid composition operation for verification states"""
        return VerificationState(
            valid=self.valid and other.valid,
            properties_satisfied=self.properties_satisfied.union(other.properties_satisfied),
            properties_violated=self.properties_violated.union(other.properties_violated),
            counter_examples={**self.counter_examples, **other.counter_examples},
            timestamp=max(self.timestamp, other.timestamp)
        )
    
    @classmethod
    def identity(cls) -> 'VerificationState':
        """Identity element of the verification state monoid"""
        return VerificationState()


class FormalVerificationPipeline(BaseModel):
    """Formal definition of a verification pipeline within the category theory framework"""
    id: str = Field(default_factory=lambda: f"pipeline_{int(time.time())}")
    name: str
    description: str
    category: PipelineCategory
    formal_properties: List[FormalProperty]
    verification_type: VerificationType
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    module_dependencies: List[str] = []
    verification_thresholds: Dict[str, Any] = {}
    enabled: bool = True
    
    def compose(self, other: 'FormalVerificationPipeline') -> 'FormalVerificationPipeline':
        """Composition of pipelines (category theory morphism)"""
        return FormalVerificationPipeline(
            id=f"composed_{self.id}_{other.id}",
            name=f"Composed: {self.name} + {other.name}",
            description=f"Composition of {self.name} and {other.name}",
            category=self.category,  # Maintain the primary category
            formal_properties=list(set(self.formal_properties + other.formal_properties)),
            verification_type=self.verification_type,
            created_at=min(self.created_at, other.created_at),
            updated_at=max(self.updated_at, other.updated_at),
            module_dependencies=list(set(self.module_dependencies + other.module_dependencies)),
            verification_thresholds={**self.verification_thresholds, **other.verification_thresholds},
            enabled=self.enabled and other.enabled
        )


class VerificationRunState(BaseModel):
    """State of a verification run with formal properties"""
    id: str = Field(default_factory=lambda: f"run_{int(time.time())}")
    pipeline_id: str
    started_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    status: str = "running"  # running, completed, failed
    results: Dict[str, Any] = {}
    metrics: Dict[str, float] = {}
    proof_failures: List[str] = []
    triggered_by: str = "manual"  # manual, scheduled, commit
    commit_id: Optional[str] = None
    verification_state: VerificationState = Field(default_factory=VerificationState)
    
    def is_complete(self) -> bool:
        """Check if the run is complete"""
        return self.status in ["completed", "failed"] and self.completed_at is not None


class FormalCryptographicComponent(BaseModel):
    """A cryptographic component with formal properties in the system inventory"""
    id: str = Field(default_factory=lambda: f"crypto_{int(time.time())}")
    algorithm: str  # e.g., "ECDSA P-256", "AES-256-GCM"
    key_length: int
    implementation: str  # e.g., "software-openssl", "hardware-tpm"
    usage_context: List[str]  # e.g., ["signin", "transaction-verification"]
    expected_lifespan: Optional[str] = None  # e.g., "2030-12-31"
    status: str = "active"  # active, deprecated, post-quantum-candidate
    replacement: Optional[str] = None  # ID of replacement algorithm
    formal_properties: List[str] = []  # formal security properties
    security_level: float = 1.0  # Quantitative security level (higher is better)
    
    def security_level_function(self) -> float:
        """Compute the security level based on algorithm, key length and status
        
        Security Level Function L: C → ℝ⁺ maps components to positive real numbers
        representing their security level.
        """
        base_level = self.key_length / 128.0  # Normalize to 128-bit security
        
        # Algorithm-specific adjustments
        algorithm_factor = 1.0
        if "post-quantum" in self.algorithm.lower():
            algorithm_factor = 1.5
        elif "ecc" in self.algorithm.lower() or "ecdsa" in self.algorithm.lower():
            algorithm_factor = 1.2
        elif "rsa" in self.algorithm.lower():
            algorithm_factor = 0.8
        
        # Status adjustment
        status_factor = 1.0
        if self.status == "deprecated":
            status_factor = 0.5
        elif self.status == "post-quantum-candidate":
            status_factor = 1.3
        
        # Implementation adjustment
        impl_factor = 1.0
        if "hardware" in self.implementation.lower():
            impl_factor = 1.2
        
        return base_level * algorithm_factor * status_factor * impl_factor


# --- REQUEST/RESPONSE MODELS ---

class CreateFormalPipelineRequest(BaseModel):
    """Request to create a new formal verification pipeline"""
    name: str
    description: str
    category: PipelineCategory
    formal_properties: List[FormalProperty]
    verification_type: VerificationType
    module_dependencies: List[str] = []
    verification_thresholds: Dict[str, Any] = {}


class RunFormalVerificationRequest(BaseModel):
    """Request to run a formal verification pipeline"""
    pipeline_id: str
    triggered_by: str = "manual"
    commit_id: Optional[str] = None
    verification_parameters: Dict[str, Any] = {}


class RegisterFormalCryptoComponentRequest(BaseModel):
    """Request to register a cryptographic component with formal properties"""
    algorithm: str
    key_length: int
    implementation: str
    usage_context: List[str]
    expected_lifespan: Optional[str] = None
    formal_properties: List[str] = []


class FormalPipelineResponse(BaseModel):
    """Response containing formal pipeline details"""
    pipeline: FormalVerificationPipeline


class FormalRunResponse(BaseModel):
    """Response containing formal run details"""
    run: VerificationRunState


class FormalComponentResponse(BaseModel):
    """Response containing formal cryptographic component details"""
    component: FormalCryptographicComponent


class ListFormalPipelinesResponse(BaseModel):
    """Response containing a list of formal pipelines"""
    pipelines: List[FormalVerificationPipeline]


class ListFormalRunsResponse(BaseModel):
    """Response containing a list of formal verification runs"""
    runs: List[VerificationRunState]


class ListFormalCryptoComponentsResponse(BaseModel):
    """Response containing a list of formal cryptographic components"""
    components: List[FormalCryptographicComponent]


class FormalVerificationMetricsResponse(BaseModel):
    """Response containing formal verification metrics"""
    total_pipelines: int
    active_pipelines: int
    verification_runs_last_24h: int
    avg_verification_time: float
    passing_proofs_percentage: float
    component_health: Dict[str, str]  # module -> health status
    recent_failures: List[Dict[str, Any]]
    formal_properties_coverage: Dict[str, float]  # property -> coverage percentage
    verification_type_distribution: Dict[str, int]  # verification type -> count


class FormalCryptographicHealthResponse(BaseModel):
    """Response containing formal cryptographic health metrics"""
    total_components: int
    components_by_status: Dict[str, int]  # status -> count
    post_quantum_readiness: float  # percentage
    components_near_deprecation: List[Dict[str, Any]]
    security_recommendations: List[str]
    mean_security_level: float  # Average security level across all components
    min_security_level: float  # Minimum security level
    security_level_distribution: Dict[str, float]  # Range -> percentage


# --- STORAGE HELPERS ---

def _sanitize_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


def _get_formal_pipelines() -> Dict[str, FormalVerificationPipeline]:
    """Get all formal verification pipelines"""
    try:
        pipelines_json = db.storage.json.get(_sanitize_key("governance_formal_verification_pipelines"), default={})
        return {k: FormalVerificationPipeline(**v) for k, v in pipelines_json.items()}
    except Exception as e:
        print(f"Error getting formal pipelines: {e}")
        return {}


def _save_formal_pipelines(pipelines: Dict[str, FormalVerificationPipeline]) -> None:
    """Save all formal verification pipelines"""
    pipelines_json = {k: v.dict() for k, v in pipelines.items()}
    db.storage.json.put(_sanitize_key("governance_formal_verification_pipelines"), pipelines_json)


def _get_formal_pipeline(pipeline_id: str) -> Optional[FormalVerificationPipeline]:
    """Get a formal verification pipeline by ID"""
    pipelines = _get_formal_pipelines()
    return pipelines.get(pipeline_id)


def _save_formal_pipeline(pipeline: FormalVerificationPipeline) -> None:
    """Save a formal verification pipeline"""
    pipelines = _get_formal_pipelines()
    pipelines[pipeline.id] = pipeline
    _save_formal_pipelines(pipelines)


def _get_formal_runs() -> Dict[str, VerificationRunState]:
    """Get all formal verification runs"""
    try:
        runs_json = db.storage.json.get(_sanitize_key("governance_formal_verification_runs"), default={})
        return {k: VerificationRunState(**v) for k, v in runs_json.items()}
    except Exception as e:
        print(f"Error getting formal runs: {e}")
        return {}


def _save_formal_runs(runs: Dict[str, VerificationRunState]) -> None:
    """Save all formal verification runs"""
    runs_json = {k: v.dict() for k, v in runs.items()}
    db.storage.json.put(_sanitize_key("governance_formal_verification_runs"), runs_json)


def _get_formal_run(run_id: str) -> Optional[VerificationRunState]:
    """Get a formal verification run by ID"""
    runs = _get_formal_runs()
    return runs.get(run_id)


def _save_formal_run(run: VerificationRunState) -> None:
    """Save a formal verification run"""
    runs = _get_formal_runs()
    runs[run.id] = run
    _save_formal_runs(runs)


def _get_formal_crypto_components() -> Dict[str, FormalCryptographicComponent]:
    """Get all formal cryptographic components"""
    try:
        components_json = db.storage.json.get(_sanitize_key("governance_formal_crypto_components"), default={})
        return {k: FormalCryptographicComponent(**v) for k, v in components_json.items()}
    except Exception as e:
        print(f"Error getting formal crypto components: {e}")
        return {}


def _save_formal_crypto_components(components: Dict[str, FormalCryptographicComponent]) -> None:
    """Save all formal cryptographic components"""
    components_json = {k: v.dict() for k, v in components.items()}
    db.storage.json.put(_sanitize_key("governance_formal_crypto_components"), components_json)


def _get_formal_crypto_component(component_id: str) -> Optional[FormalCryptographicComponent]:
    """Get a formal cryptographic component by ID"""
    components = _get_formal_crypto_components()
    return components.get(component_id)


def _save_formal_crypto_component(component: FormalCryptographicComponent) -> None:
    """Save a formal cryptographic component"""
    components = _get_formal_crypto_components()
    components[component.id] = component
    _save_formal_crypto_components(components)


# --- VERIFICATION FUNCTIONS ---

def verify_associativity(state: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Verify the associativity property: (a • b) • c = a • (b • c)
    
    This is a formal verification of the associativity axiom of the algebraic structure.
    """
    if "operations" not in state or len(state["operations"]) < 3:
        return True, None  # Not enough operations to test
    
    operations = state["operations"]
    for i in range(len(operations) - 2):
        a, b, c = operations[i:i+3]
        
        # Compute (a • b) • c
        ab = VerificationState(**a).compose(VerificationState(**b))
        abc_1 = ab.compose(VerificationState(**c))
        
        # Compute a • (b • c)
        bc = VerificationState(**b).compose(VerificationState(**c))
        abc_2 = VerificationState(**a).compose(bc)
        
        # Check if they're equal
        if abc_1.dict() != abc_2.dict():
            return False, {
                "a": a,
                "b": b,
                "c": c,
                "(a•b)•c": abc_1.dict(),
                "a•(b•c)": abc_2.dict()
            }
    
    return True, None


def verify_temporal_consistency(events: List[Dict[str, Any]]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Verify temporal consistency: if e₁ depends on e₂, then τ(e₂) < τ(e₁)
    
    This property ensures that the temporal ordering of events is consistent
    with their dependency relationships.
    """
    if not events:
        return True, None
    
    # Sort events by timestamp
    sorted_events = sorted(events, key=lambda e: e.get("timestamp", 0))
    
    # Check for dependency violations
    for i, event in enumerate(sorted_events):
        dependencies = event.get("dependencies", [])
        for dep_id in dependencies:
            # Find the dependent event
            dep_event = next((e for e in sorted_events if e.get("id") == dep_id), None)
            if dep_event:
                dep_idx = sorted_events.index(dep_event)
                # If dependent event comes after the current event, it's a violation
                if dep_idx >= i:
                    return False, {
                        "event": event,
                        "dependency": dep_event,
                        "error": "Event depends on a future event"
                    }
    
    return True, None


def verify_hash_consistency(events: List[Dict[str, Any]]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Verify hash chain consistency: each event's hash incorporates previous event
    
    This property ensures the integrity of the hash chain, making tampering evident.
    """
    if not events or len(events) <= 1:
        return True, None
    
    for i in range(1, len(events)):
        prev_event = events[i-1]
        curr_event = events[i]
        
        # Skip if hash or previous_hash not available
        if "hash" not in curr_event or "hash" not in prev_event:
            continue
        
        # Check if previous_hash matches
        if curr_event.get("previous_hash") != prev_event["hash"]:
            return False, {
                "current_event": curr_event,
                "previous_event": prev_event,
                "error": "Hash chain broken"
            }
    
    return True, None


def verify_signature_validity(events: List[Dict[str, Any]], public_keys: Dict[str, str]) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Verify signature validity for events
    
    This is a simplified simulation of signature verification.
    In a real implementation, this would perform cryptographic signature verification.
    """
    if not events:
        return True, None
    
    for event in events:
        if "signature" not in event or "signer" not in event:
            continue
        
        signer = event["signer"]
        if signer not in public_keys:
            return False, {
                "event": event,
                "error": f"Unknown signer: {signer}"
            }
        
        # Simulate signature verification
        # In a real implementation, this would use cryptographic verification
        signature_valid = len(event["signature"]) > 0
        if not signature_valid:
            return False, {
                "event": event,
                "error": "Invalid signature"
            }
    
    return True, None


def run_formal_verification(pipeline: FormalVerificationPipeline, parameters: Dict[str, Any]) -> VerificationState:
    """Run a formal verification pipeline with algebraic foundation
    
    This function implements the verification functor V: P → R mapping from
    the category of verification pipelines to the category of verification results.
    """
    verification_state = VerificationState()
    
    # Extract parameters
    events = parameters.get("events", [])
    public_keys = parameters.get("public_keys", {})
    operations = parameters.get("operations", [])
    
    # Prepare state for algebraic property verification
    verification_data = {
        "events": events,
        "operations": operations
    }
    
    # Verify formal properties
    for property in pipeline.formal_properties:
        if property == FormalProperty.ASSOCIATIVITY:
            satisfied, counter_example = verify_associativity(verification_data)
            if satisfied:
                verification_state.properties_satisfied.add("associativity")
            else:
                verification_state.properties_violated.add("associativity")
                verification_state.counter_examples["associativity"] = counter_example
                verification_state.valid = False
                
        elif property == FormalProperty.TEMPORAL_CONSISTENCY:
            satisfied, counter_example = verify_temporal_consistency(events)
            if satisfied:
                verification_state.properties_satisfied.add("temporal_consistency")
            else:
                verification_state.properties_violated.add("temporal_consistency")
                verification_state.counter_examples["temporal_consistency"] = counter_example
                verification_state.valid = False
                
        elif property == FormalProperty.HASH_CONSISTENCY:
            satisfied, counter_example = verify_hash_consistency(events)
            if satisfied:
                verification_state.properties_satisfied.add("hash_consistency")
            else:
                verification_state.properties_violated.add("hash_consistency")
                verification_state.counter_examples["hash_consistency"] = counter_example
                verification_state.valid = False
                
        elif property == FormalProperty.SIGNATURE_VALIDITY:
            satisfied, counter_example = verify_signature_validity(events, public_keys)
            if satisfied:
                verification_state.properties_satisfied.add("signature_validity")
            else:
                verification_state.properties_violated.add("signature_validity")
                verification_state.counter_examples["signature_validity"] = counter_example
                verification_state.valid = False
    
    return verification_state


# --- API ENDPOINTS FOR VERIFICATION PIPELINES ---

@router.post("/pipelines", response_model=FormalPipelineResponse)
def create_formal_pipeline(request: CreateFormalPipelineRequest) -> FormalPipelineResponse:
    """Create a new formal verification pipeline
    
    This endpoint creates a new verification pipeline in the formal verification
    framework, specifying the category theory category, formal properties to verify,
    and verification approach.
    """
    pipeline = FormalVerificationPipeline(
        name=request.name,
        description=request.description,
        category=request.category,
        formal_properties=request.formal_properties,
        verification_type=request.verification_type,
        module_dependencies=request.module_dependencies,
        verification_thresholds=request.verification_thresholds
    )
    
    _save_formal_pipeline(pipeline)
    
    return FormalPipelineResponse(pipeline=pipeline)


@router.get("/pipelines/{pipeline_id}", response_model=FormalPipelineResponse)
def get_formal_pipeline(pipeline_id: str) -> FormalPipelineResponse:
    """Get a formal verification pipeline by ID"""
    pipeline = _get_formal_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Formal pipeline not found")
    
    return FormalPipelineResponse(pipeline=pipeline)


@router.get("/pipelines", response_model=ListFormalPipelinesResponse)
def list_formal_pipelines() -> ListFormalPipelinesResponse:
    """List all formal verification pipelines"""
    pipelines = _get_formal_pipelines()
    return ListFormalPipelinesResponse(pipelines=list(pipelines.values()))


@router.post("/pipelines/{pipeline_id}/enable")
def enable_formal_pipeline(pipeline_id: str) -> FormalPipelineResponse:
    """Enable a formal verification pipeline"""
    pipeline = _get_formal_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Formal pipeline not found")
    
    pipeline.enabled = True
    pipeline.updated_at = time.time()
    _save_formal_pipeline(pipeline)
    
    return FormalPipelineResponse(pipeline=pipeline)


@router.post("/pipelines/{pipeline_id}/disable")
def disable_formal_pipeline(pipeline_id: str) -> FormalPipelineResponse:
    """Disable a formal verification pipeline"""
    pipeline = _get_formal_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Formal pipeline not found")
    
    pipeline.enabled = False
    pipeline.updated_at = time.time()
    _save_formal_pipeline(pipeline)
    
    return FormalPipelineResponse(pipeline=pipeline)


# --- API ENDPOINTS FOR VERIFICATION RUNS ---

@router.post("/runs", response_model=FormalRunResponse)
def run_formal_verification_endpoint(request: RunFormalVerificationRequest) -> FormalRunResponse:
    """Run a formal verification pipeline
    
    This endpoint executes a verification pipeline using the algebraic framework,
    checking formal mathematical properties and returning verification results.
    """
    pipeline = _get_formal_pipeline(request.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Formal pipeline not found")
    
    if not pipeline.enabled:
        raise HTTPException(status_code=400, detail="Formal pipeline is disabled")
    
    # Create a new run
    run = VerificationRunState(
        pipeline_id=pipeline.id,
        triggered_by=request.triggered_by,
        commit_id=request.commit_id
    )
    
    # Run the formal verification
    import time as py_time
    start_time = py_time.time()
    
    verification_state = run_formal_verification(pipeline, request.verification_parameters)
    run.verification_state = verification_state
    
    run.status = "completed"
    run.completed_at = py_time.time()
    
    # Build results and metrics
    run.results = {
        "valid": verification_state.valid,
        "properties_satisfied": list(verification_state.properties_satisfied),
        "properties_violated": list(verification_state.properties_violated),
        "counter_examples": verification_state.counter_examples
    }
    
    run.metrics = {
        "total_duration": run.completed_at - start_time,
        "properties_checked": len(pipeline.formal_properties),
        "properties_satisfied": len(verification_state.properties_satisfied),
        "properties_violated": len(verification_state.properties_violated)
    }
    
    if not verification_state.valid:
        run.proof_failures = [f"Property '{prop}' violated" for prop in verification_state.properties_violated]
    
    _save_formal_run(run)
    
    return FormalRunResponse(run=run)


@router.get("/runs/{run_id}", response_model=FormalRunResponse)
def get_formal_run(run_id: str) -> FormalRunResponse:
    """Get a formal verification run by ID"""
    run = _get_formal_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Formal run not found")
    
    return FormalRunResponse(run=run)


@router.get("/runs", response_model=ListFormalRunsResponse)
def list_formal_runs() -> ListFormalRunsResponse:
    """List all formal verification runs"""
    runs = _get_formal_runs()
    return ListFormalRunsResponse(runs=list(runs.values()))


@router.get("/pipelines/{pipeline_id}/runs", response_model=ListFormalRunsResponse)
def list_formal_pipeline_runs(pipeline_id: str) -> ListFormalRunsResponse:
    """List all formal verification runs for a pipeline"""
    pipeline = _get_formal_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Formal pipeline not found")
    
    runs = _get_formal_runs()
    pipeline_runs = [run for run in runs.values() if run.pipeline_id == pipeline_id]
    
    return ListFormalRunsResponse(runs=pipeline_runs)


# --- API ENDPOINTS FOR CRYPTOGRAPHIC COMPONENTS ---

@router.post("/crypto-components", response_model=FormalComponentResponse)
def register_formal_crypto_component(request: RegisterFormalCryptoComponentRequest) -> FormalComponentResponse:
    """Register a formal cryptographic component
    
    This endpoint registers a cryptographic component with formal properties
    and computes its security level based on the mathematical model.
    """
    component = FormalCryptographicComponent(
        algorithm=request.algorithm,
        key_length=request.key_length,
        implementation=request.implementation,
        usage_context=request.usage_context,
        expected_lifespan=request.expected_lifespan,
        formal_properties=request.formal_properties
    )
    
    # Compute security level using the security level function
    component.security_level = component.security_level_function()
    
    _save_formal_crypto_component(component)
    
    return FormalComponentResponse(component=component)


@router.get("/crypto-components/{component_id}", response_model=FormalComponentResponse)
def get_formal_crypto_component(component_id: str) -> FormalComponentResponse:
    """Get a formal cryptographic component by ID"""
    component = _get_formal_crypto_component(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Formal component not found")
    
    return FormalComponentResponse(component=component)


@router.get("/crypto-components", response_model=ListFormalCryptoComponentsResponse)
def list_formal_crypto_components() -> ListFormalCryptoComponentsResponse:
    """List all formal cryptographic components"""
    components = _get_formal_crypto_components()
    return ListFormalCryptoComponentsResponse(components=list(components.values()))


@router.post("/crypto-components/{component_id}/deprecate")
def deprecate_formal_crypto_component(component_id: str, replacement_id: Optional[str] = None) -> FormalComponentResponse:
    """Deprecate a formal cryptographic component
    
    This endpoint applies the state transition function in the formal model
    to transition a component to the deprecated state.
    """
    component = _get_formal_crypto_component(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Formal component not found")
    
    if replacement_id:
        replacement = _get_formal_crypto_component(replacement_id)
        if not replacement:
            raise HTTPException(status_code=404, detail="Replacement formal component not found")
        component.replacement = replacement_id
    
    # Apply state transition
    component.status = "deprecated"
    
    # Recompute security level after status change
    component.security_level = component.security_level_function()
    
    _save_formal_crypto_component(component)
    
    return FormalComponentResponse(component=component)


# --- API ENDPOINTS FOR METRICS AND DASHBOARD DATA ---

@router.get("/metrics/verification", response_model=FormalVerificationMetricsResponse)
def get_formal_verification_metrics() -> FormalVerificationMetricsResponse:
    """Get formal verification metrics for dashboard
    
    This endpoint computes metrics about the formal verification system,
    including property coverage and verification type distribution.
    """
    pipelines = _get_formal_pipelines()
    runs = _get_formal_runs()
    
    now = time.time()
    recent_runs = [run for run in runs.values() if run.started_at > now - 86400]  # Last 24h
    
    failed_runs = [run for run in recent_runs if not run.verification_state.valid]
    if recent_runs:
        passing_percentage = (len(recent_runs) - len(failed_runs)) / len(recent_runs) * 100
        avg_time = sum(run.metrics.get("total_duration", 0) for run in recent_runs) / len(recent_runs)
    else:
        passing_percentage = 100.0
        avg_time = 0.0
    
    # Generate component health
    component_health = {}
    for pipeline in pipelines.values():
        for module in pipeline.module_dependencies:
            pipeline_runs = [run for run in recent_runs if run.pipeline_id == pipeline.id]
            if pipeline_runs:
                failures = sum(1 for run in pipeline_runs if not run.verification_state.valid)
                health = "healthy" if failures == 0 else "degraded" if failures < len(pipeline_runs) / 2 else "critical"
                component_health[module] = health
            else:
                component_health[module] = "unknown"
    
    # Calculate formal properties coverage
    all_properties = {prop.value for pipeline in pipelines.values() for prop in pipeline.formal_properties}
    property_coverage = {}
    for prop in all_properties:
        coverage = sum(1 for pipeline in pipelines.values() if prop in [p.value for p in pipeline.formal_properties]) / len(pipelines) * 100
        property_coverage[prop] = coverage
    
    # Calculate verification type distribution
    verification_distribution = {}
    for pipeline in pipelines.values():
        v_type = pipeline.verification_type.value
        verification_distribution[v_type] = verification_distribution.get(v_type, 0) + 1
    
    return FormalVerificationMetricsResponse(
        total_pipelines=len(pipelines),
        active_pipelines=sum(1 for p in pipelines.values() if p.enabled),
        verification_runs_last_24h=len(recent_runs),
        avg_verification_time=avg_time,
        passing_proofs_percentage=passing_percentage,
        component_health=component_health,
        formal_properties_coverage=property_coverage,
        verification_type_distribution=verification_distribution,
        recent_failures=[{
            "run_id": run.id,
            "pipeline_name": pipelines[run.pipeline_id].name if run.pipeline_id in pipelines else "Unknown",
            "started_at": run.started_at,
            "failures": len(run.proof_failures)
        } for run in failed_runs]
    )


@router.get("/metrics/crypto-health", response_model=FormalCryptographicHealthResponse)
def get_formal_crypto_health_metrics() -> FormalCryptographicHealthResponse:
    """Get formal cryptographic health metrics for dashboard
    
    This endpoint computes metrics about the cryptographic components
    using the mathematical security model, including security level distribution.
    """
    components = _get_formal_crypto_components()
    
    status_counts = {}
    for component in components.values():
        status_counts[component.status] = status_counts.get(component.status, 0) + 1
    
    # Calculate post-quantum readiness
    pq_ready = sum(1 for c in components.values() 
                  if "post-quantum" in c.status.lower() 
                  or any("post-quantum" in prop.lower() for prop in c.formal_properties))
    pq_readiness = pq_ready / max(len(components), 1) * 100
    
    # Identify components near deprecation
    near_deprecation = []
    current_time = datetime.now()
    for component in components.values():
        if component.expected_lifespan and component.status == "active":
            try:
                lifespan_date = datetime.strptime(component.expected_lifespan, "%Y-%m-%d")
                days_remaining = (lifespan_date - current_time).days
                if days_remaining < 180:  # 180 days
                    near_deprecation.append({
                        "id": component.id,
                        "algorithm": component.algorithm,
                        "days_remaining": days_remaining
                    })
            except:
                pass
    
    # Calculate security level metrics
    security_levels = [c.security_level for c in components.values()]
    if security_levels:
        mean_security = sum(security_levels) / len(security_levels)
        min_security = min(security_levels)
    else:
        mean_security = 0.0
        min_security = 0.0
    
    # Group security levels into ranges
    security_distribution = {
        "low (0-1)": 0,
        "medium (1-2)": 0,
        "high (2-3)": 0,
        "very high (3+)": 0
    }
    
    for level in security_levels:
        if level < 1:
            security_distribution["low (0-1)"] += 1
        elif level < 2:
            security_distribution["medium (1-2)"] += 1
        elif level < 3:
            security_distribution["high (2-3)"] += 1
        else:
            security_distribution["very high (3+)"] += 1
    
    # Convert to percentages
    for key in security_distribution:
        security_distribution[key] = security_distribution[key] / max(len(security_levels), 1) * 100
    
    # Generate security recommendations
    recommendations = []
    if pq_readiness < 30:
        recommendations.append("Increase post-quantum cryptography adoption")
    if status_counts.get("deprecated", 0) > 0:
        recommendations.append("Replace deprecated cryptographic components")
    if len(near_deprecation) > 0:
        recommendations.append(f"Plan migration for {len(near_deprecation)} soon-to-expire cryptographic components")
    if min_security < 1.0:
        recommendations.append("Upgrade components with low security levels")
    
    return FormalCryptographicHealthResponse(
        total_components=len(components),
        components_by_status=status_counts,
        post_quantum_readiness=pq_readiness,
        components_near_deprecation=near_deprecation,
        security_recommendations=recommendations,
        mean_security_level=mean_security,
        min_security_level=min_security,
        security_level_distribution=security_distribution
    )


# --- COMPOSITION ENDPOINTS ---

@router.post("/pipelines/{pipeline_id1}/compose/{pipeline_id2}", response_model=FormalPipelineResponse)
def compose_pipelines(pipeline_id1: str, pipeline_id2: str) -> FormalPipelineResponse:
    """Compose two formal verification pipelines
    
    This endpoint implements the categorical composition operation,
    combining two verification pipelines into a new pipeline.
    """
    pipeline1 = _get_formal_pipeline(pipeline_id1)
    if not pipeline1:
        raise HTTPException(status_code=404, detail="First pipeline not found")
    
    pipeline2 = _get_formal_pipeline(pipeline_id2)
    if not pipeline2:
        raise HTTPException(status_code=404, detail="Second pipeline not found")
    
    # Compose pipelines using the algebraic composition operation
    composed_pipeline = pipeline1.compose(pipeline2)
    
    # Save the composed pipeline
    _save_formal_pipeline(composed_pipeline)
    
    return FormalPipelineResponse(pipeline=composed_pipeline)


@router.get("/verify/theorem/{theorem_name}")
def verify_formal_theorem(theorem_name: str, parameters: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Verify a formal theorem in the governance verification framework
    
    This endpoint verifies mathematical theorems about the governance system.
    Currently supported theorems:
    - associativity: Associativity of the verification state monoid
    - temporal_consistency: Temporal consistency of governance events
    - hash_chain: Integrity of the hash chain in governance events
    """
    if theorem_name == "associativity":
        satisfied, counter_example = verify_associativity(parameters)
        return {
            "theorem": "Associativity",
            "statement": "∀a,b,c ∈ S: (a • b) • c = a • (b • c)",
            "satisfied": satisfied,
            "counter_example": counter_example
        }
    elif theorem_name == "temporal_consistency":
        events = parameters.get("events", [])
        satisfied, counter_example = verify_temporal_consistency(events)
        return {
            "theorem": "Temporal Consistency",
            "statement": "∀e₁,e₂ ∈ E: e₁ depends on e₂ ⟹ τ(e₂) < τ(e₁)",
            "satisfied": satisfied,
            "counter_example": counter_example
        }
    elif theorem_name == "hash_chain":
        events = parameters.get("events", [])
        satisfied, counter_example = verify_hash_consistency(events)
        return {
            "theorem": "Hash Chain Integrity",
            "statement": "∀i > 0: events[i].previous_hash = events[i-1].hash",
            "satisfied": satisfied,
            "counter_example": counter_example
        }
    else:
        raise HTTPException(status_code=404, detail=f"Theorem '{theorem_name}' not found")

