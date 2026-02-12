#!/usr/bin/env python3
"""
Hybrid Economy Manager: Bridge between Local Virtual and Global Real Economies
Enables seamless transition between closed-loop and global Hardcard participation
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import logging

class EconomyMode(Enum):
    LOCAL_VIRTUAL = "local_virtual"
    GLOBAL_REAL = "global_real" 
    HYBRID = "hybrid"

class TaskSource(Enum):
    LOCAL_BUGS = "local_bugs"
    NEXUS_GLOBAL = "nexus_global"
    CROSS_PLATFORM = "cross_platform"

@dataclass
class EconomyBridge:
    """Bridge between local virtual and global real economies"""
    local_virtual_balance: Dict[str, int]  # Virtual token balances
    global_real_balance: Dict[str, float]  # Real token balances  
    conversion_rate: float  # Virtual to real conversion rate
    bridge_enabled: bool
    global_tasks_completed: int
    local_tasks_completed: int

@dataclass
class TaskReward:
    """Unified reward structure for local and global tasks"""
    task_id: str
    source: TaskSource
    base_reward_virtual: int
    base_reward_real: float
    completion_bonus: float
    global_multiplier: float
    user_level_multiplier: float

class HybridEconomyManager:
    """Manages the dual economy system with local virtual and global real integration"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.logger = self._setup_logging()
        
        # Economy state
        self.current_mode = EconomyMode.LOCAL_VIRTUAL
        self.user_bridges: Dict[str, EconomyBridge] = {}
        self.global_connection_active = False
        
        # Nexus AI integration
        self.nexus_api_endpoint = "https://nexus.hardcard.ai/api/v1"
        self.nexus_auth_token = None
        
        # Task pools
        self.local_task_pool = []
        self.global_task_pool = []
        self.hybrid_task_pool = []
        
        # Economy parameters
        self.virtual_to_real_conversion = 1000  # 1000 virtual = 1 real HGOV
        self.global_participation_threshold = 50000  # Min virtual tokens to bridge
        
        self.logger.info("🌐 Hybrid Economy Manager initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('hybrid_economy')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize_user_economy(self, user_id: str, preferred_mode: EconomyMode) -> Dict:
        """Initialize user's dual economy participation"""
        
        # Create economy bridge for user
        bridge = EconomyBridge(
            local_virtual_balance={"HGOV": 50000, "HCC": 100000},  # Starting virtual balance
            global_real_balance={"HGOV": 0.0, "HCC": 0.0},        # No real tokens initially
            conversion_rate=self.virtual_to_real_conversion,
            bridge_enabled=False,
            global_tasks_completed=0,
            local_tasks_completed=0
        )
        
        self.user_bridges[user_id] = bridge
        
        # Set initial mode
        await self._set_economy_mode(user_id, preferred_mode)
        
        result = {
            'user_id': user_id,
            'mode': preferred_mode.value,
            'local_balance': bridge.local_virtual_balance,
            'global_balance': bridge.global_real_balance,
            'bridge_available': bridge.local_virtual_balance["HGOV"] >= self.global_participation_threshold,
            'features_unlocked': self._get_available_features(user_id)
        }
        
        self.logger.info(f"👤 Initialized economy for user {user_id} in {preferred_mode.value} mode")
        return result
    
    async def _set_economy_mode(self, user_id: str, mode: EconomyMode):
        """Set user's economy participation mode"""
        
        if user_id not in self.user_bridges:
            raise ValueError(f"User {user_id} not initialized")
        
        bridge = self.user_bridges[user_id]
        
        if mode == EconomyMode.GLOBAL_REAL:
            # Enable bridge to global economy
            if bridge.local_virtual_balance["HGOV"] >= self.global_participation_threshold:
                bridge.bridge_enabled = True
                await self._connect_to_nexus_ai(user_id)
                self.logger.info(f"🌍 User {user_id} connected to global economy")
            else:
                self.logger.warning(f"⚠️ User {user_id} needs {self.global_participation_threshold} virtual HGOV to bridge")
                mode = EconomyMode.LOCAL_VIRTUAL
        
        self.current_mode = mode
    
    async def _connect_to_nexus_ai(self, user_id: str) -> bool:
        """Connect to Nexus AI for global task access"""
        
        try:
            # Authenticate with Nexus AI
            auth_payload = {
                'user_id': user_id,
                'service': 'hardcard_governance',
                'capabilities': ['bug_detection', 'uptime_monitoring', 'security_analysis']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nexus_api_endpoint}/auth",
                    json=auth_payload
                ) as response:
                    if response.status == 200:
                        auth_data = await response.json()
                        self.nexus_auth_token = auth_data['token']
                        self.global_connection_active = True
                        
                        # Load global tasks
                        await self._fetch_global_tasks(user_id)
                        
                        self.logger.info(f"🔗 Connected user {user_id} to Nexus AI")
                        return True
                    else:
                        self.logger.error(f"❌ Nexus AI authentication failed: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"❌ Nexus AI connection error: {e}")
            return False
    
    async def _fetch_global_tasks(self, user_id: str):
        """Fetch available global tasks from Nexus AI"""
        
        if not self.global_connection_active:
            return
        
        try:
            headers = {'Authorization': f'Bearer {self.nexus_auth_token}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nexus_api_endpoint}/tasks/available",
                    headers=headers,
                    params={'user_id': user_id, 'categories': 'security,monitoring,optimization'}
                ) as response:
                    if response.status == 200:
                        tasks_data = await response.json()
                        self.global_task_pool = tasks_data['tasks']
                        
                        self.logger.info(f"📋 Fetched {len(self.global_task_pool)} global tasks")
                    else:
                        self.logger.error(f"❌ Failed to fetch global tasks: {response.status}")
        
        except Exception as e:
            self.logger.error(f"❌ Global task fetch error: {e}")
    
    async def get_available_tasks(self, user_id: str) -> Dict:
        """Get all available tasks based on user's economy mode"""
        
        bridge = self.user_bridges[user_id]
        available_tasks = {
            'local_tasks': [],
            'global_tasks': [],
            'hybrid_tasks': [],
            'total_rewards_available': {'virtual': 0, 'real': 0}
        }
        
        # Always include local tasks
        available_tasks['local_tasks'] = [
            {
                'task_id': 'local_bug_hunt_001',
                'title': 'Critical Bug Detection',
                'description': 'Scan local governance contracts for vulnerabilities',
                'reward_virtual': {'HGOV': 10000, 'HCC': 25000},
                'reward_real': None,
                'estimated_time': '2 hours',
                'difficulty': 'high'
            },
            {
                'task_id': 'local_uptime_monitor_001',
                'title': 'Uptime Monitoring',
                'description': '24-hour system monitoring shift',
                'reward_virtual': {'HGOV': 5000, 'HCC': 12500},
                'reward_real': None,
                'estimated_time': '24 hours',
                'difficulty': 'medium'
            },
            {
                'task_id': 'local_optimization_001',
                'title': 'Performance Optimization',
                'description': 'Optimize gas usage in smart contracts',
                'reward_virtual': {'HGOV': 7500, 'HCC': 15000},
                'reward_real': None,
                'estimated_time': '4 hours',
                'difficulty': 'medium'
            }
        ]
        
        # Include global tasks if bridge is enabled
        if bridge.bridge_enabled and self.global_connection_active:
            available_tasks['global_tasks'] = [
                {
                    'task_id': 'global_security_audit_001',
                    'title': 'Cross-Platform Security Audit',
                    'description': 'Audit multiple Hardcard ecosystem apps',
                    'reward_virtual': {'HGOV': 50000, 'HCC': 100000},
                    'reward_real': {'HGOV': 50.0, 'HCC': 100.0},
                    'estimated_time': '1 week',
                    'difficulty': 'expert',
                    'nexus_verified': True,
                    'global_impact': 'high'
                },
                {
                    'task_id': 'global_ai_collaboration_001',
                    'title': 'AI Agent Collaboration Task',
                    'description': 'Coordinate with global AI agents on complex security analysis',
                    'reward_virtual': {'HGOV': 25000, 'HCC': 50000},
                    'reward_real': {'HGOV': 25.0, 'HCC': 50.0},
                    'estimated_time': '3 days',
                    'difficulty': 'high',
                    'nexus_verified': True,
                    'global_impact': 'medium'
                }
            ]
            
            # Hybrid tasks that combine local and global elements
            available_tasks['hybrid_tasks'] = [
                {
                    'task_id': 'hybrid_ecosystem_analysis_001',
                    'title': 'Local-Global Ecosystem Analysis',
                    'description': 'Analyze local governance impact on global Hardcard ecosystem',
                    'reward_virtual': {'HGOV': 35000, 'HCC': 75000},
                    'reward_real': {'HGOV': 15.0, 'HCC': 30.0},
                    'estimated_time': '5 days',
                    'difficulty': 'expert',
                    'requires_bridge': True,
                    'local_component': True,
                    'global_component': True
                }
            ]
        
        # Calculate total rewards
        for task_list in [available_tasks['local_tasks'], available_tasks['global_tasks'], available_tasks['hybrid_tasks']]:
            for task in task_list:
                if 'reward_virtual' in task and task['reward_virtual']:
                    available_tasks['total_rewards_available']['virtual'] += task['reward_virtual'].get('HGOV', 0)
                if 'reward_real' in task and task['reward_real']:
                    available_tasks['total_rewards_available']['real'] += task['reward_real'].get('HGOV', 0)
        
        return available_tasks
    
    async def complete_task(self, user_id: str, task_id: str, completion_data: Dict) -> Dict:
        """Process task completion and distribute rewards"""
        
        bridge = self.user_bridges[user_id]
        
        # Determine task source and rewards
        task_info = await self._get_task_info(task_id)
        if not task_info:
            raise ValueError(f"Task {task_id} not found")
        
        # Calculate rewards based on performance
        performance_multiplier = completion_data.get('performance_score', 1.0)
        speed_bonus = completion_data.get('speed_bonus', 1.0)
        quality_bonus = completion_data.get('quality_score', 1.0)
        
        total_multiplier = performance_multiplier * speed_bonus * quality_bonus
        
        # Distribute virtual rewards
        virtual_rewards = task_info.get('reward_virtual', {})
        for token, amount in virtual_rewards.items():
            final_amount = int(amount * total_multiplier)
            bridge.local_virtual_balance[token] += final_amount
        
        # Distribute real rewards if applicable
        real_rewards = {}
        if bridge.bridge_enabled and task_info.get('reward_real'):
            real_rewards = task_info['reward_real']
            for token, amount in real_rewards.items():
                final_amount = amount * total_multiplier
                bridge.global_real_balance[token] += final_amount
                
                # Submit to Nexus AI for global crediting
                await self._submit_global_completion(user_id, task_id, final_amount, token)
        
        # Update completion counters
        if task_id.startswith('local_'):
            bridge.local_tasks_completed += 1
        elif task_id.startswith('global_') or task_id.startswith('hybrid_'):
            bridge.global_tasks_completed += 1
        
        # Check for bridge eligibility
        if not bridge.bridge_enabled and bridge.local_virtual_balance["HGOV"] >= self.global_participation_threshold:
            bridge.bridge_enabled = True
            self.logger.info(f"🌉 User {user_id} now eligible for global economy bridge")
        
        result = {
            'task_id': task_id,
            'completion_success': True,
            'rewards_earned': {
                'virtual': virtual_rewards,
                'real': real_rewards
            },
            'multiplier_applied': total_multiplier,
            'new_balances': {
                'virtual': bridge.local_virtual_balance,
                'real': bridge.global_real_balance
            },
            'bridge_status': {
                'enabled': bridge.bridge_enabled,
                'eligible': bridge.local_virtual_balance["HGOV"] >= self.global_participation_threshold
            }
        }
        
        self.logger.info(f"✅ Task {task_id} completed by user {user_id} with {total_multiplier:.2f}x multiplier")
        return result
    
    async def _submit_global_completion(self, user_id: str, task_id: str, reward_amount: float, token: str):
        """Submit task completion to Nexus AI for global crediting"""
        
        try:
            headers = {'Authorization': f'Bearer {self.nexus_auth_token}'}
            payload = {
                'user_id': user_id,
                'task_id': task_id,
                'completion_time': datetime.now().isoformat(),
                'reward_amount': reward_amount,
                'reward_token': token,
                'source_system': 'hardcard_governance'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nexus_api_endpoint}/tasks/complete",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"🌍 Global completion submitted for task {task_id}")
                    else:
                        self.logger.error(f"❌ Global completion submission failed: {response.status}")
        
        except Exception as e:
            self.logger.error(f"❌ Global completion submission error: {e}")
    
    async def bridge_virtual_to_real(self, user_id: str, virtual_amount: int, token: str) -> Dict:
        """Bridge virtual tokens to real global economy"""
        
        bridge = self.user_bridges[user_id]
        
        if not bridge.bridge_enabled:
            return {'success': False, 'error': 'Bridge not enabled'}
        
        if bridge.local_virtual_balance[token] < virtual_amount:
            return {'success': False, 'error': 'Insufficient virtual balance'}
        
        # Calculate real tokens to mint
        real_amount = virtual_amount / self.virtual_to_real_conversion
        
        # Burn virtual tokens
        bridge.local_virtual_balance[token] -= virtual_amount
        
        # Credit real tokens
        bridge.global_real_balance[token] += real_amount
        
        # Submit to Nexus AI for global minting
        await self._request_global_minting(user_id, real_amount, token)
        
        result = {
            'success': True,
            'virtual_burned': virtual_amount,
            'real_minted': real_amount,
            'conversion_rate': self.virtual_to_real_conversion,
            'new_balances': {
                'virtual': bridge.local_virtual_balance,
                'real': bridge.global_real_balance
            }
        }
        
        self.logger.info(f"🌉 Bridged {virtual_amount} virtual {token} to {real_amount} real {token} for user {user_id}")
        return result
    
    async def _request_global_minting(self, user_id: str, amount: float, token: str):
        """Request global token minting through Nexus AI"""
        
        try:
            headers = {'Authorization': f'Bearer {self.nexus_auth_token}'}
            payload = {
                'user_id': user_id,
                'mint_amount': amount,
                'token': token,
                'source': 'virtual_bridge',
                'timestamp': datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.nexus_api_endpoint}/tokens/mint",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"🏭 Global minting requested: {amount} {token}")
                    else:
                        self.logger.error(f"❌ Global minting request failed: {response.status}")
        
        except Exception as e:
            self.logger.error(f"❌ Global minting request error: {e}")
    
    async def get_user_dashboard_data(self, user_id: str) -> Dict:
        """Get comprehensive user dashboard data for both economies"""
        
        bridge = self.user_bridges[user_id]
        
        dashboard_data = {
            'user_id': user_id,
            'economy_mode': self.current_mode.value,
            'bridge_status': {
                'enabled': bridge.bridge_enabled,
                'eligible': bridge.local_virtual_balance["HGOV"] >= self.global_participation_threshold,
                'threshold': self.global_participation_threshold
            },
            'balances': {
                'virtual': {
                    'HGOV': bridge.local_virtual_balance["HGOV"],
                    'HCC': bridge.local_virtual_balance["HCC"],
                    'usd_value': bridge.local_virtual_balance["HGOV"] * 2.50 + bridge.local_virtual_balance["HCC"] * 1.00
                },
                'real': {
                    'HGOV': bridge.global_real_balance["HGOV"],
                    'HCC': bridge.global_real_balance["HCC"],
                    'usd_value': bridge.global_real_balance["HGOV"] * 2.50 + bridge.global_real_balance["HCC"] * 1.00
                }
            },
            'task_completion': {
                'local_completed': bridge.local_tasks_completed,
                'global_completed': bridge.global_tasks_completed,
                'total_completed': bridge.local_tasks_completed + bridge.global_tasks_completed
            },
            'available_features': self._get_available_features(user_id),
            'next_milestones': self._get_next_milestones(user_id),
            'global_ranking': await self._get_global_ranking(user_id) if bridge.bridge_enabled else None
        }
        
        return dashboard_data
    
    def _get_available_features(self, user_id: str) -> List[str]:
        """Get list of features available to user based on their status"""
        
        bridge = self.user_bridges[user_id]
        features = [
            'virtual_economy',
            'local_tasks',
            'ai_agents',
            'virtual_marketplace',
            'local_leaderboards'
        ]
        
        if bridge.bridge_enabled:
            features.extend([
                'global_economy',
                'nexus_ai_integration',
                'global_tasks',
                'real_token_earning',
                'global_leaderboards',
                'cross_platform_collaboration'
            ])
        
        return features
    
    def _get_next_milestones(self, user_id: str) -> List[Dict]:
        """Get next achievable milestones for user"""
        
        bridge = self.user_bridges[user_id]
        milestones = []
        
        if not bridge.bridge_enabled:
            remaining_tokens = self.global_participation_threshold - bridge.local_virtual_balance["HGOV"]
            if remaining_tokens > 0:
                milestones.append({
                    'title': 'Global Economy Access',
                    'description': f'Earn {remaining_tokens:,} more virtual HGOV to unlock global features',
                    'progress': bridge.local_virtual_balance["HGOV"] / self.global_participation_threshold,
                    'category': 'economy_bridge'
                })
        
        # Task completion milestones
        task_milestones = [10, 25, 50, 100, 250, 500]
        total_tasks = bridge.local_tasks_completed + bridge.global_tasks_completed
        
        for milestone in task_milestones:
            if total_tasks < milestone:
                milestones.append({
                    'title': f'{milestone} Tasks Completed',
                    'description': f'Complete {milestone - total_tasks} more tasks to unlock special rewards',
                    'progress': total_tasks / milestone,
                    'category': 'task_completion'
                })
                break
        
        return milestones
    
    async def _get_global_ranking(self, user_id: str) -> Optional[Dict]:
        """Get user's global ranking from Nexus AI"""
        
        if not self.global_connection_active:
            return None
        
        try:
            headers = {'Authorization': f'Bearer {self.nexus_auth_token}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nexus_api_endpoint}/leaderboard/user/{user_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        ranking_data = await response.json()
                        return ranking_data
                    else:
                        return None
        
        except Exception as e:
            self.logger.error(f"❌ Global ranking fetch error: {e}")
            return None
    
    async def _get_task_info(self, task_id: str) -> Optional[Dict]:
        """Get task information from local or global pools"""
        
        # Search local tasks
        all_tasks = []
        if hasattr(self, 'current_local_tasks'):
            all_tasks.extend(self.current_local_tasks)
        if hasattr(self, 'current_global_tasks'):
            all_tasks.extend(self.current_global_tasks)
        
        # Mock task data for demo
        task_database = {
            'local_bug_hunt_001': {
                'reward_virtual': {'HGOV': 10000, 'HCC': 25000},
                'reward_real': None
            },
            'local_uptime_monitor_001': {
                'reward_virtual': {'HGOV': 5000, 'HCC': 12500},
                'reward_real': None
            },
            'global_security_audit_001': {
                'reward_virtual': {'HGOV': 50000, 'HCC': 100000},
                'reward_real': {'HGOV': 50.0, 'HCC': 100.0}
            },
            'hybrid_ecosystem_analysis_001': {
                'reward_virtual': {'HGOV': 35000, 'HCC': 75000},
                'reward_real': {'HGOV': 15.0, 'HCC': 30.0}
            }
        }
        
        return task_database.get(task_id)

# Example usage and configuration
async def demo_hybrid_economy():
    """Demonstrate the hybrid economy system"""
    
    manager = HybridEconomyManager('hybrid-config.json')
    
    # Initialize user in local mode
    user_result = await manager.initialize_user_economy("user_001", EconomyMode.LOCAL_VIRTUAL)
    print(f"👤 User initialized: {json.dumps(user_result, indent=2)}")
    
    # Complete some local tasks
    completion_result = await manager.complete_task("user_001", "local_bug_hunt_001", {
        'performance_score': 1.2,
        'speed_bonus': 1.5,
        'quality_score': 1.1
    })
    print(f"✅ Task completed: {json.dumps(completion_result, indent=2)}")
    
    # Bridge to global economy
    bridge_result = await manager.bridge_virtual_to_real("user_001", 10000, "HGOV")
    print(f"🌉 Bridge result: {json.dumps(bridge_result, indent=2)}")
    
    # Get dashboard data
    dashboard = await manager.get_user_dashboard_data("user_001")
    print(f"📊 Dashboard: {json.dumps(dashboard, indent=2)}")

if __name__ == "__main__":
    asyncio.run(demo_hybrid_economy())