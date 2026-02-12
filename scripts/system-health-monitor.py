#!/usr/bin/env python3
"""
System Health Monitor - Final component completion for self-healing system
Provides comprehensive system monitoring and health status for HardCard Multi-Agent System
"""

import os
import json
import time
import subprocess
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import sqlite3
from dataclasses import dataclass, asdict

@dataclass
class HealthEvent:
    timestamp: str
    event_type: str
    severity: str
    component: str
    message: str
    metrics: Dict[str, Any]
    auto_resolved: bool = False

class SystemHealthMonitor:
    """Complete system health monitoring and alerting"""
    
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.monitoring_active = True
        self.health_db = f"{project_root}/monitoring/health.db"
        self.alert_history = []
        self.last_alert_time = {}
        self.alert_cooldown = 1800  # 30 minutes
        
        # Ensure monitoring directory exists
        Path(f"{project_root}/monitoring").mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            filename=f"{project_root}/logs/health-monitor.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize database
        self._init_health_database()
        
        # Health thresholds
        self.thresholds = {
            "cpu_critical": 95.0,
            "cpu_warning": 80.0,
            "memory_critical": 90.0,
            "memory_warning": 75.0,
            "disk_critical": 95.0,
            "disk_warning": 85.0,
            "load_critical": 10.0,
            "load_warning": 5.0
        }
    
    def _init_health_database(self):
        """Initialize SQLite database for health events"""
        with sqlite3.connect(self.health_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    component TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metrics TEXT,
                    auto_resolved BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    load_avg_1m REAL,
                    load_avg_5m REAL,
                    load_avg_15m REAL,
                    process_count INTEGER,
                    worktree_count INTEGER
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON health_events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)")
    
    def get_comprehensive_health_status(self) -> Dict[str, Any]:
        """Get complete system health status"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(self.project_root)
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            # Process metrics
            process_count = len(list(psutil.process_iter()))
            project_processes = self._get_project_processes()
            
            # Git worktree status
            worktree_status = self._get_worktree_status()
            
            # Service status
            service_status = self._check_service_health()
            
            # File system health
            filesystem_health = self._check_filesystem_health()
            
            # Calculate overall health score
            health_score = self._calculate_health_score({
                "cpu": cpu_percent,
                "memory": memory.percent,
                "disk": (disk.used / disk.total) * 100,
                "load": load_avg[0]
            })
            
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall_health_score": health_score,
                "status": self._get_status_from_score(health_score),
                "system": {
                    "cpu": {
                        "usage_percent": cpu_percent,
                        "core_count": psutil.cpu_count(),
                        "load_average": {
                            "1m": load_avg[0],
                            "5m": load_avg[1],
                            "15m": load_avg[2]
                        }
                    },
                    "memory": {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "used_gb": round(memory.used / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "usage_percent": memory.percent
                    },
                    "disk": {
                        "total_gb": round(disk.total / (1024**3), 2),
                        "used_gb": round(disk.used / (1024**3), 2),
                        "free_gb": round(disk.free / (1024**3), 2),
                        "usage_percent": round((disk.used / disk.total) * 100, 2)
                    }
                },
                "processes": {
                    "total_count": process_count,
                    "project_processes": project_processes,
                    "critical_services": service_status
                },
                "git": worktree_status,
                "filesystem": filesystem_health,
                "alerts": self._get_recent_alerts(hours=24),
                "recommendations": self._generate_health_recommendations(health_score)
            }
            
            # Store metrics in database
            self._store_metrics(health_status)
            
            # Check for health issues and generate alerts
            self._check_health_alerts(health_status)
            
            return health_status
            
        except Exception as e:
            logging.error(f"Error getting health status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_health_score": 0,
                "status": "error",
                "error": str(e)
            }
    
    def _get_project_processes(self) -> List[Dict[str, Any]]:
        """Get processes related to HardCard project"""
        project_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    # Check if process is related to our project
                    if any(keyword in cmdline.lower() for keyword in 
                          ['hardcard', 'claude', 'worktree', 'vetsorcery', 'startup-enforcer', 'monitor']):
                        
                        project_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "status": proc.info['status'],
                            "cpu_percent": proc.info['cpu_percent'] or 0,
                            "memory_percent": proc.info['memory_percent'] or 0,
                            "cmdline": cmdline[:100]  # Truncate for readability
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logging.error(f"Error getting project processes: {e}")
            
        return project_processes
    
    def _get_worktree_status(self) -> Dict[str, Any]:
        """Get Git worktree health status"""
        try:
            os.chdir(self.project_root)
            
            # Git status
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, text=True, timeout=10)
            uncommitted_files = len(status_result.stdout.strip().split('\n')) if status_result.stdout.strip() else 0
            
            # Worktree list
            worktree_result = subprocess.run(['git', 'worktree', 'list', '--porcelain'], 
                                           capture_output=True, text=True, timeout=10)
            
            worktrees = []
            if worktree_result.stdout:
                lines = worktree_result.stdout.strip().split('\n')
                current_worktree = {}
                
                for line in lines:
                    if line.startswith('worktree '):
                        if current_worktree:
                            worktrees.append(current_worktree)
                        current_worktree = {"path": line.split(' ', 1)[1]}
                    elif line.startswith('branch '):
                        current_worktree["branch"] = line.split(' ', 1)[1]
                    elif line.startswith('HEAD '):
                        current_worktree["head"] = line.split(' ', 1)[1]
                
                if current_worktree:
                    worktrees.append(current_worktree)
            
            # Check for corruption
            fsck_result = subprocess.run(['git', 'fsck', '--no-progress'], 
                                       capture_output=True, text=True, timeout=30)
            corruption_detected = "error" in fsck_result.stderr.lower() or fsck_result.returncode != 0
            
            return {
                "worktree_count": len(worktrees),
                "worktrees": worktrees,
                "uncommitted_files": uncommitted_files,
                "corruption_detected": corruption_detected,
                "fsck_errors": fsck_result.stderr[:200] if fsck_result.stderr else None,
                "repository_healthy": not corruption_detected and fsck_result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Git commands timed out", "repository_healthy": False}
        except Exception as e:
            logging.error(f"Error checking worktree status: {e}")
            return {"error": str(e), "repository_healthy": False}
    
    def _check_service_health(self) -> Dict[str, Any]:
        """Check health of critical services"""
        services = {
            "claude_startup_enforcer": False,
            "continuous_monitor": False,
            "quality_gates": False,
            "page_tracker": False
        }
        
        try:
            # Check if critical scripts are running or recently executed
            script_dir = f"{self.project_root}/scripts"
            
            # Check for recent execution of startup enforcer
            startup_log = f"{self.project_root}/logs/startup-enforcer.log"
            if os.path.exists(startup_log):
                mod_time = os.path.getmtime(startup_log)
                if time.time() - mod_time < 3600:  # Modified within last hour
                    services["claude_startup_enforcer"] = True
            
            # Check for running monitor processes
            for proc in psutil.process_iter(['cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'claude-continuous-monitor' in cmdline:
                        services["continuous_monitor"] = True
                    elif 'quality-gates' in cmdline:
                        services["quality_gates"] = True
                    elif 'page-completion-tracker' in cmdline:
                        services["page_tracker"] = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check if quality gates are installed
            git_hooks_dir = f"{self.project_root}/.git/hooks"
            if os.path.exists(f"{git_hooks_dir}/pre-commit") and os.path.exists(f"{git_hooks_dir}/pre-push"):
                services["quality_gates"] = True
            
        except Exception as e:
            logging.error(f"Error checking service health: {e}")
        
        return services
    
    def _check_filesystem_health(self) -> Dict[str, Any]:
        """Check file system health and integrity"""
        try:
            # Count files and check for issues
            total_files = 0
            total_size = 0
            large_files = []
            unreadable_files = []
            
            for root, dirs, files in os.walk(self.project_root):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv']]
                
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        stat = os.stat(file_path)
                        file_size = stat.st_size
                        
                        total_files += 1
                        total_size += file_size
                        
                        # Check for unusually large files
                        if file_size > 50 * 1024 * 1024:  # Files larger than 50MB
                            large_files.append({
                                "path": file_path.replace(self.project_root, ""),
                                "size_mb": round(file_size / (1024**2), 2)
                            })
                        
                        # Test file readability
                        if file.endswith(('.py', '.js', '.ts', '.tsx', '.sh', '.md', '.json')):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    f.read(1)  # Read first character to test readability
                            except (UnicodeDecodeError, PermissionError, IOError):
                                unreadable_files.append(file_path.replace(self.project_root, ""))
                                
                    except (OSError, IOError) as e:
                        unreadable_files.append(f"{file_path}: {str(e)}")
            
            return {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024**2), 2),
                "large_files": large_files[:10],  # Show first 10
                "large_files_count": len(large_files),
                "unreadable_files": unreadable_files[:10],  # Show first 10
                "unreadable_files_count": len(unreadable_files),
                "filesystem_healthy": len(unreadable_files) == 0
            }
            
        except Exception as e:
            logging.error(f"Error checking filesystem health: {e}")
            return {"error": str(e), "filesystem_healthy": False}
    
    def _calculate_health_score(self, metrics: Dict[str, float]) -> int:
        """Calculate overall health score (0-100)"""
        score = 100
        
        # CPU penalty
        if metrics["cpu"] > self.thresholds["cpu_critical"]:
            score -= 30
        elif metrics["cpu"] > self.thresholds["cpu_warning"]:
            score -= 15
        
        # Memory penalty
        if metrics["memory"] > self.thresholds["memory_critical"]:
            score -= 25
        elif metrics["memory"] > self.thresholds["memory_warning"]:
            score -= 10
        
        # Disk penalty
        if metrics["disk"] > self.thresholds["disk_critical"]:
            score -= 35
        elif metrics["disk"] > self.thresholds["disk_warning"]:
            score -= 15
        
        # Load average penalty
        if metrics["load"] > self.thresholds["load_critical"]:
            score -= 20
        elif metrics["load"] > self.thresholds["load_warning"]:
            score -= 8
        
        return max(0, score)
    
    def _get_status_from_score(self, score: int) -> str:
        """Convert health score to status text"""
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        elif score >= 40:
            return "poor"
        else:
            return "critical"
    
    def _store_metrics(self, health_status: Dict[str, Any]):
        """Store metrics in database"""
        try:
            with sqlite3.connect(self.health_db) as conn:
                system = health_status.get("system", {})
                git = health_status.get("git", {})
                
                conn.execute("""
                    INSERT INTO system_metrics 
                    (timestamp, cpu_percent, memory_percent, disk_percent, 
                     load_avg_1m, load_avg_5m, load_avg_15m, process_count, worktree_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    health_status["timestamp"],
                    system.get("cpu", {}).get("usage_percent", 0),
                    system.get("memory", {}).get("usage_percent", 0),
                    system.get("disk", {}).get("usage_percent", 0),
                    system.get("cpu", {}).get("load_average", {}).get("1m", 0),
                    system.get("cpu", {}).get("load_average", {}).get("5m", 0),
                    system.get("cpu", {}).get("load_average", {}).get("15m", 0),
                    health_status.get("processes", {}).get("total_count", 0),
                    git.get("worktree_count", 0)
                ))
                
        except Exception as e:
            logging.error(f"Error storing metrics: {e}")
    
    def _check_health_alerts(self, health_status: Dict[str, Any]):
        """Check for health issues and generate alerts"""
        system = health_status.get("system", {})
        current_time = datetime.now()
        
        # CPU alerts
        cpu_usage = system.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > self.thresholds["cpu_critical"]:
            self._create_alert("cpu_critical", "critical", "system", 
                             f"Critical CPU usage: {cpu_usage}%", {"cpu_usage": cpu_usage})
        elif cpu_usage > self.thresholds["cpu_warning"]:
            self._create_alert("cpu_warning", "warning", "system",
                             f"High CPU usage: {cpu_usage}%", {"cpu_usage": cpu_usage})
        
        # Memory alerts
        memory_usage = system.get("memory", {}).get("usage_percent", 0)
        if memory_usage > self.thresholds["memory_critical"]:
            self._create_alert("memory_critical", "critical", "system",
                             f"Critical memory usage: {memory_usage}%", {"memory_usage": memory_usage})
        elif memory_usage > self.thresholds["memory_warning"]:
            self._create_alert("memory_warning", "warning", "system",
                             f"High memory usage: {memory_usage}%", {"memory_usage": memory_usage})
        
        # Disk alerts
        disk_usage = system.get("disk", {}).get("usage_percent", 0)
        if disk_usage > self.thresholds["disk_critical"]:
            self._create_alert("disk_critical", "critical", "filesystem",
                             f"Critical disk usage: {disk_usage}%", {"disk_usage": disk_usage})
        elif disk_usage > self.thresholds["disk_warning"]:
            self._create_alert("disk_warning", "warning", "filesystem",
                             f"High disk usage: {disk_usage}%", {"disk_usage": disk_usage})
        
        # Git repository alerts
        git_status = health_status.get("git", {})
        if git_status.get("corruption_detected"):
            self._create_alert("git_corruption", "critical", "git",
                             "Git repository corruption detected", git_status)
        
        # Service alerts
        services = health_status.get("processes", {}).get("critical_services", {})
        for service, running in services.items():
            if not running:
                self._create_alert(f"service_{service}", "warning", "services",
                                 f"Critical service not running: {service}", {"service": service})
    
    def _create_alert(self, event_type: str, severity: str, component: str, message: str, metrics: Dict[str, Any]):
        """Create health alert with cooldown"""
        current_time = datetime.now()
        alert_key = f"{event_type}_{component}"
        
        # Check cooldown
        if alert_key in self.last_alert_time:
            if (current_time - self.last_alert_time[alert_key]).total_seconds() < self.alert_cooldown:
                return  # Skip due to cooldown
        
        # Create alert
        alert = HealthEvent(
            timestamp=current_time.isoformat(),
            event_type=event_type,
            severity=severity,
            component=component,
            message=message,
            metrics=metrics
        )
        
        # Store in database
        try:
            with sqlite3.connect(self.health_db) as conn:
                conn.execute("""
                    INSERT INTO health_events 
                    (timestamp, event_type, severity, component, message, metrics)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    alert.timestamp, alert.event_type, alert.severity,
                    alert.component, alert.message, json.dumps(alert.metrics)
                ))
        except Exception as e:
            logging.error(f"Error storing alert: {e}")
        
        # Update alert history and cooldown
        self.alert_history.append(alert)
        self.last_alert_time[alert_key] = current_time
        
        # Log alert
        logging.warning(f"HEALTH ALERT [{severity.upper()}] {component}: {message}")
        
        # Keep only recent alerts in memory
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-50:]
    
    def _get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent health alerts"""
        try:
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.health_db) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, event_type, severity, component, message, metrics
                    FROM health_events 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                """, (since,))
                
                alerts = []
                for row in cursor.fetchall():
                    alerts.append({
                        "timestamp": row[0],
                        "event_type": row[1],
                        "severity": row[2],
                        "component": row[3],
                        "message": row[4],
                        "metrics": json.loads(row[5]) if row[5] else {}
                    })
                
                return alerts
                
        except Exception as e:
            logging.error(f"Error getting recent alerts: {e}")
            return []
    
    def _generate_health_recommendations(self, health_score: int) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        if health_score < 60:
            recommendations.append("System health is poor - immediate attention required")
        
        if health_score < 80:
            recommendations.extend([
                "Monitor system resources closely",
                "Consider cleaning up temporary files",
                "Check for memory leaks in running processes"
            ])
        
        # Add specific recommendations based on recent alerts
        recent_alerts = self._get_recent_alerts(hours=2)
        
        if any(alert["event_type"].startswith("cpu") for alert in recent_alerts):
            recommendations.append("High CPU usage detected - consider optimizing processes")
        
        if any(alert["event_type"].startswith("memory") for alert in recent_alerts):
            recommendations.append("High memory usage - restart heavy processes if needed")
        
        if any(alert["event_type"].startswith("disk") for alert in recent_alerts):
            recommendations.append("Low disk space - clean up old files and logs")
        
        if any(alert["component"] == "git" for alert in recent_alerts):
            recommendations.append("Git repository issues detected - run 'git fsck' and repair")
        
        return recommendations
    
    def get_historical_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get historical performance metrics"""
        try:
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.health_db) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, cpu_percent, memory_percent, disk_percent, 
                           load_avg_1m, process_count, worktree_count
                    FROM system_metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp ASC
                """, (since,))
                
                metrics = []
                for row in cursor.fetchall():
                    metrics.append({
                        "timestamp": row[0],
                        "cpu_percent": row[1],
                        "memory_percent": row[2],
                        "disk_percent": row[3],
                        "load_avg_1m": row[4],
                        "process_count": row[5],
                        "worktree_count": row[6]
                    })
                
                return {
                    "period_hours": hours,
                    "data_points": len(metrics),
                    "metrics": metrics,
                    "summary": self._calculate_metrics_summary(metrics)
                }
                
        except Exception as e:
            logging.error(f"Error getting historical metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_metrics_summary(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for metrics"""
        if not metrics:
            return {}
        
        cpu_values = [m["cpu_percent"] for m in metrics if m["cpu_percent"] is not None]
        memory_values = [m["memory_percent"] for m in metrics if m["memory_percent"] is not None]
        disk_values = [m["disk_percent"] for m in metrics if m["disk_percent"] is not None]
        
        return {
            "cpu": {
                "avg": round(sum(cpu_values) / len(cpu_values), 2) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0
            },
            "memory": {
                "avg": round(sum(memory_values) / len(memory_values), 2) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
                "min": min(memory_values) if memory_values else 0
            },
            "disk": {
                "avg": round(sum(disk_values) / len(disk_values), 2) if disk_values else 0,
                "max": max(disk_values) if disk_values else 0,
                "min": min(disk_values) if disk_values else 0
            }
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='System Health Monitor for HardCard')
    parser.add_argument('--status', action='store_true', help='Show current health status')
    parser.add_argument('--alerts', action='store_true', help='Show recent alerts')
    parser.add_argument('--history', type=int, default=24, help='Hours of historical data')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    
    args = parser.parse_args()
    
    monitor = SystemHealthMonitor()
    
    if args.monitor:
        print("🏥 Starting continuous health monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                status = monitor.get_comprehensive_health_status()
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} - Health Score: {status['overall_health_score']}/100 ({status['status']})")
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Health monitoring stopped")
    
    elif args.status:
        status = monitor.get_comprehensive_health_status()
        
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"🏥 HardCard System Health Status")
            print(f"Overall Score: {status['overall_health_score']}/100 ({status['status'].upper()})")
            print(f"Timestamp: {status['timestamp']}")
            
            if 'system' in status:
                sys = status['system']
                print(f"\n💻 System Resources:")
                print(f"  CPU: {sys['cpu']['usage_percent']}% | Load: {sys['cpu']['load_average']['1m']}")
                print(f"  Memory: {sys['memory']['usage_percent']}% ({sys['memory']['used_gb']:.1f}GB/{sys['memory']['total_gb']:.1f}GB)")
                print(f"  Disk: {sys['disk']['usage_percent']}% ({sys['disk']['free_gb']:.1f}GB free)")
            
            if 'git' in status:
                git = status['git']
                print(f"\n📂 Git Repository:")
                print(f"  Worktrees: {git.get('worktree_count', 0)}")
                print(f"  Uncommitted files: {git.get('uncommitted_files', 0)}")
                print(f"  Healthy: {git.get('repository_healthy', False)}")
            
            alerts = status.get('alerts', [])
            if alerts:
                print(f"\n🚨 Recent Alerts ({len(alerts)}):")
                for alert in alerts[:5]:
                    print(f"  [{alert['severity'].upper()}] {alert['message']}")
            
            recommendations = status.get('recommendations', [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"  • {rec}")
    
    elif args.alerts:
        alerts = monitor._get_recent_alerts(args.history)
        
        if args.json:
            print(json.dumps(alerts, indent=2))
        else:
            print(f"🚨 Health Alerts (Last {args.history} hours)")
            for alert in alerts:
                timestamp = datetime.fromisoformat(alert['timestamp']).strftime('%m-%d %H:%M')
                print(f"[{timestamp}] [{alert['severity'].upper()}] {alert['component']}: {alert['message']}")
    
    else:
        # Default: show brief status
        status = monitor.get_comprehensive_health_status()
        print(f"🏥 Health: {status['overall_health_score']}/100 ({status['status']}) | Alerts: {len(status.get('alerts', []))}")

if __name__ == "__main__":
    main()