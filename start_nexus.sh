#!/bin/bash

echo "Starting NEXUS App..."

# Kill existing processes
lsof -ti:3002 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true

# Start NEXUS backend
echo "Starting NEXUS backend..."
cd /Users/studio/hardcard/apps/NEXUS/backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install fastapi uvicorn python-multipart python-dotenv >/dev/null 2>&1
uvicorn main:app --reload --host 0.0.0.0 --port 8002 > nexus-backend.log 2>&1 &
BACKEND_PID=$!

# Start NEXUS frontend
echo "Starting NEXUS frontend..."
cd /Users/studio/hardcard/apps/NEXUS/frontend
if [ ! -d "node_modules" ]; then
    yarn install
fi
VITE_PORT=3002 yarn dev > nexus-frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 5

echo ""
echo "NEXUS App started!"
echo "Frontend: http://localhost:3002"
echo "Backend API: http://localhost:8002"
echo "API Docs: http://localhost:8002/docs"
echo ""
echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"