"""Unified Mathematical Formalism and Verification API

This API provides a unified framework for formal mathematical verification
across the Hardcard system. It implements foundations from category theory,
type theory, and formal logic to verify mathematical properties of various
subsystems.

Implements Task I from the formal verification roadmap:
- Unified Mathematical Formalism and Specification Framework
"""

from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Tuple, Set, Union, Literal
from enum import Enum
from datetime import datetime
import json
import databutton as db
import re
import hashlib

# Import verification functions from other APIs
from app.apis.formal_investments import verify_formal_portfolio
from app.apis.realtblock_formal import verify_formal as verify_ledger
from app.apis.family_trust_office_formal import verify_budget_constraints, verify_savings_goals_progress, verify_temporal_consistency
from app.apis.security_formal import verify_formal_security
from app.apis.governance_verification_formal import run_formal_verification as verify_governance_state

# Create router
router = APIRouter(prefix="/formal-verification")

# --- MATHEMATICAL FORMALISM FRAMEWORK ---

"""
== UNIFIED MATHEMATICAL FORMALISM ==

Foundational Frameworks:

1. Type Theory (TT):
   - A typed lambda calculus forms the core of our mathematical framework
   - Types T represent properties and specifications
   - Terms t:T represent objects satisfying those specifications
   - Functions f: A → B transform objects while preserving their properties

2. Category Theory (CT):
   - Categories represent domains of objects with transformations between them
   - Functors represent structure-preserving maps between domains
   - Natural transformations represent coherent families of transformations
   - Monads encapsulate computational effects

3. Higher-Order Logic (HOL):
   - First-order logic extended with quantification over functions and predicates
   - Provides a foundation for expressing complex specifications
   - Supports mechanized reasoning about specifications

HARDCARD FORMALISM STRUCTURE:

1. Base Categories:
   - FinSet: Category of finite sets (users, accounts, etc.)
   - Mon: Category of monoids (monetary values, accumulative metrics)
   - Meas: Category of measurable spaces (probability distributions)

2. Derived Categories:
   - Portfolio: Objects are portfolios, morphisms are transformations
   - Security: Objects are security states, morphisms are state transitions
   - Legacy: Objects are legacy rules, morphisms are rule applications

3. Core Functors:
   - Value: Portfolio → Mon (extracts monetary value)
   - Risk: Portfolio → Meas (maps to risk probability distribution)
   - Legal: Legacy → FinSet (extracts affected entities)

4. Verification Framework:
   - Properties are represented as types in dependent type theory
   - Verification is type checking: proving an object has the required type
   - Composition properties ensure modular verification
"""

# --- Models ---

class FormalismType(str, Enum):
    """Types of formal mathematical frameworks supported"""
    TYPE_THEORY = "type_theory"
    CATEGORY_THEORY = "category_theory"
    HIGHER_ORDER_LOGIC = "higher_order_logic"
    SET_THEORY = "set_theory"


class VerificationStrategy(str, Enum):
    """Verification strategies supported by the system"""
    DEDUCTIVE = "deductive"     # Proof-based verification
    MODEL_CHECKING = "model_checking"  # State-space exploration
    ABSTRACT_INTERP = "abstract_interpretation"  # Abstract semantics
    REFINEMENT = "refinement"   # Stepwise refinement verification


class MathematicalProperty(BaseModel):
    """A mathematical property to be verified"""
    id: str = Field(..., description="Unique identifier for the property")
    name: str = Field(..., description="Human-readable name")
    formalism: FormalismType = Field(..., description="Mathematical formalism used")
    formal_statement: str = Field(..., description="Formal statement in the specified formalism")
    natural_description: str = Field(..., description="Natural language description")
    verification_strategy: VerificationStrategy


class VerificationDomain(str, Enum):
    """Domains that can be verified in the system"""
    PORTFOLIO = "portfolio"
    SECURITY = "security"
    LEGACY = "legacy"
    TRUST_FUND = "trust_fund"
    HARDCARD = "hardcard"
    LEDGER = "ledger"
    GOVERNANCE = "governance"


class PropertyVerificationResult(BaseModel):
    """Result of verifying a single property"""
    property_id: str
    property_name: str
    satisfied: bool
    proof_sketch: Optional[str] = None
    counter_example: Optional[Dict[str, Any]] = None


class DomainVerificationRequest(BaseModel):
    """Request to verify properties in a specific domain"""
    domain: VerificationDomain
    entity_id: str
    properties: Optional[List[str]] = None  # If None, verify all properties
    verification_strategy: Optional[VerificationStrategy] = None  # If None, use default


class DomainVerificationResponse(BaseModel):
    """Response with verification results for a domain"""
    domain: VerificationDomain
    entity_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    valid: bool
    property_results: List[PropertyVerificationResult]
    verification_duration_ms: int


class VerifyAllRequest(BaseModel):
    """Request to verify all domains for an entity"""
    profile_id: str
    domains: Optional[List[VerificationDomain]] = None  # If None, verify all domains


class VerifyAllResponse(BaseModel):
    """Comprehensive verification results across domains"""
    profile_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    valid: bool
    domain_results: Dict[str, DomainVerificationResponse]
    verification_duration_ms: int


class FormalSpecification(BaseModel):
    """A formal specification document"""
    id: str
    name: str
    domain: VerificationDomain
    formalism: FormalismType
    version: str
    content: str
    properties: List[MathematicalProperty]


class CreateSpecificationRequest(BaseModel):
    """Request to create a new formal specification"""
    name: str
    domain: VerificationDomain
    formalism: FormalismType
    content: str
    properties: List[Dict[str, Any]]


# --- Helper Functions ---

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


def get_property_definitions() -> Dict[str, MathematicalProperty]:
    """Get all defined mathematical properties"""
    try:
        key = sanitize_storage_key("formal_verification_properties")
        data = db.storage.json.get(key, default={})
        return {prop_id: MathematicalProperty(**prop_data) for prop_id, prop_data in data.items()}
    except Exception as e:
        print(f"Error loading properties: {e}")
        return {}


def save_property_definitions(properties: Dict[str, MathematicalProperty]):
    """Save property definitions to storage"""
    key = sanitize_storage_key("formal_verification_properties")
    data = {prop_id: prop.dict() for prop_id, prop in properties.items()}
    db.storage.json.put(key, data)


def get_formal_specifications() -> Dict[str, FormalSpecification]:
    """Get all formal specifications"""
    try:
        key = sanitize_storage_key("formal_specifications")
        data = db.storage.json.get(key, default={})
        return {spec_id: FormalSpecification(**spec_data) for spec_id, spec_data in data.items()}
    except Exception as e:
        print(f"Error loading specifications: {e}")
        return {}


def save_formal_specifications(specifications: Dict[str, FormalSpecification]):
    """Save formal specifications to storage"""
    key = sanitize_storage_key("formal_specifications")
    data = {spec_id: spec.dict() for spec_id, spec in specifications.items()}
    db.storage.json.put(key, data)


def get_verification_history(entity_id: str, domain: VerificationDomain) -> List[DomainVerificationResponse]:
    """Get verification history for an entity in a domain"""
    try:
        key = sanitize_storage_key(f"verification_history_{domain}_{entity_id}")
        data = db.storage.json.get(key, default=[])
        return [DomainVerificationResponse(**item) for item in data]
    except Exception as e:
        print(f"Error loading verification history: {e}")
        return []


def save_verification_result(result: DomainVerificationResponse):
    """Save a verification result to history"""
    history = get_verification_history(result.entity_id, result.domain)
    history.append(result)
    # Keep only the last 10 results
    if len(history) > 10:
        history = history[-10:]
    key = sanitize_storage_key(f"verification_history_{result.domain}_{result.entity_id}")
    data = [item.dict() for item in history]
    db.storage.json.put(key, data)


# --- Verification Functions ---

async def verify_portfolio_properties(profile_id: str, properties: Optional[List[str]] = None) -> DomainVerificationResponse:
    """Verify mathematical properties of a portfolio"""
    import time
    start_time = time.time()
    
    # Call the existing portfolio verification function
    try:
        verification_result = verify_formal_portfolio(profile_id)
        
        # Transform the result into our unified format
        property_results = []
        for prop in verification_result.properties_satisfied:
            property_results.append(PropertyVerificationResult(
                property_id=f"portfolio_{prop}",
                property_name=prop,
                satisfied=True,
                proof_sketch=f"Verified through algebraic properties check for {prop}"
            ))
            
        for prop in verification_result.properties_violated:
            property_results.append(PropertyVerificationResult(
                property_id=f"portfolio_{prop}",
                property_name=prop,
                satisfied=False,
                counter_example=verification_result.counter_examples.get(prop, None)
            ))
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.PORTFOLIO,
            entity_id=profile_id,
            valid=verification_result.valid,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )
    except Exception as e:
        property_results = [PropertyVerificationResult(
            property_id="portfolio_verification_error",
            property_name="Portfolio Verification",
            satisfied=False,
            counter_example={"error": str(e)}
        )]
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.PORTFOLIO,
            entity_id=profile_id,
            valid=False,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )


async def verify_trust_fund_properties(profile_id: str, properties: Optional[List[str]] = None) -> DomainVerificationResponse:
    """Verify mathematical properties of a trust fund"""
    import time
    start_time = time.time()
    
    # Call the existing trust fund verification functions from family_trust_office_formal
    try:
        budget_verification = verify_budget_constraints(profile_id)
        savings_verification = verify_savings_goals_progress(profile_id)
        temporal_verification = verify_temporal_consistency(profile_id)
        
        # Transform the results into our unified format
        property_results = []
        
        # Budget constraint properties
        budget_satisfied = len(budget_verification["violated"]) == 0
        property_results.append(PropertyVerificationResult(
            property_id="trust_fund_budget_constraints",
            property_name="Budget Constraints",
            satisfied=budget_satisfied,
            proof_sketch=f"Verified through budget analysis: {len(budget_verification['satisfied'])} satisfied, {len(budget_verification['violated'])} violated",
            counter_example=budget_verification["violated"] if not budget_satisfied else None
        ))
        
        # Savings goals properties
        goals_at_risk = len(savings_verification["at_risk"]) > 0
        property_results.append(PropertyVerificationResult(
            property_id="trust_fund_savings_goals",
            property_name="Savings Goals Progress",
            satisfied=not goals_at_risk,
            proof_sketch=f"Verified through savings analysis: {len(savings_verification['achieved'])} achieved, {len(savings_verification['in_progress'])} in progress, {len(savings_verification['at_risk'])} at risk",
            counter_example=savings_verification["at_risk"] if goals_at_risk else None
        ))
        
        # Temporal consistency property
        temporal_consistent = temporal_verification["overall_consistent"]
        property_results.append(PropertyVerificationResult(
            property_id="trust_fund_temporal_consistency",
            property_name="Temporal Consistency",
            satisfied=temporal_consistent,
            proof_sketch=f"Verified through temporal analysis of events and payments",
            counter_example={"details": "Temporal inconsistency detected"} if not temporal_consistent else None
        ))
        
        # Overall validity
        valid = budget_satisfied and not goals_at_risk and temporal_consistent
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.TRUST_FUND,
            entity_id=profile_id,
            valid=valid,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )
    except Exception as e:
        property_results = [PropertyVerificationResult(
            property_id="trust_fund_verification_error",
            property_name="Trust Fund Verification",
            satisfied=False,
            counter_example={"error": str(e)}
        )]
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.TRUST_FUND,
            entity_id=profile_id,
            valid=False,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )


async def verify_security_properties(profile_id: str, properties: Optional[List[str]] = None) -> DomainVerificationResponse:
    """Verify mathematical properties of security system"""
    import time
    start_time = time.time()
    
    # Call the existing security verification function
    try:
        verification_result = verify_formal_security()
        
        # Transform the result into our unified format
        property_results = []
        for prop_name, prop_result in verification_result.properties.items():
            property_results.append(PropertyVerificationResult(
                property_id=f"security_{prop_name}",
                property_name=prop_name,
                satisfied=prop_result.satisfied,
                proof_sketch=prop_result.proof if prop_result.satisfied else None,
                counter_example=prop_result.counter_example if not prop_result.satisfied else None
            ))
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.SECURITY,
            entity_id=profile_id,
            valid=verification_result.valid,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )
    except Exception as e:
        property_results = [PropertyVerificationResult(
            property_id="security_verification_error",
            property_name="Security Verification",
            satisfied=False,
            counter_example={"error": str(e)}
        )]
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.SECURITY,
            entity_id=profile_id,
            valid=False,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )


async def verify_ledger_properties(ledger_id: str, properties: Optional[List[str]] = None) -> DomainVerificationResponse:
    """Verify mathematical properties of a ledger"""
    import time
    start_time = time.time()
    
    # For ledger verification, we need the ledger data
    # This is a simplified approach - in practice, you'd retrieve the actual ledger
    try:
        # Create a simplified request object for the existing verify_ledger function
        from app.apis.realtblock_formal import VerifyLedgerRequest
        
        # Fetch ledger data - this is a placeholder
        key = sanitize_storage_key(f"ledger_{ledger_id}")
        ledger_data = db.storage.json.get(key, default=None)
        
        if not ledger_data:
            raise ValueError(f"Ledger {ledger_id} not found")
        
        verification_request = VerifyLedgerRequest(ledger_id=ledger_id, events=ledger_data["events"])
        verification_result = verify_ledger(verification_request)
        
        # Transform the result into our unified format
        property_results = []
        if verification_result.valid:
            property_results.append(PropertyVerificationResult(
                property_id="ledger_consistency",
                property_name="Ledger Consistency",
                satisfied=True,
                proof_sketch="Verified through chain integrity and cryptographic checks"
            ))
            property_results.append(PropertyVerificationResult(
                property_id="ledger_temporal_consistency",
                property_name="Temporal Consistency",
                satisfied=True,
                proof_sketch="Verified through timestamp ordering analysis"
            ))
        else:
            for issue in verification_result.issues:
                property_results.append(PropertyVerificationResult(
                    property_id=f"ledger_{issue.type.lower()}",
                    property_name=issue.type,
                    satisfied=False,
                    counter_example={"issue": issue.description, "location": issue.location}
                ))
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.LEDGER,
            entity_id=ledger_id,
            valid=verification_result.valid,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )
    except Exception as e:
        property_results = [PropertyVerificationResult(
            property_id="ledger_verification_error",
            property_name="Ledger Verification",
            satisfied=False,
            counter_example={"error": str(e)}
        )]
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.LEDGER,
            entity_id=ledger_id,
            valid=False,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )


async def verify_governance_properties(entity_id: str, properties: Optional[List[str]] = None) -> DomainVerificationResponse:
    """Verify mathematical properties of governance system"""
    import time
    start_time = time.time()
    
    # Call the governance verification function
    try:
        # Create a pipeline with appropriate properties
        from app.apis.governance_verification_formal import FormalVerificationPipeline, PipelineCategory, FormalProperty, VerificationType
        
        # Construct a pipeline to use for verification
        pipeline = FormalVerificationPipeline(
            id="gov_verification",
            name="Governance Verification",
            description="Formal verification of governance properties",
            category=PipelineCategory.CONSISTENCY,
            formal_properties=[FormalProperty.ASSOCIATIVITY, FormalProperty.TEMPORAL_CONSISTENCY, FormalProperty.HASH_CONSISTENCY],
            verification_type=VerificationType.ALGEBRAIC
        )
        
        # Get governance verification parameters
        key = sanitize_storage_key(f"governance_{entity_id}")
        governance_data = db.storage.json.get(key, default=None)
        
        if not governance_data:
            # Create minimal verification parameters
            parameters = {
                "events": [],
                "operations": [],
                "public_keys": {}
            }
        else:
            parameters = {
                "events": governance_data.get("events", []),
                "operations": governance_data.get("operations", []),
                "public_keys": governance_data.get("public_keys", {})
            }
        
        # Run the formal verification
        verification_result = verify_governance_state(pipeline, parameters)
        
        # Transform the result into our unified format
        property_results = []
        for prop in verification_result.properties_satisfied:
            property_results.append(PropertyVerificationResult(
                property_id=f"governance_{prop}",
                property_name=prop,
                satisfied=True,
                proof_sketch=f"Verified through algebraic verification of {prop}"
            ))
            
        for prop in verification_result.properties_violated:
            property_results.append(PropertyVerificationResult(
                property_id=f"governance_{prop}",
                property_name=prop,
                satisfied=False,
                counter_example=verification_result.counter_examples.get(prop, None)
            ))
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.GOVERNANCE,
            entity_id=entity_id,
            valid=verification_result.valid,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )
    except Exception as e:
        property_results = [PropertyVerificationResult(
            property_id="governance_verification_error",
            property_name="Governance Verification",
            satisfied=False,
            counter_example={"error": str(e)}
        )]
        
        end_time = time.time()
        return DomainVerificationResponse(
            domain=VerificationDomain.GOVERNANCE,
            entity_id=entity_id,
            valid=False,
            property_results=property_results,
            verification_duration_ms=int((end_time - start_time) * 1000)
        )


async def verify_domain(request: DomainVerificationRequest) -> DomainVerificationResponse:
    """Verify properties in a specific domain"""
    if request.domain == VerificationDomain.PORTFOLIO:
        return await verify_portfolio_properties(request.entity_id, request.properties)
    elif request.domain == VerificationDomain.TRUST_FUND:
        return await verify_trust_fund_properties(request.entity_id, request.properties)
    elif request.domain == VerificationDomain.SECURITY:
        return await verify_security_properties(request.entity_id, request.properties)
    elif request.domain == VerificationDomain.LEDGER:
        return await verify_ledger_properties(request.entity_id, request.properties)
    elif request.domain == VerificationDomain.GOVERNANCE:
        return await verify_governance_properties(request.entity_id, request.properties)
    else:
        raise HTTPException(status_code=400, detail=f"Verification for domain {request.domain} not implemented")


# --- Endpoints ---

@router.post("/domains/{domain}/verify", response_model=DomainVerificationResponse)
async def verify_domain_endpoint(domain: VerificationDomain, entity_id: str, 
                         properties: Optional[List[str]] = Query(None)):
    """Verify properties in a specific domain
    
    This endpoint performs a formal verification of mathematical properties
    in the specified domain for the given entity.
    """
    request = DomainVerificationRequest(
        domain=domain,
        entity_id=entity_id,
        properties=properties
    )
    result = await verify_domain(request)
    save_verification_result(result)
    return result


@router.post("/verify-all", response_model=VerifyAllResponse)
async def verify_all_endpoint(request: VerifyAllRequest):
    """Verify all domains for an entity
    
    This endpoint performs a comprehensive formal verification across all domains
    for the given entity, checking mathematical properties and consistency.
    """
    import time
    start_time = time.time()
    profile_id = request.profile_id
    
    # Default to all available domains if none specified
    if request.domains is None:
        domains = [
            VerificationDomain.PORTFOLIO, 
            VerificationDomain.SECURITY, 
            VerificationDomain.TRUST_FUND, 
            VerificationDomain.LEDGER,
            VerificationDomain.GOVERNANCE
        ]
    else:
        domains = request.domains
    
    # Run verification for each domain
    domain_results = {}
    all_valid = True
    
    for domain in domains:
        try:
            # Create a verification request for the domain
            ver_request = DomainVerificationRequest(
                domain=domain,
                entity_id=profile_id
            )
            
            # Perform the verification
            result = await verify_domain(ver_request)
            domain_results[domain] = result
            
            # Update overall validity
            if not result.valid:
                all_valid = False
                
        except Exception as e:
            # If a domain verification fails, log it and continue
            print(f"Error verifying domain {domain}: {e}")
            # Create a failed verification result
            domain_results[domain] = DomainVerificationResponse(
                domain=domain,
                entity_id=profile_id,
                valid=False,
                property_results=[
                    PropertyVerificationResult(
                        property_id=f"{domain}_verification_error",
                        property_name=f"{domain} Verification",
                        satisfied=False,
                        counter_example={"error": str(e)}
                    )
                ],
                verification_duration_ms=0
            )
            all_valid = False
    
    end_time = time.time()
    duration_ms = int((end_time - start_time) * 1000)
    
    return VerifyAllResponse(
        profile_id=profile_id,
        timestamp=datetime.now().isoformat(),
        valid=all_valid,
        domain_results=domain_results,
        verification_duration_ms=duration_ms
    )


@router.get("/verification-history/{domain}/{entity_id}", response_model=List[DomainVerificationResponse])
async def get_verification_history_endpoint(domain: VerificationDomain, entity_id: str):
    """Get verification history for an entity in a domain
    
    This endpoint retrieves the history of formal verifications performed
    for the specified entity in the given domain.
    """
    return get_verification_history(entity_id, domain)


@router.post("/specifications", response_model=FormalSpecification)
async def create_specification(request: CreateSpecificationRequest):
    """Create a new formal specification
    
    This endpoint allows the creation of a formal mathematical specification
    for a domain, defining properties that can be verified.
    """
    # Generate a unique ID for the specification
    spec_id = f"{request.domain.lower()}_{hashlib.md5(request.name.encode()).hexdigest()[:8]}"
    
    # Create property objects
    properties = []
    for prop in request.properties:
        prop_id = f"{spec_id}_{hashlib.md5(prop['name'].encode()).hexdigest()[:8]}"
        properties.append(MathematicalProperty(
            id=prop_id,
            name=prop['name'],
            formalism=prop['formalism'],
            formal_statement=prop['formal_statement'],
            natural_description=prop['natural_description'],
            verification_strategy=prop['verification_strategy']
        ))
    
    # Create the specification
    spec = FormalSpecification(
        id=spec_id,
        name=request.name,
        domain=request.domain,
        formalism=request.formalism,
        version="1.0.0",
        content=request.content,
        properties=properties
    )
    
    # Save to storage
    specs = get_formal_specifications()
    specs[spec_id] = spec
    save_formal_specifications(specs)
    
    # Also save the properties
    prop_defs = get_property_definitions()
    for prop in properties:
        prop_defs[prop.id] = prop
    save_property_definitions(prop_defs)
    
    return spec


@router.get("/specifications", response_model=List[FormalSpecification])
async def list_specifications():
    """List all formal specifications
    
    This endpoint retrieves all formal specifications defined in the system.
    """
    specs = get_formal_specifications()
    return list(specs.values())


@router.get("/specifications/{spec_id}", response_model=FormalSpecification)
async def get_specification(spec_id: str):
    """Get a formal specification by ID
    
    This endpoint retrieves a specific formal specification by its ID.
    """
    specs = get_formal_specifications()
    if spec_id not in specs:
        raise HTTPException(status_code=404, detail=f"Specification {spec_id} not found")
    return specs[spec_id]


@router.get("/properties", response_model=List[MathematicalProperty])
async def list_properties(domain: Optional[VerificationDomain] = None):
    """List mathematical properties
    
    This endpoint retrieves all mathematical properties defined in the system,
    optionally filtered by domain.
    """
    props = get_property_definitions()
    properties = list(props.values())
    
    # Filter by domain if specified
    if domain:
        # This is a simplified approach - in practice, you'd have a domain field in the property
        # or derive it from the property ID
        properties = [p for p in properties if p.id.startswith(domain.lower())]
    
    return properties
