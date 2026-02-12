#!/bin/bash

# VetSorcery Always-Up Service
# Monitors and auto-restarts frontend and backend services
# Features: Health checks, auto-restart, port failover, logging

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_DIR="${SCRIPT_DIR}/vetsorcery-logs"
FRONTEND_DIR="/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend"
BACKEND_DIR="/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend"

# Port configurations with failover
FRONTEND_PORTS=(5173 5174 5175 5176)
BACKEND_PORTS=(8000 8001 8002 8003)

# Current active ports
FRONTEND_PORT=5173
BACKEND_PORT=8000

# Process PIDs
FRONTEND_PID=""
BACKEND_PID=""
MONITOR_PID=""

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/vetsorcery.log"
}

# Find available port from list
find_available_port() {
    local ports=("$@")
    for port in "${ports[@]}"; do
        if ! lsof -ti:$port >/dev/null 2>&1; then
            echo $port
            return 0
        fi
    done
    return 1
}

# Kill process on port
kill_port() {
    local port=$1
    log "Killing processes on port $port"
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
}

# Start frontend service
start_frontend() {
    log "Starting frontend service..."
    
    # Find available port
    FRONTEND_PORT=$(find_available_port "${FRONTEND_PORTS[@]}")
    if [ -z "$FRONTEND_PORT" ]; then
        log "ERROR: No available frontend ports"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log "Frontend dependencies missing. Starting simple HTTP server..."
        python3 -m http.server $FRONTEND_PORT > "$LOG_DIR/frontend.log" 2>&1 &
    else
        log "Starting Vite dev server on port $FRONTEND_PORT..."
        npx vite --port $FRONTEND_PORT --host 0.0.0.0 > "$LOG_DIR/frontend.log" 2>&1 &
    fi
    
    FRONTEND_PID=$!
    log "Frontend started with PID $FRONTEND_PID on port $FRONTEND_PORT"
    
    # Save port mapping
    echo "$FRONTEND_PORT" > "$LOG_DIR/frontend.port"
}

# Start backend service
start_backend() {
    log "Starting backend service..."
    
    # Find available port
    BACKEND_PORT=$(find_available_port "${BACKEND_PORTS[@]}")
    if [ -z "$BACKEND_PORT" ]; then
        log "ERROR: No available backend ports"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Setup virtual environment if needed
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv and start server
    source venv/bin/activate
    
    # Install dependencies if needed
    if ! python -m pip show uvicorn >/dev/null 2>&1; then
        log "Installing backend dependencies..."
        pip install uvicorn fastapi python-multipart PyJWT firebase-admin python-jose passlib python-dotenv > "$LOG_DIR/backend-install.log" 2>&1
    fi
    
    log "Starting Uvicorn on port $BACKEND_PORT..."
    python -m uvicorn main:app --reload --port $BACKEND_PORT --host 0.0.0.0 > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    log "Backend started with PID $BACKEND_PID on port $BACKEND_PORT"
    
    # Save port mapping
    echo "$BACKEND_PORT" > "$LOG_DIR/backend.port"
}

# Health check for frontend
check_frontend_health() {
    if [ -z "$FRONTEND_PID" ] || ! kill -0 $FRONTEND_PID 2>/dev/null; then
        return 1
    fi
    
    # HTTP health check
    if command -v curl >/dev/null 2>&1; then
        curl -sf "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1
        return $?
    fi
    
    return 0
}

# Health check for backend
check_backend_health() {
    if [ -z "$BACKEND_PID" ] || ! kill -0 $BACKEND_PID 2>/dev/null; then
        return 1
    fi
    
    # API health check
    if command -v curl >/dev/null 2>&1; then
        curl -sf "http://localhost:$BACKEND_PORT/docs" >/dev/null 2>&1
        return $?
    fi
    
    return 0
}

# Monitor services
monitor_services() {
    log "Starting service monitor..."
    
    while true; do
        # Check frontend
        if ! check_frontend_health; then
            log "Frontend health check failed. Restarting..."
            kill $FRONTEND_PID 2>/dev/null || true
            start_frontend
        fi
        
        # Check backend
        if ! check_backend_health; then
            log "Backend health check failed. Restarting..."
            kill $BACKEND_PID 2>/dev/null || true
            start_backend
        fi
        
        # Sleep before next check
        sleep 10
    done
}

# Cleanup function
cleanup() {
    log "Shutting down VetSorcery services..."
    
    # Kill monitor
    [ ! -z "$MONITOR_PID" ] && kill $MONITOR_PID 2>/dev/null
    
    # Kill services
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    
    # Clean up ports
    kill_port $FRONTEND_PORT
    kill_port $BACKEND_PORT
    
    log "Shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    log "=== VetSorcery Always-Up Service Starting ==="
    
    # Clear any existing processes on default ports
    kill_port 5173
    kill_port 8000
    
    # Start services
    start_backend
    sleep 2
    start_frontend
    sleep 2
    
    # Start monitoring in background
    monitor_services &
    MONITOR_PID=$!
    
    # Print status
    log "=== Services Started Successfully ==="
    log "Frontend: http://localhost:$FRONTEND_PORT"
    log "Backend API: http://localhost:$BACKEND_PORT"
    log "Logs: $LOG_DIR"
    log "Monitor PID: $MONITOR_PID"
    log ""
    log "Service is now monitoring and will auto-restart on failure"
    log "Press Ctrl+C to stop all services"
    
    # Open browser
    sleep 2
    open "http://localhost:$FRONTEND_PORT" 2>/dev/null || true
    
    # Wait for interrupt
    wait $MONITOR_PID
}

# Run main function
main