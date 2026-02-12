"""
Jim Collins-inspired Discipline and Strategy Tracking API

This module provides endpoints for:
1. 20-Mile March discipline tracking (daily creative hours, quality ratings)
2. Bullets-then-Cannonballs strategy management (experiments, ROI tracking)
3. Automated pattern analysis and insights generation
4. Performance analytics and recommendations
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import statistics
import json
from collections import defaultdict, Counter
import logging

# Database setup
Base = declarative_base()
router = APIRouter(prefix="/api/coaching/tracking", tags=["Coaching Tracking"])

# Models
class DisciplineEntry(Base):
    __tablename__ = "discipline_entries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    creative_hours = Column(Float, nullable=False)
    quality_rating = Column(Integer, nullable=False)  # -2 to +2
    notes = Column(Text)
    completed_tasks = Column(JSON)  # List of strings
    insights = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StrategyExperiment(Base):
    __tablename__ = "strategy_experiments"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    experiment_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)  # 'bullet' or 'cannonball'
    status = Column(String, default='planning')  # planning, active, completed, failed
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    investment = Column(Float, default=0)
    expected_roi = Column(Float, default=0)
    actual_roi = Column(Float)
    success_criteria = Column(JSON)  # List of strings
    results = Column(JSON)  # List of strings
    lessons = Column(JSON)  # List of strings
    based_on_bullets = Column(JSON)  # For cannonballs - list of bullet IDs
    milestones = Column(JSON)  # List of milestone objects
    risk_assessment = Column(JSON)  # List of risk objects
    readiness_score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models
class DisciplineEntryCreate(BaseModel):
    date: date
    creative_hours: float = Field(..., ge=0, le=24)
    quality_rating: int = Field(..., ge=-2, le=2)
    notes: Optional[str] = ""
    completed_tasks: List[str] = []
    insights: Optional[str] = ""

class DisciplineEntryResponse(BaseModel):
    id: int
    date: date
    creative_hours: float
    quality_rating: int
    notes: str
    completed_tasks: List[str]
    insights: str
    created_at: datetime
    updated_at: datetime

class StrategyExperimentCreate(BaseModel):
    name: str
    description: str
    type: str = Field(..., regex="^(bullet|cannonball)$")
    investment: float = Field(default=0, ge=0)
    expected_roi: float = Field(default=0)
    success_criteria: List[str] = []
    based_on_bullets: List[str] = []  # For cannonballs

class StrategyExperimentUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    status: Optional[str] = Field(None, regex="^(planning|active|completed|failed)$")
    end_date: Optional[date]
    actual_roi: Optional[float]
    results: List[str] = []
    lessons: List[str] = []

class StrategyExperimentResponse(BaseModel):
    id: int
    experiment_id: str
    name: str
    description: str
    type: str
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    investment: float
    expected_roi: float
    actual_roi: Optional[float]
    success_criteria: List[str]
    results: List[str]
    lessons: List[str]
    based_on_bullets: List[str]
    readiness_score: float
    created_at: datetime
    updated_at: datetime

class PatternAnalysis(BaseModel):
    average_hours: float
    average_quality: float
    best_performance_days: List[str]
    struggling_days: List[str]
    insights: List[str]
    recommendations: List[str]
    day_of_week_patterns: Dict[str, Dict[str, float]]
    monthly_trends: Dict[str, float]

class StrategyInsights(BaseModel):
    total_experiments: int
    active_bullets: int
    active_cannonballs: int
    success_rate: float
    total_investment: float
    total_returns: float
    ready_for_scale: int
    recommendations: List[str]
    risk_assessment: Dict[str, Any]

# Dependency to get database session
def get_db():
    # In a real app, this would use your actual database connection
    # For now, we'll use in-memory storage
    pass

# Helper functions
def analyze_discipline_patterns(entries: List[DisciplineEntry]) -> PatternAnalysis:
    """Analyze discipline tracking patterns and generate insights."""
    if not entries:
        return PatternAnalysis(
            average_hours=0,
            average_quality=0,
            best_performance_days=[],
            struggling_days=[],
            insights=["No data available for analysis"],
            recommendations=["Start logging daily entries to get insights"],
            day_of_week_patterns={},
            monthly_trends={}
        )
    
    # Calculate averages
    total_hours = sum(entry.creative_hours for entry in entries)
    total_quality = sum(entry.quality_rating for entry in entries)
    avg_hours = total_hours / len(entries)
    avg_quality = total_quality / len(entries)
    
    # Find best and worst performing days
    sorted_by_hours = sorted(entries, key=lambda x: x.creative_hours, reverse=True)
    best_days = [entry.date.strftime('%Y-%m-%d') for entry in sorted_by_hours[:3]]
    struggling_days = [entry.date.strftime('%Y-%m-%d') for entry in sorted_by_hours[-3:]]
    
    # Day of week analysis
    day_patterns = defaultdict(lambda: {'hours': [], 'quality': []})
    for entry in entries:
        day_name = entry.date.strftime('%A')
        day_patterns[day_name]['hours'].append(entry.creative_hours)
        day_patterns[day_name]['quality'].append(entry.quality_rating)
    
    day_of_week_patterns = {}
    for day, data in day_patterns.items():
        day_of_week_patterns[day] = {
            'avg_hours': statistics.mean(data['hours']) if data['hours'] else 0,
            'avg_quality': statistics.mean(data['quality']) if data['quality'] else 0
        }
    
    # Monthly trends
    monthly_data = defaultdict(list)
    for entry in entries:
        month_key = entry.date.strftime('%Y-%m')
        monthly_data[month_key].append(entry.creative_hours)
    
    monthly_trends = {
        month: statistics.mean(hours) for month, hours in monthly_data.items()
    }
    
    # Generate insights
    insights = []
    recommendations = []
    
    daily_target = 1000 / 365  # 1000 hours annual goal
    
    if avg_hours < daily_target:
        insights.append(f"Currently averaging {avg_hours:.1f}h/day, below 20-Mile March pace")
        recommendations.append(f"Increase daily focus time by {daily_target - avg_hours:.1f} hours")
    
    if avg_quality < 0:
        insights.append("Quality ratings trending negative - possible burnout or wrong focus")
        recommendations.append("Review task selection and energy management strategies")
    
    # Find best performing day
    if day_of_week_patterns:
        best_day = max(day_of_week_patterns.items(), key=lambda x: x[1]['avg_hours'])
        insights.append(f"{best_day[0]} is your most productive day ({best_day[1]['avg_hours']:.1f}h avg)")
        recommendations.append(f"Schedule important creative work on {best_day[0]}s")
    
    # Consistency analysis
    if len(entries) >= 7:
        recent_variance = statistics.stdev([e.creative_hours for e in entries[-7:]])
        if recent_variance > 2:
            insights.append("High variability in recent performance - inconsistent habits")
            recommendations.append("Focus on consistent daily routines to reduce variance")
    
    return PatternAnalysis(
        average_hours=avg_hours,
        average_quality=avg_quality,
        best_performance_days=best_days,
        struggling_days=struggling_days,
        insights=insights,
        recommendations=recommendations,
        day_of_week_patterns=day_of_week_patterns,
        monthly_trends=monthly_trends
    )

def analyze_strategy_performance(experiments: List[StrategyExperiment]) -> StrategyInsights:
    """Analyze strategy experiment performance and generate insights."""
    if not experiments:
        return StrategyInsights(
            total_experiments=0,
            active_bullets=0,
            active_cannonballs=0,
            success_rate=0,
            total_investment=0,
            total_returns=0,
            ready_for_scale=0,
            recommendations=["Start with 3-5 small bullet experiments"],
            risk_assessment={}
        )
    
    bullets = [e for e in experiments if e.type == 'bullet']
    cannonballs = [e for e in experiments if e.type == 'cannonball']
    
    active_bullets = len([b for b in bullets if b.status == 'active'])
    active_cannonballs = len([c for c in cannonballs if c.status == 'active'])
    
    completed_experiments = [e for e in experiments if e.status == 'completed']
    successful_experiments = [e for e in completed_experiments if (e.actual_roi or 0) > 0]
    
    success_rate = len(successful_experiments) / len(completed_experiments) * 100 if completed_experiments else 0
    
    total_investment = sum(e.investment for e in experiments)
    total_returns = sum((e.actual_roi or 0) * e.investment / 100 for e in completed_experiments)
    
    # Calculate ready for scale (bullets with >100% ROI)
    ready_bullets = [b for b in bullets if b.status == 'completed' and (b.actual_roi or 0) > 100]
    ready_for_scale = len(ready_bullets)
    
    # Generate recommendations
    recommendations = []
    
    if len(experiments) == 0:
        recommendations.append("Start with 3-5 small bullet experiments to test assumptions")
    
    if active_bullets > 5:
        recommendations.append("Consider focusing on fewer active bullets for better resource allocation")
    
    if ready_for_scale > 0 and len(cannonballs) == 0:
        recommendations.append(f"You have {ready_for_scale} bullets ready to scale into cannonballs")
    
    if success_rate < 30 and len(completed_experiments) > 3:
        recommendations.append("Review bullet selection criteria - success rate below optimal")
    
    if len(bullets) > 0 and len([b for b in bullets if b.status == 'failed']) / len(bullets) > 0.5:
        recommendations.append("High failure rate - consider smaller, lower-risk experiments")
    
    # Risk assessment
    risk_assessment = {
        "high_investment_experiments": len([e for e in experiments if e.investment > 10000]),
        "long_running_experiments": len([e for e in experiments if e.start_date and 
                                       (datetime.now() - e.start_date).days > 90]),
        "concentration_risk": "High" if active_cannonballs > active_bullets else "Low"
    }
    
    return StrategyInsights(
        total_experiments=len(experiments),
        active_bullets=active_bullets,
        active_cannonballs=active_cannonballs,
        success_rate=success_rate,
        total_investment=total_investment,
        total_returns=total_returns,
        ready_for_scale=ready_for_scale,
        recommendations=recommendations,
        risk_assessment=risk_assessment
    )

def calculate_readiness_score(bullet: StrategyExperiment) -> float:
    """Calculate cannonball readiness score for a bullet experiment."""
    if bullet.type != 'bullet' or bullet.status != 'completed':
        return 0
    
    score = 0
    
    # Financial performance (40% weight)
    if bullet.actual_roi and bullet.actual_roi > 100:
        score += 40
    elif bullet.actual_roi and bullet.actual_roi > 50:
        score += 20
    
    # Market validation (30% weight)
    if len(bullet.results) >= 3:
        score += 30
    elif len(bullet.results) >= 1:
        score += 15
    
    # Operational readiness (20% weight)
    if len(bullet.lessons) >= 2:
        score += 20
    elif len(bullet.lessons) >= 1:
        score += 10
    
    # Risk assessment (10% weight)
    if len(bullet.success_criteria) >= 3:
        score += 10
    elif len(bullet.success_criteria) >= 1:
        score += 5
    
    return min(score, 100)

# API Endpoints

@router.post("/discipline", response_model=DisciplineEntryResponse)
async def create_discipline_entry(entry: DisciplineEntryCreate, user_id: str = "default"):
    """Create a new discipline tracking entry."""
    try:
        # In a real implementation, you would save to database
        # For now, we'll return a mock response
        response_data = {
            "id": 1,
            "date": entry.date,
            "creative_hours": entry.creative_hours,
            "quality_rating": entry.quality_rating,
            "notes": entry.notes or "",
            "completed_tasks": entry.completed_tasks,
            "insights": entry.insights or "",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return DisciplineEntryResponse(**response_data)
    except Exception as e:
        logging.error(f"Error creating discipline entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create discipline entry")

@router.get("/discipline", response_model=List[DisciplineEntryResponse])
async def get_discipline_entries(user_id: str = "default", days: int = 30):
    """Get discipline tracking entries for the last N days."""
    try:
        # Mock response - in real implementation, query database
        mock_entries = []
        return mock_entries
    except Exception as e:
        logging.error(f"Error fetching discipline entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch discipline entries")

@router.get("/discipline/analysis", response_model=PatternAnalysis)
async def get_discipline_analysis(user_id: str = "default", days: int = 90):
    """Get automated pattern analysis and insights for discipline tracking."""
    try:
        # Mock response with sample insights
        return PatternAnalysis(
            average_hours=2.3,
            average_quality=0.4,
            best_performance_days=["2024-01-15", "2024-01-22", "2024-01-29"],
            struggling_days=["2024-01-08", "2024-01-16", "2024-01-23"],
            insights=[
                "Currently averaging 2.3h/day, slightly below 20-Mile March pace",
                "Tuesday is your most productive day (3.2h avg)",
                "Quality ratings improving over last 2 weeks"
            ],
            recommendations=[
                "Increase daily focus time by 0.4 hours to meet annual goal",
                "Schedule important creative work on Tuesdays",
                "Morning sessions show 40% higher quality ratings"
            ],
            day_of_week_patterns={
                "Monday": {"avg_hours": 2.1, "avg_quality": 0.2},
                "Tuesday": {"avg_hours": 3.2, "avg_quality": 0.8},
                "Wednesday": {"avg_hours": 2.4, "avg_quality": 0.3},
                "Thursday": {"avg_hours": 2.0, "avg_quality": 0.1},
                "Friday": {"avg_hours": 1.8, "avg_quality": 0.5}
            },
            monthly_trends={
                "2024-01": 2.1,
                "2024-02": 2.3,
                "2024-03": 2.5
            }
        )
    except Exception as e:
        logging.error(f"Error analyzing discipline patterns: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze discipline patterns")

@router.post("/experiments", response_model=StrategyExperimentResponse)
async def create_experiment(experiment: StrategyExperimentCreate, user_id: str = "default"):
    """Create a new strategy experiment (bullet or cannonball)."""
    try:
        experiment_id = f"{experiment.type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        response_data = {
            "id": 1,
            "experiment_id": experiment_id,
            "name": experiment.name,
            "description": experiment.description,
            "type": experiment.type,
            "status": "planning",
            "start_date": None,
            "end_date": None,
            "investment": experiment.investment,
            "expected_roi": experiment.expected_roi,
            "actual_roi": None,
            "success_criteria": experiment.success_criteria,
            "results": [],
            "lessons": [],
            "based_on_bullets": experiment.based_on_bullets,
            "readiness_score": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return StrategyExperimentResponse(**response_data)
    except Exception as e:
        logging.error(f"Error creating experiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create experiment")

@router.put("/experiments/{experiment_id}", response_model=StrategyExperimentResponse)
async def update_experiment(experiment_id: str, updates: StrategyExperimentUpdate, user_id: str = "default"):
    """Update an existing strategy experiment."""
    try:
        # Mock response for successful update
        response_data = {
            "id": 1,
            "experiment_id": experiment_id,
            "name": updates.name or "Updated Experiment",
            "description": updates.description or "Updated description",
            "type": "bullet",
            "status": updates.status or "active",
            "start_date": datetime.utcnow().date(),
            "end_date": updates.end_date,
            "investment": 1000,
            "expected_roi": 150,
            "actual_roi": updates.actual_roi,
            "success_criteria": ["Criterion 1", "Criterion 2"],
            "results": updates.results,
            "lessons": updates.lessons,
            "based_on_bullets": [],
            "readiness_score": 75,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return StrategyExperimentResponse(**response_data)
    except Exception as e:
        logging.error(f"Error updating experiment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update experiment")

@router.get("/experiments", response_model=List[StrategyExperimentResponse])
async def get_experiments(user_id: str = "default", experiment_type: Optional[str] = None):
    """Get all strategy experiments, optionally filtered by type."""
    try:
        # Mock response
        return []
    except Exception as e:
        logging.error(f"Error fetching experiments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch experiments")

@router.get("/experiments/{experiment_id}/readiness", response_model=Dict[str, Any])
async def get_experiment_readiness(experiment_id: str, user_id: str = "default"):
    """Get cannonball readiness assessment for a bullet experiment."""
    try:
        return {
            "experiment_id": experiment_id,
            "readiness_score": 85,
            "categories": {
                "financial_performance": {"score": 90, "passed": True},
                "market_validation": {"score": 80, "passed": True},
                "operational_readiness": {"score": 85, "passed": True},
                "risk_assessment": {"score": 85, "passed": True}
            },
            "recommendations": [
                "Strong financial performance indicates readiness for scale",
                "Consider launching cannonball initiative next quarter"
            ]
        }
    except Exception as e:
        logging.error(f"Error assessing readiness: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to assess experiment readiness")

@router.get("/strategy/insights", response_model=StrategyInsights)
async def get_strategy_insights(user_id: str = "default"):
    """Get comprehensive strategy performance insights and recommendations."""
    try:
        return StrategyInsights(
            total_experiments=12,
            active_bullets=3,
            active_cannonballs=1,
            success_rate=65.0,
            total_investment=25000,
            total_returns=38500,
            ready_for_scale=2,
            recommendations=[
                "You have 2 bullets ready to scale into cannonballs",
                "Success rate is healthy at 65%",
                "Consider launching next cannonball based on successful email marketing bullet"
            ],
            risk_assessment={
                "high_investment_experiments": 1,
                "long_running_experiments": 0,
                "concentration_risk": "Low"
            }
        )
    except Exception as e:
        logging.error(f"Error generating strategy insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate strategy insights")

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_coaching_dashboard(user_id: str = "default"):
    """Get comprehensive coaching dashboard data."""
    try:
        return {
            "discipline": {
                "current_streak": 7,
                "annual_progress": 23.5,
                "this_week_hours": 18.5,
                "average_quality": 0.6
            },
            "strategy": {
                "active_experiments": 4,
                "success_rate": 65.0,
                "ready_for_scale": 2,
                "total_roi": 154.0
            },
            "insights": [
                "7-day consistency streak - keep it up!",
                "2 bullets ready to scale into cannonballs",
                "Tuesday shows highest productivity patterns"
            ],
            "next_actions": [
                "Log today's creative hours",
                "Review bullet experiment results",
                "Plan next cannonball initiative"
            ]
        }
    except Exception as e:
        logging.error(f"Error generating dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate coaching dashboard")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for the coaching tracking API."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}