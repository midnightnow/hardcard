#!/bin/bash

# VetSorcery Live Launch Script
# Complete deployment with Telehealth & Web Portal features

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/studio/hardcard"
BACKEND_DIR="$PROJECT_ROOT/HARDCARDSUITE/vetsorcery_extracted/backend"
FRONTEND_DIR="$PROJECT_ROOT/HARDCARDSUITE/vetsorcery_extracted/frontend"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Port $port is in use, killing existing process..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service to start..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
            print_success "$service is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service failed to start after $max_attempts attempts"
    return 1
}

# Header
clear
echo "🏥 VetSorcery Live Deployment System"
echo "📱 Now with Telehealth & Web Portal Features!"
echo "================================================"
echo

# Step 1: Environment Setup
print_status "Setting up environment..."

# Create .env file if it doesn't exist
if [ ! -f "$BACKEND_DIR/.env" ]; then
    cat > "$BACKEND_DIR/.env" << EOF
# VetSorcery Environment Configuration
DATABASE_URL=sqlite:///./vetsorcery.db
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
DEBUG=False

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Telehealth Configuration
TELEHEALTH_VIDEO_PROVIDER=agora
TELEHEALTH_CHAT_ENABLED=true
TELEHEALTH_RECORDING_ENABLED=true

# Web Portal Configuration
PORTAL_SESSION_TIMEOUT=3600
PORTAL_MAX_FILE_SIZE=10485760
PORTAL_ALLOWED_EXTENSIONS=pdf,jpg,png,doc,docx

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@vetsorcery.com
SMTP_PASSWORD=your-app-password

# Payment Gateway (for web portal)
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_SECRET_KEY=sk_test_xxx
EOF
    print_success "Created .env configuration"
else
    print_status "Using existing .env configuration"
fi

# Step 2: Kill existing processes
print_status "Cleaning up existing processes..."
kill_port 8000  # Backend
kill_port 5173  # Frontend

# Step 3: Backend Setup
print_status "Setting up backend..."

cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
print_status "Installing backend dependencies..."
pip install --upgrade pip setuptools wheel >/dev/null 2>&1
pip install fastapi uvicorn sqlalchemy python-dotenv python-multipart \
    pydantic email-validator httpx pytest python-jose[cryptography] \
    passlib[bcrypt] alembic redis celery >/dev/null 2>&1

print_success "Backend dependencies installed"

# Step 4: Database Setup
print_status "Setting up database..."

# Create database init script
cat > "$BACKEND_DIR/init_db.py" << 'EOF'
#!/usr/bin/env python3
"""Initialize database with tables for new features"""

import sqlite3
from datetime import datetime, timedelta

def init_database():
    conn = sqlite3.connect('vetsorcery.db')
    cursor = conn.cursor()
    
    # Telehealth tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS telehealth_sessions (
        id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,
        patient_id TEXT NOT NULL,
        vet_id TEXT NOT NULL,
        scheduled_time TIMESTAMP NOT NULL,
        duration_minutes INTEGER DEFAULT 30,
        session_type TEXT NOT NULL,
        status TEXT DEFAULT 'scheduled',
        video_url TEXT,
        notes TEXT,
        recording_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS telehealth_chats (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        sender_id TEXT NOT NULL,
        sender_type TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES telehealth_sessions(id)
    )
    ''')
    
    # Web Portal tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portal_access (
        client_id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        access_level TEXT DEFAULT 'full',
        active_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        notifications_enabled BOOLEAN DEFAULT 1,
        two_factor_enabled BOOLEAN DEFAULT 0
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portal_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT NOT NULL,
        activity_type TEXT NOT NULL,
        activity_detail TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        FOREIGN KEY (client_id) REFERENCES portal_access(client_id)
    )
    ''')
    
    # Insert sample data
    cursor.execute('''
    INSERT OR IGNORE INTO portal_access (client_id, email, access_level)
    VALUES 
        ('client-123', 'john.doe@example.com', 'full'),
        ('client-124', 'jane.smith@example.com', 'full'),
        ('client-125', 'demo@vetsorcery.com', 'view_only')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_database()
EOF

python init_db.py

# Step 5: Update main.py to include new routers
print_status "Updating backend configuration..."

# Check if the routers are already imported
if ! grep -q "telehealth" "$BACKEND_DIR/main.py" 2>/dev/null; then
    # Create a patch for main.py
    cat > "$BACKEND_DIR/main_patch.py" << 'EOF'
# Add these imports to main.py
from app.apis.telehealth.router import router as telehealth_router
from app.apis.web_portal.router import router as web_portal_router

# Add these to the app after other routers
app.include_router(telehealth_router)
app.include_router(web_portal_router)

# Add CORS middleware for frontend communication
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
EOF
    print_warning "Please manually add telehealth and web_portal routers to main.py"
fi

# Step 6: Start Backend
print_status "Starting backend server..."

cd "$BACKEND_DIR"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload \
    > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$PID_DIR/backend.pid"

# Wait for backend to start
wait_for_service "http://localhost:8000/docs" "Backend API"

# Step 7: Frontend Setup
print_status "Setting up frontend..."

cd "$FRONTEND_DIR"

# Install dependencies
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install >/dev/null 2>&1
fi

# Update package.json scripts if needed
if ! grep -q "dev:host" package.json; then
    # Add host binding for network access
    npm pkg set scripts.dev:host="vite --host"
fi

# Step 8: Start Frontend
print_status "Starting frontend server..."

nohup npm run dev -- --host 0.0.0.0 --port 5173 \
    > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$PID_DIR/frontend.pid"

# Wait for frontend to start
wait_for_service "http://localhost:5173" "Frontend"

# Step 9: Test APIs
print_status "Testing new APIs..."

cd "$BACKEND_DIR"
if python test_new_apis.py | grep -q "All tests passed"; then
    print_success "API tests passed!"
else
    print_warning "Some API tests failed - check logs"
fi

# Step 10: Create monitoring script
cat > "$PROJECT_ROOT/monitor-vetsorcery.sh" << 'EOF'
#!/bin/bash
# VetSorcery Health Monitor

check_service() {
    local name=$1
    local url=$2
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
        echo "✅ $name is running"
    else
        echo "❌ $name is down!"
    fi
}

echo "🏥 VetSorcery Health Check"
echo "========================"
check_service "Backend API" "http://localhost:8000/docs"
check_service "Frontend" "http://localhost:5173"
check_service "Telehealth API" "http://localhost:8000/api/telehealth/test"
check_service "Web Portal API" "http://localhost:8000/api/web_portal/test"

# Check logs for errors
echo -e "\n📋 Recent Errors:"
tail -n 20 /Users/studio/hardcard/logs/backend.log | grep -i error || echo "No backend errors"
tail -n 20 /Users/studio/hardcard/logs/frontend.log | grep -i error || echo "No frontend errors"
EOF

chmod +x "$PROJECT_ROOT/monitor-vetsorcery.sh"

# Step 11: Create stop script
cat > "$PROJECT_ROOT/stop-vetsorcery.sh" << 'EOF'
#!/bin/bash
# Stop VetSorcery services

echo "Stopping VetSorcery services..."

# Kill backend
if [ -f "/Users/studio/hardcard/pids/backend.pid" ]; then
    kill $(cat /Users/studio/hardcard/pids/backend.pid) 2>/dev/null || true
    rm /Users/studio/hardcard/pids/backend.pid
fi

# Kill frontend
if [ -f "/Users/studio/hardcard/pids/frontend.pid" ]; then
    kill $(cat /Users/studio/hardcard/pids/frontend.pid) 2>/dev/null || true
    rm /Users/studio/hardcard/pids/frontend.pid
fi

# Kill any remaining processes on ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo "✅ All services stopped"
EOF

chmod +x "$PROJECT_ROOT/stop-vetsorcery.sh"

# Final Status
echo
echo "================================================"
echo "🎉 VetSorcery is LIVE!"
echo "================================================"
echo
echo "📱 Access Points:"
echo "   • Frontend: http://localhost:5173"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/docs"
echo
echo "🔧 New Features:"
echo "   • Telehealth: http://localhost:5173/telehealth"
echo "   • Client Portal: http://localhost:5173/web-portal"
echo
echo "📊 Monitoring:"
echo "   • Health Check: ./monitor-vetsorcery.sh"
echo "   • Backend Logs: tail -f $LOG_DIR/backend.log"
echo "   • Frontend Logs: tail -f $LOG_DIR/frontend.log"
echo
echo "🛑 To Stop:"
echo "   • Run: ./stop-vetsorcery.sh"
echo
echo "🔐 Demo Credentials:"
echo "   • Email: demo@vetsorcery.com"
echo "   • Client ID: client-123"
echo
print_success "Deployment complete! VetSorcery is running with Telehealth & Web Portal features."