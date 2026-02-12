#!/bin/bash

echo "Starting Hardcard Applications..."

# Kill any existing processes on our ports
echo "Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start backend
echo "Starting backend server..."
cd /Users/studio/hardcard/backend
source .venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Give backend time to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd /Users/studio/hardcard/frontend
yarn dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait a moment and check status
sleep 5

echo ""
echo "Checking services..."
echo "Backend: http://localhost:8000"
curl -s http://localhost:8000 > /dev/null && echo "✓ Backend is running" || echo "✗ Backend failed to start"

echo "Frontend: http://localhost:5173 (or http://localhost:3000)"
curl -s http://localhost:5173 > /dev/null && echo "✓ Frontend is running on 5173" || echo "Check http://localhost:3000"

echo ""
echo "Applications started!"
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "Backend Docs: http://localhost:8000/docs"
echo ""
echo "To stop all services, run: kill $BACKEND_PID $FRONTEND_PID"