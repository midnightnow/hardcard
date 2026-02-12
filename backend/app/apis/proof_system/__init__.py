"""Formal verification and proof system for Hardcard financial logic and ledger invariants.

This module provides utilities for formally verifying properties of the Hardcard financial system,
focusing on ledger integrity and transaction validity.

The implementation follows principles from formal methods using Lean 4 inspired techniques.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple, Any, Callable
from enum import Enum
import json
import hashlib
import time
from datetime import datetime, timezone
import databutton as db
import re

# Sanitize storage keys to only use alphanumeric, '.', '_', and '-'
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# ----- Model Definitions -----

class ProofStatus(str, Enum):
    """Status of a proof."""
    VERIFIED = "verified"
    FALSIFIED = "falsified"
    UNKNOWN = "unknown"
    IN_PROGRESS = "in_progress"
    ERROR = "error"


@dataclass
class Proposition:
    """A formal proposition that can be proven."""
    id: str
    description: str
    formal_statement: str
    dependencies: List[str] = None  # IDs of propositions this depends on
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "formal_statement": self.formal_statement,
            "dependencies": self.dependencies,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Proposition':
        return cls(
            id=data["id"],
            description=data["description"],
            formal_statement=data["formal_statement"],
            dependencies=data.get("dependencies", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class ProofStep:
    """A step in a formal proof."""
    statement: str
    justification: str
    references: List[str] = None  # References to previous steps or axioms
    
    def __post_init__(self):
        if self.references is None:
            self.references = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "statement": self.statement,
            "justification": self.justification,
            "references": self.references
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProofStep':
        return cls(
            statement=data["statement"],
            justification=data["justification"],
            references=data.get("references", [])
        )


@dataclass
class FormalProof:
    """A formal proof of a proposition."""
    id: str
    proposition_id: str
    steps: List[ProofStep]
    status: ProofStatus
    verification_time: float = 0.0  # Time taken to verify in seconds
    created_at: datetime = None
    updated_at: datetime = None
    commit_id: str = ""  # Git commit ID for version tracking
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "proposition_id": self.proposition_id,
            "steps": [step.to_dict() for step in self.steps],
            "status": self.status.value if isinstance(self.status, ProofStatus) else self.status,
            "verification_time": self.verification_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "commit_id": self.commit_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FormalProof':
        return cls(
            id=data["id"],
            proposition_id=data["proposition_id"],
            steps=[ProofStep.from_dict(step) for step in data["steps"]],
            status=ProofStatus(data["status"]) if data.get("status") else ProofStatus.UNKNOWN,
            verification_time=data.get("verification_time", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            commit_id=data.get("commit_id", "")
        )


@dataclass
class VerificationReport:
    """Report summarizing verification results."""
    id: str
    timestamp: datetime
    proofs_verified: int
    proofs_falsified: int
    proofs_unknown: int
    total_verification_time: float
    failing_proofs: List[str]  # IDs of failing proofs
    summary: str
    commit_id: str = ""  # Git commit ID this report is for
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "proofs_verified": self.proofs_verified,
            "proofs_falsified": self.proofs_falsified,
            "proofs_unknown": self.proofs_unknown,
            "total_verification_time": self.total_verification_time,
            "failing_proofs": self.failing_proofs,
            "summary": self.summary,
            "commit_id": self.commit_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationReport':
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            proofs_verified=data["proofs_verified"],
            proofs_falsified=data["proofs_falsified"],
            proofs_unknown=data["proofs_unknown"],
            total_verification_time=data["total_verification_time"],
            failing_proofs=data["failing_proofs"],
            summary=data["summary"],
            commit_id=data.get("commit_id", "")
        )


# ----- Storage Functions -----

def save_proposition(proposition: Proposition) -> bool:
    """Save a proposition to storage."""
    try:
        key = f"proposition_{sanitize_storage_key(proposition.id)}"
        db.storage.json.put(key, proposition.to_dict())
        return True
    except Exception as e:
        print(f"Error saving proposition: {str(e)}")
        return False


def get_proposition(proposition_id: str) -> Optional[Proposition]:
    """Get a proposition from storage."""
    try:
        key = f"proposition_{sanitize_storage_key(proposition_id)}"
        data = db.storage.json.get(key)
        return Proposition.from_dict(data)
    except Exception as e:
        print(f"Error getting proposition: {str(e)}")
        return None


def list_propositions() -> List[Proposition]:
    """List all propositions in storage."""
    try:
        propositions = []
        keys = [k.name for k in db.storage.text.list() if k.name.startswith("proposition_")]
        for key in keys:
            try:
                data = db.storage.json.get(key)
                propositions.append(Proposition.from_dict(data))
            except Exception as e:
                print(f"Error loading proposition {key}: {str(e)}")
        return propositions
    except Exception as e:
        print(f"Error listing propositions: {str(e)}")
        return []


def save_proof(proof: FormalProof) -> bool:
    """Save a formal proof to storage."""
    try:
        key = f"proof_{sanitize_storage_key(proof.id)}"
        db.storage.json.put(key, proof.to_dict())
        return True
    except Exception as e:
        print(f"Error saving proof: {str(e)}")
        return False


def get_proof(proof_id: str) -> Optional[FormalProof]:
    """Get a formal proof from storage."""
    try:
        key = f"proof_{sanitize_storage_key(proof_id)}"
        data = db.storage.json.get(key)
        return FormalProof.from_dict(data)
    except Exception as e:
        print(f"Error getting proof: {str(e)}")
        return None


def get_proofs_for_proposition(proposition_id: str) -> List[FormalProof]:
    """Get all proofs for a given proposition."""
    try:
        proofs = []
        all_proofs = list_proofs()
        for proof in all_proofs:
            if proof.proposition_id == proposition_id:
                proofs.append(proof)
        return proofs
    except Exception as e:
        print(f"Error getting proofs for proposition: {str(e)}")
        return []


def list_proofs() -> List[FormalProof]:
    """List all formal proofs in storage."""
    try:
        proofs = []
        keys = [k.name for k in db.storage.text.list() if k.name.startswith("proof_")]
        for key in keys:
            try:
                data = db.storage.json.get(key)
                proofs.append(FormalProof.from_dict(data))
            except Exception as e:
                print(f"Error loading proof {key}: {str(e)}")
        return proofs
    except Exception as e:
        print(f"Error listing proofs: {str(e)}")
        return []


def save_verification_report(report: VerificationReport) -> bool:
    """Save a verification report to storage."""
    try:
        key = f"verification_report_{sanitize_storage_key(report.id)}"
        db.storage.json.put(key, report.to_dict())
        return True
    except Exception as e:
        print(f"Error saving verification report: {str(e)}")
        return False


def get_verification_report(report_id: str) -> Optional[VerificationReport]:
    """Get a verification report from storage."""
    try:
        key = f"verification_report_{sanitize_storage_key(report_id)}"
        data = db.storage.json.get(key)
        return VerificationReport.from_dict(data)
    except Exception as e:
        print(f"Error getting verification report: {str(e)}")
        return None


def list_verification_reports() -> List[VerificationReport]:
    """List all verification reports in storage."""
    try:
        reports = []
        keys = [k.name for k in db.storage.text.list() if k.name.startswith("verification_report_")]
        for key in keys:
            try:
                data = db.storage.json.get(key)
                reports.append(VerificationReport.from_dict(data))
            except Exception as e:
                print(f"Error loading verification report {key}: {str(e)}")
        return reports
    except Exception as e:
        print(f"Error listing verification reports: {str(e)}")
        return []


# ----- Core Verification Logic -----

def check_proof_dependencies(proof: FormalProof) -> bool:
    """Check if all dependencies of a proof are verified."""
    try:
        proposition = get_proposition(proof.proposition_id)
        if not proposition:
            return False
        
        for dep_id in proposition.dependencies:
            # Find a verified proof for this dependency
            dep_proofs = get_proofs_for_proposition(dep_id)
            verified_proofs = [p for p in dep_proofs if p.status == ProofStatus.VERIFIED]
            if not verified_proofs:
                return False
        
        return True
    except Exception as e:
        print(f"Error checking proof dependencies: {str(e)}")
        return False


def verify_proof(proof: FormalProof) -> Tuple[ProofStatus, str, float]:
    """Verify a formal proof and return its status, explanation, and verification time."""
    start_time = time.time()
    status = ProofStatus.UNKNOWN
    explanation = ""
    
    try:
        # Check if dependencies are verified
        if not check_proof_dependencies(proof):
            status = ProofStatus.UNKNOWN
            explanation = "Proof dependencies not verified"
            return status, explanation, time.time() - start_time
        
        # Get the proposition being proved
        proposition = get_proposition(proof.proposition_id)
        if not proposition:
            status = ProofStatus.ERROR
            explanation = f"Proposition {proof.proposition_id} not found"
            return status, explanation, time.time() - start_time
        
        # Check if we have steps in the proof
        if not proof.steps:
            status = ProofStatus.ERROR
            explanation = "Proof has no steps"
            return status, explanation, time.time() - start_time
        
        # In a real implementation, this would be where Lean 4 or another theorem prover is called
        # For demonstration, we'll use a simplified verification approach
        
        # Check reference integrity - each step must only reference previous steps
        available_refs = set()
        for i, step in enumerate(proof.steps):
            for ref in step.references:
                if ref not in available_refs and not ref.startswith("axiom:"):
                    status = ProofStatus.FALSIFIED
                    explanation = f"Step {i+1} references non-existent prior step: {ref}"
                    return status, explanation, time.time() - start_time
            
            # Add this step to available references
            available_refs.add(f"step_{i+1}")
        
        # Check that the final step matches the proposition statement
        final_step = proof.steps[-1].statement
        if not final_step_equivalent_to_proposition(final_step, proposition.formal_statement):
            status = ProofStatus.FALSIFIED
            explanation = "Final step does not prove the proposition"
            return status, explanation, time.time() - start_time
        
        # If all checks pass, the proof is verified
        status = ProofStatus.VERIFIED
        explanation = "All proof steps verified successfully"
    
    except Exception as e:
        status = ProofStatus.ERROR
        explanation = f"Error during verification: {str(e)}"
    
    verification_time = time.time() - start_time
    return status, explanation, verification_time


def final_step_equivalent_to_proposition(final_step: str, proposition_statement: str) -> bool:
    """Check if the final step is equivalent to the proposition statement.
    
    In a real implementation, this would use a formal equivalence checker.
    Here we use a simplified string comparison.
    """
    # Normalize by removing whitespace and converting to lowercase
    norm_final = ' '.join(final_step.lower().split())
    norm_proposition = ' '.join(proposition_statement.lower().split())
    
    # In a real implementation, we'd use a theorem prover to check equivalence
    # For now, we'll just check if normalized strings are equal
    return norm_final == norm_proposition


def run_verification_pipeline(commit_id: str = "") -> VerificationReport:
    """Run the verification pipeline on all propositions and their proofs.
    
    This simulates a CI/CD verification pipeline that would be triggered on each commit.
    """
    start_time = time.time()
    report_id = f"report_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    
    all_proofs = list_proofs()
    verified_count = 0
    falsified_count = 0
    unknown_count = 0
    failing_proofs = []
    results = []
    
    for proof in all_proofs:
        status, explanation, verification_time = verify_proof(proof)
        
        # Update proof status and save
        proof.status = status
        proof.verification_time = verification_time
        proof.updated_at = datetime.now(timezone.utc)
        proof.commit_id = commit_id
        save_proof(proof)
        
        # Count results
        if status == ProofStatus.VERIFIED:
            verified_count += 1
        elif status == ProofStatus.FALSIFIED:
            falsified_count += 1
            failing_proofs.append(proof.id)
        else:
            unknown_count += 1
            if status == ProofStatus.ERROR:
                failing_proofs.append(proof.id)
        
        # Store result details
        proposition = get_proposition(proof.proposition_id)
        results.append({
            "proof_id": proof.id,
            "proposition_id": proof.proposition_id,
            "proposition_desc": proposition.description if proposition else "Unknown",
            "status": status.value,
            "explanation": explanation,
            "verification_time": verification_time
        })
    
    total_time = time.time() - start_time
    
    # Generate summary
    summary_lines = [
        f"Verification Report: {report_id}",
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}",
        f"Commit ID: {commit_id if commit_id else 'Not specified'}",
        f"Total Proofs: {len(all_proofs)}",
        f"  - Verified: {verified_count}",
        f"  - Falsified: {falsified_count}",
        f"  - Unknown/Error: {unknown_count}",
        f"Total Verification Time: {total_time:.2f} seconds",
        "",
        "Details:"
    ]
    
    for result in results:
        summary_lines.append(f"- {result['proposition_desc']}: {result['status']} ({result['verification_time']:.2f}s)")
        if result['status'] != ProofStatus.VERIFIED.value:
            summary_lines.append(f"  Reason: {result['explanation']}")
    
    summary = "\n".join(summary_lines)
    
    # Create and save report
    report = VerificationReport(
        id=report_id,
        timestamp=datetime.now(timezone.utc),
        proofs_verified=verified_count,
        proofs_falsified=falsified_count,
        proofs_unknown=unknown_count,
        total_verification_time=total_time,
        failing_proofs=failing_proofs,
        summary=summary,
        commit_id=commit_id
    )
    
    save_verification_report(report)
    return report


# ----- Financial Logic Initial Propositions -----

def initialize_financial_propositions():
    """Initialize foundational financial propositions for the ledger system."""
    propositions = [
        Proposition(
            id="ledger_balance_preservation",
            description="Total balance is preserved in all transactions (no money creation or destruction)",
            formal_statement="∀ t ∈ Transactions, sum(inputs(t)) = sum(outputs(t))",
            dependencies=[]
        ),
        Proposition(
            id="double_spending_prevention",
            description="No transaction output can be spent more than once",
            formal_statement="∀ o ∈ Outputs, ∀ t1, t2 ∈ Transactions, spends(t1, o) ∧ spends(t2, o) → t1 = t2",
            dependencies=[]
        ),
        Proposition(
            id="transaction_authorization",
            description="All transactions are properly authorized by the owners of the inputs",
            formal_statement="∀ t ∈ Transactions, ∀ i ∈ inputs(t), is_authorized(i, t)",
            dependencies=[]
        ),
        Proposition(
            id="ledger_consistency",
            description="The ledger maintains a consistent ordering of transactions",
            formal_statement="∃ total_order ≤ on Transactions s.t. ∀ t1, t2 ∈ Transactions, t1 depends_on t2 → t2 ≤ t1",
            dependencies=[]
        ),
        Proposition(
            id="no_negative_balances",
            description="Account balances cannot be negative",
            formal_statement="∀ a ∈ Accounts, ∀ t ∈ Time, balance(a, t) ≥ 0",
            dependencies=["ledger_balance_preservation"]
        ),
        Proposition(
            id="merkle_tree_integrity",
            description="The Merkle tree correctly represents all transactions",
            formal_statement="∀ t ∈ Transactions, t ∈ ledger ↔ merkle_proof_exists(t, root)",
            dependencies=["ledger_consistency"]
        ),
        Proposition(
            id="transaction_finality",
            description="Once a transaction is confirmed, it cannot be reversed",
            formal_statement="∀ t ∈ Transactions, confirmed(t, n) ∧ n ≥ finality_threshold → □(t ∈ ledger)",
            dependencies=["ledger_consistency", "merkle_tree_integrity"]
        )
    ]
    
    for proposition in propositions:
        save_proposition(proposition)
    
    print(f"Initialized {len(propositions)} financial propositions")
    return propositions


def initialize_sample_proofs():
    """Initialize sample proofs for some of the propositions."""
    # Sample proof for ledger_balance_preservation
    proof_balance = FormalProof(
        id="proof_ledger_balance_preservation",
        proposition_id="ledger_balance_preservation",
        steps=[
            ProofStep(
                statement="Transactions are defined as having inputs and outputs",
                justification="Definition of transaction model",
                references=["axiom:transaction_definition"]
            ),
            ProofStep(
                statement="For a valid transaction t, validation requires sum(inputs(t)) = sum(outputs(t))",
                justification="Validation rule V1 in transaction processing",
                references=["axiom:validation_rules", "step_1"]
            ),
            ProofStep(
                statement="Only valid transactions are accepted into the ledger",
                justification="Ledger inclusion policy",
                references=["axiom:ledger_inclusion"]
            ),
            ProofStep(
                statement="∀ t ∈ Transactions, sum(inputs(t)) = sum(outputs(t))",
                justification="Combination of steps 1-3",
                references=["step_2", "step_3"]
            )
        ],
        status=ProofStatus.UNKNOWN
    )
    
    # Sample proof for double_spending_prevention
    proof_double_spending = FormalProof(
        id="proof_double_spending_prevention",
        proposition_id="double_spending_prevention",
        steps=[
            ProofStep(
                statement="Transaction outputs are uniquely identified",
                justification="Transaction output model includes unique identifiers",
                references=["axiom:output_uniqueness"]
            ),
            ProofStep(
                statement="The transaction processor maintains an UTXO set",
                justification="UTXO tracking mechanism in the ledger",
                references=["axiom:utxo_tracking"]
            ),
            ProofStep(
                statement="Transaction validation checks that inputs are in the UTXO set",
                justification="Validation rule V2",
                references=["axiom:validation_rules"]
            ),
            ProofStep(
                statement="Upon successful validation, spent outputs are removed from UTXO set",
                justification="UTXO set update procedure",
                references=["step_2", "axiom:utxo_updates"]
            ),
            ProofStep(
                statement="If an output o is spent by transaction t1, it is removed from UTXO set",
                justification="Direct implication of step 4",
                references=["step_4"]
            ),
            ProofStep(
                statement="If o is not in UTXO set, it cannot be spent by another transaction t2",
                justification="Contrapositive of step 3",
                references=["step_3"]
            ),
            ProofStep(
                statement="∀ o ∈ Outputs, ∀ t1, t2 ∈ Transactions, spends(t1, o) ∧ spends(t2, o) → t1 = t2",
                justification="Combination of steps 5 and 6",
                references=["step_5", "step_6"]
            )
        ],
        status=ProofStatus.UNKNOWN
    )
    
    # Intentionally create an invalid proof to demonstrate verification failure
    proof_invalid = FormalProof(
        id="proof_invalid_no_negative_balances",
        proposition_id="no_negative_balances",
        steps=[
            ProofStep(
                statement="Accounts can only be modified through transactions",
                justification="Account state model",
                references=["axiom:account_state"]
            ),
            ProofStep(
                statement="This is a circular reference to create an invalid proof",
                justification="Invalid justification with circular reference",
                references=["step_3"]  # This references a step that doesn't exist yet
            ),
            ProofStep(
                statement="Therefore, account balances are always non-negative",
                justification="Invalid conclusion from invalid reasoning",
                references=["step_1", "step_2"]
            )
        ],
        status=ProofStatus.UNKNOWN
    )
    
    proofs = [proof_balance, proof_double_spending, proof_invalid]
    for proof in proofs:
        save_proof(proof)
    
    print(f"Initialized {len(proofs)} sample proofs")
    return proofs


# ----- Initialization Function -----

def initialize():
    """Initialize the formal verification system with sample data if empty."""
    try:
        # Check if propositions already exist
        propositions = list_propositions()
        if not propositions:
            # Initialize propositions and proofs
            initialize_financial_propositions()
            initialize_sample_proofs()
            
            # Run verification pipeline
            report = run_verification_pipeline(commit_id="initial")
            print("Verification pipeline complete")
            print(report.summary)
    except Exception as e:
        print(f"Error during initialization: {str(e)}")


# Initialize when module is loaded
# Add a router for FastAPI
from fastapi import APIRouter

router = APIRouter(prefix="/proof-system")

@router.get("/health")
def check_health_proof_system():
    """Check if the proof system API is working"""
    return {"status": "ok", "message": "Proof System API is operational"}

initialize()
