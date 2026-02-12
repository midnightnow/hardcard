from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum
import math

router = APIRouter(prefix="/coaching/hedgehog", tags=["Hedgehog Concept"])

class AssessmentType(str, Enum):
    PERSONAL = "personal"
    ORGANIZATIONAL = "organizational"

class CircleData(BaseModel):
    score: int = Field(ge=0, le=10, description="Score from 0-10")
    items: List[str] = Field(default_factory=list, description="Key items for this circle")
    notes: str = Field(default="", description="Additional notes and insights")

class IntersectionData(BaseModel):
    score: int = Field(ge=0, le=10, description="Intersection score")
    concept: str = Field(default="", description="Hedgehog concept statement")
    confidence: int = Field(ge=0, le=100, description="Confidence percentage")

class HedgehogAssessmentRequest(BaseModel):
    name: str = Field(..., description="Assessment name")
    type: AssessmentType = Field(..., description="Assessment type")
    passion: CircleData = Field(..., description="Passion circle data")
    genetic: CircleData = Field(..., description="Genetic encoding circle data")
    economic: CircleData = Field(..., description="Economic engine circle data")
    intersection: IntersectionData = Field(..., description="Intersection analysis")
    userId: Optional[str] = None
    organizationId: Optional[str] = None

class HedgehogAssessmentResponse(BaseModel):
    id: str
    name: str
    type: AssessmentType
    passion: CircleData
    genetic: CircleData
    economic: CircleData
    intersection: IntersectionData
    userId: Optional[str]
    organizationId: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    analysis: Dict[str, Any]

class HedgehogAnalysis(BaseModel):
    strengths: List[str]
    development_areas: List[str]
    recommendations: List[str]
    concept_maturity: str
    balance_score: float
    alignment_metrics: Dict[str, float]

# In-memory storage (replace with database in production)
assessments_db: Dict[str, HedgehogAssessmentResponse] = {}

def calculate_hedgehog_analysis(assessment: HedgehogAssessmentRequest) -> HedgehogAnalysis:
    """Calculate comprehensive analysis of the Hedgehog assessment"""
    
    passion_score = assessment.passion.score
    genetic_score = assessment.genetic.score
    economic_score = assessment.economic.score
    
    # Calculate balance score (how evenly developed the three circles are)
    scores = [passion_score, genetic_score, economic_score]
    mean_score = sum(scores) / len(scores)
    variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
    balance_score = max(0, 1 - (variance / 25))  # Normalize to 0-1 scale
    
    # Determine concept maturity
    min_score = min(scores)
    avg_score = mean_score
    
    if min_score >= 8 and avg_score >= 8.5:
        concept_maturity = "Highly Developed"
    elif min_score >= 6 and avg_score >= 7:
        concept_maturity = "Well Developed"
    elif min_score >= 4 and avg_score >= 5:
        concept_maturity = "Developing"
    else:
        concept_maturity = "Early Stage"
    
    # Identify strengths
    strengths = []
    if passion_score >= 8:
        strengths.append("Strong passion clarity and engagement")
    if genetic_score >= 8:
        strengths.append("Clear genetic advantages and natural talents")
    if economic_score >= 8:
        strengths.append("Robust economic engine and value creation")
    if balance_score >= 0.8:
        strengths.append("Well-balanced development across all three circles")
    if assessment.intersection.confidence >= 80:
        strengths.append("High confidence in concept articulation")
    
    # Identify development areas
    development_areas = []
    if passion_score < 6:
        development_areas.append("Need deeper exploration of core passions and motivations")
    if genetic_score < 6:
        development_areas.append("Require clearer identification of unique genetic advantages")
    if economic_score < 6:
        development_areas.append("Economic model needs strengthening and validation")
    if balance_score < 0.5:
        development_areas.append("Uneven development - focus on weaker circles")
    if assessment.intersection.confidence < 50:
        development_areas.append("Low confidence suggests need for deeper self-reflection")
    
    # Generate recommendations
    recommendations = []
    
    if concept_maturity == "Early Stage":
        recommendations.extend([
            "Focus on one circle at a time rather than trying to develop all simultaneously",
            "Conduct deep self-reflection exercises for passion discovery",
            "Seek feedback from colleagues on genetic advantages"
        ])
    elif concept_maturity == "Developing":
        recommendations.extend([
            "Begin looking for intersection patterns between your stronger circles",
            "Test economic assumptions with small experiments",
            "Refine weaker areas through targeted development"
        ])
    elif concept_maturity == "Well Developed":
        recommendations.extend([
            "Start aligning daily activities with your Hedgehog Concept",
            "Eliminate activities that don't fit within your three circles",
            "Share concept with trusted advisors for validation"
        ])
    else:  # Highly Developed
        recommendations.extend([
            "Execute ruthlessly on your clear Hedgehog Concept",
            "Help others discover their own Hedgehog Concepts",
            "Measure and optimize based on concept alignment"
        ])
    
    # Add specific recommendations based on weakest area
    weakest_circle = min(
        [("passion", passion_score), ("genetic", genetic_score), ("economic", economic_score)],
        key=lambda x: x[1]
    )
    
    if weakest_circle[0] == "passion":
        recommendations.append("Schedule dedicated time for passion exploration activities")
    elif weakest_circle[0] == "genetic":
        recommendations.append("Conduct a skills inventory and seek 360-degree feedback")
    else:  # economic
        recommendations.append("Analyze successful business models in your domain")
    
    # Calculate alignment metrics
    alignment_metrics = {
        "passion_genetic_alignment": min(passion_score, genetic_score) / 10,
        "passion_economic_alignment": min(passion_score, economic_score) / 10,
        "genetic_economic_alignment": min(genetic_score, economic_score) / 10,
        "overall_alignment": min_score / 10,
        "development_consistency": balance_score,
        "concept_readiness": (min_score * balance_score * (assessment.intersection.confidence / 100))
    }
    
    return HedgehogAnalysis(
        strengths=strengths,
        development_areas=development_areas,
        recommendations=recommendations,
        concept_maturity=concept_maturity,
        balance_score=balance_score,
        alignment_metrics=alignment_metrics
    )

def calculate_intersection_score(passion: int, genetic: int, economic: int) -> tuple[int, int]:
    """Calculate intersection score and confidence"""
    # Intersection score is the minimum of the three circles (bottleneck theory)
    intersection_score = min(passion, genetic, economic)
    
    # Confidence is based on how well-developed all circles are
    total_score = passion + genetic + economic
    balance = 1 - (max(passion, genetic, economic) - min(passion, genetic, economic)) / 10
    confidence = int((total_score / 30) * balance * 100)
    
    return intersection_score, confidence

def generate_concept_suggestions(assessment: HedgehogAssessmentRequest) -> List[str]:
    """Generate Hedgehog concept suggestions based on the assessment"""
    suggestions = []
    
    # Extract key themes from items
    all_items = (
        assessment.passion.items + 
        assessment.genetic.items + 
        assessment.economic.items
    )
    
    if len(all_items) >= 3:
        suggestions.append(
            f"Consider how your passion for {', '.join(assessment.passion.items[:2])} "
            f"combined with your genetic advantage in {', '.join(assessment.genetic.items[:2])} "
            f"can drive {', '.join(assessment.economic.items[:2])}"
        )
    
    # Add suggestions based on scores
    if min(assessment.passion.score, assessment.genetic.score, assessment.economic.score) >= 7:
        suggestions.append(
            "You have strong development in all three areas - focus on articulating "
            "the unique intersection that only you can occupy"
        )
    
    return suggestions

@router.post("/", response_model=HedgehogAssessmentResponse)
async def create_assessment(assessment: HedgehogAssessmentRequest):
    """Create a new Hedgehog Concept assessment"""
    
    # Auto-calculate intersection if not provided or seems inconsistent
    calculated_score, calculated_confidence = calculate_intersection_score(
        assessment.passion.score,
        assessment.genetic.score,
        assessment.economic.score
    )
    
    # Update intersection if it seems off
    if assessment.intersection.score == 0 or abs(assessment.intersection.score - calculated_score) > 2:
        assessment.intersection.score = calculated_score
    
    if assessment.intersection.confidence == 0 or abs(assessment.intersection.confidence - calculated_confidence) > 20:
        assessment.intersection.confidence = calculated_confidence
    
    # Generate analysis
    analysis = calculate_hedgehog_analysis(assessment)
    
    # Create response object
    assessment_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    response = HedgehogAssessmentResponse(
        id=assessment_id,
        name=assessment.name,
        type=assessment.type,
        passion=assessment.passion,
        genetic=assessment.genetic,
        economic=assessment.economic,
        intersection=assessment.intersection,
        userId=assessment.userId,
        organizationId=assessment.organizationId,
        createdAt=now,
        updatedAt=now,
        analysis=analysis.dict()
    )
    
    # Store in database (replace with actual DB in production)
    assessments_db[assessment_id] = response
    
    return response

@router.get("/", response_model=List[HedgehogAssessmentResponse])
async def get_assessments(
    userId: Optional[str] = Query(None),
    organizationId: Optional[str] = Query(None),
    type: Optional[AssessmentType] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """Get Hedgehog assessments with optional filtering"""
    
    filtered_assessments = []
    
    for assessment in assessments_db.values():
        # Apply filters
        if userId and assessment.userId != userId:
            continue
        if organizationId and assessment.organizationId != organizationId:
            continue
        if type and assessment.type != type:
            continue
            
        filtered_assessments.append(assessment)
    
    # Sort by creation date (newest first) and limit
    filtered_assessments.sort(key=lambda x: x.createdAt, reverse=True)
    return filtered_assessments[:limit]

@router.get("/{assessment_id}", response_model=HedgehogAssessmentResponse)
async def get_assessment(assessment_id: str):
    """Get a specific Hedgehog assessment by ID"""
    
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessments_db[assessment_id]

@router.put("/{assessment_id}", response_model=HedgehogAssessmentResponse)
async def update_assessment(assessment_id: str, assessment: HedgehogAssessmentRequest):
    """Update an existing Hedgehog assessment"""
    
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    existing = assessments_db[assessment_id]
    
    # Auto-calculate intersection
    calculated_score, calculated_confidence = calculate_intersection_score(
        assessment.passion.score,
        assessment.genetic.score,
        assessment.economic.score
    )
    
    assessment.intersection.score = calculated_score
    assessment.intersection.confidence = calculated_confidence
    
    # Generate new analysis
    analysis = calculate_hedgehog_analysis(assessment)
    
    # Update response object
    updated = HedgehogAssessmentResponse(
        id=assessment_id,
        name=assessment.name,
        type=assessment.type,
        passion=assessment.passion,
        genetic=assessment.genetic,
        economic=assessment.economic,
        intersection=assessment.intersection,
        userId=assessment.userId,
        organizationId=assessment.organizationId,
        createdAt=existing.createdAt,
        updatedAt=datetime.utcnow(),
        analysis=analysis.dict()
    )
    
    assessments_db[assessment_id] = updated
    return updated

@router.delete("/{assessment_id}")
async def delete_assessment(assessment_id: str):
    """Delete a Hedgehog assessment"""
    
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    del assessments_db[assessment_id]
    return {"message": "Assessment deleted successfully"}

@router.get("/{assessment_id}/analysis", response_model=HedgehogAnalysis)
async def get_assessment_analysis(assessment_id: str):
    """Get detailed analysis for a specific assessment"""
    
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment = assessments_db[assessment_id]
    return HedgehogAnalysis(**assessment.analysis)

@router.post("/calculate-intersection")
async def calculate_intersection(
    passion_score: int = Field(..., ge=0, le=10),
    genetic_score: int = Field(..., ge=0, le=10),
    economic_score: int = Field(..., ge=0, le=10)
):
    """Calculate intersection score and confidence for given circle scores"""
    
    score, confidence = calculate_intersection_score(passion_score, genetic_score, economic_score)
    
    return {
        "intersection_score": score,
        "confidence": confidence,
        "balance_score": 1 - (max(passion_score, genetic_score, economic_score) - min(passion_score, genetic_score, economic_score)) / 10,
        "total_potential": (passion_score + genetic_score + economic_score) / 30
    }

@router.get("/templates/questions")
async def get_assessment_questions():
    """Get template questions for each circle of the Hedgehog Concept"""
    
    return {
        "passion": [
            "What activities make you lose track of time?",
            "What would you do even if you weren't paid for it?",
            "What topics do you find yourself constantly reading about?",
            "What conversations energize you the most?",
            "What legacy do you want to leave behind?",
            "What problems do you feel compelled to solve?",
            "What achievements have given you the deepest satisfaction?",
            "When do you feel most authentic and alive?"
        ],
        "genetic": [
            "What comes naturally to you that others struggle with?",
            "What patterns do you see that others miss?",
            "What unique combination of skills do you possess?",
            "What do colleagues consistently ask for your help with?",
            "What achievements required minimal effort from you?",
            "What feedback do you consistently receive about your strengths?",
            "What activities energize rather than drain you?",
            "In what areas do you consistently outperform expectations?"
        ],
        "economic": [
            "What activities generate the most value per hour?",
            "What offerings have the highest profit margins?",
            "What drives sustainable revenue growth?",
            "What metrics correlate most with business success?",
            "What customer segments pay premium prices?",
            "What creates defensible competitive advantages?",
            "What business models scale most effectively?",
            "What value propositions resonate strongest with markets?"
        ]
    }

@router.get("/reports/summary")
async def get_assessment_summary(
    userId: Optional[str] = Query(None),
    organizationId: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365)
):
    """Get summary report of assessments over time"""
    
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Filter assessments
    filtered_assessments = []
    for assessment in assessments_db.values():
        if assessment.createdAt < cutoff_date:
            continue
        if userId and assessment.userId != userId:
            continue
        if organizationId and assessment.organizationId != organizationId:
            continue
        filtered_assessments.append(assessment)
    
    if not filtered_assessments:
        return {
            "total_assessments": 0,
            "average_scores": {"passion": 0, "genetic": 0, "economic": 0, "intersection": 0},
            "concept_maturity_distribution": {},
            "recent_trends": []
        }
    
    # Calculate averages
    total_passion = sum(a.passion.score for a in filtered_assessments)
    total_genetic = sum(a.genetic.score for a in filtered_assessments)
    total_economic = sum(a.economic.score for a in filtered_assessments)
    total_intersection = sum(a.intersection.score for a in filtered_assessments)
    count = len(filtered_assessments)
    
    # Concept maturity distribution
    maturity_counts = {}
    for assessment in filtered_assessments:
        maturity = assessment.analysis.get("concept_maturity", "Unknown")
        maturity_counts[maturity] = maturity_counts.get(maturity, 0) + 1
    
    return {
        "total_assessments": count,
        "average_scores": {
            "passion": round(total_passion / count, 1),
            "genetic": round(total_genetic / count, 1),
            "economic": round(total_economic / count, 1),
            "intersection": round(total_intersection / count, 1)
        },
        "concept_maturity_distribution": maturity_counts,
        "recent_trends": [
            f"Most recent assessment: {filtered_assessments[0].name}" if filtered_assessments else "",
            f"Strongest circle on average: {max(['passion', 'genetic', 'economic'], key=lambda x: {'passion': total_passion, 'genetic': total_genetic, 'economic': total_economic}[x])}"
        ]
    }