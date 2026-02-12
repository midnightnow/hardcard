from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union, Literal


router = APIRouter()


# Request models
class ParameterConfig(BaseModel):
    metric: List[int] = Field(..., description="Signature metric, e.g. [1, 1, 1] for 3D Euclidean")
    basis_names: List[str] = Field(..., description="Names for the basis vectors, e.g. ['e1', 'e2', 'e3']")


class MultivectorConfig(BaseModel):
    mv_value: Dict[str, Any] = Field(..., description="Multivector representation")


class EquationConfig(BaseModel):
    coefficients: Dict[str, Any] = Field(..., description="Equation coefficients")
    variables: List[str] = Field(..., description="Variables in the equation")


class SignatureConfigRequest(BaseModel):
    config_type: Literal["parameters", "multivector", "equation_coeffs"] = Field(..., 
                                                                description="Type of mathematical signature configuration")
    details: Union[ParameterConfig, MultivectorConfig, EquationConfig, Dict[str, Any]] = Field(..., 
                                                                 description="Configuration details")


# Response models
class SignatureResponse(BaseModel):
    config_type: str
    signature: Dict[str, Any]
    status: str = "success"
    message: str = "Signature configured successfully"


@router.post("/configure-signature")
def configure_mathematical_signature(request: SignatureConfigRequest) -> SignatureResponse:
    """
    Configure a mathematical signature based on different configuration types.
    
    This endpoint allows creating mathematical signatures for hardcard representations
    using different approaches: parameter-based, multivector-based, or equation-based.
    
    The mathematical signature is a fundamental part of the hardcard's cryptographic identity.
    """
    try:
        signature_data = {}
        config_type = request.config_type
        details = request.details
        
        print(f"Received request - config_type: {config_type}, details type: {type(details)}")
        print(f"Details content: {details}")

        if config_type == 'parameters':
            # Process parameter-based configuration
            if isinstance(details, dict):
                # Handle dict input
                if not all(key in details for key in ['metric', 'basis_names']):
                    raise HTTPException(status_code=400, detail="Parameters configuration requires metric and basis_names")
                metric = details.get("metric", [])
                basis_names = details.get("basis_names", [])
            else:
                # Handle Pydantic model input
                metric = details.metric if hasattr(details, "metric") else []
                basis_names = details.basis_names if hasattr(details, "basis_names") else []
                
                if not metric or not basis_names:
                    raise HTTPException(status_code=400, detail="Parameters configuration requires metric and basis_names")
            
            signature_data = {
                "metric": metric,
                "basis_names": basis_names,
                "dimensions": len(metric),
                "space_type": "Euclidean" if all(m == 1 for m in metric) else "Mixed"
            }
            
        elif config_type == 'multivector':
            # Process multivector-based configuration
            if isinstance(details, dict):
                # Handle dict input
                if 'mv_value' not in details:
                    raise HTTPException(status_code=400, detail="Multivector configuration requires mv_value")
                mv_value = details.get("mv_value", {})
            else:
                # Handle Pydantic model input
                mv_value = details.mv_value if hasattr(details, "mv_value") else {}
                
                if not mv_value:
                    raise HTTPException(status_code=400, detail="Multivector configuration requires mv_value")
                    
            signature_data = {
                "multivector": mv_value,
                "grade": len(mv_value),
                "norm": sum(abs(val) for val in mv_value.values()) if isinstance(mv_value, dict) else 0,
                "representation_type": "algebraic"
            }
            
        elif config_type == 'equation_coeffs':
            # Process equation-based configuration
            if isinstance(details, dict):
                # Handle dict input
                if 'coefficients' not in details or 'variables' not in details:
                    raise HTTPException(status_code=400, detail="Equation configuration requires coefficients and variables")
                
                coefficients = details.get("coefficients", {})
                variables = details.get("variables", [])
                degree = details.get("degree", 2)
            else:
                # Handle Pydantic model input
                coefficients = details.coefficients if hasattr(details, "coefficients") else {}
                variables = details.variables if hasattr(details, "variables") else []
                degree = details.degree if hasattr(details, "degree") else 2
                
                if not coefficients or not variables:
                    raise HTTPException(status_code=400, detail="Equation configuration requires coefficients and variables")
            
            signature_data = {
                "coefficients": coefficients,
                "variables": variables,
                "degree": degree,
                "equation_type": "polynomial" if all(isinstance(k, str) and "^" in k for k in coefficients.keys()) else "general"
            }
            
        else:
            raise HTTPException(status_code=400, detail=f"Invalid configuration type: {config_type}")
            
        return SignatureResponse(
            config_type=config_type,
            signature=signature_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure mathematical signature: {str(e)}")


@router.get("/supported-configurations")
def get_supported_configurations() -> Dict[str, Any]:
    """
    Get information about supported mathematical signature configurations.
    
    Returns details about the different types of configurations that can be used
    to create mathematical signatures for hardcards.
    """
    return {
        "supported_types": [
            {
                "type": "parameters",
                "description": "Define a signature using metric and basis names",
                "example": {
                    "metric": [1, 1, 1], 
                    "basis_names": ["e1", "e2", "e3"]
                }
            },
            {
                "type": "multivector",
                "description": "Define a signature using a specific multivector representation",
                "example": {
                    "mv_value": {
                        "scalar": 1.0,
                        "e1": 0.5,
                        "e2": 0.5,
                        "e12": 0.25
                    }
                }
            },
            {
                "type": "equation_coeffs",
                "description": "Define a signature using equation coefficients",
                "example": {
                    "coefficients": {
                        "x^2": 1.0,
                        "y^2": 1.0,
                        "z^2": 1.0,
                        "xy": 0.0
                    },
                    "variables": ["x", "y", "z"],
                    "degree": 2
                }
            }
        ],
        "documentation": "Mathematical signatures provide a cryptographic identity for hardcards based on geometric algebra principles."
    }
