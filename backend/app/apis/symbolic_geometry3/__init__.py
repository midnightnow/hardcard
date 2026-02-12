from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import math
import random
import json
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/symbolic-geometry3")

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
        "description": "A self-similar spiral where the distance between turnings increases in geometric progression, exhibiting 'exceedingly fine and still grinding ^n' recursive details",
        "mathematical_basis": "r = a*e^(b*θ) + Σ harmonic_i*sin(ω_i*θ + φ_i)",
        "parameters": {
            "a": {"min": 0.1, "max": 1.0},
            "b": {"min": 0.1, "max": 0.3},
            "turns": {"min": 3, "max": 12},  # Increased max turns
            "points": {"min": 100, "max": 500},  # Increased max points
            "harmonics": {"min": 1, "max": 8}  # New parameter for harmonic components
        }
    },
    "fractal": {
        "name": "Recursive Fractal",
        "description": "A self-similar pattern that exhibits similar patterns at different scales, creating an 'exceedingly fine and still grinding ^n' effect where each level reveals more intricate details",
        "mathematical_basis": "Self-similarity at scale r → r/n with harmonic perturbations",
        "parameters": {
            "iterations": {"min": 1, "max": 8},  # Increased max iterations
            "scaling_factor": {"min": 0.3, "max": 0.7},
            "rotation_angle": {"min": 0, "max": 360, "step": 15},
            "harmonic_distortion": {"min": 0.0, "max": 0.3}  # New parameter
        }
    },
    "wave": {
        "name": "Harmonic Wave",
        "description": "A pattern based on superimposed sine waves creating interference patterns with 'exceedingly fine and still grinding ^n' detail levels",
        "mathematical_basis": "y = Σ A_i*sin(ω_i*x + φ_i) + Σ B_j*cos(η_j*x + ψ_j)",
        "parameters": {
            "frequencies": {"min": 1, "max": 12},  # Increased max frequencies
            "amplitudes": {"min": 0.1, "max": 1.0},
            "phases": {"min": 0, "max": 2*math.pi},
            "harmonic_density": {"min": 1, "max": 5}  # New parameter
        }
    },
    "lattice": {
        "name": "Cosmic Lattice",
        "description": "A grid-like structure with systematic distortions representing spacetime fabric, exhibiting 'exceedingly fine and still grinding ^n' recursive details at intersection points",
        "mathematical_basis": "Perturbed grid with harmonic field equations: (x,y) → (x+δx, y+δy) where δ follows multiple overlapping field equations",
        "parameters": {
            "grid_size": {"min": 5, "max": 32},  # Increased max grid size
            "distortion": {"min": 0.0, "max": 0.7},  # Increased max distortion
            "field_intensity": {"min": 0.1, "max": 3.0},  # Increased max intensity
            "harmonic_fields": {"min": 1, "max": 4}  # New parameter
        }
    },
    "harmonicFractal": {
        "name": "Harmonic Fractal",
        "description": "An advanced fractal system that incorporates harmonic oscillations at each recursive level, producing an 'exceedingly fine and still grinding ^n' effect with dramatically increasing complexity",
        "mathematical_basis": "Multi-scale self-similarity with harmonic modulation: f(z) = z^n + c + Σ A_i*sin(ω_i*|z| + φ_i)",
        "parameters": {
            "iterations": {"min": 2, "max": 10},
            "scaling_factor": {"min": 0.2, "max": 0.8},
            "harmonic_components": {"min": 2, "max": 7},
            "complexity_exponent": {"min": 1.2, "max": 2.5}
        }
    }
}

def generate_spiral_pattern(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate an enhanced spiral pattern with harmonic components and exponential complexity scaling"""
    pattern_type = PATTERN_TYPES["spiral"]
    params = pattern_type["parameters"]
    
    # Apply super-exponential complexity scaling with safety bounds
    # Cap complexity to prevent overflow errors
    safe_complexity = min(complexity, 10.0)  # Cap at 10.0 to prevent overflow
    scaled_complexity = math.pow(safe_complexity, 1.8)  # More aggressive scaling
    
    # Scale parameters based on enhanced complexity with safety bounds
    a = params["a"]["min"] + scaled_complexity * (params["a"]["max"] - params["a"]["min"])
    b = params["b"]["min"] + scaled_complexity * (params["b"]["max"] - params["b"]["min"])
    
    # Exponentially scale turns and points for higher complexity
    # More dramatic scaling with direct calculation and safety bounds
    safe_pow = min(safe_complexity, 8.0)  # Further limit for turn calculations
    turns = round(params["turns"]["min"] + math.pow(safe_pow, 1.5) * (params["turns"]["max"] - params["turns"]["min"]))
    
    # Exponentially scale points for smoother curves at higher complexity
    points_scaling = math.pow(complexity, 1.3)  # More points at higher complexity
    points = round(params["points"]["min"] + points_scaling * (params["points"]["max"] - params["points"]["min"]))
    
    # Scale number of harmonic components with complexity
    num_harmonics = round(params["harmonics"]["min"] + scaled_complexity * (params["harmonics"]["max"] - params["harmonics"]["min"]))
    
    # Generate harmonic components
    harmonics = []
    for i in range(num_harmonics):
        amplitude = 0.02 + (0.08 * random.random()) * scaled_complexity
        frequency = 2 + i + random.random() * 3 * complexity
        phase = random.random() * 2 * math.pi
        harmonics.append({
            "amplitude": amplitude,
            "frequency": frequency,
            "phase": phase
        })
    
    # Generate spiral points with harmonic perturbations
    spiral_points = []
    for i in range(points):
        t = i / (points - 1) * turns * 2 * math.pi
        
        # Base spiral radius with safety bounds to prevent overflow errors
        # Limit the b*t value to prevent exp overflow
        exp_arg = min(b * t, 20.0)  # Cap exponential argument at 20.0
        r = a * math.exp(exp_arg)  # This will now be much safer
        
        # Add harmonic perturbations for more complex patterns
        harmonic_sum = 0
        for h in harmonics:
            # Limit frequency to prevent overflow
            safe_freq = min(h["frequency"], 20.0)
            harmonic_sum += h["amplitude"] * math.sin(safe_freq * t + h["phase"])
        
        # Apply harmonic effects more strongly at higher complexity
        # Ensure harmonic_sum is bounded to prevent extreme values
        bounded_harmonic = max(min(harmonic_sum * scaled_complexity, 5.0), -0.9)  # Prevent negative radii or extreme growth
        r_perturbed = r * (1 + bounded_harmonic)
        
        # Calculate final position
        x = r_perturbed * math.cos(t)
        y = r_perturbed * math.sin(t)
        
        spiral_points.append({"x": x, "y": y})
    
    # Generate sub-spirals for recursion - more sub-patterns at higher recursion levels
    sub_spirals = []
    if recursion_level > 0:
        # Scale number of sub-spirals with recursion_level
        num_sub_spirals = min(recursion_level + math.floor(complexity * 3), 8)
        
        for i in range(num_sub_spirals):
            # Place sub-spirals at strategic points along the main spiral
            # More variance in positioning at higher complexity
            idx = int((i + 0.5 + random.random() * complexity) * points / (num_sub_spirals + 1))
            idx = min(idx, len(spiral_points) - 1)  # Ensure index is valid
            
            point = spiral_points[idx]
            
            # Create sub-spiral with reduced complexity but maintain detail in deeper levels
            decay_factor = 0.7 + 0.2 * complexity  # slower complexity decay at higher levels
            sub_complexity = complexity * decay_factor
            
            sub_spiral = generate_spiral_pattern(sub_complexity, recursion_level - 1)
            sub_spiral["center"] = {"x": point["x"], "y": point["y"]}
            
            # Scale based on complexity and recursion level
            sub_spiral["scale"] = 0.3 / (recursion_level + 1) * (0.8 + complexity * 0.4)
            
            sub_spirals.append(sub_spiral)
    
    return {
        "type": "spiral",
        "parameters": {
            "a": a, 
            "b": b, 
            "turns": turns, 
            "points": points,
            "harmonics": harmonics
        },
        "points": spiral_points,
        "sub_patterns": sub_spirals
    }

def generate_fractal_pattern(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate an enhanced fractal pattern with exponential complexity scaling and harmonic distortions"""
    pattern_type = PATTERN_TYPES["fractal"]
    params = pattern_type["parameters"]
    
    # Apply super-exponential complexity scaling with safety bounds
    safe_complexity = min(complexity, 10.0)  # Cap at 10.0 to prevent overflow
    scaled_complexity = math.pow(safe_complexity, 2.0)  # More aggressive scaling
    
    # Scale parameters based on enhanced complexity
    iterations = round(params["iterations"]["min"] + scaled_complexity * (params["iterations"]["max"] - params["iterations"]["min"]))
    scaling_factor = params["scaling_factor"]["min"] + complexity * (params["scaling_factor"]["max"] - params["scaling_factor"]["min"])
    
    # Rotation parameters with more variation at higher complexity
    rotation_steps = round((params["rotation_angle"]["max"] - params["rotation_angle"]["min"]) / params["rotation_angle"]["step"])
    rotation_idx = round(complexity * rotation_steps)
    base_rotation_angle = (params["rotation_angle"]["min"] + rotation_idx * params["rotation_angle"]["step"]) * math.pi / 180
    
    # Harmonic distortion increases with complexity
    harmonic_distortion = params["harmonic_distortion"]["min"] + scaled_complexity * (params["harmonic_distortion"]["max"] - params["harmonic_distortion"]["min"])
    
    # Base shape (hexagon at low complexity, more sides at higher complexity)
    base_shape = []
    num_sides = 6 + round(complexity * 6)  # Up to 12 sides at max complexity
    for i in range(num_sides):
        angle = i * 2 * math.pi / num_sides
        
        # Add slight distortion to base shape at higher complexity
        radius_variation = 1.0
        if complexity > 0.5:
            radius_variation += (random.random() - 0.5) * harmonic_distortion * 2
        
        x = math.cos(angle) * radius_variation
        y = math.sin(angle) * radius_variation
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
            
            # Add harmonic distortions that vary with depth
            if harmonic_distortion > 0:
                distortion_phase = depth * 1.5 + x * 2 + y * 2
                x_distortion = harmonic_distortion * scale * math.sin(distortion_phase) * (1 + depth * 0.2)
                y_distortion = harmonic_distortion * scale * math.cos(distortion_phase * 1.3) * (1 + depth * 0.2)
                
                x += x_distortion
                y += y_distortion
            
            # Rotate with depth-dependent variation
            rotation_variation = 1.0
            if complexity > 0.7 and depth > 0:
                # Add rotation variation at higher depths and complexity
                rotation_variation += (math.sin(depth * 2.5) * 0.2 * complexity)
            
            effective_angle = angle * rotation_variation
            
            x_rot = x * math.cos(effective_angle) - y * math.sin(effective_angle)
            y_rot = x * math.sin(effective_angle) + y * math.cos(effective_angle)
            
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
            # Exponentially more sub-structures at higher recursion levels and complexity
            vertex_increment = 1
            if complexity > 0.6:
                vertex_increment = 2 if complexity > 0.8 else 1
            
            # Determine which vertices to use for recursion
            if complexity < 0.4 or depth > recursion_level / 2:
                # Use fewer vertices at lower complexity or deeper levels
                vertices_to_use = range(0, len(shape_at_level), vertex_increment)
            else:
                # Use all vertices at higher complexity and shallower levels
                vertices_to_use = range(len(shape_at_level))
            
            for i in vertices_to_use:
                point = shape_at_level[i]
                
                # Vary rotation angle more at higher complexity and deeper levels
                angle_variation = base_rotation_angle * (1 + (random.random() - 0.5) * complexity * 0.4 * depth)
                
                # Generate sub-structures
                sub_structures = generate_fractal_structure(
                    point["x"], point["y"], 
                    scale * scaling_factor * (1 + (random.random() - 0.5) * 0.1 * complexity), 
                    angle + angle_variation * (1 + depth * 0.3 * complexity), 
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
            "rotation_angle": base_rotation_angle,
            "harmonic_distortion": harmonic_distortion,
            "sides": num_sides
        },
        "base_shape": base_shape,
        "structures": fractal_structures
    }

def generate_wave_pattern(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate an enhanced harmonic wave pattern with exponential complexity scaling"""
    pattern_type = PATTERN_TYPES["wave"]
    params = pattern_type["parameters"]
    
    # Apply super-exponential complexity scaling with safety bounds
    safe_complexity = min(complexity, 10.0)  # Cap at 10.0 to prevent overflow
    scaled_complexity = math.pow(safe_complexity, 1.7)  # More aggressive scaling
    
    # Scale number of frequencies exponentially with complexity
    num_frequencies = round(params["frequencies"]["min"] + scaled_complexity * (params["frequencies"]["max"] - params["frequencies"]["min"]))
    
    # Harmonic density increases with complexity - more harmonics per base frequency
    harmonic_density = round(params["harmonic_density"]["min"] + scaled_complexity * 
                             (params["harmonic_density"]["max"] - params["harmonic_density"]["min"]))
    
    # Generate wave components
    wave_components = []
    for i in range(num_frequencies):
        # Base frequency component
        amplitude = params["amplitudes"]["min"] + (random.random() * 0.7 + 0.3) * \
                  (params["amplitudes"]["max"] - params["amplitudes"]["min"])
        
        # Higher frequencies and more variation at higher complexity
        frequency = 1 + i * (1 + complexity * 1.5) + random.random() * complexity * 2
        phase = random.random() * params["phases"]["max"]
        
        wave_components.append({
            "amplitude": amplitude,
            "frequency": frequency,
            "phase": phase,
            "type": "sine"
        })
        
        # Add harmonic overtones for each base frequency
        for h in range(1, harmonic_density + 1):
            # Overtones have decreasing amplitude
            harmonic_amplitude = amplitude * (0.5 / h) * (0.5 + complexity * 0.5)
            # Overtones are at integer multiples of base frequency
            harmonic_frequency = frequency * (h + 1) * (1 + (random.random() - 0.5) * 0.1 * complexity)
            harmonic_phase = phase + random.random() * math.pi
            
            # Alternate between sine and cosine for richer interference patterns
            harmonic_type = "cosine" if h % 2 == 0 else "sine"
            
            wave_components.append({
                "amplitude": harmonic_amplitude,
                "frequency": harmonic_frequency,
                "phase": harmonic_phase,
                "type": harmonic_type
            })
    
    # Generate wave points with all components
    # More points at higher complexity for smoother curves
    points_count = 100 + round(complexity * 400)
    wave_points = []
    
    for i in range(points_count):
        x = i / (points_count - 1) * 2 - 1  # Range -1 to 1
        y = 0
        
        # Sum all wave components
        for component in wave_components:
            input_value = component["frequency"] * math.pi * x + component["phase"]
            
            if component["type"] == "sine":
                y += component["amplitude"] * math.sin(input_value)
            else:  # cosine
                y += component["amplitude"] * math.cos(input_value)
        
        wave_points.append({"x": x, "y": y})
    
    # Generate sub-waves for recursion - more sub-patterns at higher recursion and complexity
    sub_waves = []
    if recursion_level > 0:
        # Scale number of sub-waves with both recursion_level and complexity
        num_sub_waves = min(recursion_level + math.floor(complexity * 2), 6)
        
        for i in range(num_sub_waves):
            # Create sub-waves with more position variation at higher complexity
            position_variation = 0.2 + complexity * 0.3
            x_offset = -0.5 + i * (1.0 / (num_sub_waves - 1 or 1)) + (random.random() - 0.5) * position_variation
            
            # Alternate up and down with some randomness
            y_variation = 0.2 + complexity * 0.2
            y_offset = 0.3 * ((i % 2) * 2 - 1) + (random.random() - 0.5) * y_variation
            
            # Generate sub-wave with reduced complexity but maintain detail in deeper levels
            decay_factor = 0.75 + 0.15 * complexity  # slower complexity decay at higher levels
            sub_complexity = complexity * decay_factor
            
            sub_wave = generate_wave_pattern(sub_complexity, recursion_level - 1)
            sub_wave["offset"] = {"x": x_offset, "y": y_offset}
            
            # Scale based on complexity and recursion level
            sub_wave["scale"] = 0.3 * (0.7 + complexity * 0.5) / math.sqrt(recursion_level)
            
            sub_waves.append(sub_wave)
    
    return {
        "type": "wave",
        "parameters": {
            "components": wave_components,
            "harmonic_density": harmonic_density
        },
        "points": wave_points,
        "sub_patterns": sub_waves
    }

def generate_cosmic_lattice(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate an enhanced cosmic lattice pattern with exponential complexity scaling"""
    pattern_type = PATTERN_TYPES["lattice"]
    params = pattern_type["parameters"]
    
    # Apply super-exponential complexity scaling with safety bounds
    safe_complexity = min(complexity, 10.0)  # Cap at 10.0 to prevent overflow
    scaled_complexity = math.pow(safe_complexity, 1.8)  # More aggressive scaling
    
    # Scale parameters based on enhanced complexity
    # Grid size grows dramatically at higher complexity levels
    grid_size = round(params["grid_size"]["min"] + math.pow(complexity, 1.5) * 
                      (params["grid_size"]["max"] - params["grid_size"]["min"]))
    
    # Higher distortion at higher complexity
    distortion = params["distortion"]["min"] + scaled_complexity * (params["distortion"]["max"] - params["distortion"]["min"])
    
    # Field intensity grows with complexity
    field_intensity = params["field_intensity"]["min"] + scaled_complexity * (params["field_intensity"]["max"] - params["field_intensity"]["min"])
    
    # Number of harmonic fields increases with complexity
    num_harmonic_fields = round(params["harmonic_fields"]["min"] + complexity * (params["harmonic_fields"]["max"] - params["harmonic_fields"]["min"]))
    
    # Generate harmonic field parameters
    harmonic_fields = []
    for i in range(num_harmonic_fields):
        field = {
            "frequency_x": 1 + i + random.random() * 2,
            "frequency_y": 1 + i + random.random() * 2,
            "phase_x": random.random() * 2 * math.pi,
            "phase_y": random.random() * 2 * math.pi,
            "amplitude": 0.2 + random.random() * 0.3 * complexity
        }
        harmonic_fields.append(field)
    
    # Create grid points
    grid_points = []
    for i in range(grid_size):
        for j in range(grid_size):
            # Normalize to -1 to 1 range
            base_x = 2 * i / (grid_size - 1) - 1
            base_y = 2 * j / (grid_size - 1) - 1
            
            # Calculate distance from center for radial effects
            dist_from_center = math.sqrt(base_x**2 + base_y**2)
            angle = math.atan2(base_y, base_x) if (base_x != 0 or base_y != 0) else 0
            
            # Base distortion increases with distance and complexity
            distortion_factor = distortion * dist_from_center * field_intensity
            distortion_angle = angle + complexity * 0.5 * math.pi  # Rotate distortion direction
            
            # Apply base distortion
            offset_x = distortion_factor * math.cos(distortion_angle)
            offset_y = distortion_factor * math.sin(distortion_angle)
            
            # Apply harmonic field distortions
            for field in harmonic_fields:
                # Calculate harmonic field contribution
                field_x = field["amplitude"] * math.sin(field["frequency_x"] * base_x * math.pi + 
                                              field["phase_x"] + dist_from_center * math.pi)
                field_y = field["amplitude"] * math.sin(field["frequency_y"] * base_y * math.pi + 
                                              field["phase_y"] + dist_from_center * math.pi)
                
                # Accumulate distortions
                offset_x += field_x * complexity
                offset_y += field_y * complexity
            
            # Apply all distortions to get final position
            final_x = base_x + offset_x
            final_y = base_y + offset_y
            
            grid_points.append({
                "original": {"x": base_x, "y": base_y},
                "distorted": {"x": final_x, "y": final_y},
                "distortion": {"x": offset_x, "y": offset_y}
            })
    
    # Generate nested lattices for recursion - more sub-patterns at higher recursion and complexity
    sub_lattices = []
    if recursion_level > 0:
        # Scale number of sub-lattices with both recursion_level and complexity
        num_sub_lattices = min(recursion_level + math.floor(complexity * 2), 5)
        
        # Find points with significant distortion
        sorted_points = sorted(grid_points, 
                              key=lambda p: abs(p["distortion"]["x"]) + abs(p["distortion"]["y"]), 
                              reverse=True)
        
        # Use more candidate points at higher complexity
        num_candidates = 5 + round(complexity * 10)
        candidate_points = sorted_points[:num_candidates]
        
        if candidate_points:
            for i in range(num_sub_lattices):
                # Select different points for sub-lattices
                idx = i % len(candidate_points)
                point = candidate_points[idx]
                
                # Generate sub-lattice with reduced complexity but maintain detail in deeper levels
                decay_factor = 0.8 + 0.1 * complexity  # slower complexity decay at higher levels
                sub_complexity = complexity * decay_factor
                
                sub_lattice = generate_cosmic_lattice(sub_complexity, recursion_level - 1)
                sub_lattice["center"] = point["distorted"]
                
                # Scale based on complexity and recursion level
                sub_lattice["scale"] = 0.2 * (0.8 + complexity * 0.4) / recursion_level
                
                sub_lattices.append(sub_lattice)
    
    return {
        "type": "lattice",
        "parameters": {
            "grid_size": grid_size,
            "distortion": distortion,
            "field_intensity": field_intensity,
            "harmonic_fields": harmonic_fields
        },
        "points": grid_points,
        "sub_patterns": sub_lattices
    }

def generate_harmonic_fractal(complexity: float, recursion_level: int) -> Dict[str, Any]:
    """Generate a highly detailed harmonic fractal with extreme exponential complexity scaling"""
    pattern_type = PATTERN_TYPES["harmonicFractal"]
    params = pattern_type["parameters"]
    
    # Apply extreme exponential complexity scaling with safety bounds
    safe_complexity = min(complexity, 8.0)  # Cap at 8.0 to prevent overflow with higher exponent
    scaled_complexity = math.pow(safe_complexity, 2.2)  # Very aggressive scaling
    
    # Scale parameters with extreme exponential growth
    iterations = round(params["iterations"]["min"] + math.pow(complexity, 1.8) * (params["iterations"]["max"] - params["iterations"]["min"]))
    
    scaling_factor = params["scaling_factor"]["min"] + complexity * (params["scaling_factor"]["max"] - params["scaling_factor"]["min"])
    
    # Harmonic components grow exponentially with complexity
    num_harmonics = round(params["harmonic_components"]["min"] + math.pow(complexity, 1.5) * (params["harmonic_components"]["max"] - params["harmonic_components"]["min"]))
    
    # Complexity exponent for recursive scaling - grows with complexity
    complexity_exponent = params["complexity_exponent"]["min"] + scaled_complexity * (params["complexity_exponent"]["max"] - params["complexity_exponent"]["min"])
    
    # Generate harmonic components
    harmonics = []
    for i in range(num_harmonics):
        harmonic = {
            "amplitude": 0.05 + (0.15 * random.random()) * complexity,
            "frequency": 2 + i * 2 + random.random() * 3 * complexity,
            "phase": random.random() * 2 * math.pi,
            "type": "sine" if i % 2 == 0 else "cosine"
        }
        harmonics.append(harmonic)
    
    # Base shape (pentagon or higher at high complexity)
    base_shape = []
    num_sides = 5 + round(complexity * 7)  # Up to 12 sides at max complexity
    for i in range(num_sides):
        angle = i * 2 * math.pi / num_sides
        
        # Complex radius variation based on angle and harmonics
        radius = 1.0
        for h in harmonics:
            if h["type"] == "sine":
                radius += h["amplitude"] * math.sin(h["frequency"] * angle + h["phase"])
            else:
                radius += h["amplitude"] * math.cos(h["frequency"] * angle + h["phase"])
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        base_shape.append({"x": x, "y": y})
    
    # Recursive structure generation function with extreme exponential complexity
    def generate_harmonic_structure(center_x, center_y, scale, angle, depth):
        if depth >= iterations:
            return []
        
        structures = []
        
        # Generate points for this level with harmonic distortions
        shape_at_level = []
        for point in base_shape:
            # Base position
            x = point["x"] * scale
            y = point["y"] * scale
            
            # Apply harmonics that vary with depth and position
            if depth > 0:
                for h in harmonics:
                    # Phase varies with position and depth for maximum complexity
                    phase_variation = depth * 2 + (x * y) * 3 + depth * x * 5
                    
                    harmonic_value = 0
                    if h["type"] == "sine":
                        harmonic_value = h["amplitude"] * math.sin(h["frequency"] * phase_variation + h["phase"])
                    else:
                        harmonic_value = h["amplitude"] * math.cos(h["frequency"] * phase_variation + h["phase"])
                    
                    # Scale effect with depth for increasing complexity
                    effect_scale = math.pow(depth, 0.7) * 0.1 * complexity
                    
                    # Apply distortion
                    x += harmonic_value * effect_scale * scale
                    y += harmonic_value * effect_scale * scale
            
            # Apply rotation with depth-dependent variation
            effective_angle = angle
            if depth > 0:
                # Add angle variation based on harmonics
                angle_variation = 0
                for h in harmonics[:2]:  # Use first two harmonics for angle variation
                    phase_input = depth * 1.5 + x * 3 + y * 2
                    if h["type"] == "sine":
                        angle_variation += 0.2 * h["amplitude"] * math.sin(h["frequency"] * phase_input + h["phase"])
                    else:
                        angle_variation += 0.2 * h["amplitude"] * math.cos(h["frequency"] * phase_input + h["phase"])
                
                effective_angle += angle_variation * complexity * math.pi
            
            # Rotate
            x_rot = x * math.cos(effective_angle) - y * math.sin(effective_angle)
            y_rot = x * math.sin(effective_angle) + y * math.cos(effective_angle)
            
            # Translate
            x_final = center_x + x_rot
            y_final = center_y + y_rot
            
            shape_at_level.append({"x": x_final, "y": y_final})
        
        # Add this structure
        structures.append({
            "points": shape_at_level,
            "depth": depth,
            "harmonics": harmonics
        })
        
        # Recursively add more structures with super-exponential scaling
        if depth < recursion_level:
            # Calculate number of child structures with extreme scaling
            num_children = round(num_sides * (1 - 0.1 * depth) * math.pow(complexity, complexity_exponent / (depth + 1)))
            
            # Cap the number of children to prevent explosion but allow high complexity
            max_children = 36  # Higher cap for extreme details
            num_children = min(num_children, max_children)
            
            # Determine spacing - every nth vertex at lower complexity, every vertex at high complexity
            step = max(1, round(num_sides / num_children))
            
            # Generate child structures
            for i in range(0, num_sides, step):
                if i >= len(shape_at_level):
                    continue
                    
                point = shape_at_level[i]
                
                # Calculate next scale with complexity-dependent reduction
                next_scale = scale * scaling_factor * math.pow(0.95, depth)
                
                # Generate rotation with harmonic variation
                base_rotation = math.pi * 2 / num_sides * (depth + 1) * (1 + complexity * 0.5)
                
                # Add harmonic variation to rotation
                rotation_variation = 0
                for h in harmonics[:3]:  # Use first three harmonics
                    phase_input = depth * 2 + i * 0.5
                    if h["type"] == "sine":
                        rotation_variation += 0.3 * h["amplitude"] * math.sin(h["frequency"] * phase_input + h["phase"])
                    else:
                        rotation_variation += 0.3 * h["amplitude"] * math.cos(h["frequency"] * phase_input + h["phase"])
                
                next_angle = angle + base_rotation + rotation_variation * complexity * math.pi
                
                # Generate child structures recursively
                sub_structures = generate_harmonic_structure(
                    point["x"], point["y"], 
                    next_scale, 
                    next_angle, 
                    depth + 1
                )
                
                structures.extend(sub_structures)
        
        return structures
    
    # Generate the entire structure
    harmonic_structures = generate_harmonic_structure(0, 0, 1.0, 0, 0)
    
    return {
        "type": "harmonicFractal",
        "parameters": {
            "iterations": iterations,
            "scaling_factor": scaling_factor,
            "harmonics": harmonics,
            "complexity_exponent": complexity_exponent,
            "sides": num_sides
        },
        "base_shape": base_shape,
        "structures": harmonic_structures
    }

@router.post("/generate3")
def generate_symbolic_geometry3(request: SymbolicGeometryRequest):
    """Generate highly detailed symbolic geometric patterns based on cosmic concepts.
    
    This endpoint creates intricate geometric patterns that visually represent cosmic concepts
    with 'exceedingly fine and still grinding ^n' recursive details, where each level reveals
    further fractal complexity with exponential scaling of detail.
    """
    # Add absolute safety bounds to prevent timeouts and overflow errors
    capped_complexity = min(request.complexity, 5.0)  # Hard cap at 5.0
    capped_recursion = min(request.recursion_level, 3)  # Hard cap recursion at 3
    # Determine pattern types based on the base concept
    concept_pattern_mapping = {
        "singularity": ["spiral", "harmonicFractal"],
        "metric": ["lattice", "wave"],
        "gravity": ["spiral", "harmonicFractal"],
        "electromagnetism": ["wave", "spiral"],
        "strong_force": ["fractal", "lattice"],
        "weak_force": ["wave", "fractal"],
        "particle": ["harmonicFractal", "wave"],
        "stellar": ["spiral", "harmonicFractal"],
        "galactic": ["spiral", "lattice"],
        "universal": ["lattice", "harmonicFractal"],
        "cosmic": ["harmonicFractal", "spiral", "lattice"]
    }
    
    # Default to cosmic if concept not found
    pattern_types = concept_pattern_mapping.get(request.base_concept.lower(), concept_pattern_mapping["cosmic"])
    
    # Use specified axiom type if provided
    valid_axiom_types = ["spiral", "fractal", "wave", "lattice", "harmonicFractal"]
    if request.axiom_type and request.axiom_type.lower() in valid_axiom_types:
        pattern_types = [request.axiom_type.lower()] + [pt for pt in pattern_types if pt != request.axiom_type.lower()][:1]
    
    # Generate patterns
    patterns = []
    for i, pattern_type in enumerate(pattern_types):
        pattern_id = f"{request.base_concept.lower()}_{pattern_type}_{i}"
        
        # Generate pattern data based on type - use capped values for safety
        pattern_data = {}
        if pattern_type == "spiral":
            pattern_data = generate_spiral_pattern(capped_complexity, capped_recursion)
        elif pattern_type == "fractal":
            pattern_data = generate_fractal_pattern(capped_complexity, capped_recursion)
        elif pattern_type == "wave":
            pattern_data = generate_wave_pattern(capped_complexity, capped_recursion)
        elif pattern_type == "lattice":
            pattern_data = generate_cosmic_lattice(capped_complexity, capped_recursion)
        elif pattern_type == "harmonicFractal":
            pattern_data = generate_harmonic_fractal(capped_complexity, capped_recursion)
        
        # Get pattern type info
        pattern_type_info = PATTERN_TYPES[pattern_type]
        
        # Create pattern object
        pattern = {
            "pattern_id": pattern_id,
            "name": pattern_type_info["name"],
            "description": pattern_type_info["description"],
            "mathematical_basis": pattern_type_info["mathematical_basis"],
            "symbolic_meaning": f"Representation of {request.base_concept} cosmic principle with {pattern_type} structure",
            "pattern_data": pattern_data
        }
        
        patterns.append(pattern)
    
    # Return response with patterns and metadata
    return {
        "patterns": patterns,
        "meta": {
            "base_concept": request.base_concept,
            "complexity": request.complexity,
            "recursion_level": request.recursion_level
        }
    }
    # Determine pattern types based on the base concept
    concept_pattern_mapping = {
        "singularity": ["spiral", "harmonicFractal"],
        "metric": ["lattice", "wave"],
        "gravity": ["spiral", "harmonicFractal"],
        "electromagnetism": ["wave", "spiral"],
        "strong_force": ["fractal", "lattice"],
        "weak_force": ["wave", "fractal"],
        "particle": ["harmonicFractal", "wave"],
        "stellar": ["spiral", "harmonicFractal"],
        "galactic": ["spiral", "lattice"],
        "universal": ["lattice", "harmonicFractal"],
        "cosmic": ["harmonicFractal", "spiral", "lattice"]
    }
    
    # Default to cosmic if concept not found
    pattern_types = concept_pattern_mapping.get(request.base_concept.lower(), concept_pattern_mapping["cosmic"])
    
    # Use specified axiom type if provided
    valid_axiom_types = ["spiral", "fractal", "wave", "orbit", "lattice", "harmonicFractal"]
    if request.axiom_type and request.axiom_type.lower() in valid_axiom_types:
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
        elif pattern_type == "harmonicFractal":
            pattern_data = generate_harmonic_fractal(request.complexity, request.recursion_level)
        elif pattern_type == "orbit":
            # Using spiral with modifications
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
            symbolic_meaning=f"Represents the {request.base_concept} concept through {pattern_type} patterns that exhibit 'exceedingly fine and still grinding ^n' recursive details at complexity level {request.complexity:.1f}.",
            pattern_data=pattern_data
        )
        
        patterns.append(pattern)
    
    # Create response object with explicit validation
    try:
        response = SymbolicGeometryResponse(
            patterns=patterns,
            meta={
                "base_concept": request.base_concept,
                "complexity": request.complexity,
                "recursion_level": request.recursion_level,
                "axiom_type": request.axiom_type
            }
        )
        
        # Verify the response is valid
        response_dict = response.dict()
        return response_dict
    except Exception as e:
        print(f"Error creating response: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating pattern: {str(e)}")
