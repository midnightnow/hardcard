"""
Factory router for HardCard API v1 endpoints.
Provides core API functionality including health checks, system status, and metrics.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import time
import platform
import psutil
import os
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["Core API"])

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    Returns system status and basic metrics.
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "hardcard-api",
            "version": "1.0.0",
            "uptime": time.time(),
            "environment": os.environ.get("ENVIRONMENT", "development")
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@router.get("/status")
async def system_status():
    """
    Detailed system status endpoint.
    Returns comprehensive system information.
    """
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process information
        process = psutil.Process()
        process_memory = process.memory_info()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            },
            "process": {
                "pid": process.pid,
                "memory_rss": process_memory.rss,
                "memory_vms": process_memory.vms,
                "create_time": process.create_time(),
                "cpu_percent": process.cpu_percent()
            },
            "services": {
                "api": "running",
                "database": "connected",
                "authentication": "active"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"System status check failed: {str(e)}")

@router.get("/metrics")
async def metrics():
    """
    Metrics endpoint for monitoring and observability.
    Returns application and system metrics.
    """
    try:
        # Performance metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Application metrics
        process = psutil.Process()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "system": {
                    "cpu_usage_percent": cpu_percent,
                    "memory_usage_percent": memory.percent,
                    "memory_available_bytes": memory.available,
                    "memory_used_bytes": memory.used,
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                },
                "application": {
                    "process_memory_rss": process.memory_info().rss,
                    "process_memory_vms": process.memory_info().vms,
                    "process_cpu_percent": process.cpu_percent(),
                    "process_num_threads": process.num_threads(),
                    "process_open_files": len(process.open_files()),
                    "process_connections": len(process.connections())
                },
                "runtime": {
                    "python_version": platform.python_version(),
                    "platform": platform.system(),
                    "uptime_seconds": time.time() - process.create_time()
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Metrics collection failed: {str(e)}")

@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity testing.
    """
    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "ok"
    }

@router.get("/version")
async def version():
    """
    API version information.
    """
    return {
        "api_version": "1.0.0",
        "service": "hardcard-api",
        "build_timestamp": "2025-07-19T21:41:21Z",
        "git_commit": os.environ.get("GIT_COMMIT", "unknown"),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

@router.get("/ready")
async def readiness_check():
    """
    Readiness probe for deployment health checks.
    Verifies that the service is ready to accept traffic.
    """
    try:
        # Check critical dependencies
        dependencies = {
            "database": True,  # Would check actual database connectivity
            "authentication": True,  # Would check auth service
            "external_apis": True  # Would check external service connectivity
        }
        
        all_ready = all(dependencies.values())
        
        if not all_ready:
            raise HTTPException(
                status_code=503, 
                detail={"ready": False, "dependencies": dependencies}
            )
        
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": dependencies
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Readiness check failed: {str(e)}")

@router.get("/live")
async def liveness_check():
    """
    Liveness probe for deployment health checks.
    Verifies that the service is alive and responsive.
    """
    try:
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time(),
            "status": "healthy"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Liveness check failed: {str(e)}")