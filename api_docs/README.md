# HardCard API Documentation Portal

## Overview

Welcome to the comprehensive HardCard API documentation portal. This directory contains everything you need to integrate with the HardCard Veterinary Intelligence Platform.

## Contents

### 📚 Interactive Documentation
- **`index.html`** - Interactive Swagger UI documentation
- **`openapi.json`** - Complete OpenAPI 3.0 specification

### 🚀 Getting Started
- **`getting_started.md`** - Quick start guide and authentication
- **`integration_examples.md`** - Complete integration examples
- **`phone_agent_guide.md`** - AI Phone Agent specific documentation

### 🛠️ Development Tools
- **`hardcard_api.postman_collection.json`** - Postman collection for API testing
- **`api_testing_scripts/`** - Automated testing scripts

### 🔗 API Reference

#### Core Endpoints
- **`/health`** - System health monitoring
- **`/routes/clients`** - Client management
- **`/routes/patients`** - Patient records
- **`/routes/appointments`** - Appointment scheduling
- **`/routes/phone-agent/*`** - AI phone agent operations

#### MUSE Integration
- **`/api/muse/validation/*`** - Mathematical creativity validation
- **`/api/muse/status`** - MUSE platform status

## Quick Start

1. **Get API Token**: Log in to HardCard dashboard and generate API token
2. **Test Connection**: 
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.hardcard.com/health
   ```
3. **Import Postman Collection**: Use `hardcard_api.postman_collection.json`
4. **Read Guides**: Start with `getting_started.md`

## Support

- 📧 **Email**: api-support@hardcard.com
- 📚 **Documentation**: https://docs.hardcard.com
- 💬 **Discord**: https://discord.gg/hardcard

## Features

### 🤖 AI Phone Agents
- 24/7 automated appointment booking
- Natural language conversation
- Multi-language support
- Real-time call monitoring

### 🏥 Practice Management
- Complete EMR integration
- Client and patient management
- Appointment scheduling
- Analytics and reporting

### 🎭 MUSE Creativity
- Mathematical poetry generation
- Music composition
- Video creation
- Validation framework

## Authentication

All API requests require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json" \
     https://api.hardcard.com/routes/clients
```

## Rate Limits

- **Standard requests**: 1000/hour
- **Phone agent calls**: 50/hour  
- **Bulk operations**: 10/minute

## Status & Monitoring

- **API Status**: https://status.hardcard.com
- **Health Endpoint**: https://api.hardcard.com/health
- **Metrics**: https://api.hardcard.com/metrics

---

Built with ❤️ by the HardCard team for veterinary professionals worldwide.
