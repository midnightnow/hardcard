#!/usr/bin/env python3
"""
Hardcard Spawn Protocol: spawn.py
The "First Breath" for child nodes in the Hardcard Multiverse.

This module implements the parent-child floor relationship, including:
- Ceramic commitment (10% parent → child seed)
- Ancestry handshake (cryptographic tethering)
- Shear inheritance (S(child) = σ_initial + λ·S(parent))
- Depth increment (d(child) = d(parent) + 1)

Physics: Spawning is not free. It costs ceramic and transfers ancestral weight.
"""

import json
import hashlib
import time
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional, Any, List

from .lineage import (
    calculate_recursive_shear,
    calculate_ceramic_flow,
    LineageCalculator,
    LineageNode,
    DECAY_FACTOR,
)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

SEED_RATIO = Decimal('0.10')         # 10% of parent ceramic seeds child
MIN_CERAMIC_TO_SPAWN = Decimal('1.0') # Minimum parent ceramic required
INITIAL_CHILD_SHEAR = Decimal('0.1')  # Initial σ for newborn floor
FLOORS_DIR = Path(".hardcard/floors")
HYPERSPACE_DIR = Path(".hardcard/hyperspace")

# Fracture Thresholds — structural limits on spawning
SHEAR_WARNING = Decimal('0.7')        # Warning zone: S(n) ≥ 0.7
SHEAR_CRITICAL = Decimal('0.9')       # Fracture zone: S(n) ≥ 0.9 blocks spawn


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SpawnResult:
    """Result of a spawn operation."""
    success: bool
    child_id: str
    parent_id: str
    spawn_hash: str
    seed_ceramic: Decimal
    child_depth: int
    child_cumulative_shear: Decimal
    parent_remaining_ceramic: Decimal
    error: Optional[str] = None
    manifest_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'child_id': self.child_id,
            'parent_id': self.parent_id,
            'spawn_hash': self.spawn_hash,
            'seed_ceramic': str(self.seed_ceramic),
            'child_depth': self.child_depth,
            'child_cumulative_shear': str(self.child_cumulative_shear),
            'parent_remaining_ceramic': str(self.parent_remaining_ceramic),
            'error': self.error,
            'manifest_path': str(self.manifest_path) if self.manifest_path else None,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CORE SPAWN FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_seed_transfer(parent_ceramic: Decimal) -> Dict[str, Decimal]:
    """
    Calculate the ceramic transfer for spawning a child.
    
    Economic Layer:
    - Seed = 10% of parent ceramic
    - Parent retains 90%
    
    Args:
        parent_ceramic: Current $HCL balance of parent
    
    Returns:
        Dict with 'seed', 'parent_remaining', 'transfer_ratio'
    """
    seed = (parent_ceramic * SEED_RATIO).quantize(Decimal('0.00000001'))
    remaining = (parent_ceramic - seed).quantize(Decimal('0.00000001'))
    
    return {
        'seed': seed,
        'parent_remaining': remaining,
        'transfer_ratio': SEED_RATIO,
    }


def cryptographic_handshake(parent_id: str, child_id: str, parent_state_hash: str) -> str:
    """
    Generate the spawn hash that cryptographically ties child to parent.
    
    Cryptographic Layer:
    - Hash = SHA256(parent_id : child_id : parent_state_hash : timestamp)
    
    This ensures:
    1. Child cannot exist without parent's acknowledgment
    2. The exact moment of birth is recorded
    3. Parent's state at spawn time is frozen into child's genesis
    
    Args:
        parent_id: ID of the parent floor
        child_id: ID of the new child floor
        parent_state_hash: Current state hash of parent
    
    Returns:
        16-character hex spawn hash
    """
    timestamp = int(time.time())
    data = f"{parent_id}:{child_id}:{parent_state_hash}:{timestamp}".encode()
    spawn_hash = hashlib.sha256(data).hexdigest()[:16]
    return spawn_hash


def calculate_inherited_shear(parent_cumulative: Decimal) -> Decimal:
    """
    Calculate the cumulative shear a child inherits from parent.
    
    Structural Layer:
    S(child) = σ_initial + λ·S(parent)
    
    Where:
    - σ_initial = 0.1 (child starts with minimal stress)
    - λ = 0.9 (decay factor)
    - S(parent) = parent's cumulative shear
    
    Args:
        parent_cumulative: Parent's S(n) value
    
    Returns:
        Child's initial cumulative shear
    """
    return calculate_recursive_shear(INITIAL_CHILD_SHEAR, parent_cumulative)


def create_floor_manifest(
    child_id: str,
    parent_id: str,
    spawn_hash: str,
    seed_ceramic: Decimal,
    child_depth: int,
    parent_cumulative_shear: Decimal,
) -> Dict[str, Any]:
    """
    Create the genesis manifest for a new floor.
    
    This is the "birth certificate" of the floor, containing:
    - Identity (floor_id, parent_id, spawn_hash)
    - Initial state (ceramic, shear)
    - Ancestry data (depth, parent shear)
    - Constitutional inheritance
    
    Args:
        child_id: New floor's ID
        parent_id: Parent floor's ID
        spawn_hash: Cryptographic handshake hash
        seed_ceramic: Initial $HCL (from parent)
        child_depth: Depth in ancestry tree
        parent_cumulative_shear: Parent's S(n) at spawn time
    
    Returns:
        Complete floor manifest as dict
    """
    child_cumulative = calculate_inherited_shear(parent_cumulative_shear)
    
    return {
        "floor_id": child_id,
        "parent_id": parent_id,
        "depth": child_depth,
        "created_at": int(time.time()),
        "spawn_hash": spawn_hash,
        "initial_state": {
            "ceramic_mass": str(seed_ceramic),
            "clay_volume": "0",
            "local_shear": str(INITIAL_CHILD_SHEAR),
            "cumulative_shear": str(child_cumulative),
        },
        "ancestry": {
            "parent_shear_at_birth": str(parent_cumulative_shear),
            "decay_factor": str(DECAY_FACTOR),
            "inheritance_formula": "S(n) = σₙ + λ·S(n-1)",
        },
        "constitution": {
            "inherited_from": parent_id,
            "integrity_fee": "10%",
            "anti_amnesia": True,
            "protocol_version": "HCL-07",
        },
        "status": "LIVE",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SPAWNER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Spawner:
    """
    The creation engine for child floors.
    
    Handles the complete spawn protocol:
    1. Validate parent eligibility
    2. Calculate and commit ceramic transfer
    3. Generate cryptographic handshake
    4. Create child manifest
    5. Update hyperspace registry
    """
    
    def __init__(self):
        self.floors_dir = FLOORS_DIR
        self.hyperspace_dir = HYPERSPACE_DIR
        self.lineage = LineageCalculator()
        self._last_warning = None  # For fracture threshold warnings
    
    def get_last_warning(self) -> Optional[str]:
        """Get the last warning message from spawn validation."""
        return self._last_warning
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.floors_dir.mkdir(parents=True, exist_ok=True)
        self.hyperspace_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_parent_state(self, parent_id: str) -> Optional[Dict[str, Any]]:
        """
        Load the current state of a parent floor.
        
        Checks both active floors and genesis.
        Priority:
        1. Active floor manifest (.hardcard/floors/{id}.floor)
        2. Nexus floor status (for genesis live state)
        3. Lineage calculator (for fossil data)
        4. Default genesis values
        """
        # Check for active floor manifest
        floor_file = self.floors_dir / f"{parent_id}.floor"
        if floor_file.exists():
            return json.loads(floor_file.read_text())
        
        # Check for genesis (special case)
        if parent_id == "genesis":
            # Try to get live status from nexus
            try:
                from .nexus import get_floor_status
                status = get_floor_status()
                if status and status.get('ceramic_mass', 0) > 0:
                    return {
                        "floor_id": "genesis",
                        "parent_id": None,
                        "depth": 1,
                        "initial_state": {
                            "ceramic_mass": str(status['ceramic_mass']),
                            "clay_volume": str(status.get('clay_volume', 0)),
                            "local_shear": str(status.get('shear_force', 0.1)),
                            "cumulative_shear": str(status.get('shear_force', 0.1)),
                        },
                        "status": status.get('status', 'LIVE'),
                    }
            except ImportError:
                pass
            
            # Fallback: Construct genesis state from fossils
            self.lineage.build_ancestry_map()
            genesis_node = self.lineage.get_genesis()
            if genesis_node and genesis_node.ceramic_mass > 0:
                return {
                    "floor_id": "genesis",
                    "parent_id": None,
                    "depth": 1,
                    "initial_state": {
                        "ceramic_mass": str(genesis_node.ceramic_mass),
                        "local_shear": str(genesis_node.local_shear),
                        "cumulative_shear": str(genesis_node.cumulative_shear),
                    },
                    "status": "LIVE",
                }
            
            # Default genesis state (10 $HCL)
            return {
                "floor_id": "genesis",
                "parent_id": None,
                "depth": 1,
                "initial_state": {
                    "ceramic_mass": "10.00000000",
                    "local_shear": "0.1",
                    "cumulative_shear": "0.1",
                },
                "status": "LIVE",
            }
        
        return None
    
    def _get_parent_ceramic(self, parent_state: Dict) -> Decimal:
        """Extract current ceramic mass from parent state."""
        initial = parent_state.get("initial_state", {})
        return Decimal(str(initial.get("ceramic_mass", "0")))
    
    def _get_parent_cumulative_shear(self, parent_state: Dict) -> Decimal:
        """Extract cumulative shear from parent state."""
        initial = parent_state.get("initial_state", {})
        return Decimal(str(initial.get("cumulative_shear", "0")))
    
    def _get_parent_depth(self, parent_state: Dict) -> int:
        """Extract depth from parent state."""
        return int(parent_state.get("depth", 1))
    
    def _generate_state_hash(self, parent_state: Dict) -> str:
        """Generate a hash of the parent's current state."""
        state_json = json.dumps(parent_state, sort_keys=True)
        return hashlib.sha256(state_json.encode()).hexdigest()[:16]
    
    def _save_floor_manifest(self, manifest: Dict) -> Path:
        """Save a floor manifest to disk."""
        floor_id = manifest["floor_id"]
        manifest_path = self.floors_dir / f"{floor_id}.floor"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        return manifest_path
    
    def _update_parent_ceramic(self, parent_id: str, new_ceramic: Decimal):
        """Update parent's ceramic balance after spawn."""
        floor_file = self.floors_dir / f"{parent_id}.floor"
        
        if floor_file.exists():
            parent_state = json.loads(floor_file.read_text())
            parent_state["initial_state"]["ceramic_mass"] = str(new_ceramic)
            floor_file.write_text(json.dumps(parent_state, indent=2))
        elif parent_id == "genesis":
            # Create genesis.floor to track its modified state
            genesis_state = self._load_parent_state("genesis")
            genesis_state["initial_state"]["ceramic_mass"] = str(new_ceramic)
            genesis_floor = self.floors_dir / "genesis.floor"
            genesis_floor.write_text(json.dumps(genesis_state, indent=2))
    
    def _update_hyperspace_registry(self, child_id: str, parent_id: str, spawn_hash: str):
        """Add the new floor to the hyperspace nodes registry."""
        nodes_file = self.hyperspace_dir / "nodes.json"
        
        if nodes_file.exists():
            nodes = json.loads(nodes_file.read_text())
        else:
            nodes = {"nodes": [], "spawn_events": []}
        
        # Add spawn event
        nodes.setdefault("spawn_events", []).append({
            "child_id": child_id,
            "parent_id": parent_id,
            "spawn_hash": spawn_hash,
            "timestamp": int(time.time()),
        })
        
        # Add to nodes list if not exists
        if child_id not in [n.get("floor_id") for n in nodes.get("nodes", [])]:
            nodes.setdefault("nodes", []).append({
                "floor_id": child_id,
                "parent_id": parent_id,
                "status": "LIVE",
            })
        
        nodes_file.write_text(json.dumps(nodes, indent=2))
    
    def validate_spawn(self, parent_id: str, allow_risk: bool = False) -> tuple[bool, str, Optional[Dict], Optional[str]]:
        """
        Validate that a spawn can occur.
        
        Args:
            parent_id: ID of the parent floor
            allow_risk: If True, bypass structural safety warnings (Sovereign Override)
            
        Returns:
            (is_valid, error_message, parent_state, warning_message)
        """
        parent_state = self._load_parent_state(parent_id)
        
        if parent_state is None:
            return False, f"Parent floor '{parent_id}' not found", None, None
        
        parent_ceramic = self._get_parent_ceramic(parent_state)
        
        if parent_ceramic < MIN_CERAMIC_TO_SPAWN:
            return False, f"Insufficient ceramic: {parent_ceramic} < {MIN_CERAMIC_TO_SPAWN} $HCL required", None, None
        
        # ═══ FRACTURE THRESHOLD CHECK ═══
        # Get parent's cumulative shear
        initial_state = parent_state.get('initial_state', {})
        parent_cumulative_shear = Decimal(str(initial_state.get('cumulative_shear', '0')))
        
        # For genesis, use local shear if cumulative not set
        if parent_cumulative_shear == 0:
            parent_cumulative_shear = Decimal(str(initial_state.get('local_shear', '0')))
        
        warning = None
        
        # 1. Check Parent Integrity
        if parent_cumulative_shear >= SHEAR_CRITICAL:
            return False, (
                f"⚠️ PARENT FRACTURED — Cannot spawn from '{parent_id}'\n"
                f"   Parent Shear S(n) = {parent_cumulative_shear} ≥ {SHEAR_CRITICAL}\n"
                f"   The foundation is too unstable to support a child."
            ), None, None
            
        # 2. Check Projected Child Integrity (The "Safety Buffer")
        child_projected_shear = calculate_inherited_shear(parent_cumulative_shear)
        
        if child_projected_shear >= SHEAR_CRITICAL:
            msg = (
                f"⚠️ FUTURE COMPROMISED — Child will be born Critical\n"
                f"   Projected S(n+1) = {child_projected_shear} ≥ {SHEAR_CRITICAL}\n"
                f"   This depth ({self._get_parent_depth(parent_state) + 1}) is in the Tail End."
            )
            
            if not allow_risk:
                return False, (
                    f"{msg}\n"
                    f"   🛑 SAFETY BUFFER ENGAGED.\n"
                    f"   Use '--risk' to override and accept structural instability."
                ), None, None
            else:
                warning = f"{msg}\n   🔓 SOVEREIGN OVERRIDE ACCEPTED."
        
        # WARNING: S(n) >= 0.7 — Floor is in warning zone
        elif parent_cumulative_shear >= SHEAR_WARNING:
            warning = (
                f"⚠️ WARNING: Floor '{parent_id}' is approaching fracture threshold\n"
                f"   Cumulative Shear S(n) = {parent_cumulative_shear} (threshold: {SHEAR_CRITICAL})\n"
                f"   Consider folding before spawning more children."
            )
        
        return True, "", parent_state, warning
    
    def spawn(self, parent_id: str, child_name: str, dry_run: bool = False, allow_risk: bool = False) -> SpawnResult:
        """
        Execute the complete spawn protocol.
        
        Args:
            parent_id: ID of the parent floor
            child_name: Name/ID for the new child floor
            dry_run: If True, simulate without creating files
            allow_risk: If True, bypass 'Tail End' safety checks
        
        Returns:
            SpawnResult with all spawn details
        """
        self._ensure_directories()
        
        # ═══ PHASE 1: Validation ═══
        is_valid, error, parent_state, warning = self.validate_spawn(parent_id, allow_risk)
        
        # Store warning for display (will be shown even on success)
        self._last_warning = warning
        
        if not is_valid:
            return SpawnResult(
                success=False,
                child_id=child_name,
                parent_id=parent_id,
                spawn_hash="",
                seed_ceramic=Decimal('0'),
                child_depth=0,
                child_cumulative_shear=Decimal('0'),
                parent_remaining_ceramic=Decimal('0'),
                error=error,
            )
        
        # ═══ PHASE 2: Economic Layer (Ceramic Transfer) ═══
        parent_ceramic = self._get_parent_ceramic(parent_state)
        transfer = calculate_seed_transfer(parent_ceramic)
        seed_ceramic = transfer['seed']
        parent_remaining = transfer['parent_remaining']
        
        # ═══ PHASE 3: Structural Layer (Depth & Shear) ═══
        parent_depth = self._get_parent_depth(parent_state)
        child_depth = parent_depth + 1
        
        parent_cumulative_shear = self._get_parent_cumulative_shear(parent_state)
        child_cumulative_shear = calculate_inherited_shear(parent_cumulative_shear)
        
        # ═══ PHASE 4: Cryptographic Layer (Handshake) ═══
        parent_state_hash = self._generate_state_hash(parent_state)
        spawn_hash = cryptographic_handshake(parent_id, child_name, parent_state_hash)
        
        # ═══ PHASE 5: Manifest Creation ═══
        manifest = create_floor_manifest(
            child_id=child_name,
            parent_id=parent_id,
            spawn_hash=spawn_hash,
            seed_ceramic=seed_ceramic,
            child_depth=child_depth,
            parent_cumulative_shear=parent_cumulative_shear,
        )
        
        manifest_path = None
        
        if not dry_run:
            # ═══ PHASE 6: State Anchoring ═══
            manifest_path = self._save_floor_manifest(manifest)
            self._update_parent_ceramic(parent_id, parent_remaining)
            self._update_hyperspace_registry(child_name, parent_id, spawn_hash)
        
        return SpawnResult(
            success=True,
            child_id=child_name,
            parent_id=parent_id,
            spawn_hash=spawn_hash,
            seed_ceramic=seed_ceramic,
            child_depth=child_depth,
            child_cumulative_shear=child_cumulative_shear,
            parent_remaining_ceramic=parent_remaining,
            manifest_path=manifest_path,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# CLI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def display_spawn_result(result: SpawnResult) -> str:
    """Format spawn result for CLI display."""
    if not result.success:
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    ❌ SPAWN FAILED                           ║
╚══════════════════════════════════════════════════════════════╝

   Error: {result.error}

   💡 Ensure parent floor has sufficient ceramic (min {MIN_CERAMIC_TO_SPAWN} $HCL)
"""
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║              🌱 SPAWN SUCCESSFUL — NEW FLOOR BORN            ║
╚══════════════════════════════════════════════════════════════╝

   📋 SPAWN MANIFEST
   ├─ Child ID:         {result.child_id}
   ├─ Parent ID:        {result.parent_id}
   ├─ Spawn Hash:       {result.spawn_hash}
   └─ Depth:            {result.child_depth}

   💰 CERAMIC TRANSFER
   ├─ Seed to Child:    {result.seed_ceramic} $HCL (10%)
   └─ Parent Retained:  {result.parent_remaining_ceramic} $HCL (90%)

   🧮 SHEAR INHERITANCE
   ├─ Formula:          S(n) = σₙ + λ·S(n-1)
   ├─ Child Initial σ:  {INITIAL_CHILD_SHEAR}
   └─ Child S(n):       {result.child_cumulative_shear}

───────────────────────────────────────────────────────────────
   💡 The child carries {float(DECAY_FACTOR)*100:.0f}% of the parent's cumulative shear.
      Run 'hardcard lineage --shear' to see the updated ancestry tree.
"""


def get_spawner() -> Spawner:
    """Factory function for Spawner."""
    return Spawner()


# ═══════════════════════════════════════════════════════════════════════════════
# FOLD PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════════

RECLAIM_RATIO = Decimal('0.9')   # 90% flows to parent
FOLD_SEED_RATIO = Decimal('0.1') # 10% preserved in fossil
FOSSILS_DIR = Path(".hardcard/fossils")


@dataclass
class FoldResult:
    """Result of a fold operation."""
    success: bool
    floor_id: str
    parent_id: Optional[str]
    ceramic_reclaimed: Decimal
    ceramic_seed: Decimal
    fossil_hash: str
    children_folded: List[str] = field(default_factory=list)
    error: Optional[str] = None
    fossil_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'floor_id': self.floor_id,
            'parent_id': self.parent_id,
            'ceramic_reclaimed': str(self.ceramic_reclaimed),
            'ceramic_seed': str(self.ceramic_seed),
            'fossil_hash': self.fossil_hash,
            'children_folded': self.children_folded,
            'error': self.error,
            'fossil_path': str(self.fossil_path) if self.fossil_path else None,
        }


class Folder:
    """
    The compression engine for floor folding.
    
    Handles the complete fold protocol:
    1. Cascade fold children first (depth-first)
    2. Calculate ceramic reclamation (90% to parent)
    3. Archive floor state as fossil
    4. Update parent ceramic balance
    5. Remove floor from active floors
    """
    
    def __init__(self):
        self.floors_dir = FLOORS_DIR
        self.fossils_dir = FOSSILS_DIR
        self.hyperspace_dir = HYPERSPACE_DIR
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.floors_dir.mkdir(parents=True, exist_ok=True)
        self.fossils_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_floor_state(self, floor_id: str) -> Optional[Dict[str, Any]]:
        """Load an active floor's state."""
        floor_file = self.floors_dir / f"{floor_id}.floor"
        if floor_file.exists():
            return json.loads(floor_file.read_text())
        return None
    
    def _get_floor_ceramic(self, floor_state: Dict) -> Decimal:
        """Extract ceramic mass from floor state."""
        initial = floor_state.get("initial_state", {})
        return Decimal(str(initial.get("ceramic_mass", "0")))
    
    def _find_children(self, parent_id: str) -> List[str]:
        """Find all active floor IDs that have this floor as parent."""
        children = []
        if not self.floors_dir.exists():
            return children
        
        for floor_file in self.floors_dir.glob("*.floor"):
            try:
                data = json.loads(floor_file.read_text())
                if data.get('parent_id') == parent_id:
                    children.append(data.get('floor_id'))
            except (json.JSONDecodeError, IOError):
                continue
        
        return children
    
    def _archive_as_fossil(self, floor_state: Dict, reclaimed: Decimal, seed: Decimal) -> tuple[str, Path]:
        """
        Archive a floor state as an immutable fossil.
        
        Returns:
            (fossil_hash, fossil_path)
        """
        floor_id = floor_state.get('floor_id', 'unknown')
        timestamp = int(time.time())
        
        fossil_data = {
            "floor_id": floor_id,
            "archived_at": timestamp,
            "fold_event": True,
            "parent_id": floor_state.get('parent_id'),
            "depth": floor_state.get('depth', 1),
            "metrics_snapshot": {
                "ceramic_at_fold": str(floor_state.get('initial_state', {}).get('ceramic_mass', '0')),
                "reclaimed_to_parent": str(reclaimed),
                "seed_preserved": str(seed),
                "local_shear": str(floor_state.get('initial_state', {}).get('local_shear', '0')),
                "cumulative_shear": str(floor_state.get('initial_state', {}).get('cumulative_shear', '0')),
            },
            "ancestry": floor_state.get('ancestry', {}),
            "constitution": floor_state.get('constitution', {}),
            "spawn_hash": floor_state.get('spawn_hash', ''),
            "created_at": floor_state.get('created_at', 0),
        }
        
        # Generate immutable hash
        fossil_json = json.dumps(fossil_data, sort_keys=True)
        fossil_hash = hashlib.sha256(fossil_json.encode()).hexdigest()[:16]
        
        # Write the fossil
        fossil_file = self.fossils_dir / f"{floor_id}_{timestamp}_{fossil_hash}.fossil"
        fossil_file.write_text(json.dumps(fossil_data, indent=2))
        
        return fossil_hash, fossil_file
    
    def _update_parent_ceramic(self, parent_id: str, additional_ceramic: Decimal):
        """Add reclaimed ceramic to parent's balance."""
        # Check active floors first
        floor_file = self.floors_dir / f"{parent_id}.floor"
        
        if floor_file.exists():
            parent_state = json.loads(floor_file.read_text())
            current = Decimal(str(parent_state.get('initial_state', {}).get('ceramic_mass', '0')))
            new_balance = current + additional_ceramic
            parent_state['initial_state']['ceramic_mass'] = str(new_balance.quantize(Decimal('0.00000001')))
            floor_file.write_text(json.dumps(parent_state, indent=2))
        elif parent_id == "genesis":
            # Update or create genesis.floor
            genesis_floor = self.floors_dir / "genesis.floor"
            if genesis_floor.exists():
                genesis_state = json.loads(genesis_floor.read_text())
            else:
                # Create genesis state from nexus
                try:
                    from .nexus import get_floor_status
                    status = get_floor_status()
                    genesis_state = {
                        "floor_id": "genesis",
                        "parent_id": None,
                        "depth": 1,
                        "initial_state": {
                            "ceramic_mass": str(status.get('ceramic_mass', 10)),
                            "clay_volume": str(status.get('clay_volume', 0)),
                            "local_shear": str(status.get('shear_force', 0.1)),
                            "cumulative_shear": str(status.get('shear_force', 0.1)),
                        },
                        "status": "LIVE",
                    }
                except ImportError:
                    genesis_state = {
                        "floor_id": "genesis",
                        "parent_id": None,
                        "depth": 1,
                        "initial_state": {
                            "ceramic_mass": "10.00000000",
                            "local_shear": "0.1",
                            "cumulative_shear": "0.1",
                        },
                        "status": "LIVE",
                    }
            
            current = Decimal(str(genesis_state.get('initial_state', {}).get('ceramic_mass', '0')))
            new_balance = current + additional_ceramic
            genesis_state['initial_state']['ceramic_mass'] = str(new_balance.quantize(Decimal('0.00000001')))
            genesis_floor.write_text(json.dumps(genesis_state, indent=2))
    
    def _remove_active_floor(self, floor_id: str) -> bool:
        """Remove a floor from active floors directory."""
        floor_file = self.floors_dir / f"{floor_id}.floor"
        if floor_file.exists():
            floor_file.unlink()
            return True
        return False
    
    def _update_hyperspace_registry(self, floor_id: str, fossil_hash: str):
        """Update hyperspace registry to mark floor as folded."""
        nodes_file = self.hyperspace_dir / "nodes.json"
        
        if nodes_file.exists():
            nodes = json.loads(nodes_file.read_text())
            
            # Add fold event
            nodes.setdefault("fold_events", []).append({
                "floor_id": floor_id,
                "fossil_hash": fossil_hash,
                "timestamp": int(time.time()),
            })
            
            # Update node status
            for node in nodes.get("nodes", []):
                if node.get("floor_id") == floor_id:
                    node["status"] = "FOLDED"
                    node["fossil_hash"] = fossil_hash
            
            nodes_file.write_text(json.dumps(nodes, indent=2))
    
    def validate_fold(self, floor_id: str) -> tuple[bool, str, Optional[Dict]]:
        """
        Validate that a fold can occur.
        
        Returns:
            (is_valid, error_message, floor_state)
        """
        # Cannot fold genesis
        if floor_id == "genesis":
            return False, "Cannot fold genesis — the root floor is eternal", None
        
        floor_state = self._load_floor_state(floor_id)
        
        if floor_state is None:
            return False, f"Floor '{floor_id}' not found in active floors", None
        
        parent_id = floor_state.get('parent_id')
        if parent_id is None:
            return False, f"Floor '{floor_id}' has no parent (orphan cannot fold)", None
        
        return True, "", floor_state
    
    def fold(self, floor_id: str, cascade: bool = True, dry_run: bool = False) -> FoldResult:
        """
        Execute the complete fold protocol.
        
        Args:
            floor_id: ID of the floor to fold
            cascade: If True, fold children first (depth-first)
            dry_run: If True, simulate without modifying files
        
        Returns:
            FoldResult with all fold details
        """
        self._ensure_directories()
        
        # ═══ PHASE 1: Validation ═══
        is_valid, error, floor_state = self.validate_fold(floor_id)
        
        if not is_valid:
            return FoldResult(
                success=False,
                floor_id=floor_id,
                parent_id=None,
                ceramic_reclaimed=Decimal('0'),
                ceramic_seed=Decimal('0'),
                fossil_hash="",
                error=error,
            )
        
        parent_id = floor_state.get('parent_id')
        children_folded = []
        
        # ═══ PHASE 2: Cascade Fold Children ═══
        if cascade:
            children = self._find_children(floor_id)
            for child_id in children:
                child_result = self.fold(child_id, cascade=True, dry_run=dry_run)
                if child_result.success:
                    children_folded.append(child_id)
                    # Reload floor state to get updated ceramic from child reclamation
                    if not dry_run:
                        floor_state = self._load_floor_state(floor_id)
        
        # ═══ PHASE 3: Calculate Ceramic Reclamation ═══
        floor_ceramic = self._get_floor_ceramic(floor_state)
        reclaimed = (floor_ceramic * RECLAIM_RATIO).quantize(Decimal('0.00000001'))
        seed = (floor_ceramic * FOLD_SEED_RATIO).quantize(Decimal('0.00000001'))
        
        fossil_hash = ""
        fossil_path = None
        
        if not dry_run:
            # ═══ PHASE 4: Archive as Fossil ═══
            fossil_hash, fossil_path = self._archive_as_fossil(floor_state, reclaimed, seed)
            
            # ═══ PHASE 5: Update Parent Ceramic ═══
            self._update_parent_ceramic(parent_id, reclaimed)
            
            # ═══ PHASE 6: Remove Active Floor ═══
            self._remove_active_floor(floor_id)
            
            # ═══ PHASE 7: Update Hyperspace Registry ═══
            self._update_hyperspace_registry(floor_id, fossil_hash)
        else:
            # Dry run: generate hash without writing
            fossil_hash = "dryrun_" + hashlib.sha256(floor_id.encode()).hexdigest()[:10]
        
        return FoldResult(
            success=True,
            floor_id=floor_id,
            parent_id=parent_id,
            ceramic_reclaimed=reclaimed,
            ceramic_seed=seed,
            fossil_hash=fossil_hash,
            children_folded=children_folded,
            fossil_path=fossil_path,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FOLD CLI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def display_fold_result(result: FoldResult) -> str:
    """Format fold result for CLI display."""
    if not result.success:
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    ❌ FOLD FAILED                            ║
╚══════════════════════════════════════════════════════════════╝

   Error: {result.error}

   💡 Only active child floors can fold. Genesis is eternal.
"""
    
    children_str = ", ".join(result.children_folded) if result.children_folded else "None"
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║           📦 FOLD SUCCESSFUL — FLOOR COMPRESSED              ║
╚══════════════════════════════════════════════════════════════╝

   📋 FOLD MANIFEST
   ├─ Floor ID:         {result.floor_id}
   ├─ Parent ID:        {result.parent_id}
   ├─ Fossil Hash:      {result.fossil_hash}
   └─ Children Folded:  {children_str}

   💰 CERAMIC RECLAMATION
   ├─ Reclaimed to {result.parent_id}:  {result.ceramic_reclaimed} $HCL (90%)
   └─ Seed Preserved:                  {result.ceramic_seed} $HCL (10%)

───────────────────────────────────────────────────────────────
   💡 The parent '{result.parent_id}' received {result.ceramic_reclaimed} $HCL.
      Run 'hardcard lineage --shear' to see the updated ancestry tree.
"""


def get_folder() -> Folder:
    """Factory function for Folder."""
    return Folder()


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    spawner = Spawner()
    result = spawner.spawn("genesis", "floor_alpha", dry_run=True)
    print(display_spawn_result(result))

