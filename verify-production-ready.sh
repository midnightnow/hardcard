#!/bin/bash
# Alexandria Safety Architecture - Production Readiness Check
# Quick verification that all components are ready for deployment

echo "🔍 Alexandria Production Readiness Check"
echo "========================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

check_ready() {
    local name="$1"
    local test_command="$2"
    local required="${3:-true}"
    
    printf "%-40s" "$name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ READY${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}❌ MISSING${NC}"
            ((CHECKS_FAILED++))
        else
            echo -e "${YELLOW}⚠️  OPTIONAL${NC}"
            ((CHECKS_PASSED++))
        fi
        return 1
    fi
}

echo "🛠️  Development Tools"
check_ready "gcloud CLI" "command -v gcloud"
check_ready "Firebase CLI" "command -v firebase"
check_ready "Docker" "command -v docker" "false"
check_ready "curl" "command -v curl"
check_ready "jq (JSON processor)" "command -v jq" "false"

echo ""
echo "📁 Core Files"
check_ready "Safety Wrapper" "test -f alexandria_safety_wrapper.py"
check_ready "Simple API" "test -f alexandria_api_simple.py"
check_ready "Configuration" "test -f config.yaml"
check_ready "Dockerfile" "test -f Dockerfile"
check_ready "Requirements" "test -f requirements.txt"
check_ready "Firebase Config" "test -f firebase.json"

echo ""
echo "🧪 Test Files"
check_ready "Test Suite" "test -f test_alexandria_safety.py"
check_ready "Deployment Script" "test -f deploy-alexandria-api.sh"
check_ready "End-to-End Tests" "test -f test-deployment.sh"
check_ready "Complete Deploy Script" "test -f deploy-and-verify-complete.sh"

echo ""
echo "📄 Documentation"
check_ready "README" "test -f README.md" "false"
check_ready "Deployment Complete" "test -f ALEXANDRIA_DEPLOYMENT_COMPLETE.md"

echo ""
echo "🌐 Frontend Assets"
check_ready "Index HTML" "test -f public/index.html"
check_ready "Analytics Config" "test -f public/js/analytics-config.js"
check_ready "A/B Testing" "test -f public/js/ab-testing.js"
check_ready "GA4 Script" "test -f public/js/ga4.js"

echo ""
echo "🐍 Python Dependencies"
check_ready "FastAPI importable" "python3 -c 'import fastapi'"
check_ready "Uvicorn importable" "python3 -c 'import uvicorn'"
check_ready "NumPy importable" "python3 -c 'import numpy'"
check_ready "Safety Wrapper importable" "python3 -c 'from alexandria_safety_wrapper import AlexandriaSafetyWrapper'"

echo ""
echo "🔧 Configuration Validation"
check_ready "Firebase config valid" "python3 -c 'import json; json.load(open(\"firebase.json\"))'"
check_ready "YAML config valid" "python3 -c 'import yaml; yaml.safe_load(open(\"config.yaml\"))'" "false"

echo ""
echo "🚀 Local Testing"
if command -v uvicorn > /dev/null 2>&1; then
    # Quick local server test
    echo "Testing local server startup..."
    timeout 10s uvicorn alexandria_api_simple:app --host 127.0.0.1 --port 8888 > /dev/null 2>&1 &
    SERVER_PID=$!
    sleep 3
    
    if curl -f http://127.0.0.1:8888/healthz > /dev/null 2>&1; then
        echo -e "Local server test                       ${GREEN}✅ READY${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "Local server test                       ${RED}❌ FAILED${NC}"
        ((CHECKS_FAILED++))
    fi
    
    # Clean up
    kill $SERVER_PID 2>/dev/null || true
    sleep 1
else
    echo -e "Local server test                       ${YELLOW}⚠️  SKIPPED${NC}"
fi

# Summary
echo ""
echo "📊 Production Readiness Summary"
echo "==============================="
echo -e "Checks Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Checks Failed: ${RED}$CHECKS_FAILED${NC}"
echo "Total Checks: $((CHECKS_PASSED + CHECKS_FAILED))"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 PRODUCTION READY!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: ./deploy-and-verify-complete.sh"
    echo "2. Monitor: deployment_report.json"
    echo "3. Test: https://hardcard.org/api/healthz"
    echo ""
    echo "Alexandria Safety Architecture is ready for live deployment! 🚀"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  NOT READY FOR PRODUCTION${NC}"
    echo ""
    echo "Please fix the failed checks above before deploying."
    echo "Most common fixes:"
    echo "- Install gcloud: brew install google-cloud-sdk"
    echo "- Install firebase: npm install -g firebase-tools"
    echo "- Install Python deps: pip install fastapi uvicorn numpy"
    exit 1
fi