
import hashlib
import time
import math
import json
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# --- Hardcard Core Stub for Demo ---
# In a real pip install hardcard scenario, this would be imported
class HardcardCore:
    @staticmethod
    def get_ground_truth(asset_id: str) -> str:
        """
        Simulates retrieving a 'Geostamp' - a physical connection to location and time.
        In reality this would ping the Hardcard Geostamp API or hardware oracle.
        """
        # Simulated lat/long drift and time entropy
        lat = -16.9186 + (random.random() * 0.01) # Cairnsish
        long = 145.7781 + (random.random() * 0.01)
        entropy = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:8]
        return f"GEO:{lat:.4f},{long:.4f}|TIME:{time.time_ns()}|ENT:{entropy}"

@dataclass
class LandNode:
    index: int
    parcel_id: str
    owner_signature_hash: str
    geostamp: str
    prev_hash: str
    coordinate: tuple
    solidified_hash: str

class LandAxis:
    def __init__(self, name: str):
        self.name = name
        self.chain: List[LandNode] = []
        self.genesis_hash = hashlib.sha256(f"GENESIS_LAND_AXIS_{name}".encode()).hexdigest()

    def calculate_deep_geometry(self, index: int, lat_long_seed: str) -> tuple:
        """
        Calculates the 3D coordinate. For Land, 
        X/Z are derived from physical location (mapped to the spiral),
        Y is the 'Time/Depth' axis (Solidity).
        """
        # Hash text seed to get deterministic floats
        seed_val = int(hashlib.sha256(lat_long_seed.encode()).hexdigest(), 16)
        
        # Simple mapping for visualization:
        # We want them to cluster but spiral upwards in time
        angle = (seed_val % 360) * (math.pi / 180)
        radius = 5 + (index * 0.05) # Expanding spiral
        
        x = math.cos(angle) * radius
        z = math.sin(angle) * radius
        y = index * 0.2 # Growing vertical solidity
        
        return (round(x, 4), round(y, 4), round(z, 4))

    def solidify(self, parcel_id: str, owner_signature: str) -> LandNode:
        index = len(self.chain)
        prev_hash = self.chain[-1].solidified_hash if self.chain else self.genesis_hash
        
        # 1. Capture Physical Solidity
        geostamp = HardcardCore.get_ground_truth(parcel_id)
        
        # 2. Derive Coordinate (The Deep Map)
        # We use the geostamp as the seed for the geometry to pin it to reality
        coord = self.calculate_deep_geometry(index, geostamp)
        
        # 3. Create the Solid Hash (The Reverse Index Anchor)
        # Includes previous hash to ensure immutability
        raw_data = f"{index}{parcel_id}{owner_signature}{geostamp}{prev_hash}{coord}"
        solid_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        
        node = LandNode(
            index=index,
            parcel_id=parcel_id,
            owner_signature_hash=hashlib.sha256(owner_signature.encode()).hexdigest(),
            geostamp=geostamp,
            prev_hash=prev_hash,
            coordinate=coord,
            solidified_hash=solid_hash
        )
        
        self.chain.append(node)
        return node
    
    def export_deep_map(self):
        return [asdict(n) for n in self.chain]

# --- GEMINI CODE WIKI INTERFACE (SIMULATED) ---
# The user wants the Wiki to be the "Logic Anchor"
class GeminiLogicAnchor:
    @staticmethod
    def validate_protocol(protocol_name: str):
        print(f"[GEMINI WIKI] Validating protocol: {protocol_name}...")
        print(f"[GEMINI WIKI] > Checking constraints...")
        print(f"[GEMINI WIKI] > Verifying dependency graph...")
        print(f"[GEMINI WIKI] PROTOCOL '{protocol_name}' IS VALID. PROCEEDING.")
        return True

# --- INDUSTRIALIZATION DEMO ---
if __name__ == "__main__":
    import sys
    
    # 1. Wiki Validation
    GeminiLogicAnchor.validate_protocol("HARDCARD_LAND_REGISTRY_V1")
    
    # 2. Initialize Axis
    registry = LandAxis("Cairns_North_Sector")
    print("\n--- INITIALIZING LAND REGISTRY AXIS ---")
    
    # 3. Register Deeds
    deeds = [
        ("PARCEL-8812", "User_A_Signature_300773"),
        ("PARCEL-8813", "User_B_Signature_110285"),
        ("PARCEL-9941", "User_C_Signature_GHOST"),
        ("PARCEL-8812-SUBDIV", "User_A_Signature_300773"), # Subsequent transaction on same land
    ]
    
    print(f"Processing {len(deeds)} incoming titles...\n")
    
    for parcel, sig in deeds:
        time.sleep(0.3)
        node = registry.solidify(parcel, sig)
        print(f"SOLIDIFIED: {parcel}")
        print(f" > Geo:   {node.geostamp[:30]}...")
        print(f" > Coord: {node.coordinate}")
        print(f" > Hash:  {node.solidified_hash[:16]}...")
        print("-" * 40)

    # 4. Generate JSON for Visualization
    with open("land_registry_data.json", "w") as f:
        json.dump(registry.export_deep_map(), f, indent=2)
        print("\n[SYSTEM] Deep Map Data exported to land_registry_data.json")
