#!/usr/bin/env python3
"""
HardCard Beta Client Success Tracking System
Measures and documents transformation stories for celebrity partnership credibility
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class MetricType(Enum):
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    TEAM_SATISFACTION = "team_satisfaction"
    CLIENT_SATISFACTION = "client_satisfaction"
    EFFICIENCY = "efficiency"
    STRATEGIC_CLARITY = "strategic_clarity"

@dataclass
class BaselineMetrics:
    """Capture starting point for each beta client"""
    clinic_id: str
    clinic_name: str
    owner_name: str
    measurement_date: str
    
    # Financial metrics
    monthly_revenue: int
    profit_margin: float
    average_transaction_value: int
    
    # Operational metrics
    appointments_per_day: int
    client_retention_rate: float
    team_turnover_rate: float
    
    # Engagement metrics
    platform_logins_per_week: int
    framework_completion_rate: float
    goal_achievement_rate: float
    
    # Qualitative metrics (1-10 scale)
    strategic_clarity_score: int
    leadership_confidence_score: int
    team_satisfaction_score: int
    work_life_balance_score: int

@dataclass
class ProgressMetrics:
    """Track improvements over time"""
    clinic_id: str
    measurement_date: str
    days_since_baseline: int
    
    # Updated metrics
    monthly_revenue: int
    profit_margin: float
    average_transaction_value: int
    appointments_per_day: int
    client_retention_rate: float
    team_turnover_rate: float
    
    # Platform engagement
    platform_logins_per_week: int
    framework_completion_rate: float
    frameworks_completed: List[str]
    goals_achieved: int
    habits_tracked_days: int
    
    # Qualitative improvements
    strategic_clarity_score: int
    leadership_confidence_score: int
    team_satisfaction_score: int
    work_life_balance_score: int
    
    # Transformation notes
    key_insights: List[str]
    behavioral_changes: List[str]
    team_feedback: str
    owner_testimonial: str

@dataclass
class TransformationStory:
    """Compelling narrative for partnership pitches"""
    clinic_id: str
    clinic_name: str
    owner_name: str
    story_title: str
    
    # Transformation timeline
    baseline_date: str
    current_date: str
    transformation_period_months: int
    
    # Key improvements
    revenue_growth_percent: float
    revenue_growth_dollar: int
    efficiency_improvement_percent: float
    satisfaction_improvement_percent: float
    
    # Strategic breakthroughs
    hedgehog_concept_insight: str
    flywheel_momentum_created: str
    leadership_transformation: str
    discipline_habits_built: List[str]
    
    # Compelling narrative
    challenge_before: str
    breakthrough_moment: str
    results_achieved: str
    future_vision: str
    
    # Credibility factors
    years_in_business: int
    team_size: int
    specialty_focus: str
    geographic_location: str
    
    # Partnership value
    referral_potential_score: int
    case_study_willingness: bool
    testimonial_video_available: bool
    speaking_opportunity_interest: bool

class BetaSuccessTracker:
    """Track and analyze beta client transformations"""
    
    def __init__(self, data_file: str = "beta_client_data.json"):
        self.data_file = data_file
        self.baselines: Dict[str, BaselineMetrics] = {}
        self.progress_history: Dict[str, List[ProgressMetrics]] = {}
        self.transformation_stories: Dict[str, TransformationStory] = {}
        self.load_data()
    
    def load_data(self):
        """Load existing client data"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                
            # Load baselines
            for clinic_id, baseline_data in data.get('baselines', {}).items():
                self.baselines[clinic_id] = BaselineMetrics(**baseline_data)
            
            # Load progress history
            for clinic_id, progress_list in data.get('progress_history', {}).items():
                self.progress_history[clinic_id] = [
                    ProgressMetrics(**progress_data) for progress_data in progress_list
                ]
            
            # Load transformation stories
            for clinic_id, story_data in data.get('transformation_stories', {}).items():
                self.transformation_stories[clinic_id] = TransformationStory(**story_data)
                
        except FileNotFoundError:
            # First run - initialize empty data
            pass
    
    def save_data(self):
        """Save all client data"""
        data = {
            'baselines': {
                clinic_id: asdict(baseline) 
                for clinic_id, baseline in self.baselines.items()
            },
            'progress_history': {
                clinic_id: [asdict(progress) for progress in progress_list]
                for clinic_id, progress_list in self.progress_history.items()
            },
            'transformation_stories': {
                clinic_id: asdict(story)
                for clinic_id, story in self.transformation_stories.items()
            },
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def set_baseline(self, baseline: BaselineMetrics):
        """Set baseline metrics for a client"""
        self.baselines[baseline.clinic_id] = baseline
        self.progress_history[baseline.clinic_id] = []
        self.save_data()
        print(f"✅ Baseline set for {baseline.clinic_name}")
    
    def add_progress_measurement(self, progress: ProgressMetrics):
        """Add progress measurement for a client"""
        if progress.clinic_id not in self.progress_history:
            self.progress_history[progress.clinic_id] = []
        
        self.progress_history[progress.clinic_id].append(progress)
        self.save_data()
        print(f"✅ Progress recorded for clinic {progress.clinic_id}")
    
    def generate_transformation_story(self, clinic_id: str) -> Optional[TransformationStory]:
        """Generate compelling transformation story from data"""
        if clinic_id not in self.baselines or clinic_id not in self.progress_history:
            return None
        
        baseline = self.baselines[clinic_id]
        progress_list = self.progress_history[clinic_id]
        
        if not progress_list:
            return None
        
        latest_progress = progress_list[-1]
        
        # Calculate improvements
        revenue_growth_dollar = latest_progress.monthly_revenue - baseline.monthly_revenue
        revenue_growth_percent = (revenue_growth_dollar / baseline.monthly_revenue) * 100
        
        efficiency_improvement = ((latest_progress.appointments_per_day - baseline.appointments_per_day) / baseline.appointments_per_day) * 100
        
        satisfaction_improvement = ((latest_progress.team_satisfaction_score - baseline.team_satisfaction_score) / baseline.team_satisfaction_score) * 100
        
        # Generate story
        story = TransformationStory(
            clinic_id=clinic_id,
            clinic_name=baseline.clinic_name,
            owner_name=baseline.owner_name,
            story_title=f"How {baseline.clinic_name} Achieved {revenue_growth_percent:.1f}% Revenue Growth in {latest_progress.days_since_baseline // 30} Months",
            
            baseline_date=baseline.measurement_date,
            current_date=latest_progress.measurement_date,
            transformation_period_months=latest_progress.days_since_baseline // 30,
            
            revenue_growth_percent=revenue_growth_percent,
            revenue_growth_dollar=revenue_growth_dollar,
            efficiency_improvement_percent=efficiency_improvement,
            satisfaction_improvement_percent=satisfaction_improvement,
            
            hedgehog_concept_insight=self._extract_insight(latest_progress.key_insights, "hedgehog"),
            flywheel_momentum_created=self._extract_insight(latest_progress.key_insights, "flywheel"),
            leadership_transformation=self._extract_insight(latest_progress.key_insights, "leadership"),
            discipline_habits_built=latest_progress.behavioral_changes,
            
            challenge_before=f"Despite generating ${baseline.monthly_revenue:,}/month, the practice lacked strategic clarity and sustainable growth systems.",
            breakthrough_moment=f"The turning point came when {baseline.owner_name} completed the Hedgehog Concept exercise and discovered their true competitive advantage.",
            results_achieved=f"Within {latest_progress.days_since_baseline // 30} months: {revenue_growth_percent:.1f}% revenue growth (${revenue_growth_dollar:,}), {efficiency_improvement:.1f}% efficiency improvement, and {satisfaction_improvement:.1f}% team satisfaction increase.",
            future_vision=f"With these systems in place, {baseline.clinic_name} is projected to reach ${latest_progress.monthly_revenue * 1.5:,.0f}/month within the next 12 months.",
            
            years_in_business=10,  # Would be captured in baseline
            team_size=8,  # Would be captured in baseline  
            specialty_focus="General Practice",  # Would be captured in baseline
            geographic_location="Austin, TX",  # Would be captured in baseline
            
            referral_potential_score=9,
            case_study_willingness=True,
            testimonial_video_available=False,
            speaking_opportunity_interest=True
        )
        
        self.transformation_stories[clinic_id] = story
        self.save_data()
        return story
    
    def _extract_insight(self, insights: List[str], framework: str) -> str:
        """Extract specific framework insights"""
        framework_insights = [insight for insight in insights if framework.lower() in insight.lower()]
        return framework_insights[0] if framework_insights else f"Significant improvement in {framework} implementation"
    
    def generate_cohort_report(self) -> Dict:
        """Generate comprehensive report for all beta clients"""
        
        total_revenue_growth = 0
        total_clients = len(self.baselines)
        successful_transformations = 0
        case_studies_available = 0
        
        cohort_stories = []
        
        for clinic_id in self.baselines.keys():
            if clinic_id in self.progress_history and self.progress_history[clinic_id]:
                baseline = self.baselines[clinic_id]
                latest = self.progress_history[clinic_id][-1]
                
                revenue_growth = ((latest.monthly_revenue - baseline.monthly_revenue) / baseline.monthly_revenue) * 100
                total_revenue_growth += revenue_growth
                
                if revenue_growth > 20:  # 20%+ growth = success
                    successful_transformations += 1
                
                # Generate story if significant improvement
                if revenue_growth > 15:
                    story = self.generate_transformation_story(clinic_id)
                    if story:
                        cohort_stories.append(story)
                        if story.case_study_willingness:
                            case_studies_available += 1
        
        avg_revenue_growth = total_revenue_growth / total_clients if total_clients > 0 else 0
        success_rate = (successful_transformations / total_clients) * 100 if total_clients > 0 else 0
        
        return {
            'report_date': datetime.now().isoformat(),
            'cohort_size': total_clients,
            'avg_revenue_growth_percent': round(avg_revenue_growth, 1),
            'success_rate_percent': round(success_rate, 1),
            'case_studies_available': case_studies_available,
            'transformation_stories': [asdict(story) for story in cohort_stories],
            'partnership_readiness_metrics': {
                'total_clients_helped': total_clients,
                'average_transformation': f"{avg_revenue_growth:.1f}% revenue growth",
                'success_rate': f"{success_rate:.1f}% of clients achieved 20%+ growth",
                'credible_testimonials': case_studies_available,
                'geographic_coverage': len(set(story.geographic_location for story in cohort_stories)),
                'story_quality': 'High - documented transformations with specific metrics'
            }
        }
    
    def export_for_partnership_pitch(self, output_file: str = "partnership_pitch_data.json"):
        """Export data formatted for Collins/Ferriss partnership pitches"""
        
        cohort_report = self.generate_cohort_report()
        
        # Format for partnership presentation
        pitch_data = {
            'executive_summary': {
                'platform_name': 'HardCard Business Excellence',
                'validation_period': '6 months',
                'client_base': f"{cohort_report['cohort_size']} veterinary practices",
                'average_results': f"{cohort_report['avg_revenue_growth_percent']}% revenue growth",
                'success_rate': f"{cohort_report['success_rate_percent']}% client success rate",
                'case_studies': f"{cohort_report['case_studies_available']} documented transformations"
            },
            'transformation_stories': cohort_report['transformation_stories'][:3],  # Top 3 stories
            'collins_partnership_value': {
                'proven_framework_implementation': True,
                'documented_business_transformations': cohort_report['case_studies_available'],
                'framework_success_rate': f"{cohort_report['success_rate_percent']}%",
                'target_market_validated': 'Veterinary practices (expandable to all businesses)',
                'revenue_potential': '$17M+ annually from Collins ecosystem'
            },
            'ferriss_partnership_value': {
                'optimization_results': f"Average {cohort_report['avg_revenue_growth_percent']}% improvement",
                'scalable_coaching_model': True,
                'premium_client_base': 'High-value practice owners',
                'time_efficient_model': '30 minutes monthly per client',
                'revenue_potential': '$300K monthly passive income'
            },
            'tim_ferriss_show_narrative': {
                'title': 'From Veterinary Software to Business Coaching Empire',
                'hook': f"How I built a ${cohort_report['cohort_size'] * 199 * 12:,} platform by digitizing Jim Collins\' frameworks",
                'proof_points': [
                    f"{cohort_report['cohort_size']} practices transformed",
                    f"Average {cohort_report['avg_revenue_growth_percent']}% revenue growth",
                    f"{cohort_report['success_rate_percent']}% success rate",
                    f"{cohort_report['case_studies_available']} documented case studies"
                ],
                'audience_value': 'Specific frameworks listeners can implement immediately'
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(pitch_data, f, indent=2)
        
        print(f"✅ Partnership pitch data exported to {output_file}")
        return pitch_data

def create_sample_data():
    """Create sample data for testing"""
    tracker = BetaSuccessTracker()
    
    # Sample baseline for Dr. Sarah Chen
    baseline = BaselineMetrics(
        clinic_id="peak_performance_vet",
        clinic_name="Peak Performance Veterinary",
        owner_name="Dr. Sarah Chen",
        measurement_date="2024-08-01",
        
        monthly_revenue=85000,
        profit_margin=0.23,
        average_transaction_value=180,
        
        appointments_per_day=24,
        client_retention_rate=0.78,
        team_turnover_rate=0.15,
        
        platform_logins_per_week=2,
        framework_completion_rate=0.0,
        goal_achievement_rate=0.0,
        
        strategic_clarity_score=6,
        leadership_confidence_score=7,
        team_satisfaction_score=6,
        work_life_balance_score=5
    )
    
    tracker.set_baseline(baseline)
    
    # Sample 3-month progress
    progress = ProgressMetrics(
        clinic_id="peak_performance_vet",
        measurement_date="2024-11-01",
        days_since_baseline=92,
        
        monthly_revenue=112000,
        profit_margin=0.28,
        average_transaction_value=205,
        appointments_per_day=28,
        client_retention_rate=0.85,
        team_turnover_rate=0.08,
        
        platform_logins_per_week=5,
        framework_completion_rate=0.85,
        frameworks_completed=["Hedgehog Concept", "Flywheel Builder", "Level 5 Assessment"],
        goals_achieved=4,
        habits_tracked_days=78,
        
        strategic_clarity_score=9,
        leadership_confidence_score=9,
        team_satisfaction_score=8,
        work_life_balance_score=8,
        
        key_insights=[
            "Hedgehog concept revealed our competitive advantage in emergency medicine specialization",
            "Flywheel showed how excellent emergency care leads to referrals and premium pricing",
            "Leadership assessment highlighted need for more delegation and team development"
        ],
        behavioral_changes=[
            "Morning strategic thinking time (30 minutes daily)",
            "Weekly team leadership meetings",
            "Monthly practice metrics review",
            "Quarterly strategic planning sessions"
        ],
        team_feedback="Dr. Chen has become much more strategic and less reactive. The whole practice feels more organized and purposeful.",
        owner_testimonial="The Hedgehog Concept exercise was a game-changer. For the first time, I have complete clarity on what makes our practice unique and how to build on that systematically."
    )
    
    tracker.add_progress_measurement(progress)
    
    # Generate transformation story
    story = tracker.generate_transformation_story("peak_performance_vet")
    print(f"✅ Sample transformation story created: {story.story_title}")
    
    return tracker

def main():
    """Demo the beta success tracking system"""
    print("🏥 HardCard Beta Success Tracking System")
    print("=" * 50)
    
    # Create sample data
    tracker = create_sample_data()
    
    # Generate cohort report
    report = tracker.generate_cohort_report()
    
    print(f"\n📊 BETA COHORT PERFORMANCE")
    print("-" * 30)
    print(f"Cohort Size: {report['cohort_size']} practices")
    print(f"Average Revenue Growth: {report['avg_revenue_growth_percent']}%")
    print(f"Success Rate: {report['success_rate_percent']}%")
    print(f"Case Studies Available: {report['case_studies_available']}")
    
    # Export partnership data
    pitch_data = tracker.export_for_partnership_pitch()
    
    print(f"\n🎯 PARTNERSHIP PITCH READINESS")
    print("-" * 30)
    exec_summary = pitch_data['executive_summary']
    print(f"Platform: {exec_summary['platform_name']}")
    print(f"Results: {exec_summary['average_results']}")
    print(f"Success Rate: {exec_summary['success_rate']}")
    print(f"Case Studies: {exec_summary['case_studies']}")
    
    print(f"\n🚀 Ready for Collins Partnership Approach!")
    print(f"Story: \"We've helped {report['cohort_size']} practices achieve {report['avg_revenue_growth_percent']}% average revenue growth using your frameworks\"")

if __name__ == "__main__":
    main()