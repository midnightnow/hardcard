#!/bin/bash

echo "🚀 Starting VetSorcery - Final Solution"
echo "======================================="

# 1. Kill any existing servers
echo "Cleaning up ports..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 2. Start Backend
echo ""
echo "📦 Starting Backend API..."
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install fastapi uvicorn python-multipart firebase-admin python-jose passlib python-dotenv
else
    source venv/bin/activate
fi
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# 3. Start Frontend with HTTP server (no build needed)
echo ""
echo "🌐 Starting Frontend..."
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend
python3 -m http.server 5173 &
FRONTEND_PID=$!
echo "✅ Frontend running on http://localhost:5173 (PID: $FRONTEND_PID)"

# 4. Open browser
echo ""
echo "🚀 Opening VetSorcery in browser..."
sleep 2
open http://localhost:5173

echo ""
echo "======================================="
echo "✅ VetSorcery is running!"
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "======================================="

# Wait and handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped.'; exit" INT
wait