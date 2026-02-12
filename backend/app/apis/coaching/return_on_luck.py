"""
Return on Luck (ROL) Analyzer - Jim Collins Framework

Helps businesses track luck events and measure their effectiveness in capitalizing on them.
Based on the principle that great companies don't have more luck, they get a better return on luck.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query
import statistics

router = APIRouter(prefix="/return-on-luck", tags=["coaching", "rol"])

class LuckType(str, Enum):
    """Types of luck events"""
    GOOD = "good"
    BAD = "bad"
    NEUTRAL = "neutral"

class LuckMagnitude(str, Enum):
    """Magnitude of luck events"""
    MINOR = "minor"         # Small impact
    MODERATE = "moderate"   # Noticeable impact
    MAJOR = "major"        # Significant impact
    EXTREME = "extreme"    # Game-changing impact

class ResponseQuality(str, Enum):
    """Quality of response to luck event"""
    POOR = "poor"           # Missed opportunity or made worse
    ADEQUATE = "adequate"   # Standard response
    GOOD = "good"          # Capitalized well
    EXCELLENT = "excellent" # Maximized opportunity

class LuckEvent(BaseModel):
    """A luck event and the company's response"""
    id: str
    organization_id: str
    event_date: datetime
    event_type: LuckType
    magnitude: LuckMagnitude
    
    # Event details
    title: str
    description: str
    external_factors: List[str] = Field(default_factory=list)
    was_predictable: bool = False
    
    # Response details
    response_quality: ResponseQuality
    response_timeline_days: int
    actions_taken: List[str] = Field(default_factory=list)
    resources_deployed: Optional[float] = None
    
    # Outcomes
    expected_impact: float  # What could have happened (positive or negative)
    actual_impact: float    # What actually happened
    impact_duration_months: Optional[int] = None
    
    # Learning
    lessons_learned: List[str] = Field(default_factory=list)
    process_improvements: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    tags: List[str] = Field(default_factory=list)

class ROLMetrics(BaseModel):
    """Return on Luck metrics and analysis"""
    total_events: int
    good_luck_events: int
    bad_luck_events: int
    
    # ROL scores (actual impact / expected impact)
    average_rol: float
    good_luck_rol: float
    bad_luck_rol: float
    
    # Response quality distribution
    response_distribution: Dict[ResponseQuality, int]
    
    # Financial impact
    total_positive_impact: float
    total_negative_impact: float
    net_impact: float
    
    # Opportunity analysis
    missed_opportunity_value: float
    maximized_opportunity_value: float
    improvement_potential: float
    
    # Time analysis
    average_response_time_days: float
    fastest_response_days: int
    slowest_response_days: int

class ROLAnalysis(BaseModel):
    """Comprehensive ROL analysis with insights"""
    metrics: ROLMetrics
    
    # Patterns
    luck_frequency: Dict[str, float]  # Events per month by type
    seasonal_patterns: Optional[Dict[str, float]] = None
    category_performance: Dict[str, float]  # ROL by category/tag
    
    # Comparisons
    rol_trend: List[Dict[str, Any]]  # ROL over time
    benchmark_comparison: Optional[Dict[str, float]] = None
    
    # Insights
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    recommendations: List[str]

class LuckEventCreate(BaseModel):
    """Create a new luck event"""
    organization_id: str
    event_date: datetime
    event_type: LuckType
    magnitude: LuckMagnitude
    title: str
    description: str
    external_factors: List[str] = Field(default_factory=list)
    was_predictable: bool = False
    response_quality: ResponseQuality
    response_timeline_days: int
    actions_taken: List[str] = Field(default_factory=list)
    resources_deployed: Optional[float] = None
    expected_impact: float
    actual_impact: float
    impact_duration_months: Optional[int] = None
    lessons_learned: List[str] = Field(default_factory=list)
    process_improvements: List[str] = Field(default_factory=list)
    created_by: str
    tags: List[str] = Field(default_factory=list)

# In-memory storage (replace with database in production)
luck_events_db: Dict[str, LuckEvent] = {}

def calculate_rol(event: LuckEvent) -> float:
    """Calculate Return on Luck for an event"""
    if event.expected_impact == 0:
        return 0
    
    # For bad luck, a less negative outcome is better ROL
    if event.event_type == LuckType.BAD:
        # If expected -100 and actual -50, ROL = 2.0 (halved the damage)
        if event.expected_impact < 0 and event.actual_impact < 0:
            return abs(event.expected_impact) / abs(event.actual_impact)
        # If expected -100 and actual +10, exceptional ROL
        elif event.expected_impact < 0 < event.actual_impact:
            return float('inf')  # Or cap at a high value like 10.0
    
    # For good luck, higher actual vs expected is better
    return event.actual_impact / event.expected_impact if event.expected_impact != 0 else 0

def analyze_rol_metrics(events: List[LuckEvent]) -> ROLMetrics:
    """Analyze ROL metrics from events"""
    if not events:
        return ROLMetrics(
            total_events=0,
            good_luck_events=0,
            bad_luck_events=0,
            average_rol=0,
            good_luck_rol=0,
            bad_luck_rol=0,
            response_distribution={},
            total_positive_impact=0,
            total_negative_impact=0,
            net_impact=0,
            missed_opportunity_value=0,
            maximized_opportunity_value=0,
            improvement_potential=0,
            average_response_time_days=0,
            fastest_response_days=0,
            slowest_response_days=0
        )
    
    good_events = [e for e in events if e.event_type == LuckType.GOOD]
    bad_events = [e for e in events if e.event_type == LuckType.BAD]
    
    # Calculate ROL scores
    all_rols = [calculate_rol(e) for e in events if calculate_rol(e) != float('inf')]
    good_rols = [calculate_rol(e) for e in good_events if calculate_rol(e) != float('inf')]
    bad_rols = [calculate_rol(e) for e in bad_events if calculate_rol(e) != float('inf')]
    
    # Response quality distribution
    response_dist = {}
    for quality in ResponseQuality:
        response_dist[quality] = len([e for e in events if e.response_quality == quality])
    
    # Financial impact
    positive_impact = sum(e.actual_impact for e in events if e.actual_impact > 0)
    negative_impact = sum(e.actual_impact for e in events if e.actual_impact < 0)
    
    # Opportunity analysis
    missed_value = sum(
        max(0, e.expected_impact - e.actual_impact) 
        for e in good_events
    )
    maximized_value = sum(
        max(0, e.actual_impact - e.expected_impact)
        for e in events
    )
    
    # Response times
    response_times = [e.response_timeline_days for e in events]
    
    return ROLMetrics(
        total_events=len(events),
        good_luck_events=len(good_events),
        bad_luck_events=len(bad_events),
        average_rol=statistics.mean(all_rols) if all_rols else 0,
        good_luck_rol=statistics.mean(good_rols) if good_rols else 0,
        bad_luck_rol=statistics.mean(bad_rols) if bad_rols else 0,
        response_distribution=response_dist,
        total_positive_impact=positive_impact,
        total_negative_impact=negative_impact,
        net_impact=positive_impact + negative_impact,
        missed_opportunity_value=missed_value,
        maximized_opportunity_value=maximized_value,
        improvement_potential=missed_value / (positive_impact + 1),  # Avoid division by zero
        average_response_time_days=statistics.mean(response_times) if response_times else 0,
        fastest_response_days=min(response_times) if response_times else 0,
        slowest_response_days=max(response_times) if response_times else 0
    )

def generate_rol_insights(events: List[LuckEvent], metrics: ROLMetrics) -> ROLAnalysis:
    """Generate comprehensive ROL analysis with insights"""
    
    # Calculate luck frequency
    if events:
        months_span = (max(e.event_date for e in events) - min(e.event_date for e in events)).days / 30
        luck_frequency = {
            "good": len([e for e in events if e.event_type == LuckType.GOOD]) / max(months_span, 1),
            "bad": len([e for e in events if e.event_type == LuckType.BAD]) / max(months_span, 1),
            "total": len(events) / max(months_span, 1)
        }
    else:
        luck_frequency = {"good": 0, "bad": 0, "total": 0}
    
    # Category performance
    category_performance = {}
    for tag in set(tag for event in events for tag in event.tags):
        tagged_events = [e for e in events if tag in e.tags]
        if tagged_events:
            rols = [calculate_rol(e) for e in tagged_events if calculate_rol(e) != float('inf')]
            category_performance[tag] = statistics.mean(rols) if rols else 0
    
    # ROL trend over time (last 12 months)
    rol_trend = []
    current_date = datetime.utcnow()
    for i in range(12):
        month_start = current_date - timedelta(days=30 * (i + 1))
        month_end = current_date - timedelta(days=30 * i)
        month_events = [
            e for e in events 
            if month_start <= e.event_date <= month_end
        ]
        if month_events:
            month_rols = [calculate_rol(e) for e in month_events if calculate_rol(e) != float('inf')]
            rol_trend.append({
                "month": month_start.strftime("%Y-%m"),
                "rol": statistics.mean(month_rols) if month_rols else 0,
                "events": len(month_events)
            })
    
    # Generate insights
    strengths = []
    weaknesses = []
    opportunities = []
    recommendations = []
    
    # Analyze strengths
    if metrics.average_rol > 1.5:
        strengths.append("Excellent overall return on luck (>1.5x)")
    if metrics.bad_luck_rol > 2.0:
        strengths.append("Superior bad luck mitigation (>2.0x damage reduction)")
    if metrics.average_response_time_days < 7:
        strengths.append("Fast response time to luck events (<7 days)")
    
    excellent_responses = metrics.response_distribution.get(ResponseQuality.EXCELLENT, 0)
    if excellent_responses > metrics.total_events * 0.3:
        strengths.append(f"High rate of excellent responses ({excellent_responses}/{metrics.total_events})")
    
    # Analyze weaknesses
    if metrics.average_rol < 1.0:
        weaknesses.append("Below-average return on luck (<1.0x)")
    if metrics.good_luck_rol < 1.2:
        weaknesses.append("Underperforming on good luck opportunities")
    if metrics.average_response_time_days > 30:
        weaknesses.append("Slow response time to luck events (>30 days)")
    
    poor_responses = metrics.response_distribution.get(ResponseQuality.POOR, 0)
    if poor_responses > metrics.total_events * 0.2:
        weaknesses.append(f"High rate of poor responses ({poor_responses}/{metrics.total_events})")
    
    # Identify opportunities
    if metrics.missed_opportunity_value > metrics.maximized_opportunity_value:
        opportunities.append(f"${metrics.missed_opportunity_value:,.0f} in missed opportunities to capture")
    if metrics.improvement_potential > 0.3:
        opportunities.append("30%+ improvement potential in luck capitalization")
    
    # Generate recommendations
    if metrics.average_response_time_days > 14:
        recommendations.append("Implement rapid response team for luck events")
    if metrics.good_luck_rol < metrics.bad_luck_rol:
        recommendations.append("Focus on maximizing good luck opportunities")
    if poor_responses > 0:
        recommendations.append("Review and improve response protocols for luck events")
    if not category_performance:
        recommendations.append("Implement categorization to track ROL by business area")
    
    recommendations.append("Conduct quarterly ROL reviews to identify patterns")
    recommendations.append("Create 'luck preparedness' protocols for common scenarios")
    
    return ROLAnalysis(
        metrics=metrics,
        luck_frequency=luck_frequency,
        category_performance=category_performance,
        rol_trend=rol_trend,
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        recommendations=recommendations
    )

@router.post("/events", response_model=LuckEvent)
async def create_luck_event(event: LuckEventCreate):
    """Record a new luck event"""
    event_id = f"luck_{datetime.utcnow().timestamp()}"
    luck_event = LuckEvent(id=event_id, **event.dict())
    luck_events_db[event_id] = luck_event
    return luck_event

@router.get("/events/{event_id}", response_model=LuckEvent)
async def get_luck_event(event_id: str):
    """Get a specific luck event"""
    if event_id not in luck_events_db:
        raise HTTPException(status_code=404, detail="Luck event not found")
    return luck_events_db[event_id]

@router.put("/events/{event_id}", response_model=LuckEvent)
async def update_luck_event(event_id: str, event: LuckEventCreate):
    """Update a luck event"""
    if event_id not in luck_events_db:
        raise HTTPException(status_code=404, detail="Luck event not found")
    
    luck_event = LuckEvent(id=event_id, **event.dict())
    luck_events_db[event_id] = luck_event
    return luck_event

@router.get("/events", response_model=List[LuckEvent])
async def list_luck_events(
    organization_id: str,
    event_type: Optional[LuckType] = None,
    magnitude: Optional[LuckMagnitude] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    tags: Optional[List[str]] = Query(None)
):
    """List luck events with filters"""
    events = [e for e in luck_events_db.values() if e.organization_id == organization_id]
    
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    if magnitude:
        events = [e for e in events if e.magnitude == magnitude]
    if start_date:
        events = [e for e in events if e.event_date >= start_date]
    if end_date:
        events = [e for e in events if e.event_date <= end_date]
    if tags:
        events = [e for e in events if any(tag in e.tags for tag in tags)]
    
    return sorted(events, key=lambda e: e.event_date, reverse=True)

@router.get("/analysis/{organization_id}", response_model=ROLAnalysis)
async def get_rol_analysis(
    organization_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get comprehensive ROL analysis for an organization"""
    events = await list_luck_events(
        organization_id=organization_id,
        start_date=start_date,
        end_date=end_date
    )
    
    metrics = analyze_rol_metrics(events)
    analysis = generate_rol_insights(events, metrics)
    
    return analysis

@router.get("/insights/{organization_id}/opportunities")
async def get_improvement_opportunities(organization_id: str):
    """Get specific improvement opportunities based on ROL analysis"""
    events = [e for e in luck_events_db.values() if e.organization_id == organization_id]
    
    opportunities = []
    
    # Find patterns in poor responses
    poor_responses = [e for e in events if e.response_quality == ResponseQuality.POOR]
    if poor_responses:
        common_factors = {}
        for event in poor_responses:
            for factor in event.external_factors:
                common_factors[factor] = common_factors.get(factor, 0) + 1
        
        top_factors = sorted(common_factors.items(), key=lambda x: x[1], reverse=True)[:3]
        opportunities.append({
            "title": "Common Factors in Poor Responses",
            "description": f"Address these recurring factors: {', '.join([f[0] for f in top_factors])}",
            "potential_impact": sum(e.expected_impact - e.actual_impact for e in poor_responses),
            "priority": "high"
        })
    
    # Find categories with low ROL
    analysis = await get_rol_analysis(organization_id)
    for category, rol in analysis.category_performance.items():
        if rol < 1.0:
            opportunities.append({
                "title": f"Improve {category} Response Protocols",
                "description": f"Current ROL of {rol:.2f} indicates significant improvement potential",
                "potential_impact": "medium",
                "priority": "medium"
            })
    
    # Response time improvements
    slow_responses = [e for e in events if e.response_timeline_days > 30]
    if slow_responses:
        opportunities.append({
            "title": "Accelerate Response Time",
            "description": f"{len(slow_responses)} events had response times >30 days",
            "potential_impact": sum(e.expected_impact * 0.2 for e in slow_responses),  # Estimate 20% better with faster response
            "priority": "high"
        })
    
    return {
        "opportunities": opportunities,
        "total_potential_value": sum(
            opp.get("potential_impact", 0) 
            for opp in opportunities 
            if isinstance(opp.get("potential_impact"), (int, float))
        )
    }

@router.post("/simulate")
async def simulate_rol_improvement(
    organization_id: str,
    improvement_scenarios: List[Dict[str, Any]]
):
    """Simulate the impact of improving ROL capabilities"""
    events = [e for e in luck_events_db.values() if e.organization_id == organization_id]
    current_metrics = analyze_rol_metrics(events)
    
    simulations = []
    
    for scenario in improvement_scenarios:
        # Apply improvements to events
        simulated_events = []
        for event in events:
            simulated_event = event.copy()
            
            # Improve response quality
            if scenario.get("improve_response_quality"):
                if event.response_quality == ResponseQuality.POOR:
                    simulated_event.response_quality = ResponseQuality.ADEQUATE
                    simulated_event.actual_impact *= 1.3
                elif event.response_quality == ResponseQuality.ADEQUATE:
                    simulated_event.response_quality = ResponseQuality.GOOD
                    simulated_event.actual_impact *= 1.2
            
            # Improve response time
            if scenario.get("faster_response_days"):
                time_improvement = event.response_timeline_days - scenario["faster_response_days"]
                if time_improvement > 0:
                    simulated_event.response_timeline_days = scenario["faster_response_days"]
                    # Estimate 10% better outcome for each week faster
                    simulated_event.actual_impact *= (1 + 0.1 * (time_improvement / 7))
            
            simulated_events.append(simulated_event)
        
        # Calculate new metrics
        new_metrics = analyze_rol_metrics(simulated_events)
        
        simulations.append({
            "scenario": scenario,
            "current_rol": current_metrics.average_rol,
            "projected_rol": new_metrics.average_rol,
            "roi_improvement": (new_metrics.average_rol - current_metrics.average_rol) / current_metrics.average_rol,
            "financial_impact": new_metrics.net_impact - current_metrics.net_impact
        })
    
    return {
        "current_state": current_metrics,
        "simulations": simulations
    }

if __name__ == "__main__":
    # Example usage
    example_event = LuckEventCreate(
        organization_id="org_123",
        event_date=datetime.utcnow() - timedelta(days=30),
        event_type=LuckType.GOOD,
        magnitude=LuckMagnitude.MAJOR,
        title="Major competitor unexpectedly exited market",
        description="Our biggest competitor shut down operations due to financial issues",
        external_factors=["Economic downturn", "Poor management"],
        was_predictable=False,
        response_quality=ResponseQuality.GOOD,
        response_timeline_days=14,
        actions_taken=[
            "Launched customer acquisition campaign",
            "Hired key talent from competitor",
            "Expanded into their primary markets"
        ],
        resources_deployed=500000,
        expected_impact=2000000,  # Could have gained $2M in new business
        actual_impact=1500000,    # Actually gained $1.5M
        impact_duration_months=24,
        lessons_learned=[
            "Need faster market response protocols",
            "Should maintain competitive intelligence"
        ],
        process_improvements=[
            "Created rapid response team",
            "Implemented weekly competitor monitoring"
        ],
        created_by="ceo@company.com",
        tags=["market", "competition", "opportunity"]
    )