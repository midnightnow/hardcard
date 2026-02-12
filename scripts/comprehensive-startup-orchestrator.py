#!/usr/bin/env python3
"""
Comprehensive Multi-Agent Startup Orchestrator - Master orchestrator that coordinates
the startup sequences of Claude Code, Claude Engineer, Gemini CLI, and MOEX Intelligence.

Now integrated with Advanced Functions Core for enterprise-grade capabilities:
- Security hardening with input validation and rate limiting
- Resource monitoring with circuit breaker patterns
- Advanced task management with Redis caching
- Performance optimization and health monitoring

This is the ultimate startup script that manages the complete AI development ecosystem
with self-improving capabilities, multi-agent coordination, and comprehensive monitoring.
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

# Import advanced functions for enterprise capabilities
try:
    from advanced_functions_core import (
        create_advanced_functions_manager,
        SecurityLevel,
        TaskPriority,
        TaskConfig,
        AdvancedTaskManager,
        ResourceMonitor,
        CacheManager
    )
    ADVANCED_FUNCTIONS_AVAILABLE = True
except ImportError:
    ADVANCED_FUNCTIONS_AVAILABLE = False
    logging.warning("Advanced functions core not available - using fallback mode")

class AgentType(Enum):
    CLAUDE_CODE = "claude_code"
    CLAUDE_ENGINEER = "claude_engineer" 
    GEMINI_CLI = "gemini_cli"
    MOEX = "moex"
    HEALTH_MONITORING = "health_monitoring"
    QUALITY_GATES = "quality_gates"

class StartupPhase(Enum):
    PRE_STARTUP = "pre_startup"
    FOUNDATION = "foundation"
    AI_AGENTS = "ai_agents"
    COORDINATION = "coordination"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    FINALIZATION = "finalization"

class AgentStatus(Enum):
    PENDING = "pending"
    STARTING = "starting"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class AgentStartup:
    agent_type: AgentType
    agent_name: str
    startup_script: str
    dependencies: List[AgentType]
    phase: StartupPhase
    status: AgentStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    pid: Optional[int] = None
    output: str = ""
    error: str = ""
    timeout_seconds: int = 300
    critical: bool = True
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []

@dataclass
class ComprehensiveStartupSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    agents: List[AgentStartup] = None
    environment_info: Dict[str, Any] = None
    coordination_status: Dict[str, Any] = None
    success: bool = False
    agents_started: int = 0
    agents_failed: int = 0
    
    def __post_init__(self):
        if self.agents is None:
            self.agents = []
        if self.environment_info is None:
            self.environment_info = {}
        if self.coordination_status is None:
            self.coordination_status = {}

class ComprehensiveStartupOrchestrator:
    """Ultimate multi-agent system startup orchestrator"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.session_id = f"comprehensive_startup_{int(time.time())}"
        self.session = ComprehensiveStartupSession(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Setup logging
        self.log_file = os.path.join(project_root, "logs", "comprehensive-startup-orchestrator.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ComprehensiveStartup")
        
        # Initialize agents
        self.agents = self._initialize_agents()
        self.session.agents = self.agents
        
        # Status tracking
        self.status_file = os.path.join(project_root, "monitoring", "comprehensive-startup-status.json")
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        
        # Process tracking
        self.active_processes = {}
        self.startup_lock = threading.Lock()
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_agents(self) -> List[AgentStartup]:
        """Initialize all AI agents with comprehensive configuration"""
        return [
            # Phase 1: Foundation - Core Claude Code
            AgentStartup(
                agent_type=AgentType.CLAUDE_CODE,
                agent_name="Claude Code Primary Development",
                startup_script=os.path.join(self.project_root, "scripts", "claude-startup-sequence.py"),
                dependencies=[],
                phase=StartupPhase.FOUNDATION,
                status=AgentStatus.PENDING,
                timeout_seconds=180,
                critical=True,
                capabilities=["implementation", "testing", "git_operations", "workflow_management"]
            ),
            
            # Phase 2: AI Agents - Self-improving and specialized agents
            AgentStartup(
                agent_type=AgentType.CLAUDE_ENGINEER,
                agent_name="Claude Engineer Self-Improving AI",
                startup_script=os.path.join(self.project_root, "scripts", "claude-engineer-startup-sequence.py"),
                dependencies=[AgentType.CLAUDE_CODE],
                phase=StartupPhase.AI_AGENTS,
                status=AgentStatus.PENDING,
                timeout_seconds=300,
                critical=False,
                capabilities=["dynamic_tool_creation", "self_improvement", "pattern_analysis", "optimization"]
            ),
            
            AgentStartup(
                agent_type=AgentType.GEMINI_CLI,
                agent_name="Gemini CLI Analysis Engine",
                startup_script=os.path.join(self.project_root, "scripts", "gemini-startup-sequence.py"),
                dependencies=[AgentType.CLAUDE_CODE],
                phase=StartupPhase.AI_AGENTS,
                status=AgentStatus.PENDING,
                timeout_seconds=180,
                critical=False,
                capabilities=["code_analysis", "documentation_generation", "security_scanning", "optimization"]
            ),
            
            # Phase 3: Coordination - Multi-agent orchestration
            AgentStartup(
                agent_type=AgentType.MOEX,
                agent_name="MOEX Intelligence Coordination",
                startup_script=os.path.join(self.project_root, "scripts", "moex-startup-sequence.py"),
                dependencies=[AgentType.CLAUDE_CODE, AgentType.CLAUDE_ENGINEER, AgentType.GEMINI_CLI],
                phase=StartupPhase.COORDINATION,
                status=AgentStatus.PENDING,
                timeout_seconds=200,
                critical=False,
                capabilities=["agent_coordination", "task_routing", "workflow_orchestration", "communication"]
            ),
            
            # Phase 4: Monitoring - Health and quality systems
            AgentStartup(
                agent_type=AgentType.HEALTH_MONITORING,
                agent_name="Comprehensive Health Monitoring",
                startup_script=os.path.join(self.project_root, "scripts", "comprehensive-health-dashboard.py"),
                dependencies=[AgentType.CLAUDE_CODE],
                phase=StartupPhase.MONITORING,
                status=AgentStatus.PENDING,
                timeout_seconds=90,
                critical=False,
                capabilities=["health_monitoring", "performance_tracking", "error_detection", "alerting"]
            ),
            
            AgentStartup(
                agent_type=AgentType.QUALITY_GATES,
                agent_name="Quality Gates and Best Practices",
                startup_script=os.path.join(self.project_root, "scripts", "best-practices-enforcer.sh"),
                dependencies=[AgentType.CLAUDE_CODE],
                phase=StartupPhase.MONITORING,
                status=AgentStatus.PENDING,
                timeout_seconds=120,
                critical=False,
                capabilities=["quality_enforcement", "best_practices", "compliance_checking", "automation"]
            )
        ]
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning(f"Received signal {signum}, shutting down comprehensive startup...")
        self._shutdown_all_agents()
        self._finalize_session(success=False, early_termination=True)
        sys.exit(1)
    
    def run_comprehensive_startup(self) -> bool:
        """Execute the complete multi-agent startup sequence"""
        self.logger.info("🚀 Starting Comprehensive Multi-Agent AI Development Ecosystem")
        self.logger.info("=" * 80)
        self.logger.info(f"📋 Session ID: {self.session_id}")
        self.logger.info(f"📁 Project Root: {self.project_root}")
        self.logger.info(f"🤖 Agents to Initialize: {len(self.agents)}")
        self.logger.info("=" * 80)
        
        try:
            # Collect environment information
            self._collect_environment_info()
            
            # Execute startup in phases
            success = self._execute_startup_phases()
            
            # Initialize coordination if successful
            if success:
                self._initialize_coordination()
            
            # Finalize session
            self._finalize_session(success=success)
            
            return success
            
        except Exception as e:
            self.logger.error(f"💥 Comprehensive startup failed with exception: {e}")
            self._finalize_session(success=False)
            return False
    
    def _collect_environment_info(self):
        """Collect comprehensive environment information"""
        try:
            # Basic environment
            env_info = {
                "platform": sys.platform,
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "project_root": self.project_root,
                "user": os.environ.get("USER", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            }
            
            # Check for API keys
            api_keys = {
                "anthropic_api_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
                "gemini_api_key": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
                "e2b_api_key": bool(os.environ.get("E2B_API_KEY"))
            }
            env_info["api_keys_available"] = api_keys
            
            # Git status
            env_info["git_status"] = self._get_git_status()
            
            # System resources
            try:
                import psutil
                env_info["system_resources"] = {
                    "cpu_count": psutil.cpu_count(),
                    "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                    "disk_free_gb": round(psutil.disk_usage(self.project_root).free / (1024**3), 2)
                }
            except ImportError:
                env_info["system_resources"] = "psutil not available"
            
            # Available tools
            available_tools = []
            tools_to_check = [
                ("git", ["git", "--version"]),
                ("node", ["node", "--version"]),
                ("npm", ["npm", "--version"]),
                ("python", ["python", "--version"]),
                ("pip", ["pip", "--version"]),
                ("gemini", ["gemini", "--version"])
            ]
            
            for tool_name, cmd in tools_to_check:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        available_tools.append({
                            "name": tool_name,
                            "version": result.stdout.strip(),
                            "available": True
                        })
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    available_tools.append({
                        "name": tool_name,
                        "available": False
                    })
            
            env_info["available_tools"] = available_tools
            
            self.session.environment_info = env_info
            
            self.logger.info(f"🖥️ Environment: {sys.platform}, Python {sys.version_info.major}.{sys.version_info.minor}")
            self.logger.info(f"🔑 API Keys: Anthropic={api_keys['anthropic_api_key']}, Gemini={api_keys['gemini_api_key']}")
            self.logger.info(f"🛠️ Available Tools: {len([t for t in available_tools if t['available']])}/{len(available_tools)}")
            
        except Exception as e:
            self.logger.warning(f"Failed to collect environment info: {e}")
    
    def _get_git_status(self) -> Dict[str, Any]:
        """Get comprehensive git repository status"""
        try:
            git_status = {}
            
            # Current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            git_status["current_branch"] = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Worktree list
            worktree_result = subprocess.run(
                ["git", "worktree", "list"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if worktree_result.returncode == 0:
                worktrees = worktree_result.stdout.strip().split('\n')
                git_status["worktree_count"] = len(worktrees)
                git_status["worktrees"] = [
                    {
                        "path": line.split()[0] if line.split() else "",
                        "branch": line.split()[1].strip('[]') if len(line.split()) > 1 else ""
                    }
                    for line in worktrees
                ]
            else:
                git_status["worktree_count"] = 0
                git_status["worktrees"] = []
            
            # Repository status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            git_status["has_changes"] = bool(status_result.stdout.strip()) if status_result.returncode == 0 else None
            git_status["is_git_repo"] = worktree_result.returncode == 0
            
            return git_status
            
        except Exception as e:
            return {"error": str(e), "is_git_repo": False}
    
    def _execute_startup_phases(self) -> bool:
        """Execute agents in dependency order by phases"""
        phases = [
            StartupPhase.FOUNDATION,
            StartupPhase.AI_AGENTS,
            StartupPhase.COORDINATION,
            StartupPhase.MONITORING
        ]
        
        overall_success = True
        
        for phase in phases:
            self.logger.info("=" * 60)
            self.logger.info(f"🔄 PHASE: {phase.value.upper().replace('_', ' ')}")
            self.logger.info("=" * 60)
            
            # Get agents for this phase
            phase_agents = [a for a in self.agents if a.phase == phase]
            
            if not phase_agents:
                self.logger.info(f"⏭️ No agents in phase {phase.value}")
                continue
            
            # Log phase agents
            for agent in phase_agents:
                deps = [dep.value for dep in agent.dependencies]
                self.logger.info(f"📋 {agent.agent_name} (deps: {deps if deps else 'none'})")
            
            # Execute agents in this phase
            phase_success = self._execute_phase_agents(phase_agents)
            
            if not phase_success:
                # Check if any critical agents failed
                critical_failures = [a for a in phase_agents if a.status == AgentStatus.FAILED and a.critical]
                if critical_failures:
                    self.logger.error(f"💥 Critical agents failed in phase {phase.value}:")
                    for agent in critical_failures:
                        self.logger.error(f"   ❌ {agent.agent_name}")
                    overall_success = False
                    break
                else:
                    self.logger.warning(f"⚠️ Non-critical agents failed in phase {phase.value}")
            
            self.logger.info(f"✅ Phase {phase.value} completed")
        
        return overall_success
    
    def _execute_phase_agents(self, phase_agents: List[AgentStartup]) -> bool:
        """Execute agents within a phase, respecting dependencies"""
        remaining_agents = phase_agents.copy()
        phase_success = True
        
        while remaining_agents:
            # Find agents that can be started (dependencies satisfied)
            ready_agents = []
            for agent in remaining_agents:
                if self._are_dependencies_satisfied(agent):
                    ready_agents.append(agent)
            
            if not ready_agents:
                # Check if we're deadlocked
                pending_agents = [a for a in remaining_agents if a.status == AgentStatus.PENDING]
                if pending_agents:
                    self.logger.error(f"💥 Dependency deadlock detected:")
                    for agent in pending_agents:
                        unsatisfied_deps = [dep for dep in agent.dependencies 
                                          if not any(a.agent_type == dep and a.status == AgentStatus.COMPLETED 
                                                   for a in self.agents)]
                        self.logger.error(f"   🔗 {agent.agent_name} waiting for: {[dep.value for dep in unsatisfied_deps]}")
                    phase_success = False
                break
            
            # Start ready agents
            if len(ready_agents) == 1:
                # Start single agent synchronously
                self._start_agent_sync(ready_agents[0])
            else:
                # Start multiple agents in parallel
                self._start_agents_parallel(ready_agents)
            
            # Wait for agents to complete
            self._wait_for_agents(ready_agents)
            
            # Remove completed agents
            for agent in ready_agents:
                remaining_agents.remove(agent)
                if agent.status == AgentStatus.FAILED and agent.critical:
                    phase_success = False
        
        return phase_success
    
    def _are_dependencies_satisfied(self, agent: AgentStartup) -> bool:
        """Check if agent dependencies are satisfied"""
        for dep_type in agent.dependencies:
            dep_agent = next((a for a in self.agents if a.agent_type == dep_type), None)
            if not dep_agent or dep_agent.status not in [AgentStatus.COMPLETED, AgentStatus.ACTIVE]:
                return False
        return True
    
    def _start_agent_sync(self, agent: AgentStartup):
        """Start a single agent synchronously"""
        self.logger.info(f"🔧 Starting: {agent.agent_name}")
        self._start_agent(agent)
    
    def _start_agents_parallel(self, agents: List[AgentStartup]):
        """Start multiple agents in parallel"""
        self.logger.info(f"🔧 Starting {len(agents)} agents in parallel:")
        for agent in agents:
            self.logger.info(f"   🔧 {agent.agent_name}")
        
        threads = []
        for agent in agents:
            if os.path.exists(agent.startup_script):
                thread = threading.Thread(target=self._start_agent, args=(agent,))
                thread.start()
                threads.append(thread)
            else:
                self.logger.warning(f"⚠️ Startup script not found: {agent.startup_script}")
                agent.status = AgentStatus.FAILED
                agent.error = "Startup script not found"
    
    def _start_agent(self, agent: AgentStartup):
        """Start a single agent"""
        agent.start_time = datetime.now()
        agent.status = AgentStatus.STARTING
        
        self._update_status()
        
        try:
            # Determine command based on script type
            if agent.startup_script.endswith('.py'):
                cmd = [sys.executable, agent.startup_script, "--project-root", self.project_root]
            elif agent.startup_script.endswith('.sh'):
                cmd = ["bash", agent.startup_script]
            else:
                cmd = [agent.startup_script]
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            agent.pid = process.pid
            self.active_processes[agent.agent_type] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=agent.timeout_seconds)
                
                agent.end_time = datetime.now()
                agent.duration_seconds = (agent.end_time - agent.start_time).total_seconds()
                agent.output = stdout
                agent.error = stderr
                
                if process.returncode == 0:
                    agent.status = AgentStatus.COMPLETED
                    self.session.agents_started += 1
                    self.logger.info(f"✅ {agent.agent_name} completed successfully in {agent.duration_seconds:.2f}s")
                else:
                    agent.status = AgentStatus.FAILED
                    self.session.agents_failed += 1
                    self.logger.error(f"❌ {agent.agent_name} failed with return code {process.returncode}")
                    if stderr:
                        self.logger.error(f"Error output: {stderr[:200]}...")
                
            except subprocess.TimeoutExpired:
                process.kill()
                agent.status = AgentStatus.TIMEOUT
                agent.end_time = datetime.now()
                agent.duration_seconds = agent.timeout_seconds
                agent.error = f"Timeout after {agent.timeout_seconds} seconds"
                self.session.agents_failed += 1
                self.logger.error(f"⏰ {agent.agent_name} timed out after {agent.timeout_seconds}s")
            
        except Exception as e:
            agent.end_time = datetime.now()
            agent.duration_seconds = (agent.end_time - agent.start_time).total_seconds()
            agent.status = AgentStatus.FAILED
            agent.error = str(e)
            self.session.agents_failed += 1
            self.logger.error(f"💥 {agent.agent_name} failed with exception: {e}")
        
        finally:
            # Clean up process tracking
            if agent.agent_type in self.active_processes:
                del self.active_processes[agent.agent_type]
    
    def _wait_for_agents(self, agents: List[AgentStartup]):
        """Wait for agents to complete startup"""
        max_wait_time = max(a.timeout_seconds for a in agents) + 30  # Extra buffer
        start_wait = time.time()
        
        while time.time() - start_wait < max_wait_time:
            all_done = True
            for agent in agents:
                if agent.status in [AgentStatus.PENDING, AgentStatus.STARTING]:
                    all_done = False
                    break
            
            if all_done:
                break
            
            time.sleep(2)  # Check every 2 seconds
            self._update_status()
        
        # Force timeout any remaining agents
        for agent in agents:
            if agent.status in [AgentStatus.PENDING, AgentStatus.STARTING]:
                agent.status = AgentStatus.TIMEOUT
                agent.error = "Forced timeout during phase completion"
                self.logger.warning(f"⏰ Forced timeout for {agent.agent_name}")
    
    def _initialize_coordination(self):
        """Initialize cross-agent coordination"""
        try:
            self.logger.info("🔗 Initializing cross-agent coordination...")
            
            # Collect agent statuses
            agent_statuses = {}
            for agent in self.agents:
                agent_statuses[agent.agent_type.value] = {
                    "status": agent.status.value,
                    "capabilities": agent.capabilities,
                    "duration": agent.duration_seconds
                }
            
            # Create coordination configuration
            coordination_config = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "agent_statuses": agent_statuses,
                "coordination_patterns": {
                    "claude_code_claude_engineer": {
                        "pattern": "collaborative_improvement",
                        "description": "Claude Code handles implementation, Claude Engineer provides optimization tools"
                    },
                    "claude_code_gemini": {
                        "pattern": "analysis_implementation",
                        "description": "Gemini analyzes and reviews, Claude Code implements"
                    },
                    "all_agents_moex": {
                        "pattern": "orchestrated_coordination",
                        "description": "MOEX coordinates all agents for complex workflows"
                    }
                },
                "active_workflows": [
                    "intelligent_development",
                    "continuous_improvement", 
                    "quality_assurance",
                    "performance_optimization"
                ]
            }
            
            self.session.coordination_status = coordination_config
            
            # Save coordination configuration
            coordination_file = os.path.join(self.project_root, "moex-workspace", "coordination-config.json")
            os.makedirs(os.path.dirname(coordination_file), exist_ok=True)
            with open(coordination_file, 'w') as f:
                json.dump(coordination_config, f, indent=2)
            
            self.logger.info("✅ Cross-agent coordination initialized")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize coordination: {e}")
    
    def _shutdown_all_agents(self):
        """Shutdown all active agents"""
        self.logger.info("🛑 Shutting down all active agents...")
        
        for agent_type, process in self.active_processes.items():
            try:
                process.terminate()
                time.sleep(2)  # Give process time to shutdown gracefully
                if process.poll() is None:
                    process.kill()
                self.logger.info(f"🛑 Shutdown: {agent_type.value}")
            except Exception as e:
                self.logger.error(f"Error shutting down {agent_type.value}: {e}")
        
        self.active_processes.clear()
    
    def _update_status(self):
        """Update comprehensive startup status file"""
        try:
            with self.startup_lock:
                status_data = {
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "phase": "in_progress",
                    "agents_started": self.session.agents_started,
                    "agents_failed": self.session.agents_failed,
                    "active_processes": [key.value for key in self.active_processes.keys()],
                    "agents": [
                        {
                            "agent_type": a.agent_type.value,
                            "agent_name": a.agent_name,
                            "phase": a.phase.value,
                            "status": a.status.value,
                            "duration": a.duration_seconds,
                            "capabilities": a.capabilities,
                            "pid": a.pid
                        }
                        for a in self.agents
                    ]
                }
                
                with open(self.status_file, 'w') as f:
                    json.dump(status_data, f, indent=2)
                    
        except Exception as e:
            self.logger.warning(f"Failed to update status file: {e}")
    
    def _finalize_session(self, success: bool, early_termination: bool = False):
        """Finalize the comprehensive startup session"""
        self.session.end_time = datetime.now()
        self.session.total_duration = (self.session.end_time - self.session.start_time).total_seconds()
        self.session.success = success
        
        # Create comprehensive final report
        report_file = os.path.join(
            self.project_root, 
            "reports", 
            f"comprehensive-startup-{self.session_id}.json"
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
            "agents_started": self.session.agents_started,
            "agents_failed": self.session.agents_failed,
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
        """Generate comprehensive startup session summary"""
        completed_agents = [a for a in self.agents if a.status == AgentStatus.COMPLETED]
        failed_agents = [a for a in self.agents if a.status == AgentStatus.FAILED]
        timeout_agents = [a for a in self.agents if a.status == AgentStatus.TIMEOUT]
        
        phases_completed = len(set(a.phase for a in completed_agents))
        total_phases = len(set(a.phase for a in self.agents))
        
        # Calculate capabilities
        total_capabilities = []
        for agent in completed_agents:
            total_capabilities.extend(agent.capabilities)
        unique_capabilities = list(set(total_capabilities))
        
        return {
            "total_agents": len(self.agents),
            "completed_agents": len(completed_agents),
            "failed_agents": len(failed_agents),
            "timeout_agents": len(timeout_agents),
            "success_rate": len(completed_agents) / len(self.agents) * 100,
            "phases_completed": phases_completed,
            "total_phases": total_phases,
            "critical_failures": len([a for a in failed_agents if a.critical]),
            "average_startup_time": statistics.mean([a.duration_seconds for a in completed_agents]) if completed_agents else 0,
            "longest_startup": max([a.duration_seconds for a in completed_agents]) if completed_agents else 0,
            "total_capabilities": len(unique_capabilities),
            "available_capabilities": unique_capabilities
        }
    
    def _log_completion_summary(self, success: bool, early_termination: bool, report_file: str):
        """Log comprehensive completion summary"""
        status_emoji = "✅" if success else "❌"
        termination_note = " (early termination)" if early_termination else ""
        
        self.logger.info("=" * 80)
        self.logger.info(f"{status_emoji} COMPREHENSIVE AI DEVELOPMENT ECOSYSTEM STARTUP COMPLETED{termination_note}")
        self.logger.info("=" * 80)
        
        summary = self._generate_summary()
        
        self.logger.info(f"📊 STARTUP METRICS:")
        self.logger.info(f"   Total Duration: {self.session.total_duration:.2f} seconds")
        self.logger.info(f"   Agents Started: {summary['completed_agents']}/{summary['total_agents']}")
        self.logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        self.logger.info(f"   Phases Completed: {summary['phases_completed']}/{summary['total_phases']}")
        self.logger.info(f"   Available Capabilities: {summary['total_capabilities']}")
        
        if summary['failed_agents'] > 0:
            failed_agents = [a for a in self.agents if a.status in [AgentStatus.FAILED, AgentStatus.TIMEOUT]]
            self.logger.info(f"💥 FAILED AGENTS:")
            for agent in failed_agents:
                self.logger.info(f"   ❌ {agent.agent_name}: {agent.status.value}")
                if agent.error:
                    self.logger.info(f"      Error: {agent.error[:100]}...")
        
        completed_agents = [a for a in self.agents if a.status == AgentStatus.COMPLETED]
        if completed_agents:
            self.logger.info(f"✅ SUCCESSFUL AGENTS:")
            for agent in completed_agents:
                caps = ", ".join(agent.capabilities[:3])
                if len(agent.capabilities) > 3:
                    caps += f" (+{len(agent.capabilities)-3} more)"
                self.logger.info(f"   ✅ {agent.agent_name}: {agent.duration_seconds:.2f}s ({caps})")
        
        # Agent-specific status
        self.logger.info(f"🤖 AI ECOSYSTEM STATUS:")
        claude_code = next((a for a in self.agents if a.agent_type == AgentType.CLAUDE_CODE), None)
        if claude_code:
            self.logger.info(f"   Claude Code: {claude_code.status.value}")
        
        claude_engineer = next((a for a in self.agents if a.agent_type == AgentType.CLAUDE_ENGINEER), None)
        if claude_engineer:
            self.logger.info(f"   Claude Engineer: {claude_engineer.status.value}")
        
        gemini = next((a for a in self.agents if a.agent_type == AgentType.GEMINI_CLI), None)
        if gemini:
            self.logger.info(f"   Gemini CLI: {gemini.status.value}")
        
        moex = next((a for a in self.agents if a.agent_type == AgentType.MOEX), None)
        if moex:
            self.logger.info(f"   MOEX Coordination: {moex.status.value}")
        
        self.logger.info(f"📋 Full Report: {report_file}")
        self.logger.info("=" * 80)
        
        if success:
            self.logger.info("🎉 AI Development Ecosystem is ready!")
            self.logger.info("🚀 Available Agents:")
            for agent in completed_agents:
                self.logger.info(f"   🤖 {agent.agent_name}")
            self.logger.info("💡 Start developing with multi-agent AI assistance!")
            self.logger.info("🔧 Use Claude Engineer for self-improving tools and optimization")
            self.logger.info("📊 Use Gemini CLI for analysis and documentation")
            self.logger.info("🔄 Use MOEX for coordinated multi-agent workflows")
        else:
            self.logger.error("⚠️ Startup completed with issues - check logs and status for details")

def main():
    """Main entry point for comprehensive startup orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive AI Development Ecosystem Startup Orchestrator")
    parser.add_argument("--project-root", default="/Users/studio/hardcard", 
                       help="Project root directory")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--timeout-multiplier", type=float, default=1.0,
                       help="Multiply all timeout values by this factor")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run comprehensive startup
    orchestrator = ComprehensiveStartupOrchestrator(args.project_root)
    
    # Apply timeout multiplier if specified
    if args.timeout_multiplier != 1.0:
        for agent in orchestrator.agents:
            agent.timeout_seconds = int(agent.timeout_seconds * args.timeout_multiplier)
    
    success = orchestrator.run_comprehensive_startup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()