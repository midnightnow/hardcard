#!/usr/bin/env python3
"""
Hardcard Audit Dashboard: audit.py
The "Mission Control" for the Hardcard Multiverse.

This module provides comprehensive visibility into:
- Total Network Value (Live Ceramic + Fossilized Seed)
- Brittleness Heatmap (floors approaching structural limits)
- Lineage Efficiency (reclamation tracking)
- Conservation Verification (ensuring no ceramic is lost)

The dashboard is the "truth layer" that makes the multiverse observable.
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

FLOORS_DIR = Path(".hardcard/floors")
FOSSILS_DIR = Path(".hardcard/fossils")
HYPERSPACE_DIR = Path(".hardcard/hyperspace")

# Brittleness thresholds
SHEAR_STABLE = Decimal('0.3')      # Green zone
SHEAR_WARNING = Decimal('0.6')     # Yellow zone
SHEAR_CRITICAL = Decimal('0.9')    # Red zone (fracture imminent)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FloorMetrics:
    """Metrics for a single floor (live or fossilized)."""
    floor_id: str
    status: str  # 'LIVE', 'FOLDED', 'CRITICAL'
    depth: int
    ceramic_mass: Decimal
    local_shear: Decimal
    cumulative_shear: Decimal
    parent_id: Optional[str]
    created_at: int
    brittleness: str  # 'STABLE', 'WARNING', 'CRITICAL'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'floor_id': self.floor_id,
            'status': self.status,
            'depth': self.depth,
            'ceramic_mass': str(self.ceramic_mass),
            'local_shear': str(self.local_shear),
            'cumulative_shear': str(self.cumulative_shear),
            'parent_id': self.parent_id,
            'created_at': self.created_at,
            'brittleness': self.brittleness,
        }


@dataclass
class NetworkState:
    """Complete state of the Hardcard Multiverse."""
    # Value Metrics
    live_ceramic: Decimal = Decimal('0')
    fossilized_seed: Decimal = Decimal('0')
    total_network_value: Decimal = Decimal('0')
    
    # Floor Counts
    active_floors: int = 0
    fossilized_floors: int = 0
    total_floors: int = 0
    
    # Structural Metrics
    max_depth: int = 0
    average_shear: Decimal = Decimal('0')
    brittleness_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Efficiency Metrics
    total_reclaimed: Decimal = Decimal('0')
    total_spawned: Decimal = Decimal('0')
    reclamation_efficiency: Decimal = Decimal('0')
    
    # Floor Details
    live_floors: List[FloorMetrics] = field(default_factory=list)
    fossil_floors: List[FloorMetrics] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': {
                'live_ceramic': str(self.live_ceramic),
                'fossilized_seed': str(self.fossilized_seed),
                'total_network_value': str(self.total_network_value),
            },
            'counts': {
                'active_floors': self.active_floors,
                'fossilized_floors': self.fossilized_floors,
                'total_floors': self.total_floors,
            },
            'structure': {
                'max_depth': self.max_depth,
                'average_shear': str(self.average_shear),
                'brittleness_distribution': self.brittleness_distribution,
            },
            'efficiency': {
                'total_reclaimed': str(self.total_reclaimed),
                'total_spawned': str(self.total_spawned),
                'reclamation_efficiency': str(self.reclamation_efficiency),
            },
            'floors': {
                'live': [f.to_dict() for f in self.live_floors],
                'fossilized': [f.to_dict() for f in self.fossil_floors],
            },
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class AuditEngine:
    """
    The comprehensive audit engine for the Hardcard Multiverse.
    
    Scans all active floors and fossils to provide a complete picture
    of the network's health, value distribution, and structural integrity.
    """
    
    def __init__(self):
        self.floors_dir = FLOORS_DIR
        self.fossils_dir = FOSSILS_DIR
        self.hyperspace_dir = HYPERSPACE_DIR
    
    def _calculate_brittleness(self, cumulative_shear: Decimal) -> str:
        """Determine brittleness level from cumulative shear."""
        if cumulative_shear >= SHEAR_CRITICAL:
            return 'CRITICAL'
        elif cumulative_shear >= SHEAR_WARNING:
            return 'WARNING'
        return 'STABLE'
    
    def _load_live_floors(self) -> List[FloorMetrics]:
        """Load all active floor metrics."""
        floors = []
        
        if not self.floors_dir.exists():
            return floors
        
        for floor_file in self.floors_dir.glob("*.floor"):
            try:
                data = json.loads(floor_file.read_text())
                initial = data.get('initial_state', {})
                
                ceramic = Decimal(str(initial.get('ceramic_mass', '0')))
                local_shear = Decimal(str(initial.get('local_shear', '0')))
                cumulative = Decimal(str(initial.get('cumulative_shear', '0')))
                
                # For genesis, use local_shear as cumulative if not set
                if cumulative == 0 and local_shear > 0:
                    cumulative = local_shear
                
                metrics = FloorMetrics(
                    floor_id=data.get('floor_id', 'unknown'),
                    status='LIVE',
                    depth=data.get('depth', 1),
                    ceramic_mass=ceramic,
                    local_shear=local_shear,
                    cumulative_shear=cumulative,
                    parent_id=data.get('parent_id'),
                    created_at=data.get('created_at', 0),
                    brittleness=self._calculate_brittleness(cumulative),
                )
                floors.append(metrics)
            except (json.JSONDecodeError, IOError):
                continue
        
        return floors
    
    def _load_fossil_floors(self) -> List[FloorMetrics]:
        """Load all fossilized floor metrics (fold events only)."""
        floors = []
        
        if not self.fossils_dir.exists():
            return floors
        
        for fossil_file in self.fossils_dir.glob("*.fossil"):
            try:
                data = json.loads(fossil_file.read_text())
                
                # Only include fold events for fossilized seed calculation
                # Genesis backup fossils are NOT fold events (they represent primordial state)
                if not data.get('fold_event', False):
                    continue
                
                metrics_snapshot = data.get('metrics_snapshot', {})
                
                # Fold fossil - seed_preserved is the frozen ceramic
                ceramic = Decimal(str(metrics_snapshot.get('seed_preserved', '0')))
                local_shear = Decimal(str(metrics_snapshot.get('local_shear', '0')))
                cumulative = Decimal(str(metrics_snapshot.get('cumulative_shear', '0')))
                
                metrics = FloorMetrics(
                    floor_id=data.get('floor_id', 'unknown'),
                    status='FOLDED',
                    depth=data.get('depth', 1),
                    ceramic_mass=ceramic,
                    local_shear=local_shear,
                    cumulative_shear=cumulative,
                    parent_id=data.get('parent_id'),
                    created_at=data.get('archived_at', 0),
                    brittleness=self._calculate_brittleness(cumulative),
                )
                floors.append(metrics)
            except (json.JSONDecodeError, IOError):
                continue
        
        return floors
    
    def _calculate_reclamation_totals(self) -> tuple[Decimal, Decimal]:
        """Calculate total reclaimed and spawned ceramic from fossils."""
        total_reclaimed = Decimal('0')
        total_spawned = Decimal('0')
        
        if not self.fossils_dir.exists():
            return total_reclaimed, total_spawned
        
        for fossil_file in self.fossils_dir.glob("*.fossil"):
            try:
                data = json.loads(fossil_file.read_text())
                metrics = data.get('metrics_snapshot', {})
                
                if data.get('fold_event', False):
                    # Fold fossil - track reclamation
                    reclaimed = Decimal(str(metrics.get('reclaimed_to_parent', '0')))
                    total_reclaimed += reclaimed
                
                # Track spawned (ceramic at fold = what was spawned originally)
                ceramic_at_fold = Decimal(str(metrics.get('ceramic_at_fold', '0')))
                if ceramic_at_fold > 0:
                    total_spawned += ceramic_at_fold
            except (json.JSONDecodeError, IOError):
                continue
        
        return total_reclaimed, total_spawned
    
    def scan_network(self) -> NetworkState:
        """
        Perform a complete scan of the network state.
        
        Returns:
            NetworkState with all metrics populated
        """
        state = NetworkState()
        
        # Load all floors
        live_floors = self._load_live_floors()
        fossil_floors = self._load_fossil_floors()
        
        state.live_floors = live_floors
        state.fossil_floors = fossil_floors
        
        # Calculate value metrics
        state.live_ceramic = sum(f.ceramic_mass for f in live_floors)
        state.fossilized_seed = sum(f.ceramic_mass for f in fossil_floors)
        state.total_network_value = state.live_ceramic + state.fossilized_seed
        
        # Calculate counts
        state.active_floors = len(live_floors)
        state.fossilized_floors = len(fossil_floors)
        state.total_floors = state.active_floors + state.fossilized_floors
        
        # Calculate structural metrics
        all_floors = live_floors + fossil_floors
        if all_floors:
            state.max_depth = max(f.depth for f in all_floors)
            total_shear = sum(f.cumulative_shear for f in all_floors)
            state.average_shear = (total_shear / len(all_floors)).quantize(Decimal('0.0001'))
        
        # Brittleness distribution (live floors only)
        state.brittleness_distribution = {
            'STABLE': sum(1 for f in live_floors if f.brittleness == 'STABLE'),
            'WARNING': sum(1 for f in live_floors if f.brittleness == 'WARNING'),
            'CRITICAL': sum(1 for f in live_floors if f.brittleness == 'CRITICAL'),
        }
        
        # Efficiency metrics
        total_reclaimed, total_spawned = self._calculate_reclamation_totals()
        state.total_reclaimed = total_reclaimed
        state.total_spawned = total_spawned
        if total_spawned > 0:
            state.reclamation_efficiency = (total_reclaimed / total_spawned * 100).quantize(Decimal('0.01'))
        
        return state
    
    def get_brittleness_heatmap(self) -> List[Dict[str, Any]]:
        """
        Get a sorted list of floors by brittleness (most critical first).
        """
        live_floors = self._load_live_floors()
        
        # Sort by cumulative shear (descending)
        sorted_floors = sorted(live_floors, key=lambda f: f.cumulative_shear, reverse=True)
        
        return [
            {
                'floor_id': f.floor_id,
                'cumulative_shear': str(f.cumulative_shear),
                'brittleness': f.brittleness,
                'depth': f.depth,
                'ceramic': str(f.ceramic_mass),
            }
            for f in sorted_floors
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# CLI DISPLAY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def display_network_audit(state: NetworkState) -> str:
    """Format the network state for CLI display."""
    lines = []
    
    # Header
    lines.append("╔" + "═" * 62 + "╗")
    lines.append("║" + "  🏛️  HARDCARD MULTIVERSE AUDIT — NETWORK STATE".center(62) + "║")
    lines.append("╚" + "═" * 62 + "╝")
    lines.append("")
    
    # Value Metrics
    lines.append("┌" + "─" * 62 + "┐")
    lines.append("│" + "  💰 TOTAL NETWORK VALUE".ljust(62) + "│")
    lines.append("├" + "─" * 62 + "┤")
    lines.append(f"│    Live Ceramic:       {float(state.live_ceramic):>15.8f} $HCL".ljust(62) + "  │")
    lines.append(f"│    Fossilized Seed:    {float(state.fossilized_seed):>15.8f} $HCL".ljust(62) + "  │")
    lines.append("│" + "    " + "─" * 40 + "".ljust(14) + "  │")
    lines.append(f"│    TOTAL VALUE:        {float(state.total_network_value):>15.8f} $HCL".ljust(62) + "  │")
    lines.append("└" + "─" * 62 + "┘")
    lines.append("")
    
    # Floor Counts
    lines.append("┌" + "─" * 62 + "┐")
    lines.append("│" + "  🏗️ FLOOR INVENTORY".ljust(62) + "│")
    lines.append("├" + "─" * 62 + "┤")
    lines.append(f"│    Active Floors:      {state.active_floors:>15}".ljust(62) + "  │")
    lines.append(f"│    Fossilized Floors:  {state.fossilized_floors:>15}".ljust(62) + "  │")
    lines.append(f"│    Max Depth:          {state.max_depth:>15}".ljust(62) + "  │")
    lines.append("└" + "─" * 62 + "┘")
    lines.append("")
    
    # Brittleness Heatmap
    lines.append("┌" + "─" * 62 + "┐")
    lines.append("│" + "  🌡️ BRITTLENESS HEATMAP".ljust(62) + "│")
    lines.append("├" + "─" * 62 + "┤")
    
    stable = state.brittleness_distribution.get('STABLE', 0)
    warning = state.brittleness_distribution.get('WARNING', 0)
    critical = state.brittleness_distribution.get('CRITICAL', 0)
    
    lines.append(f"│    🟢 STABLE (S(n) < 0.3):    {stable:>5} floors".ljust(62) + "  │")
    lines.append(f"│    🟡 WARNING (S(n) < 0.6):   {warning:>5} floors".ljust(62) + "  │")
    lines.append(f"│    🔴 CRITICAL (S(n) ≥ 0.9):  {critical:>5} floors".ljust(62) + "  │")
    lines.append("│" + "".ljust(62) + "│")
    lines.append(f"│    Average Shear:      {float(state.average_shear):>15.4f}".ljust(62) + "  │")
    lines.append("└" + "─" * 62 + "┘")
    lines.append("")
    
    # Efficiency Metrics
    if state.total_spawned > 0:
        lines.append("┌" + "─" * 62 + "┐")
        lines.append("│" + "  📊 LINEAGE EFFICIENCY".ljust(62) + "│")
        lines.append("├" + "─" * 62 + "┤")
        lines.append(f"│    Total Spawned:      {float(state.total_spawned):>15.8f} $HCL".ljust(62) + "  │")
        lines.append(f"│    Total Reclaimed:    {float(state.total_reclaimed):>15.8f} $HCL".ljust(62) + "  │")
        lines.append(f"│    Reclamation Rate:   {float(state.reclamation_efficiency):>14.2f}%".ljust(62) + "  │")
        lines.append("└" + "─" * 62 + "┘")
        lines.append("")
    
    # Conservation Check
    lines.append("┌" + "─" * 62 + "┐")
    lines.append("│" + "  ⚖️ CONSERVATION CHECK".ljust(62) + "│")
    lines.append("├" + "─" * 62 + "┤")
    
    # Calculate expected value (from genesis fossil or known initial)
    expected = Decimal('10.0')  # Genesis starts with 10 $HCL
    actual = state.total_network_value
    delta = actual - expected
    
    if abs(delta) < Decimal('0.00000001'):
        status = "✅ CONSERVED"
        delta_str = "±0.0"
    elif delta > 0:
        status = "⚠️ SURPLUS"
        delta_str = f"+{float(delta):.8f}"
    else:
        status = "⚠️ DEFICIT"
        delta_str = f"{float(delta):.8f}"
    
    lines.append(f"│    Expected Value:     {float(expected):>15.8f} $HCL".ljust(62) + "  │")
    lines.append(f"│    Actual Value:       {float(actual):>15.8f} $HCL".ljust(62) + "  │")
    lines.append(f"│    Delta:              {delta_str:>15} $HCL".ljust(62) + "  │")
    lines.append(f"│    Status:             {status:>15}".ljust(62) + "  │")
    lines.append("└" + "─" * 62 + "┘")
    
    return "\n".join(lines)


def display_live_floors(state: NetworkState) -> str:
    """Display detailed list of live floors."""
    lines = []
    
    lines.append("")
    lines.append("─" * 64)
    lines.append("  📋 ACTIVE FLOORS")
    lines.append("─" * 64)
    
    if not state.live_floors:
        lines.append("  (No active floors)")
        return "\n".join(lines)
    
    # Sort by depth
    sorted_floors = sorted(state.live_floors, key=lambda f: f.depth)
    
    for f in sorted_floors:
        icon = {'STABLE': '🟢', 'WARNING': '🟡', 'CRITICAL': '🔴'}.get(f.brittleness, '⚪')
        lines.append(f"  {icon} {f.floor_id}")
        lines.append(f"      ├─ Depth: {f.depth} | Ceramic: {f.ceramic_mass} $HCL")
        lines.append(f"      └─ S(n): {f.cumulative_shear} | Status: {f.brittleness}")
    
    return "\n".join(lines)


def get_audit_engine() -> AuditEngine:
    """Factory function for AuditEngine."""
    return AuditEngine()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    engine = AuditEngine()
    state = engine.scan_network()
    print(display_network_audit(state))
    print(display_live_floors(state))
