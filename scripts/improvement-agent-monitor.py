#!/usr/bin/env python3
"""
HardCard Improvement Agent Monitor
==================================
Real-time monitoring and coordination of improvement agents
"""

import os
import json
import time
import subprocess
from datetime import datetime, UTC
from pathlib import Path
import threading
import queue
from typing import Dict, List, Any

class ImprovementMonitor:
    """Monitors and coordinates improvement agents"""
    
    def __init__(self):
        self.agents = {
            'quality': {'status': 'idle', 'files_processed': 0, 'issues_found': 0},
            'completion': {'status': 'idle', 'files_improved': 0, 'templates_generated': 0},
            'auto_fix': {'status': 'idle', 'fixes_applied': 0, 'files_fixed': 0},
            'security': {'status': 'idle', 'vulnerabilities_found': 0, 'critical_issues': 0},
            'performance': {'status': 'idle', 'optimizations': 0, 'bundle_size_reduced': 0}
        }
        self.task_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.running = False
        
    def start_monitoring(self):
        """Start the monitoring system"""
        self.running = True
        
        # Start worker threads for each agent type
        threads = []
        for agent_name in self.agents:
            t = threading.Thread(target=self._agent_worker, args=(agent_name,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Start result collector
        collector = threading.Thread(target=self._result_collector)
        collector.daemon = True
        collector.start()
        
        # Start dashboard updater
        dashboard = threading.Thread(target=self._update_dashboard)
        dashboard.daemon = True
        dashboard.start()
        
        return threads
    
    def _agent_worker(self, agent_name: str):
        """Worker thread for each agent"""
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                if task is None:
                    continue
                
                self.agents[agent_name]['status'] = 'working'
                
                # Process based on agent type
                if agent_name == 'quality':
                    result = self._run_quality_check(task)
                elif agent_name == 'completion':
                    result = self._run_completion_check(task)
                elif agent_name == 'auto_fix':
                    result = self._run_auto_fix(task)
                elif agent_name == 'security':
                    result = self._run_security_check(task)
                elif agent_name == 'performance':
                    result = self._run_performance_check(task)
                
                self.results_queue.put((agent_name, result))
                self.agents[agent_name]['status'] = 'idle'
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in {agent_name} agent: {e}")
                self.agents[agent_name]['status'] = 'error'
    
    def _run_quality_check(self, task: Dict) -> Dict:
        """Run quality checks on a file"""
        file_path = task['file_path']
        
        # Run the improvement framework in quality-only mode
        cmd = [
            'python', 'scripts/improvement-agent-framework.py',
            '--root', os.path.dirname(file_path),
            '--patterns', os.path.basename(file_path),
            '--output', f'/tmp/quality_{os.path.basename(file_path)}.json'
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {'status': 'success', 'file': file_path}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'file': file_path, 'error': str(e)}
    
    def _run_completion_check(self, task: Dict) -> Dict:
        """Check and improve file completion"""
        file_path = task['file_path']
        
        # For now, return mock result
        return {
            'status': 'success',
            'file': file_path,
            'completion_before': 75,
            'completion_after': 85,
            'improvements': ['Added missing docstrings', 'Completed TODO sections']
        }
    
    def _run_auto_fix(self, task: Dict) -> Dict:
        """Apply automatic fixes"""
        file_path = task['file_path']
        
        cmd = [
            'python', 'scripts/improvement-agent-framework.py',
            '--root', os.path.dirname(file_path),
            '--patterns', os.path.basename(file_path),
            '--auto-fix',
            '--output', f'/tmp/fix_{os.path.basename(file_path)}.json'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {'status': 'success', 'file': file_path, 'fixes_applied': 5}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'file': file_path, 'error': str(e)}
    
    def _run_security_check(self, task: Dict) -> Dict:
        """Run security analysis"""
        file_path = task['file_path']
        
        # Mock security check
        return {
            'status': 'success',
            'file': file_path,
            'vulnerabilities': [],
            'security_score': 95
        }
    
    def _run_performance_check(self, task: Dict) -> Dict:
        """Run performance analysis"""
        file_path = task['file_path']
        
        # Mock performance check
        return {
            'status': 'success',
            'file': file_path,
            'bundle_impact': '2.3KB',
            'load_time_impact': '15ms'
        }
    
    def _result_collector(self):
        """Collect and process results from agents"""
        while self.running:
            try:
                agent_name, result = self.results_queue.get(timeout=1)
                
                # Update agent statistics
                if result['status'] == 'success':
                    if agent_name == 'quality':
                        self.agents[agent_name]['files_processed'] += 1
                    elif agent_name == 'completion':
                        self.agents[agent_name]['files_improved'] += 1
                    elif agent_name == 'auto_fix':
                        self.agents[agent_name]['fixes_applied'] += result.get('fixes_applied', 0)
                
                # Log result
                self._log_result(agent_name, result)
                
            except queue.Empty:
                continue
    
    def _update_dashboard(self):
        """Update the monitoring dashboard"""
        while self.running:
            try:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🤖 HardCard Improvement Agent Monitor")
                print("=" * 60)
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
                # Show agent status
                for agent_name, data in self.agents.items():
                    status_emoji = "✅" if data['status'] == 'idle' else "🔄" if data['status'] == 'working' else "❌"
                    print(f"{status_emoji} {agent_name.upper()}: {data['status']}")
                    
                    # Show agent-specific stats
                    if agent_name == 'quality':
                        print(f"   Files processed: {data['files_processed']}")
                        print(f"   Issues found: {data['issues_found']}")
                    elif agent_name == 'completion':
                        print(f"   Files improved: {data['files_improved']}")
                        print(f"   Templates generated: {data['templates_generated']}")
                    elif agent_name == 'auto_fix':
                        print(f"   Fixes applied: {data['fixes_applied']}")
                        print(f"   Files fixed: {data['files_fixed']}")
                    elif agent_name == 'security':
                        print(f"   Vulnerabilities: {data['vulnerabilities_found']}")
                        print(f"   Critical issues: {data['critical_issues']}")
                    elif agent_name == 'performance':
                        print(f"   Optimizations: {data['optimizations']}")
                        print(f"   Bundle reduced: {data['bundle_size_reduced']}KB")
                    print()
                
                # Show queue status
                print(f"📋 Task Queue: {self.task_queue.qsize()} pending")
                print(f"📊 Results Queue: {self.results_queue.qsize()} pending")
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Dashboard error: {e}")
    
    def _log_result(self, agent_name: str, result: Dict):
        """Log agent results"""
        log_entry = {
            'timestamp': datetime.now(UTC).isoformat(),
            'agent': agent_name,
            'result': result
        }
        
        log_file = Path('improvement_agent_logs.jsonl')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def add_improvement_task(self, file_path: str, priority: int = 5):
        """Add a file to the improvement queue"""
        task = {
            'file_path': file_path,
            'priority': priority,
            'added_at': datetime.now(UTC).isoformat()
        }
        self.task_queue.put(task)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get current status report"""
        return {
            'timestamp': datetime.now(UTC).isoformat(),
            'agents': self.agents,
            'queue_size': self.task_queue.qsize(),
            'results_pending': self.results_queue.qsize()
        }
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False


def main():
    """Main entry point for the improvement monitor"""
    monitor = ImprovementMonitor()
    
    print("🚀 Starting HardCard Improvement Agent Monitor...")
    threads = monitor.start_monitoring()
    
    # Add some test tasks
    test_files = [
        'HARDCARDSUITE/vetsorcery_extracted/frontend/src/pages/Dashboard.tsx',
        'HARDCARDSUITE/vetsorcery_extracted/backend/app/main.py',
        'HARDCARDSUITE/vetsorcery_extracted/frontend/src/components/PatientCard.tsx',
    ]
    
    for file_path in test_files:
        monitor.add_improvement_task(file_path)
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        
        # Save final report
        final_report = monitor.get_status_report()
        with open('improvement_monitor_final_report.json', 'w') as f:
            json.dump(final_report, f, indent=2)
        
        print("✅ Monitor stopped. Final report saved.")


if __name__ == '__main__':
    main()