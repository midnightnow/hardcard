#!/usr/bin/env python3
"""
Hardcard Lineage Calculator: lineage.py
The "Ancestry.com" of the Hardcard Economy.

This module implements the recursive mathematics for tracking floor ancestry,
cumulative shear inheritance, and ceramic flow conservation across generations.

Core Formulas (HPSS-03):
- Recursive Cumulative Shear: S(n) = σₙ + λ·S(n-1) where λ = 0.9
- Ceramic Flow Conservation: C_parent += 0.9×C_child, C_seed = 0.1×C_child
- Depth Calculation: depth = 1 + max(child_depths)
"""

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

DECAY_FACTOR = Decimal('0.9')       # λ: Shear memory decay per generation
RECLAIM_RATIO = Decimal('0.9')      # 90% ceramic flows to parent
SEED_RATIO = Decimal('0.1')         # 10% ceramic stays as seed
FOSSILS_DIR = Path(".hardcard/fossils")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class LineageNode:
    """
    Represents a single floor in the ancestry tree.
    
    Each node contains:
    - floor_id: Unique identifier for this floor
    - depth: Distance from genesis (genesis = 1)
    - local_shear: σ at time of compression (frozen in fossil)
    - cumulative_shear: S(n) = recursive shear from all ancestors
    - ceramic_mass: $HCL at compression
    - clay_volume: $HCB at compression
    - parent_id: ID of the parent floor (None for genesis)
    - children: List of child floor IDs
    - fossil_hash: Hash of the fossil record
    - archived_at: Unix timestamp of fossilization
    """
    floor_id: str
    depth: int = 1
    local_shear: Decimal = Decimal('0')
    cumulative_shear: Decimal = Decimal('0')
    ceramic_mass: Decimal = Decimal('0')
    clay_volume: Decimal = Decimal('0')
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    fossil_hash: Optional[str] = None
    archived_at: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        return {
            'floor_id': self.floor_id,
            'depth': self.depth,
            'local_shear': str(self.local_shear),
            'cumulative_shear': str(self.cumulative_shear),
            'ceramic_mass': str(self.ceramic_mass),
            'clay_volume': str(self.clay_volume),
            'parent_id': self.parent_id,
            'children': self.children,
            'fossil_hash': self.fossil_hash,
            'archived_at': self.archived_at,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CORE MATHEMATICS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_recursive_shear(local_shear: Decimal, parent_cumulative: Decimal = Decimal('0')) -> Decimal:
    """
    Recursive Cumulative Shear Formula:
    
        S(n) = σₙ + λ·S(n-1)
    
    Where:
        - S(n) = Cumulative shear at depth n
        - σₙ = Local shear force at this floor
        - λ = 0.9 (decay factor - each generation "forgets" 10%)
        - S(n-1) = Parent's cumulative shear
    
    Base Case: S(0) = 0 (genesis has no ancestors)
    
    This formula ensures that:
    1. Recent stress matters more than ancient stress
    2. The sum converges (geometric series with ratio < 1)
    3. Deep lineages carry "evolutionary memory" of past compressions
    
    Bounds: 0 ≤ S(n) ≤ σₙ / (1 - λ) = 10·σₙ (theoretical max for infinite depth)
    
    Args:
        local_shear: σₙ for this floor (0 ≤ σ ≤ 1)
        parent_cumulative: S(n-1) from parent (default 0 for genesis)
    
    Returns:
        S(n) - cumulative shear, bounded to reasonable range
    """
    # Validate inputs
    local_shear = max(Decimal('0'), min(local_shear, Decimal('1.0')))
    parent_cumulative = max(Decimal('0'), parent_cumulative)
    
    # Apply formula: S(n) = σₙ + λ·S(n-1)
    inherited = DECAY_FACTOR * parent_cumulative
    cumulative = local_shear + inherited
    
    return cumulative.quantize(Decimal('0.0001'))


def calculate_theoretical_shear(depth: int, local_shear: Decimal = Decimal('0.1')) -> Decimal:
    """
    Calculates the theoretical shear S(n) at a given depth 'n' in the probability tree.
    
    This acts as the "Address Book" lookup for Hyperspace (Heart of Gold Mode).
    The formula is deterministic: S(n) converges to 10 * local_shear.
    
    Args:
        depth: The depth (generation) to calculate for.
        local_shear: The constant local shear at each step (default 0.1).
        
    Returns:
        The cumulative shear S(n).
    """
    cumulative = Decimal('0')
    # Loop to simulate the recursive inheritance
    for _ in range(depth):
        cumulative = calculate_recursive_shear(local_shear, cumulative)
    return cumulative


def calculate_ceramic_flow(ceramic_mass: Decimal) -> Dict[str, Decimal]:
    """
    Ceramic Flow Conservation during Dimensional Fold:
    
        C_reclaimed = 0.9 × C_child  (flows to parent)
        C_seed = 0.1 × C_child       (stays for rebirth)
    
    Conservation Law:
        C_child = C_reclaimed + C_seed
    
    This ensures:
    1. Value flows upward through compression (parent gets 90%)
    2. Child always has seed capital to restart (10%)
    3. No ceramic is created or destroyed (conservation)
    
    For the Priestley Proof (revenue capture):
        Total Network Value = Σ(C_floor) + Σ(reclaimed over time)
        Every fold ADDS to parent ceramic, creating deflationary pressure.
    
    Args:
        ceramic_mass: Total $HCL in the floor before compression
    
    Returns:
        Dict with 'reclaimed_to_parent', 'seed_for_restart', 'conservation_check'
    """
    ceramic_mass = max(Decimal('0'), ceramic_mass)
    
    reclaimed = (ceramic_mass * RECLAIM_RATIO).quantize(Decimal('0.00000001'))
    seed = (ceramic_mass * SEED_RATIO).quantize(Decimal('0.00000001'))
    
    # Conservation check: should equal original (within precision)
    conservation = reclaimed + seed
    is_conserved = abs(conservation - ceramic_mass) < Decimal('0.00000001')
    
    return {
        'reclaimed_to_parent': reclaimed,
        'seed_for_restart': seed,
        'original_mass': ceramic_mass,
        'conservation_check': is_conserved,
    }


def calculate_depth(node: LineageNode, ancestry_map: Dict[str, LineageNode]) -> int:
    """
    Calculate the depth of a node in the ancestry tree.
    
        depth(genesis) = 1
        depth(child) = depth(parent) + 1
    
    Uses recursive lookup through parent chain.
    
    Args:
        node: The LineageNode to calculate depth for
        ancestry_map: Dict of floor_id -> LineageNode for parent lookup
    
    Returns:
        Integer depth (1 for genesis, 2 for first children, etc.)
    """
    if node.parent_id is None:
        return 1
    
    parent = ancestry_map.get(node.parent_id)
    if parent is None:
        return 1  # Orphan node treated as genesis
    
    return 1 + calculate_depth(parent, ancestry_map)


def calculate_shear_from_metrics(ceramic: Decimal, clay: Decimal) -> Decimal:
    """
    Calculate shear force from raw metrics.
    
        σ = Clay / (Ceramic × 10)
    
    Matches the formula in physics.py for consistency.
    
    Args:
        ceramic: $HCL mass
        clay: $HCB volume
    
    Returns:
        σ bounded to [0, 1] (clamped at 1.0 for visualization)
    """
    if ceramic <= 0:
        return Decimal('0')
    
    max_safe = ceramic * 10
    sigma = clay / max_safe
    
    # Clamp to [0, 1] for display purposes
    return min(sigma, Decimal('1.0')).quantize(Decimal('0.0001'))


# ═══════════════════════════════════════════════════════════════════════════════
# LINEAGE CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class LineageCalculator:
    """
    The ancestry engine for the Hardcard Multiverse.
    
    Builds a complete map of floor ancestry from fossil records,
    calculates cumulative shear across generations, and tracks
    ceramic flow through the lineage.
    """
    
    def __init__(self, fossils_dir: Path = FOSSILS_DIR):
        self.fossils_dir = fossils_dir
        self.ancestry_map: Dict[str, LineageNode] = {}
        self.genesis_id: Optional[str] = None
    
    def load_fossils(self) -> List[Dict[str, Any]]:
        """Load all fossil records from disk."""
        fossils = []
        
        if not self.fossils_dir.exists():
            return fossils
        
        for fossil_file in sorted(self.fossils_dir.glob("*.fossil")):
            try:
                data = json.loads(fossil_file.read_text())
                data['_file'] = fossil_file.name
                data['_hash'] = fossil_file.stem.split('_')[-1]
                fossils.append(data)
            except (json.JSONDecodeError, IOError):
                continue
        
        return fossils
    
    def load_active_floors(self) -> List[Dict[str, Any]]:
        """Load all active floor manifests from disk."""
        floors = []
        floors_dir = Path(".hardcard/floors")
        
        if not floors_dir.exists():
            return floors
        
        for floor_file in sorted(floors_dir.glob("*.floor")):
            try:
                data = json.loads(floor_file.read_text())
                data['_file'] = floor_file.name
                data['_is_active'] = True
                floors.append(data)
            except (json.JSONDecodeError, IOError):
                continue
        
        return floors
    
    def build_ancestry_map(self) -> Dict[str, LineageNode]:
        """
        Build the complete ancestry map from fossil records AND active floors.
        
        Process:
        1. Load all fossils
        2. Load all active floor manifests
        3. Create LineageNode for each floor
        4. Calculate local shear from frozen metrics
        5. Link parent-child relationships
        6. Calculate cumulative shear recursively
        7. Compute depths
        
        Returns:
            Dict mapping floor_id to LineageNode
        """
        fossils = self.load_fossils()
        active_floors = self.load_active_floors()
        
        # Phase 1a: Create nodes from fossils
        for fossil in fossils:
            floor_id = fossil.get('floor_id', 'unknown')
            fossil_hash = fossil.get('_hash', '')
            archived_at = fossil.get('archived_at', 0)
            
            # Extract metrics
            metrics = fossil.get('metrics_snapshot', {})
            ceramic = Decimal(str(metrics.get('agent_gdp_reserve', '0')))
            
            # Calculate clay from signals
            signals = fossil.get('signals_snapshot', {})
            clay = sum(Decimal(str(s.get('reward', '0'))) for s in signals.values())
            if clay == 0:
                clay = ceramic * 9  # Default 9:1 ratio
            
            # Calculate local shear
            local_shear = calculate_shear_from_metrics(ceramic, clay)
            
            # Determine parent (for now, genesis has no parent)
            parent_id = fossil.get('parent_floor_id', None)
            
            node = LineageNode(
                floor_id=floor_id,
                local_shear=local_shear,
                ceramic_mass=ceramic,
                clay_volume=clay,
                parent_id=parent_id,
                fossil_hash=fossil_hash,
                archived_at=archived_at,
            )
            
            # Track genesis (first floor with no parent)
            if parent_id is None and self.genesis_id is None:
                self.genesis_id = floor_id
            
            self.ancestry_map[floor_id] = node
        
        # Phase 1b: Create nodes from active floors
        for floor in active_floors:
            floor_id = floor.get('floor_id', 'unknown')
            
            # Skip if already in map from fossils (fossils are historical)
            if floor_id in self.ancestry_map:
                continue
            
            # Extract state from manifest
            initial_state = floor.get('initial_state', {})
            ceramic = Decimal(str(initial_state.get('ceramic_mass', '0')))
            clay = Decimal(str(initial_state.get('clay_volume', '0')))
            local_shear = Decimal(str(initial_state.get('local_shear', '0.1')))
            cumulative_shear = Decimal(str(initial_state.get('cumulative_shear', '0')))
            
            parent_id = floor.get('parent_id', None)
            depth = floor.get('depth', 1)
            created_at = floor.get('created_at', 0)
            spawn_hash = floor.get('spawn_hash', '')
            
            node = LineageNode(
                floor_id=floor_id,
                depth=depth,
                local_shear=local_shear,
                cumulative_shear=cumulative_shear,
                ceramic_mass=ceramic,
                clay_volume=clay,
                parent_id=parent_id,
                fossil_hash=spawn_hash,  # Use spawn hash for active floors
                archived_at=created_at,  # Use created_at for active floors
            )
            
            self.ancestry_map[floor_id] = node
            
            # Link as child of parent
            if parent_id and parent_id in self.ancestry_map:
                parent = self.ancestry_map[parent_id]
                if floor_id not in parent.children:
                    parent.children.append(floor_id)
        
        if not self.ancestry_map:
            return {}
        
        # Phase 2: Calculate depths (for floors without explicit depth)
        for node in self.ancestry_map.values():
            if node.depth == 0 or node.depth is None:
                node.depth = calculate_depth(node, self.ancestry_map)
        
        # Phase 3: Calculate cumulative shear for fossils (active floors already have it)
        nodes_by_depth = sorted(self.ancestry_map.values(), key=lambda n: n.depth)
        
        for node in nodes_by_depth:
            # Skip active floors that already have cumulative shear calculated
            if node.cumulative_shear > 0:
                continue
            
            if node.parent_id and node.parent_id in self.ancestry_map:
                parent = self.ancestry_map[node.parent_id]
                node.cumulative_shear = calculate_recursive_shear(
                    node.local_shear, 
                    parent.cumulative_shear
                )
            else:
                # Genesis or orphan
                node.cumulative_shear = calculate_recursive_shear(node.local_shear)
        
        return self.ancestry_map
    
    def get_genesis(self) -> Optional[LineageNode]:
        """Get the genesis (root) node of the lineage."""
        if not self.ancestry_map:
            self.build_ancestry_map()
        
        if self.genesis_id:
            return self.ancestry_map.get(self.genesis_id)
        return None
    
    def get_lineage_summary(self) -> Dict[str, Any]:
        """
        Generate a complete lineage summary.
        
        Returns:
            Dict with total_floors, max_depth, total_shear, ceramic_metrics, etc.
        """
        if not self.ancestry_map:
            self.build_ancestry_map()
        
        if not self.ancestry_map:
            return {
                'total_floors': 0,
                'max_depth': 0,
                'genesis': None,
                'total_ceramic': '0',
                'total_clay': '0',
                'average_shear': '0',
            }
        
        total_ceramic = sum(n.ceramic_mass for n in self.ancestry_map.values())
        total_clay = sum(n.clay_volume for n in self.ancestry_map.values())
        max_depth = max(n.depth for n in self.ancestry_map.values())
        avg_shear = sum(n.local_shear for n in self.ancestry_map.values()) / len(self.ancestry_map)
        
        genesis = self.get_genesis()
        
        return {
            'total_floors': len(self.ancestry_map),
            'max_depth': max_depth,
            'genesis': genesis.to_dict() if genesis else None,
            'total_ceramic': str(total_ceramic.quantize(Decimal('0.00000001'))),
            'total_clay': str(total_clay.quantize(Decimal('0.00000001'))),
            'average_shear': str(avg_shear.quantize(Decimal('0.0001'))),
            'floors': [n.to_dict() for n in sorted(self.ancestry_map.values(), key=lambda n: n.depth)],
        }
    
    def render_tree(self, max_depth: int = 10) -> str:
        """
        Render the ancestry tree as ASCII art.
        
        Returns:
            Formatted string showing the lineage tree
        """
        if not self.ancestry_map:
            self.build_ancestry_map()
        
        lines = []
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + "  🌳 LINEAGE TREE — RECURSIVE ANCESTRY MAP".center(58) + "║")
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        if not self.ancestry_map:
            lines.append("   🌱 No fossils found. The lineage awaits its first ancestor.")
            return "\n".join(lines)
        
        # Group by depth
        nodes_by_depth = sorted(self.ancestry_map.values(), key=lambda n: n.depth)
        
        for node in nodes_by_depth:
            if node.depth > max_depth:
                continue
            
            indent = "   " + "│  " * (node.depth - 1)
            branch = "└──" if node.depth > 1 else ""
            
            ts = datetime.fromtimestamp(node.archived_at).strftime('%Y-%m-%d') if node.archived_at else "N/A"
            
            lines.append(f"{indent}{branch} 🗿 {node.floor_id}_{node.fossil_hash[:8] if node.fossil_hash else 'live'}")
            lines.append(f"{indent}    ├─ Depth: {node.depth}")
            lines.append(f"{indent}    ├─ Local σ: {node.local_shear}")
            lines.append(f"{indent}    ├─ Cumulative S(n): {node.cumulative_shear}")
            lines.append(f"{indent}    ├─ Ceramic: {node.ceramic_mass} $HCL")
            lines.append(f"{indent}    └─ Archived: {ts}")
            lines.append("")
        
        # Summary
        summary = self.get_lineage_summary()
        lines.append("─" * 60)
        lines.append(f"   📊 LINEAGE METRICS")
        lines.append(f"   ├─ Total Floors: {summary['total_floors']}")
        lines.append(f"   ├─ Max Depth: {summary['max_depth']}")
        lines.append(f"   ├─ Total Ceramic: {summary['total_ceramic']} $HCL")
        lines.append(f"   └─ Average Shear: {summary['average_shear']}")
        lines.append("")
        
        return "\n".join(lines)
    
    def simulate_fold(self, floor_id: str) -> Dict[str, Any]:
        """
        Simulate a dimensional fold and calculate ceramic flow.
        
        Args:
            floor_id: The floor that is folding
        
        Returns:
            Dict with fold simulation results
        """
        if floor_id not in self.ancestry_map:
            return {'error': f'Floor {floor_id} not found in ancestry map'}
        
        node = self.ancestry_map[floor_id]
        flow = calculate_ceramic_flow(node.ceramic_mass)
        
        # Calculate new cumulative shear after fold
        # After fold, local shear resets to seed state (0.1)
        new_local_shear = Decimal('0.1')
        if node.parent_id and node.parent_id in self.ancestry_map:
            parent = self.ancestry_map[node.parent_id]
            new_cumulative = calculate_recursive_shear(new_local_shear, parent.cumulative_shear)
        else:
            new_cumulative = calculate_recursive_shear(new_local_shear)
        
        return {
            'floor_id': floor_id,
            'pre_fold': {
                'ceramic': str(node.ceramic_mass),
                'local_shear': str(node.local_shear),
                'cumulative_shear': str(node.cumulative_shear),
            },
            'fold': {
                'reclaimed_to_parent': str(flow['reclaimed_to_parent']),
                'seed_for_restart': str(flow['seed_for_restart']),
                'conservation_verified': flow['conservation_check'],
            },
            'post_fold': {
                'ceramic': str(flow['seed_for_restart']),
                'local_shear': str(new_local_shear),
                'cumulative_shear': str(new_cumulative),
            },
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_lineage_calculator() -> LineageCalculator:
    """Factory function for LineageCalculator."""
    return LineageCalculator()


def display_lineage(max_depth: int = 10, show_shear: bool = False) -> str:
    """
    Display the lineage tree for CLI output.
    
    Args:
        max_depth: Maximum depth to display
        show_shear: Include detailed shear metrics
    
    Returns:
        Formatted string for terminal output
    """
    calc = get_lineage_calculator()
    output = calc.render_tree(max_depth)
    
    if show_shear:
        output += "\n" + "─" * 60
        output += "\n   🧮 RECURSIVE SHEAR FORMULA"
        output += "\n   ├─ S(n) = σₙ + λ·S(n-1)"
        output += "\n   ├─ λ = 0.9 (decay factor)"
        output += f"\n   └─ Convergence bound: S(∞) ≤ 10·σ"
        output += "\n"
    
    return output


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(display_lineage(show_shear=True))
