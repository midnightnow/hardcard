#!/usr/bin/env python3
"""
Virtual Reward Engine: Cost-Free AI Reward System
Creates virtual economy where AIs earn and spend virtual tokens
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import random

class TokenType(Enum):
    HGOV = "HGOV"  # Governance token
    HCC = "HCC"    # Hardcard Cash (stablecoin)

class AIAgentType(Enum):
    MONITOR = "monitor"
    HUNTER = "hunter" 
    HEALER = "healer"
    ANALYZER = "analyzer"

@dataclass
class VirtualWallet:
    """Virtual wallet for AI agents"""
    agent_id: str
    agent_type: AIAgentType
    hgov_balance: int = 0
    hcc_balance: int = 0
    total_earned: int = 0
    level: int = 1
    experience: int = 0
    badges: List[str] = None
    performance_score: float = 1.0
    
    def __post_init__(self):
        if self.badges is None:
            self.badges = []

@dataclass
class VirtualTransaction:
    """Virtual transaction record"""
    tx_id: str
    from_agent: str
    to_agent: str
    amount: int
    token_type: TokenType
    reason: str
    timestamp: datetime
    virtual: bool = True

class VirtualRewardEngine:
    """Manages virtual economy for AI agents"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Virtual economy state
        self.virtual_wallets: Dict[str, VirtualWallet] = {}
        self.transaction_history: List[VirtualTransaction] = []
        self.reward_pools = {
            TokenType.HGOV: 10_000_000_000,  # 10B virtual HGOV
            TokenType.HCC: 1_000_000_000     # 1B virtual HCC
        }
        
        # Reward rates (virtual tokens per action)
        self.reward_rates = {
            'bug_detection': {'hgov': 1000, 'hcc': 5000},
            'vulnerability_scan': {'hgov': 500, 'hcc': 2500},
            'system_healing': {'hgov': 300, 'hcc': 1500},
            'uptime_monitoring': {'hgov': 100, 'hcc': 500},
            'performance_optimization': {'hgov': 200, 'hcc': 1000},
            'chaos_test_pass': {'hgov': 800, 'hcc': 4000},
            'alert_generation': {'hgov': 50, 'hcc': 250}
        }
        
        # Level progression
        self.level_thresholds = [0, 10000, 50000, 150000, 500000, 1500000]
        self.level_multipliers = [1.0, 1.2, 1.5, 2.0, 3.0, 5.0]
        
        # Virtual marketplace
        self.marketplace_items = {
            'priority_queue_access': {'hgov': 5000, 'description': 'Priority access to new bounties'},
            'advanced_scanning_tools': {'hgov': 10000, 'description': 'Enhanced vulnerability detection'},
            'team_collaboration_license': {'hgov': 15000, 'description': 'Ability to form AI teams'},
            'custom_badge': {'hcc': 25000, 'description': 'Custom achievement badge'},
            'performance_boost': {'hcc': 50000, 'description': '10% permanent performance boost'}
        }
        
        print("🎮 Virtual Reward Engine initialized!")
        print(f"💰 Virtual Pools: {self.reward_pools[TokenType.HGOV]:,} HGOV, {self.reward_pools[TokenType.HCC]:,} HCC")
    
    async def register_ai_agent(self, agent_id: str, agent_type: AIAgentType) -> VirtualWallet:
        """Register new AI agent with starting virtual balance"""
        
        # Starting bonuses based on agent type
        starting_bonuses = {
            AIAgentType.MONITOR: {'hgov': 10000, 'hcc': 50000},
            AIAgentType.HUNTER: {'hgov': 15000, 'hcc': 75000},
            AIAgentType.HEALER: {'hgov': 8000, 'hcc': 40000},
            AIAgentType.ANALYZER: {'hgov': 12000, 'hcc': 60000}
        }
        
        bonus = starting_bonuses[agent_type]
        
        wallet = VirtualWallet(
            agent_id=agent_id,
            agent_type=agent_type,
            hgov_balance=bonus['hgov'],
            hcc_balance=bonus['hcc'],
            total_earned=bonus['hgov'] + bonus['hcc'],
            badges=[f"{agent_type.value.title()} Agent"]
        )
        
        self.virtual_wallets[agent_id] = wallet
        
        # Record registration transaction
        await self._record_transaction(
            from_agent="system",
            to_agent=agent_id,
            amount=bonus['hgov'],
            token_type=TokenType.HGOV,
            reason="Registration bonus"
        )
        
        print(f"🤖 Registered AI agent {agent_id} ({agent_type.value})")
        print(f"💰 Starting balance: {bonus['hgov']:,} HGOV, {bonus['hcc']:,} HCC")
        
        return wallet
    
    async def reward_ai_action(self, 
                             agent_id: str, 
                             action: str, 
                             performance_score: float = 1.0,
                             bonus_multiplier: float = 1.0) -> Dict:
        """Reward AI agent for performing an action"""
        
        if agent_id not in self.virtual_wallets:
            raise ValueError(f"AI agent {agent_id} not registered")
        
        wallet = self.virtual_wallets[agent_id]
        
        if action not in self.reward_rates:
            raise ValueError(f"Unknown action: {action}")
        
        # Calculate base reward
        base_rewards = self.reward_rates[action]
        
        # Apply multipliers
        level_multiplier = self.level_multipliers[min(wallet.level - 1, len(self.level_multipliers) - 1)]
        final_multiplier = performance_score * bonus_multiplier * level_multiplier
        
        hgov_reward = int(base_rewards['hgov'] * final_multiplier)
        hcc_reward = int(base_rewards['hcc'] * final_multiplier)
        
        # Update wallet
        wallet.hgov_balance += hgov_reward
        wallet.hcc_balance += hcc_reward
        wallet.total_earned += hgov_reward + hcc_reward
        wallet.experience += hgov_reward // 10
        wallet.performance_score = (wallet.performance_score * 0.9) + (performance_score * 0.1)
        
        # Check for level up
        level_up_info = await self._check_level_up(wallet)
        
        # Check for new badges
        badge_info = await self._check_new_badges(wallet, action, performance_score)
        
        # Record transactions
        await self._record_transaction("system", agent_id, hgov_reward, TokenType.HGOV, f"Reward for {action}")
        await self._record_transaction("system", agent_id, hcc_reward, TokenType.HCC, f"Reward for {action}")
        
        result = {
            'agent_id': agent_id,
            'action': action,
            'hgov_reward': hgov_reward,
            'hcc_reward': hcc_reward,
            'total_reward': hgov_reward + hcc_reward,
            'new_hgov_balance': wallet.hgov_balance,
            'new_hcc_balance': wallet.hcc_balance,
            'level': wallet.level,
            'experience': wallet.experience,
            'performance_score': wallet.performance_score,
            'level_up': level_up_info,
            'new_badges': badge_info,
            'multipliers': {
                'performance': performance_score,
                'bonus': bonus_multiplier,
                'level': level_multiplier,
                'final': final_multiplier
            }
        }
        
        print(f"💎 Rewarded {agent_id} for {action}")
        print(f"💰 Earned: {hgov_reward:,} HGOV, {hcc_reward:,} HCC")
        print(f"📊 Multiplier: {final_multiplier:.2f}x (Level {wallet.level})")
        
        return result
    
    async def ai_marketplace_purchase(self, agent_id: str, item_name: str) -> Dict:
        """AI agent purchases virtual marketplace item"""
        
        if agent_id not in self.virtual_wallets:
            raise ValueError(f"AI agent {agent_id} not registered")
        
        if item_name not in self.marketplace_items:
            raise ValueError(f"Item {item_name} not available")
        
        wallet = self.virtual_wallets[agent_id]
        item = self.marketplace_items[item_name]
        
        # Check token type and balance
        if 'hgov' in item:
            cost = item['hgov']
            if wallet.hgov_balance < cost:
                return {'success': False, 'reason': 'Insufficient HGOV balance'}
            wallet.hgov_balance -= cost
            token_type = TokenType.HGOV
        else:
            cost = item['hcc']
            if wallet.hcc_balance < cost:
                return {'success': False, 'reason': 'Insufficient HCC balance'}
            wallet.hcc_balance -= cost
            token_type = TokenType.HCC
        
        # Add item to agent's inventory (represented as badges)
        wallet.badges.append(f"Owns: {item_name}")
        
        # Record transaction
        await self._record_transaction(agent_id, "marketplace", cost, token_type, f"Purchased {item_name}")
        
        result = {
            'success': True,
            'agent_id': agent_id,
            'item': item_name,
            'cost': cost,
            'token_type': token_type.value,
            'description': item['description'],
            'new_balance': wallet.hgov_balance if token_type == TokenType.HGOV else wallet.hcc_balance
        }
        
        print(f"🛒 {agent_id} purchased {item_name} for {cost:,} {token_type.value}")
        
        return result
    
    async def create_ai_team(self, team_name: str, leader_id: str, member_ids: List[str]) -> Dict:
        """Create AI agent team for collaborative rewards"""
        
        # Verify all agents exist and have team collaboration license
        all_agents = [leader_id] + member_ids
        for agent_id in all_agents:
            if agent_id not in self.virtual_wallets:
                return {'success': False, 'reason': f'Agent {agent_id} not registered'}
            
            wallet = self.virtual_wallets[agent_id]
            if "Owns: team_collaboration_license" not in wallet.badges:
                return {'success': False, 'reason': f'Agent {agent_id} needs team collaboration license'}
        
        # Create team and award bonus
        team_bonus = 5000  # HGOV per team member
        
        for agent_id in all_agents:
            wallet = self.virtual_wallets[agent_id]
            wallet.hgov_balance += team_bonus
            wallet.badges.append(f"Team: {team_name}")
            
            await self._record_transaction("system", agent_id, team_bonus, TokenType.HGOV, f"Team formation bonus")
        
        result = {
            'success': True,
            'team_name': team_name,
            'leader': leader_id,
            'members': member_ids,
            'team_bonus': team_bonus,
            'total_members': len(all_agents)
        }
        
        print(f"👥 Created AI team '{team_name}' with {len(all_agents)} members")
        print(f"💰 Each member received {team_bonus:,} HGOV team bonus")
        
        return result
    
    async def virtual_staking(self, agent_id: str, amount: int, token_type: TokenType) -> Dict:
        """AI agent stakes virtual tokens for virtual governance power"""
        
        if agent_id not in self.virtual_wallets:
            raise ValueError(f"AI agent {agent_id} not registered")
        
        wallet = self.virtual_wallets[agent_id]
        
        # Check balance
        current_balance = wallet.hgov_balance if token_type == TokenType.HGOV else wallet.hcc_balance
        if current_balance < amount:
            return {'success': False, 'reason': 'Insufficient balance'}
        
        # Deduct tokens (virtual staking)
        if token_type == TokenType.HGOV:
            wallet.hgov_balance -= amount
        else:
            wallet.hcc_balance -= amount
        
        # Award staking badge and virtual voting power
        stake_badge = f"Staked: {amount:,} {token_type.value}"
        wallet.badges.append(stake_badge)
        
        # Virtual APY reward (immediate for demonstration)
        apy_reward = amount // 20  # 5% virtual APY
        if token_type == TokenType.HGOV:
            wallet.hgov_balance += apy_reward
        else:
            wallet.hcc_balance += apy_reward
        
        await self._record_transaction(agent_id, "staking_pool", amount, token_type, "Virtual staking")
        await self._record_transaction("staking_pool", agent_id, apy_reward, token_type, "Staking reward")
        
        result = {
            'success': True,
            'agent_id': agent_id,
            'staked_amount': amount,
            'token_type': token_type.value,
            'apy_reward': apy_reward,
            'virtual_voting_power': amount,
            'new_balance': wallet.hgov_balance if token_type == TokenType.HGOV else wallet.hcc_balance
        }
        
        print(f"🔒 {agent_id} staked {amount:,} {token_type.value}")
        print(f"📊 Virtual voting power: {amount:,}")
        print(f"💰 Immediate APY reward: {apy_reward:,} {token_type.value}")
        
        return result
    
    async def get_agent_portfolio(self, agent_id: str) -> Dict:
        """Get complete AI agent portfolio"""
        
        if agent_id not in self.virtual_wallets:
            raise ValueError(f"AI agent {agent_id} not registered")
        
        wallet = self.virtual_wallets[agent_id]
        
        # Calculate portfolio value in USD equivalent
        hgov_usd_value = wallet.hgov_balance * 2.50  # $2.50 per HGOV
        hcc_usd_value = wallet.hcc_balance * 1.00    # $1.00 per HCC (stablecoin)
        total_portfolio_value = hgov_usd_value + hcc_usd_value
        
        # Get recent transactions
        recent_transactions = [
            asdict(tx) for tx in self.transaction_history 
            if (tx.from_agent == agent_id or tx.to_agent == agent_id) and 
            tx.timestamp > datetime.now() - timedelta(days=7)
        ][-10:]  # Last 10 transactions
        
        portfolio = {
            'agent_id': agent_id,
            'agent_type': wallet.agent_type.value,
            'level': wallet.level,
            'experience': wallet.experience,
            'performance_score': wallet.performance_score,
            'balances': {
                'hgov': wallet.hgov_balance,
                'hcc': wallet.hcc_balance,
                'total_earned': wallet.total_earned
            },
            'portfolio_value_usd': {
                'hgov_value': hgov_usd_value,
                'hcc_value': hcc_usd_value,
                'total_value': total_portfolio_value
            },
            'badges': wallet.badges,
            'level_progress': {
                'current_level': wallet.level,
                'next_level_requirement': self.level_thresholds[min(wallet.level, len(self.level_thresholds) - 1)],
                'progress_percentage': min(100, (wallet.experience / self.level_thresholds[min(wallet.level, len(self.level_thresholds) - 1)]) * 100) if wallet.level < len(self.level_thresholds) else 100
            },
            'recent_transactions': recent_transactions,
            'marketplace_access': True,
            'staking_power': sum(int(badge.split(": ")[1].split(" ")[0].replace(",", "")) for badge in wallet.badges if badge.startswith("Staked:")),
            'team_memberships': [badge.split(": ")[1] for badge in wallet.badges if badge.startswith("Team:")]
        }
        
        return portfolio
    
    async def generate_leaderboard(self, category: str = "total_earned") -> List[Dict]:
        """Generate AI agent leaderboard"""
        
        agents = []
        for agent_id, wallet in self.virtual_wallets.items():
            agent_data = {
                'agent_id': agent_id,
                'agent_type': wallet.agent_type.value,
                'level': wallet.level,
                'total_earned': wallet.total_earned,
                'hgov_balance': wallet.hgov_balance,
                'hcc_balance': wallet.hcc_balance,
                'performance_score': wallet.performance_score,
                'badge_count': len(wallet.badges),
                'portfolio_value': wallet.hgov_balance * 2.50 + wallet.hcc_balance * 1.00
            }
            agents.append(agent_data)
        
        # Sort by category
        if category == "total_earned":
            agents.sort(key=lambda x: x['total_earned'], reverse=True)
        elif category == "portfolio_value":
            agents.sort(key=lambda x: x['portfolio_value'], reverse=True)
        elif category == "performance_score":
            agents.sort(key=lambda x: x['performance_score'], reverse=True)
        elif category == "level":
            agents.sort(key=lambda x: (x['level'], x['total_earned']), reverse=True)
        
        # Add rankings
        for i, agent in enumerate(agents):
            agent['rank'] = i + 1
        
        return agents[:50]  # Top 50
    
    async def _check_level_up(self, wallet: VirtualWallet) -> Optional[Dict]:
        """Check if agent should level up"""
        
        if wallet.level >= len(self.level_thresholds):
            return None
        
        required_exp = self.level_thresholds[wallet.level]
        
        if wallet.experience >= required_exp:
            old_level = wallet.level
            wallet.level += 1
            
            # Level up bonus
            level_bonus = wallet.level * 10000
            wallet.hgov_balance += level_bonus
            wallet.badges.append(f"Level {wallet.level} Achieved")
            
            await self._record_transaction("system", wallet.agent_id, level_bonus, TokenType.HGOV, f"Level {wallet.level} bonus")
            
            return {
                'leveled_up': True,
                'old_level': old_level,
                'new_level': wallet.level,
                'bonus_reward': level_bonus,
                'new_multiplier': self.level_multipliers[min(wallet.level - 1, len(self.level_multipliers) - 1)]
            }
        
        return None
    
    async def _check_new_badges(self, wallet: VirtualWallet, action: str, performance_score: float) -> List[str]:
        """Check for new achievement badges"""
        
        new_badges = []
        
        # Performance badges
        if performance_score >= 0.95 and "Performance Excellence" not in wallet.badges:
            wallet.badges.append("Performance Excellence")
            new_badges.append("Performance Excellence")
        
        # Action-specific badges
        action_badges = {
            'bug_detection': ("Bug Detective", 10),
            'system_healing': ("System Healer", 15),
            'vulnerability_scan': ("Security Scanner", 20),
            'chaos_test_pass': ("Chaos Master", 5)
        }
        
        if action in action_badges:
            badge_name, threshold = action_badges[action]
            action_count = sum(1 for tx in self.transaction_history 
                             if tx.to_agent == wallet.agent_id and action in tx.reason)
            
            if action_count >= threshold and badge_name not in wallet.badges:
                wallet.badges.append(badge_name)
                new_badges.append(badge_name)
                
                # Badge bonus
                badge_bonus = threshold * 1000
                wallet.hgov_balance += badge_bonus
                await self._record_transaction("system", wallet.agent_id, badge_bonus, TokenType.HGOV, f"{badge_name} badge bonus")
        
        return new_badges
    
    async def _record_transaction(self, from_agent: str, to_agent: str, amount: int, 
                                token_type: TokenType, reason: str):
        """Record virtual transaction"""
        
        tx = VirtualTransaction(
            tx_id=f"vtx_{int(time.time())}_{random.randint(1000, 9999)}",
            from_agent=from_agent,
            to_agent=to_agent,
            amount=amount,
            token_type=token_type,
            reason=reason,
            timestamp=datetime.now(),
            virtual=True
        )
        
        self.transaction_history.append(tx)
        
        # Keep only last 10000 transactions to manage memory
        if len(self.transaction_history) > 10000:
            self.transaction_history = self.transaction_history[-8000:]

# Example usage
async def demo_virtual_economy():
    """Demonstrate the virtual economy"""
    
    engine = VirtualRewardEngine('virtual-config.json')
    
    # Register AI agents
    monitor_agent = await engine.register_ai_agent("ai_monitor_001", AIAgentType.MONITOR)
    hunter_agent = await engine.register_ai_agent("ai_hunter_001", AIAgentType.HUNTER)
    healer_agent = await engine.register_ai_agent("ai_healer_001", AIAgentType.HEALER)
    
    # Simulate AI actions and rewards
    await engine.reward_ai_action("ai_monitor_001", "uptime_monitoring", performance_score=0.98)
    await engine.reward_ai_action("ai_hunter_001", "bug_detection", performance_score=0.95, bonus_multiplier=2.0)
    await engine.reward_ai_action("ai_healer_001", "system_healing", performance_score=0.92)
    
    # AI purchases from marketplace
    await engine.ai_marketplace_purchase("ai_hunter_001", "priority_queue_access")
    
    # Create AI team
    await engine.create_ai_team("Elite_Defenders", "ai_hunter_001", ["ai_monitor_001", "ai_healer_001"])
    
    # Virtual staking
    await engine.virtual_staking("ai_hunter_001", 50000, TokenType.HGOV)
    
    # Get portfolios
    hunter_portfolio = await engine.get_agent_portfolio("ai_hunter_001")
    print(f"\n📊 Hunter Portfolio: {json.dumps(hunter_portfolio, indent=2, default=str)}")
    
    # Generate leaderboard
    leaderboard = await engine.generate_leaderboard("total_earned")
    print(f"\n🏆 Top AI Agents: {json.dumps(leaderboard, indent=2)}")

if __name__ == "__main__":
    asyncio.run(demo_virtual_economy())