"""
HardCard Business Coaching System API
Implementing Jim Collins' frameworks with VetSorcery integration

Features:
- Hedgehog Concept development and tracking
- Flywheel momentum measurement
- Level 5 Leadership assessments
- Creative Hours logging and analysis
- Bullets/Cannonballs experiment management
- Return on Luck event tracking
- Multi-tenant coaching client management
- VetSorcery revenue optimization integration
- Comprehensive analytics and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass

# Import schemas and models
from .schemas import (
    CoachingClient, CoachingClientCreate, CoachingClientUpdate,
    HedgehogConcept, HedgehogConceptCreate, HedgehogConceptUpdate,
    Flywheel, FlywheelCreate, FlywheelUpdate,
    FlywheelMomentumLog, FlywheelMomentumLogCreate,
    Level5Assessment, Level5AssessmentCreate, Level5AssessmentUpdate,
    CreativeHours, CreativeHoursCreate, CreativeHoursUpdate,
    BulletsCannonballs, BulletsCannonballsCreate, BulletsCannonballsUpdate,
    ReturnOnLuck, ReturnOnLuckCreate, ReturnOnLuckUpdate,
    CoachingSession, CoachingSessionCreate, CoachingSessionUpdate,
    CoachingMetrics, CoachingMetricsCreate,
    ClientDashboardResponse, VetSorceryIntegrationResponse,
    FrameworkProgressResponse, CoachingAnalyticsRequest, CoachingAnalyticsResponse,
    BusinessType, CoachingTier, ExperimentStatus
)

from .models import (
    CoachingClient as CoachingClientModel,
    HedgehogConcept as HedgehogConceptModel,
    Flywheel as FlywheelModel,
    FlywheelMomentumLog as FlywheelMomentumLogModel,
    Level5Assessment as Level5AssessmentModel,
    CreativeHours as CreativeHoursModel,
    BulletsCannonballs as BulletsCannonballsModel,
    ReturnOnLuck as ReturnOnLuckModel,
    CoachingSession as CoachingSessionModel,
    CoachingMetrics as CoachingMetricsModel,
    get_client_secure, get_clients_for_user,
    calculate_hedgehog_alignment, calculate_level5_composite,
    calculate_flywheel_momentum, calculate_experiment_calibration,
    calculate_return_on_luck_effectiveness
)

# Import auth and database dependencies (adjust imports based on your project structure)
try:
    from app.auth import AuthorizedUser
    from app.database import get_db
except ImportError:
    # Fallback for different project structures
    from ...auth import AuthorizedUser
    from ...database import get_db

# VetSorcery integration imports
try:
    import databutton as db
    DATABUTTON_AVAILABLE = True
except ImportError:
    DATABUTTON_AVAILABLE = False
    print("Warning: DataButton not available for VetSorcery integration")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/coaching", tags=["Business Coaching"])

# Utility functions for VetSorcery integration
class VetSorceryIntegration:
    """Handle VetSorcery data integration for coaching clients"""
    
    @staticmethod
    def get_clinic_revenue_data(clinic_ids: List[str]) -> Dict[str, Any]:
        """Fetch revenue data for specified clinics"""
        if not DATABUTTON_AVAILABLE or not clinic_ids:
            return {}
        
        try:
            # Mock implementation - replace with actual VetSorcery API calls
            revenue_data = {}
            for clinic_id in clinic_ids:
                # This would normally fetch from VetSorcery database
                revenue_data[clinic_id] = {
                    "monthly_revenue": 45000,  # Mock data
                    "appointment_count": 320,
                    "avg_revenue_per_appointment": 140.63,
                    "phone_agent_adoption": 85.5,
                    "client_satisfaction": 4.7
                }
            return revenue_data
        except Exception as e:
            logger.error(f"Failed to fetch VetSorcery data: {e}")
            return {}
    
    @staticmethod
    def analyze_revenue_trends(clinic_ids: List[str], days: int = 90) -> Dict[str, Any]:
        """Analyze revenue trends for coaching insights"""
        if not DATABUTTON_AVAILABLE:
            return {}
        
        try:
            # Mock trend analysis - replace with actual implementation
            return {
                "total_revenue_growth": 12.5,  # 12.5% growth
                "clinic_performance_variance": 8.3,  # 8.3% variance between clinics
                "top_performing_clinic": clinic_ids[0] if clinic_ids else None,
                "improvement_opportunities": [
                    "Optimize appointment scheduling efficiency",
                    "Increase phone agent utilization during peak hours",
                    "Implement follow-up protocols for missed appointments"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to analyze revenue trends: {e}")
            return {}

@dataclass
class CoachingInsights:
    """Generate coaching insights from client data"""
    
    @staticmethod
    def calculate_coaching_health_score(
        hedgehog_score: Optional[int],
        flywheel_score: Optional[int],
        leadership_score: Optional[float],
        experiments_active: int,
        sessions_frequency: float
    ) -> int:
        """Calculate overall coaching health score (0-100)"""
        scores = []
        
        # Framework implementation scores (40% weight)
        if hedgehog_score:
            scores.append(hedgehog_score * 10)  # Convert 1-10 to 1-100
        if flywheel_score:
            scores.append(flywheel_score)  # Already 1-100
        if leadership_score:
            scores.append(leadership_score * 10)  # Convert 1-10 to 1-100
            
        framework_avg = sum(scores) / len(scores) if scores else 0
        
        # Engagement scores (35% weight)
        engagement_score = min(sessions_frequency * 25, 100)  # 4+ sessions per month = 100
        
        # Experimentation score (25% weight)
        experiment_score = min(experiments_active * 20, 100)  # 5+ experiments = 100
        
        # Weighted composite
        health_score = (
            framework_avg * 0.4 +
            engagement_score * 0.35 +
            experiment_score * 0.25
        )
        
        return int(min(health_score, 100))
    
    @staticmethod
    def identify_priority_focus_areas(client_data: Dict[str, Any]) -> List[str]:
        """Identify priority areas needing attention"""
        focus_areas = []
        
        # Check Hedgehog Concept clarity
        hedgehog = client_data.get('hedgehog')
        if not hedgehog or not all([
            hedgehog.get('passion_score', 0) >= 7,
            hedgehog.get('genetic_encoding_score', 0) >= 7,
            hedgehog.get('economic_engine_score', 0) >= 7
        ]):
            focus_areas.append("Clarify Hedgehog Concept")
        
        # Check Flywheel momentum
        flywheel = client_data.get('flywheel')
        if not flywheel or flywheel.get('current_momentum_score', 0) < 70:
            focus_areas.append("Build Flywheel Momentum")
        
        # Check Leadership development
        leadership = client_data.get('leadership')
        if not leadership or leadership.get('overall_level5_score', 0) < 7:
            focus_areas.append("Develop Level 5 Leadership")
        
        # Check experimentation
        experiments = client_data.get('active_experiments', [])
        if len(experiments) < 2:
            focus_areas.append("Increase Experimentation (Bullets)")
        
        # Check Creative Hours
        creative_hours = client_data.get('creative_hours_monthly', 0)
        if creative_hours < 10:  # Less than 10 hours per month
            focus_areas.append("Establish Creative Hours Discipline")
        
        return focus_areas[:3]  # Return top 3 priorities

# Client Management Endpoints
@router.post("/clients", response_model=CoachingClient)
async def create_coaching_client(
    client_data: CoachingClientCreate,
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Create a new coaching client"""
    try:
        # Create client model
        db_client = CoachingClientModel(
            **client_data.dict(),
            primary_contact_email=current_user.email  # Override with current user
        )
        
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        
        logger.info(f"Created coaching client: {db_client.id} for user: {current_user.email}")
        return db_client
        
    except Exception as e:
        logger.error(f"Failed to create coaching client: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create coaching client: {str(e)}"
        )

@router.get("/clients", response_model=List[CoachingClient])
async def get_coaching_clients(
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    business_type: Optional[BusinessType] = None,
    coaching_tier: Optional[CoachingTier] = None
):
    """Get coaching clients for current user"""
    try:
        clients = get_clients_for_user(db, current_user.email)
        
        # Apply filters
        if business_type:
            clients = [c for c in clients if c.business_type == business_type]
        if coaching_tier:
            clients = [c for c in clients if c.coaching_tier == coaching_tier]
        
        # Apply pagination
        clients = clients[skip:skip + limit]
        
        return clients
        
    except Exception as e:
        logger.error(f"Failed to get coaching clients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coaching clients"
        )

@router.get("/clients/{client_id}", response_model=CoachingClient)
async def get_coaching_client(
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Get specific coaching client"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    return client

@router.put("/clients/{client_id}", response_model=CoachingClient)
async def update_coaching_client(
    client_data: CoachingClientUpdate,
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Update coaching client"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    try:
        # Update client fields
        for field, value in client_data.dict(exclude_unset=True).items():
            setattr(client, field, value)
        
        db.commit()
        db.refresh(client)
        
        logger.info(f"Updated coaching client: {client_id}")
        return client
        
    except Exception as e:
        logger.error(f"Failed to update coaching client: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update coaching client"
        )

# Client Dashboard Endpoint
@router.get("/clients/{client_id}/dashboard", response_model=ClientDashboardResponse)
async def get_client_dashboard(
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Get comprehensive client dashboard with all coaching data"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    try:
        # Get current Hedgehog Concept
        current_hedgehog = db.query(HedgehogConceptModel).filter(
            HedgehogConceptModel.client_id == client_id,
            HedgehogConceptModel.is_current == True
        ).first()
        
        # Get active Flywheels
        active_flywheels = db.query(FlywheelModel).filter(
            FlywheelModel.client_id == client_id,
            FlywheelModel.is_active == True
        ).all()
        
        # Get recent sessions (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_sessions = db.query(CoachingSessionModel).filter(
            CoachingSessionModel.client_id == client_id,
            CoachingSessionModel.session_date >= thirty_days_ago
        ).order_by(CoachingSessionModel.session_date.desc()).limit(10).all()
        
        # Get active experiments
        active_experiments = db.query(BulletsCannonballsModel).filter(
            BulletsCannonballsModel.client_id == client_id,
            BulletsCannonballsModel.status.in_(['planning', 'active'])
        ).all()
        
        # Get recent metrics
        recent_metrics = db.query(CoachingMetricsModel).filter(
            CoachingMetricsModel.client_id == client_id
        ).order_by(CoachingMetricsModel.metric_date.desc()).first()
        
        # Calculate coaching health score
        coaching_data = {
            'hedgehog': {
                'passion_score': current_hedgehog.passion_score if current_hedgehog else None,
                'genetic_encoding_score': current_hedgehog.genetic_encoding_score if current_hedgehog else None,
                'economic_engine_score': current_hedgehog.economic_engine_score if current_hedgehog else None
            },
            'flywheel': {
                'current_momentum_score': active_flywheels[0].current_momentum_score if active_flywheels else None
            },
            'leadership': {
                'overall_level5_score': None  # Would fetch from latest assessment
            },
            'active_experiments': active_experiments,
            'creative_hours_monthly': 0  # Would calculate from recent creative hours
        }
        
        health_score = CoachingInsights.calculate_coaching_health_score(
            hedgehog_score=current_hedgehog.hedgehog_alignment_score if current_hedgehog else None,
            flywheel_score=active_flywheels[0].current_momentum_score if active_flywheels else None,
            leadership_score=None,  # Would get from recent assessment
            experiments_active=len(active_experiments),
            sessions_frequency=len(recent_sessions) / 4  # Sessions per week over last month
        )
        
        # Identify priority focus areas
        priority_areas = CoachingInsights.identify_priority_focus_areas(coaching_data)
        
        # Generate upcoming milestones
        upcoming_milestones = []
        if current_hedgehog and current_hedgehog.next_review_date:
            upcoming_milestones.append({
                "type": "hedgehog_review",
                "date": current_hedgehog.next_review_date,
                "description": "Hedgehog Concept Review"
            })
        
        return ClientDashboardResponse(
            client=client,
            current_hedgehog=current_hedgehog,
            active_flywheels=active_flywheels,
            recent_sessions=recent_sessions,
            active_experiments=active_experiments,
            recent_metrics=recent_metrics,
            coaching_health_score=health_score,
            priority_focus_areas=priority_areas,
            upcoming_milestones=upcoming_milestones
        )
        
    except Exception as e:
        logger.error(f"Failed to get client dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client dashboard"
        )

# VetSorcery Integration Endpoints
@router.get("/clients/{client_id}/vetsorcery-integration", response_model=VetSorceryIntegrationResponse)
async def get_vetsorcery_integration(
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Get VetSorcery integration data and coaching insights"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    if not client.vetsorcery_integration_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VetSorcery integration is not active for this client"
        )
    
    try:
        clinic_ids = client.vetsorcery_clinic_ids or []
        
        # Get revenue data from VetSorcery
        revenue_data = VetSorceryIntegration.get_clinic_revenue_data(clinic_ids)
        trend_analysis = VetSorceryIntegration.analyze_revenue_trends(clinic_ids)
        
        # Calculate aggregated metrics
        total_revenue = sum(clinic['monthly_revenue'] for clinic in revenue_data.values())
        avg_revenue_per_clinic = total_revenue / len(clinic_ids) if clinic_ids else 0
        
        # Identify top performing clinics
        top_clinics = sorted(
            [{"clinic_id": k, **v} for k, v in revenue_data.items()],
            key=lambda x: x['monthly_revenue'],
            reverse=True
        )[:3]
        
        # Generate coaching-specific insights
        coaching_insights = {
            "revenue_consistency": trend_analysis.get('clinic_performance_variance', 0),
            "growth_trajectory": trend_analysis.get('total_revenue_growth', 0),
            "operational_excellence": sum(c['phone_agent_adoption'] for c in revenue_data.values()) / len(revenue_data) if revenue_data else 0
        }
        
        # Recommend focus areas based on data
        focus_areas = trend_analysis.get('improvement_opportunities', [])
        
        return VetSorceryIntegrationResponse(
            client_id=client_id,
            integration_active=True,
            clinic_count=len(clinic_ids),
            total_revenue=total_revenue,
            avg_revenue_per_clinic=avg_revenue_per_clinic,
            top_performing_clinics=top_clinics,
            coaching_impact_metrics=coaching_insights,
            recommended_focus_areas=focus_areas
        )
        
    except Exception as e:
        logger.error(f"Failed to get VetSorcery integration data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve VetSorcery integration data"
        )

@router.post("/clients/{client_id}/vetsorcery-integration/activate")
async def activate_vetsorcery_integration(
    clinic_ids: List[str],
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Activate VetSorcery integration for coaching client"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    try:
        # Validate clinic access (would normally check VetSorcery permissions)
        client.vetsorcery_clinic_ids = clinic_ids
        client.vetsorcery_integration_active = True
        client.revenue_optimization_enabled = True
        
        db.commit()
        
        logger.info(f"Activated VetSorcery integration for client {client_id} with {len(clinic_ids)} clinics")
        
        return {"message": f"VetSorcery integration activated with {len(clinic_ids)} clinics"}
        
    except Exception as e:
        logger.error(f"Failed to activate VetSorcery integration: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate VetSorcery integration"
        )

# Hedgehog Concept Endpoints
@router.post("/clients/{client_id}/hedgehog-concept", response_model=HedgehogConcept)
async def create_hedgehog_concept(
    hedgehog_data: HedgehogConceptCreate,
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Create new Hedgehog Concept for client"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    try:
        # Mark existing hedgehog concepts as not current
        db.query(HedgehogConceptModel).filter(
            HedgehogConceptModel.client_id == client_id
        ).update({"is_current": False})
        
        # Create new hedgehog concept
        db_hedgehog = HedgehogConceptModel(
            **hedgehog_data.dict(),
            client_id=client_id,
            created_by=current_user.email,
            is_current=True
        )
        
        # Calculate alignment score
        if all([
            hedgehog_data.passion_score,
            hedgehog_data.genetic_encoding_score,
            hedgehog_data.economic_engine_score
        ]):
            db_hedgehog.hedgehog_alignment_score = calculate_hedgehog_alignment(
                hedgehog_data.passion_score,
                hedgehog_data.genetic_encoding_score,
                hedgehog_data.economic_engine_score
            )
        
        db.add(db_hedgehog)
        db.commit()
        db.refresh(db_hedgehog)
        
        logger.info(f"Created Hedgehog Concept for client: {client_id}")
        return db_hedgehog
        
    except Exception as e:
        logger.error(f"Failed to create Hedgehog Concept: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Hedgehog Concept"
        )

@router.get("/clients/{client_id}/hedgehog-concept/current", response_model=Optional[HedgehogConcept])
async def get_current_hedgehog_concept(
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Get current Hedgehog Concept for client"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    hedgehog = db.query(HedgehogConceptModel).filter(
        HedgehogConceptModel.client_id == client_id,
        HedgehogConceptModel.is_current == True
    ).first()
    
    return hedgehog

# Additional framework endpoints would follow similar patterns...
# For brevity, I'll include a few key ones:

# Flywheel Endpoints
@router.post("/clients/{client_id}/flywheels", response_model=Flywheel)
async def create_flywheel(
    flywheel_data: FlywheelCreate,
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Create new Flywheel for client"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    try:
        db_flywheel = FlywheelModel(
            **flywheel_data.dict(),
            client_id=client_id
        )
        
        db.add(db_flywheel)
        db.commit()
        db.refresh(db_flywheel)
        
        logger.info(f"Created Flywheel for client: {client_id}")
        return db_flywheel
        
    except Exception as e:
        logger.error(f"Failed to create Flywheel: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Flywheel"
        )

# Coaching Session Endpoints
@router.post("/clients/{client_id}/sessions", response_model=CoachingSession)
async def create_coaching_session(
    session_data: CoachingSessionCreate,
    client_id: str = Path(...),
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Create new coaching session"""
    client = get_client_secure(db, client_id, current_user.email)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching client not found"
        )
    
    try:
        db_session = CoachingSessionModel(
            **session_data.dict(),
            client_id=client_id
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        
        logger.info(f"Created coaching session for client: {client_id}")
        return db_session
        
    except Exception as e:
        logger.error(f"Failed to create coaching session: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create coaching session"
        )

# Analytics Endpoints
@router.post("/analytics", response_model=CoachingAnalyticsResponse)
async def get_coaching_analytics(
    analytics_request: CoachingAnalyticsRequest,
    db: Session = Depends(get_db),
    current_user: AuthorizedUser = Depends()
):
    """Generate comprehensive coaching analytics"""
    try:
        # Get clients for analysis
        client_ids = analytics_request.client_ids
        if not client_ids:
            # Get all clients for user
            clients = get_clients_for_user(db, current_user.email)
            client_ids = [c.id for c in clients]
        
        # Generate analytics (mock implementation)
        summary_stats = {
            "total_clients": len(client_ids),
            "avg_coaching_health_score": 75,
            "total_experiments": 24,
            "successful_experiments": 18,
            "avg_session_satisfaction": 8.4
        }
        
        framework_effectiveness = {
            "hedgehog_concept": 0.85,
            "flywheel": 0.78,
            "level5_leadership": 0.72,
            "bullets_cannonballs": 0.89,
            "return_on_luck": 0.66
        }
        
        recommendations = [
            "Focus on Level 5 Leadership development across all clients",
            "Increase Creative Hours discipline - average is below recommended threshold",
            "More clients should scale successful bullets to cannonballs",
            "Improve Return on Luck preparation and response protocols"
        ]
        
        return CoachingAnalyticsResponse(
            summary_stats=summary_stats,
            framework_effectiveness=framework_effectiveness,
            client_progression_patterns=[],
            roi_analysis={},
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Failed to generate coaching analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate coaching analytics"
        )

# Health check endpoint
@router.get("/health")
async def coaching_health_check():
    """Health check for coaching system"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "features": {
            "jim_collins_frameworks": True,
            "vetsorcery_integration": DATABUTTON_AVAILABLE,
            "multi_tenant_support": True,
            "analytics": True
        }
    }