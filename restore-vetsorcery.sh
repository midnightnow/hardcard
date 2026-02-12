#!/bin/bash
# Script to restore the original VetSorcery rich frontend

echo "🔄 Restoring Original VetSorcery Frontend..."

# Navigate to frontend directory
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend

# Use Node 20 for compatibility
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 20

# Clean install with proper flags
echo "🧹 Cleaning previous installation..."
rm -rf node_modules package-lock.json

# Install core dependencies first
echo "📦 Installing core dependencies..."
npm install react@18 react-dom@18 typescript @types/react @types/react-dom --save-dev --legacy-peer-deps

# Install Vite and plugins
echo "🔧 Installing Vite and plugins..."
npm install vite@4 @vitejs/plugin-react --save-dev --legacy-peer-deps

# Install essential packages that might be missing
echo "📋 Installing additional dependencies..."
npm install tailwindcss autoprefixer postcss --save-dev --legacy-peer-deps

echo "✅ Dependencies installed. Testing Vite..."

# Kill any existing process on port 5173
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Start Vite with the proper config
echo "🚀 Starting Vite development server..."
npx vite --port 5173 --host 0.0.0.0 &
VITE_PID=$!

# Wait a moment for startup
sleep 3

echo "✅ VetSorcery restoration complete!"
echo "Frontend: http://localhost:5173"
echo "Vite PID: $VITE_PID"

# Open browser
open http://localhost:5173