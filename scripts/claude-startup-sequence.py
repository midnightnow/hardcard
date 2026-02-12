#!/usr/bin/env python3
"""
Claude Code Startup Sequence - Advanced startup automation for Claude Code
that integrates with Gemini CLI and MOEX coordination system.

This script implements the complete Claude Code startup sequence with best practices.
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

class StartupPhase(Enum):
    INITIALIZATION = "initialization"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    COMPLETION = "completion"

class ComponentStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StartupComponent:
    name: str
    description: str
    phase: StartupPhase
    status: ComponentStatus
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
class StartupSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    components: List[StartupComponent] = None
    environment: Dict[str, Any] = None
    success: bool = False
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.environment is None:
            self.environment = {}

class ClaudeStartupSequence:
    """Advanced Claude Code startup sequence manager"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.session_id = f"claude_startup_{int(time.time())}"
        self.session = StartupSession(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Setup logging
        self.log_file = os.path.join(project_root, "logs", "claude-startup-sequence.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ClaudeStartup")
        
        # Component registry
        self.components = self._initialize_components()
        
        # Status tracking
        self.status_file = os.path.join(project_root, "monitoring", "claude-startup-status.json")
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_components(self) -> List[StartupComponent]:
        """Initialize all startup components in proper order"""
        return [
            # Phase 1: Initialization
            StartupComponent(
                name="environment_check",
                description="Validate environment and prerequisites",
                phase=StartupPhase.INITIALIZATION,
                status=ComponentStatus.PENDING
            ),
            StartupComponent(
                name="directory_structure",
                description="Ensure required directory structure exists",
                phase=StartupPhase.INITIALIZATION,
                status=ComponentStatus.PENDING,
                dependencies=["environment_check"]
            ),
            
            # Phase 2: Validation
            StartupComponent(
                name="claude_config_validation",
                description="Validate Claude Code configuration",
                phase=StartupPhase.VALIDATION,
                status=ComponentStatus.PENDING,
                dependencies=["directory_structure"]
            ),
            StartupComponent(
                name="git_worktree_validation",
                description="Validate git worktree setup",
                phase=StartupPhase.VALIDATION,
                status=ComponentStatus.PENDING,
                dependencies=["claude_config_validation"]
            ),
            
            # Phase 3: Configuration
            StartupComponent(
                name="tool_permissions",
                description="Configure tool permissions and allowlists",
                phase=StartupPhase.CONFIGURATION,
                status=ComponentStatus.PENDING,
                dependencies=["git_worktree_validation"]
            ),
            StartupComponent(
                name="mcp_servers",
                description="Initialize MCP servers",
                phase=StartupPhase.CONFIGURATION,
                status=ComponentStatus.PENDING,
                dependencies=["tool_permissions"]
            ),
            StartupComponent(
                name="custom_commands",
                description="Validate custom slash commands",
                phase=StartupPhase.CONFIGURATION,
                status=ComponentStatus.PENDING,
                dependencies=["mcp_servers"]
            ),
            
            # Phase 4: Integration
            StartupComponent(
                name="gemini_integration",
                description="Initialize Gemini CLI integration",
                phase=StartupPhase.INTEGRATION,
                status=ComponentStatus.PENDING,
                dependencies=["custom_commands"]
            ),
            StartupComponent(
                name="moex_coordination",
                description="Initialize MOEX coordination system",
                phase=StartupPhase.INTEGRATION,
                status=ComponentStatus.PENDING,
                dependencies=["gemini_integration"]
            ),
            
            # Phase 5: Monitoring
            StartupComponent(
                name="health_monitoring",
                description="Start health monitoring systems",
                phase=StartupPhase.MONITORING,
                status=ComponentStatus.PENDING,
                dependencies=["moex_coordination"]
            ),
            StartupComponent(
                name="quality_gates",
                description="Activate quality gates and enforcement",
                phase=StartupPhase.MONITORING,
                status=ComponentStatus.PENDING,
                dependencies=["health_monitoring"]
            ),
            
            # Phase 6: Completion
            StartupComponent(
                name="best_practices_validation",
                description="Final best practices validation",
                phase=StartupPhase.COMPLETION,
                status=ComponentStatus.PENDING,
                dependencies=["quality_gates"]
            ),
            StartupComponent(
                name="session_finalization",
                description="Finalize startup session and create report",
                phase=StartupPhase.COMPLETION,
                status=ComponentStatus.PENDING,
                dependencies=["best_practices_validation"]
            )
        ]
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning(f"Received signal {signum}, shutting down gracefully...")
        self._finalize_session(success=False, early_termination=True)
        sys.exit(1)
    
    def run_startup_sequence(self) -> bool:
        """Execute the complete startup sequence"""
        self.logger.info(f"🚀 Starting Claude Code startup sequence (Session: {self.session_id})")
        
        try:
            # Execute components in dependency order
            for component in self.components:
                if not self._can_execute_component(component):
                    self.logger.info(f"⏸️ Skipping {component.name} - dependencies not met")
                    component.status = ComponentStatus.SKIPPED
                    continue
                
                success = self._execute_component(component)
                if not success and component.name not in ["gemini_integration", "moex_coordination"]:
                    # Allow non-critical components to fail
                    self.logger.error(f"❌ Critical component {component.name} failed")
                    self._finalize_session(success=False)
                    return False
            
            # Complete startup
            self._finalize_session(success=True)
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Startup sequence failed with exception: {e}")
            self._finalize_session(success=False)
            return False
    
    def _can_execute_component(self, component: StartupComponent) -> bool:
        """Check if component dependencies are satisfied"""
        for dep_name in component.dependencies:
            dep_component = next((c for c in self.components if c.name == dep_name), None)
            if not dep_component or dep_component.status != ComponentStatus.COMPLETED:
                return False
        return True
    
    def _execute_component(self, component: StartupComponent) -> bool:
        """Execute a single startup component"""
        component.start_time = datetime.now()
        component.status = ComponentStatus.ACTIVE
        
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
            component.status = ComponentStatus.COMPLETED if success else ComponentStatus.FAILED
            
            status_emoji = "✅" if success else "❌"
            self.logger.info(f"{status_emoji} {component.description} completed in {component.duration_seconds:.2f}s")
            
            return success
            
        except Exception as e:
            component.end_time = datetime.now()
            component.duration_seconds = (component.end_time - component.start_time).total_seconds()
            component.error = str(e)
            component.status = ComponentStatus.FAILED
            
            self.logger.error(f"❌ {component.description} failed: {e}")
            return False
    
    # Component Handlers
    
    def _handle_environment_check(self, component: StartupComponent) -> bool:
        """Validate environment and prerequisites"""
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                component.error = "Python 3.8+ required"
                return False
            
            # Check project root
            if not os.path.exists(self.project_root):
                component.error = f"Project root not found: {self.project_root}"
                return False
            
            # Check if in git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"], 
                cwd=self.project_root, 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                component.error = "Not in a git repository"
                return False
            
            # Check for Claude Code
            if not os.path.exists(os.path.join(self.project_root, "CLAUDE.md")):
                component.error = "CLAUDE.md not found"
                return False
            
            component.output = "Environment validation passed"
            return True
            
        except Exception as e:
            component.error = f"Environment check failed: {e}"
            return False
    
    def _handle_directory_structure(self, component: StartupComponent) -> bool:
        """Ensure required directory structure exists"""
        try:
            required_dirs = [
                "logs",
                "monitoring", 
                "reports",
                "scripts",
                ".claude",
                ".claude/commands",
                "moex-workspace"
            ]
            
            created_dirs = []
            for dir_path in required_dirs:
                full_path = os.path.join(self.project_root, dir_path)
                if not os.path.exists(full_path):
                    os.makedirs(full_path, exist_ok=True)
                    created_dirs.append(dir_path)
            
            component.output = f"Created directories: {created_dirs}" if created_dirs else "All directories exist"
            return True
            
        except Exception as e:
            component.error = f"Directory creation failed: {e}"
            return False
    
    def _handle_claude_config_validation(self, component: StartupComponent) -> bool:
        """Validate Claude Code configuration"""
        try:
            issues = []
            
            # Check CLAUDE.md
            claude_md = os.path.join(self.project_root, "CLAUDE.md")
            if not os.path.exists(claude_md):
                issues.append("CLAUDE.md missing")
            else:
                with open(claude_md, 'r') as f:
                    content = f.read()
                    required_sections = [
                        "Essential Workflow",
                        "Tool Configuration", 
                        "Custom Slash Commands",
                        "MCP Integration"
                    ]
                    for section in required_sections:
                        if section not in content:
                            issues.append(f"Missing section: {section}")
            
            # Check settings.json
            settings_file = os.path.join(self.project_root, ".claude", "settings.json")
            if os.path.exists(settings_file):
                try:
                    with open(settings_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    issues.append("Invalid settings.json")
            
            if issues:
                component.error = "; ".join(issues)
                return False
            
            component.output = "Claude configuration validated"
            return True
            
        except Exception as e:
            component.error = f"Configuration validation failed: {e}"
            return False
    
    def _handle_git_worktree_validation(self, component: StartupComponent) -> bool:
        """Validate git worktree setup"""
        try:
            result = subprocess.run(
                ["git", "worktree", "list"], 
                cwd=self.project_root, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                component.error = "Git worktree command failed"
                return False
            
            worktrees = result.stdout.strip().split('\n')
            component.output = f"Found {len(worktrees)} worktrees"
            return True
            
        except Exception as e:
            component.error = f"Worktree validation failed: {e}"
            return False
    
    def _handle_tool_permissions(self, component: StartupComponent) -> bool:
        """Configure tool permissions and allowlists"""
        try:
            settings_file = os.path.join(self.project_root, ".claude", "settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                allowed_tools = settings.get("allowedTools", [])
                component.output = f"Configured {len(allowed_tools)} allowed tools"
            else:
                component.output = "No settings.json found - using defaults"
            
            return True
            
        except Exception as e:
            component.error = f"Tool permissions setup failed: {e}"
            return False
    
    def _handle_mcp_servers(self, component: StartupComponent) -> bool:
        """Initialize MCP servers"""
        try:
            mcp_file = os.path.join(self.project_root, ".mcp.json")
            if os.path.exists(mcp_file):
                with open(mcp_file, 'r') as f:
                    mcp_config = json.load(f)
                
                servers = mcp_config.get("mcpServers", {})
                component.output = f"Configured {len(servers)} MCP servers"
            else:
                component.output = "No MCP configuration found"
            
            return True
            
        except Exception as e:
            component.error = f"MCP initialization failed: {e}"
            return False
    
    def _handle_custom_commands(self, component: StartupComponent) -> bool:
        """Validate custom slash commands"""
        try:
            commands_dir = os.path.join(self.project_root, ".claude", "commands")
            if os.path.exists(commands_dir):
                commands = [f for f in os.listdir(commands_dir) if f.endswith('.md')]
                component.output = f"Found {len(commands)} custom commands"
            else:
                component.output = "No custom commands directory"
            
            return True
            
        except Exception as e:
            component.error = f"Custom commands validation failed: {e}"
            return False
    
    def _handle_gemini_integration(self, component: StartupComponent) -> bool:
        """Initialize Gemini CLI integration"""
        try:
            # Check if Gemini CLI is available
            result = subprocess.run(
                ["gemini", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                component.output = f"Gemini CLI available: {version}"
                
                # Check configuration
                gemini_config = os.path.join(self.project_root, "gemini.yaml")
                if os.path.exists(gemini_config):
                    component.output += " - Configuration found"
                
                return True
            else:
                component.output = "Gemini CLI not available - skipping"
                return True  # Non-critical
                
        except subprocess.TimeoutExpired:
            component.output = "Gemini CLI check timed out - skipping"
            return True  # Non-critical
        except Exception as e:
            component.error = f"Gemini integration failed: {e}"
            return True  # Non-critical
    
    def _handle_moex_coordination(self, component: StartupComponent) -> bool:
        """Initialize MOEX coordination system"""
        try:
            moex_script = os.path.join(self.project_root, "scripts", "moex-coordinator.sh")
            if os.path.exists(moex_script):
                result = subprocess.run(
                    [moex_script, "init"], 
                    cwd=self.project_root,
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                
                component.output = f"MOEX coordinator: {result.stdout.strip()}"
                return True
            else:
                component.output = "MOEX coordinator not found - skipping"
                return True  # Non-critical
                
        except subprocess.TimeoutExpired:
            component.output = "MOEX initialization timed out - skipping"
            return True  # Non-critical
        except Exception as e:
            component.error = f"MOEX coordination failed: {e}"
            return True  # Non-critical
    
    def _handle_health_monitoring(self, component: StartupComponent) -> bool:
        """Start health monitoring systems"""
        try:
            monitoring_scripts = [
                "comprehensive-health-dashboard.py",
                "automated-stability-monitor.py"
            ]
            
            available_scripts = []
            for script in monitoring_scripts:
                script_path = os.path.join(self.project_root, "scripts", script)
                if os.path.exists(script_path):
                    available_scripts.append(script)
            
            component.output = f"Available monitoring: {available_scripts}"
            return True
            
        except Exception as e:
            component.error = f"Health monitoring setup failed: {e}"
            return False
    
    def _handle_quality_gates(self, component: StartupComponent) -> bool:
        """Activate quality gates and enforcement"""
        try:
            hooks_dir = os.path.join(self.project_root, ".git", "hooks")
            active_hooks = []
            
            if os.path.exists(hooks_dir):
                for hook in ["pre-commit", "pre-push", "commit-msg"]:
                    hook_path = os.path.join(hooks_dir, hook)
                    if os.path.exists(hook_path) and os.access(hook_path, os.X_OK):
                        active_hooks.append(hook)
            
            component.output = f"Active git hooks: {active_hooks}"
            return True
            
        except Exception as e:
            component.error = f"Quality gates setup failed: {e}"
            return False
    
    def _handle_best_practices_validation(self, component: StartupComponent) -> bool:
        """Final best practices validation"""
        try:
            validator_script = os.path.join(self.project_root, "scripts", "best-practices-enforcer.sh")
            if os.path.exists(validator_script):
                result = subprocess.run(
                    [validator_script], 
                    cwd=self.project_root,
                    capture_output=True, 
                    text=True,
                    timeout=60
                )
                
                # Extract score from output if available
                output_lines = result.stdout.split('\n')
                score_line = next((line for line in output_lines if "Best Practices Score" in line), "")
                component.output = score_line or "Best practices validation completed"
                
                return result.returncode == 0
            else:
                component.output = "Best practices validator not found"
                return True
                
        except subprocess.TimeoutExpired:
            component.output = "Best practices validation timed out"
            return False
        except Exception as e:
            component.error = f"Best practices validation failed: {e}"
            return False
    
    def _handle_session_finalization(self, component: StartupComponent) -> bool:
        """Finalize startup session and create report"""
        try:
            # Calculate session metrics
            completed_components = [c for c in self.components if c.status == ComponentStatus.COMPLETED]
            failed_components = [c for c in self.components if c.status == ComponentStatus.FAILED]
            
            success_rate = len(completed_components) / len(self.components) * 100
            
            component.output = f"Session completed: {len(completed_components)}/{len(self.components)} components successful ({success_rate:.1f}%)"
            
            if failed_components:
                component.output += f" - Failed: {[c.name for c in failed_components]}"
            
            return len(failed_components) == 0
            
        except Exception as e:
            component.error = f"Session finalization failed: {e}"
            return False
    
    def _update_status(self):
        """Update startup status file"""
        try:
            status_data = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "phase": "in_progress",
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
        """Finalize the startup session"""
        self.session.end_time = datetime.now()
        self.session.total_duration = (self.session.end_time - self.session.start_time).total_seconds()
        self.session.success = success
        self.session.components = self.components
        
        # Create final report
        report_file = os.path.join(
            self.project_root, 
            "reports", 
            f"claude-startup-{self.session_id}.json"
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
        
        self.logger.info(f"{status_emoji} Claude Code startup sequence completed{termination_note}")
        self.logger.info(f"📊 Total duration: {self.session.total_duration:.2f} seconds")
        self.logger.info(f"📋 Report saved: {report_file}")
        
        if not success:
            failed_components = [c.name for c in self.components if c.status == ComponentStatus.FAILED]
            self.logger.error(f"💥 Failed components: {failed_components}")

def main():
    """Main entry point for Claude startup sequence"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Startup Sequence")
    parser.add_argument("--project-root", default="/Users/studio/hardcard", 
                       help="Project root directory")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run startup sequence
    startup = ClaudeStartupSequence(args.project_root)
    success = startup.run_startup_sequence()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()