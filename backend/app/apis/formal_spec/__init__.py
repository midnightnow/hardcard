from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

router = APIRouter()

class ExplainMathRequest(BaseModel):
    specificationId: str
    detailLevel: str = "intermediate"  # "basic", "intermediate", or "advanced"

class ExplainMathResponse(BaseModel):
    explanation: str
    references: Optional[List[str]] = None
    domains: List[str] = []

@router.post("/explain_math")
def explain_formal_math(body: ExplainMathRequest) -> ExplainMathResponse:
    """Generate a natural language explanation of a formal mathematical specification in the registry."""
    
    # Dictionary of predefined explanations for each specification
    explanations = {
        "portfolio_addition": {
            "basic": "The Portfolio Addition Monoid defines how investment portfolios can be combined in a consistent way. It guarantees that the order of combining portfolios doesn't matter, and ensures that portfolio values are preserved through operations.",
            "intermediate": (
                "The Portfolio Addition Monoid creates a mathematical structure where portfolios can be combined through an operation that satisfies key algebraic properties. "
                "\n\nFirst, the associativity property ensures that (A + B) + C = A + (B + C), meaning the grouping of operations doesn't affect the outcome. "
                "\n\nSecond, the identity property guarantees that an empty portfolio acts as a neutral element - combining any portfolio with the empty one leaves it unchanged. "
                "\n\nFinally, the value preservation property ensures that any operation on a portfolio will never decrease its value, providing mathematical guarantees for principal protection."
            ),
            "advanced": (
                "The Portfolio Addition Monoid formalizes portfolio operations as an algebraic structure (P, ⋅, e) where P is the set of all portfolios, ⋅ is the binary composition operation, and e is the identity element. "
                "\n\nThis structure satisfies the monoid axioms: "
                "\n\n1. Associativity: ∀a,b,c ∈ P: (a ⋅ b) ⋅ c = a ⋅ (b ⋅ c), which ensures operational consistency regardless of execution order. "
                "\n\n2. Identity: ∀a ∈ P: a ⋅ e = e ⋅ a = a, establishing the empty portfolio as the neutral element. "
                "\n\n3. Value Preservation: ∀p ∈ P, a: 𝒱(a(p)) ≥ 𝒱(p), which provides a rigorous guarantee of principal protection. "
                "\n\nThis algebraic model enables formal verification of portfolio operations, allowing us to prove that compositions and transformations maintain critical invariants across the system."
            )
        },
        "budget_constraint": {
            "basic": "The Budget Constraint Theorem ensures that the family trust can never spend more money than it has available, providing a mathematical guarantee of financial discipline.",
            "intermediate": (
                "The Budget Constraint Theorem establishes a fundamental rule in the trust's financial system: total expenses cannot exceed total income. "
                "\n\nThis is formalized through three key properties: "
                "\n\n1. The Expense Sum Bound ensures that all expenses are limited by the allocated budget. "
                "\n\n2. The Budget Limit property guarantees that the budget itself cannot exceed available income. "
                "\n\n3. The Temporal Consistency property ensures that account balances accurately reflect all historical transactions."
            ),
            "advanced": (
                "The Budget Constraint Theorem formalizes financial soundness through a precise mathematical model: ∀b ∈ Budgets, t ∈ Time: ∑_{e ∈ Expenses(b, t)} 𝒜(e) ≤ ∑_{i ∈ Income(b, t)} 𝒜(i) "
                "\n\nThis theorem is proven using three derived lemmas: "
                "\n\n1. Expense Sum Bound: ∑_{e ∈ Expenses(b, t)} 𝒜(e) ≤ Budget(b, t), which constrains expenditures to authorized limits. "
                "\n\n2. Budget Limit: Budget(b, t) ≤ ∑_{i ∈ Income(b, t)} 𝒜(i), which ensures budgets cannot exceed available resources. "
                "\n\n3. Temporal Consistency: ∀t_1 < t_2: Balance(b, t_1) + Income(b, t_1, t_2) - Expenses(b, t_1, t_2) = Balance(b, t_2), enforcing invariant account balances. "
                "\n\nThis formal model enables automated verification of financial operations, guaranteeing that all transactions maintain system-wide fiscal responsibility."
            )
        },
        "rotate_crypto_key": {
            "basic": "The Key Rotation Lemma proves that when we update cryptographic keys, existing signatures remain valid, allowing for smooth transitions while maintaining security.",
            "intermediate": (
                "The Key Rotation Lemma establishes that when cryptographic keys are rotated, three critical properties are maintained: "
                "\n\n1. Preservation of Verification ensures that existing signatures can be transformed to remain valid with new keys. "
                "\n\n2. Rotation Transitivity allows multiple key rotations to be composed, enabling sequential updates. "
                "\n\n3. Security Preservation guarantees that key rotation never reduces the security level, only maintains or improves it."
            ),
            "advanced": (
                "The Key Rotation Lemma formalizes a crucial cryptographic invariant: ∀m ∈ Messages, k_{old}, k_{new} ∈ Keys: Verify(m, Sign(m, k_{old}), Pub(k_{old})) ∧ Verify(m, Sign(m, k_{new}), Pub(k_{new})). "
                "\n\nThis lemma establishes three fundamental properties: "
                "\n\n1. Preservation of Verification: ∀m, σ, k_{old}, k_{new}: Verify(m, σ, Pub(k_{old})) ⟹ Rotate(σ, k_{old}, k_{new}) ⟹ Verify(m, σ, Pub(k_{new})). "
                "\n\n2. Rotation Transitivity: ∀k_1, k_2, k_3 ∈ Keys: Rotate(k_1, k_2) ∧ Rotate(k_2, k_3) ⟹ Rotate(k_1, k_3). "
                "\n\n3. Security Preservation: ∀k_{old}, k_{new} ∈ Keys: SecurityLevel(k_{new}) ≥ SecurityLevel(k_{old}). "
                "\n\nThese properties have been formally verified using interactive theorem proving in EasyCrypt, providing mathematical certainty about the security of key rotation operations."
            )
        },
        "ledger_hash_chain": {
            "basic": "The Ledger Hash Chain ensures that once data is recorded in the ledger, it cannot be altered without detection, providing tamper evidence for financial records.",
            "intermediate": (
                "The Ledger Hash Chain specification defines a structure where each entry in the ledger contains the cryptographic hash of the previous entry, creating an unbreakable chain. "
                "\n\nThis chain has three key properties: "
                "\n\n1. Hash Chain Integrity ensures each entry links to the previous one through its hash. "
                "\n\n2. Temporal Consistency guarantees that events occur in a causally consistent order. "
                "\n\n3. Immutability ensures that modifying any entry would require finding a hash collision, which is computationally infeasible."
            ),
            "advanced": (
                "The Ledger Hash Chain specification establishes a formally verified structure with the primary invariant: ∀i > 0: events[i].previous_hash = hash(events[i-1]). "
                "\n\nThis structure ensures three critical properties: "
                "\n\n1. Hash Chain Integrity: Each entry contains the cryptographic hash of the previous entry, creating an inviolable chain of provenance. "
                "\n\n2. Temporal Consistency: ∀e_1, e_2 ∈ Events: e_1 depends on e_2 ⟹ τ(e_2) < τ(e_1), ensuring causal ordering of events. "
                "\n\n3. Immutability: ∀i, h = hash(events[i]): P(find m ≠ events[i] : hash(m) = h) ≈ 0, leveraging the preimage resistance property of cryptographic hash functions. "
                "\n\nThis specification has been formally verified using model checking in TLA+, proving that modifying any historical record would be detected through hash chain invalidation."
            )
        },
        "governance_state_monoid": {
            "basic": "The Governance State Monoid ensures that governance decisions form a consistent chain, with each new decision building properly on previous ones.",
            "intermediate": (
                "The Governance State Monoid models governance as a mathematical structure where states transition according to strict rules. "
                "\n\nIt has three key properties: "
                "\n\n1. Associativity ensures that governance decisions can be applied in any order without changing the outcome. "
                "\n\n2. The Identity property ensures there's a neutral state that doesn't affect governance when combined with other states. "
                "\n\n3. History Preservation guarantees that the history of governance decisions is always maintained through transitions."
            ),
            "advanced": (
                "The Governance State Monoid formalizes governance as an algebraic structure (G, ⋅, e) where G is the set of governance states, ⋅ is the state transition operation, and e is the initial state. "
                "\n\nThis algebraic model satisfies: "
                "\n\n1. Associativity: ∀a,b,c ∈ G: (a ⋅ b) ⋅ c = a ⋅ (b ⋅ c), ensuring order-independent application of governance transitions. "
                "\n\n2. Identity: ∀a ∈ G: a ⋅ e = e ⋅ a = a, establishing the initial state as a neutral element. "
                "\n\n3. History Preservation: ∀a,b ∈ G: a ⋅ b preserves the history of a, formally encoding that governance transitions accumulate rather than override historical decisions. "
                "\n\nThis model has been formally verified using algebraic methods in the Lean proof assistant, providing mathematical guarantees about governance state evolution consistency."
            )
        }
    }
    
    # Get the appropriate explanation or return an error if not found
    if body.specificationId not in explanations:
        raise HTTPException(status_code=404, detail=f"Specification ID '{body.specificationId}' not found in the registry")
    
    # Get the explanation for the requested detail level or default to intermediate
    detail_level = body.detailLevel
    if detail_level not in ["basic", "intermediate", "advanced"]:
        detail_level = "intermediate"
    
    # Map specification IDs to domains for metadata
    domain_map = {
        "portfolio_addition": ["formal_investments", "portfolio"],
        "budget_constraint": ["family_trust_office", "budget"],
        "rotate_crypto_key": ["crypto_agility_formal", "cryptography"],
        "ledger_hash_chain": ["ledger"],
        "governance_state_monoid": ["governance"]
    }
    
    # Return the explanation with applicable references
    return ExplainMathResponse(
        explanation=explanations[body.specificationId][detail_level],
        references=[
            "Category Theory for Computer Science",
            "Principles of Formal Verification", 
            "Algebraic Methods in Cryptography"
        ],
        domains=domain_map.get(body.specificationId, [])
    )