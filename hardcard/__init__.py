"""
Hardcard - Mathematical verification primitives.

A zero-dependency library providing:
- anchor(): Create verifiable hashes
- link(): Chain hashes together
- verify(): Check proofs
- Chain(): Hash chain management
- Identity(): Ed25519 signatures (optional)
"""

from hardcard.core.hash import anchor, link
from hardcard.core.chain import Chain
from hardcard.core.proof import verify
from hardcard.identity.ed25519 import Identity

__all__ = ["anchor", "link", "Chain", "verify", "Identity"]
__version__ = "1.1.0"
