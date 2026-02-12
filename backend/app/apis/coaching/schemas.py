"""
Pydantic schemas for HardCard Business Coaching System
Comprehensive validation and serialization for Jim Collins frameworks
with VetSorcery integration and multi-tenant support
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import re

# Enums and Constants
class BusinessType(str, Enum):
    veterinary_clinic = "veterinary_clinic"
    veterinary_chain = "veterinary_chain"
    tech_startup = "tech_startup"
    professional_services = "professional_services"
    healthcare = "healthcare"
    retail = "retail"
    manufacturing = "manufacturing"
    other = "other"

class CoachingTier(str, Enum):
    basic = "basic"
    professional = "professional"
    enterprise = "enterprise"
    vip = "vip"

class ExperimentType(str, Enum):
    bullet = "bullet"
    cannonball = "cannonball"

class ExperimentStatus(str, Enum):
    planning = "planning"
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"

class LuckType(str, Enum):
    good_luck = "good_luck"
    bad_luck = "bad_luck"

class SessionType(str, Enum):
    onboarding = "onboarding"
    regular = "regular"
    crisis = "crisis"
    review = "review"

# Base schemas
class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ScoreValidationMixin(BaseModel):
    @validator('*')
    def validate_scores(cls, v, field):
        if field.name.endswith('_score') and v is not None:
            if not 1 <= v <= 10:
                raise ValueError(f'{field.name} must be between 1 and 10')
        return v

# Client Management Schemas
class CoachingClientBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    business_type: BusinessType
    industry: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1800, le=2030)
    employee_count: Optional[int] = Field(None, ge=1)
    annual_revenue: Optional[float] = Field(None, ge=0)
    
    primary_contact_name: str = Field(..., min_length=1, max_length=255)
    primary_contact_email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    address: Optional[str] = None
    
    coaching_tier: CoachingTier = CoachingTier.basic
    vetsorcery_clinic_ids: Optional[List[str]] = None
    vetsorcery_integration_active: bool = False
    revenue_optimization_enabled: bool = False

class CoachingClientCreate(CoachingClientBase):
    pass

class CoachingClientUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    business_type: Optional[BusinessType] = None
    industry: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, ge=1)
    annual_revenue: Optional[float] = Field(None, ge=0)
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    address: Optional[str] = None
    coaching_tier: Optional[CoachingTier] = None
    vetsorcery_clinic_ids: Optional[List[str]] = None
    vetsorcery_integration_active: Optional[bool] = None
    revenue_optimization_enabled: Optional[bool] = None

class CoachingClient(CoachingClientBase, TimestampMixin):
    id: str
    onboarding_completed: bool = False
    coaching_start_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    is_active: bool = True

    class Config:
        orm_mode = True

# Hedgehog Concept Schemas
class HedgehogConceptBase(BaseModel, ScoreValidationMixin):
    # Passion Circle
    passion_description: Optional[str] = None
    passion_keywords: Optional[List[str]] = Field(None, max_items=20)
    passion_score: Optional[int] = Field(None, ge=1, le=10)
    passion_evidence: Optional[List[str]] = Field(None, max_items=10)
    
    # Genetic Encoding Circle
    genetic_encoding_description: Optional[str] = None
    core_competencies: Optional[List[str]] = Field(None, max_items=15)
    competitive_advantages: Optional[List[str]] = Field(None, max_items=10)
    genetic_encoding_score: Optional[int] = Field(None, ge=1, le=10)
    market_differentiation: Optional[str] = None
    
    # Economic Engine Circle
    economic_engine_description: Optional[str] = None
    revenue_model: Optional[str] = Field(None, max_length=100)
    key_metrics: Optional[List[str]] = Field(None, max_items=10)
    profit_per_x: Optional[str] = Field(None, max_length=100)
    economic_engine_score: Optional[int] = Field(None, ge=1, le=10)
    
    # Integration Analysis
    gaps_identified: Optional[List[str]] = Field(None, max_items=10)
    action_items: Optional[List[Dict[str, Any]]] = Field(None, max_items=20)
    
    # VetSorcery Integration
    vetsorcery_revenue_data: Optional[Dict[str, Any]] = None
    clinic_performance_metrics: Optional[Dict[str, Any]] = None

    @root_validator
    def validate_hedgehog_completeness(cls, values):
        passion_score = values.get('passion_score')
        genetic_score = values.get('genetic_encoding_score')
        economic_score = values.get('economic_engine_score')
        
        # If any score is provided, description should be provided too
        if passion_score and not values.get('passion_description'):
            raise ValueError('passion_description required when passion_score is provided')
        if genetic_score and not values.get('genetic_encoding_description'):
            raise ValueError('genetic_encoding_description required when genetic_encoding_score is provided')
        if economic_score and not values.get('economic_engine_description'):
            raise ValueError('economic_engine_description required when economic_engine_score is provided')
        
        return values

class HedgehogConceptCreate(HedgehogConceptBase):
    pass

class HedgehogConceptUpdate(BaseModel):
    passion_description: Optional[str] = None
    passion_keywords: Optional[List[str]] = None
    passion_score: Optional[int] = Field(None, ge=1, le=10)
    genetic_encoding_description: Optional[str] = None
    genetic_encoding_score: Optional[int] = Field(None, ge=1, le=10)
    economic_engine_description: Optional[str] = None
    economic_engine_score: Optional[int] = Field(None, ge=1, le=10)
    action_items: Optional[List[Dict[str, Any]]] = None

class HedgehogConcept(HedgehogConceptBase, TimestampMixin):
    id: str
    client_id: str
    hedgehog_alignment_score: Optional[int] = Field(None, ge=1, le=10)
    version: int = 1
    is_current: bool = True
    created_by: Optional[str] = None
    reviewed_date: Optional[datetime] = None
    next_review_date: Optional[datetime] = None

    class Config:
        orm_mode = True

# Flywheel Schemas
class FlywheelComponentSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    metrics: Optional[List[str]] = Field(None, max_items=5)
    current_performance: Optional[int] = Field(None, ge=1, le=10)

class FlywheelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    core_flywheel_components: List[FlywheelComponentSchema] = Field(..., min_items=3, max_items=12)
    component_metrics: Optional[Dict[str, Any]] = None
    current_momentum_score: Optional[int] = Field(None, ge=1, le=100)
    doom_loop_risks: Optional[List[str]] = Field(None, max_items=10)
    accelerator_opportunities: Optional[List[str]] = Field(None, max_items=10)
    measurement_frequency: Optional[str] = Field(None, regex=r'^(daily|weekly|monthly|quarterly)$')
    clinic_flywheel_performance: Optional[Dict[str, Any]] = None
    revenue_correlation: Optional[Dict[str, Any]] = None

    @validator('core_flywheel_components')
    def validate_flywheel_flow(cls, v):
        if len(v) < 3:
            raise ValueError('Flywheel must have at least 3 components')
        return v

class FlywheelCreate(FlywheelBase):
    pass

class FlywheelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    current_momentum_score: Optional[int] = Field(None, ge=1, le=100)
    doom_loop_risks: Optional[List[str]] = None
    accelerator_opportunities: Optional[List[str]] = None

class Flywheel(FlywheelBase, TimestampMixin):
    id: str
    client_id: str
    is_active: bool = True
    momentum_history: Optional[List[Dict[str, Any]]] = None
    breakthrough_moments: Optional[List[Dict[str, Any]]] = None

    class Config:
        orm_mode = True

# Flywheel Momentum Log Schemas
class FlywheelMomentumLogBase(BaseModel):
    momentum_score: int = Field(..., ge=1, le=100)
    component_scores: List[int] = Field(..., min_items=1)
    notes: Optional[str] = None
    key_actions_taken: Optional[List[str]] = Field(None, max_items=10)
    obstacles_encountered: Optional[List[str]] = Field(None, max_items=10)
    measurement_date: datetime
    measured_by: Optional[str] = Field(None, max_length=255)

    @validator('component_scores')
    def validate_component_scores(cls, v):
        for score in v:
            if not 1 <= score <= 10:
                raise ValueError('Component scores must be between 1 and 10')
        return v

class FlywheelMomentumLogCreate(FlywheelMomentumLogBase):
    pass

class FlywheelMomentumLog(FlywheelMomentumLogBase):
    id: str
    flywheel_id: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Level 5 Leadership Schemas
class Level5AssessmentBase(BaseModel, ScoreValidationMixin):
    leader_name: str = Field(..., min_length=1, max_length=255)
    leader_role: str = Field(..., min_length=1, max_length=100)
    assessment_date: datetime
    
    # Level scores
    level1_individual_contributor: Optional[int] = Field(None, ge=1, le=10)
    level2_contributing_team_member: Optional[int] = Field(None, ge=1, le=10)
    level3_competent_manager: Optional[int] = Field(None, ge=1, le=10)
    level4_effective_leader: Optional[int] = Field(None, ge=1, le=10)
    level5_executive: Optional[int] = Field(None, ge=1, le=10)
    
    personal_humility_score: Optional[int] = Field(None, ge=1, le=10)
    professional_will_score: Optional[int] = Field(None, ge=1, le=10)
    
    humility_indicators: Optional[List[str]] = Field(None, max_items=15)
    will_indicators: Optional[List[str]] = Field(None, max_items=15)
    strengths: Optional[List[str]] = Field(None, max_items=10)
    development_areas: Optional[List[str]] = Field(None, max_items=10)
    development_plan: Optional[List[Dict[str, Any]]] = Field(None, max_items=10)
    
    window_behaviors: Optional[List[str]] = Field(None, max_items=10)
    mirror_behaviors: Optional[List[str]] = Field(None, max_items=10)
    
    next_assessment_date: Optional[datetime] = None
    assessor: Optional[str] = Field(None, max_length=255)

    @root_validator
    def validate_level5_consistency(cls, values):
        humility = values.get('personal_humility_score')
        will = values.get('professional_will_score')
        level5 = values.get('level5_executive')
        
        # Level 5 requires balance of humility and will
        if level5 and level5 >= 8:
            if not humility or not will:
                raise ValueError('High Level 5 score requires both humility and will scores')
            if humility < 7 or will < 7:
                raise ValueError('Level 5 executives must have high humility AND will (7+)')
        
        return values

class Level5AssessmentCreate(Level5AssessmentBase):
    pass

class Level5AssessmentUpdate(BaseModel):
    level1_individual_contributor: Optional[int] = Field(None, ge=1, le=10)
    level2_contributing_team_member: Optional[int] = Field(None, ge=1, le=10)
    level3_competent_manager: Optional[int] = Field(None, ge=1, le=10)
    level4_effective_leader: Optional[int] = Field(None, ge=1, le=10)
    level5_executive: Optional[int] = Field(None, ge=1, le=10)
    personal_humility_score: Optional[int] = Field(None, ge=1, le=10)
    professional_will_score: Optional[int] = Field(None, ge=1, le=10)
    development_areas: Optional[List[str]] = None
    development_plan: Optional[List[Dict[str, Any]]] = None

class Level5Assessment(Level5AssessmentBase, TimestampMixin):
    id: str
    client_id: str
    overall_level5_score: Optional[float] = Field(None, ge=0, le=10)

    class Config:
        orm_mode = True

# Creative Hours Schemas
class CreativeHoursBase(BaseModel):
    session_date: datetime
    duration_minutes: int = Field(..., ge=15, le=480)  # 15 min to 8 hours
    location: Optional[str] = Field(None, max_length=255)
    environment_description: Optional[str] = None
    focus_area: Optional[str] = Field(None, max_length=255)
    thinking_mode: Optional[str] = Field(None, regex=r'^(structured|freeform|problem_solving|brainstorming)$')
    tools_used: Optional[List[str]] = Field(None, max_items=10)
    
    key_insights: Optional[List[str]] = Field(None, max_items=20)
    breakthrough_moments: Optional[List[str]] = Field(None, max_items=10)
    questions_generated: Optional[List[str]] = Field(None, max_items=15)
    connection_patterns: Optional[List[str]] = Field(None, max_items=10)
    
    immediate_actions: Optional[List[str]] = Field(None, max_items=10)
    research_needed: Optional[List[str]] = Field(None, max_items=10)
    experiments_to_try: Optional[List[str]] = Field(None, max_items=10)
    
    session_quality_score: Optional[int] = Field(None, ge=1, le=10)
    distractions_count: Optional[int] = Field(None, ge=0, le=50)
    follow_up_required: bool = False
    
    ideas_implemented: Optional[List[str]] = None
    business_impact: Optional[str] = None

class CreativeHoursCreate(CreativeHoursBase):
    pass

class CreativeHoursUpdate(BaseModel):
    session_quality_score: Optional[int] = Field(None, ge=1, le=10)
    ideas_implemented: Optional[List[str]] = None
    business_impact: Optional[str] = None
    follow_up_required: Optional[bool] = None

class CreativeHours(CreativeHoursBase, TimestampMixin):
    id: str
    client_id: str

    class Config:
        orm_mode = True

# Bullets/Cannonballs Schemas
class ExperimentMetricSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_value: Union[int, float, str]
    measurement_method: str = Field(..., min_length=1, max_length=200)
    current_value: Optional[Union[int, float, str]] = None

class BulletsCannonballsBase(BaseModel):
    experiment_type: ExperimentType
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=1000)
    hypothesis: str = Field(..., min_length=1, max_length=500)
    
    budget_allocated: Optional[float] = Field(None, ge=0)
    time_allocated_hours: Optional[int] = Field(None, ge=1)
    people_allocated: Optional[List[str]] = Field(None, max_items=20)
    
    success_metrics: List[ExperimentMetricSchema] = Field(..., min_items=1, max_items=10)
    minimum_viable_success: Optional[Dict[str, Any]] = None
    stretch_goals: Optional[Dict[str, Any]] = None
    
    start_date: datetime
    planned_end_date: datetime
    milestone_dates: Optional[List[Dict[str, Any]]] = Field(None, max_items=10)
    
    vetsorcery_clinics_involved: Optional[List[str]] = None

    @validator('planned_end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('planned_end_date must be after start_date')
        return v

    @root_validator
    def validate_experiment_constraints(cls, values):
        exp_type = values.get('experiment_type')
        budget = values.get('budget_allocated', 0)
        
        # Bullets should be low-cost, low-risk
        if exp_type == ExperimentType.bullet:
            if budget and budget > 50000:  # $50k limit for bullets
                raise ValueError('Bullet experiments should have budget under $50,000')
        
        # Cannonballs should have proven bullet success
        elif exp_type == ExperimentType.cannonball:
            if budget and budget < 10000:  # Minimum investment for cannonballs
                raise ValueError('Cannonball experiments typically require substantial investment ($10k+)')
        
        return values

class BulletsCannonballsCreate(BulletsCannonballsBase):
    pass

class BulletsCannonballsUpdate(BaseModel):
    status: Optional[ExperimentStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    current_results: Optional[Dict[str, Any]] = None
    lessons_learned: Optional[List[str]] = None
    pivot_decisions: Optional[List[str]] = None
    actual_end_date: Optional[datetime] = None
    calibration_accuracy: Optional[int] = Field(None, ge=1, le=10)
    calibration_notes: Optional[str] = None
    scale_to_cannonball: Optional[bool] = None
    cannonball_budget_estimate: Optional[float] = Field(None, ge=0)
    cannonball_timeline_estimate: Optional[int] = Field(None, ge=1)

class BulletsCannonballs(BulletsCannonballsBase, TimestampMixin):
    id: str
    client_id: str
    status: ExperimentStatus = ExperimentStatus.planning
    progress_percentage: int = 0
    current_results: Optional[Dict[str, Any]] = None
    actual_end_date: Optional[datetime] = None
    lessons_learned: Optional[List[str]] = None
    calibration_accuracy: Optional[int] = None
    scale_to_cannonball: bool = False
    revenue_impact_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

# Return on Luck Schemas
class ReturnOnLuckBase(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=255)
    event_date: datetime
    luck_type: LuckType
    luck_magnitude: int = Field(..., ge=1, le=10)
    
    event_description: str = Field(..., min_length=10, max_length=2000)
    external_factors: Optional[List[str]] = Field(None, max_items=10)
    initial_impact: Optional[str] = None
    
    response_description: str = Field(..., min_length=10, max_length=2000)
    response_speed: Optional[int] = Field(None, ge=1, le=10)
    response_quality: Optional[int] = Field(None, ge=1, le=10)
    resources_deployed: Optional[List[str]] = Field(None, max_items=15)
    
    return_multiplier: Optional[float] = Field(None, ge=0, le=50)  # 0-50x return
    quantitative_return: Optional[float] = Field(None, ge=0)
    qualitative_benefits: Optional[List[str]] = Field(None, max_items=10)
    
    preparation_level: Optional[int] = Field(None, ge=1, le=10)
    lessons_learned: Optional[List[str]] = Field(None, max_items=15)
    future_preparation_plans: Optional[List[str]] = Field(None, max_items=10)
    
    clinics_affected: Optional[List[str]] = None
    revenue_impact: Optional[float] = None
    operational_changes: Optional[List[str]] = Field(None, max_items=15)

    @root_validator
    def validate_return_consistency(cls, values):
        luck_type = values.get('luck_type')
        return_mult = values.get('return_multiplier')
        
        if luck_type == LuckType.bad_luck and return_mult and return_mult > 5:
            raise ValueError('Bad luck events rarely generate >5x return multiplier')
        
        return values

class ReturnOnLuckCreate(ReturnOnLuckBase):
    pass

class ReturnOnLuckUpdate(BaseModel):
    return_multiplier: Optional[float] = Field(None, ge=0, le=50)
    quantitative_return: Optional[float] = Field(None, ge=0)
    qualitative_benefits: Optional[List[str]] = None
    lessons_learned: Optional[List[str]] = None
    long_term_impact: Optional[str] = None
    follow_up_required: Optional[bool] = None

class ReturnOnLuck(ReturnOnLuckBase, TimestampMixin):
    id: str
    client_id: str
    similar_events_history: Optional[List[str]] = None
    pattern_insights: Optional[str] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    long_term_impact: Optional[str] = None

    class Config:
        orm_mode = True

# Coaching Session Schemas
class CoachingSessionBase(BaseModel):
    session_date: datetime
    duration_minutes: int = Field(..., ge=15, le=300)  # 15 min to 5 hours
    session_type: SessionType
    coach_name: str = Field(..., min_length=1, max_length=255)
    
    topics_covered: List[str] = Field(..., min_items=1, max_items=20)
    frameworks_reviewed: Optional[List[str]] = Field(None, max_items=10)
    key_insights: Optional[List[str]] = Field(None, max_items=15)
    
    action_items: Optional[List[Dict[str, Any]]] = Field(None, max_items=20)
    homework_assigned: Optional[List[str]] = Field(None, max_items=10)
    
    progress_since_last_session: Optional[List[str]] = Field(None, max_items=15)
    challenges_discussed: Optional[List[str]] = Field(None, max_items=10)
    breakthrough_moments: Optional[List[str]] = Field(None, max_items=10)
    
    vetsorcery_data_reviewed: bool = False
    clinic_performance_discussed: Optional[List[str]] = None
    revenue_optimization_topics: Optional[List[str]] = None
    
    client_satisfaction_score: Optional[int] = Field(None, ge=1, le=10)
    coach_assessment_score: Optional[int] = Field(None, ge=1, le=10)
    next_session_date: Optional[datetime] = None
    next_session_focus: Optional[List[str]] = Field(None, max_items=10)
    
    coach_notes: Optional[str] = None
    client_notes: Optional[str] = None
    recording_available: bool = False

class CoachingSessionCreate(CoachingSessionBase):
    pass

class CoachingSessionUpdate(BaseModel):
    client_satisfaction_score: Optional[int] = Field(None, ge=1, le=10)
    coach_assessment_score: Optional[int] = Field(None, ge=1, le=10)
    coach_notes: Optional[str] = None
    client_notes: Optional[str] = None
    next_session_date: Optional[datetime] = None
    next_session_focus: Optional[List[str]] = None

class CoachingSession(CoachingSessionBase, TimestampMixin):
    id: str
    client_id: str

    class Config:
        orm_mode = True

# Coaching Metrics Schemas
class CoachingMetricsBase(BaseModel):
    metric_date: datetime
    reporting_period: str = Field(..., regex=r'^(weekly|monthly|quarterly|annual)$')
    
    # Framework scores (normalized to 1-100)
    hedgehog_clarity_score: Optional[int] = Field(None, ge=0, le=100)
    flywheel_momentum_score: Optional[int] = Field(None, ge=0, le=100)
    level5_leadership_score: Optional[int] = Field(None, ge=0, le=100)
    creative_hours_effectiveness: Optional[int] = Field(None, ge=0, le=100)
    experiment_calibration_accuracy: Optional[int] = Field(None, ge=0, le=100)
    return_on_luck_score: Optional[int] = Field(None, ge=0, le=100)
    
    # Business impact metrics
    revenue_growth_percentage: Optional[float] = Field(None, ge=-100, le=1000)
    profit_margin_improvement: Optional[float] = Field(None, ge=-100, le=100)
    employee_engagement_score: Optional[int] = Field(None, ge=0, le=100)
    customer_satisfaction_score: Optional[int] = Field(None, ge=0, le=100)
    
    # VetSorcery metrics
    avg_revenue_per_clinic: Optional[float] = Field(None, ge=0)
    clinic_performance_variance: Optional[float] = Field(None, ge=0, le=100)
    phone_agent_adoption_rate: Optional[float] = Field(None, ge=0, le=100)
    client_retention_rate: Optional[float] = Field(None, ge=0, le=100)
    
    # Engagement metrics
    sessions_completed_period: Optional[int] = Field(None, ge=0)
    action_items_completion_rate: Optional[float] = Field(None, ge=0, le=100)
    homework_completion_rate: Optional[float] = Field(None, ge=0, le=100)
    creative_hours_logged: Optional[int] = Field(None, ge=0)
    experiments_launched: Optional[int] = Field(None, ge=0)

class CoachingMetricsCreate(CoachingMetricsBase):
    pass

class CoachingMetrics(CoachingMetricsBase):
    id: str
    client_id: str
    overall_coaching_effectiveness: Optional[int] = Field(None, ge=0, le=100)
    business_transformation_score: Optional[int] = Field(None, ge=0, le=100)
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Response schemas for API endpoints
class ClientDashboardResponse(BaseModel):
    client: CoachingClient
    current_hedgehog: Optional[HedgehogConcept] = None
    active_flywheels: List[Flywheel] = []
    recent_sessions: List[CoachingSession] = []
    active_experiments: List[BulletsCannonballs] = []
    recent_metrics: Optional[CoachingMetrics] = None
    
    # Calculated insights
    coaching_health_score: int = Field(..., ge=0, le=100)
    priority_focus_areas: List[str] = []
    upcoming_milestones: List[Dict[str, Any]] = []

class VetSorceryIntegrationResponse(BaseModel):
    client_id: str
    integration_active: bool
    clinic_count: int
    total_revenue: Optional[float] = None
    avg_revenue_per_clinic: Optional[float] = None
    top_performing_clinics: List[Dict[str, Any]] = []
    coaching_impact_metrics: Dict[str, Any] = {}
    recommended_focus_areas: List[str] = []

class FrameworkProgressResponse(BaseModel):
    framework_name: str
    current_score: int = Field(..., ge=0, le=100)
    score_history: List[Dict[str, Any]] = []
    improvement_trend: str = Field(..., regex=r'^(improving|stable|declining|insufficient_data)$')
    next_milestone: Optional[str] = None
    recommended_actions: List[str] = []

# Bulk operation schemas
class BulkClientUpdateRequest(BaseModel):
    client_ids: List[str] = Field(..., min_items=1, max_items=100)
    updates: CoachingClientUpdate

class BulkOperationResponse(BaseModel):
    success_count: int
    failure_count: int
    errors: List[Dict[str, str]] = []
    updated_clients: List[str] = []

# Analytics and reporting schemas
class CoachingAnalyticsRequest(BaseModel):
    client_ids: Optional[List[str]] = None
    date_range_start: datetime
    date_range_end: datetime
    frameworks: Optional[List[str]] = Field(None, max_items=10)
    business_types: Optional[List[BusinessType]] = None
    coaching_tiers: Optional[List[CoachingTier]] = None

class CoachingAnalyticsResponse(BaseModel):
    summary_stats: Dict[str, Any]
    framework_effectiveness: Dict[str, float]
    client_progression_patterns: List[Dict[str, Any]]
    roi_analysis: Dict[str, Any]
    recommendations: List[str]