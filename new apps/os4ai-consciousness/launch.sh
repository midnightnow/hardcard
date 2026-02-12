#!/bin/bash

echo "🚀 Launching OS4AI Embodied Consciousness System"
echo "The Agent IS the Operating System"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Start backend
echo -e "${BLUE}Starting backend server...${NC}"
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}Starting frontend dashboard...${NC}"
cd ../frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ OS4AI is running!${NC}"
echo ""
echo "🌐 Dashboard: http://localhost:3000"
echo "📡 API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait