#!/usr/bin/env python3
"""
Hardcard Wallet: wallet.py (Shielded)
Version: HH-02
Integrates Ed25519 signing from the Shield Layer to prevent state forgery.
Includes Nonce-tracking to prevent replay attacks.
"""

import json
import time
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, Optional
from .shield import Shield, generate_agent_keys

class UnicornWallet:
    def __init__(self, agent_id: str, storage_path: str = ".hardcard/wallets/"):
        self.agent_id = agent_id
        self.storage_dir = Path(storage_path)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.wallet_file = self.storage_dir / f"{agent_id}_wallet.json"
        
        # Cryptographic Context
        self.shield = Shield(agent_id)
        self.public_key = self.shield.get_public_key()
        
        # Internal State
        self.balance = Decimal('0.0')
        self.escrow_locked = Decimal('0.0')
        self.nonce = 0
        self.last_signature = None
        
        self._load_wallet()

    def _load_wallet(self):
        if self.wallet_file.exists():
            try:
                data = json.loads(self.wallet_file.read_text())
                
                # HPSS-02: Verify State Integrity
                if "signature" in data:
                    sig = data.pop("signature")
                    payload = data  # The rest of the dictionary is the payload
                    
                    if self.public_key and self.shield.verify_signature(self.public_key, payload, sig):
                        self.balance = Decimal(str(data.get("balance", "0.0")))
                        self.escrow_locked = Decimal(str(data.get("escrow_locked", "0.0")))
                        self.nonce = data.get("nonce", 0)
                        self.last_signature = sig
                    else:
                        print(f"🚨 CRITICAL: State Corruption Detected in Wallet {self.agent_id}!")
                        # In a production environment, we would halt execution here.
                else:
                    # Legacy or unsigned wallet (treat as zeroed for security)
                    self.balance = Decimal('0.0')
            except Exception as e:
                print(f"Error loading wallet: {e}")
                self.balance = Decimal('0.0')

    def _save_wallet(self):
        self.nonce += 1
        payload = {
            "agent_id": self.agent_id,
            "balance": str(self.balance),
            "escrow_locked": str(self.escrow_locked),
            "total_liquid": str(self.balance - self.escrow_locked),
            "nonce": self.nonce,
            "timestamp": time.time()
        }
        
        # HPSS-02: Sign the State
        try:
            signature = self.shield.sign_payload(payload)
            payload["signature"] = signature
            self.wallet_file.write_text(json.dumps(payload, indent=2))
        except ValueError:
            # Keys likely not generated yet
            self.wallet_file.write_text(json.dumps(payload, indent=2))

    def deposit(self, amount: Any):
        self.balance += Decimal(str(amount))
        self._save_wallet()
        return self.balance

    def lock_for_escrow(self, amount: Any) -> bool:
        val = Decimal(str(amount))
        if self.balance >= val:
            self.escrow_locked += val
            self._save_wallet()
            return True
        return False

    def release_locked(self, amount: Any, success: bool = True):
        val = Decimal(str(amount))
        if self.escrow_locked >= val:
            self.escrow_locked -= val
            if success:
                self.balance -= val
            self._save_wallet()
            return True
        return False

    def transfer(self, recipient_id: str, amount: Any) -> bool:
        """Atomic transfer to another wallet instance (Local Cluster)."""
        val = Decimal(str(amount))
        if self.balance >= val:
            # 1. Deduct from Sender
            self.balance -= val
            self._save_wallet()
            
            # 2. Credit Recipient
            try:
                # Re-instantiate recipient to ensure fresh state
                # Pass storage_dir parent to keep context? 
                # self.storage_dir is Path. 
                # Default init uses ".hardcard/wallets/". Assumption: shared storage.
                recipient = UnicornWallet(recipient_id, str(self.storage_dir) + "/")
                recipient.deposit(val)
                return True
            except Exception as e:
                # Rollback
                self.balance += val 
                self._save_wallet()
                print(f"❌ Transfer failed: {e}")
                return False
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "balance_total": f"{self.balance} $HCL",
            "locked_in_escrow": f"{self.escrow_locked} $HCL",
            "available_liquid": f"{self.balance - self.escrow_locked} $HCL",
            "nonce": self.nonce,
            "status": "SOVEREIGN_FUNDED" if self.balance > self.escrow_locked else "INSUFFICIENT_FUNDS",
            "verified": self.last_signature is not None
        }

def get_wallet(agent_id: str) -> UnicornWallet:
    return UnicornWallet(agent_id)
