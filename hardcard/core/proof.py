"""Verification primitives."""

from hardcard.core.hash import anchor

def verify(claim: str, content: Any) -> bool:
    """
    Verify that content matches a claimed hash.
    
    Args:
        claim: Claimed hash value
        content: Content to verify
        
    Returns:
        True if content hashes to claim, False otherwise
    """
    return anchor(content) == claim

__all__ = ["verify"]
