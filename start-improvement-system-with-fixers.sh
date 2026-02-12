#!/bin/bash

# Start the improvement system with code fixing agents

echo "🚀 Starting HardCard Continuous Improvement System with Code Fixers..."

# Ensure we're in the right directory
cd /Users/studio/hardcard

# Set Python path to include current directory
export PYTHONPATH="${PYTHONPATH}:/Users/studio/hardcard"

# Kill any existing instances
pkill -f simple-improvement-system.py

# Start the system
echo "Starting improvement system..."
python simple-improvement-system.py &

echo "✅ System started with all agents including Code Fixing Agent!"
echo "📊 Monitor status at: http://localhost:8001/development-dashboard.html"
echo "📄 Check logs at: tail -f logs/improvement-system.log"