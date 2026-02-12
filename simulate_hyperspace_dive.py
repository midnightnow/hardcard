#!/usr/bin/env python3
"""
Hardcard Hyperspace: The Infinite Probability Coordinate Directory
"The Heart of Gold Mode"

This script simulates a deep dive into the Hardcard Lineage, visualizing it
as a deterministic probability tree where every "floor" is a coordinate
defined by its recursive shear signature and depth.

Usage:
    python3 simulate_hyperspace_dive.py
"""

import time
from decimal import Decimal
from hardcard_core.lineage import (
    calculate_recursive_shear,
    calculate_ceramic_flow,
    DECAY_FACTOR,
    SEED_RATIO
)

def format_coordinate(depth, shear, ceramic, clay):
    """Formats the probability coordinate string."""
    # The "Address" in Hyperspace
    return f"COORD [{depth:03} : {shear:08.5f}] | Fuel: {ceramic:08.2f} HCL"

def simulate_deep_dive(target_depth=50):
    print("\n🚀 INITIATING HYPERSPACE DEEP DIVE")
    print("   Target Depth: 50")
    print("   Mode: Infinite Probability Drive (Heart of Gold)")
    print("   Structure: Deterministic Tail-End Recursion")
    print("=" * 70)
    
    # Initial State (Genesis)
    current_depth = 1
    current_ceramic = Decimal('1000.00')  # Strong genesis
    current_cumulative_shear = Decimal('0.10') # Starting shear
    
    # We will track the "Vector" of our dive
    vectors = []
    
    # Print Genesis
    print(format_coordinate(current_depth, current_cumulative_shear, current_ceramic, Decimal('0')))
    vectors.append({
        "depth": current_depth,
        "shear": current_cumulative_shear,
        "ceramic": current_ceramic
    })
    
    # Dive loop
    for _ in range(target_depth - 1):
        # 1. Spawning Cost (Economic Physics)
        # Parent gives 10% to child
        seed_ceramic = current_ceramic * SEED_RATIO
        parent_remaining = current_ceramic - seed_ceramic
        
        # 2. Shear Inheritance (Recursive probability weighting)
        # S(child) = sigma_initial + lambda * S(parent)
        # We assume a standard 'cold' spawn with sigma_initial = 0.1
        local_shear_at_birth = Decimal('0.1')
        new_cumulative_shear = calculate_recursive_shear(local_shear_at_birth, current_cumulative_shear)
        
        # 3. Move to Child Coordinate
        current_depth += 1
        current_ceramic = seed_ceramic # Child is born with the seed
        current_cumulative_shear = new_cumulative_shear
        
        vectors.append({
            "depth": current_depth,
            "shear": current_cumulative_shear,
            "ceramic": current_ceramic
        })
        
        # Visualize the coordinate
        time.sleep(0.02) # Trivial delay for effect
        coord_str = format_coordinate(current_depth, current_cumulative_shear, current_ceramic, Decimal('0'))
        
        # Add some "tail end" flavor text for deep nodes
        status = ""
        if current_depth > 40:
            status = " [Tail End - High Probability Density]"
        elif current_depth > 20:
            status = " [Deep Field]"
            
        print(f"{coord_str}{status}")

    print("=" * 70)
    print("🌌 DIVE COMPLETE")
    print(f"   Reached Probability Coordinate: {current_depth}")
    print(f"   Terminal Shear Signature: {current_cumulative_shear}")
    print(f"   Remaining Structural Fuel: {current_ceramic} HCL")
    print("=" * 70)

    # Analyze the Mathematical Convergence (The "Predictable" part)
    # The formula S(n) = 0.1 + 0.9*S(n-1) converges to 1.0
    print("\n📊 TELEMETRY ANALYSIS")
    print("   TheRecursive Shear S(n) acts as the 'Gravitational Constant' of the branch.")
    print("   Notice how it asymptotically approaches 1.0 (Criticality) even with minimal local stress.")
    print("   This confirms the 'Tail End' hypothesis: deeply nested realities are inherently fragile")
    print("   unless supported by massive Ceramic reserves (which decay exponentially).")

if __name__ == "__main__":
    simulate_deep_dive()
