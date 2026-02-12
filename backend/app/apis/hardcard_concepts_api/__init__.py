from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union

router = APIRouter()

class HardcardConcept(BaseModel):
    name: str
    description: str
    core_function: str
    key_principles: List[str]

@router.get("/hardcard-concept")
def get_hardcard_concept() -> HardcardConcept:
    """
    Returns the core concept of the Hardcard.
    """
    return HardcardConcept(
        name="Hardcard",
        description="A physical artifact that serves as a key to a user's digital legacy, blending top-tier security with a tangible, generational heirloom.",
        core_function="Authentication and access to the Legacy Vault.",
        key_principles=[
            "Physicality: A tangible object that can be held and passed down.",
            "Security: Uncompromising security, resistant to digital and physical threats.",
            "Longevity: Designed to last for generations, with future-proof technology.",
            "Simplicity: Easy to use for authentication, abstracting away the complexity of the underlying technology.",
        ],
    )
