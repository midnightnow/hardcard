#!/usr/bin/env python3
"""
Claude Engineer Startup Sequence - Advanced startup automation for Claude Engineer
that integrates with Claude Code, Gemini CLI, and MOEX coordination system.

This script implements the complete Claude Engineer startup sequence with self-improving
AI capabilities and tool generation.
"""

import os
import sys
import json
import time
import subprocess
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import signal
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ClaudeEngineerPhase(Enum):
    INITIALIZATION = "initialization"
    INSTALLATION = "installation"
    CONFIGURATION = "configuration"
    TOOL_SETUP = "tool_setup"
    INTEGRATION = "integration"
    COORDINATION = "coordination"
    COMPLETION = "completion"

class ClaudeEngineerComponentStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ClaudeEngineerStartupComponent:
    name: str
    description: str
    phase: ClaudeEngineerPhase
    status: ClaudeEngineerComponentStatus
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
class ClaudeEngineerStartupSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    components: List[ClaudeEngineerStartupComponent] = None
    claude_engineer_version: str = ""
    installation_path: str = ""
    available_tools: List[str] = None
    configuration: Dict[str, Any] = None
    success: bool = False
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.available_tools is None:
            self.available_tools = []
        if self.configuration is None:
            self.configuration = {}

class ClaudeEngineerStartupSequence:
    """Advanced Claude Engineer startup sequence manager"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.session_id = f"claude_engineer_startup_{int(time.time())}"
        self.session = ClaudeEngineerStartupSession(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Setup logging
        self.log_file = os.path.join(project_root, "logs", "claude-engineer-startup-sequence.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ClaudeEngineerStartup")
        
        # Component registry
        self.components = self._initialize_components()
        
        # Configuration paths
        self.claude_engineer_dir = os.path.join(project_root, ".claude-engineer")
        self.config_file = os.path.join(self.claude_engineer_dir, "config.json")
        self.status_file = os.path.join(project_root, "monitoring", "claude-engineer-startup-status.json")
        self.integration_file = os.path.join(project_root, ".claude", "claude-engineer-integration.json")
        
        # Installation path - will be set to system or local
        self.installation_path = ""
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        os.makedirs(self.claude_engineer_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.integration_file), exist_ok=True)
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_components(self) -> List[ClaudeEngineerStartupComponent]:
        """Initialize all Claude Engineer startup components"""
        return [
            # Phase 1: Initialization
            ClaudeEngineerStartupComponent(
                name="environment_check",
                description="Check environment and prerequisites for Claude Engineer",
                phase=ClaudeEngineerPhase.INITIALIZATION,
                status=ClaudeEngineerComponentStatus.PENDING
            ),
            ClaudeEngineerStartupComponent(
                name="api_key_validation",
                description="Validate Anthropic API key for Claude Engineer",
                phase=ClaudeEngineerPhase.INITIALIZATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["environment_check"]
            ),
            
            # Phase 2: Installation
            ClaudeEngineerStartupComponent(
                name="claude_engineer_installation",
                description="Install or update Claude Engineer",
                phase=ClaudeEngineerPhase.INSTALLATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["api_key_validation"]
            ),
            ClaudeEngineerStartupComponent(
                name="dependency_validation",
                description="Validate Claude Engineer dependencies",
                phase=ClaudeEngineerPhase.INSTALLATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["claude_engineer_installation"]
            ),
            
            # Phase 3: Configuration
            ClaudeEngineerStartupComponent(
                name="basic_configuration",
                description="Set up basic Claude Engineer configuration",
                phase=ClaudeEngineerPhase.CONFIGURATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["dependency_validation"]
            ),
            ClaudeEngineerStartupComponent(
                name="project_workspace_setup",
                description="Configure Claude Engineer workspace for project",
                phase=ClaudeEngineerPhase.CONFIGURATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["basic_configuration"]
            ),
            
            # Phase 4: Tool Setup
            ClaudeEngineerStartupComponent(
                name="core_tools_initialization",
                description="Initialize Claude Engineer core tools",
                phase=ClaudeEngineerPhase.TOOL_SETUP,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["project_workspace_setup"]
            ),
            ClaudeEngineerStartupComponent(
                name="custom_tools_setup",
                description="Set up project-specific custom tools",
                phase=ClaudeEngineerPhase.TOOL_SETUP,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["core_tools_initialization"]
            ),
            
            # Phase 5: Integration
            ClaudeEngineerStartupComponent(
                name="claude_code_integration",
                description="Set up integration with Claude Code",
                phase=ClaudeEngineerPhase.INTEGRATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["custom_tools_setup"]
            ),
            ClaudeEngineerStartupComponent(
                name="workflow_coordination",
                description="Configure workflow coordination with other agents",
                phase=ClaudeEngineerPhase.INTEGRATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["claude_code_integration"]
            ),
            
            # Phase 6: Coordination
            ClaudeEngineerStartupComponent(
                name="moex_registration",
                description="Register with MOEX coordination system",
                phase=ClaudeEngineerPhase.COORDINATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["workflow_coordination"]
            ),
            ClaudeEngineerStartupComponent(
                name="agent_specialization",
                description="Configure Claude Engineer agent specialization",
                phase=ClaudeEngineerPhase.COORDINATION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["moex_registration"]
            ),
            
            # Phase 7: Completion
            ClaudeEngineerStartupComponent(
                name="health_check",
                description="Perform comprehensive health check",
                phase=ClaudeEngineerPhase.COMPLETION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["agent_specialization"]
            ),
            ClaudeEngineerStartupComponent(
                name="session_finalization",
                description="Finalize Claude Engineer startup session",
                phase=ClaudeEngineerPhase.COMPLETION,
                status=ClaudeEngineerComponentStatus.PENDING,
                dependencies=["health_check"]
            )
        ]
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning(f"Received signal {signum}, shutting down Claude Engineer startup...")
        self._finalize_session(success=False, early_termination=True)
        sys.exit(1)
    
    def run_startup_sequence(self) -> bool:
        """Execute the complete Claude Engineer startup sequence"""
        self.logger.info(f"🛠️ Starting Claude Engineer startup sequence (Session: {self.session_id})")
        
        try:
            # Execute components in dependency order
            for component in self.components:
                if not self._can_execute_component(component):
                    self.logger.info(f"⏸️ Skipping {component.name} - dependencies not met")
                    component.status = ClaudeEngineerComponentStatus.SKIPPED
                    continue
                
                success = self._execute_component(component)
                if not success and component.name not in ["api_key_validation", "moex_registration", "agent_specialization"]:
                    # Allow some components to fail gracefully (API key validation is not critical)
                    self.logger.error(f"❌ Critical component {component.name} failed")
                    self._finalize_session(success=False)
                    return False
            
            # Complete startup
            self._finalize_session(success=True)
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Claude Engineer startup sequence failed with exception: {e}")
            self._finalize_session(success=False)
            return False
    
    def _can_execute_component(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Check if component dependencies are satisfied"""
        for dep_name in component.dependencies:
            dep_component = next((c for c in self.components if c.name == dep_name), None)
            if not dep_component or dep_component.status != ClaudeEngineerComponentStatus.COMPLETED:
                return False
        return True
    
    def _execute_component(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Execute a single startup component"""
        component.start_time = datetime.now()
        component.status = ClaudeEngineerComponentStatus.ACTIVE
        
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
            component.status = ClaudeEngineerComponentStatus.COMPLETED if success else ClaudeEngineerComponentStatus.FAILED
            
            status_emoji = "✅" if success else "❌"
            self.logger.info(f"{status_emoji} {component.description} completed in {component.duration_seconds:.2f}s")
            
            return success
            
        except Exception as e:
            component.end_time = datetime.now()
            component.duration_seconds = (component.end_time - component.start_time).total_seconds()
            component.error = str(e)
            component.status = ClaudeEngineerComponentStatus.FAILED
            
            self.logger.error(f"❌ {component.description} failed: {e}")
            return False
    
    # Component Handlers
    
    def _handle_environment_check(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Check environment and prerequisites for Claude Engineer"""
        try:
            issues = []
            
            # Check Python version
            if sys.version_info < (3, 8):
                issues.append("Python 3.8+ required")
            
            # Check if git is available
            try:
                subprocess.run(["git", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                issues.append("Git not available")
            
            # Check if we can install packages
            try:
                subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                issues.append("pip not available")
            
            # Check internet connectivity
            try:
                import urllib.request
                urllib.request.urlopen('https://github.com', timeout=10)
            except Exception:
                issues.append("Internet connectivity issues")
            
            if issues:
                component.error = "; ".join(issues)
                return False
            
            component.output = "Environment check passed"
            return True
            
        except Exception as e:
            component.error = f"Environment check failed: {e}"
            return False
    
    def _handle_api_key_validation(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Validate Anthropic API key for Claude Engineer"""
        try:
            # Check for API key in environment
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            
            if not api_key:
                # Check if API key exists in config files
                possible_configs = [
                    os.path.expanduser("~/.anthropic"),
                    os.path.join(self.project_root, ".env"),
                    os.path.join(self.claude_engineer_dir, "config.json")
                ]
                
                api_key_found = False
                for config_path in possible_configs:
                    if os.path.exists(config_path):
                        try:
                            if config_path.endswith('.json'):
                                with open(config_path, 'r') as f:
                                    config = json.load(f)
                                    if config.get("anthropic_api_key"):
                                        api_key_found = True
                                        break
                            else:
                                with open(config_path, 'r') as f:
                                    content = f.read()
                                    if "ANTHROPIC_API_KEY" in content:
                                        api_key_found = True
                                        break
                        except Exception:
                            continue
                
                if not api_key_found:
                    component.output = "Anthropic API key not found - Claude Engineer will run in offline mode"
                    self.logger.warning("Claude Engineer will run without API access - some features may be limited")
                    return True  # Allow to continue without API key
                else:
                    component.output = "API key found in configuration file"
            else:
                # Validate key format (basic check)
                if not api_key.startswith("sk-ant-"):
                    component.output = "Invalid Anthropic API key format - Claude Engineer will run in offline mode"
                    self.logger.warning("Invalid API key format - Claude Engineer will run with limited features")
                    return True  # Allow to continue with invalid key
                component.output = "API key validated from environment"
            
            return True
            
        except Exception as e:
            component.error = f"API key validation failed: {e}"
            return False
    
    def _handle_claude_engineer_installation(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Install or update Claude Engineer"""
        try:
            # Check if Claude Engineer is already installed
            try:
                result = subprocess.run(
                    ["python", "-c", "import claude_engineer; print(claude_engineer.__version__)"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.session.claude_engineer_version = result.stdout.strip()
                    component.output = f"Claude Engineer already installed: {self.session.claude_engineer_version}"
                    return True
            except subprocess.TimeoutExpired:
                pass
            
            # Install Claude Engineer from GitHub
            install_commands = [
                # Clone the repository
                ["git", "clone", "https://github.com/Doriandarko/claude-engineer.git", 
                 os.path.join(self.claude_engineer_dir, "claude-engineer")],
                # Install dependencies
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            ]
            
            for cmd in install_commands:
                try:
                    if "git clone" in " ".join(cmd):
                        # Handle git clone specially
                        if os.path.exists(os.path.join(self.claude_engineer_dir, "claude-engineer")):
                            # Repository already exists, pull updates instead
                            result = subprocess.run(
                                ["git", "pull"],
                                cwd=os.path.join(self.claude_engineer_dir, "claude-engineer"),
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                        else:
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    elif "requirements.txt" in " ".join(cmd):
                        # Install requirements from the cloned repository
                        requirements_path = os.path.join(self.claude_engineer_dir, "claude-engineer", "requirements.txt")
                        if os.path.exists(requirements_path):
                            cmd[-1] = requirements_path
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                        else:
                            # Skip if requirements.txt doesn't exist
                            continue
                    else:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if result.returncode != 0:
                        component.error = f"Installation command failed: {' '.join(cmd)}\nError: {result.stderr}"
                        return False
                        
                except subprocess.TimeoutExpired:
                    component.error = f"Installation command timed out: {' '.join(cmd)}"
                    return False
            
            # Set installation path
            self.installation_path = os.path.join(self.claude_engineer_dir, "claude-engineer")
            self.session.installation_path = self.installation_path
            
            # Check if installation was successful
            if os.path.exists(self.installation_path):
                component.output = f"Claude Engineer installed successfully at {self.installation_path}"
                return True
            else:
                component.error = "Installation completed but Claude Engineer not found"
                return False
            
        except Exception as e:
            component.error = f"Claude Engineer installation failed: {e}"
            return False
    
    def _handle_dependency_validation(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Validate Claude Engineer dependencies"""
        try:
            # Check for required Python packages
            required_packages = [
                "anthropic",
                "rich",
                "python-dotenv",
                "pyyaml"
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package.replace("-", "_"))
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                # Try to install missing packages
                install_cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
                try:
                    result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)
                    if result.returncode != 0:
                        component.error = f"Failed to install missing packages: {missing_packages}"
                        return False
                except subprocess.TimeoutExpired:
                    component.error = f"Package installation timed out for: {missing_packages}"
                    return False
            
            component.output = f"All dependencies validated (installed {len(missing_packages)} missing packages)"
            return True
            
        except Exception as e:
            component.error = f"Dependency validation failed: {e}"
            return False
    
    def _handle_basic_configuration(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Set up basic Claude Engineer configuration"""
        try:
            # Create basic configuration
            config = {
                "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
                "e2b_api_key": os.environ.get("E2B_API_KEY", ""),
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 4096,
                "temperature": 0.1,
                "project_root": self.project_root,
                "installation_path": self.installation_path,
                "tools": {
                    "core_tools_enabled": True,
                    "custom_tools_enabled": True,
                    "auto_tool_generation": True
                },
                "integration": {
                    "claude_code_enabled": True,
                    "gemini_cli_enabled": True,
                    "moex_coordination": True
                },
                "logging": {
                    "level": "INFO",
                    "file": os.path.join(self.project_root, "logs", "claude-engineer.log")
                }
            }
            
            # Save configuration
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.session.configuration = config
            component.output = "Basic configuration created"
            return True
            
        except Exception as e:
            component.error = f"Basic configuration failed: {e}"
            return False
    
    def _handle_project_workspace_setup(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Configure Claude Engineer workspace for project"""
        try:
            # Create workspace directories
            workspace_dirs = [
                "tools",
                "sessions", 
                "outputs",
                "templates",
                "workflows"
            ]
            
            created_dirs = []
            for directory in workspace_dirs:
                dir_path = os.path.join(self.claude_engineer_dir, directory)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    created_dirs.append(directory)
            
            # Create project-specific configuration
            project_config = {
                "project_name": "hardcard",
                "project_type": "veterinary_software",
                "workspace_directories": workspace_dirs,
                "agent_role": "self_improving_assistant",
                "specializations": [
                    "dynamic_tool_creation",
                    "code_analysis_and_optimization", 
                    "automated_testing",
                    "documentation_generation"
                ]
            }
            
            project_config_file = os.path.join(self.claude_engineer_dir, "project-config.json")
            with open(project_config_file, 'w') as f:
                json.dump(project_config, f, indent=2)
            
            component.output = f"Workspace configured with {len(workspace_dirs)} directories"
            if created_dirs:
                component.output += f" (created: {created_dirs})"
            
            return True
            
        except Exception as e:
            component.error = f"Project workspace setup failed: {e}"
            return False
    
    def _handle_core_tools_initialization(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Initialize Claude Engineer core tools"""
        try:
            # Define core tools that should be available
            core_tools = [
                "tool_creator",
                "file_manager", 
                "code_executor",
                "package_manager",
                "linting_tool"
            ]
            
            # Create tool registry
            tool_registry = {
                "core_tools": core_tools,
                "custom_tools": [],
                "auto_generated_tools": [],
                "last_updated": datetime.now().isoformat()
            }
            
            tools_registry_file = os.path.join(self.claude_engineer_dir, "tools", "registry.json")
            with open(tools_registry_file, 'w') as f:
                json.dump(tool_registry, f, indent=2)
            
            self.session.available_tools = core_tools
            component.output = f"Initialized {len(core_tools)} core tools"
            return True
            
        except Exception as e:
            component.error = f"Core tools initialization failed: {e}"
            return False
    
    def _handle_custom_tools_setup(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Set up project-specific custom tools"""
        try:
            # Define project-specific tools for veterinary software development
            custom_tools = [
                {
                    "name": "veterinary_compliance_checker",
                    "description": "Check code for veterinary software compliance",
                    "type": "analysis",
                    "enabled": True
                },
                {
                    "name": "medical_data_validator", 
                    "description": "Validate medical data structures and schemas",
                    "type": "validation",
                    "enabled": True
                },
                {
                    "name": "security_audit_tool",
                    "description": "Perform security audits specific to medical software",
                    "type": "security",
                    "enabled": True
                },
                {
                    "name": "performance_optimizer",
                    "description": "Optimize performance for real-time veterinary operations",
                    "type": "optimization", 
                    "enabled": True
                }
            ]
            
            custom_tools_file = os.path.join(self.claude_engineer_dir, "tools", "custom-tools.json")
            with open(custom_tools_file, 'w') as f:
                json.dump({"custom_tools": custom_tools}, f, indent=2)
            
            # Add to available tools
            self.session.available_tools.extend([tool["name"] for tool in custom_tools])
            
            component.output = f"Set up {len(custom_tools)} custom tools"
            return True
            
        except Exception as e:
            component.error = f"Custom tools setup failed: {e}"
            return False
    
    def _handle_claude_code_integration(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Set up integration with Claude Code"""
        try:
            # Create integration configuration
            integration_config = {
                "integration": {
                    "enabled": True,
                    "claude_engineer_config": self.config_file,
                    "coordination_mode": "collaborative",
                    "task_distribution": {
                        "self_improving_tasks": "claude_engineer",
                        "implementation_tasks": "claude_code",
                        "tool_generation": "claude_engineer",
                        "git_operations": "claude_code",
                        "analysis_and_optimization": "claude_engineer"
                    }
                },
                "workflows": {
                    "intelligent_development": [
                        {"agent": "claude_code", "task": "explore_codebase"},
                        {"agent": "claude_engineer", "task": "analyze_and_generate_tools"},
                        {"agent": "claude_code", "task": "implement_features"},
                        {"agent": "claude_engineer", "task": "optimize_and_improve"},
                        {"agent": "claude_code", "task": "test_and_commit"}
                    ],
                    "continuous_improvement": [
                        {"agent": "claude_engineer", "task": "monitor_development_patterns"},
                        {"agent": "claude_engineer", "task": "generate_productivity_tools"},
                        {"agent": "claude_code", "task": "integrate_new_tools"},
                        {"agent": "claude_engineer", "task": "measure_improvement"}
                    ]
                },
                "shared_workspace": {
                    "tools_directory": os.path.join(self.claude_engineer_dir, "tools"),
                    "outputs_directory": os.path.join(self.claude_engineer_dir, "outputs"),
                    "communication_file": os.path.join(self.project_root, "moex-workspace", "claude-engineer-messages.json")
                }
            }
            
            with open(self.integration_file, 'w') as f:
                json.dump(integration_config, f, indent=2)
            
            component.output = "Claude Code integration configured"
            return True
            
        except Exception as e:
            component.error = f"Claude Code integration failed: {e}"
            return False
    
    def _handle_workflow_coordination(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Configure workflow coordination with other agents"""
        try:
            # Create workflow coordination configuration
            coordination_config = {
                "agent_roles": {
                    "claude_engineer": {
                        "primary_responsibilities": [
                            "dynamic_tool_creation",
                            "code_analysis_and_optimization",
                            "automated_improvement",
                            "pattern_recognition"
                        ],
                        "coordination_capabilities": [
                            "tool_sharing",
                            "workflow_enhancement",
                            "adaptive_assistance"
                        ]
                    }
                },
                "interaction_protocols": {
                    "tool_sharing": {
                        "auto_share_new_tools": True,
                        "tool_validation_required": True,
                        "sharing_directory": os.path.join(self.claude_engineer_dir, "tools", "shared")
                    },
                    "workflow_coordination": {
                        "status_updates_interval": 300,
                        "coordination_queue": os.path.join(self.project_root, "moex-workspace", "coordination-queue.json")
                    }
                }
            }
            
            coordination_file = os.path.join(self.claude_engineer_dir, "coordination.json")
            with open(coordination_file, 'w') as f:
                json.dump(coordination_config, f, indent=2)
            
            # Create shared tools directory
            shared_tools_dir = coordination_config["interaction_protocols"]["tool_sharing"]["sharing_directory"]
            os.makedirs(shared_tools_dir, exist_ok=True)
            
            component.output = "Workflow coordination configured"
            return True
            
        except Exception as e:
            component.error = f"Workflow coordination failed: {e}"
            return False
    
    def _handle_moex_registration(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Register with MOEX coordination system"""
        try:
            # Update MOEX workspace with Claude Engineer status
            moex_workspace = os.path.join(self.project_root, "moex-workspace")
            if os.path.exists(moex_workspace):
                status_file = os.path.join(moex_workspace, "claude-engineer-status.json")
                
                claude_engineer_status = {
                    "status": "active",
                    "timestamp": datetime.now().isoformat(),
                    "version": self.session.claude_engineer_version,
                    "installation_path": self.installation_path,
                    "capabilities": [
                        "dynamic_tool_creation",
                        "self_improving_assistance", 
                        "code_analysis_and_optimization",
                        "automated_testing",
                        "pattern_recognition"
                    ],
                    "available_tools": self.session.available_tools,
                    "session_id": self.session_id,
                    "specialization": "self_improving_ai_assistant"
                }
                
                with open(status_file, 'w') as f:
                    json.dump(claude_engineer_status, f, indent=2)
                
                component.output = "Registered with MOEX coordination system"
            else:
                component.output = "MOEX workspace not found - skipping registration"
            
            return True
            
        except Exception as e:
            component.error = f"MOEX registration failed: {e}"
            return True  # Non-critical
    
    def _handle_agent_specialization(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Configure Claude Engineer agent specialization"""
        try:
            # Define specialization configuration
            specialization = {
                "agent_type": "self_improving_ai_assistant",
                "primary_focus": "dynamic_capability_expansion",
                "specialized_domains": [
                    "veterinary_software_development",
                    "medical_data_processing",
                    "real_time_system_optimization",
                    "compliance_automation"
                ],
                "adaptive_capabilities": {
                    "tool_generation": {
                        "enabled": True,
                        "auto_generate_on_need": True,
                        "generation_threshold": "high_confidence"
                    },
                    "workflow_improvement": {
                        "enabled": True,
                        "pattern_learning": True,
                        "efficiency_optimization": True
                    },
                    "knowledge_expansion": {
                        "enabled": True,
                        "domain_specific_learning": True,
                        "best_practices_integration": True
                    }
                },
                "coordination_preferences": {
                    "collaboration_style": "proactive_assistance",
                    "communication_frequency": "as_needed",
                    "tool_sharing_willingness": "high"
                }
            }
            
            specialization_file = os.path.join(self.claude_engineer_dir, "specialization.json")
            with open(specialization_file, 'w') as f:
                json.dump(specialization, f, indent=2)
            
            component.output = "Agent specialization configured"
            return True
            
        except Exception as e:
            component.error = f"Agent specialization failed: {e}"
            return False
    
    def _handle_health_check(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Perform comprehensive health check"""
        try:
            health_checks = []
            
            # Check installation
            if os.path.exists(self.installation_path):
                health_checks.append("✅ Installation: OK")
            else:
                health_checks.append("❌ Installation: Missing")
            
            # Check configuration
            if os.path.exists(self.config_file):
                health_checks.append("✅ Configuration: OK") 
            else:
                health_checks.append("❌ Configuration: Missing")
            
            # Check tools registry
            tools_registry_file = os.path.join(self.claude_engineer_dir, "tools", "registry.json")
            if os.path.exists(tools_registry_file):
                health_checks.append("✅ Tools Registry: OK")
            else:
                health_checks.append("❌ Tools Registry: Missing")
            
            # Check integration
            if os.path.exists(self.integration_file):
                health_checks.append("✅ Integration: OK")
            else:
                health_checks.append("❌ Integration: Missing")
            
            # Check API key
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key and api_key.startswith("sk-ant-"):
                health_checks.append("✅ API Key: OK")
            else:
                health_checks.append("❌ API Key: Invalid")
            
            component.output = "\n".join(health_checks)
            
            # Return success if most checks pass
            success_count = len([check for check in health_checks if check.startswith("✅")])
            total_checks = len(health_checks)
            
            return success_count >= (total_checks * 0.8)  # 80% success rate
            
        except Exception as e:
            component.error = f"Health check failed: {e}"
            return False
    
    def _handle_session_finalization(self, component: ClaudeEngineerStartupComponent) -> bool:
        """Finalize Claude Engineer startup session"""
        try:
            # Calculate session metrics
            completed_components = [c for c in self.components if c.status == ClaudeEngineerComponentStatus.COMPLETED]
            failed_components = [c for c in self.components if c.status == ClaudeEngineerComponentStatus.FAILED]
            
            success_rate = len(completed_components) / len(self.components) * 100
            
            component.output = f"Claude Engineer session completed: {len(completed_components)}/{len(self.components)} components successful ({success_rate:.1f}%)"
            
            if failed_components:
                component.output += f" - Failed: {[c.name for c in failed_components]}"
            
            return len(failed_components) == 0
            
        except Exception as e:
            component.error = f"Session finalization failed: {e}"
            return False
    
    def _update_status(self):
        """Update Claude Engineer startup status file"""
        try:
            status_data = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "phase": "in_progress",
                "installation_path": self.installation_path,
                "available_tools": len(self.session.available_tools),
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
        """Finalize the Claude Engineer startup session"""
        self.session.end_time = datetime.now()
        self.session.total_duration = (self.session.end_time - self.session.start_time).total_seconds()
        self.session.success = success
        self.session.components = self.components
        
        # Create final report
        report_file = os.path.join(
            self.project_root, 
            "reports", 
            f"claude-engineer-startup-{self.session_id}.json"
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
            "installation_path": self.installation_path,
            "available_tools": self.session.available_tools,
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
        
        self.logger.info(f"{status_emoji} Claude Engineer startup sequence completed{termination_note}")
        self.logger.info(f"📊 Total duration: {self.session.total_duration:.2f} seconds")
        self.logger.info(f"📋 Report saved: {report_file}")
        
        if not success:
            failed_components = [c.name for c in self.components if c.status == ClaudeEngineerComponentStatus.FAILED]
            self.logger.error(f"💥 Failed components: {failed_components}")

def main():
    """Main entry point for Claude Engineer startup sequence"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Engineer Startup Sequence")
    parser.add_argument("--project-root", default="/Users/studio/hardcard", 
                       help="Project root directory")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run startup sequence
    startup = ClaudeEngineerStartupSequence(args.project_root)
    success = startup.run_startup_sequence()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()