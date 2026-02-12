#!/usr/bin/env python3
"""
HardCard World Deployment Configuration & Security Headers
Complete deployment setup for HardCard World platform
"""

import os
import json
import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HardCardWorldDeployment:
    """Complete deployment configuration for HardCard World"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.base_path = Path(__file__).parent
        self.project_name = "hardcard-world"
        
        # Deployment configurations
        self.domains = {
            "production": ["hardcard.world", "www.hardcard.world"],
            "staging": ["staging.hardcard.world"],
            "development": ["localhost:3000"]
        }
        
        # Security headers configuration
        self.security_headers = {
            "production": {
                "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
                "Content-Security-Policy": self._get_csp_policy(),
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": self._get_permissions_policy(),
                "Cross-Origin-Embedder-Policy": "require-corp",
                "Cross-Origin-Opener-Policy": "same-origin",
                "Cross-Origin-Resource-Policy": "same-origin"
            }
        }
    
    def _get_csp_policy(self) -> str:
        """Generate Content Security Policy"""
        if self.environment == "production":
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https://api.hardcard.world https://auth.hardcard.world wss://hardcard.world; "
                "media-src 'self' blob:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            )
        else:
            # More permissive for development
            return (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
                "connect-src 'self' ws://localhost:* http://localhost:* https:; "
                "img-src 'self' data: https: blob:; "
                "media-src 'self' blob:;"
            )
    
    def _get_permissions_policy(self) -> str:
        """Generate Permissions Policy"""
        return (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "cross-origin-isolated=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "execution-while-not-rendered=(), "
            "execution-while-out-of-viewport=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "navigation-override=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )
    
    def generate_firebase_config(self) -> Dict[str, Any]:
        """Generate Firebase hosting configuration"""
        config = {
            "hosting": {
                "public": "public",
                "ignore": [
                    "firebase.json",
                    "**/.*",
                    "**/node_modules/**",
                    ".git/**",
                    ".env*",
                    "*.md",
                    "*.log",
                    "*.bak",
                    "package-lock.json",
                    "yarn.lock"
                ],
                "cleanUrls": True,
                "trailingSlash": False,
                "redirects": [
                    {
                        "source": "/old-path/**",
                        "destination": "/new-path/:splat",
                        "type": 301
                    },
                    {
                        "source": "/hardcard-world",
                        "destination": "/",
                        "type": 301
                    }
                ],
                "rewrites": [
                    {
                        "source": "/api/**",
                        "function": "api"
                    },
                    {
                        "source": "/auth/**",
                        "run": {
                            "serviceId": "hardcard-auth-service",
                            "region": "us-central1"
                        }
                    },
                    {
                        "source": "**",
                        "destination": "/index.html"
                    }
                ],
                "headers": self._generate_firebase_headers()
            },
            "functions": {
                "source": "functions",
                "runtime": "nodejs18",
                "predeploy": [
                    "npm --prefix \"$RESOURCE_DIR\" run build"
                ]
            },
            "firestore": {
                "rules": "firestore.rules",
                "indexes": "firestore.indexes.json"
            },
            "storage": {
                "rules": "storage.rules"
            },
            "emulators": {
                "auth": {"port": 9099},
                "functions": {"port": 5001},
                "firestore": {"port": 8080},
                "hosting": {"port": 5000},
                "ui": {"enabled": True}
            }
        }
        
        return config
    
    def _generate_firebase_headers(self) -> List[Dict[str, Any]]:
        """Generate Firebase headers configuration"""
        headers = []
        
        # Security headers for all routes
        headers.append({
            "source": "**",
            "headers": [
                {"key": key, "value": value}
                for key, value in self.security_headers[self.environment].items()
            ]
        })
        
        # API-specific headers
        headers.append({
            "source": "/api/**",
            "headers": [
                {"key": "Access-Control-Allow-Origin", "value": f"https://{self.domains[self.environment][0]}"},
                {"key": "Access-Control-Allow-Methods", "value": "GET, POST, PUT, DELETE, OPTIONS"},
                {"key": "Access-Control-Allow-Headers", "value": "Content-Type, Authorization, X-Requested-With"},
                {"key": "Access-Control-Max-Age", "value": "86400"},
                {"key": "Vary", "value": "Accept-Encoding, Origin"},
            ]
        })
        
        # Static asset caching
        headers.append({
            "source": "**/*.@(js|css|woff|woff2|ttf|eot)",
            "headers": [
                {"key": "Cache-Control", "value": "max-age=31536000, immutable"},
                {"key": "Vary", "value": "Accept-Encoding"}
            ]
        })
        
        headers.append({
            "source": "**/*.@(jpg|jpeg|png|gif|ico|svg|webp|avif)",
            "headers": [
                {"key": "Cache-Control", "value": "max-age=31536000, immutable"},
                {"key": "Vary", "value": "Accept-Encoding"}
            ]
        })
        
        # HTML caching (shorter for dynamic content)
        headers.append({
            "source": "**/*.html",
            "headers": [
                {"key": "Cache-Control", "value": "max-age=3600, must-revalidate"},
                {"key": "Vary", "value": "Accept-Encoding"}
            ]
        })
        
        # Service Worker caching
        headers.append({
            "source": "/sw.js",
            "headers": [
                {"key": "Cache-Control", "value": "max-age=0, no-cache, no-store, must-revalidate"},
                {"key": "Pragma", "value": "no-cache"},
                {"key": "Expires", "value": "0"}
            ]
        })
        
        return headers
    
    def generate_nginx_config(self) -> str:
        """Generate Nginx configuration for reverse proxy setup"""
        config = f"""
# HardCard World Nginx Configuration
# Generated on {datetime.now().isoformat()}

upstream hardcard_backend {{
    server 127.0.0.1:8000;
    server 127.0.0.1:8001 backup;
    keepalive 32;
}}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;

# Redirect HTTP to HTTPS
server {{
    listen 80;
    server_name {' '.join(self.domains[self.environment])};
    return 301 https://$server_name$request_uri;
}}

# Main HTTPS server
server {{
    listen 443 ssl http2;
    server_name {' '.join(self.domains[self.environment])};
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/hardcard.world/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hardcard.world/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "{self.security_headers[self.environment]['Strict-Transport-Security']}" always;
    add_header Content-Security-Policy "{self.security_headers[self.environment]['Content-Security-Policy']}" always;
    add_header X-Content-Type-Options "{self.security_headers[self.environment]['X-Content-Type-Options']}" always;
    add_header X-Frame-Options "{self.security_headers[self.environment]['X-Frame-Options']}" always;
    add_header X-XSS-Protection "{self.security_headers[self.environment]['X-XSS-Protection']}" always;
    add_header Referrer-Policy "{self.security_headers[self.environment]['Referrer-Policy']}" always;
    add_header Permissions-Policy "{self.security_headers[self.environment]['Permissions-Policy']}" always;
    
    # Rate limiting
    limit_req zone=api burst=20 nodelay;
    limit_conn conn_limit_per_ip 10;
    
    # Root directory
    root /var/www/hardcard-world;
    index index.html;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # API routes
    location /api/ {{
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://hardcard_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
        proxy_send_timeout 30s;
    }}
    
    # Authentication routes
    location /auth/ {{
        limit_req zone=auth burst=5 nodelay;
        proxy_pass http://hardcard_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # WebSocket support
    location /ws/ {{
        proxy_pass http://hardcard_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }}
    
    # Static files with caching
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
        access_log off;
    }}
    
    # HTML files
    location ~* \\.html$ {{
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
        add_header Vary "Accept-Encoding";
    }}
    
    # Service worker (no cache)
    location /sw.js {{
        expires 0;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
    }}
    
    # SPA fallback
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    # Security: Hide sensitive files
    location ~ /\\. {{
        deny all;
    }}
    
    location ~ \\.(env|json|md|log|bak)$ {{
        deny all;
    }}
    
    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}}
"""
        return config.strip()
    
    def generate_docker_config(self) -> Dict[str, str]:
        """Generate Docker configuration files"""
        dockerfile = f"""
# HardCard World Production Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install security updates
RUN apk update && apk upgrade

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add non-root user
RUN addgroup -g 1001 -S hardcard && \\
    adduser -S hardcard -u 1001

# Set ownership
RUN chown -R hardcard:hardcard /usr/share/nginx/html

# Switch to non-root user
USER hardcard

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \\
  CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
"""

        docker_compose = f"""
# HardCard World Docker Compose
version: '3.8'

services:
  hardcard-world:
    build: .
    ports:
      - "80:80"
      - "443:443"
    environment:
      - NODE_ENV={self.environment}
      - DOMAIN=hardcard.world
    volumes:
      - ./ssl:/etc/ssl/certs:ro
      - ./logs:/var/log/nginx
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.hardcard-world.rule=Host(`hardcard.world`)"
      - "traefik.http.routers.hardcard-world.tls=true"
      - "traefik.http.routers.hardcard-world.tls.certresolver=letsencrypt"

  hardcard-backend:
    image: hardcard-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT={self.environment}
      - DATABASE_URL=${{DATABASE_URL}}
      - REDIS_URL=${{REDIS_URL}}
    restart: unless-stopped
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=hardcard_world
      - POSTGRES_USER=hardcard
      - POSTGRES_PASSWORD=${{POSTGRES_PASSWORD}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
"""

        return {
            "Dockerfile": dockerfile.strip(),
            "docker-compose.yml": docker_compose.strip()
        }
    
    def generate_kubernetes_config(self) -> Dict[str, str]:
        """Generate Kubernetes deployment configuration"""
        deployment = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hardcard-world
  namespace: hardcard
  labels:
    app: hardcard-world
    environment: {self.environment}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: hardcard-world
  template:
    metadata:
      labels:
        app: hardcard-world
    spec:
      containers:
      - name: hardcard-world
        image: hardcard-world:{self.environment}
        ports:
        - containerPort: 80
        env:
        - name: NODE_ENV
          value: "{self.environment}"
        - name: DOMAIN
          value: "hardcard.world"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          runAsNonRoot: true
          runAsUser: 1001
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
---
apiVersion: v1
kind: Service
metadata:
  name: hardcard-world-service
  namespace: hardcard
spec:
  selector:
    app: hardcard-world
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hardcard-world-ingress
  namespace: hardcard
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - hardcard.world
    - www.hardcard.world
    secretName: hardcard-world-tls
  rules:
  - host: hardcard.world
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hardcard-world-service
            port:
              number: 80
"""

        return {"deployment.yaml": deployment.strip()}
    
    def generate_github_actions_workflow(self) -> str:
        """Generate GitHub Actions CI/CD workflow"""
        workflow = f"""
name: Deploy HardCard World

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '18'
  REGISTRY: ghcr.io
  IMAGE_NAME: hardcard-world

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{{{ env.NODE_VERSION }}}}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Run security audit
      run: npm audit --audit-level=high
    
    - name: Build application
      run: npm run build
    
    - name: Run deployment readiness check
      run: python3 hardcard_world_deployment_config.py --validate

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  deploy-staging:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{{{ env.NODE_VERSION }}}}
        cache: 'npm'
    
    - name: Build for staging
      run: |
        npm ci
        npm run build:staging
    
    - name: Deploy to Firebase Hosting (Staging)
      uses: FirebaseExtended/action-hosting-deploy@v0
      with:
        repoToken: '${{{{ secrets.GITHUB_TOKEN }}}}'
        firebaseServiceAccount: '${{{{ secrets.FIREBASE_SERVICE_ACCOUNT_STAGING }}}}'
        projectId: hardcard-world-staging
        channelId: live

  deploy-production:
    needs: [deploy-staging]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{{{ env.NODE_VERSION }}}}
        cache: 'npm'
    
    - name: Build for production
      run: |
        npm ci
        npm run build:production
    
    - name: Run production security checks
      run: |
        python3 hardcard_world_deployment_config.py --security-check
        npm run security:headers-test
    
    - name: Deploy to Firebase Hosting (Production)
      uses: FirebaseExtended/action-hosting-deploy@v0
      with:
        repoToken: '${{{{ secrets.GITHUB_TOKEN }}}}'
        firebaseServiceAccount: '${{{{ secrets.FIREBASE_SERVICE_ACCOUNT_PRODUCTION }}}}'
        projectId: hardcard-world-production
        channelId: live
    
    - name: Run post-deployment tests
      run: |
        npm run test:e2e:production
        python3 hardcard_world_audit.py --quick-check
    
    - name: Notify deployment success
      uses: 8398a7/action-slack@v3
      with:
        status: success
        channel: '#deployments'
      env:
        SLACK_WEBHOOK_URL: '${{{{ secrets.SLACK_WEBHOOK }}}}'
"""

        return workflow.strip()
    
    def generate_security_checklist(self) -> Dict[str, Any]:
        """Generate security deployment checklist"""
        checklist = {
            "security_checklist": {
                "headers": {
                    "description": "Security headers configuration",
                    "items": [
                        {
                            "check": "HSTS enabled with preload",
                            "status": "✅",
                            "details": "Strict-Transport-Security header with preload directive"
                        },
                        {
                            "check": "CSP policy configured",
                            "status": "✅",
                            "details": "Content Security Policy prevents XSS attacks"
                        },
                        {
                            "check": "X-Frame-Options set to DENY",
                            "status": "✅",
                            "details": "Prevents clickjacking attacks"
                        },
                        {
                            "check": "X-Content-Type-Options nosniff",
                            "status": "✅",
                            "details": "Prevents MIME type sniffing attacks"
                        },
                        {
                            "check": "Permissions-Policy configured",
                            "status": "✅",
                            "details": "Restricts access to browser APIs"
                        }
                    ]
                },
                "ssl_tls": {
                    "description": "SSL/TLS configuration",
                    "items": [
                        {
                            "check": "TLS 1.2+ only",
                            "status": "✅",
                            "details": "Disabled older TLS versions"
                        },
                        {
                            "check": "Strong cipher suites",
                            "status": "✅",
                            "details": "Using ECDHE and AES-GCM ciphers"
                        },
                        {
                            "check": "Certificate chain valid",
                            "status": "⏳",
                            "details": "Verify with SSL Labs test"
                        }
                    ]
                },
                "access_control": {
                    "description": "Access control and authentication",
                    "items": [
                        {
                            "check": "Rate limiting configured",
                            "status": "✅",
                            "details": "API and auth endpoints rate limited"
                        },
                        {
                            "check": "CORS properly configured",
                            "status": "✅",
                            "details": "Origins restricted to hardcard.world"
                        },
                        {
                            "check": "Authentication required for sensitive endpoints",
                            "status": "⏳",
                            "details": "Verify all admin/user endpoints protected"
                        }
                    ]
                },
                "infrastructure": {
                    "description": "Infrastructure security",
                    "items": [
                        {
                            "check": "Non-root user in containers",
                            "status": "✅",
                            "details": "Running as user ID 1001"
                        },
                        {
                            "check": "Security contexts configured",
                            "status": "✅",
                            "details": "Kubernetes security contexts set"
                        },
                        {
                            "check": "Secrets management",
                            "status": "⏳",
                            "details": "Verify no secrets in environment variables"
                        }
                    ]
                }
            },
            "deployment_checklist": {
                "pre_deployment": [
                    "Run security scan with Trivy",
                    "Validate all environment variables",
                    "Test SSL certificate installation",
                    "Verify DNS configuration",
                    "Run load testing"
                ],
                "post_deployment": [
                    "Test all major user flows",
                    "Verify security headers with curl",
                    "Check SSL Labs score (A+ target)",
                    "Monitor error rates",
                    "Validate CDN caching"
                ],
                "monitoring": [
                    "Set up uptime monitoring",
                    "Configure error alerting",
                    "Monitor performance metrics",
                    "Set up security incident alerts",
                    "Regular security scans"
                ]
            }
        }
        
        return checklist
    
    def validate_configuration(self) -> bool:
        """Validate deployment configuration"""
        logger.info("🔍 Validating HardCard World deployment configuration...")
        
        issues = []
        
        # Check required directories
        required_dirs = ["public", "functions", "src"]
        for directory in required_dirs:
            if not (self.base_path / directory).exists():
                issues.append(f"Missing required directory: {directory}")
        
        # Validate security headers
        csp_policy = self._get_csp_policy()
        if "unsafe-eval" in csp_policy and self.environment == "production":
            issues.append("CSP contains 'unsafe-eval' in production")
        
        # Check environment configuration
        if self.environment == "production":
            required_env = ["SSL_CERT_PATH", "SSL_KEY_PATH", "DATABASE_URL"]
            for env_var in required_env:
                if not os.getenv(env_var):
                    issues.append(f"Missing environment variable: {env_var}")
        
        if issues:
            logger.error(f"❌ Configuration validation failed:")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("✅ Configuration validation passed")
        return True
    
    def run_security_check(self) -> bool:
        """Run comprehensive security check"""
        logger.info("🔒 Running security checks...")
        
        security_issues = []
        
        # Check for common security issues
        security_checks = [
            {
                "name": "Environment variables",
                "check": lambda: not any(key.startswith("API_KEY") for key in os.environ.keys() if "test" not in key.lower()),
                "message": "API keys found in environment variables"
            },
            {
                "name": "Debug mode",
                "check": lambda: os.getenv("DEBUG", "false").lower() != "true",
                "message": "Debug mode enabled in production"
            },
            {
                "name": "Default credentials",
                "check": lambda: os.getenv("ADMIN_PASSWORD", "").lower() not in ["admin", "password", "123456"],
                "message": "Default/weak admin credentials detected"
            }
        ]
        
        for check in security_checks:
            try:
                if not check["check"]():
                    security_issues.append(f"{check['name']}: {check['message']}")
            except Exception as e:
                security_issues.append(f"{check['name']}: Check failed - {str(e)}")
        
        if security_issues:
            logger.error("❌ Security check failed:")
            for issue in security_issues:
                logger.error(f"  - {issue}")
            return False
        
        logger.info("✅ Security check passed")
        return True
    
    def deploy(self, target: str = "firebase") -> bool:
        """Deploy HardCard World"""
        logger.info(f"🚀 Deploying HardCard World to {target}...")
        
        try:
            if target == "firebase":
                # Generate and write Firebase config
                firebase_config = self.generate_firebase_config()
                with open("firebase.json", "w") as f:
                    json.dump(firebase_config, f, indent=2)
                
                # Deploy to Firebase
                subprocess.run(["firebase", "deploy", "--only", "hosting"], check=True)
                
            elif target == "docker":
                # Generate Docker files
                docker_configs = self.generate_docker_config()
                for filename, content in docker_configs.items():
                    with open(filename, "w") as f:
                        f.write(content)
                
                # Build and run Docker
                subprocess.run(["docker", "build", "-t", "hardcard-world", "."], check=True)
                subprocess.run(["docker-compose", "up", "-d"], check=True)
                
            elif target == "kubernetes":
                # Generate Kubernetes config
                k8s_configs = self.generate_kubernetes_config()
                for filename, content in k8s_configs.items():
                    with open(f"k8s-{filename}", "w") as f:
                        f.write(content)
                
                # Apply Kubernetes config
                subprocess.run(["kubectl", "apply", "-f", "k8s-deployment.yaml"], check=True)
                
            logger.info(f"✅ Deployment to {target} completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Deployment failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Deployment error: {str(e)}")
            return False
    
    def generate_all_configs(self, output_dir: Path = None) -> bool:
        """Generate all deployment configuration files"""
        if output_dir is None:
            output_dir = self.base_path / "deployment_configs"
        
        output_dir.mkdir(exist_ok=True)
        
        try:
            logger.info(f"📁 Generating deployment configs in {output_dir}")
            
            # Firebase configuration
            firebase_config = self.generate_firebase_config()
            with open(output_dir / "firebase.json", "w") as f:
                json.dump(firebase_config, f, indent=2)
            
            # Nginx configuration
            nginx_config = self.generate_nginx_config()
            with open(output_dir / "nginx.conf", "w") as f:
                f.write(nginx_config)
            
            # Docker configurations
            docker_configs = self.generate_docker_config()
            for filename, content in docker_configs.items():
                with open(output_dir / filename, "w") as f:
                    f.write(content)
            
            # Kubernetes configuration
            k8s_configs = self.generate_kubernetes_config()
            for filename, content in k8s_configs.items():
                with open(output_dir / filename, "w") as f:
                    f.write(content)
            
            # GitHub Actions workflow
            workflow = self.generate_github_actions_workflow()
            workflow_dir = output_dir / ".github" / "workflows"
            workflow_dir.mkdir(parents=True, exist_ok=True)
            with open(workflow_dir / "deploy.yml", "w") as f:
                f.write(workflow)
            
            # Security checklist
            security_checklist = self.generate_security_checklist()
            with open(output_dir / "security_checklist.json", "w") as f:
                json.dump(security_checklist, f, indent=2)
            
            logger.info("✅ All deployment configurations generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate configurations: {str(e)}")
            return False


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HardCard World Deployment Configuration")
    parser.add_argument("--environment", choices=["development", "staging", "production"], default="production")
    parser.add_argument("--generate-configs", action="store_true", help="Generate all configuration files")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--security-check", action="store_true", help="Run security checks")
    parser.add_argument("--deploy", choices=["firebase", "docker", "kubernetes"], help="Deploy to target")
    parser.add_argument("--output-dir", type=Path, help="Output directory for configs")
    
    args = parser.parse_args()
    
    # Initialize deployment manager
    deployment = HardCardWorldDeployment(environment=args.environment)
    
    print(f"🌍 HardCard World Deployment Configuration")
    print(f"Environment: {args.environment}")
    print(f"Domains: {', '.join(deployment.domains[args.environment])}")
    print("="*60)
    
    success = True
    
    if args.validate:
        success &= deployment.validate_configuration()
    
    if args.security_check:
        success &= deployment.run_security_check()
    
    if args.generate_configs:
        success &= deployment.generate_all_configs(args.output_dir)
    
    if args.deploy:
        success &= deployment.deploy(args.deploy)
    
    if not any([args.validate, args.security_check, args.generate_configs, args.deploy]):
        # Default action - generate all configs
        success &= deployment.generate_all_configs(args.output_dir)
    
    if success:
        print("\n✅ HardCard World deployment configuration completed successfully!")
    else:
        print("\n❌ HardCard World deployment configuration failed!")
        exit(1)


if __name__ == "__main__":
    main()