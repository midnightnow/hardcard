from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
import databutton as db
import re

router = APIRouter(prefix="/hardcard/proof")

# --- Models for Lean 4 proof skeleton ---

class ProofScript(BaseModel):
    id: str
    name: str
    description: str
    content: str
    status: str  # draft, verified, failed
    last_verified: Optional[str] = None

class ProofRequest(BaseModel):
    name: str
    description: str
    content: str

class ProofResponse(BaseModel):
    success: bool
    message: str
    proof: Optional[ProofScript] = None

class CIJobResult(BaseModel):
    job_id: str
    proofs: List[str]
    status: str  # running, completed, failed
    logs: List[str]
    started_at: str
    completed_at: Optional[str] = None

# --- Helper functions ---

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_proofs() -> List[ProofScript]:
    """Get all proofs from storage"""
    try:
        proofs_data = db.storage.json.get("hardcard_proofs", default=[])
        return [ProofScript(**proof) for proof in proofs_data]
    except Exception as e:
        print(f"Error getting proofs: {str(e)}")
        return []

def save_proofs(proofs: List[ProofScript]) -> bool:
    """Save proofs to storage"""
    try:
        proofs_data = [proof.model_dump() for proof in proofs]
        db.storage.json.put("hardcard_proofs", proofs_data)
        return True
    except Exception as e:
        print(f"Error saving proofs: {str(e)}")
        return False

# --- Endpoints ---

@router.get("/scripts", response_model=Dict)
def list_proof_scripts():
    """List all proof scripts"""
    proofs = get_proofs()
    return {
        "success": True,
        "message": f"Retrieved {len(proofs)} proof scripts",
        "proofs": [proof.model_dump() for proof in proofs]
    }

@router.post("/scripts", response_model=ProofResponse)
def create_proof_script(proof_request: ProofRequest):
    """Create a new proof script"""
    proofs = get_proofs()
    
    # Generate ID
    import uuid
    proof_id = f"proof-{uuid.uuid4().hex[:8]}"
    
    # Create new proof
    new_proof = ProofScript(
        id=proof_id,
        name=proof_request.name,
        description=proof_request.description,
        content=proof_request.content,
        status="draft"
    )
    
    proofs.append(new_proof)
    
    if save_proofs(proofs):
        return ProofResponse(
            success=True,
            message=f"Successfully created proof script '{new_proof.name}'",
            proof=new_proof
        )
    else:
        return ProofResponse(
            success=False,
            message="Failed to save proof script"
        )

@router.get("/scripts/{proof_id}", response_model=ProofResponse)
def get_proof_script(proof_id: str):
    """Get a specific proof script by ID"""
    proofs = get_proofs()
    
    for proof in proofs:
        if proof.id == proof_id:
            return ProofResponse(
                success=True,
                message=f"Successfully retrieved proof script '{proof.name}'",
                proof=proof
            )
    
    return ProofResponse(
        success=False,
        message=f"Proof script with ID '{proof_id}' not found"
    )

@router.get("/ci/status", response_model=Dict)
def get_ci_status():
    """Get the status of CI proof verification"""
    # In a real implementation, this would connect to a CI system
    # For demo purposes, we'll return a mock status
    
    # Lean 4 sample proof for ledger invariant
    ledger_proof = """
import Mathlib

structure Tx where
  sender   : String
  receiver : String
  amount   : Nat

def apply_tx (bal : String → Nat) (t : Tx) : String → Nat :=
  fun a =>
    if h : a = t.sender then bal a - t.amount else
    if h' : a = t.receiver then bal a + t.amount else
    bal a

lemma total_conserved (bal : String → Nat) (t : Tx) :
    (∑ a, bal a) = (∑ a, apply_tx bal t a) := by
  -- proof omitted for brevity
  admit
"""
    
    return {
        "success": True,
        "message": "Retrieved CI status",
        "ci_job": {
            "job_id": "ci-job-12345",
            "status": "completed",
            "proofs": ["ledger_invariant", "consensus_safety"],
            "logs": [
                "Running Lean 4 verification...",
                "Checking ledger_invariant...",
                "Warning: using 'admit' in proof",
                "Checking consensus_safety...",
                "All proofs completed successfully"
            ],
            "started_at": "2025-04-18T03:30:00Z",
            "completed_at": "2025-04-18T03:35:42Z",
            "proof_content": {
                "ledger_invariant": ledger_proof
            }
        }
    }

@router.post("/ci/trigger", response_model=Dict)
def trigger_ci_job():
    """Trigger a CI job to verify all proofs"""
    # In a real implementation, this would trigger a CI pipeline
    # For demo purposes, we'll just return a successful response
    
    return {
        "success": True,
        "message": "CI job triggered successfully",
        "job_id": "ci-job-12346"
    }
