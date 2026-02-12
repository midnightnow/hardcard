# 🚀 MacAgent Pro Inference Server

## Production-Ready AI Inference for macOS Automation

The MacAgent Pro Inference Server provides a high-performance, secure API for running your trained MacAgent models locally. It includes support for LoRA models, HardCard encryption integration, and production-ready features.

---

## ✨ Features

- **🤖 Multi-Model Support**: Load and switch between 4B, 13B, and 32B models
- **🔒 HardCard Integration**: Optional visual encryption for commands
- **⚡ Optimized Performance**: GPU acceleration, quantization, and caching
- **🛡️ Safety First**: Built-in safety scoring and validation
- **📊 Production Ready**: Health checks, metrics, and monitoring
- **🔄 Hot Reload**: Development mode with automatic reloading
- **📚 API Documentation**: Auto-generated OpenAPI/Swagger docs

---

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
cd hardcard
python3 -m venv venv
source venv/bin/activate
pip install -r inference/requirements.txt
```

### 2. **Start the Server**

```bash
# Start with default model (macagent-4b)
./start_inference_server.sh

# Start with specific model
./start_inference_server.sh macagent-13b 8000

# Or directly
cd inference
python3 server.py --model macagent-4b --port 8000
```

### 3. **Test the Server**

```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/models

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Empty the trash"}'
```

---

## 📡 API Endpoints

### **GET /** - Server Info
Returns server status and configuration.

### **GET /health** - Health Check
```json
{
  "status": "healthy",
  "model_loaded": true,
  "current_model": "macagent-4b",
  "timestamp": "2024-01-15T10:30:00"
}
```

### **GET /models** - List Models
```json
[
  {
    "name": "macagent-4b",
    "base_model": "microsoft/Phi-3-mini-4k-instruct",
    "status": "loaded",
    "device": "cuda",
    "description": "Fast model for real-time responses"
  }
]
```

### **POST /models/{model_name}/load** - Load Model
Load a specific model into memory.

### **POST /predict** - Generate Prediction

**Request:**
```json
{
  "prompt": "Clean up my Downloads folder",
  "max_new_tokens": 512,
  "temperature": 0.7,
  "return_reasoning": true,
  "encrypt_response": false
}
```

**Response:**
```json
{
  "success": true,
  "generated_text": "Full model response...",
  "command": "find ~/Downloads -type f -mtime +30 -exec mv {} ~/Downloads/Archive/ \\;",
  "reasoning": [
    "1. Identify files older than 30 days",
    "2. Create Archive folder if needed",
    "3. Move (not delete) for safety"
  ],
  "safety_score": 0.95,
  "model": "macagent-4b",
  "inference_time_ms": 87.3,
  "timestamp": "2024-01-15T10:30:00"
}
```

### **POST /verify** - Verify Encrypted Command
Verify a HardCard encrypted command.

---

## 🔧 Configuration

### Environment Variables

```bash
# Model configuration
export MACAGENT_DEFAULT_MODEL="macagent-13b"
export MACAGENT_MODELS_PATH="/path/to/models"

# Server configuration
export MACAGENT_HOST="0.0.0.0"
export MACAGENT_PORT="8000"

# Performance tuning
export MACAGENT_MAX_BATCH_SIZE="8"
export MACAGENT_USE_GPU="true"
```

### Model Configuration

Models should be stored in the `models/` directory with this structure:

```
models/
├── macagent-4b/
│   ├── config.json
│   ├── adapter_config.json  (for LoRA)
│   ├── adapter_model.bin    (for LoRA)
│   ├── tokenizer.json
│   └── tokenizer_config.json
├── macagent-13b/
└── macagent-32b/
```

---

## 💻 Client Usage

### Python Client

```python
from inference.client import MacAgentClient

async with MacAgentClient() as client:
    # Make prediction
    result = await client.predict(
        prompt="Organize my Desktop files",
        temperature=0.7
    )
    
    print(f"Command: {result['command']}")
    print(f"Safety: {result['safety_score']}")
```

### Interactive Session

```bash
# Start interactive client
python3 inference/client.py --demo interactive

# Available commands:
# > help              - Show commands
# > models            - List available models
# > load macagent-13b - Load specific model
# > Empty the trash   - Process automation request
```

### Batch Processing

```python
async with MacAgentBatchClient() as client:
    prompts = [
        "Empty trash",
        "Take screenshot", 
        "Check disk space"
    ]
    results = await client.batch_predict(prompts)
```

---

## 🛡️ Security Features

### Safety Validation
- Every command is scored for safety (0-1)
- Dangerous operations are flagged
- User consent required for system changes

### HardCard Encryption
- Optional visual encryption for commands
- Cryptographic verification
- Tamper-proof command storage

### Local-Only Processing
- No data leaves your machine
- No telemetry or analytics
- Complete privacy protection

---

## 📊 Performance Optimization

### GPU Acceleration
```python
# Automatic GPU detection
# Supports CUDA and Apple Silicon (MPS)
DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
```

### Model Quantization
```python
# 4-bit quantization for GPU memory efficiency
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)
```

### Response Caching
- Frequently used commands are cached
- Configurable cache size and TTL
- Significant latency reduction

---

## 🔍 Monitoring & Debugging

### Logging
```bash
# Server logs
tail -f inference_server.log

# Set log level
export LOG_LEVEL=DEBUG
```

### Metrics
- Request count and latency
- Model loading time
- Memory usage
- Cache hit rates

### Health Monitoring
```bash
# Continuous health check
watch -n 5 'curl -s http://localhost:8000/health | jq'
```

---

## 🚦 Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  inference.server:app
```

### Using Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY inference/requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "inference/server.py"]
```

### Systemd Service
```ini
[Unit]
Description=MacAgent Pro Inference Server
After=network.target

[Service]
Type=simple
User=macagent
WorkingDirectory=/opt/macagent
ExecStart=/opt/macagent/venv/bin/python inference/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🧪 Testing

### Unit Tests
```bash
pytest inference/tests/test_server.py -v
```

### Load Testing
```bash
# Using locust
locust -f inference/tests/load_test.py --host http://localhost:8000
```

### Integration Tests
```bash
python3 test_macagent_integration.py
```

---

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤝 Integration Examples

### With MacAgent Pro App
```swift
// Swift integration
let response = await MacAgentAPI.predict(
    prompt: "Clean Downloads folder",
    model: "macagent-4b"
)
```

### With HardCard Encryption
```python
result = await client.process_automation_request(
    "Organize Documents folder"
)
if result['encrypted']:
    print(f"Visual proof: {result['visual_proof']}")
```

---

## 🆘 Troubleshooting

### Model Loading Issues
```bash
# Check model files exist
ls -la models/macagent-4b/

# Verify model config
cat models/macagent-4b/config.json | jq
```

### Memory Issues
```bash
# Reduce batch size
export MACAGENT_MAX_BATCH_SIZE=1

# Use CPU instead of GPU
export CUDA_VISIBLE_DEVICES=""
```

### Performance Issues
- Enable quantization for large models
- Use smaller model variants (4B vs 13B)
- Increase server workers
- Enable response caching

---

**The MacAgent Pro Inference Server is your gateway to powerful, private, and secure macOS automation!** 🚀