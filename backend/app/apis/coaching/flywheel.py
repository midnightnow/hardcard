"""
Flywheel Mapping and Analytics API

Provides comprehensive flywheel management including:
- Dynamic flywheel creation and editing
- Momentum tracking and simulation
- Performance metrics and analytics
- Causal relationship validation
- Business model templates
- Revenue integration
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
import asyncio
import json
import math
from enum import Enum

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

# Import your database and auth dependencies
# from app.core.database import get_db
# from app.core.auth import get_current_user

router = APIRouter(prefix="/api/flywheel", tags=["flywheel"])

class ComponentCategory(str, Enum):
    INPUT = "input"
    PROCESS = "process"
    OUTPUT = "output"
    FEEDBACK = "feedback"

class BlockageSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InsightType(str, Enum):
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TREND = "trend"
    ACHIEVEMENT = "achievement"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComponentMetrics(BaseModel):
    efficiency: float = Field(ge=0, le=10, description="Efficiency rating 0-10")
    impact: float = Field(ge=0, le=10, description="Impact rating 0-10")
    reliability: float = Field(ge=0, le=10, description="Reliability rating 0-10")
    speed: float = Field(ge=0, le=10, description="Speed rating 0-10")

class Position(BaseModel):
    x: float = Field(description="X coordinate on canvas")
    y: float = Field(description="Y coordinate on canvas")

class FlywheelComponent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500, default="")
    category: ComponentCategory
    performance: float = Field(ge=1, le=10, default=5)
    momentum: float = Field(ge=-100, le=100, default=0)
    position: Position
    connections: List[str] = Field(default_factory=list, description="IDs of connected components")
    metrics: ComponentMetrics = Field(default_factory=lambda: ComponentMetrics(efficiency=5, impact=5, reliability=5, speed=5))
    blockages: List[str] = Field(default_factory=list, description="List of current blockages")
    is_active: bool = Field(default=True)
    color: str = Field(default="#3B82F6", description="Display color")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('color')
    def validate_color(cls, v):
        if not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color')
        return v

class BlockageData(BaseModel):
    component_id: str
    component_name: str
    severity: BlockageSeverity
    description: str
    impact: float = Field(ge=0, le=100, description="Impact percentage")
    duration_days: int = Field(ge=0, description="How long this blockage has existed")
    estimated_fix_days: int = Field(ge=0, description="Estimated days to fix")

class FlywheelValidation(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    score: float = Field(ge=0, le=100, description="Overall validation score")

class PerformanceInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: InsightType
    title: str
    description: str
    priority: Priority
    component_id: Optional[str] = None
    component_name: Optional[str] = None
    metric: str
    change: float = Field(description="Percentage change or impact")
    recommendation: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FlywheelSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    flywheel_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    overall_momentum: float = Field(ge=0, le=100)
    velocity_score: float = Field(ge=0, le=100)
    efficiency: float = Field(ge=0, le=100)
    impact: float = Field(ge=0, le=100)
    reliability: float = Field(ge=0, le=100)
    speed: float = Field(ge=0, le=100)
    components: List[FlywheelComponent]
    revenue: Optional[float] = None
    customers: Optional[int] = None
    conversion_rate: Optional[float] = None
    cycle_time_days: Optional[float] = None
    blockages: List[BlockageData] = Field(default_factory=list)
    validation: FlywheelValidation
    insights: List[PerformanceInsight] = Field(default_factory=list)

class Flywheel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000, default="")
    industry: Optional[str] = None
    business_model: Optional[str] = None
    components: List[FlywheelComponent] = Field(default_factory=list)
    is_template: bool = Field(default=False)
    is_public: bool = Field(default=False)
    owner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_simulation: Optional[datetime] = None
    
    # Computed fields
    overall_momentum: float = Field(default=0, ge=0, le=100)
    component_count: int = Field(default=0)
    connection_count: int = Field(default=0)
    validation_score: float = Field(default=0, ge=0, le=100)

class BusinessTemplate(BaseModel):
    id: str
    name: str
    description: str
    industry: str
    expected_momentum: float = Field(ge=0, le=100)
    components: List[Dict[str, Any]]
    success_metrics: List[str]
    common_blockages: List[str]
    optimization_tips: List[str]

class FlywheelCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=1000, default="")
    industry: Optional[str] = None
    business_model: Optional[str] = None
    template_id: Optional[str] = None

class FlywheelUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    industry: Optional[str] = None
    business_model: Optional[str] = None

class ComponentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500, default="")
    category: ComponentCategory
    performance: float = Field(ge=1, le=10, default=5)
    position: Position
    metrics: Optional[ComponentMetrics] = None
    color: str = Field(default="#3B82F6")

class ComponentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[ComponentCategory] = None
    performance: Optional[float] = Field(None, ge=1, le=10)
    position: Optional[Position] = None
    connections: Optional[List[str]] = None
    metrics: Optional[ComponentMetrics] = None
    blockages: Optional[List[str]] = None
    is_active: Optional[bool] = None
    color: Optional[str] = None

class SimulationRequest(BaseModel):
    duration_seconds: int = Field(ge=1, le=3600, default=60)
    speed_multiplier: float = Field(ge=0.1, le=10.0, default=1.0)
    include_random_events: bool = Field(default=True)
    save_snapshots: bool = Field(default=True)

# Business Model Templates
BUSINESS_TEMPLATES = {
    "saas": BusinessTemplate(
        id="saas",
        name="SaaS Growth Flywheel",
        description="Product-led growth model for software companies",
        industry="Technology",
        expected_momentum=75,
        components=[
            {
                "name": "Product Value",
                "description": "Core product delivers exceptional value",
                "category": "input",
                "performance": 8,
                "position": {"x": 100, "y": 100},
                "metrics": {"efficiency": 8, "impact": 9, "reliability": 8, "speed": 7},
                "color": "#3B82F6"
            },
            {
                "name": "User Acquisition",
                "description": "Attract and convert new users",
                "category": "process",
                "performance": 7,
                "position": {"x": 300, "y": 100},
                "metrics": {"efficiency": 7, "impact": 8, "reliability": 7, "speed": 8},
                "color": "#10B981"
            },
            {
                "name": "User Engagement",
                "description": "Users actively use and love the product",
                "category": "output",
                "performance": 6,
                "position": {"x": 300, "y": 300},
                "metrics": {"efficiency": 6, "impact": 8, "reliability": 6, "speed": 7},
                "color": "#F59E0B"
            },
            {
                "name": "Revenue Growth",
                "description": "Increased revenue from engaged users",
                "category": "output",
                "performance": 8,
                "position": {"x": 100, "y": 300},
                "metrics": {"efficiency": 8, "impact": 9, "reliability": 8, "speed": 8},
                "color": "#8B5CF6"
            },
            {
                "name": "Product Investment",
                "description": "Reinvest revenue into product improvements",
                "category": "feedback",
                "performance": 7,
                "position": {"x": 100, "y": 200},
                "metrics": {"efficiency": 7, "impact": 8, "reliability": 7, "speed": 6},
                "color": "#EF4444"
            }
        ],
        success_metrics=[
            "Monthly Recurring Revenue (MRR)",
            "Customer Acquisition Cost (CAC)",
            "Customer Lifetime Value (CLV)",
            "Net Promoter Score (NPS)",
            "Feature Adoption Rate"
        ],
        common_blockages=[
            "High customer acquisition cost",
            "Low product-market fit",
            "Poor user onboarding",
            "Churn in early stages",
            "Slow feature development"
        ],
        optimization_tips=[
            "Focus on product-market fit before scaling",
            "Optimize user onboarding experience", 
            "Implement comprehensive analytics",
            "Build strong feedback loops",
            "Invest in customer success"
        ]
    ),
    "ecommerce": BusinessTemplate(
        id="ecommerce",
        name="E-commerce Flywheel",
        description="Customer-centric growth model for online retail",
        industry="Retail",
        expected_momentum=65,
        components=[
            {
                "name": "Customer Experience",
                "description": "Exceptional shopping experience",
                "category": "input",
                "performance": 7,
                "position": {"x": 100, "y": 100},
                "metrics": {"efficiency": 7, "impact": 8, "reliability": 7, "speed": 8},
                "color": "#3B82F6"
            },
            {
                "name": "Customer Satisfaction",
                "description": "Happy customers become loyal advocates",
                "category": "process",
                "performance": 8,
                "position": {"x": 300, "y": 150},
                "metrics": {"efficiency": 8, "impact": 9, "reliability": 8, "speed": 7},
                "color": "#10B981"
            },
            {
                "name": "Word of Mouth",
                "description": "Customers refer friends and family",
                "category": "output",
                "performance": 6,
                "position": {"x": 300, "y": 300},
                "metrics": {"efficiency": 6, "impact": 7, "reliability": 6, "speed": 8},
                "color": "#F59E0B"
            },
            {
                "name": "Traffic Growth",
                "description": "Increased organic traffic and sales",
                "category": "output",
                "performance": 7,
                "position": {"x": 150, "y": 350},
                "metrics": {"efficiency": 7, "impact": 8, "reliability": 7, "speed": 8},
                "color": "#8B5CF6"
            },
            {
                "name": "Economies of Scale",
                "description": "Lower costs, better pricing, more selection",
                "category": "feedback",
                "performance": 8,
                "position": {"x": 50, "y": 250},
                "metrics": {"efficiency": 8, "impact": 8, "reliability": 8, "speed": 6},
                "color": "#EF4444"
            }
        ],
        success_metrics=[
            "Customer Acquisition Cost (CAC)",
            "Average Order Value (AOV)",
            "Customer Lifetime Value (CLV)",
            "Conversion Rate",
            "Net Promoter Score (NPS)"
        ],
        common_blockages=[
            "High shipping costs",
            "Poor website performance",
            "Limited payment options",
            "Inventory management issues",
            "Customer service bottlenecks"
        ],
        optimization_tips=[
            "Optimize for mobile experience",
            "Implement personalization",
            "Streamline checkout process",
            "Build loyalty programs",
            "Focus on customer reviews"
        ]
    ),
    "marketplace": BusinessTemplate(
        id="marketplace",
        name="Marketplace Flywheel",
        description="Two-sided market growth model",
        industry="Platform",
        expected_momentum=80,
        components=[
            {
                "name": "Supply Quality",
                "description": "High-quality suppliers and inventory",
                "category": "input",
                "performance": 7,
                "position": {"x": 100, "y": 100},
                "metrics": {"efficiency": 7, "impact": 8, "reliability": 7, "speed": 7},
                "color": "#3B82F6"
            },
            {
                "name": "Buyer Experience",
                "description": "Great selection and competitive prices",
                "category": "process",
                "performance": 8,
                "position": {"x": 300, "y": 100},
                "metrics": {"efficiency": 8, "impact": 9, "reliability": 8, "speed": 8},
                "color": "#10B981"
            },
            {
                "name": "Buyer Demand",
                "description": "Increased buyer traffic and purchases",
                "category": "output",
                "performance": 8,
                "position": {"x": 300, "y": 300},
                "metrics": {"efficiency": 8, "impact": 9, "reliability": 8, "speed": 9},
                "color": "#F59E0B"
            },
            {
                "name": "Supplier Attraction",
                "description": "More suppliers join the platform",
                "category": "feedback",
                "performance": 7,
                "position": {"x": 100, "y": 300},
                "metrics": {"efficiency": 7, "impact": 8, "reliability": 7, "speed": 8},
                "color": "#8B5CF6"
            }
        ],
        success_metrics=[
            "Gross Merchandise Value (GMV)",
            "Take Rate",
            "Supplier/Buyer Ratio",
            "Transaction Volume",
            "Platform Engagement"
        ],
        common_blockages=[
            "Chicken and egg problem",
            "Quality control issues",
            "Trust and safety concerns",
            "Payment processing delays",
            "Search and discovery problems"
        ],
        optimization_tips=[
            "Solve chicken-egg with single-sided utility",
            "Implement strong quality controls",
            "Build trust through reviews and ratings",
            "Optimize search and discovery",
            "Focus on network effects"
        ]
    )
}

class FlywheelValidator:
    """Validates flywheel structure and provides optimization suggestions"""
    
    @staticmethod
    def validate_flywheel(flywheel: Flywheel) -> FlywheelValidation:
        errors = []
        warnings = []
        suggestions = []
        
        # Basic structure validation
        if len(flywheel.components) < 3:
            errors.append("Flywheel needs at least 3 components to function effectively")
        
        # Check for disconnected components
        connected_components = set()
        for comp in flywheel.components:
            for conn_id in comp.connections:
                connected_components.add(conn_id)
                connected_components.add(comp.id)
        
        disconnected = [comp for comp in flywheel.components if comp.id not in connected_components]
        if disconnected:
            warnings.append(f"{len(disconnected)} components are not connected to the flywheel")
        
        # Check for circular flow
        has_cycle = FlywheelValidator._check_circular_flow(flywheel.components)
        if not has_cycle and len(flywheel.components) >= 3:
            errors.append("Flywheel lacks circular flow - components should form a cycle")
        
        # Category balance
        categories = {}
        for comp in flywheel.components:
            categories[comp.category.value] = categories.get(comp.category.value, 0) + 1
        
        if 'feedback' not in categories and len(flywheel.components) > 3:
            warnings.append("Consider adding feedback components to strengthen the flywheel")
        
        # Performance analysis
        low_performers = [comp for comp in flywheel.components if comp.performance < 5]
        if low_performers:
            suggestions.append(f"{len(low_performers)} components have low performance scores")
        
        blocked_components = [comp for comp in flywheel.components if comp.blockages]
        if blocked_components:
            warnings.append(f"{len(blocked_components)} components have identified blockages")
        
        # Calculate validation score
        score = 100
        score -= len(errors) * 20
        score -= len(warnings) * 5
        score -= len(low_performers) * 3
        score -= len(blocked_components) * 2
        score = max(0, min(100, score))
        
        return FlywheelValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            score=score
        )
    
    @staticmethod
    def _check_circular_flow(components: List[FlywheelComponent]) -> bool:
        """Check if components form a circular flow using DFS"""
        if len(components) < 3:
            return False
        
        # Build adjacency list
        graph = {}
        for comp in components:
            graph[comp.id] = comp.connections
        
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str) -> bool:
            if node_id in rec_stack:
                return True  # Found cycle
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for neighbor_id in graph.get(node_id, []):
                if dfs(neighbor_id):
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for comp in components:
            if comp.id not in visited:
                if dfs(comp.id):
                    return True
        
        return False

class FlywheelSimulator:
    """Simulates flywheel momentum and generates insights"""
    
    @staticmethod
    async def simulate_flywheel(
        flywheel: Flywheel,
        duration_seconds: int = 60,
        speed_multiplier: float = 1.0,
        include_random_events: bool = True
    ) -> List[FlywheelSnapshot]:
        """Run flywheel simulation and return snapshots"""
        snapshots = []
        steps = max(10, duration_seconds // 5)  # At least 10 snapshots
        
        current_components = [comp.copy() for comp in flywheel.components]
        
        for step in range(steps):
            # Update momentum for each component
            for comp in current_components:
                # Calculate momentum from connected components
                connected_momentum = 0
                connection_count = 0
                
                for conn_id in comp.connections:
                    connected_comp = next((c for c in current_components if c.id == conn_id), None)
                    if connected_comp:
                        connected_momentum += connected_comp.momentum
                        connection_count += 1
                
                avg_connected_momentum = connected_momentum / max(1, connection_count)
                
                # Apply performance factor
                performance_factor = comp.performance / 10.0
                
                # Apply blockage penalty
                blockage_penalty = len(comp.blockages) * 5
                
                # Calculate momentum change
                momentum_change = (
                    avg_connected_momentum * 0.1 * performance_factor -
                    blockage_penalty * 0.5
                )
                
                # Add random variation if enabled
                if include_random_events:
                    momentum_change += (math.sin(step * 0.1) + (hash(comp.id) % 100 - 50) / 100) * 2
                
                # Update momentum with bounds
                comp.momentum = max(-100, min(100, comp.momentum + momentum_change))
            
            # Calculate overall metrics
            overall_momentum = sum(comp.momentum for comp in current_components) / len(current_components)
            overall_momentum = max(0, min(100, overall_momentum + 50))  # Normalize to 0-100
            
            # Create snapshot
            validation = FlywheelValidator.validate_flywheel(flywheel)
            insights = FlywheelAnalytics.generate_insights(snapshots[-1:] + [None] if snapshots else [])
            
            snapshot = FlywheelSnapshot(
                flywheel_id=flywheel.id,
                timestamp=datetime.utcnow(),
                overall_momentum=overall_momentum,
                velocity_score=overall_momentum * 0.8 + (step / steps) * 20,
                efficiency=sum(comp.metrics.efficiency for comp in current_components) / len(current_components),
                impact=sum(comp.metrics.impact for comp in current_components) / len(current_components),
                reliability=sum(comp.metrics.reliability for comp in current_components) / len(current_components),
                speed=sum(comp.metrics.speed for comp in current_components) / len(current_components),
                components=[comp.copy() for comp in current_components],
                revenue=10000 + overall_momentum * 100 + step * 50,
                customers=100 + int(overall_momentum * 2) + step * 2,
                conversion_rate=15 + (overall_momentum - 50) * 0.2,
                cycle_time_days=max(1, 10 - overall_momentum * 0.08),
                validation=validation,
                insights=insights
            )
            
            snapshots.append(snapshot)
            
            # Simulate delay
            await asyncio.sleep(duration_seconds / steps / speed_multiplier)
        
        return snapshots

class FlywheelAnalytics:
    """Generates insights and analytics from flywheel data"""
    
    @staticmethod
    def generate_insights(snapshots: List[FlywheelSnapshot]) -> List[PerformanceInsight]:
        """Generate actionable insights from flywheel snapshots"""
        if len(snapshots) < 2:
            return []
        
        insights = []
        latest = snapshots[-1]
        previous = snapshots[-2]
        
        # Momentum trend analysis
        momentum_change = ((latest.overall_momentum - previous.overall_momentum) / 
                          max(previous.overall_momentum, 1)) * 100
        
        if abs(momentum_change) > 5:
            insights.append(PerformanceInsight(
                type=InsightType.ACHIEVEMENT if momentum_change > 0 else InsightType.RISK,
                title=f"Momentum {'Surge' if momentum_change > 0 else 'Decline'}",
                description=f"Overall momentum {momentum_change:+.1f}% change detected",
                priority=Priority.HIGH if abs(momentum_change) > 15 else Priority.MEDIUM,
                metric="momentum",
                change=momentum_change,
                recommendation=(
                    "Capitalize on positive momentum by increasing investment in high-performing components"
                    if momentum_change > 0 else
                    "Address bottlenecks immediately to restore momentum"
                )
            ))
        
        # Component analysis
        for i, comp in enumerate(latest.components):
            prev_comp = previous.components[i] if i < len(previous.components) else None
            if not prev_comp:
                continue
            
            # Performance change
            perf_change = ((comp.performance - prev_comp.performance) / prev_comp.performance) * 100
            
            # Identify bottlenecks (components with high impact but low performance)
            is_bottleneck = comp.metrics.impact > 7 and comp.performance < 6
            if is_bottleneck:
                insights.append(PerformanceInsight(
                    type=InsightType.RISK,
                    title="Bottleneck Detected",
                    description=f"{comp.name} is constraining overall performance",
                    priority=Priority.CRITICAL,
                    component_id=comp.id,
                    component_name=comp.name,
                    metric="bottleneck",
                    change=-comp.metrics.impact,
                    recommendation=f"Focus resources on optimizing {comp.name} to unlock performance"
                ))
            
            # High blockage warning
            if len(comp.blockages) > 2:
                insights.append(PerformanceInsight(
                    type=InsightType.RISK,
                    title="Multiple Blockages",
                    description=f"{comp.name} has {len(comp.blockages)} active blockages",
                    priority=Priority.HIGH,
                    component_id=comp.id,
                    component_name=comp.name,
                    metric="blockages",
                    change=-len(comp.blockages) * 5,
                    recommendation=f"Prioritize resolving blockages in {comp.name}"
                ))
            
            # Performance improvement recognition
            if perf_change > 10:
                insights.append(PerformanceInsight(
                    type=InsightType.ACHIEVEMENT,
                    title="Component Breakthrough",
                    description=f"{comp.name} performance improved {perf_change:+.1f}%",
                    priority=Priority.MEDIUM,
                    component_id=comp.id,
                    component_name=comp.name,
                    metric="performance",
                    change=perf_change,
                    recommendation=f"Analyze success factors in {comp.name} for broader application"
                ))
        
        # Revenue correlation analysis
        revenue_change = ((latest.revenue - previous.revenue) / previous.revenue) * 100 if latest.revenue and previous.revenue else 0
        
        if revenue_change > 10 and momentum_change > 0:
            insights.append(PerformanceInsight(
                type=InsightType.OPPORTUNITY,
                title="Revenue-Momentum Alignment",
                description=f"Revenue (+{revenue_change:.1f}%) correlates with momentum increase",
                priority=Priority.MEDIUM,
                metric="revenue_correlation",
                change=revenue_change,
                recommendation="Continue momentum-driving investments for sustained revenue growth"
            ))
        
        return sorted(insights, key=lambda x: {
            Priority.CRITICAL: 4, Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1
        }[x.priority], reverse=True)
    
    @staticmethod
    def calculate_health_score(component: FlywheelComponent) -> float:
        """Calculate overall health score for a component"""
        metrics_avg = (
            component.metrics.efficiency +
            component.metrics.impact +
            component.metrics.reliability +
            component.metrics.speed
        ) / 4
        
        # Factor in performance and momentum
        health = (metrics_avg * 0.4 + component.performance * 0.4 + 
                 max(0, component.momentum + 50) * 0.2)
        
        # Apply penalties
        blockage_penalty = len(component.blockages) * 3
        health = max(0, min(100, health - blockage_penalty))
        
        return health

# API Endpoints

@router.get("/templates", response_model=List[BusinessTemplate])
async def get_business_templates():
    """Get all available business model templates"""
    return list(BUSINESS_TEMPLATES.values())

@router.get("/templates/{template_id}", response_model=BusinessTemplate)
async def get_business_template(template_id: str):
    """Get a specific business template"""
    if template_id not in BUSINESS_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    return BUSINESS_TEMPLATES[template_id]

@router.post("/create", response_model=Flywheel)
async def create_flywheel(
    request: FlywheelCreateRequest,
    # current_user = Depends(get_current_user)
):
    """Create a new flywheel"""
    flywheel = Flywheel(
        name=request.name,
        description=request.description,
        industry=request.industry,
        business_model=request.business_model,
        # owner_id=current_user.id
    )
    
    # Apply template if specified
    if request.template_id and request.template_id in BUSINESS_TEMPLATES:
        template = BUSINESS_TEMPLATES[request.template_id]
        
        # Create components from template
        component_map = {}
        for template_comp in template.components:
            component = FlywheelComponent(**template_comp)
            flywheel.components.append(component)
            component_map[template_comp["name"].lower().replace(" ", "-")] = component.id
        
        # Set up connections based on template logic
        if request.template_id == "saas":
            flywheel.components[0].connections = [flywheel.components[1].id]  # Product Value -> User Acquisition
            flywheel.components[1].connections = [flywheel.components[2].id]  # User Acquisition -> User Engagement
            flywheel.components[2].connections = [flywheel.components[3].id]  # User Engagement -> Revenue Growth
            flywheel.components[3].connections = [flywheel.components[4].id]  # Revenue Growth -> Product Investment
            flywheel.components[4].connections = [flywheel.components[0].id]  # Product Investment -> Product Value
    
    # Calculate initial metrics
    flywheel.component_count = len(flywheel.components)
    flywheel.connection_count = sum(len(comp.connections) for comp in flywheel.components)
    
    validation = FlywheelValidator.validate_flywheel(flywheel)
    flywheel.validation_score = validation.score
    
    # Save to database would go here
    # db.add(flywheel)
    # db.commit()
    
    return flywheel

@router.get("/{flywheel_id}", response_model=Flywheel)
async def get_flywheel(flywheel_id: str):
    """Get a specific flywheel"""
    # Database lookup would go here
    # flywheel = db.query(Flywheel).filter(Flywheel.id == flywheel_id).first()
    # if not flywheel:
    #     raise HTTPException(status_code=404, detail="Flywheel not found")
    
    # For demo, return a sample flywheel
    return Flywheel(
        id=flywheel_id,
        name="Sample SaaS Flywheel",
        description="Demo flywheel for testing",
        industry="Technology",
        business_model="SaaS"
    )

@router.put("/{flywheel_id}", response_model=Flywheel)
async def update_flywheel(
    flywheel_id: str,
    request: FlywheelUpdateRequest
):
    """Update an existing flywheel"""
    # Database lookup and update would go here
    raise HTTPException(status_code=501, detail="Not implemented")

@router.delete("/{flywheel_id}")
async def delete_flywheel(flywheel_id: str):
    """Delete a flywheel"""
    # Database deletion would go here
    return {"message": "Flywheel deleted successfully"}

@router.post("/{flywheel_id}/components", response_model=FlywheelComponent)
async def add_component(
    flywheel_id: str,
    request: ComponentCreateRequest
):
    """Add a new component to a flywheel"""
    component = FlywheelComponent(
        name=request.name,
        description=request.description,
        category=request.category,
        performance=request.performance,
        position=request.position,
        metrics=request.metrics or ComponentMetrics(),
        color=request.color
    )
    
    # Database operations would go here
    return component

@router.put("/{flywheel_id}/components/{component_id}", response_model=FlywheelComponent)
async def update_component(
    flywheel_id: str,
    component_id: str,
    request: ComponentUpdateRequest
):
    """Update a component in a flywheel"""
    # Database lookup and update would go here
    raise HTTPException(status_code=501, detail="Not implemented")

@router.delete("/{flywheel_id}/components/{component_id}")
async def delete_component(flywheel_id: str, component_id: str):
    """Delete a component from a flywheel"""
    # Database deletion would go here
    return {"message": "Component deleted successfully"}

@router.post("/{flywheel_id}/validate", response_model=FlywheelValidation)
async def validate_flywheel(flywheel_id: str):
    """Validate a flywheel structure"""
    # Get flywheel from database
    # For demo, create a sample flywheel
    flywheel = Flywheel(id=flywheel_id, name="Test Flywheel")
    
    validation = FlywheelValidator.validate_flywheel(flywheel)
    return validation

@router.post("/{flywheel_id}/simulate")
async def simulate_flywheel(
    flywheel_id: str,
    request: SimulationRequest,
    background_tasks: BackgroundTasks
):
    """Run flywheel simulation"""
    # Get flywheel from database
    flywheel = Flywheel(id=flywheel_id, name="Test Flywheel")
    
    # Run simulation in background
    snapshots = await FlywheelSimulator.simulate_flywheel(
        flywheel,
        request.duration_seconds,
        request.speed_multiplier,
        request.include_random_events
    )
    
    if request.save_snapshots:
        # Save snapshots to database
        pass
    
    return {
        "message": "Simulation completed",
        "snapshots_count": len(snapshots),
        "final_momentum": snapshots[-1].overall_momentum if snapshots else 0
    }

@router.get("/{flywheel_id}/snapshots", response_model=List[FlywheelSnapshot])
async def get_flywheel_snapshots(
    flywheel_id: str,
    limit: int = Query(default=50, le=500),
    days: int = Query(default=30, le=365)
):
    """Get historical snapshots for a flywheel"""
    # Database query would go here
    # For demo, generate mock data
    snapshots = []
    base_date = datetime.utcnow()
    
    for i in range(min(limit, days)):
        timestamp = base_date - timedelta(days=i)
        momentum = 50 + math.sin(i * 0.1) * 20 + (hash(flywheel_id) % 10)
        
        snapshot = FlywheelSnapshot(
            flywheel_id=flywheel_id,
            timestamp=timestamp,
            overall_momentum=momentum,
            velocity_score=momentum * 0.8,
            efficiency=70 + (hash(str(i)) % 20),
            impact=65 + (hash(str(i+1)) % 25),
            reliability=80 + (hash(str(i+2)) % 15),
            speed=60 + (hash(str(i+3)) % 30),
            components=[],
            revenue=10000 + i * 100,
            customers=100 + i * 2,
            conversion_rate=15 + (momentum - 50) * 0.1,
            cycle_time_days=max(1, 10 - momentum * 0.05),
            validation=FlywheelValidation(is_valid=True, score=85),
            insights=[]
        )
        snapshots.append(snapshot)
    
    return sorted(snapshots, key=lambda x: x.timestamp, reverse=True)

@router.get("/{flywheel_id}/insights", response_model=List[PerformanceInsight])
async def get_flywheel_insights(
    flywheel_id: str,
    priority: Optional[Priority] = None,
    component_id: Optional[str] = None,
    limit: int = Query(default=20, le=100)
):
    """Get performance insights for a flywheel"""
    # Database query would go here
    # For demo, generate sample insights
    insights = [
        PerformanceInsight(
            type=InsightType.OPPORTUNITY,
            title="Momentum Building",
            description="Overall flywheel momentum increased by 12%",
            priority=Priority.MEDIUM,
            metric="momentum",
            change=12.0,
            recommendation="Continue current optimization efforts"
        ),
        PerformanceInsight(
            type=InsightType.RISK,
            title="Component Bottleneck",
            description="User acquisition is constraining growth",
            priority=Priority.HIGH,
            component_name="User Acquisition",
            metric="bottleneck",
            change=-15.0,
            recommendation="Increase marketing spend and optimize conversion funnel"
        )
    ]
    
    # Apply filters
    if priority:
        insights = [i for i in insights if i.priority == priority]
    if component_id:
        insights = [i for i in insights if i.component_id == component_id]
    
    return insights[:limit]

@router.get("/{flywheel_id}/analytics")
async def get_flywheel_analytics(
    flywheel_id: str,
    timeframe: str = Query(default="30d", regex="^(7d|14d|30d|60d|90d)$")
):
    """Get comprehensive analytics for a flywheel"""
    days = int(timeframe.rstrip('d'))
    
    # This would typically query your analytics database
    analytics = {
        "summary": {
            "avg_momentum": 67.5,
            "momentum_trend": 8.2,
            "top_performing_component": "Revenue Growth",
            "bottleneck_component": "User Engagement",
            "total_revenue": 45000,
            "revenue_growth": 15.3
        },
        "trends": {
            "momentum": [65, 67, 69, 68, 70, 72, 68, 67],
            "revenue": [8000, 8500, 9200, 9800, 10200, 10800, 11200, 11500],
            "customers": [120, 125, 132, 138, 145, 152, 158, 165]
        },
        "component_health": [
            {"name": "Product Value", "health": 85, "trend": "up"},
            {"name": "User Acquisition", "health": 72, "trend": "stable"},
            {"name": "User Engagement", "health": 58, "trend": "down"},
            {"name": "Revenue Growth", "health": 88, "trend": "up"},
            {"name": "Product Investment", "health": 75, "trend": "stable"}
        ],
        "recommendations": [
            "Focus on improving user engagement metrics",
            "Consider A/B testing new onboarding flows",
            "Investigate user churn patterns",
            "Optimize feature adoption tracking"
        ]
    }
    
    return analytics

@router.post("/{flywheel_id}/export")
async def export_flywheel(flywheel_id: str, format: str = "json"):
    """Export flywheel data"""
    if format not in ["json", "csv", "pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported export format")
    
    # Export logic would go here
    return {
        "message": f"Flywheel exported in {format} format",
        "download_url": f"/downloads/flywheel_{flywheel_id}.{format}"
    }

@router.post("/{flywheel_id}/duplicate", response_model=Flywheel)
async def duplicate_flywheel(flywheel_id: str, name: str):
    """Create a copy of an existing flywheel"""
    # Database operations would go here
    new_flywheel = Flywheel(
        id=str(uuid4()),
        name=name,
        description=f"Copy of flywheel {flywheel_id}"
    )
    
    return new_flywheel