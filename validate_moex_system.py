#!/usr/bin/env python3
"""
MOEX System Validation Script
Comprehensive testing and validation of the MOEX terminal system
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from moex_terminal import MOEXTerminal, ConversationPattern as BasicPattern
    from kimi_heavy_moex_terminal import KimiHeavyTerminal, ConversationPattern as HeavyPattern
    moex_imports_successful = True
except ImportError as e:
    print(f"❌ Failed to import MOEX modules: {e}")
    moex_imports_successful = False

class MOEXSystemValidator:
    """Comprehensive MOEX system validator"""
    
    def __init__(self):
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'environment': self._get_environment_info(),
            'api_keys': self._check_api_keys(),
            'system_tests': [],
            'performance_metrics': {},
            'recommendations': []
        }
        
        self.basic_terminal = None
        self.heavy_terminal = None
        
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'working_directory': os.getcwd(),
            'modules_available': moex_imports_successful
        }
    
    def _check_api_keys(self) -> Dict[str, bool]:
        """Check API key availability"""
        keys = {
            'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
            'OPENROUTER_API_KEY': bool(os.getenv('OPENROUTER_API_KEY'))
        }
        return keys
    
    async def initialize_terminals(self) -> bool:
        """Initialize both MOEX terminals"""
        print("🔧 Initializing MOEX terminals...")
        
        if not moex_imports_successful:
            print("❌ Cannot initialize terminals - import failed")
            return False
        
        try:
            # Initialize basic terminal
            self.basic_terminal = MOEXTerminal()
            print("✅ Basic MOEX terminal initialized")
            
            # Initialize heavy terminal
            self.heavy_terminal = KimiHeavyTerminal()
            print("✅ Kimi Heavy MOEX terminal initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Terminal initialization failed: {e}")
            return False
    
    async def validate_basic_moex(self) -> Dict[str, Any]:
        """Validate basic MOEX terminal functionality"""
        print(f"\n{'='*60}")
        print("🧠 VALIDATING BASIC MOEX TERMINAL")
        print(f"{'='*60}")
        
        validation_result = {
            'terminal_type': 'basic',
            'patterns_tested': [],
            'api_connections': {},
            'performance': {},
            'errors': []
        }
        
        if not self.basic_terminal:
            validation_result['errors'].append("Terminal not initialized")
            return validation_result
        
        # Test API connections
        print("🔗 Testing API connections...")
        api_tests = [
            ('Claude', self.basic_terminal.call_claude),
            ('Gemini', self.basic_terminal.call_gemini),
            ('DeepSeek', self.basic_terminal.call_deepseek),
            ('GPT-4', self.basic_terminal.call_gpt4)
        ]
        
        for api_name, api_func in api_tests:
            try:
                start_time = time.time()
                result = await api_func("Hello, this is a validation test", "Testing API connection")
                end_time = time.time()
                
                validation_result['api_connections'][api_name] = {
                    'success': result.confidence > 0,
                    'latency': end_time - start_time,
                    'confidence': result.confidence,
                    'response_length': len(result.response)
                }
                
                if result.confidence > 0:
                    print(f"✅ {api_name}: Connected ({end_time - start_time:.2f}s)")
                else:
                    print(f"❌ {api_name}: Failed")
                    
            except Exception as e:
                print(f"❌ {api_name}: Error - {e}")
                validation_result['api_connections'][api_name] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Test conversation patterns
        print("\n🎯 Testing conversation patterns...")
        test_query = "What are the benefits of renewable energy?"
        
        patterns = [
            BasicPattern.COMPETE,
            BasicPattern.BUILD,
            BasicPattern.DEBATE,
            BasicPattern.CONSENSUS,
            BasicPattern.SYNTHESIZE
        ]
        
        for pattern in patterns:
            try:
                start_time = time.time()
                result = await self.basic_terminal.process_query(test_query, pattern)
                end_time = time.time()
                
                pattern_result = {
                    'pattern': pattern.value,
                    'success': len(result.responses) > 0,
                    'response_count': len(result.responses),
                    'processing_time': end_time - start_time,
                    'has_synthesis': bool(result.synthesis)
                }
                
                validation_result['patterns_tested'].append(pattern_result)
                
                if pattern_result['success']:
                    print(f"✅ {pattern.value}: {len(result.responses)} responses in {end_time - start_time:.2f}s")
                else:
                    print(f"❌ {pattern.value}: Failed")
                    
            except Exception as e:
                print(f"❌ {pattern.value}: Error - {e}")
                validation_result['patterns_tested'].append({
                    'pattern': pattern.value,
                    'success': False,
                    'error': str(e)
                })
        
        return validation_result
    
    async def validate_heavy_moex(self) -> Dict[str, Any]:
        """Validate heavy MOEX terminal functionality"""
        print(f"\n{'='*60}")
        print("🔥 VALIDATING KIMI HEAVY MOEX TERMINAL")
        print(f"{'='*60}")
        
        validation_result = {
            'terminal_type': 'heavy',
            'agent_fleet': {},
            'patterns_tested': [],
            'orchestration': {},
            'performance': {},
            'errors': []
        }
        
        if not self.heavy_terminal:
            validation_result['errors'].append("Terminal not initialized")
            return validation_result
        
        # Test agent fleet
        print("🤖 Testing agent fleet...")
        validation_result['agent_fleet'] = {
            'total_agents': len(self.heavy_terminal.agent_fleet),
            'active_agents': sum(1 for agent in self.heavy_terminal.agent_fleet.values() if agent.active),
            'roles': list(set(agent.role.value for agent in self.heavy_terminal.agent_fleet.values())),
            'experts': list(set(agent.expert_type.value for agent in self.heavy_terminal.agent_fleet.values()))
        }
        
        print(f"✅ Agent fleet: {validation_result['agent_fleet']['total_agents']} agents, {validation_result['agent_fleet']['active_agents']} active")
        
        # Test orchestrator
        print("🎯 Testing Kimi orchestrator...")
        try:
            start_time = time.time()
            orch_result = await self.heavy_terminal.call_kimi_orchestrator("Test orchestration capabilities")
            end_time = time.time()
            
            validation_result['orchestration'] = {
                'success': orch_result.confidence > 0,
                'latency': end_time - start_time,
                'confidence': orch_result.confidence,
                'research_questions_generated': len(orch_result.research_questions),
                'tools_used': len(orch_result.tools_used)
            }
            
            if orch_result.confidence > 0:
                print(f"✅ Orchestrator: Connected ({end_time - start_time:.2f}s)")
            else:
                print(f"❌ Orchestrator: Failed")
                
        except Exception as e:
            print(f"❌ Orchestrator: Error - {e}")
            validation_result['orchestration'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test heavy patterns
        print("\n🔥 Testing heavy patterns...")
        test_query = "Create a comprehensive business plan for a tech startup"
        
        patterns = [
            HeavyPattern.HEAVY_RESEARCH,
            HeavyPattern.PARALLEL_CREATION,
            HeavyPattern.SYNTHESIZE
        ]
        
        for pattern in patterns:
            try:
                start_time = time.time()
                result = await self.heavy_terminal.run_heavy_consultation(test_query, pattern)
                end_time = time.time()
                
                pattern_result = {
                    'pattern': pattern.value,
                    'success': len(result.responses) > 0,
                    'response_count': len(result.responses),
                    'agents_deployed': len(result.agents_deployed),
                    'processing_time': end_time - start_time,
                    'research_questions': len(result.research_questions),
                    'has_synthesis': bool(result.synthesis)
                }
                
                validation_result['patterns_tested'].append(pattern_result)
                
                if pattern_result['success']:
                    print(f"✅ {pattern.value}: {len(result.responses)} responses, {len(result.agents_deployed)} agents in {end_time - start_time:.2f}s")
                else:
                    print(f"❌ {pattern.value}: Failed")
                    
            except Exception as e:
                print(f"❌ {pattern.value}: Error - {e}")
                validation_result['patterns_tested'].append({
                    'pattern': pattern.value,
                    'success': False,
                    'error': str(e)
                })
        
        return validation_result
    
    async def test_snake_game_creation(self) -> Dict[str, Any]:
        """Test the specific snake game creation request"""
        print(f"\n{'='*60}")
        print("🐍 TESTING SNAKE GAME CREATION")
        print(f"{'='*60}")
        
        snake_test_result = {
            'query': 'build a snake game',
            'basic_terminal': {},
            'heavy_terminal': {},
            'comparison': {}
        }
        
        # Test with basic terminal
        if self.basic_terminal:
            try:
                print("🧠 Testing with Basic MOEX...")
                start_time = time.time()
                result = await self.basic_terminal.process_query("build a snake game", BasicPattern.SYNTHESIZE)
                end_time = time.time()
                
                snake_test_result['basic_terminal'] = {
                    'success': len(result.responses) > 0,
                    'response_count': len(result.responses),
                    'processing_time': end_time - start_time,
                    'synthesis_length': len(result.synthesis) if result.synthesis else 0
                }
                
                print(f"✅ Basic: {len(result.responses)} responses in {end_time - start_time:.2f}s")
                
            except Exception as e:
                print(f"❌ Basic: Error - {e}")
                snake_test_result['basic_terminal'] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Test with heavy terminal
        if self.heavy_terminal:
            try:
                print("🔥 Testing with Heavy MOEX...")
                start_time = time.time()
                result = await self.heavy_terminal.run_heavy_consultation("build a snake game", HeavyPattern.PARALLEL_CREATION)
                end_time = time.time()
                
                snake_test_result['heavy_terminal'] = {
                    'success': len(result.responses) > 0,
                    'response_count': len(result.responses),
                    'agents_deployed': len(result.agents_deployed),
                    'processing_time': end_time - start_time,
                    'research_questions': len(result.research_questions),
                    'synthesis_length': len(result.synthesis) if result.synthesis else 0
                }
                
                print(f"✅ Heavy: {len(result.responses)} responses, {len(result.agents_deployed)} agents in {end_time - start_time:.2f}s")
                
                # Save detailed results
                with open('snake_game_detailed_results.json', 'w') as f:
                    json.dump({
                        'query': result.query,
                        'pattern': result.pattern.value,
                        'agents_deployed': len(result.agents_deployed),
                        'responses': [
                            {
                                'agent_id': resp.agent_id,
                                'expert': resp.expert.value,
                                'role': resp.role.value,
                                'response': resp.response,
                                'confidence': resp.confidence,
                                'latency': resp.latency
                            }
                            for resp in result.responses
                        ],
                        'synthesis': result.synthesis
                    }, f, indent=2)
                
                print("📁 Detailed results saved to snake_game_detailed_results.json")
                
            except Exception as e:
                print(f"❌ Heavy: Error - {e}")
                snake_test_result['heavy_terminal'] = {
                    'success': False,
                    'error': str(e)
                }
        
        return snake_test_result
    
    def generate_recommendations(self):
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # Check API keys
        if not all(self.validation_results['api_keys'].values()):
            recommendations.append({
                'category': 'Configuration',
                'priority': 'High',
                'issue': 'Missing API keys',
                'recommendation': 'Set all required API keys: OPENAI_API_KEY, OPENROUTER_API_KEY'
            })
        
        # Check basic terminal performance
        basic_results = next((r for r in self.validation_results['system_tests'] if r['terminal_type'] == 'basic'), None)
        if basic_results:
            failed_apis = [name for name, result in basic_results['api_connections'].items() if not result.get('success', False)]
            if failed_apis:
                recommendations.append({
                    'category': 'Connectivity',
                    'priority': 'High',
                    'issue': f'API connection failures: {", ".join(failed_apis)}',
                    'recommendation': 'Check API keys and network connectivity'
                })
        
        # Check heavy terminal performance
        heavy_results = next((r for r in self.validation_results['system_tests'] if r['terminal_type'] == 'heavy'), None)
        if heavy_results:
            if not heavy_results['orchestration'].get('success', False):
                recommendations.append({
                    'category': 'Heavy System',
                    'priority': 'High',
                    'issue': 'Kimi orchestrator not functioning',
                    'recommendation': 'Check Kimi API connection and OpenRouter configuration'
                })
        
        # Performance recommendations
        if basic_results and heavy_results:
            basic_avg_time = sum(p['processing_time'] for p in basic_results['patterns_tested'] if p.get('processing_time', 0) > 0) / len(basic_results['patterns_tested'])
            heavy_avg_time = sum(p['processing_time'] for p in heavy_results['patterns_tested'] if p.get('processing_time', 0) > 0) / len(heavy_results['patterns_tested'])
            
            if basic_avg_time > 30:
                recommendations.append({
                    'category': 'Performance',
                    'priority': 'Medium',
                    'issue': 'Basic terminal response times high',
                    'recommendation': 'Consider reducing query complexity or optimizing API calls'
                })
            
            if heavy_avg_time > 60:
                recommendations.append({
                    'category': 'Performance',
                    'priority': 'Medium',
                    'issue': 'Heavy terminal response times high',
                    'recommendation': 'Consider reducing agent count or implementing caching'
                })
        
        self.validation_results['recommendations'] = recommendations
    
    def generate_report(self):
        """Generate comprehensive validation report"""
        print(f"\n{'='*80}")
        print("📊 MOEX SYSTEM VALIDATION REPORT")
        print(f"{'='*80}")
        
        # Environment summary
        print(f"🖥️  Environment:")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   Platform: {sys.platform}")
        print(f"   Modules: {'✅ Available' if moex_imports_successful else '❌ Import failed'}")
        
        # API Keys
        print(f"\n🔑 API Keys:")
        for key, available in self.validation_results['api_keys'].items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"   {key}: {status}")
        
        # System tests summary
        print(f"\n🧪 System Tests:")
        for test in self.validation_results['system_tests']:
            terminal_type = test['terminal_type'].title()
            
            if test['terminal_type'] == 'basic':
                api_success = sum(1 for conn in test['api_connections'].values() if conn.get('success', False))
                api_total = len(test['api_connections'])
                pattern_success = sum(1 for p in test['patterns_tested'] if p.get('success', False))
                pattern_total = len(test['patterns_tested'])
                
                print(f"   {terminal_type} Terminal:")
                print(f"     API Connections: {api_success}/{api_total}")
                print(f"     Patterns: {pattern_success}/{pattern_total}")
                
            elif test['terminal_type'] == 'heavy':
                agent_count = test['agent_fleet']['total_agents']
                active_agents = test['agent_fleet']['active_agents']
                orch_success = test['orchestration'].get('success', False)
                pattern_success = sum(1 for p in test['patterns_tested'] if p.get('success', False))
                pattern_total = len(test['patterns_tested'])
                
                print(f"   {terminal_type} Terminal:")
                print(f"     Agent Fleet: {active_agents}/{agent_count} active")
                print(f"     Orchestrator: {'✅ Working' if orch_success else '❌ Failed'}")
                print(f"     Patterns: {pattern_success}/{pattern_total}")
        
        # Recommendations
        if self.validation_results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in self.validation_results['recommendations']:
                priority_emoji = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🔵"
                print(f"   {priority_emoji} {rec['category']}: {rec['issue']}")
                print(f"      → {rec['recommendation']}")
        
        # Save detailed report
        with open('moex_validation_report.json', 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)
        
        print(f"\n📁 Detailed validation report saved to moex_validation_report.json")
        
        # Overall assessment
        total_issues = len([r for r in self.validation_results['recommendations'] if r['priority'] == 'High'])
        
        if total_issues == 0:
            print(f"\n✅ MOEX System: FULLY OPERATIONAL")
        elif total_issues <= 2:
            print(f"\n⚠️  MOEX System: MOSTLY OPERATIONAL ({total_issues} high priority issues)")
        else:
            print(f"\n❌ MOEX System: REQUIRES ATTENTION ({total_issues} high priority issues)")
    
    async def run_full_validation(self):
        """Run complete validation suite"""
        print("🧪 Starting MOEX System Validation")
        print("=" * 80)
        
        # Initialize terminals
        if not await self.initialize_terminals():
            print("❌ Validation failed - cannot initialize terminals")
            return
        
        # Run validations
        basic_results = await self.validate_basic_moex()
        self.validation_results['system_tests'].append(basic_results)
        
        heavy_results = await self.validate_heavy_moex()
        self.validation_results['system_tests'].append(heavy_results)
        
        # Test snake game creation
        snake_results = await self.test_snake_game_creation()
        self.validation_results['snake_game_test'] = snake_results
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Generate report
        self.generate_report()
        
        print(f"\n✅ Validation complete!")

async def main():
    """Main validation entry point"""
    validator = MOEXSystemValidator()
    await validator.run_full_validation()

if __name__ == "__main__":
    asyncio.run(main())