from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
import firebase_admin
from firebase_admin import credentials, firestore
import json
import databutton as db

def get_firestore_client():
    """Initializes and returns a Firestore client."""
    try:
        firebase_admin.get_app()
    except ValueError:
        service_account_info = json.loads(db.secrets.get("FIREBASE_SERVICE_ACCOUNT"))
        creds = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(creds)
    return firestore.client()

router = APIRouter(prefix="/actors", tags=["Actor Model"])

class ActorState(BaseModel):
    state: Dict

@router.post("/{actor_id}")
async def set_actor_state(actor_id: str, state: ActorState):
    db = get_firestore_client()
    db.collection("actors").document(actor_id).set(state.dict())
    return {"status": "ok"}

@router.get("/{actor_id}", response_model=ActorState)
async def get_actor_state(actor_id: str):
    db = get_firestore_client()
    doc = db.collection("actors").document(actor_id).get()
    if doc.exists:
        return ActorState(**doc.to_dict())
    raise HTTPException(status_code=404, detail="Actor not found")