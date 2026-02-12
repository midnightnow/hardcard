#!/bin/bash

# Script to safely remove hardcard.ai from studio project
# This should be run AFTER the domain is successfully added to the production project

set -e

echo "========================================"
echo "🔄 Remove hardcard.ai from Studio Project"
echo "========================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check current project
CURRENT_PROJECT=$(firebase use 2>/dev/null | grep "Active Project:" | cut -d':' -f2 | tr -d ' ')

echo "Current Firebase project: ${CURRENT_PROJECT}"
echo ""

# Verify hardcard.ai is working on production first
echo "Checking if hardcard.ai is accessible..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://hardcard.ai || echo "000")

if [ "$HTTP_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ hardcard.ai is accessible (HTTP ${HTTP_STATUS})${NC}"
    
    # Check if it's serving the correct content
    SITE_CONTENT=$(curl -s https://hardcard.ai | grep -o "HardCard OS" | head -1 || echo "")
    if [ "$SITE_CONTENT" == "HardCard OS" ]; then
        echo -e "${GREEN}✅ hardcard.ai is serving HardCard OS content${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: hardcard.ai may not be serving the correct content${NC}"
        echo "Continue anyway? (y/N)"
        read -r continue_removal
        if [ "$continue_removal" != "y" ]; then
            echo "Removal cancelled."
            exit 1
        fi
    fi
else
    echo -e "${RED}❌ hardcard.ai is not accessible (HTTP ${HTTP_STATUS})${NC}"
    echo ""
    echo "Before removing from studio, make sure:"
    echo "1. DNS is configured (CNAME hardcard.ai → hardcard.web.app)"
    echo "2. Custom domain is added in Firebase Console (hardcard project)"
    echo "3. SSL certificate is provisioned (wait 5-10 minutes)"
    echo ""
    echo "Force continue anyway? (y/N)"
    read -r force_continue
    if [ "$force_continue" != "y" ]; then
        echo "Removal cancelled. Please complete DNS setup first."
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "📋 Manual Steps Required"
echo "========================================"
echo ""
echo "Since Firebase doesn't have a CLI command to remove custom domains,"
echo "you need to do this manually:"
echo ""
echo -e "${YELLOW}1. Open Firebase Console:${NC}"
echo "   https://console.firebase.google.com/project/hardcard-firebase-studio/hosting/sites"
echo ""
echo -e "${YELLOW}2. Find the site with hardcard.ai:${NC}"
echo "   - Click on 'hardcard-ai' or whichever site has the domain"
echo "   - Go to the 'Custom domains' tab"
echo ""
echo -e "${YELLOW}3. Remove the domain:${NC}"
echo "   - Find 'hardcard.ai' in the list"
echo "   - Click the three dots menu (⋮)"
echo "   - Select 'Delete domain'"
echo "   - Confirm the deletion"
echo ""
echo -e "${YELLOW}4. Verify removal:${NC}"
echo "   - The domain should disappear from the list"
echo "   - hardcard.ai should continue working via the production project"
echo ""

# Create a verification script
cat > verify-domain-migration.sh << 'EOF'
#!/bin/bash

echo "Verifying domain migration..."
echo ""

# Check DNS
echo "1. DNS Configuration:"
DNS_RESULT=$(dig hardcard.ai CNAME +short)
if [ "$DNS_RESULT" == "hardcard.web.app." ] || [ "$DNS_RESULT" == "hardcard.web.app" ]; then
    echo "   ✅ DNS correctly points to hardcard.web.app"
else
    echo "   ❌ DNS not configured correctly. Current: $DNS_RESULT"
fi

# Check site accessibility
echo ""
echo "2. Site Accessibility:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://hardcard.ai)
if [ "$HTTP_STATUS" == "200" ]; then
    echo "   ✅ hardcard.ai is accessible (HTTP $HTTP_STATUS)"
else
    echo "   ❌ hardcard.ai returned HTTP $HTTP_STATUS"
fi

# Check content
echo ""
echo "3. Content Verification:"
CONTENT=$(curl -s https://hardcard.ai | grep -o "HardCard OS" | head -1)
if [ "$CONTENT" == "HardCard OS" ]; then
    echo "   ✅ Serving correct HardCard OS content"
else
    echo "   ❌ Not serving expected content"
fi

# Check hardcard.web.app
echo ""
echo "4. Production Site:"
PROD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://hardcard.web.app)
if [ "$PROD_STATUS" == "200" ]; then
    echo "   ✅ hardcard.web.app is accessible"
else
    echo "   ❌ hardcard.web.app returned HTTP $PROD_STATUS"
fi

echo ""
echo "========================================"
echo "Migration verification complete!"
echo "========================================"
EOF

chmod +x verify-domain-migration.sh

echo "========================================"
echo -e "${GREEN}✅ Verification script created: ./verify-domain-migration.sh${NC}"
echo "========================================"
echo ""
echo "After removing the domain from studio, run:"
echo "  ./verify-domain-migration.sh"
echo ""
echo "This will confirm the migration was successful."