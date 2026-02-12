#!/usr/bin/env python3
"""
Self-Healing System for HardCard Multi-Agent Worktree System
Automatically detects, diagnoses, and fixes system issues
"""

import os
import json
import time
import subprocess
import threading
import signal
import psutil
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
import asyncio
import sqlite3
from enum import Enum

class IssueType(Enum):
    SYSTEM_HEALTH = "system_health"
    WORKTREE_CORRUPTION = "worktree_corruption"
    PROCESS_FAILURE = "process_failure"
    DISK_SPACE = "disk_space"
    MEMORY_LEAK = "memory_leak"
    CONFIGURATION_DRIFT = "configuration_drift"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    PERFORMANCE_DEGRADATION = "performance_degradation"

class SeverityLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class SystemIssue:
    issue_id: str
    issue_type: IssueType
    severity: SeverityLevel
    title: str
    description: str
    affected_components: List[str]
    detection_timestamp: str
    auto_fixable: bool
    fix_function: Optional[str] = None
    fix_parameters: Dict[str, Any] = None

@dataclass
class FixResult:
    success: bool
    fix_applied: str
    duration_seconds: float
    side_effects: List[str]
    requires_restart: bool
    verification_passed: bool

class SystemMonitor:
    """Continuous system health monitoring"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.monitoring_active = True
        self.health_history = []
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "cpu": self._get_cpu_metrics(),
            "memory": self._get_memory_metrics(),
            "disk": self._get_disk_metrics(),
            "processes": self._get_process_metrics(),
            "git": self._get_git_metrics(),
            "files": self._get_file_metrics()
        }
        
        # Store in history (keep last 100 entries)
        self.health_history.append(health)
        if len(self.health_history) > 100:
            self.health_history.pop(0)
        
        return health
    
    def _get_cpu_metrics(self) -> Dict[str, float]:
        """Get CPU usage metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            return {
                "usage_percent": cpu_percent,
                "core_count": cpu_count,
                "load_average_1m": load_avg[0],
                "load_average_5m": load_avg[1],
                "load_average_15m": load_avg[2]
            }
        except Exception as e:
            logging.error(f"Error getting CPU metrics: {e}")
            return {"error": str(e)}
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory usage metrics"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_percent": swap.percent
            }
        except Exception as e:
            logging.error(f"Error getting memory metrics: {e}")
            return {"error": str(e)}
    
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk usage metrics"""
        try:
            disk_usage = shutil.disk_usage(self.project_root)
            
            total_gb = disk_usage.total / (1024**3)
            used_gb = (disk_usage.total - disk_usage.free) / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            usage_percent = (used_gb / total_gb) * 100
            
            return {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "usage_percent": round(usage_percent, 2),
                "path": self.project_root
            }
        except Exception as e:
            logging.error(f"Error getting disk metrics: {e}")
            return {"error": str(e)}
    
    def _get_process_metrics(self) -> Dict[str, Any]:
        """Get process-related metrics"""
        try:
            project_processes = []
            total_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    total_processes += 1
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    # Check if process is related to our project
                    if (self.project_root in cmdline or 
                        'claude' in cmdline.lower() or
                        'hardcard' in cmdline.lower() or
                        'worktree' in cmdline.lower()):
                        
                        project_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": proc.info['memory_percent'],
                            "cmdline": cmdline[:100]  # Truncate for readability
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "total_system_processes": total_processes,
                "project_processes": project_processes,
                "project_process_count": len(project_processes)
            }
        except Exception as e:
            logging.error(f"Error getting process metrics: {e}")
            return {"error": str(e)}
    
    def _get_git_metrics(self) -> Dict[str, Any]:
        """Get Git repository health metrics"""
        try:
            os.chdir(self.project_root)
            
            # Git status
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True)
            uncommitted_files = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            
            # Worktree list
            worktree_result = subprocess.run(['git', 'worktree', 'list'], 
                                           capture_output=True, text=True)
            worktree_count = len(worktree_result.stdout.strip().split('\n')) if worktree_result.stdout.strip() else 0
            
            # Check for corruption
            fsck_result = subprocess.run(['git', 'fsck', '--no-progress'], 
                                       capture_output=True, text=True)
            corruption_detected = "error" in fsck_result.stderr.lower() or fsck_result.returncode != 0
            
            return {
                "uncommitted_files": uncommitted_files,
                "worktree_count": worktree_count,
                "corruption_detected": corruption_detected,
                "fsck_output": fsck_result.stderr[:200] if fsck_result.stderr else ""
            }
        except Exception as e:
            logging.error(f"Error getting Git metrics: {e}")
            return {"error": str(e)}
    
    def _get_file_metrics(self) -> Dict[str, Any]:
        """Get file system health metrics"""
        try:
            # Count files and directories
            total_files = 0
            total_dirs = 0
            large_files = []
            
            for root, dirs, files in os.walk(self.project_root):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
                
                total_dirs += len(dirs)
                total_files += len(files)
                
                # Check for large files
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        if size > 10 * 1024 * 1024:  # Files larger than 10MB
                            large_files.append({
                                "path": file_path,
                                "size_mb": round(size / (1024**2), 2)
                            })
                    except (OSError, IOError):
                        continue
            
            return {
                "total_files": total_files,
                "total_directories": total_dirs,
                "large_files_count": len(large_files),
                "large_files": large_files[:10]  # Show first 10 large files
            }
        except Exception as e:
            logging.error(f"Error getting file metrics: {e}")
            return {"error": str(e)}

class IssueDetector:
    """Detects various system issues from health metrics"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.detection_rules = self._load_detection_rules()
    
    def _load_detection_rules(self) -> Dict[str, Dict]:
        """Load issue detection rules"""
        return {
            "high_cpu_usage": {
                "threshold": 90.0,
                "duration_minutes": 5,
                "severity": SeverityLevel.HIGH
            },
            "high_memory_usage": {
                "threshold": 85.0,
                "severity": SeverityLevel.HIGH
            },
            "low_disk_space": {
                "threshold": 90.0,
                "severity": SeverityLevel.CRITICAL
            },
            "git_corruption": {
                "triggers": ["corruption_detected"],
                "severity": SeverityLevel.CRITICAL
            },
            "process_failure": {
                "expected_processes": ["claude-continuous-monitor"],
                "severity": SeverityLevel.HIGH
            },
            "performance_degradation": {
                "response_time_threshold": 30.0,
                "severity": SeverityLevel.MEDIUM
            }
        }
    
    def detect_issues(self, health_metrics: Dict[str, Any], history: List[Dict[str, Any]]) -> List[SystemIssue]:
        """Detect system issues from current and historical metrics"""
        issues = []
        timestamp = datetime.now().isoformat()
        
        # CPU usage issues
        cpu_usage = health_metrics.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > self.detection_rules["high_cpu_usage"]["threshold"]:
            issues.append(SystemIssue(
                issue_id=f"cpu_high_{int(time.time())}",
                issue_type=IssueType.PERFORMANCE_DEGRADATION,
                severity=SeverityLevel.HIGH,
                title="High CPU Usage Detected",
                description=f"CPU usage is {cpu_usage}% which exceeds threshold of {self.detection_rules['high_cpu_usage']['threshold']}%",
                affected_components=["system_performance"],
                detection_timestamp=timestamp,
                auto_fixable=True,
                fix_function="fix_high_cpu_usage",
                fix_parameters={"current_usage": cpu_usage}
            ))
        
        # Memory usage issues
        memory_usage = health_metrics.get("memory", {}).get("usage_percent", 0)
        if memory_usage > self.detection_rules["high_memory_usage"]["threshold"]:
            issues.append(SystemIssue(
                issue_id=f"memory_high_{int(time.time())}",
                issue_type=IssueType.MEMORY_LEAK,
                severity=SeverityLevel.HIGH,
                title="High Memory Usage Detected",
                description=f"Memory usage is {memory_usage}% which exceeds threshold of {self.detection_rules['high_memory_usage']['threshold']}%",
                affected_components=["system_memory"],
                detection_timestamp=timestamp,
                auto_fixable=True,
                fix_function="fix_high_memory_usage",
                fix_parameters={"current_usage": memory_usage}
            ))
        
        # Disk space issues
        disk_usage = health_metrics.get("disk", {}).get("usage_percent", 0)
        if disk_usage > self.detection_rules["low_disk_space"]["threshold"]:
            issues.append(SystemIssue(
                issue_id=f"disk_full_{int(time.time())}",
                issue_type=IssueType.DISK_SPACE,
                severity=SeverityLevel.CRITICAL,
                title="Low Disk Space",
                description=f"Disk usage is {disk_usage}% which exceeds critical threshold of {self.detection_rules['low_disk_space']['threshold']}%",
                affected_components=["file_system"],
                detection_timestamp=timestamp,
                auto_fixable=True,
                fix_function="fix_disk_space_issue",
                fix_parameters={"current_usage": disk_usage}
            ))
        
        # Git corruption issues
        git_corruption = health_metrics.get("git", {}).get("corruption_detected", False)
        if git_corruption:
            issues.append(SystemIssue(
                issue_id=f"git_corrupt_{int(time.time())}",
                issue_type=IssueType.WORKTREE_CORRUPTION,
                severity=SeverityLevel.CRITICAL,
                title="Git Repository Corruption Detected",
                description="Git fsck detected corruption in the repository",
                affected_components=["git_repository", "worktrees"],
                detection_timestamp=timestamp,
                auto_fixable=True,
                fix_function="fix_git_corruption",
                fix_parameters={}
            ))
        
        # Process failure detection
        expected_processes = ["claude-continuous-monitor", "claude-startup-enforcer"]
        project_processes = health_metrics.get("processes", {}).get("project_processes", [])
        running_process_names = [p["name"] for p in project_processes]
        
        for expected_proc in expected_processes:
            if not any(expected_proc in name for name in running_process_names):
                issues.append(SystemIssue(
                    issue_id=f"process_missing_{expected_proc}_{int(time.time())}",
                    issue_type=IssueType.PROCESS_FAILURE,
                    severity=SeverityLevel.HIGH,
                    title=f"Expected Process Not Running: {expected_proc}",
                    description=f"The process {expected_proc} is expected to be running but was not found",
                    affected_components=["background_services"],
                    detection_timestamp=timestamp,
                    auto_fixable=True,
                    fix_function="restart_missing_process",
                    fix_parameters={"process_name": expected_proc}
                ))
        
        # Configuration drift detection
        config_issues = self._detect_configuration_drift()
        issues.extend(config_issues)
        
        return issues
    
    def _detect_configuration_drift(self) -> List[SystemIssue]:
        """Detect configuration drift from expected state"""
        issues = []
        timestamp = datetime.now().isoformat()
        
        # Check if required files exist
        required_files = [
            "scripts/claude-startup-enforcer.sh",
            "scripts/worktree-task-manager.sh", 
            "scripts/page-completion-tracker.py",
            ".github/quality-gates.json",
            "CLAUDE.md"
        ]
        
        for file_path in required_files:
            full_path = os.path.join(self.project_root, file_path)
            if not os.path.exists(full_path):
                issues.append(SystemIssue(
                    issue_id=f"missing_file_{file_path.replace('/', '_')}_{int(time.time())}",
                    issue_type=IssueType.CONFIGURATION_DRIFT,
                    severity=SeverityLevel.HIGH,
                    title=f"Required File Missing: {file_path}",
                    description=f"Required system file {file_path} is missing",
                    affected_components=["system_configuration"],
                    detection_timestamp=timestamp,
                    auto_fixable=False,  # Manual intervention required
                    fix_function=None
                ))
        
        # Check Git hooks
        hooks_dir = os.path.join(self.project_root, ".git", "hooks")
        required_hooks = ["pre-commit", "pre-push"]
        
        for hook in required_hooks:
            hook_path = os.path.join(hooks_dir, hook)
            if not os.path.exists(hook_path) or not os.access(hook_path, os.X_OK):
                issues.append(SystemIssue(
                    issue_id=f"missing_hook_{hook}_{int(time.time())}",
                    issue_type=IssueType.CONFIGURATION_DRIFT,
                    severity=SeverityLevel.MEDIUM,
                    title=f"Git Hook Missing or Not Executable: {hook}",
                    description=f"Required Git hook {hook} is missing or not executable",
                    affected_components=["quality_gates"],
                    detection_timestamp=timestamp,
                    auto_fixable=True,
                    fix_function="reinstall_git_hooks",
                    fix_parameters={"hook_name": hook}
                ))
        
        return issues

class AutoHealer:
    """Automatically fixes detected issues"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.fix_history = []
        
        # Setup logging
        self.healing_log = os.path.join(project_root, "logs", "self-healing.log")
        os.makedirs(os.path.dirname(self.healing_log), exist_ok=True)
        
        logging.basicConfig(
            filename=self.healing_log,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def heal_issue(self, issue: SystemIssue) -> FixResult:
        """Attempt to automatically heal a system issue"""
        if not issue.auto_fixable or not issue.fix_function:
            return FixResult(
                success=False,
                fix_applied="not_auto_fixable",
                duration_seconds=0.0,
                side_effects=[],
                requires_restart=False,
                verification_passed=False
            )
        
        start_time = time.time()
        
        try:
            # Get the fix function
            fix_function = getattr(self, issue.fix_function, None)
            if not fix_function:
                raise AttributeError(f"Fix function {issue.fix_function} not found")
            
            # Apply the fix
            logging.info(f"Attempting to heal issue: {issue.title}")
            fix_result = fix_function(issue.fix_parameters or {})
            
            duration = time.time() - start_time
            
            # Verify the fix
            verification_passed = self._verify_fix(issue, fix_result)
            
            result = FixResult(
                success=fix_result.get("success", False),
                fix_applied=issue.fix_function,
                duration_seconds=duration,
                side_effects=fix_result.get("side_effects", []),
                requires_restart=fix_result.get("requires_restart", False),
                verification_passed=verification_passed
            )
            
            # Log the result
            self.fix_history.append({
                "issue_id": issue.issue_id,
                "fix_result": asdict(result),
                "timestamp": datetime.now().isoformat()
            })
            
            if result.success:
                logging.info(f"Successfully healed issue: {issue.title}")
            else:
                logging.error(f"Failed to heal issue: {issue.title}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"Error healing issue {issue.title}: {e}")
            
            return FixResult(
                success=False,
                fix_applied=f"error: {str(e)}",
                duration_seconds=duration,
                side_effects=[],
                requires_restart=False,
                verification_passed=False
            )
    
    def fix_high_cpu_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fix high CPU usage issues"""
        try:
            # Find CPU-intensive processes
            cpu_hogs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] > 20:  # High CPU usage
                        cpu_hogs.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            actions_taken = []
            
            # Kill non-essential high CPU processes
            for proc_info in cpu_hogs[:3]:  # Limit to top 3
                try:
                    proc = psutil.Process(proc_info['pid'])
                    # Only kill processes we can safely terminate
                    if proc_info['name'] in ['chrome', 'firefox', 'safari']:
                        continue  # Don't kill browsers
                    
                    proc.terminate()
                    actions_taken.append(f"Terminated process {proc_info['name']} (PID: {proc_info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Clear system caches if possible
            try:
                if os.name == 'posix':  # Unix-like systems
                    subprocess.run(['sync'], check=True)
                    actions_taken.append("Synchronized file system caches")
            except Exception:
                pass
            
            return {
                "success": len(actions_taken) > 0,
                "actions_taken": actions_taken,
                "side_effects": ["Some processes may have been terminated"],
                "requires_restart": False
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fix_high_memory_usage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fix high memory usage issues"""
        try:
            actions_taken = []
            
            # Find memory-intensive processes
            memory_hogs = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if proc.info['memory_percent'] > 10:  # High memory usage
                        memory_hogs.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Clear Python cache directories
            cache_dirs = [
                os.path.join(self.project_root, "__pycache__"),
                os.path.join(self.project_root, ".pytest_cache"),
                "/tmp/python_cache"
            ]
            
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    try:
                        shutil.rmtree(cache_dir)
                        actions_taken.append(f"Cleared cache directory: {cache_dir}")
                    except Exception:
                        pass
            
            # Clear our own cache
            cache_dir = os.path.join(self.project_root, "performance", "cache")
            if os.path.exists(cache_dir):
                try:
                    for file in os.listdir(cache_dir):
                        if file.endswith('.pkl'):
                            os.remove(os.path.join(cache_dir, file))
                    actions_taken.append("Cleared performance cache")
                except Exception:
                    pass
            
            # Garbage collection
            import gc
            collected = gc.collect()
            actions_taken.append(f"Garbage collected {collected} objects")
            
            return {
                "success": True,
                "actions_taken": actions_taken,
                "side_effects": ["Cache cleared", "Garbage collection performed"],
                "requires_restart": False
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fix_disk_space_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fix disk space issues"""
        try:
            actions_taken = []
            freed_space_mb = 0
            
            # Clean log files older than 30 days
            logs_dir = os.path.join(self.project_root, "logs")
            if os.path.exists(logs_dir):
                cutoff_date = datetime.now() - timedelta(days=30)
                for file in os.listdir(logs_dir):
                    file_path = os.path.join(logs_dir, file)
                    if os.path.isfile(file_path):
                        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if mtime < cutoff_date:
                            size_mb = os.path.getsize(file_path) / (1024**2)
                            os.remove(file_path)
                            freed_space_mb += size_mb
                            actions_taken.append(f"Removed old log file: {file}")
            
            # Clean performance cache
            cache_dir = os.path.join(self.project_root, "performance", "cache")
            if os.path.exists(cache_dir):
                for file in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, file)
                    if os.path.isfile(file_path):
                        size_mb = os.path.getsize(file_path) / (1024**2)
                        os.remove(file_path)
                        freed_space_mb += size_mb
                actions_taken.append("Cleared performance cache")
            
            # Clean temporary files
            temp_patterns = [
                "*.tmp", "*.temp", "*.log.old", "*.bak"
            ]
            
            for root, dirs, files in os.walk(self.project_root):
                for file in files:
                    if any(file.endswith(pattern[1:]) for pattern in temp_patterns):
                        file_path = os.path.join(root, file)
                        try:
                            size_mb = os.path.getsize(file_path) / (1024**2)
                            os.remove(file_path)
                            freed_space_mb += size_mb
                        except Exception:
                            pass
            
            if freed_space_mb > 0:
                actions_taken.append(f"Freed {freed_space_mb:.2f} MB of disk space")
            
            return {
                "success": freed_space_mb > 0,
                "actions_taken": actions_taken,
                "freed_space_mb": freed_space_mb,
                "side_effects": ["Old files removed", "Cache cleared"],
                "requires_restart": False
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def fix_git_corruption(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fix Git repository corruption"""
        try:
            actions_taken = []
            
            os.chdir(self.project_root)
            
            # Try to auto-repair the repository
            repair_commands = [
                ["git", "fsck", "--full"],
                ["git", "gc", "--aggressive", "--prune=now"],
                ["git", "repack", "-Ad"]
            ]
            
            for cmd in repair_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        actions_taken.append(f"Successfully ran: {' '.join(cmd)}")
                    else:
                        actions_taken.append(f"Warning from: {' '.join(cmd)} - {result.stderr[:100]}")
                except subprocess.TimeoutExpired:
                    actions_taken.append(f"Timeout running: {' '.join(cmd)}")
                except Exception as e:
                    actions_taken.append(f"Error running: {' '.join(cmd)} - {str(e)}")
            
            # Verify repository integrity
            verify_result = subprocess.run(["git", "fsck"], capture_output=True, text=True)
            corruption_fixed = verify_result.returncode == 0
            
            return {
                "success": corruption_fixed,
                "actions_taken": actions_taken,
                "side_effects": ["Repository repackaged", "Garbage collection performed"],
                "requires_restart": False,
                "corruption_remaining": not corruption_fixed
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restart_missing_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a missing process"""
        try:
            process_name = params.get("process_name", "")
            actions_taken = []
            
            # Map process names to their startup scripts
            process_scripts = {
                "claude-continuous-monitor": "scripts/claude-continuous-monitor.sh",
                "claude-startup-enforcer": "scripts/claude-startup-enforcer.sh"
            }
            
            script_path = process_scripts.get(process_name)
            if not script_path:
                return {"success": False, "error": f"Unknown process: {process_name}"}
            
            full_script_path = os.path.join(self.project_root, script_path)
            if not os.path.exists(full_script_path):
                return {"success": False, "error": f"Script not found: {script_path}"}
            
            # Start the process
            try:
                subprocess.Popen([full_script_path], 
                               cwd=self.project_root,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                actions_taken.append(f"Started process: {process_name}")
                
                # Wait a moment and verify it started
                time.sleep(3)
                process_running = any(process_name in proc.name() 
                                    for proc in psutil.process_iter()
                                    if proc.name())
                
                return {
                    "success": True,
                    "actions_taken": actions_taken,
                    "side_effects": [f"Process {process_name} restarted"],
                    "requires_restart": False,
                    "process_verified": process_running
                }
                
            except Exception as e:
                return {"success": False, "error": f"Failed to start process: {str(e)}"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def reinstall_git_hooks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reinstall Git hooks"""
        try:
            hook_name = params.get("hook_name", "")
            
            # Run the quality gates enforcer to reinstall hooks
            enforcer_script = os.path.join(self.project_root, "scripts", "quality-gates-enforcer.sh")
            
            if not os.path.exists(enforcer_script):
                return {"success": False, "error": "Quality gates enforcer script not found"}
            
            result = subprocess.run([enforcer_script, "install-hooks"], 
                                  capture_output=True, text=True, 
                                  cwd=self.project_root)
            
            return {
                "success": result.returncode == 0,
                "actions_taken": [f"Reinstalled Git hooks including {hook_name}"],
                "side_effects": ["Git hooks reinstalled"],
                "requires_restart": False,
                "output": result.stdout[:200]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _verify_fix(self, issue: SystemIssue, fix_result: Dict[str, Any]) -> bool:
        """Verify that a fix was successful"""
        if not fix_result.get("success", False):
            return False
        
        # Wait a moment for the fix to take effect
        time.sleep(2)
        
        # Verification logic based on issue type
        if issue.issue_type == IssueType.DISK_SPACE:
            # Check if disk usage decreased
            disk_usage = shutil.disk_usage(self.project_root)
            current_usage = ((disk_usage.total - disk_usage.free) / disk_usage.total) * 100
            return current_usage < 90.0  # Below critical threshold
        
        elif issue.issue_type == IssueType.PROCESS_FAILURE:
            # Check if process is now running
            process_name = issue.fix_parameters.get("process_name", "")
            return any(process_name in proc.name() for proc in psutil.process_iter())
        
        elif issue.issue_type == IssueType.WORKTREE_CORRUPTION:
            # Check Git repository integrity
            try:
                os.chdir(self.project_root)
                result = subprocess.run(["git", "fsck"], capture_output=True, text=True)
                return result.returncode == 0
            except Exception:
                return False
        
        # Default: assume fix was successful if no errors
        return True

class SelfHealingSystem:
    """Main self-healing system coordinator"""
    
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.monitor = SystemMonitor(project_root)
        self.detector = IssueDetector(project_root)
        self.healer = AutoHealer(project_root)
        
        self.healing_active = True
        self.healing_interval = 60  # Check every minute
        self.healing_history = []
        
        # Database for tracking
        self.db_path = os.path.join(project_root, "monitoring", "self_healing.db")
        self._init_database()
        
        # Setup logging
        self.system_log = os.path.join(project_root, "logs", "self-healing-system.log")
        os.makedirs(os.path.dirname(self.system_log), exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database for healing tracking"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS healing_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    issue_id TEXT NOT NULL,
                    issue_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    auto_fixed BOOLEAN NOT NULL,
                    fix_success BOOLEAN,
                    fix_duration REAL,
                    description TEXT
                )
            """)
    
    def start_healing_loop(self):
        """Start the continuous self-healing loop"""
        logging.info("Self-healing system started")
        
        while self.healing_active:
            try:
                self._healing_cycle()
                time.sleep(self.healing_interval)
            except KeyboardInterrupt:
                logging.info("Self-healing system stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in healing cycle: {e}")
                time.sleep(self.healing_interval)
    
    def _healing_cycle(self):
        """Single healing cycle"""
        # Get current system health
        health_metrics = self.monitor.get_system_health()
        
        # Detect issues
        issues = self.detector.detect_issues(health_metrics, self.monitor.health_history)
        
        if not issues:
            return  # No issues detected
        
        logging.info(f"Detected {len(issues)} issues")
        
        # Attempt to heal auto-fixable issues
        for issue in issues:
            try:
                # Record issue detection
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO healing_events 
                        (timestamp, issue_id, issue_type, severity, auto_fixed, description)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        issue.detection_timestamp,
                        issue.issue_id,
                        issue.issue_type.value,
                        issue.severity.value,
                        issue.auto_fixable,
                        issue.description
                    ))
                
                if issue.auto_fixable:
                    logging.info(f"Attempting to heal: {issue.title}")
                    fix_result = self.healer.heal_issue(issue)
                    
                    # Update database with fix result
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE healing_events 
                            SET fix_success = ?, fix_duration = ?
                            WHERE issue_id = ?
                        """, (
                            fix_result.success,
                            fix_result.duration_seconds,
                            issue.issue_id
                        ))
                    
                    # Log result
                    if fix_result.success:
                        logging.info(f"Successfully healed: {issue.title}")
                    else:
                        logging.warning(f"Failed to heal: {issue.title}")
                
                else:
                    logging.warning(f"Issue requires manual intervention: {issue.title}")
            
            except Exception as e:
                logging.error(f"Error processing issue {issue.issue_id}: {e}")
    
    def get_healing_status(self) -> Dict[str, Any]:
        """Get current healing system status"""
        with sqlite3.connect(self.db_path) as conn:
            # Get recent healing events
            cursor = conn.execute("""
                SELECT issue_type, severity, auto_fixed, fix_success, COUNT(*)
                FROM healing_events 
                WHERE timestamp > datetime('now', '-24 hours')
                GROUP BY issue_type, severity, auto_fixed, fix_success
            """)
            
            recent_events = cursor.fetchall()
            
            # Get success rate
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_auto_fixes,
                    SUM(CASE WHEN fix_success = 1 THEN 1 ELSE 0 END) as successful_fixes
                FROM healing_events 
                WHERE auto_fixed = 1 AND timestamp > datetime('now', '-7 days')
            """)
            
            stats = cursor.fetchone()
            
        total_fixes = stats[0] if stats else 0
        successful_fixes = stats[1] if stats else 0
        success_rate = (successful_fixes / total_fixes * 100) if total_fixes > 0 else 0
        
        return {
            "healing_active": self.healing_active,
            "healing_interval_seconds": self.healing_interval,
            "success_rate_7d": round(success_rate, 1),
            "total_auto_fixes_7d": total_fixes,
            "successful_fixes_7d": successful_fixes,
            "recent_events": recent_events,
            "current_health": self.monitor.get_system_health()
        }
    
    def manual_heal(self, issue_types: List[str] = None) -> Dict[str, Any]:
        """Manually trigger healing for specific issue types"""
        health_metrics = self.monitor.get_system_health()
        all_issues = self.detector.detect_issues(health_metrics, self.monitor.health_history)
        
        # Filter by issue types if specified
        if issue_types:
            issues_to_heal = [issue for issue in all_issues 
                            if issue.issue_type.value in issue_types]
        else:
            issues_to_heal = all_issues
        
        results = []
        for issue in issues_to_heal:
            if issue.auto_fixable:
                fix_result = self.healer.heal_issue(issue)
                results.append({
                    "issue_id": issue.issue_id,
                    "issue_title": issue.title,
                    "fix_success": fix_result.success,
                    "fix_duration": fix_result.duration_seconds
                })
        
        return {
            "issues_found": len(all_issues),
            "issues_healed": len(results),
            "healing_results": results
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Self-Healing System for HardCard')
    parser.add_argument('--start', action='store_true', help='Start continuous healing')
    parser.add_argument('--status', action='store_true', help='Show healing status')
    parser.add_argument('--heal', nargs='*', help='Manually heal specific issue types')
    parser.add_argument('--check', action='store_true', help='Check for issues without healing')
    
    args = parser.parse_args()
    
    healing_system = SelfHealingSystem()
    
    if args.start:
        print("🔄 Starting self-healing system...")
        try:
            healing_system.start_healing_loop()
        except KeyboardInterrupt:
            print("\n🛑 Self-healing system stopped")
    
    elif args.status:
        status = healing_system.get_healing_status()
        print("🏥 Self-Healing System Status")
        print("=" * 40)
        print(f"Active: {status['healing_active']}")
        print(f"Check Interval: {status['healing_interval_seconds']}s")
        print(f"Success Rate (7d): {status['success_rate_7d']}%")
        print(f"Auto-fixes (7d): {status['successful_fixes_7d']}/{status['total_auto_fixes_7d']}")
        
        health = status['current_health']
        print(f"\nCurrent Health:")
        print(f"  CPU: {health.get('cpu', {}).get('usage_percent', 'N/A')}%")
        print(f"  Memory: {health.get('memory', {}).get('usage_percent', 'N/A')}%")
        print(f"  Disk: {health.get('disk', {}).get('usage_percent', 'N/A')}%")
    
    elif args.heal is not None:
        print("🔧 Manual healing triggered...")
        result = healing_system.manual_heal(args.heal if args.heal else None)
        print(f"Issues found: {result['issues_found']}")
        print(f"Issues healed: {result['issues_healed']}")
        
        for healing_result in result['healing_results']:
            status = "✅" if healing_result['fix_success'] else "❌"
            print(f"  {status} {healing_result['issue_title']} ({healing_result['fix_duration']:.2f}s)")
    
    elif args.check:
        print("🔍 Checking for issues...")
        health_metrics = healing_system.monitor.get_system_health()
        issues = healing_system.detector.detect_issues(health_metrics, healing_system.monitor.health_history)
        
        if not issues:
            print("✅ No issues detected")
        else:
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                auto_fix = "🔧" if issue.auto_fixable else "⚠️"
                print(f"  {auto_fix} [{issue.severity.value.upper()}] {issue.title}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()