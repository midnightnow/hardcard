#!/usr/bin/env python3
"""
Comprehensive Health Monitoring Dashboard - Unified monitoring interface
that integrates all stability enhancement systems into a cohesive dashboard.

The central nervous system command center of our software body.
"""

import os
import json
import time
import asyncio
import threading
import logging
import sqlite3
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
import statistics
import hashlib

# Import our stability enhancement systems
try:
    from enhanced_resilience_system import (
        EnhancedHealthMonitor, ResilienceLevel, ComponentState, 
        CircuitBreaker, BulkheadIsolation
    )
    from automated_stability_monitor import (
        StabilityMonitor, StabilityLevel, MetricsCollector, 
        StabilityPredictor
    )
    from fail_safe_deployment_system import (
        FailSafeDeploymentOrchestrator, DeploymentStatus, DeploymentStage
    )
    from resilient_error_recovery import (
        ErrorRecoveryOrchestrator, ErrorSeverity, RecoveryStatus
    )
    from self_healing_system import (
        SelfHealingSystem, IssueType, SeverityLevel
    )
    ALL_SYSTEMS_AVAILABLE = True
except ImportError:
    ALL_SYSTEMS_AVAILABLE = False
    print("⚠️ Some stability systems not available - running in standalone mode")

class OverallSystemHealth(Enum):
    CRITICAL = "critical"      # Multiple system failures
    DEGRADED = "degraded"      # Some components failing
    STABLE = "stable"          # Normal operation
    OPTIMAL = "optimal"        # Peak performance
    UNKNOWN = "unknown"        # Cannot determine

class DashboardMode(Enum):
    CONSOLE = "console"        # Terminal dashboard
    WEB = "web"               # Web interface
    API = "api"               # REST API
    REALTIME = "realtime"     # Live monitoring

@dataclass
class SystemHealthSnapshot:
    timestamp: datetime
    overall_health: OverallSystemHealth
    component_states: Dict[str, Any]
    active_alerts: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    predictions: List[Dict[str, Any]]
    recommendations: List[str]
    uptime_seconds: float

@dataclass
class HealthTrend:
    component: str
    metric: str
    trend_direction: str  # "improving", "degrading", "stable"
    severity: str
    time_window_hours: int
    data_points: List[float]

class ComprehensiveHealthDashboard:
    """Unified health monitoring dashboard for all stability systems"""
    
    def __init__(self, project_root: str, mode: DashboardMode = DashboardMode.CONSOLE):
        self.project_root = project_root
        self.mode = mode
        self.db_path = os.path.join(project_root, "health_dashboard.db")
        self.start_time = datetime.now()
        
        # Initialize database
        self._init_database()
        
        # Initialize component systems
        self._init_subsystems()
        
        # Dashboard state
        self.running = True
        self.refresh_interval = 5  # seconds
        self.alert_history = deque(maxlen=1000)
        self.health_snapshots = deque(maxlen=100)
        
        # Setup logging
        self._setup_logging()
    
    def _init_database(self):
        """Initialize SQLite database for health data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS health_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_health TEXT NOT NULL,
                    component_states TEXT NOT NULL,
                    performance_metrics TEXT NOT NULL,
                    active_alerts_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS component_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    baseline REAL,
                    deviation REAL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_time TEXT
                )
            """)
    
    def _init_subsystems(self):
        """Initialize all stability monitoring subsystems"""
        self.subsystems = {}
        
        if ALL_SYSTEMS_AVAILABLE:
            try:
                self.subsystems['resilience'] = EnhancedHealthMonitor(self.project_root)
                self.subsystems['stability'] = StabilityMonitor(
                    self.project_root, 
                    check_interval_minutes=1
                )
                self.subsystems['deployment'] = FailSafeDeploymentOrchestrator(
                    self.project_root
                )
                self.subsystems['error_recovery'] = ErrorRecoveryOrchestrator(
                    self.project_root
                )
                self.subsystems['self_healing'] = SelfHealingSystem(
                    self.project_root
                )
            except Exception as e:
                print(f"⚠️ Error initializing subsystems: {e}")
                self.subsystems = {}
        
        print(f"✅ Initialized {len(self.subsystems)} monitoring subsystems")
    
    def _setup_logging(self):
        """Setup logging for the dashboard"""
        log_file = os.path.join(self.project_root, "health_dashboard.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("HealthDashboard")
    
    def collect_comprehensive_health(self) -> SystemHealthSnapshot:
        """Collect health data from all subsystems"""
        timestamp = datetime.now()
        component_states = {}
        active_alerts = []
        performance_metrics = {}
        predictions = []
        recommendations = []
        
        # Collect from resilience system
        if 'resilience' in self.subsystems:
            try:
                resilience_health = self.subsystems['resilience'].get_comprehensive_health()
                component_states['resilience'] = resilience_health
                
                # Extract performance metrics
                for component, health in resilience_health.items():
                    if isinstance(health, dict) and 'metrics' in health:
                        for metric, value in health['metrics'].items():
                            performance_metrics[f"resilience_{component}_{metric}"] = value
            except Exception as e:
                self.logger.error(f"Error collecting resilience health: {e}")
        
        # Collect from stability monitor
        if 'stability' in self.subsystems:
            try:
                stability_data = self.subsystems['stability'].get_current_stability()
                component_states['stability'] = stability_data
                
                # Extract alerts
                if 'alerts' in stability_data:
                    for alert in stability_data['alerts']:
                        active_alerts.append({
                            'source': 'stability',
                            'component': alert.get('component', 'unknown'),
                            'severity': alert.get('severity', 'medium'),
                            'message': alert.get('message', ''),
                            'timestamp': timestamp.isoformat()
                        })
            except Exception as e:
                self.logger.error(f"Error collecting stability data: {e}")
        
        # Collect from deployment system
        if 'deployment' in self.subsystems:
            try:
                deployment_status = self.subsystems['deployment'].get_system_status()
                component_states['deployment'] = deployment_status
            except Exception as e:
                self.logger.error(f"Error collecting deployment status: {e}")
        
        # Collect from error recovery
        if 'error_recovery' in self.subsystems:
            try:
                recovery_stats = self.subsystems['error_recovery'].get_recovery_statistics()
                component_states['error_recovery'] = recovery_stats
                
                # Add recommendations based on error patterns
                if recovery_stats.get('recent_errors', 0) > 5:
                    recommendations.append("High error rate detected - review recent failures")
            except Exception as e:
                self.logger.error(f"Error collecting error recovery stats: {e}")
        
        # Collect from self-healing system
        if 'self_healing' in self.subsystems:
            try:
                healing_status = self.subsystems['self_healing'].get_system_status()
                component_states['self_healing'] = healing_status
                
                # Add alerts for critical issues
                if healing_status.get('critical_issues', 0) > 0:
                    active_alerts.append({
                        'source': 'self_healing',
                        'component': 'system',
                        'severity': 'critical',
                        'message': f"{healing_status['critical_issues']} critical issues detected",
                        'timestamp': timestamp.isoformat()
                    })
            except Exception as e:
                self.logger.error(f"Error collecting self-healing status: {e}")
        
        # Calculate overall health
        overall_health = self._calculate_overall_health(component_states, active_alerts)
        
        # Add general recommendations
        if len(active_alerts) > 10:
            recommendations.append("High alert volume - investigate system stability")
        
        if overall_health == OverallSystemHealth.OPTIMAL:
            recommendations.append("System operating optimally - maintain current configuration")
        
        # Calculate uptime
        uptime_seconds = (timestamp - self.start_time).total_seconds()
        
        return SystemHealthSnapshot(
            timestamp=timestamp,
            overall_health=overall_health,
            component_states=component_states,
            active_alerts=active_alerts,
            performance_metrics=performance_metrics,
            predictions=predictions,
            recommendations=recommendations,
            uptime_seconds=uptime_seconds
        )
    
    def _calculate_overall_health(self, component_states: Dict, alerts: List) -> OverallSystemHealth:
        """Calculate overall system health from component states"""
        if not component_states:
            return OverallSystemHealth.UNKNOWN
        
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        high_alerts = [a for a in alerts if a.get('severity') == 'high']
        
        # Critical condition checks
        if len(critical_alerts) > 0:
            return OverallSystemHealth.CRITICAL
        
        # Check for degraded components
        degraded_components = 0
        total_components = 0
        
        for system, state in component_states.items():
            if isinstance(state, dict):
                total_components += 1
                if 'status' in state:
                    if state['status'] in ['degraded', 'failing', 'failed']:
                        degraded_components += 1
        
        if total_components == 0:
            return OverallSystemHealth.UNKNOWN
        
        degradation_ratio = degraded_components / total_components
        
        if degradation_ratio > 0.5:  # More than half degraded
            return OverallSystemHealth.CRITICAL
        elif degradation_ratio > 0.25:  # More than quarter degraded
            return OverallSystemHealth.DEGRADED
        elif len(high_alerts) > 5:  # Many high-severity alerts
            return OverallSystemHealth.DEGRADED
        elif len(alerts) == 0 and degraded_components == 0:
            return OverallSystemHealth.OPTIMAL
        else:
            return OverallSystemHealth.STABLE
    
    def persist_snapshot(self, snapshot: SystemHealthSnapshot):
        """Persist health snapshot to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO health_snapshots 
                    (timestamp, overall_health, component_states, performance_metrics, active_alerts_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    snapshot.timestamp.isoformat(),
                    snapshot.overall_health.value,
                    json.dumps(snapshot.component_states),
                    json.dumps(snapshot.performance_metrics),
                    len(snapshot.active_alerts)
                ))
                
                # Persist component metrics
                for metric_name, value in snapshot.performance_metrics.items():
                    conn.execute("""
                        INSERT INTO component_metrics 
                        (timestamp, component, metric_name, metric_value)
                        VALUES (?, ?, ?, ?)
                    """, (
                        snapshot.timestamp.isoformat(),
                        metric_name.split('_')[0] if '_' in metric_name else 'system',
                        metric_name,
                        value
                    ))
                
                # Persist new alerts
                for alert in snapshot.active_alerts:
                    conn.execute("""
                        INSERT INTO alert_history 
                        (timestamp, component, alert_type, severity, message)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        alert['timestamp'],
                        alert['component'],
                        alert.get('type', 'unknown'),
                        alert['severity'],
                        alert['message']
                    ))
        except Exception as e:
            self.logger.error(f"Error persisting snapshot: {e}")
    
    def display_console_dashboard(self, snapshot: SystemHealthSnapshot):
        """Display dashboard in console mode"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Header
        print("=" * 80)
        print("🏥 COMPREHENSIVE HEALTH MONITORING DASHBOARD")
        print("=" * 80)
        print(f"📅 {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Uptime: {self._format_uptime(snapshot.uptime_seconds)}")
        
        # Overall Health Status
        health_emoji = {
            OverallSystemHealth.CRITICAL: "🔴",
            OverallSystemHealth.DEGRADED: "🟡", 
            OverallSystemHealth.STABLE: "🟢",
            OverallSystemHealth.OPTIMAL: "✨",
            OverallSystemHealth.UNKNOWN: "❓"
        }
        
        print(f"\n🩺 OVERALL HEALTH: {health_emoji[snapshot.overall_health]} {snapshot.overall_health.value.upper()}")
        
        # Active Alerts
        if snapshot.active_alerts:
            print(f"\n🚨 ACTIVE ALERTS ({len(snapshot.active_alerts)}):")
            for alert in snapshot.active_alerts[-5:]:  # Show last 5
                severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(alert['severity'], "⚪")
                print(f"  {severity_emoji} [{alert['component']}] {alert['message']}")
        else:
            print("\n✅ NO ACTIVE ALERTS")
        
        # Component Status
        print(f"\n🔧 COMPONENT STATUS:")
        for system, state in snapshot.component_states.items():
            if isinstance(state, dict):
                status = state.get('status', 'unknown')
                status_emoji = {"healthy": "✅", "degraded": "⚠️", "failed": "❌", "unknown": "❓"}.get(status, "❓")
                print(f"  {status_emoji} {system.upper()}: {status}")
        
        # Performance Metrics (top 5)
        if snapshot.performance_metrics:
            print(f"\n📊 KEY METRICS:")
            sorted_metrics = sorted(snapshot.performance_metrics.items(), key=lambda x: abs(x[1]), reverse=True)
            for metric, value in sorted_metrics[:5]:
                print(f"  📈 {metric}: {value:.2f}")
        
        # Recommendations
        if snapshot.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in snapshot.recommendations[:3]:
                print(f"  • {rec}")
        
        print("\n" + "=" * 80)
        print("⌨️  Press Ctrl+C to exit | Refreshing every 5 seconds...")
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    async def run_monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting comprehensive health monitoring...")
        
        while self.running:
            try:
                # Collect health snapshot
                snapshot = self.collect_comprehensive_health()
                
                # Store snapshot
                self.health_snapshots.append(snapshot)
                
                # Persist to database
                self.persist_snapshot(snapshot)
                
                # Display based on mode
                if self.mode == DashboardMode.CONSOLE:
                    self.display_console_dashboard(snapshot)
                
                # Wait for next cycle
                await asyncio.sleep(self.refresh_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Shutdown requested by user")
                self.running = False
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.refresh_interval)
    
    def get_health_trends(self, hours: int = 24) -> List[HealthTrend]:
        """Analyze health trends over specified time period"""
        trends = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT component, metric_name, metric_value, timestamp
                    FROM component_metrics 
                    WHERE timestamp > datetime('now', '-{} hours')
                    ORDER BY component, metric_name, timestamp
                """.format(hours))
                
                # Group by component and metric
                metric_data = defaultdict(list)
                for row in cursor.fetchall():
                    component, metric_name, value, timestamp = row
                    metric_data[(component, metric_name)].append((value, timestamp))
                
                # Analyze trends
                for (component, metric_name), data_points in metric_data.items():
                    if len(data_points) >= 3:
                        values = [point[0] for point in data_points]
                        
                        # Simple trend analysis
                        if len(values) >= 2:
                            recent_avg = statistics.mean(values[-3:])
                            older_avg = statistics.mean(values[:3])
                            
                            if recent_avg > older_avg * 1.1:
                                trend_direction = "improving" if "error" not in metric_name.lower() else "degrading"
                            elif recent_avg < older_avg * 0.9:
                                trend_direction = "degrading" if "error" not in metric_name.lower() else "improving"
                            else:
                                trend_direction = "stable"
                            
                            trends.append(HealthTrend(
                                component=component,
                                metric=metric_name,
                                trend_direction=trend_direction,
                                severity="medium",
                                time_window_hours=hours,
                                data_points=values
                            ))
        
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
        
        return trends
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        latest_snapshot = self.health_snapshots[-1] if self.health_snapshots else None
        trends = self.get_health_trends(24)
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "system_uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "current_health": latest_snapshot.overall_health.value if latest_snapshot else "unknown",
            "active_alerts_count": len(latest_snapshot.active_alerts) if latest_snapshot else 0,
            "component_count": len(latest_snapshot.component_states) if latest_snapshot else 0,
            "trends_analyzed": len(trends),
            "degrading_trends": len([t for t in trends if t.trend_direction == "degrading"]),
            "improving_trends": len([t for t in trends if t.trend_direction == "improving"]),
            "recommendations": latest_snapshot.recommendations if latest_snapshot else [],
            "subsystems_active": list(self.subsystems.keys())
        }

def main():
    """Main entry point for the health dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Health Monitoring Dashboard")
    parser.add_argument("--project-root", default="/Users/studio/hardcard", 
                       help="Project root directory")
    parser.add_argument("--mode", choices=["console", "web", "api", "realtime"], 
                       default="console", help="Dashboard mode")
    parser.add_argument("--refresh-interval", type=int, default=5,
                       help="Refresh interval in seconds")
    
    args = parser.parse_args()
    
    # Create and run dashboard
    dashboard = ComprehensiveHealthDashboard(
        project_root=args.project_root,
        mode=DashboardMode(args.mode)
    )
    dashboard.refresh_interval = args.refresh_interval
    
    print("🚀 Starting Comprehensive Health Monitoring Dashboard...")
    print(f"📁 Project root: {args.project_root}")
    print(f"🖥️  Mode: {args.mode}")
    print(f"⏱️  Refresh interval: {args.refresh_interval}s")
    
    try:
        asyncio.run(dashboard.run_monitoring_loop())
    except KeyboardInterrupt:
        print("\n👋 Dashboard shutdown complete")

if __name__ == "__main__":
    main()