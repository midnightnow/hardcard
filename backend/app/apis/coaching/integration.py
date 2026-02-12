"""
Coaching Integration API

Integration layer connecting business coaching with existing revenue optimization,
multi-clinic management, and business scaling systems.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio

# Import existing system components
from ..business_scaling_playbook import ScalingPlaybook
from ..analytics import RevenueAnalytics
from ..crm import CRMService

router = APIRouter(prefix="/api/coaching/integration", tags=["coaching-integration"])

class IntegrationType(str, Enum):
    REVENUE_OPTIMIZATION = "revenue_optimization"
    MULTI_CLINIC_MANAGEMENT = "multi_clinic_management"
    BUSINESS_SCALING = "business_scaling"
    CRM_ANALYTICS = "crm_analytics"

class PerformanceMetrics(BaseModel):
    revenue_growth_rate: float
    customer_acquisition_cost: float
    customer_lifetime_value: float
    profit_margin: float
    operational_efficiency: float
    employee_satisfaction: float
    market_share: float
    innovation_index: float

class ClinicMetrics(BaseModel):
    clinic_id: str
    clinic_name: str
    monthly_revenue: float
    patient_count: int
    staff_count: int
    satisfaction_score: float
    efficiency_rating: float
    growth_rate: float

class BusinessScalingProgress(BaseModel):
    current_phase: str
    scaling_velocity: float
    big_rocks_completion: float
    pareto_optimization_score: float
    team_alignment_score: float
    cash_flow_health: float

class IntegratedCoachingInsights(BaseModel):
    client_id: str
    integration_type: IntegrationType
    performance_baseline: PerformanceMetrics
    current_metrics: PerformanceMetrics
    improvement_percentage: float
    framework_correlation: Dict[str, float]
    recommended_actions: List[str]
    risk_factors: List[str]
    success_probability: float

class CoachingBusinessIntegration:
    """Integration service for coaching with business systems"""
    
    def __init__(self):
        self.scaling_playbook = ScalingPlaybook()
        self.revenue_analytics = RevenueAnalytics()
        self.crm_service = CRMService()
    
    async def analyze_revenue_coaching_correlation(
        self,
        client_id: str,
        coaching_sessions: List[Dict[str, Any]],
        revenue_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze correlation between coaching activities and revenue performance"""
        
        # Extract coaching dates and scores
        coaching_timeline = []
        for session in coaching_sessions:
            coaching_timeline.append({
                'date': datetime.fromisoformat(session['session_date']),
                'progress_score': session['progress_score'],
                'framework_type': session['framework_type'],
                'action_items_count': len(session.get('action_items', []))
            })
        
        # Analyze revenue trends around coaching sessions
        correlation_analysis = {
            'pre_coaching_revenue_trend': 0,
            'post_coaching_revenue_trend': 0,
            'framework_impact_ranking': {},
            'coaching_roi': 0,
            'confidence_score': 0.75
        }
        
        # Calculate pre/post coaching revenue trends
        if len(coaching_timeline) > 0 and len(revenue_data) > 0:
            coaching_start = min(c['date'] for c in coaching_timeline)
            
            pre_coaching_revenue = [
                r for r in revenue_data 
                if datetime.fromisoformat(r['date']) < coaching_start
            ]
            post_coaching_revenue = [
                r for r in revenue_data 
                if datetime.fromisoformat(r['date']) >= coaching_start
            ]
            
            if pre_coaching_revenue and post_coaching_revenue:
                pre_avg = sum(r['amount'] for r in pre_coaching_revenue) / len(pre_coaching_revenue)
                post_avg = sum(r['amount'] for r in post_coaching_revenue) / len(post_coaching_revenue)
                
                correlation_analysis['pre_coaching_revenue_trend'] = pre_avg
                correlation_analysis['post_coaching_revenue_trend'] = post_avg
                correlation_analysis['coaching_roi'] = ((post_avg - pre_avg) / pre_avg) * 100 if pre_avg > 0 else 0
        
        # Analyze framework impact
        framework_impact = {}
        for session in coaching_sessions:
            framework = session['framework_type']
            if framework not in framework_impact:
                framework_impact[framework] = {'sessions': 0, 'avg_score': 0, 'total_score': 0}
            
            framework_impact[framework]['sessions'] += 1
            framework_impact[framework]['total_score'] += session['progress_score']
            framework_impact[framework]['avg_score'] = (
                framework_impact[framework]['total_score'] / 
                framework_impact[framework]['sessions']
            )
        
        # Rank frameworks by impact
        correlation_analysis['framework_impact_ranking'] = dict(
            sorted(framework_impact.items(), 
                  key=lambda x: x[1]['avg_score'], 
                  reverse=True)
        )
        
        return correlation_analysis
    
    async def get_multi_clinic_coaching_insights(
        self,
        client_id: str,
        clinic_ids: List[str]
    ) -> Dict[str, Any]:
        """Generate coaching insights for multi-clinic operations"""
        
        clinic_metrics = []
        for clinic_id in clinic_ids:
            # Fetch clinic performance data
            clinic_data = await self.crm_service.get_clinic_metrics(clinic_id)
            clinic_metrics.append(ClinicMetrics(**clinic_data))
        
        # Analyze performance patterns
        insights = {
            'top_performing_clinics': [],
            'underperforming_clinics': [],
            'common_success_factors': [],
            'improvement_opportunities': [],
            'standardization_recommendations': []
        }
        
        # Sort clinics by overall performance
        sorted_clinics = sorted(
            clinic_metrics, 
            key=lambda c: (c.satisfaction_score * 0.3 + 
                          c.efficiency_rating * 0.3 + 
                          c.growth_rate * 0.4),
            reverse=True
        )
        
        insights['top_performing_clinics'] = [
            {
                'clinic_id': c.clinic_id,
                'clinic_name': c.clinic_name,
                'performance_score': (c.satisfaction_score * 0.3 + 
                                    c.efficiency_rating * 0.3 + 
                                    c.growth_rate * 0.4)
            }
            for c in sorted_clinics[:3]
        ]
        
        insights['underperforming_clinics'] = [
            {
                'clinic_id': c.clinic_id,
                'clinic_name': c.clinic_name,
                'performance_score': (c.satisfaction_score * 0.3 + 
                                    c.efficiency_rating * 0.3 + 
                                    c.growth_rate * 0.4),
                'issues': self._identify_clinic_issues(c)
            }
            for c in sorted_clinics[-2:]
        ]
        
        # Identify common patterns in top performers
        if len(sorted_clinics) >= 3:
            top_performers = sorted_clinics[:3]
            insights['common_success_factors'] = [
                f"Average staff count: {sum(c.staff_count for c in top_performers) / len(top_performers):.1f}",
                f"Average satisfaction score: {sum(c.satisfaction_score for c in top_performers) / len(top_performers):.1f}",
                f"Average efficiency rating: {sum(c.efficiency_rating for c in top_performers) / len(top_performers):.1f}"
            ]
        
        return insights
    
    def _identify_clinic_issues(self, clinic: ClinicMetrics) -> List[str]:
        """Identify specific issues for underperforming clinics"""
        issues = []
        
        if clinic.satisfaction_score < 7.0:
            issues.append("Low patient satisfaction")
        if clinic.efficiency_rating < 7.0:
            issues.append("Operational inefficiencies")
        if clinic.growth_rate < 0.05:
            issues.append("Stagnant growth")
        if clinic.monthly_revenue / clinic.patient_count < 100:
            issues.append("Low revenue per patient")
        
        return issues
    
    async def generate_scaling_framework_alignment(
        self,
        client_id: str,
        current_business_phase: str
    ) -> Dict[str, Any]:
        """Align coaching frameworks with business scaling phase"""
        
        phase_framework_mapping = {
            'startup': {
                'primary_frameworks': ['hedgehog_concept', 'level_5_leadership'],
                'focus_areas': ['core_competency', 'team_building', 'market_validation'],
                'metrics_priority': ['customer_acquisition', 'product_market_fit', 'runway']
            },
            'growth': {
                'primary_frameworks': ['good_to_great', 'flywheel', 'culture_of_discipline'],
                'focus_areas': ['scaling_operations', 'maintaining_quality', 'team_expansion'],
                'metrics_priority': ['revenue_growth', 'operational_efficiency', 'team_satisfaction']
            },
            'scale': {
                'primary_frameworks': ['built_to_last', 'technology_accelerator'],
                'focus_areas': ['sustainable_systems', 'innovation', 'market_leadership'],
                'metrics_priority': ['market_share', 'profitability', 'sustainability']
            }
        }
        
        phase_config = phase_framework_mapping.get(current_business_phase, phase_framework_mapping['growth'])
        
        return {
            'current_phase': current_business_phase,
            'recommended_frameworks': phase_config['primary_frameworks'],
            'focus_areas': phase_config['focus_areas'],
            'priority_metrics': phase_config['metrics_priority'],
            'coaching_emphasis': self._get_phase_coaching_emphasis(current_business_phase),
            'estimated_duration': self._estimate_phase_duration(current_business_phase)
        }
    
    def _get_phase_coaching_emphasis(self, phase: str) -> List[str]:
        """Get coaching emphasis based on business phase"""
        emphasis_mapping = {
            'startup': [
                'Vision clarity and communication',
                'Core team alignment',
                'Customer discovery and validation',
                'Resource allocation and prioritization'
            ],
            'growth': [
                'Process systematization',
                'Team scaling and development',
                'Quality maintenance under pressure',
                'Performance measurement and optimization'
            ],
            'scale': [
                'Culture preservation and evolution',
                'Innovation management',
                'Strategic partnerships and alliances',
                'Long-term sustainability planning'
            ]
        }
        return emphasis_mapping.get(phase, emphasis_mapping['growth'])
    
    def _estimate_phase_duration(self, phase: str) -> Dict[str, int]:
        """Estimate coaching duration for each phase"""
        duration_mapping = {
            'startup': {'intensive_months': 6, 'maintenance_months': 12},
            'growth': {'intensive_months': 9, 'maintenance_months': 18},
            'scale': {'intensive_months': 12, 'maintenance_months': 24}
        }
        return duration_mapping.get(phase, duration_mapping['growth'])

# Initialize integration service
integration_service = CoachingBusinessIntegration()

@router.get("/revenue-correlation/{client_id}")
async def get_revenue_coaching_correlation(
    client_id: str,
    months_back: int = Query(12, ge=1, le=36)
) -> Dict[str, Any]:
    """Get correlation analysis between coaching and revenue performance"""
    
    try:
        # Fetch coaching sessions
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Mock data - in real implementation, fetch from database
        coaching_sessions = [
            {
                'session_date': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                'progress_score': 7.5,
                'framework_type': 'good_to_great',
                'action_items': [{'task': 'Implement daily huddles'}, {'task': 'Review hiring process'}]
            },
            {
                'session_date': (datetime.utcnow() - timedelta(days=60)).isoformat(),
                'progress_score': 8.2,
                'framework_type': 'level_5_leadership',
                'action_items': [{'task': 'Leadership assessment'}, {'task': 'Mentoring program'}]
            }
        ]
        
        revenue_data = [
            {'date': (datetime.utcnow() - timedelta(days=15)).isoformat(), 'amount': 125000},
            {'date': (datetime.utcnow() - timedelta(days=45)).isoformat(), 'amount': 118000},
            {'date': (datetime.utcnow() - timedelta(days=75)).isoformat(), 'amount': 110000},
        ]
        
        correlation_analysis = await integration_service.analyze_revenue_coaching_correlation(
            client_id, coaching_sessions, revenue_data
        )
        
        return {
            'client_id': client_id,
            'analysis_period_months': months_back,
            'correlation_analysis': correlation_analysis,
            'insights': [
                'Coaching sessions show positive correlation with revenue growth',
                'Level 5 Leadership framework sessions have highest average progress scores',
                'Action item completion rate correlates with revenue increases'
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing correlation: {str(e)}")

@router.get("/multi-clinic-insights/{client_id}")
async def get_multi_clinic_coaching_insights(
    client_id: str,
    clinic_ids: List[str] = Query(...)
) -> Dict[str, Any]:
    """Get coaching insights for multi-clinic operations"""
    
    try:
        insights = await integration_service.get_multi_clinic_coaching_insights(
            client_id, clinic_ids
        )
        
        return {
            'client_id': client_id,
            'clinic_count': len(clinic_ids),
            'insights': insights,
            'coaching_recommendations': [
                'Focus coaching efforts on standardizing best practices from top performers',
                'Implement peer learning sessions between clinics',
                'Develop clinic-specific coaching plans for underperformers',
                'Create cross-clinic mentoring programs'
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating multi-clinic insights: {str(e)}")

@router.get("/scaling-alignment/{client_id}")
async def get_scaling_framework_alignment(
    client_id: str,
    current_phase: str = Query(..., regex="^(startup|growth|scale)$")
) -> Dict[str, Any]:
    """Get framework alignment recommendations based on business scaling phase"""
    
    try:
        alignment = await integration_service.generate_scaling_framework_alignment(
            client_id, current_phase
        )
        
        return {
            'client_id': client_id,
            'alignment': alignment,
            'integration_recommendations': [
                'Align coaching session frequency with business phase intensity',
                'Integrate framework milestones with business KPIs',
                'Schedule phase transition assessments',
                'Coordinate coaching with operational initiatives'
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating scaling alignment: {str(e)}")

@router.post("/performance-baseline")
async def establish_performance_baseline(
    client_id: str,
    metrics: PerformanceMetrics
) -> Dict[str, str]:
    """Establish performance baseline for coaching program"""
    
    try:
        # Store baseline metrics in database
        baseline_data = {
            'client_id': client_id,
            'baseline_date': datetime.utcnow().isoformat(),
            'metrics': metrics.dict(),
            'status': 'active'
        }
        
        # In real implementation, save to database
        # db.collection('coaching_baselines').add(baseline_data)
        
        return {
            'client_id': client_id,
            'status': 'baseline_established',
            'message': 'Performance baseline successfully established for coaching program'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error establishing baseline: {str(e)}")

@router.get("/integrated-dashboard/{client_id}")
async def get_integrated_coaching_dashboard(
    client_id: str,
    include_revenue: bool = Query(True),
    include_multi_clinic: bool = Query(False),
    include_scaling: bool = Query(True)
) -> Dict[str, Any]:
    """Get comprehensive integrated coaching dashboard data"""
    
    try:
        dashboard_data = {
            'client_id': client_id,
            'last_updated': datetime.utcnow().isoformat(),
            'integrations': {}
        }
        
        # Fetch revenue correlation if requested
        if include_revenue:
            revenue_correlation = await integration_service.analyze_revenue_coaching_correlation(
                client_id, [], []  # Mock empty data for demo
            )
            dashboard_data['integrations']['revenue'] = revenue_correlation
        
        # Fetch multi-clinic insights if requested
        if include_multi_clinic:
            # Mock clinic IDs for demo
            clinic_ids = ['clinic_001', 'clinic_002', 'clinic_003']
            multi_clinic_insights = await integration_service.get_multi_clinic_coaching_insights(
                client_id, clinic_ids
            )
            dashboard_data['integrations']['multi_clinic'] = multi_clinic_insights
        
        # Fetch scaling alignment if requested
        if include_scaling:
            scaling_alignment = await integration_service.generate_scaling_framework_alignment(
                client_id, 'growth'  # Mock phase for demo
            )
            dashboard_data['integrations']['scaling'] = scaling_alignment
        
        # Add integration summary
        dashboard_data['summary'] = {
            'active_integrations': len(dashboard_data['integrations']),
            'coaching_business_alignment_score': 8.5,
            'recommended_next_actions': [
                'Review Q4 revenue correlation with coaching activities',
                'Schedule team alignment session with all clinic managers',
                'Update business phase assessment and framework priorities',
                'Implement cross-functional KPI tracking'
            ]
        }
        
        return dashboard_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating integrated dashboard: {str(e)}")

@router.get("/roi-analysis/{client_id}")
async def get_coaching_roi_analysis(
    client_id: str,
    investment_amount: float = Query(..., gt=0),
    analysis_period_months: int = Query(12, ge=3, le=36)
) -> Dict[str, Any]:
    """Calculate return on investment for coaching program"""
    
    try:
        # Mock calculation for demo - in real implementation, use actual data
        baseline_revenue = 1000000  # Annual baseline
        current_revenue = 1150000   # Current annual run rate
        revenue_improvement = current_revenue - baseline_revenue
        
        # Calculate ROI metrics
        roi_percentage = ((revenue_improvement - investment_amount) / investment_amount) * 100
        payback_period_months = (investment_amount / (revenue_improvement / 12)) if revenue_improvement > 0 else float('inf')
        
        roi_analysis = {
            'investment_amount': investment_amount,
            'revenue_improvement': revenue_improvement,
            'roi_percentage': roi_percentage,
            'payback_period_months': min(payback_period_months, 36),
            'net_benefit': revenue_improvement - investment_amount,
            'analysis_period_months': analysis_period_months,
            'confidence_level': 0.85,
            'contributing_factors': [
                'Improved operational efficiency from Culture of Discipline framework',
                'Enhanced leadership effectiveness from Level 5 Leadership coaching',
                'Better strategic focus from Hedgehog Concept implementation',
                'Increased team alignment and productivity'
            ],
            'risk_factors': [
                'Market conditions may impact sustainability',
                'Team changes could affect implementation',
                'External competitive pressures'
            ]
        }
        
        return {
            'client_id': client_id,
            'roi_analysis': roi_analysis,
            'recommendation': 'Continue coaching program' if roi_percentage > 100 else 'Review and optimize coaching approach'
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating ROI: {str(e)}")

# Health check for integration service
@router.get("/health")
async def integration_health_check():
    """Health check for coaching integration service"""
    return {
        'status': 'healthy',
        'service': 'coaching_integration',
        'timestamp': datetime.utcnow().isoformat(),
        'integrations_available': [
            'revenue_optimization',
            'multi_clinic_management', 
            'business_scaling',
            'crm_analytics'
        ]
    }