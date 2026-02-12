from fastapi import APIRouter, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
import databutton as db
import json
import time
import math
import hashlib
import hmac
import base64
import random
from datetime import datetime, timedelta

# Router for cryptographic identity verification
router = APIRouter(tags=["open"])

# Data Models
class Challenge(BaseModel):
    """A cryptographic challenge for identity verification"""
    challenge_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this challenge")
    value: str = Field(..., description="The challenge value to sign")
    identity_id: str = Field(..., description="ID of the identity being verified")
    created_at: float = Field(default_factory=time.time, description="Timestamp when the challenge was created")
    expires_at: float = Field(..., description="Timestamp when the challenge expires")

class ChallengeResponse(BaseModel):
    """A response to a cryptographic challenge"""
    challenge_id: str = Field(..., description="ID of the challenge being responded to")
    signature: str = Field(..., description="Cryptographic signature of the challenge value")
    public_key: str = Field(..., description="Public key that corresponds to the signing key")

class VerificationResult(BaseModel):
    """Result of a verification attempt"""
    success: bool = Field(..., description="Whether verification was successful")
    identity_id: str = Field(..., description="ID of the identity that was verified")
    verification_time: float = Field(default_factory=time.time, description="Time when verification occurred")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional verification details")

class ZeroKnowledgeProofRequest(BaseModel):
    """Request to generate a zero-knowledge proof"""
    identity_id: str = Field(..., description="ID of the identity to generate proof for")
    attribute: str = Field(..., description="Attribute to prove (e.g., 'age_over_18')")
    nonce: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Nonce for the proof")

class ZeroKnowledgeProof(BaseModel):
    """A zero-knowledge proof of an identity attribute"""
    proof_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this proof")
    identity_id: str = Field(..., description="ID of the identity the proof relates to")
    attribute: str = Field(..., description="The attribute being proven")
    proof_value: str = Field(..., description="The cryptographic proof value")
    created_at: float = Field(default_factory=time.time, description="Timestamp when the proof was created")
    expires_at: float = Field(..., description="Timestamp when the proof expires")
    verification_hint: Dict[str, Any] = Field(..., description="Hint on how to verify this proof")

class DIDDocument(BaseModel):
    """A W3C compliant Decentralized Identifier (DID) document"""
    id: str = Field(..., description="The DID URI")
    controller: str = Field(..., description="The DID controller")
    verification_method: List[Dict[str, Any]] = Field(..., description="List of verification methods")
    authentication: List[str] = Field(..., description="List of verification methods for authentication")
    assertion_method: Optional[List[str]] = Field(None, description="List of verification methods for assertions")
    service: Optional[List[Dict[str, Any]]] = Field(None, description="List of services") 
    created: str = Field(..., description="Timestamp when the DID was created")
    updated: Optional[str] = Field(None, description="Timestamp when the DID was last updated")

# Storage helpers
def _get_challenges():
    """Get stored challenges from Databutton storage"""
    try:
        return db.storage.json.get("hardcard_identity_challenges", default=[])
    except Exception as e:
        print(f"Error retrieving challenges: {e}")
        return []

def _save_challenges(challenges):
    """Save challenges to Databutton storage"""
    try:
        db.storage.json.put("hardcard_identity_challenges", challenges)
    except Exception as e:
        print(f"Error saving challenges: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save challenge data: {str(e)}")

def _get_proofs():
    """Get stored ZK proofs from Databutton storage"""
    try:
        return db.storage.json.get("hardcard_zk_proofs", default=[])
    except Exception as e:
        print(f"Error retrieving ZK proofs: {e}")
        return []

def _save_proofs(proofs):
    """Save ZK proofs to Databutton storage"""
    try:
        db.storage.json.put("hardcard_zk_proofs", proofs)
    except Exception as e:
        print(f"Error saving ZK proofs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save proof data: {str(e)}")

def _get_did_documents():
    """Get stored DID documents from Databutton storage"""
    try:
        return db.storage.json.get("hardcard_did_documents", default=[])
    except Exception as e:
        print(f"Error retrieving DID documents: {e}")
        return []

def _save_did_documents(documents):
    """Save DID documents to Databutton storage"""
    try:
        db.storage.json.put("hardcard_did_documents", documents)
    except Exception as e:
        print(f"Error saving DID documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save DID data: {str(e)}")

# Helper for getting identities from the identity API
def _get_identities():
    """Get stored identities from Databutton storage"""
    try:
        return db.storage.json.get("hardcard_identities", default=[])
    except Exception as e:
        print(f"Error retrieving identities: {e}")
        return []

# API Endpoints
@router.post("/verification/challenge", response_model=Challenge)
def generate_challenge(identity_id: str = Query(..., description="ID of the identity to verify")):
    """Generate a cryptographic challenge for identity verification
    
    This endpoint creates a random challenge that must be signed with the private key 
    corresponding to the identity's public key. The challenge expires after a short time.
    """
    # Check if identity exists
    identities = _get_identities()
    identity_exists = False
    
    for identity in identities:
        if identity.get("id") == identity_id:
            identity_exists = True
            break
            
    if not identity_exists:
        raise HTTPException(status_code=404, detail=f"Identity with ID {identity_id} not found")
    
    # Generate a random challenge
    random_bytes = uuid.uuid4().bytes + uuid.uuid4().bytes
    challenge_value = base64.b64encode(random_bytes).decode('utf-8')
    
    # Create the challenge
    expires_at = time.time() + 300  # 5 minutes from now
    challenge = Challenge(
        value=challenge_value,
        identity_id=identity_id,
        expires_at=expires_at
    )
    
    # Store the challenge
    challenges = _get_challenges()
    challenges.append(challenge.dict())
    _save_challenges(challenges)
    
    return challenge

@router.post("/verification/verify", response_model=VerificationResult)
def verify_challenge_response(response: ChallengeResponse):
    """Verify a response to a challenge for identity verification
    
    This endpoint verifies that the signature for a challenge is valid, proving that
    the user controls the private key associated with their identity.
    """
    # Get the challenge
    challenges = _get_challenges()
    challenge = None
    
    for c in challenges:
        if c.get("challenge_id") == response.challenge_id:
            challenge = c
            break
            
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Check if the challenge has expired
    if challenge.get("expires_at") < time.time():
        raise HTTPException(status_code=400, detail="Challenge has expired")
    
    # In a real implementation, we would verify the signature here
    # For this demo, we'll just simulate successful verification
    # PLACEHOLDER: Replace with actual cryptographic verification
    verification_successful = True
    
    # Create the result
    result = VerificationResult(
        success=verification_successful,
        identity_id=challenge.get("identity_id"),
        details={
            "challenge_id": response.challenge_id,
            "verification_method": "ed25519",
        }
    )
    
    return result

@router.post("/verification/zkp/generate", response_model=ZeroKnowledgeProof)
def generate_zero_knowledge_proof(request: ZeroKnowledgeProofRequest):
    """Generate a zero-knowledge proof for an identity attribute
    
    This endpoint creates a proof that an attribute is true without revealing
    the underlying data. For example, proving someone is over 18 without revealing their birth date.
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
    
    # Validate that we can prove the requested attribute
    # In a real implementation, this would depend on the attributes in the identity
    # PLACEHOLDER: Replace with actual ZKP generation
    supported_attributes = ["age_over_18", "is_family_member", "has_inheritance_rights"]
    
    if request.attribute not in supported_attributes:
        raise HTTPException(status_code=400, detail=f"Attribute '{request.attribute}' cannot be proven")
    
    # Generate a simulated zero-knowledge proof
    # In a real implementation, this would be a cryptographic proof
    proof_value = hmac.new(
        key=bytes(request.nonce, 'utf-8'),
        msg=bytes(f"{request.identity_id}:{request.attribute}", 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Create the proof
    expires_at = time.time() + 86400  # 24 hours from now
    proof = ZeroKnowledgeProof(
        identity_id=request.identity_id,
        attribute=request.attribute,
        proof_value=proof_value,
        expires_at=expires_at,
        verification_hint={
            "method": "hmac-sha256",
            "nonce": request.nonce,
            "attribute": request.attribute
        }
    )
    
    # Store the proof
    proofs = _get_proofs()
    proofs.append(proof.dict())
    _save_proofs(proofs)
    
    return proof

@router.get("/verification/zkp/{proof_id}", response_model=ZeroKnowledgeProof)
def get_zero_knowledge_proof(proof_id: str = Path(..., description="ID of the proof to retrieve")):
    """Retrieve a previously generated zero-knowledge proof
    
    This endpoint allows retrieving a stored zero-knowledge proof by its ID.
    """
    proofs = _get_proofs()
    
    for proof in proofs:
        if proof.get("proof_id") == proof_id:
            # Check if the proof has expired
            if proof.get("expires_at") < time.time():
                raise HTTPException(status_code=400, detail="Proof has expired")
            return proof
            
    raise HTTPException(status_code=404, detail=f"Proof with ID {proof_id} not found")

@router.post("/verification/zkp/verify", response_model=VerificationResult)
def verify_zero_knowledge_proof(
    proof_id: str = Query(..., description="ID of the proof to verify"),
    attribute: str = Query(..., description="Attribute to verify")
):
    """Verify a zero-knowledge proof
    
    This endpoint verifies that a zero-knowledge proof is valid for a given attribute.
    """
    # Get the proof
    proofs = _get_proofs()
    proof = None
    
    for p in proofs:
        if p.get("proof_id") == proof_id:
            proof = p
            break
            
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    # Check if the proof has expired
    if proof.get("expires_at") < time.time():
        raise HTTPException(status_code=400, detail="Proof has expired")
    
    # Check if the proof is for the requested attribute
    if proof.get("attribute") != attribute:
        raise HTTPException(status_code=400, detail=f"Proof is for attribute '{proof.get('attribute')}', not '{attribute}'")
    
    # In a real implementation, we would cryptographically verify the proof here
    # For this demo, we'll just consider it valid if it exists and hasn't expired
    # PLACEHOLDER: Replace with actual verification logic
    verification_successful = True
    
    # Create the result
    result = VerificationResult(
        success=verification_successful,
        identity_id=proof.get("identity_id"),
        details={
            "proof_id": proof_id,
            "attribute": attribute,
            "verification_method": proof.get("verification_hint", {}).get("method"),
        }
    )
    
    return result

@router.post("/did/create", response_model=DIDDocument)
def create_did_document(identity_id: str = Query(..., description="ID of the identity to create a DID for")):
    """Create a W3C compliant Decentralized Identifier (DID) document for an identity
    
    This endpoint generates a DID document that follows the W3C DID specification,
    allowing the identity to participate in decentralized identity systems.
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
    
    # Check if a DID document already exists for this identity
    did_documents = _get_did_documents()
    
    for doc in did_documents:
        if doc.get("controller") == identity_id:
            # Return the existing document
            return doc
    
    # Create a DID with the hardcard method
    did = f"did:hardcard:{identity_id}"
    
    # Generate a key ID based on the identity's signature
    key_id = f"{did}#keys-1"
    
    # Get the current time in ISO format
    current_time = datetime.utcnow().isoformat() + "Z"
    
    # Create the DID document
    did_document = DIDDocument(
        id=did,
        controller=identity_id,
        verification_method=[
            {
                "id": key_id,
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyMultibase": identity.get("identity_signature", {}).get("value")
            }
        ],
        authentication=[key_id],
        assertion_method=[key_id],
        service=[
            {
                "id": f"{did}#hardcard-service",
                "type": "HardcardIdentityService",
                "serviceEndpoint": "https://hardcard.ai/api/identity"
            }
        ],
        created=current_time
    )
    
    # Store the DID document
    did_documents.append(did_document.dict())
    _save_did_documents(did_documents)
    
    return did_document

@router.get("/did/{did}", response_model=DIDDocument)
def get_did_document(did: str = Path(..., description="The DID to retrieve")):
    """Retrieve a W3C compliant Decentralized Identifier (DID) document
    
    This endpoint retrieves a DID document by its DID URI.
    """
    if not did.startswith("did:hardcard:"):
        raise HTTPException(status_code=400, detail="Only did:hardcard DIDs are supported")
    
    # Extract the identity ID from the DID
    identity_id = did.replace("did:hardcard:", "")
    
    # Get DID documents
    did_documents = _get_did_documents()
    
    for doc in did_documents:
        if doc.get("id") == did:
            return doc
            
    raise HTTPException(status_code=404, detail=f"DID document for {did} not found")
