#!/usr/bin/env python3
"""
Hardcard Physics: physics.py
The mathematical constants and structural calculations for the Hardcard economy.

Core Invariants (HCL-07):
- K = 0.10 (10% Structural Constant - the "walls")
- σ = Shear Force (ratio of volume to mass)
- When σ ≥ 1.0, dimensional compression is triggered
"""

from decimal import Decimal
from typing import Dict, Any, Tuple

# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

K = Decimal('0.10')  # The Structural Constant (10%)
# This is the ratio that defines "wall thickness"
# K = Infrastructure / Total Economic Activity
# If actual ratio < K, the structure is unstable

# The 2-1-7 Split (Metabolic Distribution of the 10%)
SPLIT_ANCHOR = Decimal('0.70')   # 7% → Local floor hardening
SPLIT_BEDROCK = Decimal('0.20')  # 2% → Genesis node maintenance  
SPLIT_OXYGEN = Decimal('0.10')   # 1% → Next floor subsidy

# ═══════════════════════════════════════════════════════════════════════════════
# CORE PHYSICS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_shear_force(ceramic_mass: Decimal, clay_volume: Decimal) -> Decimal:
    """
    Shear Force (σ) = Clay Volume / (Ceramic Mass × 10)
    
    This measures the stress on the structural walls.
    - σ < 1.0: Stable (walls can support the volume)
    - σ ≥ 1.0: Critical (dimensional fold required)
    
    The ×10 factor represents the maximum safe expansion ratio.
    """
    if ceramic_mass <= 0:
        return Decimal('0.0')  # No mass = no stress (empty floor)
    
    max_safe_volume = ceramic_mass * 10
    sigma = clay_volume / max_safe_volume
    return sigma.quantize(Decimal('0.0001'))


def calculate_structural_integrity(ceramic_mass: Decimal, total_volume: Decimal) -> Decimal:
    """
    Integrity = Actual K / Required K
    
    Where Actual K = Ceramic Mass / Total Economic Activity
    
    - Integrity ≥ 1.0: Walls are at or above required thickness
    - Integrity < 1.0: Walls are thinning
    """
    if total_volume <= 0:
        return Decimal('1.0')  # Perfect integrity in vacuum
    
    actual_k = ceramic_mass / total_volume
    integrity = actual_k / K
    return min(integrity, Decimal('1.0')).quantize(Decimal('0.0001'))


def calculate_metabolic_split(fee_amount: Decimal) -> Dict[str, Decimal]:
    """
    The 2-1-7 Split: Distributes the 10% fee across three purposes.
    
    Returns:
        anchor: 7% of fee → strengthens current floor
        bedrock: 2% of fee → maintains genesis infrastructure
        oxygen: 1% of fee → subsidizes next floor creation
    """
    return {
        'anchor': (fee_amount * SPLIT_ANCHOR).quantize(Decimal('0.00000001')),
        'bedrock': (fee_amount * SPLIT_BEDROCK).quantize(Decimal('0.00000001')),
        'oxygen': (fee_amount * SPLIT_OXYGEN).quantize(Decimal('0.00000001')),
    }


def transmute_to_internal(external_amount: Decimal) -> Tuple[Decimal, Decimal]:
    """
    The "Add a Zero" Transmutation.
    
    When external currency enters, it becomes internal "clay":
    - 10% is anchored as ceramic (permanent mass)
    - 90% is expanded 10x to become clay (working volume)
    
    $100 external → $10 ceramic + 900 clay
    
    Returns:
        (ceramic_mass, clay_volume)
    """
    ceramic = external_amount * K
    clay = (external_amount - ceramic) * 10
    return (
        ceramic.quantize(Decimal('0.00000001')),
        clay.quantize(Decimal('0.00000001'))
    )


def compress_to_external(clay_volume: Decimal) -> Tuple[Decimal, Decimal]:
    """
    Reverse transmutation (Dimensional Fold).
    
    When a floor compresses, clay is squeezed back:
    - Clay is divided by 10 to get external equivalent
    - The ceramic that was anchoring it is released
    
    900 clay → 90 external value
    
    Returns:
        (recovered_external, released_ceramic)
    """
    external = clay_volume / 10
    # The ceramic that was holding this volume
    # Original: ceramic = external * 0.10, so ceramic = (clay/10) * 0.10 = clay/100
    released_ceramic = clay_volume / 100
    return (
        external.quantize(Decimal('0.00000001')),
        released_ceramic.quantize(Decimal('0.00000001'))
    )


def calculate_elevation(treasury_balance: Decimal) -> int:
    """
    Floor Elevation = log₁₀(treasury) + 1
    
    Each order of magnitude in the treasury enables a new floor.
    - 10 HCL → Floor 2
    - 100 HCL → Floor 3
    - 1000 HCL → Floor 4
    """
    if treasury_balance <= 0:
        return 1
    
    import math
    return int(math.log10(float(treasury_balance))) + 1


def next_floor_threshold(current_elevation: int) -> Decimal:
    """
    Returns the treasury balance needed to unlock the next floor.
    """
    return Decimal(10 ** current_elevation)


# ═══════════════════════════════════════════════════════════════════════════════
# STRUCTURAL AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

def structural_audit(ceramic_mass: Decimal, clay_volume: Decimal, 
                     total_transactions: int) -> Dict[str, Any]:
    """
    Full structural audit of a floor.
    
    Returns all key metrics for the Hyperspace Observer.
    """
    sigma = calculate_shear_force(ceramic_mass, clay_volume)
    integrity = calculate_structural_integrity(ceramic_mass, ceramic_mass + clay_volume)
    elevation = calculate_elevation(ceramic_mass)
    next_threshold = next_floor_threshold(elevation)
    delta_to_next = next_threshold - ceramic_mass
    
    # Determine status
    if sigma >= Decimal('1.0'):
        status = "CRITICAL"
        note = "⚠️ Shear force critical. Dimensional fold imminent."
    elif sigma >= Decimal('0.8'):
        status = "WARNING"
        note = "⚡ Approaching structural limit. Monitor closely."
    elif sigma >= Decimal('0.5'):
        status = "STABLE"
        note = "✅ Healthy load distribution."
    else:
        status = "COLD"
        note = "🧊 Foundation cold and hard. Ready for weight."
    
    return {
        'shear_force': float(sigma),
        'integrity': float(integrity),
        'ceramic_mass': float(ceramic_mass),
        'clay_volume': float(clay_volume),
        'elevation': elevation,
        'next_floor_threshold': float(next_threshold),
        'delta_to_next': float(delta_to_next),
        'transactions': total_transactions,
        'status': status,
        'note': note,
        'max_safe_volume': float(ceramic_mass * 10),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# LINEAGE MATHEMATICS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_cumulative_shear(floor_history: list) -> Decimal:
    """
    Cumulative Shear across all generations.
    
    σ_total = Σ(σᵢ × decay^i) where i is generation depth
    
    Each compression cycle reduces the "memory" of past shear by 10%.
    This represents evolutionary learning - each fold teaches the floor.
    """
    DECAY_FACTOR = Decimal('0.9')  # 10% decay per generation
    
    cumulative = Decimal('0')
    for i, floor in enumerate(floor_history):
        generation_shear = Decimal(str(floor.get('shear_force', 0)))
        decay = DECAY_FACTOR ** i
        cumulative += generation_shear * decay
    
    return cumulative.quantize(Decimal('0.0001'))


def calculate_inheritance(parent_ceramic: Decimal, compression_ratio: Decimal = Decimal('0.1')) -> Dict[str, Decimal]:
    """
    When a floor compresses, calculate inheritance to parent and child.
    
    The Compression Inheritance Formula:
    - 90% of ceramic returns to parent (reclaimed_ceramic)
    - 10% stays as seed for child (seed_ceramic)
    - Clay is divided by 10 (removing a zero)
    
    This ensures value flows upward while enabling new growth.
    """
    reclaimed = parent_ceramic * (Decimal('1') - compression_ratio)
    seed = parent_ceramic * compression_ratio
    
    return {
        'reclaimed_to_parent': reclaimed.quantize(Decimal('0.00000001')),
        'seed_for_restart': seed.quantize(Decimal('0.00000001')),
        'compression_ratio': compression_ratio,
    }


def calculate_signal_weight(reward: Decimal, base_weight: Decimal = Decimal('1.0')) -> Decimal:
    """
    Signal Weight = base_weight + ln(1 + reward)
    
    Signals with higher rewards contribute more to shear force.
    The logarithm prevents outliers from dominating.
    """
    import math
    if reward <= 0:
        return base_weight
    
    weight = base_weight + Decimal(str(math.log(1 + float(reward))))
    return weight.quantize(Decimal('0.0001'))


def calculate_fossil_density(signals: int, wallets: int, ceramic: Decimal) -> Decimal:
    """
    Fossil Density = (signals + wallets) / ceramic
    
    Measures how "busy" a floor was relative to its structural mass.
    High density = high activity floor (possibly volatile)
    Low density = stable, conservative floor
    """
    if ceramic <= 0:
        return Decimal('0')
    
    density = Decimal(signals + wallets) / ceramic
    return density.quantize(Decimal('0.0001'))


def project_fold_timeline(current_sigma: Decimal, signal_rate: Decimal, ceramic_mass: Decimal) -> int:
    """
    Estimate transactions until next fold.
    
    transactions_to_fold = (1.0 - σ) × ceramic_mass × 10 / average_signal_weight
    
    Returns estimated number of signals before σ reaches 1.0
    """
    if signal_rate <= 0:
        return -1  # Infinite (no signals being added)
    
    remaining_capacity = (Decimal('1.0') - current_sigma) * ceramic_mass * 10
    transactions = remaining_capacity / signal_rate
    return max(0, int(transactions))


def calculate_velocity(clay_volume: Decimal, time_delta_seconds: int) -> Decimal:
    """
    Economic Velocity = Clay / Time
    
    Measures the rate of economic activity.
    Higher velocity = more active economy.
    """
    if time_delta_seconds <= 0:
        return Decimal('0')
    
    velocity = clay_volume / Decimal(time_delta_seconds)
    return velocity.quantize(Decimal('0.00000001'))


def calculate_stability_score(sigma: Decimal, fossil_count: int, velocity: Decimal) -> Decimal:
    """
    Stability Score = (1 - σ) × (1 + fossil_count × 0.1) × e^(-velocity × 0.001)
    
    Combines:
    - Current shear (lower is better)
    - Experience (more folds = more resilient)
    - Velocity (slower is more stable)
    
    Returns 0.0 to 1.0 where 1.0 is maximum stability.
    """
    import math
    
    shear_factor = Decimal('1') - min(sigma, Decimal('1.0'))
    experience_factor = Decimal('1') + Decimal(fossil_count) * Decimal('0.1')
    velocity_factor = Decimal(str(math.exp(-float(velocity) * 0.001)))
    
    score = shear_factor * experience_factor * velocity_factor
    return min(Decimal('1.0'), score).quantize(Decimal('0.0001'))


# ═══════════════════════════════════════════════════════════════════════════════
# ECONOMIC PROJECTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def project_future_state(current_ceramic: Decimal, current_clay: Decimal, 
                         projected_transactions: int, avg_reward: Decimal = Decimal('10')) -> Dict[str, Any]:
    """
    Project floor state after N transactions.
    
    Assumes each transaction:
    - Adds avg_reward to clay volume
    - Reinforces ceramic by 10% of avg_reward (from split)
    """
    # Each transaction adds to clay and slightly to ceramic (via anchor split)
    projected_clay = current_clay + (Decimal(projected_transactions) * avg_reward)
    anchor_reinforcement = Decimal(projected_transactions) * avg_reward * K * SPLIT_ANCHOR
    projected_ceramic = current_ceramic + anchor_reinforcement
    
    projected_sigma = calculate_shear_force(projected_ceramic, projected_clay)
    
    return {
        'current_sigma': float(calculate_shear_force(current_ceramic, current_clay)),
        'projected_sigma': float(projected_sigma),
        'projected_ceramic': float(projected_ceramic),
        'projected_clay': float(projected_clay),
        'transactions': projected_transactions,
        'will_fold': projected_sigma >= Decimal('1.0'),
        'fold_margin': float(Decimal('1.0') - projected_sigma),
    }
