#!/bin/bash

echo "Starting ALL Hardcard Suite Applications..."

# Configuration
BASE_DIR="/Users/studio/00 Constellation/hardcard"
APPS_DIR="$BASE_DIR/apps"

# App configurations
declare -A APPS=(
    ["NEXUS"]="3001:8001"      # frontend:backend
    ["HARDCARD"]="3002:8002"
    ["HEMPEX"]="3003:8003"
    ["VETSORCERY"]="3004:8004"
)

# Kill existing processes
echo "Cleaning up existing processes..."
for port in 3001 3002 3003 3004 8001 8002 8003 8004; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done

# Function to start an app
start_app() {
    local app_name=$1
    local ports=$2
    local frontend_port=${ports%:*}
    local backend_port=${ports#*:}
    
    echo ""
    echo "Starting $app_name..."
    
    # Start backend
    cd "$APPS_DIR/$app_name/backend"
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment for $app_name backend..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install fastapi uvicorn python-multipart python-dotenv >/dev/null 2>&1
    else
        source .venv/bin/activate
    fi
    
    echo "Starting $app_name backend on port $backend_port..."
    uvicorn main:app --reload --host 0.0.0.0 --port $backend_port > "$app_name-backend.log" 2>&1 &
    
    # Start frontend
    cd "$APPS_DIR/$app_name/frontend"
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies for $app_name frontend..."
        yarn install >/dev/null 2>&1
    fi
    
    echo "Starting $app_name frontend on port $frontend_port..."
    PORT=$frontend_port yarn dev > "$app_name-frontend.log" 2>&1 &
}

# Start all apps
for app in "${!APPS[@]}"; do
    start_app "$app" "${APPS[$app]}"
done

# Wait a bit and show status
sleep 10

echo ""
echo "========================================="
echo "All Hardcard Suite Apps Started!"
echo "========================================="
echo ""
echo "Main App (already running):"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo ""
echo "Suite Apps:"
echo "  NEXUS:      http://localhost:3001 (backend: 8001)"
echo "  HARDCARD:   http://localhost:3002 (backend: 8002)"
echo "  HEMPEX:     http://localhost:3003 (backend: 8003)"
echo "  VETSORCERY: http://localhost:3004 (backend: 8004)"
echo ""
echo "API Documentation:"
echo "  Main:       http://localhost:8000/docs"
echo "  NEXUS:      http://localhost:8001/docs"
echo "  HARDCARD:   http://localhost:8002/docs"
echo "  HEMPEX:     http://localhost:8003/docs"
echo "  VETSORCERY: http://localhost:8004/docs"
echo ""
echo "To stop all services, run: killall node Python"
echo "========================================="