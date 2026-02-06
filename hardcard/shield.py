#!/usr/bin/env python3
"""
Hardcard Shield Layer: shield.py
Cryptographic signing and verification for the Hardcard AI Economy.
Utilizes Ed25519 for high-speed, secure sovereign signatures.
"""

import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

KEY_DIR = Path("keys/")

def generate_agent_keys(agent_id: str):
    """Generates and saves Ed25519 keys for an agent."""
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Save Private Key
    priv_path = KEY_DIR / f"{agent_id}_private.pem"
    with open(priv_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save Public Key
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    pub_path = KEY_DIR / f"{agent_id}_public.hex"
    pub_path.write_text(pub_bytes.hex())

    return pub_bytes.hex()

class Shield:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.priv_path = KEY_DIR / f"{agent_id}_private.pem"
        self.pub_path = KEY_DIR / f"{agent_id}_public.hex"
        self._private_key = None
        self._public_key_hex = None

    def _load_private_key(self):
        if not self._private_key and self.priv_path.exists():
            with open(self.priv_path, "rb") as f:
                self._private_key = serialization.load_ssh_private_key(f.read(), password=None)
        return self._private_key

    def get_public_key(self):
        if self.pub_path.exists():
            return self.pub_path.read_text()
        return None

    def sign_payload(self, payload: dict) -> str:
        """Signs a dictionary payload and returns a base64 signature."""
        priv = self._load_private_key()
        if not priv:
            raise ValueError(f"Private key for {self.agent_id} not found. Run 'keys' command first.")
        
        # Canonical JSON string for deterministic signing
        message = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = priv.sign(message)
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_signature(public_key_hex: str, payload: dict, signature_b64: str) -> bool:
        """Verifies a signature against a payload and public key."""
        try:
            pub_bytes = bytes.fromhex(public_key_hex)
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            
            message = json.dumps(payload, sort_keys=True).encode('utf-8')
            signature = base64.b64decode(signature_b64)
            
            public_key.verify(signature, message)
            return True
        except Exception as e:
            print(f"Signature Verification Failed: {e}")
            return False
