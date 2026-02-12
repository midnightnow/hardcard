from fastapi import APIRouter, Response

router = APIRouter()

# PowerChat markdown documentation
powerchat_documentation = """
# PowerChat

PowerChat is a context-aware AI assistant overlay system that provides real-time suggestions based on various data sources including clipboard content and API data.

## Features

- Real-time context monitoring (clipboard, API data)
- Context-aware suggestions
- Websocket-based real-time communication
- Transparent overlay UI
- Confidence-based transparency

## API Documentation

### HTTP Endpoints

#### `GET /powerchat/health`

Check if the PowerChat API is running.

**Response**
```json
{
  "status": "ok",
  "message": "PowerChat API is operational"
}
```

#### `POST /powerchat/context/{client_id}`

Update context for a specific client.

**Request**
```json
{
  "context": {
    "clipboard": {
      "value": "Some clipboard content",
      "timestamp": 1650000000.0
    },
    "api_products": {
      "value": "[{\"name\": \"Product 1\", \"sku\": \"SKU123\"}]",
      "timestamp": 1650000000.0
    }
  }
}
```

**Response**
```json
{
  "status": "success",
  "message": "Context updated"
}
```

#### `GET /powerchat/context/{client_id}`

Get context for a specific client.

**Response**
```json
{
  "clipboard": {
    "value": "Some clipboard content",
    "timestamp": 1650000000.0
  },
  "api_products": {
    "value": "[{\"name\": \"Product 1\", \"sku\": \"SKU123\"}]",
    "timestamp": 1650000000.0
  }
}
```

#### `GET /powerchat/suggestions/{client_id}`

Get suggestions for a specific client.

**Response**
```json
{
  "suggestions": [
    {
      "text": "Product: Product 1 (SKU: SKU123)",
      "confidence": 0.85,
      "source": "api_products"
    },
    {
      "text": "Use this from clipboard: Some clipboard content",
      "confidence": 0.8,
      "source": "clipboard"
    }
  ],
  "confidence": 0.4,
  "timestamp": "2023-04-15T12:34:56.789Z"
}
```

### WebSocket Endpoint

#### `WebSocket /powerchat/ws/{client_id}`

WebSocket endpoint for real-time communication with PowerChat clients.

**Messages from client to server**

1. Context Update:
```json
{
  "context": {
    "clipboard": {
      "value": "Some clipboard content",
      "timestamp": 1650000000.0
    }
  }
}
```

2. Heartbeat:
```json
{
  "heartbeat": 1650000000.0
}
```

**Messages from server to client**

1. Suggestions Update:
```json
{
  "suggestions": [
    {
      "text": "Use this from clipboard: Some clipboard content",
      "confidence": 0.8,
      "source": "clipboard"
    }
  ],
  "confidence": 0.2,
  "timestamp": "2023-04-15T12:34:56.789Z"
}
```

2. Heartbeat Acknowledgment:
```json
{
  "heartbeat_ack": 1650000000.0
}
```

## Client Usage

A Python desktop client implementation is available for Windows, macOS, and Linux. The client connects to the PowerChat API and displays suggestions in a transparent overlay window.

See the included `powerchat_client.py` script for more details.

### Installation

```bash
pip install overlay pyperclip websocket-client requests python-dotenv Pillow
```

### Running the Client

First, download the client script from the API endpoint:

```bash
curl -o powerchat_client.py https://api.databutton.com/_projects/abfc4236-481d-4bd9-bfe1-7a0124980081/dbtn/prodx/app/routes/client_storage/download-client
chmod +x powerchat_client.py
python powerchat_client.py
```

Optional arguments:
- `--ws-uri WS_URI`: WebSocket URI for backend connection
- `--api-url API_URL`: Base API URL for monitoring
- `--client-id CLIENT_ID`: Client ID for WebSocket connection
- `--disable-clipboard`: Disable clipboard monitoring
- `--disable-api`: Disable API monitoring
- `--offline`: Run in offline mode without backend connection

## Architecture

The PowerChat system consists of the following components:

1. **Context Engine**: Manages context data from various sources.
2. **Backend Bridge**: Handles communication with the PowerChat API.
3. **Plugin Sources**: Monitors clipboard, API data, and other potential sources.
4. **Overlay Renderer**: Displays suggestions in a transparent overlay.

## Future Enhancements

- Keystroke monitoring
- OCR for on-screen text
- Voice recognition
- More sophisticated suggestion generation
- Browser extension variant
- More context sources
"""

@router.get("/readme-md-documentation")
def get_markdown_documentation():
    """Get PowerChat markdown documentation"""
    return Response(content=powerchat_documentation, media_type="text/markdown")

@router.get("/readme-md/health")
def check_health_readme_md():
    """Check if the readme_md API is running"""
    return {"status": "ok", "message": "Readme_md API is operational"}
