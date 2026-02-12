#!/bin/bash

# HardCard Production Deployment Script
# Deploys ONLY to hardcard.web.app in the hardcard project
# This is the PRODUCTION deployment for the core HardCard OS platform

set -e

echo "====================================="
echo "HardCard OS Production Deployment"
echo "Target: hardcard.web.app"
echo "====================================="

# Safety checks
if [ ! -f "firebase.json" ]; then
    echo "Error: firebase.json not found. Are you in the hardcard directory?"
    exit 1
fi

# Verify we're using the correct project
CURRENT_PROJECT=$(firebase use 2>/dev/null | grep "Active Project:" | cut -d':' -f2 | tr -d ' ')
if [ "$CURRENT_PROJECT" != "hardcard" ]; then
    echo "Switching to hardcard project..."
    firebase use hardcard
fi

# Build the production app
echo "Building production app..."
npm run build

# Inject site metadata
echo "Injecting site metadata..."
if [ -f "scripts/inject-site-meta.js" ]; then
    node scripts/inject-site-meta.js hardcard-os hardcard.web.app dist
else
    echo "Warning: inject-site-meta.js not found, skipping metadata injection"
fi

# Create firebase.json for hardcard site only
cat > firebase.production.json << 'EOF'
{
  "hosting": {
    "site": "hardcard",
    "public": "dist",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css|json|woff2)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "public, max-age=31536000, immutable"
          }
        ]
      },
      {
        "source": "**",
        "headers": [
          {
            "key": "X-Frame-Options",
            "value": "SAMEORIGIN"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          },
          {
            "key": "X-Site-ID",
            "value": "hardcard-os"
          },
          {
            "key": "X-Deploy-Target",
            "value": "production"
          }
        ]
      }
    ]
  }
}
EOF

# Deploy to production
echo "Deploying to hardcard.web.app..."
firebase deploy --only hosting:hardcard --config firebase.production.json

# Verify deployment
echo ""
echo "Verifying deployment..."
SITE_ID=$(curl -s -I https://hardcard.web.app | grep -i "x-site-id" | cut -d':' -f2 | tr -d ' \r')
if [ "$SITE_ID" = "hardcard-os" ]; then
    echo "✅ Deployment verified successfully!"
    echo "✅ hardcard.web.app is now serving HardCard OS"
else
    echo "⚠️  Warning: Could not verify site metadata"
fi

# Clean up temporary config
rm -f firebase.production.json

echo ""
echo "====================================="
echo "Deployment Complete!"
echo "Production URL: https://hardcard.web.app"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Configure hardcard.ai to point to hardcard.web.app"
echo "2. Remove hardcard.ai from studio project"
echo "3. Set up monitoring and alerts"