from fastapi import APIRouter, HTTPException
import json
from pydantic import BaseModel
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import random

router = APIRouter()

# Define enum types for statuses
class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    CHECKING = "checking"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskType(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    DATABASE = "database"
    BACKUP = "backup"
    UPDATES = "updates"

# Define models for requests and responses
class SystemHealthResponse(BaseModel):
    security_status: HealthStatus
    performance_status: HealthStatus
    database_status: HealthStatus
    backup_status: HealthStatus
    updates_status: HealthStatus
    checked_at: str
    issues_found: int

class SecurityScanRequest(BaseModel):
    scan_type: str
    parameters: Optional[Dict] = None

class SecurityScanResponse(BaseModel):
    scan_id: str
    scan_type: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    issues_found: Optional[int] = None
    severity_breakdown: Optional[Dict[str, int]] = None

class MaintenanceTask(BaseModel):
    id: str
    name: str
    description: str
    type: TaskType
    status: TaskStatus
    last_run: Optional[str] = None
    duration: Optional[str] = None

class MaintenanceTaskListResponse(BaseModel):
    tasks: List[MaintenanceTask]

class PerformanceMetricsResponse(BaseModel):
    response_time_avg: float  # in ms
    error_rate: float  # percentage
    resource_utilization: Dict[str, float]  # CPU, memory, etc. in percentage
    db_query_time_avg: float  # in ms
    api_requests_per_minute: float
    measured_at: str

class BackupInfoResponse(BaseModel):
    last_backup_time: str
    backup_status: str
    backup_size: str
    backup_location: str
    next_scheduled_backup: str

# Helper function to generate random task data (for demo purposes)
def generate_random_tasks(count: int = 5) -> List[MaintenanceTask]:
    tasks = [
        MaintenanceTask(
            id=f"task-{i+1}",
            name=[
                "Database Optimization",
                "Security Vulnerability Scan",
                "System Backup",
                "Cache Cleanup",
                "Security Patch Deployment",
                "Log Rotation",
                "Data Integrity Check",
                "Network Configuration Audit",
                "SSL Certificate Renewal",
                "User Permission Audit"
            ][i % 10],
            description=[
                "Optimize database indexes and query performance",
                "Scan for security vulnerabilities in all system components",
                "Create a full system backup",
                "Clear system caches to improve performance",
                "Deploy latest security patches to all components",
                "Rotate and archive system logs",
                "Verify data integrity across all storage systems",
                "Audit network configuration for security and performance",
                "Check and renew SSL certificates if needed",
                "Audit user permissions and access controls"
            ][i % 10],
            type=[
                TaskType.DATABASE,
                TaskType.SECURITY,
                TaskType.BACKUP,
                TaskType.PERFORMANCE,
                TaskType.UPDATES,
                TaskType.PERFORMANCE,
                TaskType.DATABASE,
                TaskType.SECURITY,
                TaskType.SECURITY,
                TaskType.SECURITY
            ][i % 10],
            status=random.choice(list(TaskStatus)),
            last_run=datetime.now().strftime("%Y-%m-%d %H:%M:%S") if random.random() > 0.5 else None,
            duration=f"{random.randint(1, 60)} minutes" if random.random() > 0.5 else None
        )
        for i in range(count)
    ]
    return tasks

# Endpoints
@router.get("/system/health")
def get_system_health() -> SystemHealthResponse:
    """Get the current health status of all system components"""
    # In a real implementation, this would check actual system components
    # For demo purposes, we'll return random statuses
    statuses = [HealthStatus.HEALTHY, HealthStatus.WARNING, HealthStatus.CRITICAL]
    weights = [0.7, 0.2, 0.1]  # More likely to be healthy than critical
    
    security_status = random.choices(statuses, weights=weights)[0]
    performance_status = random.choices(statuses, weights=weights)[0]
    database_status = random.choices(statuses, weights=weights)[0]
    backup_status = random.choices(statuses, weights=weights)[0]
    updates_status = random.choices(statuses, weights=weights)[0]
    
    issues_found = sum([status != HealthStatus.HEALTHY for status in 
                        [security_status, performance_status, database_status, backup_status, updates_status]])
    
    return SystemHealthResponse(
        security_status=security_status,
        performance_status=performance_status,
        database_status=database_status,
        backup_status=backup_status,
        updates_status=updates_status,
        checked_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        issues_found=issues_found
    )

@router.post("/security/scan")
def system_maintenance_run_security_scan(request: SecurityScanRequest) -> SecurityScanResponse:
    """Run a security scan of the specified type"""
    # In a real implementation, this would initiate an actual security scan
    scan_id = f"scan-{random.randint(1000, 9999)}"
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # For demo purposes, generate random results
    issues_found = random.randint(0, 10)
    severity_breakdown = {
        "critical": random.randint(0, 2),
        "high": random.randint(0, 3),
        "medium": random.randint(0, 5),
        "low": random.randint(0, 5)
    }
    
    return SecurityScanResponse(
        scan_id=scan_id,
        scan_type=request.scan_type,
        status="completed",
        started_at=started_at,
        completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        issues_found=issues_found,
        severity_breakdown=severity_breakdown
    )

@router.get("/security/scan/{scan_id}")
def system_maintenance_get_security_scan_result(scan_id: str) -> SecurityScanResponse:
    """Get the results of a previously run security scan"""
    # In a real implementation, this would fetch results from a database
    if random.random() < 0.1:  # 10% chance of not finding the scan
        raise HTTPException(status_code=404, detail=f"Security scan with ID {scan_id} not found")
    
    # For demo purposes, generate random results
    issues_found = random.randint(0, 10)
    severity_breakdown = {
        "critical": random.randint(0, 2),
        "high": random.randint(0, 3),
        "medium": random.randint(0, 5),
        "low": random.randint(0, 5)
    }
    
    scan_types = ["Full System", "Quick", "Vulnerability", "Database", "API"]
    
    return SecurityScanResponse(
        scan_id=scan_id,
        scan_type=random.choice(scan_types),
        status="completed",
        started_at=(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        issues_found=issues_found,
        severity_breakdown=severity_breakdown
    )

@router.get("/security/scans")
def system_maintenance_list_security_scans() -> List[SecurityScanResponse]:
    """List all security scans that have been run"""
    # In a real implementation, this would fetch from a database
    # For demo purposes, generate random data
    scan_types = ["Full System", "Quick", "Vulnerability", "Database", "API"]
    scans = []
    
    for i in range(random.randint(3, 8)):
        scan_type = random.choice(scan_types)
        started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if random.random() > 0.2 else None
        
        issues_found = random.randint(0, 10) if completed_at else None
        severity_breakdown = None
        if completed_at and issues_found:
            severity_breakdown = {
                "critical": random.randint(0, 2),
                "high": random.randint(0, 3),
                "medium": random.randint(0, 5),
                "low": random.randint(0, 5)
            }
        
        scans.append(SecurityScanResponse(
            scan_id=f"scan-{1000 + i}",
            scan_type=scan_type,
            status="completed" if completed_at else "in-progress",
            started_at=started_at,
            completed_at=completed_at,
            issues_found=issues_found,
            severity_breakdown=severity_breakdown
        ))
    
    return scans

@router.get("/maintenance/tasks")
def system_maintenance_get_tasks() -> MaintenanceTaskListResponse:
    """Get a list of all maintenance tasks"""
    # In a real implementation, this would fetch from a database
    # For demo purposes, generate random data
    tasks = generate_random_tasks(random.randint(5, 10))
    return MaintenanceTaskListResponse(tasks=tasks)

@router.post("/maintenance/tasks/{task_id}/run")
def system_maintenance_run_task(task_id: str) -> MaintenanceTask:
    """Run a specific maintenance task"""
    # In a real implementation, this would initiate the actual task
    # For demo purposes, return a task with updated status
    if random.random() < 0.1:  # 10% chance of not finding the task
        raise HTTPException(status_code=404, detail=f"Maintenance task with ID {task_id} not found")
    
    task_types = list(TaskType)
    
    return MaintenanceTask(
        id=task_id,
        name="Task Run Example",
        description="This task was run via the API",
        type=random.choice(task_types),
        status=TaskStatus.COMPLETED if random.random() > 0.2 else TaskStatus.FAILED,
        last_run=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        duration=f"{random.randint(1, 60)} minutes"
    )

@router.get("/performance/metrics")
def system_maintenance_get_performance_metrics() -> PerformanceMetricsResponse:
    """Get current system performance metrics"""
    # In a real implementation, this would fetch actual performance metrics
    # For demo purposes, generate random data
    return PerformanceMetricsResponse(
        response_time_avg=random.uniform(50, 500),  # ms
        error_rate=random.uniform(0, 2),  # %
        resource_utilization={
            "cpu": random.uniform(10, 90),  # %
            "memory": random.uniform(20, 80),  # %
            "disk": random.uniform(30, 70),  # %
            "network": random.uniform(5, 60)  # %
        },
        db_query_time_avg=random.uniform(10, 200),  # ms
        api_requests_per_minute=random.uniform(10, 1000),
        measured_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@router.get("/backup/info")
def get_backup_info() -> BackupInfoResponse:
    """Get information about the latest system backup"""
    # In a real implementation, this would fetch actual backup information
    # For demo purposes, generate random data
    return BackupInfoResponse(
        last_backup_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        backup_status=random.choice(["successful", "failed", "in-progress"]),
        backup_size=f"{random.randint(1, 50)} GB",
        backup_location=random.choice(["Local Storage", "Cloud Storage", "Off-site Backup"]),
        next_scheduled_backup=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@router.post("/backup/create")
def system_maintenance_create_backup() -> BackupInfoResponse:
    """Create a new system backup"""
    # In a real implementation, this would initiate an actual backup
    # For demo purposes, return random data
    return BackupInfoResponse(
        last_backup_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        backup_status=random.choice(["successful", "in-progress"]),
        backup_size=f"{random.randint(1, 50)} GB",
        backup_location=random.choice(["Local Storage", "Cloud Storage", "Off-site Backup"]),
        next_scheduled_backup=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
