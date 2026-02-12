#!/bin/bash

# VetSorcery Backend Startup Script for PM2
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend

# Create venv if doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -m pip show uvicorn >/dev/null 2>&1; then
    echo "Installing backend dependencies..."
    pip install uvicorn fastapi python-multipart PyJWT firebase-admin python-jose passlib python-dotenv
fi

# Start the backend server
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload