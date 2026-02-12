#!/usr/bin/env python3
"""
Flash Bounty System: Instant rewards for critical bug detection
Creates immediate bounties for urgent issues with gamified incentives
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import aiohttp
import asyncpg
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class HunterLevel(Enum):
    ROOKIE = "rookie"
    VETERAN = "veteran"
    ELITE = "elite"
    LEGENDARY = "legendary"

@dataclass
class FlashBounty:
    """Flash bounty for urgent issues"""
    id: str
    title: str
    description: str
    severity: Severity
    pool_amount: int
    multiplier: float
    deadline: datetime
    auto_created: bool
    requirements: List[str]
    eligible_levels: List[HunterLevel]
    created_at: datetime
    status: str = "active"

@dataclass
class Hunter:
    """Bug bounty hunter profile"""
    id: str
    username: str
    level: HunterLevel
    points: int
    total_rewards: int
    bugs_found: int
    response_time_avg: float
    success_rate: float
    badges: List[str]
    team_id: Optional[str] = None

@dataclass
class BugSubmission:
    """Bug submission from hunter"""
    id: str
    bounty_id: str
    hunter_id: str
    title: str
    description: str
    severity: Severity
    proof_of_concept: str
    fix_suggestion: str
    submitted_at: datetime
    verified: bool = False
    reward_amount: int = 0

class FlashBountySystem:
    """Manages flash bounties and instant rewards"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.db_pool = None
        self.active_bounties = {}
        self.hunters = {}
        self.submissions = {}
        
        # Reward multipliers
        self.level_multipliers = {
            HunterLevel.ROOKIE: 1.0,
            HunterLevel.VETERAN: 1.2,
            HunterLevel.ELITE: 1.5,
            HunterLevel.LEGENDARY: 2.0
        }
        
        # Achievement thresholds
        self.achievements = self.config['gamification']['achievement_system']
    
    async def initialize(self):
        """Initialize the flash bounty system"""
        # Connect to database
        self.db_pool = await asyncpg.create_pool(
            host=self.config['database']['host'],
            port=self.config['database']['port'],
            user=self.config['database']['user'],
            password=self.config['database']['password'],
            database=self.config['database']['name']
        )
        
        # Load existing hunters and bounties
        await self._load_hunters()
        await self._load_active_bounties()
        
        print("🚀 Flash Bounty System initialized!")
    
    async def create_flash_bounty(self, 
                                issue_data: Dict, 
                                urgency_score: float,
                                auto_created: bool = True) -> FlashBounty:
        """Create a flash bounty for urgent issues"""
        
        # Calculate bounty parameters
        severity = self._calculate_severity(issue_data, urgency_score)
        pool_amount = self._calculate_pool_amount(severity, urgency_score)
        multiplier = self._calculate_multiplier(urgency_score, auto_created)
        deadline = datetime.now() + timedelta(hours=self._calculate_deadline_hours(severity))
        eligible_levels = self._get_eligible_levels(severity)
        
        # Create flash bounty
        flash_bounty = FlashBounty(
            id=f"flash_{int(time.time())}_{severity.value}",
            title=f"🚨 FLASH BOUNTY: {issue_data.get('title', 'Critical Issue')}",
            description=self._format_bounty_description(issue_data, urgency_score),
            severity=severity,
            pool_amount=pool_amount,
            multiplier=multiplier,
            deadline=deadline,
            auto_created=auto_created,
            requirements=self._generate_requirements(issue_data, severity),
            eligible_levels=eligible_levels,
            created_at=datetime.now()
        )
        
        # Store bounty
        await self._store_bounty(flash_bounty)
        self.active_bounties[flash_bounty.id] = flash_bounty
        
        # Notify eligible hunters
        await self._notify_eligible_hunters(flash_bounty)
        
        # Start bounty monitoring
        asyncio.create_task(self._monitor_bounty(flash_bounty))
        
        print(f"⚡ Flash bounty created: {flash_bounty.title}")
        print(f"💰 Pool: ${flash_bounty.pool_amount:,} (${flash_bounty.multiplier}x multiplier)")
        print(f"⏰ Deadline: {flash_bounty.deadline}")
        
        return flash_bounty
    
    async def submit_bug_report(self, 
                              bounty_id: str, 
                              hunter_id: str, 
                              report_data: Dict) -> BugSubmission:
        """Submit a bug report for a bounty"""
        
        # Validate submission
        if bounty_id not in self.active_bounties:
            raise ValueError("Bounty not found or inactive")
        
        if hunter_id not in self.hunters:
            raise ValueError("Hunter not registered")
        
        bounty = self.active_bounties[bounty_id]
        hunter = self.hunters[hunter_id]
        
        # Check eligibility
        if hunter.level not in bounty.eligible_levels:
            raise ValueError(f"Hunter level {hunter.level.value} not eligible for this bounty")
        
        # Check deadline
        if datetime.now() > bounty.deadline:
            raise ValueError("Bounty deadline has passed")
        
        # Create submission
        submission = BugSubmission(
            id=f"sub_{int(time.time())}_{hunter_id}",
            bounty_id=bounty_id,
            hunter_id=hunter_id,
            title=report_data['title'],
            description=report_data['description'],
            severity=Severity(report_data['severity']),
            proof_of_concept=report_data['proof_of_concept'],
            fix_suggestion=report_data.get('fix_suggestion', ''),
            submitted_at=datetime.now()
        )
        
        # Store submission
        await self._store_submission(submission)
        self.submissions[submission.id] = submission
        
        # Start instant verification for high-value bounties
        if bounty.pool_amount >= 10000:
            asyncio.create_task(self._instant_verification(submission))
        
        print(f"📝 Bug submission received: {submission.title}")
        print(f"🕒 Response time: {self._calculate_response_time(bounty, submission)} minutes")
        
        return submission
    
    async def verify_and_reward(self, 
                              submission_id: str, 
                              verification_result: Dict) -> Dict:
        """Verify submission and distribute rewards"""
        
        if submission_id not in self.submissions:
            raise ValueError("Submission not found")
        
        submission = self.submissions[submission_id]
        bounty = self.active_bounties[submission.bounty_id]
        hunter = self.hunters[submission.hunter_id]
        
        # Process verification
        if verification_result['valid']:
            # Calculate reward
            base_reward = self._calculate_base_reward(bounty, submission)
            level_bonus = base_reward * (self.level_multipliers[hunter.level] - 1.0)
            speed_bonus = self._calculate_speed_bonus(bounty, submission)
            quality_bonus = self._calculate_quality_bonus(submission, verification_result)
            
            total_reward = int(base_reward + level_bonus + speed_bonus + quality_bonus)
            
            # Update submission
            submission.verified = True
            submission.reward_amount = total_reward
            
            # Update hunter stats
            await self._update_hunter_stats(hunter, submission, total_reward)
            
            # Distribute reward
            await self._distribute_reward(hunter, total_reward)
            
            # Check for achievements
            await self._check_achievements(hunter, submission)
            
            # Close bounty if resolved
            if verification_result.get('resolves_issue', False):
                await self._close_bounty(bounty, submission)
            
            print(f"✅ Bug verified and rewarded!")
            print(f"💰 Reward: ${total_reward:,}")
            print(f"🏆 Hunter: {hunter.username} ({hunter.level.value})")
            
            return {
                'verified': True,
                'reward_amount': total_reward,
                'hunter_level': hunter.level.value,
                'achievements_unlocked': verification_result.get('achievements', [])
            }
        
        else:
            print(f"❌ Bug submission rejected: {verification_result.get('reason', 'Invalid')}")
            return {
                'verified': False,
                'reason': verification_result.get('reason', 'Invalid submission')
            }
    
    async def get_leaderboard(self, period: str = "all_time") -> List[Dict]:
        """Get hunter leaderboard"""
        
        # Calculate period filter
        if period == "monthly":
            since = datetime.now() - timedelta(days=30)
        elif period == "weekly":
            since = datetime.now() - timedelta(days=7)
        else:
            since = None
        
        # Get rankings
        rankings = []
        for hunter in self.hunters.values():
            stats = await self._get_hunter_period_stats(hunter, since)
            rankings.append({
                'rank': 0,  # Will be calculated
                'username': hunter.username,
                'level': hunter.level.value,
                'points': stats['points'],
                'rewards': stats['rewards'],
                'bugs_found': stats['bugs_found'],
                'success_rate': stats['success_rate'],
                'avg_response_time': stats['avg_response_time'],
                'badges': hunter.badges
            })
        
        # Sort by points and assign ranks
        rankings.sort(key=lambda x: x['points'], reverse=True)
        for i, hunter_data in enumerate(rankings):
            hunter_data['rank'] = i + 1
        
        return rankings[:50]  # Top 50
    
    async def start_seasonal_event(self, event_name: str):
        """Start a seasonal bug bounty event"""
        
        event_config = self.config['gamification']['seasonal_events'][event_name]
        
        print(f"🎉 Starting seasonal event: {event_name}")
        print(f"💰 Total pool: ${event_config['total_pool']:,}")
        print(f"⏰ Duration: {event_config['duration']}")
        
        # Create special bounties
        for challenge in event_config['special_challenges']:
            await self._create_challenge_bounty(challenge, event_config)
        
        # Start event monitoring
        asyncio.create_task(self._monitor_seasonal_event(event_name, event_config))
    
    def _calculate_severity(self, issue_data: Dict, urgency_score: float) -> Severity:
        """Calculate bug severity"""
        if urgency_score >= 0.9:
            return Severity.CRITICAL
        elif urgency_score >= 0.7:
            return Severity.HIGH
        elif urgency_score >= 0.4:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def _calculate_pool_amount(self, severity: Severity, urgency_score: float) -> int:
        """Calculate bounty pool amount"""
        base_amounts = {
            Severity.CRITICAL: 100000,
            Severity.HIGH: 25000,
            Severity.MEDIUM: 5000,
            Severity.LOW: 1000
        }
        
        base_amount = base_amounts[severity]
        urgency_multiplier = 1.0 + urgency_score
        
        return int(base_amount * urgency_multiplier)
    
    def _calculate_multiplier(self, urgency_score: float, auto_created: bool) -> float:
        """Calculate reward multiplier"""
        base_multiplier = 1.0
        
        # Urgency bonus
        if urgency_score >= 0.9:
            base_multiplier += 2.0
        elif urgency_score >= 0.7:
            base_multiplier += 1.0
        elif urgency_score >= 0.5:
            base_multiplier += 0.5
        
        # Flash bounty bonus
        if auto_created:
            base_multiplier += 0.5
        
        return base_multiplier
    
    def _calculate_deadline_hours(self, severity: Severity) -> int:
        """Calculate bounty deadline in hours"""
        deadlines = {
            Severity.CRITICAL: 4,   # 4 hours
            Severity.HIGH: 12,      # 12 hours  
            Severity.MEDIUM: 48,    # 2 days
            Severity.LOW: 168       # 1 week
        }
        return deadlines[severity]
    
    def _get_eligible_levels(self, severity: Severity) -> List[HunterLevel]:
        """Get eligible hunter levels for severity"""
        if severity == Severity.CRITICAL:
            return [HunterLevel.ELITE, HunterLevel.LEGENDARY]
        elif severity == Severity.HIGH:
            return [HunterLevel.VETERAN, HunterLevel.ELITE, HunterLevel.LEGENDARY]
        else:
            return list(HunterLevel)
    
    async def _notify_eligible_hunters(self, bounty: FlashBounty):
        """Notify eligible hunters about flash bounty"""
        eligible_hunters = [
            hunter for hunter in self.hunters.values()
            if hunter.level in bounty.eligible_levels
        ]
        
        notification_data = {
            'type': 'flash_bounty',
            'bounty_id': bounty.id,
            'title': bounty.title,
            'pool_amount': bounty.pool_amount,
            'multiplier': bounty.multiplier,
            'deadline': bounty.deadline.isoformat(),
            'severity': bounty.severity.value
        }
        
        # Send notifications via multiple channels
        tasks = []
        for hunter in eligible_hunters:
            tasks.append(self._send_hunter_notification(hunter, notification_data))
        
        await asyncio.gather(*tasks)
        
        print(f"📢 Notified {len(eligible_hunters)} eligible hunters")

# Example usage
async def main():
    """Example usage of flash bounty system"""
    
    # Initialize system
    system = FlashBountySystem('bounty-config.json')
    await system.initialize()
    
    # Create flash bounty for critical issue
    issue_data = {
        'title': 'Smart Contract Reentrancy Vulnerability',
        'description': 'Critical reentrancy vulnerability in GuardianCouncil contract',
        'component': 'smart_contract',
        'affected_users': 10000,
        'financial_impact': 1000000
    }
    
    flash_bounty = await system.create_flash_bounty(issue_data, urgency_score=0.95)
    
    # Simulate bug submission
    report_data = {
        'title': 'Reentrancy in emergency freeze function',
        'description': 'Detailed vulnerability analysis...',
        'severity': 'critical',
        'proof_of_concept': 'exploit code...',
        'fix_suggestion': 'Use reentrancy guard...'
    }
    
    submission = await system.submit_bug_report(
        flash_bounty.id, 
        'hunter_123', 
        report_data
    )
    
    # Verify and reward
    verification_result = {
        'valid': True,
        'quality_score': 0.95,
        'resolves_issue': True,
        'achievements': ['speed_demon']
    }
    
    result = await system.verify_and_reward(submission.id, verification_result)
    print(f"Reward distributed: {result}")

if __name__ == "__main__":
    asyncio.run(main())