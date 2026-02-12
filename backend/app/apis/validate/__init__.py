import json
import jsonschema
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Tuple, Optional
# Import the schema from event_tag_schema_json module instead
# # from app.apis.event_tag_schema_json import EVENT_TAG_SCHEMA, BIRTH_EVENT_EXAMPLE, MARRIAGE_EVENT_EXAMPLE, DEATH_EVENT_EXAMPLE, COMPLETE_EVENT_TAG_EXAMPLE

# Create router required for APIs
router = APIRouter()

# Define Pydantic models for request and response
class EventTagValidationRequest(BaseModel):
    """Request model for event tag validation."""
    tag_data: Dict[str, Any]

class ValidationError(BaseModel):
    """Model for validation error details."""
    path: str
    message: str

class EventTagValidationResponse(BaseModel):
    """Response model for event tag validation."""
    valid: bool
    errors: Optional[List[ValidationError]] = None

def validate_event_tag(event_tag_data) -> Tuple[bool, List[ValidationError]]:
    """
    Validate an event tag against the JSON Schema.
    
    Args:
        event_tag_data (dict): The event tag data to validate.
        
    Returns:
        Tuple[bool, List[ValidationError]]: A tuple containing:
            - bool: True if valid, False otherwise
            - List[ValidationError]: List of validation errors if any
    """
    errors = []
    
    try:
        jsonschema.validate(instance=event_tag_data, schema=EVENT_TAG_SCHEMA)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        # Extract detailed error information
        error_path = "/".join([str(p) for p in e.path]) if e.path else "root"
        error_message = e.message
        errors.append(ValidationError(path=error_path, message=error_message))
        
        # Check for specific validation issues to provide more helpful messages
        if "required" in error_message:
            field = error_message.split("'")[1] if "'" in error_message else "unknown"
            errors.append(ValidationError(
                path=field,
                message=f"Field '{field}' is required but was not provided"
            ))
        elif "is not of type" in error_message:
            errors.append(ValidationError(
                path=error_path,
                message=f"Type mismatch at {error_path}: {error_message}"
            ))
        elif "does not match" in error_message and "pattern" in error_message:
            errors.append(ValidationError(
                path=error_path,
                message=f"Invalid format at {error_path}: Value does not match the required pattern"
            ))
        elif "is not a multiple of" in error_message or "not less than" in error_message or "not greater than" in error_message:
            errors.append(ValidationError(
                path=error_path,
                message=f"Value constraint violation at {error_path}: {error_message}"
            ))
        
        return False, errors

def run_validation_tests():
    """
    Run validation tests on the example event tags.
    
    Returns:
        dict: Results of validation tests.
    """
    results = {}
    
    # Validate birth event
    try:
        is_valid, errors = validate_event_tag(BIRTH_EVENT_EXAMPLE)
        results["birth_event"] = {
            "valid": is_valid,
            "message": "Valid birth event schema" if is_valid else "Invalid birth event schema",
            "errors": [e.dict() for e in errors] if errors else []
        }
    except Exception as e:
        results["birth_event"] = {"valid": False, "message": str(e), "errors": [{"path": "root", "message": str(e)}]}
    
    # Validate marriage event
    try:
        is_valid, errors = validate_event_tag(MARRIAGE_EVENT_EXAMPLE)
        results["marriage_event"] = {
            "valid": is_valid,
            "message": "Valid marriage event schema" if is_valid else "Invalid marriage event schema",
            "errors": [e.dict() for e in errors] if errors else []
        }
    except Exception as e:
        results["marriage_event"] = {"valid": False, "message": str(e), "errors": [{"path": "root", "message": str(e)}]}
    
    # Validate death event
    try:
        is_valid, errors = validate_event_tag(DEATH_EVENT_EXAMPLE)
        results["death_event"] = {
            "valid": is_valid,
            "message": "Valid death event schema" if is_valid else "Invalid death event schema",
            "errors": [e.dict() for e in errors] if errors else []
        }
    except Exception as e:
        results["death_event"] = {"valid": False, "message": str(e), "errors": [{"path": "root", "message": str(e)}]}
    
    return results

# Create a modified event example with missing required fields for testing
def create_invalid_event_example():
    """Create an invalid event example with missing required fields."""
    invalid_example = BIRTH_EVENT_EXAMPLE.copy()
    # Remove required fields
    if "identity_id" in invalid_example:
        del invalid_example["identity_id"]
    return invalid_example

# Create an event example with incorrect field types
def create_type_error_example():
    """Create an event example with incorrect field types."""
    invalid_example = BIRTH_EVENT_EXAMPLE.copy()
    # Set incorrect type for timestamp (should be string in ISO format)
    invalid_example["timestamp"] = 12345
    return invalid_example

@router.post("/validate-event-tag", response_model=EventTagValidationResponse)
async def validate_event_tag_endpoint(request: EventTagValidationRequest):
    """
    Validate an event tag against the JSON Schema.
    
    This endpoint performs validation of event tag data against the Hardcard
    EventTag JSON Schema. It provides detailed error messages for validation failures.
    """
    is_valid, errors = validate_event_tag(request.tag_data)
    return EventTagValidationResponse(valid=is_valid, errors=errors)

@router.get("/test-validation", response_model=Dict[str, Any])
async def test_validation_endpoint():
    """
    Run validation tests on example event tags.
    
    This endpoint tests validation against known-good examples and intentionally
    invalid examples to demonstrate validation behavior.
    """
    results = run_validation_tests()
    
    # Add tests with intentionally invalid examples
    try:
        invalid_example = create_invalid_event_example()
        is_valid, errors = validate_event_tag(invalid_example)
        results["missing_required_field"] = {
            "valid": is_valid,
            "message": "Example with missing required field",
            "errors": [e.dict() for e in errors] if errors else []
        }
    except Exception as e:
        results["missing_required_field"] = {"valid": False, "message": str(e), "errors": [{"path": "root", "message": str(e)}]}
    
    try:
        type_error_example = create_type_error_example()
        is_valid, errors = validate_event_tag(type_error_example)
        results["type_error"] = {
            "valid": is_valid,
            "message": "Example with incorrect field type",
            "errors": [e.dict() for e in errors] if errors else []
        }
    except Exception as e:
        results["type_error"] = {"valid": False, "message": str(e), "errors": [{"path": "root", "message": str(e)}]}
    
    return results

if __name__ == "__main__":
    results = run_validation_tests()
    print(json.dumps(results, indent=2))