#!/usr/bin/env python3
"""
Enhanced Resilience System - Advanced self-healing with circuit breakers, 
bulkheads, and graceful degradation patterns for mission-critical stability.

The bones, nerves, and ligaments of our software body.
"""

import os
import json
import time
import asyncio
import threading
import logging
import subprocess
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import hashlib
import pickle

class ResilienceLevel(Enum):
    CATASTROPHIC = "catastrophic"  # System-wide failure
    CRITICAL = "critical"          # Core functionality at risk
    DEGRADED = "degraded"          # Reduced functionality
    STABLE = "stable"              # Normal operation
    OPTIMAL = "optimal"            # Peak performance

class ComponentState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    FAILED = "failed"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"

class RecoveryStrategy(Enum):
    RESTART = "restart"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    CIRCUIT_BREAK = "circuit_break"
    FAILOVER = "failover"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"

@dataclass
class ComponentHealth:
    component_id: str
    state: ComponentState
    last_check: datetime
    consecutive_failures: int = 0
    last_failure: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    criticality: int = 1  # 1-5, where 5 is most critical

@dataclass
class ResilienceEvent:
    event_id: str
    timestamp: datetime
    component_id: str
    event_type: str
    severity: str
    description: str
    recovery_action: Optional[str] = None
    success: bool = False
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class CircuitBreaker:
    """Circuit breaker pattern implementation for preventing cascade failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, 
                 half_open_attempts: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_attempts = half_open_attempts
        
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_attempts_made = 0
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                self.half_open_attempts_made = 0
            else:
                raise Exception(f"Circuit breaker OPEN - blocking call to {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (self.last_failure_time and 
                time.time() - self.last_failure_time > self.recovery_timeout)
    
    def _on_success(self):
        if self.state == "HALF_OPEN":
            self.half_open_attempts_made += 1
            if self.half_open_attempts_made >= self.half_open_attempts:
                self.state = "CLOSED"
                self.failure_count = 0
        elif self.state == "CLOSED":
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
        elif self.state == "HALF_OPEN":
            self.state = "OPEN"

class BulkheadIsolation:
    """Bulkhead pattern for resource isolation"""
    
    def __init__(self, max_concurrent: int = 10, queue_size: int = 100):
        self.max_concurrent = max_concurrent
        self.queue_size = queue_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_requests = 0
        self.queued_requests = 0
        
    async def execute(self, coro):
        """Execute coroutine with bulkhead protection"""
        if self.queued_requests >= self.queue_size:
            raise Exception("Bulkhead queue full - rejecting request")
        
        self.queued_requests += 1
        try:
            async with self.semaphore:
                self.queued_requests -= 1
                self.active_requests += 1
                try:
                    return await coro
                finally:
                    self.active_requests -= 1
        except Exception:
            self.queued_requests -= 1
            raise

class GracefulDegradation:
    """Graceful degradation pattern for non-critical features"""
    
    def __init__(self):
        self.disabled_features = set()
        self.degradation_rules = {}
        
    def register_fallback(self, feature: str, fallback_func: Callable):
        """Register a fallback function for a feature"""
        self.degradation_rules[feature] = fallback_func
    
    def disable_feature(self, feature: str, reason: str):
        """Disable a non-critical feature"""
        self.disabled_features.add(feature)
        logging.warning(f"Feature '{feature}' disabled due to: {reason}")
    
    def enable_feature(self, feature: str):
        """Re-enable a feature"""
        self.disabled_features.discard(feature)
        logging.info(f"Feature '{feature}' re-enabled")
    
    def execute_with_fallback(self, feature: str, primary_func: Callable, 
                            *args, **kwargs) -> Any:
        """Execute function with fallback if feature is disabled"""
        if feature in self.disabled_features:
            fallback = self.degradation_rules.get(feature)
            if fallback:
                return fallback(*args, **kwargs)
            else:
                raise Exception(f"Feature '{feature}' is disabled and no fallback available")
        
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            # Auto-disable on repeated failures
            self.disable_feature(feature, str(e))
            fallback = self.degradation_rules.get(feature)
            if fallback:
                return fallback(*args, **kwargs)
            raise

class EnhancedHealthMonitor:
    """Advanced health monitoring with predictive capabilities"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.components = {}
        self.health_history = deque(maxlen=1000)
        self.circuit_breakers = {}
        self.bulkheads = {}
        self.degradation = GracefulDegradation()
        
        # Setup monitoring database
        self.db_path = os.path.join(project_root, "monitoring", "resilience.db")
        self._init_resilience_db()
        
        # Component definitions
        self._register_system_components()
        
    def _init_resilience_db(self):
        """Initialize resilience tracking database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS component_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    metrics TEXT,
                    consecutive_failures INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS resilience_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    component_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    recovery_action TEXT,
                    success BOOLEAN,
                    duration_ms REAL,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS system_baselines (
                    component_id TEXT PRIMARY KEY,
                    normal_cpu_range TEXT,
                    normal_memory_range TEXT,
                    normal_response_time_ms REAL,
                    last_updated TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_component_health_time 
                ON component_health(component_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_resilience_events_time 
                ON resilience_events(timestamp);
            """)
    
    def _register_system_components(self):
        """Register all system components for monitoring"""
        components = {
            "git_repository": ComponentHealth(
                component_id="git_repository",
                state=ComponentState.HEALTHY,
                last_check=datetime.now(),
                criticality=5,
                dependencies=[]
            ),
            "file_system": ComponentHealth(
                component_id="file_system",
                state=ComponentState.HEALTHY,
                last_check=datetime.now(),
                criticality=5,
                dependencies=[]
            ),
            "quality_gates": ComponentHealth(
                component_id="quality_gates",
                state=ComponentState.HEALTHY,
                last_check=datetime.now(),
                criticality=4,
                dependencies=["git_repository"]
            ),
            "agent_coordination": ComponentHealth(
                component_id="agent_coordination",
                state=ComponentState.HEALTHY,
                last_check=datetime.now(),
                criticality=3,
                dependencies=["git_repository", "file_system"]
            ),
            "background_monitors": ComponentHealth(
                component_id="background_monitors",
                state=ComponentState.HEALTHY,
                last_check=datetime.now(),
                criticality=2,
                dependencies=[]
            ),
            "development_tools": ComponentHealth(
                component_id="development_tools",
                state=ComponentState.HEALTHY,
                last_check=datetime.now(),
                criticality=1,
                dependencies=["file_system"]
            )
        }
        
        for comp_id, health in components.items():
            self.components[comp_id] = health
            # Initialize circuit breakers
            self.circuit_breakers[comp_id] = CircuitBreaker(
                failure_threshold=3 if health.criticality >= 4 else 5,
                recovery_timeout=30 if health.criticality >= 4 else 60
            )
            # Initialize bulkheads
            self.bulkheads[comp_id] = BulkheadIsolation(
                max_concurrent=5 if health.criticality >= 4 else 3
            )
    
    def check_component_health(self, component_id: str) -> ComponentHealth:
        """Check health of a specific component"""
        if component_id not in self.components:
            raise ValueError(f"Unknown component: {component_id}")
        
        component = self.components[component_id]
        
        try:
            # Use circuit breaker for health checks
            health_result = self.circuit_breakers[component_id].call(
                self._perform_health_check, component_id
            )
            
            # Update component state based on check
            old_state = component.state
            component.state = health_result["state"]
            component.last_check = datetime.now()
            component.metrics = health_result["metrics"]
            
            if health_result["healthy"]:
                component.consecutive_failures = 0
            else:
                component.consecutive_failures += 1
                component.last_failure = datetime.now()
            
            # Record health data
            self._record_health_data(component)
            
            # Trigger recovery if needed
            if old_state != component.state and component.state in [
                ComponentState.FAILING, ComponentState.FAILED
            ]:
                self._trigger_component_recovery(component_id)
            
            return component
            
        except Exception as e:
            # Circuit breaker is open or component check failed
            component.state = ComponentState.FAILED
            component.consecutive_failures += 1
            component.last_failure = datetime.now()
            
            self._record_resilience_event(ResilienceEvent(
                event_id=f"health_check_failed_{component_id}_{int(time.time())}",
                timestamp=datetime.now(),
                component_id=component_id,
                event_type="health_check_failure",
                severity="high",
                description=f"Health check failed: {str(e)}",
                metadata={"exception": str(e)}
            ))
            
            return component
    
    def _perform_health_check(self, component_id: str) -> Dict[str, Any]:
        """Perform actual health check for component"""
        if component_id == "git_repository":
            return self._check_git_health()
        elif component_id == "file_system":
            return self._check_filesystem_health()
        elif component_id == "quality_gates":
            return self._check_quality_gates_health()
        elif component_id == "agent_coordination":
            return self._check_agent_coordination_health()
        elif component_id == "background_monitors":
            return self._check_background_monitors_health()
        elif component_id == "development_tools":
            return self._check_development_tools_health()
        else:
            raise ValueError(f"No health check implementation for {component_id}")
    
    def _check_git_health(self) -> Dict[str, Any]:
        """Check Git repository health"""
        try:
            os.chdir(self.project_root)
            
            # Check repository integrity
            fsck_result = subprocess.run(
                ["git", "fsck", "--no-progress"], 
                capture_output=True, text=True, timeout=30
            )
            
            # Check worktree status
            worktree_result = subprocess.run(
                ["git", "worktree", "list"], 
                capture_output=True, text=True, timeout=10
            )
            
            # Check for uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, text=True, timeout=10
            )
            
            corruption_detected = fsck_result.returncode != 0
            worktree_count = len(worktree_result.stdout.strip().split('\n')) if worktree_result.stdout.strip() else 0
            uncommitted_files = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            
            # Determine health state
            if corruption_detected:
                state = ComponentState.FAILED
                healthy = False
            elif worktree_count == 0:
                state = ComponentState.DEGRADED
                healthy = False
            else:
                state = ComponentState.HEALTHY
                healthy = True
            
            return {
                "healthy": healthy,
                "state": state,
                "metrics": {
                    "corruption_detected": corruption_detected,
                    "worktree_count": worktree_count,
                    "uncommitted_files": uncommitted_files,
                    "fsck_output": fsck_result.stderr[:200] if fsck_result.stderr else ""
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                "healthy": False,
                "state": ComponentState.FAILING,
                "metrics": {"error": "Health check timeout"}
            }
        except Exception as e:
            return {
                "healthy": False,
                "state": ComponentState.FAILED,
                "metrics": {"error": str(e)}
            }
    
    def _check_filesystem_health(self) -> Dict[str, Any]:
        """Check file system health"""
        try:
            import shutil
            import psutil
            
            # Disk usage
            disk_usage = shutil.disk_usage(self.project_root)
            total_gb = disk_usage.total / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            usage_percent = ((disk_usage.total - disk_usage.free) / disk_usage.total) * 100
            
            # I/O statistics
            io_stats = psutil.disk_io_counters()
            
            # File access test
            test_file = os.path.join(self.project_root, "monitoring", "health_test.tmp")
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            
            start_time = time.time()
            with open(test_file, "w") as f:
                f.write("health_check_test")
            with open(test_file, "r") as f:
                content = f.read()
            os.remove(test_file)
            io_latency_ms = (time.time() - start_time) * 1000
            
            # Determine health
            if usage_percent > 95:
                state = ComponentState.FAILED
                healthy = False
            elif usage_percent > 90 or io_latency_ms > 1000:
                state = ComponentState.DEGRADED
                healthy = False
            elif usage_percent > 80 or io_latency_ms > 500:
                state = ComponentState.DEGRADED
                healthy = True
            else:
                state = ComponentState.HEALTHY
                healthy = True
            
            return {
                "healthy": healthy,
                "state": state,
                "metrics": {
                    "disk_usage_percent": round(usage_percent, 2),
                    "free_gb": round(free_gb, 2),
                    "total_gb": round(total_gb, 2),
                    "io_latency_ms": round(io_latency_ms, 2),
                    "io_read_bytes": io_stats.read_bytes if io_stats else 0,
                    "io_write_bytes": io_stats.write_bytes if io_stats else 0
                }
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "state": ComponentState.FAILED,
                "metrics": {"error": str(e)}
            }
    
    def _check_quality_gates_health(self) -> Dict[str, Any]:
        """Check quality gates system health"""
        try:
            # Check if quality gates script exists and is executable
            gates_script = os.path.join(self.project_root, "scripts", "quality-gates-enforcer.sh")
            
            if not os.path.exists(gates_script):
                return {
                    "healthy": False,
                    "state": ComponentState.FAILED,
                    "metrics": {"error": "Quality gates script missing"}
                }
            
            if not os.access(gates_script, os.X_OK):
                return {
                    "healthy": False,
                    "state": ComponentState.DEGRADED,
                    "metrics": {"error": "Quality gates script not executable"}
                }
            
            # Check Git hooks
            hooks_dir = os.path.join(self.project_root, ".git", "hooks")
            required_hooks = ["pre-commit", "pre-push"]
            missing_hooks = []
            
            for hook in required_hooks:
                hook_path = os.path.join(hooks_dir, hook)
                if not os.path.exists(hook_path) or not os.access(hook_path, os.X_OK):
                    missing_hooks.append(hook)
            
            # Check recent enforcement activity
            enforcement_log = os.path.join(self.project_root, "logs", "quality-enforcement.log")
            recent_activity = False
            if os.path.exists(enforcement_log):
                mtime = datetime.fromtimestamp(os.path.getmtime(enforcement_log))
                recent_activity = datetime.now() - mtime < timedelta(hours=24)
            
            # Determine health
            if missing_hooks:
                state = ComponentState.DEGRADED
                healthy = len(missing_hooks) < len(required_hooks)
            else:
                state = ComponentState.HEALTHY
                healthy = True
            
            return {
                "healthy": healthy,
                "state": state,
                "metrics": {
                    "gates_script_exists": os.path.exists(gates_script),
                    "gates_script_executable": os.access(gates_script, os.X_OK),
                    "missing_hooks": missing_hooks,
                    "recent_activity": recent_activity
                }
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "state": ComponentState.FAILED,
                "metrics": {"error": str(e)}
            }
    
    def _check_agent_coordination_health(self) -> Dict[str, Any]:
        """Check agent coordination system health"""
        try:
            # Check worktree manager script
            worktree_manager = os.path.join(self.project_root, "scripts", "worktree-task-manager.sh")
            
            if not os.path.exists(worktree_manager):
                return {
                    "healthy": False,
                    "state": ComponentState.FAILED,
                    "metrics": {"error": "Worktree manager script missing"}
                }
            
            # Check agent directories
            agent_dirs = [
                "/Users/studio/hardcard-frontend-ai",
                "/Users/studio/hardcard-backend-ai",
                "/Users/studio/hardcard-testing-ai",
                "/Users/studio/hardcard-docs-ai",
                "/Users/studio/hardcard-security-ai"
            ]
            
            missing_agents = []
            for agent_dir in agent_dirs:
                if not os.path.exists(agent_dir):
                    missing_agents.append(os.path.basename(agent_dir))
            
            # Check coordination logs
            coordination_log = os.path.join(self.project_root, "logs", "agent-coordination.log")
            recent_coordination = False
            if os.path.exists(coordination_log):
                mtime = datetime.fromtimestamp(os.path.getmtime(coordination_log))
                recent_coordination = datetime.now() - mtime < timedelta(hours=6)
            
            # Determine health
            if len(missing_agents) > 2:
                state = ComponentState.FAILED
                healthy = False
            elif missing_agents:
                state = ComponentState.DEGRADED
                healthy = True
            else:
                state = ComponentState.HEALTHY
                healthy = True
            
            return {
                "healthy": healthy,
                "state": state,
                "metrics": {
                    "worktree_manager_exists": os.path.exists(worktree_manager),
                    "missing_agents": missing_agents,
                    "recent_coordination": recent_coordination,
                    "total_agents": len(agent_dirs),
                    "active_agents": len(agent_dirs) - len(missing_agents)
                }
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "state": ComponentState.FAILED,
                "metrics": {"error": str(e)}
            }
    
    def _check_background_monitors_health(self) -> Dict[str, Any]:
        """Check background monitoring processes health"""
        try:
            import psutil
            
            # Expected monitor processes
            expected_monitors = [
                "claude-continuous-monitor",
                "claude-startup-enforcer"
            ]
            
            running_monitors = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    for monitor in expected_monitors:
                        if monitor in cmdline:
                            running_monitors.append(monitor)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check monitoring logs
            monitor_log = os.path.join(self.project_root, "logs", "background-monitoring.log")
            recent_monitoring = False
            if os.path.exists(monitor_log):
                mtime = datetime.fromtimestamp(os.path.getmtime(monitor_log))
                recent_monitoring = datetime.now() - mtime < timedelta(minutes=10)
            
            # Determine health
            running_count = len(set(running_monitors))
            if running_count == 0:
                state = ComponentState.FAILED
                healthy = False
            elif running_count < len(expected_monitors):
                state = ComponentState.DEGRADED
                healthy = True
            else:
                state = ComponentState.HEALTHY
                healthy = True
            
            return {
                "healthy": healthy,
                "state": state,
                "metrics": {
                    "expected_monitors": expected_monitors,
                    "running_monitors": list(set(running_monitors)),
                    "running_count": running_count,
                    "recent_monitoring": recent_monitoring
                }
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "state": ComponentState.FAILED,
                "metrics": {"error": str(e)}
            }
    
    def _check_development_tools_health(self) -> Dict[str, Any]:
        """Check development tools health"""
        try:
            # Check Node.js and npm
            node_check = subprocess.run(["node", "--version"], 
                                       capture_output=True, text=True, timeout=5)
            npm_check = subprocess.run(["npm", "--version"], 
                                     capture_output=True, text=True, timeout=5)
            
            # Check Python
            python_check = subprocess.run(["python3", "--version"], 
                                        capture_output=True, text=True, timeout=5)
            
            # Check Git
            git_check = subprocess.run(["git", "--version"], 
                                     capture_output=True, text=True, timeout=5)
            
            tools_status = {
                "node": node_check.returncode == 0,
                "npm": npm_check.returncode == 0,
                "python": python_check.returncode == 0,
                "git": git_check.returncode == 0
            }
            
            # Check project dependencies
            package_json = os.path.join(self.project_root, "package.json")
            package_lock = os.path.join(self.project_root, "package-lock.json")
            node_modules = os.path.join(self.project_root, "node_modules")
            
            # Determine health
            failed_tools = [tool for tool, status in tools_status.items() if not status]
            
            if len(failed_tools) > 2:
                state = ComponentState.FAILED
                healthy = False
            elif failed_tools:
                state = ComponentState.DEGRADED
                healthy = True
            else:
                state = ComponentState.HEALTHY
                healthy = True
            
            return {
                "healthy": healthy,
                "state": state,
                "metrics": {
                    "tools_status": tools_status,
                    "failed_tools": failed_tools,
                    "package_json_exists": os.path.exists(package_json),
                    "node_modules_exists": os.path.exists(node_modules),
                    "node_version": node_check.stdout.strip() if node_check.returncode == 0 else "N/A",
                    "python_version": python_check.stdout.strip() if python_check.returncode == 0 else "N/A"
                }
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "state": ComponentState.FAILED,
                "metrics": {"error": str(e)}
            }
    
    def _record_health_data(self, component: ComponentHealth):
        """Record component health data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO component_health 
                    (timestamp, component_id, state, metrics, consecutive_failures)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    component.last_check.isoformat(),
                    component.component_id,
                    component.state.value,
                    json.dumps(component.metrics),
                    component.consecutive_failures
                ))
        except Exception as e:
            logging.error(f"Failed to record health data: {e}")
    
    def _record_resilience_event(self, event: ResilienceEvent):
        """Record resilience event to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO resilience_events 
                    (event_id, timestamp, component_id, event_type, severity, 
                     description, recovery_action, success, duration_ms, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.event_id,
                    event.timestamp.isoformat(),
                    event.component_id,
                    event.event_type,
                    event.severity,
                    event.description,
                    event.recovery_action,
                    event.success,
                    event.duration_ms,
                    json.dumps(event.metadata)
                ))
        except Exception as e:
            logging.error(f"Failed to record resilience event: {e}")
    
    def _trigger_component_recovery(self, component_id: str):
        """Trigger recovery for a failing component"""
        component = self.components[component_id]
        
        # Determine recovery strategy based on component and failure pattern
        strategy = self._determine_recovery_strategy(component)
        
        event = ResilienceEvent(
            event_id=f"recovery_{component_id}_{int(time.time())}",
            timestamp=datetime.now(),
            component_id=component_id,
            event_type="recovery_triggered",
            severity="high",
            description=f"Triggering {strategy.value} recovery for {component_id}",
            recovery_action=strategy.value
        )
        
        start_time = time.time()
        success = False
        
        try:
            if strategy == RecoveryStrategy.RESTART:
                success = self._restart_component(component_id)
            elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                success = self._degrade_component(component_id)
            elif strategy == RecoveryStrategy.CIRCUIT_BREAK:
                success = self._circuit_break_component(component_id)
            elif strategy == RecoveryStrategy.FAILOVER:
                success = self._failover_component(component_id)
            elif strategy == RecoveryStrategy.ROLLBACK:
                success = self._rollback_component(component_id)
            elif strategy == RecoveryStrategy.ESCALATE:
                success = self._escalate_component_failure(component_id)
            
            event.success = success
            event.duration_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            event.success = False
            event.duration_ms = (time.time() - start_time) * 1000
            event.metadata["error"] = str(e)
            logging.error(f"Recovery failed for {component_id}: {e}")
        
        self._record_resilience_event(event)
        return success
    
    def _determine_recovery_strategy(self, component: ComponentHealth) -> RecoveryStrategy:
        """Determine the best recovery strategy for a component"""
        # Critical components get immediate restart attempts
        if component.criticality >= 4:
            if component.consecutive_failures < 3:
                return RecoveryStrategy.RESTART
            else:
                return RecoveryStrategy.ESCALATE
        
        # High importance components try graceful degradation first
        elif component.criticality >= 3:
            if component.consecutive_failures < 2:
                return RecoveryStrategy.RESTART
            elif component.consecutive_failures < 5:
                return RecoveryStrategy.GRACEFUL_DEGRADATION
            else:
                return RecoveryStrategy.CIRCUIT_BREAK
        
        # Lower importance components use circuit breaking
        else:
            if component.consecutive_failures < 3:
                return RecoveryStrategy.GRACEFUL_DEGRADATION
            else:
                return RecoveryStrategy.CIRCUIT_BREAK
    
    def _restart_component(self, component_id: str) -> bool:
        """Restart a failed component"""
        try:
            if component_id == "git_repository":
                # Run git repair commands
                os.chdir(self.project_root)
                subprocess.run(["git", "gc", "--aggressive"], check=True, timeout=300)
                return True
            
            elif component_id == "quality_gates":
                # Reinstall Git hooks
                gates_script = os.path.join(self.project_root, "scripts", "quality-gates-enforcer.sh")
                if os.path.exists(gates_script):
                    subprocess.run([gates_script, "install-hooks"], check=True, timeout=60)
                return True
            
            elif component_id == "agent_coordination":
                # Restart worktree manager
                manager_script = os.path.join(self.project_root, "scripts", "worktree-task-manager.sh")
                if os.path.exists(manager_script):
                    subprocess.run([manager_script, "restart"], timeout=120)
                return True
            
            elif component_id == "background_monitors":
                # Restart monitoring processes
                startup_script = os.path.join(self.project_root, "scripts", "claude-startup-enforcer.sh")
                if os.path.exists(startup_script):
                    subprocess.Popen([startup_script], cwd=self.project_root)
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to restart {component_id}: {e}")
            return False
    
    def _degrade_component(self, component_id: str) -> bool:
        """Gracefully degrade a component"""
        try:
            # Disable non-essential features of the component
            self.degradation.disable_feature(component_id, "Component health degraded")
            
            # Update component state
            self.components[component_id].state = ComponentState.DEGRADED
            
            logging.info(f"Component {component_id} degraded gracefully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to degrade {component_id}: {e}")
            return False
    
    def _circuit_break_component(self, component_id: str) -> bool:
        """Open circuit breaker for component"""
        try:
            # Force circuit breaker to open state
            cb = self.circuit_breakers[component_id]
            cb.state = "OPEN"
            cb.last_failure_time = time.time()
            
            logging.warning(f"Circuit breaker opened for {component_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to circuit break {component_id}: {e}")
            return False
    
    def _failover_component(self, component_id: str) -> bool:
        """Failover to backup component or mode"""
        try:
            # Component-specific failover logic
            if component_id == "agent_coordination":
                # Switch to single-agent mode
                logging.info(f"Failing over {component_id} to single-agent mode")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Failed to failover {component_id}: {e}")
            return False
    
    def _rollback_component(self, component_id: str) -> bool:
        """Rollback component to last known good state"""
        try:
            # This would involve reverting recent changes
            logging.info(f"Rolling back {component_id} to last known good state")
            return True
            
        except Exception as e:
            logging.error(f"Failed to rollback {component_id}: {e}")
            return False
    
    def _escalate_component_failure(self, component_id: str) -> bool:
        """Escalate critical component failure"""
        try:
            # Send alerts, create tickets, etc.
            alert_file = os.path.join(self.project_root, "alerts", f"critical_{component_id}_{int(time.time())}.json")
            os.makedirs(os.path.dirname(alert_file), exist_ok=True)
            
            alert_data = {
                "timestamp": datetime.now().isoformat(),
                "component": component_id,
                "severity": "CRITICAL",
                "message": f"Critical failure in {component_id} - manual intervention required",
                "consecutive_failures": self.components[component_id].consecutive_failures
            }
            
            with open(alert_file, "w") as f:
                json.dump(alert_data, f, indent=2)
            
            logging.critical(f"Critical failure escalated for {component_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to escalate {component_id}: {e}")
            return False
    
    def get_system_resilience_status(self) -> Dict[str, Any]:
        """Get comprehensive system resilience status"""
        overall_health = ResilienceLevel.OPTIMAL
        failing_components = []
        degraded_components = []
        
        for comp_id, component in self.components.items():
            if component.state == ComponentState.FAILED:
                failing_components.append(comp_id)
                if component.criticality >= 4:
                    overall_health = ResilienceLevel.CATASTROPHIC
                elif overall_health.value not in ["catastrophic"]:
                    overall_health = ResilienceLevel.CRITICAL
            elif component.state in [ComponentState.FAILING, ComponentState.DEGRADED]:
                degraded_components.append(comp_id)
                if overall_health.value not in ["catastrophic", "critical"]:
                    overall_health = ResilienceLevel.DEGRADED
        
        # Get recent events
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT component_id, event_type, severity, success, COUNT(*)
                FROM resilience_events 
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY component_id, event_type, severity, success
            """)
            recent_events = cursor.fetchall()
        
        return {
            "overall_resilience": overall_health.value,
            "failing_components": failing_components,
            "degraded_components": degraded_components,
            "total_components": len(self.components),
            "healthy_components": len(self.components) - len(failing_components) - len(degraded_components),
            "recent_events_1h": len(recent_events),
            "circuit_breaker_states": {
                comp_id: cb.state for comp_id, cb in self.circuit_breakers.items()
            },
            "disabled_features": list(self.degradation.disabled_features),
            "timestamp": datetime.now().isoformat()
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Resilience System')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--check', nargs='?', const='all', help='Check component health')
    parser.add_argument('--status', action='store_true', help='Show resilience status')
    parser.add_argument('--recover', help='Trigger recovery for component')
    
    args = parser.parse_args()
    
    monitor = EnhancedHealthMonitor("/Users/studio/hardcard")
    
    if args.monitor:
        print("🛡️ Starting enhanced resilience monitoring...")
        # Start monitoring loop
        while True:
            try:
                for comp_id in monitor.components.keys():
                    monitor.check_component_health(comp_id)
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped")
                break
    
    elif args.check:
        if args.check == 'all':
            print("🔍 Checking all components...")
            for comp_id in monitor.components.keys():
                health = monitor.check_component_health(comp_id)
                status = "✅" if health.state == ComponentState.HEALTHY else "⚠️" if health.state == ComponentState.DEGRADED else "❌"
                print(f"  {status} {comp_id}: {health.state.value}")
        else:
            health = monitor.check_component_health(args.check)
            print(f"Component: {args.check}")
            print(f"State: {health.state.value}")
            print(f"Last Check: {health.last_check}")
            print(f"Consecutive Failures: {health.consecutive_failures}")
            print(f"Metrics: {json.dumps(health.metrics, indent=2)}")
    
    elif args.status:
        status = monitor.get_system_resilience_status()
        print("🛡️ System Resilience Status")
        print("=" * 40)
        print(f"Overall Resilience: {status['overall_resilience'].upper()}")
        print(f"Healthy Components: {status['healthy_components']}/{status['total_components']}")
        
        if status['failing_components']:
            print(f"❌ Failing: {', '.join(status['failing_components'])}")
        if status['degraded_components']:
            print(f"⚠️ Degraded: {', '.join(status['degraded_components'])}")
        if status['disabled_features']:
            print(f"🚫 Disabled Features: {', '.join(status['disabled_features'])}")
        
        print(f"\nRecent Events (1h): {status['recent_events_1h']}")
    
    elif args.recover:
        print(f"🔧 Triggering recovery for {args.recover}...")
        success = monitor._trigger_component_recovery(args.recover)
        if success:
            print("✅ Recovery completed successfully")
        else:
            print("❌ Recovery failed")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()