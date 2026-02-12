"""Regression Verification API

This API implements automated regression verification pipelines that continuously
verify that updates or modifications do not break previously verified properties.
It forms a critical part of the Long-Term Governance and Regression Verification
framework, ensuring that Hardcard remains secure, maintainable, and adaptable
over its entire lifecycle.
"""

from fastapi import APIRouter, HTTPException, Body, Query, Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from enum import Enum
import time
import re
import json
import databutton as db
from datetime import datetime, timedelta

router = APIRouter(prefix="/regression-verification")

# --- MODEL DEFINITIONS ---

class SMTSolver(str, Enum):
    """Supported SMT solvers for verification"""
    Z3 = "z3"
    CVC5 = "cvc5"
    VAMPIRE = "vampire"
    YICES = "yices"
    ALT_ERGO = "alt-ergo"

class InvariantGenerationTool(str, Enum):
    """Supported invariant generation tools"""
    TEMPLATE_SYNTHESIS = "template_synthesis"
    IC3 = "ic3"
    PREDICATE_ABSTRACTION = "predicate_abstraction"
    NEURAL_INFERENCE = "neural_inference"
    HEURISTIC = "heuristic"

class TriggerFrequency(str, Enum):
    """Frequency of verification pipeline triggers"""
    EVERY_COMMIT = "every_commit"
    NIGHTLY = "nightly"
    WEEKLY = "weekly"
    PER_SPRINT = "per_sprint"
    MANUAL = "manual"

class VerificationStatus(str, Enum):
    """Status of verification run"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"

class PipelineTarget(str, Enum):
    """Target component for verification"""
    FINANCIAL_LEDGER = "financial_ledger"
    CRYPTO_PROTOCOL = "crypto_protocol"
    HARDWARE_INTERFACE = "hardware_interface"
    USER_INTERFACE = "user_interface"
    GOVERNANCE_PROTOCOL = "governance_protocol"
    LEGACY_INTERFACE = "legacy_interface"
    CONSENSUS_MECHANISM = "consensus_mechanism"

class VerificationPriority(str, Enum):
    """Priority level for verification pipelines"""
    CRITICAL = "critical"  # Security-critical properties
    HIGH = "high"         # Core functionality 
    MEDIUM = "medium"     # Important but not critical
    LOW = "low"           # Nice-to-have properties

# --- MAIN MODELS ---

class VerificationInvariant(BaseModel):
    """Formal invariant to be verified"""
    id: str = Field(default_factory=lambda: f"inv_{int(time.time())}")
    name: str
    description: str
    formal_expression: str  # The actual mathematical expression of the invariant
    category: str  # Domain category (financial, cryptographic, etc.)
    priority: VerificationPriority = VerificationPriority.MEDIUM
    dependencies: List[str] = []  # IDs of invariants this depends on
    metadata: Dict[str, Any] = {}

class RegressionPipeline(BaseModel):
    """Configuration for a regression verification pipeline"""
    id: str = Field(default_factory=lambda: f"pipeline_{int(time.time())}")
    name: str
    description: str
    target: PipelineTarget
    invariants: List[str]  # List of invariant IDs this pipeline verifies
    solvers: List[SMTSolver]
    invariant_tools: List[InvariantGenerationTool] = []
    trigger_frequency: TriggerFrequency = TriggerFrequency.NIGHTLY
    timeout_seconds: int = 3600  # Default 1 hour
    notification_emails: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    enabled: bool = True
    verification_thresholds: Dict[str, Any] = {
        "proof_verification_max_time": 300,  # Max 300 seconds per proof
        "manual_repair_threshold": 5,      # Alert if more than 5 proofs need manual fixing
        "success_rate_threshold": 95       # Success rate threshold percentage
    }

class ProofFailure(BaseModel):
    """Details of a proof failure"""
    invariant_id: str
    failure_reason: str
    counter_example: Optional[Dict[str, Any]] = None
    solver_output: str = ""
    failing_components: List[str] = []
    repair_suggestion: Optional[str] = None

class VerificationRun(BaseModel):
    """Record of a verification pipeline run"""
    id: str = Field(default_factory=lambda: f"run_{int(time.time())}")
    pipeline_id: str
    commit_id: Optional[str] = None
    branch: Optional[str] = None
    triggered_by: str = "manual"  # manual, scheduled, commit
    status: VerificationStatus = VerificationStatus.QUEUED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    verification_results: Dict[str, bool] = {}  # Mapping of invariant ID to verification result
    failures: List[ProofFailure] = []
    metrics: Dict[str, Any] = {}

class VerificationTrend(BaseModel):
    """Trend data for verification metrics over time"""
    pipeline_id: str
    data_points: List[Dict[str, Any]] = []  # Time series data 
    trend_start: datetime
    trend_end: datetime
    trend_granularity: str = "daily"  # daily, weekly, monthly

class MaintenanceAlert(BaseModel):
    """Alert for proof maintenance issues"""
    id: str = Field(default_factory=lambda: f"alert_{int(time.time())}")
    pipeline_id: str
    severity: str  # high, medium, low
    title: str
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    affected_invariants: List[str] = []
    suggested_actions: List[str] = []

# --- REQUEST/RESPONSE MODELS ---

class CreateInvariantRequest(BaseModel):
    """Request to create a new verification invariant"""
    name: str
    description: str
    formal_expression: str
    category: str
    priority: VerificationPriority = VerificationPriority.MEDIUM
    dependencies: List[str] = []
    metadata: Dict[str, Any] = {}

class CreatePipelineRequest(BaseModel):
    """Request to create a new regression verification pipeline"""
    name: str
    description: str
    target: PipelineTarget
    invariants: List[str]
    solvers: List[SMTSolver]
    invariant_tools: List[InvariantGenerationTool] = []
    trigger_frequency: TriggerFrequency = TriggerFrequency.NIGHTLY
    timeout_seconds: int = 3600
    notification_emails: List[str] = []
    verification_thresholds: Dict[str, Any] = {}

class RunVerificationRequest(BaseModel):
    """Request to run a verification pipeline"""
    pipeline_id: str
    commit_id: Optional[str] = None
    branch: Optional[str] = None

class InvariantResponse(BaseModel):
    """Response containing a verification invariant"""
    invariant: VerificationInvariant

class InvariantsListResponse(BaseModel):
    """Response containing a list of verification invariants"""
    invariants: List[VerificationInvariant]

class PipelineResponse(BaseModel):
    """Response containing a regression verification pipeline"""
    pipeline: RegressionPipeline

class PipelinesListResponse(BaseModel):
    """Response containing a list of regression verification pipelines"""
    pipelines: List[RegressionPipeline]

class VerificationRunResponse(BaseModel):
    """Response containing a verification run"""
    run: VerificationRun

class VerificationRunsListResponse(BaseModel):
    """Response containing a list of verification runs"""
    runs: List[VerificationRun]

class DashboardMetricsResponse(BaseModel):
    """Response containing metrics for the verification dashboard"""
    total_invariants: int
    total_pipelines: int
    active_pipelines: int
    verification_runs_last_24h: int
    success_rate: float  # 0-100 percentage
    average_verification_time: float  # seconds
    failure_by_category: Dict[str, int]  # category -> count
    maintenance_alerts: List[MaintenanceAlert]
    category_coverage: Dict[str, float]  # category -> percentage coverage

class TrendsResponse(BaseModel):
    """Response containing verification trends"""
    trends: List[VerificationTrend]

# --- STORAGE HELPERS ---

def _sanitize_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def _get_invariants() -> Dict[str, VerificationInvariant]:
    """Get all verification invariants"""
    try:
        invariants_json = db.storage.json.get(_sanitize_key("verification_invariants"), default={})
        return {k: VerificationInvariant(**v) for k, v in invariants_json.items()}
    except Exception as e:
        print(f"Error getting invariants: {e}")
        return {}

def _save_invariants(invariants: Dict[str, VerificationInvariant]) -> None:
    """Save all verification invariants"""
    invariants_json = {k: v.dict() for k, v in invariants.items()}
    db.storage.json.put(_sanitize_key("verification_invariants"), invariants_json)

def _get_pipelines() -> Dict[str, RegressionPipeline]:
    """Get all regression verification pipelines"""
    try:
        pipelines_json = db.storage.json.get(_sanitize_key("regression_pipelines"), default={})
        return {k: RegressionPipeline(**v) for k, v in pipelines_json.items()}
    except Exception as e:
        print(f"Error getting pipelines: {e}")
        return {}

def _save_pipelines(pipelines: Dict[str, RegressionPipeline]) -> None:
    """Save all regression verification pipelines"""
    pipelines_json = {k: v.dict() for k, v in pipelines.items()}
    db.storage.json.put(_sanitize_key("regression_pipelines"), pipelines_json)

def _get_verification_runs() -> Dict[str, VerificationRun]:
    """Get all verification runs"""
    try:
        runs_json = db.storage.json.get(_sanitize_key("verification_runs"), default={})
        return {k: VerificationRun(**v) for k, v in runs_json.items()}
    except Exception as e:
        print(f"Error getting verification runs: {e}")
        return {}

def _save_verification_runs(runs: Dict[str, VerificationRun]) -> None:
    """Save all verification runs"""
    runs_json = {k: v.dict() for k, v in runs.items()}
    db.storage.json.put(_sanitize_key("verification_runs"), runs_json)

def _get_maintenance_alerts() -> Dict[str, MaintenanceAlert]:
    """Get all maintenance alerts"""
    try:
        alerts_json = db.storage.json.get(_sanitize_key("maintenance_alerts"), default={})
        return {k: MaintenanceAlert(**v) for k, v in alerts_json.items()}
    except Exception as e:
        print(f"Error getting maintenance alerts: {e}")
        return {}

def _save_maintenance_alerts(alerts: Dict[str, MaintenanceAlert]) -> None:
    """Save all maintenance alerts"""
    alerts_json = {k: v.dict() for k, v in alerts.items()}
    db.storage.json.put(_sanitize_key("maintenance_alerts"), alerts_json)

# --- VERIFICATION LOGIC ---

def verify_invariant(
    invariant: VerificationInvariant, 
    solver: SMTSolver, 
    timeout: int = 300
) -> Tuple[bool, Optional[ProofFailure]]:
    """Verify a single invariant against an SMT solver
    
    This is a mock implementation that simulates the verification process.
    In a real implementation, this would interface with actual SMT solvers.
    """
    # Mock implementation - in reality would call out to SMT solvers
    import random
    success_rate = 0.9  # 90% success rate for simulation
    
    # Simulate verification time based on the complexity of the expression
    verification_time = len(invariant.formal_expression) / 10 + random.randint(1, 20)
    
    # Simulate a timeout
    if verification_time > timeout:
        return False, ProofFailure(
            invariant_id=invariant.id,
            failure_reason="Verification timeout",
            solver_output=f"Solver {solver} exceeded timeout of {timeout} seconds"
        )
    
    # Simulate success/failure
    if random.random() < success_rate:
        return True, None
    else:
        # Generate a plausible counter-example
        counter_example = None
        if "=" in invariant.formal_expression:
            # For an equality, create a counter example where they're not equal
            parts = invariant.formal_expression.split("=")
            if len(parts) == 2:
                counter_example = {
                    "left_side": parts[0].strip(),
                    "right_side": parts[1].strip(),
                    "values": {
                        "x": 5,
                        "y": 10
                    },
                    "evaluation": {
                        "left": 15,
                        "right": 16
                    }
                }
        
        return False, ProofFailure(
            invariant_id=invariant.id,
            failure_reason="Verification failed",
            counter_example=counter_example,
            solver_output=f"Solver {solver} found a counter-example",
            failing_components=[invariant.category],
            repair_suggestion="Check boundary conditions in the formal expression"
        )

# --- API ENDPOINTS FOR INVARIANTS ---

@router.post("/invariants", response_model=InvariantResponse)
def create_invariant(request: CreateInvariantRequest) -> InvariantResponse:
    """Create a new verification invariant
    
    This endpoint allows defining new formal invariants that can be verified
    against system changes to detect regressions.
    """
    invariant = VerificationInvariant(
        name=request.name,
        description=request.description,
        formal_expression=request.formal_expression,
        category=request.category,
        priority=request.priority,
        dependencies=request.dependencies,
        metadata=request.metadata
    )
    
    invariants = _get_invariants()
    invariants[invariant.id] = invariant
    _save_invariants(invariants)
    
    return InvariantResponse(invariant=invariant)

@router.get("/invariants/{invariant_id}", response_model=InvariantResponse)
def get_invariant(invariant_id: str) -> InvariantResponse:
    """Get a verification invariant by ID"""
    invariants = _get_invariants()
    if invariant_id not in invariants:
        raise HTTPException(status_code=404, detail=f"Invariant with ID {invariant_id} not found")
    
    return InvariantResponse(invariant=invariants[invariant_id])

@router.get("/invariants", response_model=InvariantsListResponse)
def list_invariants(
    category: Optional[str] = None,
    priority: Optional[VerificationPriority] = None
) -> InvariantsListResponse:
    """List all verification invariants with optional filtering"""
    invariants = _get_invariants()
    
    filtered_invariants = list(invariants.values())
    
    # Apply category filter if provided
    if category:
        filtered_invariants = [inv for inv in filtered_invariants if inv.category == category]
    
    # Apply priority filter if provided
    if priority:
        filtered_invariants = [inv for inv in filtered_invariants if inv.priority == priority]
    
    return InvariantsListResponse(invariants=filtered_invariants)

# --- API ENDPOINTS FOR PIPELINES ---

@router.post("/pipelines", response_model=PipelineResponse)
def create_regression_pipeline(request: CreatePipelineRequest) -> PipelineResponse:
    """Create a new regression verification pipeline
    
    This endpoint creates a new pipeline that will automatically verify
    a set of invariants on a specified schedule or trigger.
    """
    # Validate invariants exist
    invariants = _get_invariants()
    for invariant_id in request.invariants:
        if invariant_id not in invariants:
            raise HTTPException(status_code=400, detail=f"Invariant with ID {invariant_id} not found")
    
    pipeline = RegressionPipeline(
        name=request.name,
        description=request.description,
        target=request.target,
        invariants=request.invariants,
        solvers=request.solvers,
        invariant_tools=request.invariant_tools,
        trigger_frequency=request.trigger_frequency,
        timeout_seconds=request.timeout_seconds,
        notification_emails=request.notification_emails
    )
    
    # Add custom verification thresholds if provided
    if request.verification_thresholds:
        pipeline.verification_thresholds.update(request.verification_thresholds)
    
    pipelines = _get_pipelines()
    pipelines[pipeline.id] = pipeline
    _save_pipelines(pipelines)
    
    return PipelineResponse(pipeline=pipeline)

@router.get("/pipelines/{pipeline_id}", response_model=PipelineResponse)
def get_regression_pipeline(pipeline_id: str) -> PipelineResponse:
    """Get a regression verification pipeline by ID"""
    pipelines = _get_pipelines()
    if pipeline_id not in pipelines:
        raise HTTPException(status_code=404, detail=f"Pipeline with ID {pipeline_id} not found")
    
    return PipelineResponse(pipeline=pipelines[pipeline_id])

@router.get("/pipelines", response_model=PipelinesListResponse)
def list_regression_pipelines(
    target: Optional[PipelineTarget] = None,
    enabled: Optional[bool] = None
) -> PipelinesListResponse:
    """List all regression verification pipelines with optional filtering"""
    pipelines = _get_pipelines()
    
    filtered_pipelines = list(pipelines.values())
    
    # Apply target filter if provided
    if target:
        filtered_pipelines = [p for p in filtered_pipelines if p.target == target]
    
    # Apply enabled filter if provided
    if enabled is not None:
        filtered_pipelines = [p for p in filtered_pipelines if p.enabled == enabled]
    
    return PipelinesListResponse(pipelines=filtered_pipelines)

@router.post("/pipelines/{pipeline_id}/enable")
def enable_regression_pipeline(pipeline_id: str) -> PipelineResponse:
    """Enable a regression verification pipeline"""
    pipelines = _get_pipelines()
    if pipeline_id not in pipelines:
        raise HTTPException(status_code=404, detail=f"Pipeline with ID {pipeline_id} not found")
    
    pipeline = pipelines[pipeline_id]
    pipeline.enabled = True
    pipeline.updated_at = datetime.now()
    _save_pipelines(pipelines)
    
    return PipelineResponse(pipeline=pipeline)

@router.post("/pipelines/{pipeline_id}/disable")
def disable_regression_pipeline(pipeline_id: str) -> PipelineResponse:
    """Disable a regression verification pipeline"""
    pipelines = _get_pipelines()
    if pipeline_id not in pipelines:
        raise HTTPException(status_code=404, detail=f"Pipeline with ID {pipeline_id} not found")
    
    pipeline = pipelines[pipeline_id]
    pipeline.enabled = False
    pipeline.updated_at = datetime.now()
    _save_pipelines(pipelines)
    
    return PipelineResponse(pipeline=pipeline)

# --- API ENDPOINTS FOR VERIFICATION RUNS ---

@router.post("/runs", response_model=VerificationRunResponse)
def run_regression_verification(request: RunVerificationRequest) -> VerificationRunResponse:
    """Run a verification pipeline
    
    This endpoint triggers a verification run for the specified pipeline.
    The verification will check all invariants associated with the pipeline.
    """
    pipelines = _get_pipelines()
    if request.pipeline_id not in pipelines:
        raise HTTPException(status_code=404, detail=f"Pipeline with ID {request.pipeline_id} not found")
    
    pipeline = pipelines[request.pipeline_id]
    if not pipeline.enabled:
        raise HTTPException(status_code=400, detail="Pipeline is disabled")
    
    # Create a new verification run
    run = VerificationRun(
        pipeline_id=pipeline.id,
        commit_id=request.commit_id,
        branch=request.branch,
        triggered_by="manual",
        status=VerificationStatus.QUEUED
    )
    
    # In a real implementation, this would queue the job for asynchronous processing
    # For this demonstration, we'll simulate immediate verification
    
    # Start verification
    run.status = VerificationStatus.RUNNING
    run.started_at = datetime.now()
    
    # Simulate verification process
    invariants = _get_invariants()
    start_time = time.time()
    
    for invariant_id in pipeline.invariants:
        if invariant_id not in invariants:
            continue  # Skip missing invariants
        
        invariant = invariants[invariant_id]
        
        # Try verification with all configured solvers
        verified = False
        failures = []
        
        for solver in pipeline.solvers:
            success, failure = verify_invariant(
                invariant, 
                solver, 
                timeout=pipeline.timeout_seconds
            )
            
            if success:
                verified = True
                break
            elif failure:
                failures.append(failure)
        
        run.verification_results[invariant_id] = verified
        
        # Record failures if all solvers failed
        if not verified and failures:
            # Take the most informative failure (the one with a counter-example if available)
            best_failure = next((f for f in failures if f.counter_example), failures[0])
            run.failures.append(best_failure)
    
    # Complete verification
    end_time = time.time()
    run.completed_at = datetime.now()
    run.duration_seconds = int(end_time - start_time)
    
    # Determine overall status
    if any(not result for result in run.verification_results.values()):
        run.status = VerificationStatus.FAILED
    else:
        run.status = VerificationStatus.SUCCEEDED
    
    # Calculate metrics
    total_invariants = len(run.verification_results)
    verified_invariants = sum(1 for result in run.verification_results.values() if result)
    
    run.metrics = {
        "total_invariants": total_invariants,
        "verified_invariants": verified_invariants,
        "success_rate": (verified_invariants / total_invariants * 100) if total_invariants > 0 else 100,
        "average_time_per_invariant": run.duration_seconds / total_invariants if total_invariants > 0 else 0,
        "total_failures": len(run.failures)
    }
    
    # Generate maintenance alerts if needed
    if run.status == VerificationStatus.FAILED:
        failed_invariants = [failure.invariant_id for failure in run.failures]
        
        # Group failures by category
        failure_categories = {}
        for inv_id in failed_invariants:
            if inv_id in invariants:
                category = invariants[inv_id].category
                failure_categories[category] = failure_categories.get(category, 0) + 1
        
        # Create alert if manual repair threshold is exceeded
        manual_repair_threshold = pipeline.verification_thresholds.get("manual_repair_threshold", 5)
        if len(run.failures) > manual_repair_threshold:
            alert = MaintenanceAlert(
                pipeline_id=pipeline.id,
                severity="high" if len(run.failures) > manual_repair_threshold * 2 else "medium",
                title=f"Verification failures exceed threshold in {pipeline.name}",
                description=f"{len(run.failures)} invariants failed verification, exceeding the threshold of {manual_repair_threshold}",
                affected_invariants=failed_invariants,
                suggested_actions=[
                    "Review counter-examples for patterns",
                    "Check for recent system changes that could affect these properties",
                    "Prioritize repairs based on invariant priority"
                ]
            )
            
            alerts = _get_maintenance_alerts()
            alerts[alert.id] = alert
            _save_maintenance_alerts(alerts)
    
    # Save the run
    runs = _get_verification_runs()
    runs[run.id] = run
    _save_verification_runs(runs)
    
    return VerificationRunResponse(run=run)

@router.get("/runs/{run_id}", response_model=VerificationRunResponse)
def get_verification_run(run_id: str) -> VerificationRunResponse:
    """Get a verification run by ID"""
    runs = _get_verification_runs()
    if run_id not in runs:
        raise HTTPException(status_code=404, detail=f"Verification run with ID {run_id} not found")
    
    return VerificationRunResponse(run=runs[run_id])

@router.get("/runs", response_model=VerificationRunsListResponse)
def list_verification_runs(
    pipeline_id: Optional[str] = None,
    status: Optional[VerificationStatus] = None,
    limit: int = 100
) -> VerificationRunsListResponse:
    """List verification runs with optional filtering"""
    runs = _get_verification_runs()
    
    filtered_runs = list(runs.values())
    
    # Apply pipeline filter if provided
    if pipeline_id:
        filtered_runs = [r for r in filtered_runs if r.pipeline_id == pipeline_id]
    
    # Apply status filter if provided
    if status:
        filtered_runs = [r for r in filtered_runs if r.status == status]
    
    # Sort by started_at descending (most recent first)
    filtered_runs.sort(key=lambda r: r.started_at.timestamp() if r.started_at else 0, reverse=True)
    
    # Apply limit
    filtered_runs = filtered_runs[:limit]
    
    return VerificationRunsListResponse(runs=filtered_runs)

# --- DASHBOARD ENDPOINTS ---

@router.get("/dashboard/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics() -> DashboardMetricsResponse:
    """Get metrics for the verification dashboard
    
    This endpoint provides aggregated metrics about the verification system,
    including success rates, trends, and alerts.
    """
    invariants = _get_invariants()
    pipelines = _get_pipelines()
    runs = _get_verification_runs()
    alerts = _get_maintenance_alerts()
    
    # Get active alerts
    active_alerts = [alert for alert in alerts.values() if not alert.resolved_at]
    
    # Get recent runs (last 24h)
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    recent_runs = [r for r in runs.values() if r.started_at and r.started_at >= yesterday]
    
    # Calculate success rate
    successful_runs = sum(1 for r in recent_runs if r.status == VerificationStatus.SUCCEEDED)
    success_rate = (successful_runs / len(recent_runs) * 100) if recent_runs else 100
    
    # Calculate average verification time
    verification_times = [r.duration_seconds for r in recent_runs if r.duration_seconds is not None]
    avg_verification_time = sum(verification_times) / len(verification_times) if verification_times else 0
    
    # Count failures by category
    failure_by_category = {}
    for run in recent_runs:
        if run.status == VerificationStatus.FAILED:
            for failure in run.failures:
                if failure.invariant_id in invariants:
                    inv = invariants[failure.invariant_id]
                    failure_by_category[inv.category] = failure_by_category.get(inv.category, 0) + 1
    
    # Calculate category coverage
    all_categories = set(inv.category for inv in invariants.values())
    category_coverage = {}
    
    for category in all_categories:
        category_invariants = [inv for inv in invariants.values() if inv.category == category]
        covered_invariants = []
        
        for pipeline in pipelines.values():
            if not pipeline.enabled:
                continue
            covered_invariants.extend([inv_id for inv_id in pipeline.invariants 
                                      if inv_id in invariants and invariants[inv_id].category == category])
        
        # Remove duplicates
        covered_invariants = set(covered_invariants)
        coverage = (len(covered_invariants) / len(category_invariants) * 100) if category_invariants else 0
        category_coverage[category] = coverage
    
    return DashboardMetricsResponse(
        total_invariants=len(invariants),
        total_pipelines=len(pipelines),
        active_pipelines=sum(1 for p in pipelines.values() if p.enabled),
        verification_runs_last_24h=len(recent_runs),
        success_rate=success_rate,
        average_verification_time=avg_verification_time,
        failure_by_category=failure_by_category,
        maintenance_alerts=active_alerts,
        category_coverage=category_coverage
    )

@router.get("/dashboard/trends", response_model=TrendsResponse)
def get_trends(
    pipeline_id: Optional[str] = None,
    days: int = 30,
    granularity: str = "daily"
) -> TrendsResponse:
    """Get verification trends over time
    
    This endpoint provides time series data for verification metrics,
    allowing visualization of trends.
    """
    if granularity not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Granularity must be one of: daily, weekly, monthly")
    
    runs = _get_verification_runs()
    pipelines = _get_pipelines()
    
    # Filter runs by pipeline if specified
    if pipeline_id:
        if pipeline_id not in pipelines:
            raise HTTPException(status_code=404, detail=f"Pipeline with ID {pipeline_id} not found")
        pipeline_runs = [r for r in runs.values() if r.pipeline_id == pipeline_id]
        pipeline_ids = [pipeline_id]
    else:
        pipeline_runs = list(runs.values())
        pipeline_ids = list(pipelines.keys())
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Prepare trends for each pipeline
    trends = []
    for p_id in pipeline_ids:
        # Skip if no runs for this pipeline
        if not any(r.pipeline_id == p_id for r in pipeline_runs):
            continue
        
        p_runs = [r for r in pipeline_runs if r.pipeline_id == p_id and r.started_at and r.started_at >= start_date]
        if not p_runs:
            continue
        
        # Group data points by time bucket based on granularity
        data_points = []
        
        if granularity == "daily":
            # Group by day
            day_buckets = {}
            for run in p_runs:
                day_key = run.started_at.strftime("%Y-%m-%d")
                if day_key not in day_buckets:
                    day_buckets[day_key] = {"date": day_key, "runs": [], "success_count": 0, "failure_count": 0}
                day_buckets[day_key]["runs"].append(run)
                
                if run.status == VerificationStatus.SUCCEEDED:
                    day_buckets[day_key]["success_count"] += 1
                elif run.status in [VerificationStatus.FAILED, VerificationStatus.ERROR]:
                    day_buckets[day_key]["failure_count"] += 1
            
            # Calculate success rate for each day
            for day_key, bucket in day_buckets.items():
                total = bucket["success_count"] + bucket["failure_count"]
                success_rate = (bucket["success_count"] / total * 100) if total > 0 else 0
                avg_time = sum(r.duration_seconds or 0 for r in bucket["runs"]) / len(bucket["runs"]) if bucket["runs"] else 0
                
                data_points.append({
                    "date": day_key,
                    "success_rate": success_rate,
                    "avg_verification_time": avg_time,
                    "total_runs": len(bucket["runs"]),
                    "failures": bucket["failure_count"]
                })
        
        # Add more granularity options as needed (weekly, monthly)
        
        # Sort data points by date
        data_points.sort(key=lambda dp: dp["date"])
        
        trends.append(VerificationTrend(
            pipeline_id=p_id,
            data_points=data_points,
            trend_start=start_date,
            trend_end=end_date,
            trend_granularity=granularity
        ))
    
    return TrendsResponse(trends=trends)
