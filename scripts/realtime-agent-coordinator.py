#!/usr/bin/env python3
"""
Real-time Agent Coordination System
Enables live collaboration, conflict resolution, and synchronized work between AI agents
"""

import os
import json
import time
import asyncio
import threading
import websockets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
import queue
import hashlib
from enum import Enum
import fcntl

class MessageType(Enum):
    TASK_CLAIM = "task_claim"
    TASK_COMPLETE = "task_complete"
    FILE_LOCK = "file_lock"
    FILE_UNLOCK = "file_unlock"
    PROGRESS_UPDATE = "progress_update"
    CONFLICT_RESOLUTION = "conflict_resolution"
    AGENT_STATUS = "agent_status"
    COORDINATION_REQUEST = "coordination_request"
    DEPENDENCY_NOTIFY = "dependency_notify"

@dataclass
class AgentMessage:
    id: str
    timestamp: str
    agent_id: str
    message_type: MessageType
    data: Dict[str, Any]
    priority: int = 5  # 1=critical, 5=normal, 10=low

@dataclass
class FileLock:
    file_path: str
    agent_id: str
    timestamp: str
    lock_type: str  # read, write, exclusive
    expiry: str

@dataclass
class TaskDependency:
    task_id: str
    depends_on: List[str]
    blocking: List[str]
    estimated_completion: str

@dataclass
class AgentState:
    agent_id: str
    status: str  # active, idle, working, blocked
    current_task: Optional[str]
    locked_files: List[str]
    last_heartbeat: str
    completion_rate: float
    workload: int

class FileConflictResolver:
    """Intelligent file conflict resolution system"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.conflicts_dir = Path(project_root) / "coordination" / "conflicts"
        self.conflicts_dir.mkdir(parents=True, exist_ok=True)
    
    def detect_conflict(self, file_path: str, agent1: str, agent2: str) -> Dict[str, Any]:
        """Detect and analyze file conflicts between agents"""
        conflict_id = hashlib.md5(f"{file_path}{agent1}{agent2}{time.time()}".encode()).hexdigest()[:8]
        
        # Read current file state
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
        except Exception:
            current_content = ""
        
        # Analyze conflict type
        conflict_type = self._analyze_conflict_type(file_path, agent1, agent2)
        
        # Generate resolution strategy
        resolution_strategy = self._generate_resolution_strategy(conflict_type, file_path)
        
        conflict_data = {
            "conflict_id": conflict_id,
            "file_path": file_path,
            "agents": [agent1, agent2],
            "conflict_type": conflict_type,
            "timestamp": datetime.now().isoformat(),
            "current_content_hash": hashlib.md5(current_content.encode()).hexdigest(),
            "resolution_strategy": resolution_strategy,
            "status": "detected"
        }
        
        # Save conflict record
        conflict_file = self.conflicts_dir / f"conflict_{conflict_id}.json"
        with open(conflict_file, 'w') as f:
            json.dump(conflict_data, f, indent=2)
        
        return conflict_data
    
    def _analyze_conflict_type(self, file_path: str, agent1: str, agent2: str) -> str:
        """Analyze the type of conflict"""
        file_extension = Path(file_path).suffix
        
        # Check agent specializations
        agent_types = {
            "frontend-ai": ["tsx", "ts", "css", "jsx", "js"],
            "backend-ai": ["py", "sql", "yaml", "json"],
            "testing-ai": ["test.ts", "test.tsx", "spec.ts"],
            "docs-ai": ["md", "txt", "rst"],
            "security-ai": ["*"]  # Can work on any file for security fixes
        }
        
        agent1_specialized = any(ext in file_extension for ext in agent_types.get(agent1, []))
        agent2_specialized = any(ext in file_extension for ext in agent_types.get(agent2, []))
        
        if agent1_specialized and not agent2_specialized:
            return "specialization_conflict_agent1_priority"
        elif agent2_specialized and not agent1_specialized:
            return "specialization_conflict_agent2_priority"
        elif agent1_specialized and agent2_specialized:
            return "dual_specialization_conflict"
        else:
            return "general_conflict"
    
    def _generate_resolution_strategy(self, conflict_type: str, file_path: str) -> Dict[str, Any]:
        """Generate strategy to resolve conflict"""
        strategies = {
            "specialization_conflict_agent1_priority": {
                "method": "priority_assignment",
                "primary_agent": "agent1",
                "secondary_role": "reviewer",
                "coordination_required": True
            },
            "specialization_conflict_agent2_priority": {
                "method": "priority_assignment", 
                "primary_agent": "agent2",
                "secondary_role": "reviewer",
                "coordination_required": True
            },
            "dual_specialization_conflict": {
                "method": "time_based_allocation",
                "time_slice_minutes": 30,
                "handoff_protocol": "commit_and_notify",
                "coordination_required": True
            },
            "general_conflict": {
                "method": "task_splitting",
                "split_strategy": "line_based",
                "coordination_required": True
            }
        }
        
        base_strategy = strategies.get(conflict_type, strategies["general_conflict"])
        
        # Add file-specific considerations
        if "medical" in file_path.lower() or "patient" in file_path.lower():
            base_strategy["medical_review_required"] = True
            base_strategy["completion_threshold"] = 100
        
        if "test" in file_path.lower():
            base_strategy["test_coordination"] = True
            
        return base_strategy
    
    def resolve_conflict(self, conflict_id: str, resolution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply conflict resolution"""
        conflict_file = self.conflicts_dir / f"conflict_{conflict_id}.json"
        
        if not conflict_file.exists():
            return {"error": "Conflict not found"}
        
        with open(conflict_file, 'r') as f:
            conflict = json.load(f)
        
        # Apply resolution
        conflict["resolution_applied"] = resolution_data
        conflict["resolved_timestamp"] = datetime.now().isoformat()
        conflict["status"] = "resolved"
        
        # Save updated conflict
        with open(conflict_file, 'w') as f:
            json.dump(conflict, f, indent=2)
        
        return conflict

class RealtimeCoordinator:
    """Main real-time coordination system"""
    
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.coordination_dir = Path(project_root) / "coordination"
        self.coordination_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.conflict_resolver = FileConflictResolver(project_root)
        self.file_locks: Dict[str, FileLock] = {}
        self.agent_states: Dict[str, AgentState] = {}
        self.task_dependencies: Dict[str, TaskDependency] = {}
        self.message_queue = queue.PriorityQueue()
        
        # WebSocket connections for real-time communication
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Coordination state
        self.coordination_log = project_root + "/logs/coordination.log"
        
        # Setup logging
        logging.basicConfig(
            filename=self.coordination_log,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Load existing state
        self._load_coordination_state()
        
        # Start background services
        self._start_background_services()
    
    def _load_coordination_state(self):
        """Load existing coordination state from disk"""
        state_file = self.coordination_dir / "coordination_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                # Restore file locks (check if still valid)
                for lock_data in state.get("file_locks", []):
                    lock = FileLock(**lock_data)
                    expiry_time = datetime.fromisoformat(lock.expiry)
                    if expiry_time > datetime.now():
                        self.file_locks[lock.file_path] = lock
                
                # Restore agent states
                for agent_data in state.get("agent_states", []):
                    agent_state = AgentState(**agent_data)
                    # Reset status to idle on restart
                    agent_state.status = "idle"
                    self.agent_states[agent_state.agent_id] = agent_state
                
                logging.info("Coordination state loaded successfully")
                
            except Exception as e:
                logging.error(f"Error loading coordination state: {e}")
    
    def _save_coordination_state(self):
        """Save coordination state to disk"""
        state_file = self.coordination_dir / "coordination_state.json"
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "file_locks": [asdict(lock) for lock in self.file_locks.values()],
            "agent_states": [asdict(state) for state in self.agent_states.values()],
            "task_dependencies": [asdict(dep) for dep in self.task_dependencies.values()]
        }
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving coordination state: {e}")
    
    def _start_background_services(self):
        """Start background coordination services"""
        # Message processor thread
        threading.Thread(target=self._process_messages, daemon=True).start()
        
        # Lock cleanup thread
        threading.Thread(target=self._cleanup_expired_locks, daemon=True).start()
        
        # Heartbeat monitor thread
        threading.Thread(target=self._monitor_agent_heartbeats, daemon=True).start()
        
        # State persistence thread
        threading.Thread(target=self._periodic_state_save, daemon=True).start()
        
        logging.info("Background coordination services started")
    
    def register_agent(self, agent_id: str) -> Dict[str, Any]:
        """Register a new agent with the coordination system"""
        agent_state = AgentState(
            agent_id=agent_id,
            status="active",
            current_task=None,
            locked_files=[],
            last_heartbeat=datetime.now().isoformat(),
            completion_rate=0.0,
            workload=0
        )
        
        self.agent_states[agent_id] = agent_state
        
        logging.info(f"Agent {agent_id} registered")
        
        # Send welcome message with current coordination state
        return {
            "status": "registered",
            "agent_id": agent_id,
            "coordination_info": {
                "active_agents": len(self.agent_states),
                "active_locks": len(self.file_locks),
                "pending_dependencies": len(self.task_dependencies)
            }
        }
    
    def claim_task(self, agent_id: str, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent claims a task"""
        # Check if task has dependencies
        if task_id in self.task_dependencies:
            dependency = self.task_dependencies[task_id]
            unresolved_deps = [dep for dep in dependency.depends_on 
                             if not self._is_task_completed(dep)]
            
            if unresolved_deps:
                return {
                    "status": "blocked",
                    "reason": "unresolved_dependencies",
                    "dependencies": unresolved_deps
                }
        
        # Check for conflicts with other agents
        file_paths = task_data.get("files", [])
        conflicts = []
        
        for file_path in file_paths:
            if file_path in self.file_locks:
                existing_lock = self.file_locks[file_path]
                if existing_lock.agent_id != agent_id:
                    conflicts.append({
                        "file": file_path,
                        "locked_by": existing_lock.agent_id,
                        "lock_type": existing_lock.lock_type
                    })
        
        if conflicts:
            # Try to resolve conflicts
            resolution_results = []
            for conflict in conflicts:
                conflict_data = self.conflict_resolver.detect_conflict(
                    conflict["file"], agent_id, conflict["locked_by"]
                )
                resolution_results.append(conflict_data)
            
            return {
                "status": "conflict_detected",
                "conflicts": conflicts,
                "resolution_strategies": resolution_results
            }
        
        # Claim task
        if agent_id in self.agent_states:
            self.agent_states[agent_id].current_task = task_id
            self.agent_states[agent_id].status = "working"
            self.agent_states[agent_id].workload += 1
        
        # Lock files
        for file_path in file_paths:
            self._lock_file(file_path, agent_id, "write")
        
        # Broadcast task claim
        message = AgentMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            message_type=MessageType.TASK_CLAIM,
            data={"task_id": task_id, "files": file_paths},
            priority=3
        )
        
        self._broadcast_message(message)
        
        logging.info(f"Agent {agent_id} claimed task {task_id}")
        
        return {
            "status": "claimed",
            "task_id": task_id,
            "locked_files": file_paths
        }
    
    def complete_task(self, agent_id: str, task_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent completes a task"""
        # Update agent state
        if agent_id in self.agent_states:
            agent = self.agent_states[agent_id]
            agent.current_task = None
            agent.status = "idle"
            agent.workload = max(0, agent.workload - 1)
            
            # Update completion rate
            completed_tasks = completion_data.get("completed_tasks", 1)
            time_taken = completion_data.get("time_taken_minutes", 30)
            agent.completion_rate = completed_tasks / max(1, time_taken / 60)  # tasks per hour
        
        # Release file locks
        files_to_unlock = []
        for file_path, lock in list(self.file_locks.items()):
            if lock.agent_id == agent_id:
                files_to_unlock.append(file_path)
                del self.file_locks[file_path]
        
        # Notify dependent tasks
        self._notify_dependent_tasks(task_id)
        
        # Broadcast completion
        message = AgentMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            message_type=MessageType.TASK_COMPLETE,
            data={
                "task_id": task_id,
                "completion_data": completion_data,
                "unlocked_files": files_to_unlock
            },
            priority=3
        )
        
        self._broadcast_message(message)
        
        logging.info(f"Agent {agent_id} completed task {task_id}")
        
        return {
            "status": "completed",
            "task_id": task_id,
            "unlocked_files": files_to_unlock
        }
    
    def request_coordination(self, agent_id: str, request_type: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent requests coordination assistance"""
        coordination_id = str(uuid.uuid4())[:8]
        
        coordination_request = {
            "coordination_id": coordination_id,
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "request_type": request_type,
            "request_data": request_data,
            "status": "pending"
        }
        
        # Handle different coordination types
        if request_type == "dependency_resolution":
            response = self._handle_dependency_resolution(agent_id, request_data)
        elif request_type == "conflict_mediation":
            response = self._handle_conflict_mediation(agent_id, request_data)
        elif request_type == "workload_balancing":
            response = self._handle_workload_balancing(agent_id, request_data)
        elif request_type == "resource_allocation":
            response = self._handle_resource_allocation(agent_id, request_data)
        else:
            response = {"status": "unknown_request_type"}
        
        coordination_request["response"] = response
        coordination_request["status"] = "resolved"
        
        # Save coordination record
        coord_file = self.coordination_dir / f"coordination_{coordination_id}.json"
        with open(coord_file, 'w') as f:
            json.dump(coordination_request, f, indent=2)
        
        return response
    
    def _lock_file(self, file_path: str, agent_id: str, lock_type: str = "write", duration_minutes: int = 60):
        """Lock a file for an agent"""
        expiry = datetime.now() + timedelta(minutes=duration_minutes)
        
        lock = FileLock(
            file_path=file_path,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
            lock_type=lock_type,
            expiry=expiry.isoformat()
        )
        
        self.file_locks[file_path] = lock
        
        # Update agent state
        if agent_id in self.agent_states:
            if file_path not in self.agent_states[agent_id].locked_files:
                self.agent_states[agent_id].locked_files.append(file_path)
    
    def _handle_dependency_resolution(self, agent_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dependency resolution requests"""
        task_id = request_data.get("task_id")
        dependencies = request_data.get("dependencies", [])
        
        # Analyze dependency chain
        dependency_status = {}
        blocking_agents = {}
        
        for dep_task in dependencies:
            status = self._get_task_status(dep_task)
            dependency_status[dep_task] = status
            
            if status == "in_progress":
                # Find which agent is working on it
                for agent, state in self.agent_states.items():
                    if state.current_task == dep_task:
                        blocking_agents[dep_task] = agent
                        break
        
        # Generate resolution strategy
        if all(status == "completed" for status in dependency_status.values()):
            return {
                "status": "dependencies_resolved",
                "can_proceed": True
            }
        
        # Calculate estimated wait time
        estimated_wait = 0
        for dep_task, status in dependency_status.items():
            if status == "in_progress" and dep_task in blocking_agents:
                blocking_agent = blocking_agents[dep_task]
                agent_state = self.agent_states.get(blocking_agent)
                if agent_state and agent_state.completion_rate > 0:
                    estimated_wait += max(30, 60 / agent_state.completion_rate)  # minutes
        
        return {
            "status": "dependencies_pending",
            "can_proceed": False,
            "dependency_status": dependency_status,
            "blocking_agents": blocking_agents,
            "estimated_wait_minutes": estimated_wait,
            "recommendation": "wait" if estimated_wait < 120 else "work_on_other_tasks"
        }
    
    def _handle_conflict_mediation(self, agent_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conflict mediation requests"""
        file_path = request_data.get("file_path")
        conflict_type = request_data.get("conflict_type", "general")
        
        if file_path in self.file_locks:
            existing_lock = self.file_locks[file_path]
            
            # Generate conflict resolution
            conflict_data = self.conflict_resolver.detect_conflict(
                file_path, agent_id, existing_lock.agent_id
            )
            
            strategy = conflict_data["resolution_strategy"]
            
            return {
                "status": "conflict_resolution_generated",
                "conflict_id": conflict_data["conflict_id"],
                "strategy": strategy,
                "recommendation": self._format_conflict_recommendation(strategy)
            }
        
        return {
            "status": "no_conflict_detected",
            "can_proceed": True
        }
    
    def _handle_workload_balancing(self, agent_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workload balancing requests"""
        current_workload = request_data.get("current_workload", 0)
        
        # Analyze workload across all agents
        workloads = {agent: state.workload for agent, state in self.agent_states.items()}
        avg_workload = sum(workloads.values()) / max(1, len(workloads))
        
        # Find agents with lower workload
        available_agents = [
            agent for agent, workload in workloads.items()
            if workload < avg_workload and agent != agent_id
        ]
        
        if current_workload > avg_workload * 1.5 and available_agents:
            return {
                "status": "rebalancing_recommended",
                "overloaded": True,
                "available_agents": available_agents,
                "recommended_action": "delegate_tasks",
                "current_workload": current_workload,
                "average_workload": avg_workload
            }
        
        return {
            "status": "workload_balanced",
            "overloaded": False,
            "current_workload": current_workload,
            "average_workload": avg_workload
        }
    
    def _handle_resource_allocation(self, agent_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resource allocation requests"""
        requested_resources = request_data.get("resources", [])
        
        # Check resource availability
        available_resources = []
        unavailable_resources = []
        
        for resource in requested_resources:
            if resource.startswith("file:"):
                file_path = resource[5:]  # Remove "file:" prefix
                if file_path not in self.file_locks:
                    available_resources.append(resource)
                else:
                    unavailable_resources.append({
                        "resource": resource,
                        "locked_by": self.file_locks[file_path].agent_id,
                        "lock_expiry": self.file_locks[file_path].expiry
                    })
            else:
                # Other resource types
                available_resources.append(resource)
        
        return {
            "status": "resource_allocation_analyzed",
            "available_resources": available_resources,
            "unavailable_resources": unavailable_resources,
            "can_proceed": len(unavailable_resources) == 0
        }
    
    def _format_conflict_recommendation(self, strategy: Dict[str, Any]) -> str:
        """Format conflict resolution strategy into human-readable recommendation"""
        method = strategy.get("method", "unknown")
        
        if method == "priority_assignment":
            primary = strategy.get("primary_agent", "unknown")
            return f"Assign primary responsibility to {primary}, other agent acts as reviewer"
        elif method == "time_based_allocation":
            time_slice = strategy.get("time_slice_minutes", 30)
            return f"Alternate work in {time_slice}-minute time slices with commit handoffs"
        elif method == "task_splitting":
            return "Split the task into non-overlapping components"
        else:
            return "Manual coordination required"
    
    def _process_messages(self):
        """Background message processing"""
        while True:
            try:
                priority, message_data = self.message_queue.get(timeout=1)
                message = AgentMessage(**message_data)
                
                # Process message based on type
                self._handle_message(message)
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing message: {e}")
    
    def _handle_message(self, message: AgentMessage):
        """Handle incoming coordination messages"""
        logging.info(f"Processing message: {message.message_type.value} from {message.agent_id}")
        
        # Update last heartbeat
        if message.agent_id in self.agent_states:
            self.agent_states[message.agent_id].last_heartbeat = message.timestamp
    
    def _cleanup_expired_locks(self):
        """Clean up expired file locks"""
        while True:
            try:
                current_time = datetime.now()
                expired_locks = []
                
                for file_path, lock in self.file_locks.items():
                    expiry_time = datetime.fromisoformat(lock.expiry)
                    if current_time > expiry_time:
                        expired_locks.append(file_path)
                
                # Remove expired locks
                for file_path in expired_locks:
                    lock = self.file_locks[file_path]
                    del self.file_locks[file_path]
                    
                    # Update agent state
                    if lock.agent_id in self.agent_states:
                        agent = self.agent_states[lock.agent_id]
                        if file_path in agent.locked_files:
                            agent.locked_files.remove(file_path)
                    
                    logging.info(f"Expired lock removed: {file_path} (was locked by {lock.agent_id})")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error cleaning up locks: {e}")
                time.sleep(60)
    
    def _monitor_agent_heartbeats(self):
        """Monitor agent heartbeats and mark inactive agents"""
        while True:
            try:
                current_time = datetime.now()
                inactive_agents = []
                
                for agent_id, state in self.agent_states.items():
                    last_heartbeat = datetime.fromisoformat(state.last_heartbeat)
                    if current_time - last_heartbeat > timedelta(minutes=10):
                        inactive_agents.append(agent_id)
                
                # Mark inactive agents and release their locks
                for agent_id in inactive_agents:
                    logging.warning(f"Agent {agent_id} marked as inactive due to missing heartbeat")
                    
                    # Release locks
                    locks_to_remove = []
                    for file_path, lock in self.file_locks.items():
                        if lock.agent_id == agent_id:
                            locks_to_remove.append(file_path)
                    
                    for file_path in locks_to_remove:
                        del self.file_locks[file_path]
                    
                    # Update agent state
                    if agent_id in self.agent_states:
                        self.agent_states[agent_id].status = "inactive"
                        self.agent_states[agent_id].locked_files = []
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logging.error(f"Error monitoring heartbeats: {e}")
                time.sleep(300)
    
    def _periodic_state_save(self):
        """Periodically save coordination state"""
        while True:
            try:
                self._save_coordination_state()
                time.sleep(120)  # Save every 2 minutes
            except Exception as e:
                logging.error(f"Error saving state: {e}")
                time.sleep(120)
    
    def _broadcast_message(self, message: AgentMessage):
        """Broadcast message to all connected agents"""
        # Add to message queue for processing
        self.message_queue.put((message.priority, asdict(message)))
        
        # In a real implementation, this would send via WebSocket to connected agents
        logging.info(f"Broadcasting message: {message.message_type.value}")
    
    def _is_task_completed(self, task_id: str) -> bool:
        """Check if a task is completed"""
        # This would integrate with the task tracking system
        # For now, simulate based on coordination records
        return False  # Placeholder
    
    def _get_task_status(self, task_id: str) -> str:
        """Get current status of a task"""
        # Check if any agent is currently working on this task
        for agent, state in self.agent_states.items():
            if state.current_task == task_id:
                return "in_progress"
        
        # Check completion records
        if self._is_task_completed(task_id):
            return "completed"
        
        return "pending"
    
    def _notify_dependent_tasks(self, completed_task_id: str):
        """Notify tasks that depend on the completed task"""
        dependent_tasks = []
        
        for task_id, dependency in self.task_dependencies.items():
            if completed_task_id in dependency.depends_on:
                dependent_tasks.append(task_id)
        
        for task_id in dependent_tasks:
            # Notify agents about dependency resolution
            message = AgentMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                agent_id="coordinator",
                message_type=MessageType.DEPENDENCY_NOTIFY,
                data={
                    "task_id": task_id,
                    "resolved_dependency": completed_task_id
                },
                priority=2
            )
            
            self._broadcast_message(message)
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "total": len(self.agent_states),
                "active": len([s for s in self.agent_states.values() if s.status == "active"]),
                "working": len([s for s in self.agent_states.values() if s.status == "working"]),
                "idle": len([s for s in self.agent_states.values() if s.status == "idle"])
            },
            "file_locks": {
                "total": len(self.file_locks),
                "by_agent": {agent: len([l for l in self.file_locks.values() if l.agent_id == agent])
                           for agent in self.agent_states.keys()}
            },
            "dependencies": {
                "total": len(self.task_dependencies),
                "blocking": len([d for d in self.task_dependencies.values() if d.blocking])
            },
            "message_queue_size": self.message_queue.qsize()
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real-time Agent Coordinator')
    parser.add_argument('--start-server', action='store_true', help='Start coordination server')
    parser.add_argument('--agent-id', help='Register as agent')
    parser.add_argument('--status', action='store_true', help='Show coordination status')
    parser.add_argument('--claim-task', help='Claim a task')
    parser.add_argument('--complete-task', help='Complete a task')
    
    args = parser.parse_args()
    
    coordinator = RealtimeCoordinator()
    
    if args.status:
        status = coordinator.get_coordination_status()
        print(json.dumps(status, indent=2))
    
    elif args.agent_id:
        response = coordinator.register_agent(args.agent_id)
        print(f"Agent {args.agent_id} registered: {response}")
    
    elif args.claim_task and args.agent_id:
        response = coordinator.claim_task(args.agent_id, args.claim_task, {"files": []})
        print(f"Task claim response: {response}")
    
    elif args.complete_task and args.agent_id:
        response = coordinator.complete_task(args.agent_id, args.complete_task, {"completed_tasks": 1})
        print(f"Task completion response: {response}")
    
    elif args.start_server:
        print("🔄 Real-time Agent Coordination Server starting...")
        print(f"📊 Initial status: {coordinator.get_coordination_status()}")
        
        # Keep server running
        try:
            while True:
                time.sleep(60)
                status = coordinator.get_coordination_status()
                print(f"⏰ Coordination status: {status['agents']['working']} working, {status['file_locks']['total']} locks")
        except KeyboardInterrupt:
            print("\n🛑 Coordination server stopped")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()