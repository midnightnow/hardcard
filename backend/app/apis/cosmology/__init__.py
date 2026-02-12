from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
from fastapi import APIRouter
import math
import random

router = APIRouter()


class SingularitasModel(BaseModel):
    description: str
    mathematical_representation: str
    philosophical_analog: str


class MetricModel(BaseModel):
    description: str
    tensor_representation: str
    cosmological_significance: str


class PrimeFoundationModel(BaseModel):
    singularitas: SingularitasModel
    metric: MetricModel


class FundamentalForceModel(BaseModel):
    name: str
    symbol: str
    description: str
    equation: str
    mythic_significance: str


class CosmicWheelModel(BaseModel):
    name: str
    description: str
    sub_structures: List[Dict[str, Any]]
    parent_forces: List[str]
    visual_representation: Dict[str, Any]


class FractalDetailModel(BaseModel):
    name: str
    description: str
    mathematical_representation: str
    visual_properties: Dict[str, Any]
    recursive_pattern: str
    dimensional_depth: int


class SymbolicGeometryRequest(BaseModel):
    format: str = "svg"
    resolution: str = "medium"
    include_fractal_detail: bool = True
    wheel_name: Optional[str] = None
    force_name: Optional[str] = None


class SymbolicGeometryResponse(BaseModel):
    svg_content: Optional[str] = None
    canvas_instructions: Optional[List[Dict[str, Any]]] = None
    fractal_components: Optional[List[Dict[str, Any]]] = None


class CosmologyModel(BaseModel):
    prime_foundation: PrimeFoundationModel
    fundamental_forces: List[FundamentalForceModel]
    cosmic_wheels: List[CosmicWheelModel]
    fractal_details: Optional[List[FractalDetailModel]] = None


@router.get("/cosmology-framework-core")
def get_cosmology_framework_core() -> CosmologyModel:
    """
    Returns the complete cosmological framework structure including the Prime Foundation (Singularitas),
    the Four Eternal Axles (Fundamental Forces), and the Wheels of the Cosmos (cosmic architecture).
    """
    return CosmologyModel(
        prime_foundation=PrimeFoundationModel(
            singularitas=SingularitasModel(
                description="In the beginning, the cosmos lay compressed into a point of incomputable density and curvature—both origin and boundary of spacetime.",
                mathematical_representation="A mathematical regime where General Relativity and Quantum Mechanics converge into undefined extremes.",
                philosophical_analog="Just as Dante described an ineffable center of divine light, so does Singularitas stand beyond normal measure or direct analysis."
            ),
            metric=MetricModel(
                description="The Metric Tensor as the immediate embodiment of the cosmos, giving shape to the stage on which matter, light, and energy interplay.",
                tensor_representation="g_{\\mu\\nu}",
                cosmological_significance="This 'holy grammar' of spacetime guides the curvature that births galaxies, black holes, and the entire cosmic wheel."
            )
        ),
        fundamental_forces=[
            FundamentalForceModel(
                name="Gravitas",
                symbol="G",
                description="Gravity binds the cosmic spheres and sets them in their majesty of orbits.",
                equation="\\nabla_\\mu G_{\\nu}^{\\mu} = 8 \\pi T_{\\nu}^{\\mu}",
                mythic_significance="The first axle, drawing all matter into cosmic choreography."
            ),
            FundamentalForceModel(
                name="Lumenflux",
                symbol="EM",
                description="Electromagnetism embodies all radiant energy, from the soft glow of nebulae to the blaze of stars.",
                equation="\\nabla \\cdot \\mathbf{E} = \\rho/\\epsilon_0",
                mythic_significance="The great illuminator, bridging regions of space at the finite yet unstoppable speed c."
            ),
            FundamentalForceModel(
                name="Fortis",
                symbol="QCD",
                description="The Strong Nuclear Force keeps protons and neutrons intact, forging the chemical elements.",
                equation="SU(3) gauge theory of color charge",
                mythic_significance="Without Fortis, all nuclei would dissolve into quarks—no stable stage upon which life might arise."
            ),
            FundamentalForceModel(
                name="Transitus",
                symbol="W",
                description="The Weak Nuclear Force manifests in decays and transmutations of particles.",
                equation="SU(2) × U(1) electroweak interaction",
                mythic_significance="Ensures the cycles of stellar alchemy, from hydrogen fusion to the final metamorphoses in dying stars."
            )
        ],
        cosmic_wheels=[
            CosmicWheelModel(
                name="Wheel of Particle Fields",
                description="The innermost 'circle,' hosting the Quantum Fields for electrons, quarks, photons, gluons, etc.",
                sub_structures=[
                    {"name": "Fermion Fields", "description": "Matter particles like electrons and quarks"},
                    {"name": "Boson Fields", "description": "Force-carrying particles like photons and gluons"},
                    {"name": "Quantum Vacuum", "description": "The perpetual interplay of creation and annihilation operators"}
                ],
                parent_forces=["Fortis", "Transitus", "Lumenflux"],
                visual_representation={
                    "shape": "fractal_network",
                    "color": "quantum_blue",
                    "animation": "fluctuation"
                }
            ),
            CosmicWheelModel(
                name="Wheel of Stellar Forges",
                description="Spans from proto-stellar nebulae to supernova cataclysms, where matter is transmuted and heavy elements are forged.",
                sub_structures=[
                    {"name": "Stellar Nurseries", "description": "Clouds of gas and dust where stars are born"},
                    {"name": "Main Sequence Stars", "description": "Stars in stable hydrogen fusion"},
                    {"name": "Supernovae", "description": "Explosive stellar deaths creating heavier elements"}
                ],
                parent_forces=["Gravitas", "Fortis"],
                visual_representation={
                    "shape": "spiral_cluster",
                    "color": "stellar_gold",
                    "animation": "pulsation"
                }
            ),
            CosmicWheelModel(
                name="Wheel of Galactic Harmonies",
                description="Galaxies swirl in gravitational dance, forming spiral arms akin to cosmic filigree.",
                sub_structures=[
                    {"name": "Galactic Cores", "description": "Central black holes and dense star clusters"},
                    {"name": "Spiral Arms", "description": "Star-forming regions in pinwheel patterns"},
                    {"name": "Galactic Halos", "description": "Spherical regions of dark matter and old stars"}
                ],
                parent_forces=["Gravitas"],
                visual_representation={
                    "shape": "spiral_galaxy",
                    "color": "cosmic_purple",
                    "animation": "rotation"
                }
            ),
            CosmicWheelModel(
                name="Wheel of Universal Expansion",
                description="The outermost progression, defined by Hubble's Law and the evolving scale factor of the universe.",
                sub_structures=[
                    {"name": "Cosmic Web", "description": "The largest structure in the universe, with filaments of galaxies"},
                    {"name": "Voids", "description": "Vast empty regions between galaxy clusters"},
                    {"name": "Dark Energy Field", "description": "The mysterious force accelerating cosmic expansion"}
                ],
                parent_forces=["Gravitas", "Dark Energy"],
                visual_representation={
                    "shape": "expanding_lattice",
                    "color": "void_black",
                    "animation": "expansion"
                }
            )
        ],
        fractal_details=[
            FractalDetailModel(
                name="Quantum Recursion",
                description="Every line in every moment splits into curves, circles, and spirals to the power of n, mirroring the fractal grammar of the quantum realm.",
                mathematical_representation="z → z² + c (Mandelbrot iteration)",
                visual_properties={
                    "base_color": "quantum_blue",
                    "iteration_depth": 7,
                    "branching_factor": 4
                },
                recursive_pattern="self-similar quantum fluctuations at increasingly finer scales",
                dimensional_depth=11
            ),
            FractalDetailModel(
                name="Celestial Filigree",
                description="The interwoven patterns of stellar formations reveal mathematical harmonies that repeat at different scales throughout the cosmos.",
                mathematical_representation="Golden ratio (φ) spirals embedded in nested pentagonal structures",
                visual_properties={
                    "base_color": "stellar_gold",
                    "iteration_depth": 5,
                    "branching_factor": 5
                },
                recursive_pattern="golden spirals that nest inward and expand outward simultaneously",
                dimensional_depth=7
            ),
            FractalDetailModel(
                name="Cosmic Lattice",
                description="The fabric of spacetime itself exhibits an 'exceedingly fine' gridwork that becomes increasingly complex as one examines smaller scales.",
                mathematical_representation="Planck-scale spacetime foam with topological fluctuations",
                visual_properties={
                    "base_color": "cosmic_purple",
                    "iteration_depth": 9,
                    "branching_factor": 3
                },
                recursive_pattern="interlocking geometric forms that become increasingly detailed at finer scales",
                dimensional_depth=10
            ),
            FractalDetailModel(
                name="Wheels within Wheels",
                description="Each cosmic wheel contains smaller wheels grinding within it, revealing new structures and patterns at each level of examination.",
                mathematical_representation="Nested toroidal manifolds with varying rotational vectors",
                visual_properties={
                    "base_color": "amber_gold",
                    "iteration_depth": 6,
                    "branching_factor": 7
                },
                recursive_pattern="concentric wheels that spin on different axes, each containing smaller wheels",
                dimensional_depth=9
            )
        ]
    )


@router.get("/wheel/{wheel_name}")
def get_cosmic_wheel(wheel_name: str) -> CosmicWheelModel:
    """
    Returns details for a specific cosmic wheel by name.
    """
    # This would normally query a database, but for simplicity we're recreating the data here
    cosmology = get_cosmology_framework_core()
    for wheel in cosmology.cosmic_wheels:
        if wheel.name.lower().replace(" ", "_") == wheel_name.lower().replace(" ", "_"):
            return wheel
    
    # Return a default wheel if not found
    result = CosmicWheelModel(
        name="Unknown Wheel",
        description="This cosmic structure has not yet been discovered or mapped within the exceedingly fine grid of cosmic reality.",
        sub_structures=[{"name": "Unknown Component", "description": "Undefined fractal component"}],
        parent_forces=[],
        visual_representation={"shape": "unknown", "color": "gray", "animation": "none"}
    ).dict()
    return result


@router.get("/force/{force_name}")
def get_fundamental_force(force_name: str) -> FundamentalForceModel:
    """
    Returns details for a specific fundamental force by name.
    """
    cosmology = get_cosmology_framework_core()
    for force in cosmology.fundamental_forces:
        if force.name.lower() == force_name.lower():
            return force
    
    # Return a default force if not found
    return FundamentalForceModel(
        name="Unknown Force",
        symbol="?",
        description="This fundamental force has not yet been discovered or mapped.",
        equation="Unknown",
        mythic_significance="Unknown"
    )


@router.post("/symbolic-geometry")
def generate_symbolic_geometry4(request: SymbolicGeometryRequest) -> SymbolicGeometryResponse:
    """
    Generates a symbolic geometric representation of the cosmic framework,
    including fractal details that illustrate the 'exceedingly fine' nature
    of the cosmic wheels and their recursive structures.
    
    The geometry implements the concept of "exceedingly fine and still grinding ^n",
    where each level of detail reveals further levels of complexity in a
    recursive pattern that demonstrates the fractal nature of the cosmos.
    Each wheel contains smaller wheels that grind within it, revealing new
    structures at each level of examination.
    """
    # Generate SVG or canvas instructions based on request format
    if request.format == "svg":
        return generate_svg_representation(request)
    else:
        return generate_canvas_instructions(request)


def generate_svg_representation(request: SymbolicGeometryRequest) -> SymbolicGeometryResponse:
    """Generate SVG representation of cosmic geometry"""
    # Base dimensions
    width = 800
    height = 800
    center_x = width / 2
    center_y = height / 2
    max_radius = min(width, height) * 0.45
    
    # Start SVG content
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += f'<rect width="{width}" height="{height}" fill="#0a0a14" />\n'
    
    # Get cosmology data
    cosmology = get_cosmology_framework_core()
    
    # Add defs for gradients and patterns
    svg += '<defs>\n'
    
    # Gold radial gradient for singularity
    svg += '''  <radialGradient id="singularityGlow" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">\n
  <stop offset="0%" stop-color="#fff0c0" stop-opacity="1" />\n
  <stop offset="25%" stop-color="#ffd700" stop-opacity="0.8" />\n
  <stop offset="100%" stop-color="#b8860b" stop-opacity="0" />\n
</radialGradient>\n'''
    
    # Advanced fractal patterns - exceedingly fine and still grinding ^n
    svg += '''  <pattern id="fractalPattern1" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">\n
  <path d="M0,20 Q10,0 20,20 Q30,40 40,20" stroke="rgba(255, 215, 0, 0.3)" fill="none" stroke-width="0.5" />\n
  <path d="M0,10 Q20,30 40,10" stroke="rgba(255, 215, 0, 0.2)" fill="none" stroke-width="0.3" />\n
  <circle cx="20" cy="20" r="2" stroke="rgba(255, 215, 0, 0.4)" fill="none" />\n
</pattern>\n'''
    
    svg += '''  <pattern id="fractalPattern2" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">\n
  <circle cx="15" cy="15" r="5" stroke="rgba(100, 200, 255, 0.3)" fill="none" stroke-width="0.5" />\n
  <circle cx="15" cy="15" r="10" stroke="rgba(100, 200, 255, 0.2)" fill="none" stroke-width="0.3" />\n
  <path d="M5,15 L25,15" stroke="rgba(100, 200, 255, 0.2)" stroke-width="0.2" />\n
  <path d="M15,5 L15,25" stroke="rgba(100, 200, 255, 0.2)" stroke-width="0.2" />\n
</pattern>\n'''
    
    # Spiral pattern for wheels
    svg += '''  <pattern id="spiralPattern" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse">\n
  <path d="M25,25 L30,20 A15,15 0 0 1 35,25 A10,10 0 0 1 30,35 A5,5 0 0 1 20,30 A2,2 0 0 1 25,25" 
        stroke="rgba(255, 180, 0, 0.2)" fill="none" stroke-width="0.3" />\n
</pattern>\n'''
    
    # Recursive grid pattern
    svg += '''  <pattern id="recursiveGrid" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">\n
  <path d="M0,0 L100,0 L100,100 L0,100 Z" stroke="rgba(120, 140, 180, 0.1)" fill="none" stroke-width="0.2" />\n
  <path d="M25,25 L75,25 L75,75 L25,75 Z" stroke="rgba(120, 140, 180, 0.15)" fill="none" stroke-width="0.3" />\n
  <path d="M40,40 L60,40 L60,60 L40,60 Z" stroke="rgba(120, 140, 180, 0.2)" fill="none" stroke-width="0.4" />\n
  <path d="M45,45 L55,45 L55,55 L45,55 Z" stroke="rgba(120, 140, 180, 0.25)" fill="none" stroke-width="0.5" />\n
</pattern>\n'''
    
    svg += '</defs>\n'
    
    # Draw background grid with subtle pattern
    svg += f'<rect width="{width}" height="{height}" fill="url(#fractalPattern1)" opacity="0.1" />\n'
    
    # Draw cosmic wheels as concentric circles
    wheels = cosmology.cosmic_wheels
    num_wheels = len(wheels)
    
    for i, wheel in enumerate(wheels):
        # Calculate radius based on position (outer to inner)
        radius = max_radius * (1 - i * 0.2)
        
        # Add wheel circle
        wheel_color = get_color_for_wheel(wheel.name)
        svg += f'<circle cx="{center_x}" cy="{center_y}" r="{radius}" '
        svg += f'stroke="{wheel_color}" stroke-width="2" fill="none" '
        svg += f'stroke-dasharray="4 2" opacity="0.6" />\n'
        
        # Add label
        label_angle = 45 + i * 90  # Positioning labels at different angles
        label_x = center_x + (radius * 0.9) * math.cos(math.radians(label_angle))
        label_y = center_y + (radius * 0.9) * math.sin(math.radians(label_angle))
        svg += f'<text x="{label_x}" y="{label_y}" fill="{wheel_color}" font-size="12" '
        svg += f'text-anchor="middle" transform="rotate({label_angle}, {label_x}, {label_y})">{wheel.name}</text>\n'
        
        # Add fractal details for each wheel if requested
        if request.include_fractal_detail:
            add_fractal_details_svg(svg, wheel, center_x, center_y, radius, i)
    
    # Draw fundamental forces as radial axes
    forces = cosmology.fundamental_forces
    num_forces = len(forces)
    
    for i, force in enumerate(forces):
        angle = (i * 360 / num_forces) + 45  # Offset by 45 degrees
        end_x = center_x + max_radius * math.cos(math.radians(angle))
        end_y = center_y + max_radius * math.sin(math.radians(angle))
        
        force_color = get_color_for_force(force.name)
        svg += f'<line x1="{center_x}" y1="{center_y}" x2="{end_x}" y2="{end_y}" '
        svg += f'stroke="{force_color}" stroke-width="1.5" opacity="0.7" />\n'
        
        # Add force label
        label_distance = max_radius * 0.8
        label_x = center_x + label_distance * math.cos(math.radians(angle))
        label_y = center_y + label_distance * math.sin(math.radians(angle))
        
        svg += f'<circle cx="{label_x}" cy="{label_y}" r="15" fill="{force_color}" opacity="0.2" />\n'
        svg += f'<text x="{label_x}" y="{label_y}" fill="{force_color}" font-size="10" '
        svg += f'text-anchor="middle" dominant-baseline="middle">{force.symbol}</text>\n'
    
    # Draw the singularity at the center
    svg += f'<circle cx="{center_x}" cy="{center_y}" r="15" fill="url(#singularityGlow)" />\n'
    svg += f'<circle cx="{center_x}" cy="{center_y}" r="5" fill="#ffd700" />\n'
    
    # Add particles
    if request.include_fractal_detail:
        # Add dynamic particles around the structure
        for _ in range(100):
            particle_radius = random.uniform(0.5, 2)
            distance = random.uniform(0, max_radius * 1.1)
            angle = random.uniform(0, 360)
            p_x = center_x + distance * math.cos(math.radians(angle))
            p_y = center_y + distance * math.sin(math.radians(angle))
            opacity = random.uniform(0.3, 0.8)
            p_color = random.choice(['#ffd700', '#88ccff', '#ff88aa', '#88ffaa'])
            
            svg += f'<circle cx="{p_x}" cy="{p_y}" r="{particle_radius}" '
            svg += f'fill="{p_color}" opacity="{opacity}" />\n'
    
    # Close SVG
    svg += '</svg>'
    
    # Generate fractal components data for frontend to use in animations
    fractal_components = []
    
    for detail in cosmology.fractal_details:
        fractal_components.append({
            "name": detail.name,
            "depth": detail.dimensional_depth,
            "pattern": detail.recursive_pattern,
            "color": detail.visual_properties.get("base_color", "gold"),
            "iterations": detail.visual_properties.get("iteration_depth", 5),
            "branching": detail.visual_properties.get("branching_factor", 4)
        })
    
    return SymbolicGeometryResponse(
        svg_content=svg,
        fractal_components=fractal_components
    )


def add_fractal_details_svg(svg, wheel, center_x, center_y, radius, wheel_index):
    """Add fractal details to the SVG for a specific wheel - exceedingly fine and still grinding ^n"""
    # Different fractal patterns based on wheel type
    if wheel.name == "Wheel of Particle Fields":
        # Quantum field fluctuations - with recursive details
        num_circles = 30 + wheel_index * 10
        for _ in range(num_circles):
            circle_radius = random.uniform(0.5, 3)
            distance = random.uniform(radius * 0.7, radius * 0.95)
            angle = random.uniform(0, 360)
            cx = center_x + distance * math.cos(math.radians(angle))
            cy = center_y + distance * math.sin(math.radians(angle))
            opacity = random.uniform(0.2, 0.6)
            
            svg += f'<circle cx="{cx}" cy="{cy}" r="{circle_radius}" '
            svg += f'fill="#88ccff" opacity="{opacity}" />\n'
            
            # Add recursive detail to some particles - "exceedingly fine"
            if random.random() < 0.3:  # Only 30% of particles get recursive details
                # Add orbital paths around some particles
                num_orbits = random.randint(1, 3)
                for i in range(num_orbits):
                    orbit_radius = circle_radius * (1.5 + i * 0.8)
                    svg += f'<circle cx="{cx}" cy="{cy}" r="{orbit_radius}" '
                    svg += f'stroke="#88ccff" stroke-width="0.2" fill="none" '
                    svg += f'opacity="{opacity * 0.7}" />\n'
                    
                    # Add sub-particles in orbit - grinding ^n
                    num_sub_particles = random.randint(2, 4)
                    for j in range(num_sub_particles):
                        sub_angle = random.uniform(0, 360)
                        sub_radius = circle_radius * 0.3
                        sub_cx = cx + orbit_radius * math.cos(math.radians(sub_angle))
                        sub_cy = cy + orbit_radius * math.sin(math.radians(sub_angle))
                        
                        svg += f'<circle cx="{sub_cx}" cy="{sub_cy}" r="{sub_radius}" '
                        svg += f'fill="#aaddff" opacity="{opacity * 0.8}" />\n'
                        
                        # Recursive sub-sub-particles - grinding ^n^n
                        if random.random() < 0.4:  # Further recursion for 40% of sub-particles
                            sub_sub_radius = sub_radius * 0.4
                            sub_orbit_radius = sub_radius * 2
                            sub_sub_cx = sub_cx + sub_orbit_radius * math.cos(math.radians(sub_angle + 120))
                            sub_sub_cy = sub_cy + sub_orbit_radius * math.sin(math.radians(sub_angle + 120))
                            
                            svg += f'<circle cx="{sub_sub_cx}" cy="{sub_sub_cy}" r="{sub_sub_radius}" '
                            svg += f'fill="#ccffff" opacity="{opacity * 0.7}" />\n'
                            svg += f'<line x1="{sub_cx}" y1="{sub_cy}" x2="{sub_sub_cx}" y2="{sub_sub_cy}" '
                            svg += f'stroke="#ccffff" stroke-width="0.1" opacity="{opacity * 0.5}" />\n'
            
    elif wheel.name == "Wheel of Stellar Forges":
        # Star-like points in a ring
        num_stars = 12 + wheel_index * 2
        for i in range(num_stars):
            angle = i * 360 / num_stars
            distance = radius * random.uniform(0.85, 0.95)
            px = center_x + distance * math.cos(math.radians(angle))
            py = center_y + distance * math.sin(math.radians(angle))
            
            # Create a star shape
            points = []
            star_radius_outer = random.uniform(3, 7)
            star_radius_inner = star_radius_outer * 0.4
            
            for j in range(10):
                r = star_radius_outer if j % 2 == 0 else star_radius_inner
                a = math.radians(j * 36)
                points.append(f"{px + r * math.cos(a)},{py + r * math.sin(a)}")
            
            points_str = ' '.join(points)
            svg += f'<polygon points="{points_str}" fill="#ffcc00" opacity="0.7" />\n'
            
    elif wheel.name == "Wheel of Galactic Harmonies":
        # Spiral arms
        num_arms = 5
        for arm in range(num_arms):
            start_angle = arm * 360 / num_arms
            points = []
            points.append(f"{center_x},{center_y}")
            
            for i in range(30):
                angle = start_angle + i * 20
                distance = radius * (0.2 + i * 0.03)
                px = center_x + distance * math.cos(math.radians(angle))
                py = center_y + distance * math.sin(math.radians(angle))
                points.append(f"{px},{py}")
            
            points_str = ' '.join(points)
            svg += f'<polyline points="{points_str}" '
            svg += f'stroke="#cc88ff" stroke-width="1.5" fill="none" opacity="0.4" />\n'
            
    else:  # Wheel of Universal Expansion or others
        # Grid pattern with expanding cells
        cells = 6 + wheel_index
        for i in range(cells):
            cell_radius = radius * (0.2 + 0.8 * i / cells)
            svg += f'<circle cx="{center_x}" cy="{center_y}" r="{cell_radius}" '
            svg += f'stroke="#aaaaff" stroke-width="0.5" fill="none" '
            svg += f'opacity="{0.1 + 0.4 * i / cells}" />\n'
            
            # Add connecting lines
            if i > 0:
                num_lines = 6 + i * 2
                for j in range(num_lines):
                    angle = j * 360 / num_lines
                    inner_radius = radius * (0.2 + 0.8 * (i-1) / cells)
                    outer_radius = cell_radius
                    
                    inner_x = center_x + inner_radius * math.cos(math.radians(angle))
                    inner_y = center_y + inner_radius * math.sin(math.radians(angle))
                    outer_x = center_x + outer_radius * math.cos(math.radians(angle))
                    outer_y = center_y + outer_radius * math.sin(math.radians(angle))
                    
                    svg += f'<line x1="{inner_x}" y1="{inner_y}" x2="{outer_x}" y2="{outer_y}" '
                    svg += f'stroke="#8888ff" stroke-width="0.5" opacity="0.3" />\n'


def generate_canvas_instructions(request: SymbolicGeometryRequest) -> SymbolicGeometryResponse:
    """Generate canvas drawing instructions for frontend implementation with exceedingly fine detail"""
    # Base dimensions
    width = 800
    height = 800
    center_x = width / 2
    center_y = height / 2
    max_radius = min(width, height) * 0.45
    
    # Get cosmology data
    cosmology = get_cosmology_framework_core()
    
    # Prepare instructions list
    instructions = []
    
    # Background
    instructions.append({
        "type": "fill_rect",
        "x": 0,
        "y": 0,
        "width": width,
        "height": height,
        "color": "#0a0a14"
    })
    
    # Draw cosmic wheels
    wheels = cosmology.cosmic_wheels
    for i, wheel in enumerate(wheels):
        radius = max_radius * (1 - i * 0.2)
        wheel_color = get_color_for_wheel(wheel.name)
        
        instructions.append({
            "type": "stroke_circle",
            "x": center_x,
            "y": center_y,
            "radius": radius,
            "color": wheel_color,
            "lineWidth": 2,
            "dashPattern": [4, 2],
            "opacity": 0.6
        })
        
        # Wheel label
        label_angle = 45 + i * 90
        label_x = center_x + (radius * 0.9) * math.cos(math.radians(label_angle))
        label_y = center_y + (radius * 0.9) * math.sin(math.radians(label_angle))
        
        instructions.append({
            "type": "text",
            "x": label_x,
            "y": label_y,
            "text": wheel.name,
            "color": wheel_color,
            "fontSize": 12,
            "textAlign": "center",
            "rotation": label_angle
        })
        
        # Add wheel-specific fractal details
        if request.include_fractal_detail:
            add_fractal_details_canvas(instructions, wheel, center_x, center_y, radius, i)
    
    # Draw fundamental forces
    forces = cosmology.fundamental_forces
    num_forces = len(forces)
    
    for i, force in enumerate(forces):
        angle = (i * 360 / num_forces) + 45
        end_x = center_x + max_radius * math.cos(math.radians(angle))
        end_y = center_y + max_radius * math.sin(math.radians(angle))
        
        force_color = get_color_for_force(force.name)
        
        instructions.append({
            "type": "line",
            "x1": center_x,
            "y1": center_y,
            "x2": end_x,
            "y2": end_y,
            "color": force_color,
            "lineWidth": 1.5,
            "opacity": 0.7
        })
        
        # Force symbol
        label_distance = max_radius * 0.8
        label_x = center_x + label_distance * math.cos(math.radians(angle))
        label_y = center_y + label_distance * math.sin(math.radians(angle))
        
        instructions.append({
            "type": "fill_circle",
            "x": label_x,
            "y": label_y,
            "radius": 15,
            "color": force_color,
            "opacity": 0.2
        })
        
        instructions.append({
            "type": "text",
            "x": label_x,
            "y": label_y,
            "text": force.symbol,
            "color": force_color,
            "fontSize": 10,
            "textAlign": "center",
            "textBaseline": "middle"
        })
    
    # Singularity
    instructions.append({
        "type": "radial_gradient_circle",
        "x": center_x,
        "y": center_y,
        "radius": 15,
        "innerColor": "#fff0c0",
        "outerColor": "#b8860b",
        "innerOpacity": 1,
        "outerOpacity": 0
    })
    
    instructions.append({
        "type": "fill_circle",
        "x": center_x,
        "y": center_y,
        "radius": 5,
        "color": "#ffd700"
    })
    
    # Particles
    if request.include_fractal_detail:
        particle_instructions = generate_particle_instructions(center_x, center_y, max_radius)
        instructions.extend(particle_instructions)
    
    # Generate fractal components data
    fractal_components = []
    
    for detail in cosmology.fractal_details:
        fractal_components.append({
            "name": detail.name,
            "depth": detail.dimensional_depth,
            "pattern": detail.recursive_pattern,
            "color": detail.visual_properties.get("base_color", "gold"),
            "iterations": detail.visual_properties.get("iteration_depth", 5),
            "branching": detail.visual_properties.get("branching_factor", 4)
        })
    
    return SymbolicGeometryResponse(
        canvas_instructions=instructions,
        fractal_components=fractal_components
    )


def add_fractal_details_canvas(instructions, wheel, center_x, center_y, radius, wheel_index):
    """Add fractal detail instructions for canvas rendering - exceedingly fine and still grinding ^n"""
    if wheel.name == "Wheel of Particle Fields":
        # Quantum field fluctuations with recursive detail
        num_circles = 30 + wheel_index * 10
        for _ in range(num_circles):
            circle_radius = random.uniform(0.5, 3)
            distance = random.uniform(radius * 0.7, radius * 0.95)
            angle = random.uniform(0, 360)
            cx = center_x + distance * math.cos(math.radians(angle))
            cy = center_y + distance * math.sin(math.radians(angle))
            opacity = random.uniform(0.2, 0.6)
            
            # Main particle
            instructions.append({
                "type": "fill_circle",
                "x": cx,
                "y": cy,
                "radius": circle_radius,
                "color": "#88ccff",
                "opacity": opacity
            })
            
            # Add fractal recursion - "exceedingly fine"
            if random.random() < 0.3:  # Only add to 30% of particles
                # Add orbital paths
                num_orbits = random.randint(1, 3)
                for i in range(num_orbits):
                    orbit_radius = circle_radius * (1.5 + i * 0.8)
                    
                    instructions.append({
                        "type": "stroke_circle",
                        "x": cx,
                        "y": cy,
                        "radius": orbit_radius,
                        "color": "#88ccff",
                        "lineWidth": 0.2,
                        "opacity": opacity * 0.7
                    })
                    
                    # Sub-particles in orbit - "grinding ^n"
                    num_sub_particles = random.randint(2, 4)
                    for j in range(num_sub_particles):
                        sub_angle = random.uniform(0, 360)
                        sub_radius = circle_radius * 0.3
                        sub_cx = cx + orbit_radius * math.cos(math.radians(sub_angle))
                        sub_cy = cy + orbit_radius * math.sin(math.radians(sub_angle))
                        
                        instructions.append({
                            "type": "fill_circle",
                            "x": sub_cx,
                            "y": sub_cy,
                            "radius": sub_radius,
                            "color": "#aaddff",
                            "opacity": opacity * 0.8
                        })
                        
                        # Recursive sub-sub-particles - "grinding ^n^n" - recursive iteration
                        if random.random() < 0.4:  # Further recursion for 40% of sub-particles
                            sub_sub_radius = sub_radius * 0.4
                            sub_orbit_radius = sub_radius * 2
                            sub_sub_cx = sub_cx + sub_orbit_radius * math.cos(math.radians(sub_angle + 120))
                            sub_sub_cy = sub_cy + sub_orbit_radius * math.sin(math.radians(sub_angle + 120))
                            
                            instructions.append({
                                "type": "fill_circle",
                                "x": sub_sub_cx,
                                "y": sub_sub_cy,
                                "radius": sub_sub_radius,
                                "color": "#ccffff",
                                "opacity": opacity * 0.7
                            })
                            
                            instructions.append({
                                "type": "line",
                                "x1": sub_cx,
                                "y1": sub_cy,
                                "x2": sub_sub_cx,
                                "y2": sub_sub_cy,
                                "color": "#ccffff",
                                "lineWidth": 0.1,
                                "opacity": opacity * 0.5
                            })
            
    elif wheel.name == "Wheel of Stellar Forges":
        # Star formations
        num_stars = 12 + wheel_index * 2
        for i in range(num_stars):
            angle = i * 360 / num_stars
            distance = radius * random.uniform(0.85, 0.95)
            px = center_x + distance * math.cos(math.radians(angle))
            py = center_y + distance * math.sin(math.radians(angle))
            
            instructions.append({
                "type": "star",
                "x": px,
                "y": py,
                "outer_radius": random.uniform(3, 7),
                "inner_radius": random.uniform(1, 3),
                "points": 5,
                "color": "#ffcc00",
                "opacity": 0.7
            })
            
    elif wheel.name == "Wheel of Galactic Harmonies":
        # Spiral arms
        num_arms = 5
        for arm in range(num_arms):
            start_angle = arm * 360 / num_arms
            spiral_points = []
            
            for i in range(30):
                angle = start_angle + i * 20
                distance = radius * (0.2 + i * 0.03)
                px = center_x + distance * math.cos(math.radians(angle))
                py = center_y + distance * math.sin(math.radians(angle))
                spiral_points.append({"x": px, "y": py})
            
            instructions.append({
                "type": "polyline",
                "points": spiral_points,
                "color": "#cc88ff",
                "lineWidth": 1.5,
                "opacity": 0.4
            })
            
    else:  # Wheel of Universal Expansion
        # Expanding grid
        cells = 6 + wheel_index
        for i in range(cells):
            cell_radius = radius * (0.2 + 0.8 * i / cells)
            
            instructions.append({
                "type": "stroke_circle",
                "x": center_x,
                "y": center_y,
                "radius": cell_radius,
                "color": "#aaaaff",
                "lineWidth": 0.5,
                "opacity": 0.1 + 0.4 * i / cells
            })


def generate_particle_instructions(center_x, center_y, max_radius):
    """Generate particle instructions for the canvas"""
    particles = []
    
    for _ in range(100):
        particle_radius = random.uniform(0.5, 2)
        distance = random.uniform(0, max_radius * 1.1)
        angle = random.uniform(0, 360)
        p_x = center_x + distance * math.cos(math.radians(angle))
        p_y = center_y + distance * math.sin(math.radians(angle))
        opacity = random.uniform(0.3, 0.8)
        p_color = random.choice(['#ffd700', '#88ccff', '#ff88aa', '#88ffaa'])
        
        particles.append({
            "type": "fill_circle",
            "x": p_x,
            "y": p_y,
            "radius": particle_radius,
            "color": p_color,
            "opacity": opacity
        })
    
    return particles


def get_color_for_wheel(wheel_name):
    """Return a color based on the wheel name"""
    color_map = {
        "Wheel of Particle Fields": "#88ccff",  # Quantum blue
        "Wheel of Stellar Forges": "#ffcc55",   # Stellar gold
        "Wheel of Galactic Harmonies": "#cc88ff",  # Cosmic purple
        "Wheel of Universal Expansion": "#aaaaff"  # Void blue
    }
    
    return color_map.get(wheel_name, "#ffd700")  # Default gold


def get_color_for_force(force_name):
    """Return a color based on the force name"""
    color_map = {
        "Gravitas": "#ffaa55",  # Golden orange
        "Lumenflux": "#ffff88",  # Light yellow
        "Fortis": "#ff5555",  # Strong red
        "Transitus": "#55ff55"  # Transition green
    }
    
    return color_map.get(force_name, "#ffffff")  # Default white