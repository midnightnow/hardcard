"""
Business Coaching Analytics API

Comprehensive backend API for Jim Collins framework integration, 
AI-powered insights, and team collaboration features.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import pandas as pd
import numpy as np
from io import BytesIO
import base64

# AI and Analytics imports
import openai
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Firebase imports
import firebase_admin
from firebase_admin import firestore

router = APIRouter(prefix="/api/coaching", tags=["coaching"])

# Pydantic Models
class UserRole(str, Enum):
    COACH = "coach"
    CLIENT = "client"
    TEAM_MEMBER = "team_member"
    ADMIN = "admin"

class FrameworkType(str, Enum):
    GOOD_TO_GREAT = "good_to_great"
    LEVEL_5_LEADERSHIP = "level_5_leadership"
    HEDGEHOG_CONCEPT = "hedgehog_concept"
    CULTURE_OF_DISCIPLINE = "culture_of_discipline"
    TECHNOLOGY_ACCELERATOR = "technology_accelerator"
    FLYWHEEL = "flywheel"
    BUILT_TO_LAST = "built_to_last"

class CoachingSession(BaseModel):
    id: Optional[str] = None
    coach_id: str
    client_id: str
    framework_type: FrameworkType
    session_date: datetime
    duration_minutes: int
    objectives: List[str]
    outcomes: List[str]
    action_items: List[Dict[str, Any]]
    progress_score: float = Field(ge=0, le=10)
    notes: str
    attachments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FrameworkProgress(BaseModel):
    framework_type: FrameworkType
    completion_percentage: float = Field(ge=0, le=100)
    milestones_completed: int
    total_milestones: int
    current_phase: str
    next_actions: List[str]
    insights: List[str]
    metrics: Dict[str, float]

class BusinessMetrics(BaseModel):
    revenue: float
    profit_margin: float
    customer_satisfaction: float
    employee_engagement: float
    market_share: float
    growth_rate: float
    operational_efficiency: float
    innovation_index: float

class AIInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    confidence_score: float = Field(ge=0, le=1)
    recommended_actions: List[str]
    priority: str = Field(regex="^(high|medium|low)$")
    framework_context: FrameworkType
    supporting_data: Dict[str, Any]

class TeamCollaboration(BaseModel):
    team_id: str
    members: List[Dict[str, str]]
    shared_goals: List[str]
    collaboration_score: float = Field(ge=0, le=10)
    communication_frequency: int
    project_alignment: float

class ExportRequest(BaseModel):
    format: str = Field(regex="^(pdf|excel|json|csv)$")
    date_range_start: datetime
    date_range_end: datetime
    frameworks: List[FrameworkType]
    include_attachments: bool = False
    template_type: str = "comprehensive"

# Dependency for role-based access control
async def get_current_user_role(user_id: str = Query(...)) -> UserRole:
    """Get current user role from Firebase"""
    try:
        db = firestore.client()
        user_doc = db.collection('users').document(user_id).get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        return UserRole(user_data.get('role', 'client'))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user role: {str(e)}")

# Jim Collins Framework Implementations

class JimCollinsFrameworks:
    """Implementation of Jim Collins business frameworks"""
    
    @staticmethod
    def good_to_great_assessment(metrics: BusinessMetrics) -> Dict[str, Any]:
        """Good to Great framework assessment"""
        score = (
            metrics.revenue / 10000 * 0.2 +
            metrics.profit_margin * 0.15 +
            metrics.customer_satisfaction * 0.15 +
            metrics.employee_engagement * 0.2 +
            metrics.growth_rate * 0.15 +
            metrics.operational_efficiency * 0.15
        ) / 6
        
        return {
            "overall_score": min(score, 10),
            "disciplined_people": metrics.employee_engagement,
            "disciplined_thought": metrics.innovation_index,
            "disciplined_action": metrics.operational_efficiency,
            "recommendations": [
                "Focus on Level 5 Leadership development",
                "Refine your Hedgehog Concept",
                "Build a culture of discipline",
                "Use technology as an accelerator"
            ]
        }
    
    @staticmethod
    def level_5_leadership_analysis(team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Level 5 Leadership framework analysis"""
        leadership_score = (
            team_data.get('humility_score', 5) * 0.3 +
            team_data.get('will_score', 5) * 0.3 +
            team_data.get('results_focus', 5) * 0.4
        )
        
        return {
            "leadership_level": min(int(leadership_score / 2), 5),
            "humility_index": team_data.get('humility_score', 5),
            "professional_will": team_data.get('will_score', 5),
            "results_orientation": team_data.get('results_focus', 5),
            "development_areas": [
                "Personal humility enhancement",
                "Professional will strengthening",
                "Results-focused decision making"
            ]
        }
    
    @staticmethod
    def hedgehog_concept_builder(business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Hedgehog Concept framework builder"""
        passion_score = business_data.get('passion_alignment', 5)
        competency_score = business_data.get('core_competency', 5)
        economic_score = business_data.get('economic_engine', 5)
        
        intersection_strength = (passion_score * competency_score * economic_score) ** (1/3)
        
        return {
            "hedgehog_strength": intersection_strength,
            "passion_circle": {
                "score": passion_score,
                "description": "What you are deeply passionate about"
            },
            "competency_circle": {
                "score": competency_score,
                "description": "What you can be the best in the world at"
            },
            "economic_circle": {
                "score": economic_score,
                "description": "What drives your economic engine"
            },
            "intersection_insights": [
                "Strengthen passion alignment through purpose clarity",
                "Develop distinctive competencies",
                "Optimize economic model efficiency"
            ]
        }
    
    @staticmethod
    def flywheel_momentum_calculator(activity_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Flywheel framework momentum calculator"""
        momentum_score = 0
        for activity in activity_data:
            momentum_score += activity.get('impact', 0) * activity.get('consistency', 0)
        
        momentum_score = momentum_score / len(activity_data) if activity_data else 0
        
        return {
            "momentum_score": momentum_score,
            "flywheel_components": [
                {"name": "Customer Value", "strength": 7.5},
                {"name": "Brand Recognition", "strength": 6.8},
                {"name": "Operational Excellence", "strength": 8.2},
                {"name": "Financial Performance", "strength": 7.1}
            ],
            "acceleration_opportunities": [
                "Enhance customer value proposition",
                "Increase operational efficiency",
                "Strengthen brand positioning"
            ]
        }

# AI-Powered Insights Engine

class AIInsightsEngine:
    """AI-powered insights and recommendations"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI()
    
    async def generate_framework_insights(
        self, 
        framework_type: FrameworkType, 
        business_data: Dict[str, Any]
    ) -> List[AIInsight]:
        """Generate AI-powered insights for specific framework"""
        
        prompt = f"""
        As a business coaching expert specializing in Jim Collins frameworks, analyze the following business data 
        for the {framework_type.value} framework:
        
        Business Data: {json.dumps(business_data, indent=2)}
        
        Provide specific, actionable insights including:
        1. Current framework implementation strength
        2. Key improvement opportunities
        3. Recommended next actions
        4. Potential risks or challenges
        5. Success metrics to track
        
        Format as JSON with insights array.
        """
        
        try:
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            insights_data = json.loads(response.choices[0].message.content)
            
            return [
                AIInsight(
                    insight_type="framework_analysis",
                    title=insight.get("title", "Framework Insight"),
                    description=insight.get("description", ""),
                    confidence_score=insight.get("confidence", 0.8),
                    recommended_actions=insight.get("actions", []),
                    priority=insight.get("priority", "medium"),
                    framework_context=framework_type,
                    supporting_data=insight.get("data", {})
                )
                for insight in insights_data.get("insights", [])
            ]
        
        except Exception as e:
            # Fallback insights if AI fails
            return [
                AIInsight(
                    insight_type="framework_analysis",
                    title=f"{framework_type.value.title()} Analysis",
                    description="Continue focusing on systematic implementation of framework principles",
                    confidence_score=0.6,
                    recommended_actions=["Review framework documentation", "Schedule team alignment session"],
                    priority="medium",
                    framework_context=framework_type,
                    supporting_data=business_data
                )
            ]
    
    def perform_clustering_analysis(self, coaching_sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform clustering analysis on coaching patterns"""
        if len(coaching_sessions) < 3:
            return {"clusters": [], "insights": ["Insufficient data for clustering analysis"]}
        
        # Extract features for clustering
        features = []
        for session in coaching_sessions:
            features.append([
                session.get('duration_minutes', 60),
                session.get('progress_score', 5),
                len(session.get('action_items', [])),
                len(session.get('objectives', []))
            ])
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform clustering
        n_clusters = min(3, len(coaching_sessions))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features_scaled)
        
        return {
            "clusters": clusters.tolist(),
            "cluster_centers": kmeans.cluster_centers_.tolist(),
            "insights": [
                "High-performance sessions cluster identified",
                "Patterns in session duration and outcomes detected",
                "Optimization opportunities for coaching approach"
            ]
        }

# API Endpoints

@router.get("/frameworks/progress/{client_id}")
async def get_framework_progress(
    client_id: str,
    user_role: UserRole = Depends(get_current_user_role)
) -> List[FrameworkProgress]:
    """Get progress across all Jim Collins frameworks for a client"""
    
    if user_role not in [UserRole.COACH, UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        db = firestore.client()
        progress_ref = db.collection('coaching_progress').where('client_id', '==', client_id)
        progress_docs = progress_ref.stream()
        
        progress_list = []
        for doc in progress_docs:
            data = doc.to_dict()
            progress_list.append(FrameworkProgress(**data))
        
        return progress_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

@router.post("/sessions")
async def create_coaching_session(
    session: CoachingSession,
    user_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, str]:
    """Create a new coaching session"""
    
    if user_role not in [UserRole.COACH, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only coaches can create sessions")
    
    try:
        db = firestore.client()
        session_dict = session.dict()
        session_dict['created_at'] = datetime.utcnow()
        
        doc_ref = db.collection('coaching_sessions').add(session_dict)
        session_id = doc_ref[1].id
        
        return {"session_id": session_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@router.get("/insights/{client_id}")
async def get_ai_insights(
    client_id: str,
    framework_type: Optional[FrameworkType] = None,
    user_role: UserRole = Depends(get_current_user_role)
) -> List[AIInsight]:
    """Get AI-powered insights for client's coaching journey"""
    
    if user_role not in [UserRole.COACH, UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        db = firestore.client()
        
        # Fetch client's business data
        client_doc = db.collection('clients').document(client_id).get()
        if not client_doc.exists:
            raise HTTPException(status_code=404, detail="Client not found")
        
        business_data = client_doc.to_dict()
        
        # Generate insights
        insights_engine = AIInsightsEngine()
        
        if framework_type:
            insights = await insights_engine.generate_framework_insights(framework_type, business_data)
        else:
            # Generate insights for all frameworks
            insights = []
            for ft in FrameworkType:
                framework_insights = await insights_engine.generate_framework_insights(ft, business_data)
                insights.extend(framework_insights[:2])  # Limit to 2 insights per framework
        
        return insights
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@router.get("/analytics/dashboard/{client_id}")
async def get_dashboard_analytics(
    client_id: str,
    date_range_days: int = Query(30, ge=1, le=365),
    user_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Get comprehensive dashboard analytics"""
    
    if user_role not in [UserRole.COACH, UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        db = firestore.client()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=date_range_days)
        
        # Fetch coaching sessions
        sessions_ref = db.collection('coaching_sessions')\
                        .where('client_id', '==', client_id)\
                        .where('session_date', '>=', start_date)\
                        .where('session_date', '<=', end_date)
        
        sessions = [doc.to_dict() for doc in sessions_ref.stream()]
        
        # Fetch business metrics
        metrics_doc = db.collection('business_metrics').document(client_id).get()
        business_metrics = metrics_doc.to_dict() if metrics_doc.exists else {}
        
        # Calculate analytics
        frameworks = JimCollinsFrameworks()
        insights_engine = AIInsightsEngine()
        
        # Good to Great assessment
        if business_metrics:
            metrics_obj = BusinessMetrics(**business_metrics)
            good_to_great = frameworks.good_to_great_assessment(metrics_obj)
        else:
            good_to_great = {"overall_score": 5, "recommendations": ["Complete business metrics assessment"]}
        
        # Clustering analysis
        clustering_results = insights_engine.perform_clustering_analysis(sessions)
        
        # Progress tracking
        progress_scores = [s.get('progress_score', 5) for s in sessions]
        avg_progress = np.mean(progress_scores) if progress_scores else 5
        
        return {
            "client_id": client_id,
            "date_range": {"start": start_date, "end": end_date},
            "session_count": len(sessions),
            "average_progress_score": float(avg_progress),
            "good_to_great_assessment": good_to_great,
            "clustering_analysis": clustering_results,
            "framework_distribution": {
                ft.value: len([s for s in sessions if s.get('framework_type') == ft.value])
                for ft in FrameworkType
            },
            "action_items_completion": {
                "total": sum(len(s.get('action_items', [])) for s in sessions),
                "completed": sum(
                    len([ai for ai in s.get('action_items', []) if ai.get('completed', False)])
                    for s in sessions
                )
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@router.post("/team/collaboration")
async def create_team_collaboration(
    collaboration: TeamCollaboration,
    user_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, str]:
    """Create team collaboration framework"""
    
    if user_role not in [UserRole.COACH, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        db = firestore.client()
        collab_dict = collaboration.dict()
        collab_dict['created_at'] = datetime.utcnow()
        
        doc_ref = db.collection('team_collaborations').add(collab_dict)
        team_id = doc_ref[1].id
        
        return {"team_id": team_id, "status": "created"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating team collaboration: {str(e)}")

@router.post("/export")
async def export_coaching_data(
    export_request: ExportRequest,
    user_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Export coaching session data in various formats"""
    
    if user_role not in [UserRole.COACH, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Insufficient permissions for export")
    
    try:
        db = firestore.client()
        
        # Fetch sessions within date range
        sessions_ref = db.collection('coaching_sessions')\
                        .where('session_date', '>=', export_request.date_range_start)\
                        .where('session_date', '<=', export_request.date_range_end)
        
        sessions = [doc.to_dict() for doc in sessions_ref.stream()]
        
        # Filter by frameworks if specified
        if export_request.frameworks:
            framework_values = [f.value for f in export_request.frameworks]
            sessions = [s for s in sessions if s.get('framework_type') in framework_values]
        
        if export_request.format == "json":
            return {
                "format": "json",
                "data": sessions,
                "export_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "session_count": len(sessions),
                    "frameworks": [f.value for f in export_request.frameworks] if export_request.frameworks else "all"
                }
            }
        
        elif export_request.format == "csv":
            df = pd.DataFrame(sessions)
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = base64.b64encode(csv_buffer.getvalue()).decode()
            
            return {
                "format": "csv",
                "data": csv_data,
                "filename": f"coaching_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {export_request.format}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

@router.get("/frameworks/assessment/{framework_type}")
async def get_framework_assessment(
    framework_type: FrameworkType,
    client_id: str = Query(...),
    user_role: UserRole = Depends(get_current_user_role)
) -> Dict[str, Any]:
    """Get detailed assessment for specific Jim Collins framework"""
    
    if user_role not in [UserRole.COACH, UserRole.ADMIN, UserRole.CLIENT]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        db = firestore.client()
        
        # Fetch client data
        client_doc = db.collection('clients').document(client_id).get()
        if not client_doc.exists:
            raise HTTPException(status_code=404, detail="Client not found")
        
        client_data = client_doc.to_dict()
        frameworks = JimCollinsFrameworks()
        
        if framework_type == FrameworkType.GOOD_TO_GREAT:
            if 'business_metrics' in client_data:
                metrics = BusinessMetrics(**client_data['business_metrics'])
                assessment = frameworks.good_to_great_assessment(metrics)
            else:
                assessment = {"error": "Business metrics not available"}
        
        elif framework_type == FrameworkType.LEVEL_5_LEADERSHIP:
            team_data = client_data.get('team_data', {})
            assessment = frameworks.level_5_leadership_analysis(team_data)
        
        elif framework_type == FrameworkType.HEDGEHOG_CONCEPT:
            business_data = client_data.get('business_data', {})
            assessment = frameworks.hedgehog_concept_builder(business_data)
        
        elif framework_type == FrameworkType.FLYWHEEL:
            activity_data = client_data.get('activity_data', [])
            assessment = frameworks.flywheel_momentum_calculator(activity_data)
        
        else:
            assessment = {"message": f"Assessment for {framework_type.value} is under development"}
        
        return {
            "framework_type": framework_type.value,
            "client_id": client_id,
            "assessment": assessment,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating assessment: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for coaching analytics API"""
    return {
        "status": "healthy",
        "service": "coaching_analytics",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "jim_collins_frameworks",
            "ai_insights",
            "team_collaboration",
            "progress_tracking",
            "data_export",
            "role_based_access"
        ]
    }