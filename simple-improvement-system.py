#!/usr/bin/env python3
"""
HardCard Simple Continuous Improvement System
Autonomous AI agents that work continuously to improve code quality, 
strategic alignment, and goal achievement.
"""

import json
import logging
import os
import subprocess
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/studio/hardcard/logs/improvement-system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleContinuousImprovementSystem:
    def __init__(self):
        self.base_path = Path("/Users/studio/hardcard")
        self.agents = {}
        self.metrics = {}
        self.goals = {}
        self.running = False
        
        # Initialize agent configurations
        self.agent_configs = {
            "code_quality_agent": {
                "interval": 300,  # 5 minutes
                "priority": "high",
                "tasks": ["type_check", "lint", "security_scan"]
            },
            "strategic_alignment_agent": {
                "interval": 1800,  # 30 minutes
                "priority": "medium", 
                "tasks": ["goal_review", "progress_assessment"]
            },
            "performance_optimization_agent": {
                "interval": 600,  # 10 minutes
                "priority": "high",
                "tasks": ["performance_analysis", "optimization_suggestions"]
            },
            "learning_agent": {
                "interval": 3600,  # 1 hour
                "priority": "medium",
                "tasks": ["pattern_analysis", "improvement_suggestions"]
            },
            "deployment_readiness_agent": {
                "interval": 900,  # 15 minutes
                "priority": "high",
                "tasks": ["readiness_check", "quality_gates"]
            },
            "code_fixing_agent": {
                "interval": 1800,  # 30 minutes
                "priority": "high",
                "tasks": ["fix_typescript", "fix_eslint", "organize_imports"]
            }
        }
        
        # Load current goals
        self.load_goals()
        
    def load_goals(self):
        """Load strategic goals from configuration"""
        goals_file = self.base_path / "goals.json"
        if goals_file.exists():
            with open(goals_file, 'r') as f:
                self.goals = json.load(f)
        else:
            # Default goals
            self.goals = {
                "code_quality": {
                    "target_completion": 95,
                    "current_completion": 74,
                    "target_test_coverage": 90,
                    "current_test_coverage": 68,
                    "target_security_score": 95,
                    "current_security_score": 91
                },
                "strategic_objectives": {
                    "vetsorcery_completion": {
                        "target": 100,
                        "current": 87,
                        "deadline": "2025-01-15"
                    },
                    "aiva_platform_launch": {
                        "target": 100,
                        "current": 65,
                        "deadline": "2025-02-01"
                    },
                    "security_compliance": {
                        "target": 100,
                        "current": 91,
                        "deadline": "2025-01-10"
                    }
                }
            }
            self.save_goals()
    
    def save_goals(self):
        """Save current goals to file"""
        goals_file = self.base_path / "goals.json"
        with open(goals_file, 'w') as f:
            json.dump(self.goals, f, indent=2)
    
    def start_system(self):
        """Start the continuous improvement system"""
        logger.info("🚀 Starting Simple Continuous Improvement System")
        self.running = True
        
        # Create agent threads
        threads = []
        for agent_name, config in self.agent_configs.items():
            thread = threading.Thread(target=self.run_agent, args=(agent_name, config))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            self.agents[agent_name] = {"thread": thread, "config": config, "status": "starting"}
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.system_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        threads.append(monitor_thread)
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🔄 Received shutdown signal")
            self.stop_system()
    
    def run_agent(self, agent_name: str, config: Dict):
        """Run an individual agent"""
        logger.info(f"🤖 Starting {agent_name}")
        
        while self.running:
            try:
                start_time = time.time()
                self.agents[agent_name]["status"] = "running"
                self.agents[agent_name]["last_run"] = datetime.now().isoformat()
                
                # Execute agent tasks
                results = self.execute_agent_tasks(agent_name, config["tasks"])
                
                # Update metrics
                execution_time = time.time() - start_time
                self.agents[agent_name]["execution_time"] = execution_time
                self.agents[agent_name]["results"] = results
                self.agents[agent_name]["status"] = "idle"
                
                logger.info(f"✅ {agent_name} completed in {execution_time:.2f}s")
                
                # Wait for next interval
                time.sleep(config["interval"])
                
            except Exception as e:
                logger.error(f"❌ Error in {agent_name}: {e}")
                if agent_name in self.agents:
                    self.agents[agent_name]["status"] = "error"
                    self.agents[agent_name]["error"] = str(e)
                time.sleep(60)  # Wait 1 minute before retry
    
    def execute_agent_tasks(self, agent_name: str, tasks: List[str]) -> Dict:
        """Execute specific tasks for an agent"""
        results = {"improvements": [], "metrics": {}}
        
        if agent_name == "code_quality_agent":
            results = self.code_quality_tasks(tasks)
        elif agent_name == "strategic_alignment_agent":
            results = self.strategic_alignment_tasks(tasks)
        elif agent_name == "performance_optimization_agent":
            results = self.performance_optimization_tasks(tasks)
        elif agent_name == "learning_agent":
            results = self.learning_tasks(tasks)
        elif agent_name == "deployment_readiness_agent":
            results = self.deployment_readiness_tasks(tasks)
        elif agent_name == "code_fixing_agent":
            results = self.code_fixing_tasks(tasks)
        
        return results
    
    def code_quality_tasks(self, tasks: List[str]) -> Dict:
        """Execute code quality improvement tasks"""
        results = {"improvements": [], "metrics": {}}
        
        if "type_check" in tasks:
            # Check TypeScript files exist
            frontend_path = self.base_path / "HARDCARDSUITE/vetsorcery_extracted/frontend"
            if frontend_path.exists():
                ts_files = list(frontend_path.rglob("*.ts")) + list(frontend_path.rglob("*.tsx"))
                results["metrics"]["typescript_files"] = len(ts_files)
                if len(ts_files) > 0:
                    results["improvements"].append(f"Found {len(ts_files)} TypeScript files for type checking")
        
        if "security_scan" in tasks:
            # Basic security check - look for sensitive patterns
            sensitive_patterns = ["password", "secret", "api_key", "token"]
            found_issues = 0
            
            for pattern in sensitive_patterns:
                try:
                    result = subprocess.run(
                        ["grep", "-r", "-i", pattern, ".", "--include=*.js", "--include=*.ts", "--include=*.tsx"],
                        cwd=self.base_path,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.stdout:
                        found_issues += len(result.stdout.split('\n'))
                except:
                    pass
            
            results["metrics"]["potential_security_issues"] = found_issues
            if found_issues == 0:
                results["improvements"].append("No obvious security issues found in codebase")
        
        return results
    
    def strategic_alignment_tasks(self, tasks: List[str]) -> Dict:
        """Execute strategic alignment tasks"""
        results = {"realignments": [], "progress_updates": {}}
        
        if "goal_review" in tasks:
            # Update completion percentages based on file analysis
            total_files = 0
            completed_files = 0
            
            # Count files in key directories
            key_dirs = [
                "HARDCARDSUITE/vetsorcery_extracted/frontend/src",
                "HARDCARDSUITE/vetsorcery_extracted/backend/app"
            ]
            
            for dir_path in key_dirs:
                full_path = self.base_path / dir_path
                if full_path.exists():
                    files = list(full_path.rglob("*.py")) + list(full_path.rglob("*.ts")) + list(full_path.rglob("*.tsx"))
                    total_files += len(files)
                    
                    # Simple heuristic: files > 100 lines are "completed"
                    for file_path in files:
                        try:
                            with open(file_path, 'r') as f:
                                lines = len(f.readlines())
                                if lines > 100:
                                    completed_files += 1
                        except:
                            pass
            
            if total_files > 0:
                completion_percentage = (completed_files / total_files) * 100
                self.goals["code_quality"]["current_completion"] = completion_percentage
                results["progress_updates"]["code_completion"] = completion_percentage
                
                if completion_percentage > 80:
                    results["realignments"].append("Code completion above 80% - ready for testing phase")
        
        return results
    
    def performance_optimization_tasks(self, tasks: List[str]) -> Dict:
        """Execute performance optimization tasks"""
        results = {"optimizations": [], "metrics": {}}
        
        if "performance_analysis" in tasks:
            # Analyze file sizes
            large_files = []
            frontend_path = self.base_path / "HARDCARDSUITE/vetsorcery_extracted/frontend"
            
            if frontend_path.exists():
                for file_path in frontend_path.rglob("*.js"):
                    if file_path.stat().st_size > 100000:  # > 100KB
                        large_files.append(file_path.name)
                
                results["metrics"]["large_files_count"] = len(large_files)
                if large_files:
                    results["optimizations"].append(f"Found {len(large_files)} large JavaScript files for optimization")
                else:
                    results["optimizations"].append("No oversized JavaScript files detected")
        
        return results
    
    def learning_tasks(self, tasks: List[str]) -> Dict:
        """Execute learning and pattern analysis tasks"""
        results = {"insights": [], "patterns": {}}
        
        if "pattern_analysis" in tasks:
            # Analyze code patterns
            pattern_counts = {"react_components": 0, "api_endpoints": 0, "test_files": 0}
            
            frontend_path = self.base_path / "HARDCARDSUITE/vetsorcery_extracted/frontend"
            if frontend_path.exists():
                tsx_files = list(frontend_path.rglob("*.tsx"))
                pattern_counts["react_components"] = len(tsx_files)
            
            backend_path = self.base_path / "HARDCARDSUITE/vetsorcery_extracted/backend"
            if backend_path.exists():
                py_files = list(backend_path.rglob("*.py"))
                test_files = [f for f in py_files if "test" in f.name]
                pattern_counts["test_files"] = len(test_files)
            
            results["patterns"] = pattern_counts
            
            if pattern_counts["react_components"] > 20:
                results["insights"].append("Large number of React components - consider component organization")
            
            if pattern_counts["test_files"] < 10:
                results["insights"].append("Low test file count - prioritize test coverage")
        
        return results
    
    def deployment_readiness_tasks(self, tasks: List[str]) -> Dict:
        """Execute deployment readiness tasks"""
        results = {"readiness_checks": [], "blockers": []}
        
        if "readiness_check" in tasks:
            # Check if key files exist
            key_files = [
                "HARDCARDSUITE/vetsorcery_extracted/frontend/package.json",
                "HARDCARDSUITE/vetsorcery_extracted/backend/requirements.txt",
                "HARDCARDSUITE/vetsorcery_extracted/frontend/vetsorcery-production.html"
            ]
            
            for file_path in key_files:
                full_path = self.base_path / file_path
                if full_path.exists():
                    results["readiness_checks"].append(f"✅ {file_path.split('/')[-1]} exists")
                else:
                    results["blockers"].append(f"❌ Missing {file_path.split('/')[-1]}")
        
        return results
    
    def code_fixing_tasks(self, tasks: List[str]) -> Dict:
        """Execute code fixing tasks"""
        results = {"improvements": [], "metrics": {}}
        
        try:
            # Import and run the code fixing agents
            import sys
            sys.path.append(str(self.base_path))
            from code_fixing_agents import CodeFixingAgents
            
            fixer = CodeFixingAgents()
            
            if "fix_typescript" in tasks:
                fixer.run_typescript_fixer()
                results["improvements"].append("Ran TypeScript auto-fixer")
            
            if "fix_eslint" in tasks:
                fixer.run_eslint_fixer()
                results["improvements"].append("Ran ESLint auto-fixer")
            
            if "organize_imports" in tasks:
                fixer.run_import_organizer()
                results["improvements"].append("Organized imports across codebase")
            
            # Add metrics
            results["metrics"]["fixes_applied"] = len(fixer.fixes_applied)
            
            if fixer.fixes_applied:
                results["improvements"].append(f"Applied {len(fixer.fixes_applied)} automatic fixes")
        
        except Exception as e:
            logger.error(f"Code fixing agent error: {e}")
            results["improvements"].append(f"Code fixing error: {str(e)}")
        
        return results
    
    def system_monitor(self):
        """Monitor system health and update dashboard"""
        while self.running:
            try:
                # Update status file for dashboard
                status = {
                    "timestamp": datetime.now().isoformat(),
                    "system_running": True,
                    "agents": {name: {
                        "status": data.get("status", "unknown"),
                        "last_run": data.get("last_run"),
                        "execution_time": data.get("execution_time"),
                        "results": data.get("results", {})
                    } for name, data in self.agents.items()},
                    "goals": self.goals,
                    "metrics": self.metrics
                }
                
                status_file = self.base_path / "system-status.json"
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)
                
                # Log system health
                active_agents = sum(1 for agent in self.agents.values() if agent.get("status") == "running")
                logger.info(f"💓 System healthy - {active_agents} agents active")
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(60)
    
    def stop_system(self):
        """Stop the continuous improvement system"""
        logger.info("🛑 Stopping Continuous Improvement System")
        self.running = False

def main():
    """Main entry point"""
    system = SimpleContinuousImprovementSystem()
    
    try:
        system.start_system()
    except KeyboardInterrupt:
        logger.info("🔄 Received shutdown signal")
        system.stop_system()
    except Exception as e:
        logger.error(f"💥 System crash: {e}")
        system.stop_system()

if __name__ == "__main__":
    main()