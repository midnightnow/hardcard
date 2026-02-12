from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
import time
import databutton as db
import json

router = APIRouter(prefix="/crypto-agility")

class CryptoAlgorithm(BaseModel):
    """A cryptographic algorithm"""
    id: str
    name: str
    type: str  # hash, signature, encryption, key-exchange
    security_level: str  # bits of security
    post_quantum_resistant: bool = False
    status: str = "active"  # active, deprecated, planned
    replacement_for: Optional[str] = None  # id of algorithm this replaces
    formal_verification: Optional[str] = None  # reference to formal proof

class CryptoImplementation(BaseModel):
    """An implementation of a cryptographic algorithm"""
    id: str = Field(default_factory=lambda: f"impl_{int(time.time())}")
    algorithm_id: str
    name: str
    version: str
    source: str  # library-openssl, hardware-tpm, etc.
    performance_rating: float = 0.0  # 0-10
    verified: bool = False
    status: str = "active"  # active, deprecated, planned

class CryptoInstance(BaseModel):
    """An instance of a cryptographic implementation used in the system"""
    id: str = Field(default_factory=lambda: f"inst_{int(time.time())}")
    implementation_id: str
    name: str
    context: str  # where it's used
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    key_rotation_policy: Optional[str] = None
    last_rotation: Optional[float] = None
    parameters: Dict[str, Any] = {}

class CryptoRotationPlan(BaseModel):
    """A plan for rotating cryptographic algorithms/implementations"""
    id: str = Field(default_factory=lambda: f"plan_{int(time.time())}")
    name: str
    description: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    from_algorithm_id: str
    to_algorithm_id: str
    affected_instances: List[str] = []
    phases: List[Dict[str, Any]] = []
    status: str = "draft"  # draft, approved, in-progress, completed
    progress: float = 0.0  # 0-100

class CreateAlgorithmRequest(BaseModel):
    """Request to create a new cryptographic algorithm"""
    id: str
    name: str
    type: str
    security_level: str
    post_quantum_resistant: bool = False
    formal_verification: Optional[str] = None

class UpdateAlgorithmRequest(BaseModel):
    """Request to update a cryptographic algorithm"""
    name: Optional[str] = None
    security_level: Optional[str] = None
    post_quantum_resistant: Optional[bool] = None
    status: Optional[str] = None
    formal_verification: Optional[str] = None

class CreateImplementationRequest(BaseModel):
    """Request to create a new cryptographic implementation"""
    algorithm_id: str
    name: str
    version: str
    source: str
    performance_rating: float = 0.0
    verified: bool = False

class CreateInstanceRequest(BaseModel):
    """Request to create a new cryptographic instance"""
    implementation_id: str
    name: str
    context: str
    key_rotation_policy: Optional[str] = None
    parameters: Dict[str, Any] = {}

class CreateRotationPlanRequest(BaseModel):
    """Request to create a new rotation plan"""
    name: str
    description: str
    from_algorithm_id: str
    to_algorithm_id: str
    affected_instances: List[str] = []
    phases: List[Dict[str, Any]] = []

class UpdateRotationPlanRequest(BaseModel):
    """Request to update a rotation plan"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    phases: Optional[List[Dict[str, Any]]] = None

class AlgorithmResponse(BaseModel):
    """Response containing algorithm details"""
    algorithm: CryptoAlgorithm

class ImplementationResponse(BaseModel):
    """Response containing implementation details"""
    implementation: CryptoImplementation

class InstanceResponse(BaseModel):
    """Response containing instance details"""
    instance: CryptoInstance

class RotationPlanResponse(BaseModel):
    """Response containing rotation plan details"""
    plan: CryptoRotationPlan

class ListAlgorithmsResponse(BaseModel):
    """Response containing a list of algorithms"""
    algorithms: List[CryptoAlgorithm]

class ListImplementationsResponse(BaseModel):
    """Response containing a list of implementations"""
    implementations: List[CryptoImplementation]

class ListInstancesResponse(BaseModel):
    """Response containing a list of instances"""
    instances: List[CryptoInstance]

class ListRotationPlansResponse(BaseModel):
    """Response containing a list of rotation plans"""
    plans: List[CryptoRotationPlan]

class CryptoAgilitySummaryResponse(BaseModel):
    """Response containing a summary of cryptographic agility"""
    total_algorithms: int
    algorithms_by_type: Dict[str, int]
    post_quantum_percentage: float
    deprecated_algorithms: int
    total_implementations: int
    verified_implementations_percentage: float
    active_rotation_plans: int
    risk_assessments: List[Dict[str, Any]]

# Storage helpers
def _sanitize_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def _get_algorithms() -> Dict[str, CryptoAlgorithm]:
    """Get all cryptographic algorithms"""
    try:
        algs_json = db.storage.json.get("cryptographic_agility_algorithms", default={})
        return {k: CryptoAlgorithm(**v) for k, v in algs_json.items()}
    except Exception as e:
        print(f"Error getting algorithms: {e}")
        return {}

def _save_algorithms(algorithms: Dict[str, CryptoAlgorithm]) -> None:
    """Save all cryptographic algorithms"""
    algs_json = {k: v.dict() for k, v in algorithms.items()}
    db.storage.json.put(_sanitize_key("cryptographic_agility_algorithms"), algs_json)

def _get_algorithm(algorithm_id: str) -> Optional[CryptoAlgorithm]:
    """Get a cryptographic algorithm by ID"""
    algorithms = _get_algorithms()
    return algorithms.get(algorithm_id)

def _save_algorithm(algorithm: CryptoAlgorithm) -> None:
    """Save a cryptographic algorithm"""
    algorithms = _get_algorithms()
    algorithms[algorithm.id] = algorithm
    _save_algorithms(algorithms)

def _get_implementations() -> Dict[str, CryptoImplementation]:
    """Get all cryptographic implementations"""
    try:
        impls_json = db.storage.json.get("cryptographic_agility_implementations", default={})
        return {k: CryptoImplementation(**v) for k, v in impls_json.items()}
    except Exception as e:
        print(f"Error getting implementations: {e}")
        return {}

def _save_implementations(implementations: Dict[str, CryptoImplementation]) -> None:
    """Save all cryptographic implementations"""
    impls_json = {k: v.dict() for k, v in implementations.items()}
    db.storage.json.put(_sanitize_key("cryptographic_agility_implementations"), impls_json)

def _get_implementation(implementation_id: str) -> Optional[CryptoImplementation]:
    """Get a cryptographic implementation by ID"""
    implementations = _get_implementations()
    return implementations.get(implementation_id)

def _save_implementation(implementation: CryptoImplementation) -> None:
    """Save a cryptographic implementation"""
    implementations = _get_implementations()
    implementations[implementation.id] = implementation
    _save_implementations(implementations)

def _get_instances() -> Dict[str, CryptoInstance]:
    """Get all cryptographic instances"""
    try:
        instances_json = db.storage.json.get("cryptographic_agility_instances", default={})
        return {k: CryptoInstance(**v) for k, v in instances_json.items()}
    except Exception as e:
        print(f"Error getting instances: {e}")
        return {}

def _save_instances(instances: Dict[str, CryptoInstance]) -> None:
    """Save all cryptographic instances"""
    instances_json = {k: v.dict() for k, v in instances.items()}
    db.storage.json.put(_sanitize_key("cryptographic_agility_instances"), instances_json)

def _get_instance(instance_id: str) -> Optional[CryptoInstance]:
    """Get a cryptographic instance by ID"""
    instances = _get_instances()
    return instances.get(instance_id)

def _save_instance(instance: CryptoInstance) -> None:
    """Save a cryptographic instance"""
    instances = _get_instances()
    instances[instance.id] = instance
    _save_instances(instances)

def _get_rotation_plans() -> Dict[str, CryptoRotationPlan]:
    """Get all rotation plans"""
    try:
        plans_json = db.storage.json.get("cryptographic_agility_rotation_plans", default={})
        return {k: CryptoRotationPlan(**v) for k, v in plans_json.items()}
    except Exception as e:
        print(f"Error getting rotation plans: {e}")
        return {}

def _save_rotation_plans(plans: Dict[str, CryptoRotationPlan]) -> None:
    """Save all rotation plans"""
    plans_json = {k: v.dict() for k, v in plans.items()}
    db.storage.json.put(_sanitize_key("cryptographic_agility_rotation_plans"), plans_json)

def _get_rotation_plan(plan_id: str) -> Optional[CryptoRotationPlan]:
    """Get a rotation plan by ID"""
    plans = _get_rotation_plans()
    return plans.get(plan_id)

def _save_rotation_plan(plan: CryptoRotationPlan) -> None:
    """Save a rotation plan"""
    plans = _get_rotation_plans()
    plans[plan.id] = plan
    _save_rotation_plans(plans)

# API endpoints for algorithms
@router.post("/algorithms", response_model=AlgorithmResponse)
def create_algorithm(request: CreateAlgorithmRequest) -> AlgorithmResponse:
    """Create a new cryptographic algorithm"""
    if _get_algorithm(request.id):
        raise HTTPException(status_code=400, detail="Algorithm ID already exists")
    
    algorithm = CryptoAlgorithm(
        id=request.id,
        name=request.name,
        type=request.type,
        security_level=request.security_level,
        post_quantum_resistant=request.post_quantum_resistant,
        formal_verification=request.formal_verification
    )
    
    _save_algorithm(algorithm)
    
    return AlgorithmResponse(algorithm=algorithm)

@router.get("/algorithms/{algorithm_id}", response_model=AlgorithmResponse)
def get_algorithm_endpoint(algorithm_id: str) -> AlgorithmResponse:
    """Get a cryptographic algorithm by ID"""
    algorithm = _get_algorithm(algorithm_id)
    if not algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    return AlgorithmResponse(algorithm=algorithm)

@router.put("/algorithms/{algorithm_id}", response_model=AlgorithmResponse)
def update_algorithm(algorithm_id: str, request: UpdateAlgorithmRequest) -> AlgorithmResponse:
    """Update a cryptographic algorithm"""
    algorithm = _get_algorithm(algorithm_id)
    if not algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    if request.name is not None:
        algorithm.name = request.name
    if request.security_level is not None:
        algorithm.security_level = request.security_level
    if request.post_quantum_resistant is not None:
        algorithm.post_quantum_resistant = request.post_quantum_resistant
    if request.status is not None:
        algorithm.status = request.status
    if request.formal_verification is not None:
        algorithm.formal_verification = request.formal_verification
    
    _save_algorithm(algorithm)
    
    return AlgorithmResponse(algorithm=algorithm)

@router.post("/algorithms/{algorithm_id}/deprecate")
def deprecate_algorithm2(algorithm_id: str, replacement_id: Optional[str] = None) -> AlgorithmResponse:
    """Deprecate a cryptographic algorithm"""
    algorithm = _get_algorithm(algorithm_id)
    if not algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    if replacement_id:
        replacement = _get_algorithm(replacement_id)
        if not replacement:
            raise HTTPException(status_code=404, detail="Replacement algorithm not found")
    
    algorithm.status = "deprecated"
    if replacement_id:
        algorithm.replacement_for = replacement_id
    
    _save_algorithm(algorithm)
    
    return AlgorithmResponse(algorithm=algorithm)

@router.get("/algorithms", response_model=ListAlgorithmsResponse)
def list_algorithms() -> ListAlgorithmsResponse:
    """List all cryptographic algorithms"""
    algorithms = _get_algorithms()
    return ListAlgorithmsResponse(algorithms=list(algorithms.values()))

# API endpoints for implementations
@router.post("/implementations", response_model=ImplementationResponse)
def create_implementation(request: CreateImplementationRequest) -> ImplementationResponse:
    """Create a new cryptographic implementation"""
    algorithm = _get_algorithm(request.algorithm_id)
    if not algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    implementation = CryptoImplementation(
        algorithm_id=request.algorithm_id,
        name=request.name,
        version=request.version,
        source=request.source,
        performance_rating=request.performance_rating,
        verified=request.verified
    )
    
    _save_implementation(implementation)
    
    return ImplementationResponse(implementation=implementation)

@router.get("/implementations/{implementation_id}", response_model=ImplementationResponse)
def get_implementation(implementation_id: str) -> ImplementationResponse:
    """Get a cryptographic implementation by ID"""
    implementation = _get_implementation(implementation_id)
    if not implementation:
        raise HTTPException(status_code=404, detail="Implementation not found")
    
    return ImplementationResponse(implementation=implementation)

@router.get("/implementations", response_model=ListImplementationsResponse)
def list_implementations() -> ListImplementationsResponse:
    """List all cryptographic implementations"""
    implementations = _get_implementations()
    return ListImplementationsResponse(implementations=list(implementations.values()))

@router.get("/algorithms/{algorithm_id}/implementations", response_model=ListImplementationsResponse)
def list_algorithm_implementations(algorithm_id: str) -> ListImplementationsResponse:
    """List all implementations of an algorithm"""
    algorithm = _get_algorithm(algorithm_id)
    if not algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    implementations = _get_implementations()
    algorithm_impls = [impl for impl in implementations.values() if impl.algorithm_id == algorithm_id]
    
    return ListImplementationsResponse(implementations=algorithm_impls)

# API endpoints for instances
@router.post("/instances", response_model=InstanceResponse)
def create_instance(request: CreateInstanceRequest) -> InstanceResponse:
    """Create a new cryptographic instance"""
    implementation = _get_implementation(request.implementation_id)
    if not implementation:
        raise HTTPException(status_code=404, detail="Implementation not found")
    
    instance = CryptoInstance(
        implementation_id=request.implementation_id,
        name=request.name,
        context=request.context,
        key_rotation_policy=request.key_rotation_policy,
        parameters=request.parameters
    )
    
    _save_instance(instance)
    
    return InstanceResponse(instance=instance)

@router.get("/instances/{instance_id}", response_model=InstanceResponse)
def get_instance_endpoint(instance_id: str) -> InstanceResponse:
    """Get a cryptographic instance by ID"""
    instance = _get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return InstanceResponse(instance=instance)

@router.post("/instances/{instance_id}/rotate-key")
def rotate_instance_key(instance_id: str) -> InstanceResponse:
    """Rotate the key for a cryptographic instance"""
    instance = _get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # In a real implementation, this would actually perform a key rotation
    # For now, we'll just update the last_rotation timestamp
    instance.last_rotation = time.time()
    instance.updated_at = time.time()
    
    _save_instance(instance)
    
    return InstanceResponse(instance=instance)

@router.get("/instances", response_model=ListInstancesResponse)
def list_instances() -> ListInstancesResponse:
    """List all cryptographic instances"""
    instances = _get_instances()
    return ListInstancesResponse(instances=list(instances.values()))

# API endpoints for rotation plans
@router.post("/rotation-plans", response_model=RotationPlanResponse)
def create_rotation_plan(request: CreateRotationPlanRequest) -> RotationPlanResponse:
    """Create a new rotation plan"""
    from_algorithm = _get_algorithm(request.from_algorithm_id)
    if not from_algorithm:
        raise HTTPException(status_code=404, detail="Source algorithm not found")
    
    to_algorithm = _get_algorithm(request.to_algorithm_id)
    if not to_algorithm:
        raise HTTPException(status_code=404, detail="Target algorithm not found")
    
    # Validate affected instances
    instances = _get_instances()
    implementations = _get_implementations()
    
    for instance_id in request.affected_instances:
        if instance_id not in instances:
            raise HTTPException(status_code=404, detail=f"Instance {instance_id} not found")
        
        instance = instances[instance_id]
        implementation = implementations.get(instance.implementation_id)
        if not implementation or implementation.algorithm_id != request.from_algorithm_id:
            raise HTTPException(status_code=400, detail=f"Instance {instance_id} is not using the source algorithm")
    
    plan = CryptoRotationPlan(
        name=request.name,
        description=request.description,
        from_algorithm_id=request.from_algorithm_id,
        to_algorithm_id=request.to_algorithm_id,
        affected_instances=request.affected_instances,
        phases=request.phases
    )
    
    _save_rotation_plan(plan)
    
    return RotationPlanResponse(plan=plan)

@router.get("/rotation-plans/{plan_id}", response_model=RotationPlanResponse)
def get_rotation_plan_endpoint(plan_id: str) -> RotationPlanResponse:
    """Get a rotation plan by ID"""
    plan = _get_rotation_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Rotation plan not found")
    
    return RotationPlanResponse(plan=plan)

@router.put("/rotation-plans/{plan_id}", response_model=RotationPlanResponse)
def update_rotation_plan(plan_id: str, request: UpdateRotationPlanRequest) -> RotationPlanResponse:
    """Update a rotation plan"""
    plan = _get_rotation_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Rotation plan not found")
    
    if request.name is not None:
        plan.name = request.name
    if request.description is not None:
        plan.description = request.description
    if request.status is not None:
        plan.status = request.status
    if request.progress is not None:
        plan.progress = request.progress
    if request.phases is not None:
        plan.phases = request.phases
    
    plan.updated_at = time.time()
    _save_rotation_plan(plan)
    
    return RotationPlanResponse(plan=plan)

@router.post("/rotation-plans/{plan_id}/approve")
def approve_rotation_plan(plan_id: str) -> RotationPlanResponse:
    """Approve a rotation plan"""
    plan = _get_rotation_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Rotation plan not found")
    
    if plan.status != "draft":
        raise HTTPException(status_code=400, detail=f"Plan is in {plan.status} state, not draft")
    
    plan.status = "approved"
    plan.updated_at = time.time()
    
    _save_rotation_plan(plan)
    
    return RotationPlanResponse(plan=plan)

@router.post("/rotation-plans/{plan_id}/execute")
def execute_rotation_plan(plan_id: str) -> RotationPlanResponse:
    """Start executing a rotation plan"""
    plan = _get_rotation_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Rotation plan not found")
    
    if plan.status != "approved":
        raise HTTPException(status_code=400, detail=f"Plan is in {plan.status} state, not approved")
    
    plan.status = "in-progress"
    plan.updated_at = time.time()
    
    _save_rotation_plan(plan)
    
    return RotationPlanResponse(plan=plan)

@router.post("/rotation-plans/{plan_id}/complete")
def complete_rotation_plan(plan_id: str) -> RotationPlanResponse:
    """Mark a rotation plan as completed"""
    plan = _get_rotation_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Rotation plan not found")
    
    if plan.status != "in-progress":
        raise HTTPException(status_code=400, detail=f"Plan is in {plan.status} state, not in-progress")
    
    plan.status = "completed"
    plan.progress = 100.0
    plan.updated_at = time.time()
    
    _save_rotation_plan(plan)
    
    # In a real implementation, we would update all affected instances here
    # For now, we'll just simulate that by updating their implementation references
    instances = _get_instances()
    implementations = _get_implementations()
    
    # Find an implementation of the target algorithm
    target_impls = [impl for impl in implementations.values() if impl.algorithm_id == plan.to_algorithm_id]
    if target_impls:
        target_impl = target_impls[0]  # Just use the first one for this simulation
        
        for instance_id in plan.affected_instances:
            if instance_id in instances:
                instance = instances[instance_id]
                instance.implementation_id = target_impl.id
                instance.updated_at = time.time()
                _save_instance(instance)
    
    return RotationPlanResponse(plan=plan)

@router.get("/rotation-plans", response_model=ListRotationPlansResponse)
def list_rotation_plans() -> ListRotationPlansResponse:
    """List all rotation plans"""
    plans = _get_rotation_plans()
    return ListRotationPlansResponse(plans=list(plans.values()))

# API endpoint for summary data
@router.get("/summary", response_model=CryptoAgilitySummaryResponse)
def get_crypto_agility_summary() -> CryptoAgilitySummaryResponse:
    """Get a summary of cryptographic agility"""
    algorithms = _get_algorithms()
    implementations = _get_implementations()
    instances = _get_instances()
    plans = _get_rotation_plans()
    
    # Count algorithms by type
    algorithm_types = {}
    for alg in algorithms.values():
        algorithm_types[alg.type] = algorithm_types.get(alg.type, 0) + 1
    
    # Count post-quantum algorithms
    pq_algs = sum(1 for alg in algorithms.values() if alg.post_quantum_resistant)
    pq_percentage = pq_algs / max(len(algorithms), 1) * 100
    
    # Count deprecated algorithms
    deprecated = sum(1 for alg in algorithms.values() if alg.status == "deprecated")
    
    # Count verified implementations
    verified = sum(1 for impl in implementations.values() if impl.verified)
    verified_percentage = verified / max(len(implementations), 1) * 100
    
    # Count active rotation plans
    active_plans = sum(1 for plan in plans.values() if plan.status in ["approved", "in-progress"])
    
    # Prepare risk assessments
    risks = []
    
    # Risk 1: Deprecated algorithms still in use
    deprecated_algs_in_use = set()
    for instance in instances.values():
        impl = implementations.get(instance.implementation_id)
        if impl and impl.algorithm_id in algorithms:
            alg = algorithms[impl.algorithm_id]
            if alg.status == "deprecated":
                deprecated_algs_in_use.add(alg.id)
    
    if deprecated_algs_in_use:
        risks.append({
            "severity": "high",
            "description": f"Deprecated algorithms still in use: {', '.join(deprecated_algs_in_use)}",
            "mitigation": "Create and execute rotation plans for these algorithms."
        })
    
    # Risk 2: Low post-quantum readiness
    if pq_percentage < 30:
        risks.append({
            "severity": "medium",
            "description": f"Low post-quantum readiness ({pq_percentage:.1f}%)",
            "mitigation": "Increase adoption of post-quantum algorithms in critical areas."
        })
    
    # Risk 3: Low implementation verification
    if verified_percentage < 50:
        risks.append({
            "severity": "medium",
            "description": f"Many crypto implementations not formally verified ({verified_percentage:.1f}% verified)",
            "mitigation": "Increase formal verification coverage for cryptographic implementations."
        })
    
    # Risk 4: Missing key rotation
    missing_rotation = []
    for instance in instances.values():
        if instance.key_rotation_policy and not instance.last_rotation:
            missing_rotation.append(instance.id)
    
    if missing_rotation:
        risks.append({
            "severity": "medium",
            "description": f"{len(missing_rotation)} instances have never had key rotation",
            "mitigation": "Perform initial key rotation for affected instances."
        })
    
    return CryptoAgilitySummaryResponse(
        total_algorithms=len(algorithms),
        algorithms_by_type=algorithm_types,
        post_quantum_percentage=pq_percentage,
        deprecated_algorithms=deprecated,
        total_implementations=len(implementations),
        verified_implementations_percentage=verified_percentage,
        active_rotation_plans=active_plans,
        risk_assessments=risks
    )
