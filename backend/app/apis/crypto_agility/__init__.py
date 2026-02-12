from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import databutton as db
import json
import re

router = APIRouter()

# Constants
CRYPTO_INVENTORY_KEY = "crypto_inventory"
ALGORITHM_KEY = "algorithms"
IMPLEMENTATION_KEY = "implementations"
INSTANCE_KEY = "instances"
ROTATION_PLAN_KEY = "rotation_plans"

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Enums
class AlgorithmType(str, Enum):
    SYMMETRIC_ENCRYPTION = "symmetric_encryption"
    ASYMMETRIC_ENCRYPTION = "asymmetric_encryption"
    DIGITAL_SIGNATURE = "digital_signature"
    HASH_FUNCTION = "hash_function"
    MESSAGE_AUTHENTICATION = "message_authentication"
    KEY_AGREEMENT = "key_agreement"
    RANDOM_NUMBER_GENERATION = "random_number_generation"
    POST_QUANTUM = "post_quantum"

class AlgorithmStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    UPCOMING = "upcoming"
    VULNERABLE = "vulnerable"

class ImplementationLanguage(str, Enum):
    C = "c"
    CPP = "cpp"
    PYTHON = "python"
    RUST = "rust"
    GO = "go"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    HARDWARE = "hardware"

class RotationPhase(str, Enum):
    PLANNING = "planning"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CANCELED = "canceled"

# Crypto Inventory Models
class Algorithm(BaseModel):
    id: str
    name: str
    type: AlgorithmType
    description: str
    status: AlgorithmStatus
    key_sizes: List[int]
    quantum_resistant: bool = False
    standard_references: List[str] = []
    nist_compliance: Optional[str] = None
    estimated_lifespan_years: int
    vulnerabilities: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Implementation(BaseModel):
    id: str
    algorithm_id: str
    name: str
    version: str
    language: ImplementationLanguage
    source_repository: Optional[str] = None
    library_name: Optional[str] = None
    certified: bool = False
    certification_details: Optional[str] = None
    performance_metrics: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Instance(BaseModel):
    id: str
    implementation_id: str
    name: str
    key_size: int
    parameters: Dict[str, Any] = {}
    component_path: str  # Where this is used in the system
    creation_date: datetime = Field(default_factory=datetime.now)
    key_generation_date: datetime = Field(default_factory=datetime.now)
    key_expiration_date: Optional[datetime] = None
    last_rotation_date: Optional[datetime] = None
    next_rotation_date: Optional[datetime] = None
    active: bool = True

class RotationPlan(BaseModel):
    id: str
    name: str
    description: str
    source_instance_id: str
    target_algorithm_id: str
    target_implementation_id: str
    target_key_size: int
    target_parameters: Dict[str, Any] = {}
    phase: RotationPhase = RotationPhase.PLANNING
    dual_operation_period_days: int = 30  # Period both old and new will operate simultaneously
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    planned_execution_date: Optional[datetime] = None
    approver_id: Optional[str] = None
    executor_id: Optional[str] = None

# Response Models
class AlgorithmListResponse(BaseModel):
    algorithms: List[Algorithm]

class AlgorithmResponse(BaseModel):
    algorithm: Algorithm

class ImplementationListResponse(BaseModel):
    implementations: List[Implementation]

class ImplementationResponse(BaseModel):
    implementation: Implementation

class InstanceListResponse(BaseModel):
    instances: List[Instance]

class InstanceResponse(BaseModel):
    instance: Instance

class RotationPlanListResponse(BaseModel):
    rotation_plans: List[RotationPlan]

class RotationPlanResponse(BaseModel):
    rotation_plan: RotationPlan

class CryptoAgilitySummary(BaseModel):
    total_algorithms: int
    total_implementations: int
    total_instances: int
    active_rotation_plans: int
    upcoming_rotations: int
    deprecated_algorithms_in_use: int
    quantum_resistance_percentage: float
    average_key_size: float
    vulnerable_instances: int

# Helper Functions
def get_algorithms() -> List[Algorithm]:
    """Get all algorithms from storage"""
    try:
        algorithms_json = db.storage.json.get(sanitize_storage_key(ALGORITHM_KEY), default=[])
        return [Algorithm(**alg) for alg in algorithms_json]
    except Exception:
        return []

def get_implementations() -> List[Implementation]:
    """Get all implementations from storage"""
    try:
        implementations_json = db.storage.json.get(sanitize_storage_key(IMPLEMENTATION_KEY), default=[])
        return [Implementation(**impl) for impl in implementations_json]
    except Exception:
        return []

def get_instances() -> List[Instance]:
    """Get all instances from storage"""
    try:
        instances_json = db.storage.json.get(sanitize_storage_key(INSTANCE_KEY), default=[])
        return [Instance(**inst) for inst in instances_json]
    except Exception:
        return []

def get_rotation_plans() -> List[RotationPlan]:
    """Get all rotation plans from storage"""
    try:
        plans_json = db.storage.json.get(sanitize_storage_key(ROTATION_PLAN_KEY), default=[])
        return [RotationPlan(**plan) for plan in plans_json]
    except Exception:
        return []

def save_algorithms(algorithms: List[Algorithm]) -> None:
    """Save algorithms to storage"""
    db.storage.json.put(sanitize_storage_key(ALGORITHM_KEY), [alg.dict() for alg in algorithms])

def save_implementations(implementations: List[Implementation]) -> None:
    """Save implementations to storage"""
    db.storage.json.put(sanitize_storage_key(IMPLEMENTATION_KEY), [impl.dict() for impl in implementations])

def save_instances(instances: List[Instance]) -> None:
    """Save instances to storage"""
    db.storage.json.put(sanitize_storage_key(INSTANCE_KEY), [inst.dict() for inst in instances])

def save_rotation_plans(plans: List[RotationPlan]) -> None:
    """Save rotation plans to storage"""
    db.storage.json.put(sanitize_storage_key(ROTATION_PLAN_KEY), [plan.dict() for plan in plans])

# API Endpoints
@router.get("/algorithms", response_model=AlgorithmListResponse)
def list_crypto_agility_algorithms() -> AlgorithmListResponse:
    """List all cryptographic algorithms in the inventory"""
    return AlgorithmListResponse(algorithms=get_algorithms())

@router.post("/algorithms", response_model=AlgorithmResponse)
def create_crypto_agility_algorithm(algorithm: Algorithm) -> AlgorithmResponse:
    """Add a new cryptographic algorithm to the inventory"""
    algorithms = get_algorithms()
    
    # Check for duplicate ID
    if any(alg.id == algorithm.id for alg in algorithms):
        raise HTTPException(status_code=400, detail=f"Algorithm with ID {algorithm.id} already exists")
    
    # Set timestamps
    now = datetime.now()
    algorithm.created_at = now
    algorithm.updated_at = now
    
    # Add the new algorithm
    algorithms.append(algorithm)
    save_algorithms(algorithms)
    
    return AlgorithmResponse(algorithm=algorithm)

@router.get("/algorithms/{algorithm_id}", response_model=AlgorithmResponse)
def get_crypto_agility_algorithm(algorithm_id: str) -> AlgorithmResponse:
    """Get a specific cryptographic algorithm by ID"""
    algorithms = get_algorithms()
    
    # Find the algorithm
    for algorithm in algorithms:
        if algorithm.id == algorithm_id:
            return AlgorithmResponse(algorithm=algorithm)
    
    raise HTTPException(status_code=404, detail=f"Algorithm with ID {algorithm_id} not found")

@router.put("/algorithms/{algorithm_id}", response_model=AlgorithmResponse)
def update_algorithm_agility(algorithm_id: str, updated_algorithm: Algorithm) -> AlgorithmResponse:
    """Update a cryptographic algorithm"""
    algorithms = get_algorithms()
    
    # Find and update the algorithm
    for i, algorithm in enumerate(algorithms):
        if algorithm.id == algorithm_id:
            # Preserve original creation date
            updated_algorithm.created_at = algorithm.created_at
            updated_algorithm.updated_at = datetime.now()
            
            # Update the algorithm
            algorithms[i] = updated_algorithm
            save_algorithms(algorithms)
            
            return AlgorithmResponse(algorithm=updated_algorithm)
    
    raise HTTPException(status_code=404, detail=f"Algorithm with ID {algorithm_id} not found")

@router.post("/algorithms/{algorithm_id}/deprecate", response_model=AlgorithmResponse)
def deprecate_algorithm(algorithm_id: str) -> AlgorithmResponse:
    """Mark an algorithm as deprecated"""
    algorithms = get_algorithms()
    
    # Find and deprecate the algorithm
    for i, algorithm in enumerate(algorithms):
        if algorithm.id == algorithm_id:
            algorithm.status = AlgorithmStatus.DEPRECATED
            algorithm.updated_at = datetime.now()
            
            # Update the algorithm
            algorithms[i] = algorithm
            save_algorithms(algorithms)
            
            return AlgorithmResponse(algorithm=algorithm)
    
    raise HTTPException(status_code=404, detail=f"Algorithm with ID {algorithm_id} not found")

@router.get("/implementations", response_model=ImplementationListResponse)
def list_crypto_agility_implementations() -> ImplementationListResponse:
    """List all cryptographic implementations in the inventory"""
    return ImplementationListResponse(implementations=get_implementations())

@router.post("/implementations", response_model=ImplementationResponse)
def create_crypto_agility_implementation(implementation: Implementation) -> ImplementationResponse:
    """Add a new cryptographic implementation to the inventory"""
    implementations = get_implementations()
    
    # Check for duplicate ID
    if any(impl.id == implementation.id for impl in implementations):
        raise HTTPException(status_code=400, detail=f"Implementation with ID {implementation.id} already exists")
    
    # Verify the algorithm exists
    algorithms = get_algorithms()
    if not any(alg.id == implementation.algorithm_id for alg in algorithms):
        raise HTTPException(status_code=400, detail=f"Algorithm with ID {implementation.algorithm_id} not found")
    
    # Set timestamps
    now = datetime.now()
    implementation.created_at = now
    implementation.updated_at = now
    
    # Add the new implementation
    implementations.append(implementation)
    save_implementations(implementations)
    
    return ImplementationResponse(implementation=implementation)

@router.get("/implementations/{implementation_id}", response_model=ImplementationResponse)
def get_crypto_agility_implementation(implementation_id: str) -> ImplementationResponse:
    """Get a specific cryptographic implementation by ID"""
    implementations = get_implementations()
    
    # Find the implementation
    for implementation in implementations:
        if implementation.id == implementation_id:
            return ImplementationResponse(implementation=implementation)
    
    raise HTTPException(status_code=404, detail=f"Implementation with ID {implementation_id} not found")

@router.get("/algorithms/{algorithm_id}/implementations", response_model=ImplementationListResponse)
def list_crypto_agility_algorithm_implementations(algorithm_id: str) -> ImplementationListResponse:
    """List all implementations for a specific algorithm"""
    # Verify the algorithm exists
    algorithms = get_algorithms()
    if not any(alg.id == algorithm_id for alg in algorithms):
        raise HTTPException(status_code=404, detail=f"Algorithm with ID {algorithm_id} not found")
    
    # Get matching implementations
    implementations = get_implementations()
    matching_implementations = [impl for impl in implementations if impl.algorithm_id == algorithm_id]
    
    return ImplementationListResponse(implementations=matching_implementations)

@router.get("/instances", response_model=InstanceListResponse)
def list_crypto_agility_instances() -> InstanceListResponse:
    """List all cryptographic instances in the inventory"""
    return InstanceListResponse(instances=get_instances())

@router.post("/instances", response_model=InstanceResponse)
def create_crypto_agility_instance(instance: Instance) -> InstanceResponse:
    """Add a new cryptographic instance to the inventory"""
    instances = get_instances()
    
    # Check for duplicate ID
    if any(inst.id == instance.id for inst in instances):
        raise HTTPException(status_code=400, detail=f"Instance with ID {instance.id} already exists")
    
    # Verify the implementation exists
    implementations = get_implementations()
    impl = next((impl for impl in implementations if impl.id == instance.implementation_id), None)
    if not impl:
        raise HTTPException(status_code=400, detail=f"Implementation with ID {instance.implementation_id} not found")
    
    # Get the algorithm to check key size
    algorithms = get_algorithms()
    alg = next((alg for alg in algorithms if alg.id == impl.algorithm_id), None)
    if alg and instance.key_size not in alg.key_sizes:
        raise HTTPException(status_code=400, detail=f"Key size {instance.key_size} is not supported for algorithm {alg.name}")
    
    # Set dates if not provided
    now = datetime.now()
    if not instance.key_expiration_date and alg:
        # Set expiration based on algorithm lifespan
        instance.key_expiration_date = now + timedelta(days=alg.estimated_lifespan_years * 365)
    
    if alg and alg.estimated_lifespan_years > 0:
        # Set next rotation at 80% of lifespan
        days_to_rotation = int(alg.estimated_lifespan_years * 365 * 0.8)
        instance.next_rotation_date = now + timedelta(days=days_to_rotation)
    
    # Add the new instance
    instances.append(instance)
    save_instances(instances)
    
    return InstanceResponse(instance=instance)

@router.get("/instances/{instance_id}", response_model=InstanceResponse)
def get_crypto_agility_instance(instance_id: str) -> InstanceResponse:
    """Get a specific cryptographic instance by ID"""
    instances = get_instances()
    
    # Find the instance
    for instance in instances:
        if instance.id == instance_id:
            return InstanceResponse(instance=instance)
    
    raise HTTPException(status_code=404, detail=f"Instance with ID {instance_id} not found")

@router.post("/instances/{instance_id}/rotate-key", response_model=InstanceResponse)
def rotate_crypto_agility_instance_key(instance_id: str) -> InstanceResponse:
    """Rotate the key for a specific instance"""
    instances = get_instances()
    
    # Find the instance
    for i, instance in enumerate(instances):
        if instance.id == instance_id:
            # Update key rotation dates
            now = datetime.now()
            instance.last_rotation_date = now
            instance.key_generation_date = now
            
            # Calculate new expiration date
            implementations = get_implementations()
            algorithms = get_algorithms()
            
            impl = next((impl for impl in implementations if impl.id == instance.implementation_id), None)
            if impl:
                alg = next((alg for alg in algorithms if alg.id == impl.algorithm_id), None)
                if alg and alg.estimated_lifespan_years > 0:
                    # Update expiration date
                    instance.key_expiration_date = now + timedelta(days=alg.estimated_lifespan_years * 365)
                    
                    # Set next rotation at 80% of lifespan
                    days_to_rotation = int(alg.estimated_lifespan_years * 365 * 0.8)
                    instance.next_rotation_date = now + timedelta(days=days_to_rotation)
            
            # Update the instance
            instances[i] = instance
            save_instances(instances)
            
            return InstanceResponse(instance=instance)
    
    raise HTTPException(status_code=404, detail=f"Instance with ID {instance_id} not found")

@router.get("/rotation-plans", response_model=RotationPlanListResponse)
def list_crypto_agility_rotation_plans() -> RotationPlanListResponse:
    """List all cryptographic key rotation plans"""
    return RotationPlanListResponse(rotation_plans=get_rotation_plans())

@router.post("/rotation-plans", response_model=RotationPlanResponse)
def create_crypto_agility_rotation_plan(plan: RotationPlan) -> RotationPlanResponse:
    """Create a new cryptographic key rotation plan"""
    plans = get_rotation_plans()
    
    # Check for duplicate ID
    if any(p.id == plan.id for p in plans):
        raise HTTPException(status_code=400, detail=f"Rotation plan with ID {plan.id} already exists")
    
    # Verify source instance exists
    instances = get_instances()
    if not any(inst.id == plan.source_instance_id for inst in instances):
        raise HTTPException(status_code=400, detail=f"Source instance with ID {plan.source_instance_id} not found")
    
    # Verify target algorithm exists
    algorithms = get_algorithms()
    if not any(alg.id == plan.target_algorithm_id for alg in algorithms):
        raise HTTPException(status_code=400, detail=f"Target algorithm with ID {plan.target_algorithm_id} not found")
    
    # Verify target implementation exists
    implementations = get_implementations()
    if not any(impl.id == plan.target_implementation_id for impl in implementations):
        raise HTTPException(status_code=400, detail=f"Target implementation with ID {plan.target_implementation_id} not found")
    
    # Set timestamps
    now = datetime.now()
    plan.created_at = now
    plan.updated_at = now
    
    # Set planned execution date if not provided
    if not plan.planned_execution_date:
        plan.planned_execution_date = now + timedelta(days=30)  # Default to 30 days in the future
    
    # Add the new plan
    plans.append(plan)
    save_rotation_plans(plans)
    
    return RotationPlanResponse(rotation_plan=plan)

@router.get("/rotation-plans/{plan_id}", response_model=RotationPlanResponse)
def get_crypto_agility_rotation_plan(plan_id: str) -> RotationPlanResponse:
    """Get a specific cryptographic key rotation plan by ID"""
    plans = get_rotation_plans()
    
    # Find the plan
    for plan in plans:
        if plan.id == plan_id:
            return RotationPlanResponse(rotation_plan=plan)
    
    raise HTTPException(status_code=404, detail=f"Rotation plan with ID {plan_id} not found")

@router.put("/rotation-plans/{plan_id}", response_model=RotationPlanResponse)
def update_crypto_agility_rotation_plan(plan_id: str, updated_plan: RotationPlan) -> RotationPlanResponse:
    """Update a cryptographic key rotation plan"""
    plans = get_rotation_plans()
    
    # Find and update the plan
    for i, plan in enumerate(plans):
        if plan.id == plan_id:
            # Verify the plan can be updated (not completed or canceled)
            if plan.phase in [RotationPhase.COMPLETED, RotationPhase.CANCELED]:
                raise HTTPException(status_code=400, detail=f"Cannot update rotation plan in {plan.phase} phase")
            
            # Preserve original creation date
            updated_plan.created_at = plan.created_at
            updated_plan.updated_at = datetime.now()
            
            # Preserve phase-specific dates
            updated_plan.approved_at = plan.approved_at
            updated_plan.executed_at = plan.executed_at
            updated_plan.completed_at = plan.completed_at
            
            # Update the plan
            plans[i] = updated_plan
            save_rotation_plans(plans)
            
            return RotationPlanResponse(rotation_plan=updated_plan)
    
    raise HTTPException(status_code=404, detail=f"Rotation plan with ID {plan_id} not found")

@router.post("/rotation-plans/{plan_id}/approve", response_model=RotationPlanResponse)
def approve_crypto_agility_rotation_plan(plan_id: str, approver_id: str) -> RotationPlanResponse:
    """Approve a cryptographic key rotation plan"""
    plans = get_rotation_plans()
    
    # Find and approve the plan
    for i, plan in enumerate(plans):
        if plan.id == plan_id:
            # Verify the plan is in planning phase
            if plan.phase != RotationPhase.PLANNING:
                raise HTTPException(status_code=400, detail=f"Cannot approve rotation plan in {plan.phase} phase")
            
            # Update phase and approver
            plan.phase = RotationPhase.APPROVED
            plan.approved_at = datetime.now()
            plan.approver_id = approver_id
            plan.updated_at = datetime.now()
            
            # Update the plan
            plans[i] = plan
            save_rotation_plans(plans)
            
            return RotationPlanResponse(rotation_plan=plan)
    
    raise HTTPException(status_code=404, detail=f"Rotation plan with ID {plan_id} not found")

@router.post("/rotation-plans/{plan_id}/execute", response_model=RotationPlanResponse)
def execute_crypto_agility_rotation_plan(plan_id: str, executor_id: str) -> RotationPlanResponse:
    """Execute a cryptographic key rotation plan"""
    plans = get_rotation_plans()
    instances = get_instances()
    
    # Find the plan
    for plan_index, plan in enumerate(plans):
        if plan.id == plan_id:
            # Verify the plan is in approved phase
            if plan.phase != RotationPhase.APPROVED:
                raise HTTPException(status_code=400, detail=f"Cannot execute rotation plan in {plan.phase} phase")
            
            # Find the source instance
            source_instance = None
            for i, instance in enumerate(instances):
                if instance.id == plan.source_instance_id:
                    source_instance = instance
                    break
            
            if not source_instance:
                raise HTTPException(status_code=404, detail=f"Source instance with ID {plan.source_instance_id} not found")
            
            # Create a new instance with target algorithm and implementation
            now = datetime.now()
            new_instance_id = f"{source_instance.id}-rotated-{now.strftime('%Y%m%d')}"
            
            # Get algorithm details for expiration calculation
            algorithms = get_algorithms()
            alg = next((alg for alg in algorithms if alg.id == plan.target_algorithm_id), None)
            
            # Create the new instance
            new_instance = Instance(
                id=new_instance_id,
                implementation_id=plan.target_implementation_id,
                name=f"{source_instance.name} (Rotated)",
                key_size=plan.target_key_size,
                parameters=plan.target_parameters,
                component_path=source_instance.component_path,
                creation_date=now,
                key_generation_date=now,
                active=True
            )
            
            # Set expiration and next rotation dates
            if alg and alg.estimated_lifespan_years > 0:
                new_instance.key_expiration_date = now + timedelta(days=alg.estimated_lifespan_years * 365)
                days_to_rotation = int(alg.estimated_lifespan_years * 365 * 0.8)
                new_instance.next_rotation_date = now + timedelta(days=days_to_rotation)
            
            # Mark source instance as inactive (after dual operation period)
            # source_instance.active = False  # Will be set in the complete phase
            
            # Update the rotation plan
            plan.phase = RotationPhase.EXECUTING
            plan.executed_at = now
            plan.executor_id = executor_id
            plan.updated_at = now
            
            # Save changes
            instances.append(new_instance)
            plans[plan_index] = plan
            save_instances(instances)
            save_rotation_plans(plans)
            
            return RotationPlanResponse(rotation_plan=plan)
    
    raise HTTPException(status_code=404, detail=f"Rotation plan with ID {plan_id} not found")

@router.post("/rotation-plans/{plan_id}/complete", response_model=RotationPlanResponse)
def complete_crypto_agility_rotation_plan(plan_id: str) -> RotationPlanResponse:
    """Complete a cryptographic key rotation plan"""
    plans = get_rotation_plans()
    instances = get_instances()
    
    # Find the plan
    for plan_index, plan in enumerate(plans):
        if plan.id == plan_id:
            # Verify the plan is in executing phase
            if plan.phase != RotationPhase.EXECUTING:
                raise HTTPException(status_code=400, detail=f"Cannot complete rotation plan in {plan.phase} phase")
            
            # Find the source instance
            source_instance = None
            source_instance_index = -1
            for i, instance in enumerate(instances):
                if instance.id == plan.source_instance_id:
                    source_instance = instance
                    source_instance_index = i
                    break
            
            if not source_instance:
                raise HTTPException(status_code=404, detail=f"Source instance with ID {plan.source_instance_id} not found")
            
            # Mark source instance as inactive
            source_instance.active = False
            instances[source_instance_index] = source_instance
            
            # Update the rotation plan
            now = datetime.now()
            plan.phase = RotationPhase.COMPLETED
            plan.completed_at = now
            plan.updated_at = now
            
            # Save changes
            plans[plan_index] = plan
            save_instances(instances)
            save_rotation_plans(plans)
            
            return RotationPlanResponse(rotation_plan=plan)
    
    raise HTTPException(status_code=404, detail=f"Rotation plan with ID {plan_id} not found")

@router.get("/summary", response_model=CryptoAgilitySummary)
def get_crypto_agility_summary2() -> CryptoAgilitySummary:
    """Get a summary of the cryptographic agility status"""
    algorithms = get_algorithms()
    implementations = get_implementations()
    instances = get_instances()
    plans = get_rotation_plans()
    
    # Count active rotation plans
    active_rotation_plans = len([p for p in plans if p.phase in [RotationPhase.PLANNING, RotationPhase.APPROVED, RotationPhase.EXECUTING]])
    
    # Count upcoming rotations
    now = datetime.now()
    upcoming_rotations = len([i for i in instances if i.active and i.next_rotation_date and i.next_rotation_date <= now + timedelta(days=90)])
    
    # Count deprecated algorithms in use
    deprecated_algorithms_in_use = 0
    for instance in instances:
        if not instance.active:
            continue
        
        implementation = next((impl for impl in implementations if impl.id == instance.implementation_id), None)
        if implementation:
            algorithm = next((alg for alg in algorithms if alg.id == implementation.algorithm_id), None)
            if algorithm and algorithm.status == AlgorithmStatus.DEPRECATED:
                deprecated_algorithms_in_use += 1
    
    # Calculate quantum resistance percentage
    quantum_resistant_instances = 0
    for instance in instances:
        if not instance.active:
            continue
        
        implementation = next((impl for impl in implementations if impl.id == instance.implementation_id), None)
        if implementation:
            algorithm = next((alg for alg in algorithms if alg.id == implementation.algorithm_id), None)
            if algorithm and algorithm.quantum_resistant:
                quantum_resistant_instances += 1
    
    quantum_resistance_percentage = 0.0
    active_instances_count = len([i for i in instances if i.active])
    if active_instances_count > 0:
        quantum_resistance_percentage = (quantum_resistant_instances / active_instances_count) * 100
    
    # Calculate average key size
    key_sizes = [i.key_size for i in instances if i.active]
    average_key_size = sum(key_sizes) / len(key_sizes) if key_sizes else 0
    
    # Count vulnerable instances
    vulnerable_instances = 0
    for instance in instances:
        if not instance.active:
            continue
        
        implementation = next((impl for impl in implementations if impl.id == instance.implementation_id), None)
        if implementation:
            algorithm = next((alg for alg in algorithms if alg.id == implementation.algorithm_id), None)
            if algorithm and algorithm.status == AlgorithmStatus.VULNERABLE:
                vulnerable_instances += 1
    
    return CryptoAgilitySummary(
        total_algorithms=len(algorithms),
        total_implementations=len(implementations),
        total_instances=len(instances),
        active_rotation_plans=active_rotation_plans,
        upcoming_rotations=upcoming_rotations,
        deprecated_algorithms_in_use=deprecated_algorithms_in_use,
        quantum_resistance_percentage=quantum_resistance_percentage,
        average_key_size=average_key_size,
        vulnerable_instances=vulnerable_instances
    )
