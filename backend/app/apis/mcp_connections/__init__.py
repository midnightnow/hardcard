
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
import databutton as db
from app.auth import AuthorizedUser
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.query import Query
import json
from slugify import slugify

# --- App Initialization ---
# Initialize Firebase Admin SDK
db_firestore = None
try:
    service_account_str = db.secrets.get("FIREBASE_SERVICE_ACCOUNT_KEY")
    if service_account_str:
        service_account_info = json.loads(service_account_str)
        
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        
        db_firestore = firestore.client()
except Exception as e:
    print(f"Failed to initialize Firebase: {e}")

# --- API Router ---
router = APIRouter(prefix="/mcp", tags=["MCP"])


# --- Pydantic Models ---
class ConnectionRequest(BaseModel):
    name: str
    url: HttpUrl
    api_key: str

class ConnectionResponse(BaseModel):
    id: str
    name: str
    url: HttpUrl
    createdAt: str


# --- API Endpoints ---
@router.post("/connections", response_model=ConnectionResponse)
async def create_connection(
    connection_data: ConnectionRequest,
    user: AuthorizedUser,
):
    """
    Creates a new MCP connection.
    - Securely stores the API key in Databutton secrets.
    - Saves the public connection details (name, url) to Firestore.
    """
    if not db_firestore:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    # Sanitize name for use in secret key
    slugified_name = slugify(connection_data.name)
    secret_key = f"MCP_KEY_{slugified_name.upper().replace('-', '_')}"
    
    # Store the API key in secrets
    db.secrets.put(secret_key, connection_data.api_key)
    
    # Prepare data for Firestore
    firestore_data = {
        "name": connection_data.name,
        "url": str(connection_data.url),
        "createdAt": firestore.SERVER_TIMESTAMP,
        "createdBy": user.sub, # User's Firebase UID
    }
    
    # Add the new connection to the user's 'mcp_connections' subcollection
    update_time, doc_ref = db_firestore.collection("users", user.sub, "mcp_connections").add(firestore_data)
    
    return ConnectionResponse(
        id=doc_ref.id,
        name=connection_data.name,
        url=connection_data.url,
        createdAt=update_time.isoformat()
    )

@router.get("/connections", response_model=list[ConnectionResponse])
async def get_mcp_connections(
    user: AuthorizedUser,
):
    """
    Retrieves all MCP connections for the authenticated user.
    """
    if not db_firestore:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    connections_ref = (
        db_firestore.collection("users", user.sub, "mcp_connections")
        .order_by("createdAt", direction=firestore.Query.DESCENDING)
        .stream()
    )
    connections = []
    for conn in connections_ref:
        conn_data = conn.to_dict()
        created_at = conn_data.get("createdAt")
        connections.append(ConnectionResponse(
            id=conn.id,
            name=conn_data.get("name"),
            url=conn_data.get("url"),
            createdAt=created_at.isoformat() if created_at else ""
        ))
    return connections


@router.put("/connections/{connection_id}", response_model=ConnectionResponse)
async def update_connection(
    connection_id: str,
    connection_data: ConnectionRequest,
    user: AuthorizedUser,
):
    """
    Updates an MCP connection.
    - Updates the connection details in Firestore.
    - Updates the associated API key in Databutton secrets.
    """
    if not db_firestore:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    # Get the connection from Firestore
    doc_ref = db_firestore.collection("mcp_connections").document(connection_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Connection not found")

    existing_connection_data = doc.to_dict()

    # Check if the user is authorized to update the connection
    if existing_connection_data.get("createdBy") != user.sub:
        raise HTTPException(status_code=403, detail="Not authorized to update this connection")

    # Sanitize name for use in secret key
    slugified_name = slugify(connection_data.name)
    secret_key = f"MCP_KEY_{slugified_name.upper().replace('-', '_')}"

    # Update the API key in secrets
    db.secrets.put(secret_key, connection_data.api_key)

    # Prepare data for Firestore
    firestore_data = {
        "name": connection_data.name,
        "url": str(connection_data.url),
    }

    # Update the connection in Firestore
    doc_ref.update(firestore_data)

    return ConnectionResponse(
        id=connection_id,
        name=connection_data.name,
        url=connection_data.url,
    )

@router.post("/connections/{connection_id}/test", status_code=200)
async def test_connection(
    connection_id: str,
    user: AuthorizedUser,
):
    """
    Tests an MCP connection.
    - Fetches the connection's URL and API key.
    - Sends a test request to the connection's /mcp/config endpoint.
    - Returns a success or failure message.
    """
    if not db_firestore:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    # Get the connection from Firestore
    doc_ref = db_firestore.collection("mcp_connections").document(connection_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Connection not found")

    connection_data = doc.to_dict()

    # Check if the user is authorized to test the connection
    if connection_data.get("createdBy") != user.sub:
        raise HTTPException(status_code=403, detail="Not authorized to test this connection")

    # Sanitize name for use in secret key
    slugified_name = slugify(connection_data.get("name"))
    secret_key = f"MCP_KEY_{slugified_name.upper().replace('-', '_')}"

    # Get the API key from secrets
    api_key = db.secrets.get(secret_key)

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Make a test request to the connection's /mcp/config endpoint
    try:
        import requests
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{connection_data.get('url')}/mcp/config", headers=headers)
        response.raise_for_status()
        return {"message": "Connection test successful"}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Connection test failed: {e}")

@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: str,
    user: AuthorizedUser,
):
    """
    Deletes an MCP connection.
    - Deletes the connection details from Firestore.
    - Deletes the associated API key from Databutton secrets.
    """
    if not db_firestore:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    # Get the connection from Firestore
    doc_ref = db_firestore.collection("mcp_connections").document(connection_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Connection not found")

    connection_data = doc.to_dict()

    # Check if the user is authorized to delete the connection
    if connection_data.get("createdBy") != user.sub:
        raise HTTPException(status_code=403, detail="Not authorized to delete this connection")

    # Sanitize name for use in secret key
    slugified_name = slugify(connection_data.get("name"))
    secret_key = f"MCP_KEY_{slugified_name.upper().replace('-', '_')}"

    # Delete the API key from secrets
    db.secrets.delete(secret_key)

    # Delete the connection from Firestore
    doc_ref.delete()

    return
