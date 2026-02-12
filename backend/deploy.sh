#!/bin/bash
set -e

echo "🚀 HardCard Universal OS - Production Backend Deployment"
echo "Target Revenue: $495K+ Monthly Recurring Revenue"
echo "=========================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="hardcard-universal-os"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check requirements
check_requirements() {
    print_status "Checking deployment requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

# Create environment file if it doesn't exist
create_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_status "Creating environment file..."
        cat > "$ENV_FILE" << 'EOF'
# Database Configuration
POSTGRES_PASSWORD=secure_hardcard_password_$(date +%s)

# JWT Secret
JWT_SECRET=super_secure_jwt_secret_$(openssl rand -base64 32)

# Firebase Configuration
FIREBASE_PROJECT_ID=hardcard-universal-os
FIREBASE_CREDENTIALS_PATH=/app/credentials/firebase-key.json

# Twilio Configuration (VetSorcery)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key

# Visual Encoding Encryption Key
VISUAL_ENCODING_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Grafana Configuration
GRAFANA_PASSWORD=admin_$(openssl rand -base64 12)

# Base URL
BASE_URL=https://api.hardcard.co
EOF
        print_success "Environment file created at $ENV_FILE"
        print_warning "Please update the configuration values in $ENV_FILE before deployment"
    else
        print_status "Environment file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p credentials
    mkdir -p nginx/conf.d
    mkdir -p ssl
    mkdir -p grafana/dashboards
    mkdir -p grafana/datasources
    mkdir -p logs
    
    print_success "Directories created"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certs() {
    print_status "Generating SSL certificates..."
    
    if [ ! -f "ssl/server.crt" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/server.key \
            -out ssl/server.crt \
            -subj "/C=US/ST=State/L=City/O=HardCard/CN=localhost"
        
        print_success "SSL certificates generated"
    else
        print_status "SSL certificates already exist"
    fi
}

# Create nginx configuration
create_nginx_config() {
    print_status "Creating nginx configuration..."
    
    cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream api_gateway {
        server api-gateway:8000;
    }
    
    upstream vetsorcery {
        server vetsorcery-service:8001;
    }
    
    upstream macagent {
        server macagent-service:8002;
    }
    
    upstream alexandria {
        server alexandria-service:8003;
    }
    
    upstream visual_encoding {
        server visual-encoding-service:8004;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;

    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name _;
        
        ssl_certificate /etc/nginx/ssl/server.crt;
        ssl_certificate_key /etc/nginx/ssl/server.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Main API routes
        location /api/v1/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_gateway;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # WebSocket support
        location /ws/ {
            proxy_pass http://api_gateway;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health checks
        location /health {
            proxy_pass http://api_gateway/api/v1/health;
            access_log off;
        }
        
        # Metrics for Prometheus
        location /metrics {
            proxy_pass http://api_gateway/metrics;
            allow 172.20.0.0/16;  # Docker network
            deny all;
        }
        
        # File uploads (with larger body size)
        location /api/v1/upload {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://api_gateway;
            client_max_body_size 100M;
            proxy_request_buffering off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
    
    print_success "Nginx configuration created"
}

# Create Prometheus configuration
create_prometheus_config() {
    print_status "Creating Prometheus configuration..."
    
    cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  external_labels:
    monitor: 'hardcard-monitor'

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'vetsorcery'
    static_configs:
      - targets: ['vetsorcery-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'macagent'
    static_configs:
      - targets: ['macagent-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'alexandria'
    static_configs:
      - targets: ['alexandria-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'visual-encoding'
    static_configs:
      - targets: ['visual-encoding-service:8004']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    scrape_interval: 15s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 15s
EOF
    
    print_success "Prometheus configuration created"
}

# Create Grafana datasource configuration
create_grafana_config() {
    print_status "Creating Grafana configuration..."
    
    mkdir -p grafana/datasources grafana/dashboards
    
    cat > grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    cat > grafana/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF
    
    print_success "Grafana configuration created"
}

# Build and deploy services
deploy_services() {
    print_status "Building and deploying services..."
    
    # Pull latest images
    docker-compose pull --ignore-pull-failures || true
    
    # Build services
    docker-compose build --no-cache
    
    # Deploy services
    docker-compose up -d
    
    print_success "Services deployed"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    services=("api-gateway" "vetsorcery-service" "macagent-service" "alexandria-service" "visual-encoding-service")
    
    for service in "${services[@]}"; do
        print_status "Waiting for $service to be healthy..."
        
        for i in {1..30}; do
            if docker-compose exec -T "$service" curl -f http://localhost:800$((${#service} % 10))/api/v1/health > /dev/null 2>&1; then
                print_success "$service is healthy"
                break
            fi
            
            if [ $i -eq 30 ]; then
                print_error "$service failed to become healthy"
                exit 1
            fi
            
            sleep 10
        done
    done
    
    print_success "All services are healthy"
}

# Run system tests
run_tests() {
    print_status "Running system tests..."
    
    # Test API Gateway
    if curl -f -s https://localhost/api/v1/health > /dev/null; then
        print_success "API Gateway health check passed"
    else
        print_error "API Gateway health check failed"
    fi
    
    # Test each microservice
    services=(
        "vetsorcery:8001"
        "macagent:8002"
        "alexandria:8003"
        "visual-encoding:8004"
    )
    
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -f -s "https://localhost/api/v1/$name/health" > /dev/null; then
            print_success "$name service test passed"
        else
            print_warning "$name service test failed (may not be fully initialized)"
        fi
    done
    
    print_success "System tests completed"
}

# Display deployment summary
show_summary() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}🎉 HardCard Universal OS Deployment Complete!${NC}"
    echo "=========================================="
    echo ""
    echo "🌐 Services Available:"
    echo "  - API Gateway:      https://localhost/api/v1/"
    echo "  - VetSorcery:       https://localhost/api/v1/vetsorcery/"
    echo "  - MacAgent Pro:     https://localhost/api/v1/macagent/"
    echo "  - Alexandria:       https://localhost/api/v1/alexandria/"
    echo "  - Visual Encoding:  https://localhost/api/v1/visual-encoding/"
    echo ""
    echo "📊 Monitoring:"
    echo "  - Grafana:          http://localhost:3000"
    echo "  - Prometheus:       http://localhost:9090"
    echo ""
    echo "💰 Revenue Targets:"
    echo "  - VetSorcery:       $150,000/month"
    echo "  - MacAgent Pro:     $200,000/month"
    echo "  - Alexandria:       $100,000/month"
    echo "  - Visual Encoding:  $45,000/month"
    echo "  - Total Target:     $495,000/month"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Update environment variables in $ENV_FILE"
    echo "  2. Add Firebase credentials to credentials/"
    echo "  3. Configure external services (Twilio, Stripe, etc.)"
    echo "  4. Set up domain and SSL certificates"
    echo "  5. Configure monitoring alerts"
    echo ""
    echo "🔧 Management Commands:"
    echo "  - View logs:        docker-compose logs -f"
    echo "  - Stop services:    docker-compose down"
    echo "  - Update services:  docker-compose pull && docker-compose up -d"
    echo "  - Scale services:   docker-compose up -d --scale api-gateway=3"
    echo ""
}

# Main deployment flow
main() {
    print_status "Starting HardCard Universal OS deployment..."
    
    check_requirements
    create_env_file
    create_directories
    generate_ssl_certs
    create_nginx_config
    create_prometheus_config
    create_grafana_config
    deploy_services
    wait_for_services
    run_tests
    show_summary
    
    print_success "Deployment completed successfully!"
}

# Handle script interruption
trap 'print_error "Deployment interrupted"; exit 1' INT

# Run main function
main "$@"