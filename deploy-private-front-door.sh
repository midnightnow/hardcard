#!/bin/bash

# Deploy hardcard.me Private Front Door
# Your personal gateway to the HardCard universe

set -e

echo "========================================"
echo "🔐 Deploying HardCard Private Front Door"
echo "Target: hardcard.me"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -d "private-front-door" ]; then
    echo "Error: private-front-door directory not found"
    exit 1
fi

cd private-front-door

# Use the hardcard project
echo "Setting Firebase project..."
firebase use hardcard

# Check if hardcard-me site exists, create if not
echo "Checking Firebase hosting site..."
if firebase hosting:sites:list | grep -q "hardcard-me"; then
    echo "✅ Site hardcard-me already exists"
else
    echo "Creating hardcard-me hosting site..."
    firebase hosting:sites:create hardcard-me
fi

# Create firebase.json for this specific deployment
cat > firebase.json << 'EOF'
{
  "hosting": {
    "site": "hardcard-me",
    "public": ".",
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
            "key": "X-Frame-Options",
            "value": "DENY"
          },
          {
            "key": "X-Content-Type-Options",
            "value": "nosniff"
          },
          {
            "key": "Strict-Transport-Security",
            "value": "max-age=31536000; includeSubDomains; preload"
          },
          {
            "key": "X-XSS-Protection",
            "value": "1; mode=block"
          },
          {
            "key": "Content-Security-Policy",
            "value": "default-src 'self' https:; script-src 'self' 'unsafe-inline' https://www.gstatic.com; style-src 'self' 'unsafe-inline';"
          },
          {
            "key": "Referrer-Policy",
            "value": "strict-origin"
          }
        ]
      }
    ]
  }
}
EOF

# Deploy to Firebase
echo ""
echo "Deploying to Firebase..."
firebase deploy --only hosting:hardcard-me

# Clean up
rm firebase.json

echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "Site URL: https://hardcard-me.web.app"
echo ""
echo "Next steps:"
echo "1. Configure DNS in Cloudflare:"
echo "   - Add CNAME record: hardcard.me → hardcard-me.web.app"
echo ""
echo "2. Add custom domain in Firebase Console:"
echo "   - Go to: https://console.firebase.google.com/project/hardcard/hosting/sites"
echo "   - Click on hardcard-me"
echo "   - Add custom domain: hardcard.me"
echo ""
echo "3. Test access:"
echo "   - Sign in with dallasm@gmail.com"
echo "   - Verify all links work"
echo ""
echo "Your private front door will be ready at: https://hardcard.me"
echo "========================================"

# Return to parent directory
cd ..