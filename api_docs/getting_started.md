# Getting Started with HardCard API

## Overview

The HardCard API provides comprehensive access to our AI-powered veterinary platform, including:

- 🤖 **AI Phone Agents**: 24/7 automated call handling
- 👥 **Client Management**: Complete CRM functionality  
- 🐕 **Patient Records**: Comprehensive EMR system
- 📅 **Appointment Scheduling**: Smart booking system
- 🎭 **MUSE Integration**: Mathematical creativity validation

## Authentication

All API requests require authentication using Bearer tokens:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     https://api.hardcard.com/health
```

### Obtaining API Tokens

1. Log in to your HardCard dashboard
2. Navigate to **Settings** → **API Access**
3. Generate a new API token
4. Copy and securely store your token

## Base URLs

- **Production**: `https://api.hardcard.com`
- **Staging**: `https://staging-api.hardcard.com`
- **Development**: `http://localhost:8000`

## Response Format

All API responses follow a consistent JSON format:

```json
{
  "data": { /* Response data */ },
  "status": "success",
  "message": "Operation completed successfully",
  "timestamp": "2025-07-19T12:00:00Z"
}
```

## Error Handling

Errors are returned with appropriate HTTP status codes:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": { /* Additional error context */ }
  },
  "status": "error",
  "timestamp": "2025-07-19T12:00:00Z"
}
```

## Rate Limiting

API requests are rate limited:

- **Authenticated requests**: 1000 requests/hour
- **Phone agent calls**: 50 calls/hour
- **Bulk operations**: 10 requests/minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642694400
```

## Quick Start Example

```python
import requests

# Configure API client
API_BASE = "https://api.hardcard.com"
headers = {
    "Authorization": "Bearer YOUR_API_TOKEN",
    "Content-Type": "application/json"
}

# Check system health
response = requests.get(f"{API_BASE}/health", headers=headers)
print(f"System Status: {response.json()['status']}")

# List clients
clients = requests.get(f"{API_BASE}/routes/clients", headers=headers)
print(f"Total Clients: {len(clients.json()['clients'])}")

# Create new client
new_client = {
    "name": "Dr. Sarah Johnson",
    "email": "sarah@example.com",
    "phone": "+1234567890"
}
response = requests.post(f"{API_BASE}/routes/clients", 
                        json=new_client, headers=headers)
print(f"Client Created: {response.json()['id']}")
```

## SDKs and Libraries

Official SDKs available:
- **Python**: `pip install hardcard-api`
- **JavaScript**: `npm install @hardcard/api`
- **Go**: `go get github.com/hardcard/go-sdk`

## Support

- 📧 **Email**: api-support@hardcard.com
- 📚 **Documentation**: https://docs.hardcard.com
- 💬 **Discord**: https://discord.gg/hardcard
