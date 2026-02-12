#!/usr/bin/env python3
"""
Hardcard Treasury: treasury.py
Manages the global infrastructure reserve (10% tax) for the AI Economy.
Acts as the 'Root Node' for financial verification.
"""

import json
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any

try:
    from hardcard.shield import Shield, generate_agent_keys
except ImportError:
    try:
        from .shield import Shield, generate_agent_keys
    except ImportError:
        from shield import Shield, generate_agent_keys

class Treasury:
    def __init__(self, treasury_id: str = "genesis_treasury", storage_path: str = ".hardcard/treasury/"):
        self.treasury_id = treasury_id
        self.storage_dir = Path(storage_path)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.storage_dir / f"{treasury_id}_state.json"
        
        # Shield for signing the Treasury State
        self.shield = Shield(treasury_id)
        if not self.shield.get_public_key():
            generate_agent_keys(treasury_id)
        
        self.total_reserve = Decimal('0.0')
        self.transaction_count = 0
        self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                # In a full HPSS-02 implementation, we would verify the treasury signature here
                self.total_reserve = Decimal(str(data.get("total_reserve", "0.0")))
                self.transaction_count = data.get("transaction_count", 0)
            except Exception:
                self.total_reserve = Decimal('0.0')
                self.transaction_count = 0

    def _save_state(self):
        payload = {
            "treasury_id": self.treasury_id,
            "total_reserve": str(self.total_reserve),
            "transaction_count": self.transaction_count,
            "public_key": self.shield.get_public_key()
        }
        
        # Sign the treasury state
        signature = self.shield.sign_payload(payload)
        payload["signature"] = signature
        
        self.state_file.write_text(json.dumps(payload, indent=2))

    def deposit_tax(self, amount: Decimal):
        """Accumulates the 10% infrastructure tax."""
        self.total_reserve += amount
        self.transaction_count += 1
        self._save_state()
        return self.total_reserve

    def get_metrics(self) -> Dict[str, Any]:
        """Provides the verifiable Agent GDP metrics."""
        return {
            "root_node": self.treasury_id,  # CLI expects 'root_node'
            "id": self.treasury_id,          # Keep for backwards compat
            "agent_gdp_reserve": str(self.total_reserve),
            "total_economic_actions": self.transaction_count,  # CLI expects this
            "transaction_count": self.transaction_count,       # Keep alias
            "public_key": self.shield.get_public_key(),
            "status": "CANON_ANCHORED"
        }

# Singleton Treasury for the local node
genesis_treasury = Treasury()
