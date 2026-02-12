#!/usr/bin/env python3
"""
Advanced Functions Core - Integration of SuperClaude and Claude Engineer Functions
for MOEX and Claude Code Startup System

This module provides the advanced capabilities extracted from the OS4AI refactoring:
- Secure configuration management
- Optimized task management 
- Resource monitoring and circuit breakers
- Input validation and sanitization
- Performance monitoring and metrics
- Redis connection pooling
- Rate limiting and throttling
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
import subprocess
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import signal
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import weakref
import gc

# Try to import Redis - graceful fallback if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class AdvancedFunctionsError(Exception):
    """Base exception for advanced functions"""
    pass

class SecurityError(AdvancedFunctionsError):
    """Security-related errors"""
    pass

class ResourceError(AdvancedFunctionsError):
    """Resource-related errors"""
    pass

class CircuitOpenError(AdvancedFunctionsError):
    """Circuit breaker is open"""
    pass

@dataclass
class SecurityConfig:
    """Security configuration for advanced functions"""
    jwt_secret_key: str = field(default_factory=lambda: secrets.token_hex(32))
    max_input_length: int = 10000
    allowed_commands: List[str] = field(default_factory=lambda: [
        'git', 'npm', 'pip', 'python', 'node', 'ls', 'cat', 'grep', 'find'
    ])
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r'[;&|`]', r'\.\./+', r'rm\s+-rf', r'sudo\s+', r'eval\s*\('
    ])
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

@dataclass
class ResourceConfig:
    """Resource monitoring configuration"""
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    disk_threshold: float = 90.0
    max_concurrent_tasks: int = 5
    task_timeout: int = 300
    cleanup_interval: int = 60

@dataclass
class TaskConfig:
    """Advanced task configuration"""
    name: str
    interval: float
    timeout: float = 30.0
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: float = 1.0
    resource_limits: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)

class InputValidator:
    """Advanced input validation and sanitization"""
    
    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
        import re
        self.blocked_patterns = [re.compile(pattern) for pattern in security_config.blocked_patterns]
    
    def validate_string(self, value: str, field_name: str = "input") -> str:
        """Validate and sanitize string input"""
        if not isinstance(value, str):
            raise SecurityError(f"Invalid type for {field_name}: expected string")
        
        if len(value) > self.config.max_input_length:
            raise SecurityError(f"{field_name} exceeds maximum length")
        
        # Check for dangerous patterns
        for pattern in self.blocked_patterns:
            if pattern.search(value):
                raise SecurityError(f"Dangerous pattern detected in {field_name}")
        
        # Basic sanitization
        sanitized = value.strip()
        return sanitized
    
    def validate_path(self, path: str) -> Path:
        """Validate file paths to prevent directory traversal"""
        path_obj = Path(path).resolve()
        
        # Check for directory traversal
        if '..' in str(path_obj):
            raise SecurityError("Directory traversal detected")
        
        return path_obj
    
    def validate_command(self, command: str, args: List[str]) -> bool:
        """Validate command execution requests"""
        if command not in self.config.allowed_commands:
            raise SecurityError(f"Command not allowed: {command}")
        
        # Validate arguments
        for arg in args:
            self.validate_string(arg, f"command_arg")
        
        return True

class SecureExecutor:
    """Secure command execution with validation"""
    
    def __init__(self, validator: InputValidator):
        self.validator = validator
    
    async def execute_safe_command(
        self, 
        command: str, 
        args: List[str], 
        timeout: float = 30.0,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute commands with security validation"""
        
        # Validate command and arguments
        self.validator.validate_command(command, args)
        
        if cwd:
            cwd_path = self.validator.validate_path(cwd)
        else:
            cwd_path = None
        
        try:
            process = await asyncio.create_subprocess_exec(
                command, *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd_path) if cwd_path else None
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "success": process.returncode == 0
            }
            
        except asyncio.TimeoutError:
            raise ResourceError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise AdvancedFunctionsError(f"Command execution failed: {e}")

class ResourceMonitor:
    """Advanced resource monitoring with thresholds"""
    
    def __init__(self, config: ResourceConfig):
        self.config = config
        self._last_check = 0
        self._check_interval = 5.0  # Check every 5 seconds
        self._cached_stats = {}
    
    def get_system_stats(self) -> Dict[str, float]:
        """Get current system resource statistics"""
        now = time.time()
        if now - self._last_check < self._check_interval:
            return self._cached_stats
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self._cached_stats = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "timestamp": now
            }
            
            self._last_check = now
            return self._cached_stats
            
        except Exception as e:
            logging.warning(f"Failed to get system stats: {e}")
            return {"error": str(e), "timestamp": now}
    
    def can_start_task(self) -> bool:
        """Check if system resources allow starting a new task"""
        stats = self.get_system_stats()
        
        if "error" in stats:
            return False
        
        return (
            stats["cpu_percent"] < self.config.cpu_threshold and
            stats["memory_percent"] < self.config.memory_threshold and
            stats["disk_percent"] < self.config.disk_threshold
        )
    
    def get_resource_pressure(self) -> float:
        """Get overall resource pressure (0.0 to 1.0)"""
        stats = self.get_system_stats()
        
        if "error" in stats:
            return 1.0
        
        pressure = max(
            stats["cpu_percent"] / 100.0,
            stats["memory_percent"] / 100.0,
            stats["disk_percent"] / 100.0
        )
        
        return min(pressure, 1.0)

class CircuitBreaker:
    """Circuit breaker pattern for resilience"""
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

class RateLimiter:
    """Advanced rate limiting with Redis backing"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_cache = {}  # Fallback for when Redis unavailable
        self.cleanup_interval = 300  # Clean local cache every 5 minutes
        self.last_cleanup = time.time()
    
    async def check_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> bool:
        """Check if request is within rate limit"""
        
        if self.redis_client:
            return await self._check_redis_rate_limit(key, limit, window)
        else:
            return self._check_local_rate_limit(key, limit, window)
    
    async def _check_redis_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> bool:
        """Redis-based rate limiting"""
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            result = await pipe.execute()
            
            current_count = result[0]
            return current_count <= limit
            
        except Exception as e:
            logging.warning(f"Redis rate limiting failed: {e}")
            return self._check_local_rate_limit(key, limit, window)
    
    def _check_local_rate_limit(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> bool:
        """Local cache-based rate limiting"""
        now = time.time()
        
        # Cleanup old entries
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_local_cache(now)
        
        if key not in self.local_cache:
            self.local_cache[key] = {"count": 1, "window_start": now}
            return True
        
        entry = self.local_cache[key]
        
        # Reset if window expired
        if now - entry["window_start"] > window:
            entry["count"] = 1
            entry["window_start"] = now
            return True
        
        entry["count"] += 1
        return entry["count"] <= limit
    
    def _cleanup_local_cache(self, now: float):
        """Clean expired entries from local cache"""
        expired_keys = []
        for key, entry in self.local_cache.items():
            if now - entry["window_start"] > 3600:  # Remove entries older than 1 hour
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.local_cache[key]
        
        self.last_cleanup = now

class RedisConnectionPool:
    """Redis connection pool with health monitoring"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", max_connections: int = 10):
        self.redis_url = redis_url
        self.max_connections = max_connections
        self.pool = None
        self.client = None
        self.is_healthy = False
        
    async def initialize(self):
        """Initialize Redis connection pool"""
        if not REDIS_AVAILABLE:
            logging.warning("Redis not available - using fallback")
            return
        
        try:
            self.pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            self.is_healthy = True
            logging.info("Redis connection pool initialized")
            
        except Exception as e:
            logging.warning(f"Redis initialization failed: {e}")
            self.is_healthy = False
    
    @asynccontextmanager
    async def get_connection(self):
        """Get Redis connection from pool"""
        if not self.is_healthy or not self.client:
            raise ResourceError("Redis not available")
        
        try:
            yield self.client
        except Exception as e:
            logging.error(f"Redis operation failed: {e}")
            raise
    
    async def close(self):
        """Close Redis connection pool"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()

class CacheManager:
    """Advanced cache management with TTL and stats"""
    
    def __init__(self, redis_pool: Optional[RedisConnectionPool] = None):
        self.redis_pool = redis_pool
        self.local_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0, "errors": 0}
        self.cleanup_task = None
    
    async def get(self, key: str, default=None):
        """Get value from cache"""
        try:
            if self.redis_pool and self.redis_pool.is_healthy:
                async with self.redis_pool.get_connection() as redis_client:
                    value = await redis_client.get(key)
                    if value:
                        self.cache_stats["hits"] += 1
                        return json.loads(value.decode('utf-8'))
            
            # Fallback to local cache
            if key in self.local_cache:
                entry = self.local_cache[key]
                if time.time() < entry["expires"]:
                    self.cache_stats["hits"] += 1
                    return entry["value"]
                else:
                    del self.local_cache[key]
            
            self.cache_stats["misses"] += 1
            return default
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            logging.warning(f"Cache get failed: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        try:
            json_value = json.dumps(value)
            
            if self.redis_pool and self.redis_pool.is_healthy:
                async with self.redis_pool.get_connection() as redis_client:
                    await redis_client.setex(key, ttl, json_value)
            
            # Also store in local cache as backup
            self.local_cache[key] = {
                "value": value,
                "expires": time.time() + ttl
            }
            
            self.cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            logging.warning(f"Cache set failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            **self.cache_stats
        }

class AdvancedTaskManager:
    """Advanced task manager with resource monitoring and circuit breakers"""
    
    def __init__(
        self, 
        resource_config: ResourceConfig,
        security_config: SecurityConfig,
        redis_pool: Optional[RedisConnectionPool] = None
    ):
        self.resource_config = resource_config
        self.security_config = security_config
        self.redis_pool = redis_pool
        
        # Core components
        self.resource_monitor = ResourceMonitor(resource_config)
        self.validator = InputValidator(security_config)
        self.secure_executor = SecureExecutor(self.validator)
        self.rate_limiter = RateLimiter(redis_pool.client if redis_pool else None)
        self.cache_manager = CacheManager(redis_pool)
        
        # Task management
        self.tasks = {}
        self.task_configs = {}
        self.circuit_breakers = {}
        self.task_stats = {}
        self.active_tasks = set()
        self.shutdown_event = asyncio.Event()
        self.start_time = time.time()
        
        # Cleanup
        self.cleanup_task = None
        
    def register_task(self, config: TaskConfig, task_func: Callable):
        """Register a task with advanced configuration"""
        self.task_configs[config.name] = config
        self.tasks[config.name] = task_func
        self.task_stats[config.name] = {
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "last_execution": None,
            "last_success": None,
            "last_failure": None,
            "total_duration": 0.0,
            "average_duration": 0.0
        }
        
        # Create circuit breaker for task
        self.circuit_breakers[config.name] = CircuitBreaker(
            failure_threshold=config.max_retries,
            timeout=config.retry_delay * 10
        )
        
        logging.info(f"Registered advanced task: {config.name}")
    
    async def start_all_tasks(self):
        """Start all registered tasks"""
        for task_name in self.tasks:
            await self.start_task(task_name)
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logging.info(f"Started {len(self.tasks)} advanced tasks")
    
    async def start_task(self, task_name: str):
        """Start a specific task"""
        if task_name not in self.tasks:
            raise ValueError(f"Task not registered: {task_name}")
        
        config = self.task_configs[task_name]
        task_func = self.tasks[task_name]
        
        # Check dependencies
        for dep in config.dependencies:
            if dep not in self.active_tasks:
                logging.warning(f"Task {task_name} dependency {dep} not active")
        
        # Start task loop
        task = asyncio.create_task(self._task_loop(task_name, config, task_func))
        self.active_tasks.add(task_name)
        
        logging.info(f"Started advanced task: {task_name}")
    
    async def _task_loop(self, task_name: str, config: TaskConfig, task_func: Callable):
        """Advanced task execution loop with monitoring"""
        circuit_breaker = self.circuit_breakers[task_name]
        
        while not self.shutdown_event.is_set():
            try:
                # Resource check
                if not self.resource_monitor.can_start_task():
                    await asyncio.sleep(config.interval * 2)
                    continue
                
                # Rate limiting check
                rate_limit_key = f"task:{task_name}:rate_limit"
                if not await self.rate_limiter.check_rate_limit(
                    rate_limit_key, 
                    limit=60,  # Max 60 executions per minute
                    window=60
                ):
                    await asyncio.sleep(config.interval)
                    continue
                
                # Execute task with circuit breaker
                start_time = time.time()
                
                try:
                    result = await circuit_breaker.call(
                        self._execute_task_safely,
                        task_name,
                        config,
                        task_func
                    )
                    
                    # Update success stats
                    duration = time.time() - start_time
                    self._update_task_stats(task_name, True, duration)
                    
                except CircuitOpenError:
                    logging.warning(f"Circuit breaker open for task: {task_name}")
                    await asyncio.sleep(config.interval * 5)  # Wait longer when circuit is open
                    continue
                    
                except Exception as e:
                    duration = time.time() - start_time
                    self._update_task_stats(task_name, False, duration)
                    logging.error(f"Task {task_name} failed: {e}")
                
                # Wait for next execution
                await asyncio.sleep(config.interval)
                
            except asyncio.CancelledError:
                logging.info(f"Task {task_name} cancelled")
                break
            except Exception as e:
                logging.error(f"Unexpected error in task {task_name}: {e}")
                await asyncio.sleep(config.interval)
    
    async def _execute_task_safely(self, task_name: str, config: TaskConfig, task_func: Callable):
        """Execute task with timeout and error handling"""
        try:
            if asyncio.iscoroutinefunction(task_func):
                result = await asyncio.wait_for(
                    task_func(config),
                    timeout=config.timeout
                )
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    task_func,
                    config
                )
            
            return result
            
        except asyncio.TimeoutError:
            raise ResourceError(f"Task {task_name} timed out after {config.timeout}s")
        except Exception as e:
            raise AdvancedFunctionsError(f"Task {task_name} execution failed: {e}")
    
    def _update_task_stats(self, task_name: str, success: bool, duration: float):
        """Update task execution statistics"""
        stats = self.task_stats[task_name]
        
        stats["execution_count"] += 1
        stats["total_duration"] += duration
        stats["average_duration"] = stats["total_duration"] / stats["execution_count"]
        stats["last_execution"] = time.time()
        
        if success:
            stats["success_count"] += 1
            stats["last_success"] = time.time()
        else:
            stats["failure_count"] += 1
            stats["last_failure"] = time.time()
    
    async def _cleanup_loop(self):
        """Periodic cleanup of resources"""
        while not self.shutdown_event.is_set():
            try:
                # Force garbage collection
                gc.collect()
                
                # Clean rate limiter cache
                if hasattr(self.rate_limiter, '_cleanup_local_cache'):
                    self.rate_limiter._cleanup_local_cache(time.time())
                
                # Log system stats
                system_stats = self.resource_monitor.get_system_stats()
                logging.info(f"System resources: CPU={system_stats.get('cpu_percent', 0):.1f}% "
                           f"Memory={system_stats.get('memory_percent', 0):.1f}%")
                
                await asyncio.sleep(self.resource_config.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    async def stop_all_tasks(self):
        """Stop all tasks gracefully"""
        self.shutdown_event.set()
        
        # Cancel cleanup task
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Wait for tasks to finish
        await asyncio.sleep(2)
        
        logging.info("All advanced tasks stopped")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        system_stats = self.resource_monitor.get_system_stats()
        
        return {
            "uptime_seconds": time.time() - self.start_time,
            "active_task_count": len(self.active_tasks),
            "total_tasks_registered": len(self.tasks),
            "resource_pressure": self.resource_monitor.get_resource_pressure(),
            "system_stats": system_stats,
            "cache_stats": self.cache_manager.get_stats()
        }
    
    def get_task_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed task metrics"""
        metrics = {}
        
        for task_name, stats in self.task_stats.items():
            config = self.task_configs[task_name]
            circuit_breaker = self.circuit_breakers[task_name]
            
            metrics[task_name] = {
                **stats,
                "priority": config.priority.value,
                "interval": config.interval,
                "timeout": config.timeout,
                "circuit_state": circuit_breaker.state.value,
                "failure_count": circuit_breaker.failure_count,
                "success_rate": stats["success_count"] / max(stats["execution_count"], 1)
            }
        
        return metrics

# Factory function to create advanced functions manager
def create_advanced_functions_manager(
    redis_url: str = "redis://localhost:6379",
    security_level: SecurityLevel = SecurityLevel.MEDIUM,
    max_concurrent_tasks: int = 5
) -> AdvancedTaskManager:
    """Create configured advanced functions manager"""
    
    # Configure security based on level
    if security_level == SecurityLevel.HIGH:
        security_config = SecurityConfig(
            max_input_length=5000,
            rate_limit_requests=50,
            rate_limit_window=60
        )
    elif security_level == SecurityLevel.CRITICAL:
        security_config = SecurityConfig(
            max_input_length=1000,
            rate_limit_requests=20,
            rate_limit_window=60
        )
    else:
        security_config = SecurityConfig()
    
    # Configure resources
    resource_config = ResourceConfig(
        max_concurrent_tasks=max_concurrent_tasks
    )
    
    # Initialize Redis if available
    redis_pool = None
    if REDIS_AVAILABLE:
        redis_pool = RedisConnectionPool(redis_url)
    
    # Create manager
    manager = AdvancedTaskManager(
        resource_config=resource_config,
        security_config=security_config,
        redis_pool=redis_pool
    )
    
    return manager

if __name__ == "__main__":
    # Example usage
    async def main():
        logging.basicConfig(level=logging.INFO)
        
        # Create advanced functions manager
        manager = create_advanced_functions_manager(
            security_level=SecurityLevel.HIGH,
            max_concurrent_tasks=3
        )
        
        # Initialize Redis if available
        if manager.redis_pool:
            await manager.redis_pool.initialize()
        
        # Example task
        async def example_task(config: TaskConfig):
            logging.info(f"Executing {config.name}")
            await asyncio.sleep(0.1)
            return {"status": "success", "timestamp": time.time()}
        
        # Register and start task
        task_config = TaskConfig(
            name="example_task",
            interval=5.0,
            timeout=10.0,
            priority=TaskPriority.NORMAL
        )
        
        manager.register_task(task_config, example_task)
        await manager.start_all_tasks()
        
        # Run for a short time
        await asyncio.sleep(15)
        
        # Print metrics
        print("System Metrics:", manager.get_system_metrics())
        print("Task Metrics:", manager.get_task_metrics())
        
        # Stop
        await manager.stop_all_tasks()
        
        if manager.redis_pool:
            await manager.redis_pool.close()
    
    asyncio.run(main())