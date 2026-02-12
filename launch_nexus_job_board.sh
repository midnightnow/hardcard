#!/bin/bash
# HardCard Nexus Job Board Launch Script

echo "🚀 Launching HardCard Nexus Job Board..."
echo ""

# Navigate to Nexus app directory
cd "$(dirname "$0")/apps/NEXUS" || exit 1

echo "📦 Installing dependencies..."
echo ""

# Install backend dependencies
echo "Backend (Python)..."
cd backend
python3 -m pip install -r requirements.txt --quiet
cd ..

# Install frontend dependencies  
echo "Frontend (Node.js)..."
cd frontend
npm install --silent
cd ../..

echo ""
echo "✅ Dependencies installed"
echo ""

# Start backend in background
echo "🔧 Starting backend server (port 8000)..."
cd apps/NEXUS/backend
python3 -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ../../..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend dev server (port 5173)..."
cd apps/NEXUS/frontend
npm run dev &
FRONTEND_PID=$!
cd ../../..

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✨ HardCard Nexus Job Board is LIVE!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 Frontend:  http://localhost:5173/job-board"
echo "🔌 API:       http://localhost:8000/routes/signals/"
echo ""
echo "Quick Commands:"
echo "  • Broadcast signal:  hardcard nexus --broadcast \"Task description\""
echo "  • Start watcher:     python3 nexus_watcher.py"
echo "  • View stats:        python3 nexus_watcher.py --stats"
echo ""
echo "Press Ctrl+C to stop all services"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Wait for user interrupt
trap "echo ''; echo '⏹️  Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait
