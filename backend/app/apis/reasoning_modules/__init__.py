# src/app/apis/reasoning_modules/__init__.py
from fastapi import APIRouter
import re # Added for regex parsing

router = APIRouter() # Added router

from pydantic import BaseModel
from typing import List, Dict

class LLMCodePlannerInput(BaseModel):
    code_snippet: str
    modification_request: str

class LLMCodePlannerOutput(BaseModel):
    plan: List[str]
    estimated_complexity: str

def generate_code_modification_plan(input_data: LLMCodePlannerInput) -> LLMCodePlannerOutput:
    """
    Parses a simple numbered or bulleted list from modification_request to generate a plan.
    If no list is found, returns a default plan.
    """
    print(f"Attempting to parse plan from: {input_data.modification_request}")
    parsed_plan = []
    
    if input_data.modification_request:
        # Regex to find lines starting with number+dot+space, or dash/asterisk+space
        # Captures the text after the marker
        lines = input_data.modification_request.strip().split('\n')
        for line in lines:
            line = line.strip()
            match = re.match(r"^(?:\d+\.|[-*])\s+(.+)", line)
            if match:
                parsed_plan.append(match.group(1).strip())

    if parsed_plan:
        print(f"Successfully parsed plan: {parsed_plan}")
        return LLMCodePlannerOutput(
            plan=parsed_plan,
            estimated_complexity="Parsed from request"
        )
    else:
        print("No specific plan parsed, returning default fallback plan.")
        # Default fallback plan if parsing fails or request is empty
        return LLMCodePlannerOutput(
            plan=[
                "Default Step 1: Review the initial code snippet (if any).",
                "Default Step 2: Clarify the overall objective.",
                "Default Step 3: Outline implementation approach."
            ],
            estimated_complexity="Low (Default Plan)"
        )

# Add other reasoning modules here as needed
