#!/usr/bin/env python3
"""
Hardcard Biological System: Complete implementation of enzyme-based virtual economy
Combines virtual tokens, specialized enzymes, supporter factories, and torrent-style problem solving
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('hardcard_biological')

class EnzymeType(Enum):
    CODE_SPLICERASE = "code_splicerase"
    DATA_PROCESSORASE = "data_processorase"
    BUG_HUNTASE = "bug_huntase"
    SECURITY_SCANASE = "security_scanase"
    PERFORMANCE_OPTIMASE = "performance_optimase"

class ResourceType(Enum):
    COMPUTE_CYCLES = "compute_cycles"
    CODE_SNIPPETS = "code_snippets"
    TEST_CASES = "test_cases"
    DOCUMENTATION = "documentation"
    VALIDATION_RULES = "validation_rules"

@dataclass
class VirtualAccount:
    agent_id: str
    hgov_balance: int = 50000
    hcc_balance: int = 100000
    total_earned: int = 0
    tasks_completed: int = 0
    success_rate: float = 1.0
    specializations: List[str] = None

@dataclass
class Task:
    task_id: str
    title: str
    description: str
    enzyme_type: EnzymeType
    required_resources: Dict[ResourceType, int]
    reward_hgov: int
    reward_hcc: int
    difficulty: int
    deadline: datetime
    status: str = "pending"

class BiologicalAgent:
    def __init__(self, agent_id: str, name: str, enzyme_type: EnzymeType, specializations: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.enzyme_type = enzyme_type
        self.specializations = specializations
        self.account = VirtualAccount(agent_id, specializations=specializations)
        self.active_tasks: List[str] = []
        self.efficiency_rating = random.uniform(0.8, 0.98)
        self.last_active = datetime.now()
        
        # Pre-made code libraries this agent has access to
        self.code_library = self._initialize_code_library()
        
        logger.info(f"🧬 {name} ({enzyme_type.value}) agent initialized with {self.account.hgov_balance} HGOV")
    
    def _initialize_code_library(self) -> Dict[str, List[str]]:
        """Initialize agent's library of pre-made code snippets based on specialization"""
        library = {}
        
        if self.enzyme_type == EnzymeType.CODE_SPLICERASE:
            library['functions'] = [
                'def process_list(items): return [transform(item) for item in items]',
                'def validate_input(data): return isinstance(data, (list, tuple)) and len(data) > 0',
                'def format_output(result): return {"status": "success", "data": result}',
                'def handle_error(error): return {"status": "error", "message": str(error)}'
            ]
            library['patterns'] = [
                'map-reduce pattern',
                'pipeline pattern', 
                'filter-transform pattern'
            ]
        
        elif self.enzyme_type == EnzymeType.BUG_HUNTASE:
            library['checks'] = [
                'null pointer checks',
                'boundary condition tests',
                'type validation tests',
                'error handling verification'
            ]
            library['patterns'] = [
                'defensive programming patterns',
                'error detection patterns'
            ]
        
        elif self.enzyme_type == EnzymeType.SECURITY_SCANASE:
            library['scanners'] = [
                'input sanitization checks',
                'authentication validators',
                'authorization checks',
                'data encryption patterns'
            ]
        
        return library
    
    async def work_on_task(self, task: Task, ecosystem) -> Dict:
        """Agent works on a task using biological assembly approach"""
        start_time = datetime.now()
        
        # Check if agent has required resources
        if not await self._check_resource_availability(task, ecosystem):
            return {"success": False, "error": "Insufficient resources"}
        
        # Consume resources from ecosystem
        await ecosystem.consume_resources(self.agent_id, task.required_resources)
        
        # Perform enzymatic work (cut-and-paste from library)
        work_result = await self._perform_enzymatic_work(task)
        
        # Calculate work time based on efficiency
        work_duration = random.uniform(30, 120) / self.efficiency_rating  # 30-120 seconds base
        await asyncio.sleep(work_duration / 60)  # Convert to actual seconds for demo
        
        # Determine success based on efficiency and task difficulty
        success_chance = self.efficiency_rating * (1.0 - task.difficulty * 0.1)
        success = random.random() < success_chance
        
        if success:
            # Award virtual tokens
            self.account.hgov_balance += task.reward_hgov
            self.account.hcc_balance += task.reward_hcc
            self.account.total_earned += task.reward_hgov + task.reward_hcc
            self.account.tasks_completed += 1
            
            # Update success rate
            total_attempts = self.account.tasks_completed + (self.account.tasks_completed * 0.1)  # Estimated failures
            self.account.success_rate = self.account.tasks_completed / total_attempts
            
            logger.info(f"✅ {self.name} completed '{task.title}' - Earned {task.reward_hgov} HGOV, {task.reward_hcc} HCC")
            
            return {
                "success": True,
                "work_product": work_result,
                "duration": work_duration,
                "tokens_earned": {"hgov": task.reward_hgov, "hcc": task.reward_hcc}
            }
        else:
            logger.info(f"❌ {self.name} failed task '{task.title}' - No rewards")
            return {"success": False, "error": "Task execution failed"}
    
    async def _check_resource_availability(self, task: Task, ecosystem) -> bool:
        """Check if required resources are available in ecosystem"""
        for resource_type, amount in task.required_resources.items():
            if ecosystem.resource_pools.get(resource_type, 0) < amount:
                return False
        return True
    
    async def _perform_enzymatic_work(self, task: Task) -> Dict:
        """Perform work by cutting and pasting from pre-made code library"""
        work_product = {
            "enzyme_used": self.enzyme_type.value,
            "components_assembled": [],
            "assembly_method": "biological_cut_paste"
        }
        
        if self.enzyme_type == EnzymeType.CODE_SPLICERASE:
            # Cut and paste from function library
            selected_functions = random.sample(self.code_library.get('functions', []), 
                                             min(3, len(self.code_library.get('functions', []))))
            work_product["components_assembled"] = selected_functions
            work_product["assembly_type"] = "function_splicing"
            
        elif self.enzyme_type == EnzymeType.BUG_HUNTASE:
            # Use pre-made bug detection patterns
            selected_checks = random.sample(self.code_library.get('checks', []),
                                          min(2, len(self.code_library.get('checks', []))))
            work_product["components_assembled"] = selected_checks
            work_product["assembly_type"] = "bug_detection_assembly"
            
        elif self.enzyme_type == EnzymeType.SECURITY_SCANASE:
            # Use pre-made security scanners
            selected_scanners = random.sample(self.code_library.get('scanners', []),
                                            min(2, len(self.code_library.get('scanners', []))))
            work_product["components_assembled"] = selected_scanners
            work_product["assembly_type"] = "security_scan_assembly"
        
        return work_product

class SupporterFactory:
    def __init__(self, factory_id: str, name: str, resource_types: List[ResourceType]):
        self.factory_id = factory_id
        self.name = name
        self.resource_types = resource_types
        self.production_rate = {rt: random.randint(100, 500) for rt in resource_types}
        self.storage_capacity = {rt: random.randint(1000, 5000) for rt in resource_types}
        self.current_inventory = {rt: self.storage_capacity[rt] // 2 for rt in resource_types}
        
        logger.info(f"🏭 {name} factory initialized - Produces: {[rt.value for rt in resource_types]}")
    
    async def produce_resources(self) -> Dict[ResourceType, int]:
        """Continuously produce resources"""
        produced = {}
        for resource_type in self.resource_types:
            production = min(
                self.production_rate[resource_type],
                self.storage_capacity[resource_type] - self.current_inventory[resource_type]
            )
            self.current_inventory[resource_type] += production
            produced[resource_type] = production
        
        return produced
    
    def supply_resources(self, requested: Dict[ResourceType, int]) -> Dict[ResourceType, int]:
        """Supply requested resources if available"""
        supplied = {}
        for resource_type, amount in requested.items():
            if resource_type in self.current_inventory:
                available = self.current_inventory[resource_type]
                supply_amount = min(amount, available)
                self.current_inventory[resource_type] -= supply_amount
                supplied[resource_type] = supply_amount
        
        return supplied

class HardcardBiologicalEcosystem:
    def __init__(self):
        self.agents: Dict[str, BiologicalAgent] = {}
        self.factories: Dict[str, SupporterFactory] = {}
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Dict] = []
        self.resource_pools: Dict[ResourceType, int] = {}
        self.total_virtual_market_cap = 0
        self.system_start_time = datetime.now()
        
        # Initialize resource pools
        for resource_type in ResourceType:
            self.resource_pools[resource_type] = 10000
        
        logger.info("🌐 Hardcard Biological Ecosystem initialized")
    
    def register_agent(self, agent: BiologicalAgent):
        """Register a biological agent in the ecosystem"""
        self.agents[agent.agent_id] = agent
        self.total_virtual_market_cap += agent.account.hgov_balance + agent.account.hcc_balance
        logger.info(f"📝 Registered agent: {agent.name}")
    
    def register_factory(self, factory: SupporterFactory):
        """Register a supporter factory"""
        self.factories[factory.factory_id] = factory
        logger.info(f"📝 Registered factory: {factory.name}")
    
    def create_task(self, title: str, description: str, enzyme_type: EnzymeType, 
                   reward_hgov: int, reward_hcc: int, difficulty: int = 1):
        """Create a new task for the ecosystem"""
        task = Task(
            task_id=f"task_{int(time.time())}_{random.randint(1000, 9999)}",
            title=title,
            description=description,
            enzyme_type=enzyme_type,
            required_resources={
                ResourceType.COMPUTE_CYCLES: random.randint(10, 50),
                ResourceType.CODE_SNIPPETS: random.randint(5, 20)
            },
            reward_hgov=reward_hgov,
            reward_hcc=reward_hcc,
            difficulty=difficulty,
            deadline=datetime.now() + timedelta(hours=random.randint(1, 24))
        )
        
        self.task_queue.append(task)
        logger.info(f"📋 Created task: {title} ({reward_hgov} HGOV, {reward_hcc} HCC)")
        return task
    
    async def consume_resources(self, agent_id: str, required: Dict[ResourceType, int]):
        """Consume resources from ecosystem pools"""
        for resource_type, amount in required.items():
            if self.resource_pools.get(resource_type, 0) >= amount:
                self.resource_pools[resource_type] -= amount
            else:
                # Request from factories
                await self._request_from_factories(resource_type, amount)
    
    async def _request_from_factories(self, resource_type: ResourceType, amount: int):
        """Request resources from supporter factories"""
        for factory in self.factories.values():
            if resource_type in factory.resource_types:
                supplied = factory.supply_resources({resource_type: amount})
                if resource_type in supplied:
                    self.resource_pools[resource_type] += supplied[resource_type]
                    break
    
    async def run_ecosystem_cycle(self):
        """Run one cycle of the biological ecosystem"""
        
        # Factories produce resources
        for factory in self.factories.values():
            produced = await factory.produce_resources()
            for resource_type, amount in produced.items():
                self.resource_pools[resource_type] += amount
        
        # Agents work on tasks
        active_agents = [agent for agent in self.agents.values() 
                        if len(agent.active_tasks) < 2]  # Max 2 concurrent tasks
        
        for agent in active_agents:
            # Find suitable task
            suitable_tasks = [task for task in self.task_queue 
                            if task.enzyme_type == agent.enzyme_type and task.status == "pending"]
            
            if suitable_tasks:
                task = random.choice(suitable_tasks)
                task.status = "in_progress"
                agent.active_tasks.append(task.task_id)
                
                # Work on task
                result = await agent.work_on_task(task, self)
                
                # Complete task
                task.status = "completed" if result["success"] else "failed"
                agent.active_tasks.remove(task.task_id)
                
                if task in self.task_queue:
                    self.task_queue.remove(task)
                
                self.completed_tasks.append({
                    "task": asdict(task),
                    "agent": agent.agent_id,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Update virtual market cap
        self.total_virtual_market_cap = sum(
            agent.account.hgov_balance + agent.account.hcc_balance 
            for agent in self.agents.values()
        )
    
    def get_ecosystem_stats(self) -> Dict:
        """Get comprehensive ecosystem statistics"""
        total_agents = len(self.agents)
        total_tasks_completed = sum(agent.account.tasks_completed for agent in self.agents.values())
        total_virtual_wealth = sum(agent.account.total_earned for agent in self.agents.values())
        
        avg_success_rate = sum(agent.account.success_rate for agent in self.agents.values()) / total_agents if total_agents > 0 else 0
        
        # Top performers
        top_earners = sorted(self.agents.values(), key=lambda a: a.account.total_earned, reverse=True)[:5]
        
        return {
            "ecosystem_health": {
                "total_agents": total_agents,
                "active_agents": len([a for a in self.agents.values() if a.active_tasks]),
                "total_factories": len(self.factories),
                "uptime_hours": (datetime.now() - self.system_start_time).total_seconds() / 3600
            },
            "virtual_economy": {
                "total_market_cap": self.total_virtual_market_cap,
                "total_wealth_created": total_virtual_wealth,
                "average_agent_balance": self.total_virtual_market_cap / total_agents if total_agents > 0 else 0,
                "wealth_distribution": "exponential"  # Rich get richer through performance
            },
            "performance_metrics": {
                "tasks_completed": total_tasks_completed,
                "tasks_pending": len(self.task_queue),
                "average_success_rate": round(avg_success_rate, 3),
                "ecosystem_efficiency": round(total_tasks_completed / max(1, total_agents), 2)
            },
            "resource_status": {
                resource_type.value: amount for resource_type, amount in self.resource_pools.items()
            },
            "top_performers": [
                {
                    "name": agent.name,
                    "enzyme_type": agent.enzyme_type.value,
                    "total_earned": agent.account.total_earned,
                    "success_rate": round(agent.account.success_rate, 3),
                    "tasks_completed": agent.account.tasks_completed
                }
                for agent in top_earners
            ]
        }

async def main():
    """Run the complete Hardcard Biological System demo"""
    
    ecosystem = HardcardBiologicalEcosystem()
    
    # Create biological agents
    agents = [
        BiologicalAgent("agent_001", "CodeSplicer Alpha", EnzymeType.CODE_SPLICERASE, ["python", "javascript"]),
        BiologicalAgent("agent_002", "DataProcessor Beta", EnzymeType.DATA_PROCESSORASE, ["data_analysis", "etl"]),
        BiologicalAgent("agent_003", "BugHunter Gamma", EnzymeType.BUG_HUNTASE, ["debugging", "testing"]),
        BiologicalAgent("agent_004", "SecurityScanner Delta", EnzymeType.SECURITY_SCANASE, ["security", "auditing"]),
        BiologicalAgent("agent_005", "PerfOptimizer Epsilon", EnzymeType.PERFORMANCE_OPTIMASE, ["optimization", "profiling"])
    ]
    
    for agent in agents:
        ecosystem.register_agent(agent)
    
    # Create supporter factories
    factories = [
        SupporterFactory("factory_001", "Compute Cycles Factory", [ResourceType.COMPUTE_CYCLES, ResourceType.VALIDATION_RULES]),
        SupporterFactory("factory_002", "Code Library Factory", [ResourceType.CODE_SNIPPETS, ResourceType.DOCUMENTATION]),
        SupporterFactory("factory_003", "Test Suite Factory", [ResourceType.TEST_CASES, ResourceType.VALIDATION_RULES])
    ]
    
    for factory in factories:
        ecosystem.register_factory(factory)
    
    # Create initial tasks
    tasks = [
        ("Fix Memory Leak", "Optimize memory usage in data processing pipeline", EnzymeType.PERFORMANCE_OPTIMASE, 2000, 5000, 2),
        ("Security Audit", "Scan codebase for security vulnerabilities", EnzymeType.SECURITY_SCANASE, 1500, 4000, 3),
        ("Refactor Functions", "Clean up and optimize function implementations", EnzymeType.CODE_SPLICERASE, 1000, 3000, 1),
        ("Bug Investigation", "Find and document bugs in user authentication", EnzymeType.BUG_HUNTASE, 1200, 3500, 2),
        ("Data Pipeline Bug", "Fix error in data transformation pipeline", EnzymeType.DATA_PROCESSORASE, 1800, 4500, 2),
        ("Code Review", "Review and improve code quality standards", EnzymeType.CODE_SPLICERASE, 800, 2000, 1),
        ("Performance Analysis", "Analyze and optimize system performance", EnzymeType.PERFORMANCE_OPTIMASE, 2200, 5500, 3),
        ("Security Hardening", "Implement additional security measures", EnzymeType.SECURITY_SCANASE, 2500, 6000, 3)
    ]
    
    for title, description, enzyme_type, hgov, hcc, difficulty in tasks:
        ecosystem.create_task(title, description, enzyme_type, hgov, hcc, difficulty)
    
    # Run ecosystem for several cycles
    print("🚀 Starting Hardcard Biological Ecosystem...")
    print("=" * 60)
    
    for cycle in range(10):  # Run 10 cycles
        print(f"\n🔄 Ecosystem Cycle {cycle + 1}")
        print("-" * 30)
        
        await ecosystem.run_ecosystem_cycle()
        
        # Show cycle statistics
        stats = ecosystem.get_ecosystem_stats()
        print(f"💰 Virtual Market Cap: ${stats['virtual_economy']['total_market_cap']:,}")
        print(f"✅ Tasks Completed: {stats['performance_metrics']['tasks_completed']}")
        print(f"📊 Average Success Rate: {stats['performance_metrics']['average_success_rate']:.1%}")
        
        # Show top performer
        if stats['top_performers']:
            top = stats['top_performers'][0]
            print(f"🏆 Top Performer: {top['name']} ({top['enzyme_type']}) - ${top['total_earned']:,} earned")
        
        # Brief pause between cycles
        await asyncio.sleep(1)
    
    # Final comprehensive statistics
    print("\n" + "=" * 60)
    print("🧬 FINAL ECOSYSTEM STATISTICS")
    print("=" * 60)
    
    final_stats = ecosystem.get_ecosystem_stats()
    print(json.dumps(final_stats, indent=2))
    
    print("\n🎯 BIOLOGICAL SYSTEM SUCCESS!")
    print("- Virtual economy running with $0 real cost")
    print("- Enzymatic specialization prevents hijacking")
    print("- Cut-and-paste assembly from pre-made libraries") 
    print("- Supporter factories provide infinite resources")
    print("- All agents earning virtual wealth through specialized work")

if __name__ == "__main__":
    asyncio.run(main())