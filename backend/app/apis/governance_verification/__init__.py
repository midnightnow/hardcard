from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
import time
import hashlib
import databutton as db
import json

router = APIRouter(prefix="/governance")

class VerificationPipeline(BaseModel):
    """Configuration for a verification pipeline"""
    id: str = Field(default_factory=lambda: f"pipeline_{int(time.time())}")
    name: str
    description: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    module_dependencies: List[str] = []
    verification_thresholds: Dict[str, Any] = {}
    enabled: bool = True

class VerificationRun(BaseModel):
    """A single run of a verification pipeline"""
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

class CryptographicComponent(BaseModel):
    """A cryptographic component in the system inventory"""
    id: str = Field(default_factory=lambda: f"crypto_{int(time.time())}")
    algorithm: str  # e.g., "ECDSA P-256", "AES-256-GCM"
    key_length: int
    implementation: str  # e.g., "software-openssl", "hardware-tpm"
    usage_context: List[str]  # e.g., ["signin", "transaction-verification"]
    expected_lifespan: Optional[str] = None  # e.g., "2030-12-31"
    status: str = "active"  # active, deprecated, post-quantum-candidate
    replacement: Optional[str] = None  # ID of replacement algorithm
    formal_properties: List[str] = []  # formal security properties

class CreatePipelineRequest(BaseModel):
    """Request to create a new verification pipeline"""
    name: str
    description: str
    module_dependencies: List[str] = []
    verification_thresholds: Dict[str, Any] = {}

class RunVerificationRequest(BaseModel):
    """Request to run a verification pipeline"""
    pipeline_id: str
    triggered_by: str = "manual"
    commit_id: Optional[str] = None

class RegisterCryptoComponentRequest(BaseModel):
    """Request to register a cryptographic component"""
    algorithm: str
    key_length: int
    implementation: str
    usage_context: List[str]
    expected_lifespan: Optional[str] = None
    formal_properties: List[str] = []

class PipelineResponse(BaseModel):
    """Response containing pipeline details"""
    pipeline: VerificationPipeline

class RunResponse(BaseModel):
    """Response containing run details"""
    run: VerificationRun

class ComponentResponse(BaseModel):
    """Response containing cryptographic component details"""
    component: CryptographicComponent

class ListPipelinesResponse(BaseModel):
    """Response containing a list of pipelines"""
    pipelines: List[VerificationPipeline]

class ListRunsResponse(BaseModel):
    """Response containing a list of verification runs"""
    runs: List[VerificationRun]

class ListCryptoComponentsResponse(BaseModel):
    """Response containing a list of cryptographic components"""
    components: List[CryptographicComponent]

class VerificationMetricsResponse(BaseModel):
    """Response containing verification metrics"""
    total_pipelines: int
    active_pipelines: int
    verification_runs_last_24h: int
    avg_verification_time: float
    passing_proofs_percentage: float
    component_health: Dict[str, str]  # module -> health status
    recent_failures: List[Dict[str, Any]]

class CryptographicHealthResponse(BaseModel):
    """Response containing cryptographic health metrics"""
    total_components: int
    components_by_status: Dict[str, int]  # status -> count
    post_quantum_readiness: float  # percentage
    components_near_deprecation: List[Dict[str, Any]]
    security_recommendations: List[str]

# Storage helpers
def _sanitize_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def _get_pipelines() -> Dict[str, VerificationPipeline]:
    """Get all verification pipelines"""
    try:
        pipelines_json = db.storage.json.get("governance_verification_pipelines", default={})
        return {k: VerificationPipeline(**v) for k, v in pipelines_json.items()}
    except Exception as e:
        print(f"Error getting pipelines: {e}")
        return {}

def _save_pipelines(pipelines: Dict[str, VerificationPipeline]) -> None:
    """Save all verification pipelines"""
    pipelines_json = {k: v.dict() for k, v in pipelines.items()}
    db.storage.json.put(_sanitize_key("governance_verification_pipelines"), pipelines_json)

def _get_pipeline(pipeline_id: str) -> Optional[VerificationPipeline]:
    """Get a verification pipeline by ID"""
    pipelines = _get_pipelines()
    return pipelines.get(pipeline_id)

def _save_pipeline(pipeline: VerificationPipeline) -> None:
    """Save a verification pipeline"""
    pipelines = _get_pipelines()
    pipelines[pipeline.id] = pipeline
    _save_pipelines(pipelines)

def _get_runs() -> Dict[str, VerificationRun]:
    """Get all verification runs"""
    try:
        runs_json = db.storage.json.get("governance_verification_runs", default={})
        return {k: VerificationRun(**v) for k, v in runs_json.items()}
    except Exception as e:
        print(f"Error getting runs: {e}")
        return {}

def _save_runs(runs: Dict[str, VerificationRun]) -> None:
    """Save all verification runs"""
    runs_json = {k: v.dict() for k, v in runs.items()}
    db.storage.json.put(_sanitize_key("governance_verification_runs"), runs_json)

def _get_run(run_id: str) -> Optional[VerificationRun]:
    """Get a verification run by ID"""
    runs = _get_runs()
    return runs.get(run_id)

def _save_run(run: VerificationRun) -> None:
    """Save a verification run"""
    runs = _get_runs()
    runs[run.id] = run
    _save_runs(runs)

def _get_crypto_components() -> Dict[str, CryptographicComponent]:
    """Get all cryptographic components"""
    try:
        components_json = db.storage.json.get("governance_crypto_components", default={})
        return {k: CryptographicComponent(**v) for k, v in components_json.items()}
    except Exception as e:
        print(f"Error getting crypto components: {e}")
        return {}

def _save_crypto_components(components: Dict[str, CryptographicComponent]) -> None:
    """Save all cryptographic components"""
    components_json = {k: v.dict() for k, v in components.items()}
    db.storage.json.put(_sanitize_key("governance_crypto_components"), components_json)

def _get_crypto_component(component_id: str) -> Optional[CryptographicComponent]:
    """Get a cryptographic component by ID"""
    components = _get_crypto_components()
    return components.get(component_id)

def _save_crypto_component(component: CryptographicComponent) -> None:
    """Save a cryptographic component"""
    components = _get_crypto_components()
    components[component.id] = component
    _save_crypto_components(components)

# API endpoints for verification pipelines
@router.post("/pipelines", response_model=PipelineResponse)
def create_pipeline(request: CreatePipelineRequest) -> PipelineResponse:
    """Create a new verification pipeline"""
    pipeline = VerificationPipeline(
        name=request.name,
        description=request.description,
        module_dependencies=request.module_dependencies,
        verification_thresholds=request.verification_thresholds
    )
    
    _save_pipeline(pipeline)
    
    return PipelineResponse(pipeline=pipeline)

@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(pipeline_id: str) -> PipelineResponse:
    """Get a verification pipeline by ID"""
    pipeline = _get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return PipelineResponse(pipeline=pipeline)

@router.get("/pipelines", response_model=ListPipelinesResponse)
def list_pipelines() -> ListPipelinesResponse:
    """List all verification pipelines"""
    pipelines = _get_pipelines()
    return ListPipelinesResponse(pipelines=list(pipelines.values()))

@router.post("/pipelines/{pipeline_id}/enable")
def enable_pipeline(pipeline_id: str) -> PipelineResponse:
    """Enable a verification pipeline"""
    pipeline = _get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline.enabled = True
    pipeline.updated_at = time.time()
    _save_pipeline(pipeline)
    
    return PipelineResponse(pipeline=pipeline)

@router.post("/pipelines/{pipeline_id}/disable")
def disable_pipeline(pipeline_id: str) -> PipelineResponse:
    """Disable a verification pipeline"""
    pipeline = _get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline.enabled = False
    pipeline.updated_at = time.time()
    _save_pipeline(pipeline)
    
    return PipelineResponse(pipeline=pipeline)

# API endpoints for verification runs
@router.post("/runs", response_model=RunResponse)
def run_verification(request: RunVerificationRequest) -> RunResponse:
    """Run a verification pipeline"""
    pipeline = _get_pipeline(request.pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    if not pipeline.enabled:
        raise HTTPException(status_code=400, detail="Pipeline is disabled")
    
    # Create a new run
    run = VerificationRun(
        pipeline_id=pipeline.id,
        triggered_by=request.triggered_by,
        commit_id=request.commit_id
    )
    
    # In a real implementation, this would start an async task to run the verification
    # For now, we'll simulate a completed verification
    run.status = "completed"
    run.completed_at = time.time()
    run.results = {
        "passed": True,
        "verification_steps": [
            {"name": "Hash Chain Verification", "passed": True, "duration": 0.5},
            {"name": "Temporal Integrity Verification", "passed": True, "duration": 0.3},
            {"name": "Signature Verification", "passed": True, "duration": 0.8}
        ]
    }
    run.metrics = {
        "total_duration": 1.6,
        "proofs_verified": 42,
        "proofs_failed": 0
    }
    
    _save_run(run)
    
    return RunResponse(run=run)

@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str) -> RunResponse:
    """Get a verification run by ID"""
    run = _get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return RunResponse(run=run)

@router.get("/runs", response_model=ListRunsResponse)
def list_runs() -> ListRunsResponse:
    """List all verification runs"""
    runs = _get_runs()
    return ListRunsResponse(runs=list(runs.values()))

@router.get("/pipelines/{pipeline_id}/runs", response_model=ListRunsResponse)
def list_pipeline_runs(pipeline_id: str) -> ListRunsResponse:
    """List all verification runs for a pipeline"""
    pipeline = _get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    runs = _get_runs()
    pipeline_runs = [run for run in runs.values() if run.pipeline_id == pipeline_id]
    
    return ListRunsResponse(runs=pipeline_runs)

# API endpoints for cryptographic components
@router.post("/crypto-components", response_model=ComponentResponse)
def register_crypto_component(request: RegisterCryptoComponentRequest) -> ComponentResponse:
    """Register a cryptographic component"""
    component = CryptographicComponent(
        algorithm=request.algorithm,
        key_length=request.key_length,
        implementation=request.implementation,
        usage_context=request.usage_context,
        expected_lifespan=request.expected_lifespan,
        formal_properties=request.formal_properties
    )
    
    _save_crypto_component(component)
    
    return ComponentResponse(component=component)

@router.get("/crypto-components/{component_id}", response_model=ComponentResponse)
def get_crypto_component(component_id: str) -> ComponentResponse:
    """Get a cryptographic component by ID"""
    component = _get_crypto_component(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return ComponentResponse(component=component)

@router.get("/crypto-components", response_model=ListCryptoComponentsResponse)
def list_crypto_components() -> ListCryptoComponentsResponse:
    """List all cryptographic components"""
    components = _get_crypto_components()
    return ListCryptoComponentsResponse(components=list(components.values()))

@router.post("/crypto-components/{component_id}/deprecate")
def deprecate_crypto_component(component_id: str, replacement_id: Optional[str] = None) -> ComponentResponse:
    """Deprecate a cryptographic component"""
    component = _get_crypto_component(component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    if replacement_id:
        replacement = _get_crypto_component(replacement_id)
        if not replacement:
            raise HTTPException(status_code=404, detail="Replacement component not found")
        component.replacement = replacement_id
    
    component.status = "deprecated"
    _save_crypto_component(component)
    
    return ComponentResponse(component=component)

# API endpoints for metrics and dashboard data
@router.get("/metrics/verification", response_model=VerificationMetricsResponse)
def get_verification_metrics() -> VerificationMetricsResponse:
    """Get verification metrics for dashboard"""
    pipelines = _get_pipelines()
    runs = _get_runs()
    
    now = time.time()
    recent_runs = [run for run in runs.values() if run.started_at > now - 86400]  # Last 24h
    
    failed_runs = [run for run in recent_runs if run.status == "failed"]
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
                failures = sum(1 for run in pipeline_runs if run.status == "failed")
                health = "healthy" if failures == 0 else "degraded" if failures < len(pipeline_runs) / 2 else "critical"
                component_health[module] = health
            else:
                component_health[module] = "unknown"
    
    return VerificationMetricsResponse(
        total_pipelines=len(pipelines),
        active_pipelines=sum(1 for p in pipelines.values() if p.enabled),
        verification_runs_last_24h=len(recent_runs),
        avg_verification_time=avg_time,
        passing_proofs_percentage=passing_percentage,
        component_health=component_health,
        recent_failures=[{
            "run_id": run.id,
            "pipeline_name": pipelines[run.pipeline_id].name if run.pipeline_id in pipelines else "Unknown",
            "started_at": run.started_at,
            "failures": len(run.proof_failures)
        } for run in failed_runs]
    )

@router.get("/metrics/crypto-health", response_model=CryptographicHealthResponse)
def get_crypto_health_metrics() -> CryptographicHealthResponse:
    """Get cryptographic health metrics for dashboard"""
    components = _get_crypto_components()
    
    status_counts = {}
    for component in components.values():
        status_counts[component.status] = status_counts.get(component.status, 0) + 1
    
    # Calculate post-quantum readiness
    pq_ready = sum(1 for c in components.values() if "post-quantum" in c.status.lower() or any("post-quantum" in prop.lower() for prop in c.formal_properties))
    pq_readiness = pq_ready / max(len(components), 1) * 100
    
    # Identify components near deprecation
    near_deprecation = []
    for component in components.values():
        if component.expected_lifespan and component.status == "active":
            try:
                import datetime
                lifespan_date = datetime.datetime.strptime(component.expected_lifespan, "%Y-%m-%d").timestamp()
                if lifespan_date - now < 15552000:  # 180 days
                    near_deprecation.append({
                        "id": component.id,
                        "algorithm": component.algorithm,
                        "days_remaining": int((lifespan_date - now) / 86400)
                    })
            except:
                pass
    
    # Generate security recommendations
    recommendations = []
    if pq_readiness < 30:
        recommendations.append("Increase post-quantum cryptography adoption")
    if status_counts.get("deprecated", 0) > 0:
        recommendations.append("Replace deprecated cryptographic components")
    if len(near_deprecation) > 0:
        recommendations.append(f"Plan migration for {len(near_deprecation)} soon-to-expire cryptographic components")
    
    return CryptographicHealthResponse(
        total_components=len(components),
        components_by_status=status_counts,
        post_quantum_readiness=pq_readiness,
        components_near_deprecation=near_deprecation,
        security_recommendations=recommendations
    )
