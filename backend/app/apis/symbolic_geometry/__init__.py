from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import math
import random
import json
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/symbolic-geometry")

class SymbolicGeometryRequest(BaseModel):
    base_concept: str
    complexity: float = 1.0
    recursion_level: int = 3
    axiom_type: Optional[str] = None

class GeometricPattern(BaseModel):
    pattern_id: str
    name: str
    description: str
    mathematical_basis: str
    symbolic_meaning: str
    pattern_data: Dict[str, Any]

class SymbolicGeometryResponse(BaseModel):
    patterns: List[GeometricPattern]
    meta: Dict[str, Any]

# Constants for different pattern types
PATTERN_TYPES = {
    "spiral": {
        "name": "Logarithmic Spiral",
        "description": "A self-similar spiral where the distance between turnings increases in geometric progression",
        "mathematical_basis": "r = a*e^(b*θ)",
        "parameters": {
            "a": {"min": 0.1, "max": 1.0},
            "b": {"min": 0.1, "max": 0.3},
            "turns": {"min": 3, "max": 8},
            "points": {"min": 100, "max": 200}
        }
    },
    "fractal": {
        "name": "Recursive Fractal",
        "description": "A self-similar pattern that exhibits similar patterns at different scales",
        "mathematical_basis": "Self-similarity at scale r → r/n",
        "parameters": {
            "iterations": {"min": 1, "max": 5},
            "scaling_factor": {"min": 0.3, "max": 0.7},
            "rotation_angle": {"min": 0, "max": 360, "step": 15}
        }
    },
    "wave": {
        "name": "Harmonic Wave",
        "description": "A pattern based on superimposed sine waves creating interference patterns",
        "mathematical_basis": "y = Σ A_i*sin(ω_i*x + φ_i)",
        "parameters": {
            "frequencies": {"min": 1, "max": 5},
            "amplitudes": {"min": 0.1, "max": 1.0},
            "phases": {"min": 0, "max": 2*math.pi}
        }
    },
    "orbit": {
        "name": "Nested Orbits",
        "description": "Concentric orbital patterns with periodic perturbations",
        "mathematical_basis": "r = r_0 + Σ e_i*sin(n_i*θ)",
        "parameters": {
            "base_radius": {"min": 0.5, "max": 1.0},
            "eccentricities": {"min": 0.05, "max": 0.2},
            "frequencies": {"min": 2, "max": 7}
        }
    },
    "lattice": {
        "name": "Cosmic Lattice",
        "description": "A grid-like structure with systematic distortions representing spacetime fabric",
        "mathematical_basis": "Perturbed grid: (x,y) → (x+δx, y+δy) where δ follows a field equation",
        "parameters": {
            "grid_size": {"min": 5, "max": 20},
            "distortion": {"min": 0.0, "max": 0.5},
            "field_intensity": {"min": 0.1, "max": 2.0}
        }
    }
}

def generate_spiral_pattern(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate a spiral pattern with parameters based on complexity"""
    pattern_type = PATTERN_TYPES["spiral"]
    params = pattern_type["parameters"]
    
    # Scale parameters based on complexity
    a = params["a"]["min"] + complexity * (params["a"]["max"] - params["a"]["min"])
    b = params["b"]["min"] + complexity * (params["b"]["max"] - params["b"]["min"])
    turns = round(params["turns"]["min"] + complexity * (params["turns"]["max"] - params["turns"]["min"]))
    points = round(params["points"]["min"] + complexity * (params["points"]["max"] - params["points"]["min"]))
    
    # Generate spiral points
    spiral_points = []
    for i in range(points):
        t = i / (points - 1) * turns * 2 * math.pi
        r = a * math.exp(b * t)
        x = r * math.cos(t)
        y = r * math.sin(t)
        spiral_points.append({"x": x, "y": y})
    
    # Generate sub-spirals for recursion
    sub_spirals = []
    if recursion_level > 0:
        num_sub_spirals = min(recursion_level + 1, 5)
        for i in range(num_sub_spirals):
            # Place sub-spirals along the main spiral
            idx = int((i + 1) * points / (num_sub_spirals + 1))
            if idx < len(spiral_points):
                point = spiral_points[idx]
                # Generate a smaller spiral at this point
                sub_spiral = generate_spiral_pattern(complexity * 0.8, recursion_level - 1)
                sub_spiral["center"] = {"x": point["x"], "y": point["y"]}
                sub_spiral["scale"] = 0.3 / (recursion_level + 1)
                sub_spirals.append(sub_spiral)
    
    return {
        "type": "spiral",
        "parameters": {"a": a, "b": b, "turns": turns, "points": points},
        "points": spiral_points,
        "sub_patterns": sub_spirals
    }

def generate_fractal_pattern(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate a fractal pattern with parameters based on complexity"""
    pattern_type = PATTERN_TYPES["fractal"]
    params = pattern_type["parameters"]
    
    # Scale parameters based on complexity
    iterations = round(params["iterations"]["min"] + complexity * (params["iterations"]["max"] - params["iterations"]["min"]))
    scaling_factor = params["scaling_factor"]["min"] + complexity * (params["scaling_factor"]["max"] - params["scaling_factor"]["min"])
    rotation_steps = round((params["rotation_angle"]["max"] - params["rotation_angle"]["min"]) / params["rotation_angle"]["step"])
    rotation_idx = round(complexity * rotation_steps)
    rotation_angle = (params["rotation_angle"]["min"] + rotation_idx * params["rotation_angle"]["step"]) * math.pi / 180
    
    # Base shape (hexagon)
    base_shape = []
    num_sides = 6
    for i in range(num_sides):
        angle = i * 2 * math.pi / num_sides
        x = math.cos(angle)
        y = math.sin(angle)
        base_shape.append({"x": x, "y": y})
    
    # Generate the fractal structure recursively
    def generate_fractal_structure(center_x, center_y, scale, angle, depth):
        if depth >= iterations:
            return []
        
        structures = []
        # Add the base shape at this level
        shape_at_level = []
        for point in base_shape:
            # Apply scaling, rotation and translation
            x = point["x"] * scale
            y = point["y"] * scale
            # Rotate
            x_rot = x * math.cos(angle) - y * math.sin(angle)
            y_rot = x * math.sin(angle) + y * math.cos(angle)
            # Translate
            x_final = center_x + x_rot
            y_final = center_y + y_rot
            shape_at_level.append({"x": x_final, "y": y_final})
        
        structures.append({
            "points": shape_at_level,
            "depth": depth
        })
        
        # Recursively add more shapes at vertices
        if depth < recursion_level:
            for point in shape_at_level:
                sub_structures = generate_fractal_structure(
                    point["x"], point["y"], 
                    scale * scaling_factor, 
                    angle + rotation_angle * (1 + depth * 0.5), 
                    depth + 1
                )
                structures.extend(sub_structures)
        
        return structures
    
    fractal_structures = generate_fractal_structure(0, 0, 1.0, 0, 0)
    
    return {
        "type": "fractal",
        "parameters": {
            "iterations": iterations,
            "scaling_factor": scaling_factor,
            "rotation_angle": rotation_angle
        },
        "base_shape": base_shape,
        "structures": fractal_structures
    }

def generate_wave_pattern(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate a harmonic wave pattern with parameters based on complexity"""
    pattern_type = PATTERN_TYPES["wave"]
    params = pattern_type["parameters"]
    
    # Scale parameters based on complexity
    num_frequencies = round(params["frequencies"]["min"] + complexity * (params["frequencies"]["max"] - params["frequencies"]["min"]))
    
    # Generate wave components
    wave_components = []
    for i in range(num_frequencies):
        amplitude = params["amplitudes"]["min"] + random.random() * (params["amplitudes"]["max"] - params["amplitudes"]["min"])
        # Higher frequencies for more complex patterns
        frequency = 1 + i * (1 + complexity)
        phase = random.random() * params["phases"]["max"]
        
        wave_components.append({
            "amplitude": amplitude,
            "frequency": frequency,
            "phase": phase
        })
    
    # Generate wave points
    points = 100
    wave_points = []
    for i in range(points):
        x = i / (points - 1) * 2 - 1  # Range -1 to 1
        y = 0
        
        # Sum all wave components
        for component in wave_components:
            y += component["amplitude"] * math.sin(component["frequency"] * math.pi * x + component["phase"])
        
        wave_points.append({"x": x, "y": y})
    
    # Generate sub-waves for recursion
    sub_waves = []
    if recursion_level > 0:
        num_sub_waves = min(recursion_level, 3)
        for i in range(num_sub_waves):
            # Create sub-waves at different positions
            x_offset = -0.5 + i * 0.5
            y_offset = 0.3 * (i % 2 * 2 - 1)  # Alternate up and down
            
            sub_wave = generate_wave_pattern(complexity * 0.7, recursion_level - 1)
            sub_wave["offset"] = {"x": x_offset, "y": y_offset}
            sub_wave["scale"] = 0.3
            sub_waves.append(sub_wave)
    
    return {
        "type": "wave",
        "parameters": {"components": wave_components},
        "points": wave_points,
        "sub_patterns": sub_waves
    }

def generate_cosmic_lattice(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate a cosmic lattice pattern with parameters based on complexity"""
    pattern_type = PATTERN_TYPES["lattice"]
    params = pattern_type["parameters"]
    
    # Scale parameters based on complexity
    grid_size = round(params["grid_size"]["min"] + complexity * (params["grid_size"]["max"] - params["grid_size"]["min"]))
    distortion = params["distortion"]["min"] + complexity * (params["distortion"]["max"] - params["distortion"]["min"])
    field_intensity = params["field_intensity"]["min"] + complexity * (params["field_intensity"]["max"] - params["field_intensity"]["min"])
    
    # Create grid points
    grid_points = []
    for i in range(grid_size):
        for j in range(grid_size):
            # Normalize to -1 to 1 range
            base_x = 2 * i / (grid_size - 1) - 1
            base_y = 2 * j / (grid_size - 1) - 1
            
            # Apply field distortion
            dist_from_center = math.sqrt(base_x**2 + base_y**2)
            angle = math.atan2(base_y, base_x) if (base_x != 0 or base_y != 0) else 0
            
            # Distortion increases with distance and complexity
            distortion_factor = distortion * dist_from_center * field_intensity
            distortion_angle = angle + complexity * 0.5 * math.pi  # Rotate distortion direction
            
            # Apply distortion
            offset_x = distortion_factor * math.cos(distortion_angle)
            offset_y = distortion_factor * math.sin(distortion_angle)
            
            final_x = base_x + offset_x
            final_y = base_y + offset_y
            
            grid_points.append({
                "original": {"x": base_x, "y": base_y},
                "distorted": {"x": final_x, "y": final_y},
                "distortion": {"x": offset_x, "y": offset_y}
            })
    
    # Generate nested lattices for recursion
    sub_lattices = []
    if recursion_level > 0:
        num_sub_lattices = min(recursion_level, 2)
        for i in range(num_sub_lattices):
            # Place sub-lattices at interesting distortion points
            # Find points with significant distortion
            sorted_points = sorted(grid_points, key=lambda p: abs(p["distortion"]["x"]) + abs(p["distortion"]["y"]), reverse=True)
            candidate_points = sorted_points[:5]  # Top 5 most distorted points
            
            if candidate_points:
                idx = i % len(candidate_points)
                point = candidate_points[idx]
                
                sub_lattice = generate_cosmic_lattice(complexity * 0.8, recursion_level - 1)
                sub_lattice["center"] = point["distorted"]
                sub_lattice["scale"] = 0.2 / (recursion_level)
                sub_lattices.append(sub_lattice)
    
    return {
        "type": "lattice",
        "parameters": {
            "grid_size": grid_size,
            "distortion": distortion,
            "field_intensity": field_intensity
        },
        "points": grid_points,
        "sub_patterns": sub_lattices
    }

@router.post("/generate")
def generate_symbolic_geometry(request: SymbolicGeometryRequest) -> SymbolicGeometryResponse:
    """Generate symbolic geometric patterns based on cosmic concepts.
    
    This endpoint creates intricate geometric patterns that visually represent cosmic concepts
    with "exceedingly fine and still grinding ^n" recursive details, where each level reveals
    further fractal complexity.
    """
    # Determine pattern types based on the base concept
    concept_pattern_mapping = {
        "singularity": ["spiral", "fractal"],
        "metric": ["lattice", "wave"],
        "gravity": ["spiral", "orbit"],
        "electromagnetism": ["wave", "spiral"],
        "strong_force": ["fractal", "lattice"],
        "weak_force": ["wave", "fractal"],
        "particle": ["fractal", "wave"],
        "stellar": ["spiral", "orbit"],
        "galactic": ["spiral", "lattice"],
        "universal": ["lattice", "wave"],
        "cosmic": ["fractal", "spiral", "lattice"]
    }
    
    # Default to cosmic if concept not found
    pattern_types = concept_pattern_mapping.get(request.base_concept.lower(), concept_pattern_mapping["cosmic"])
    
    # Use specified axiom type if provided
    if request.axiom_type and request.axiom_type.lower() in ["spiral", "fractal", "wave", "orbit", "lattice"]:
        pattern_types = [request.axiom_type.lower()] + [pt for pt in pattern_types if pt != request.axiom_type.lower()][:1]
    
    # Generate patterns
    patterns = []
    for i, pattern_type in enumerate(pattern_types):
        pattern_id = f"{request.base_concept.lower()}_{pattern_type}_{i}"
        
        # Generate pattern data based on type
        pattern_data = {}
        if pattern_type == "spiral":
            pattern_data = generate_spiral_pattern(request.complexity, request.recursion_level)
        elif pattern_type == "fractal":
            pattern_data = generate_fractal_pattern(request.complexity, request.recursion_level)
        elif pattern_type == "wave":
            pattern_data = generate_wave_pattern(request.complexity, request.recursion_level)
        elif pattern_type == "lattice":
            pattern_data = generate_cosmic_lattice(request.complexity, request.recursion_level)
        elif pattern_type == "orbit":
            # Simplified to spiral for now
            pattern_data = generate_spiral_pattern(request.complexity, request.recursion_level)
            pattern_data["type"] = "orbit"
        
        # Get pattern type info
        type_info = PATTERN_TYPES.get(pattern_type, PATTERN_TYPES["fractal"])
        
        # Create pattern object
        pattern = GeometricPattern(
            pattern_id=pattern_id,
            name=f"{type_info['name']} of {request.base_concept.title()}",
            description=type_info["description"],
            mathematical_basis=type_info["mathematical_basis"],
            symbolic_meaning=f"Represents the {request.base_concept} concept through {pattern_type} patterns that exhibit 'exceedingly fine and still grinding ^n' recursive details.",
            pattern_data=pattern_data
        )
        
        patterns.append(pattern)
    
    # Create response
    response = SymbolicGeometryResponse(
        patterns=patterns,
        meta={
            "base_concept": request.base_concept,
            "complexity": request.complexity,
            "recursion_level": request.recursion_level
        }
    )
    
    return response
