from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from .models import *
from .schemas import *
from app.core.database import get_db
from app.core.auth import get_current_user

router = APIRouter(prefix="/coaching", tags=["coaching"])

# User Management
@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new coaching user"""
    db_user = User(
        email=user.email,
        name=user.name,
        subscription_tier=user.subscription_tier
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Leadership Assessment Endpoints
@router.post("/assessments", response_model=LeadershipAssessmentResponse)
async def create_assessment(
    assessment: LeadershipAssessmentCreate, 
    db: Session = Depends(get_db)
):
    """Create a new Level 5 Leadership Assessment"""
    
    # Calculate overall score and leadership level
    scores = [
        assessment.humility_score,
        assessment.will_score,
        assessment.window_mirror_score,
        assessment.resolve_score,
        assessment.team_first_score
    ]
    overall_score = sum(scores) / len(scores)
    leadership_level = min(5.0, overall_score / 20)  # Convert to 0-5 scale
    
    # Generate AI insights
    strengths = []
    development_areas = []
    recommendations = []
    
    if assessment.humility_score >= 80:
        strengths.append("Exceptional humility and self-awareness")
    elif assessment.humility_score < 60:
        development_areas.append("Develop greater humility and receptiveness to feedback")
        recommendations.append("Seek 360-degree feedback from peers and direct reports")
    
    if assessment.will_score >= 80:
        strengths.append("Strong professional will and determination")
    elif assessment.will_score < 60:
        development_areas.append("Strengthen resolve and standards")
        recommendations.append("Set higher standards and hold yourself accountable")
    
    db_assessment = LeadershipAssessment(
        user_id=assessment.user_id,
        humility_score=assessment.humility_score,
        will_score=assessment.will_score,
        window_mirror_score=assessment.window_mirror_score,
        resolve_score=assessment.resolve_score,
        team_first_score=assessment.team_first_score,
        overall_score=overall_score,
        leadership_level=leadership_level,
        responses=assessment.responses,
        strengths=strengths,
        development_areas=development_areas,
        recommendations=recommendations
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment

@router.get("/assessments/{user_id}", response_model=List[LeadershipAssessmentResponse])
async def get_user_assessments(user_id: str, db: Session = Depends(get_db)):
    """Get all assessments for a user"""
    assessments = db.query(LeadershipAssessment).filter(
        LeadershipAssessment.user_id == user_id
    ).all()
    return assessments

@router.get("/assessments/{user_id}/latest", response_model=LeadershipAssessmentResponse)
async def get_latest_assessment(user_id: str, db: Session = Depends(get_db)):
    """Get user's most recent assessment"""
    assessment = db.query(LeadershipAssessment).filter(
        LeadershipAssessment.user_id == user_id
    ).order_by(LeadershipAssessment.created_at.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No assessments found")
    return assessment

# Hedgehog Concept Endpoints
@router.post("/hedgehog", response_model=HedgehogConceptResponse)
async def create_hedgehog(hedgehog: HedgehogConceptCreate, db: Session = Depends(get_db)):
    """Create or update a Hedgehog Concept"""
    
    # Calculate intersection strength based on overlap
    all_words = []
    for items in [hedgehog.passion_items, hedgehog.best_at_items, hedgehog.economic_items]:
        for item in items:
            all_words.extend(item.lower().split())
    
    word_freq = {}
    for word in all_words:
        if len(word) > 3:  # Filter out short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    common_themes = [word for word, count in word_freq.items() if count >= 2]
    intersection_strength = min(100, len(common_themes) * 20)
    
    # Generate insights
    insights = [
        f"Common themes identified: {', '.join(common_themes[:3])}" if common_themes else "No strong themes identified yet",
        f"Intersection strength: {intersection_strength}%",
        "Strong passion alignment" if len(hedgehog.passion_items) >= 3 else "Consider exploring more passions",
        "Diverse economic opportunities" if len(hedgehog.economic_items) >= 3 else "Expand revenue model thinking"
    ]
    
    clarity_score = min(100, (len(hedgehog.passion_items) + len(hedgehog.best_at_items) + len(hedgehog.economic_items)) * 10)
    
    db_hedgehog = HedgehogConcept(
        user_id=hedgehog.user_id,
        passion_items=hedgehog.passion_items,
        best_at_items=hedgehog.best_at_items,
        economic_items=hedgehog.economic_items,
        intersection_strength=intersection_strength,
        intersection_items=common_themes,
        insights=insights,
        clarity_score=clarity_score
    )
    
    db.add(db_hedgehog)
    db.commit()
    db.refresh(db_hedgehog)
    return db_hedgehog

@router.get("/hedgehog/{user_id}", response_model=HedgehogConceptResponse)
async def get_hedgehog(user_id: str, db: Session = Depends(get_db)):
    """Get user's Hedgehog Concept"""
    hedgehog = db.query(HedgehogConcept).filter(
        HedgehogConcept.user_id == user_id
    ).order_by(HedgehogConcept.updated_at.desc()).first()
    
    if not hedgehog:
        raise HTTPException(status_code=404, detail="Hedgehog Concept not found")
    return hedgehog

@router.put("/hedgehog/{hedgehog_id}", response_model=HedgehogConceptResponse)
async def update_hedgehog(
    hedgehog_id: str, 
    hedgehog_update: HedgehogConceptCreate, 
    db: Session = Depends(get_db)
):
    """Update an existing Hedgehog Concept"""
    db_hedgehog = db.query(HedgehogConcept).filter(HedgehogConcept.id == hedgehog_id).first()
    if not db_hedgehog:
        raise HTTPException(status_code=404, detail="Hedgehog Concept not found")
    
    # Update fields
    db_hedgehog.passion_items = hedgehog_update.passion_items
    db_hedgehog.best_at_items = hedgehog_update.best_at_items
    db_hedgehog.economic_items = hedgehog_update.economic_items
    db_hedgehog.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_hedgehog)
    return db_hedgehog

# Flywheel Endpoints
@router.post("/flywheel", response_model=FlywheelResponse)
async def create_flywheel(flywheel: FlywheelCreate, db: Session = Depends(get_db)):
    """Create a new Flywheel"""
    
    # Calculate momentum metrics
    stage_momentums = [stage.get('momentum', 50) for stage in flywheel.stages]
    overall_momentum = sum(stage_momentums) / len(stage_momentums) if stage_momentums else 0
    
    # Find weakest and strongest stages
    if stage_momentums:
        min_momentum = min(stage_momentums)
        max_momentum = max(stage_momentums)
        weakest_stage = next(stage['title'] for stage in flywheel.stages if stage.get('momentum') == min_momentum)
        strongest_stage = next(stage['title'] for stage in flywheel.stages if stage.get('momentum') == max_momentum)
    else:
        weakest_stage = strongest_stage = "Unknown"
    
    # Generate recommendations
    recommendations = []
    if overall_momentum < 50:
        recommendations.append("Focus on removing friction from each flywheel stage")
    if min_momentum < 30:
        recommendations.append(f"Critical: '{weakest_stage}' is severely limiting momentum")
    if max_momentum - min_momentum > 40:
        recommendations.append("Large momentum gaps between stages - balance the flywheel")
    
    projected_growth = 1.0 + (overall_momentum / 100) * 2  # 1.0x to 3.0x multiplier
    
    db_flywheel = Flywheel(
        user_id=flywheel.user_id,
        name=flywheel.name,
        description=flywheel.description,
        stages=flywheel.stages,
        overall_momentum=overall_momentum,
        weakest_stage=weakest_stage,
        strongest_stage=strongest_stage,
        recommendations=recommendations,
        projected_growth=projected_growth
    )
    
    db.add(db_flywheel)
    db.commit()
    db.refresh(db_flywheel)
    return db_flywheel

@router.get("/flywheel/{user_id}", response_model=List[FlywheelResponse])
async def get_user_flywheels(user_id: str, db: Session = Depends(get_db)):
    """Get all flywheels for a user"""
    flywheels = db.query(Flywheel).filter(Flywheel.user_id == user_id).all()
    return flywheels

@router.get("/flywheel/detail/{flywheel_id}", response_model=FlywheelResponse)
async def get_flywheel(flywheel_id: str, db: Session = Depends(get_db)):
    """Get specific flywheel by ID"""
    flywheel = db.query(Flywheel).filter(Flywheel.id == flywheel_id).first()
    if not flywheel:
        raise HTTPException(status_code=404, detail="Flywheel not found")
    return flywheel

@router.put("/flywheel/{flywheel_id}", response_model=FlywheelResponse)
async def update_flywheel(
    flywheel_id: str,
    flywheel_update: FlywheelCreate,
    db: Session = Depends(get_db)
):
    """Update an existing flywheel"""
    db_flywheel = db.query(Flywheel).filter(Flywheel.id == flywheel_id).first()
    if not db_flywheel:
        raise HTTPException(status_code=404, detail="Flywheel not found")
    
    # Update fields
    db_flywheel.name = flywheel_update.name
    db_flywheel.description = flywheel_update.description
    db_flywheel.stages = flywheel_update.stages
    db_flywheel.updated_at = datetime.utcnow()
    
    # Recalculate metrics
    stage_momentums = [stage.get('momentum', 50) for stage in flywheel_update.stages]
    db_flywheel.overall_momentum = sum(stage_momentums) / len(stage_momentums) if stage_momentums else 0
    
    db.commit()
    db.refresh(db_flywheel)
    return db_flywheel

# AI Insights Endpoints
@router.get("/insights/{user_id}", response_model=List[AIInsightResponse])
async def get_user_insights(
    user_id: str,
    framework: Optional[str] = Query(None),
    insight_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get AI insights for a user with optional filtering"""
    query = db.query(AIInsight).filter(AIInsight.user_id == user_id)
    
    if framework:
        query = query.filter(AIInsight.framework == framework)
    if insight_type:
        query = query.filter(AIInsight.insight_type == insight_type)
    
    insights = query.order_by(AIInsight.created_at.desc()).limit(20).all()
    return insights

@router.post("/insights", response_model=AIInsightResponse)
async def create_insight(insight: AIInsightCreate, db: Session = Depends(get_db)):
    """Create a new AI insight"""
    db_insight = AIInsight(
        user_id=insight.user_id,
        insight_type=insight.insight_type,
        framework=insight.framework,
        title=insight.title,
        message=insight.message,
        action_suggestion=insight.action_suggestion,
        confidence_score=insight.confidence_score,
        data_sources=insight.data_sources
    )
    
    db.add(db_insight)
    db.commit()
    db.refresh(db_insight)
    return db_insight

@router.put("/insights/{insight_id}/read")
async def mark_insight_read(insight_id: str, db: Session = Depends(get_db)):
    """Mark an insight as read"""
    insight = db.query(AIInsight).filter(AIInsight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_read = True
    db.commit()
    return {"status": "marked as read"}

@router.put("/insights/{insight_id}/rate")
async def rate_insight(
    insight_id: str, 
    rating: int = Query(..., ge=1, le=5),
    db: Session = Depends(get_db)
):
    """Rate an insight (1-5 stars)"""
    insight = db.query(AIInsight).filter(AIInsight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.user_rating = rating
    db.commit()
    return {"status": "rating updated"}

# Dashboard Summary Endpoint
@router.get("/dashboard/{user_id}")
async def get_dashboard_summary(user_id: str, db: Session = Depends(get_db)):
    """Get comprehensive dashboard summary for a user"""
    
    # Get latest data
    latest_assessment = db.query(LeadershipAssessment).filter(
        LeadershipAssessment.user_id == user_id
    ).order_by(LeadershipAssessment.created_at.desc()).first()
    
    hedgehog = db.query(HedgehogConcept).filter(
        HedgehogConcept.user_id == user_id
    ).order_by(HedgehogConcept.updated_at.desc()).first()
    
    recent_insights = db.query(AIInsight).filter(
        AIInsight.user_id == user_id
    ).order_by(AIInsight.created_at.desc()).limit(4).all()
    
    flywheels = db.query(Flywheel).filter(Flywheel.user_id == user_id).all()
    
    # Calculate metrics
    metrics = {
        "overallProgress": 65,  # Calculate based on completion
        "hedgehogClarity": hedgehog.clarity_score if hedgehog else 0,
        "flywheelMomentum": sum(f.overall_momentum for f in flywheels) / len(flywheels) if flywheels else 0,
        "leadershipLevel": latest_assessment.leadership_level if latest_assessment else 0,
        "disciplineStreak": 21,  # Would come from discipline tracker
        "strategyExperiments": 8,  # Would come from experiments
        "luckROI": 2.8  # Would come from ROL tracker
    }
    
    # Format insights
    insights_data = []
    for insight in recent_insights:
        insights_data.append({
            "id": insight.id,
            "type": insight.insight_type,
            "title": insight.title,
            "message": insight.message,
            "action": insight.action_suggestion,
            "framework": insight.framework
        })
    
    return {
        "metrics": metrics,
        "insights": insights_data,
        "hedgehogScore": hedgehog.intersection_strength if hedgehog else 0,
        "businessAlignment": metrics["overallProgress"],
        "lastAssessment": latest_assessment.created_at.isoformat() if latest_assessment else "Never",
        "recommendations": latest_assessment.recommendations if latest_assessment else [],
        "nextSteps": [
            "Complete Hedgehog Concept analysis",
            "Design your business flywheel",
            "Take Level 5 Leadership assessment"
        ]
    }

# Business Metrics Endpoints
@router.post("/metrics", response_model=BusinessMetricsResponse)
async def create_metrics(metrics: BusinessMetricsCreate, db: Session = Depends(get_db)):
    """Record business metrics"""
    db_metrics = BusinessMetrics(**metrics.dict())
    db.add(db_metrics)
    db.commit()
    db.refresh(db_metrics)
    return db_metrics

@router.get("/metrics/{user_id}", response_model=List[BusinessMetricsResponse])
async def get_user_metrics(
    user_id: str,
    period: Optional[str] = Query(None),
    limit: int = Query(default=12),
    db: Session = Depends(get_db)
):
    """Get business metrics for a user"""
    query = db.query(BusinessMetrics).filter(BusinessMetrics.user_id == user_id)
    
    if period:
        query = query.filter(BusinessMetrics.reporting_period == period)
    
    metrics = query.order_by(BusinessMetrics.period_date.desc()).limit(limit).all()
    return metrics

# Premium Session Endpoints (Tim Ferriss Coaching)
@router.post("/premium-sessions", response_model=PremiumSessionResponse)
async def create_premium_session(session: PremiumSessionCreate, db: Session = Depends(get_db)):
    """Create a premium coaching session"""
    db_session = PremiumSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/premium-sessions/{user_id}", response_model=List[PremiumSessionResponse])
async def get_user_premium_sessions(user_id: str, db: Session = Depends(get_db)):
    """Get premium sessions for a user"""
    sessions = db.query(PremiumSession).filter(
        PremiumSession.user_id == user_id
    ).order_by(PremiumSession.scheduled_at.desc()).all()
    return sessions

# Partnership Management
@router.get("/partnerships", response_model=List[PartnershipResponse])
async def get_partnerships(db: Session = Depends(get_db)):
    """Get all active partnerships"""
    partnerships = db.query(Partnership).filter(
        Partnership.status == "active"
    ).all()
    return partnerships

@router.post("/partnerships", response_model=PartnershipResponse)
async def create_partnership(partnership: PartnershipCreate, db: Session = Depends(get_db)):
    """Create a new partnership"""
    db_partnership = Partnership(**partnership.dict())
    db.add(db_partnership)
    db.commit()
    db.refresh(db_partnership)
    return db_partnership