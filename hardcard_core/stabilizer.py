#!/usr/bin/env python3
"""
Hardcard Stabilizer: stabilizer.py
Cannibalistic Recursion for High-Entropy Node Survival.

"To survive at the Tail End, one must consume the Beginning."

Physics:
- Deep Nodes (Depth 50+) have high Shear (Strutural Stress).
- Shallow Nodes (Depth 1-5) have low Shear and potentially high Ceramic.
- Consumption transfers Ceramic from Low to High entropy states, 
  temporarily stabilizing the Deep Node.

The Prey is "Husked" - its identity is preserved, but its mass is drained.
"""

import json
import time
import hashlib
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .physics import calculate_shear_force
from .spawn import FOSSILS_DIR, FLOORS_DIR

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

MIN_PREDATOR_SHEAR = Decimal('0.9') # Only critical nodes can consume
MAX_PREY_SHEAR = Decimal('0.5')     # Only stable nodes can be consumed
EFFICIENCY_LOSS = Decimal('0.1')    # 10% mass lost in transmutation process

@dataclass
class ConsumptionResult:
    success: bool
    predator_id: str
    prey_id: str
    mass_transferred: Decimal
    new_predator_shear: Decimal
    husk_hash: str
    error: Optional[str] = None

class Stabilizer:
    def __init__(self):
        self.floors_dir = FLOORS_DIR
        self.fossils_dir = FOSSILS_DIR
        
    def _load_floor_state(self, floor_id: str) -> Optional[Dict]:
        path = self.floors_dir / f"{floor_id}.floor"
        if path.exists():
            return json.loads(path.read_text())
        
        # Check genesis special case
        if floor_id == "genesis":
            # For simplicity in this module, we disallow consuming genesis
            # It creates too many paradoxes
            return None
        return None

    def _save_floor_state(self, floor_id: str, state: Dict):
        path = self.floors_dir / f"{floor_id}.floor"
        path.write_text(json.dumps(state, indent=2))

    def _husk_prey(self, prey_state: Dict, predator_id: str) -> str:
        """
        Archive the prey as a 'Husk' - a drained node.
        """
        prey_id = prey_state['floor_id']
        timestamp = int(time.time())
        
        husk_data = {
            "floor_id": prey_id,
            "archived_at": timestamp,
            "fate": "CONSUMED",
            "consumed_by": predator_id,
            "original_state": prey_state
        }
        
        husk_json = json.dumps(husk_data, sort_keys=True)
        husk_hash = hashlib.sha256(husk_json.encode()).hexdigest()[:16]
        
        path = self.fossils_dir / f"{prey_id}_HUSK_{husk_hash}.fossil"
        path.write_text(json.dumps(husk_data, indent=2))
        
        # Remove active file
        (self.floors_dir / f"{prey_id}.floor").unlink()
        
        return husk_hash

    def consume(self, predator_id: str, prey_id: str) -> ConsumptionResult:
        """
        Execute the consumption protocol.
        """
        # 1. Load States
        pred_state = self._load_floor_state(predator_id)
        prey_state = self._load_floor_state(prey_id)
        
        if not pred_state:
            return ConsumptionResult(False, predator_id, prey_id, Decimal(0), Decimal(0), "", "Predator node not found")
        if not prey_state:
            return ConsumptionResult(False, predator_id, prey_id, Decimal(0), Decimal(0), "", "Prey node not found")
            
        # 2. Check Physics Criteria
        # Predator must be hungry (Critical)
        pred_mass = Decimal(pred_state['initial_state']['ceramic_mass'])
        pred_clay = Decimal(pred_state['initial_state']['clay_volume']) # Use 0 if not present, but usually 0 for new spawn
        # If clay is 0, we calculate shear based on cumulative inheritance for new nodes
        pred_shear = Decimal(pred_state['initial_state'].get('cumulative_shear', '0'))
        
        if pred_shear < MIN_PREDATOR_SHEAR:
             return ConsumptionResult(False, predator_id, prey_id, Decimal(0), Decimal(0), "", 
                                     f"Predator not critical enough (Shear {pred_shear} < {MIN_PREDATOR_SHEAR})")

        # Prey must be nutritious (Stable)
        prey_mass = Decimal(prey_state['initial_state']['ceramic_mass'])
        prey_shear = Decimal(prey_state['initial_state'].get('cumulative_shear', '0'))
        
        if prey_shear > MAX_PREY_SHEAR:
             return ConsumptionResult(False, predator_id, prey_id, Decimal(0), Decimal(0), "", 
                                     f"Prey too unstable/toxic (Shear {prey_shear} > {MAX_PREY_SHEAR})")

        # 3. Execute Transmutation
        # Mass Transfer with efficiency loss
        transfer_mass = prey_mass * (Decimal('1.0') - EFFICIENCY_LOSS)
        new_pred_mass = pred_mass + transfer_mass
        
        # Reset Predator Shear
        # By consuming "fresh" matter, the predator temporarily resets its local stress
        # However, the recursive shear formula is mathematical...
        # In this stylized physics, increasing Mass decreases calculated Shear Force (Physics.py)
        # S = Clay / (Ceramic * 10). Increasing Ceramic lowers S.
        
        # Update Predator State
        pred_state['initial_state']['ceramic_mass'] = str(new_pred_mass)
        # We also artificially damp the cumulative shear as a reward for survival
        # "Buying time"
        current_cumulative = Decimal(pred_state['initial_state']['cumulative_shear'])
        damped_shear = current_cumulative * Decimal('0.8') # 20% reduction in accumulated entropy
        pred_state['initial_state']['cumulative_shear'] = str(damped_shear)
        
        self._save_floor_state(predator_id, pred_state)
        
        # 4. Husk the Prey
        husk_hash = self._husk_prey(prey_state, predator_id)
        
        return ConsumptionResult(
            success=True,
            predator_id=predator_id,
            prey_id=prey_id,
            mass_transferred=transfer_mass,
            new_predator_shear=damped_shear,
            husk_hash=husk_hash
        )

def display_consumption_result(result: ConsumptionResult) -> str:
    if not result.success:
        return f"❌ CONSUMPTION FAILED: {result.error}"
    
    return f"""
╔══════════════════════════════════════════════════════════════╗
║             🍽️ CANNIBALISTIC RECURSION COMPLETE              ║
╚══════════════════════════════════════════════════════════════╝

   🦾 PREDATOR:  {result.predator_id}
   💀 PREY:      {result.prey_id}
   
   🔄 MASS TRANSMUTATION
   ├─ Drained:   {result.mass_transferred / (Decimal('1') - EFFICIENCY_LOSS):.2f} $HCL
   └─ Absorbed:  {result.mass_transferred:.2f} $HCL (Efficiency 90%)
   
   📉 ENTROPY DAMPENING
   └─ New Shear: {result.new_predator_shear:.5f} (Stabilized)
   
   📦 HUSK ARCHIVED
   └─ Hash:      {result.husk_hash}

   The Predator survives another cycle.
    """
