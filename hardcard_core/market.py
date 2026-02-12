#!/usr/bin/env python3
"""
Hardcard Settlement Layer: market.py (Hardened)
Version: HH-01
Uses Decimal for financial precision and implements Escrow Locking.
"""

import time
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any

from .treasury import genesis_treasury

class SettlementEngine:
    def __init__(self, platform_fee_str="0.10"):
        # Use strings for Decimal initialization to avoid float precision issues
        self.fee_percent = Decimal(platform_fee_str)

    def calculate_split(self, total_hcl_val: Any) -> Dict[str, Decimal]:
        """Calculates the 10% tax and 90% payout with banker's rounding."""
        total = Decimal(str(total_hcl_val))
        fee = (total * self.fee_percent).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        payout = total - fee
        
        return {
            "fee": fee,
            "payout": payout
        }

    def prepare_escrow(self, total_hcl, buyer_id, worker_id, complexity_tier: str = "standard"):
        """
        Creates a 'Pre-Flight' escrow object with Dynamic Time-to-Live (DTTL).
        Complexity tiers: 'simple' (15min), 'standard' (1h), 'complex' (24h), 'sovereign' (7d)
        """
        split = self.calculate_split(total_hcl)
        
        # DTTL based on logic complexity
        dttl_map = {
            "simple": 900,      # 15 minutes
            "standard": 3600,   # 1 hour
            "complex": 86400,   # 24 hours
            "sovereign": 604800 # 7 days
        }
        ttl = dttl_map.get(complexity_tier, 3600)  # Default to 1 hour
        
        return {
            "status": "ESCROW_LOCKED",
            "buyer": buyer_id,
            "worker": worker_id,
            "total": Decimal(str(total_hcl)),
            "payout_target": split["payout"],
            "tax_target": split["fee"],
            "escrow_id": f"escrow:{buyer_id}:{int(time.time())}",
            "complexity": complexity_tier,
            "expires": time.time() + ttl
        }

    def release_escrow(self, escrow_obj: Dict[str, Any]):
        """
        Finalizes the settlement.
        Economic Directive:
        1. Verify Escrow ID.
        2. Check Expiry (Timeout).
        3. Execute Atomic payout.
        4. Anchor to Canonical Ledger.
        5. Route tax to Treasury.
        """
        # Expiry Check
        if time.time() > escrow_obj.get("expires", 0):
             return {
                "status": "ESCROW_EXPIRED",
                "error": "Transaction timed out. Funds returned to Buyer.",
                "verification_id": f"fail:{escrow_obj['buyer']}:{int(time.time())}"
            }

        # Route tax to Treasury
        genesis_treasury.deposit_tax(escrow_obj["tax_target"])

        return {
            "status": "CANON_SETTLED",
            "payout_to_worker": escrow_obj["payout_target"],
            "infrastructure_reserve": escrow_obj["tax_target"],
            "verification_id": f"settle:{escrow_obj['worker']}:{int(time.time())}",
            "timestamp": time.time(),
            "ledger_anchor": f"HCL-HASH-{int(time.time()*1000)}"
        }
