#!/bin/bash

echo "🚀 Starting VetSorcery Application..."

# Kill any process on ports 5173 and 8000
echo "Clearing ports..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Start backend
echo "Starting backend server..."
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend

# Create/activate virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -m uvicorn --version &>/dev/null; then
    echo "Installing backend dependencies..."
    pip install uvicorn fastapi python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv firebase-admin
fi

python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID"

# Start frontend
echo "Starting frontend server..."
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend

# Create a minimal package.json if npm install is taking too long
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a few minutes)..."
    npm install --legacy-peer-deps --no-audit --no-fund --prefer-offline
fi

# Start the dev server
npm run dev &
FRONTEND_PID=$!
echo "Frontend started with PID $FRONTEND_PID"

echo ""
echo "✅ VetSorcery is starting up!"
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait a bit for servers to start, then open browser
(sleep 5 && open http://localhost:5173) &

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait