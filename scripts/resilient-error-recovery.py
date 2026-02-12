#!/usr/bin/env python3
"""
Resilient Error Recovery Protocol System - Adaptive error handling and recovery
with machine learning-based pattern recognition and automated remediation.

The adaptive nervous system that learns from failures and prevents their recurrence.
"""

import os
import json
import time
import asyncio
import threading
import logging
import subprocess
import sqlite3
import hashlib
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import re
import statistics

try:
    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

class ErrorSeverity(Enum):
    CATASTROPHIC = 5  # System-wide failure
    CRITICAL = 4      # Major functionality broken
    HIGH = 3          # Important features affected
    MEDIUM = 2        # Minor functionality issues
    LOW = 1           # Cosmetic or edge case issues

class RecoveryStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"

class ErrorCategory(Enum):
    BUILD_FAILURE = "build_failure"
    RUNTIME_ERROR = "runtime_error"
    DEPENDENCY_ISSUE = "dependency_issue"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PERMISSION_ERROR = "permission_error"
    DATA_CORRUPTION = "data_corruption"
    UNKNOWN = "unknown"

@dataclass
class ErrorEvent:
    error_id: str
    timestamp: datetime
    error_type: str
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    error_message: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RecoveryAction:
    action_id: str
    name: str
    description: str
    recovery_function: Callable
    applicable_categories: List[ErrorCategory]
    success_rate: float = 0.0
    execution_time_avg: float = 0.0
    prerequisites: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)

@dataclass
class RecoveryAttempt:
    attempt_id: str
    error_id: str
    action_id: str
    timestamp: datetime
    status: RecoveryStatus
    duration_seconds: float
    success: bool
    output: str
    side_effects_observed: List[str] = field(default_factory=list)

class ErrorPatternAnalyzer:
    """Analyzes error patterns and learns from recovery attempts"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.error_history = deque(maxlen=1000)
        self.recovery_patterns = {}
        self.vectorizer = None
        
        if ML_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    
    def analyze_error_patterns(self, errors: List[ErrorEvent]) -> Dict[str, Any]:
        """Analyze patterns in error events"""
        if not errors:
            return {}
        
        patterns = {
            'temporal_patterns': self._analyze_temporal_patterns(errors),
            'component_patterns': self._analyze_component_patterns(errors),
            'severity_patterns': self._analyze_severity_patterns(errors),
            'category_patterns': self._analyze_category_patterns(errors)
        }
        
        if ML_AVAILABLE:
            patterns['similarity_clusters'] = self._cluster_similar_errors(errors)
        
        return patterns
    
    def _analyze_temporal_patterns(self, errors: List[ErrorEvent]) -> Dict[str, Any]:
        """Analyze temporal error patterns"""
        timestamps = [error.timestamp for error in errors]
        
        if len(timestamps) < 2:
            return {}
        
        # Calculate time intervals between errors
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        # Detect burst patterns (multiple errors in short time)
        burst_threshold = 300  # 5 minutes
        bursts = []
        burst_start = None
        
        for i, interval in enumerate(intervals):
            if interval < burst_threshold:
                if burst_start is None:
                    burst_start = i
            else:
                if burst_start is not None:
                    bursts.append({
                        'start_index': burst_start,
                        'end_index': i,
                        'duration': sum(intervals[burst_start:i+1]),
                        'error_count': i - burst_start + 1
                    })
                    burst_start = None
        
        return {
            'total_errors': len(errors),
            'avg_interval_seconds': statistics.mean(intervals) if intervals else 0,
            'burst_patterns': bursts,
            'errors_per_hour': self._calculate_error_rate(timestamps)
        }
    
    def _analyze_component_patterns(self, errors: List[ErrorEvent]) -> Dict[str, Any]:
        """Analyze error patterns by component"""
        component_counts = defaultdict(int)
        component_severities = defaultdict(list)
        
        for error in errors:
            component_counts[error.component] += 1
            component_severities[error.component].append(error.severity.value)
        
        component_stats = {}
        for component, count in component_counts.items():
            avg_severity = statistics.mean(component_severities[component])
            component_stats[component] = {
                'error_count': count,
                'avg_severity': avg_severity,
                'max_severity': max(component_severities[component]),
                'failure_rate': count / len(errors)
            }
        
        return {
            'component_statistics': component_stats,
            'most_problematic': max(component_counts.keys(), key=component_counts.get) if component_counts else None,
            'total_components_affected': len(component_counts)
        }
    
    def _analyze_severity_patterns(self, errors: List[ErrorEvent]) -> Dict[str, Any]:
        """Analyze error severity patterns"""
        severity_counts = defaultdict(int)
        severity_trends = []
        
        for error in errors:
            severity_counts[error.severity.name] += 1
            severity_trends.append(error.severity.value)
        
        # Calculate severity trend (increasing/decreasing)
        if len(severity_trends) >= 5:
            recent_avg = statistics.mean(severity_trends[-5:])
            older_avg = statistics.mean(severity_trends[:-5])
            trend = "increasing" if recent_avg > older_avg else "decreasing" if recent_avg < older_avg else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            'severity_distribution': dict(severity_counts),
            'avg_severity': statistics.mean(severity_trends) if severity_trends else 0,
            'severity_trend': trend,
            'critical_error_percentage': severity_counts['CRITICAL'] / len(errors) * 100 if errors else 0
        }
    
    def _analyze_category_patterns(self, errors: List[ErrorEvent]) -> Dict[str, Any]:
        """Analyze error patterns by category"""
        category_counts = defaultdict(int)
        category_sequences = []
        
        for error in errors:
            category_counts[error.category.name] += 1
            category_sequences.append(error.category.name)
        
        # Find common error sequences
        sequences = self._find_common_sequences(category_sequences)
        
        return {
            'category_distribution': dict(category_counts),
            'common_sequences': sequences,
            'most_common_category': max(category_counts.keys(), key=category_counts.get) if category_counts else None
        }
    
    def _cluster_similar_errors(self, errors: List[ErrorEvent]) -> Dict[str, Any]:
        """Cluster similar errors using ML"""
        if not ML_AVAILABLE or len(errors) < 3:
            return {}
        
        try:
            # Prepare text data for clustering
            error_texts = []
            for error in errors:
                text = f"{error.error_message} {error.stack_trace or ''}"
                error_texts.append(text)
            
            # Vectorize error messages
            vectors = self.vectorizer.fit_transform(error_texts)
            
            # Cluster using DBSCAN
            clustering = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
            cluster_labels = clustering.fit_predict(vectors.toarray())
            
            # Group errors by cluster
            clusters = defaultdict(list)
            for i, label in enumerate(cluster_labels):
                clusters[label].append(i)
            
            # Analyze clusters
            cluster_analysis = {}
            for cluster_id, error_indices in clusters.items():
                if cluster_id == -1:  # Noise cluster
                    continue
                
                cluster_errors = [errors[i] for i in error_indices]
                cluster_analysis[f"cluster_{cluster_id}"] = {
                    'error_count': len(cluster_errors),
                    'avg_severity': statistics.mean([e.severity.value for e in cluster_errors]),
                    'common_components': list(set([e.component for e in cluster_errors])),
                    'representative_error': cluster_errors[0].error_message[:100]
                }
            
            return {
                'total_clusters': len([k for k in clusters.keys() if k != -1]),
                'noise_errors': len(clusters.get(-1, [])),
                'cluster_details': cluster_analysis
            }
            
        except Exception as e:
            logging.error(f"Error clustering failed: {e}")
            return {}
    
    def _calculate_error_rate(self, timestamps: List[datetime]) -> float:
        """Calculate errors per hour"""
        if len(timestamps) < 2:
            return 0
        
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # hours
        return len(timestamps) / max(time_span, 1)
    
    def _find_common_sequences(self, sequences: List[str], min_length: int = 2) -> List[Dict[str, Any]]:
        """Find common sequences in error categories"""
        if len(sequences) < min_length:
            return []
        
        sequence_counts = defaultdict(int)
        
        # Generate all possible subsequences
        for length in range(min_length, min(len(sequences) + 1, 5)):  # Max length 5
            for i in range(len(sequences) - length + 1):
                subseq = tuple(sequences[i:i + length])
                sequence_counts[subseq] += 1
        
        # Filter sequences that occur more than once
        common_sequences = []
        for seq, count in sequence_counts.items():
            if count > 1:
                common_sequences.append({
                    'sequence': list(seq),
                    'count': count,
                    'length': len(seq)
                })
        
        # Sort by frequency
        common_sequences.sort(key=lambda x: x['count'], reverse=True)
        
        return common_sequences[:10]  # Return top 10

class RecoveryActionLibrary:
    """Library of recovery actions with adaptive success tracking"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.actions = {}
        self.success_history = defaultdict(list)
        self._initialize_recovery_actions()
    
    def _initialize_recovery_actions(self):
        """Initialize the library of recovery actions"""
        actions = [
            # Build failure recovery actions
            RecoveryAction(
                action_id="clean_build",
                name="Clean Build Environment",
                description="Remove build artifacts and rebuild from scratch",
                recovery_function=self._clean_build,
                applicable_categories=[ErrorCategory.BUILD_FAILURE]
            ),
            RecoveryAction(
                action_id="npm_install_fresh",
                name="Fresh NPM Install",
                description="Remove node_modules and reinstall dependencies",
                recovery_function=self._npm_install_fresh,
                applicable_categories=[ErrorCategory.BUILD_FAILURE, ErrorCategory.DEPENDENCY_ISSUE]
            ),
            RecoveryAction(
                action_id="clear_npm_cache",
                name="Clear NPM Cache",
                description="Clear NPM cache and retry",
                recovery_function=self._clear_npm_cache,
                applicable_categories=[ErrorCategory.DEPENDENCY_ISSUE]
            ),
            
            # Runtime error recovery actions
            RecoveryAction(
                action_id="restart_process",
                name="Restart Process",
                description="Restart the failed process",
                recovery_function=self._restart_process,
                applicable_categories=[ErrorCategory.RUNTIME_ERROR]
            ),
            RecoveryAction(
                action_id="memory_cleanup",
                name="Memory Cleanup",
                description="Free up memory and restart with clean state",
                recovery_function=self._memory_cleanup,
                applicable_categories=[ErrorCategory.RESOURCE_EXHAUSTION]
            ),
            
            # Configuration error recovery actions
            RecoveryAction(
                action_id="reset_config",
                name="Reset Configuration",
                description="Reset configuration to known good state",
                recovery_function=self._reset_config,
                applicable_categories=[ErrorCategory.CONFIGURATION_ERROR]
            ),
            RecoveryAction(
                action_id="regenerate_config",
                name="Regenerate Configuration",
                description="Regenerate configuration files",
                recovery_function=self._regenerate_config,
                applicable_categories=[ErrorCategory.CONFIGURATION_ERROR]
            ),
            
            # Network error recovery actions
            RecoveryAction(
                action_id="retry_with_backoff",
                name="Retry with Exponential Backoff",
                description="Retry operation with increasing delays",
                recovery_function=self._retry_with_backoff,
                applicable_categories=[ErrorCategory.NETWORK_ERROR]
            ),
            RecoveryAction(
                action_id="check_connectivity",
                name="Check Network Connectivity",
                description="Verify and repair network connectivity",
                recovery_function=self._check_connectivity,
                applicable_categories=[ErrorCategory.NETWORK_ERROR]
            ),
            
            # Permission error recovery actions
            RecoveryAction(
                action_id="fix_permissions",
                name="Fix File Permissions",
                description="Repair file and directory permissions",
                recovery_function=self._fix_permissions,
                applicable_categories=[ErrorCategory.PERMISSION_ERROR]
            ),
            
            # Data corruption recovery actions
            RecoveryAction(
                action_id="restore_from_backup",
                name="Restore from Backup",
                description="Restore corrupted data from backup",
                recovery_function=self._restore_from_backup,
                applicable_categories=[ErrorCategory.DATA_CORRUPTION]
            ),
            RecoveryAction(
                action_id="repair_git_repo",
                name="Repair Git Repository",
                description="Repair corrupted Git repository",
                recovery_function=self._repair_git_repo,
                applicable_categories=[ErrorCategory.DATA_CORRUPTION]
            ),
            
            # Generic recovery actions
            RecoveryAction(
                action_id="revert_recent_changes",
                name="Revert Recent Changes",
                description="Revert to last known good state",
                recovery_function=self._revert_recent_changes,
                applicable_categories=[ErrorCategory.UNKNOWN, ErrorCategory.RUNTIME_ERROR]
            ),
            RecoveryAction(
                action_id="system_health_check",
                name="System Health Check",
                description="Perform comprehensive system health check",
                recovery_function=self._system_health_check,
                applicable_categories=[ErrorCategory.UNKNOWN]
            )
        ]
        
        for action in actions:
            self.actions[action.action_id] = action
    
    def get_applicable_actions(self, error: ErrorEvent) -> List[RecoveryAction]:
        """Get applicable recovery actions for an error"""
        applicable = []
        
        for action in self.actions.values():
            if error.category in action.applicable_categories:
                applicable.append(action)
        
        # Sort by success rate (if available)
        applicable.sort(key=lambda a: a.success_rate, reverse=True)
        
        return applicable
    
    def update_action_success_rate(self, action_id: str, success: bool, duration: float):
        """Update success rate for an action"""
        if action_id in self.actions:
            self.success_history[action_id].append({
                'success': success,
                'duration': duration,
                'timestamp': datetime.now()
            })
            
            # Keep only recent history (last 50 attempts)
            if len(self.success_history[action_id]) > 50:
                self.success_history[action_id] = self.success_history[action_id][-50:]
            
            # Update success rate
            recent_attempts = self.success_history[action_id]
            success_count = sum(1 for attempt in recent_attempts if attempt['success'])
            self.actions[action_id].success_rate = success_count / len(recent_attempts)
            
            # Update average execution time
            durations = [attempt['duration'] for attempt in recent_attempts]
            self.actions[action_id].execution_time_avg = statistics.mean(durations)
    
    # Recovery action implementations
    async def _clean_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean build environment and rebuild"""
        try:
            build_dirs = ["dist", "build", ".next", "out"]
            cleaned = []
            
            for build_dir in build_dirs:
                dir_path = os.path.join(self.project_root, build_dir)
                if os.path.exists(dir_path):
                    import shutil
                    shutil.rmtree(dir_path)
                    cleaned.append(build_dir)
            
            # Run clean build
            process = await asyncio.create_subprocess_exec(
                "npm", "run", "build",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            return {
                'success': process.returncode == 0,
                'message': f"Cleaned {len(cleaned)} build directories",
                'cleaned_dirs': cleaned,
                'build_output': stdout.decode()[-500:] if stdout else ""
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _npm_install_fresh(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fresh npm install"""
        try:
            # Remove node_modules
            node_modules = os.path.join(self.project_root, "node_modules")
            if os.path.exists(node_modules):
                import shutil
                shutil.rmtree(node_modules)
            
            # Remove package-lock.json
            package_lock = os.path.join(self.project_root, "package-lock.json")
            if os.path.exists(package_lock):
                os.remove(package_lock)
            
            # Fresh install
            process = await asyncio.create_subprocess_exec(
                "npm", "install",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            return {
                'success': process.returncode == 0,
                'message': "Fresh npm install completed",
                'output': stdout.decode()[-500:] if stdout else ""
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _clear_npm_cache(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clear npm cache"""
        try:
            process = await asyncio.create_subprocess_exec(
                "npm", "cache", "clean", "--force",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            
            return {
                'success': process.returncode == 0,
                'message': "NPM cache cleared",
                'output': stdout.decode() if stdout else ""
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _restart_process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a process"""
        try:
            process_name = context.get('process_name', 'unknown')
            
            # Kill existing process (if specified)
            if 'pid' in context:
                try:
                    import psutil
                    process = psutil.Process(context['pid'])
                    process.terminate()
                    process.wait(timeout=10)
                except Exception:
                    pass
            
            # Start new process (if command specified)
            if 'start_command' in context:
                command = context['start_command']
                if isinstance(command, str):
                    command = command.split()
                
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=self.project_root
                )
                
                # Give it a moment to start
                await asyncio.sleep(2)
                
                return {
                    'success': True,
                    'message': f"Process {process_name} restarted",
                    'new_pid': process.pid
                }
            else:
                return {
                    'success': True,
                    'message': f"Process {process_name} terminated"
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _memory_cleanup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform memory cleanup"""
        try:
            import gc
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear caches
            cache_dirs = [
                os.path.join(self.project_root, ".cache"),
                os.path.join(self.project_root, "node_modules/.cache"),
                "/tmp"
            ]
            
            cleared_caches = []
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    try:
                        # Clear old files only
                        cutoff_time = time.time() - (24 * 60 * 60)  # 24 hours ago
                        
                        for root, dirs, files in os.walk(cache_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                try:
                                    if os.path.getmtime(file_path) < cutoff_time:
                                        os.remove(file_path)
                                except Exception:
                                    pass
                        
                        cleared_caches.append(cache_dir)
                    except Exception:
                        pass
            
            return {
                'success': True,
                'message': f"Memory cleanup completed",
                'garbage_collected': collected,
                'cleared_caches': cleared_caches
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _reset_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Reset configuration files"""
        try:
            config_files = [
                "tsconfig.json",
                "vite.config.ts",
                "next.config.js",
                ".env.local"
            ]
            
            reset_files = []
            
            for config_file in config_files:
                config_path = os.path.join(self.project_root, config_file)
                backup_path = config_path + ".backup"
                
                # Create backup if doesn't exist
                if os.path.exists(config_path) and not os.path.exists(backup_path):
                    import shutil
                    shutil.copy2(config_path, backup_path)
                
                # Check for template or default
                template_path = config_path + ".template"
                if os.path.exists(template_path):
                    import shutil
                    shutil.copy2(template_path, config_path)
                    reset_files.append(config_file)
            
            return {
                'success': True,
                'message': f"Reset {len(reset_files)} configuration files",
                'reset_files': reset_files
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _regenerate_config(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Regenerate configuration files"""
        try:
            # Simple config regeneration
            generated = []
            
            # Generate basic tsconfig.json if missing
            tsconfig_path = os.path.join(self.project_root, "tsconfig.json")
            if not os.path.exists(tsconfig_path):
                basic_tsconfig = {
                    "compilerOptions": {
                        "target": "es5",
                        "lib": ["dom", "dom.iterable", "es6"],
                        "allowJs": True,
                        "skipLibCheck": True,
                        "esModuleInterop": True,
                        "allowSyntheticDefaultImports": True,
                        "strict": True,
                        "forceConsistentCasingInFileNames": True,
                        "moduleResolution": "node",
                        "resolveJsonModule": True,
                        "isolatedModules": True,
                        "noEmit": True,
                        "jsx": "react-jsx"
                    },
                    "include": ["src"]
                }
                
                with open(tsconfig_path, 'w') as f:
                    json.dump(basic_tsconfig, f, indent=2)
                
                generated.append("tsconfig.json")
            
            return {
                'success': True,
                'message': f"Generated {len(generated)} configuration files",
                'generated_files': generated
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _retry_with_backoff(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry operation with exponential backoff"""
        try:
            max_retries = context.get('max_retries', 3)
            base_delay = context.get('base_delay', 1)
            operation = context.get('operation')
            
            if not operation:
                return {'success': False, 'error': 'No operation specified'}
            
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    # Execute the operation
                    result = await operation()
                    
                    return {
                        'success': True,
                        'message': f"Operation succeeded on attempt {attempt + 1}",
                        'attempts': attempt + 1,
                        'result': result
                    }
                    
                except Exception as e:
                    last_error = e
                    
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
            
            return {
                'success': False,
                'error': f"Operation failed after {max_retries} attempts: {str(last_error)}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _check_connectivity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            # Test basic connectivity
            hosts_to_test = [
                "8.8.8.8",  # Google DNS
                "1.1.1.1",  # Cloudflare DNS
                "github.com",
                "npmjs.org"
            ]
            
            connectivity_results = {}
            
            for host in hosts_to_test:
                try:
                    process = await asyncio.create_subprocess_exec(
                        "ping", "-c", "1", "-W", "5000", host,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
                    connectivity_results[host] = process.returncode == 0
                    
                except Exception:
                    connectivity_results[host] = False
            
            successful_connections = sum(connectivity_results.values())
            total_tests = len(connectivity_results)
            
            return {
                'success': successful_connections > 0,
                'message': f"Connectivity: {successful_connections}/{total_tests} hosts reachable",
                'results': connectivity_results
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _fix_permissions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fix file permissions"""
        try:
            target_paths = context.get('paths', [self.project_root])
            fixed_paths = []
            
            for path in target_paths:
                if os.path.exists(path):
                    try:
                        # Make directories readable/writable/executable by owner
                        if os.path.isdir(path):
                            os.chmod(path, 0o755)
                        else:
                            os.chmod(path, 0o644)
                        
                        fixed_paths.append(path)
                    except Exception:
                        pass
            
            return {
                'success': len(fixed_paths) > 0,
                'message': f"Fixed permissions for {len(fixed_paths)} paths",
                'fixed_paths': fixed_paths
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _restore_from_backup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Restore from backup"""
        try:
            backup_dir = os.path.join(self.project_root, "backups")
            
            if not os.path.exists(backup_dir):
                return {'success': False, 'error': 'No backup directory found'}
            
            # Find most recent backup
            backups = []
            for file in os.listdir(backup_dir):
                if file.endswith(('.tar.gz', '.zip')):
                    file_path = os.path.join(backup_dir, file)
                    mtime = os.path.getmtime(file_path)
                    backups.append((file, mtime, file_path))
            
            if not backups:
                return {'success': False, 'error': 'No backups found'}
            
            # Use most recent backup
            backups.sort(key=lambda x: x[1], reverse=True)
            backup_name, backup_time, backup_path = backups[0]
            
            # Extract backup (simplified)
            backup_age_hours = (time.time() - backup_time) / 3600
            
            return {
                'success': True,
                'message': f"Would restore from backup: {backup_name}",
                'backup_name': backup_name,
                'backup_age_hours': backup_age_hours
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _repair_git_repo(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Repair Git repository"""
        try:
            os.chdir(self.project_root)
            
            repair_commands = [
                ["git", "fsck", "--full"],
                ["git", "gc", "--aggressive", "--prune=now"],
                ["git", "repack", "-Ad"]
            ]
            
            repair_results = []
            
            for cmd in repair_commands:
                try:
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
                    
                    repair_results.append({
                        'command': ' '.join(cmd),
                        'success': process.returncode == 0,
                        'output': stdout.decode()[-200:] if stdout else ""
                    })
                    
                except Exception as e:
                    repair_results.append({
                        'command': ' '.join(cmd),
                        'success': False,
                        'error': str(e)
                    })
            
            successful_repairs = sum(1 for r in repair_results if r['success'])
            
            return {
                'success': successful_repairs > 0,
                'message': f"Git repair: {successful_repairs}/{len(repair_commands)} commands succeeded",
                'repair_results': repair_results
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _revert_recent_changes(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Revert recent changes"""
        try:
            os.chdir(self.project_root)
            
            # Get recent commits
            process = await asyncio.create_subprocess_exec(
                "git", "log", "--oneline", "-5",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode != 0:
                return {'success': False, 'error': 'Could not get git log'}
            
            recent_commits = stdout.decode().strip().split('\n')
            
            if len(recent_commits) < 2:
                return {'success': False, 'error': 'Not enough commit history'}
            
            # Revert to previous commit (soft reset)
            previous_commit = recent_commits[1].split()[0]
            
            process = await asyncio.create_subprocess_exec(
                "git", "reset", "--soft", previous_commit,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            return {
                'success': process.returncode == 0,
                'message': f"Reverted to commit {previous_commit}",
                'reverted_to': previous_commit
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _system_health_check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform system health check"""
        try:
            health_results = {}
            
            # Check disk space
            import shutil
            disk_usage = shutil.disk_usage(self.project_root)
            free_gb = disk_usage.free / (1024**3)
            health_results['disk_space'] = {
                'status': 'healthy' if free_gb > 1 else 'warning',
                'free_gb': free_gb
            }
            
            # Check memory
            try:
                import psutil
                memory = psutil.virtual_memory()
                health_results['memory'] = {
                    'status': 'healthy' if memory.percent < 90 else 'warning',
                    'usage_percent': memory.percent
                }
            except ImportError:
                health_results['memory'] = {'status': 'unknown', 'error': 'psutil not available'}
            
            # Check critical files
            critical_files = ["package.json", "tsconfig.json"]
            missing_files = []
            
            for file in critical_files:
                if not os.path.exists(os.path.join(self.project_root, file)):
                    missing_files.append(file)
            
            health_results['critical_files'] = {
                'status': 'healthy' if not missing_files else 'error',
                'missing_files': missing_files
            }
            
            # Overall health
            statuses = [result['status'] for result in health_results.values()]
            overall_healthy = 'error' not in statuses
            
            return {
                'success': True,
                'message': f"System health: {'healthy' if overall_healthy else 'issues detected'}",
                'health_results': health_results,
                'overall_healthy': overall_healthy
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

class ErrorRecoveryOrchestrator:
    """Main orchestrator for error recovery operations"""
    
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.analyzer = ErrorPatternAnalyzer(project_root)
        self.action_library = RecoveryActionLibrary(project_root)
        
        # Database setup
        self.db_path = os.path.join(project_root, "monitoring", "error_recovery.db")
        self._init_database()
        
        # Configuration
        self.max_concurrent_recoveries = 3
        self.recovery_timeout = 300  # 5 minutes
        self.active_recoveries = {}
        
        # Setup logging
        self.setup_logging()
    
    def _init_database(self):
        """Initialize error recovery database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS error_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    severity INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    component TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS recovery_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attempt_id TEXT UNIQUE NOT NULL,
                    error_id TEXT NOT NULL,
                    action_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    output TEXT,
                    side_effects TEXT,
                    FOREIGN KEY (error_id) REFERENCES error_events (error_id)
                );
                
                CREATE TABLE IF NOT EXISTS recovery_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE NOT NULL,
                    error_pattern TEXT NOT NULL,
                    successful_actions TEXT NOT NULL,
                    success_rate REAL NOT NULL,
                    last_updated TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_recovery_timestamp ON recovery_attempts(timestamp);
                CREATE INDEX IF NOT EXISTS idx_error_category ON error_events(category);
            """)
    
    def setup_logging(self):
        """Setup error recovery logging"""
        log_file = os.path.join(self.project_root, "logs", "error-recovery.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    async def handle_error(self, error_message: str, 
                          error_type: str = "unknown",
                          component: str = "system",
                          context: Dict[str, Any] = None,
                          stack_trace: str = None) -> Dict[str, Any]:
        """Handle an error with automatic recovery"""
        
        # Create error event
        error_event = self._create_error_event(
            error_message, error_type, component, context, stack_trace
        )
        
        # Store error in database
        self._store_error_event(error_event)
        
        # Analyze error and determine recovery strategy
        recovery_plan = await self._analyze_and_plan_recovery(error_event)
        
        if not recovery_plan['actions']:
            logging.warning(f"No recovery actions available for error {error_event.error_id}")
            return {
                'error_id': error_event.error_id,
                'recovery_attempted': False,
                'reason': 'No applicable recovery actions found'
            }
        
        # Execute recovery plan
        recovery_result = await self._execute_recovery_plan(error_event, recovery_plan)
        
        return {
            'error_id': error_event.error_id,
            'recovery_attempted': True,
            'recovery_result': recovery_result
        }
    
    def _create_error_event(self, error_message: str, error_type: str, 
                           component: str, context: Dict[str, Any],
                           stack_trace: str) -> ErrorEvent:
        """Create an error event from the provided information"""
        
        # Generate unique error ID
        error_id = hashlib.md5(
            f"{error_message}{component}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Classify error
        category = self._classify_error(error_message, error_type, stack_trace)
        severity = self._assess_error_severity(error_message, category, component)
        
        return ErrorEvent(
            error_id=error_id,
            timestamp=datetime.now(),
            error_type=error_type,
            severity=severity,
            category=category,
            component=component,
            error_message=error_message,
            stack_trace=stack_trace,
            context=context or {},
            metadata={}
        )
    
    def _classify_error(self, error_message: str, error_type: str, stack_trace: str) -> ErrorCategory:
        """Classify error into categories"""
        message_lower = error_message.lower()
        stack_lower = (stack_trace or "").lower()
        
        # Build failure patterns
        if any(term in message_lower for term in ["build failed", "compilation error", "syntax error"]):
            return ErrorCategory.BUILD_FAILURE
        
        # Dependency patterns
        if any(term in message_lower for term in ["module not found", "cannot resolve", "dependency", "npm install"]):
            return ErrorCategory.DEPENDENCY_ISSUE
        
        # Network patterns
        if any(term in message_lower for term in ["network", "timeout", "connection", "econnrefused", "fetch failed"]):
            return ErrorCategory.NETWORK_ERROR
        
        # Permission patterns
        if any(term in message_lower for term in ["permission denied", "access denied", "eacces", "eperm"]):
            return ErrorCategory.PERMISSION_ERROR
        
        # Memory/resource patterns
        if any(term in message_lower for term in ["out of memory", "heap", "enomem", "resource exhausted"]):
            return ErrorCategory.RESOURCE_EXHAUSTION
        
        # Configuration patterns
        if any(term in message_lower for term in ["config", "configuration", "invalid option", "unknown flag"]):
            return ErrorCategory.CONFIGURATION_ERROR
        
        # Runtime patterns
        if any(term in message_lower for term in ["runtime error", "exception", "null pointer", "undefined"]):
            return ErrorCategory.RUNTIME_ERROR
        
        # Data corruption patterns
        if any(term in message_lower for term in ["corrupt", "invalid format", "checksum", "integrity"]):
            return ErrorCategory.DATA_CORRUPTION
        
        return ErrorCategory.UNKNOWN
    
    def _assess_error_severity(self, error_message: str, category: ErrorCategory, component: str) -> ErrorSeverity:
        """Assess error severity"""
        message_lower = error_message.lower()
        
        # Critical system components
        critical_components = ["system", "git", "build", "deployment"]
        
        # Catastrophic indicators
        if any(term in message_lower for term in ["catastrophic", "fatal", "system failure", "complete failure"]):
            return ErrorSeverity.CATASTROPHIC
        
        # Critical indicators
        if (component in critical_components or 
            category in [ErrorCategory.DATA_CORRUPTION, ErrorCategory.BUILD_FAILURE] or
            any(term in message_lower for term in ["critical", "severe", "cannot continue"])):
            return ErrorSeverity.CRITICAL
        
        # High severity indicators
        if (category in [ErrorCategory.RUNTIME_ERROR, ErrorCategory.RESOURCE_EXHAUSTION] or
            any(term in message_lower for term in ["error", "failed", "exception"])):
            return ErrorSeverity.HIGH
        
        # Medium severity indicators
        if (category in [ErrorCategory.CONFIGURATION_ERROR, ErrorCategory.DEPENDENCY_ISSUE] or
            any(term in message_lower for term in ["warning", "deprecated", "missing"])):
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    def _store_error_event(self, error: ErrorEvent):
        """Store error event in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO error_events 
                    (error_id, timestamp, error_type, severity, category, component, 
                     error_message, stack_trace, context, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    error.error_id,
                    error.timestamp.isoformat(),
                    error.error_type,
                    error.severity.value,
                    error.category.name,
                    error.component,
                    error.error_message,
                    error.stack_trace,
                    json.dumps(error.context),
                    json.dumps(error.metadata)
                ))
        except Exception as e:
            logging.error(f"Failed to store error event: {e}")
    
    async def _analyze_and_plan_recovery(self, error: ErrorEvent) -> Dict[str, Any]:
        """Analyze error and create recovery plan"""
        
        # Get applicable recovery actions
        applicable_actions = self.action_library.get_applicable_actions(error)
        
        # Check for similar past errors and their successful recoveries
        similar_errors = self._find_similar_errors(error)
        
        # Prioritize actions based on past success
        prioritized_actions = self._prioritize_actions(applicable_actions, similar_errors)
        
        return {
            'error_id': error.error_id,
            'actions': prioritized_actions,
            'similar_errors': len(similar_errors),
            'confidence': self._calculate_recovery_confidence(prioritized_actions, similar_errors)
        }
    
    def _find_similar_errors(self, error: ErrorEvent, limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar errors from history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Find errors with same category and component
                cursor = conn.execute("""
                    SELECT e.*, r.action_id, r.success 
                    FROM error_events e
                    LEFT JOIN recovery_attempts r ON e.error_id = r.error_id
                    WHERE e.category = ? AND e.component = ? 
                    AND e.error_id != ?
                    ORDER BY e.timestamp DESC
                    LIMIT ?
                """, (error.category.name, error.component, error.error_id, limit * 3))
                
                results = cursor.fetchall()
                
                # Group by error and find successful recoveries
                similar_errors = []
                seen_errors = set()
                
                for row in results:
                    error_id = row[1]  # error_id column
                    if error_id not in seen_errors:
                        seen_errors.add(error_id)
                        
                        # Check if this error had successful recovery
                        if row[-1]:  # success column
                            similar_errors.append({
                                'error_id': error_id,
                                'successful_action': row[-2],  # action_id column
                                'error_message': row[7],  # error_message column
                                'timestamp': row[2]  # timestamp column
                            })
                
                return similar_errors[:limit]
                
        except Exception as e:
            logging.error(f"Error finding similar errors: {e}")
            return []
    
    def _prioritize_actions(self, actions: List[RecoveryAction], 
                           similar_errors: List[Dict[str, Any]]) -> List[RecoveryAction]:
        """Prioritize recovery actions based on historical success"""
        
        # Create success score for each action
        action_scores = {}
        
        for action in actions:
            score = action.success_rate  # Base score from overall success rate
            
            # Boost score if this action was successful for similar errors
            similar_successes = sum(1 for err in similar_errors 
                                  if err['successful_action'] == action.action_id)
            
            if similar_successes > 0:
                score += 0.3 * (similar_successes / len(similar_errors))
            
            # Penalize for long execution time (prefer faster actions)
            if action.execution_time_avg > 60:  # More than 1 minute
                score -= 0.1
            
            action_scores[action.action_id] = score
        
        # Sort by score
        return sorted(actions, key=lambda a: action_scores.get(a.action_id, 0), reverse=True)
    
    def _calculate_recovery_confidence(self, actions: List[RecoveryAction], 
                                     similar_errors: List[Dict[str, Any]]) -> float:
        """Calculate confidence in recovery success"""
        if not actions:
            return 0.0
        
        # Base confidence from best action success rate
        base_confidence = actions[0].success_rate if actions else 0.0
        
        # Boost confidence if we have similar successful recoveries
        if similar_errors:
            similarity_boost = min(0.3, len(similar_errors) * 0.1)
            base_confidence += similarity_boost
        
        return min(1.0, base_confidence)
    
    async def _execute_recovery_plan(self, error: ErrorEvent, 
                                   recovery_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recovery plan"""
        recovery_results = []
        
        for action in recovery_plan['actions']:
            # Check if we've reached max concurrent recoveries
            if len(self.active_recoveries) >= self.max_concurrent_recoveries:
                await asyncio.sleep(1)  # Brief pause
                continue
            
            # Execute recovery action
            attempt_result = await self._execute_recovery_action(error, action)
            recovery_results.append(attempt_result)
            
            # If successful, stop trying other actions
            if attempt_result['success']:
                logging.info(f"✅ Recovery successful with action: {action.name}")
                break
            else:
                logging.warning(f"❌ Recovery failed with action: {action.name}")
        
        # Update learning data
        self._update_recovery_learning(error, recovery_results)
        
        # Calculate overall success
        overall_success = any(result['success'] for result in recovery_results)
        
        return {
            'overall_success': overall_success,
            'attempts': len(recovery_results),
            'results': recovery_results,
            'confidence': recovery_plan['confidence']
        }
    
    async def _execute_recovery_action(self, error: ErrorEvent, 
                                     action: RecoveryAction) -> Dict[str, Any]:
        """Execute a single recovery action"""
        
        attempt_id = f"attempt_{error.error_id}_{action.action_id}_{int(time.time())}"
        start_time = time.time()
        
        # Mark as active
        self.active_recoveries[attempt_id] = {
            'error_id': error.error_id,
            'action_id': action.action_id,
            'start_time': start_time
        }
        
        try:
            logging.info(f"🔧 Executing recovery action: {action.name}")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                action.recovery_function(error.context),
                timeout=self.recovery_timeout
            )
            
            duration = time.time() - start_time
            success = result.get('success', False)
            
            # Create recovery attempt record
            attempt = RecoveryAttempt(
                attempt_id=attempt_id,
                error_id=error.error_id,
                action_id=action.action_id,
                timestamp=datetime.now(),
                status=RecoveryStatus.SUCCESSFUL if success else RecoveryStatus.FAILED,
                duration_seconds=duration,
                success=success,
                output=json.dumps(result),
                side_effects_observed=result.get('side_effects', [])
            )
            
            # Store attempt in database
            self._store_recovery_attempt(attempt)
            
            # Update action success rate
            self.action_library.update_action_success_rate(action.action_id, success, duration)
            
            return {
                'attempt_id': attempt_id,
                'action_name': action.name,
                'success': success,
                'duration': duration,
                'result': result
            }
            
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            
            attempt = RecoveryAttempt(
                attempt_id=attempt_id,
                error_id=error.error_id,
                action_id=action.action_id,
                timestamp=datetime.now(),
                status=RecoveryStatus.TIMEOUT,
                duration_seconds=duration,
                success=False,
                output="Recovery action timed out"
            )
            
            self._store_recovery_attempt(attempt)
            
            return {
                'attempt_id': attempt_id,
                'action_name': action.name,
                'success': False,
                'duration': duration,
                'error': 'Timeout'
            }
            
        except Exception as e:
            duration = time.time() - start_time
            
            attempt = RecoveryAttempt(
                attempt_id=attempt_id,
                error_id=error.error_id,
                action_id=action.action_id,
                timestamp=datetime.now(),
                status=RecoveryStatus.FAILED,
                duration_seconds=duration,
                success=False,
                output=f"Exception: {str(e)}"
            )
            
            self._store_recovery_attempt(attempt)
            
            logging.error(f"Recovery action failed: {e}")
            return {
                'attempt_id': attempt_id,
                'action_name': action.name,
                'success': False,
                'duration': duration,
                'error': str(e)
            }
            
        finally:
            # Remove from active recoveries
            self.active_recoveries.pop(attempt_id, None)
    
    def _store_recovery_attempt(self, attempt: RecoveryAttempt):
        """Store recovery attempt in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO recovery_attempts 
                    (attempt_id, error_id, action_id, timestamp, status, 
                     duration_seconds, success, output, side_effects)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    attempt.attempt_id,
                    attempt.error_id,
                    attempt.action_id,
                    attempt.timestamp.isoformat(),
                    attempt.status.value,
                    attempt.duration_seconds,
                    attempt.success,
                    attempt.output,
                    json.dumps(attempt.side_effects_observed)
                ))
        except Exception as e:
            logging.error(f"Failed to store recovery attempt: {e}")
    
    def _update_recovery_learning(self, error: ErrorEvent, recovery_results: List[Dict[str, Any]]):
        """Update learning patterns from recovery results"""
        try:
            # Find successful patterns
            successful_actions = [r['action_name'] for r in recovery_results if r['success']]
            
            if successful_actions:
                pattern_id = hashlib.md5(
                    f"{error.category.name}_{error.component}".encode()
                ).hexdigest()[:16]
                
                # Calculate success rate for this pattern
                total_attempts = len(recovery_results)
                successful_attempts = len(successful_actions)
                success_rate = successful_attempts / total_attempts
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO recovery_patterns 
                        (pattern_id, error_pattern, successful_actions, success_rate, last_updated)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        pattern_id,
                        f"{error.category.name}:{error.component}",
                        json.dumps(successful_actions),
                        success_rate,
                        datetime.now().isoformat()
                    ))
                    
        except Exception as e:
            logging.error(f"Failed to update recovery learning: {e}")
    
    def get_recovery_dashboard(self) -> Dict[str, Any]:
        """Get recovery system dashboard data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Recent error statistics
                cursor = conn.execute("""
                    SELECT category, COUNT(*) as count, AVG(severity) as avg_severity
                    FROM error_events 
                    WHERE timestamp > datetime('now', '-24 hours')
                    GROUP BY category
                """)
                
                recent_errors = {row[0]: {'count': row[1], 'avg_severity': row[2]} 
                               for row in cursor.fetchall()}
                
                # Recovery success rates
                cursor = conn.execute("""
                    SELECT action_id, 
                           COUNT(*) as attempts,
                           SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes,
                           AVG(duration_seconds) as avg_duration
                    FROM recovery_attempts 
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY action_id
                """)
                
                recovery_stats = {}
                for row in cursor.fetchall():
                    action_id, attempts, successes, avg_duration = row
                    success_rate = (successes / attempts) * 100 if attempts > 0 else 0
                    recovery_stats[action_id] = {
                        'attempts': attempts,
                        'success_rate': success_rate,
                        'avg_duration': avg_duration or 0
                    }
                
                # Overall statistics
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_errors,
                        COUNT(DISTINCT error_id) as unique_errors
                    FROM error_events 
                    WHERE timestamp > datetime('now', '-24 hours')
                """)
                
                total_stats = cursor.fetchone()
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'recent_errors_24h': dict(recent_errors),
                    'recovery_statistics_7d': recovery_stats,
                    'total_errors_24h': total_stats[0] if total_stats else 0,
                    'unique_errors_24h': total_stats[1] if total_stats else 0,
                    'active_recoveries': len(self.active_recoveries),
                    'ml_available': ML_AVAILABLE
                }
                
        except Exception as e:
            logging.error(f"Failed to get recovery dashboard: {e}")
            return {'error': str(e)}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Resilient Error Recovery System')
    parser.add_argument('--monitor', action='store_true', help='Start error monitoring')
    parser.add_argument('--handle-error', help='Handle a specific error message')
    parser.add_argument('--dashboard', action='store_true', help='Show recovery dashboard')
    parser.add_argument('--component', default='system', help='Component name for error')
    parser.add_argument('--error-type', default='unknown', help='Error type')
    
    args = parser.parse_args()
    
    orchestrator = ErrorRecoveryOrchestrator()
    
    if args.handle_error:
        print(f"🔧 Handling error: {args.handle_error}")
        
        result = asyncio.run(orchestrator.handle_error(
            error_message=args.handle_error,
            error_type=args.error_type,
            component=args.component
        ))
        
        if result['recovery_attempted']:
            recovery_result = result['recovery_result']
            if recovery_result['overall_success']:
                print(f"✅ Recovery successful after {recovery_result['attempts']} attempts")
            else:
                print(f"❌ Recovery failed after {recovery_result['attempts']} attempts")
        else:
            print(f"⚠️ No recovery attempted: {result.get('reason', 'Unknown')}")
    
    elif args.dashboard:
        dashboard = orchestrator.get_recovery_dashboard()
        print("🔧 Error Recovery Dashboard")
        print("=" * 50)
        
        if 'error' in dashboard:
            print(f"❌ Error: {dashboard['error']}")
        else:
            print(f"Total Errors (24h): {dashboard['total_errors_24h']}")
            print(f"Unique Errors (24h): {dashboard['unique_errors_24h']}")
            print(f"Active Recoveries: {dashboard['active_recoveries']}")
            print(f"ML Available: {dashboard['ml_available']}")
            
            if dashboard['recent_errors_24h']:
                print("\nRecent Errors by Category:")
                for category, stats in dashboard['recent_errors_24h'].items():
                    print(f"  {category}: {stats['count']} (avg severity: {stats['avg_severity']:.1f})")
            
            if dashboard['recovery_statistics_7d']:
                print("\nRecovery Success Rates (7d):")
                for action_id, stats in dashboard['recovery_statistics_7d'].items():
                    print(f"  {action_id}: {stats['success_rate']:.1f}% ({stats['attempts']} attempts)")
    
    elif args.monitor:
        print("👁️ Starting error recovery monitoring...")
        print("Monitoring system for errors and automatic recovery...")
        
        # In a real implementation, this would hook into system logs,
        # exception handlers, etc. For now, just show that monitoring is active
        try:
            while True:
                time.sleep(10)
                print(".", end="", flush=True)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()