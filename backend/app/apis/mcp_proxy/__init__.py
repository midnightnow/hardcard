# src/app/apis/mcp_proxy/__init__.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import httpx
from starlette.responses import StreamingResponse

from app.auth import AuthorizedUser
from app.libs.firebase_admin_service import get_firestore_client
from google.cloud import firestore

router = APIRouter(prefix="/api/mcp_proxy", tags=["MCP Proxy"])

class ToolCallArgs(BaseModel):
    tool: str = Field(..., description="The name of the tool to execute.")
    args: Dict[str, Any] = Field(..., description="The arguments for the tool.")

async def stream_and_log(client, request, log_data, db):
    """Helper to stream response and handle logging."""
    try:
        upstream_response = await client.send(request, stream=True)
        log_data["status_code"] = upstream_response.status_code
        await db.collection("proxy_logs").add(log_data)

        return StreamingResponse(
            upstream_response.aiter_bytes(),
            status_code=upstream_response.status_code,
            headers=dict(upstream_response.headers),
        )
    except httpx.RequestError as e:
        log_data["status_code"] = 500
        log_data["error"] = str(e)
        await db.collection("proxy_logs").add(log_data)
        raise HTTPException(status_code=502, detail=f"Failed to connect to target: {e}") from e

@router.post("/{connection_id}/tool-call", tags=["stream"])
async def proxy_tool_call(
    connection_id: str,
    payload: ToolCallArgs,
    user: AuthorizedUser
):
    """
    Proxies a tool call to a remote Databutton project using a stored MCP connection.
    """
    db = get_firestore_client()
    if not db:
        raise HTTPException(status_code=500, detail="Firestore client not available.")

    # 1. Fetch connection and verify ownership
    conn_ref = db.collection("mcp_connections").document(connection_id)
    conn_doc = await conn_ref.get()

    if not conn_doc.exists:
        raise HTTPException(status_code=404, detail="Connection not found.")

    connection_data = conn_doc.to_dict()
    if connection_data.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    target_project_url = connection_data.get("project_url")
    secret_token = connection_data.get("secret_token")

    if not target_project_url or not secret_token:
        raise HTTPException(status_code=400, detail="Connection not configured.")

    # 2. Prepare and forward the request
    target_api_url = f"{target_project_url.rstrip('/')}/api/dev-helper-proxy"
    headers = {
        "Authorization": f"Bearer {secret_token}",
        "Content-Type": "application/json",
        "X-DevHelper-UID": user.user_id,
    }

    log_entry_base = {
        "user_id": user.user_id,
        "connection_id": connection_id,
        "target_project_url": target_project_url,
        "tool": payload.tool,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }

    # 3. Stream the response
    async with httpx.AsyncClient() as client:
        upstream_request = client.build_request(
            method="POST",
            url=target_api_url,
            json={"tool": payload.tool, "args": payload.args},
            headers=headers,
            timeout=300.0,
        )
        return await stream_and_log(client, upstream_request, log_entry_base, db)
