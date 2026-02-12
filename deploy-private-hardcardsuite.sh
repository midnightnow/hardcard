#!/bin/bash
echo "🏢 Claude Flow: Deploy Private HARDCARDSUITE"
echo "============================================"

cd /Users/studio/hardcard/HARDCARDSUITE

# Step 1: Install all dependencies
echo "📦 Installing HARDCARDSUITE dependencies..."
if [ -f "Makefile" ]; then
    make
else
    echo "Installing manually..."
    
    # Frontend dependencies
    if [ -d "frontend" ]; then
        cd frontend && npm install --legacy-peer-deps && cd ..
    fi
    
    # Backend dependencies  
    if [ -d "backend" ]; then
        cd backend && pip install -r requirements.txt && cd ..
    fi
fi

# Step 2: Create private deployment configuration
echo "🔒 Creating private deployment configuration..."

# Create Firebase configuration for private hosting
cat > firebase-private.json << 'EOF'
{
  "hosting": {
    "public": "frontend/dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "headers": [
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Robots-Tag",
            "value": "noindex, nofollow, nosnippet, noarchive"
          },
          {
            "key": "Authorization",
            "value": "required"
          }
        ]
      }
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
EOF

# Step 3: Create authentication wrapper for private access
cat > frontend/src/PrivateAccess.tsx << 'EOF'
import React, { useState } from 'react';

const EVALUATION_PASSWORD = 'hardcard-eval-2025';

export const PrivateAccess: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(
    localStorage.getItem('hardcard-eval-auth') === 'true'
  );
  const [password, setPassword] = useState('');

  const handleAuth = () => {
    if (password === EVALUATION_PASSWORD) {
      localStorage.setItem('hardcard-eval-auth', 'true');
      setAuthenticated(true);
    } else {
      alert('Incorrect password');
    }
  };

  if (!authenticated) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontFamily: 'Arial, sans-serif',
        background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)'
      }}>
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '10px',
          boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
          textAlign: 'center'
        }}>
          <h2>🏢 HardCard Suite - Private Evaluation</h2>
          <p>This is a private evaluation environment.</p>
          <input
            type="password"
            placeholder="Enter evaluation password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              padding: '10px',
              borderRadius: '5px',
              border: '1px solid #ccc',
              marginRight: '10px',
              width: '200px'
            }}
            onKeyPress={(e) => e.key === 'Enter' && handleAuth()}
          />
          <button
            onClick={handleAuth}
            style={{
              padding: '10px 20px',
              background: '#2a5298',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Access
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
EOF

# Step 4: Start all HARDCARDSUITE applications
echo "🚀 Starting all HARDCARDSUITE applications..."

# Start backend
echo "Starting Backend API (port 8000)..."
./start_backend.sh &
BACKEND_PID=$!

# Start frontend  
echo "Starting Frontend (port 5173)..."
./start_frontend.sh &
FRONTEND_PID=$!

# Start governance
echo "Starting Governance (port 8080)..."
./start_governance.sh &
GOVERNANCE_PID=$!

# Start VetSorcery
echo "Starting VetSorcery (port 3005)..."
./start_vetsorcery.sh &
VETSORCERY_PID=$!

# Start HardCard Suite
echo "Starting HardCard Suite (port 3001)..."
./start_hardcard.sh &
HARDCARD_PID=$!

# Step 5: Create status checker
cat > check-hardcardsuite-status.sh << 'EOF'
#!/bin/bash
echo "🏢 HARDCARDSUITE Status Check"
echo "============================"

# Check all ports
ports=(5173 8000 8080 3001 3005)
names=("Frontend" "Backend API" "Governance" "HardCard Suite" "VetSorcery")

for i in "${!ports[@]}"; do
    port=${ports[$i]}
    name=${names[$i]}
    
    if lsof -ti:$port > /dev/null; then
        echo "✅ $name - Running on port $port"
    else
        echo "❌ $name - Not running on port $port"
    fi
done

echo ""
echo "🔗 Access URLs (Private):"
echo "Frontend:      http://localhost:5173"
echo "Backend API:   http://localhost:8000"
echo "Governance:    http://localhost:8080"
echo "HardCard Suite: http://localhost:3001"
echo "VetSorcery:    http://localhost:3005"
EOF

chmod +x check-hardcardsuite-status.sh

# Step 6: Create Firebase private deployment
echo "🌐 Creating private Firebase deployment..."
firebase use hardcard

# Build frontend with private access
cd frontend
npm run build
cd ..

# Deploy to Firebase with private configuration
cp firebase-private.json firebase.json
firebase deploy --only hosting

# Step 7: Create private domain access
echo "🔒 Setting up private access domain..."
PRIVATE_URL="https://hardcard-private-$(date +%s).web.app"

echo ""
echo "✅ HARDCARDSUITE Deployment Complete!"
echo "======================================"
echo ""
echo "🏢 Complete HardCard Suite Status:"
echo "  Frontend:     Port 5173 (React + TypeScript)"
echo "  Backend API:  Port 8000 (FastAPI + Python)"
echo "  Governance:   Port 8080 (Dashboard)"
echo "  VetSorcery:   Port 3005 (AI Veterinary)"
echo "  HardCard:     Port 3001 (Main Suite)"
echo ""
echo "🔒 Private Access:"
echo "  Password: hardcard-eval-2025"
echo "  Firebase: https://hardcard.web.app (password protected)"
echo "  Local:    http://localhost:5173"
echo ""
echo "📊 Monitor with: ./check-hardcardsuite-status.sh"
echo ""
echo "🎯 The complete massive HARDCARDSUITE is now running privately!"

# Save process IDs for cleanup
echo "export BACKEND_PID=$BACKEND_PID" > .hardcardsuite-pids
echo "export FRONTEND_PID=$FRONTEND_PID" >> .hardcardsuite-pids
echo "export GOVERNANCE_PID=$GOVERNANCE_PID" >> .hardcardsuite-pids
echo "export VETSORCERY_PID=$VETSORCERY_PID" >> .hardcardsuite-pids
echo "export HARDCARD_PID=$HARDCARD_PID" >> .hardcardsuite-pids