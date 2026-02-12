#!/usr/bin/env python3
"""
MOEX Startup Sequence - Advanced startup automation for MOEX Intelligence
Coordination system that orchestrates Claude Code and Gemini CLI integration.

This script implements the complete MOEX startup sequence with coordination capabilities.
"""

import os
import sys
import json
import time
import subprocess
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import signal
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

class MOEXStartupPhase(Enum):
    INITIALIZATION = "initialization"
    COORDINATION_SETUP = "coordination_setup"
    AGENT_DISCOVERY = "agent_discovery"
    INTEGRATION = "integration"
    ORCHESTRATION = "orchestration"
    MONITORING = "monitoring"
    COMPLETION = "completion"

class MOEXComponentStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class AgentType(Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    UNKNOWN = "unknown"

@dataclass
class MOEXAgent:
    agent_type: AgentType
    agent_id: str
    status: str
    capabilities: List[str]
    last_seen: datetime
    session_id: str = ""
    version: str = ""
    workspace: str = ""

@dataclass
class MOEXStartupComponent:
    name: str
    description: str
    phase: MOEXStartupPhase
    status: MOEXComponentStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    output: str = ""
    error: str = ""
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class MOEXStartupSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    components: List[MOEXStartupComponent] = None
    discovered_agents: List[MOEXAgent] = None
    coordination_config: Dict[str, Any] = None
    active_workflows: List[str] = None
    success: bool = False
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.discovered_agents is None:
            self.discovered_agents = []
        if self.coordination_config is None:
            self.coordination_config = {}
        if self.active_workflows is None:
            self.active_workflows = []

class MOEXStartupSequence:
    """Advanced MOEX Intelligence Coordination startup sequence manager"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.session_id = f"moex_startup_{int(time.time())}"
        self.session = MOEXStartupSession(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Setup logging
        self.log_file = os.path.join(project_root, "logs", "moex-startup-sequence.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("MOEXStartup")
        
        # Component registry
        self.components = self._initialize_components()
        
        # Configuration files
        self.config_file = os.path.join(project_root, "moex-config.json")
        self.workspace_dir = os.path.join(project_root, "moex-workspace")
        self.status_file = os.path.join(project_root, "monitoring", "moex-startup-status.json")
        
        # Agent tracking
        self.claude_status_file = os.path.join(self.workspace_dir, "claude-status.json")
        self.gemini_status_file = os.path.join(self.workspace_dir, "gemini-status.json")
        self.coordination_queue_file = os.path.join(self.workspace_dir, "coordination-queue.json")
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_components(self) -> List[MOEXStartupComponent]:
        """Initialize all MOEX startup components"""
        return [
            # Phase 1: Initialization
            MOEXStartupComponent(
                name="workspace_initialization",
                description="Initialize MOEX coordination workspace",
                phase=MOEXStartupPhase.INITIALIZATION,
                status=MOEXComponentStatus.PENDING
            ),
            MOEXStartupComponent(
                name="configuration_setup",
                description="Load and validate MOEX configuration",
                phase=MOEXStartupPhase.INITIALIZATION,
                status=MOEXComponentStatus.PENDING,
                dependencies=["workspace_initialization"]
            ),
            
            # Phase 2: Coordination Setup
            MOEXStartupComponent(
                name="communication_channels",
                description="Set up inter-agent communication channels",
                phase=MOEXStartupPhase.COORDINATION_SETUP,
                status=MOEXComponentStatus.PENDING,
                dependencies=["configuration_setup"]
            ),
            MOEXStartupComponent(
                name="task_queue_system",
                description="Initialize task queue and coordination system",
                phase=MOEXStartupPhase.COORDINATION_SETUP,
                status=MOEXComponentStatus.PENDING,
                dependencies=["communication_channels"]
            ),
            
            # Phase 3: Agent Discovery
            MOEXStartupComponent(
                name="claude_discovery",
                description="Discover and register Claude Code agents",
                phase=MOEXStartupPhase.AGENT_DISCOVERY,
                status=MOEXComponentStatus.PENDING,
                dependencies=["task_queue_system"]
            ),
            MOEXStartupComponent(
                name="gemini_discovery",
                description="Discover and register Gemini CLI agents",
                phase=MOEXStartupPhase.AGENT_DISCOVERY,
                status=MOEXComponentStatus.PENDING,
                dependencies=["claude_discovery"]
            ),
            
            # Phase 4: Integration
            MOEXStartupComponent(
                name="workflow_registration",
                description="Register coordination workflows",
                phase=MOEXStartupPhase.INTEGRATION,
                status=MOEXComponentStatus.PENDING,
                dependencies=["gemini_discovery"]
            ),
            MOEXStartupComponent(
                name="task_routing_setup",
                description="Configure intelligent task routing",
                phase=MOEXStartupPhase.INTEGRATION,
                status=MOEXComponentStatus.PENDING,
                dependencies=["workflow_registration"]
            ),
            
            # Phase 5: Orchestration
            MOEXStartupComponent(
                name="coordination_engine",
                description="Start coordination engine",
                phase=MOEXStartupPhase.ORCHESTRATION,
                status=MOEXComponentStatus.PENDING,
                dependencies=["task_routing_setup"]
            ),
            MOEXStartupComponent(
                name="workflow_scheduler",
                description="Initialize workflow scheduler",
                phase=MOEXStartupPhase.ORCHESTRATION,
                status=MOEXComponentStatus.PENDING,
                dependencies=["coordination_engine"]
            ),
            
            # Phase 6: Monitoring
            MOEXStartupComponent(
                name="health_monitoring",
                description="Start agent health monitoring",
                phase=MOEXStartupPhase.MONITORING,
                status=MOEXComponentStatus.PENDING,
                dependencies=["workflow_scheduler"]
            ),
            MOEXStartupComponent(
                name="performance_tracking",
                description="Initialize performance tracking",
                phase=MOEXStartupPhase.MONITORING,
                status=MOEXComponentStatus.PENDING,
                dependencies=["health_monitoring"]
            ),
            
            # Phase 7: Completion
            MOEXStartupComponent(
                name="dashboard_activation",
                description="Activate coordination dashboard",
                phase=MOEXStartupPhase.COMPLETION,
                status=MOEXComponentStatus.PENDING,
                dependencies=["performance_tracking"]
            ),
            MOEXStartupComponent(
                name="session_finalization",
                description="Finalize MOEX startup session",
                phase=MOEXStartupPhase.COMPLETION,
                status=MOEXComponentStatus.PENDING,
                dependencies=["dashboard_activation"]
            )
        ]
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning(f"Received signal {signum}, shutting down MOEX startup...")
        self._finalize_session(success=False, early_termination=True)
        sys.exit(1)
    
    def run_startup_sequence(self) -> bool:
        """Execute the complete MOEX startup sequence"""
        self.logger.info(f"🔄 Starting MOEX Intelligence Coordination startup sequence (Session: {self.session_id})")
        
        try:
            # Execute components in dependency order
            for component in self.components:
                if not self._can_execute_component(component):
                    self.logger.info(f"⏸️ Skipping {component.name} - dependencies not met")
                    component.status = MOEXComponentStatus.SKIPPED
                    continue
                
                success = self._execute_component(component)
                if not success and component.name not in ["dashboard_activation"]:
                    # Allow some components to fail gracefully
                    self.logger.error(f"❌ Critical component {component.name} failed")
                    self._finalize_session(success=False)
                    return False
            
            # Complete startup
            self._finalize_session(success=True)
            return True
            
        except Exception as e:
            self.logger.error(f"💥 MOEX startup sequence failed with exception: {e}")
            self._finalize_session(success=False)
            return False
    
    def _can_execute_component(self, component: MOEXStartupComponent) -> bool:
        """Check if component dependencies are satisfied"""
        for dep_name in component.dependencies:
            dep_component = next((c for c in self.components if c.name == dep_name), None)
            if not dep_component or dep_component.status != MOEXComponentStatus.COMPLETED:
                return False
        return True
    
    def _execute_component(self, component: MOEXStartupComponent) -> bool:
        """Execute a single startup component"""
        component.start_time = datetime.now()
        component.status = MOEXComponentStatus.ACTIVE
        
        self.logger.info(f"⚙️ Executing: {component.description}")
        self._update_status()
        
        try:
            # Route to appropriate handler
            handler_name = f"_handle_{component.name}"
            if hasattr(self, handler_name):
                handler = getattr(self, handler_name)
                success = handler(component)
            else:
                self.logger.warning(f"No handler found for {component.name}")
                success = True  # Default to success for unhandled components
            
            # Update component status
            component.end_time = datetime.now()
            component.duration_seconds = (component.end_time - component.start_time).total_seconds()
            component.status = MOEXComponentStatus.COMPLETED if success else MOEXComponentStatus.FAILED
            
            status_emoji = "✅" if success else "❌"
            self.logger.info(f"{status_emoji} {component.description} completed in {component.duration_seconds:.2f}s")
            
            return success
            
        except Exception as e:
            component.end_time = datetime.now()
            component.duration_seconds = (component.end_time - component.start_time).total_seconds()
            component.error = str(e)
            component.status = MOEXComponentStatus.FAILED
            
            self.logger.error(f"❌ {component.description} failed: {e}")
            return False
    
    # Component Handlers
    
    def _handle_workspace_initialization(self, component: MOEXStartupComponent) -> bool:
        """Initialize MOEX coordination workspace"""
        try:
            # Create workspace directory structure
            workspace_subdirs = [
                "tasks",
                "agents", 
                "workflows",
                "reports",
                "logs"
            ]
            
            created_dirs = []
            for subdir in workspace_subdirs:
                full_path = os.path.join(self.workspace_dir, subdir)
                if not os.path.exists(full_path):
                    os.makedirs(full_path, exist_ok=True)
                    created_dirs.append(subdir)
            
            # Initialize status files
            self._initialize_status_files()
            
            component.output = f"Workspace initialized with {len(workspace_subdirs)} directories"
            if created_dirs:
                component.output += f" (created: {created_dirs})"
            
            return True
            
        except Exception as e:
            component.error = f"Workspace initialization failed: {e}"
            return False
    
    def _handle_configuration_setup(self, component: MOEXStartupComponent) -> bool:
        """Load and validate MOEX configuration"""
        try:
            if not os.path.exists(self.config_file):
                # Create default configuration
                default_config = {
                    "coordinator": {
                        "name": "hardcard-moex",
                        "version": "1.0.0",
                        "project_root": self.project_root
                    },
                    "agents": {
                        "claude": {
                            "type": "implementation",
                            "workspace": self.project_root,
                            "capabilities": ["feature_implementation", "bug_fixing", "testing", "git_operations"]
                        },
                        "gemini": {
                            "type": "analysis",
                            "config": "./gemini.yaml",
                            "capabilities": ["code_analysis", "security_scanning", "documentation_generation"]
                        }
                    },
                    "routing": {
                        "implementation_tasks": {"primary": "claude", "review": "gemini"},
                        "analysis_tasks": {"primary": "gemini", "validation": "claude"},
                        "documentation_tasks": {"primary": "gemini", "integration": "claude"}
                    },
                    "workflows": {
                        "feature_development": {
                            "name": "Full Feature Development",
                            "steps": [
                                {"name": "exploration", "agent": "claude", "action": "explore_codebase"},
                                {"name": "planning", "agent": "claude", "action": "create_implementation_plan"},
                                {"name": "analysis", "agent": "gemini", "action": "analyze_impact"},
                                {"name": "implementation", "agent": "claude", "action": "implement_feature"},
                                {"name": "review", "agent": "gemini", "action": "comprehensive_review"}
                            ]
                        }
                    },
                    "monitoring": {
                        "health_check_interval": 300,
                        "performance_tracking": True,
                        "error_recovery": True
                    }
                }
                
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                component.output = "Created default MOEX configuration"
            else:
                # Load existing configuration
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        # Try to parse as YAML first, fallback to JSON
                        try:
                            import yaml
                            config = yaml.safe_load(f)
                        except ImportError:
                            f.seek(0)
                            config = json.load(f)
                    else:
                        config = json.load(f)
                
                component.output = f"Loaded configuration with {len(config.get('agents', {}))} agents"
            
            # Store configuration in session
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    try:
                        import yaml
                        self.session.coordination_config = yaml.safe_load(f)
                    except ImportError:
                        f.seek(0)
                        self.session.coordination_config = json.load(f)
                else:
                    self.session.coordination_config = json.load(f)
            
            return True
            
        except Exception as e:
            component.error = f"Configuration setup failed: {e}"
            return False
    
    def _handle_communication_channels(self, component: MOEXStartupComponent) -> bool:
        """Set up inter-agent communication channels"""
        try:
            # Create communication files
            communication_files = [
                "agent-messages.json",
                "coordination-log.json", 
                "status-updates.json"
            ]
            
            for comm_file in communication_files:
                file_path = os.path.join(self.workspace_dir, comm_file)
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        json.dump({"messages": [], "created": datetime.now().isoformat()}, f, indent=2)
            
            component.output = f"Created {len(communication_files)} communication channels"
            return True
            
        except Exception as e:
            component.error = f"Communication channels setup failed: {e}"
            return False
    
    def _handle_task_queue_system(self, component: MOEXStartupComponent) -> bool:
        """Initialize task queue and coordination system"""
        try:
            # Initialize coordination queue
            queue_data = {
                "queue": [],
                "last_updated": datetime.now().isoformat(),
                "active_tasks": {},
                "completed_tasks": [],
                "failed_tasks": []
            }
            
            with open(self.coordination_queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
            
            component.output = "Task queue system initialized"
            return True
            
        except Exception as e:
            component.error = f"Task queue system setup failed: {e}"
            return False
    
    def _handle_claude_discovery(self, component: MOEXStartupComponent) -> bool:
        """Discover and register Claude Code agents"""
        try:
            discovered_agents = []
            
            # Check for Claude status file
            if os.path.exists(self.claude_status_file):
                with open(self.claude_status_file, 'r') as f:
                    claude_status = json.load(f)
                
                claude_agent = MOEXAgent(
                    agent_type=AgentType.CLAUDE,
                    agent_id="claude-main",
                    status=claude_status.get("status", "unknown"),
                    capabilities=claude_status.get("capabilities", ["implementation", "testing", "git_operations"]),
                    last_seen=datetime.now(),
                    session_id=claude_status.get("session_id", ""),
                    workspace=self.project_root
                )
                
                discovered_agents.append(claude_agent)
            
            # Check for additional Claude agents in worktrees
            try:
                result = subprocess.run(
                    ["git", "worktree", "list"], 
                    cwd=self.project_root, 
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    worktrees = result.stdout.strip().split('\n')
                    for i, worktree_line in enumerate(worktrees[1:], 1):  # Skip main worktree
                        parts = worktree_line.split()
                        if len(parts) >= 2:
                            workspace = parts[0]
                            branch = parts[1].strip('[]')
                            
                            if "ai" in branch.lower():
                                agent_id = f"claude-{os.path.basename(workspace)}"
                                worktree_agent = MOEXAgent(
                                    agent_type=AgentType.CLAUDE,
                                    agent_id=agent_id,
                                    status="available",
                                    capabilities=["specialized_development"],
                                    last_seen=datetime.now(),
                                    workspace=workspace
                                )
                                discovered_agents.append(worktree_agent)
            except Exception as e:
                self.logger.warning(f"Error discovering worktree agents: {e}")
            
            self.session.discovered_agents.extend(discovered_agents)
            component.output = f"Discovered {len(discovered_agents)} Claude agents"
            return True
            
        except Exception as e:
            component.error = f"Claude discovery failed: {e}"
            return False
    
    def _handle_gemini_discovery(self, component: MOEXStartupComponent) -> bool:
        """Discover and register Gemini CLI agents"""
        try:
            discovered_agents = []
            
            # Check for Gemini status file
            if os.path.exists(self.gemini_status_file):
                with open(self.gemini_status_file, 'r') as f:
                    gemini_status = json.load(f)
                
                gemini_agent = MOEXAgent(
                    agent_type=AgentType.GEMINI,
                    agent_id="gemini-main",
                    status=gemini_status.get("status", "unknown"),
                    capabilities=gemini_status.get("capabilities", ["analysis", "documentation", "review"]),
                    last_seen=datetime.now(),
                    session_id=gemini_status.get("session_id", ""),
                    version=gemini_status.get("version", "")
                )
                
                discovered_agents.append(gemini_agent)
            
            # Check for specialized Gemini agents
            if self.session.coordination_config:
                agents_config = self.session.coordination_config.get("agents", {})
                if "gemini" in agents_config:
                    gemini_config = agents_config["gemini"]
                    capabilities = gemini_config.get("capabilities", [])
                    
                    # Create specialized agents for each capability
                    for capability in capabilities:
                        if capability not in ["analysis", "documentation", "review"]:  # Skip already covered
                            specialized_agent = MOEXAgent(
                                agent_type=AgentType.GEMINI,
                                agent_id=f"gemini-{capability}",
                                status="available",
                                capabilities=[capability],
                                last_seen=datetime.now()
                            )
                            discovered_agents.append(specialized_agent)
            
            self.session.discovered_agents.extend(discovered_agents)
            component.output = f"Discovered {len(discovered_agents)} Gemini agents"
            return True
            
        except Exception as e:
            component.error = f"Gemini discovery failed: {e}"
            return False
    
    def _handle_workflow_registration(self, component: MOEXStartupComponent) -> bool:
        """Register coordination workflows"""
        try:
            workflows = []
            
            if self.session.coordination_config:
                config_workflows = self.session.coordination_config.get("workflows", {})
                workflows = list(config_workflows.keys())
                self.session.active_workflows = workflows
            
            component.output = f"Registered {len(workflows)} workflows: {workflows}"
            return True
            
        except Exception as e:
            component.error = f"Workflow registration failed: {e}"
            return False
    
    def _handle_task_routing_setup(self, component: MOEXStartupComponent) -> bool:
        """Configure intelligent task routing"""
        try:
            routing_rules = {}
            
            if self.session.coordination_config:
                routing_config = self.session.coordination_config.get("routing", {})
                routing_rules = routing_config
            
            # Create routing logic file
            routing_file = os.path.join(self.workspace_dir, "task-routing.json")
            with open(routing_file, 'w') as f:
                json.dump({
                    "routing_rules": routing_rules,
                    "last_updated": datetime.now().isoformat(),
                    "active_routes": []
                }, f, indent=2)
            
            component.output = f"Configured {len(routing_rules)} routing rules"
            return True
            
        except Exception as e:
            component.error = f"Task routing setup failed: {e}"
            return False
    
    def _handle_coordination_engine(self, component: MOEXStartupComponent) -> bool:
        """Start coordination engine"""
        try:
            # Create coordination engine status
            engine_status = {
                "status": "active",
                "started_at": datetime.now().isoformat(),
                "session_id": self.session_id,
                "discovered_agents": len(self.session.discovered_agents),
                "active_workflows": len(self.session.active_workflows)
            }
            
            engine_file = os.path.join(self.workspace_dir, "coordination-engine.json")
            with open(engine_file, 'w') as f:
                json.dump(engine_status, f, indent=2)
            
            component.output = f"Coordination engine started with {len(self.session.discovered_agents)} agents"
            return True
            
        except Exception as e:
            component.error = f"Coordination engine startup failed: {e}"
            return False
    
    def _handle_workflow_scheduler(self, component: MOEXStartupComponent) -> bool:
        """Initialize workflow scheduler"""
        try:
            # Create scheduler configuration
            scheduler_config = {
                "status": "active",
                "check_interval_seconds": 30,
                "max_concurrent_workflows": 5,
                "started_at": datetime.now().isoformat(),
                "active_schedules": []
            }
            
            scheduler_file = os.path.join(self.workspace_dir, "workflow-scheduler.json")
            with open(scheduler_file, 'w') as f:
                json.dump(scheduler_config, f, indent=2)
            
            component.output = "Workflow scheduler initialized"
            return True
            
        except Exception as e:
            component.error = f"Workflow scheduler initialization failed: {e}"
            return False
    
    def _handle_health_monitoring(self, component: MOEXStartupComponent) -> bool:
        """Start agent health monitoring"""
        try:
            # Create health monitoring configuration
            health_config = {
                "status": "active",
                "monitoring_interval_seconds": 60,
                "agents_monitored": [agent.agent_id for agent in self.session.discovered_agents],
                "health_checks": ["status", "responsiveness", "capability"],
                "started_at": datetime.now().isoformat()
            }
            
            health_file = os.path.join(self.workspace_dir, "health-monitoring.json")
            with open(health_file, 'w') as f:
                json.dump(health_config, f, indent=2)
            
            component.output = f"Health monitoring started for {len(self.session.discovered_agents)} agents"
            return True
            
        except Exception as e:
            component.error = f"Health monitoring startup failed: {e}"
            return False
    
    def _handle_performance_tracking(self, component: MOEXStartupComponent) -> bool:
        """Initialize performance tracking"""
        try:
            # Create performance tracking configuration
            performance_config = {
                "status": "active",
                "metrics_tracked": [
                    "task_completion_time",
                    "agent_response_time", 
                    "workflow_success_rate",
                    "coordination_overhead"
                ],
                "reporting_interval_minutes": 15,
                "started_at": datetime.now().isoformat(),
                "baseline_metrics": {}
            }
            
            performance_file = os.path.join(self.workspace_dir, "performance-tracking.json")
            with open(performance_file, 'w') as f:
                json.dump(performance_config, f, indent=2)
            
            component.output = f"Performance tracking initialized with {len(performance_config['metrics_tracked'])} metrics"
            return True
            
        except Exception as e:
            component.error = f"Performance tracking initialization failed: {e}"
            return False
    
    def _handle_dashboard_activation(self, component: MOEXStartupComponent) -> bool:
        """Activate coordination dashboard"""
        try:
            # Check if MOEX coordinator script exists
            coordinator_script = os.path.join(self.project_root, "scripts", "moex-coordinator.sh")
            if os.path.exists(coordinator_script):
                # Test dashboard functionality
                result = subprocess.run(
                    [coordinator_script, "status"], 
                    cwd=self.project_root,
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                component.output = f"Dashboard activated: {result.stdout.strip()}"
                return result.returncode == 0
            else:
                component.output = "Dashboard script not found - manual activation required"
                return True  # Non-critical
                
        except subprocess.TimeoutExpired:
            component.output = "Dashboard activation timed out"
            return True  # Non-critical
        except Exception as e:
            component.error = f"Dashboard activation failed: {e}"
            return True  # Non-critical
    
    def _handle_session_finalization(self, component: MOEXStartupComponent) -> bool:
        """Finalize MOEX startup session"""
        try:
            # Calculate session metrics
            completed_components = [c for c in self.components if c.status == MOEXComponentStatus.COMPLETED]
            failed_components = [c for c in self.components if c.status == MOEXComponentStatus.FAILED]
            
            success_rate = len(completed_components) / len(self.components) * 100
            
            # Create final session summary
            session_summary = {
                "session_id": self.session_id,
                "success_rate": success_rate,
                "agents_discovered": len(self.session.discovered_agents),
                "workflows_registered": len(self.session.active_workflows),
                "coordination_active": True,
                "finalized_at": datetime.now().isoformat()
            }
            
            summary_file = os.path.join(self.workspace_dir, "session-summary.json")
            with open(summary_file, 'w') as f:
                json.dump(session_summary, f, indent=2)
            
            component.output = f"MOEX session finalized: {len(completed_components)}/{len(self.components)} components successful ({success_rate:.1f}%)"
            
            if failed_components:
                component.output += f" - Failed: {[c.name for c in failed_components]}"
            
            return len(failed_components) == 0
            
        except Exception as e:
            component.error = f"Session finalization failed: {e}"
            return False
    
    def _initialize_status_files(self):
        """Initialize agent status files"""
        try:
            # Initialize Claude status if not exists
            if not os.path.exists(self.claude_status_file):
                claude_status = {
                    "status": "initialized",
                    "timestamp": datetime.now().isoformat(),
                    "capabilities": ["implementation", "testing", "git_operations"],
                    "session_id": self.session_id
                }
                with open(self.claude_status_file, 'w') as f:
                    json.dump(claude_status, f, indent=2)
            
            # Initialize Gemini status if not exists
            if not os.path.exists(self.gemini_status_file):
                gemini_status = {
                    "status": "initialized",
                    "timestamp": datetime.now().isoformat(),
                    "capabilities": ["analysis", "documentation", "review"],
                    "session_id": self.session_id
                }
                with open(self.gemini_status_file, 'w') as f:
                    json.dump(gemini_status, f, indent=2)
            
            # Initialize coordination queue if not exists
            if not os.path.exists(self.coordination_queue_file):
                queue_data = {
                    "queue": [],
                    "last_updated": datetime.now().isoformat(),
                    "initialized_by": self.session_id
                }
                with open(self.coordination_queue_file, 'w') as f:
                    json.dump(queue_data, f, indent=2)
                    
        except Exception as e:
            self.logger.warning(f"Failed to initialize status files: {e}")
    
    def _update_status(self):
        """Update MOEX startup status file"""
        try:
            status_data = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "phase": "in_progress",
                "discovered_agents": len(self.session.discovered_agents),
                "active_workflows": len(self.session.active_workflows),
                "components": [
                    {
                        "name": c.name,
                        "status": c.status.value,
                        "duration": c.duration_seconds
                    }
                    for c in self.components
                ]
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to update status file: {e}")
    
    def _finalize_session(self, success: bool, early_termination: bool = False):
        """Finalize the MOEX startup session"""
        self.session.end_time = datetime.now()
        self.session.total_duration = (self.session.end_time - self.session.start_time).total_seconds()
        self.session.success = success
        self.session.components = self.components
        
        # Create final report
        report_file = os.path.join(
            self.project_root, 
            "reports", 
            f"moex-startup-{self.session_id}.json"
        )
        
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
            "agents_discovered": len(self.session.discovered_agents),
            "workflows_active": len(self.session.active_workflows),
            "report_file": report_file
        }
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(final_status, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to update final status: {e}")
        
        # Log completion
        status_emoji = "✅" if success else "❌"
        termination_note = " (early termination)" if early_termination else ""
        
        self.logger.info(f"{status_emoji} MOEX Intelligence Coordination startup sequence completed{termination_note}")
        self.logger.info(f"📊 Total duration: {self.session.total_duration:.2f} seconds")
        self.logger.info(f"🤖 Agents discovered: {len(self.session.discovered_agents)}")
        self.logger.info(f"🔄 Workflows active: {len(self.session.active_workflows)}")
        self.logger.info(f"📋 Report saved: {report_file}")
        
        if not success:
            failed_components = [c.name for c in self.components if c.status == MOEXComponentStatus.FAILED]
            self.logger.error(f"💥 Failed components: {failed_components}")

def main():
    """Main entry point for MOEX startup sequence"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MOEX Intelligence Coordination Startup Sequence")
    parser.add_argument("--project-root", default="/Users/studio/hardcard", 
                       help="Project root directory")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run startup sequence
    startup = MOEXStartupSequence(args.project_root)
    success = startup.run_startup_sequence()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()