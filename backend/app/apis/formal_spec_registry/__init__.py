import json
import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import databutton as db

router = APIRouter(prefix="/formal/spec_registry")

# Model definitions
class ProofStep(BaseModel):
    step_number: int
    statement: str
    justification: str

class Proof(BaseModel):
    proof_technique: str
    proof_steps: Optional[List[ProofStep]] = None
    proof_sketch: Optional[str] = None

class Implication(BaseModel):
    description: str
    impacted_component: str
    severity: str

class SpecMetadata(BaseModel):
    created_at: str
    updated_at: str
    authors: List[str]
    tags: List[str]

class FormalSpec(BaseModel):
    id: str
    domain: str
    type: str
    title: str
    formal_statement: str
    natural_language: Optional[str] = None
    proof: Optional[Proof] = None
    implications: Optional[List[Implication]] = None
    dependencies: Optional[List[str]] = None
    verification_status: str
    llm_explanation: Optional[str] = None
    metadata: Optional[SpecMetadata] = None

class SpecRegistry(BaseModel):
    version: str
    specs: List[FormalSpec]

class SpecResponse(BaseModel):
    spec: FormalSpec

class SpecListResponse(BaseModel):
    specs: List[FormalSpec]
    total: int
    domains: List[str]
    types: List[str]

class SpecSearchParams(BaseModel):
    domain: Optional[str] = None
    type: Optional[str] = None
    verification_status: Optional[str] = None
    search_term: Optional[str] = None

# Helper function to load the spec registry
def load_spec_registry() -> SpecRegistry:
    try:
        # Check if we have it in storage first
        if db.storage.json.exists("formal_spec_registry"):
            registry_data = db.storage.json.get("formal_spec_registry")
            return SpecRegistry(**registry_data)
        
        # If not in storage, load from file system (development mode)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        registry_path = os.path.join(script_dir, "../../../app/formal/spec_registry/spec_registry.json")
        
        with open(registry_path, 'r') as f:
            registry_data = json.load(f)
            # Store in DB for future access
            db.storage.json.put("formal_spec_registry", registry_data)
            return SpecRegistry(**registry_data)
    except Exception as e:
        print(f"Error loading spec registry: {e}")
        # Return empty registry in case of error
        return SpecRegistry(version="1.0.0", specs=[])

# Endpoint to get all specs
@router.get("/specs", response_model=SpecListResponse)
def get_all_specs():
    registry = load_spec_registry()
    domains = list(set(spec.domain for spec in registry.specs))
    types = list(set(spec.type for spec in registry.specs))
    
    return {
        "specs": registry.specs,
        "total": len(registry.specs),
        "domains": domains,
        "types": types
    }

# Endpoint to get a spec by ID
@router.get("/specs/{spec_id}", response_model=SpecResponse)
def get_spec_by_id(spec_id: str):
    registry = load_spec_registry()
    for spec in registry.specs:
        if spec.id == spec_id:
            return {"spec": spec}
    
    raise HTTPException(status_code=404, detail=f"Spec with ID {spec_id} not found")

# Endpoint to search specs
@router.post("/search", response_model=SpecListResponse)
def search_specs(params: SpecSearchParams):
    registry = load_spec_registry()
    domains = list(set(spec.domain for spec in registry.specs))
    types = list(set(spec.type for spec in registry.specs))
    
    filtered_specs = registry.specs
    
    # Apply filters
    if params.domain:
        filtered_specs = [spec for spec in filtered_specs if spec.domain == params.domain]
    
    if params.type:
        filtered_specs = [spec for spec in filtered_specs if spec.type == params.type]
    
    if params.verification_status:
        filtered_specs = [spec for spec in filtered_specs if spec.verification_status == params.verification_status]
    
    if params.search_term:
        search_term = params.search_term.lower()
        filtered_specs = [
            spec for spec in filtered_specs 
            if search_term in spec.id.lower() or 
               search_term in spec.title.lower() or 
               (spec.natural_language and search_term in spec.natural_language.lower()) or
               search_term in spec.formal_statement.lower()
        ]
    
    return {
        "specs": filtered_specs,
        "total": len(filtered_specs),
        "domains": domains,
        "types": types
    }

# Endpoint to get specs by domain
@router.get("/domains/{domain}", response_model=SpecListResponse)
def get_specs_by_domain(domain: str):
    registry = load_spec_registry()
    domains = list(set(spec.domain for spec in registry.specs))
    types = list(set(spec.type for spec in registry.specs))
    
    filtered_specs = [spec for spec in registry.specs if spec.domain == domain]
    
    return {
        "specs": filtered_specs,
        "total": len(filtered_specs),
        "domains": domains,
        "types": types
    }

# Endpoint to get specs by type
@router.get("/types/{type}", response_model=SpecListResponse)
def get_specs_by_type(type: str):
    registry = load_spec_registry()
    domains = list(set(spec.domain for spec in registry.specs))
    types = list(set(spec.type for spec in registry.specs))
    
    filtered_specs = [spec for spec in registry.specs if spec.type == type]
    
    return {
        "specs": filtered_specs,
        "total": len(filtered_specs),
        "domains": domains,
        "types": types
    }

# Endpoint to get dependent specs
@router.get("/dependencies/{spec_id}", response_model=SpecListResponse)
def get_dependent_specs(spec_id: str):
    registry = load_spec_registry()
    domains = list(set(spec.domain for spec in registry.specs))
    types = list(set(spec.type for spec in registry.specs))
    
    # Find specs that depend on the given spec
    dependent_specs = [
        spec for spec in registry.specs 
        if spec.dependencies and spec_id in spec.dependencies
    ]
    
    return {
        "specs": dependent_specs,
        "total": len(dependent_specs),
        "domains": domains,
        "types": types
    }

# Endpoint to generate explanation for a spec using LLM
@router.get("/explain/{spec_id}")
def generate_explanation(spec_id: str):
    registry = load_spec_registry()
    
    # Find the spec
    spec = next((s for s in registry.specs if s.id == spec_id), None)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Spec with ID {spec_id} not found")
    
    # If the spec already has an LLM explanation, return it
    if spec.llm_explanation:
        return {"explanation": spec.llm_explanation}
    
    # Otherwise, return a placeholder
    # In a real implementation, this would call an LLM API
    return {
        "explanation": f"This is a {spec.type.lower()} in the {spec.domain} domain that defines mathematical properties for the system."
    }
