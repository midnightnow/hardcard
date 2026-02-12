from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    subscription_tier = Column(String, default="standard")  # standard, premium, enterprise
    
    # Relationships
    assessments = relationship("LeadershipAssessment", back_populates="user")
    hedgehogs = relationship("HedgehogConcept", back_populates="user")
    flywheels = relationship("Flywheel", back_populates="user")
    insights = relationship("AIInsight", back_populates="user")

class LeadershipAssessment(Base):
    __tablename__ = "leadership_assessments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Level 5 Leadership dimensions
    humility_score = Column(Float)
    will_score = Column(Float)
    window_mirror_score = Column(Float)
    resolve_score = Column(Float)
    team_first_score = Column(Float)
    
    # Calculated metrics
    overall_score = Column(Float)
    leadership_level = Column(Float)
    
    # Assessment responses
    responses = Column(JSON)  # Store all question responses
    
    # Insights and recommendations
    strengths = Column(JSON)
    development_areas = Column(JSON)
    recommendations = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assessments")

class HedgehogConcept(Base):
    __tablename__ = "hedgehog_concepts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Three circles data
    passion_items = Column(JSON)  # List of passion statements
    best_at_items = Column(JSON)  # List of capabilities
    economic_items = Column(JSON)  # List of economic drivers
    
    # Analysis results
    intersection_strength = Column(Float)
    intersection_items = Column(JSON)
    insights = Column(JSON)
    clarity_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="hedgehogs")

class Flywheel(Base):
    __tablename__ = "flywheels"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Flywheel configuration
    name = Column(String)
    description = Column(Text)
    stages = Column(JSON)  # List of flywheel stages with details
    
    # Performance metrics
    overall_momentum = Column(Float)
    weakest_stage = Column(String)
    strongest_stage = Column(String)
    
    # Analysis
    recommendations = Column(JSON)
    projected_growth = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="flywheels")

class AIInsight(Base):
    __tablename__ = "ai_insights"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Insight metadata
    insight_type = Column(String)  # success, warning, critical, info
    framework = Column(String)  # hedgehog, flywheel, leadership, discipline, strategy, luck
    title = Column(String)
    message = Column(Text)
    action_suggestion = Column(String)
    
    # Data analysis
    confidence_score = Column(Float)
    data_sources = Column(JSON)  # Which data was used to generate this insight
    
    # User interaction
    is_read = Column(Boolean, default=False)
    is_acted_upon = Column(Boolean, default=False)
    user_rating = Column(Integer)  # 1-5 star rating of insight quality
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="insights")

class DisciplineTracker(Base):
    __tablename__ = "discipline_tracker"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # 20-Mile March data
    daily_goal = Column(String)
    target_metric = Column(Float)
    actual_metric = Column(Float)
    date = Column(DateTime)
    
    # Progress tracking
    streak_count = Column(Integer, default=0)
    consistency_score = Column(Float)
    
    # Contextual data
    notes = Column(Text)
    mood_rating = Column(Integer)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    
    created_at = Column(DateTime, default=datetime.utcnow)

class BusinessMetrics(Base):
    __tablename__ = "business_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Key business indicators
    revenue = Column(Float)
    customer_count = Column(Integer)
    employee_count = Column(Integer)
    nps_score = Column(Float)
    
    # Operational metrics
    productivity_score = Column(Float)
    innovation_index = Column(Float)
    leadership_effectiveness = Column(Float)
    
    # Time period
    reporting_period = Column(String)  # daily, weekly, monthly, quarterly
    period_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Partnership(Base):
    __tablename__ = "partnerships"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Partner information
    partner_name = Column(String)  # Jim Collins, Tim Ferriss, etc.
    partner_type = Column(String)  # framework_licensor, premium_coach, etc.
    
    # Partnership details
    revenue_share_percentage = Column(Float)
    minimum_guarantee = Column(Float)
    exclusive_rights = Column(JSON)
    
    # Status
    status = Column(String)  # negotiating, active, suspended
    signed_date = Column(DateTime)
    expiry_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class PremiumSession(Base):
    __tablename__ = "premium_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Session details for Tim Ferriss Premium Service
    coach_name = Column(String)  # Tim Ferriss, etc.
    session_type = Column(String)  # monthly_strategy, emergency_consult
    session_duration = Column(Integer)  # minutes
    
    # Content
    session_notes = Column(Text)
    action_items = Column(JSON)
    follow_up_date = Column(DateTime)
    
    # Billing
    session_fee = Column(Float)
    coach_share = Column(Float)
    platform_share = Column(Float)
    
    scheduled_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)