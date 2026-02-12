#!/bin/bash

# VetSorcery Control Script
# Usage: ./vetsorcery-control.sh [start|stop|restart|status|logs|open]

case "$1" in
    start)
        echo "🚀 Starting VetSorcery services..."
        pm2 start /Users/studio/hardcard/vetsorcery-ecosystem.config.js
        echo "✅ Services started"
        pm2 status
        ;;
    stop)
        echo "🛑 Stopping VetSorcery services..."
        pm2 stop vetsorcery-backend vetsorcery-frontend
        echo "✅ Services stopped"
        ;;
    restart)
        echo "🔄 Restarting VetSorcery services..."
        pm2 restart vetsorcery-backend vetsorcery-frontend
        echo "✅ Services restarted"
        pm2 status
        ;;
    status)
        echo "📊 VetSorcery Status:"
        pm2 status
        echo ""
        echo "🌐 Frontend: http://localhost:5173"
        echo "🔧 Backend API: http://localhost:8000/docs"
        ;;
    logs)
        echo "📜 VetSorcery Logs (Ctrl+C to exit):"
        pm2 logs vetsorcery-backend vetsorcery-frontend
        ;;
    open)
        echo "🌐 Opening VetSorcery in browser..."
        open http://localhost:5173
        ;;
    *)
        echo "VetSorcery Control Script"
        echo "Usage: $0 {start|stop|restart|status|logs|open}"
        echo ""
        echo "Commands:"
        echo "  start   - Start VetSorcery services"
        echo "  stop    - Stop VetSorcery services"
        echo "  restart - Restart VetSorcery services"
        echo "  status  - Show service status"
        echo "  logs    - Show real-time logs"
        echo "  open    - Open frontend in browser"
        exit 1
        ;;
esac