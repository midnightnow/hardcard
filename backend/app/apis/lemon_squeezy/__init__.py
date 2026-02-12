from fastapi import APIRouter, Request, HTTPException
import databutton as db
import requests

router = APIRouter()

import hashlib
import hmac
from fastapi import Request, HTTPException

@router.post("/webhook")
async def lemon_squeezy_webhook(request: Request):
    """Handle Lemon Squeezy webhooks"""
    secret = db.secrets.get("LEMON_SIGNING_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Signing secret not configured")

    signature = request.headers.get("X-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing X-Signature header")

    raw_body = await request.body()
    try:
        digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute signature: {e}")

    if not hmac.compare_digest(digest, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process the webhook payload
    payload = await request.json()
    event_name = payload.get("meta", {}).get("event_name")
    
    # Generate a unique key for the event
    event_id = payload.get("meta", {}).get("custom_data", {}).get("event_id", f"{event_name}_{payload.get('data', {}).get('id', '')}")
    storage_key = f"lemonsqueezy_event_{event_id}"
    
    # Store the event
    db.storage.json.put(storage_key, payload)
    
    print(f"Received and stored Lemon Squeezy event: {event_name}")
    
    return {"status": "success"}

@router.get("/events")
async def get_events():
    """Get all stored Lemon Squeezy events"""
    event_files = db.storage.json.list()
    events = []
    for file in event_files:
        if file.name.startswith("lemonsqueezy_event_"):
            events.append(db.storage.json.get(file.name))
    return events

@router.get("/products")
async def get_products():
    """Get all products from Lemon Squeezy"""
    api_key = db.secrets.get("LEMON_SQUEEZY_API_KEY")
    store_id = db.secrets.get("LEMON_SQUEEZY_STORE_ID")
    
    if not api_key or not store_id:
        raise HTTPException(status_code=400, detail="Lemon Squeezy API key or Store ID not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json"
    }
    
    response = requests.get(f"https://api.lemonsqueezy.com/v1/products?filter[store_id]={store_id}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)