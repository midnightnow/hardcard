"""Hash chain for sequential verification."""

from typing import List, Any, Dict, Optional
from hardcard.core.hash import link

class Chain:
    """
    A sequence of linked hashes providing tamper-evident history.
    
    Each block contains:
    - index: Position in chain
    - prev: Hash of previous block
    - data: User content
    - hash: SHA-256 of (prev + data)
    """
    
    def __init__(self):
        self.blocks: List[Dict[str, Any]] = []
    
    def add(self, data: Any) -> str:
        """
        Append a new block to the chain.
        
        Args:
            data: Any JSON-serializable content
            
        Returns:
            Hash of the new block
        """
        prev_hash = self.blocks[-1]["hash"] if self.blocks else "0"*64
        block = {
            "index": len(self.blocks),
            "prev": prev_hash,
            "data": data,
            "hash": link(prev_hash, data)
        }
        self.blocks.append(block)
        return block["hash"]
    
    def verify(self) -> bool:
        """
        Verify the integrity of the entire chain.
        
        Returns:
            True if chain is unbroken, False otherwise
        """
        for i in range(1, len(self.blocks)):
            expected = link(self.blocks[i-1]["hash"], self.blocks[i]["data"])
            if self.blocks[i]["hash"] != expected:
                return False
        return True
    
    def get_block(self, index: int) -> Optional[Dict[str, Any]]:
        """Retrieve a block by index."""
        if 0 <= index < len(self.blocks):
            return self.blocks[index].copy()
        return None
    
    def __len__(self) -> int:
        return len(self.blocks)

__all__ = ["Chain"]
