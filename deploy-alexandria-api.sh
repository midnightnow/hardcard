#!/bin/bash
# Alexandria Safety API - Cloud Run Deployment Script

echo "🚀 Alexandria Safety API - Cloud Run Deployment"
echo "=============================================="

# Set variables
PROJECT_ID=${PROJECT_ID:-"hardcard-firebase-studio"}
SERVICE_NAME="alexandria-api"
REGION="us-central1"
SOURCE_DIR="/Users/studio/hardcard"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo_error "gcloud CLI not found. Please install it:"
    echo "  brew install google-cloud-sdk"
    echo "  OR visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check authentication
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
    echo_warn "Not authenticated with gcloud. Running auth flow..."
    gcloud auth login
fi

# Set project
echo_info "Setting project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo_info "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create secrets if they don't exist
echo_info "Setting up secrets..."
echo "jwt-secret-key-$(date +%s)" | gcloud secrets create jwt-secret --data-file=- --quiet 2>/dev/null || echo_warn "JWT secret already exists"

# Deploy to Cloud Run
echo_info "Deploying Alexandria Safety API to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source=$SOURCE_DIR \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --set-env-vars="ENV=production,PROJECT_ID=$PROJECT_ID" \
    --set-secrets="JWT_SECRET=jwt-secret:latest" \
    --cpu=2 \
    --memory=2Gi \
    --min-instances=0 \
    --max-instances=10 \
    --port=8080 \
    --timeout=300s

if [ $? -eq 0 ]; then
    echo_info "✅ Deployment successful!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    echo_info "Service URL: $SERVICE_URL"
    
    # Test the deployment
    echo_info "Testing deployment..."
    echo "Health check:"
    curl -s "$SERVICE_URL/healthz" | jq . || echo "Health check response (raw): $(curl -s $SERVICE_URL/healthz)"
    
    echo ""
    echo "Readiness check:"
    curl -s "$SERVICE_URL/readyz" | jq . || echo "Readiness check response (raw): $(curl -s $SERVICE_URL/readyz)"
    
    echo ""
    echo "🎉 Alexandria Safety API is live!"
    echo "📍 Service URL: $SERVICE_URL"
    echo "📊 Health: $SERVICE_URL/healthz"
    echo "🔍 Ready: $SERVICE_URL/readyz"
    echo "🧪 Validate: $SERVICE_URL/validate (POST)"
    
else
    echo_error "❌ Deployment failed!"
    exit 1
fi