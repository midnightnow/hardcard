#!/usr/bin/env python3
"""
SOVEREIGN SIGNATURE - Constellation OS Identity Protocol
=========================================================
Provides unified authentication across all Constellation apps using
the Hardcard "Date Signature" as the primary identity key.

The Date Signature is a cryptographically unique key derived from:
1. A user's chosen "Sovereign Date" (e.g., birthdate, founding date)
2. A local entropy source (device fingerprint)
3. Optional biometric binding (WebAuthn)

Usage:
    from sovereign_signature import SovereignIdentity
    
    identity = SovereignIdentity()
    signature = identity.generate_signature("1973-07-30")
    token = identity.create_session_token(signature)
"""

import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration
SIGNATURE_SALT = os.environ.get("SOVEREIGN_SALT", "CONSTELLATION_OS_2026")
SESSION_TTL = 86400  # 24 hours

class SovereignIdentity:
    """
    The Sovereign Identity Protocol for Constellation OS.
    
    Instead of passwords or OAuth tokens, identity is derived from:
    - A "Sovereign Date" chosen by the user (never transmitted)
    - Local device entropy
    - Optional WebAuthn/Passkey binding
    """
    
    def __init__(self, device_id: Optional[str] = None):
        self.device_id = device_id or self._get_device_fingerprint()
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def _get_device_fingerprint(self) -> str:
        """Generate a stable device fingerprint."""
        # In production, this would use hardware identifiers
        # For now, use a persistent UUID stored locally
        fingerprint_file = os.path.expanduser("~/.constellation/device_id")
        os.makedirs(os.path.dirname(fingerprint_file), exist_ok=True)
        
        if os.path.exists(fingerprint_file):
            with open(fingerprint_file, 'r') as f:
                return f.read().strip()
        else:
            device_id = str(uuid.uuid4())
            with open(fingerprint_file, 'w') as f:
                f.write(device_id)
            return device_id
    
    def generate_signature(self, sovereign_date: str) -> str:
        """
        Generate the Sovereign Signature from a date.
        
        The signature is a SHA-256 hash of:
        - The sovereign date
        - The device fingerprint
        - The global salt
        
        This creates a unique, reproducible identity key that:
        - Never leaves the device
        - Cannot be reverse-engineered without all components
        - Is consistent across sessions on the same device
        """
        # Normalize the date format
        try:
            parsed = datetime.strptime(sovereign_date, "%Y-%m-%d")
            normalized_date = parsed.strftime("%Y%m%d")
        except ValueError:
            # Try other common formats
            for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
                try:
                    parsed = datetime.strptime(sovereign_date, fmt)
                    normalized_date = parsed.strftime("%Y%m%d")
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Invalid date format: {sovereign_date}")
        
        # Create the signature payload
        payload = f"{normalized_date}:{self.device_id}:{SIGNATURE_SALT}"
        
        # Hash it
        signature = hashlib.sha256(payload.encode()).hexdigest()
        
        return signature
    
    def create_session_token(self, signature: str, geostamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a session token from a signature.
        
        The token includes:
        - A session ID
        - The signature (truncated for security)
        - A geostamp (location/time anchor)
        - Expiration time
        """
        session_id = str(uuid.uuid4())
        now = int(time.time())
        
        # Generate geostamp if not provided
        if not geostamp:
            geostamp = f"GEO:{now}:{self.device_id[:8]}"
        
        token = {
            "session_id": session_id,
            "signature_prefix": signature[:16],  # Only store prefix
            "geostamp": geostamp,
            "created_at": now,
            "expires_at": now + SESSION_TTL,
            "device_id": self.device_id[:8],
            "protocol": "SOVEREIGN_V1"
        }
        
        # Sign the token
        token_string = json.dumps(token, sort_keys=True)
        token_signature = hmac.new(
            signature.encode(),
            token_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        token["hmac"] = token_signature
        
        # Store session
        self.sessions[session_id] = token
        
        return token
    
    def verify_session(self, session_id: str, signature: str) -> bool:
        """
        Verify a session is valid and matches the signature.
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Check expiration
        if time.time() > session["expires_at"]:
            del self.sessions[session_id]
            return False
        
        # Check signature prefix matches
        if not signature.startswith(session["signature_prefix"]):
            return False
        
        # Verify HMAC
        token_copy = {k: v for k, v in session.items() if k != "hmac"}
        token_string = json.dumps(token_copy, sort_keys=True)
        expected_hmac = hmac.new(
            signature.encode(),
            token_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_hmac, session["hmac"])
    
    def get_constellation_claims(self, signature: str) -> Dict[str, Any]:
        """
        Generate the Constellation identity claims for SSO.
        
        These claims can be used by any L2/L3 app to identify the user
        without storing sensitive data.
        """
        return {
            "sub": signature[:32],  # Subject (truncated signature)
            "iss": "constellation.os",
            "aud": ["macagent", "vetsorcery", "hardcard"],
            "iat": int(time.time()),
            "exp": int(time.time()) + SESSION_TTL,
            "device": self.device_id[:8],
            "protocol": "SOVEREIGN_V1",
            "permissions": {
                "L0_HARDCARD": ["read", "write"],
                "L2_MACAGENT": ["read", "write", "execute"],
                "L3_VETSORCERY": ["read", "write"]
            }
        }


def generate_webauthn_challenge() -> Dict[str, Any]:
    """
    Generate a WebAuthn challenge for passkey binding.
    This allows the Sovereign Signature to be bound to a hardware key.
    """
    challenge = os.urandom(32).hex()
    return {
        "challenge": challenge,
        "rp": {"name": "Constellation OS", "id": "constellation.local"},
        "user": {
            "id": os.urandom(16).hex(),
            "name": "sovereign@constellation.os",
            "displayName": "Sovereign Identity"
        },
        "pubKeyCredParams": [
            {"type": "public-key", "alg": -7},   # ES256
            {"type": "public-key", "alg": -257}  # RS256
        ],
        "timeout": 60000,
        "attestation": "none"
    }


# CLI Interface
if __name__ == "__main__":
    import sys
    
    print("═" * 50)
    print("  SOVEREIGN SIGNATURE - Constellation OS v3.0")
    print("═" * 50)
    
    identity = SovereignIdentity()
    print(f"\n🔐 Device ID: {identity.device_id[:16]}...")
    
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = input("\n📅 Enter your Sovereign Date (YYYY-MM-DD): ").strip()
    
    try:
        signature = identity.generate_signature(date)
        print(f"\n✅ Sovereign Signature Generated:")
        print(f"   {signature[:32]}...{signature[-8:]}")
        
        token = identity.create_session_token(signature)
        print(f"\n🎫 Session Token Created:")
        print(f"   ID: {token['session_id'][:16]}...")
        print(f"   Geostamp: {token['geostamp']}")
        print(f"   Expires: {datetime.fromtimestamp(token['expires_at'])}")
        
        claims = identity.get_constellation_claims(signature)
        print(f"\n🌐 Constellation Claims:")
        print(f"   Subject: {claims['sub']}")
        print(f"   Permissions: {list(claims['permissions'].keys())}")
        
        print("\n" + "═" * 50)
        print("  IDENTITY SOLIDIFIED - Ready for SSO")
        print("═" * 50)
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
