from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
import uuid
import databutton as db
import json
import time
import math
from collections import defaultdict

# This router handles personal identity in the Hardcard Hyperspace
router = APIRouter(tags=["open"])

# Data Models
class IdentitySignature(BaseModel):
    """A cryptographic signature that securely identifies a person"""
    value: str = Field(..., description="The cryptographic signature value")
    algorithm: str = Field("ed25519", description="The signature algorithm used")
    created_at: float = Field(default_factory=time.time, description="Timestamp when the signature was created")

class RelationshipData(BaseModel):
    """Data describing a relationship between identities"""
    relation_type: str = Field(..., description="Type of relationship (e.g. parent-child, spouse, etc.)")
    related_id: str = Field(..., description="ID of the related identity")
    description: Optional[str] = Field(None, description="Human-readable description of the relationship")
    strength: Optional[float] = Field(1.0, description="Strength of relationship (0.0 to 1.0)")
    established_date: Optional[float] = Field(None, description="Time point when this relationship was established")

class PersonalIdentity(BaseModel):
    """A personal identity in the Hardcard Hyperspace"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this identity")
    name: str = Field(..., description="The person's name")
    relationship_description: Optional[str] = Field(None, description="Human-readable description of primary relationship (e.g. 'son of John')")
    time_point: float = Field(..., description="The time point on the spiral where this identity is anchored")
    sector: str = Field("PersonalDomain", description="The sector in Hardcard Hyperspace where this identity exists")
    identity_signature: IdentitySignature
    relationships: List[RelationshipData] = Field(default_factory=list, description="Relationships to other identities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for this identity")
    did: Optional[str] = Field(None, description="Decentralized Identifier (DID) for this identity")
    verification_methods: List[str] = Field(default_factory=list, description="List of supported verification methods")

class CreateIdentityRequest(BaseModel):
    """Request to create a new personal identity"""
    name: str = Field(..., description="The person's name")
    relationship_description: Optional[str] = Field(None, description="Human-readable description of primary relationship")
    time_point: float = Field(..., description="The time point on the spiral where this identity is anchored")
    sector: Optional[str] = Field("PersonalDomain", description="The sector in Hardcard Hyperspace")
    signature_value: Optional[str] = Field(None, description="Optional identity signature value")
    relationships: Optional[List[RelationshipData]] = Field(None, description="Optional relationships to other identities")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for this identity")

class IdentityQueryResponse(BaseModel):
    """Response for an identity query"""
    identity: PersonalIdentity
    spiral_coordinates: Dict[str, float]
    ancestry_path: List[Dict[str, Any]] = Field(default_factory=list)
    descendants_path: List[Dict[str, Any]] = Field(default_factory=list)

# Helper Functions
def _generate_identity_signature() -> str:
    """Generate a secure identity signature (simplified for demo purposes)"""
    return str(uuid.uuid4())

def _get_identities_storage() -> List[PersonalIdentity]:
    """Get the stored identities from Databutton storage"""
    try:
        identities_json = db.storage.json.get("hardcard_identities", default=[])
        return [PersonalIdentity.parse_obj(item) for item in identities_json]
    except Exception as e:
        print(f"Error retrieving identities: {e}")
        return []

def _save_identities(identities: List[PersonalIdentity]) -> None:
    """Save identities to Databutton storage"""
    try:
        identities_json = [identity.dict() for identity in identities]
        db.storage.json.put("hardcard_identities", identities_json)
    except Exception as e:
        print(f"Error saving identities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save identity data: {str(e)}")

def _calculate_spiral_coordinates(time_point: float) -> Dict[str, float]:
    """Calculate the coordinates on the spiral for a given time point"""
    # Default parameters for the spiral
    pitch = 1.0
    turns_per_log_unit = 1.0
    initial_radius = 1.0
    
    # Ensure time is positive
    if time_point <= 0:
        time_point = 0.001
    
    # Calculate coordinates based on logarithmic spiral equations
    import math
    z = pitch * math.log(time_point)
    theta = turns_per_log_unit * math.log(time_point)
    radius = initial_radius + z
    
    # Convert to Cartesian coordinates
    x = radius * math.cos(theta)
    y = radius * math.sin(theta)
    
    return {
        "x": x,
        "y": y,
        "z": z,
        "t": time_point,
        "radius": radius,
        "theta": theta
    }

# API Endpoints
@router.post("/identity", response_model=PersonalIdentity)
def create_identity(request: CreateIdentityRequest) -> PersonalIdentity:
    """Create a new personal identity in the Hardcard Hyperspace"""
    # Generate signature if not provided
    signature_value = request.signature_value or _generate_identity_signature()
    
    # Create the identity object
    identity = PersonalIdentity(
        name=request.name,
        relationship_description=request.relationship_description,
        time_point=request.time_point,
        sector=request.sector,
        identity_signature=IdentitySignature(value=signature_value),
        relationships=request.relationships or [],
        metadata=request.metadata or {}
    )
    
    # Save the new identity
    identities = _get_identities_storage()
    identities.append(identity)
    _save_identities(identities)
    
    return identity

@router.get("/identity/{identity_id}", response_model=PersonalIdentity)
def get_identity(identity_id: str = Path(..., description="The unique ID of the identity to retrieve")) -> PersonalIdentity:
    """Retrieve a personal identity by its ID"""
    identities = _get_identities_storage()
    
    for identity in identities:
        if identity.id == identity_id:
            return identity
    
    raise HTTPException(status_code=404, detail=f"Identity with ID {identity_id} not found")

@router.get("/identities", response_model=List[PersonalIdentity])
def list_identities() -> List[PersonalIdentity]:
    """List all personal identities in the system"""
    return _get_identities_storage()

@router.get("/identity/query", response_model=IdentityQueryResponse)
def query_identity(
    name: str = Query(..., description="The name of the person to query"),
    include_ancestry: bool = Query(False, description="Whether to include ancestry information in the response"),
    include_descendants: bool = Query(False, description="Whether to include descendants information in the response"),
    max_generations: int = Query(3, description="Maximum number of generations to traverse")
) -> IdentityQueryResponse:
    """Query a personal identity and return relevant information including genealogical connections"""
    identities = _get_identities_storage()
    
    # Find the identity with the given name
    found_identity = None
    for identity in identities:
        if identity.name.lower() == name.lower():
            found_identity = identity
            break
    
    if not found_identity:
        raise HTTPException(status_code=404, detail=f"Identity with name {name} not found")
    
    # Calculate spiral coordinates
    coordinates = _calculate_spiral_coordinates(found_identity.time_point)
    
    # Build ancestry path if requested
    ancestry_path = []
    if include_ancestry:
        current = found_identity
        visited = set([current.id])
        generation = 0
        
        # Look for parent relationships and build the ancestry path
        while generation < max_generations:
            parent_relation = None
            for relation in current.relationships:
                if relation.relation_type.lower() in ["parent", "father", "mother"]:
                    parent_relation = relation
                    break
            
            if not parent_relation:
                break
                
            # Find the parent identity
            parent = None
            for identity in identities:
                if identity.id == parent_relation.related_id:
                    parent = identity
                    break
            
            if not parent or parent.id in visited:
                break
                
            # Add parent to ancestry path
            ancestry_path.append({
                "id": parent.id,
                "name": parent.name,
                "relationship": parent_relation.relation_type,
                "time_point": parent.time_point,
                "generation": generation + 1,
                "coordinates": _calculate_spiral_coordinates(parent.time_point),
                "relation_details": {
                    "strength": getattr(parent_relation, "strength", 1.0),
                    "established_date": getattr(parent_relation, "established_date", None),
                    "description": parent_relation.description
                }
            })
            
            # Move up to the parent
            current = parent
            visited.add(current.id)
            generation += 1
    
    # Build descendants path if requested
    descendants_path = []
    if include_descendants:
        # Get all identities that have a parent relationship with the found identity
        def find_descendants(parent_id, gen=0, visited_ids=None):
            if visited_ids is None:
                visited_ids = set()
            if parent_id in visited_ids or gen >= max_generations:
                return []
                
            visited_ids.add(parent_id)
            descendants = []
            
            for identity in identities:
                for relation in identity.relationships:
                    if (relation.relation_type.lower() in ["parent", "father", "mother"] and 
                        relation.related_id == parent_id):
                        # This identity has the found identity as a parent
                        descendant_coords = _calculate_spiral_coordinates(identity.time_point)
                        descendants.append({
                            "id": identity.id,
                            "name": identity.name,
                            "relationship": "child",
                            "time_point": identity.time_point,
                            "generation": gen + 1,
                            "coordinates": descendant_coords,
                            "relation_details": {
                                "strength": getattr(relation, "strength", 1.0),
                                "established_date": getattr(relation, "established_date", None),
                                "description": relation.description
                            }
                        })
                        # Recursively find the descendants of this child
                        child_descendants = find_descendants(identity.id, gen + 1, visited_ids)
                        descendants.extend(child_descendants)
            return descendants
        
        descendants_path = find_descendants(found_identity.id)
    
    return IdentityQueryResponse(
        identity=found_identity,
        spiral_coordinates=coordinates,
        ancestry_path=ancestry_path,
        descendants_path=descendants_path
    )

@router.post("/identity/{identity_id}/relationship", response_model=PersonalIdentity)
def add_relationship(
    identity_id: str = Path(..., description="The ID of the identity to update"),
    relationship: RelationshipData = ...
) -> PersonalIdentity:
    """Add a relationship to an existing identity"""
    identities = _get_identities_storage()
    
    # Find the identity to update
    identity_to_update = None
    index_to_update = -1
    for i, identity in enumerate(identities):
        if identity.id == identity_id:
            identity_to_update = identity
            index_to_update = i
            break
    
    if not identity_to_update:
        raise HTTPException(status_code=404, detail=f"Identity with ID {identity_id} not found")
    
    # Check if related identity exists
    related_exists = False
    for identity in identities:
        if identity.id == relationship.related_id:
            related_exists = True
            break
    
    if not related_exists:
        raise HTTPException(status_code=404, detail=f"Related identity with ID {relationship.related_id} not found")
    
    # Add the relationship
    identity_to_update.relationships.append(relationship)
    identities[index_to_update] = identity_to_update
    
    # If this is a parent-child relationship, we might want to add the inverse relationship
    if relationship.relation_type.lower() in ["parent", "father", "mother"]:
        # Find the related identity
        related_idx = -1
        for i, identity in enumerate(identities):
            if identity.id == relationship.related_id:
                related_idx = i
                break
                
        if related_idx != -1:
            # Determine the inverse relationship type
            inverse_type = "child"
            if relationship.relation_type.lower() == "father":
                inverse_type = "son" if identity_to_update.metadata.get("gender") == "male" else "daughter"
            elif relationship.relation_type.lower() == "mother":
                inverse_type = "son" if identity_to_update.metadata.get("gender") == "male" else "daughter"
                
            # Create the inverse relationship
            inverse_relationship = RelationshipData(
                relation_type=inverse_type,
                related_id=identity_id,
                description=f"Child of {identities[related_idx].name}",
                strength=relationship.strength,
                established_date=relationship.established_date
            )
            
            # Check if the inverse relationship already exists
            exists = False
            for rel in identities[related_idx].relationships:
                if rel.related_id == identity_id and rel.relation_type.lower() == inverse_type.lower():
                    exists = True
                    break
                    
            if not exists:
                identities[related_idx].relationships.append(inverse_relationship)
    
    _save_identities(identities)
    
    return identity_to_update

@router.get("/identity/{identity_id}/lineage", response_model=Dict[str, Any])
def get_identity_lineage(
    identity_id: str = Path(..., description="The ID of the identity to retrieve lineage for"),
    depth: int = Query(2, description="Maximum depth of relations to include")
) -> Dict[str, Any]:
    """Retrieve a comprehensive lineage tree for a personal identity"""
    identities = _get_identities_storage()
    
    # Find the identity
    found_identity = None
    for identity in identities:
        if identity.id == identity_id:
            found_identity = identity
            break
    
    if not found_identity:
        raise HTTPException(status_code=404, detail=f"Identity with ID {identity_id} not found")
    
    # Build a complete lineage tree
    def build_lineage_node(current_id, current_depth=0, visited=None):
        if visited is None:
            visited = set()
            
        if current_id in visited or current_depth >= depth:
            return None
            
        visited.add(current_id)
        
        # Find the current identity
        current = None
        for identity in identities:
            if identity.id == current_id:
                current = identity
                break
                
        if not current:
            return None
            
        # Calculate spiral coordinates
        coordinates = _calculate_spiral_coordinates(current.time_point)
        
        # Organize relationships by type
        parents = []
        children = []
        siblings = []
        spouses = []
        other_relations = []
        
        # Find all direct relationships
        for rel in current.relationships:
            rel_type = rel.relation_type.lower()
            
            # Skip if we've already visited this identity
            if rel.related_id in visited:
                continue
                
            # Recursively build the related person's node if within depth
            if current_depth < depth - 1:
                related_node = build_lineage_node(rel.related_id, current_depth + 1, visited)
            else:
                # Just get basic information without recursion
                related_person = None
                for identity in identities:
                    if identity.id == rel.related_id:
                        related_person = identity
                        break
                        
                if not related_person:
                    continue
                    
                related_coords = _calculate_spiral_coordinates(related_person.time_point)
                related_node = {
                    "id": related_person.id,
                    "name": related_person.name,
                    "time_point": related_person.time_point,
                    "coordinates": related_coords,
                    "relationship": rel.relation_type,
                    "relationship_details": {
                        "strength": getattr(rel, "strength", 1.0),
                        "established_date": getattr(rel, "established_date", None),
                        "description": rel.description
                    }
                }
            
            if not related_node:
                continue
                
            relationship_data = {
                "relationship": rel.relation_type,
                "person": related_node
            }
            
            # Categorize the relationship
            if rel_type in ["parent", "father", "mother"]:
                parents.append(relationship_data)
            elif rel_type in ["child", "son", "daughter"]:
                children.append(relationship_data)
            elif rel_type in ["sibling", "brother", "sister"]:
                siblings.append(relationship_data)
            elif rel_type in ["spouse", "husband", "wife"]:
                spouses.append(relationship_data)
            else:
                other_relations.append(relationship_data)
                
        # Find siblings by common parents
        if current_depth < depth - 1:
            # Check for siblings who share parents with the current identity
            for identity in identities:
                if identity.id == current_id or identity.id in visited:
                    continue
                    
                # Get parents of this potential sibling
                sibling_parents = []
                for rel in identity.relationships:
                    if rel.relation_type.lower() in ["parent", "father", "mother"]:
                        sibling_parents.append(rel.related_id)
                        
                # Get parents of the current identity
                current_parents = []
                for rel in current.relationships:
                    if rel.relation_type.lower() in ["parent", "father", "mother"]:
                        current_parents.append(rel.related_id)
                        
                # Find common parents
                common_parents = set(sibling_parents).intersection(set(current_parents))
                if common_parents:
                    # This is a sibling by shared parents
                    if identity.id not in visited:
                        sibling_node = build_lineage_node(identity.id, current_depth + 1, visited)
                        if sibling_node:
                            siblings.append({
                                "relationship": "sibling",
                                "common_parents": len(common_parents),
                                "person": sibling_node
                            })
        
        return {
            "id": current.id,
            "name": current.name,
            "time_point": current.time_point,
            "coordinates": coordinates,
            "parents": parents,
            "children": children,
            "siblings": siblings,
            "spouses": spouses,
            "other_relations": other_relations
        }
    
    # Build the lineage tree starting from the found identity
    lineage_tree = build_lineage_node(found_identity.id)
    
    # Return the result
    return {
        "identity": found_identity.dict(),
        "lineage_tree": lineage_tree
    }

@router.delete("/identity/{identity_id}", response_model=Dict[str, str])
def delete_identity(identity_id: str = Path(..., description="The ID of the identity to delete")) -> Dict[str, str]:
    """Delete a personal identity"""
    identities = _get_identities_storage()
    
    # Filter out the identity to delete
    original_length = len(identities)
    identities = [identity for identity in identities if identity.id != identity_id]
    
    if len(identities) == original_length:
        raise HTTPException(status_code=404, detail=f"Identity with ID {identity_id} not found")
    
    _save_identities(identities)
    
    return {"status": "success", "message": f"Identity with ID {identity_id} has been deleted"}
