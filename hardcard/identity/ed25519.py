"""Ed25519 digital signature primitives."""

import os
from typing import Optional, Tuple
import nacl.signing
import nacl.encoding

class Identity:
    """
    Ed25519 key pair management for digital signatures.
    
    Provides:
    - Key generation
    - Message signing
    - Signature verification
    """
    
    def __init__(self, seed: Optional[bytes] = None):
        """
        Initialize identity with optional seed.
        
        Args:
            seed: 32-byte seed for deterministic keys (for testing)
        """
        if seed:
            self.signing_key = nacl.signing.SigningKey(seed)
        else:
            self.signing_key = nacl.signing.SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
    
    @classmethod
    def from_private_key(cls, private_key_hex: str) -> 'Identity':
        """Load identity from existing private key."""
        seed = bytes.fromhex(private_key_hex)
        return cls(seed)
    
    def sign(self, message: bytes) -> str:
        """
        Sign a message.
        
        Args:
            message: Bytes to sign
            
        Returns:
            Hexadecimal signature
        """
        signed = self.signing_key.sign(message)
        return signed.signature.hex()
    
    def verify(self, message: bytes, signature_hex: str, public_key_hex: str) -> bool:
        """
        Verify a signature.
        
        Args:
            message: Original message bytes
            signature_hex: Signature to verify
            public_key_hex: Signer's public key
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            verify_key = nacl.signing.VerifyKey(
                bytes.fromhex(public_key_hex),
                encoder=nacl.encoding.HexEncoder
            )
            verify_key.verify(message, bytes.fromhex(signature_hex))
            return True
        except Exception:
            return False
    
    @property
    def public_key(self) -> str:
        """Get public key as hex string."""
        return self.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()
    
    @property
    def private_key(self) -> str:
        """Get private key as hex string."""
        return self.signing_key.encode(encoder=nacl.encoding.HexEncoder).decode()

__all__ = ["Identity"]
