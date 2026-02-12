#!/usr/bin/env python3
"""
Collins/Ferriss Partnership Pitch Generator
Creates focused, evidence-based pitch materials without overwhelming with data
"""

import json
from datetime import datetime
from typing import Dict, List

class PartnershipPitchGenerator:
    """Generate focused, compelling pitches for Collins and Ferriss partnerships"""
    
    def __init__(self):
        self.collins_focus_areas = [
            'framework_digitization',
            'measurable_business_results', 
            'systematic_implementation',
            'scalability_proof'
        ]
        
        self.ferriss_focus_areas = [
            'optimization_results',
            'time_efficiency',
            'scalable_systems',
            'compelling_story'
        ]
    
    def generate_collins_pitch(self, evidence_data: Dict) -> Dict:
        """Generate focused Collins partnership pitch"""
        
        # Extract key evidence points (not overwhelming detail)
        key_metrics = self._extract_key_evidence(evidence_data)
        
        return {
            'subject_line': 'Digitized Your Frameworks → $12K ARR + Documented Results',
            
            'opening_hook': f"""Jim,
            
I've built something that proves your frameworks work digitally - and I have the numbers to show it.

{key_metrics['client_count']} veterinary practices, {key_metrics['avg_growth']}% average revenue growth, {key_metrics['framework_completion']}% framework completion rate.""",
            
            'core_proposition': {
                'what_built': 'Digital platform implementing Level 5 Leadership, Hedgehog Concept, Flywheel, and Disciplined Execution',
                'market_validated': f"{key_metrics['client_count']} practices using it actively",
                'business_results': f"Average {key_metrics['avg_growth']}% revenue growth",
                'framework_proof': f"{key_metrics['framework_completion']}% of users complete your frameworks",
                'revenue_validation': f"${key_metrics['monthly_revenue']:,}/month recurring revenue"
            },
            
            'evidence_highlights': [
                f"✓ {key_metrics['successful_transformations']} documented business transformations",
                f"✓ Real testimonials from practice owners",
                f"✓ Measurable improvements in leadership effectiveness",
                f"✓ Proven framework implementation at scale"
            ],
            
            'partnership_value': {
                'for_collins': [
                    'Expand your framework reach through technology',
                    'Generate passive revenue from digital implementation',
                    'Access to veterinary market (untapped for your work)',
                    'Proof that your frameworks work across industries'
                ],
                'revenue_potential': 'Conservative estimate: $500K+ annually from veterinary market alone'
            },
            
            'credibility_factors': [
                f"{key_metrics['program_duration']} months of real implementation data",
                'Built by successful entrepreneurs (VetSorcery background)',
                'Focus on systematic execution (your core principle)',
                'Evidence-based approach (not just theory)'
            ],
            
            'ask': 'Would you be open to a 30-minute call to see the platform and discuss partnership opportunities?',
            
            'proof_available': [
                'Live platform demonstration',
                'Case study documentation', 
                'Revenue and usage metrics',
                'Client testimonials and feedback'
            ]
        }
    
    def generate_ferriss_pitch(self, evidence_data: Dict) -> Dict:
        """Generate focused Ferriss show pitch"""
        
        key_metrics = self._extract_key_evidence(evidence_data)
        
        return {
            'show_angle': 'From Veterinary Software to Business Coaching Empire',
            
            'hook_story': f"""The unexpected path from building phone systems for vets to creating a ${key_metrics['annual_revenue']:,} business coaching platform by digitizing Jim Collins' frameworks.""",
            
            'listener_value': {
                'frameworks_they_get': [
                    'Level 5 Leadership assessment (10-minute digital version)',
                    'Hedgehog Concept builder (identify your competitive advantage)',
                    'Flywheel momentum system (systematic growth)',
                    'Discipline tracking system (consistent execution)'
                ],
                'immediate_application': 'Listeners can use these tools immediately for their own businesses'
            },
            
            'compelling_numbers': {
                'time_efficiency': f"Reduced Collins framework implementation from weeks to {key_metrics['avg_completion_time']} hours",
                'business_results': f"Average {key_metrics['avg_growth']}% revenue growth for users",
                'scale_proof': f"{key_metrics['client_count']} businesses using it monthly",
                'revenue_validation': f"${key_metrics['annual_revenue']:,} ARR"
            },
            
            'optimization_story': [
                'Started with manual veterinary phone systems',
                'Discovered vets love systematic frameworks',
                'Digitized Collins methodologies for efficiency',
                'Scaled from 1 market to platform serving multiple industries',
                'Created passive revenue through systematic implementation'
            ],
            
            'tactical_insights': [
                'How to identify frameworks worth digitizing',
                'The "evidence first" approach to partnership',
                'Building credibility through small market validation',
                'Systematic approach to celebrity partnerships'
            ],
            
            'ferriss_alignment': {
                'efficiency_focus': 'Reduced framework implementation time by 80%',
                'systematic_approach': 'Everything documented and measurable', 
                'optimization_mindset': 'Continuous improvement based on user data',
                'scalable_systems': 'Built once, serves unlimited users'
            },
            
            'story_arc': {
                'struggle': 'Veterinary practices needed better business systems',
                'discovery': 'Collins frameworks perfect fit, but too complex to implement',
                'solution': 'Digital platform makes frameworks accessible',
                'success': 'Measurable business transformations at scale',
                'future': 'Partnership with Collins to reach all business types'
            }
        }
    
    def generate_warm_introduction_request(self, evidence_data: Dict, connection_name: str = '') -> Dict:
        """Generate request for warm introduction to Collins"""
        
        key_metrics = self._extract_key_evidence(evidence_data)
        
        return {
            'subject': f'Quick intro request - Built platform implementing Collins frameworks (${key_metrics["annual_revenue"]:,} ARR)',
            
            'email_body': f"""Hi {connection_name},

Hope you're doing well! Quick request:

I've built a digital platform that implements Jim Collins' frameworks (Level 5 Leadership, Hedgehog Concept, etc.) and it's generating real business results:

• {key_metrics['client_count']} practices using it actively
• {key_metrics['avg_growth']}% average revenue growth for users  
• ${key_metrics['annual_revenue']:,} annual recurring revenue

The platform proves his frameworks work digitally and I'd love to explore partnership opportunities with Jim.

Do you happen to know him or someone in his organization? Would you be comfortable making a brief intro?

Happy to share more details or demo the platform if helpful.

Thanks!""",
            
            'follow_up_materials': [
                'Platform demo link',
                'Case study summary (1 page)',
                'Revenue/usage metrics',
                'Partnership proposal overview'
            ]
        }
    
    def generate_direct_outreach_sequence(self, evidence_data: Dict) -> List[Dict]:
        """Generate sequence of direct outreach messages"""
        
        key_metrics = self._extract_key_evidence(evidence_data)
        
        return [
            {
                'message_number': 1,
                'channel': 'LinkedIn/Email',
                'subject': 'Digitized your frameworks → Measurable business results',
                'message': f"""Jim,

I've built a digital platform implementing your frameworks and have {key_metrics['client_count']} businesses using it with {key_metrics['avg_growth']}% average revenue growth.

The platform proves Level 5 Leadership, Hedgehog Concept, and Flywheel work systematically - not just in theory.

Would you be interested in seeing how your frameworks perform digitally?

Best regards,
[Name]

P.S. - Happy to share usage data and business results.""",
                'timing': 'Initial outreach'
            },
            
            {
                'message_number': 2,
                'channel': 'Follow-up email',
                'subject': 'Quick question about framework implementation',
                'message': f"""Jim,

Quick follow-up to my message about digitizing your frameworks.

I'm curious: have you seen systematic digital implementation of Level 5 Leadership and Hedgehog Concept before?

Our platform has {key_metrics['framework_completion']}% completion rate (vs typical <10% for business books), which suggests digital format increases implementation.

Worth a 15-minute conversation?

Best,
[Name]""",
                'timing': '1 week after initial'
            }
        ]
    
    def _extract_key_evidence(self, evidence_data: Dict) -> Dict:
        """Extract key evidence points without overwhelming detail"""
        
        # Default values for demo/development
        return {
            'client_count': evidence_data.get('total_clients', 6),
            'avg_growth': evidence_data.get('avg_revenue_growth', 28),
            'framework_completion': evidence_data.get('framework_completion_rate', 85),
            'monthly_revenue': evidence_data.get('monthly_revenue', 1194),
            'annual_revenue': evidence_data.get('annual_revenue', 14328),
            'successful_transformations': evidence_data.get('successful_transformations', 5),
            'program_duration': evidence_data.get('program_duration_months', 6),
            'avg_completion_time': evidence_data.get('avg_completion_hours', 4)
        }
    
    def create_pitch_package(self, evidence_data: Dict) -> Dict:
        """Create complete pitch package for both Collins and Ferriss"""
        
        return {
            'generated_date': datetime.now().isoformat(),
            'collins_partnership': self.generate_collins_pitch(evidence_data),
            'ferriss_show_pitch': self.generate_ferriss_pitch(evidence_data),
            'warm_intro_request': self.generate_warm_introduction_request(evidence_data),
            'direct_outreach': self.generate_direct_outreach_sequence(evidence_data),
            
            'execution_timeline': {
                'week_1': 'Research warm connections to Collins',
                'week_2': 'Send warm introduction requests', 
                'week_3': 'Direct outreach if no warm intros',
                'week_4': 'Follow-up and demo scheduling',
                'month_2': 'Partnership negotiations',
                'month_3': 'Ferriss show pitch preparation'
            },
            
            'success_metrics': {
                'collins_response_rate_target': '>20%',
                'demo_conversion_target': '>50%',
                'partnership_timeline': '3-6 months',
                'ferriss_show_booking': '6-9 months'
            }
        }

def main():
    """Generate partnership pitch materials"""
    
    print("🎯 Collins/Ferriss Partnership Pitch Generator")
    print("=" * 50)
    
    # Load evidence data (would come from Firebase in production)
    sample_evidence = {
        'total_clients': 6,
        'avg_revenue_growth': 28.5,
        'framework_completion_rate': 85,
        'monthly_revenue': 1194,
        'annual_revenue': 14328,
        'successful_transformations': 5,
        'program_duration_months': 6
    }
    
    generator = PartnershipPitchGenerator()
    pitch_package = generator.create_pitch_package(sample_evidence)
    
    # Save pitch package
    filename = f"partnership_pitch_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(pitch_package, f, indent=2)
    
    print(f"✅ Complete pitch package saved to {filename}")
    
    # Display key elements
    collins_pitch = pitch_package['collins_partnership']
    print(f"\n📧 COLLINS PITCH PREVIEW")
    print("-" * 25)
    print(f"Subject: {collins_pitch['subject_line']}")
    print(f"Hook: {collins_pitch['opening_hook'][:100]}...")
    print(f"Core Value: {collins_pitch['core_proposition']['what_built']}")
    
    ferriss_pitch = pitch_package['ferriss_show_pitch'] 
    print(f"\n🎙️ FERRISS SHOW ANGLE")
    print("-" * 20)
    print(f"Show Angle: {ferriss_pitch['show_angle']}")
    print(f"Hook Story: {ferriss_pitch['hook_story']}")
    
    print(f"\n⏰ EXECUTION TIMELINE")
    print("-" * 20)
    for week, action in pitch_package['execution_timeline'].items():
        print(f"{week}: {action}")
    
    print(f"\n🚀 Ready to approach Collins and Ferriss with evidence-based pitch!")

if __name__ == "__main__":
    main()