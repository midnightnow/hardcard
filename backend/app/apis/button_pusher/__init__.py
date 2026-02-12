import os
import fnmatch

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from app.auth import AuthorizedUser

router = APIRouter(prefix="/button_pusher", tags=["ButtonPusher"])

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

def list_files(pattern: str = "*") -> List[str]:
    """Lists files in the project workspace matching a pattern."""
    matches = []
    # Restrict to current working directory for security
    for root, dirnames, filenames in os.walk(os.getcwd()):
        for filename in fnmatch.filter(filenames, pattern):
            # Create a relative path from the current working directory
            relative_path = os.path.relpath(os.path.join(root, filename))
            matches.append(relative_path)
    return matches

def read_code(filepath: str) -> str:
    """Reads the content of a file securely."""
    # Security: Prevent directory traversal attacks
    base_dir = os.getcwd()
    abs_path = os.path.abspath(os.path.join(base_dir, filepath))

    if not abs_path.startswith(base_dir):
        raise HTTPException(status_code=400, detail="Invalid filepath")

    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

TOOL_DISPATCHER = {
    "list_files": list_files,
    "read_code": read_code,
}

@router.post("/execute")
async def execute_tool(
    request: ToolExecutionRequest,
    user: AuthorizedUser,
):
    """
    Executes a core Databutton tool securely.
    """
    tool_name = request.tool_name
    params = request.parameters

    if tool_name not in TOOL_DISPATCHER:
        raise HTTPException(status_code=400, detail=f"Tool '{tool_name}' not found.")

    tool_function = TOOL_DISPATCHER[tool_name]

    try:
        # Note: This uses keyword argument unpacking.
        # Ensure the 'parameters' dict keys match the function's argument names.
        result = tool_function(**params)
        return {"result": result}
    except TypeError as e:
        # This can happen if parameters don't match the function signature
        raise HTTPException(status_code=400, detail=f"Invalid parameters for tool '{tool_name}': {e}")
    except Exception as e:
        # Catch-all for other exceptions from the tool function itself
        # The tool functions are responsible for raising appropriate HTTPExceptions
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

