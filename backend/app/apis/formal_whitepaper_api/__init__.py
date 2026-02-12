from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, Response
import databutton as db
from pydantic import BaseModel
from typing import Literal, Optional
import io

# Compiler script co-located with this API
from app.apis.compiler_logic import (
    compile_whitepaper_markdown,
    convert_markdown_to_latex,
)

router = APIRouter(prefix="/formal-whitepaper")

# --- Helper Functions & Models ---

def sanitize_storage_key(key: str) -> str:
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

class GenerateResponse(BaseModel):
    success: bool
    message: str
    markdown_key: Optional[str] = None
    latex_key: Optional[str] = None
    error: Optional[str] = None

# --- API Endpoints ---

@router.post("/generate", response_model=GenerateResponse)
def generate_whitepaper_endpoint():
    """
    Generates the formal methodology whitepaper in Markdown and LaTeX formats,
    and stores them in Databutton text storage.
    """
    try:
        print("Starting whitepaper generation...")
        markdown_content = compile_whitepaper_markdown()
        print("Markdown compilation complete.")
        latex_content = convert_markdown_to_latex(markdown_content)
        print("LaTeX conversion complete.")

        if "% PANDOC CONVERSION FAILED" in latex_content:
            print(f"Pandoc conversion failed. LaTeX content: {latex_content[:500]}") # Log part of the error
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to convert Markdown to LaTeX. {latex_content}"
            )

        md_filename = "hardcard_formal_methodology.md"
        tex_filename = "hardcard_formal_methodology.tex"
        
        sanitized_md_key = sanitize_storage_key(md_filename)
        sanitized_tex_key = sanitize_storage_key(tex_filename)

        db.storage.text.put(sanitized_md_key, markdown_content)
        print(f"Markdown content stored as {sanitized_md_key}")
        db.storage.text.put(sanitized_tex_key, latex_content)
        print(f"LaTeX content stored as {sanitized_tex_key}")

        return GenerateResponse(
            success=True,
            message="Whitepaper generated and stored successfully in Markdown and LaTeX formats.",
            markdown_key=sanitized_md_key,
            latex_key=sanitized_tex_key
        )
    except HTTPException as http_exc:
        # Re-raise HTTPException to ensure FastAPI handles it correctly
        raise http_exc
    except Exception as e:
        print(f"Error during whitepaper generation: {str(e)}")
        # Log the full traceback for internal debugging if possible
        import traceback
        traceback.print_exc()
        return GenerateResponse(
            success=False,
            message="An unexpected error occurred during whitepaper generation.",
            error=str(e)
        )

@router.get("/download/{format_type}/{filename}")
async def download_whitepaper(
    format_type: Literal["markdown", "latex"],
    filename: str # Though filename is passed, we use fixed keys for now
):
    """
    Downloads the generated whitepaper in the specified format (Markdown or LaTeX).
    The filename parameter is for conventional URL structure but current implementation uses fixed keys.
    """
    actual_filename = ""
    storage_key = ""
    media_type = ""

    if format_type == "markdown":
        actual_filename = "hardcard_formal_methodology.md"
        storage_key = sanitize_storage_key(actual_filename)
        media_type = "text/markdown; charset=utf-8"
    elif format_type == "latex":
        actual_filename = "hardcard_formal_methodology.tex"
        storage_key = sanitize_storage_key(actual_filename)
        media_type = "application/x-tex; charset=utf-8"
    else:
        raise HTTPException(status_code=400, detail="Invalid format_type. Must be 'markdown' or 'latex'.")

    try:
        print(f"Attempting to retrieve {storage_key} for download.")
        file_content = db.storage.text.get(storage_key)
        if not file_content:
            print(f"File not found in storage: {storage_key}")
            raise HTTPException(status_code=404, detail=f"{format_type.capitalize()} whitepaper not found in storage with key {storage_key}. Please generate it first.")
        
        print(f"Successfully retrieved {storage_key}. Preparing download.")
        return Response(
            content=file_content,
            media_type=media_type,
            headers={ "Content-Disposition": f"attachment; filename={actual_filename}" }
        )

    except FileNotFoundError:
        print(f"FileNotFoundError: {storage_key} not found in db.storage.")
        raise HTTPException(status_code=404, detail=f"{format_type.capitalize()} whitepaper not found. Please generate it first.")
    except Exception as e:
        print(f"Error during whitepaper download for key {storage_key}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Could not retrieve {format_type} whitepaper. Error: {str(e)}")

# Example usage (can be tested via Databutton's endpoint testing or by calling from frontend)
# To generate: POST to /formal-whitepaper/generate
# To download Markdown: GET /formal-whitepaper/download/markdown/hardcard_formal_methodology.md
# To download LaTeX: GET /formal-whitepaper/download/latex/hardcard_formal_methodology.tex
