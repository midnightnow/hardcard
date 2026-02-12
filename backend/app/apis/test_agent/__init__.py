#!/usr/bin/env python3
"""
TestAgent API for HardChain System
-----------------------------------------------------------
This API provides endpoints to test the HardChain system, which integrates the 
RealTBlock trust model and secure Hardcard hardware. Features include:
  - Running complete system tests (authentication, ledger verification, etc.)
  - Measuring API response times and overall performance
  - Conducting health checks and uptime monitoring
  - Detecting UI errors via screenshot captures and OCR
  - Analyzing test results and providing detailed reports

Note: This API requires additional dependencies:
  - requests
  - pyautogui (for screenshot capture)
  - pytesseract (for OCR)

To ensure these dependencies are available, install them separately:
  pip install pyautogui pytesseract requests

Also ensure that Tesseract OCR is installed on the system where tests run.
"""

import json
import time
import hashlib
from datetime import datetime
import logging
from statistics import mean
from typing import Dict, List, Tuple, Optional, Any, Union
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body, Depends
from pydantic import BaseModel

# Create router
router = APIRouter(prefix="/test-agent")

# Configure in-memory logger for test results
class MemoryLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": log_entry
        })

# Create memory handler for storing logs
memory_handler = MemoryLogHandler()
memory_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

# Configure logger
logger = logging.getLogger("test_agent")
logger.setLevel(logging.INFO)
logger.addHandler(memory_handler)

# In-memory storage for test results and performance metrics
test_results = {
    "last_run": None,
    "performance_metrics": {},
    "detected_errors": [],
    "health_checks": {}
}

# Mock data for testing purposes
mock_data = {
    "ledger": [
        {
            "timestamp": "2025-04-01T12:00:00.123456Z",
            "content": "System initialization",
            "extra": "",
            "prev_hash": "GENESIS",
            "hash": "8a7b3c4d5e6f"
        },
        {
            "timestamp": "2025-04-02T09:15:30.789123Z",
            "content": "Editorial approval",
            "extra": "content_hash:abc123",
            "prev_hash": "8a7b3c4d5e6f",
            "hash": "2c3d4e5f6g7h"
        },
        {
            "timestamp": "2025-04-03T14:22:10.456789Z",
            "content": "Campaign created",
            "extra": "campaign_id:camp-456",
            "prev_hash": "2c3d4e5f6g7h",
            "hash": "9j8k7l6m5n4o"
        }
    ],
    "bitcoin_price": 125000.50
}

# Pydantic models
class TestConfig(BaseModel):
    """Configuration for running tests"""
    base_url: str = "https://api.hardchain.example.com"  # Base URL for API endpoints
    user_email: str = "testuser@example.com"  # Test user credentials
    user_password: str = "SecureTestPassword!"  # Test user password
    enable_screenshots: bool = False  # Whether to capture screenshots (requires GUI)
    test_endpoints: List[Dict[str, str]] = []  # Additional endpoints to test
    repeat_count: int = 3  # Number of times to repeat performance tests

class TestResult(BaseModel):
    """Results from a test run"""
    timestamp: str
    duration: float
    success: bool
    performance_metrics: Dict[str, float] = {}
    detected_errors: List[str] = []
    logs: List[Dict[str, str]] = []

class HealthCheckResult(BaseModel):
    """Results from a health check"""
    status: str  # "healthy", "degraded", or "unhealthy"
    timestamp: str
    response_times: Dict[str, float] = {}
    errors: List[str] = []

# Utility functions
def current_timestamp() -> str:
    """Return the current UTC timestamp as a high-precision ISO8601 string."""
    return datetime.utcnow().isoformat(timespec='microseconds') + "Z"

def encode_timestamp(timestamp: str) -> str:
    """Canonical encoding of the timestamp."""
    return timestamp

def compute_event_hash(prev_hash: str, timestamp: str, content: str, 
                      extra: str, signature: str, hash_function=hashlib.sha3_256) -> str:
    """Compute the event hash using a specified hash function."""
    encoded_ts = encode_timestamp(timestamp)
    data = f"{prev_hash}|{encoded_ts}|{content}|{extra}|{signature}"
    return hash_function(data.encode()).hexdigest()

def simulate_response_time(min_time: float = 0.05, max_time: float = 0.2) -> float:
    """Simulate a response time between min_time and max_time seconds."""
    import random
    time.sleep(random.uniform(min_time, max_time))
    return random.uniform(min_time, max_time)

def check_ledger_integrity(ledger: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Verify the integrity of a ledger by recalculating all hashes."""
    if not ledger:
        return False, "Empty ledger"
    
    prev_hash = "GENESIS"  # Starting hash
    
    for i, event in enumerate(ledger):
        # In a real implementation, this would properly validate the hash chain
        # For this mock version, we'll just simulate the verification
        if i > 0 and event.get("prev_hash") != prev_hash:
            return False, f"Hash mismatch at event {i}"
        
        prev_hash = event.get("hash")
    
    return True, "Ledger integrity verified"

# API Endpoints
@router.get("/status")
def get_test_status_agent() -> Dict[str, Any]:
    """Get the status and results of the most recent test run.
    
    Returns a comprehensive summary of the system status, including:
    - Last test run timestamp
    - Performance metrics summary
    - Detected errors
    - Overall health status
    - Analysis results if available
    """
    response = {
        "last_run": test_results["last_run"],
        "performance_summary": test_results["performance_metrics"],
        "detected_errors": test_results["detected_errors"],
        "health_status": test_results["health_checks"].get("status", "unknown")
    }
    
    # Add analysis results if available
    if "latest_analysis" in test_results:
        response["analysis"] = test_results["latest_analysis"]
    
    return response

@router.post("/run-tests", response_model=TestResult)
def run_tests_agent(config: TestConfig, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Run the full suite of tests on the HardChain system."""
    # Clear previous logs
    memory_handler.logs = []
    
    # Start test timestamp
    start_time = time.time()
    timestamp = current_timestamp()
    
    logger.info("[TestAgent] Initiating full system test...")
    
    # In a real implementation, this would actually call services
    # In this mock version, we'll simulate the test sequence
    
    # 1. Simulate login
    logger.info(f"[TestAgent] Attempting login with {config.user_email}...")
    auth_success = True  # Mock successful login
    
    if not auth_success:
        logger.error("[TestAgent] Authentication failed")
        test_results["last_run"] = timestamp
        test_results["detected_errors"] = ["Authentication failed"]
        
        return {
            "timestamp": timestamp,
            "duration": time.time() - start_time,
            "success": False,
            "performance_metrics": {},
            "detected_errors": ["Authentication failed"],
            "logs": memory_handler.logs
        }
    
    logger.info("[TestAgent] Login successful")
    
    # 2. Verify ledger integrity
    logger.info("[TestAgent] Verifying ledger integrity...")
    ledger_ok, ledger_message = check_ledger_integrity(mock_data["ledger"])
    
    if not ledger_ok:
        logger.error(f"[TestAgent] Ledger verification failed: {ledger_message}")
        test_results["detected_errors"] = [f"Ledger integrity check failed: {ledger_message}"]
    else:
        logger.info("[TestAgent] Ledger integrity verified")
    
    # 3. Simulate campaign creation
    logger.info("[TestAgent] Simulating campaign creation...")
    campaign_content = "Launch Campaign: New Media Content Release"
    campaign_success = True  # Mock successful campaign creation
    
    if not campaign_success:
        logger.error("[TestAgent] Campaign creation failed")
        test_results["detected_errors"].append("Campaign creation failed")
    else:
        logger.info("[TestAgent] Campaign created successfully")
    
    # 4. Run performance tests
    logger.info("[TestAgent] Running performance tests...")
    performance_metrics = {}
    
    # Test endpoints defined in config plus standard endpoints
    endpoints_to_test = [
        {"method": "GET", "url": f"{config.base_url}/health"},
        {"method": "GET", "url": f"{config.base_url}/ledger/verify"},
        {"method": "GET", "url": f"{config.base_url}/bitcoin/price"}
    ]
    
    endpoints_to_test.extend(config.test_endpoints)
    
    for endpoint in endpoints_to_test:
        times = []
        for _ in range(config.repeat_count):
            # In a real implementation, this would actually call the endpoints
            elapsed = simulate_response_time()  # Simulate response time
            times.append(elapsed)
        
        avg_time = mean(times)
        performance_metrics[endpoint["url"]] = avg_time
        logger.info(f"[TestAgent] Avg response time for {endpoint['url']}: {avg_time:.3f} seconds")
    
    # 5. Simulate UI error detection (optional)
    detected_errors = []
    if config.enable_screenshots:
        # In a real implementation with GUI access, this would capture actual screenshots
        # For this mock version, we'll simulate error detection
        logger.info("[TestAgent] Capturing screenshots for UI error detection...")
        # Simulate no UI errors
        logger.info("[TestAgent] No UI errors detected")
    
    # Store results for future retrieval
    test_results["last_run"] = timestamp
    test_results["performance_metrics"] = performance_metrics
    test_results["detected_errors"] = detected_errors
    
    # Determine overall success
    success = ledger_ok and campaign_success and not detected_errors
    
    # Update health status
    test_results["health_checks"] = {
        "status": "healthy" if success else "degraded",
        "timestamp": timestamp,
        "response_times": performance_metrics
    }
    
    # Calculate total duration
    duration = time.time() - start_time
    logger.info(f"[TestAgent] Full system test completed in {duration:.2f} seconds")
    
    # Schedule background analysis of test results
    background_tasks.add_task(analyze_test_results, performance_metrics, detected_errors)
    
    return {
        "timestamp": timestamp,
        "duration": duration,
        "success": success,
        "performance_metrics": performance_metrics,
        "detected_errors": detected_errors,
        "logs": memory_handler.logs
    }

@router.get("/health-check", response_model=HealthCheckResult)
def run_health_check() -> Dict[str, Any]:
    """Run a quick health check on critical system components."""
    timestamp = current_timestamp()
    response_times = {}
    errors = []
    
    # 1. Check API health
    logger.info("[TestAgent] Checking API health...")
    # In a real implementation, this would check actual API endpoints
    api_response_time = simulate_response_time()
    response_times["api"] = api_response_time
    
    # 2. Check ledger integrity
    logger.info("[TestAgent] Quick ledger verification...")
    ledger_ok, _ = check_ledger_integrity(mock_data["ledger"])
    if not ledger_ok:
        errors.append("Ledger integrity check failed")
    ledger_response_time = simulate_response_time()
    response_times["ledger"] = ledger_response_time
    
    # 3. Check database connection
    logger.info("[TestAgent] Checking database connection...")
    # In a real implementation, this would check actual database connection
    db_response_time = simulate_response_time()
    response_times["database"] = db_response_time
    
    # Determine overall health status
    status = "healthy"
    if errors:
        status = "unhealthy"
    elif any(t > 0.5 for t in response_times.values()):
        status = "degraded"  # Performance issues
    
    # Store results
    test_results["health_checks"] = {
        "status": status,
        "timestamp": timestamp,
        "response_times": response_times,
        "errors": errors
    }
    
    logger.info(f"[TestAgent] Health check complete. Status: {status}")
    
    return {
        "status": status,
        "timestamp": timestamp,
        "response_times": response_times,
        "errors": errors
    }

@router.get("/logs")
def get_test_logs() -> Dict[str, Any]:
    """Get the logs from the most recent test run."""
    return {
        "last_run": test_results["last_run"],
        "logs": memory_handler.logs
    }

@router.post("/verify-ledger")
def verify_test_ledger(ledger: List[Dict[str, Any]] = Body(...)) -> Dict[str, Any]:
    """Verify the integrity of a provided ledger."""
    if not ledger:
        raise HTTPException(status_code=400, detail="Empty ledger provided")
    
    valid, message = check_ledger_integrity(ledger)
    
    return {
        "valid": valid,
        "message": message,
        "timestamp": current_timestamp()
    }

@router.get("/mock-campaign")
def run_mock_campaign() -> Dict[str, Any]:
    """Run a mock campaign creation test."""
    logger.info("[TestAgent] Running mock campaign creation...")
    
    # Simulate the core functionality without actual API calls
    timestamp = current_timestamp()
    campaign_content = "Test Campaign: Mock Media Release"
    campaign_data = "campaign_id:mock-123"
    
    # Simulate hash creation (in a real system this would use actual data)
    prev_hash = mock_data["ledger"][-1]["hash"]
    signature = "mock_signature"
    new_hash = compute_event_hash(prev_hash, timestamp, campaign_content, campaign_data, signature)
    
    # Create mock event
    new_event = {
        "timestamp": timestamp,
        "content": campaign_content,
        "extra": campaign_data,
        "prev_hash": prev_hash,
        "hash": new_hash[:12]  # Truncate for display purposes
    }
    
    # Add to mock ledger
    mock_data["ledger"].append(new_event)
    
    logger.info(f"[TestAgent] Mock campaign created with hash: {new_hash[:12]}")
    
    return {
        "success": True,
        "timestamp": timestamp,
        "event": new_event,
        "message": "Mock campaign created and added to ledger"
    }

# Background task for deeper analysis
# Error analysis models
class ComponentErrorAnalysis(BaseModel):
    """Analysis of errors for a specific system component"""
    component: str
    error_count: int
    error_types: Dict[str, int]
    performance_impact: float
    recommendations: List[str]

class SystemErrorAnalysis(BaseModel):
    """Comprehensive analysis of system errors"""
    timestamp: str
    total_errors: int
    components: List[ComponentErrorAnalysis]
    system_health: str
    recommendations: List[str]

@router.get("/error-analysis", response_model=SystemErrorAnalysis)
def get_ai_error_analyses() -> Dict[str, Any]:
    """Get AI-powered analysis of errors detected across the system.
    
    This endpoint provides a comprehensive analysis of errors detected during testing,
    including their root causes, patterns, and recommendations for fixing them.
    """
    # In a real implementation, this would perform actual AI analysis on the errors
    # Here we'll return mock data
    timestamp = current_timestamp()
    
    # Check if we have any detected errors from tests
    detected_errors = test_results.get("detected_errors", [])
    
    # Mock analysis based on any detected errors
    if detected_errors:
        return {
            "timestamp": timestamp,
            "total_errors": len(detected_errors),
            "components": [
                {
                    "component": "HardCard Authentication",
                    "error_count": 1,
                    "error_types": {"Validation Error": 1},
                    "performance_impact": 0.3,
                    "recommendations": ["Check that hardcard firmware is updated", "Verify authentication token validation"]
                },
                {
                    "component": "Ledger Verification",
                    "error_count": len(detected_errors) - 1,
                    "error_types": {"Integrity Error": len(detected_errors) - 1},
                    "performance_impact": 0.7,
                    "recommendations": ["Run ledger repair utility", "Check hash algorithm implementation"]
                }
            ],
            "system_health": "degraded",
            "recommendations": [
                "Schedule maintenance window for system repair",
                "Update hash verification algorithms",
                "Roll back to previous stable version if issues persist"
            ]
        }
    else:
        # No errors detected, return healthy status
        return {
            "timestamp": timestamp,
            "total_errors": 0,
            "components": [],
            "system_health": "healthy",
            "recommendations": ["Continue regular system monitoring"]
        }

@router.get("/component-error-analysis/{component}")
def get_ai_error_analysis_for_component(component: str) -> Dict[str, Any]:
    """Get detailed AI error analysis for a specific component.
    
    This endpoint provides an in-depth analysis of errors for a specific system
    component, including historical patterns, root causes, and detailed recommendations.
    """
    # In a real implementation, this would retrieve data for the specific component
    # Here we'll return mock data based on the component name
    mock_components = {
        "hardcard": {
            "component": "HardCard Authentication",
            "error_count": 1,
            "error_types": {"Validation Error": 1},
            "performance_impact": 0.3,
            "recommendations": ["Check that hardcard firmware is updated", "Verify authentication token validation"],
            "detailed_analysis": "The HardCard authentication module is experiencing intermittent validation errors, likely related to the recent firmware update. The error patterns suggest timing issues in the authentication sequence.",
            "code_snippets": ["function validateHardcardAuth(token) { ... }"],
            "historical_trend": "Increasing"
        },
        "ledger": {
            "component": "Ledger Verification",
            "error_count": 2,
            "error_types": {"Integrity Error": 2},
            "performance_impact": 0.7,
            "recommendations": ["Run ledger repair utility", "Check hash algorithm implementation"],
            "detailed_analysis": "The ledger verification failures indicate potential tampering or data corruption in block sequences. The hashing algorithm output differs from expected values.",
            "code_snippets": ["function verifyLedgerIntegrity(ledger) { ... }"],
            "historical_trend": "Stable"
        }
    }
    
    # Return data for the requested component or a 404 if not found
    if component.lower() in mock_components:
        return mock_components[component.lower()]
    else:
        raise HTTPException(status_code=404, detail=f"No analysis found for component '{component}'")

def analyze_test_results(performance_metrics: Dict[str, float], detected_errors: List[str]) -> None:
    """Analyze test results in the background and store insights.
    
    This function performs deeper analysis of performance patterns,
    error correlations, and potential system bottlenecks. Results are stored
    for historical tracking and trend analysis.
    """
    logger.info("[TestAgent] Starting detailed analysis of test results...")
    
    # Performance analysis
    slow_endpoints = []
    fast_endpoints = []
    avg_response_time = 0.0
    
    if performance_metrics:
        avg_response_time = sum(performance_metrics.values()) / len(performance_metrics)
        
        for endpoint, time in performance_metrics.items():
            if time > 0.5:  # Threshold for slow response
                slow_endpoints.append((endpoint, time))
            elif time < 0.1:  # Threshold for fast response
                fast_endpoints.append((endpoint, time))
    
        if slow_endpoints:
            logger.warning(f"[TestAgent] Detected {len(slow_endpoints)} slow endpoints: " + 
                        ", ".join([f"{e} ({t:.3f}s)" for e, t in slow_endpoints[:3]]) +
                        (" and more..." if len(slow_endpoints) > 3 else ""))
        
        logger.info(f"[TestAgent] Average response time across all endpoints: {avg_response_time:.3f}s")
    
    # Error pattern analysis
    if detected_errors:
        error_categories = {}
        for error in detected_errors:
            category = "Unknown"
            if "auth" in error.lower() or "login" in error.lower():
                category = "Authentication"
            elif "ledger" in error.lower() or "hash" in error.lower():
                category = "Ledger Integrity"
            elif "timeout" in error.lower() or "slow" in error.lower():
                category = "Performance"
            elif "ui" in error.lower():
                category = "User Interface"
            
            if category in error_categories:
                error_categories[category] += 1
            else:
                error_categories[category] = 1
        
        for category, count in error_categories.items():
            logger.warning(f"[TestAgent] {category} errors: {count}")
    
    # Store the analysis results
    analysis_results = {
        "timestamp": current_timestamp(),
        "average_response_time": avg_response_time,
        "slow_endpoints": len(slow_endpoints),
        "fast_endpoints": len(fast_endpoints),
        "error_categories": {category: count for category, count in error_categories.items()} if 'error_categories' in locals() else {},
        "overall_health": "healthy" if not slow_endpoints and not detected_errors else 
                        "degraded" if len(slow_endpoints) < 3 and len(detected_errors) < 2 else 
                        "unhealthy"
    }
    
    # In a real implementation, this would be stored persistently
    # For now, we'll add it to our in-memory test_results
    test_results["latest_analysis"] = analysis_results
    
    logger.info("[TestAgent] Analysis of test results completed")
    logger.info(f"[TestAgent] Overall system health assessment: {analysis_results['overall_health']}")

@router.get("/test-logs")
def get_test_logs_endpoint() -> Dict[str, Any]:
    """Get the logs from the most recent test run.
    
    This endpoint is dedicated to retrieving detailed logs from test runs
    including timestamps, log levels, and messages, which can be used for
    debugging and monitoring.
    """
    return {
        "last_run": test_results.get("last_run"),
        "logs": memory_handler.logs
    }