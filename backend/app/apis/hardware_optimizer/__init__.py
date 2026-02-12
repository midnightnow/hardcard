from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Literal
import random

router = APIRouter(prefix="/hardware-optimizer", tags=["hardware-optimizer"])


# Shared hardware component models
class HardwareComponent(BaseModel):
    """Base model for hardware components"""
    name: str
    description: str
    type: str
    power_consumption_mw: float
    durability_years: float
    computational_capacity_score: float
    cost_usd: float
    weight_grams: float
    dimensions_mm: List[float]  # [length, width, height]
    tags: List[str] = []


class PassiveComponent(HardwareComponent):
    """Model for passive hardware components"""
    passive_functionality: List[str]
    estimated_lifetime_years: float
    temperature_range_celsius: List[float]  # [min, max]
    humidity_resistance_percent: float
    corrosion_resistance_score: float


class PoweredComponent(HardwareComponent):
    """Model for powered hardware components"""
    voltage_requirements: List[float]  # [min, max]
    current_draw_ma: float
    processor_speed_mhz: Optional[float] = None
    memory_kb: Optional[float] = None
    interfaces: List[str] = []  # e.g., ['SPI', 'I2C', 'UART']


class PrintedComponent(HardwareComponent):
    """Model for printed electronic components"""
    printing_technology: str
    substrate_material: str
    conductive_material: str
    resolution_dpi: float
    layer_count: int
    flexible: bool


class NanoComponent(HardwareComponent):
    """Model for nano-scale components"""
    fabrication_process_nm: float
    quantum_effects: List[str] = []
    self_assembly_capable: bool = False
    bio_compatibility_score: float = 0.0


# Hardware architecture model
class HardcardArchitecture(BaseModel):
    """Model for Hardcard architectures"""
    id: str
    name: str
    description: str
    type: Literal["passive", "powered", "printed", "nano"]
    components: List[Dict[str, Any]]
    estimated_total_cost_usd: float
    estimated_lifespan_years: float
    power_requirements_mw: float
    performance_score: float
    physical_dimensions_mm: List[float]  # [length, width, height]
    weight_grams: float
    tags: List[str] = []


# Request/Response models
class SymbolicGeometryRequest(BaseModel):
    """Request model for generating symbolic geometry"""
    architecture_id: str
    resolution: str = "medium"  # low, medium, high
    include_components: bool = True
    format: Literal["svg", "graph"] = "svg"


class SymbolicGeometryResponse(BaseModel):
    """Response model for symbolic geometry"""
    architecture_id: str
    geometry_data: str  # SVG string or graph JSON
    components_mapped: List[str]
    format: str


class HardwareEvaluationRequest(BaseModel):
    """Request model for hardware evaluation"""
    architecture_ids: List[str]
    optimization_goals: Dict[str, float]  # e.g., {"power": 0.2, "durability": 0.4, "cost": 0.3, "performance": 0.1}
    constraints: Optional[Dict[str, Any]] = None


class HardwareScores(BaseModel):
    """Scores for a hardware architecture"""
    power_efficiency: float
    durability: float
    computational_capacity: float
    cost_efficiency: float
    weight_efficiency: float
    size_efficiency: float
    overall_score: float


class HardwareEvaluationResult(BaseModel):
    """Evaluation result for a single architecture"""
    architecture_id: str
    architecture_name: str
    scores: HardwareScores
    meets_constraints: bool
    constraint_violations: List[str] = []
    rank: int


class HardwareEvaluationResponse(BaseModel):
    """Response model for hardware evaluation"""
    results: List[HardwareEvaluationResult]
    best_architecture_id: str
    optimization_goals_used: Dict[str, float]


class OptimalStackComponent(BaseModel):
    """Component in the optimal hardware stack"""
    name: str
    type: str
    description: str
    quantity: int
    unit_cost_usd: float
    total_cost_usd: float
    alternatives: List[str] = []


class OptimalStackResponse(BaseModel):
    """Response model for optimal hardware stack"""
    architecture_id: str
    architecture_name: str
    total_cost_usd: float
    estimated_build_time_hours: float
    components: List[OptimalStackComponent]
    tools_required: List[str]
    fabrication_methods: List[str]
    assembly_instructions_url: str
    build_complexity_score: float  # 1-10


class FeedbackLoggingRequest(BaseModel):
    """Request model for logging feedback from real builds"""
    architecture_id: str
    build_successful: bool
    actual_build_time_hours: float
    actual_cost_usd: float
    performance_rating: float  # 1-10
    durability_rating: float  # 1-10
    issues_encountered: List[str] = []
    improvements_suggested: List[str] = []
    components_replaced: List[Dict[str, str]] = []  # [{"original": "X", "replacement": "Y"}]


class FeedbackLoggingResponse(BaseModel):
    """Response model for feedback logging"""
    success: bool
    feedback_id: str
    learning_points: List[str]
    architecture_score_adjustment: float


# Sample data
SAMPLE_ARCHITECTURES = [
    HardcardArchitecture(
        id="arch-passive-001",
        name="Passive Crystal Lattice",
        description="A fully passive design using crystalline structures to encode data through physical geometry",
        type="passive",
        components=[
            {
                "name": "Crystalline Data Matrix",
                "type": "storage",
                "description": "Diamond-based crystalline structure for long-term data storage"
            },
            {
                "name": "Optical Access Ports",
                "type": "interface",
                "description": "Sapphire windows allowing optical reading of encoded data"
            },
            {
                "name": "Protective Shell",
                "type": "housing",
                "description": "Corrosion-resistant gold alloy with graphene reinforcement"
            }
        ],
        estimated_total_cost_usd=2850.0,
        estimated_lifespan_years=500.0,
        power_requirements_mw=0.0,  # Fully passive, no power required
        performance_score=3.2,
        physical_dimensions_mm=[85.60, 53.98, 0.76],  # Standard card dimensions
        weight_grams=12.8,
        tags=["passive", "radiation-resistant", "EMP-proof", "archival"]
    ),
    HardcardArchitecture(
        id="arch-powered-001",
        name="Solar-Powered Microcontroller",
        description="A powered design using an ultra-low-power microcontroller with solar recharging",
        type="powered",
        components=[
            {
                "name": "RP2040 Microcontroller",
                "type": "processor",
                "description": "Ultra-low-power ARM Cortex-M0+ dual-core processor"
            },
            {
                "name": "Flash Memory",
                "type": "storage",
                "description": "2MB QSPI Flash memory for data storage"
            },
            {
                "name": "Flexible Solar Panel",
                "type": "power",
                "description": "Thin-film solar panel for energy harvesting"
            },
            {
                "name": "Super Capacitor",
                "type": "power",
                "description": "Energy storage for operation during low light"
            },
            {
                "name": "E-Ink Display",
                "type": "interface",
                "description": "Low-power bistable display for visual data access"
            }
        ],
        estimated_total_cost_usd=45.0,
        estimated_lifespan_years=25.0,
        power_requirements_mw=5.0,  # Very low power with solar recharging
        performance_score=7.8,
        physical_dimensions_mm=[85.60, 53.98, 2.50],
        weight_grams=18.5,
        tags=["powered", "solar", "microcontroller", "interactive"]
    ),
    HardcardArchitecture(
        id="arch-printed-001",
        name="Flexible Printed Circuit",
        description="A flexible printed electronic circuit using conductive inks on polymer substrate",
        type="printed",
        components=[
            {
                "name": "Silver Nanoparticle Traces",
                "type": "circuitry",
                "description": "Conductive pathways using silver nanoparticle ink"
            },
            {
                "name": "Printed Memory Cells",
                "type": "storage",
                "description": "Non-volatile memory using printed organic electronics"
            },
            {
                "name": "Printed Battery",
                "type": "power",
                "description": "Thin-film printed zinc-air battery"
            },
            {
                "name": "Polymer Substrate",
                "type": "substrate",
                "description": "Flexible polyimide substrate with protective coating"
            }
        ],
        estimated_total_cost_usd=28.0,
        estimated_lifespan_years=15.0,
        power_requirements_mw=12.0,
        performance_score=5.5,
        physical_dimensions_mm=[85.60, 53.98, 0.5],
        weight_grams=8.2,
        tags=["printed", "flexible", "thin", "bendable"]
    ),
    HardcardArchitecture(
        id="arch-nano-001",
        name="Molecular Data Crystal",
        description="A nanoscale architecture using molecular computing and self-assembly",
        type="nano",
        components=[
            {
                "name": "DNA Storage Matrix",
                "type": "storage",
                "description": "Synthetic DNA strands encoding digital information"
            },
            {
                "name": "Quantum Dot Array",
                "type": "processing",
                "description": "Nanoscale quantum dots for computational functions"
            },
            {
                "name": "Molecular Logic Gates",
                "type": "logic",
                "description": "Chemical-based computing elements using molecular switches"
            },
            {
                "name": "Self-healing Encapsulation",
                "type": "protection",
                "description": "Biomimetic encapsulation with self-healing properties"
            }
        ],
        estimated_total_cost_usd=12000.0,  # Advanced research-grade technology
        estimated_lifespan_years=350.0,
        power_requirements_mw=0.001,  # Nearly passive with molecular energy harvesting
        performance_score=6.2,
        physical_dimensions_mm=[85.60, 53.98, 0.2],  # Very thin
        weight_grams=4.5,
        tags=["nano", "molecular", "quantum", "self-healing"]
    )
]


@router.get("/architectures")
def list_architectures():
    """List all available hardware architectures"""
    return {
        "architectures": SAMPLE_ARCHITECTURES,
        "count": len(SAMPLE_ARCHITECTURES)
    }


@router.get("/architectures/{architecture_id}")
def get_architecture(architecture_id: str):
    """Get details of a specific hardware architecture"""
    for arch in SAMPLE_ARCHITECTURES:
        if arch.id == architecture_id:
            return arch
    
    return {"error": "Architecture not found"}, 404


@router.post("/symbolic-geometry")
def generate_hardware_symbolic_geometry(request: SymbolicGeometryRequest) -> SymbolicGeometryResponse:
    """Generate symbolic geometry representation of a hardware architecture"""
    # Find the requested architecture
    architecture = None
    for arch in SAMPLE_ARCHITECTURES:
        if arch.id == request.architecture_id:
            architecture = arch
            break
    
    if not architecture:
        return {"error": "Architecture not found"}, 404
    
    # In a real implementation, we would generate actual SVG or graph data
    # For this prototype, we'll return placeholder data based on the architecture type
    
    component_names = [comp["name"] for comp in architecture.components]
    
    if request.format == "svg":
        if architecture.type == "passive":
            geometry_data = f"<svg width='500' height='300' xmlns='http://www.w3.org/2000/svg'>\n"
            geometry_data += f"  <rect x='50' y='50' width='400' height='200' fill='gold' opacity='0.7'/>\n"
            geometry_data += f"  <circle cx='250' cy='150' r='100' fill='none' stroke='black' stroke-width='2'/>\n"
            geometry_data += f"  <text x='250' y='150' text-anchor='middle'>{architecture.name}</text>\n"
            geometry_data += f"</svg>"
        elif architecture.type == "powered":
            geometry_data = f"<svg width='500' height='300' xmlns='http://www.w3.org/2000/svg'>\n"
            geometry_data += f"  <rect x='50' y='50' width='400' height='200' fill='lightblue' opacity='0.7'/>\n"
            geometry_data += f"  <rect x='100' y='100' width='100' height='100' fill='gray'/>\n"  # CPU
            geometry_data += f"  <rect x='300' y='100' width='100' height='50' fill='green'/>\n"  # Battery
            geometry_data += f"  <text x='250' y='150' text-anchor='middle'>{architecture.name}</text>\n"
            geometry_data += f"</svg>"
        elif architecture.type == "printed":
            geometry_data = f"<svg width='500' height='300' xmlns='http://www.w3.org/2000/svg'>\n"
            geometry_data += f"  <rect x='50' y='50' width='400' height='200' fill='lightgray' opacity='0.7'/>\n"
            geometry_data += f"  <path d='M100,100 L400,100 L400,200 L100,200 Z' fill='none' stroke='silver' stroke-width='3'/>\n"
            geometry_data += f"  <text x='250' y='150' text-anchor='middle'>{architecture.name}</text>\n"
            geometry_data += f"</svg>"
        else:  # nano
            geometry_data = f"<svg width='500' height='300' xmlns='http://www.w3.org/2000/svg'>\n"
            geometry_data += f"  <rect x='50' y='50' width='400' height='200' fill='lightpurple' opacity='0.5'/>\n"
            geometry_data += f"  <circle cx='150' cy='150' r='10' fill='blue'/>\n"
            geometry_data += f"  <circle cx='200' cy='150' r='10' fill='blue'/>\n"
            geometry_data += f"  <circle cx='250' cy='150' r='10' fill='blue'/>\n"
            geometry_data += f"  <text x='250' y='120' text-anchor='middle'>{architecture.name}</text>\n"
            geometry_data += f"</svg>"
    else:  # graph format
        nodes = []
        edges = []
        
        # Create a node for each component
        for i, comp in enumerate(architecture.components):
            nodes.append({
                "id": f"n{i}",
                "label": comp["name"],
                "type": comp["type"]
            })
        
        # Create some edges between components
        for i in range(len(nodes) - 1):
            edges.append({
                "source": f"n{i}",
                "target": f"n{i+1}",
                "label": "connects to"
            })
        
        geometry_data = {
            "nodes": nodes,
            "edges": edges
        }
    
    return SymbolicGeometryResponse(
        architecture_id=request.architecture_id,
        geometry_data=str(geometry_data),
        components_mapped=component_names,
        format=request.format
    )


@router.post("/evaluate")
def evaluate_architectures(request: HardwareEvaluationRequest) -> HardwareEvaluationResponse:
    """Evaluate and rank hardware architectures based on specified optimization goals"""
    # Validate optimization goals
    total_weight = sum(request.optimization_goals.values())
    if abs(total_weight - 1.0) > 0.01:  # Allow small rounding errors
        normalized_goals = {k: v/total_weight for k, v in request.optimization_goals.items()}
    else:
        normalized_goals = request.optimization_goals
    
    # Find requested architectures
    architectures_to_evaluate = []
    for arch_id in request.architecture_ids:
        for arch in SAMPLE_ARCHITECTURES:
            if arch.id == arch_id:
                architectures_to_evaluate.append(arch)
                break
    
    if not architectures_to_evaluate:
        return {"error": "No valid architectures found"}, 404
    
    # Evaluate each architecture
    evaluation_results = []
    for arch in architectures_to_evaluate:
        # Calculate individual scores (in a real system, these would be much more sophisticated)
        power_efficiency = 10.0 if arch.power_requirements_mw == 0 else 10.0 / (1 + arch.power_requirements_mw/10)
        durability = min(10.0, arch.estimated_lifespan_years / 50)  # Scale to 0-10
        computational_capacity = arch.performance_score
        cost_efficiency = 10.0 - min(10.0, arch.estimated_total_cost_usd / 1000)  # Lower cost is better
        weight_efficiency = 10.0 - min(10.0, arch.weight_grams / 20)  # Lower weight is better
        size_efficiency = 10.0 - min(10.0, arch.physical_dimensions_mm[2])  # Thinner is better
        
        # Calculate overall score based on optimization goals
        overall_score = (
            normalized_goals.get("power", 0) * power_efficiency +
            normalized_goals.get("durability", 0) * durability +
            normalized_goals.get("performance", 0) * computational_capacity +
            normalized_goals.get("cost", 0) * cost_efficiency +
            normalized_goals.get("weight", 0) * weight_efficiency +
            normalized_goals.get("size", 0) * size_efficiency
        )
        
        # Check constraints if provided
        meets_constraints = True
        constraint_violations = []
        if request.constraints:
            if request.constraints.get("max_cost") and arch.estimated_total_cost_usd > request.constraints["max_cost"]:
                meets_constraints = False
                constraint_violations.append(f"Cost exceeds maximum: ${arch.estimated_total_cost_usd} > ${request.constraints['max_cost']}")
            
            if request.constraints.get("min_lifespan") and arch.estimated_lifespan_years < request.constraints["min_lifespan"]:
                meets_constraints = False
                constraint_violations.append(f"Lifespan below minimum: {arch.estimated_lifespan_years} years < {request.constraints['min_lifespan']} years")
            
            if request.constraints.get("max_power") and arch.power_requirements_mw > request.constraints["max_power"]:
                meets_constraints = False
                constraint_violations.append(f"Power requirement exceeds maximum: {arch.power_requirements_mw} mW > {request.constraints['max_power']} mW")
        
        # Create evaluation result
        result = HardwareEvaluationResult(
            architecture_id=arch.id,
            architecture_name=arch.name,
            scores=HardwareScores(
                power_efficiency=power_efficiency,
                durability=durability,
                computational_capacity=computational_capacity,
                cost_efficiency=cost_efficiency,
                weight_efficiency=weight_efficiency,
                size_efficiency=size_efficiency,
                overall_score=overall_score
            ),
            meets_constraints=meets_constraints,
            constraint_violations=constraint_violations,
            rank=0  # Will be set after sorting
        )
        
        evaluation_results.append(result)
    
    # Sort results by overall score (descending)
    evaluation_results.sort(key=lambda x: x.scores.overall_score, reverse=True)
    
    # Assign ranks
    for i, result in enumerate(evaluation_results):
        result.rank = i + 1
    
    # Find best architecture (that meets constraints)
    valid_results = [r for r in evaluation_results if r.meets_constraints]
    best_architecture_id = valid_results[0].architecture_id if valid_results else evaluation_results[0].architecture_id
    
    return HardwareEvaluationResponse(
        results=evaluation_results,
        best_architecture_id=best_architecture_id,
        optimization_goals_used=normalized_goals
    )


@router.get("/optimal-stack/{architecture_id}")
def get_optimal_stack(architecture_id: str) -> OptimalStackResponse:
    """Get the optimal hardware stack (BOM and build instructions) for a specific architecture"""
    # Find the requested architecture
    architecture = None
    for arch in SAMPLE_ARCHITECTURES:
        if arch.id == architecture_id:
            architecture = arch
            break
    
    if not architecture:
        return {"error": "Architecture not found"}, 404
    
    # Convert architecture components to stack components
    components = []
    for comp in architecture.components:
        component = OptimalStackComponent(
            name=comp["name"],
            type=comp["type"],
            description=comp["description"],
            quantity=1,
            unit_cost_usd=random.uniform(5, 2000),  # In a real system, this would come from a parts database
            total_cost_usd=0,  # Will be calculated
            alternatives=[f"Alternative {comp['name']} {i}" for i in range(1, 3)]  # Sample alternatives
        )
        component.total_cost_usd = component.unit_cost_usd * component.quantity
        components.append(component)
    
    # Generate tools and fabrication methods based on architecture type
    if architecture.type == "passive":
        tools = ["Precision laser cutter", "Optical microscope", "Polishing equipment"]
        fabrication = ["Crystal growing", "Precision engraving", "Optical alignment"]
        complexity = 8.5
    elif architecture.type == "powered":
        tools = ["Soldering iron", "Multimeter", "Programmer", "Microscope"]
        fabrication = ["PCB assembly", "Microcontroller programming", "Battery integration"]
        complexity = 6.0
    elif architecture.type == "printed":
        tools = ["Screen printer", "UV curing station", "Thermal annealer"]
        fabrication = ["Screen printing", "Inkjet printing", "Thermal curing"]
        complexity = 7.2
    else:  # nano
        tools = ["Electron microscope", "Molecular assembler", "Clean room equipment"]
        fabrication = ["Molecular self-assembly", "DNA origami", "Quantum dot synthesis"]
        complexity = 9.8
    
    # Calculate total cost and build time
    total_cost = sum(comp.total_cost_usd for comp in components)
    # Build time is based on complexity and number of components
    build_time = complexity * 0.5 * len(components)
    
    return OptimalStackResponse(
        architecture_id=architecture.id,
        architecture_name=architecture.name,
        total_cost_usd=total_cost,
        estimated_build_time_hours=build_time,
        components=components,
        tools_required=tools,
        fabrication_methods=fabrication,
        assembly_instructions_url=f"/documentation/assembly/{architecture.id}.pdf",  # Placeholder URL
        build_complexity_score=complexity
    )


@router.post("/feedback")
def log_build_feedback(request: FeedbackLoggingRequest) -> FeedbackLoggingResponse:
    """Log feedback from real hardware builds for continual improvement"""
    # In a real system, this would store the feedback in a database and update the optimization models
    
    # Generate some learning points based on the feedback
    learning_points = []
    
    if not request.build_successful:
        learning_points.append("Build failure indicates potential design issues that need addressing")
    
    if request.actual_build_time_hours > 0:
        # Compare actual vs. estimated build time
        # In a real system, we'd retrieve the estimated time from the database
        estimated_time = 10.0  # Placeholder
        time_ratio = request.actual_build_time_hours / estimated_time
        if time_ratio > 1.5:
            learning_points.append(f"Build took {time_ratio:.1f}x longer than estimated, suggesting complexity underestimation")
        elif time_ratio < 0.75:
            learning_points.append(f"Build was faster than estimated, suggesting complexity overestimation")
    
    if request.actual_cost_usd > 0:
        # Compare actual vs. estimated cost
        # In a real system, we'd retrieve the estimated cost from the database
        for arch in SAMPLE_ARCHITECTURES:
            if arch.id == request.architecture_id:
                estimated_cost = arch.estimated_total_cost_usd
                cost_ratio = request.actual_cost_usd / estimated_cost
                if cost_ratio > 1.2:
                    learning_points.append(f"Cost was {cost_ratio:.1f}x higher than estimated, requiring budget adjustment")
                elif cost_ratio < 0.8:
                    learning_points.append(f"Cost was lower than estimated, suggesting efficiency opportunities")
                break
    
    # Process issues and improvements
    for issue in request.issues_encountered:
        learning_points.append(f"Issue to address: {issue}")
    
    for improvement in request.improvements_suggested:
        learning_points.append(f"Potential improvement: {improvement}")
    
    # Calculate a score adjustment based on feedback
    performance_influence = (request.performance_rating - 5) / 5  # -1 to 1 scale
    durability_influence = (request.durability_rating - 5) / 5  # -1 to 1 scale
    success_influence = 0.5 if request.build_successful else -0.5
    
    score_adjustment = (performance_influence + durability_influence + success_influence) / 3
    score_adjustment = round(score_adjustment * 100) / 100  # Round to 2 decimal places
    
    return FeedbackLoggingResponse(
        success=True,
        feedback_id=f"feedback-{random.randint(1000, 9999)}",
        learning_points=learning_points,
        architecture_score_adjustment=score_adjustment
    )


@router.get("/hardware-finder")
def find_matching_hardware(use_case: str, power_available: bool = True, budget_usd: float = 1000.0):
    """Find matching hardware for a specific use case"""
    # Parse the use case to determine requirements
    use_cases = {
        "archival": {
            "durability_weight": 0.6,
            "cost_weight": 0.2,
            "power_weight": 0.1,
            "performance_weight": 0.1,
            "preferred_type": "passive"
        },
        "interactive": {
            "durability_weight": 0.2,
            "cost_weight": 0.3,
            "power_weight": 0.1,
            "performance_weight": 0.4,
            "preferred_type": "powered"
        },
        "portable": {
            "durability_weight": 0.3,
            "cost_weight": 0.2,
            "power_weight": 0.3,
            "performance_weight": 0.2,
            "preferred_type": "printed"
        },
        "experimental": {
            "durability_weight": 0.2,
            "cost_weight": 0.1,
            "power_weight": 0.3,
            "performance_weight": 0.4,
            "preferred_type": "nano"
        }
    }
    
    # Default weights if use case not recognized
    weights = use_cases.get(use_case.lower(), {
        "durability_weight": 0.25,
        "cost_weight": 0.25,
        "power_weight": 0.25,
        "performance_weight": 0.25,
        "preferred_type": None
    })
    
    # Filter architectures by budget and power availability
    filtered_architectures = []
    for arch in SAMPLE_ARCHITECTURES:
        if arch.estimated_total_cost_usd <= budget_usd:
            if not power_available and arch.power_requirements_mw > 0:
                continue  # Skip powered architectures if no power is available
            filtered_architectures.append(arch)
    
    if not filtered_architectures:
        return {"message": "No matching hardware found within constraints"}
    
    # Score each architecture
    scored_architectures = []
    for arch in filtered_architectures:
        # Normalize scores to 0-1 scale
        durability_score = min(1.0, arch.estimated_lifespan_years / 500)  # Assuming 500 years is max
        cost_score = 1.0 - min(1.0, arch.estimated_total_cost_usd / budget_usd)
        power_score = 1.0 if arch.power_requirements_mw == 0 else 1.0 - min(1.0, arch.power_requirements_mw / 100)
        performance_score = arch.performance_score / 10.0  # Assuming 10 is max
        
        # Type preference bonus
        type_bonus = 0.2 if weights["preferred_type"] and arch.type == weights["preferred_type"] else 0
        
        # Calculate total score
        total_score = (
            durability_score * weights["durability_weight"] +
            cost_score * weights["cost_weight"] +
            power_score * weights["power_weight"] +
            performance_score * weights["performance_weight"] +
            type_bonus
        )
        
        scored_architectures.append({
            "architecture": arch,
            "score": total_score,
            "type_match": arch.type == weights.get("preferred_type")
        })
    
    # Sort by score
    scored_architectures.sort(key=lambda x: x["score"], reverse=True)
    top_matches = scored_architectures[:3]  # Get top 3
    
    return {
        "use_case": use_case,
        "power_available": power_available,
        "budget_usd": budget_usd,
        "matches": [
            {
                "architecture_id": match["architecture"].id,
                "name": match["architecture"].name,
                "score": match["score"],
                "type": match["architecture"].type,
                "type_match": match["type_match"],
                "estimated_cost_usd": match["architecture"].estimated_total_cost_usd,
                "estimated_lifespan_years": match["architecture"].estimated_lifespan_years,
                "power_requirements_mw": match["architecture"].power_requirements_mw,
                "performance_score": match["architecture"].performance_score
            } for match in top_matches
        ]
    }
