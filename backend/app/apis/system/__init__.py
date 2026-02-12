from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import time
from datetime import datetime, timedelta
import json
import re
import databutton as db

router = APIRouter()

# Helper function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Storage keys for system data
HEALTH_STATUS_KEY = "system_health_status"
PERFORMANCE_METRICS_KEY = "system_performance_metrics"
SECURITY_SCANS_KEY = "system_security_scans"
BACKUPS_KEY = "system_backups"
MAINTENANCE_TASKS_KEY = "system_maintenance_tasks"

# Initialize system data if not exists
def initialize_system_data():
    try:
        try:
            db.storage.json.get(HEALTH_STATUS_KEY)
        except Exception:
            # Key not found, create it
            db.storage.json.put(HEALTH_STATUS_KEY, {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "components": {
                    "frontend": {"status": "healthy", "message": "No issues detected"},
                    "backend": {"status": "healthy", "message": "No issues detected"},
                    "database": {"status": "healthy", "message": "No issues detected"},
                    "storage": {"status": "healthy", "message": "No issues detected"},
                    "integrations": {"status": "healthy", "message": "No issues detected"}
                }
            })
        
        try:
            db.storage.json.get(PERFORMANCE_METRICS_KEY)
        except Exception:
            # Key not found, create it
            db.storage.json.put(PERFORMANCE_METRICS_KEY, {
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "response_time": {
                        "avg_ms": 120,
                        "p95_ms": 350,
                        "p99_ms": 500
                    },
                    "memory_usage": {
                        "current_mb": 512,
                        "limit_mb": 2048,
                        "percent": 25
                    },
                    "cpu_usage": {
                        "percent": 15,
                        "trend": "stable"
                    },
                    "database_queries": {
                        "per_second": 10,
                        "avg_time_ms": 35
                    },
                    "error_rate": {
                        "percent": 0.1,
                        "trend": "decreasing"
                    }
                },
                "history": []
            })
        
        try:
            db.storage.json.get(SECURITY_SCANS_KEY)
        except Exception:
            # Key not found, create it
            db.storage.json.put(SECURITY_SCANS_KEY, [])
        
        try:
            db.storage.json.get(BACKUPS_KEY)
        except Exception:
            # Key not found, create it
            db.storage.json.put(BACKUPS_KEY, [])
        
        try:
            db.storage.json.get(MAINTENANCE_TASKS_KEY)
        except Exception:
            # Key not found, create it
            db.storage.json.put(MAINTENANCE_TASKS_KEY, [])
    except Exception as e:
        print(f"Error initializing system data: {e}")

# Models
class HealthResponse(BaseModel):
    timestamp: str
    overall_status: str
    components: Dict[str, Dict[str, str]]

class PerformanceMetrics(BaseModel):
    timestamp: str
    metrics: Dict[str, Any]
    history: List[Dict[str, Any]]

class SecurityScan(BaseModel):
    scan_id: str
    scan_type: str
    timestamp: str
    status: str
    findings: List[Dict[str, Any]]
    risk_score: float
    completed: bool

class SecurityScanRequest(BaseModel):
    scan_type: str

class SecurityScanResult(BaseModel):
    scan_id: str
    message: str

class Backup(BaseModel):
    backup_id: str
    timestamp: str
    type: str
    size_mb: float
    status: str
    location: str

class MaintenanceTask(BaseModel):
    task_id: str
    task_type: str
    timestamp: str
    status: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None

class MaintenanceTaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any]

class MaintenanceTaskResponse(BaseModel):
    task_id: str
    message: str

# Initialize system data
initialize_system_data()

# Endpoints
@router.get("/check-system-health")
async def check_system_health2() -> HealthResponse:
    try:
        # Get current health status
        health_data = db.storage.json.get(HEALTH_STATUS_KEY)
        
        # Update timestamp
        health_data["timestamp"] = datetime.now().isoformat()
        
        # For demo purposes, simulate checking components and update status
        for component in health_data["components"]:
            # In a real system, this would actually check each component
            health_data["components"][component]["status"] = "healthy"
            health_data["components"][component]["message"] = "No issues detected"
        
        # Determine overall status (healthy if all components are healthy)
        all_healthy = all(c["status"] == "healthy" for c in health_data["components"].values())
        health_data["overall_status"] = "healthy" if all_healthy else "degraded"
        
        # Save updated health data
        db.storage.json.put(HEALTH_STATUS_KEY, health_data)
        
        return HealthResponse(**health_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking system health: {str(e)}")

@router.get("/get-performance-metrics")
async def system_get_performance_metrics() -> PerformanceMetrics:
    try:
        # Get current performance metrics
        metrics_data = db.storage.json.get(PERFORMANCE_METRICS_KEY)
        
        # Update timestamp
        current_time = datetime.now().isoformat()
        
        # Archive current metrics to history (keeping last 24 hours)
        if len(metrics_data["history"]) >= 24:  # If we have 24+ entries
            metrics_data["history"] = metrics_data["history"][1:]
        
        # Add current metrics to history
        metrics_data["history"].append({
            "timestamp": metrics_data["timestamp"],
            **metrics_data["metrics"]
        })
        
        # For demo purposes, simulate new performance metrics
        # In a real system, this would actually measure performance
        metrics_data["timestamp"] = current_time
        metrics_data["metrics"]["response_time"]["avg_ms"] = 125
        metrics_data["metrics"]["memory_usage"]["current_mb"] = 550
        metrics_data["metrics"]["memory_usage"]["percent"] = 27
        metrics_data["metrics"]["cpu_usage"]["percent"] = 18
        
        # Save updated metrics data
        db.storage.json.put(PERFORMANCE_METRICS_KEY, metrics_data)
        
        return PerformanceMetrics(**metrics_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")

@router.get("/get-performance-history")
async def get_performance_history() -> Dict[str, Any]:
    try:
        metrics_data = db.storage.json.get(PERFORMANCE_METRICS_KEY)
        return {"history": metrics_data["history"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance history: {str(e)}")

@router.post("/run-security-scan")
async def system_run_security_scan(request: SecurityScanRequest, background_tasks: BackgroundTasks) -> SecurityScanResult:
    try:
        # Validate scan type
        valid_scan_types = ["vulnerability", "dependency", "code", "config", "full"]
        if request.scan_type not in valid_scan_types:
            raise HTTPException(status_code=400, detail=f"Invalid scan type. Must be one of: {', '.join(valid_scan_types)}")
        
        # Get existing scans
        scans = db.storage.json.get(SECURITY_SCANS_KEY)
        
        # Create new scan
        scan_id = f"scan_{int(time.time())}"
        new_scan = {
            "scan_id": scan_id,
            "scan_type": request.scan_type,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "findings": [],
            "risk_score": 0.0,
            "completed": False
        }
        
        # Add scan to list
        scans.append(new_scan)
        db.storage.json.put(SECURITY_SCANS_KEY, scans)
        
        # Run scan in background
        background_tasks.add_task(perform_security_scan, scan_id, request.scan_type)
        
        return SecurityScanResult(scan_id=scan_id, message=f"Security scan initiated: {request.scan_type}")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running security scan: {str(e)}")

@router.get("/get-security-scan-result/{scan_id}")
async def system_get_security_scan_result(scan_id: str) -> SecurityScan:
    try:
        # Get existing scans
        scans = db.storage.json.get(SECURITY_SCANS_KEY)
        
        # Find scan by ID
        scan = next((s for s in scans if s["scan_id"] == scan_id), None)
        if not scan:
            raise HTTPException(status_code=404, detail=f"Security scan not found: {scan_id}")
        
        return SecurityScan(**scan)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting security scan result: {str(e)}")

@router.get("/list-security-scans")
async def system_list_security_scans() -> Dict[str, List[SecurityScan]]:
    try:
        # Get existing scans
        scans = db.storage.json.get(SECURITY_SCANS_KEY)
        
        # Convert to response model
        scan_models = [SecurityScan(**scan) for scan in scans]
        
        return {"scans": scan_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing security scans: {str(e)}")

@router.post("/create-backup")
async def system_create_backup(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    try:
        # Get existing backups
        backups = db.storage.json.get(BACKUPS_KEY)
        
        # Create new backup
        backup_id = f"backup_{int(time.time())}"
        new_backup = {
            "backup_id": backup_id,
            "timestamp": datetime.now().isoformat(),
            "type": "full",
            "size_mb": 0.0,
            "status": "in_progress",
            "location": "cloud-storage"
        }
        
        # Add backup to list
        backups.append(new_backup)
        db.storage.json.put(BACKUPS_KEY, backups)
        
        # Create backup in background
        background_tasks.add_task(perform_backup, backup_id)
        
        return {"backup_id": backup_id, "message": "Backup initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating backup: {str(e)}")

@router.get("/list-backups")
async def list_backups() -> Dict[str, List[Backup]]:
    try:
        # Get existing backups
        backups = db.storage.json.get(BACKUPS_KEY)
        
        # Convert to response model
        backup_models = [Backup(**backup) for backup in backups]
        
        return {"backups": backup_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing backups: {str(e)}")

@router.post("/restore-from-backup/{backup_id}")
async def restore_from_backup(backup_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    try:
        # Get existing backups
        backups = db.storage.json.get(BACKUPS_KEY)
        
        # Find backup by ID
        backup = next((b for b in backups if b["backup_id"] == backup_id), None)
        if not backup:
            raise HTTPException(status_code=404, detail=f"Backup not found: {backup_id}")
        
        # Check backup status
        if backup["status"] != "completed":
            raise HTTPException(status_code=400, detail=f"Backup is not completed: {backup_id}")
        
        # In a real system, this would restore from the backup
        # For demo purposes, just simulate a restore operation
        
        return {"message": f"Restore from backup {backup_id} initiated"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restoring from backup: {str(e)}")

@router.get("/list-maintenance-tasks")
async def list_maintenance_tasks() -> Dict[str, List[MaintenanceTask]]:
    try:
        # Get existing tasks
        tasks = db.storage.json.get(MAINTENANCE_TASKS_KEY)
        
        # Convert to response model
        task_models = [MaintenanceTask(**task) for task in tasks]
        
        return {"tasks": task_models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing maintenance tasks: {str(e)}")

@router.post("/run-maintenance-task")
async def system_run_maintenance_task(request: MaintenanceTaskRequest, background_tasks: BackgroundTasks) -> MaintenanceTaskResponse:
    try:
        # Validate task type
        valid_task_types = ["db_optimize", "db_cleanup", "cache_clear", "logs_rotate", "index_rebuild", "storage_cleanup"]
        if request.task_type not in valid_task_types:
            raise HTTPException(status_code=400, detail=f"Invalid task type. Must be one of: {', '.join(valid_task_types)}")
        
        # Get existing tasks
        tasks = db.storage.json.get(MAINTENANCE_TASKS_KEY)
        
        # Create new task
        task_id = f"task_{int(time.time())}"
        new_task = {
            "task_id": task_id,
            "task_type": request.task_type,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "parameters": request.parameters,
            "result": None
        }
        
        # Add task to list
        tasks.append(new_task)
        db.storage.json.put(MAINTENANCE_TASKS_KEY, tasks)
        
        # Run task in background
        background_tasks.add_task(perform_maintenance_task, task_id, request.task_type, request.parameters)
        
        return MaintenanceTaskResponse(task_id=task_id, message=f"Maintenance task initiated: {request.task_type}")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running maintenance task: {str(e)}")

@router.get("/get-maintenance-task/{task_id}")
async def get_maintenance_task(task_id: str) -> MaintenanceTask:
    try:
        # Get existing tasks
        tasks = db.storage.json.get(MAINTENANCE_TASKS_KEY)
        
        # Find task by ID
        task = next((t for t in tasks if t["task_id"] == task_id), None)
        if not task:
            raise HTTPException(status_code=404, detail=f"Maintenance task not found: {task_id}")
        
        return MaintenanceTask(**task)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting maintenance task: {str(e)}")

# Background tasks implementation
async def perform_security_scan(scan_id: str, scan_type: str):
    try:
        # Get existing scans
        scans = db.storage.json.get(SECURITY_SCANS_KEY)
        
        # Find scan by ID
        scan_index = next((i for i, s in enumerate(scans) if s["scan_id"] == scan_id), None)
        if scan_index is None:
            return
        
        # In a real system, this would perform a security scan
        # For demo purposes, simulate a scan with different findings based on scan type
        time.sleep(2)  # Simulate scan taking time
        
        findings = []
        risk_score = 0.0
        
        if scan_type == "vulnerability":
            findings = [
                {"severity": "medium", "component": "third-party-library", "description": "Outdated package with known vulnerability", "remediation": "Update to latest version"},
                {"severity": "low", "component": "api-endpoint", "description": "Missing rate limiting", "remediation": "Implement rate limiting"}
            ]
            risk_score = 25.0
        elif scan_type == "dependency":
            findings = [
                {"severity": "low", "component": "npm-packages", "description": "Multiple outdated dependencies", "remediation": "Run npm update"},
                {"severity": "info", "component": "python-packages", "description": "Unused dependencies", "remediation": "Remove unused packages"}
            ]
            risk_score = 15.0
        elif scan_type == "code":
            findings = [
                {"severity": "medium", "component": "authentication", "description": "Weak password policy", "remediation": "Strengthen password requirements"},
                {"severity": "low", "component": "data-validation", "description": "Insufficient input validation", "remediation": "Implement comprehensive validation"}
            ]
            risk_score = 30.0
        elif scan_type == "config":
            findings = [
                {"severity": "high", "component": "server-config", "description": "Insecure default settings", "remediation": "Update configuration based on security best practices"},
                {"severity": "medium", "component": "permissions", "description": "Overly permissive access", "remediation": "Implement principle of least privilege"}
            ]
            risk_score = 40.0
        elif scan_type == "full":
            findings = [
                {"severity": "critical", "component": "authentication", "description": "Session fixation vulnerability", "remediation": "Regenerate session IDs after login"},
                {"severity": "high", "component": "database", "description": "SQL injection risk", "remediation": "Use parameterized queries"},
                {"severity": "medium", "component": "api-endpoints", "description": "Missing input validation", "remediation": "Implement comprehensive validation"},
                {"severity": "low", "component": "logging", "description": "Insufficient error logging", "remediation": "Enhance logging for security events"}
            ]
            risk_score = 65.0
        
        # Update scan result
        scans[scan_index]["status"] = "completed"
        scans[scan_index]["findings"] = findings
        scans[scan_index]["risk_score"] = risk_score
        scans[scan_index]["completed"] = True
        
        # Save updated scans
        db.storage.json.put(SECURITY_SCANS_KEY, scans)
    except Exception as e:
        print(f"Error performing security scan: {e}")
        # Try to update scan status to failed
        try:
            scans = db.storage.json.get(SECURITY_SCANS_KEY)
            scan_index = next((i for i, s in enumerate(scans) if s["scan_id"] == scan_id), None)
            if scan_index is not None:
                scans[scan_index]["status"] = "failed"
                scans[scan_index]["completed"] = True
                db.storage.json.put(SECURITY_SCANS_KEY, scans)
        except:
            pass

async def perform_backup(backup_id: str):
    try:
        # Get existing backups
        backups = db.storage.json.get(BACKUPS_KEY)
        
        # Find backup by ID
        backup_index = next((i for i, b in enumerate(backups) if b["backup_id"] == backup_id), None)
        if backup_index is None:
            return
        
        # In a real system, this would perform a backup
        # For demo purposes, simulate a backup process
        time.sleep(3)  # Simulate backup taking time
        
        # Update backup result
        backups[backup_index]["status"] = "completed"
        backups[backup_index]["size_mb"] = 256.5  # Simulated backup size
        
        # Save updated backups
        db.storage.json.put(BACKUPS_KEY, backups)
    except Exception as e:
        print(f"Error performing backup: {e}")
        # Try to update backup status to failed
        try:
            backups = db.storage.json.get(BACKUPS_KEY)
            backup_index = next((i for i, b in enumerate(backups) if b["backup_id"] == backup_id), None)
            if backup_index is not None:
                backups[backup_index]["status"] = "failed"
                db.storage.json.put(BACKUPS_KEY, backups)
        except:
            pass

async def perform_maintenance_task(task_id: str, task_type: str, parameters: Dict[str, Any]):
    try:
        # Get existing tasks
        tasks = db.storage.json.get(MAINTENANCE_TASKS_KEY)
        
        # Find task by ID
        task_index = next((i for i, t in enumerate(tasks) if t["task_id"] == task_id), None)
        if task_index is None:
            return
        
        # In a real system, this would perform the actual maintenance task
        # For demo purposes, simulate different maintenance tasks
        time.sleep(2)  # Simulate task taking time
        
        result = {}
        
        if task_type == "db_optimize":
            result = {
                "tables_optimized": 15,
                "space_reclaimed_mb": 45.2,
                "query_performance_improvement": "25%"
            }
        elif task_type == "db_cleanup":
            result = {
                "deleted_records": 1250,
                "tables_affected": 8,
                "space_reclaimed_mb": 78.5
            }
        elif task_type == "cache_clear":
            result = {
                "cache_entries_cleared": 1856,
                "memory_freed_mb": 128.7
            }
        elif task_type == "logs_rotate":
            result = {
                "log_files_rotated": 12,
                "oldest_log": "2025-03-28",
                "space_reclaimed_mb": 256.3
            }
        elif task_type == "index_rebuild":
            result = {
                "indexes_rebuilt": 24,
                "query_performance_improvement": "18%"
            }
        elif task_type == "storage_cleanup":
            result = {
                "files_deleted": 145,
                "space_reclaimed_mb": 512.8
            }
        
        # Update task result
        tasks[task_index]["status"] = "completed"
        tasks[task_index]["result"] = result
        
        # Save updated tasks
        db.storage.json.put(MAINTENANCE_TASKS_KEY, tasks)
    except Exception as e:
        print(f"Error performing maintenance task: {e}")
        # Try to update task status to failed
        try:
            tasks = db.storage.json.get(MAINTENANCE_TASKS_KEY)
            task_index = next((i for i, t in enumerate(tasks) if t["task_id"] == task_id), None)
            if task_index is not None:
                tasks[task_index]["status"] = "failed"
                db.storage.json.put(MAINTENANCE_TASKS_KEY, tasks)
        except:
            pass
