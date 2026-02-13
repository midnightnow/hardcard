#!/usr/bin/env python3
"""
Hardcard Address Book: address_book.py
The Coordinate Reconstruction Engine for the Infinite Probability Directory.

"The map is the territory, if the territory is predictable."

This module implements the logic to take a Seed, Depth, and Branch Coordinate
and reconstruct the "State" or "Workspace" that exists at that point in the
Hyperspace probability tree.
"""

import json
import hashlib
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List, Optional

from .shield import Shield
from hardcard_core.lineage import calculate_theoretical_shear

class AddressBook:
    def __init__(self, storage_root: Path = Path(".hardcard/address_book")):
        self.storage_root = storage_root
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.storage_root / "registry.json"
        self._load_registry()

    def _load_registry(self):
        if self.manifest_file.exists():
            try:
                self.registry = json.loads(self.manifest_file.read_text())
            except:
                self.registry = {}
        else:
            self.registry = {}

    def _save_registry(self):
        self.manifest_file.write_text(json.dumps(self.registry, indent=2))

    @staticmethod
    def generate_coordinate_hash(seed: str, depth: int, branch: str) -> str:
        """Deterministic hash for a hyperspace coordinate."""
        data = f"{seed}:{depth}:{branch}".encode()
        return hashlib.sha256(data).hexdigest()

    def index_reality(self, seed: str, depth: int, branch: str, content: Dict[str, Any], agent_id: str):
        """
        Stores the instructions/metadata to reconstruct a reality.
        Instead of the full data, we store the 'DNA' and the coordinate.
        """
        coord_hash = self.generate_coordinate_hash(seed, depth, branch)
        shear = calculate_theoretical_shear(depth)
        
        entry = {
            "coordinate": {
                "seed": seed,
                "depth": depth,
                "branch": branch,
                "hash": coord_hash
            },
            "physics": {
                "theoretical_shear": str(shear),
                "entropy_status": "TAIL_END" if shear >= Decimal('0.9') else "STABLE"
            },
            "meta": {
                "agent_id": agent_id,
                "timestamp": int(__import__('time').time())
            },
            "content_dna": content  # The "Instructions" to expand
        }
        
        self.registry[coord_hash] = entry
        self._save_registry()
        return coord_hash

    def reconstruct(self, coord_hash: str) -> Optional[Dict[str, Any]]:
        """
        Expands a coordinate back into a usable workspace/state.
        "instantly expands it back into a usable clinical/technical workspace"
        """
        if coord_hash not in self.registry:
            # Try to find by partial hash or lookup
            for key in self.registry:
                if key.startswith(coord_hash):
                    coord_hash = key
                    break
            else:
                return None

        entry = self.registry[coord_hash]
        coord = entry["coordinate"]
        dna = entry["content_dna"]
        
        # Physics validation (Safety Check)
        shear = Decimal(entry["physics"]["theoretical_shear"])
        
        print(f"🌌 Reconstructing Reality at Coordinate {coord['hash'][:16]}...")
        print(f"   Seed: {coord['seed']} | Depth: {coord['depth']} | Shear: {shear}")
        
        # Expansion Logic: In this model, DNA is the blueprints
        # In a real app, this might trigger file generation or DB pulls
        reconstruction = {
            "status": "EXPANDED",
            "coordinate_id": coord_hash,
            "workspace_type": dna.get("type", "Generic"),
            "assets": dna.get("assets", []),
            "integrity_signature": self._generate_verify_sig(dna)
        }
        
        if shear >= Decimal('0.99'):
            print("⚠️ WARNING: High-entropy reconstruction. Reality may be transparent.")
            
        return reconstruction

    def _generate_verify_sig(self, dna: Dict) -> str:
        return hashlib.md5(json.dumps(dna, sort_keys=True).encode()).hexdigest()

def get_address_book() -> AddressBook:
    return AddressBook()
