#!/usr/bin/env python3
"""
Automated Stability Monitor - Predictive monitoring with machine learning
for proactive stability management and early warning systems.

The nervous system of our software body - detecting issues before they become critical.
"""

import os
import json
import time
import asyncio
import threading
import logging
import subprocess
import sqlite3
import pickle
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
from collections import defaultdict, deque
import statistics

try:
    import sklearn
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ scikit-learn not available - using statistical methods only")

class StabilityLevel(Enum):
    CRITICAL = 0    # Immediate intervention required
    UNSTABLE = 1    # High risk of failure
    DEGRADING = 2   # Trend toward instability
    STABLE = 3      # Normal operation
    EXCELLENT = 4   # Optimal performance

class PredictionConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class StabilityMetric:
    timestamp: datetime
    component: str
    metric_name: str
    value: float
    baseline: float
    deviation: float
    trend: str  # "increasing", "decreasing", "stable"
    anomaly_score: float = 0.0

@dataclass
class StabilityPrediction:
    component: str
    predicted_failure_time: Optional[datetime]
    confidence: PredictionConfidence
    risk_factors: List[str]
    recommended_actions: List[str]
    current_trend: str
    prediction_horizon_hours: int

@dataclass
class StabilityAlert:
    alert_id: str
    timestamp: datetime
    component: str
    severity: StabilityLevel
    message: str
    metrics: List[StabilityMetric]
    prediction: Optional[StabilityPrediction]
    auto_actionable: bool

class MetricsCollector:
    """Collects and normalizes stability metrics from various sources"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.baseline_cache = {}
        self.last_collection = {}
        
    def collect_system_metrics(self) -> List[StabilityMetric]:
        """Collect comprehensive system stability metrics"""
        metrics = []
        timestamp = datetime.now()
        
        # System resource metrics
        metrics.extend(self._collect_resource_metrics(timestamp))
        
        # Git repository metrics
        metrics.extend(self._collect_git_metrics(timestamp))
        
        # Build and deployment metrics
        metrics.extend(self._collect_build_metrics(timestamp))
        
        # Code quality metrics
        metrics.extend(self._collect_quality_metrics(timestamp))
        
        # Performance metrics
        metrics.extend(self._collect_performance_metrics(timestamp))
        
        # Error rate metrics
        metrics.extend(self._collect_error_metrics(timestamp))
        
        return metrics
    
    def _collect_resource_metrics(self, timestamp: datetime) -> List[StabilityMetric]:
        """Collect system resource metrics"""
        metrics = []
        
        try:
            import psutil
            import shutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_baseline = self._get_baseline("system", "cpu_percent", 15.0)
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="system",
                metric_name="cpu_percent",
                value=cpu_percent,
                baseline=cpu_baseline,
                deviation=abs(cpu_percent - cpu_baseline) / cpu_baseline,
                trend=self._calculate_trend("system_cpu", cpu_percent)
            ))
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_baseline = self._get_baseline("system", "memory_percent", 30.0)
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="system",
                metric_name="memory_percent",
                value=memory.percent,
                baseline=memory_baseline,
                deviation=abs(memory.percent - memory_baseline) / memory_baseline,
                trend=self._calculate_trend("system_memory", memory.percent)
            ))
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                read_rate = disk_io.read_bytes / (1024 * 1024)  # MB
                write_rate = disk_io.write_bytes / (1024 * 1024)  # MB
                
                read_baseline = self._get_baseline("system", "disk_read_mb", 100.0)
                write_baseline = self._get_baseline("system", "disk_write_mb", 50.0)
                
                metrics.extend([
                    StabilityMetric(
                        timestamp=timestamp,
                        component="system",
                        metric_name="disk_read_mb",
                        value=read_rate,
                        baseline=read_baseline,
                        deviation=abs(read_rate - read_baseline) / max(read_baseline, 1),
                        trend=self._calculate_trend("disk_read", read_rate)
                    ),
                    StabilityMetric(
                        timestamp=timestamp,
                        component="system",
                        metric_name="disk_write_mb",
                        value=write_rate,
                        baseline=write_baseline,
                        deviation=abs(write_rate - write_baseline) / max(write_baseline, 1),
                        trend=self._calculate_trend("disk_write", write_rate)
                    )
                ])
            
            # Network I/O metrics
            net_io = psutil.net_io_counters()
            if net_io:
                net_sent_rate = net_io.bytes_sent / (1024 * 1024)  # MB
                net_recv_rate = net_io.bytes_recv / (1024 * 1024)  # MB
                
                sent_baseline = self._get_baseline("system", "net_sent_mb", 10.0)
                recv_baseline = self._get_baseline("system", "net_recv_mb", 20.0)
                
                metrics.extend([
                    StabilityMetric(
                        timestamp=timestamp,
                        component="system",
                        metric_name="net_sent_mb",
                        value=net_sent_rate,
                        baseline=sent_baseline,
                        deviation=abs(net_sent_rate - sent_baseline) / max(sent_baseline, 1),
                        trend=self._calculate_trend("net_sent", net_sent_rate)
                    ),
                    StabilityMetric(
                        timestamp=timestamp,
                        component="system",
                        metric_name="net_recv_mb",
                        value=net_recv_rate,
                        baseline=recv_baseline,
                        deviation=abs(net_recv_rate - recv_baseline) / max(recv_baseline, 1),
                        trend=self._calculate_trend("net_recv", net_recv_rate)
                    )
                ])
            
        except Exception as e:
            logging.error(f"Error collecting resource metrics: {e}")
        
        return metrics
    
    def _collect_git_metrics(self, timestamp: datetime) -> List[StabilityMetric]:
        """Collect Git repository stability metrics"""
        metrics = []
        
        try:
            os.chdir(self.project_root)
            
            # Repository size metrics
            git_dir_size = self._get_directory_size(".git")
            size_baseline = self._get_baseline("git", "repo_size_mb", 100.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="git",
                metric_name="repo_size_mb",
                value=git_dir_size / (1024 * 1024),
                baseline=size_baseline,
                deviation=abs((git_dir_size / (1024 * 1024)) - size_baseline) / size_baseline,
                trend=self._calculate_trend("git_size", git_dir_size)
            ))
            
            # Commit frequency metrics
            recent_commits = self._count_recent_commits(hours=24)
            commit_baseline = self._get_baseline("git", "commits_per_day", 5.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="git",
                metric_name="commits_per_day",
                value=recent_commits,
                baseline=commit_baseline,
                deviation=abs(recent_commits - commit_baseline) / max(commit_baseline, 1),
                trend=self._calculate_trend("git_commits", recent_commits)
            ))
            
            # Branch metrics
            branch_count = self._count_git_branches()
            branch_baseline = self._get_baseline("git", "branch_count", 10.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="git",
                metric_name="branch_count",
                value=branch_count,
                baseline=branch_baseline,
                deviation=abs(branch_count - branch_baseline) / max(branch_baseline, 1),
                trend=self._calculate_trend("git_branches", branch_count)
            ))
            
            # Worktree health
            worktree_count = self._count_git_worktrees()
            worktree_baseline = self._get_baseline("git", "worktree_count", 5.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="git",
                metric_name="worktree_count",
                value=worktree_count,
                baseline=worktree_baseline,
                deviation=abs(worktree_count - worktree_baseline) / max(worktree_baseline, 1),
                trend=self._calculate_trend("git_worktrees", worktree_count)
            ))
            
        except Exception as e:
            logging.error(f"Error collecting Git metrics: {e}")
        
        return metrics
    
    def _collect_build_metrics(self, timestamp: datetime) -> List[StabilityMetric]:
        """Collect build and deployment stability metrics"""
        metrics = []
        
        try:
            # Build time estimation
            package_json = os.path.join(self.project_root, "package.json")
            if os.path.exists(package_json):
                build_time = self._estimate_build_time()
                build_baseline = self._get_baseline("build", "time_seconds", 30.0)
                
                metrics.append(StabilityMetric(
                    timestamp=timestamp,
                    component="build",
                    metric_name="time_seconds",
                    value=build_time,
                    baseline=build_baseline,
                    deviation=abs(build_time - build_baseline) / max(build_baseline, 1),
                    trend=self._calculate_trend("build_time", build_time)
                ))
            
            # Dependency health
            node_modules_size = 0
            node_modules_path = os.path.join(self.project_root, "node_modules")
            if os.path.exists(node_modules_path):
                node_modules_size = self._get_directory_size(node_modules_path)
            
            deps_baseline = self._get_baseline("build", "dependencies_mb", 500.0)
            deps_size_mb = node_modules_size / (1024 * 1024)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="build",
                metric_name="dependencies_mb",
                value=deps_size_mb,
                baseline=deps_baseline,
                deviation=abs(deps_size_mb - deps_baseline) / max(deps_baseline, 1),
                trend=self._calculate_trend("deps_size", deps_size_mb)
            ))
            
        except Exception as e:
            logging.error(f"Error collecting build metrics: {e}")
        
        return metrics
    
    def _collect_quality_metrics(self, timestamp: datetime) -> List[StabilityMetric]:
        """Collect code quality stability metrics"""
        metrics = []
        
        try:
            # TypeScript error count
            ts_errors = self._count_typescript_errors()
            ts_baseline = self._get_baseline("quality", "ts_errors", 0.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="quality",
                metric_name="ts_errors",
                value=ts_errors,
                baseline=ts_baseline,
                deviation=abs(ts_errors - ts_baseline) if ts_baseline > 0 else ts_errors,
                trend=self._calculate_trend("ts_errors", ts_errors)
            ))
            
            # Code complexity metrics
            file_count = self._count_source_files()
            file_baseline = self._get_baseline("quality", "source_files", 100.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="quality",
                metric_name="source_files",
                value=file_count,
                baseline=file_baseline,
                deviation=abs(file_count - file_baseline) / max(file_baseline, 1),
                trend=self._calculate_trend("source_files", file_count)
            ))
            
            # Test coverage estimation
            test_files = self._count_test_files()
            test_baseline = self._get_baseline("quality", "test_files", 20.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="quality",
                metric_name="test_files",
                value=test_files,
                baseline=test_baseline,
                deviation=abs(test_files - test_baseline) / max(test_baseline, 1),
                trend=self._calculate_trend("test_files", test_files)
            ))
            
        except Exception as e:
            logging.error(f"Error collecting quality metrics: {e}")
        
        return metrics
    
    def _collect_performance_metrics(self, timestamp: datetime) -> List[StabilityMetric]:
        """Collect performance stability metrics"""
        metrics = []
        
        try:
            # File I/O performance test
            io_latency = self._measure_file_io_latency()
            io_baseline = self._get_baseline("performance", "file_io_ms", 10.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="performance",
                metric_name="file_io_ms",
                value=io_latency,
                baseline=io_baseline,
                deviation=abs(io_latency - io_baseline) / max(io_baseline, 1),
                trend=self._calculate_trend("file_io", io_latency)
            ))
            
            # Git operation performance
            git_latency = self._measure_git_operation_latency()
            git_baseline = self._get_baseline("performance", "git_op_ms", 100.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="performance",
                metric_name="git_op_ms",
                value=git_latency,
                baseline=git_baseline,
                deviation=abs(git_latency - git_baseline) / max(git_baseline, 1),
                trend=self._calculate_trend("git_op", git_latency)
            ))
            
        except Exception as e:
            logging.error(f"Error collecting performance metrics: {e}")
        
        return metrics
    
    def _collect_error_metrics(self, timestamp: datetime) -> List[StabilityMetric]:
        """Collect error rate and failure metrics"""
        metrics = []
        
        try:
            # Log file error analysis
            error_count = self._count_recent_errors()
            error_baseline = self._get_baseline("errors", "error_count", 0.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="errors",
                metric_name="error_count",
                value=error_count,
                baseline=error_baseline,
                deviation=error_count if error_baseline == 0 else abs(error_count - error_baseline) / max(error_baseline, 1),
                trend=self._calculate_trend("error_count", error_count)
            ))
            
            # Process failure count
            process_failures = self._count_process_failures()
            process_baseline = self._get_baseline("errors", "process_failures", 0.0)
            
            metrics.append(StabilityMetric(
                timestamp=timestamp,
                component="errors",
                metric_name="process_failures",
                value=process_failures,
                baseline=process_baseline,
                deviation=process_failures if process_baseline == 0 else abs(process_failures - process_baseline) / max(process_baseline, 1),
                trend=self._calculate_trend("process_failures", process_failures)
            ))
            
        except Exception as e:
            logging.error(f"Error collecting error metrics: {e}")
        
        return metrics
    
    def _get_baseline(self, component: str, metric: str, default: float) -> float:
        """Get or establish baseline for a metric"""
        key = f"{component}_{metric}"
        
        if key not in self.baseline_cache:
            # Try to load from database or use default
            self.baseline_cache[key] = default
        
        return self.baseline_cache[key]
    
    def _calculate_trend(self, metric_key: str, current_value: float) -> str:
        """Calculate trend for a metric"""
        if metric_key not in self.last_collection:
            self.last_collection[metric_key] = deque(maxlen=10)
        
        self.last_collection[metric_key].append(current_value)
        
        if len(self.last_collection[metric_key]) < 3:
            return "stable"
        
        recent_values = list(self.last_collection[metric_key])
        
        # Simple trend analysis
        if len(recent_values) >= 3:
            slope = (recent_values[-1] - recent_values[0]) / len(recent_values)
            
            if slope > 0.1 * recent_values[0]:
                return "increasing"
            elif slope < -0.1 * recent_values[0]:
                return "decreasing"
        
        return "stable"
    
    # Helper methods for specific metric collection
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
    
    def _count_recent_commits(self, hours: int = 24) -> int:
        """Count commits in recent time period"""
        try:
            since = datetime.now() - timedelta(hours=hours)
            result = subprocess.run([
                "git", "rev-list", "--count", 
                f"--since={since.isoformat()}", "HEAD"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return int(result.stdout.strip() or "0")
        except Exception:
            pass
        return 0
    
    def _count_git_branches(self) -> int:
        """Count total Git branches"""
        try:
            result = subprocess.run([
                "git", "branch", "-a"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n'))
        except Exception:
            pass
        return 0
    
    def _count_git_worktrees(self) -> int:
        """Count Git worktrees"""
        try:
            result = subprocess.run([
                "git", "worktree", "list"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n'))
        except Exception:
            pass
        return 0
    
    def _estimate_build_time(self) -> float:
        """Estimate build time based on project size"""
        try:
            # Simple heuristic based on file count and size
            source_files = self._count_source_files()
            return max(10.0, source_files * 0.5)  # Rough estimate
        except Exception:
            return 30.0
    
    def _count_typescript_errors(self) -> int:
        """Count TypeScript compilation errors"""
        try:
            result = subprocess.run([
                "npx", "tsc", "--noEmit", "--pretty", "false"
            ], capture_output=True, text=True, timeout=30, cwd=self.project_root)
            
            if result.returncode != 0:
                # Count error lines
                error_lines = [line for line in result.stdout.split('\n') 
                             if 'error TS' in line]
                return len(error_lines)
        except Exception:
            pass
        return 0
    
    def _count_source_files(self) -> int:
        """Count TypeScript/JavaScript source files"""
        count = 0
        for root, dirs, files in os.walk(self.project_root):
            # Skip node_modules and other irrelevant directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'dist', 'build']]
            
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    count += 1
        return count
    
    def _count_test_files(self) -> int:
        """Count test files"""
        count = 0
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git']]
            
            for file in files:
                if any(pattern in file for pattern in ['.test.', '.spec.', '__tests__']):
                    count += 1
        return count
    
    def _measure_file_io_latency(self) -> float:
        """Measure file I/O latency"""
        try:
            test_file = os.path.join(self.project_root, "monitoring", "io_test.tmp")
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            
            start_time = time.time()
            
            # Write test
            with open(test_file, "w") as f:
                f.write("performance_test" * 100)
            
            # Read test
            with open(test_file, "r") as f:
                content = f.read()
            
            # Clean up
            os.remove(test_file)
            
            return (time.time() - start_time) * 1000  # Convert to milliseconds
            
        except Exception:
            return 100.0  # Default high latency on error
    
    def _measure_git_operation_latency(self) -> float:
        """Measure Git operation latency"""
        try:
            start_time = time.time()
            subprocess.run(["git", "status", "--porcelain"], 
                         capture_output=True, text=True, timeout=10)
            return (time.time() - start_time) * 1000
        except Exception:
            return 500.0  # Default high latency on error
    
    def _count_recent_errors(self) -> int:
        """Count recent errors in log files"""
        error_count = 0
        logs_dir = os.path.join(self.project_root, "logs")
        
        if os.path.exists(logs_dir):
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            for log_file in os.listdir(logs_dir):
                if log_file.endswith('.log'):
                    log_path = os.path.join(logs_dir, log_file)
                    try:
                        mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
                        if mtime > cutoff_time:
                            with open(log_path, 'r') as f:
                                content = f.read()
                                error_count += content.lower().count('error')
                                error_count += content.lower().count('exception')
                                error_count += content.lower().count('failed')
                    except Exception:
                        continue
        
        return error_count
    
    def _count_process_failures(self) -> int:
        """Count recent process failures"""
        # This would check for recently failed processes
        # For now, return 0 as a placeholder
        return 0

class StabilityPredictor:
    """Predictive analytics for system stability"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.models = {}
        self.scalers = {}
        self.training_data = defaultdict(list)
        self.prediction_cache = {}
        
        # Model file paths
        self.models_dir = os.path.join(project_root, "monitoring", "models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.load_models()
    
    def train_models(self, historical_metrics: List[StabilityMetric]):
        """Train prediction models on historical data"""
        if not ML_AVAILABLE:
            logging.warning("Machine learning not available - using statistical methods only")
            return
        
        # Group metrics by component
        component_data = defaultdict(list)
        for metric in historical_metrics:
            component_data[metric.component].append(metric)
        
        for component, metrics in component_data.items():
            if len(metrics) < 50:  # Need sufficient data for training
                continue
            
            try:
                # Prepare training data
                X, y = self._prepare_training_data(metrics)
                
                if len(X) == 0:
                    continue
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train anomaly detection model
                anomaly_model = IsolationForest(
                    contamination=0.1, random_state=42
                )
                anomaly_model.fit(X_train_scaled)
                
                # Train classification model for failure prediction
                classifier = RandomForestClassifier(
                    n_estimators=100, random_state=42
                )
                classifier.fit(X_train_scaled, y_train)
                
                # Store models
                self.models[component] = {
                    'anomaly': anomaly_model,
                    'classifier': classifier,
                    'trained_at': datetime.now()
                }
                self.scalers[component] = scaler
                
                # Save models to disk
                self._save_model(component, anomaly_model, classifier, scaler)
                
                logging.info(f"Trained models for component: {component}")
                
            except Exception as e:
                logging.error(f"Error training models for {component}: {e}")
    
    def predict_stability(self, current_metrics: List[StabilityMetric]) -> List[StabilityPrediction]:
        """Predict future stability issues"""
        predictions = []
        
        # Group metrics by component
        component_metrics = defaultdict(list)
        for metric in current_metrics:
            component_metrics[metric.component].append(metric)
        
        for component, metrics in component_metrics.items():
            try:
                prediction = self._predict_component_stability(component, metrics)
                if prediction:
                    predictions.append(prediction)
            except Exception as e:
                logging.error(f"Error predicting stability for {component}: {e}")
        
        return predictions
    
    def _prepare_training_data(self, metrics: List[StabilityMetric]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from historical metrics"""
        features = []
        labels = []
        
        # Sort metrics by timestamp
        sorted_metrics = sorted(metrics, key=lambda m: m.timestamp)
        
        # Create sliding windows of metrics for features
        window_size = 10
        for i in range(len(sorted_metrics) - window_size):
            window_metrics = sorted_metrics[i:i + window_size]
            
            # Extract features from window
            feature_vector = []
            for metric in window_metrics:
                feature_vector.extend([
                    metric.value,
                    metric.deviation,
                    1 if metric.trend == "increasing" else -1 if metric.trend == "decreasing" else 0
                ])
            
            features.append(feature_vector)
            
            # Label: 1 if any metric in next period shows high deviation, 0 otherwise
            next_period = sorted_metrics[i + window_size:i + window_size + 5]
            label = 1 if any(m.deviation > 0.5 for m in next_period) else 0
            labels.append(label)
        
        return np.array(features), np.array(labels)
    
    def _predict_component_stability(self, component: str, metrics: List[StabilityMetric]) -> Optional[StabilityPrediction]:
        """Predict stability for a specific component"""
        if component not in self.models and not self._use_statistical_prediction(metrics):
            return None
        
        try:
            # Use ML model if available
            if component in self.models and ML_AVAILABLE:
                return self._ml_predict_stability(component, metrics)
            else:
                return self._statistical_predict_stability(component, metrics)
                
        except Exception as e:
            logging.error(f"Error in component prediction for {component}: {e}")
            return None
    
    def _ml_predict_stability(self, component: str, metrics: List[StabilityMetric]) -> StabilityPrediction:
        """Use ML models for stability prediction"""
        models = self.models[component]
        scaler = self.scalers[component]
        
        # Prepare current features
        feature_vector = []
        for metric in metrics[-10:]:  # Use last 10 metrics
            feature_vector.extend([
                metric.value,
                metric.deviation,
                1 if metric.trend == "increasing" else -1 if metric.trend == "decreasing" else 0
            ])
        
        # Pad if insufficient data
        while len(feature_vector) < 30:  # 10 metrics * 3 features each
            feature_vector.append(0)
        
        # Scale features
        features_scaled = scaler.transform([feature_vector])
        
        # Get anomaly score
        anomaly_score = models['anomaly'].decision_function(features_scaled)[0]
        is_anomaly = models['anomaly'].predict(features_scaled)[0] == -1
        
        # Get failure probability
        failure_prob = models['classifier'].predict_proba(features_scaled)[0][1]
        
        # Determine prediction details
        confidence = PredictionConfidence.HIGH if failure_prob > 0.8 else \
                    PredictionConfidence.MEDIUM if failure_prob > 0.5 else \
                    PredictionConfidence.LOW
        
        # Estimate failure time based on trend analysis
        predicted_failure_time = None
        if failure_prob > 0.5:
            # Simple trend-based estimation
            deteriorating_metrics = [m for m in metrics if m.deviation > 0.3 and m.trend == "increasing"]
            if deteriorating_metrics:
                avg_rate = statistics.mean([m.deviation for m in deteriorating_metrics])
                hours_to_failure = max(1, int(1.0 / avg_rate * 24))  # Rough estimation
                predicted_failure_time = datetime.now() + timedelta(hours=hours_to_failure)
        
        # Generate risk factors and recommendations
        risk_factors = []
        recommendations = []
        
        if is_anomaly:
            risk_factors.append("Anomalous behavior detected")
            recommendations.append("Investigate recent changes")
        
        if failure_prob > 0.7:
            risk_factors.append("High failure probability")
            recommendations.append("Consider preventive maintenance")
        
        # Analyze specific metrics for additional insights
        for metric in metrics:
            if metric.deviation > 0.5:
                risk_factors.append(f"High deviation in {metric.metric_name}")
                recommendations.append(f"Monitor {metric.metric_name} closely")
        
        return StabilityPrediction(
            component=component,
            predicted_failure_time=predicted_failure_time,
            confidence=confidence,
            risk_factors=risk_factors,
            recommended_actions=recommendations,
            current_trend=self._analyze_overall_trend(metrics),
            prediction_horizon_hours=24
        )
    
    def _statistical_predict_stability(self, component: str, metrics: List[StabilityMetric]) -> StabilityPrediction:
        """Use statistical methods for stability prediction when ML is unavailable"""
        # Simple statistical analysis
        recent_metrics = metrics[-5:]  # Last 5 measurements
        
        # Calculate average deviation
        avg_deviation = statistics.mean([m.deviation for m in recent_metrics]) if recent_metrics else 0
        
        # Count deteriorating trends
        deteriorating_count = sum(1 for m in recent_metrics if m.trend == "increasing" and m.deviation > 0.2)
        
        # Simple risk assessment
        risk_score = avg_deviation + (deteriorating_count * 0.2)
        
        # Determine confidence and prediction
        if risk_score > 0.8:
            confidence = PredictionConfidence.HIGH
            failure_time = datetime.now() + timedelta(hours=6)
        elif risk_score > 0.5:
            confidence = PredictionConfidence.MEDIUM
            failure_time = datetime.now() + timedelta(hours=24)
        elif risk_score > 0.3:
            confidence = PredictionConfidence.LOW
            failure_time = None
        else:
            confidence = PredictionConfidence.LOW
            failure_time = None
        
        # Generate basic recommendations
        risk_factors = []
        recommendations = []
        
        if avg_deviation > 0.4:
            risk_factors.append("High average deviation from baseline")
            recommendations.append("Review recent system changes")
        
        if deteriorating_count > 2:
            risk_factors.append("Multiple metrics showing deteriorating trends")
            recommendations.append("Investigate system performance")
        
        return StabilityPrediction(
            component=component,
            predicted_failure_time=failure_time,
            confidence=confidence,
            risk_factors=risk_factors,
            recommended_actions=recommendations,
            current_trend=self._analyze_overall_trend(recent_metrics),
            prediction_horizon_hours=24
        )
    
    def _use_statistical_prediction(self, metrics: List[StabilityMetric]) -> bool:
        """Determine if we should use statistical prediction"""
        return len(metrics) >= 5  # Need at least 5 data points
    
    def _analyze_overall_trend(self, metrics: List[StabilityMetric]) -> str:
        """Analyze overall trend across all metrics"""
        if not metrics:
            return "stable"
        
        increasing_count = sum(1 for m in metrics if m.trend == "increasing")
        decreasing_count = sum(1 for m in metrics if m.trend == "decreasing")
        
        if increasing_count > decreasing_count * 1.5:
            return "deteriorating"
        elif decreasing_count > increasing_count * 1.5:
            return "improving"
        else:
            return "stable"
    
    def _save_model(self, component: str, anomaly_model, classifier, scaler):
        """Save trained models to disk"""
        model_file = os.path.join(self.models_dir, f"{component}_models.pkl")
        try:
            with open(model_file, 'wb') as f:
                pickle.dump({
                    'anomaly': anomaly_model,
                    'classifier': classifier,
                    'scaler': scaler,
                    'trained_at': datetime.now()
                }, f)
        except Exception as e:
            logging.error(f"Failed to save model for {component}: {e}")
    
    def load_models(self):
        """Load trained models from disk"""
        for model_file in os.listdir(self.models_dir):
            if model_file.endswith('_models.pkl'):
                component = model_file.replace('_models.pkl', '')
                model_path = os.path.join(self.models_dir, model_file)
                
                try:
                    with open(model_path, 'rb') as f:
                        data = pickle.load(f)
                        self.models[component] = {
                            'anomaly': data['anomaly'],
                            'classifier': data['classifier'],
                            'trained_at': data['trained_at']
                        }
                        self.scalers[component] = data['scaler']
                        
                    logging.info(f"Loaded models for component: {component}")
                except Exception as e:
                    logging.error(f"Failed to load model for {component}: {e}")

class StabilityMonitor:
    """Main stability monitoring system"""
    
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.collector = MetricsCollector(project_root)
        self.predictor = StabilityPredictor(project_root)
        
        # Database setup
        self.db_path = os.path.join(project_root, "monitoring", "stability.db")
        self._init_database()
        
        # Configuration
        self.monitoring_active = True
        self.collection_interval = 30  # seconds
        self.prediction_interval = 300  # 5 minutes
        
        # Alert thresholds
        self.alert_thresholds = {
            StabilityLevel.CRITICAL: 0.9,
            StabilityLevel.UNSTABLE: 0.7,
            StabilityLevel.DEGRADING: 0.5
        }
        
        # Setup logging
        self.setup_logging()
    
    def _init_database(self):
        """Initialize stability monitoring database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS stability_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    baseline REAL NOT NULL,
                    deviation REAL NOT NULL,
                    trend TEXT NOT NULL,
                    anomaly_score REAL DEFAULT 0.0
                );
                
                CREATE TABLE IF NOT EXISTS stability_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    predicted_failure_time TEXT,
                    confidence TEXT NOT NULL,
                    risk_factors TEXT,
                    recommended_actions TEXT,
                    current_trend TEXT
                );
                
                CREATE TABLE IF NOT EXISTS stability_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    auto_actionable BOOLEAN DEFAULT FALSE,
                    resolved BOOLEAN DEFAULT FALSE
                );
                
                CREATE INDEX IF NOT EXISTS idx_metrics_component_time 
                ON stability_metrics(component, timestamp);
                CREATE INDEX IF NOT EXISTS idx_predictions_time 
                ON stability_predictions(timestamp);
                CREATE INDEX IF NOT EXISTS idx_alerts_time 
                ON stability_alerts(timestamp);
            """)
    
    def setup_logging(self):
        """Setup monitoring logging"""
        log_file = os.path.join(self.project_root, "logs", "stability-monitor.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    async def start_monitoring(self):
        """Start continuous stability monitoring"""
        logging.info("🔍 Starting automated stability monitoring...")
        
        # Start collection and prediction tasks
        collection_task = asyncio.create_task(self._collection_loop())
        prediction_task = asyncio.create_task(self._prediction_loop())
        
        try:
            await asyncio.gather(collection_task, prediction_task)
        except KeyboardInterrupt:
            logging.info("Monitoring stopped by user")
        except Exception as e:
            logging.error(f"Monitoring error: {e}")
        finally:
            self.monitoring_active = False
    
    async def _collection_loop(self):
        """Continuous metrics collection loop"""
        while self.monitoring_active:
            try:
                # Collect current metrics
                metrics = self.collector.collect_system_metrics()
                
                # Store metrics in database
                self._store_metrics(metrics)
                
                # Check for immediate alerts
                await self._check_immediate_alerts(metrics)
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logging.error(f"Error in collection loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _prediction_loop(self):
        """Continuous prediction loop"""
        while self.monitoring_active:
            try:
                # Get recent metrics for prediction
                recent_metrics = self._get_recent_metrics(hours=24)
                
                if len(recent_metrics) > 100:  # Need sufficient data
                    # Make predictions
                    predictions = self.predictor.predict_stability(recent_metrics)
                    
                    # Store predictions
                    self._store_predictions(predictions)
                    
                    # Generate predictive alerts
                    await self._check_predictive_alerts(predictions)
                
                await asyncio.sleep(self.prediction_interval)
                
            except Exception as e:
                logging.error(f"Error in prediction loop: {e}")
                await asyncio.sleep(self.prediction_interval)
    
    def _store_metrics(self, metrics: List[StabilityMetric]):
        """Store metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for metric in metrics:
                    conn.execute("""
                        INSERT INTO stability_metrics 
                        (timestamp, component, metric_name, value, baseline, deviation, trend, anomaly_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metric.timestamp.isoformat(),
                        metric.component,
                        metric.metric_name,
                        metric.value,
                        metric.baseline,
                        metric.deviation,
                        metric.trend,
                        metric.anomaly_score
                    ))
        except Exception as e:
            logging.error(f"Failed to store metrics: {e}")
    
    def _store_predictions(self, predictions: List[StabilityPrediction]):
        """Store predictions in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for prediction in predictions:
                    conn.execute("""
                        INSERT INTO stability_predictions 
                        (timestamp, component, predicted_failure_time, confidence, 
                         risk_factors, recommended_actions, current_trend)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().isoformat(),
                        prediction.component,
                        prediction.predicted_failure_time.isoformat() if prediction.predicted_failure_time else None,
                        prediction.confidence.value,
                        json.dumps(prediction.risk_factors),
                        json.dumps(prediction.recommended_actions),
                        prediction.current_trend
                    ))
        except Exception as e:
            logging.error(f"Failed to store predictions: {e}")
    
    async def _check_immediate_alerts(self, metrics: List[StabilityMetric]):
        """Check for immediate stability alerts"""
        for metric in metrics:
            # Check for critical deviations
            if metric.deviation > self.alert_thresholds[StabilityLevel.CRITICAL]:
                alert = StabilityAlert(
                    alert_id=f"critical_{metric.component}_{metric.metric_name}_{int(time.time())}",
                    timestamp=datetime.now(),
                    component=metric.component,
                    severity=StabilityLevel.CRITICAL,
                    message=f"Critical deviation in {metric.metric_name}: {metric.deviation:.2f}",
                    metrics=[metric],
                    prediction=None,
                    auto_actionable=True
                )
                await self._process_alert(alert)
            
            elif metric.deviation > self.alert_thresholds[StabilityLevel.UNSTABLE]:
                alert = StabilityAlert(
                    alert_id=f"unstable_{metric.component}_{metric.metric_name}_{int(time.time())}",
                    timestamp=datetime.now(),
                    component=metric.component,
                    severity=StabilityLevel.UNSTABLE,
                    message=f"Unstable behavior in {metric.metric_name}: {metric.deviation:.2f}",
                    metrics=[metric],
                    prediction=None,
                    auto_actionable=True
                )
                await self._process_alert(alert)
    
    async def _check_predictive_alerts(self, predictions: List[StabilityPrediction]):
        """Check for predictive stability alerts"""
        for prediction in predictions:
            if prediction.confidence in [PredictionConfidence.HIGH, PredictionConfidence.VERY_HIGH]:
                if prediction.predicted_failure_time:
                    time_to_failure = prediction.predicted_failure_time - datetime.now()
                    if time_to_failure.total_seconds() < 3600:  # Less than 1 hour
                        severity = StabilityLevel.CRITICAL
                    elif time_to_failure.total_seconds() < 6 * 3600:  # Less than 6 hours
                        severity = StabilityLevel.UNSTABLE
                    else:
                        severity = StabilityLevel.DEGRADING
                    
                    alert = StabilityAlert(
                        alert_id=f"predictive_{prediction.component}_{int(time.time())}",
                        timestamp=datetime.now(),
                        component=prediction.component,
                        severity=severity,
                        message=f"Predicted failure in {prediction.component} at {prediction.predicted_failure_time}",
                        metrics=[],
                        prediction=prediction,
                        auto_actionable=len(prediction.recommended_actions) > 0
                    )
                    await self._process_alert(alert)
    
    async def _process_alert(self, alert: StabilityAlert):
        """Process and respond to stability alerts"""
        # Store alert
        self._store_alert(alert)
        
        # Log alert
        severity_emoji = {
            StabilityLevel.CRITICAL: "🚨",
            StabilityLevel.UNSTABLE: "⚠️",
            StabilityLevel.DEGRADING: "📉"
        }
        
        emoji = severity_emoji.get(alert.severity, "ℹ️")
        logging.warning(f"{emoji} STABILITY ALERT: {alert.message}")
        
        # Take automatic action if possible
        if alert.auto_actionable:
            await self._take_automatic_action(alert)
    
    def _store_alert(self, alert: StabilityAlert):
        """Store alert in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR IGNORE INTO stability_alerts 
                    (alert_id, timestamp, component, severity, message, auto_actionable)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.timestamp.isoformat(),
                    alert.component,
                    alert.severity.name,
                    alert.message,
                    alert.auto_actionable
                ))
        except Exception as e:
            logging.error(f"Failed to store alert: {e}")
    
    async def _take_automatic_action(self, alert: StabilityAlert):
        """Take automatic remediation action"""
        try:
            if alert.severity == StabilityLevel.CRITICAL:
                # Trigger emergency procedures
                logging.info(f"Triggering emergency procedures for {alert.component}")
                # Could trigger the self-healing system here
                
            elif alert.prediction and alert.prediction.recommended_actions:
                # Execute recommended actions
                for action in alert.prediction.recommended_actions:
                    logging.info(f"Executing recommended action: {action}")
                    # Implement specific actions based on the recommendation
                    
        except Exception as e:
            logging.error(f"Failed to take automatic action: {e}")
    
    def _get_recent_metrics(self, hours: int = 24) -> List[StabilityMetric]:
        """Get recent metrics from database"""
        metrics = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, component, metric_name, value, baseline, deviation, trend, anomaly_score
                    FROM stability_metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                """, (cutoff_time.isoformat(),))
                
                for row in cursor.fetchall():
                    metrics.append(StabilityMetric(
                        timestamp=datetime.fromisoformat(row[0]),
                        component=row[1],
                        metric_name=row[2],
                        value=row[3],
                        baseline=row[4],
                        deviation=row[5],
                        trend=row[6],
                        anomaly_score=row[7]
                    ))
        except Exception as e:
            logging.error(f"Failed to get recent metrics: {e}")
        
        return metrics
    
    def get_stability_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive stability dashboard data"""
        # Get current metrics
        current_metrics = self.collector.collect_system_metrics()
        
        # Get recent predictions
        recent_predictions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT component, predicted_failure_time, confidence, risk_factors, recommended_actions
                    FROM stability_predictions 
                    WHERE timestamp > datetime('now', '-1 hour')
                    ORDER BY timestamp DESC
                    LIMIT 10
                """)
                
                for row in cursor.fetchall():
                    recent_predictions.append({
                        'component': row[0],
                        'predicted_failure_time': row[1],
                        'confidence': row[2],
                        'risk_factors': json.loads(row[3]) if row[3] else [],
                        'recommended_actions': json.loads(row[4]) if row[4] else []
                    })
        except Exception as e:
            logging.error(f"Failed to get recent predictions: {e}")
        
        # Get active alerts
        active_alerts = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT component, severity, message, timestamp
                    FROM stability_alerts 
                    WHERE resolved = FALSE AND timestamp > datetime('now', '-24 hours')
                    ORDER BY timestamp DESC
                """)
                
                for row in cursor.fetchall():
                    active_alerts.append({
                        'component': row[0],
                        'severity': row[1],
                        'message': row[2],
                        'timestamp': row[3]
                    })
        except Exception as e:
            logging.error(f"Failed to get active alerts: {e}")
        
        # Calculate overall stability score
        stability_score = self._calculate_stability_score(current_metrics)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_stability_score': stability_score,
            'stability_level': self._get_stability_level(stability_score).name,
            'current_metrics': [asdict(m) for m in current_metrics],
            'recent_predictions': recent_predictions,
            'active_alerts': active_alerts,
            'monitoring_active': self.monitoring_active,
            'ml_available': ML_AVAILABLE
        }
    
    def _calculate_stability_score(self, metrics: List[StabilityMetric]) -> float:
        """Calculate overall stability score (0-100)"""
        if not metrics:
            return 50.0  # Neutral score
        
        # Weight metrics by component importance
        component_weights = {
            'system': 0.25,
            'git': 0.20,
            'build': 0.15,
            'quality': 0.15,
            'performance': 0.15,
            'errors': 0.10
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for component, weight in component_weights.items():
            component_metrics = [m for m in metrics if m.component == component]
            if component_metrics:
                # Calculate component score based on deviations
                avg_deviation = statistics.mean([m.deviation for m in component_metrics])
                component_score = max(0, 100 - (avg_deviation * 100))
                
                weighted_score += component_score * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        else:
            return 50.0
    
    def _get_stability_level(self, score: float) -> StabilityLevel:
        """Convert score to stability level"""
        if score >= 90:
            return StabilityLevel.EXCELLENT
        elif score >= 70:
            return StabilityLevel.STABLE
        elif score >= 50:
            return StabilityLevel.DEGRADING
        elif score >= 30:
            return StabilityLevel.UNSTABLE
        else:
            return StabilityLevel.CRITICAL

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Stability Monitor')
    parser.add_argument('--start', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--dashboard', action='store_true', help='Show stability dashboard')
    parser.add_argument('--train', action='store_true', help='Train prediction models')
    parser.add_argument('--collect', action='store_true', help='Collect metrics once')
    parser.add_argument('--predict', action='store_true', help='Make stability predictions')
    
    args = parser.parse_args()
    
    monitor = StabilityMonitor()
    
    if args.start:
        print("🔍 Starting automated stability monitoring...")
        asyncio.run(monitor.start_monitoring())
    
    elif args.dashboard:
        dashboard = monitor.get_stability_dashboard()
        print("📊 Stability Dashboard")
        print("=" * 50)
        print(f"Overall Stability Score: {dashboard['overall_stability_score']:.1f}")
        print(f"Stability Level: {dashboard['stability_level']}")
        print(f"ML Available: {dashboard['ml_available']}")
        print(f"Active Alerts: {len(dashboard['active_alerts'])}")
        print(f"Recent Predictions: {len(dashboard['recent_predictions'])}")
        
        if dashboard['active_alerts']:
            print("\n🚨 Active Alerts:")
            for alert in dashboard['active_alerts']:
                print(f"  - {alert['component']}: {alert['message']}")
    
    elif args.collect:
        print("📈 Collecting stability metrics...")
        metrics = monitor.collector.collect_system_metrics()
        monitor._store_metrics(metrics)
        print(f"Collected {len(metrics)} metrics")
    
    elif args.train:
        print("🤖 Training prediction models...")
        recent_metrics = monitor._get_recent_metrics(hours=168)  # Last week
        if len(recent_metrics) > 100:
            monitor.predictor.train_models(recent_metrics)
            print("✅ Model training completed")
        else:
            print("⚠️ Insufficient data for training (need at least 100 metrics)")
    
    elif args.predict:
        print("🔮 Making stability predictions...")
        recent_metrics = monitor._get_recent_metrics(hours=24)
        predictions = monitor.predictor.predict_stability(recent_metrics)
        
        if predictions:
            for prediction in predictions:
                print(f"\n📊 {prediction.component}:")
                print(f"  Confidence: {prediction.confidence.value}")
                print(f"  Trend: {prediction.current_trend}")
                if prediction.predicted_failure_time:
                    print(f"  Predicted Issue: {prediction.predicted_failure_time}")
                if prediction.risk_factors:
                    print(f"  Risk Factors: {', '.join(prediction.risk_factors)}")
        else:
            print("No predictions available")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()