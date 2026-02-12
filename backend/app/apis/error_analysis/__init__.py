from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class SuggestFixRequest(BaseModel):
    message: str
    stack: Optional[str] = None

class SuggestFixResponse(BaseModel):
    insights: List[str]
    probable_causes: List[str]
    suggested_fixes: List[str]

@router.post("/analyze-errors-detailed")
def analyze_errors_detailed(request: SuggestFixRequest) -> SuggestFixResponse:
    """Analyze an error and suggest potential fixes using AI reasoning"""
    # This is a mock implementation - in a real system, this would call Claude or OpenAI
    
    # Default response for any error
    response = SuggestFixResponse(
        insights=[
            "This error suggests a problem with accessing an undefined value or method."
        ],
        probable_causes=[
            "The variable or object might be undefined when accessed",
            "An async operation might not have completed before the value was used",
            "There could be a typo in a variable or method name"
        ],
        suggested_fixes=[
            "Add conditional checks before accessing properties (e.g., `if (obj) { obj.method() }`)",
            "Use optional chaining where supported (e.g., `obj?.method?.())`)",
            "Ensure async data is loaded before rendering components that depend on it",
            "Check for typos in variable and method names"
        ]
    )
    
    # Customize response based on specific error messages
    if "Cannot read properties of undefined" in request.message or "TypeError: null is not an object" in request.message:
        response = SuggestFixResponse(
            insights=[
                "This is a null/undefined reference error - you're trying to access a property on an object that doesn't exist."
            ],
            probable_causes=[
                "The object you're accessing hasn't been initialized yet",
                "An API response might be empty or in an unexpected format",
                "A component prop might be missing or undefined"
            ],
            suggested_fixes=[
                "Add a null check before accessing the object",
                "Use optional chaining: obj?.prop instead of obj.prop",
                "Provide default values using || or ??",
                "Check that API responses match your expected format"
            ]
        )
    
    return response
