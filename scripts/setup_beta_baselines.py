#!/usr/bin/env python3
"""
Set up baseline measurements for all 6 selected beta clients
Creates initial measurement data for tracking transformations
"""

import json
from datetime import datetime
from beta_success_tracker import BetaSuccessTracker, BaselineMetrics

def setup_all_beta_baselines():
    """Set up baseline measurements for all 6 selected beta clients"""
    
    tracker = BetaSuccessTracker("beta_client_data.json")
    
    # Load selected clients from selection results
    with open('/Users/studio/hardcard/beta_client_selection.json', 'r') as f:
        selection_data = json.load(f)
    
    selected_clients = selection_data['selected_cohort']
    
    print("🏥 Setting up baseline measurements for beta clients")
    print("=" * 55)
    
    baselines = []
    
    for i, client_data in enumerate(selected_clients, 1):
        # Parse clinic info from the string representation
        clinic_str = client_data['clinic']
        
        # Extract clinic details (this is a simplified parser)
        if "Peak Performance Veterinary" in clinic_str:
            baseline = BaselineMetrics(
                clinic_id="peak_performance_vet",
                clinic_name="Peak Performance Veterinary",
                owner_name="Dr. Sarah Chen",
                measurement_date=datetime.now().strftime("%Y-%m-%d"),
                
                # Financial metrics (estimated based on revenue)
                monthly_revenue=85000,
                profit_margin=0.23,
                average_transaction_value=180,
                
                # Operational metrics (industry standards)
                appointments_per_day=24,
                client_retention_rate=0.78,
                team_turnover_rate=0.15,
                
                # Platform engagement (pre-beta)
                platform_logins_per_week=2,
                framework_completion_rate=0.0,
                goal_achievement_rate=0.0,
                
                # Qualitative metrics (1-10 scale, estimated baseline)
                strategic_clarity_score=6,
                leadership_confidence_score=7,
                team_satisfaction_score=6,
                work_life_balance_score=5
            )
        
        elif "Coastal Veterinary Services" in clinic_str:
            baseline = BaselineMetrics(
                clinic_id="coastal_veterinary",
                clinic_name="Coastal Veterinary Services",
                owner_name="Dr. Amanda Foster",
                measurement_date=datetime.now().strftime("%Y-%m-%d"),
                
                monthly_revenue=55000,
                profit_margin=0.21,
                average_transaction_value=165,
                
                appointments_per_day=18,
                client_retention_rate=0.75,
                team_turnover_rate=0.18,
                
                platform_logins_per_week=3,
                framework_completion_rate=0.0,
                goal_achievement_rate=0.0,
                
                strategic_clarity_score=5,
                leadership_confidence_score=6,
                team_satisfaction_score=7,
                work_life_balance_score=4
            )
        
        elif "Riverside Animal Hospital" in clinic_str:
            baseline = BaselineMetrics(
                clinic_id="riverside_animal",
                clinic_name="Riverside Animal Hospital",
                owner_name="Dr. Michael Rodriguez",
                measurement_date=datetime.now().strftime("%Y-%m-%d"),
                
                monthly_revenue=65000,
                profit_margin=0.25,
                average_transaction_value=175,
                
                appointments_per_day=22,
                client_retention_rate=0.82,
                team_turnover_rate=0.12,
                
                platform_logins_per_week=2,
                framework_completion_rate=0.0,
                goal_achievement_rate=0.0,
                
                strategic_clarity_score=7,
                leadership_confidence_score=8,
                team_satisfaction_score=6,
                work_life_balance_score=6
            )
        
        elif "Mountain View Veterinary Clinic" in clinic_str:
            baseline = BaselineMetrics(
                clinic_id="mountain_view_vet",
                clinic_name="Mountain View Veterinary Clinic",
                owner_name="Dr. Jennifer Park",
                measurement_date=datetime.now().strftime("%Y-%m-%d"),
                
                monthly_revenue=45000,
                profit_margin=0.19,
                average_transaction_value=155,
                
                appointments_per_day=16,
                client_retention_rate=0.73,
                team_turnover_rate=0.20,
                
                platform_logins_per_week=4,
                framework_completion_rate=0.0,
                goal_achievement_rate=0.0,
                
                strategic_clarity_score=5,
                leadership_confidence_score=6,
                team_satisfaction_score=8,
                work_life_balance_score=3
            )
        
        elif "Happy Paws Veterinary" in clinic_str:
            baseline = BaselineMetrics(
                clinic_id="happy_paws_vet",
                clinic_name="Happy Paws Veterinary",
                owner_name="Dr. Lisa Thompson",
                measurement_date=datetime.now().strftime("%Y-%m-%d"),
                
                monthly_revenue=35000,
                profit_margin=0.17,
                average_transaction_value=140,
                
                appointments_per_day=14,
                client_retention_rate=0.70,
                team_turnover_rate=0.25,
                
                platform_logins_per_week=3,
                framework_completion_rate=0.0,
                goal_achievement_rate=0.0,
                
                strategic_clarity_score=4,
                leadership_confidence_score=5,
                team_satisfaction_score=7,
                work_life_balance_score=3
            )
        
        elif "Sunset Boulevard Pet Care" in clinic_str:
            baseline = BaselineMetrics(
                clinic_id="sunset_boulevard",
                clinic_name="Sunset Boulevard Pet Care",
                owner_name="Dr. David Kim",
                measurement_date=datetime.now().strftime("%Y-%m-%d"),
                
                monthly_revenue=95000,
                profit_margin=0.27,
                average_transaction_value=195,
                
                appointments_per_day=28,
                client_retention_rate=0.85,
                team_turnover_rate=0.10,
                
                platform_logins_per_week=1,
                framework_completion_rate=0.0,
                goal_achievement_rate=0.0,
                
                strategic_clarity_score=8,
                leadership_confidence_score=7,
                team_satisfaction_score=5,
                work_life_balance_score=7
            )
        
        else:
            continue  # Skip if we can't parse this clinic
        
        baselines.append(baseline)
        tracker.set_baseline(baseline)
        
        print(f"✅ {i}. {baseline.clinic_name}")
        print(f"   Owner: {baseline.owner_name}")
        print(f"   Revenue: ${baseline.monthly_revenue:,}/month")
        print(f"   Strategic Clarity: {baseline.strategic_clarity_score}/10")
        print(f"   Leadership Confidence: {baseline.leadership_confidence_score}/10")
        print()
    
    # Generate initial cohort report
    print("📊 INITIAL COHORT BASELINE SUMMARY")
    print("-" * 40)
    
    total_revenue = sum(b.monthly_revenue for b in baselines)
    avg_strategic_clarity = sum(b.strategic_clarity_score for b in baselines) / len(baselines)
    avg_leadership_confidence = sum(b.leadership_confidence_score for b in baselines) / len(baselines)
    
    print(f"Cohort Size: {len(baselines)} practices")
    print(f"Total Monthly Revenue: ${total_revenue:,}")
    print(f"Average Strategic Clarity: {avg_strategic_clarity:.1f}/10")
    print(f"Average Leadership Confidence: {avg_leadership_confidence:.1f}/10")
    print(f"Beta Program Revenue: ${len(baselines) * 199:,}/month")
    
    # Save baseline summary
    baseline_summary = {
        'baseline_date': datetime.now().isoformat(),
        'cohort_size': len(baselines),
        'total_monthly_revenue': total_revenue,
        'beta_program_revenue': len(baselines) * 199,
        'avg_strategic_clarity': round(avg_strategic_clarity, 1),
        'avg_leadership_confidence': round(avg_leadership_confidence, 1),
        'baseline_metrics': [
            {
                'clinic_id': b.clinic_id,
                'clinic_name': b.clinic_name,
                'owner_name': b.owner_name,
                'monthly_revenue': b.monthly_revenue,
                'strategic_clarity_score': b.strategic_clarity_score,
                'leadership_confidence_score': b.leadership_confidence_score,
                'team_satisfaction_score': b.team_satisfaction_score
            }
            for b in baselines
        ]
    }
    
    with open('/Users/studio/hardcard/beta_baseline_summary.json', 'w') as f:
        json.dump(baseline_summary, f, indent=2)
    
    print(f"\n✅ Baseline data saved to beta_client_data.json")
    print(f"✅ Summary saved to beta_baseline_summary.json")
    print(f"\n🚀 Ready to begin 6-month beta program!")
    print(f"📈 Projected monthly revenue: ${len(baselines) * 199:,}")

if __name__ == "__main__":
    setup_all_beta_baselines()