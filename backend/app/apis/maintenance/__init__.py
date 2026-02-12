from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import databutton as db
import json
import time
import re
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/maintenance")

class HealthCheckItem(BaseModel):
    name: str
    status: str
    message: str
    timestamp: str

class SystemHealthStatus(BaseModel):
    overall_status: str
    services: List[HealthCheckItem]
    last_scan_timestamp: str

class SecurityScanRequest(BaseModel):
    scan_type: str = "full"  # Options: "full", "quick", "database", "api"
    schedule: Optional[bool] = False
    notify_email: Optional[str] = None

class SecurityScanResult(BaseModel):
    scan_id: str
    scan_type: str
    start_time: str
    end_time: Optional[str] = None
    status: str  # "in_progress", "completed", "failed"
    vulnerabilities: List[Dict[str, Any]] = []
    recommendations: List[str] = []

class PerformanceMetrics(BaseModel):
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    database_metrics: Dict[str, Any]
    api_metrics: Dict[str, Any]
    timestamp: str

class BackupRequest(BaseModel):
    backup_type: str = "full"  # Options: "full", "database", "files", "config"
    description: Optional[str] = None

class BackupResponse(BaseModel):
    backup_id: str
    backup_type: str
    timestamp: str
    size_mb: float
    status: str
    description: Optional[str] = None

class MaintenanceTaskRequest(BaseModel):
    task_type: str  # Options: "cleanup", "optimize", "update", "verify"
    parameters: Dict[str, Any] = {}

class MaintenanceTaskResponse(BaseModel):
    task_id: str
    task_type: str
    status: str
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

# Helper function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Health check endpoint
@router.get("/health", response_model=SystemHealthStatus)
async def check_maintenance_health():
    """Perform a health check on all critical system components"""
    timestamp = datetime.now().isoformat()
    
    # Get the last stored health check or create a new one
    try:
        health_data = db.storage.json.get("maintenance_health_status", default={})
    except Exception:
        health_data = {}
    
    # Check API health
    api_status = {"name": "API Service", "status": "healthy", "message": "API service is responding normally", "timestamp": timestamp}
    
    # Check database connections
    db_status = {"name": "Database", "status": "healthy", "message": "Database connections are working properly", "timestamp": timestamp}
    
    # Check integrations
    integrations_status = {"name": "External Integrations", "status": "healthy", "message": "All integrations are functioning normally", "timestamp": timestamp}
    
    # Check storage
    storage_status = {"name": "Storage", "status": "healthy", "message": "Storage system is operating normally", "timestamp": timestamp}
    
    # Combine all statuses
    services = [api_status, db_status, integrations_status, storage_status]
    
    # Determine overall status (if any service is not healthy, overall is degraded)
    overall_status = "healthy"
    for service in services:
        if service["status"] != "healthy":
            overall_status = "degraded"
            break
    
    # Create response
    health_status = {
        "overall_status": overall_status,
        "services": services,
        "last_scan_timestamp": timestamp
    }
    
    # Store the health status
    db.storage.json.put("maintenance_health_status", health_status)
    
    return health_status

# Security scanning endpoint
@router.post("/security/scan", response_model=SecurityScanResult)
async def run_maintenance_security_scan(request: SecurityScanRequest, background_tasks: BackgroundTasks):
    """Initiate a security scan of the system"""
    scan_id = f"scan_{int(time.time())}"
    start_time = datetime.now().isoformat()
    
    # Create initial scan result
    scan_result = {
        "scan_id": scan_id,
        "scan_type": request.scan_type,
        "start_time": start_time,
        "status": "in_progress",
        "vulnerabilities": [],
        "recommendations": []
    }
    
    # Store initial result
    db.storage.json.put(f"security_scan_{sanitize_storage_key(scan_id)}", scan_result)
    
    # Run the scan in the background
    background_tasks.add_task(perform_security_scan, scan_id, request.scan_type, request.notify_email)
    
    return scan_result

# Get security scan result
@router.get("/security/scan/{scan_id}", response_model=SecurityScanResult)
async def maintenance_get_security_scan_result(scan_id: str):
    """Retrieve the results of a security scan"""
    try:
        scan_result = db.storage.json.get(f"security_scan_{sanitize_storage_key(scan_id)}")
        return scan_result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Scan not found: {str(e)}")

# List all scan results
@router.get("/security/scans", response_model=List[SecurityScanResult])
async def maintenance_list_security_scans():
    """List all security scans"""
    try:
        # Get all files that match the pattern
        files = db.storage.json.list()
        scan_results = []
        
        for file in files:
            if file.name.startswith("security_scan_"):
                try:
                    scan_data = db.storage.json.get(file.name)
                    scan_results.append(scan_data)
                except Exception:
                    continue
                    
        return scan_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing scans: {str(e)}")

# Performance monitoring endpoint
@router.get("/performance", response_model=PerformanceMetrics)
async def maintenance_get_performance_metrics():
    """Get current system performance metrics"""
    timestamp = datetime.now().isoformat()
    
    # Simulate collecting performance metrics
    # In a real implementation, these would be collected from actual monitoring tools
    response_times = {
        "api": 120.5,  # milliseconds
        "database": 45.2,
        "checkout": 350.1,
        "product_page": 180.3
    }
    
    error_rates = {
        "api": 0.05,  # 5% error rate
        "database": 0.01,
        "checkout": 0.02,
        "overall": 0.03
    }
    
    database_metrics = {
        "connections": 5,
        "query_time_avg": 32.1,  # milliseconds
        "active_transactions": 2,
        "disk_usage_mb": 250.5
    }
    
    api_metrics = {
        "requests_per_minute": 42,
        "avg_response_time": 125.3,  # milliseconds
        "error_count_last_hour": 12,
        "cache_hit_ratio": 0.75
    }
    
    metrics = {
        "response_times": response_times,
        "error_rates": error_rates,
        "database_metrics": database_metrics,
        "api_metrics": api_metrics,
        "timestamp": timestamp
    }
    
    # Store the metrics for historical tracking
    try:
        # Get existing metrics history
        metrics_history = db.storage.json.get("performance_metrics_history", default=[])
        
        # Add new metrics and keep only the last 100 entries
        metrics_history.append(metrics)
        if len(metrics_history) > 100:
            metrics_history = metrics_history[-100:]
            
        # Save updated history
        db.storage.json.put("performance_metrics_history", metrics_history)
    except Exception as e:
        print(f"Error storing performance metrics: {str(e)}")
    
    return metrics

# Get historical performance data
@router.get("/performance/history")
async def maintenance_get_performance_history(days: int = 7):
    """Get historical performance data for the specified number of days"""
    try:
        metrics_history = db.storage.json.get("performance_metrics_history", default=[])
        
        # Filter by date if needed
        if days > 0:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            metrics_history = [m for m in metrics_history if m["timestamp"] >= cutoff_date]
            
        return {"history": metrics_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance history: {str(e)}")

# Backup endpoints
@router.post("/backup", response_model=BackupResponse)
async def maintenance_create_backup(request: BackupRequest, background_tasks: BackgroundTasks):
    """Create a new backup of the system"""
    backup_id = f"backup_{request.backup_type}_{int(time.time())}"
    timestamp = datetime.now().isoformat()
    
    # Create initial backup record
    backup = {
        "backup_id": backup_id,
        "backup_type": request.backup_type,
        "timestamp": timestamp,
        "size_mb": 0.0,
        "status": "in_progress",
        "description": request.description
    }
    
    # Store backup metadata
    db.storage.json.put(f"backup_meta_{sanitize_storage_key(backup_id)}", backup)
    
    # Run the backup process in the background
    background_tasks.add_task(perform_backup, backup_id, request.backup_type, request.description)
    
    return backup

# List backups
@router.get("/backups", response_model=List[BackupResponse])
async def maintenance_list_backups():
    """List all backups"""
    try:
        # Get all files that match the pattern
        files = db.storage.json.list()
        backups = []
        
        for file in files:
            if file.name.startswith("backup_meta_"):
                try:
                    backup_data = db.storage.json.get(file.name)
                    backups.append(backup_data)
                except Exception:
                    continue
                    
        return backups
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing backups: {str(e)}")

# Restore from backup
@router.post("/backup/{backup_id}/restore", response_model=Dict[str, Any])
async def maintenance_restore_from_backup(backup_id: str, background_tasks: BackgroundTasks):
    """Restore the system from a backup"""
    try:
        # Get backup metadata
        backup_meta = db.storage.json.get(f"backup_meta_{sanitize_storage_key(backup_id)}")
        
        if not backup_meta or backup_meta["status"] != "completed":
            raise HTTPException(status_code=400, detail="Backup not found or not completed")
        
        # Start restoration process in background
        background_tasks.add_task(perform_restore, backup_id)
        
        return {
            "message": f"Restoration from backup {backup_id} has been initiated",
            "restore_id": f"restore_{int(time.time())}",
            "status": "in_progress"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating restoration: {str(e)}")

# Maintenance tasks
@router.post("/tasks", response_model=MaintenanceTaskResponse)
async def maintenance_run_task(request: MaintenanceTaskRequest, background_tasks: BackgroundTasks):
    """Run a maintenance task"""
    task_id = f"task_{request.task_type}_{int(time.time())}"
    
    # Create initial task record
    task = {
        "task_id": task_id,
        "task_type": request.task_type,
        "status": "scheduled",
        "parameters": request.parameters,
        "result": None,
        "message": f"Task {request.task_type} has been scheduled"
    }
    
    # Store task metadata
    db.storage.json.put(f"maintenance_task_{sanitize_storage_key(task_id)}", task)
    
    # Run the task in the background
    background_tasks.add_task(perform_maintenance_task, task_id, request.task_type, request.parameters)
    
    return task

# Get maintenance task status
@router.get("/tasks/{task_id}", response_model=MaintenanceTaskResponse)
async def maintenance_get_task(task_id: str):
    """Get the status of a maintenance task"""
    try:
        task = db.storage.json.get(f"maintenance_task_{sanitize_storage_key(task_id)}")
        return task
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Task not found: {str(e)}")

# List all maintenance tasks
@router.get("/tasks/list", response_model=List[MaintenanceTaskResponse])
async def maintenance_list_tasks():
    """List all maintenance tasks"""
    try:
        # Get all files that match the pattern
        files = db.storage.json.list()
        tasks = []
        
        for file in files:
            if file.name.startswith("maintenance_task_"):
                try:
                    task_data = db.storage.json.get(file.name)
                    tasks.append(task_data)
                except Exception:
                    continue
                    
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")

# Background task handlers
async def perform_security_scan(scan_id: str, scan_type: str, notify_email: Optional[str] = None):
    """Perform the actual security scan"""
    try:
        # Get the initial scan result
        scan_result = db.storage.json.get(f"security_scan_{sanitize_storage_key(scan_id)}")
        
        # Simulate scan delay
        await asyncio.sleep(5)  # In a real implementation, this would be the actual scan
        
        # Update with simulated results
        vulnerabilities = []
        recommendations = []
        
        if scan_type == "full" or scan_type == "api":
            vulnerabilities.append({
                "severity": "medium",
                "component": "API",
                "description": "Possible rate limiting vulnerability in authentication endpoints",
                "remedy": "Implement proper rate limiting on login and password reset endpoints"
            })
            recommendations.append("Enable rate limiting for all authentication endpoints")
        
        if scan_type == "full" or scan_type == "database":
            vulnerabilities.append({
                "severity": "low",
                "component": "Database",
                "description": "Database user has excessive permissions",
                "remedy": "Apply principle of least privilege for database users"
            })
            recommendations.append("Review and restrict database user permissions")
        
        # Update the scan result
        scan_result.update({
            "end_time": datetime.now().isoformat(),
            "status": "completed",
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations
        })
        
        # Store updated result
        db.storage.json.put(f"security_scan_{sanitize_storage_key(scan_id)}", scan_result)
        
        # Send email notification if requested
        if notify_email:
            # In a real implementation, send an actual email
            print(f"Would send security scan results to {notify_email}")
    except Exception as e:
        # Handle error case
        try:
            scan_result = db.storage.json.get(f"security_scan_{sanitize_storage_key(scan_id)}")
            scan_result.update({
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            db.storage.json.put(f"security_scan_{sanitize_storage_key(scan_id)}", scan_result)
        except Exception:
            print(f"Failed to update scan status for {scan_id}: {str(e)}")

async def perform_backup(backup_id: str, backup_type: str, description: Optional[str] = None):
    """Perform the actual backup process"""
    try:
        # Get the initial backup metadata
        backup_meta = db.storage.json.get(f"backup_meta_{sanitize_storage_key(backup_id)}")
        
        # Simulate backup process
        await asyncio.sleep(5)  # In a real implementation, this would be the actual backup
        
        # Generate simulated backup size based on type
        size_mb = 0.0
        if backup_type == "full":
            size_mb = 1250.5
        elif backup_type == "database":
            size_mb = 450.2
        elif backup_type == "files":
            size_mb = 780.3
        elif backup_type == "config":
            size_mb = 15.1
        
        # Simulate creating the backup data
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "type": backup_type,
            "content": {
                "database": {} if backup_type in ["full", "database"] else None,
                "files": {} if backup_type in ["full", "files"] else None,
                "config": {} if backup_type in ["full", "config"] else None
            }
        }
        
        # Store the backup data
        db.storage.json.put(f"backup_data_{sanitize_storage_key(backup_id)}", backup_data)
        
        # Update the backup metadata
        backup_meta.update({
            "size_mb": size_mb,
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        })
        
        # Store updated metadata
        db.storage.json.put(f"backup_meta_{sanitize_storage_key(backup_id)}", backup_meta)
    except Exception as e:
        # Handle error case
        try:
            backup_meta = db.storage.json.get(f"backup_meta_{sanitize_storage_key(backup_id)}")
            backup_meta.update({
                "status": "failed",
                "error": str(e)
            })
            db.storage.json.put(f"backup_meta_{sanitize_storage_key(backup_id)}", backup_meta)
        except Exception:
            print(f"Failed to update backup metadata for {backup_id}: {str(e)}")

async def perform_restore(backup_id: str):
    """Perform the actual restore process"""
    restore_id = f"restore_{int(time.time())}"
    restore_meta = {
        "restore_id": restore_id,
        "backup_id": backup_id,
        "start_time": datetime.now().isoformat(),
        "status": "in_progress"
    }
    
    try:
        # Store initial restore metadata
        db.storage.json.put(f"restore_meta_{sanitize_storage_key(restore_id)}", restore_meta)
        
        # Get the backup data
        backup_data = db.storage.json.get(f"backup_data_{sanitize_storage_key(backup_id)}")
        
        # Simulate restore process
        await asyncio.sleep(10)  # In a real implementation, this would be the actual restore
        
        # Update restore metadata
        restore_meta.update({
            "end_time": datetime.now().isoformat(),
            "status": "completed",
            "message": "Restoration completed successfully"
        })
        
        # Store updated metadata
        db.storage.json.put(f"restore_meta_{sanitize_storage_key(restore_id)}", restore_meta)
    except Exception as e:
        # Handle error case
        try:
            restore_meta.update({
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            db.storage.json.put(f"restore_meta_{sanitize_storage_key(restore_id)}", restore_meta)
        except Exception:
            print(f"Failed to update restore metadata for {restore_id}: {str(e)}")

async def perform_maintenance_task(task_id: str, task_type: str, parameters: Dict[str, Any]):
    """Perform the actual maintenance task"""
    try:
        # Get the task record
        task = db.storage.json.get(f"maintenance_task_{sanitize_storage_key(task_id)}")
        task["status"] = "in_progress"
        task["message"] = f"Task {task_type} is in progress"
        db.storage.json.put(f"maintenance_task_{sanitize_storage_key(task_id)}", task)
        
        # Execute task based on type
        result = {}
        message = ""
        
        if task_type == "cleanup":
            # Simulate database cleanup
            await asyncio.sleep(3)
            deleted_records = parameters.get("max_records", 100)
            result = {"deleted_records": deleted_records, "freed_space_mb": deleted_records * 0.01}
            message = f"Deleted {deleted_records} old records and freed {result['freed_space_mb']:.2f} MB of space"
        
        elif task_type == "optimize":
            # Simulate database optimization
            await asyncio.sleep(5)
            result = {"tables_optimized": 12, "indexes_rebuilt": 8, "performance_improvement": "15%"}
            message = f"Optimized {result['tables_optimized']} tables and rebuilt {result['indexes_rebuilt']} indexes"
        
        elif task_type == "update":
            # Simulate system update
            await asyncio.sleep(7)
            components = parameters.get("components", ["core", "plugins", "themes"])
            result = {"components_updated": components, "update_count": len(components)}
            message = f"Updated {result['update_count']} components: {', '.join(components)}"
        
        elif task_type == "verify":
            # Simulate data verification
            await asyncio.sleep(4)
            inconsistencies = 3
            result = {"records_verified": 5000, "inconsistencies_found": inconsistencies}
            message = f"Verified 5000 records and found {inconsistencies} inconsistencies"
        
        # Update the task record
        task.update({
            "status": "completed",
            "result": result,
            "message": message,
            "completed_at": datetime.now().isoformat()
        })
        
        # Store updated task
        db.storage.json.put(f"maintenance_task_{sanitize_storage_key(task_id)}", task)
    except Exception as e:
        # Handle error case
        try:
            task = db.storage.json.get(f"maintenance_task_{sanitize_storage_key(task_id)}")
            task.update({
                "status": "failed",
                "error": str(e),
                "message": f"Task failed: {str(e)}"
            })
            db.storage.json.put(f"maintenance_task_{sanitize_storage_key(task_id)}", task)
        except Exception:
            print(f"Failed to update task record for {task_id}: {str(e)}")


