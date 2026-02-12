#!/bin/bash

echo "🚀 Launching VetSorcery..."
echo "This will install minimal dependencies and start the app"
echo ""

# Navigate to frontend
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend

# Kill any existing process on port 5173
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Install just the critical dependencies in a temporary location
echo "📦 Installing critical dependencies..."
mkdir -p .temp_modules
cd .temp_modules
npm init -y >/dev/null 2>&1
npm install vite@4 @vitejs/plugin-react react react-dom --no-save >/dev/null 2>&1
cd ..

# Start Vite using the temporary modules
echo "🌐 Starting VetSorcery on http://localhost:5173"
./temp_modules/node_modules/.bin/vite --port 5173 --open

# Alternative: Use npx with specific version
# npx -p vite@4 -p @vitejs/plugin-react vite --port 5173 --open