#!/bin/bash

echo "========================================"
echo "Starting Hardcard Complete Suite"
echo "========================================"

# Configuration
BASE_DIR="/Users/studio/00 Constellation/hardcard"

# Function to check if port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# Kill existing processes
echo "Cleaning up existing processes..."
for port in 3000 3001 3002 3003 3004 5173 8000 8001 8002 8003 8004; do
    if check_port $port; then
        echo "Killing process on port $port..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

sleep 2

# Start main backend if not running
if ! check_port 8000; then
    echo ""
    echo "Starting main backend..."
    cd "$BASE_DIR/backend"
    source .venv/bin/activate
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend-main.log 2>&1 &
fi

# Start main frontend if not running
if ! check_port 5173; then
    echo "Starting main frontend on port 5173..."
    cd "$BASE_DIR/frontend"
    yarn dev > frontend-main.log 2>&1 &
fi

# Start additional frontends on different ports
echo ""
echo "Starting additional frontend instances..."

# Port 3000
if ! check_port 3000; then
    echo "Starting frontend on port 3000..."
    cd "$BASE_DIR/frontend"
    PORT=3000 yarn dev --port 3000 > frontend-3000.log 2>&1 &
fi

# Port 3002
if ! check_port 3002; then
    echo "Starting frontend on port 3002..."
    cd "$BASE_DIR/frontend"
    PORT=3002 yarn dev --port 3002 > frontend-3002.log 2>&1 &
fi

# Wait for services to start
echo ""
echo "Waiting for services to start..."
sleep 10

# Check status
echo ""
echo "========================================"
echo "Service Status Check"
echo "========================================"
echo ""

# Function to check service
check_service() {
    local port=$1
    local name=$2
    if curl -s http://localhost:$port >/dev/null 2>&1; then
        echo "✅ $name on port $port is running"
    else
        echo "❌ $name on port $port is NOT running"
    fi
}

check_service 5173 "Main Frontend"
check_service 8000 "Main Backend API"
check_service 3000 "Frontend (Alt 1)"
check_service 3002 "Frontend (Alt 2)"

echo ""
echo "========================================"
echo "Available Services"
echo "========================================"
echo ""
echo "Main Application:"
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""
echo "Alternative Frontend Ports:"
echo "  http://localhost:3000"
echo "  http://localhost:3002"
echo ""
echo "Logs are available in:"
echo "  $BASE_DIR/backend/backend-main.log"
echo "  $BASE_DIR/frontend/frontend-main.log"
echo "  $BASE_DIR/frontend/frontend-3000.log"
echo "  $BASE_DIR/frontend/frontend-3002.log"
echo ""
echo "To stop all services, run:"
echo "  killall node Python"
echo ""
echo "========================================"