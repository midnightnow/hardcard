#!/bin/bash

# HardCard Production Deploy Guard
# Prevents accidental deployments to production without verification

set -e

echo "======================================"
echo "🔒 HardCard Production Deploy Guard"
echo "======================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "firebase.json" ]; then
    echo -e "${RED}Error: Not in a Firebase project directory${NC}"
    exit 1
fi

# Get current Firebase project
CURRENT_PROJECT=$(firebase use 2>/dev/null | grep "Active Project:" | cut -d':' -f2 | tr -d ' ')

# Production project check
if [ "$CURRENT_PROJECT" == "hardcard" ]; then
    echo -e "${YELLOW}⚠️  WARNING: You are about to deploy to PRODUCTION (hardcard)${NC}"
    echo ""
    echo "Current project: ${CURRENT_PROJECT}"
    echo "Target site: hardcard.web.app"
    echo ""
    
    # Check for site metadata
    if [ -f "dist/index.html" ]; then
        SITE_ID=$(grep -o 'x-site-id" content="[^"]*' dist/index.html | cut -d'"' -f3)
        if [ "$SITE_ID" != "hardcard-os" ]; then
            echo -e "${RED}❌ ERROR: Wrong site content detected!${NC}"
            echo "Expected: hardcard-os"
            echo "Found: ${SITE_ID:-none}"
            echo ""
            echo "This content is not meant for production!"
            exit 1
        fi
    fi
    
    # Require explicit confirmation
    echo -e "${YELLOW}This will deploy to the PRODUCTION HardCard OS platform.${NC}"
    echo "Type 'DEPLOY TO PRODUCTION' to confirm:"
    read -r confirmation
    
    if [ "$confirmation" != "DEPLOY TO PRODUCTION" ]; then
        echo -e "${RED}Deployment cancelled.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Production deployment authorized${NC}"
    
    # Run tests if available
    if [ -f "package.json" ] && grep -q '"test"' package.json; then
        echo "Running tests before deployment..."
        npm test || {
            echo -e "${RED}❌ Tests failed! Deployment aborted.${NC}"
            exit 1
        }
    fi
    
    # Check for common issues
    echo "Checking for common issues..."
    
    # Check for hardcoded localhost URLs
    if grep -r "localhost" dist/ --include="*.html" --include="*.js" 2>/dev/null | grep -v "//localhost"; then
        echo -e "${YELLOW}⚠️  Warning: Found localhost references in production build${NC}"
        echo "Continue anyway? (y/N)"
        read -r continue_deploy
        if [ "$continue_deploy" != "y" ]; then
            echo -e "${RED}Deployment cancelled.${NC}"
            exit 1
        fi
    fi
    
    # Check for console.log statements
    if grep -r "console.log" dist/ --include="*.js" 2>/dev/null | head -5; then
        echo -e "${YELLOW}⚠️  Warning: Found console.log statements in production build${NC}"
    fi
    
    # Log deployment
    echo "$(date): Production deployment to hardcard.web.app by $(whoami)" >> deploy.log
    
    echo -e "${GREEN}Proceeding with production deployment...${NC}"
    
elif [ "$CURRENT_PROJECT" == "hardcard-firebase-studio" ]; then
    echo -e "${YELLOW}Deploying to sandbox environment (${CURRENT_PROJECT})${NC}"
    echo "This is safe for experiments and testing."
    
else
    echo "Deploying to project: ${CURRENT_PROJECT}"
fi

# Add pre-deployment backup
if [ "$CURRENT_PROJECT" == "hardcard" ]; then
    echo "Creating backup of current production..."
    mkdir -p backups
    BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
    curl -s https://hardcard.web.app > "backups/${BACKUP_NAME}.html"
    echo "Backup saved to backups/${BACKUP_NAME}.html"
fi

echo ""
echo "======================================"
echo "Deploy guard checks complete"
echo "======================================"