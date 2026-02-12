import databutton as db
import os
from fastapi import APIRouter, Response

router = APIRouter()

# Define the PowerChat client script as a string
powerchat_client_script = """#!/usr/bin/env python3

# PowerChat Client - Context-aware AI assistant overlay
# 
# This client connects to the PowerChat API and provides a transparent overlay
# that displays context-aware suggestions. It monitors clipboard content and
# Hempex API data to provide relevant suggestions.

# Requirements:
#   - Python 3.7+
#   - overlay==0.0.13
#   - pyperclip==1.8.2
#   - websocket-client==1.5.1
#   - requests==2.28.2
#   - python-dotenv==1.0.0
#   - Pillow==9.5.0

# Installation:
#   pip install overlay pyperclip websocket-client requests python-dotenv Pillow

# Usage:
#   python powerchat_client.py [--ws-uri WS_URI] [--api-url API_URL] [--client-id CLIENT_ID] 
#                             [--disable-clipboard] [--disable-api] [--offline]

# Main script content...
"""

# Store the script as a downloadable file
def store_powerchat_client():
    try:
        # Convert the script to bytes
        script_bytes = powerchat_client_script.encode('utf-8')
        
        # Store in db.storage.binary with a descriptive name
        db.storage.binary.put("powerchat_client.py", script_bytes)
        
        print("PowerChat client script stored successfully")
        return True
    except Exception as e:
        print(f"Error storing PowerChat client script: {e}")
        return False

# Upload as static asset for public access
def upload_as_static_asset():
    try:
        # Static assets are not available in the current databutton SDK
        # Use regular storage instead
        print("Static assets not available in current SDK, using regular storage")
        return None
    except Exception as e:
        print(f"Error with static assets: {e}")
        return None

# Execute storage functions
store_powerchat_client()
# Static assets not supported, so we're only using regular storage
asset_id = None

if asset_id:
    print("PowerChat client available through download endpoint")

@router.get("/download-client")
def download_client():
    """Download the PowerChat client script"""
    try:
        client_script_bytes = db.storage.binary.get("powerchat_client.py")
        return Response(
            content=client_script_bytes,
            media_type="text/x-python",
            headers={"Content-Disposition": "attachment; filename=powerchat_client.py"}
        )
    except Exception as e:
        return {"error": f"Failed to download client: {str(e)}"}

@router.get("/client-health")
def check_client_storage_health():
    """Check if the client storage API is running"""
    return {"status": "ok", "message": "Client storage API is operational"}
