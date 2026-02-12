#!/usr/bin/env python3
"""
VetSorcery Beta Client Scoring System
Identifies the 10-15 highest potential clients for HardCard coaching platform beta
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ClinicProfile:
    name: str
    owner: str
    monthly_revenue: int
    team_size: int
    years_in_business: int
    engagement_score: int  # 1-10 based on VetSorcery usage
    growth_trajectory: str  # "declining", "stable", "growing", "rapidly_growing"
    tech_adoption: int  # 1-10 willingness to try new tools
    feedback_quality: int  # 1-10 based on past interactions
    referral_potential: int  # 1-10 likelihood to refer others
    geographic_location: str
    specialties: List[str]

class BetaClientScorer:
    """
    Scores VetSorcery clients for beta program suitability
    Focus: Quality feedback + Success potential + Reference value
    """
    
    def __init__(self, min_score: float = 7.0):
        self.min_score = min_score
        self.weight_factors = {
            'revenue_stability': 0.15,      # Higher revenue = more credible case study
            'engagement': 0.25,             # High engagement = will actually use tools
            'growth_potential': 0.20,       # Growing practices = better transformation stories
            'feedback_quality': 0.20,       # Quality feedback = better product development
            'referral_potential': 0.20      # References = future client acquisition
        }
    
    def calculate_revenue_score(self, revenue: int) -> int:
        """Score based on monthly revenue - higher = more credible testimonial"""
        if revenue >= 100000: return 10    # $100K+ monthly = premium practice
        elif revenue >= 75000: return 9    # $75-100K = very successful
        elif revenue >= 50000: return 8    # $50-75K = successful
        elif revenue >= 30000: return 6    # $30-50K = stable
        elif revenue >= 20000: return 4    # $20-30K = growing
        else: return 2                     # <$20K = struggling
    
    def calculate_engagement_score(self, engagement: int, tech_adoption: int) -> int:
        """Combined engagement and tech adoption score"""
        return min(10, int((engagement * 0.7) + (tech_adoption * 0.3)))
    
    def calculate_growth_score(self, trajectory: str, years: int) -> int:
        """Score based on growth trajectory and business maturity"""
        trajectory_scores = {
            'rapidly_growing': 10,
            'growing': 8,
            'stable': 6,
            'declining': 2
        }
        
        base_score = trajectory_scores.get(trajectory, 4)
        
        # Bonus for established practices (3+ years) - more credible
        if years >= 5:
            base_score += 2
        elif years >= 3:
            base_score += 1
        
        return min(10, base_score)
    
    def calculate_composite_score(self, clinic: ClinicProfile) -> Tuple[int, Dict[str, int]]:
        """Calculate weighted composite score with breakdown"""
        
        scores = {
            'revenue_stability': self.calculate_revenue_score(clinic.monthly_revenue),
            'engagement': self.calculate_engagement_score(clinic.engagement_score, clinic.tech_adoption),
            'growth_potential': self.calculate_growth_score(clinic.growth_trajectory, clinic.years_in_business),
            'feedback_quality': clinic.feedback_quality,
            'referral_potential': clinic.referral_potential
        }
        
        # Calculate weighted average
        composite = sum(scores[factor] * weight for factor, weight in self.weight_factors.items())
        
        return round(composite, 1), scores
    
    def rank_clients(self, clinics: List[ClinicProfile]) -> List[Tuple[ClinicProfile, int, Dict[str, int]]]:
        """Rank all clinics by beta suitability score"""
        
        scored_clinics = []
        for clinic in clinics:
            score, breakdown = self.calculate_composite_score(clinic)
            scored_clinics.append((clinic, score, breakdown))
        
        # Sort by score descending
        return sorted(scored_clinics, key=lambda x: x[1], reverse=True)
    
    def select_beta_cohort(self, clinics: List[ClinicProfile], target_count: int = 15) -> Dict:
        """Select optimal beta client cohort"""
        
        ranked = self.rank_clients(clinics)
        
        # Filter by minimum score  
        qualified = [(clinic, score, breakdown) for clinic, score, breakdown in ranked if score >= self.min_score]
        
        # Debug: show all scores
        print(f"\\n🔍 SCORING BREAKDOWN:")
        for clinic, score, breakdown in ranked[:5]:  # Show top 5
            print(f"   {clinic.name}: {score}/100 - {breakdown}")
        
        print(f"\\n✅ {len(qualified)} clinics meet minimum score of {self.min_score}/10")
        
        
        # Select top candidates ensuring diversity
        selected = []
        locations_used = set()
        specialties_used = set()
        
        for clinic, score, breakdown in qualified:
            if len(selected) >= target_count:
                break
                
            # Prefer geographic diversity for broader case studies
            location_bonus = 0 if clinic.geographic_location in locations_used else 5
            
            # Prefer specialty diversity
            specialty_bonus = 0
            for specialty in clinic.specialties:
                if specialty not in specialties_used:
                    specialty_bonus += 2
                    break
            
            adjusted_score = score + location_bonus + specialty_bonus
            
            selected.append({
                'clinic': clinic,
                'score': score,
                'adjusted_score': adjusted_score,
                'breakdown': breakdown,
                'selection_reasons': self._get_selection_reasons(clinic, score, breakdown)
            })
            
            locations_used.add(clinic.geographic_location)
            specialties_used.update(clinic.specialties)
        
        return {
            'selected_cohort': selected[:target_count],
            'total_qualified': len(qualified),
            'cohort_stats': self._calculate_cohort_stats(selected[:target_count]),
            'selection_timestamp': datetime.now().isoformat()
        }
    
    def _get_selection_reasons(self, clinic: ClinicProfile, score: int, breakdown: Dict[str, int]) -> List[str]:
        """Generate human-readable selection reasons"""
        reasons = []
        
        if breakdown['revenue_stability'] >= 8:
            reasons.append(f"Strong revenue base (${clinic.monthly_revenue:,}/month)")
        
        if breakdown['engagement'] >= 8:
            reasons.append("High engagement with VetSorcery platform")
        
        if breakdown['growth_potential'] >= 8:
            reasons.append(f"Strong growth trajectory ({clinic.growth_trajectory})")
        
        if breakdown['feedback_quality'] >= 8:
            reasons.append("History of providing valuable feedback")
        
        if breakdown['referral_potential'] >= 8:
            reasons.append("High likelihood to refer other practices")
        
        if clinic.years_in_business >= 5:
            reasons.append(f"Established practice ({clinic.years_in_business} years)")
        
        return reasons
    
    def _calculate_cohort_stats(self, selected: List[Dict]) -> Dict:
        """Calculate statistics for selected cohort"""
        
        if not selected:
            return {
                'cohort_size': 0,
                'total_monthly_revenue': 0,
                'average_score': 0,
                'projected_beta_revenue': 0,
                'growth_distribution': {},
                'geographic_coverage': 0,
                'specialty_coverage': 0
            }
        
        total_revenue = sum(s['clinic'].monthly_revenue for s in selected)
        avg_score = sum(s['score'] for s in selected) / len(selected)
        
        growth_distribution = {}
        for s in selected:
            trajectory = s['clinic'].growth_trajectory
            growth_distribution[trajectory] = growth_distribution.get(trajectory, 0) + 1
        
        return {
            'cohort_size': len(selected),
            'total_monthly_revenue': total_revenue,
            'average_score': round(avg_score, 1),
            'projected_beta_revenue': len(selected) * 199,  # $199/month per client
            'growth_distribution': growth_distribution,
            'geographic_coverage': len(set(s['clinic'].geographic_location for s in selected)),
            'specialty_coverage': len(set(spec for s in selected for spec in s['clinic'].specialties))
        }

def generate_sample_clinics() -> List[ClinicProfile]:
    """Generate sample VetSorcery client data for testing"""
    
    return [
        ClinicProfile(
            name="Peak Performance Veterinary",
            owner="Dr. Sarah Chen",
            monthly_revenue=85000,
            team_size=12,
            years_in_business=7,
            engagement_score=9,
            growth_trajectory="rapidly_growing",
            tech_adoption=9,
            feedback_quality=9,
            referral_potential=8,
            geographic_location="Austin, TX",
            specialties=["Emergency Medicine", "Surgery"]
        ),
        ClinicProfile(
            name="Riverside Animal Hospital", 
            owner="Dr. Michael Rodriguez",
            monthly_revenue=65000,
            team_size=8,
            years_in_business=12,
            engagement_score=8,
            growth_trajectory="growing",
            tech_adoption=7,
            feedback_quality=8,
            referral_potential=9,
            geographic_location="Portland, OR",
            specialties=["General Practice", "Dentistry"]
        ),
        ClinicProfile(
            name="Mountain View Veterinary Clinic",
            owner="Dr. Jennifer Park",
            monthly_revenue=45000,
            team_size=6,
            years_in_business=4,
            engagement_score=9,
            growth_trajectory="growing",
            tech_adoption=8,
            feedback_quality=9,
            referral_potential=7,
            geographic_location="Denver, CO",
            specialties=["General Practice", "Exotic Animals"]
        ),
        ClinicProfile(
            name="Sunset Boulevard Pet Care",
            owner="Dr. David Kim",
            monthly_revenue=95000,
            team_size=15,
            years_in_business=8,
            engagement_score=7,
            growth_trajectory="stable",
            tech_adoption=6,
            feedback_quality=7,
            referral_potential=8,
            geographic_location="Los Angeles, CA",
            specialties=["Surgery", "Oncology", "Cardiology"]
        ),
        ClinicProfile(
            name="Happy Paws Veterinary",
            owner="Dr. Lisa Thompson",
            monthly_revenue=35000,
            team_size=4,
            years_in_business=3,
            engagement_score=8,
            growth_trajectory="rapidly_growing",
            tech_adoption=9,
            feedback_quality=8,
            referral_potential=6,
            geographic_location="Nashville, TN",
            specialties=["General Practice"]
        ),
        # Add more sample clinics to test algorithm
        ClinicProfile(
            name="City Center Animal Hospital",
            owner="Dr. Robert Martinez",
            monthly_revenue=75000,
            team_size=10,
            years_in_business=15,
            engagement_score=6,
            growth_trajectory="stable",
            tech_adoption=5,
            feedback_quality=6,
            referral_potential=7,
            geographic_location="Chicago, IL",
            specialties=["General Practice", "Surgery"]
        ),
        ClinicProfile(
            name="Coastal Veterinary Services",
            owner="Dr. Amanda Foster",
            monthly_revenue=55000,
            team_size=7,
            years_in_business=6,
            engagement_score=9,
            growth_trajectory="growing",
            tech_adoption=8,
            feedback_quality=9,
            referral_potential=8,
            geographic_location="San Diego, CA",
            specialties=["Marine Animal Care", "Surgery"]
        ),
        ClinicProfile(
            name="Northside Pet Clinic",
            owner="Dr. James Wilson",
            monthly_revenue=42000,
            team_size=5,
            years_in_business=9,
            engagement_score=7,
            growth_trajectory="stable",
            tech_adoption=6,
            feedback_quality=7,
            referral_potential=6,
            geographic_location="Minneapolis, MN",
            specialties=["General Practice", "Geriatric Care"]
        )
    ]

def main():
    """Run beta client selection process"""
    
    print("🏥 VetSorcery Beta Client Selection System")
    print("=" * 50)
    
    # Initialize scorer
    scorer = BetaClientScorer(min_score=7.0)
    
    # Load sample data (in production, load from VetSorcery database)
    clinics = generate_sample_clinics()
    print(f"📊 Analyzing {len(clinics)} VetSorcery clients...")
    
    # Select beta cohort
    result = scorer.select_beta_cohort(clinics, target_count=15)
    
    # Display results
    print(f"\n🎯 SELECTED BETA COHORT ({result['cohort_stats']['cohort_size']} clients)")
    print("-" * 50)
    
    for i, client in enumerate(result['selected_cohort'], 1):
        clinic = client['clinic']
        print(f"\n{i}. {clinic.name}")
        print(f"   Owner: {clinic.owner}")
        print(f"   Revenue: ${clinic.monthly_revenue:,}/month")
        print(f"   Score: {client['score']}/100 (Adjusted: {client['adjusted_score']}/100)")
        print(f"   Location: {clinic.geographic_location}")
        print(f"   Reasons: {', '.join(client['selection_reasons'])}")
    
    # Display cohort statistics
    stats = result['cohort_stats']
    print(f"\n📈 COHORT STATISTICS")
    print("-" * 30)
    print(f"Total Cohort Revenue: ${stats['total_monthly_revenue']:,}/month")
    print(f"Beta Program Revenue: ${stats['projected_beta_revenue']:,}/month")
    print(f"Average Score: {stats['average_score']}/100")
    print(f"Geographic Coverage: {stats['geographic_coverage']} locations")
    print(f"Specialty Coverage: {stats['specialty_coverage']} specialties")
    print(f"Growth Distribution: {stats['growth_distribution']}")
    
    # Save results
    with open('beta_client_selection.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to beta_client_selection.json")
    print(f"🚀 Ready to begin VetSorcery beta program outreach!")

if __name__ == "__main__":
    main()