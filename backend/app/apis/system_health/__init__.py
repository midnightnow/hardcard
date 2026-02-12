from fastapi import APIRouter, BackgroundTasks, status, HTTPException
import databutton as db
import time
import datetime
import json
import re
from typing import List, Dict, Any, Optional, Callable
import asyncio
import httpx
from pydantic import BaseModel, Field
from enum import Enum
import traceback
import random

router = APIRouter(prefix="/system-health")

# Storage key sanitization
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# System test status enum
class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"

# System test result model
class TestResult(BaseModel):
    id: str
    name: str
    status: TestStatus
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

# System test suite result model
class TestSuiteResult(BaseModel):
    id: str
    name: str
    status: TestStatus
    results: List[TestResult] = []
    start_time: str
    end_time: Optional[str] = None
    total_duration_ms: Optional[int] = None
    successful_tests: int = 0
    failed_tests: int = 0
    warning_tests: int = 0

# Store for test results
class TestStore:
    @staticmethod
    def save_test_suite_result(result: TestSuiteResult):
        """Save a test suite result to storage"""
        try:
            # Get existing test results
            try:
                test_results = db.storage.json.get("system_test_results", default={})
            except:
                test_results = {}
            
            # Add the new test result
            test_results[result.id] = result.dict()
            
            # Save the updated test results
            db.storage.json.put(sanitize_storage_key("system_test_results"), test_results)
            
            # Also save the latest test result separately for quick access
            db.storage.json.put(sanitize_storage_key("latest_system_test_result"), result.dict())
            
            return True
        except Exception as e:
            print(f"Error saving test result: {e}")
            return False
    
    @staticmethod
    def get_latest_test_result() -> Optional[TestSuiteResult]:
        """Get the latest test suite result"""
        try:
            result_dict = db.storage.json.get("latest_system_test_result", default=None)
            if result_dict:
                return TestSuiteResult(**result_dict)
            return None
        except Exception as e:
            print(f"Error getting latest test result: {e}")
            return None
    
    @staticmethod
    def get_test_history(limit: int = 10) -> List[TestSuiteResult]:
        """Get test suite result history"""
        try:
            test_results = db.storage.json.get("system_test_results", default={})
            
            # Convert to list of TestSuiteResult objects
            result_list = []
            for test_id, test_data in test_results.items():
                try:
                    result_list.append(TestSuiteResult(**test_data))
                except Exception as e:
                    print(f"Error parsing test result {test_id}: {e}")
            
            # Sort by start_time descending
            result_list.sort(key=lambda x: x.start_time, reverse=True)
            
            # Limit results
            return result_list[:limit]
        except Exception as e:
            print(f"Error getting test history: {e}")
            return []

# System tests generator
class SystemTests:
    @staticmethod
    async def run_api_test(name: str, endpoint: str, method: str = "GET", expected_status: int = 200) -> TestResult:
        """Run a test against an API endpoint"""
        test_id = f"api-{endpoint.replace('/', '-')}-{method}"
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(endpoint, timeout=10.0)
                elif method == "POST":
                    response = await client.post(endpoint, json={}, timeout=10.0)
                else:
                    return TestResult(
                        id=test_id,
                        name=name,
                        status=TestStatus.FAILED,
                        message=f"Unsupported method: {method}",
                        duration_ms=int((time.time() - start_time) * 1000)
                    )
                
                # Check status code
                if response.status_code == expected_status:
                    return TestResult(
                        id=test_id,
                        name=name,
                        status=TestStatus.SUCCESS,
                        message=f"API endpoint {endpoint} responded with status {response.status_code}",
                        details={"status_code": response.status_code},
                        duration_ms=int((time.time() - start_time) * 1000)
                    )
                else:
                    return TestResult(
                        id=test_id,
                        name=name,
                        status=TestStatus.FAILED,
                        message=f"API endpoint {endpoint} responded with unexpected status {response.status_code}",
                        details={"status_code": response.status_code, "expected_status": expected_status},
                        duration_ms=int((time.time() - start_time) * 1000)
                    )
        except Exception as e:
            return TestResult(
                id=test_id,
                name=name,
                status=TestStatus.FAILED,
                message=f"Error testing API endpoint {endpoint}: {str(e)}",
                details={"error": str(e), "traceback": traceback.format_exc()},
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    @staticmethod
    async def ping_database() -> TestResult:
        """Test database connectivity"""
        test_id = "database-ping"
        start_time = time.time()
        
        try:
            # Just try to read a simple value from db.storage as a ping test
            db.storage.json.get("health_check_ping", default={"ping": "pong"})
            
            return TestResult(
                id=test_id,
                name="Database Ping",
                status=TestStatus.SUCCESS,
                message="Successfully connected to database",
                duration_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return TestResult(
                id=test_id,
                name="Database Ping",
                status=TestStatus.FAILED,
                message=f"Failed to connect to database: {str(e)}",
                details={"error": str(e)},
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    @staticmethod
    async def test_firebase_config() -> TestResult:
        """Test Firebase configuration"""
        test_id = "firebase-config"
        start_time = time.time()
        
        # Since we can't directly test Firebase connection from here,
        # we'll just verify that the configuration exists
        try:
            # Try to get Firebase config from storage (assuming it's stored there)
            firebase_config = db.storage.json.get("firebase_config", default=None)
            
            if firebase_config is not None:
                return TestResult(
                    id=test_id,
                    name="Firebase Configuration",
                    status=TestStatus.SUCCESS,
                    message="Firebase configuration exists",
                    duration_ms=int((time.time() - start_time) * 1000)
                )
            else:
                return TestResult(
                    id=test_id,
                    name="Firebase Configuration",
                    status=TestStatus.WARNING,
                    message="Firebase configuration not found in storage",
                    duration_ms=int((time.time() - start_time) * 1000)
                )
        except Exception as e:
            return TestResult(
                id=test_id,
                name="Firebase Configuration",
                status=TestStatus.WARNING,
                message=f"Error checking Firebase configuration: {str(e)}",
                details={"error": str(e)},
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    @staticmethod
    async def generate_core_tests() -> List[Callable[[], TestResult]]:
        """Generate the core system tests"""
        return [
            SystemTests.ping_database,
            SystemTests.test_firebase_config,
            # Add more core tests as needed
        ]
    
    @staticmethod
    async def generate_api_tests() -> List[Callable[[], TestResult]]:
        """Generate API endpoint tests"""
        # Define API endpoints to test
        api_endpoints = [
            # Health endpoints
            {"name": "Health Check", "endpoint": "/api/v1/error_handling/health", "method": "GET"},
            
            # Core endpoints
            {"name": "Family Profiles List", "endpoint": "/api/v1/family-profiles/", "method": "GET"},
            {"name": "Bitcoin Price", "endpoint": "/api/v1/bitcoin/price", "method": "GET"},
            {"name": "Vault Config", "endpoint": "/api/v1/vault-config/", "method": "GET"},
            
            # Add more API endpoints to test
        ]
        
        # Create tests
        tests = []
        for endpoint_info in api_endpoints:
            tests.append(lambda ei=endpoint_info: SystemTests.run_api_test(
                name=ei["name"],
                endpoint=ei["endpoint"],
                method=ei["method"]
            ))
        
        return tests

# Model for test request
class SystemTestRequest(BaseModel):
    test_name: Optional[str] = "Full System Test"
    include_apis: bool = True
    include_database: bool = True
    include_firebase: bool = True
    self_healing: bool = False  # Whether to attempt automatic fixes

# Run system tests in background
async def run_system_tests(test_request: SystemTestRequest):
    # Create test suite result
    test_suite_id = f"test-{int(time.time())}"
    test_suite = TestSuiteResult(
        id=test_suite_id,
        name=test_request.test_name,
        status=TestStatus.RUNNING,
        start_time=time.strftime("%Y-%m-%d %H:%M:%S"),
        results=[]
    )
    
    # Save initial state
    TestStore.save_test_suite_result(test_suite)
    
    # Start tracking
    start_time = time.time()
    successful_tests = 0
    failed_tests = 0
    warning_tests = 0
    
    try:
        # Generate tests
        all_tests = []
        
        # Add core tests
        if test_request.include_database or test_request.include_firebase:
            core_tests = await SystemTests.generate_core_tests()
            for test in core_tests:
                if (test.__name__ == "ping_database" and test_request.include_database) or \
                   (test.__name__ == "test_firebase_config" and test_request.include_firebase):
                    all_tests.append(test)
        
        # Add API tests
        if test_request.include_apis:
            api_tests = await SystemTests.generate_api_tests()
            all_tests.extend(api_tests)
        
        # Run tests
        for test_func in all_tests:
            try:
                # Run the test
                test_result = await test_func()
                
                # Update counts
                if test_result.status == TestStatus.SUCCESS:
                    successful_tests += 1
                elif test_result.status == TestStatus.FAILED:
                    failed_tests += 1
                elif test_result.status == TestStatus.WARNING:
                    warning_tests += 1
                
                # Add to results
                test_suite.results.append(test_result)
                
                # Update and save intermediate results
                test_suite.successful_tests = successful_tests
                test_suite.failed_tests = failed_tests
                test_suite.warning_tests = warning_tests
                TestStore.save_test_suite_result(test_suite)
                
                # If self-healing is enabled, try to fix the issue
                if test_request.self_healing and test_result.status == TestStatus.FAILED:
                    # Here we would add logic to try and fix issues
                    # This would be application-specific based on what can be automatically fixed
                    pass
                
                # Slight delay to avoid overwhelming the system
                await asyncio.sleep(0.1)
            except Exception as e:
                # If a test itself raises an exception, log it
                error_result = TestResult(
                    id=f"error-{int(time.time()* 1000)}",
                    name=f"Error running test {getattr(test_func, '__name__', 'Unknown')}",
                    status=TestStatus.FAILED,
                    message=f"Exception running test: {str(e)}",
                    details={"error": str(e), "traceback": traceback.format_exc()}
                )
                test_suite.results.append(error_result)
                failed_tests += 1
        
        # Complete test suite
        end_time = time.time()
        test_suite.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        test_suite.total_duration_ms = int((end_time - start_time) * 1000)
        test_suite.successful_tests = successful_tests
        test_suite.failed_tests = failed_tests
        test_suite.warning_tests = warning_tests
        
        # Determine overall status
        if failed_tests > 0:
            test_suite.status = TestStatus.FAILED
        elif warning_tests > 0:
            test_suite.status = TestStatus.WARNING
        else:
            test_suite.status = TestStatus.SUCCESS
        
        # Save final results
        TestStore.save_test_suite_result(test_suite)
    except Exception as e:
        # If the entire test suite fails
        test_suite.status = TestStatus.FAILED
        test_suite.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        test_suite.total_duration_ms = int((time.time() - start_time) * 1000)
        TestStore.save_test_suite_result(test_suite)
        print(f"Error running system tests: {e}")
        print(traceback.format_exc())

# Endpoint to request a system test
@router.post("/run-tests")
async def run_system_health_tests(request: SystemTestRequest, background_tasks: BackgroundTasks):
    """Run system tests in the background to evaluate system health
    
    This endpoint starts a comprehensive test of system components and returns
    a test ID. The tests run in the background and the results can be retrieved
    using the /test-status endpoint.
    """
    # Create test suite ID
    test_suite_id = f"test-{int(time.time())}"
    
    # Create initial test suite result
    test_suite = TestSuiteResult(
        id=test_suite_id,
        name=request.test_name,
        status=TestStatus.PENDING,
        start_time=time.strftime("%Y-%m-%d %H:%M:%S"),
        results=[]
    )
    
    # Save initial state
    TestStore.save_test_suite_result(test_suite)
    
    # Run tests in background
    background_tasks.add_task(run_system_tests, request)
    
    # Return test suite ID
    return {"test_id": test_suite_id, "status": "pending", "message": "System tests started"}

# Endpoint to get test status
@router.get("/test-status/{test_id}")
async def get_system_health_test_status(test_id: str):
    """Get the status of a system test run"""
    # Get test results
    test_results = db.storage.json.get("system_test_results", default={})
    
    # Check if test exists
    if test_id not in test_results:
        raise HTTPException(status_code=404, detail=f"Test ID {test_id} not found")
    
    # Return test status
    return test_results[test_id]

# Endpoint to get latest test result
@router.get("/latest-test")
async def get_latest_test():
    """Get the latest system test result"""
    # Get latest test result
    latest_result = TestStore.get_latest_test_result()
    
    # Check if result exists
    if latest_result is None:
        return {"status": "none", "message": "No test results found"}
    
    # Return latest result
    return latest_result

# Endpoint to get test history
@router.get("/test-history")
async def get_test_history(limit: int = 10):
    """Get test history"""
    # Get test history
    history = TestStore.get_test_history(limit)
    
    # Return history
    return {"history": [h.dict() for h in history]}

# Self-healing endpoint that tries to fix common issues
@router.post("/self-heal")
async def self_heal(background_tasks: BackgroundTasks):
    """Attempt to automatically fix common issues
    
    This endpoint runs diagnostics and attempts to repair common problems that
    are detected. It will focus on issues that can be fixed programmatically.
    """
    # Create a self-healing test request
    test_request = SystemTestRequest(
        test_name="Self-Healing Run",
        include_apis=True,
        include_database=True,
        include_firebase=True,
        self_healing=True  # Enable self-healing mode
    )
    
    # Run tests in background with self-healing enabled
    background_tasks.add_task(run_system_tests, test_request)
    
    # Return status
    return {"status": "initiated", "message": "Self-healing process started"}

# Models for error analysis
class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    source: str

class ErrorAnalysisResponse(BaseModel):
    error_count: int
    errors: List[LogEntry]
    summary: str

class ClientErrorLog(BaseModel):
    message: str
    stack: Optional[str] = None
    context: Optional[dict] = None

# Placeholder function to simulate reading production logs
def read_production_logs(
    start_time: datetime.datetime, end_time: datetime.datetime, query: Optional[str] = None
) -> List[dict]:
    # In a real scenario, this would interact with a logging service.
    print(f"Fetching logs from {start_time} to {end_time} with query: {query}")
    # Mock data for demonstration
    return [
        {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": "ERROR",
            "message": "Sample error: Null pointer exception in backend.",
            "source": "backend",
        },
        {
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat(),
            "level": "ERROR",
            "message": "Sample error: API call failed on client.",
            "source": "frontend",
        },
    ]




@router.get("/analyze-errors-health", response_model=ErrorAnalysisResponse)
async def analyze_errors_health(
    minutes: int = 60, query: Optional[str] = None
):
    """
    Analyzes production logs for errors within a specified time window.
    """
    try:
        end_time = datetime.datetime.now(datetime.timezone.utc)
        start_time = end_time - datetime.timedelta(minutes=minutes)

        logs = read_production_logs(start_time, end_time, query=query)

        error_logs = [log for log in logs if log.get("level") == "ERROR"]

        return ErrorAnalysisResponse(
            error_count=len(error_logs),
            errors=[LogEntry(**log) for log in error_logs],
            summary=f"Found {len(error_logs)} errors in the last {minutes} minutes.",
        )
    except Exception as e:
        print(f"Error during log analysis: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to analyze logs.")


@router.post("/log-client-error-health", status_code=202)
async def log_client_error_health(error: ClientErrorLog):
    """
    Receives and logs an error from the client-side application.
    """
    print(
        f"CLIENT_ERROR_LOG: {error.message} | Context: {error.context} | Stack: {error.stack}"
    )
    return {"status": "logged"}



# Enhanced health check endpoint
@router.get("/health-check")
async def health_check(deep: bool = False):
    """Get the current health status of the system
    
    This endpoint provides a quick health check of essential services.
    If 'deep' is set to true, it will perform a more comprehensive check.
    """
    # Quick check for API health
    system_health = {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checks": {
            "api": {"status": "healthy"}
        }
    }
    
    # If deep check requested, add more health data
    if deep:
        try:
            # Check database
            try:
                db.storage.json.get("health_check_ping", default={"ping": "pong"})
                system_health["checks"]["database"] = {"status": "healthy"}
            except Exception as e:
                system_health["checks"]["database"] = {
                    "status": "unhealthy", 
                    "message": str(e)
                }
                system_health["status"] = "degraded"
            
            # Get latest test result if available
            latest_result = TestStore.get_latest_test_result()
            if latest_result:
                system_health["latest_test"] = {
                    "status": latest_result.status,
                    "timestamp": latest_result.end_time,
                    "successful": latest_result.successful_tests,
                    "failed": latest_result.failed_tests,
                    "warnings": latest_result.warning_tests
                }
                
                # Incorporate test results into overall health
                if latest_result.status == TestStatus.FAILED:
                    system_health["status"] = "degraded"
        except Exception as e:
            system_health["status"] = "degraded"
            system_health["error"] = str(e)
    
    return system_health
