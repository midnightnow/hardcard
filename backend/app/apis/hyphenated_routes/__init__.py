from fastapi import APIRouter, HTTPException, Depends
from app.auth import AuthorizedUser
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import re

# Import functionality from the original version with underscores
from app.apis.hwx_compression import (
    decode_hwx_endpoint as original_decode,
    HWXDecodeRequest,
    encode_hyperspace_path_endpoint as original_encode,
    HWXEncodeRequest,
    anchor_hwx_data_endpoint as original_anchor, # Updated from anchor_hwx_endpoint
#    verify_anchor_endpoint as original_verify, # Updated from verify_hwx_anchor
    HWXAnchorRequest
)

router = APIRouter(prefix="/hwx-compression")

@router.post("/generate-key", operation_id="generate_key_endpoint")
async def generate_key_endpoint(user: AuthorizedUser = None) -> Dict[str, Any]:
    """Generate a new HWX encryption key"""
    # Generate a random key ID
    import uuid
    import databutton as db
    import base64
    import os
    
    key_id = f"key-{uuid.uuid4().hex[:8]}"
    key_bytes = os.urandom(32)  # Generate 256-bit random key
    key_b64 = base64.b64encode(key_bytes).decode('utf-8')
    
    # Store the key
    key_storage = db.storage.json.get("hwx_keys", default={})
    key_storage[key_id] = key_b64
    db.storage.json.put("hwx_keys", key_storage)
    
    return {
        "key_id": key_id,
        "created_at": int(db.time.time()),
        "status": "created"
    }



@router.post("/anchor", operation_id="anchor_hwx2")
async def anchor_hwx(request: HWXAnchorRequest, user: AuthorizedUser = None) -> Dict[str, Any]:
    """Anchor HWX data on-chain for L3 security"""
    return await original_anchor(request)

# @router.get("/verify-anchor/{hwx_id}", operation_id="hyphenated_verify_anchor")
# async def verify_anchor(hwx_id: str, user: AuthorizedUser = None) -> Dict[str, Any]:
#     """Verify the anchor for an HWX object"""
#     return await original_verify(hwx_id)
