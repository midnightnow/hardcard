#!/bin/bash

echo "🚀 Restoring Rich VetSorcery App..."

cd /Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend

# First, let's check if there's a pre-built version
if [ -d "dist" ]; then
    echo "📦 Found pre-built dist folder, serving that..."
    cd dist
    python3 -m http.server 5173 --bind 0.0.0.0
else
    echo "🔧 No dist folder found. Checking for node_modules..."
    
    # Check what dependencies we actually have
    if [ -d "node_modules/react" ] && [ -d "node_modules/react-dom" ]; then
        echo "✅ React dependencies found"
    else
        echo "❌ React dependencies missing"
    fi
    
    # Try to serve with a development server
    echo "🌐 Starting development server..."
    
    # Create a simple server that can handle modules
    cat > serve-dev.py << 'EOF'
import http.server
import socketserver
import os
import mimetypes

# Add proper MIME types
mimetypes.add_type('application/javascript', '.tsx')
mimetypes.add_type('application/javascript', '.ts')
mimetypes.add_type('application/javascript', '.jsx')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('text/javascript', '.mjs')

class DevServerHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS and module headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()
    
    def do_GET(self):
        # Handle module imports
        if self.path.startswith('/@'):
            self.send_error(404, "Module not found")
            return
            
        # Serve index.html for SPA routes
        if not os.path.exists(self.path.lstrip('/')) and '.' not in self.path:
            self.path = '/index.html'
        
        return super().do_GET()

PORT = 5173
print(f"🚀 VetSorcery Development Server starting on http://localhost:{PORT}")
print("⚠️  Note: This is a fallback server. Full functionality requires proper Vite setup.")

with socketserver.TCPServer(("0.0.0.0", PORT), DevServerHandler) as httpd:
    httpd.serve_forever()
EOF

    python3 serve-dev.py
fi