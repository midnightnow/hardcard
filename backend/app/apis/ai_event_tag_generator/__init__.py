from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import databutton as db
from openai import OpenAI

router = APIRouter()

# --- Pydantic Models ---

class GenerateExampleEventTagRequest(BaseModel):
    event_type: Optional[str] = Field(None, description="The type of event to generate an example for (e.g., 'Birth', 'Asset Acquisition').")

class GeneratedEventTagData(BaseModel):
    name: Optional[str] = Field(None, description="Example name for the event tag.")
    event_type: Optional[str] = Field(None, description="Example event type.")
    description: Optional[str] = Field(None, description="Example description for the event.")
    actor: Optional[str] = Field(None, description="Example actor involved in the event.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Example metadata related to the event.")
    # Add other fields from TagForm.tsx as needed, e.g., latitude, longitude, referenceIds
    # For now, focusing on text-based fields that AI can generate well.
    # timestamp will likely be set by the form's default or user, not AI example.

class GenerateExampleEventTagResponse(BaseModel):
    generated_data: GeneratedEventTagData

import json

# --- OpenAI client initialization ---
try:
    client = OpenAI(api_key=db.secrets.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    client = None

# --- API Endpoint ---

@router.post("/generate-example-event-tag", response_model=GenerateExampleEventTagResponse)
async def generate_example_event_tag_endpoint(request: GenerateExampleEventTagRequest):
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized. Check API key.")

    base_prompt = (
        "You are an AI assistant helping to create example data for an event tagging system. "
        "Generate a realistic and illustrative example for an event tag. "
        "The output MUST be a JSON object with the exact following keys: "
        "'name' (string), 'event_type' (string, use the provided one or a plausible one if none provided), "
        "'description' (string, 2-3 sentences), 'actor' (string, e.g., person, system, or role), "
        "and 'metadata' (a JSON object containing 2-3 relevant key-value pairs)."
    )

    if request.event_type:
        prompt = (
            f"{base_prompt} The event type for this example is '{request.event_type}'. "
            "Please ensure the generated 'name', 'description', 'actor', and 'metadata' are highly relevant "
            f"and specific to the '{request.event_type}' event type. For example, if eventType is 'Birth', "
            "the name could be 'Birth of [Fictional Name]', description related to birth details, "
            "actor could be 'Midwife [Fictional Name]' or 'City General Hospital', "
            "and metadata could include 'birth_weight_kg', 'time_of_birth_utc'."
        )
    else:
        prompt = (
            f"{base_prompt} Since no specific event type is provided, generate a generic but plausible example. "
            "This could relate to a common business or personal lifecycle event like a meeting, a project milestone, "
            "a document creation, or a system update. Ensure event_type field is filled with a plausible type."
        )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please generate the example event tag data as a JSON object."}
            ],
            response_format={"type": "json_object"}
        )
        
        ai_response_content = completion.choices[0].message.content
        if not ai_response_content:
            raise HTTPException(status_code=502, detail="OpenAI returned an empty response.")

        generated_json = json.loads(ai_response_content)
        
        # Ensure all expected keys are present, even if None, to match Pydantic model
        # Pydantic will use defaults or None for missing fields if they are Optional
        # but good to be explicit with what AI is expected to return.
        event_data = GeneratedEventTagData(
            name=generated_json.get("name"),
            event_type=generated_json.get("event_type", request.event_type), # Fallback to request if AI misses it
            description=generated_json.get("description"),
            actor=generated_json.get("actor"),
            metadata=generated_json.get("metadata")
        )

        return GenerateExampleEventTagResponse(generated_data=event_data)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from OpenAI: {ai_response_content}")
        raise HTTPException(status_code=502, detail="Failed to parse AI-generated JSON data.") from e
    except Exception as e:
        print(f"Error calling OpenAI or processing response: {e}")
        # Log the actual error for debugging
        # Consider more specific error handling for different OpenAI API errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred with the AI service: {str(e)}") from e

