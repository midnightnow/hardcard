#!/bin/bash

# MacAgent Pro Inference Server Startup Script

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFERENCE_DIR="$SCRIPT_DIR/inference"
MODEL_NAME="${1:-macagent-4b}"
PORT="${2:-8000}"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║       MacAgent Pro Inference Server              ║"
echo "║         AI-Powered macOS Automation              ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required${NC}"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d "$SCRIPT_DIR/venv" ]]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r "$INFERENCE_DIR/requirements.txt"
fi

# Check if model exists
MODEL_PATH="$SCRIPT_DIR/models/$MODEL_NAME"
if [[ ! -d "$MODEL_PATH" ]]; then
    echo -e "${YELLOW}Warning: Model $MODEL_NAME not found at $MODEL_PATH${NC}"
    echo -e "${YELLOW}The server will start but you'll need to load a model${NC}"
fi

# Start the server
echo -e "${GREEN}Starting inference server...${NC}"
echo -e "  Model: ${CYAN}$MODEL_NAME${NC}"
echo -e "  Port: ${CYAN}$PORT${NC}"
echo -e "  URL: ${CYAN}http://localhost:$PORT${NC}"
echo -e "  Docs: ${CYAN}http://localhost:$PORT/docs${NC}"
echo ""

cd "$INFERENCE_DIR"
python3 server.py --model "$MODEL_NAME" --port "$PORT" --reload