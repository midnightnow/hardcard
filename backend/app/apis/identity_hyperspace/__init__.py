from fastapi import APIRouter, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import databutton as db
import json
import time
import math
import hashlib
import random
from datetime import datetime

router = APIRouter(tags=["open"])

# Data Models
class SpiralCoordinates(BaseModel):
    """Coordinates in the Hardcard Hyperspace spiral"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    t: float = Field(..., description="Time coordinate")
    radius: float = Field(..., description="Radius from origin")
    theta: float = Field(..., description="Angle in radians")

class IdentityAnchor(BaseModel):
    """An anchor of an identity in the Hardcard Hyperspace"""
    anchor_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this anchor")
    identity_id: str = Field(..., description="ID of the identity being anchored")
    coordinates: SpiralCoordinates = Field(..., description="Coordinates in the Hardcard Hyperspace")
    hwx_path: str = Field(..., description="Hyperspace eXtensible path")
    created_at: float = Field(default_factory=time.time, description="Timestamp when the anchor was created")
    verification_hash: str = Field(..., description="Hash to verify the anchor's integrity")

class AnchorVerificationRequest(BaseModel):
    """Request to verify an anchor's integrity"""
    anchor_id: str = Field(..., description="ID of the anchor to verify")
    identity_id: str = Field(..., description="ID of the identity to verify")
    hwx_path: str = Field(..., description="Claimed HWX path")

class AnchorVerificationResult(BaseModel):
    """Result of an anchor verification"""
    anchor_id: str = Field(..., description="ID of the verified anchor")
    identity_id: str = Field(..., description="ID of the verified identity")
    is_valid: bool = Field(..., description="Whether the anchor is valid")
    coordinates: Optional[SpiralCoordinates] = Field(None, description="Coordinates if valid")
    verification_time: float = Field(default_factory=time.time, description="Timestamp of verification")

class HyperspacePathRequest(BaseModel):
    """Request to encode an identity to a hyperspace path"""
    identity_id: str = Field(..., description="ID of the identity to encode")

class HyperspacePathResponse(BaseModel):
    """Response with a hyperspace path encoding"""
    identity_id: str = Field(..., description="ID of the encoded identity")
    hwx_path: str = Field(..., description="Encoded hyperspace path")
    coordinates: SpiralCoordinates = Field(..., description="Coordinates in hyperspace")

# Storage helpers
def _get_anchors():
    """Get stored anchors from Databutton storage"""
    try:
        return db.storage.json.get("hardcard_anchors", default=[])
    except Exception as e:
        print(f"Error retrieving anchors: {e}")
        return []

def _save_anchors(anchors):
    """Save anchors to Databutton storage"""
    try:
        db.storage.json.put("hardcard_anchors", anchors)
    except Exception as e:
        print(f"Error saving anchors: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save anchor data: {str(e)}")

# Helper for getting identities from the identity API
def _get_identities():
    """Get stored identities from Databutton storage"""
    try:
        return db.storage.json.get("hardcard_identities", default=[])
    except Exception as e:
        print(f"Error retrieving identities: {e}")
        return []

# Hyperspace encoding functions
def encode_to_hwx(identity_id: str, time_point: float) -> str:
    """Encode an identity and time point to a Hyperspace eXtensible (HWX) path"""
    # The HWX path format is: hwx://identity/{identity_id}/time/{time_point}/spiral/{theta}
    # Calculate theta from time_point using the log-spiral model
    # In a real implementation, this would use the proper mathematical model
    # Here we're using a simplification for demonstration
    theta = math.log(time_point + 1)  # Adding 1 to avoid log(0) error
    
    # Create the path
    hwx_path = f"hwx://identity/{identity_id}/time/{time_point:.6f}/spiral/{theta:.6f}"
    
    return hwx_path

def decode_hwx(hwx_path: str) -> Dict[str, Any]:
    """Decode a Hyperspace eXtensible (HWX) path to its components"""
    # Parse the HWX path format: hwx://identity/{identity_id}/time/{time_point}/spiral/{theta}
    try:
        # Remove the protocol part
        path = hwx_path.replace("hwx://", "")
        
        # Split into segments
        segments = path.split("/")
        
        # Extract components
        identity_id = segments[1]
        time_point = float(segments[3])
        theta = float(segments[5])
        
        # Calculate radius using the log-spiral formula: r = e^θ
        radius = math.exp(theta)
        
        # Calculate Cartesian coordinates
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        z = 0  # For simplicity in 2D representation
        
        return {
            "identity_id": identity_id,
            "time_point": time_point,
            "theta": theta,
            "radius": radius,
            "coordinates": {
                "x": x,
                "y": y,
                "z": z,
                "t": time_point,
                "radius": radius,
                "theta": theta
            }
        }
    except Exception as e:
        raise ValueError(f"Failed to decode HWX path: {str(e)}")

# API Endpoints
@router.post("/hyperspace/encode", response_model=HyperspacePathResponse)
def encode_hyperspace_path(request: HyperspacePathRequest):
    """Encode an identity to a Hyperspace eXtensible (HWX) path
    
    This endpoint converts an identity ID to a hyperspace path that represents 
    its position in the Hardcard log-spiral time model.
    """
    # Check if identity exists
    identities = _get_identities()
    identity = None
    
    for i in identities:
        if i.get("id") == request.identity_id:
            identity = i
            break
            
    if not identity:
        raise HTTPException(status_code=404, detail=f"Identity with ID {request.identity_id} not found")
    
    # Get the time point from the identity
    time_point = identity.get("time_point", 0)
    
    # Encode to HWX path
    hwx_path = encode_to_hwx(request.identity_id, time_point)
    
    # Decode to get coordinates
    decoded = decode_hwx(hwx_path)
    
    # Create the response
    response = HyperspacePathResponse(
        identity_id=request.identity_id,
        hwx_path=hwx_path,
        coordinates=SpiralCoordinates(**decoded["coordinates"])
    )
    
    return response

@router.get("/hyperspace/decode", response_model=Dict[str, Any])
def decode_hwx_path_endpoint(hwx_path: str = Query(..., description="The HWX path to decode")):
    """Decode a Hyperspace eXtensible (HWX) path to its components
    
    This endpoint parses a HWX path and returns the identity, time point, and coordinates.
    """
    try:
        decoded = decode_hwx(hwx_path)
        return decoded
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/hyperspace/anchor", response_model=IdentityAnchor)
def anchor_identity_hwx(identity_id: str = Query(..., description="ID of the identity to anchor")):
    """Anchor an identity in the Hardcard Hyperspace
    
    This endpoint creates a permanent anchor for an identity in the Hardcard Hyperspace,
    allowing it to be referenced and verified cryptographically.
    """
    # Check if identity exists
    identities = _get_identities()
    identity = None
    
    for i in identities:
        if i.get("id") == identity_id:
            identity = i
            break
            
    if not identity:
        raise HTTPException(status_code=404, detail=f"Identity with ID {identity_id} not found")
    
    # Get the time point
    time_point = identity.get("time_point", 0)
    
    # Encode to HWX path
    hwx_path = encode_to_hwx(identity_id, time_point)
    
    # Decode to get coordinates
    decoded = decode_hwx(hwx_path)
    coordinates = SpiralCoordinates(**decoded["coordinates"])
    
    # Create a verification hash
    verification_string = f"{identity_id}:{hwx_path}:{time.time()}"
    verification_hash = hashlib.sha256(verification_string.encode()).hexdigest()
    
    # Create the anchor
    anchor = IdentityAnchor(
        identity_id=identity_id,
        coordinates=coordinates,
        hwx_path=hwx_path,
        verification_hash=verification_hash
    )
    
    # Store the anchor
    anchors = _get_anchors()
    anchors.append(anchor.dict())
    _save_anchors(anchors)
    
    return anchor

@router.post("/hyperspace/verify-anchor", response_model=AnchorVerificationResult, operation_id="verify_anchor_identity")
def verify_anchor_api(request: AnchorVerificationRequest):
    """Verify an identity anchor in the Hardcard Hyperspace
    
    This endpoint verifies that an anchor represents a valid identity in the
    correct position in the Hardcard Hyperspace.
    """
    # Get the anchor
    anchors = _get_anchors()
    anchor = None
    
    for a in anchors:
        if a.get("anchor_id") == request.anchor_id:
            anchor = a
            break
            
    if not anchor:
        raise HTTPException(status_code=404, detail=f"Anchor with ID {request.anchor_id} not found")
    
    # Verify the identity matches
    identity_valid = anchor.get("identity_id") == request.identity_id
    
    # Verify the HWX path matches
    hwx_valid = anchor.get("hwx_path") == request.hwx_path
    
    # Overall validity
    is_valid = identity_valid and hwx_valid
    
    # Create the result
    result = AnchorVerificationResult(
        anchor_id=request.anchor_id,
        identity_id=request.identity_id,
        is_valid=is_valid,
        coordinates=SpiralCoordinates(**anchor.get("coordinates")) if is_valid else None
    )
    
    return result

@router.get("/hyperspace/anchor/{anchor_id}", response_model=IdentityAnchor, operation_id="get_anchor_hyperspace")
def get_anchor_hyperspace(anchor_id: str = Path(..., description="ID of the anchor to retrieve")):
    """Retrieve an identity anchor from the Hardcard Hyperspace
    
    This endpoint returns an anchor by its ID, allowing verification of an identity's
    position in the Hardcard Hyperspace.
    """
    # Get the anchor
    anchors = _get_anchors()
    
    for anchor in anchors:
        if anchor.get("anchor_id") == anchor_id:
            return anchor
            
    raise HTTPException(status_code=404, detail=f"Anchor with ID {anchor_id} not found")

@router.get("/hyperspace/anchors", response_model=List[IdentityAnchor], operation_id="list_anchors2")
def list_hyperspace_anchors(identity_id: Optional[str] = Query(None, description="Filter anchors by identity ID")):
    """List identity anchors in the Hardcard Hyperspace
    
    This endpoint returns all anchors, optionally filtered by identity ID.
    """
    anchors = _get_anchors()
    
    if identity_id:
        anchors = [a for a in anchors if a.get("identity_id") == identity_id]
        
    return anchors

@router.post("/hyperspace/generate-sample", response_model=HyperspacePathResponse, operation_id="generate_sample_hwx_identity_unique")
def generate_sample_hwx_unique(identity_id: Optional[str] = Query(None, description="Optional identity ID to use")):
    """Generate a sample Hyperspace eXtensible (HWX) path
    
    This endpoint creates a sample HWX path for testing or demonstration purposes.
    """
    # Generate a random identity ID if not provided
    if not identity_id:
        identity_id = str(uuid.uuid4())
    
    # Generate a random time point between 1 and 100
    time_point = 1 + 99 * random.random()
    
    # Encode to HWX path
    hwx_path = encode_to_hwx(identity_id, time_point)
    
    # Decode to get coordinates
    decoded = decode_hwx(hwx_path)
    
    # Create the response
    response = HyperspacePathResponse(
        identity_id=identity_id,
        hwx_path=hwx_path,
        coordinates=SpiralCoordinates(**decoded["coordinates"])
    )
    
    return response
