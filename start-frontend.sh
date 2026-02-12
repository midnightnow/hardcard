#!/bin/bash

# VetSorcery Frontend Startup Script for PM2
cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend

# Serve the ultimate VetSorcery interface with all modules
echo "🚀 Starting VetSorcery Ultimate Interface..."
echo "📍 Access at: http://localhost:5173/vetsorcery-complete.html"
exec python3 -m http.server 5173 --bind 0.0.0.0