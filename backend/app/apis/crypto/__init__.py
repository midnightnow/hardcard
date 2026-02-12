"""
Cryptographic utilities for MathMessenger.

This module provides REAL cryptographic operations - not placeholders.
See TRUST_MODEL.md for what these provide and what they don't.

PROVIDES:
- Ed25519 digital signatures (authentication, non-repudiation)
- Key generation and serialization

DOES NOT PROVIDE:
- Encryption (messages are still readable by anyone)
- External timestamp attestation
- Key management (keys are ephemeral unless you store them)
"""

import os
import base64
from typing import Optional, Tuple
from dataclasses import dataclass

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


@dataclass
class SignatureBundle:
    """
    A complete signature with the public key needed to verify it.

    This proves the message was signed by whoever holds the private key.
    It does NOT prove WHO that person is (that requires PKI/web-of-trust).
    """
    algorithm: str  # Always "Ed25519" for now
    public_key_b64: str  # Base64-encoded public key
    signature_b64: str  # Base64-encoded signature
    signed_data_hash: str  # SHA256 of what was signed (for reference)


class MathMessengerCrypto:
    """
    Cryptographic operations for MathMessenger.

    IMPORTANT: This class uses ephemeral keys by default.
    For persistent identity, you must store and reload keys yourself.
    """

    def __init__(self, private_key: Optional[Ed25519PrivateKey] = None):
        """
        Initialize with an existing private key or generate a new one.

        Args:
            private_key: Existing Ed25519 private key, or None to generate new
        """
        if private_key is None:
            self._private_key = Ed25519PrivateKey.generate()
        else:
            self._private_key = private_key

        self._public_key = self._private_key.public_key()

    @classmethod
    def from_private_key_bytes(cls, key_bytes: bytes) -> "MathMessengerCrypto":
        """
        Create instance from raw private key bytes.

        Args:
            key_bytes: 32-byte Ed25519 private key seed

        Returns:
            MathMessengerCrypto instance with the loaded key
        """
        private_key = Ed25519PrivateKey.from_private_bytes(key_bytes)
        return cls(private_key)

    @classmethod
    def from_private_key_b64(cls, key_b64: str) -> "MathMessengerCrypto":
        """
        Create instance from Base64-encoded private key.

        Args:
            key_b64: Base64-encoded 32-byte Ed25519 private key seed

        Returns:
            MathMessengerCrypto instance with the loaded key
        """
        key_bytes = base64.b64decode(key_b64)
        return cls.from_private_key_bytes(key_bytes)

    def get_public_key_b64(self) -> str:
        """Get the public key as Base64 string."""
        public_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return base64.b64encode(public_bytes).decode('utf-8')

    def get_private_key_b64(self) -> str:
        """
        Get the private key as Base64 string.

        WARNING: Treat this as a secret. Anyone with this can sign as you.
        """
        private_bytes = self._private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        return base64.b64encode(private_bytes).decode('utf-8')

    def sign(self, data: bytes, data_hash: str) -> SignatureBundle:
        """
        Sign data and return a complete signature bundle.

        Args:
            data: The raw bytes to sign
            data_hash: SHA256 hash of the data (for reference in bundle)

        Returns:
            SignatureBundle with signature and public key
        """
        signature = self._private_key.sign(data)

        return SignatureBundle(
            algorithm="Ed25519",
            public_key_b64=self.get_public_key_b64(),
            signature_b64=base64.b64encode(signature).decode('utf-8'),
            signed_data_hash=data_hash
        )

    @staticmethod
    def verify(
        data: bytes,
        signature_b64: str,
        public_key_b64: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify a signature against data and public key.

        Args:
            data: The raw bytes that were signed
            signature_b64: Base64-encoded signature
            public_key_b64: Base64-encoded public key

        Returns:
            Tuple of (is_valid, error_message)
            If valid: (True, None)
            If invalid: (False, "reason")
        """
        try:
            public_key_bytes = base64.b64decode(public_key_b64)
            signature_bytes = base64.b64decode(signature_b64)

            public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature_bytes, data)

            return (True, None)

        except InvalidSignature:
            return (False, "Signature does not match data and public key")
        except Exception as e:
            return (False, f"Verification error: {str(e)}")


# Server-level signing key (loaded from environment or generated)
# In production, this should be loaded from a secure key store
_server_crypto: Optional[MathMessengerCrypto] = None


def get_server_crypto() -> MathMessengerCrypto:
    """
    Get the server's signing instance.

    Uses MATHMESSENGER_SIGNING_KEY environment variable if set,
    otherwise generates an ephemeral key (WARNING: changes on restart).
    """
    global _server_crypto

    if _server_crypto is None:
        env_key = os.environ.get("MATHMESSENGER_SIGNING_KEY")

        if env_key:
            _server_crypto = MathMessengerCrypto.from_private_key_b64(env_key)
            print("MathMessenger: Loaded signing key from environment")
        else:
            _server_crypto = MathMessengerCrypto()
            print("MathMessenger: WARNING - Using ephemeral signing key (will change on restart)")
            print(f"MathMessenger: To persist, set MATHMESSENGER_SIGNING_KEY={_server_crypto.get_private_key_b64()}")

    return _server_crypto


def generate_new_keypair() -> Tuple[str, str]:
    """
    Generate a new Ed25519 keypair for user key management.

    Returns:
        Tuple of (private_key_b64, public_key_b64)

    WARNING: Store the private key securely. Anyone with it can sign as you.
    """
    crypto = MathMessengerCrypto()
    return (crypto.get_private_key_b64(), crypto.get_public_key_b64())
