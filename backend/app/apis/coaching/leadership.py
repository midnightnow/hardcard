"""
Level 5 Leadership Assessment API
Implementation of Jim Collins' Level 5 Leadership Framework

Features:
- Humility vs Will matrix assessment
- Window/Mirror attribution tracking  
- Communication pattern analysis (I vs We usage)
- Succession planning readiness score
- 360-degree feedback integration
- Automated text analysis for leadership communications
- Team performance metrics integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import re
import statistics
import asyncio
from collections import Counter, defaultdict
import json
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade
from textblob import TextBlob
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

router = APIRouter(prefix="/coaching/leadership", tags=["Leadership Assessment"])

# =============================================================================
# MODELS & ENUMS
# =============================================================================

class LeadershipLevel(Enum):
    LEVEL_1 = "Level 1: Highly Capable Individual"
    LEVEL_2 = "Level 2: Contributing Team Member"
    LEVEL_3 = "Level 3: Competent Manager"
    LEVEL_4 = "Level 4: Effective Leader"
    LEVEL_5 = "Level 5: Executive"

class AttributionType(Enum):
    WINDOW = "window"  # Looking out (blaming external factors)
    MIRROR = "mirror"  # Looking in (taking responsibility)

class CommunicationType(Enum):
    I_FOCUSED = "i_focused"   # Self-centered communication
    WE_FOCUSED = "we_focused" # Team-centered communication
    THEY_FOCUSED = "they_focused" # Other-focused communication

class FeedbackCategory(Enum):
    HUMILITY = "humility"
    WILL = "will"
    COMMUNICATION = "communication"
    SUCCESSION = "succession"
    TEAM_BUILDING = "team_building"
    RESULTS_FOCUS = "results_focus"

class AssessmentRequest(BaseModel):
    user_id: str
    assessment_type: str = "comprehensive"
    include_360_feedback: bool = True
    include_text_analysis: bool = True
    communication_samples: Optional[List[str]] = []
    
class HumilityWillMatrix(BaseModel):
    humility_score: float = Field(..., ge=0, le=10, description="Humility score (0-10)")
    will_score: float = Field(..., ge=0, le=10, description="Professional will score (0-10)")
    matrix_quadrant: str = Field(..., description="Matrix position")
    level_5_potential: float = Field(..., ge=0, le=1, description="Level 5 leadership potential")

class AttributionPattern(BaseModel):
    window_instances: int = 0
    mirror_instances: int = 0
    attribution_ratio: float = Field(..., description="Mirror/(Window+Mirror) ratio")
    recent_trend: str = Field(..., description="Recent attribution trend")
    examples: List[Dict[str, Any]] = []

class AdvancedTextAnalysis(BaseModel):
    readability_score: float = 0.0
    complexity_grade: float = 0.0
    sentiment_polarity: float = 0.0  # -1 to 1
    sentiment_subjectivity: float = 0.0  # 0 to 1
    empathy_indicators: int = 0
    authority_indicators: int = 0
    inclusive_language_score: float = 0.0
    future_orientation_score: float = 0.0

class CommunicationAnalysis(BaseModel):
    i_usage_count: int = 0
    we_usage_count: int = 0
    they_usage_count: int = 0
    total_words: int = 0
    we_to_i_ratio: float = 0.0
    communication_style: str = ""
    leadership_language_score: float = 0.0
    advanced_analysis: AdvancedTextAnalysis = Field(default_factory=AdvancedTextAnalysis)
    emotional_intelligence_score: float = 0.0
    clarity_score: float = 0.0
    influence_patterns: List[str] = []

class SuccessionPlanningScore(BaseModel):
    mentoring_activity: float = Field(..., ge=0, le=10)
    knowledge_transfer: float = Field(..., ge=0, le=10)
    team_development: float = Field(..., ge=0, le=10)
    succession_readiness: float = Field(..., ge=0, le=10)
    bench_strength: float = Field(..., ge=0, le=10)
    overall_score: float = Field(..., ge=0, le=10)

class Feedback360Item(BaseModel):
    feedback_id: str
    from_user_id: str
    from_role: str  # "subordinate", "peer", "superior", "self"
    category: FeedbackCategory
    rating: float = Field(..., ge=1, le=10)
    comments: Optional[str] = ""
    timestamp: datetime
    is_anonymous: bool = True
    behavioral_examples: List[str] = []
    improvement_suggestions: List[str] = []
    strengths_noted: List[str] = []

class Feedback360Analytics(BaseModel):
    total_responses: int = 0
    response_rate: float = 0.0
    average_rating: float = 0.0
    rating_distribution: Dict[str, int] = {}
    sentiment_analysis: Dict[str, float] = {}
    key_themes: List[str] = []
    improvement_priorities: List[str] = []
    strength_areas: List[str] = []
    consistency_score: float = 0.0  # How consistent feedback is across roles

class TeamPerformanceCorrelation(BaseModel):
    leadership_score: float
    team_engagement: float
    retention_rate: float
    productivity_index: float
    correlation_strength: float
    performance_trend: str
    team_feedback_alignment: float

class TeamPerformanceMetrics(BaseModel):
    team_engagement_score: float = 0.0
    retention_rate: float = 0.0
    productivity_trend: float = 0.0
    collaboration_index: float = 0.0
    innovation_metrics: float = 0.0
    goal_achievement_rate: float = 0.0

class LeadershipAssessmentResult(BaseModel):
    assessment_id: str
    user_id: str
    timestamp: datetime
    leadership_level: LeadershipLevel
    humility_will_matrix: HumilityWillMatrix
    attribution_pattern: AttributionPattern
    communication_analysis: CommunicationAnalysis
    succession_planning: SuccessionPlanningScore
    feedback_360_summary: Dict[str, Any]
    team_performance: TeamPerformanceMetrics
    overall_score: float
    recommendations: List[str]
    development_plan: List[Dict[str, Any]]
    next_assessment_date: datetime

class LeadershipDevelopmentPlan(BaseModel):
    plan_id: str
    user_id: str
    current_level: LeadershipLevel
    target_level: LeadershipLevel
    development_areas: List[str]
    action_items: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    resources: List[Dict[str, Any]]
    timeline_weeks: int
    coach_assigned: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# =============================================================================
# CORE ASSESSMENT ENGINE
# =============================================================================

class Level5AssessmentEngine:
    """Core engine for Level 5 Leadership Assessment with Advanced Text Analysis"""
    
    def __init__(self):
        # Load NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model 'en_core_web_sm' not found. Some advanced features may not work.")
            self.nlp = None
        
        # Leadership language indicators
        self.humility_indicators = [
            "mistake", "learn", "wrong", "help", "team", "together", "we", 
            "grateful", "humble", "listen", "feedback", "improve", "grow",
            "thank", "appreciate", "honor", "privilege", "fortunate", "blessed"
        ]
        
        self.will_indicators = [
            "achieve", "results", "deliver", "execute", "commit", "drive",
            "push", "standard", "excellence", "performance", "success",
            "relentless", "unstoppable", "determined", "focused", "rigorous"
        ]
        
        self.empathy_indicators = [
            "understand", "feel", "empathize", "support", "care", "concern",
            "perspective", "experience", "struggle", "challenge", "difficulty"
        ]
        
        self.authority_indicators = [
            "decide", "determine", "direct", "command", "instruct", "require",
            "mandate", "order", "must", "will", "expect", "demand"
        ]
        
        self.inclusive_language = [
            "everyone", "all", "together", "collectively", "inclusive", "diverse",
            "belong", "welcome", "include", "embrace", "value", "respect"
        ]
        
        self.future_orientation = [
            "vision", "future", "tomorrow", "ahead", "forward", "next", "coming",
            "will", "plan", "strategy", "goal", "objective", "aspire", "dream"
        ]
        
        # Attribution patterns (enhanced)
        self.window_patterns = [
            r"\b(because of|due to|blamed|market|economy|competition|luck)\b",
            r"\b(external|outside|beyond our control|circumstances)\b",
            r"\b(they didn't|they failed|they couldn't|their fault)\b",
            r"\b(market conditions|economic climate|unforeseen|unexpected)\b"
        ]
        
        self.mirror_patterns = [
            r"\b(I should have|we should have|my mistake|our fault)\b",
            r"\b(I failed|we failed|I didn't|we didn't)\b",
            r"\b(my responsibility|our responsibility|accountable)\b",
            r"\b(I take|we take|taking responsibility|owning this)\b"
        ]
        
        # Influence patterns
        self.influence_patterns = {
            "inspirational": [r"\b(inspire|motivate|energize|passionate|vision)\b"],
            "rational": [r"\b(data|evidence|analysis|logic|reason|facts)\b"],
            "consultative": [r"\b(discuss|explore|consider|thoughts|ideas|input)\b"],
            "directive": [r"\b(need|must|should|require|expect|direct)\b"]
        }

    async def assess_humility_will_matrix(self, 
                                        communication_samples: List[str],
                                        feedback_360: List[Feedback360Item]) -> HumilityWillMatrix:
        """Assess leader's position on Humility vs Will matrix"""
        
        # Analyze communication for humility indicators
        humility_score = await self._calculate_humility_score(
            communication_samples, feedback_360
        )
        
        # Analyze for professional will indicators
        will_score = await self._calculate_will_score(
            communication_samples, feedback_360
        )
        
        # Determine matrix quadrant
        matrix_quadrant = self._determine_matrix_quadrant(humility_score, will_score)
        
        # Calculate Level 5 potential
        level_5_potential = self._calculate_level_5_potential(humility_score, will_score)
        
        return HumilityWillMatrix(
            humility_score=humility_score,
            will_score=will_score,
            matrix_quadrant=matrix_quadrant,
            level_5_potential=level_5_potential
        )

    async def _calculate_humility_score(self, 
                                      communication_samples: List[str],
                                      feedback_360: List[Feedback360Item]) -> float:
        """Calculate humility score from multiple sources"""
        
        # Text analysis score (0-5)
        text_score = 0.0
        if communication_samples:
            total_words = sum(len(sample.split()) for sample in communication_samples)
            humility_words = 0
            
            for sample in communication_samples:
                words = sample.lower().split()
                humility_words += sum(1 for word in words if word in self.humility_indicators)
            
            if total_words > 0:
                text_score = min(5.0, (humility_words / total_words) * 100)
        
        # 360 feedback score (0-5)
        feedback_score = 0.0
        humility_feedback = [f for f in feedback_360 if f.category == FeedbackCategory.HUMILITY]
        if humility_feedback:
            feedback_score = statistics.mean([f.rating for f in humility_feedback]) / 2
        
        return min(10.0, text_score + feedback_score)

    async def _calculate_will_score(self, 
                                  communication_samples: List[str],
                                  feedback_360: List[Feedback360Item]) -> float:
        """Calculate professional will score"""
        
        # Text analysis score (0-5)
        text_score = 0.0
        if communication_samples:
            total_words = sum(len(sample.split()) for sample in communication_samples)
            will_words = 0
            
            for sample in communication_samples:
                words = sample.lower().split()
                will_words += sum(1 for word in words if word in self.will_indicators)
            
            if total_words > 0:
                text_score = min(5.0, (will_words / total_words) * 100)
        
        # 360 feedback score (0-5)
        feedback_score = 0.0
        will_feedback = [f for f in feedback_360 if f.category == FeedbackCategory.WILL]
        if will_feedback:
            feedback_score = statistics.mean([f.rating for f in will_feedback]) / 2
        
        return min(10.0, text_score + feedback_score)

    def _determine_matrix_quadrant(self, humility_score: float, will_score: float) -> str:
        """Determine position in Humility vs Will matrix"""
        
        if humility_score >= 7 and will_score >= 7:
            return "Level 5 Executive (High Humility, High Will)"
        elif humility_score >= 7 and will_score < 7:
            return "Modest Manager (High Humility, Low Will)"
        elif humility_score < 7 and will_score >= 7:
            return "Ferocious Professional (Low Humility, High Will)"
        else:
            return "Ineffective Leader (Low Humility, Low Will)"

    def _calculate_level_5_potential(self, humility_score: float, will_score: float) -> float:
        """Calculate Level 5 leadership potential (0-1)"""
        
        # Level 5 requires both high humility and high will
        if humility_score >= 7 and will_score >= 7:
            # Perfect balance at 8.5/8.5 gives maximum potential
            humility_factor = min(1.0, humility_score / 8.5)
            will_factor = min(1.0, will_score / 8.5)
            return (humility_factor + will_factor) / 2
        else:
            # Penalize imbalance
            return max(0.0, (humility_score + will_score) / 20 - 0.3)

    async def analyze_attribution_patterns(self, 
                                         communication_samples: List[str],
                                         historical_statements: List[Dict[str, Any]]) -> AttributionPattern:
        """Analyze Window vs Mirror attribution patterns"""
        
        window_instances = 0
        mirror_instances = 0
        examples = []
        
        all_text = communication_samples + [stmt.get('text', '') for stmt in historical_statements]
        
        for text in all_text:
            # Check for window (external attribution) patterns
            for pattern in self.window_patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    window_instances += len(matches)
                    examples.append({
                        "type": "window",
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "pattern": pattern
                    })
            
            # Check for mirror (internal attribution) patterns
            for pattern in self.mirror_patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    mirror_instances += len(matches)
                    examples.append({
                        "type": "mirror", 
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "pattern": pattern
                    })
        
        total_attributions = window_instances + mirror_instances
        attribution_ratio = mirror_instances / total_attributions if total_attributions > 0 else 0.5
        
        # Determine trend
        recent_trend = "improving" if attribution_ratio > 0.6 else "declining" if attribution_ratio < 0.4 else "stable"
        
        return AttributionPattern(
            window_instances=window_instances,
            mirror_instances=mirror_instances,
            attribution_ratio=attribution_ratio,
            recent_trend=recent_trend,
            examples=examples[:10]  # Limit examples
        )

    async def perform_advanced_text_analysis(self, 
                                        communication_samples: List[str]) -> AdvancedTextAnalysis:
        """Perform advanced NLP analysis on communication samples"""
        
        if not communication_samples:
            return AdvancedTextAnalysis()
        
        combined_text = " ".join(communication_samples)
        
        # Readability analysis
        readability_score = flesch_reading_ease(combined_text)
        complexity_grade = flesch_kincaid_grade(combined_text)
        
        # Sentiment analysis
        blob = TextBlob(combined_text)
        sentiment_polarity = blob.sentiment.polarity
        sentiment_subjectivity = blob.sentiment.subjectivity
        
        # Count various indicators
        words = combined_text.lower().split()
        empathy_count = sum(1 for word in words if word in self.empathy_indicators)
        authority_count = sum(1 for word in words if word in self.authority_indicators)
        inclusive_count = sum(1 for word in words if word in self.inclusive_language)
        future_count = sum(1 for word in words if word in self.future_orientation)
        
        total_words = len(words)
        
        # Calculate scores (0-10 scale)
        inclusive_language_score = min(10.0, (inclusive_count / max(total_words, 1)) * 1000)
        future_orientation_score = min(10.0, (future_count / max(total_words, 1)) * 1000)
        
        return AdvancedTextAnalysis(
            readability_score=min(100.0, max(0.0, readability_score)),
            complexity_grade=min(20.0, max(0.0, complexity_grade)),
            sentiment_polarity=sentiment_polarity,
            sentiment_subjectivity=sentiment_subjectivity,
            empathy_indicators=empathy_count,
            authority_indicators=authority_count,
            inclusive_language_score=inclusive_language_score,
            future_orientation_score=future_orientation_score
        )

    async def analyze_influence_patterns(self, 
                                       communication_samples: List[str]) -> List[str]:
        """Analyze influence patterns in communication"""
        
        if not communication_samples:
            return []
        
        combined_text = " ".join(communication_samples).lower()
        detected_patterns = []
        
        for pattern_type, patterns in self.influence_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text):
                    detected_patterns.append(pattern_type)
                    break
        
        return list(set(detected_patterns))

    async def calculate_emotional_intelligence_score(self,
                                                   communication_samples: List[str],
                                                   feedback_360: List[Feedback360Item]) -> float:
        """Calculate emotional intelligence score based on communication and feedback"""
        
        if not communication_samples:
            return 5.0
        
        combined_text = " ".join(communication_samples).lower()
        words = combined_text.split()
        total_words = len(words)
        
        # Empathy indicators
        empathy_score = min(5.0, (sum(1 for word in words if word in self.empathy_indicators) / max(total_words, 1)) * 500)
        
        # Emotional feedback from 360
        emotional_feedback = [f for f in feedback_360 if 'emotional' in f.comments.lower() or 'empathy' in f.comments.lower()]
        feedback_score = statistics.mean([f.rating for f in emotional_feedback]) / 2 if emotional_feedback else 2.5
        
        return min(10.0, empathy_score + feedback_score)

    async def calculate_clarity_score(self, communication_samples: List[str]) -> float:
        """Calculate communication clarity score"""
        
        if not communication_samples:
            return 5.0
        
        total_clarity = 0.0
        
        for sample in communication_samples:
            # Readability contributes to clarity
            readability = flesch_reading_ease(sample)
            
            # Sentence length analysis
            sentences = sample.split('.')
            avg_sentence_length = statistics.mean([len(s.split()) for s in sentences if s.strip()])
            
            # Clarity score: higher readability + reasonable sentence length
            sample_clarity = min(10.0, (readability / 10) + max(0, 10 - (avg_sentence_length - 15) / 2))
            total_clarity += sample_clarity
        
        return total_clarity / len(communication_samples)

    async def analyze_communication_patterns(self, 
                                           communication_samples: List[str],
                                           feedback_360: List[Feedback360Item] = []) -> CommunicationAnalysis:
        """Analyze I vs We vs They usage in communication with advanced analysis"""
        
        i_count = 0
        we_count = 0
        they_count = 0
        total_words = 0
        
        for sample in communication_samples:
            words = sample.lower().split()
            total_words += len(words)
            
            # Count pronouns (more sophisticated than simple word matching)
            i_patterns = r'\b(i|my|me|mine|myself)\b'
            we_patterns = r'\b(we|our|us|ours|ourselves)\b'
            they_patterns = r'\b(they|their|them|theirs|themselves)\b'
            
            i_count += len(re.findall(i_patterns, sample.lower()))
            we_count += len(re.findall(we_patterns, sample.lower()))
            they_count += len(re.findall(they_patterns, sample.lower()))
        
        we_to_i_ratio = we_count / i_count if i_count > 0 else float('inf')
        
        # Determine communication style
        if we_to_i_ratio > 2.0:
            communication_style = "Team-Focused Leader"
            leadership_language_score = 9.0
        elif we_to_i_ratio > 1.0:
            communication_style = "Balanced Communicator"
            leadership_language_score = 7.0
        elif we_to_i_ratio > 0.5:
            communication_style = "Self-Aware Individual"
            leadership_language_score = 5.0
        else:
            communication_style = "Self-Centered Communicator"
            leadership_language_score = 3.0
        
        # Get advanced analysis
        advanced_analysis = await self.perform_advanced_text_analysis(communication_samples)
        
        # Calculate emotional intelligence and clarity
        emotional_intelligence_score = await self.calculate_emotional_intelligence_score(
            communication_samples, feedback_360
        )
        clarity_score = await self.calculate_clarity_score(communication_samples)
        
        # Get influence patterns
        influence_patterns = await self.analyze_influence_patterns(communication_samples)
        
        return CommunicationAnalysis(
            i_usage_count=i_count,
            we_usage_count=we_count,
            they_usage_count=they_count,
            total_words=total_words,
            we_to_i_ratio=we_to_i_ratio,
            communication_style=communication_style,
            leadership_language_score=leadership_language_score,
            advanced_analysis=advanced_analysis,
            emotional_intelligence_score=emotional_intelligence_score,
            clarity_score=clarity_score,
            influence_patterns=influence_patterns
        )

    async def assess_succession_planning(self, 
                                       user_id: str,
                                       team_metrics: TeamPerformanceMetrics,
                                       feedback_360: List[Feedback360Item]) -> SuccessionPlanningScore:
        """Assess succession planning readiness"""
        
        # Get succession-related feedback
        succession_feedback = [f for f in feedback_360 if f.category == FeedbackCategory.SUCCESSION]
        
        # Calculate component scores
        mentoring_activity = statistics.mean([f.rating for f in succession_feedback]) if succession_feedback else 5.0
        
        # Knowledge transfer score (based on team metrics and feedback)
        knowledge_transfer = min(10.0, team_metrics.team_engagement_score + 2.0)
        
        # Team development score  
        team_development = min(10.0, (team_metrics.retention_rate * 10 + team_metrics.collaboration_index) / 2)
        
        # Succession readiness (how ready are team members to step up)
        succession_readiness = min(10.0, team_metrics.productivity_trend + team_metrics.innovation_metrics)
        
        # Bench strength (depth of capable successors)
        bench_strength = min(10.0, team_metrics.goal_achievement_rate)
        
        # Overall score
        overall_score = statistics.mean([
            mentoring_activity, knowledge_transfer, team_development,
            succession_readiness, bench_strength
        ])
        
        return SuccessionPlanningScore(
            mentoring_activity=mentoring_activity,
            knowledge_transfer=knowledge_transfer,
            team_development=team_development,
            succession_readiness=succession_readiness,
            bench_strength=bench_strength,
            overall_score=overall_score
        )

    async def analyze_360_feedback_advanced(self, 
                                          feedback_360: List[Feedback360Item]) -> Feedback360Analytics:
        """Advanced analysis of 360-degree feedback"""
        
        if not feedback_360:
            return Feedback360Analytics()
        
        total_responses = len(feedback_360)
        average_rating = statistics.mean([f.rating for f in feedback_360])
        
        # Rating distribution
        rating_distribution = defaultdict(int)
        for feedback in feedback_360:
            rating_range = f"{int(feedback.rating)}-{int(feedback.rating)+1}"
            rating_distribution[rating_range] += 1
        
        # Sentiment analysis of comments
        all_comments = " ".join([f.comments for f in feedback_360 if f.comments])
        if all_comments:
            blob = TextBlob(all_comments)
            sentiment_analysis = {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity
            }
        else:
            sentiment_analysis = {"polarity": 0.0, "subjectivity": 0.0}
        
        # Extract key themes using simple keyword analysis
        # In production, you'd use more sophisticated NLP
        theme_keywords = {
            "communication": ["communicate", "listen", "speak", "talk", "message"],
            "leadership": ["lead", "guide", "direct", "inspire", "motivate"],
            "collaboration": ["team", "collaborate", "work together", "support"],
            "decision_making": ["decide", "choice", "judgment", "analysis"],
            "empathy": ["understand", "empathy", "care", "support", "feel"]
        }
        
        key_themes = []
        improvement_priorities = []
        strength_areas = []
        
        for theme, keywords in theme_keywords.items():
            mentions = sum(1 for comment in [f.comments.lower() for f in feedback_360 if f.comments] 
                         for keyword in keywords if keyword in comment)
            
            if mentions >= 2:  # Threshold for theme significance
                key_themes.append(theme)
                
                # Determine if it's strength or improvement area based on ratings
                theme_ratings = [f.rating for f in feedback_360 
                               if any(keyword in f.comments.lower() for keyword in keywords)]
                
                if theme_ratings:
                    avg_theme_rating = statistics.mean(theme_ratings)
                    if avg_theme_rating >= 7:
                        strength_areas.append(theme)
                    elif avg_theme_rating <= 5:
                        improvement_priorities.append(theme)
        
        # Calculate consistency score (how consistent feedback is across roles)
        role_ratings = defaultdict(list)
        for feedback in feedback_360:
            role_ratings[feedback.from_role].append(feedback.rating)
        
        if len(role_ratings) > 1:
            role_averages = [statistics.mean(ratings) for ratings in role_ratings.values()]
            consistency_score = 10.0 - (statistics.stdev(role_averages) * 2)  # Lower stdev = higher consistency
            consistency_score = max(0.0, min(10.0, consistency_score))
        else:
            consistency_score = 10.0
        
        return Feedback360Analytics(
            total_responses=total_responses,
            response_rate=min(100.0, (total_responses / 10) * 100),  # Assume 10 expected responses
            average_rating=average_rating,
            rating_distribution=dict(rating_distribution),
            sentiment_analysis=sentiment_analysis,
            key_themes=key_themes,
            improvement_priorities=improvement_priorities,
            strength_areas=strength_areas,
            consistency_score=consistency_score
        )

    async def analyze_team_performance_correlation(self,
                                                 leadership_score: float,
                                                 team_metrics: TeamPerformanceMetrics) -> TeamPerformanceCorrelation:
        """Analyze correlation between leadership effectiveness and team performance"""
        
        # Calculate correlation strength (simplified)
        leadership_normalized = leadership_score / 10.0
        team_scores = [
            team_metrics.team_engagement_score / 10.0,
            team_metrics.retention_rate / 100.0,
            team_metrics.productivity_trend / 10.0,
            team_metrics.collaboration_index / 10.0,
            team_metrics.innovation_metrics / 10.0,
            team_metrics.goal_achievement_rate / 100.0
        ]
        
        avg_team_performance = statistics.mean(team_scores)
        
        # Simple correlation calculation
        correlation_strength = 1.0 - abs(leadership_normalized - avg_team_performance)
        
        # Determine trend
        if avg_team_performance > 0.7:
            performance_trend = "strong"
        elif avg_team_performance > 0.5:
            performance_trend = "moderate"
        else:
            performance_trend = "needs_improvement"
        
        # Team feedback alignment (how well team metrics align with feedback)
        team_feedback_alignment = min(1.0, correlation_strength + 0.1)
        
        return TeamPerformanceCorrelation(
            leadership_score=leadership_score,
            team_engagement=team_metrics.team_engagement_score,
            retention_rate=team_metrics.retention_rate,
            productivity_index=team_metrics.productivity_trend,
            correlation_strength=correlation_strength,
            performance_trend=performance_trend,
            team_feedback_alignment=team_feedback_alignment
        )

# =============================================================================
# API ENDPOINTS
# =============================================================================

assessment_engine = Level5AssessmentEngine()

# In-memory storage (replace with proper database)
assessments_db = {}
feedback_360_db = defaultdict(list)
development_plans_db = {}

@router.post("/assess", response_model=LeadershipAssessmentResult)
async def conduct_leadership_assessment(
    request: AssessmentRequest,
    background_tasks: BackgroundTasks
):
    """Conduct comprehensive Level 5 Leadership Assessment"""
    
    try:
        assessment_id = f"assessment_{request.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get 360 feedback for user
        feedback_360 = feedback_360_db.get(request.user_id, [])
        
        # Mock team performance metrics (integrate with actual team data)
        team_performance = TeamPerformanceMetrics(
            team_engagement_score=7.5,
            retention_rate=8.2,
            productivity_trend=7.8,
            collaboration_index=8.0,
            innovation_metrics=7.2,
            goal_achievement_rate=8.5
        )
        
        # Run assessments in parallel
        humility_will_task = assessment_engine.assess_humility_will_matrix(
            request.communication_samples, feedback_360
        )
        
        attribution_task = assessment_engine.analyze_attribution_patterns(
            request.communication_samples, []  # Add historical data here
        )
        
        communication_task = assessment_engine.analyze_communication_patterns(
            request.communication_samples, feedback_360
        )
        
        succession_task = assessment_engine.assess_succession_planning(
            request.user_id, team_performance, feedback_360
        )
        
        # Wait for all assessments to complete
        humility_will_matrix, attribution_pattern, communication_analysis, succession_planning = await asyncio.gather(
            humility_will_task, attribution_task, communication_task, succession_task
        )
        
        # Determine leadership level
        leadership_level = _determine_leadership_level(
            humility_will_matrix, communication_analysis, succession_planning
        )
        
        # Calculate overall score
        overall_score = _calculate_overall_score(
            humility_will_matrix, attribution_pattern, communication_analysis, 
            succession_planning, team_performance
        )
        
        # Generate recommendations
        recommendations = _generate_recommendations(
            leadership_level, humility_will_matrix, communication_analysis, succession_planning
        )
        
        # Create development plan
        development_plan = _create_development_plan(
            leadership_level, recommendations
        )
        
        # Summarize 360 feedback
        feedback_360_summary = _summarize_360_feedback(feedback_360)
        
        # Create assessment result
        result = LeadershipAssessmentResult(
            assessment_id=assessment_id,
            user_id=request.user_id,
            timestamp=datetime.now(),
            leadership_level=leadership_level,
            humility_will_matrix=humility_will_matrix,
            attribution_pattern=attribution_pattern,
            communication_analysis=communication_analysis,
            succession_planning=succession_planning,
            feedback_360_summary=feedback_360_summary,
            team_performance=team_performance,
            overall_score=overall_score,
            recommendations=recommendations,
            development_plan=development_plan,
            next_assessment_date=datetime.now() + timedelta(days=90)
        )
        
        # Store assessment
        assessments_db[assessment_id] = result
        
        # Schedule follow-up tasks
        background_tasks.add_task(
            _schedule_follow_up_assessment, request.user_id, assessment_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

@router.post("/feedback/360")
async def submit_360_feedback(feedback: Feedback360Item):
    """Submit 360-degree feedback"""
    
    try:
        feedback.timestamp = datetime.now()
        feedback_360_db[feedback.from_user_id].append(feedback)
        
        return {
            "message": "360 feedback submitted successfully",
            "feedback_id": feedback.feedback_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@router.get("/feedback/360/{user_id}")
async def get_360_feedback_summary(user_id: str):
    """Get 360 feedback summary for user"""
    
    try:
        feedback_list = feedback_360_db.get(user_id, [])
        
        if not feedback_list:
            return {"message": "No feedback found", "summary": {}}
        
        summary = _summarize_360_feedback(feedback_list)
        
        return {
            "user_id": user_id,
            "total_feedback_items": len(feedback_list),
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feedback: {str(e)}")

@router.get("/assessment/{assessment_id}", response_model=LeadershipAssessmentResult)
async def get_assessment_result(assessment_id: str):
    """Get assessment result by ID"""
    
    if assessment_id not in assessments_db:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessments_db[assessment_id]

@router.get("/assessments/{user_id}")
async def get_user_assessments(user_id: str):
    """Get all assessments for a user"""
    
    user_assessments = [
        assessment for assessment in assessments_db.values()
        if assessment.user_id == user_id
    ]
    
    return {
        "user_id": user_id,
        "total_assessments": len(user_assessments),
        "assessments": user_assessments
    }

@router.post("/development-plan", response_model=LeadershipDevelopmentPlan)
async def create_development_plan(
    user_id: str,
    target_level: LeadershipLevel,
    timeline_weeks: int = 12
):
    """Create personalized leadership development plan"""
    
    try:
        # Get latest assessment
        user_assessments = [a for a in assessments_db.values() if a.user_id == user_id]
        if not user_assessments:
            raise HTTPException(status_code=404, detail="No assessments found for user")
        
        latest_assessment = max(user_assessments, key=lambda x: x.timestamp)
        
        plan_id = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        development_plan = LeadershipDevelopmentPlan(
            plan_id=plan_id,
            user_id=user_id,
            current_level=latest_assessment.leadership_level,
            target_level=target_level,
            development_areas=latest_assessment.recommendations,
            action_items=_create_action_items(latest_assessment, target_level),
            milestones=_create_milestones(timeline_weeks),
            resources=_get_development_resources(target_level),
            timeline_weeks=timeline_weeks,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        development_plans_db[plan_id] = development_plan
        
        return development_plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create development plan: {str(e)}")

@router.get("/analytics/leadership-trends/{user_id}")
async def get_leadership_trends(user_id: str):
    """Get leadership development trends over time"""
    
    try:
        user_assessments = [
            a for a in assessments_db.values() 
            if a.user_id == user_id
        ]
        
        if not user_assessments:
            return {"message": "No assessment data found"}
        
        # Sort by timestamp
        sorted_assessments = sorted(user_assessments, key=lambda x: x.timestamp)
        
        trends = {
            "humility_trend": [a.humility_will_matrix.humility_score for a in sorted_assessments],
            "will_trend": [a.humility_will_matrix.will_score for a in sorted_assessments],
            "overall_score_trend": [a.overall_score for a in sorted_assessments],
            "attribution_ratio_trend": [a.attribution_pattern.attribution_ratio for a in sorted_assessments],
            "we_to_i_ratio_trend": [a.communication_analysis.we_to_i_ratio for a in sorted_assessments],
            "timestamps": [a.timestamp.isoformat() for a in sorted_assessments]
        }
        
        return {
            "user_id": user_id,
            "trends": trends,
            "improvement_areas": _identify_improvement_areas(sorted_assessments)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _determine_leadership_level(
    humility_will_matrix: HumilityWillMatrix,
    communication_analysis: CommunicationAnalysis,
    succession_planning: SuccessionPlanningScore
) -> LeadershipLevel:
    """Determine overall leadership level"""
    
    # Level 5 requires high humility, high will, team-focused communication, and succession planning
    if (humility_will_matrix.level_5_potential > 0.8 and
        communication_analysis.leadership_language_score > 7 and
        succession_planning.overall_score > 7):
        return LeadershipLevel.LEVEL_5
    
    # Level 4 - Effective Leader
    elif (humility_will_matrix.will_score > 6 and
          communication_analysis.leadership_language_score > 6):
        return LeadershipLevel.LEVEL_4
    
    # Level 3 - Competent Manager  
    elif succession_planning.overall_score > 5:
        return LeadershipLevel.LEVEL_3
    
    # Level 2 - Contributing Team Member
    elif communication_analysis.we_to_i_ratio > 0.5:
        return LeadershipLevel.LEVEL_2
    
    # Level 1 - Highly Capable Individual
    else:
        return LeadershipLevel.LEVEL_1

def _calculate_overall_score(
    humility_will_matrix: HumilityWillMatrix,
    attribution_pattern: AttributionPattern,
    communication_analysis: CommunicationAnalysis,
    succession_planning: SuccessionPlanningScore,
    team_performance: TeamPerformanceMetrics
) -> float:
    """Calculate overall leadership score"""
    
    scores = [
        humility_will_matrix.level_5_potential * 10,
        attribution_pattern.attribution_ratio * 10,
        communication_analysis.leadership_language_score,
        succession_planning.overall_score,
        (team_performance.team_engagement_score + 
         team_performance.retention_rate + 
         team_performance.collaboration_index) / 3
    ]
    
    return round(statistics.mean(scores), 2)

def _generate_recommendations(
    leadership_level: LeadershipLevel,
    humility_will_matrix: HumilityWillMatrix,
    communication_analysis: CommunicationAnalysis,
    succession_planning: SuccessionPlanningScore
) -> List[str]:
    """Generate personalized development recommendations"""
    
    recommendations = []
    
    # Humility recommendations
    if humility_will_matrix.humility_score < 7:
        recommendations.append("Practice active listening and acknowledge others' contributions more frequently")
        recommendations.append("Seek feedback regularly and respond positively to constructive criticism")
    
    # Will recommendations
    if humility_will_matrix.will_score < 7:
        recommendations.append("Set more ambitious goals and hold yourself accountable to higher standards")
        recommendations.append("Drive results more aggressively while maintaining team morale")
    
    # Communication recommendations
    if communication_analysis.we_to_i_ratio < 1.0:
        recommendations.append("Use more 'we' language and less 'I' language in team communications")
        recommendations.append("Focus on team achievements rather than individual accomplishments")
    
    # Succession planning recommendations
    if succession_planning.overall_score < 7:
        recommendations.append("Invest more time in mentoring and developing team members")
        recommendations.append("Create formal knowledge transfer processes and documentation")
        recommendations.append("Identify and develop potential successors within your team")
    
    # Level-specific recommendations
    if leadership_level == LeadershipLevel.LEVEL_1:
        recommendations.append("Focus on contributing to team goals rather than just individual performance")
    elif leadership_level == LeadershipLevel.LEVEL_2:
        recommendations.append("Take on more leadership responsibilities within team projects")
    elif leadership_level == LeadershipLevel.LEVEL_3:
        recommendations.append("Develop a compelling vision and inspire others to follow")
    elif leadership_level == LeadershipLevel.LEVEL_4:
        recommendations.append("Build institutional leadership capabilities that outlast your tenure")
    
    return recommendations

def _create_development_plan(
    leadership_level: LeadershipLevel,
    recommendations: List[str]
) -> List[Dict[str, Any]]:
    """Create structured development plan"""
    
    development_items = []
    
    for i, recommendation in enumerate(recommendations):
        development_items.append({
            "item_id": f"dev_item_{i+1}",
            "recommendation": recommendation,
            "priority": "high" if i < 3 else "medium",
            "estimated_weeks": 4 if i < 3 else 6,
            "resources_needed": ["coaching", "practice", "feedback"],
            "success_metrics": ["behavioral observation", "360 feedback improvement"]
        })
    
    return development_items

def _create_action_items(
    assessment: LeadershipAssessmentResult,
    target_level: LeadershipLevel
) -> List[Dict[str, Any]]:
    """Create specific action items for development plan"""
    
    action_items = []
    
    # Create action items based on assessment gaps
    if assessment.humility_will_matrix.humility_score < 7:
        action_items.append({
            "action": "Schedule weekly one-on-ones with team members to practice active listening",
            "deadline_weeks": 2,
            "success_metric": "Team feedback on listening skills"
        })
    
    if assessment.communication_analysis.we_to_i_ratio < 1.0:
        action_items.append({
            "action": "Review and revise all team communications to use 'we' language",
            "deadline_weeks": 1,
            "success_metric": "Communication analysis shows >1.5 we:I ratio"
        })
    
    if assessment.succession_planning.overall_score < 7:
        action_items.append({
            "action": "Create individual development plans for all direct reports",
            "deadline_weeks": 4,
            "success_metric": "100% of team has active development plan"
        })
    
    return action_items

def _create_milestones(timeline_weeks: int) -> List[Dict[str, Any]]:
    """Create development milestones"""
    
    milestones = []
    
    # Create milestones every 3-4 weeks
    for week in range(4, timeline_weeks + 1, 4):
        milestones.append({
            "week": week,
            "milestone": f"Assessment checkpoint - Week {week}",
            "deliverables": ["360 feedback collection", "self-assessment", "coach review"],
            "success_criteria": "Demonstrated improvement in target areas"
        })
    
    return milestones

def _get_development_resources(target_level: LeadershipLevel) -> List[Dict[str, Any]]:
    """Get recommended development resources"""
    
    resources = [
        {
            "type": "book",
            "title": "Good to Great",
            "author": "Jim Collins",
            "relevance": "Core Level 5 Leadership concepts"
        },
        {
            "type": "assessment",
            "title": "360-Degree Feedback Tool",
            "provider": "Internal",
            "relevance": "Ongoing development tracking"
        }
    ]
    
    if target_level == LeadershipLevel.LEVEL_5:
        resources.extend([
            {
                "type": "coaching",
                "title": "Executive Leadership Coaching",
                "duration": "6 months",
                "relevance": "Level 5 transition support"
            },
            {
                "type": "book",
                "title": "Built to Last",
                "author": "Jim Collins",
                "relevance": "Institutional leadership building"
            }
        ])
    
    return resources

def _summarize_360_feedback(feedback_list: List[Feedback360Item]) -> Dict[str, Any]:
    """Summarize 360-degree feedback"""
    
    if not feedback_list:
        return {}
    
    # Group by category
    by_category = defaultdict(list)
    for feedback in feedback_list:
        by_category[feedback.category.value].append(feedback.rating)
    
    # Group by role
    by_role = defaultdict(list)
    for feedback in feedback_list:
        by_role[feedback.from_role].append(feedback.rating)
    
    summary = {
        "total_responses": len(feedback_list),
        "average_rating": round(statistics.mean([f.rating for f in feedback_list]), 2),
        "by_category": {
            category: {
                "average": round(statistics.mean(ratings), 2),
                "count": len(ratings)
            }
            for category, ratings in by_category.items()
        },
        "by_role": {
            role: {
                "average": round(statistics.mean(ratings), 2),
                "count": len(ratings)
            }
            for role, ratings in by_role.items()
        }
    }
    
    return summary

def _identify_improvement_areas(assessments: List[LeadershipAssessmentResult]) -> List[str]:
    """Identify areas needing improvement based on trends"""
    
    if len(assessments) < 2:
        return []
    
    improvement_areas = []
    
    # Check humility trend
    humility_scores = [a.humility_will_matrix.humility_score for a in assessments]
    if humility_scores[-1] < humility_scores[0]:
        improvement_areas.append("Humility and self-awareness")
    
    # Check communication trend
    we_ratios = [a.communication_analysis.we_to_i_ratio for a in assessments]
    if we_ratios[-1] < we_ratios[0]:
        improvement_areas.append("Team-focused communication")
    
    # Check succession planning trend
    succession_scores = [a.succession_planning.overall_score for a in assessments]
    if succession_scores[-1] < succession_scores[0]:
        improvement_areas.append("Succession planning and mentoring")
    
    return improvement_areas

@router.get("/analytics/360-feedback/{user_id}")
async def get_360_feedback_analytics(user_id: str):
    """Get advanced 360-degree feedback analytics"""
    
    try:
        feedback_list = feedback_360_db.get(user_id, [])
        
        if not feedback_list:
            return {"message": "No feedback found"}
        
        analytics = await assessment_engine.analyze_360_feedback_advanced(feedback_list)
        
        return {
            "user_id": user_id,
            "analytics": analytics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.get("/analytics/team-correlation/{user_id}")
async def get_team_performance_correlation(user_id: str):
    """Get team performance correlation analysis"""
    
    try:
        # Get latest assessment for leadership score
        user_assessments = [a for a in assessments_db.values() if a.user_id == user_id]
        if not user_assessments:
            raise HTTPException(status_code=404, detail="No assessments found")
        
        latest_assessment = max(user_assessments, key=lambda x: x.timestamp)
        
        # Mock team metrics (replace with actual data)
        team_metrics = TeamPerformanceMetrics(
            team_engagement_score=8.1,
            retention_rate=87.5,
            productivity_trend=7.8,
            collaboration_index=8.3,
            innovation_metrics=7.2,
            goal_achievement_rate=82.0
        )
        
        correlation = await assessment_engine.analyze_team_performance_correlation(
            latest_assessment.overall_score, team_metrics
        )
        
        return {
            "user_id": user_id,
            "correlation_analysis": correlation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get correlation: {str(e)}")

@router.post("/feedback/360/bulk")
async def submit_bulk_360_feedback(feedback_list: List[Feedback360Item]):
    """Submit multiple 360-degree feedback items"""
    
    try:
        results = []
        
        for feedback in feedback_list:
            feedback.timestamp = datetime.now()
            
            # Group by user being evaluated (assuming from_user_id is the evaluator)
            # In real system, you'd have a separate field for who's being evaluated
            target_user_id = feedback.from_user_id  # This should be the evaluated user ID
            feedback_360_db[target_user_id].append(feedback)
            
            results.append({
                "feedback_id": feedback.feedback_id,
                "status": "submitted"
            })
        
        return {
            "message": f"Successfully submitted {len(feedback_list)} feedback items",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit bulk feedback: {str(e)}")

@router.get("/text-analysis/preview")
async def preview_text_analysis(text_sample: str):
    """Preview advanced text analysis for a sample"""
    
    try:
        if not text_sample or len(text_sample) < 10:
            raise HTTPException(status_code=400, detail="Text sample too short")
        
        analysis = await assessment_engine.perform_advanced_text_analysis([text_sample])
        influence_patterns = await assessment_engine.analyze_influence_patterns([text_sample])
        
        return {
            "text_sample": text_sample[:100] + "..." if len(text_sample) > 100 else text_sample,
            "advanced_analysis": analysis,
            "influence_patterns": influence_patterns,
            "word_count": len(text_sample.split()),
            "character_count": len(text_sample)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/benchmarks/{user_id}")
async def get_leadership_benchmarks(user_id: str):
    """Get leadership benchmarks and peer comparisons"""
    
    try:
        # Get user's latest assessment
        user_assessments = [a for a in assessments_db.values() if a.user_id == user_id]
        if not user_assessments:
            raise HTTPException(status_code=404, detail="No assessments found")
        
        user_assessment = max(user_assessments, key=lambda x: x.timestamp)
        
        # Mock peer data (replace with actual peer analysis)
        peer_benchmarks = {
            "industry_average": {
                "overall_score": 6.8,
                "level_5_potential": 0.52,
                "we_to_i_ratio": 1.3,
                "succession_score": 6.2
            },
            "role_average": {
                "overall_score": 7.1,
                "level_5_potential": 0.58,
                "we_to_i_ratio": 1.5,
                "succession_score": 6.7
            },
            "top_10_percent": {
                "overall_score": 8.9,
                "level_5_potential": 0.88,
                "we_to_i_ratio": 2.8,
                "succession_score": 8.7
            },
            "user_position": {
                "overall_score": "above_average" if user_assessment.overall_score > 7.1 else "below_average",
                "percentile": min(95, max(5, int((user_assessment.overall_score / 10) * 100)))
            }
        }
        
        return {
            "user_id": user_id,
            "benchmarks": peer_benchmarks,
            "user_scores": {
                "overall_score": user_assessment.overall_score,
                "level_5_potential": user_assessment.humility_will_matrix.level_5_potential,
                "we_to_i_ratio": user_assessment.communication_analysis.we_to_i_ratio,
                "succession_score": user_assessment.succession_planning.overall_score
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get benchmarks: {str(e)}")

async def _schedule_follow_up_assessment(user_id: str, assessment_id: str):
    """Schedule follow-up assessment (background task)"""
    
    # In a real implementation, this would integrate with a scheduling system
    # For now, just log the scheduling
    print(f"Scheduled follow-up assessment for user {user_id} in 90 days")
    
    # Could send email notification, create calendar event, etc.
    pass