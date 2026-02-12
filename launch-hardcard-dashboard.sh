#!/bin/bash

# HardCard Dashboard Launcher
# This script launches the HardCard Command Center dashboard

echo "🚀 Launching HardCard Command Center..."

# Change to HardCard directory
cd /Users/studio/hardcard

# Start the HTTP server if not already running
if ! lsof -i :8001 > /dev/null 2>&1; then
    echo "Starting HTTP server on port 8001..."
    python3 -m http.server 8001 &
    SERVER_PID=$!
    echo "Server started with PID: $SERVER_PID"
    
    # Wait for server to start
    sleep 2
else
    echo "HTTP server already running on port 8001"
fi

# Open the dashboard in default browser
echo "Opening HardCard Command Center in browser..."
open http://localhost:8001/hardcard-dashboard.html

# Optional: Launch VS Code with HardCard workspace
# echo "Opening VS Code..."
# code /Users/studio/hardcard

# Optional: Open terminal in HardCard directory
# echo "Opening terminal..."
# osascript -e 'tell app "Terminal" to do script "cd /Users/studio/hardcard"'

echo "✅ HardCard Command Center launched successfully!"
echo ""
echo "Keyboard shortcuts:"
echo "  Cmd+L : Launch all primary systems"
echo "  Cmd+R : Refresh dashboard"
echo "  Cmd+T : Open terminal"
echo "  Cmd+H : Run health check"
echo ""
echo "Dashboard available at: http://localhost:8001/hardcard-dashboard.html"