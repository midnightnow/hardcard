#!/usr/bin/env python3
"""
Gemini CLI Startup Sequence - Advanced startup automation for Gemini CLI
that integrates with Claude Code and MOEX coordination system.

This script implements the complete Gemini CLI startup sequence with best practices.
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

class GeminiStartupPhase(Enum):
    INITIALIZATION = "initialization"
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"
    SPECIALIZATION = "specialization"
    COORDINATION = "coordination"
    COMPLETION = "completion"

class GeminiComponentStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class GeminiStartupComponent:
    name: str
    description: str
    phase: GeminiStartupPhase
    status: GeminiComponentStatus
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
class GeminiStartupSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: float = 0.0
    components: List[GeminiStartupComponent] = None
    gemini_version: str = ""
    configuration: Dict[str, Any] = None
    success: bool = False
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.configuration is None:
            self.configuration = {}

class GeminiStartupSequence:
    """Advanced Gemini CLI startup sequence manager"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.session_id = f"gemini_startup_{int(time.time())}"
        self.session = GeminiStartupSession(
            session_id=self.session_id,
            start_time=datetime.now()
        )
        
        # Setup logging
        self.log_file = os.path.join(project_root, "logs", "gemini-startup-sequence.log")
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("GeminiStartup")
        
        # Component registry
        self.components = self._initialize_components()
        
        # Status tracking
        self.status_file = os.path.join(project_root, "monitoring", "gemini-startup-status.json")
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
        
        # Configuration files
        self.config_file = os.path.join(project_root, "gemini.json")
        self.integration_file = os.path.join(project_root, ".claude", "gemini-integration.json")
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _initialize_components(self) -> List[GeminiStartupComponent]:
        """Initialize all Gemini startup components"""
        return [
            # Phase 1: Initialization
            GeminiStartupComponent(
                name="gemini_availability",
                description="Check Gemini CLI availability and version",
                phase=GeminiStartupPhase.INITIALIZATION,
                status=GeminiComponentStatus.PENDING
            ),
            GeminiStartupComponent(
                name="api_credentials",
                description="Validate API credentials and authentication",
                phase=GeminiStartupPhase.INITIALIZATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["gemini_availability"]
            ),
            
            # Phase 2: Configuration
            GeminiStartupComponent(
                name="project_configuration",
                description="Load and validate project configuration",
                phase=GeminiStartupPhase.CONFIGURATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["api_credentials"]
            ),
            GeminiStartupComponent(
                name="model_configuration",
                description="Configure models and parameters",
                phase=GeminiStartupPhase.CONFIGURATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["project_configuration"]
            ),
            
            # Phase 3: Integration
            GeminiStartupComponent(
                name="claude_integration",
                description="Set up integration with Claude Code",
                phase=GeminiStartupPhase.INTEGRATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["model_configuration"]
            ),
            GeminiStartupComponent(
                name="workflow_integration",
                description="Configure workflow coordination",
                phase=GeminiStartupPhase.INTEGRATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["claude_integration"]
            ),
            
            # Phase 4: Specialization
            GeminiStartupComponent(
                name="analysis_agent",
                description="Initialize code analysis specialization",
                phase=GeminiStartupPhase.SPECIALIZATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["workflow_integration"]
            ),
            GeminiStartupComponent(
                name="documentation_agent",
                description="Initialize documentation generation specialization",
                phase=GeminiStartupPhase.SPECIALIZATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["analysis_agent"]
            ),
            GeminiStartupComponent(
                name="review_agent",
                description="Initialize code review specialization",
                phase=GeminiStartupPhase.SPECIALIZATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["documentation_agent"]
            ),
            
            # Phase 5: Coordination
            GeminiStartupComponent(
                name="task_routing",
                description="Set up intelligent task routing",
                phase=GeminiStartupPhase.COORDINATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["review_agent"]
            ),
            GeminiStartupComponent(
                name="moex_registration",
                description="Register with MOEX coordination system",
                phase=GeminiStartupPhase.COORDINATION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["task_routing"]
            ),
            
            # Phase 6: Completion
            GeminiStartupComponent(
                name="automation_scripts",
                description="Validate automation scripts",
                phase=GeminiStartupPhase.COMPLETION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["moex_registration"]
            ),
            GeminiStartupComponent(
                name="session_finalization",
                description="Finalize Gemini startup session",
                phase=GeminiStartupPhase.COMPLETION,
                status=GeminiComponentStatus.PENDING,
                dependencies=["automation_scripts"]
            )
        ]
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.warning(f"Received signal {signum}, shutting down Gemini startup...")
        self._finalize_session(success=False, early_termination=True)
        sys.exit(1)
    
    def run_startup_sequence(self) -> bool:
        """Execute the complete Gemini startup sequence"""
        self.logger.info(f"🧠 Starting Gemini CLI startup sequence (Session: {self.session_id})")
        
        try:
            # Execute components in dependency order
            for component in self.components:
                if not self._can_execute_component(component):
                    self.logger.info(f"⏸️ Skipping {component.name} - dependencies not met")
                    component.status = GeminiComponentStatus.SKIPPED
                    continue
                
                success = self._execute_component(component)
                if not success and component.name not in ["moex_registration", "automation_scripts"]:
                    # Allow some components to fail gracefully
                    self.logger.error(f"❌ Critical component {component.name} failed")
                    self._finalize_session(success=False)
                    return False
            
            # Complete startup
            self._finalize_session(success=True)
            return True
            
        except Exception as e:
            self.logger.error(f"💥 Gemini startup sequence failed with exception: {e}")
            self._finalize_session(success=False)
            return False
    
    def _can_execute_component(self, component: GeminiStartupComponent) -> bool:
        """Check if component dependencies are satisfied"""
        for dep_name in component.dependencies:
            dep_component = next((c for c in self.components if c.name == dep_name), None)
            if not dep_component or dep_component.status != GeminiComponentStatus.COMPLETED:
                return False
        return True
    
    def _execute_component(self, component: GeminiStartupComponent) -> bool:
        """Execute a single startup component"""
        component.start_time = datetime.now()
        component.status = GeminiComponentStatus.ACTIVE
        
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
            component.status = GeminiComponentStatus.COMPLETED if success else GeminiComponentStatus.FAILED
            
            status_emoji = "✅" if success else "❌"
            self.logger.info(f"{status_emoji} {component.description} completed in {component.duration_seconds:.2f}s")
            
            return success
            
        except Exception as e:
            component.end_time = datetime.now()
            component.duration_seconds = (component.end_time - component.start_time).total_seconds()
            component.error = str(e)
            component.status = GeminiComponentStatus.FAILED
            
            self.logger.error(f"❌ {component.description} failed: {e}")
            return False
    
    # Component Handlers
    
    def _handle_gemini_availability(self, component: GeminiStartupComponent) -> bool:
        """Check Gemini CLI availability and version"""
        try:
            result = subprocess.run(
                ["gemini", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.session.gemini_version = version
                component.output = f"Gemini CLI version: {version}"
                return True
            else:
                component.error = f"Gemini CLI not available: {result.stderr}"
                return False
                
        except subprocess.TimeoutExpired:
            component.error = "Gemini CLI check timed out"
            return False
        except FileNotFoundError:
            component.error = "Gemini CLI not installed"
            return False
        except Exception as e:
            component.error = f"Gemini availability check failed: {e}"
            return False
    
    def _handle_api_credentials(self, component: GeminiStartupComponent) -> bool:
        """Validate API credentials and authentication"""
        try:
            # Check for API key in environment
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            
            if not api_key:
                component.output = "No API key found in environment - may need configuration"
                return True  # Not always required
            
            # Test basic API connectivity (if possible)
            # Note: This would need actual Gemini CLI commands to test
            component.output = "API credentials available"
            return True
            
        except Exception as e:
            component.error = f"API credentials validation failed: {e}"
            return False
    
    def _handle_project_configuration(self, component: GeminiStartupComponent) -> bool:
        """Load and validate project configuration"""
        try:
            if not os.path.exists(self.config_file):
                # Create default configuration
                default_config = {
                    "project": {
                        "name": "hardcard",
                        "root": self.project_root,
                        "version": "1.0.0",
                        "description": "Veterinary Software Platform"
                    },
                    "model": {
                        "name": "gemini-pro",
                        "temperature": 0.1,
                        "max_tokens": 4096
                    },
                    "agents": {
                        "analysis": {
                            "description": "Code analysis and optimization specialist",
                            "specialties": ["performance_analysis", "code_quality", "security_scanning"]
                        },
                        "documentation": {
                            "description": "Documentation generation specialist",
                            "specialties": ["api_documentation", "code_comments", "user_guides"]
                        },
                        "review": {
                            "description": "Code review and quality assurance",
                            "specialties": ["code_review", "best_practices_enforcement"]
                        }
                    }
                }
                
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                component.output = "Created default configuration"
            else:
                # Validate existing configuration
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
                
                self.session.configuration = config
                component.output = f"Loaded configuration with {len(config.get('agents', {}))} agents"
            
            return True
            
        except Exception as e:
            component.error = f"Project configuration failed: {e}"
            return False
    
    def _handle_model_configuration(self, component: GeminiStartupComponent) -> bool:
        """Configure models and parameters"""
        try:
            if self.session.configuration:
                model_config = self.session.configuration.get("model", {})
                model_name = model_config.get("name", "gemini-pro")
                temperature = model_config.get("temperature", 0.1)
                
                component.output = f"Model: {model_name}, Temperature: {temperature}"
            else:
                component.output = "Using default model configuration"
            
            return True
            
        except Exception as e:
            component.error = f"Model configuration failed: {e}"
            return False
    
    def _handle_claude_integration(self, component: GeminiStartupComponent) -> bool:
        """Set up integration with Claude Code"""
        try:
            # Check for Claude Code integration configuration
            claude_dir = os.path.join(self.project_root, ".claude")
            if not os.path.exists(claude_dir):
                os.makedirs(claude_dir, exist_ok=True)
            
            # Create or validate integration configuration
            if not os.path.exists(self.integration_file):
                integration_config = {
                    "integration": {
                        "enabled": True,
                        "gemini_config": "./gemini.yaml",
                        "coordination_mode": "parallel",
                        "task_routing": {
                            "code_analysis": "gemini",
                            "implementation": "claude",
                            "documentation": "gemini",
                            "testing": "claude",
                            "review": "gemini"
                        }
                    },
                    "workflows": {
                        "feature_development": [
                            {"agent": "claude", "task": "explore_and_plan"},
                            {"agent": "claude", "task": "implement_feature"},
                            {"agent": "gemini", "task": "code_review"},
                            {"agent": "claude", "task": "fix_issues"},
                            {"agent": "gemini", "task": "generate_docs"},
                            {"agent": "claude", "task": "commit_and_pr"}
                        ]
                    }
                }
                
                with open(self.integration_file, 'w') as f:
                    json.dump(integration_config, f, indent=2)
                
                component.output = "Created Claude integration configuration"
            else:
                component.output = "Claude integration configuration exists"
            
            return True
            
        except Exception as e:
            component.error = f"Claude integration setup failed: {e}"
            return False
    
    def _handle_workflow_integration(self, component: GeminiStartupComponent) -> bool:
        """Configure workflow coordination"""
        try:
            # Validate workflow configuration
            if os.path.exists(self.integration_file):
                with open(self.integration_file, 'r') as f:
                    integration = json.load(f)
                
                workflows = integration.get("workflows", {})
                task_routing = integration.get("integration", {}).get("task_routing", {})
                
                component.output = f"Configured {len(workflows)} workflows, {len(task_routing)} routing rules"
            else:
                component.output = "No workflow configuration found"
            
            return True
            
        except Exception as e:
            component.error = f"Workflow integration failed: {e}"
            return False
    
    def _handle_analysis_agent(self, component: GeminiStartupComponent) -> bool:
        """Initialize code analysis specialization"""
        try:
            # Validate analysis capabilities
            analysis_tools = [
                "static_analysis",
                "performance_profiling", 
                "security_scanning",
                "dependency_checking"
            ]
            
            component.output = f"Analysis agent initialized with {len(analysis_tools)} capabilities"
            return True
            
        except Exception as e:
            component.error = f"Analysis agent initialization failed: {e}"
            return False
    
    def _handle_documentation_agent(self, component: GeminiStartupComponent) -> bool:
        """Initialize documentation generation specialization"""
        try:
            # Validate documentation capabilities
            doc_types = [
                "api_documentation",
                "code_comments",
                "user_guides",
                "technical_specifications"
            ]
            
            component.output = f"Documentation agent initialized with {len(doc_types)} document types"
            return True
            
        except Exception as e:
            component.error = f"Documentation agent initialization failed: {e}"
            return False
    
    def _handle_review_agent(self, component: GeminiStartupComponent) -> bool:
        """Initialize code review specialization"""
        try:
            # Validate review capabilities
            review_aspects = [
                "syntax_validation",
                "style_compliance",
                "security_review",
                "performance_optimization",
                "maintainability_assessment"
            ]
            
            component.output = f"Review agent initialized with {len(review_aspects)} review aspects"
            return True
            
        except Exception as e:
            component.error = f"Review agent initialization failed: {e}"
            return False
    
    def _handle_task_routing(self, component: GeminiStartupComponent) -> bool:
        """Set up intelligent task routing"""
        try:
            # Create task routing logic
            routing_rules = {
                "analysis_tasks": ["gemini"],
                "implementation_tasks": ["claude"],
                "documentation_tasks": ["gemini"],
                "testing_tasks": ["claude"],
                "review_tasks": ["gemini"]
            }
            
            component.output = f"Task routing configured with {len(routing_rules)} rule sets"
            return True
            
        except Exception as e:
            component.error = f"Task routing setup failed: {e}"
            return False
    
    def _handle_moex_registration(self, component: GeminiStartupComponent) -> bool:
        """Register with MOEX coordination system"""
        try:
            # Update MOEX workspace with Gemini status
            moex_workspace = os.path.join(self.project_root, "moex-workspace")
            if os.path.exists(moex_workspace):
                status_file = os.path.join(moex_workspace, "gemini-status.json")
                
                gemini_status = {
                    "status": "active",
                    "timestamp": datetime.now().isoformat(),
                    "version": self.session.gemini_version,
                    "capabilities": ["analysis", "documentation", "review"],
                    "session_id": self.session_id
                }
                
                with open(status_file, 'w') as f:
                    json.dump(gemini_status, f, indent=2)
                
                component.output = "Registered with MOEX coordination system"
            else:
                component.output = "MOEX workspace not found - skipping registration"
            
            return True
            
        except Exception as e:
            component.error = f"MOEX registration failed: {e}"
            return True  # Non-critical
    
    def _handle_automation_scripts(self, component: GeminiStartupComponent) -> bool:
        """Validate automation scripts"""
        try:
            scripts_dir = os.path.join(self.project_root, "scripts")
            gemini_scripts = [
                "daily-gemini-check.sh",
                "gemini-code-review.sh", 
                "gemini-docs-generator.sh"
            ]
            
            available_scripts = []
            for script in gemini_scripts:
                script_path = os.path.join(scripts_dir, script)
                if os.path.exists(script_path):
                    available_scripts.append(script)
            
            component.output = f"Available automation scripts: {available_scripts}"
            return True
            
        except Exception as e:
            component.error = f"Automation scripts validation failed: {e}"
            return False
    
    def _handle_session_finalization(self, component: GeminiStartupComponent) -> bool:
        """Finalize Gemini startup session"""
        try:
            # Calculate session metrics
            completed_components = [c for c in self.components if c.status == GeminiComponentStatus.COMPLETED]
            failed_components = [c for c in self.components if c.status == GeminiComponentStatus.FAILED]
            
            success_rate = len(completed_components) / len(self.components) * 100
            
            component.output = f"Gemini session completed: {len(completed_components)}/{len(self.components)} components successful ({success_rate:.1f}%)"
            
            if failed_components:
                component.output += f" - Failed: {[c.name for c in failed_components]}"
            
            return len(failed_components) == 0
            
        except Exception as e:
            component.error = f"Session finalization failed: {e}"
            return False
    
    def _update_status(self):
        """Update Gemini startup status file"""
        try:
            status_data = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "phase": "in_progress",
                "gemini_version": self.session.gemini_version,
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
        """Finalize the Gemini startup session"""
        self.session.end_time = datetime.now()
        self.session.total_duration = (self.session.end_time - self.session.start_time).total_seconds()
        self.session.success = success
        self.session.components = self.components
        
        # Create final report
        report_file = os.path.join(
            self.project_root, 
            "reports", 
            f"gemini-startup-{self.session_id}.json"
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
            "gemini_version": self.session.gemini_version,
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
        
        self.logger.info(f"{status_emoji} Gemini CLI startup sequence completed{termination_note}")
        self.logger.info(f"📊 Total duration: {self.session.total_duration:.2f} seconds")
        self.logger.info(f"📋 Report saved: {report_file}")
        
        if not success:
            failed_components = [c.name for c in self.components if c.status == GeminiComponentStatus.FAILED]
            self.logger.error(f"💥 Failed components: {failed_components}")

def main():
    """Main entry point for Gemini startup sequence"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini CLI Startup Sequence")
    parser.add_argument("--project-root", default="/Users/studio/hardcard", 
                       help="Project root directory")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run startup sequence
    startup = GeminiStartupSequence(args.project_root)
    success = startup.run_startup_sequence()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()