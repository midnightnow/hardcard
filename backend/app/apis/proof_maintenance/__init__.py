from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
import time
import databutton as db
import json

router = APIRouter(prefix="/proof-maintenance")

class ProofDependency(BaseModel):
    """Dependency relationship between proofs/modules"""
    id: str = Field(default_factory=lambda: f"dep_{int(time.time())}")
    source_module: str
    target_module: str
    dependency_type: str  # direct, transitive, abstract-implementation
    created_at: float = Field(default_factory=time.time)

class ProofModule(BaseModel):
    """A module containing proofs"""
    id: str
    name: str
    description: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    num_proofs: int = 0
    status: str = "stable"  # stable, needs-repair, refactoring
    verification_time: float = 0.0  # seconds
    health_score: float = 100.0  # 0-100
    tags: List[str] = []

class ProofMaintenanceMetric(BaseModel):
    """Metrics for proof maintenance"""
    id: str = Field(default_factory=lambda: f"metric_{int(time.time())}")
    module_id: str
    timestamp: float = Field(default_factory=time.time)
    verification_time: float
    num_proofs: int
    num_failed_proofs: int
    proof_complexity: float  # calculated metric
    dependency_depth: int
    changes_since_last_verification: int

class ProofAudit(BaseModel):
    """An audit of the proof system"""
    id: str = Field(default_factory=lambda: f"audit_{int(time.time())}")
    started_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    status: str = "running"  # running, completed, failed
    auditor: str
    findings: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    health_assessment: str = ""  # overall assessment

class CreateModuleRequest(BaseModel):
    """Request to create a proof module"""
    id: str
    name: str
    description: str
    tags: List[str] = []

class UpdateModuleRequest(BaseModel):
    """Request to update a proof module"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None

class AddDependencyRequest(BaseModel):
    """Request to add a dependency between modules"""
    source_module: str
    target_module: str
    dependency_type: str

class RecordMetricsRequest(BaseModel):
    """Request to record metrics for a module"""
    module_id: str
    verification_time: float
    num_proofs: int
    num_failed_proofs: int
    proof_complexity: float
    dependency_depth: int
    changes_since_last_verification: int

class StartAuditRequest(BaseModel):
    """Request to start a new proof audit"""
    auditor: str

class CompleteAuditRequest(BaseModel):
    """Request to complete a proof audit"""
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    health_assessment: str

class ModuleResponse(BaseModel):
    """Response containing module details"""
    module: ProofModule

class DependencyResponse(BaseModel):
    """Response containing dependency details"""
    dependency: ProofDependency

class MetricResponse(BaseModel):
    """Response containing metric details"""
    metric: ProofMaintenanceMetric

class AuditResponse(BaseModel):
    """Response containing audit details"""
    audit: ProofAudit

class ListModulesResponse(BaseModel):
    """Response containing a list of modules"""
    modules: List[ProofModule]

class ListDependenciesResponse(BaseModel):
    """Response containing a list of dependencies"""
    dependencies: List[ProofDependency]

class ListMetricsResponse(BaseModel):
    """Response containing a list of metrics"""
    metrics: List[ProofMaintenanceMetric]

class ListAuditsResponse(BaseModel):
    """Response containing a list of audits"""
    audits: List[ProofAudit]

class MaintenanceDashboardResponse(BaseModel):
    """Response containing proof maintenance dashboard data"""
    total_modules: int
    modules_by_status: Dict[str, int]
    avg_verification_time: float
    avg_health_score: float
    proof_debt_modules: List[Dict[str, Any]]
    high_impact_modules: List[Dict[str, Any]]
    time_series_data: Dict[str, List[float]]

# Storage helpers
def _sanitize_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def _get_modules() -> Dict[str, ProofModule]:
    """Get all proof modules"""
    try:
        modules_json = db.storage.json.get("proof_maintenance_modules", default={})
        return {k: ProofModule(**v) for k, v in modules_json.items()}
    except Exception as e:
        print(f"Error getting modules: {e}")
        return {}

def _save_modules(modules: Dict[str, ProofModule]) -> None:
    """Save all proof modules"""
    modules_json = {k: v.dict() for k, v in modules.items()}
    db.storage.json.put(_sanitize_key("proof_maintenance_modules"), modules_json)

def _get_module(module_id: str) -> Optional[ProofModule]:
    """Get a proof module by ID"""
    modules = _get_modules()
    return modules.get(module_id)

def _save_module(module: ProofModule) -> None:
    """Save a proof module"""
    modules = _get_modules()
    modules[module.id] = module
    _save_modules(modules)

def _get_dependencies() -> Dict[str, ProofDependency]:
    """Get all proof dependencies"""
    try:
        deps_json = db.storage.json.get("proof_maintenance_dependencies", default={})
        return {k: ProofDependency(**v) for k, v in deps_json.items()}
    except Exception as e:
        print(f"Error getting dependencies: {e}")
        return {}

def _save_dependencies(dependencies: Dict[str, ProofDependency]) -> None:
    """Save all proof dependencies"""
    deps_json = {k: v.dict() for k, v in dependencies.items()}
    db.storage.json.put(_sanitize_key("proof_maintenance_dependencies"), deps_json)

def _save_dependency(dependency: ProofDependency) -> None:
    """Save a proof dependency"""
    dependencies = _get_dependencies()
    dependencies[dependency.id] = dependency
    _save_dependencies(dependencies)

def _get_metrics() -> Dict[str, ProofMaintenanceMetric]:
    """Get all proof maintenance metrics"""
    try:
        metrics_json = db.storage.json.get("proof_maintenance_metrics", default={})
        return {k: ProofMaintenanceMetric(**v) for k, v in metrics_json.items()}
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return {}

def _save_metrics(metrics: Dict[str, ProofMaintenanceMetric]) -> None:
    """Save all proof maintenance metrics"""
    metrics_json = {k: v.dict() for k, v in metrics.items()}
    db.storage.json.put(_sanitize_key("proof_maintenance_metrics"), metrics_json)

def _save_metric(metric: ProofMaintenanceMetric) -> None:
    """Save a proof maintenance metric"""
    metrics = _get_metrics()
    metrics[metric.id] = metric
    _save_metrics(metrics)

def _get_audits() -> Dict[str, ProofAudit]:
    """Get all proof audits"""
    try:
        audits_json = db.storage.json.get("proof_maintenance_audits", default={})
        return {k: ProofAudit(**v) for k, v in audits_json.items()}
    except Exception as e:
        print(f"Error getting audits: {e}")
        return {}

def _save_audits(audits: Dict[str, ProofAudit]) -> None:
    """Save all proof audits"""
    audits_json = {k: v.dict() for k, v in audits.items()}
    db.storage.json.put(_sanitize_key("proof_maintenance_audits"), audits_json)

def _get_audit(audit_id: str) -> Optional[ProofAudit]:
    """Get a proof audit by ID"""
    audits = _get_audits()
    return audits.get(audit_id)

def _save_audit(audit: ProofAudit) -> None:
    """Save a proof audit"""
    audits = _get_audits()
    audits[audit.id] = audit
    _save_audits(audits)

# API endpoints for proof modules
@router.post("/modules", response_model=ModuleResponse)
def create_module(request: CreateModuleRequest) -> ModuleResponse:
    """Create a new proof module"""
    if _get_module(request.id):
        raise HTTPException(status_code=400, detail="Module ID already exists")
    
    module = ProofModule(
        id=request.id,
        name=request.name,
        description=request.description,
        tags=request.tags
    )
    
    _save_module(module)
    
    return ModuleResponse(module=module)

@router.get("/modules/{module_id}", response_model=ModuleResponse)
def get_module_endpoint(module_id: str) -> ModuleResponse:
    """Get a proof module by ID"""
    module = _get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return ModuleResponse(module=module)

@router.put("/modules/{module_id}", response_model=ModuleResponse)
def update_module(module_id: str, request: UpdateModuleRequest) -> ModuleResponse:
    """Update a proof module"""
    module = _get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    if request.name is not None:
        module.name = request.name
    if request.description is not None:
        module.description = request.description
    if request.status is not None:
        module.status = request.status
    if request.tags is not None:
        module.tags = request.tags
    
    module.updated_at = time.time()
    _save_module(module)
    
    return ModuleResponse(module=module)

@router.get("/modules", response_model=ListModulesResponse)
def list_modules() -> ListModulesResponse:
    """List all proof modules"""
    modules = _get_modules()
    return ListModulesResponse(modules=list(modules.values()))

# API endpoints for dependencies
@router.post("/dependencies", response_model=DependencyResponse)
def add_dependency(request: AddDependencyRequest) -> DependencyResponse:
    """Add a dependency between modules"""
    source = _get_module(request.source_module)
    if not source:
        raise HTTPException(status_code=404, detail="Source module not found")
    
    target = _get_module(request.target_module)
    if not target:
        raise HTTPException(status_code=404, detail="Target module not found")
    
    # Check for existing dependency
    dependencies = _get_dependencies()
    for dep in dependencies.values():
        if dep.source_module == request.source_module and dep.target_module == request.target_module:
            raise HTTPException(status_code=400, detail="Dependency already exists")
    
    # Check for circular dependencies
    if _has_path(request.target_module, request.source_module, dependencies):
        raise HTTPException(status_code=400, detail="Adding this dependency would create a circular reference")
    
    dependency = ProofDependency(
        source_module=request.source_module,
        target_module=request.target_module,
        dependency_type=request.dependency_type
    )
    
    _save_dependency(dependency)
    
    return DependencyResponse(dependency=dependency)

@router.get("/dependencies", response_model=ListDependenciesResponse)
def list_dependencies() -> ListDependenciesResponse:
    """List all dependencies"""
    dependencies = _get_dependencies()
    return ListDependenciesResponse(dependencies=list(dependencies.values()))

@router.get("/modules/{module_id}/dependencies", response_model=ListDependenciesResponse)
def get_module_dependencies(module_id: str) -> ListDependenciesResponse:
    """Get all dependencies for a module"""
    module = _get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    dependencies = _get_dependencies()
    module_deps = [dep for dep in dependencies.values() if dep.source_module == module_id or dep.target_module == module_id]
    
    return ListDependenciesResponse(dependencies=module_deps)

# API endpoints for metrics
@router.post("/metrics", response_model=MetricResponse)
def record_metrics(request: RecordMetricsRequest) -> MetricResponse:
    """Record metrics for a module"""
    module = _get_module(request.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    metric = ProofMaintenanceMetric(
        module_id=request.module_id,
        verification_time=request.verification_time,
        num_proofs=request.num_proofs,
        num_failed_proofs=request.num_failed_proofs,
        proof_complexity=request.proof_complexity,
        dependency_depth=request.dependency_depth,
        changes_since_last_verification=request.changes_since_last_verification
    )
    
    _save_metric(metric)
    
    # Update module with latest metrics
    module.num_proofs = request.num_proofs
    module.verification_time = request.verification_time
    
    # Calculate health score
    failure_rate = request.num_failed_proofs / max(request.num_proofs, 1)
    complexity_factor = min(1.0, request.proof_complexity / 10.0)
    change_factor = min(1.0, request.changes_since_last_verification / 20.0)
    
    health_score = 100 - (
        30 * failure_rate +  # 30% weight for failures
        25 * complexity_factor +  # 25% weight for complexity
        25 * change_factor +  # 25% weight for change frequency
        20 * min(1.0, request.verification_time / 60.0)  # 20% weight for verification time
    )
    
    module.health_score = max(0.0, min(100.0, health_score))
    
    if module.health_score < 60:
        module.status = "needs-repair"
    elif module.health_score < 80:
        module.status = "refactoring"
    else:
        module.status = "stable"
    
    module.updated_at = time.time()
    _save_module(module)
    
    return MetricResponse(metric=metric)

@router.get("/metrics", response_model=ListMetricsResponse)
def list_metrics() -> ListMetricsResponse:
    """List all metrics"""
    metrics = _get_metrics()
    return ListMetricsResponse(metrics=list(metrics.values()))

@router.get("/modules/{module_id}/metrics", response_model=ListMetricsResponse)
def get_module_metrics(module_id: str) -> ListMetricsResponse:
    """Get all metrics for a module"""
    module = _get_module(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    metrics = _get_metrics()
    module_metrics = [m for m in metrics.values() if m.module_id == module_id]
    
    return ListMetricsResponse(metrics=module_metrics)

# API endpoints for audits
@router.post("/audits", response_model=AuditResponse)
def start_audit(request: StartAuditRequest) -> AuditResponse:
    """Start a new proof audit"""
    audit = ProofAudit(auditor=request.auditor)
    _save_audit(audit)
    
    return AuditResponse(audit=audit)

@router.put("/audits/{audit_id}/complete", response_model=AuditResponse)
def complete_audit(audit_id: str, request: CompleteAuditRequest) -> AuditResponse:
    """Complete a proof audit"""
    audit = _get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    if audit.status != "running":
        raise HTTPException(status_code=400, detail="Audit is not in running state")
    
    audit.findings = request.findings
    audit.recommendations = request.recommendations
    audit.health_assessment = request.health_assessment
    audit.status = "completed"
    audit.completed_at = time.time()
    
    _save_audit(audit)
    
    return AuditResponse(audit=audit)

@router.get("/audits/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: str) -> AuditResponse:
    """Get an audit by ID"""
    audit = _get_audit(audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return AuditResponse(audit=audit)

@router.get("/audits", response_model=ListAuditsResponse)
def list_audits() -> ListAuditsResponse:
    """List all audits"""
    audits = _get_audits()
    return ListAuditsResponse(audits=list(audits.values()))

# API endpoint for dashboard
@router.get("/dashboard", response_model=MaintenanceDashboardResponse)
def get_maintenance_dashboard() -> MaintenanceDashboardResponse:
    """Get proof maintenance dashboard data"""
    modules = _get_modules()
    metrics = _get_metrics()
    
    # Calculate status counts
    status_counts = {}
    for module in modules.values():
        status_counts[module.status] = status_counts.get(module.status, 0) + 1
    
    # Calculate averages
    if modules:
        avg_time = sum(m.verification_time for m in modules.values()) / len(modules)
        avg_health = sum(m.health_score for m in modules.values()) / len(modules)
    else:
        avg_time = 0.0
        avg_health = 0.0
    
    # Identify modules with proof debt
    proof_debt_modules = [
        {
            "id": m.id,
            "name": m.name,
            "health_score": m.health_score,
            "status": m.status
        }
        for m in sorted(modules.values(), key=lambda x: x.health_score)[:5]  # Lowest 5 health scores
    ]
    
    # Identify high impact modules
    dependencies = _get_dependencies()
    module_impact = {}
    for module_id in modules:
        # Count incoming dependencies
        incoming = sum(1 for dep in dependencies.values() if dep.target_module == module_id)
        # Weight by verification time
        module = modules[module_id]
        module_impact[module_id] = incoming * module.verification_time
    
    high_impact_modules = [
        {
            "id": modules[module_id].id,
            "name": modules[module_id].name,
            "impact_score": impact,
            "dependency_count": sum(1 for dep in dependencies.values() if dep.target_module == module_id)
        }
        for module_id, impact in sorted(module_impact.items(), key=lambda x: x[1], reverse=True)[:5]  # Highest 5 impact scores
    ]
    
    # Generate time series data (last 30 data points)
    metrics_by_module_by_time = {}
    for metric in sorted(metrics.values(), key=lambda x: x.timestamp):
        if metric.module_id not in metrics_by_module_by_time:
            metrics_by_module_by_time[metric.module_id] = []
        metrics_by_module_by_time[metric.module_id].append(metric)
    
    verification_times = []
    health_scores = []
    failed_proofs = []
    
    # Get the most recent metrics for each module, for up to the last 30 time points
    for module_metrics in metrics_by_module_by_time.values():
        for metric in module_metrics[-30:]:
            verification_times.append(metric.verification_time)
            health_scores.append(modules[metric.module_id].health_score if metric.module_id in modules else 0)
            failed_proofs.append(metric.num_failed_proofs)
    
    time_series = {
        "verification_times": verification_times[-30:],
        "health_scores": health_scores[-30:],
        "failed_proofs": failed_proofs[-30:]
    }
    
    return MaintenanceDashboardResponse(
        total_modules=len(modules),
        modules_by_status=status_counts,
        avg_verification_time=avg_time,
        avg_health_score=avg_health,
        proof_debt_modules=proof_debt_modules,
        high_impact_modules=high_impact_modules,
        time_series_data=time_series
    )

# Helper function to check for circular dependencies
def _has_path(start: str, end: str, dependencies: Dict[str, ProofDependency]) -> bool:
    """Check if there is a path from start to end in the dependency graph"""
    if start == end:
        return True
    
    visited = set()
    stack = [start]
    
    while stack:
        current = stack.pop()
        if current in visited:
            continue
        
        visited.add(current)
        
        for dep in dependencies.values():
            if dep.source_module == current:
                if dep.target_module == end:
                    return True
                stack.append(dep.target_module)
    
    return False
