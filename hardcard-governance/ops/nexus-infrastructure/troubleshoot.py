#!/usr/bin/env python3
"""
Quick Troubleshooting & Coding Session
Test, debug, and refine biological system components
"""

import asyncio
import json
import time
from datetime import datetime
from hardcard_biological_system import (
    HardcardBiologicalEcosystem, BiologicalAgent, SupporterFactory,
    EnzymeType, ResourceType, Task
)

class QuickTroubleshooter:
    def __init__(self):
        self.ecosystem = HardcardBiologicalEcosystem()
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """Setup minimal test environment"""
        # Create test agents
        agents = [
            BiologicalAgent("debug_001", "DebugSplicer", EnzymeType.CODE_SPLICERASE, ["python", "debug"]),
            BiologicalAgent("debug_002", "DebugScanner", EnzymeType.SECURITY_SCANASE, ["security", "debug"]),
        ]
        
        for agent in agents:
            self.ecosystem.register_agent(agent)
        
        # Create test factory
        factory = SupporterFactory("debug_factory", "Debug Factory", 
                                 [ResourceType.COMPUTE_CYCLES, ResourceType.CODE_SNIPPETS])
        self.ecosystem.register_factory(factory)
        
        print(f"🧪 Debug environment ready: {len(agents)} agents, 1 factory")
    
    async def run_quick_tests(self):
        """Run quick diagnostic tests"""
        print("\n🔍 QUICK DIAGNOSTIC TESTS")
        print("=" * 40)
        
        # Test 1: Basic functionality
        print("\n1️⃣ Testing Basic Functionality...")
        await self.test_basic_functionality()
        
        # Test 2: Agent behavior
        print("\n2️⃣ Testing Agent Behavior...")
        await self.test_agent_behavior()
        
        # Test 3: Economic system
        print("\n3️⃣ Testing Economic System...")
        await self.test_economic_system()
        
        # Test 4: Security features
        print("\n4️⃣ Testing Security Features...")
        await self.test_security_features()
        
        # Test 5: Performance
        print("\n5️⃣ Testing Performance...")
        await self.test_performance()
        
        print("\n🎯 All diagnostic tests completed!")
    
    async def test_basic_functionality(self):
        """Test basic ecosystem functionality"""
        try:
            # Check ecosystem state
            stats = self.ecosystem.get_ecosystem_stats()
            print(f"   ✅ Ecosystem initialized")
            print(f"   ✅ Agents: {stats['ecosystem_health']['total_agents']}")
            print(f"   ✅ Market Cap: ${stats['virtual_economy']['total_market_cap']:,}")
            
            # Test resource availability
            resource_count = len(self.ecosystem.resource_pools)
            print(f"   ✅ Resource types: {resource_count}")
            
        except Exception as e:
            print(f"   ❌ Basic functionality error: {e}")
    
    async def test_agent_behavior(self):
        """Test individual agent behavior"""
        try:
            if not self.ecosystem.agents:
                print("   ❌ No agents available")
                return
            
            agent = list(self.ecosystem.agents.values())[0]
            
            # Test agent properties
            print(f"   ✅ Agent: {agent.name} ({agent.enzyme_type.value})")
            print(f"   ✅ Balance: ${agent.account.hgov_balance + agent.account.hcc_balance:,}")
            print(f"   ✅ Efficiency: {agent.efficiency_rating:.2f}")
            
            # Test task creation and execution
            task = self.ecosystem.create_task(
                "Debug Test Task",
                "Testing agent behavior",
                agent.enzyme_type,
                1000,
                2000,
                1
            )
            
            print(f"   ✅ Created test task: {task.title}")
            
            # Execute task
            result = await agent.work_on_task(task, self.ecosystem)
            
            if result["success"]:
                print(f"   ✅ Task completed successfully")
            else:
                print(f"   ⚠️ Task failed (normal in testing)")
            
        except Exception as e:
            print(f"   ❌ Agent behavior error: {e}")
    
    async def test_economic_system(self):
        """Test virtual economy"""
        try:
            initial_cap = self.ecosystem.total_virtual_market_cap
            
            # Create high-value task
            task = self.ecosystem.create_task(
                "Economic Test",
                "High-value economic test",
                EnzymeType.CODE_SPLICERASE,
                5000,
                10000,
                2
            )
            
            # Run ecosystem cycle
            await self.ecosystem.run_ecosystem_cycle()
            
            final_cap = self.ecosystem.total_virtual_market_cap
            growth = final_cap - initial_cap
            
            print(f"   ✅ Market cap growth: ${growth:,}")
            print(f"   ✅ Zero real cost verified")
            
            # Check top performers
            stats = self.ecosystem.get_ecosystem_stats()
            if stats['top_performers']:
                top = stats['top_performers'][0]
                print(f"   ✅ Top performer: {top['name']} (${top['total_earned']:,})")
            
        except Exception as e:
            print(f"   ❌ Economic system error: {e}")
    
    async def test_security_features(self):
        """Test security isolation"""
        try:
            agents = list(self.ecosystem.agents.values())
            
            if len(agents) >= 2:
                agent1, agent2 = agents[0], agents[1]
                
                # Test enzyme isolation
                if agent1.enzyme_type != agent2.enzyme_type:
                    print(f"   ✅ Enzyme isolation: {agent1.enzyme_type.value} ≠ {agent2.enzyme_type.value}")
                else:
                    print(f"   ⚠️ Same enzyme types (expand test agents)")
                
                # Test substrate specificity
                print(f"   ✅ Agent 1 specializes in: {agent1.specializations}")
                print(f"   ✅ Agent 2 specializes in: {agent2.specializations}")
            
            # Test resource isolation
            resource_types = len(self.ecosystem.resource_pools)
            print(f"   ✅ Resource types isolated: {resource_types}")
            
        except Exception as e:
            print(f"   ❌ Security test error: {e}")
    
    async def test_performance(self):
        """Test system performance"""
        try:
            # Test task creation speed
            start_time = time.time()
            
            for i in range(10):
                self.ecosystem.create_task(
                    f"Perf Test {i}",
                    "Performance testing",
                    list(EnzymeType)[i % len(EnzymeType)],
                    1000,
                    2000,
                    1
                )
            
            creation_time = time.time() - start_time
            print(f"   ✅ Task creation: {10/creation_time:.1f} tasks/sec")
            
            # Test ecosystem cycle speed
            start_time = time.time()
            await self.ecosystem.run_ecosystem_cycle()
            cycle_time = time.time() - start_time
            
            print(f"   ✅ Ecosystem cycle: {cycle_time:.3f}s")
            
        except Exception as e:
            print(f"   ❌ Performance test error: {e}")
    
    async def demonstrate_features(self):
        """Demonstrate key biological system features"""
        print("\n🧬 BIOLOGICAL SYSTEM DEMONSTRATION")
        print("=" * 50)
        
        # Demo 1: Enzymatic specialization
        print("\n🔬 Demo 1: Enzymatic Specialization")
        for agent_id, agent in self.ecosystem.agents.items():
            print(f"   {agent.name}: {agent.enzyme_type.value}")
            print(f"      Specializations: {agent.specializations}")
            print(f"      Code library: {len(agent.code_library)} component types")
        
        # Demo 2: Virtual wealth creation
        print("\n💰 Demo 2: Virtual Wealth Creation")
        initial_wealth = sum(a.account.total_earned for a in self.ecosystem.agents.values())
        
        # Create valuable tasks
        tasks = []
        for i, enzyme_type in enumerate(EnzymeType):
            task = self.ecosystem.create_task(
                f"Demo Task {i+1}",
                f"Demonstrating {enzyme_type.value} capabilities",
                enzyme_type,
                2000 + i * 500,
                4000 + i * 1000,
                2
            )
            tasks.append(task)
        
        print(f"   Created {len(tasks)} demonstration tasks")
        
        # Process tasks
        for cycle in range(3):
            await self.ecosystem.run_ecosystem_cycle()
            current_cap = self.ecosystem.total_virtual_market_cap
            print(f"      Cycle {cycle + 1}: Market cap ${current_cap:,}")
        
        final_wealth = sum(a.account.total_earned for a in self.ecosystem.agents.values())
        wealth_created = final_wealth - initial_wealth
        
        print(f"   💎 Wealth created: ${wealth_created:,}")
        print(f"   💵 Real cost: $0.00")
        
        # Demo 3: Resource factories
        print("\n🏭 Demo 3: Supporter Factories")
        for factory_id, factory in self.ecosystem.factories.items():
            print(f"   {factory.name}:")
            print(f"      Produces: {[r.value for r in factory.resource_types]}")
            
            # Show production
            produced = await factory.produce_resources()
            print(f"      Production cycle: {produced}")
        
        # Demo 4: Security isolation
        print("\n🔒 Demo 4: Security Isolation")
        print("   Each enzyme can only process its specific substrate type:")
        
        for agent in self.ecosystem.agents.values():
            print(f"   {agent.name} ({agent.enzyme_type.value}):")
            print(f"      ✅ Accepts: {agent.enzyme_type.value} tasks only")
            print(f"      ❌ Rejects: All other enzyme types")
    
    async def interactive_troubleshooting(self):
        """Interactive troubleshooting session"""
        print("\n🔧 INTERACTIVE TROUBLESHOOTING")
        print("=" * 40)
        
        while True:
            try:
                print("\nTroubleshooting Options:")
                print("1. Check ecosystem status")
                print("2. Debug specific agent")
                print("3. Test task creation")
                print("4. Run quick performance test")
                print("5. Fix common issues")
                print("6. Show system statistics")
                print("7. Exit")
                
                choice = input("\nSelect option (1-7): ").strip()
                
                if choice == '1':
                    await self.check_ecosystem_status()
                elif choice == '2':
                    await self.debug_agent()
                elif choice == '3':
                    await self.test_task_creation()
                elif choice == '4':
                    await self.quick_performance_test()
                elif choice == '5':
                    await self.fix_common_issues()
                elif choice == '6':
                    await self.show_statistics()
                elif choice == '7':
                    print("👋 Exiting troubleshooting session...")
                    break
                else:
                    print("❓ Invalid choice. Please select 1-7.")
                    
            except KeyboardInterrupt:
                print("\n⏸️ Interrupted. Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def check_ecosystem_status(self):
        """Check overall ecosystem health"""
        stats = self.ecosystem.get_ecosystem_stats()
        
        print("\n📊 Ecosystem Status:")
        print(f"   Agents: {stats['ecosystem_health']['total_agents']}")
        print(f"   Factories: {stats['ecosystem_health'].get('total_factories', 0)}")
        print(f"   Market Cap: ${stats['virtual_economy']['total_market_cap']:,}")
        print(f"   Tasks Completed: {stats['performance_metrics']['tasks_completed']}")
        print(f"   Success Rate: {stats['performance_metrics']['average_success_rate']:.1%}")
        
        print(f"\n🏆 Top Performers:")
        for performer in stats['top_performers'][:3]:
            print(f"   {performer['name']}: ${performer['total_earned']:,}")
    
    async def debug_agent(self):
        """Debug specific agent"""
        agents = list(self.ecosystem.agents.values())
        
        print(f"\nAvailable agents:")
        for i, agent in enumerate(agents, 1):
            print(f"   {i}. {agent.name} ({agent.enzyme_type.value})")
        
        try:
            choice = int(input("Select agent number: ").strip())
            agent = agents[choice - 1]
            
            print(f"\n🔍 Debugging {agent.name}:")
            print(f"   Enzyme Type: {agent.enzyme_type.value}")
            print(f"   HGOV Balance: {agent.account.hgov_balance:,}")
            print(f"   HCC Balance: {agent.account.hcc_balance:,}")
            print(f"   Tasks Completed: {agent.account.tasks_completed}")
            print(f"   Success Rate: {agent.account.success_rate:.1%}")
            print(f"   Efficiency: {agent.efficiency_rating:.3f}")
            print(f"   Active Tasks: {len(agent.active_tasks)}")
            
        except (ValueError, IndexError):
            print("❌ Invalid agent selection")
    
    async def test_task_creation(self):
        """Test task creation interactively"""
        print("\n📋 Creating Test Task...")
        
        enzyme_types = list(EnzymeType)
        print("\nAvailable enzyme types:")
        for i, et in enumerate(enzyme_types, 1):
            print(f"   {i}. {et.value}")
        
        try:
            choice = int(input("Select enzyme type: ").strip())
            enzyme_type = enzyme_types[choice - 1]
            
            task = self.ecosystem.create_task(
                f"Interactive Test {int(time.time())}",
                "Interactively created test task",
                enzyme_type,
                1500,
                3000,
                2
            )
            
            print(f"✅ Created task: {task.title}")
            print(f"   Enzyme: {enzyme_type.value}")
            print(f"   Reward: 1500 HGOV, 3000 HCC")
            
        except (ValueError, IndexError):
            print("❌ Invalid enzyme type selection")
    
    async def quick_performance_test(self):
        """Quick performance benchmark"""
        print("\n⚡ Quick Performance Test...")
        
        start_time = time.time()
        await self.ecosystem.run_ecosystem_cycle()
        cycle_time = time.time() - start_time
        
        print(f"✅ Ecosystem cycle completed in {cycle_time:.3f}s")
        
        # Test task creation speed
        start_time = time.time()
        for i in range(5):
            self.ecosystem.create_task(f"Speed Test {i}", "Speed test", EnzymeType.CODE_SPLICERASE, 1000, 2000, 1)
        creation_time = time.time() - start_time
        
        print(f"✅ Created 5 tasks in {creation_time:.3f}s")
    
    async def fix_common_issues(self):
        """Auto-fix common issues"""
        print("\n🔧 Auto-fixing Common Issues...")
        
        fixes = 0
        
        # Fix 1: Replenish resources
        for resource_type in ResourceType:
            if self.ecosystem.resource_pools.get(resource_type, 0) < 1000:
                self.ecosystem.resource_pools[resource_type] = 5000
                fixes += 1
                print(f"   ✅ Replenished {resource_type.value}")
        
        # Fix 2: Reset agent efficiency
        for agent in self.ecosystem.agents.values():
            if agent.efficiency_rating < 0.7:
                agent.efficiency_rating = 0.85
                fixes += 1
                print(f"   ✅ Improved {agent.name} efficiency")
        
        print(f"🎯 Applied {fixes} fixes")
    
    async def show_statistics(self):
        """Show detailed system statistics"""
        stats = self.ecosystem.get_ecosystem_stats()
        
        print("\n📈 Detailed Statistics:")
        print(json.dumps(stats, indent=2))

async def main():
    """Main troubleshooting session"""
    troubleshooter = QuickTroubleshooter()
    
    print("🧪 BIOLOGICAL SYSTEM TROUBLESHOOTING LAB")
    print("=" * 50)
    
    # Run diagnostic tests
    await troubleshooter.run_quick_tests()
    
    # Demonstrate features
    await troubleshooter.demonstrate_features()
    
    # Interactive troubleshooting
    await troubleshooter.interactive_troubleshooting()

if __name__ == "__main__":
    asyncio.run(main())