"""Pure SHA-256 hashing primitives with canonical JSON."""

import hashlib
import json
from typing import Any, Union

def anchor(content: Any) -> str:
    """
    Create a deterministic hash of any JSON-serializable content.
    
    Args:
        content: Any JSON-serializable data (dict, list, str, int, etc.)
        
    Returns:
        Hex digest of SHA-256 hash
    """
    # Canonical JSON: sorted keys, no extra whitespace
    canonical = json.dumps(content, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

def link(prev_hash: str, content: Any) -> str:
    """
    Create a hash that chains to previous state.
    
    Args:
        prev_hash: Hash of previous state
        content: New content to link
        
    Returns:
        Hash of (prev_hash + content)
    """
    return anchor({"prev": prev_hash, "content": content})

__all__ = ["anchor", "link"]
