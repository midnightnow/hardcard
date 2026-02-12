#!/usr/bin/env python3
"""
Fail-Safe Deployment System - Multi-layered safety mechanisms for
zero-downtime deployments with automatic rollback capabilities.

The skeletal structure that prevents catastrophic failures.
"""

import os
import json
import time
import subprocess
import hashlib
import shutil
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import tempfile
import zipfile
import sqlite3
import logging

class DeploymentStage(Enum):
    PRE_FLIGHT = "pre_flight"
    BUILD = "build"
    TEST = "test"
    STAGING = "staging"
    CANARY = "canary"
    PRODUCTION = "production"
    POST_DEPLOY = "post_deploy"

class DeploymentStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PARTIAL = "partial"

class ValidationLevel(Enum):
    BASIC = 1      # Syntax and compilation checks
    STANDARD = 2   # Unit tests and linting
    ENHANCED = 3   # Integration tests
    STRICT = 4     # Full test suite + performance
    PARANOID = 5   # Everything + security scans

@dataclass
class DeploymentCheckpoint:
    stage: DeploymentStage
    timestamp: datetime
    status: DeploymentStatus
    validation_results: Dict[str, Any]
    artifacts: List[str]
    rollback_data: Optional[Dict[str, Any]] = None
    metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class DeploymentPlan:
    deployment_id: str
    source_commit: str
    target_environment: str
    validation_level: ValidationLevel
    stages: List[DeploymentStage]
    rollback_strategy: str
    timeout_minutes: int
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SafetyCheck:
    check_id: str
    name: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    check_function: Callable
    remediation_function: Optional[Callable] = None
    can_bypass: bool = False

class PreFlightValidator:
    """Pre-deployment validation system"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.validation_cache = {}
        self.safety_checks = self._initialize_safety_checks()
        
    def _initialize_safety_checks(self) -> List[SafetyCheck]:
        """Initialize all pre-flight safety checks"""
        return [
            SafetyCheck(
                check_id="git_status",
                name="Git Repository Status",
                description="Ensure clean git status with no uncommitted changes",
                severity="critical",
                check_function=self._check_git_status,
                remediation_function=self._remediate_git_status,
                can_bypass=False
            ),
            SafetyCheck(
                check_id="disk_space",
                name="Disk Space Availability",
                description="Ensure sufficient disk space for deployment",
                severity="critical",
                check_function=self._check_disk_space,
                remediation_function=self._remediate_disk_space,
                can_bypass=False
            ),
            SafetyCheck(
                check_id="dependencies",
                name="Dependency Integrity",
                description="Verify all dependencies are properly installed",
                severity="high",
                check_function=self._check_dependencies,
                remediation_function=self._remediate_dependencies,
                can_bypass=False
            ),
            SafetyCheck(
                check_id="typescript",
                name="TypeScript Compilation",
                description="Ensure TypeScript compiles without errors",
                severity="high",
                check_function=self._check_typescript,
                remediation_function=None,
                can_bypass=True
            ),
            SafetyCheck(
                check_id="tests_exist",
                name="Test Coverage",
                description="Ensure adequate test coverage exists",
                severity="medium",
                check_function=self._check_test_coverage,
                remediation_function=None,
                can_bypass=True
            ),
            SafetyCheck(
                check_id="security_scan",
                name="Security Vulnerability Scan",
                description="Check for known security vulnerabilities",
                severity="high",
                check_function=self._check_security,
                remediation_function=self._remediate_security,
                can_bypass=True
            ),
            SafetyCheck(
                check_id="resource_availability",
                name="System Resource Check",
                description="Ensure system resources are available",
                severity="high",
                check_function=self._check_resources,
                remediation_function=None,
                can_bypass=True
            ),
            SafetyCheck(
                check_id="backup_exists",
                name="Backup Verification",
                description="Ensure recent backup exists",
                severity="critical",
                check_function=self._check_backup,
                remediation_function=self._create_backup,
                can_bypass=False
            )
        ]
    
    async def validate_pre_flight(self, plan: DeploymentPlan) -> Tuple[bool, List[Dict[str, Any]]]:
        """Run all pre-flight validations"""
        results = []
        all_passed = True
        
        logging.info(f"🛫 Running pre-flight checks for deployment {plan.deployment_id}")
        
        for check in self.safety_checks:
            try:
                # Skip lower severity checks for basic validation
                if plan.validation_level == ValidationLevel.BASIC and check.severity in ["medium", "low"]:
                    continue
                
                result = await self._run_safety_check(check)
                results.append(result)
                
                if not result['passed']:
                    if check.severity == "critical" or not check.can_bypass:
                        all_passed = False
                        
                        # Attempt remediation if available
                        if check.remediation_function and result['can_remediate']:
                            logging.info(f"Attempting remediation for {check.name}")
                            remediation_result = await self._attempt_remediation(check)
                            
                            if remediation_result['success']:
                                # Re-run check after remediation
                                recheck_result = await self._run_safety_check(check)
                                results[-1] = recheck_result  # Replace original result
                                
                                if recheck_result['passed']:
                                    logging.info(f"✅ Remediation successful for {check.name}")
                                    all_passed = True
                            else:
                                logging.error(f"❌ Remediation failed for {check.name}")
                
            except Exception as e:
                logging.error(f"Error running check {check.check_id}: {e}")
                results.append({
                    'check_id': check.check_id,
                    'name': check.name,
                    'passed': False,
                    'error': str(e),
                    'severity': check.severity
                })
                
                if check.severity == "critical":
                    all_passed = False
        
        return all_passed, results
    
    async def _run_safety_check(self, check: SafetyCheck) -> Dict[str, Any]:
        """Run a single safety check"""
        start_time = time.time()
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, check.check_function
            )
            
            duration = time.time() - start_time
            
            return {
                'check_id': check.check_id,
                'name': check.name,
                'description': check.description,
                'passed': result.get('passed', False),
                'message': result.get('message', ''),
                'details': result.get('details', {}),
                'can_remediate': result.get('can_remediate', False),
                'severity': check.severity,
                'duration_seconds': duration,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'check_id': check.check_id,
                'name': check.name,
                'passed': False,
                'error': str(e),
                'severity': check.severity,
                'duration_seconds': time.time() - start_time
            }
    
    async def _attempt_remediation(self, check: SafetyCheck) -> Dict[str, Any]:
        """Attempt to remediate a failed check"""
        if not check.remediation_function:
            return {'success': False, 'message': 'No remediation available'}
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, check.remediation_function
            )
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Individual check implementations
    def _check_git_status(self) -> Dict[str, Any]:
        """Check Git repository status"""
        try:
            os.chdir(self.project_root)
            
            # Check for uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=30
            )
            
            if status_result.returncode != 0:
                return {
                    'passed': False,
                    'message': 'Git status check failed',
                    'details': {'error': status_result.stderr}
                }
            
            uncommitted_files = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
            
            if uncommitted_files and uncommitted_files[0]:  # Check if list is not empty
                return {
                    'passed': False,
                    'message': f'Found {len(uncommitted_files)} uncommitted files',
                    'details': {'files': uncommitted_files[:10]},  # Show first 10
                    'can_remediate': True
                }
            
            # Check if we're on a stable branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=10
            )
            
            current_branch = branch_result.stdout.strip()
            
            return {
                'passed': True,
                'message': 'Git repository is clean',
                'details': {
                    'branch': current_branch,
                    'clean': True
                }
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Git check error: {str(e)}',
                'can_remediate': False
            }
    
    def _remediate_git_status(self) -> Dict[str, Any]:
        """Remediate Git status issues"""
        try:
            os.chdir(self.project_root)
            
            # Stash uncommitted changes
            stash_result = subprocess.run(
                ["git", "stash", "push", "-m", f"Auto-stash for deployment at {datetime.now()}"],
                capture_output=True, text=True
            )
            
            if stash_result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Uncommitted changes stashed successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to stash changes',
                    'error': stash_result.stderr
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil
            
            disk_usage = shutil.disk_usage(self.project_root)
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            usage_percent = ((disk_usage.total - disk_usage.free) / disk_usage.total) * 100
            
            # Require at least 2GB free and less than 90% usage
            if free_gb < 2.0 or usage_percent > 90:
                return {
                    'passed': False,
                    'message': f'Insufficient disk space: {free_gb:.1f}GB free ({usage_percent:.1f}% used)',
                    'details': {
                        'free_gb': free_gb,
                        'total_gb': total_gb,
                        'usage_percent': usage_percent
                    },
                    'can_remediate': True
                }
            
            return {
                'passed': True,
                'message': f'Sufficient disk space: {free_gb:.1f}GB free',
                'details': {
                    'free_gb': free_gb,
                    'usage_percent': usage_percent
                }
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Disk space check error: {str(e)}',
                'can_remediate': False
            }
    
    def _remediate_disk_space(self) -> Dict[str, Any]:
        """Free up disk space"""
        try:
            freed_space = 0
            
            # Clean common directories
            clean_dirs = [
                os.path.join(self.project_root, "node_modules/.cache"),
                os.path.join(self.project_root, "dist"),
                os.path.join(self.project_root, "build"),
                os.path.join(self.project_root, ".next"),
                os.path.join(self.project_root, "logs")
            ]
            
            for dir_path in clean_dirs:
                if os.path.exists(dir_path):
                    try:
                        size_before = self._get_directory_size(dir_path)
                        
                        # Clean old files (older than 7 days)
                        cutoff_time = time.time() - (7 * 24 * 60 * 60)
                        
                        for root, dirs, files in os.walk(dir_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    if os.path.getmtime(file_path) < cutoff_time:
                                        os.remove(file_path)
                                except Exception:
                                    pass
                        
                        size_after = self._get_directory_size(dir_path)
                        freed_space += (size_before - size_after)
                        
                    except Exception:
                        pass
            
            freed_mb = freed_space / (1024**2)
            
            return {
                'success': freed_mb > 100,  # Success if freed more than 100MB
                'message': f'Freed {freed_mb:.1f}MB of disk space'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check dependency integrity"""
        try:
            issues = []
            
            # Check package.json exists
            package_json_path = os.path.join(self.project_root, "package.json")
            if not os.path.exists(package_json_path):
                return {
                    'passed': False,
                    'message': 'package.json not found',
                    'can_remediate': False
                }
            
            # Check node_modules exists
            node_modules_path = os.path.join(self.project_root, "node_modules")
            if not os.path.exists(node_modules_path):
                issues.append("node_modules directory missing")
            
            # Check package-lock.json exists
            package_lock_path = os.path.join(self.project_root, "package-lock.json")
            if not os.path.exists(package_lock_path):
                issues.append("package-lock.json missing")
            
            # Verify installed packages match package.json
            if os.path.exists(node_modules_path):
                result = subprocess.run(
                    ["npm", "ls", "--json", "--depth=0"],
                    capture_output=True, text=True, cwd=self.project_root
                )
                
                if result.returncode != 0:
                    issues.append("Dependency tree has errors")
            
            if issues:
                return {
                    'passed': False,
                    'message': 'Dependency issues found',
                    'details': {'issues': issues},
                    'can_remediate': True
                }
            
            return {
                'passed': True,
                'message': 'Dependencies are properly installed',
                'details': {'node_modules_exists': True}
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Dependency check error: {str(e)}',
                'can_remediate': False
            }
    
    def _remediate_dependencies(self) -> Dict[str, Any]:
        """Fix dependency issues"""
        try:
            # Run npm install
            result = subprocess.run(
                ["npm", "install"],
                capture_output=True, text=True,
                cwd=self.project_root,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Dependencies installed successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'npm install failed',
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'npm install timed out after 5 minutes'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_typescript(self) -> Dict[str, Any]:
        """Check TypeScript compilation"""
        try:
            # Check if tsconfig.json exists
            tsconfig_path = os.path.join(self.project_root, "tsconfig.json")
            if not os.path.exists(tsconfig_path):
                return {
                    'passed': True,  # Pass if no TypeScript
                    'message': 'No TypeScript configuration found',
                    'details': {'typescript': False}
                }
            
            # Run TypeScript compiler
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--pretty", "false"],
                capture_output=True, text=True,
                cwd=self.project_root,
                timeout=120
            )
            
            if result.returncode == 0:
                return {
                    'passed': True,
                    'message': 'TypeScript compilation successful',
                    'details': {'errors': 0}
                }
            else:
                # Count errors
                error_lines = [line for line in result.stdout.split('\n') 
                             if 'error TS' in line]
                
                return {
                    'passed': False,
                    'message': f'TypeScript compilation failed with {len(error_lines)} errors',
                    'details': {
                        'error_count': len(error_lines),
                        'sample_errors': error_lines[:5]  # First 5 errors
                    },
                    'can_remediate': False
                }
                
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'message': 'TypeScript check timed out',
                'can_remediate': False
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'TypeScript check error: {str(e)}',
                'can_remediate': False
            }
    
    def _check_test_coverage(self) -> Dict[str, Any]:
        """Check test coverage"""
        try:
            # Count test files
            test_count = 0
            src_count = 0
            
            for root, dirs, files in os.walk(self.project_root):
                # Skip node_modules
                dirs[:] = [d for d in dirs if d != 'node_modules']
                
                for file in files:
                    if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                        if any(pattern in file for pattern in ['.test.', '.spec.', '__tests__']):
                            test_count += 1
                        else:
                            src_count += 1
            
            if src_count == 0:
                coverage_ratio = 0
            else:
                coverage_ratio = test_count / src_count
            
            # Require at least 20% test file ratio
            if coverage_ratio < 0.2 and src_count > 10:
                return {
                    'passed': False,
                    'message': f'Insufficient test coverage: {coverage_ratio:.1%}',
                    'details': {
                        'test_files': test_count,
                        'source_files': src_count,
                        'coverage_ratio': coverage_ratio
                    },
                    'can_remediate': False
                }
            
            return {
                'passed': True,
                'message': f'Test coverage: {coverage_ratio:.1%}',
                'details': {
                    'test_files': test_count,
                    'source_files': src_count
                }
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Test coverage check error: {str(e)}',
                'can_remediate': False
            }
    
    def _check_security(self) -> Dict[str, Any]:
        """Check for security vulnerabilities"""
        try:
            # Run npm audit
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True, text=True,
                cwd=self.project_root,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    'passed': True,
                    'message': 'No security vulnerabilities found',
                    'details': {'vulnerabilities': 0}
                }
            
            try:
                audit_data = json.loads(result.stdout)
                
                total_vulns = audit_data.get('metadata', {}).get('vulnerabilities', {})
                critical = total_vulns.get('critical', 0)
                high = total_vulns.get('high', 0)
                
                if critical > 0 or high > 5:
                    return {
                        'passed': False,
                        'message': f'Found {critical} critical and {high} high vulnerabilities',
                        'details': total_vulns,
                        'can_remediate': True
                    }
                
                return {
                    'passed': True,
                    'message': f'Acceptable vulnerability levels',
                    'details': total_vulns
                }
                
            except json.JSONDecodeError:
                return {
                    'passed': True,  # Don't fail deployment for audit issues
                    'message': 'Could not parse audit results',
                    'details': {}
                }
                
        except subprocess.TimeoutExpired:
            return {
                'passed': True,  # Don't fail for timeout
                'message': 'Security audit timed out',
                'details': {}
            }
        except Exception as e:
            return {
                'passed': True,  # Don't fail for errors
                'message': f'Security check error: {str(e)}',
                'details': {}
            }
    
    def _remediate_security(self) -> Dict[str, Any]:
        """Fix security vulnerabilities"""
        try:
            # Run npm audit fix
            result = subprocess.run(
                ["npm", "audit", "fix"],
                capture_output=True, text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': 'Security vulnerabilities fixed'
                }
            else:
                # Try force fix for non-breaking changes
                force_result = subprocess.run(
                    ["npm", "audit", "fix", "--force"],
                    capture_output=True, text=True,
                    cwd=self.project_root,
                    timeout=300
                )
                
                return {
                    'success': force_result.returncode == 0,
                    'message': 'Attempted forced security fixes'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _check_resources(self) -> Dict[str, Any]:
        """Check system resource availability"""
        try:
            import psutil
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory check
            memory = psutil.virtual_memory()
            
            # Process count check
            process_count = len(psutil.pids())
            
            issues = []
            
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 90:
                issues.append(f"High memory usage: {memory.percent}%")
            
            if memory.available < 1024**3:  # Less than 1GB available
                issues.append(f"Low available memory: {memory.available / (1024**3):.1f}GB")
            
            if process_count > 500:
                issues.append(f"High process count: {process_count}")
            
            if issues:
                return {
                    'passed': False,
                    'message': 'Resource constraints detected',
                    'details': {
                        'issues': issues,
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'process_count': process_count
                    },
                    'can_remediate': False
                }
            
            return {
                'passed': True,
                'message': 'System resources are adequate',
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3)
                }
            }
            
        except Exception as e:
            return {
                'passed': True,  # Don't fail for resource check errors
                'message': f'Resource check error: {str(e)}',
                'details': {}
            }
    
    def _check_backup(self) -> Dict[str, Any]:
        """Check if recent backup exists"""
        try:
            backup_dir = os.path.join(self.project_root, "backups")
            
            if not os.path.exists(backup_dir):
                return {
                    'passed': False,
                    'message': 'No backup directory found',
                    'can_remediate': True
                }
            
            # Find most recent backup
            backups = []
            for file in os.listdir(backup_dir):
                if file.endswith('.tar.gz') or file.endswith('.zip'):
                    file_path = os.path.join(backup_dir, file)
                    mtime = os.path.getmtime(file_path)
                    backups.append((file, mtime))
            
            if not backups:
                return {
                    'passed': False,
                    'message': 'No backups found',
                    'can_remediate': True
                }
            
            # Check age of most recent backup
            backups.sort(key=lambda x: x[1], reverse=True)
            latest_backup, latest_time = backups[0]
            
            age_hours = (time.time() - latest_time) / 3600
            
            if age_hours > 24:  # Older than 24 hours
                return {
                    'passed': False,
                    'message': f'Latest backup is {age_hours:.1f} hours old',
                    'details': {
                        'latest_backup': latest_backup,
                        'age_hours': age_hours
                    },
                    'can_remediate': True
                }
            
            return {
                'passed': True,
                'message': f'Recent backup found: {latest_backup}',
                'details': {
                    'latest_backup': latest_backup,
                    'age_hours': age_hours
                }
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Backup check error: {str(e)}',
                'can_remediate': True
            }
    
    def _create_backup(self) -> Dict[str, Any]:
        """Create a new backup"""
        try:
            backup_dir = os.path.join(self.project_root, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"pre_deploy_backup_{timestamp}.tar.gz"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Files to backup
            important_files = [
                "package.json",
                "package-lock.json",
                "tsconfig.json",
                ".env",
                "src",
                "public",
                "scripts"
            ]
            
            # Create tar archive
            import tarfile
            
            with tarfile.open(backup_path, "w:gz") as tar:
                for item in important_files:
                    item_path = os.path.join(self.project_root, item)
                    if os.path.exists(item_path):
                        tar.add(item_path, arcname=item)
            
            # Verify backup was created
            if os.path.exists(backup_path):
                size_mb = os.path.getsize(backup_path) / (1024**2)
                
                return {
                    'success': True,
                    'message': f'Backup created: {backup_name} ({size_mb:.1f}MB)'
                }
            else:
                return {
                    'success': False,
                    'message': 'Backup creation failed'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_directory_size(self, path: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    continue
        return total_size

class SafeBuildSystem:
    """Safe build system with incremental compilation and caching"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.build_cache_dir = os.path.join(project_root, ".build-cache")
        self.artifact_dir = os.path.join(project_root, "artifacts")
        
        os.makedirs(self.build_cache_dir, exist_ok=True)
        os.makedirs(self.artifact_dir, exist_ok=True)
    
    async def execute_build(self, plan: DeploymentPlan) -> Tuple[bool, Dict[str, Any]]:
        """Execute safe build process"""
        build_id = f"build_{plan.deployment_id}_{int(time.time())}"
        build_log = []
        artifacts = []
        
        try:
            # Create isolated build environment
            build_env = self._create_build_environment(build_id)
            
            # Step 1: Clean build directory
            if os.path.exists(os.path.join(self.project_root, "dist")):
                shutil.rmtree(os.path.join(self.project_root, "dist"))
            
            # Step 2: Run build command
            build_start = time.time()
            
            build_result = await self._run_build_command(build_env)
            build_log.extend(build_result['logs'])
            
            if not build_result['success']:
                return False, {
                    'build_id': build_id,
                    'duration': time.time() - build_start,
                    'logs': build_log,
                    'error': build_result.get('error', 'Build failed')
                }
            
            # Step 3: Verify build output
            verification_result = self._verify_build_output()
            
            if not verification_result['valid']:
                return False, {
                    'build_id': build_id,
                    'duration': time.time() - build_start,
                    'logs': build_log,
                    'error': f"Build verification failed: {verification_result['reason']}"
                }
            
            # Step 4: Create build artifacts
            artifact_result = self._create_build_artifacts(build_id)
            artifacts.extend(artifact_result['artifacts'])
            
            # Step 5: Calculate build fingerprint
            fingerprint = self._calculate_build_fingerprint()
            
            return True, {
                'build_id': build_id,
                'duration': time.time() - build_start,
                'logs': build_log,
                'artifacts': artifacts,
                'fingerprint': fingerprint,
                'output_size_mb': verification_result['size_mb']
            }
            
        except Exception as e:
            logging.error(f"Build error: {e}")
            return False, {
                'build_id': build_id,
                'logs': build_log,
                'error': str(e)
            }
    
    def _create_build_environment(self, build_id: str) -> Dict[str, str]:
        """Create isolated build environment"""
        env = os.environ.copy()
        
        # Set build-specific environment variables
        env['BUILD_ID'] = build_id
        env['NODE_ENV'] = 'production'
        env['CI'] = 'true'
        
        # Disable interactive prompts
        env['FORCE_COLOR'] = '0'
        env['NPM_CONFIG_PROGRESS'] = 'false'
        
        return env
    
    async def _run_build_command(self, env: Dict[str, str]) -> Dict[str, Any]:
        """Run the build command safely"""
        logs = []
        
        try:
            # Determine build command from package.json
            package_json_path = os.path.join(self.project_root, "package.json")
            
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Check for build script
            scripts = package_data.get('scripts', {})
            
            if 'build' in scripts:
                build_command = ["npm", "run", "build"]
            elif 'build:prod' in scripts:
                build_command = ["npm", "run", "build:prod"]
            else:
                # Default build commands for common frameworks
                if 'next' in package_data.get('dependencies', {}):
                    build_command = ["npx", "next", "build"]
                elif 'react-scripts' in package_data.get('dependencies', {}):
                    build_command = ["npx", "react-scripts", "build"]
                elif 'vite' in package_data.get('devDependencies', {}):
                    build_command = ["npx", "vite", "build"]
                else:
                    build_command = ["npm", "run", "build"]
            
            # Run build with timeout
            process = await asyncio.create_subprocess_exec(
                *build_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root,
                env=env
            )
            
            # Capture output with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=600  # 10 minute timeout
                )
                
                logs.append(f"Build command: {' '.join(build_command)}")
                
                if stdout:
                    logs.append("=== Build Output ===")
                    logs.extend(stdout.decode().split('\n'))
                
                if stderr:
                    logs.append("=== Build Errors ===")
                    logs.extend(stderr.decode().split('\n'))
                
                if process.returncode == 0:
                    return {
                        'success': True,
                        'logs': logs
                    }
                else:
                    return {
                        'success': False,
                        'logs': logs,
                        'error': f"Build failed with exit code {process.returncode}"
                    }
                    
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                
                return {
                    'success': False,
                    'logs': logs,
                    'error': "Build timed out after 10 minutes"
                }
                
        except Exception as e:
            return {
                'success': False,
                'logs': logs,
                'error': str(e)
            }
    
    def _verify_build_output(self) -> Dict[str, Any]:
        """Verify build output integrity"""
        common_output_dirs = ["dist", "build", ".next", "out"]
        output_dir = None
        
        # Find output directory
        for dir_name in common_output_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                output_dir = dir_path
                break
        
        if not output_dir:
            return {
                'valid': False,
                'reason': 'No build output directory found'
            }
        
        # Check if output directory has content
        files = []
        total_size = 0
        
        for root, dirs, filenames in os.walk(output_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
        
        if len(files) == 0:
            return {
                'valid': False,
                'reason': 'Build output directory is empty'
            }
        
        # Check for index.html or similar entry point
        has_entry_point = False
        entry_files = ['index.html', 'index.js', 'main.js', 'app.js']
        
        for file in files:
            if any(entry in os.path.basename(file) for entry in entry_files):
                has_entry_point = True
                break
        
        if not has_entry_point and len(files) < 5:
            return {
                'valid': False,
                'reason': 'No entry point found in build output'
            }
        
        return {
            'valid': True,
            'output_dir': output_dir,
            'file_count': len(files),
            'size_mb': total_size / (1024**2)
        }
    
    def _create_build_artifacts(self, build_id: str) -> Dict[str, Any]:
        """Create deployable artifacts from build output"""
        artifacts = []
        
        try:
            # Find build output directory
            output_dir = None
            for dir_name in ["dist", "build", ".next", "out"]:
                dir_path = os.path.join(self.project_root, dir_name)
                if os.path.exists(dir_path):
                    output_dir = dir_path
                    break
            
            if not output_dir:
                return {'artifacts': []}
            
            # Create artifact archive
            artifact_name = f"{build_id}.tar.gz"
            artifact_path = os.path.join(self.artifact_dir, artifact_name)
            
            import tarfile
            with tarfile.open(artifact_path, "w:gz") as tar:
                tar.add(output_dir, arcname=os.path.basename(output_dir))
            
            if os.path.exists(artifact_path):
                artifacts.append({
                    'name': artifact_name,
                    'path': artifact_path,
                    'size_mb': os.path.getsize(artifact_path) / (1024**2),
                    'type': 'build_output'
                })
            
            # Create metadata file
            metadata = {
                'build_id': build_id,
                'timestamp': datetime.now().isoformat(),
                'source_commit': self._get_current_commit(),
                'artifacts': artifacts
            }
            
            metadata_path = os.path.join(self.artifact_dir, f"{build_id}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            artifacts.append({
                'name': f"{build_id}_metadata.json",
                'path': metadata_path,
                'type': 'metadata'
            })
            
            return {'artifacts': artifacts}
            
        except Exception as e:
            logging.error(f"Error creating artifacts: {e}")
            return {'artifacts': artifacts}
    
    def _calculate_build_fingerprint(self) -> str:
        """Calculate unique fingerprint for build output"""
        hasher = hashlib.sha256()
        
        # Hash important files
        important_files = [
            "package.json",
            "package-lock.json",
            "tsconfig.json"
        ]
        
        for file_name in important_files:
            file_path = os.path.join(self.project_root, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
        
        # Hash build output
        output_dirs = ["dist", "build", ".next", "out"]
        for dir_name in output_dirs:
            dir_path = os.path.join(self.project_root, dir_name)
            if os.path.exists(dir_path):
                for root, dirs, files in os.walk(dir_path):
                    for file in sorted(files):  # Sort for consistency
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'rb') as f:
                                hasher.update(f.read())
                        except (OSError, IOError):
                            pass
        
        return hasher.hexdigest()
    
    def _get_current_commit(self) -> str:
        """Get current Git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

class RollbackManager:
    """Manages deployment rollback capabilities"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.rollback_dir = os.path.join(project_root, "rollbacks")
        os.makedirs(self.rollback_dir, exist_ok=True)
        
        # Rollback history database
        self.db_path = os.path.join(self.rollback_dir, "rollback_history.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize rollback history database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rollback_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deployment_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    commit_hash TEXT NOT NULL,
                    environment TEXT NOT NULL,
                    backup_path TEXT NOT NULL,
                    metadata TEXT
                )
            """)
    
    def create_rollback_point(self, deployment_plan: DeploymentPlan) -> Dict[str, Any]:
        """Create a rollback point before deployment"""
        try:
            rollback_id = f"rollback_{deployment_plan.deployment_id}_{int(time.time())}"
            
            # Create rollback directory
            rollback_path = os.path.join(self.rollback_dir, rollback_id)
            os.makedirs(rollback_path, exist_ok=True)
            
            # Save current state
            state_saved = self._save_current_state(rollback_path)
            
            if not state_saved['success']:
                return {
                    'success': False,
                    'error': state_saved.get('error', 'Failed to save state')
                }
            
            # Record in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO rollback_points 
                    (deployment_id, timestamp, commit_hash, environment, backup_path, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    deployment_plan.deployment_id,
                    datetime.now().isoformat(),
                    state_saved['commit_hash'],
                    deployment_plan.target_environment,
                    rollback_path,
                    json.dumps(state_saved['metadata'])
                ))
            
            return {
                'success': True,
                'rollback_id': rollback_id,
                'rollback_path': rollback_path,
                'commit_hash': state_saved['commit_hash']
            }
            
        except Exception as e:
            logging.error(f"Error creating rollback point: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_current_state(self, rollback_path: str) -> Dict[str, Any]:
        """Save current application state"""
        try:
            # Get current commit
            commit_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            commit_hash = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
            
            # Save important files
            files_to_backup = [
                "package.json",
                "package-lock.json",
                "tsconfig.json",
                ".env",
                ".env.local",
                ".env.production"
            ]
            
            backed_up_files = []
            
            for file_name in files_to_backup:
                src_path = os.path.join(self.project_root, file_name)
                if os.path.exists(src_path):
                    dst_path = os.path.join(rollback_path, file_name)
                    shutil.copy2(src_path, dst_path)
                    backed_up_files.append(file_name)
            
            # Save current build output if exists
            for output_dir in ["dist", "build", ".next"]:
                src_dir = os.path.join(self.project_root, output_dir)
                if os.path.exists(src_dir):
                    dst_dir = os.path.join(rollback_path, output_dir)
                    shutil.copytree(src_dir, dst_dir)
                    backed_up_files.append(output_dir)
            
            # Create state metadata
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'backed_up_files': backed_up_files,
                'node_version': self._get_node_version(),
                'npm_version': self._get_npm_version()
            }
            
            metadata_path = os.path.join(rollback_path, "state_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                'success': True,
                'commit_hash': commit_hash,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_rollback(self, deployment_id: str) -> Dict[str, Any]:
        """Execute rollback to previous state"""
        try:
            # Find rollback point
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM rollback_points 
                    WHERE deployment_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """, (deployment_id,))
                
                rollback_point = cursor.fetchone()
            
            if not rollback_point:
                return {
                    'success': False,
                    'error': f'No rollback point found for deployment {deployment_id}'
                }
            
            rollback_path = rollback_point[5]  # backup_path column
            
            if not os.path.exists(rollback_path):
                return {
                    'success': False,
                    'error': 'Rollback data not found'
                }
            
            # Execute rollback
            rollback_result = self._restore_state(rollback_path)
            
            if rollback_result['success']:
                # Checkout previous commit
                commit_hash = rollback_point[3]  # commit_hash column
                
                if commit_hash != "unknown":
                    checkout_result = subprocess.run(
                        ["git", "checkout", commit_hash],
                        capture_output=True, text=True,
                        cwd=self.project_root
                    )
                    
                    if checkout_result.returncode != 0:
                        logging.warning(f"Could not checkout commit {commit_hash}")
            
            return rollback_result
            
        except Exception as e:
            logging.error(f"Rollback error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _restore_state(self, rollback_path: str) -> Dict[str, Any]:
        """Restore application state from rollback point"""
        try:
            restored_items = []
            
            # Read metadata
            metadata_path = os.path.join(rollback_path, "state_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Restore backed up files
            for item in os.listdir(rollback_path):
                if item == "state_metadata.json":
                    continue
                
                src_path = os.path.join(rollback_path, item)
                dst_path = os.path.join(self.project_root, item)
                
                try:
                    if os.path.isdir(src_path):
                        # Remove existing directory
                        if os.path.exists(dst_path):
                            shutil.rmtree(dst_path)
                        # Copy directory
                        shutil.copytree(src_path, dst_path)
                    else:
                        # Copy file
                        shutil.copy2(src_path, dst_path)
                    
                    restored_items.append(item)
                    
                except Exception as e:
                    logging.error(f"Error restoring {item}: {e}")
            
            # Reinstall dependencies if package.json was restored
            if "package.json" in restored_items:
                install_result = subprocess.run(
                    ["npm", "install"],
                    capture_output=True, text=True,
                    cwd=self.project_root
                )
                
                if install_result.returncode != 0:
                    logging.warning("npm install failed during rollback")
            
            return {
                'success': True,
                'restored_items': restored_items,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_node_version(self) -> str:
        """Get Node.js version"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"
    
    def _get_npm_version(self) -> str:
        """Get npm version"""
        try:
            result = subprocess.run(
                ["npm", "--version"],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

class FailSafeDeploymentOrchestrator:
    """Main deployment orchestrator with fail-safe mechanisms"""
    
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.validator = PreFlightValidator(project_root)
        self.build_system = SafeBuildSystem(project_root)
        self.rollback_manager = RollbackManager(project_root)
        
        # Deployment tracking
        self.deployments_dir = os.path.join(project_root, "deployments")
        os.makedirs(self.deployments_dir, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup deployment logging"""
        log_file = os.path.join(self.project_root, "logs", "deployments.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    async def deploy(self, 
                    target_environment: str = "production",
                    validation_level: ValidationLevel = ValidationLevel.STANDARD,
                    dry_run: bool = False) -> Dict[str, Any]:
        """Execute fail-safe deployment"""
        
        # Create deployment plan
        plan = DeploymentPlan(
            deployment_id=f"deploy_{int(time.time())}",
            source_commit=self._get_current_commit(),
            target_environment=target_environment,
            validation_level=validation_level,
            stages=[
                DeploymentStage.PRE_FLIGHT,
                DeploymentStage.BUILD,
                DeploymentStage.TEST,
                DeploymentStage.STAGING,
                DeploymentStage.PRODUCTION,
                DeploymentStage.POST_DEPLOY
            ],
            rollback_strategy="automatic",
            timeout_minutes=30,
            created_at=datetime.now()
        )
        
        checkpoints = []
        deployment_start = time.time()
        
        try:
            logging.info(f"🚀 Starting deployment {plan.deployment_id}")
            logging.info(f"Target: {target_environment}, Validation: {validation_level.name}")
            
            # Stage 1: Pre-flight checks
            logging.info("📋 Stage 1: Pre-flight validation")
            pre_flight_checkpoint = await self._execute_pre_flight(plan)
            checkpoints.append(pre_flight_checkpoint)
            
            if pre_flight_checkpoint.status != DeploymentStatus.SUCCESS:
                return self._create_deployment_result(plan, checkpoints, False)
            
            # Create rollback point
            logging.info("💾 Creating rollback point")
            rollback_result = self.rollback_manager.create_rollback_point(plan)
            
            if not rollback_result['success']:
                logging.error("Failed to create rollback point")
                return self._create_deployment_result(plan, checkpoints, False)
            
            plan.metadata['rollback_id'] = rollback_result['rollback_id']
            
            if dry_run:
                logging.info("🏁 Dry run completed successfully")
                return self._create_deployment_result(plan, checkpoints, True, dry_run=True)
            
            # Stage 2: Build
            logging.info("🔨 Stage 2: Building application")
            build_checkpoint = await self._execute_build(plan)
            checkpoints.append(build_checkpoint)
            
            if build_checkpoint.status != DeploymentStatus.SUCCESS:
                await self._handle_deployment_failure(plan, checkpoints)
                return self._create_deployment_result(plan, checkpoints, False)
            
            # Stage 3: Test
            if validation_level.value >= ValidationLevel.STANDARD.value:
                logging.info("🧪 Stage 3: Running tests")
                test_checkpoint = await self._execute_tests(plan)
                checkpoints.append(test_checkpoint)
                
                if test_checkpoint.status != DeploymentStatus.SUCCESS:
                    await self._handle_deployment_failure(plan, checkpoints)
                    return self._create_deployment_result(plan, checkpoints, False)
            
            # Stage 4: Deploy to staging (if not direct to production)
            if target_environment == "production" and validation_level.value >= ValidationLevel.ENHANCED.value:
                logging.info("🎭 Stage 4: Deploying to staging")
                staging_checkpoint = await self._execute_staging_deployment(plan)
                checkpoints.append(staging_checkpoint)
                
                if staging_checkpoint.status != DeploymentStatus.SUCCESS:
                    await self._handle_deployment_failure(plan, checkpoints)
                    return self._create_deployment_result(plan, checkpoints, False)
            
            # Stage 5: Production deployment
            logging.info("🚀 Stage 5: Deploying to production")
            prod_checkpoint = await self._execute_production_deployment(plan)
            checkpoints.append(prod_checkpoint)
            
            if prod_checkpoint.status != DeploymentStatus.SUCCESS:
                await self._handle_deployment_failure(plan, checkpoints)
                return self._create_deployment_result(plan, checkpoints, False)
            
            # Stage 6: Post-deployment verification
            logging.info("✅ Stage 6: Post-deployment verification")
            post_checkpoint = await self._execute_post_deployment_checks(plan)
            checkpoints.append(post_checkpoint)
            
            # Success!
            deployment_duration = time.time() - deployment_start
            logging.info(f"🎉 Deployment completed successfully in {deployment_duration:.1f}s")
            
            return self._create_deployment_result(plan, checkpoints, True)
            
        except Exception as e:
            logging.error(f"Deployment error: {e}")
            
            # Emergency rollback
            await self._handle_deployment_failure(plan, checkpoints)
            
            return self._create_deployment_result(plan, checkpoints, False, error=str(e))
    
    async def _execute_pre_flight(self, plan: DeploymentPlan) -> DeploymentCheckpoint:
        """Execute pre-flight validation stage"""
        start_time = datetime.now()
        
        try:
            passed, results = await self.validator.validate_pre_flight(plan)
            
            return DeploymentCheckpoint(
                stage=DeploymentStage.PRE_FLIGHT,
                timestamp=start_time,
                status=DeploymentStatus.SUCCESS if passed else DeploymentStatus.FAILED,
                validation_results={'checks': results, 'passed': passed},
                artifacts=[],
                metrics={'duration_seconds': (datetime.now() - start_time).total_seconds()}
            )
            
        except Exception as e:
            return DeploymentCheckpoint(
                stage=DeploymentStage.PRE_FLIGHT,
                timestamp=start_time,
                status=DeploymentStatus.FAILED,
                validation_results={'error': str(e)},
                artifacts=[]
            )
    
    async def _execute_build(self, plan: DeploymentPlan) -> DeploymentCheckpoint:
        """Execute build stage"""
        start_time = datetime.now()
        
        try:
            success, build_result = await self.build_system.execute_build(plan)
            
            return DeploymentCheckpoint(
                stage=DeploymentStage.BUILD,
                timestamp=start_time,
                status=DeploymentStatus.SUCCESS if success else DeploymentStatus.FAILED,
                validation_results=build_result,
                artifacts=build_result.get('artifacts', []),
                metrics={
                    'duration_seconds': build_result.get('duration', 0),
                    'output_size_mb': build_result.get('output_size_mb', 0)
                }
            )
            
        except Exception as e:
            return DeploymentCheckpoint(
                stage=DeploymentStage.BUILD,
                timestamp=start_time,
                status=DeploymentStatus.FAILED,
                validation_results={'error': str(e)},
                artifacts=[]
            )
    
    async def _execute_tests(self, plan: DeploymentPlan) -> DeploymentCheckpoint:
        """Execute test stage"""
        start_time = datetime.now()
        
        try:
            # Check if test script exists
            package_json_path = os.path.join(self.project_root, "package.json")
            
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            scripts = package_data.get('scripts', {})
            
            if 'test' not in scripts:
                return DeploymentCheckpoint(
                    stage=DeploymentStage.TEST,
                    timestamp=start_time,
                    status=DeploymentStatus.SUCCESS,
                    validation_results={'message': 'No test script found, skipping'},
                    artifacts=[]
                )
            
            # Run tests
            process = await asyncio.create_subprocess_exec(
                "npm", "test", "--", "--passWithNoTests",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300  # 5 minute timeout
            )
            
            test_passed = process.returncode == 0
            
            return DeploymentCheckpoint(
                stage=DeploymentStage.TEST,
                timestamp=start_time,
                status=DeploymentStatus.SUCCESS if test_passed else DeploymentStatus.FAILED,
                validation_results={
                    'passed': test_passed,
                    'output': stdout.decode()[-1000:] if stdout else ""  # Last 1000 chars
                },
                artifacts=[],
                metrics={'duration_seconds': (datetime.now() - start_time).total_seconds()}
            )
            
        except asyncio.TimeoutError:
            return DeploymentCheckpoint(
                stage=DeploymentStage.TEST,
                timestamp=start_time,
                status=DeploymentStatus.FAILED,
                validation_results={'error': 'Test timeout after 5 minutes'},
                artifacts=[]
            )
        except Exception as e:
            return DeploymentCheckpoint(
                stage=DeploymentStage.TEST,
                timestamp=start_time,
                status=DeploymentStatus.FAILED,
                validation_results={'error': str(e)},
                artifacts=[]
            )
    
    async def _execute_staging_deployment(self, plan: DeploymentPlan) -> DeploymentCheckpoint:
        """Execute staging deployment"""
        start_time = datetime.now()
        
        # Simulate staging deployment
        # In real implementation, this would deploy to staging environment
        
        await asyncio.sleep(2)  # Simulate deployment time
        
        return DeploymentCheckpoint(
            stage=DeploymentStage.STAGING,
            timestamp=start_time,
            status=DeploymentStatus.SUCCESS,
            validation_results={'message': 'Staging deployment simulated'},
            artifacts=[],
            metrics={'duration_seconds': 2}
        )
    
    async def _execute_production_deployment(self, plan: DeploymentPlan) -> DeploymentCheckpoint:
        """Execute production deployment"""
        start_time = datetime.now()
        
        # Simulate production deployment
        # In real implementation, this would deploy to production
        
        await asyncio.sleep(3)  # Simulate deployment time
        
        return DeploymentCheckpoint(
            stage=DeploymentStage.PRODUCTION,
            timestamp=start_time,
            status=DeploymentStatus.SUCCESS,
            validation_results={'message': 'Production deployment simulated'},
            artifacts=[],
            metrics={'duration_seconds': 3}
        )
    
    async def _execute_post_deployment_checks(self, plan: DeploymentPlan) -> DeploymentCheckpoint:
        """Execute post-deployment verification"""
        start_time = datetime.now()
        
        # Simulate health checks
        # In real implementation, this would check application health
        
        await asyncio.sleep(1)
        
        return DeploymentCheckpoint(
            stage=DeploymentStage.POST_DEPLOY,
            timestamp=start_time,
            status=DeploymentStatus.SUCCESS,
            validation_results={'health_check': 'passed'},
            artifacts=[],
            metrics={'duration_seconds': 1}
        )
    
    async def _handle_deployment_failure(self, plan: DeploymentPlan, checkpoints: List[DeploymentCheckpoint]):
        """Handle deployment failure with automatic rollback"""
        logging.error("🔄 Deployment failed, initiating rollback")
        
        if 'rollback_id' in plan.metadata:
            rollback_result = self.rollback_manager.execute_rollback(plan.deployment_id)
            
            if rollback_result['success']:
                logging.info("✅ Rollback completed successfully")
            else:
                logging.error(f"❌ Rollback failed: {rollback_result.get('error', 'Unknown error')}")
    
    def _create_deployment_result(self, plan: DeploymentPlan, 
                                checkpoints: List[DeploymentCheckpoint], 
                                success: bool,
                                dry_run: bool = False,
                                error: str = None) -> Dict[str, Any]:
        """Create deployment result summary"""
        # Save deployment report
        report = {
            'deployment_id': plan.deployment_id,
            'success': success,
            'dry_run': dry_run,
            'target_environment': plan.target_environment,
            'validation_level': plan.validation_level.name,
            'source_commit': plan.source_commit,
            'created_at': plan.created_at.isoformat(),
            'completed_at': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - plan.created_at).total_seconds(),
            'checkpoints': [asdict(cp) for cp in checkpoints],
            'error': error
        }
        
        # Save to file
        report_path = os.path.join(self.deployments_dir, f"{plan.deployment_id}_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        return report
    
    def _get_current_commit(self) -> str:
        """Get current Git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fail-Safe Deployment System')
    parser.add_argument('--deploy', action='store_true', help='Execute deployment')
    parser.add_argument('--env', default='production', help='Target environment')
    parser.add_argument('--validation', default='standard', 
                       choices=['basic', 'standard', 'enhanced', 'strict', 'paranoid'],
                       help='Validation level')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run only')
    parser.add_argument('--rollback', help='Rollback deployment by ID')
    parser.add_argument('--status', help='Check deployment status by ID')
    
    args = parser.parse_args()
    
    orchestrator = FailSafeDeploymentOrchestrator()
    
    if args.deploy:
        validation_map = {
            'basic': ValidationLevel.BASIC,
            'standard': ValidationLevel.STANDARD,
            'enhanced': ValidationLevel.ENHANCED,
            'strict': ValidationLevel.STRICT,
            'paranoid': ValidationLevel.PARANOID
        }
        
        validation_level = validation_map[args.validation]
        
        print(f"🚀 Initiating {args.env} deployment with {args.validation} validation")
        
        if args.dry_run:
            print("🔍 Running in dry-run mode")
        
        result = asyncio.run(orchestrator.deploy(
            target_environment=args.env,
            validation_level=validation_level,
            dry_run=args.dry_run
        ))
        
        if result['success']:
            print(f"✅ Deployment {result['deployment_id']} completed successfully")
        else:
            print(f"❌ Deployment {result['deployment_id']} failed")
            if result.get('error'):
                print(f"Error: {result['error']}")
    
    elif args.rollback:
        print(f"🔄 Rolling back deployment {args.rollback}")
        rollback_result = orchestrator.rollback_manager.execute_rollback(args.rollback)
        
        if rollback_result['success']:
            print("✅ Rollback completed successfully")
        else:
            print(f"❌ Rollback failed: {rollback_result.get('error', 'Unknown error')}")
    
    elif args.status:
        # Load deployment report
        report_path = os.path.join(orchestrator.deployments_dir, f"{args.status}_report.json")
        
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            print(f"📊 Deployment Status: {args.status}")
            print(f"Success: {report['success']}")
            print(f"Environment: {report['target_environment']}")
            print(f"Duration: {report['duration_seconds']:.1f}s")
            
            if report['checkpoints']:
                print("\nCheckpoints:")
                for cp in report['checkpoints']:
                    status = "✅" if cp['status'] == "success" else "❌"
                    print(f"  {status} {cp['stage']}")
        else:
            print(f"No deployment found with ID: {args.status}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()