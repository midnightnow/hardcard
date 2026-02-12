#!/bin/bash
set -e

echo "🔒 Hardcard Governance Security Audit Suite"
echo "=========================================="
echo "Starting comprehensive security analysis..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="/audit/results/report_${TIMESTAMP}"
mkdir -p "${REPORT_DIR}"

# Function to run audit and check results
run_audit() {
    local name=$1
    local script=$2
    local output_dir=$3
    
    echo -e "${YELLOW}[*] Running ${name}...${NC}"
    
    if bash "/audit/scripts/${script}" "${output_dir}" > "${output_dir}/audit.log" 2>&1; then
        echo -e "${GREEN}[✓] ${name} completed${NC}"
        return 0
    else
        echo -e "${RED}[✗] ${name} failed${NC}"
        return 1
    fi
}

# 1. Slither Static Analysis
echo "1. Static Analysis with Slither"
echo "------------------------------"
run_audit "Slither" "run-slither.sh" "/audit/results/slither"
echo ""

# 2. Mythril Symbolic Execution
echo "2. Symbolic Execution with Mythril"
echo "---------------------------------"
run_audit "Mythril" "run-mythril.sh" "/audit/results/mythril"
echo ""

# 3. Echidna Fuzzing
echo "3. Property Testing with Echidna"
echo "-------------------------------"
run_audit "Echidna" "run-echidna.sh" "/audit/results/echidna"
echo ""

# 4. Foundry Tests
echo "4. Foundry Invariant Tests"
echo "-------------------------"
run_audit "Foundry" "run-foundry.sh" "/audit/results/foundry"
echo ""

# 5. Gas Analysis
echo "5. Gas Optimization Analysis"
echo "---------------------------"
run_audit "Gas Analysis" "run-gas-analysis.sh" "/audit/results/gas"
echo ""

# 6. Access Control Analysis
echo "6. Access Control Review"
echo "-----------------------"
run_audit "Access Control" "run-access-control.sh" "/audit/results/access"
echo ""

# Generate Summary Report
echo "Generating Security Report..."
echo "============================"

# Collect all results
cat > "${REPORT_DIR}/summary.json" <<EOF
{
    "timestamp": "${TIMESTAMP}",
    "project": "Hardcard Governance",
    "version": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
    "audits": {
        "slither": {
            "status": "$(test -f /audit/results/slither/report.json && echo 'complete' || echo 'failed')",
            "high_severity": $(jq '[.results.detectors[] | select(.impact == "High")] | length' /audit/results/slither/report.json 2>/dev/null || echo 0),
            "medium_severity": $(jq '[.results.detectors[] | select(.impact == "Medium")] | length' /audit/results/slither/report.json 2>/dev/null || echo 0),
            "low_severity": $(jq '[.results.detectors[] | select(.impact == "Low")] | length' /audit/results/slither/report.json 2>/dev/null || echo 0)
        },
        "mythril": {
            "status": "$(test -f /audit/results/mythril/report.json && echo 'complete' || echo 'failed')",
            "issues": $(jq '.issues | length' /audit/results/mythril/report.json 2>/dev/null || echo 0)
        },
        "echidna": {
            "status": "$(test -f /audit/results/echidna/coverage.txt && echo 'complete' || echo 'failed')",
            "tests_run": $(grep -o 'tests:.*' /audit/results/echidna/output.txt 2>/dev/null | awk '{print $2}' || echo 0)
        },
        "gas": {
            "status": "$(test -f /audit/results/gas/report.txt && echo 'complete' || echo 'failed')"
        }
    }
}
EOF

# Generate human-readable report
bash /audit/scripts/generate-report.sh "${REPORT_DIR}"

echo ""
echo "✅ Security audit complete!"
echo "📊 Results saved to: ${REPORT_DIR}"
echo ""
echo "Summary:"
echo "--------"
cat "${REPORT_DIR}/summary.txt" 2>/dev/null || echo "No summary available"

# Exit with error if any high severity issues found
HIGH_ISSUES=$(jq '.audits.slither.high_severity + .audits.mythril.issues' "${REPORT_DIR}/summary.json" 2>/dev/null || echo 0)
if [ "${HIGH_ISSUES}" -gt 0 ]; then
    echo ""
    echo -e "${RED}⚠️  Found ${HIGH_ISSUES} high severity issues!${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ No high severity issues found${NC}"
    exit 0
fi