#!/bin/bash

echo "🚀 Starting HardCard Continuous Improvement System..."

# Create logs directory if it doesn't exist
mkdir -p /Users/studio/hardcard/logs

# Install required Python packages if needed
echo "📦 Installing Python dependencies..."
pip3 install aiofiles aiohttp psutil > /dev/null 2>&1

# Load the launch agent
echo "🔧 Setting up auto-start..."
launchctl unload ~/Library/LaunchAgents/com.hardcard.improvement.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.hardcard.improvement.plist

# Start the system manually for now
echo "▶️ Starting improvement system..."
cd /Users/studio/hardcard
python3 simple-improvement-system.py &

echo "✅ Continuous Improvement System started!"
echo ""
echo "The system will now:"
echo "  • Monitor code quality continuously"
echo "  • Perform strategic realignment checks"
echo "  • Optimize performance automatically"
echo "  • Learn from patterns and suggest improvements"
echo "  • Check deployment readiness"
echo ""
echo "View real-time status at: http://localhost:8001/development-dashboard.html"
echo "System logs: /Users/studio/hardcard/logs/"