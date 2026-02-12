#!/usr/bin/env python3
"""
Unified Startup Orchestrator - Master orchestrator that coordinates the startup
sequences of Claude Code, Gemini CLI, and MOEX Intelligence systems.

This script manages the complete multi-agent system startup with dependencies,
monitoring, and comprehensive reporting.
"""

import os
import sys
import json
import time
import subprocess
import threading
import logging
import asyncio
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

class SystemType(Enum):
    CLAUDE = "claude"
    CLAUDE_ENGINEER = "claude_engineer"
    GEMINI = "gemini"
    MOEX = "moex"
    HEALTH_MONITORING = "health_monitoring"
    QUALITY_GATES = "quality_gates"

class StartupPhase(Enum):
    PRE_STARTUP = "pre_startup"
    FOUNDATION = "foundation"
    COORDINATION = "coordination"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    FINALIZATION = "finalization"

class SystemStatus(Enum):
    PENDING = "pending"
    STARTING = "starting"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class SystemStartup:
    system_type: SystemType
    system_name: str
    startup_script: str
    dependencies: List[SystemType]
    phase: StartupPhase
    status: SystemStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    pid: Optional[int] = None
    output: str = ""
    error: str = ""
    timeout_seconds: int = 300
    critical: bool = True

@dataclass
class UnifiedStartupSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    systems: List[SystemStartup] = None
    environment_info: Dict[str, Any] = None
    success: bool = False
    systems_started: int = 0
    systems_failed: int = 0
    
    def __post_init__(self):
        if self.systems is None:
            self.systems = []
        if self.environment_info is None:
            self.environment_info = {}

class UnifiedStartupOrchestrator:
    """Master orchestrator for multi-agent system startup"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.session_id = f"unified_startup_{int(time.time())}"
        self.session = UnifiedStartupSession(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Setup logging
        self.log_file = os.path.join(project_root, "logs", "unified-startup-orchestrator.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("UnifiedStartup")
        
        # Initialize systems
        self.systems = self._initialize_systems()
        self.session.systems = self.systems
        
        # Status tracking
        self.status_file = os.path.join(project_root, "monitoring", "unified-startup-status.json")
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        
        # Process tracking
        self.active_processes = {}
        self.startup_lock = threading.Lock()
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_systems(self) -> List[SystemStartup]:
        """Initialize all startup systems with dependencies"""
        return [
            # Phase 1: Foundation - Core system setup
            SystemStartup(
                system_type=SystemType.CLAUDE,
                system_name="Claude Code Startup",
                startup_script=os.path.join(self.project_root, "scripts", "claude-startup-sequence.py"),
                dependencies=[],
                phase=StartupPhase.FOUNDATION,
                status=SystemStatus.PENDING,
                timeout_seconds=180,
                critical=True
            ),
            
            # Phase 2: Coordination - Agent systems
            SystemStartup(
                system_type=SystemType.CLAUDE_ENGINEER,
                system_name="Claude Engineer Self-Improving AI",
                startup_script=os.path.join(self.project_root, "scripts", "claude-engineer-startup-sequence.py"),
                dependencies=[SystemType.CLAUDE],
                phase=StartupPhase.COORDINATION,
                status=SystemStatus.PENDING,
                timeout_seconds=240,
                critical=False  # Allow to fail gracefully
            ),
            
            SystemStartup(
                system_type=SystemType.GEMINI,
                system_name="Gemini CLI Startup",
                startup_script=os.path.join(self.project_root, "scripts", "gemini-startup-sequence.py"),
                dependencies=[SystemType.CLAUDE],
                phase=StartupPhase.COORDINATION,
                status=SystemStatus.PENDING,
                timeout_seconds=120,
                critical=False  # Allow to fail gracefully
            ),
            
            # Phase 3: Integration - Coordination layer
            SystemStartup(
                system_type=SystemType.MOEX,
                system_name="MOEX Intelligence Coordination",
                startup_script=os.path.join(self.project_root, "scripts", "moex-startup-sequence.py"),
                dependencies=[SystemType.CLAUDE, SystemType.CLAUDE_ENGINEER, SystemType.GEMINI],
                phase=StartupPhase.INTEGRATION,
                status=SystemStatus.PENDING,
                timeout_seconds=150,
                critical=False
            ),
            
            # Phase 4: Monitoring - Health and quality systems
            SystemStartup(
                system_type=SystemType.HEALTH_MONITORING,
                system_name="Health Monitoring Systems",
                startup_script=os.path.join(self.project_root, "scripts", "comprehensive-health-dashboard.py"),
                dependencies=[SystemType.CLAUDE],
                phase=StartupPhase.MONITORING,
                status=SystemStatus.PENDING,
                timeout_seconds=60,
                critical=False
            ),
            
            SystemStartup(
                system_type=SystemType.QUALITY_GATES,
                system_name="Quality Gates Enforcement",
                startup_script=os.path.join(self.project_root, "scripts", "best-practices-enforcer.sh"),
                dependencies=[SystemType.CLAUDE],
                phase=StartupPhase.MONITORING,
                status=SystemStatus.PENDING,
                timeout_seconds=90,
                critical=False
            )
        ]
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning(f"Received signal {signum}, shutting down unified startup...")
        self._shutdown_all_systems()
        self._finalize_session(success=False, early_termination=True)
        sys.exit(1)
    
    def run_unified_startup(self) -> bool:
        """Execute the complete unified startup sequence"""
        self.logger.info("🚀 Starting Unified Multi-Agent System Startup Orchestrator")
        self.logger.info(f"📋 Session ID: {self.session_id}")
        self.logger.info(f"📁 Project Root: {self.project_root}")
        
        try:
            # Collect environment information
            self._collect_environment_info()
            
            # Execute startup in phases
            success = self._execute_startup_phases()
            
            # Finalize session
            self._finalize_session(success=success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"💥 Unified startup failed with exception: {e}")
            self._finalize_session(success=False)
            return False
    
    def _collect_environment_info(self):
        """Collect environment information"""
        try:
            self.session.environment_info = {
                "platform": sys.platform,
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "project_root": self.project_root,
                "user": os.environ.get("USER", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "git_status": self._get_git_status()
            }
            
            self.logger.info(f"🖥️ Environment: {sys.platform}, Python {sys.version_info.major}.{sys.version_info.minor}")
            
        except Exception as e:
            self.logger.warning(f"Failed to collect environment info: {e}")
    
    def _get_git_status(self) -> Dict[str, Any]:
        """Get git repository status"""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Get worktree list
            worktree_result = subprocess.run(
                ["git", "worktree", "list"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            return {
                "current_branch": branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown",
                "worktree_count": len(worktree_result.stdout.strip().split('\n')) if worktree_result.returncode == 0 else 0,
                "is_git_repo": branch_result.returncode == 0
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _execute_startup_phases(self) -> bool:
        """Execute startup systems in dependency order"""
        phases = [
            StartupPhase.FOUNDATION,
            StartupPhase.COORDINATION, 
            StartupPhase.INTEGRATION,
            StartupPhase.MONITORING
        ]
        
        overall_success = True
        
        for phase in phases:
            self.logger.info(f"🔄 Starting Phase: {phase.value.upper()}")
            
            # Get systems for this phase
            phase_systems = [s for s in self.systems if s.phase == phase]
            
            if not phase_systems:
                self.logger.info(f"⏭️ No systems in phase {phase.value}")
                continue
            
            # Execute systems in parallel where possible
            phase_success = self._execute_phase_systems(phase_systems)
            
            if not phase_success:
                # Check if any critical systems failed
                critical_failures = [s for s in phase_systems if s.status == SystemStatus.FAILED and s.critical]
                if critical_failures:
                    self.logger.error(f"💥 Critical systems failed in phase {phase.value}: {[s.system_name for s in critical_failures]}")
                    overall_success = False
                    break
                else:
                    self.logger.warning(f"⚠️ Non-critical systems failed in phase {phase.value}")
            
            self.logger.info(f"✅ Phase {phase.value} completed")
        
        return overall_success
    
    def _execute_phase_systems(self, phase_systems: List[SystemStartup]) -> bool:
        """Execute systems within a phase, respecting dependencies"""
        remaining_systems = phase_systems.copy()
        phase_success = True
        
        while remaining_systems:
            # Find systems that can be started (dependencies satisfied)
            ready_systems = []
            for system in remaining_systems:
                if self._are_dependencies_satisfied(system):
                    ready_systems.append(system)
            
            if not ready_systems:
                # Check if we're deadlocked
                pending_systems = [s for s in remaining_systems if s.status == SystemStatus.PENDING]
                if pending_systems:
                    self.logger.error(f"💥 Dependency deadlock detected with systems: {[s.system_name for s in pending_systems]}")
                    phase_success = False
                break
            
            # Start ready systems in parallel
            self._start_systems_parallel(ready_systems)
            
            # Wait for systems to complete
            self._wait_for_systems(ready_systems)
            
            # Remove completed systems
            for system in ready_systems:
                remaining_systems.remove(system)
                if system.status == SystemStatus.FAILED and system.critical:
                    phase_success = False
        
        return phase_success
    
    def _are_dependencies_satisfied(self, system: SystemStartup) -> bool:
        """Check if system dependencies are satisfied"""
        for dep_type in system.dependencies:
            dep_system = next((s for s in self.systems if s.system_type == dep_type), None)
            if not dep_system or dep_system.status not in [SystemStatus.COMPLETED, SystemStatus.ACTIVE]:
                return False
        return True
    
    def _start_systems_parallel(self, systems: List[SystemStartup]):
        """Start multiple systems in parallel"""
        threads = []
        
        for system in systems:
            if os.path.exists(system.startup_script):
                thread = threading.Thread(target=self._start_system, args=(system,))
                thread.start()
                threads.append(thread)
            else:
                self.logger.warning(f"⚠️ Startup script not found for {system.system_name}: {system.startup_script}")
                system.status = SystemStatus.FAILED
                system.error = "Startup script not found"
        
        # Don't wait here - let _wait_for_systems handle it
    
    def _start_system(self, system: SystemStartup):
        """Start a single system"""
        system.start_time = datetime.now()
        system.status = SystemStatus.STARTING
        
        self.logger.info(f"🔧 Starting: {system.system_name}")
        self._update_status()
        
        try:
            # Determine command based on script type
            if system.startup_script.endswith('.py'):
                cmd = [sys.executable, system.startup_script, "--project-root", self.project_root]
            elif system.startup_script.endswith('.sh'):
                cmd = [system.startup_script]
            else:
                cmd = [system.startup_script]
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            system.pid = process.pid
            self.active_processes[system.system_type] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=system.timeout_seconds)
                
                system.end_time = datetime.now()
                system.duration_seconds = (system.end_time - system.start_time).total_seconds()
                system.output = stdout
                system.error = stderr
                
                if process.returncode == 0:
                    system.status = SystemStatus.COMPLETED
                    self.session.systems_started += 1
                    self.logger.info(f"✅ {system.system_name} completed successfully in {system.duration_seconds:.2f}s")
                else:
                    system.status = SystemStatus.FAILED
                    self.session.systems_failed += 1
                    self.logger.error(f"❌ {system.system_name} failed with return code {process.returncode}")
                    if stderr:
                        self.logger.error(f"Error output: {stderr}")
                
            except subprocess.TimeoutExpired:
                process.kill()
                system.status = SystemStatus.TIMEOUT
                system.end_time = datetime.now()
                system.duration_seconds = system.timeout_seconds
                system.error = f"Timeout after {system.timeout_seconds} seconds"
                self.session.systems_failed += 1
                self.logger.error(f"⏰ {system.system_name} timed out after {system.timeout_seconds}s")
            
        except Exception as e:
            system.end_time = datetime.now()
            system.duration_seconds = (system.end_time - system.start_time).total_seconds()
            system.status = SystemStatus.FAILED
            system.error = str(e)
            self.session.systems_failed += 1
            self.logger.error(f"💥 {system.system_name} failed with exception: {e}")
        
        finally:
            # Clean up process tracking
            if system.system_type in self.active_processes:
                del self.active_processes[system.system_type]
    
    def _wait_for_systems(self, systems: List[SystemStartup]):
        """Wait for systems to complete startup"""
        max_wait_time = max(s.timeout_seconds for s in systems) + 30  # Extra buffer
        start_wait = time.time()
        
        while time.time() - start_wait < max_wait_time:
            all_done = True
            for system in systems:
                if system.status in [SystemStatus.PENDING, SystemStatus.STARTING]:
                    all_done = False
                    break
            
            if all_done:
                break
            
            time.sleep(1)  # Check every second
            self._update_status()
        
        # Force timeout any remaining systems
        for system in systems:
            if system.status in [SystemStatus.PENDING, SystemStatus.STARTING]:
                system.status = SystemStatus.TIMEOUT
                system.error = "Forced timeout during phase completion"
                self.logger.warning(f"⏰ Forced timeout for {system.system_name}")
    
    def _shutdown_all_systems(self):
        """Shutdown all active systems"""
        self.logger.info("🛑 Shutting down all active systems...")
        
        for system_type, process in self.active_processes.items():
            try:
                process.terminate()
                time.sleep(2)  # Give process time to shutdown gracefully
                if process.poll() is None:
                    process.kill()
                self.logger.info(f"🛑 Shutdown: {system_type.value}")
            except Exception as e:
                self.logger.error(f"Error shutting down {system_type.value}: {e}")
        
        self.active_processes.clear()
    
    def _update_status(self):
        """Update startup status file"""
        try:
            with self.startup_lock:
                status_data = {
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "phase": "in_progress",
                    "systems_started": self.session.systems_started,
                    "systems_failed": self.session.systems_failed,
                    "active_processes": [key.value for key in self.active_processes.keys()],
                    "systems": [
                        {
                            "system_type": s.system_type.value,
                            "system_name": s.system_name,
                            "phase": s.phase.value,
                            "status": s.status.value,
                            "duration": s.duration_seconds,
                            "pid": s.pid
                        }
                        for s in self.systems
                    ]
                }
                
                with open(self.status_file, 'w') as f:
                    json.dump(status_data, f, indent=2)
                    
        except Exception as e:
            self.logger.warning(f"Failed to update status file: {e}")
    
    def _finalize_session(self, success: bool, early_termination: bool = False):
        """Finalize the unified startup session"""
        self.session.end_time = datetime.now()
        self.session.total_duration = (self.session.end_time - self.session.start_time).total_seconds()
        self.session.success = success
        
        # Create comprehensive final report
        report_file = os.path.join(
            self.project_root, 
            "reports", 
            f"unified-startup-{self.session_id}.json"
        )
        
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        try:
            with open(report_file, 'w') as f:
                json.dump(asdict(self.session), f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to write final report: {e}")
        
        # Update final status
        final_status = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "completed" if success else "failed",
            "success": success,
            "early_termination": early_termination,
            "total_duration": self.session.total_duration,
            "systems_started": self.session.systems_started,
            "systems_failed": self.session.systems_failed,
            "report_file": report_file,
            "summary": self._generate_summary()
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(final_status, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to update final status: {e}")
        
        # Log comprehensive completion summary
        self._log_completion_summary(success, early_termination, report_file)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate startup session summary"""
        completed_systems = [s for s in self.systems if s.status == SystemStatus.COMPLETED]
        failed_systems = [s for s in self.systems if s.status == SystemStatus.FAILED]
        timeout_systems = [s for s in self.systems if s.status == SystemStatus.TIMEOUT]
        
        phases_completed = len(set(s.phase for s in completed_systems))
        total_phases = len(set(s.phase for s in self.systems))
        
        return {
            "total_systems": len(self.systems),
            "completed_systems": len(completed_systems),
            "failed_systems": len(failed_systems),
            "timeout_systems": len(timeout_systems),
            "success_rate": len(completed_systems) / len(self.systems) * 100,
            "phases_completed": phases_completed,
            "total_phases": total_phases,
            "critical_failures": len([s for s in failed_systems if s.critical]),
            "average_startup_time": statistics.mean([s.duration_seconds for s in completed_systems]) if completed_systems else 0,
            "longest_startup": max([s.duration_seconds for s in completed_systems]) if completed_systems else 0
        }
    
    def _log_completion_summary(self, success: bool, early_termination: bool, report_file: str):
        """Log comprehensive completion summary"""
        status_emoji = "✅" if success else "❌"
        termination_note = " (early termination)" if early_termination else ""
        
        self.logger.info("=" * 80)
        self.logger.info(f"{status_emoji} UNIFIED MULTI-AGENT STARTUP COMPLETED{termination_note}")
        self.logger.info("=" * 80)
        
        summary = self._generate_summary()
        
        self.logger.info(f"📊 STARTUP METRICS:")
        self.logger.info(f"   Total Duration: {self.session.total_duration:.2f} seconds")
        self.logger.info(f"   Systems Started: {summary['completed_systems']}/{summary['total_systems']}")
        self.logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"   Phases Completed: {summary['phases_completed']}/{summary['total_phases']}")
        
        if summary['failed_systems'] > 0:
            failed_systems = [s for s in self.systems if s.status in [SystemStatus.FAILED, SystemStatus.TIMEOUT]]
            self.logger.info(f"💥 FAILED SYSTEMS:")
            for system in failed_systems:
                self.logger.info(f"   ❌ {system.system_name}: {system.status.value}")
                if system.error:
                    self.logger.info(f"      Error: {system.error[:100]}...")
        
        completed_systems = [s for s in self.systems if s.status == SystemStatus.COMPLETED]
        if completed_systems:
            self.logger.info(f"✅ SUCCESSFUL SYSTEMS:")
            for system in completed_systems:
                self.logger.info(f"   ✅ {system.system_name}: {system.duration_seconds:.2f}s")
        
        # System-specific status
        self.logger.info(f"🤖 AGENT STATUS:")
        claude_system = next((s for s in self.systems if s.system_type == SystemType.CLAUDE), None)
        if claude_system:
            self.logger.info(f"   Claude Code: {claude_system.status.value}")
        
        claude_engineer_system = next((s for s in self.systems if s.system_type == SystemType.CLAUDE_ENGINEER), None)
        if claude_engineer_system:
            self.logger.info(f"   Claude Engineer: {claude_engineer_system.status.value}")
        
        gemini_system = next((s for s in self.systems if s.system_type == SystemType.GEMINI), None)
        if gemini_system:
            self.logger.info(f"   Gemini CLI: {gemini_system.status.value}")
        
        moex_system = next((s for s in self.systems if s.system_type == SystemType.MOEX), None)
        if moex_system:
            self.logger.info(f"   MOEX Coordination: {moex_system.status.value}")
        
        self.logger.info(f"📋 Full Report: {report_file}")
        self.logger.info("=" * 80)
        
        if success:
            self.logger.info("🎉 Multi-agent system is ready for development!")
            self.logger.info("💡 Available agents: Claude Code, Claude Engineer, Gemini CLI, MOEX Coordination")
            self.logger.info("🤖 Claude Engineer provides self-improving AI with dynamic tool creation")
            self.logger.info("🚀 Quick start: Use custom slash commands and follow best practices workflows")
        else:
            self.logger.error("⚠️ Startup completed with issues - check logs and status for details")

def main():
    """Main entry point for unified startup orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Multi-Agent System Startup Orchestrator")
    parser.add_argument("--project-root", default="/Users/studio/hardcard", 
                       help="Project root directory")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--timeout-multiplier", type=float, default=1.0,
                       help="Multiply all timeout values by this factor")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run unified startup
    orchestrator = UnifiedStartupOrchestrator(args.project_root)
    
    # Apply timeout multiplier if specified
    if args.timeout_multiplier != 1.0:
        for system in orchestrator.systems:
            system.timeout_seconds = int(system.timeout_seconds * args.timeout_multiplier)
    
    success = orchestrator.run_unified_startup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()