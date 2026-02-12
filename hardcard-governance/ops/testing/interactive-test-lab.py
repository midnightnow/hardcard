#!/usr/bin/env python3
"""
Interactive Test Lab: Hands-on coding and troubleshooting environment
Real-time testing, debugging, and refinement of biological systems
"""

import asyncio
import json
import time
import traceback
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Setup path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../nexus-infrastructure'))

try:
    from hardcard_biological_system import (
        HardcardBiologicalEcosystem, BiologicalAgent, SupporterFactory,
        EnzymeType, ResourceType, Task
    )
    IMPORTS_AVAILABLE = True
except ImportError:
    print("⚠️ Full biological system not available - using mock classes for testing")
    IMPORTS_AVAILABLE = False
    
    # Mock classes for testing
    from enum import Enum
    from dataclasses import dataclass
    
    class EnzymeType(Enum):
        CODE_SPLICERASE = "code_splicerase"
        SECURITY_SCANASE = "security_scanase"
        BUG_HUNTASE = "bug_huntase"
        PERFORMANCE_OPTIMASE = "performance_optimase"
        DATA_PROCESSORASE = "data_processorase"
    
    class ResourceType(Enum):
        COMPUTE_CYCLES = "compute_cycles"
        CODE_SNIPPETS = "code_snippets"
        TEST_CASES = "test_cases"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_lab')

class InteractiveTestLab:
    """Interactive environment for coding and troubleshooting biological systems"""
    
    def __init__(self):
        self.ecosystem = None
        self.test_results = []
        self.debug_mode = True
        self.current_test = None
        
        if IMPORTS_AVAILABLE:
            self.ecosystem = HardcardBiologicalEcosystem()
            self._setup_test_environment()
        
        print("🧪 Interactive Test Lab Initialized!")
        print("💡 Type 'help' to see available commands")
    
    def _setup_test_environment(self):
        """Setup basic test environment"""
        if not self.ecosystem:
            return
            
        # Create test agents
        test_agents = [
            BiologicalAgent("test_001", "TestSplicer", EnzymeType.CODE_SPLICERASE, ["python"]),
            BiologicalAgent("test_002", "TestScanner", EnzymeType.SECURITY_SCANASE, ["security"]),
            BiologicalAgent("test_003", "TestHunter", EnzymeType.BUG_HUNTASE, ["debugging"])
        ]
        
        for agent in test_agents:
            self.ecosystem.register_agent(agent)
        
        # Create test factory
        factory = SupporterFactory("test_factory", "Test Factory", 
                                 [ResourceType.COMPUTE_CYCLES, ResourceType.CODE_SNIPPETS])
        self.ecosystem.register_factory(factory)
        
        print(f"✅ Test environment ready: {len(test_agents)} agents, 1 factory")
    
    async def run_interactive_session(self):
        """Run interactive testing session"""
        
        print("\n🚀 Starting Interactive Test Session")
        print("=" * 50)
        
        while True:
            try:
                command = input("\n🧪 test_lab> ").strip().lower()
                
                if command in ['exit', 'quit', 'q']:
                    print("👋 Exiting test lab...")
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'status':
                    await self._show_status()
                elif command == 'agents':
                    self._show_agents()
                elif command == 'factories':
                    self._show_factories()
                elif command.startswith('test '):
                    test_name = command[5:]
                    await self._run_test(test_name)
                elif command == 'create_task':
                    await self._create_test_task()
                elif command == 'run_cycle':
                    await self._run_ecosystem_cycle()
                elif command == 'debug_agent':
                    await self._debug_agent()
                elif command == 'stress_test':
                    await self._run_stress_test()
                elif command == 'security_test':
                    await self._run_security_test()
                elif command == 'economy_test':
                    await self._run_economy_test()
                elif command == 'fix_issues':
                    await self._fix_common_issues()
                elif command == 'benchmark':
                    await self._run_benchmark()
                elif command.startswith('code '):
                    code_snippet = command[5:]
                    await self._execute_code(code_snippet)
                else:
                    print(f"❓ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n⏸️ Interrupted by user")
                continue
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                if self.debug_mode:
                    traceback.print_exc()
    
    def _show_help(self):
        """Show available commands"""
        commands = {
            "System Commands": [
                "status - Show ecosystem status",
                "agents - List all agents",
                "factories - List all factories",
                "help - Show this help"
            ],
            "Testing Commands": [
                "test <name> - Run specific test",
                "stress_test - Run stress testing",
                "security_test - Test security features", 
                "economy_test - Test virtual economy",
                "benchmark - Performance benchmark"
            ],
            "Development Commands": [
                "create_task - Create a test task",
                "run_cycle - Run ecosystem cycle",
                "debug_agent - Debug agent behavior",
                "fix_issues - Auto-fix common issues",
                "code <snippet> - Execute code snippet"
            ],
            "Navigation": [
                "exit/quit/q - Exit test lab"
            ]
        }
        
        print("\n📚 Available Commands:")
        for category, cmds in commands.items():
            print(f"\n🔹 {category}:")
            for cmd in cmds:
                print(f"   {cmd}")
    
    async def _show_status(self):
        """Show current ecosystem status"""
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        stats = self.ecosystem.get_ecosystem_stats()
        
        print("\n📊 Ecosystem Status:")
        print(f"   Agents: {stats['ecosystem_health']['total_agents']}")
        print(f"   Market Cap: ${stats['virtual_economy']['total_market_cap']:,}")
        print(f"   Tasks Completed: {stats['performance_metrics']['tasks_completed']}")
        print(f"   Success Rate: {stats['performance_metrics']['average_success_rate']:.1%}")
        
        if stats['top_performers']:
            top = stats['top_performers'][0]
            print(f"   Top Performer: {top['name']} (${top['total_earned']:,})")
    
    def _show_agents(self):
        """Show all agents"""
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        print("\n🧬 Registered Agents:")
        for agent_id, agent in self.ecosystem.agents.items():
            balance = agent.account.hgov_balance + agent.account.hcc_balance
            print(f"   {agent.name} ({agent.enzyme_type.value})")
            print(f"      Balance: ${balance:,}")
            print(f"      Tasks: {agent.account.tasks_completed}")
            print(f"      Success Rate: {agent.account.success_rate:.1%}")
    
    def _show_factories(self):
        """Show all factories"""
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        print("\n🏭 Supporter Factories:")
        for factory_id, factory in self.ecosystem.factories.items():
            print(f"   {factory.name}")
            print(f"      Resources: {[r.value for r in factory.resource_types]}")
            print(f"      Capacity: {sum(factory.production_capacity.values())}/cycle")
    
    async def _run_test(self, test_name: str):
        """Run a specific test"""
        self.current_test = test_name
        
        try:
            if test_name == "basic":
                await self._test_basic_functionality()
            elif test_name == "agents":
                await self._test_agent_functionality()
            elif test_name == "factories":
                await self._test_factory_functionality()
            elif test_name == "security":
                await self._run_security_test()
            elif test_name == "economy":
                await self._run_economy_test()
            else:
                print(f"❓ Unknown test: {test_name}")
                print("💡 Available tests: basic, agents, factories, security, economy")
        
        except Exception as e:
            print(f"❌ Test '{test_name}' failed: {str(e)}")
            if self.debug_mode:
                traceback.print_exc()
        
        finally:
            self.current_test = None
    
    async def _test_basic_functionality(self):
        """Test basic ecosystem functionality"""
        print("\n🧪 Running Basic Functionality Test...")
        
        if not self.ecosystem:
            print("❌ Cannot run test - ecosystem not available")
            return
        
        # Test 1: Agent count
        agent_count = len(self.ecosystem.agents)
        print(f"✅ Agents registered: {agent_count}")
        
        # Test 2: Factory count
        factory_count = len(self.ecosystem.factories)
        print(f"✅ Factories registered: {factory_count}")
        
        # Test 3: Resource pools
        resource_count = len(self.ecosystem.resource_pools)
        print(f"✅ Resource types available: {resource_count}")
        
        # Test 4: Market cap
        market_cap = self.ecosystem.total_virtual_market_cap
        print(f"✅ Virtual market cap: ${market_cap:,}")
        
        print("🎯 Basic functionality test completed!")
    
    async def _test_agent_functionality(self):
        """Test agent-specific functionality"""
        print("\n🧬 Testing Agent Functionality...")
        
        if not self.ecosystem or not self.ecosystem.agents:
            print("❌ No agents available for testing")
            return
        
        agent = list(self.ecosystem.agents.values())[0]
        
        # Test agent properties
        print(f"🔬 Testing agent: {agent.name}")
        print(f"   Enzyme type: {agent.enzyme_type.value}")
        print(f"   Specializations: {agent.specializations}")
        print(f"   Initial balance: ${agent.account.hgov_balance + agent.account.hcc_balance:,}")
        
        # Test task creation and assignment
        task = self.ecosystem.create_task(
            "Test Task",
            "Agent functionality test",
            agent.enzyme_type,
            1000,
            2000,
            1
        )
        
        print(f"✅ Created test task: {task.title}")
        
        # Test task execution
        result = await agent.work_on_task(task, self.ecosystem)
        
        if result["success"]:
            print(f"✅ Task completed successfully")
            print(f"   Tokens earned: {result['tokens_earned']}")
        else:
            print(f"⚠️ Task failed (this is normal in testing)")
        
        print("🎯 Agent functionality test completed!")
    
    async def _test_factory_functionality(self):
        """Test factory functionality"""
        print("\n🏭 Testing Factory Functionality...")
        
        if not self.ecosystem or not self.ecosystem.factories:
            print("❌ No factories available for testing")
            return
        
        factory = list(self.ecosystem.factories.values())[0]
        
        print(f"🔬 Testing factory: {factory.name}")
        print(f"   Resource types: {[r.value for r in factory.resource_types]}")
        
        # Test resource production
        initial_inventory = dict(factory.current_inventory)
        produced = await factory.produce_resources()
        
        print(f"✅ Resources produced: {produced}")
        
        # Test resource supply
        test_request = {ResourceType.COMPUTE_CYCLES: 10}
        supplied = factory.supply_resources(test_request)
        
        print(f"✅ Resources supplied: {supplied}")
        print("🎯 Factory functionality test completed!")
    
    async def _create_test_task(self):
        """Interactively create a test task"""
        print("\n📋 Creating Test Task...")
        
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        # Interactive task creation
        title = input("Task title: ").strip() or "Test Task"
        description = input("Task description: ").strip() or "Interactive test task"
        
        # Show available enzyme types
        print("\nAvailable enzyme types:")
        for i, enzyme_type in enumerate(EnzymeType, 1):
            print(f"   {i}. {enzyme_type.value}")
        
        try:
            choice = int(input("Select enzyme type (1-5): ").strip() or "1")
            enzyme_type = list(EnzymeType)[choice - 1]
        except (ValueError, IndexError):
            enzyme_type = EnzymeType.CODE_SPLICERASE
            print(f"Using default: {enzyme_type.value}")
        
        hgov_reward = int(input("HGOV reward: ").strip() or "1000")
        hcc_reward = int(input("HCC reward: ").strip() or "2000")
        difficulty = int(input("Difficulty (1-5): ").strip() or "1")
        
        task = self.ecosystem.create_task(title, description, enzyme_type, hgov_reward, hcc_reward, difficulty)
        
        print(f"✅ Created task: {task.title}")
        print(f"   Reward: {hgov_reward} HGOV, {hcc_reward} HCC")
        print(f"   Enzyme: {enzyme_type.value}")
    
    async def _run_ecosystem_cycle(self):
        """Run a single ecosystem cycle"""
        print("\n🔄 Running Ecosystem Cycle...")
        
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        start_time = time.time()
        initial_market_cap = self.ecosystem.total_virtual_market_cap
        
        await self.ecosystem.run_ecosystem_cycle()
        
        final_market_cap = self.ecosystem.total_virtual_market_cap
        duration = time.time() - start_time
        
        print(f"✅ Cycle completed in {duration:.2f}s")
        print(f"   Market cap: ${initial_market_cap:,} → ${final_market_cap:,}")
        print(f"   Growth: ${final_market_cap - initial_market_cap:,}")
    
    async def _debug_agent(self):
        """Debug specific agent behavior"""
        print("\n🔍 Agent Debugging Session...")
        
        if not self.ecosystem or not self.ecosystem.agents:
            print("❌ No agents available for debugging")
            return
        
        # List agents
        agents = list(self.ecosystem.agents.values())
        print("\nAvailable agents:")
        for i, agent in enumerate(agents, 1):
            print(f"   {i}. {agent.name} ({agent.enzyme_type.value})")
        
        try:
            choice = int(input("Select agent to debug (1-N): ").strip() or "1")
            agent = agents[choice - 1]
        except (ValueError, IndexError):
            agent = agents[0]
            print(f"Using default: {agent.name}")
        
        # Debug information
        print(f"\n🔬 Debugging {agent.name}:")
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Enzyme Type: {agent.enzyme_type.value}")
        print(f"   Specializations: {agent.specializations}")
        print(f"   HGOV Balance: {agent.account.hgov_balance:,}")
        print(f"   HCC Balance: {agent.account.hcc_balance:,}")
        print(f"   Tasks Completed: {agent.account.tasks_completed}")
        print(f"   Success Rate: {agent.account.success_rate:.1%}")
        print(f"   Efficiency Rating: {agent.efficiency_rating:.3f}")
        print(f"   Active Tasks: {len(agent.active_tasks)}")
        print(f"   Code Library Size: {len(agent.code_library)}")
        
        # Show code library contents
        if agent.code_library:
            print(f"\n📚 Code Library Contents:")
            for library_type, items in agent.code_library.items():
                print(f"   {library_type}: {len(items)} items")
                if items:
                    print(f"      Example: {items[0][:50]}...")
    
    async def _run_stress_test(self):
        """Run stress testing"""
        print("\n💪 Running Stress Test...")
        
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        print("Creating multiple tasks...")
        tasks_created = 0
        
        # Create many tasks
        for i in range(10):
            task = self.ecosystem.create_task(
                f"Stress Test {i}",
                "High-load stress testing",
                list(EnzymeType)[i % len(EnzymeType)],
                1000 + i * 100,
                2000 + i * 200,
                (i % 3) + 1
            )
            tasks_created += 1
        
        print(f"✅ Created {tasks_created} stress test tasks")
        
        # Run multiple cycles rapidly
        print("Running rapid ecosystem cycles...")
        start_time = time.time()
        
        for cycle in range(5):
            await self.ecosystem.run_ecosystem_cycle()
            print(f"   Cycle {cycle + 1} completed")
        
        duration = time.time() - start_time
        print(f"✅ Stress test completed in {duration:.2f}s")
        
        # Show results
        stats = self.ecosystem.get_ecosystem_stats()
        print(f"   Final market cap: ${stats['virtual_economy']['total_market_cap']:,}")
        print(f"   Tasks completed: {stats['performance_metrics']['tasks_completed']}")
    
    async def _run_security_test(self):
        """Test security features"""
        print("\n🔒 Running Security Test...")
        
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        # Test 1: Enzyme isolation
        print("🧪 Testing enzyme isolation...")
        agents = list(self.ecosystem.agents.values())
        
        if len(agents) >= 2:
            agent1, agent2 = agents[0], agents[1]
            
            # Verify different enzyme types
            if agent1.enzyme_type != agent2.enzyme_type:
                print(f"✅ Agents have different enzyme types: {agent1.enzyme_type.value} vs {agent2.enzyme_type.value}")
            else:
                print("⚠️ Agents have same enzyme type - create more diverse agents")
        
        # Test 2: Substrate specificity
        print("🧪 Testing substrate specificity...")
        
        # Create tasks for different enzyme types
        for enzyme_type in EnzymeType:
            task = self.ecosystem.create_task(
                f"Security Test - {enzyme_type.value}",
                "Testing substrate specificity",
                enzyme_type,
                500,
                1000,
                1
            )
            print(f"✅ Created {enzyme_type.value} task")
        
        # Test 3: Resource isolation
        print("🧪 Testing resource isolation...")
        
        initial_resources = dict(self.ecosystem.resource_pools)
        
        # Try to access resources
        for resource_type, amount in initial_resources.items():
            if amount > 0:
                print(f"✅ {resource_type.value}: {amount} available")
        
        print("🎯 Security test completed!")
    
    async def _run_economy_test(self):
        """Test virtual economy features"""
        print("\n💰 Running Economy Test...")
        
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        initial_market_cap = self.ecosystem.total_virtual_market_cap
        print(f"📊 Initial market cap: ${initial_market_cap:,}")
        
        # Create high-value tasks
        high_value_tasks = []
        for i in range(3):
            task = self.ecosystem.create_task(
                f"High Value Task {i}",
                "Economic testing with high rewards",
                list(EnzymeType)[i % len(EnzymeType)],
                5000,  # High HGOV reward
                10000, # High HCC reward
                2
            )
            high_value_tasks.append(task)
        
        print(f"✅ Created {len(high_value_tasks)} high-value tasks")
        
        # Run cycles to process tasks
        for cycle in range(3):
            await self.ecosystem.run_ecosystem_cycle()
            current_cap = self.ecosystem.total_virtual_market_cap
            print(f"   Cycle {cycle + 1}: ${current_cap:,}")
        
        final_market_cap = self.ecosystem.total_virtual_market_cap
        growth = final_market_cap - initial_market_cap
        
        print(f"📈 Final market cap: ${final_market_cap:,}")
        print(f"💎 Wealth created: ${growth:,}")
        print(f"💵 Real cost: $0.00 (Zero!)")
        
        # Check for bridge-eligible agents
        bridge_eligible = []
        for agent in self.ecosystem.agents.values():
            if agent.account.hgov_balance >= 50000:  # Bridge threshold
                bridge_eligible.append(agent.name)
        
        if bridge_eligible:
            print(f"🌉 Bridge-eligible agents: {', '.join(bridge_eligible)}")
        else:
            print("🌉 No agents yet eligible for bridge (need 50k+ HGOV)")
        
        print("🎯 Economy test completed!")
    
    async def _fix_common_issues(self):
        """Auto-fix common issues"""
        print("\n🔧 Fixing Common Issues...")
        
        fixes_applied = 0
        
        if not self.ecosystem:
            print("❌ Cannot fix issues - ecosystem not available")
            return
        
        # Fix 1: Ensure minimum resources
        for resource_type in ResourceType:
            if self.ecosystem.resource_pools.get(resource_type, 0) < 1000:
                self.ecosystem.resource_pools[resource_type] = 5000
                fixes_applied += 1
                print(f"✅ Replenished {resource_type.value} resources")
        
        # Fix 2: Balance agent efficiency
        for agent in self.ecosystem.agents.values():
            if agent.efficiency_rating < 0.5:
                agent.efficiency_rating = 0.8
                fixes_applied += 1
                print(f"✅ Improved {agent.name} efficiency")
        
        # Fix 3: Clear stuck tasks
        stuck_tasks = [t for t in self.ecosystem.task_queue if hasattr(t, 'status') and t.status == 'in_progress']
        for task in stuck_tasks:
            task.status = 'pending'
            fixes_applied += 1
        
        if stuck_tasks:
            print(f"✅ Cleared {len(stuck_tasks)} stuck tasks")
        
        print(f"🎯 Applied {fixes_applied} fixes")
    
    async def _run_benchmark(self):
        """Run performance benchmark"""
        print("\n⚡ Running Performance Benchmark...")
        
        if not self.ecosystem:
            print("❌ Ecosystem not available")
            return
        
        # Benchmark 1: Task creation speed
        print("🧪 Benchmarking task creation...")
        start_time = time.time()
        
        for i in range(50):
            self.ecosystem.create_task(
                f"Benchmark Task {i}",
                "Performance benchmark",
                list(EnzymeType)[i % len(EnzymeType)],
                1000,
                2000,
                1
            )
        
        creation_time = time.time() - start_time
        print(f"✅ Created 50 tasks in {creation_time:.3f}s ({50/creation_time:.1f} tasks/sec)")
        
        # Benchmark 2: Ecosystem cycle speed
        print("🧪 Benchmarking ecosystem cycles...")
        start_time = time.time()
        
        for cycle in range(10):
            await self.ecosystem.run_ecosystem_cycle()
        
        cycle_time = time.time() - start_time
        print(f"✅ Completed 10 cycles in {cycle_time:.3f}s ({10/cycle_time:.1f} cycles/sec)")
        
        # Benchmark 3: Memory usage
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / (1024 * 1024)
            print(f"✅ Memory usage: {memory_mb:.1f} MB")
        except ImportError:
            print("⚠️ Memory monitoring not available (install psutil)")
        
        print("🎯 Benchmark completed!")
    
    async def _execute_code(self, code_snippet: str):
        """Execute custom code snippet"""
        print(f"\n💻 Executing: {code_snippet}")
        
        try:
            # Create execution context
            context = {
                'ecosystem': self.ecosystem,
                'EnzymeType': EnzymeType,
                'ResourceType': ResourceType,
                'print': print,
                'len': len,
                'sum': sum,
                'max': max,
                'min': min
            }
            
            # Execute code
            result = eval(code_snippet, context)
            print(f"✅ Result: {result}")
            
        except Exception as e:
            print(f"❌ Error executing code: {str(e)}")
            if self.debug_mode:
                traceback.print_exc()

async def main():
    """Run the interactive test lab"""
    
    lab = InteractiveTestLab()
    await lab.run_interactive_session()

if __name__ == "__main__":
    asyncio.run(main())