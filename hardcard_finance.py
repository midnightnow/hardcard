
import hashlib
import time
import json
import math
from dataclasses import dataclass, asdict
from typing import List, Dict

# --- HARDCARD CORE FINANCE STUB ---

@dataclass
class AssetNode:
    asset_type: str # 'LAND', 'BTC', 'FIAT'
    identifier: str # Parcel ID, TX Hash, Bank Acct
    value_raw: float # Standardized value for visualization scale
    signature: str # Owner Signature
    resonance_frequency: float # The 'Arm' angle/frequency
    coordinate: tuple # (x, y, z)
    meta: Dict

class HardcardWallet:
    def __init__(self, signature: str):
        self.signature = signature
        self.ledger: List[AssetNode] = []
        
        # Resonance Frequencies (The "Arms" of the Spiral)
        self.arms = {
            "LAND": 1.0,      # Base Earth Frequency
            "BTC": 1.618,     # The Golden Ratio (Scarcity)
            "FIAT": 0.618,    # The Inverse (Liquidity/Flow)
            "DEBT": -1.0      # Anti-matter (Liability)
        }

    def _calculate_geometry(self, index: int, value: float, asset_type: str) -> tuple:
        """
        Maps the asset to the 3D spiral based on its Type (Arm) and Value (Magnitude).
        """
        frequency = self.arms.get(asset_type, 1.0)
        
        # Angle depends on the 'Arm' frequency + index progression
        theta = (index * 0.2) + (frequency * math.pi * 2)
        
        # Radius depends on the 'Value' (Magnitude of the asset)
        # Log scale for visualization since 1 BTC != 1 USD
        if value > 0:
            normalized_value = math.log10(value) if value > 1 else 1
        else:
            normalized_value = 1
            
        radius = 5 + (index * 0.1) + (normalized_value * 0.5)
        
        # Height (Y) represents Time/Solidity Index
        y = index * 0.5
        
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        
        return (round(x, 4), round(y, 4), round(z, 4))

    def pin_blockchain_asset(self, ticker: str, tx_hash: str, amount: float, context: Dict = None):
        index = len(self.ledger)
        coord = self._calculate_geometry(index, amount, ticker)
        
        node = AssetNode(
            asset_type=ticker,
            identifier=tx_hash,
            value_raw=amount,
            signature=self.signature,
            resonance_frequency=self.arms.get(ticker, 1.5),
            coordinate=coord,
            meta=context or {}
        )
        self.ledger.append(node)
        return node

    def pin_fiat_asset(self, bank: str, amount: float, context: Dict = None):
        index = len(self.ledger)
        coord = self._calculate_geometry(index, amount, "FIAT")
        
        node = AssetNode(
            asset_type="FIAT",
            identifier=f"{bank}_HOLDING",
            value_raw=amount,
            signature=self.signature,
            resonance_frequency=self.arms.get("FIAT", 0.5),
            coordinate=coord,
            meta=context or {}
        )
        self.ledger.append(node)
        return node
    
    def ingest_land_assets(self, land_data_path: str):
        """
        Imports the Land Registry data to mix into the portfolio.
        """
        try:
            with open(land_data_path, 'r') as f:
                land_nodes = json.load(f)
                
            for ln in land_nodes:
                # Convert LandNode dict to AssetNode format
                index = len(self.ledger)
                # Land value assumed constant for geo-viz for now, or could extract from metadata
                coord = self._calculate_geometry(index, 500000, "LAND") 
                
                node = AssetNode(
                    asset_type="LAND",
                    identifier=ln['parcel_id'],
                    value_raw=500000, # Mock value
                    signature=self.signature,
                    resonance_frequency=self.arms["LAND"],
                    coordinate=coord,
                    meta={"geostamp": ln['geostamp']}
                )
                self.ledger.append(node)
                print(f"MERGED LAND TITLE: {ln['parcel_id']}")
                
        except FileNotFoundError:
            print("[WARNING] No Land Registry data found. Skipping mix-in.")

    def export_portfolio(self):
        return [asdict(n) for n in self.ledger]

if __name__ == "__main__":
    print("\n--- INITIALIZING HARDCARD FINANCE PROTOCOL ---")
    
    # 1. Initialize Wallet with Sovereign Signature
    my_wallet = HardcardWallet(signature="30-07-73")
    
    # 2. Ingest Physical Assets (Land)
    my_wallet.ingest_land_assets("land_registry_data.json")
    
    # 3. Pin Virtual Assets (Bitcoin - Scarcity Arm)
    print("\n[PINNING] Virtual Assets (Scarcity Arm)...")
    my_wallet.pin_blockchain_asset(
        ticker="BTC", 
        tx_hash="03f03b8479ebb0a5dad4...", 
        amount=1.5,
        context={"block_height": 840000}
    )
    my_wallet.pin_blockchain_asset(
        ticker="BTC", 
        tx_hash="a1b2c3d4e5...", 
        amount=0.05,
        context={"block_height": 840005}
    )
    
    # 4. Pin Fiat Assets (HSBC - Liquidity Arm)
    print("\n[PINNING] Fiat Assets (Liquidity Arm)...")
    my_wallet.pin_fiat_asset(
        bank="HSBC",
        amount=50000,
        context={"M2_index": "GLOBAL_FIAT_V1"}
    )
    my_wallet.pin_fiat_asset(
        bank="Chase",
        amount=1200,
        context={"M2_index": "GLOBAL_FIAT_V1"}
    )

    # 5. Export Total Resonance
    filename = "hardcard_total_portfolio.json"
    with open(filename, 'w') as f:
        json.dump(my_wallet.export_portfolio(), f, indent=2)
        
    print(f"\n[SYSTEM] Total Portfolio Resonance exported to {filename}")
    print(f"[SYSTEM] Total Nodes: {len(my_wallet.ledger)}")
