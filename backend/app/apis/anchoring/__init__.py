import hashlib
import databutton as db
import base64
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status

# Create FastAPI router
router = APIRouter()


class AnchorRecord(BaseModel):
    """Record of an anchor transaction"""
    tx_id: str
    timestamp: int
    cid: Optional[str] = None
    hwx_id: str
    proof_hash: str


class AnchorRequest(BaseModel):
    """Request to create an anchor"""
    hwx_id: str
    proof_hash: str


class VerifyRequest(BaseModel):
    """Request to verify an anchor"""
    hwx_id: str
    proof_hash: str


class AnchorResponse(BaseModel):
    """Response from anchor creation"""
    tx_id: str
    timestamp: int
    cid: Optional[str]
    hwx_id: str
    proof_hash: str
    success: bool = True
    message: str = "Anchor created successfully"


class VerifyResponse(BaseModel):
    """Response from anchor verification"""
    verified: bool
    error: Optional[str] = None
    anchor: Optional[Dict[str, Any]] = None
    timestamp: Optional[int] = None
    age_seconds: Optional[int] = None


def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


def store_anchor_record(record: AnchorRecord) -> None:
    """Store an anchor record in Databutton storage"""
    # Get existing anchors
    anchors = db.storage.json.get("hwx_anchors", default={})
    
    # Add new anchor
    anchors[record.hwx_id] = record.dict()
    
    # Store back to storage
    db.storage.json.put(sanitize_storage_key("hwx_anchors"), anchors)


def get_anchor_record(hwx_id: str) -> Optional[AnchorRecord]:
    """Get an anchor record from Databutton storage"""
    anchors = db.storage.json.get("hwx_anchors", default={})
    if hwx_id in anchors:
        return AnchorRecord(**anchors[hwx_id])
    return None


class OnChainAnchor:
    """Class for anchoring HWX proofs to a blockchain (simulated for demo)"""
    
    @staticmethod
    def create_anchor(hwx_id: str, proof_hash: str) -> AnchorRecord:
        """Create a blockchain anchor for an HWX proof (simulated)
        
        In a real implementation, this would submit an OP_RETURN transaction
        to Bitcoin or another blockchain.
        
        Args:
            hwx_id: ID of the HWX container
            proof_hash: Hash of the proof to anchor
            
        Returns:
            Anchor record with transaction ID
        """
        # Simulate transaction ID creation
        # In reality, this would be the TXID from the blockchain
        tx_id = f"tx-{hashlib.sha256(f'{hwx_id}-{proof_hash}-{time.time()}'.encode()).hexdigest()[:16]}"
        
        # Create anchor record
        record = AnchorRecord(
            tx_id=tx_id,
            timestamp=int(time.time()),
            hwx_id=hwx_id,
            proof_hash=proof_hash,
            # In reality, this would be an IPFS CID
            cid=f"Qm{hashlib.sha256(proof_hash.encode()).hexdigest()[:44]}"
        )
        
        # Store the record
        store_anchor_record(record)
        
        return record
    
    @staticmethod
    def verify_anchor(hwx_id: str, proof_hash: str) -> Dict[str, Any]:
        """Verify an HWX proof against its blockchain anchor
        
        In a real implementation, this would query the blockchain
        to verify the existence and content of the anchor transaction.
        
        Args:
            hwx_id: ID of the HWX container
            proof_hash: Hash of the proof to verify
            
        Returns:
            Verification result with status and details
        """
        # Get the anchor record
        record = get_anchor_record(hwx_id)
        
        if not record:
            return {
                "verified": False,
                "error": "No anchor record found"
            }
        
        # Check if the proof hash matches
        if record.proof_hash != proof_hash:
            return {
                "verified": False,
                "error": "Proof hash does not match anchor record",
                "anchor": record.dict()
            }
        
        # In a real implementation, we would verify the transaction
        # exists on the blockchain and contains the correct OP_RETURN data
        
        return {
            "verified": True,
            "anchor": record.dict(),
            "timestamp": record.timestamp,
            "age_seconds": int(time.time()) - record.timestamp
        }


# Add an endpoint that matches the one expected by HandwritingCompression component
@router.post("/anchor", response_model=AnchorResponse)
async def create_anchor_from_hwx(request: AnchorRequest) -> AnchorResponse:
    """Create a blockchain anchor for the specified HWX ID
    
    This endpoint is used by the HandwritingCompression component to
    anchor HWX data to the blockchain, providing an immutable timestamp.
    
    Args:
        request: The request containing the HWX ID and proof hash
        
    Returns:
        Details of the newly created anchor
    """
    # Use the OnChainAnchor class to create the anchor
    record = OnChainAnchor.create_anchor(request.hwx_id, request.proof_hash)
    
    # Return the response
    return AnchorResponse(
        tx_id=record.tx_id,
        timestamp=record.timestamp,
        cid=record.cid,
        hwx_id=record.hwx_id,
        proof_hash=record.proof_hash
    )

@router.post("/create-anchor", response_model=AnchorResponse, deprecated=True)
def create_anchor(request: AnchorRequest) -> AnchorResponse:
    """[DEPRECATED] Use /anchor endpoint instead.
    
    Create a blockchain anchor for an HWX proof
    
    This endpoint creates a simulated blockchain anchor for an HWX proof,
    providing an immutable timestamp and proof of existence.
    
    Args:
        request: The request containing the HWX ID and proof hash
        
    Returns:
        Details of the newly created anchor
    """
    # Manually implement the same functionality to avoid calling an async function from a sync function
    record = OnChainAnchor.create_anchor(request.hwx_id, request.proof_hash)
    
    # Return the response
    return AnchorResponse(
        tx_id=record.tx_id,
        timestamp=record.timestamp,
        cid=record.cid,
        hwx_id=record.hwx_id,
        proof_hash=record.proof_hash
    )


@router.post("/verify-anchor", response_model=VerifyResponse, operation_id="verify_anchor_endpoint")
def verify_anchor_endpoint(request: VerifyRequest) -> VerifyResponse:
    """Verify an HWX proof against its blockchain anchor
    
    This endpoint verifies an HWX proof against its blockchain anchor,
    ensuring the integrity and timestamp of the data.
    
    Args:
        request: The request containing the HWX ID and proof hash to verify
        
    Returns:
        Verification result with status and details
    """
    # Use the OnChainAnchor class to verify the anchor
    result = OnChainAnchor.verify_anchor(request.hwx_id, request.proof_hash)
    
    # Return the response
    return VerifyResponse(**result)


@router.get("/get-anchor/{hwx_id}", response_model=Optional[AnchorResponse])
def get_anchor(hwx_id: str) -> Optional[AnchorResponse]:
    """Get an anchor record for an HWX proof
    
    This endpoint retrieves the anchor record for a specific HWX ID.
    
    Args:
        hwx_id: The ID of the HWX container
        
    Returns:
        The anchor record if found, None otherwise
    """
    # Get the anchor record
    record = get_anchor_record(hwx_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No anchor record found for HWX ID: {hwx_id}"
        )
    
    # Return the response
    return AnchorResponse(
        tx_id=record.tx_id,
        timestamp=record.timestamp,
        cid=record.cid,
        hwx_id=record.hwx_id,
        proof_hash=record.proof_hash
    )


@router.get("/list-anchors", response_model=List[AnchorResponse])
def list_anchors() -> List[AnchorResponse]:
    """List all anchor records
    
    This endpoint retrieves all anchor records stored in the system.
    
    Returns:
        List of all anchor records
    """
    # Get all anchors
    anchors = db.storage.json.get("hwx_anchors", default={})
    
    # Convert to response objects
    return [
        AnchorResponse(
            tx_id=anchor["tx_id"],
            timestamp=anchor["timestamp"],
            cid=anchor.get("cid"),
            hwx_id=anchor["hwx_id"],
            proof_hash=anchor["proof_hash"]
        )
        for anchor in anchors.values()
    ]
