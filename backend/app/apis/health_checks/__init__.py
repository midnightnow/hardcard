# src/app/apis/health_checks/__init__.py
from fastapi import APIRouter, HTTPException, Depends
from google.cloud import firestore
import httpx

from app.libs.firebase_admin_service import get_firestore_client
from app.auth import AuthorizedUser # To protect the trigger endpoint if needed

router = APIRouter(prefix="/api/health_checks", tags=["Health Checks"])

async def run_single_check(db, connection: dict):
    """
    Runs a health check for a single MCP connection.
    """
    conn_id = connection.get("id")
    name = connection.get("name", "Unknown")
    project_url = connection.get("project_url")
    secret_token = connection.get("secret_token")
    user_id = connection.get("user_id")

    if not all([conn_id, project_url, secret_token, user_id]):
        print(f"Skipping connection {conn_id or name} due to missing configuration.")
        return {"status": "error", "reason": "incomplete_config"}

    # Use a simple, non-destructive tool call like `read_code` on the root.
    # We assume the target has a proxy endpoint ready to receive this.
    target_api_url = f"{project_url.rstrip('/')}/api/dev-helper-proxy"
    headers = {"Authorization": f"Bearer {secret_token}", "Content-Type": "application/json"}
    payload = {"tool": "read_code", "args": {"path": "/", "lines": 5}}

    status = "error"
    latency = -1
    status_code = -1
    reason = "unknown"

    try:
        async with httpx.AsyncClient() as client:
            start_time = firestore.SERVER_TIMESTAMP
            resp = await client.post(target_api_url, json=payload, headers=headers, timeout=30.0)
            end_time = firestore.SERVER_TIMESTAMP # Approx latency
            
            status_code = resp.status_code
            if resp.is_success:
                status = "success"
                reason = "ok"
            else:
                reason = f"http_{status_code}"
                print(f"Health check failed for {name} ({conn_id}) with status {status_code}: {resp.text}")

    except httpx.TimeoutException:
        reason = "timeout"
        print(f"Health check timed out for {name} ({conn_id}).")
    except httpx.RequestError as e:
        reason = "connection_error"
        print(f"Health check connection error for {name} ({conn_id}): {e}")
    except Exception as e:
        reason = "internal_error"
        print(f"An unexpected error occurred during health check for {name} ({conn_id}): {e}")

    # Log the result to the health_checks collection
    log_entry = {
        "connection_id": conn_id,
        "connection_name": name,
        "user_id": user_id,
        "status": status,
        "reason": reason,
        "http_status_code": status_code,
        # 'latency_ms': latency, # Latency calculation is tricky with server timestamps
        "checked_at": firestore.SERVER_TIMESTAMP,
    }
    await db.collection("health_checks").add(log_entry)
    return log_entry


@router.post("/trigger")
async def trigger_health_checks(user: AuthorizedUser):
    """
    Manually triggers a health check for all MCP connections.
    This endpoint would typically be called by a scheduler (e.g., Google Cloud Scheduler).
    """
    db = get_firestore_client()
    if not db:
        raise HTTPException(status_code=500, detail="Firestore client not available.")

    connections_ref = db.collection("mcp_connections")
    connections = connections_ref.stream()
    
    results = []
    print("Starting manual health check for all connections...")
    async for conn in connections:
        conn_data = conn.to_dict()
        conn_data["id"] = conn.id
        result = await run_single_check(db, conn_data)
        results.append(result)
    
    print(f"Health check complete. Processed {len(results)} connections.")
    return {"message": "Health checks triggered successfully.", "results": results}

# NOTE: For this to run on a schedule, you would configure a service like
# Google Cloud Scheduler to send a POST request to this /api/health_checks/trigger
# endpoint. The request would need to include a valid authentication token for a user.
# For simplicity, we are creating a manual trigger endpoint first.
