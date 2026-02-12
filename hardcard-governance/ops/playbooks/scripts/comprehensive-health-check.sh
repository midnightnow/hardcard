#!/bin/bash
set -e

# Comprehensive Health Check for Hardcard Governance
# Performs a complete system status assessment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_FILE="health-check-$(date +%Y%m%d-%H%M%S).md"
NETWORK=${NETWORK:-mainnet}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Initialize report
cat > "$REPORT_FILE" <<EOF
# Hardcard Governance Health Check Report

**Generated**: $(date -u)  
**Network**: $NETWORK  
**Version**: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')

---

## Executive Summary

EOF

# Track overall health
CRITICAL_ISSUES=0
WARNING_ISSUES=0
TOTAL_CHECKS=0

check_result() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    case "$status" in
        "PASS")
            echo "✅ $test_name" >> "$REPORT_FILE"
            log_success "$test_name"
            ;;
        "FAIL")
            echo "❌ $test_name" >> "$REPORT_FILE"
            log_error "$test_name"
            CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
            ;;
        "WARN")
            echo "⚠️ $test_name" >> "$REPORT_FILE"
            log_warning "$test_name"
            WARNING_ISSUES=$((WARNING_ISSUES + 1))
            ;;
    esac
    
    if [ -n "$details" ]; then
        echo "   - $details" >> "$REPORT_FILE"
    fi
    echo >> "$REPORT_FILE"
}

# Network Connectivity Check
echo "## Network Connectivity" >> "$REPORT_FILE"
log_info "Checking network connectivity..."

if npx hardhat run --network "$NETWORK" scripts/debug/check-network.ts > /dev/null 2>&1; then
    check_result "Network Connection" "PASS" "Successfully connected to $NETWORK"
else
    check_result "Network Connection" "FAIL" "Cannot connect to $NETWORK"
fi

# Contract Deployment Check
echo "## Contract Deployments" >> "$REPORT_FILE"
log_info "Checking contract deployments..."

for contract in "GuardianCouncil" "TimelockController" "GovernorDAO"; do
    if [ -f "deployments/$NETWORK/$contract.json" ]; then
        address=$(jq -r '.address' "deployments/$NETWORK/$contract.json")
        if [ "$address" != "null" ] && [ "$address" != "0x0000000000000000000000000000000000000000" ]; then
            check_result "$contract Deployment" "PASS" "Deployed at $address"
        else
            check_result "$contract Deployment" "FAIL" "Invalid address in deployment file"
        fi
    else
        check_result "$contract Deployment" "FAIL" "Deployment file not found"
    fi
done

# Guardian Council Health
echo "## Guardian Council Health" >> "$REPORT_FILE"
log_info "Checking Guardian Council..."

if npx hardhat run --network "$NETWORK" scripts/ops/check-guardians.ts > guardian_status.tmp 2>&1; then
    guardian_count=$(grep "Guardian Count:" guardian_status.tmp | awk '{print $3}' || echo "0")
    threshold=$(grep "Threshold:" guardian_status.tmp | awk '{print $2}' || echo "0")
    
    if [ "$guardian_count" -ge 3 ] && [ "$guardian_count" -le 5 ]; then
        check_result "Guardian Count" "PASS" "$guardian_count guardians (threshold: $threshold)"
    else
        check_result "Guardian Count" "FAIL" "$guardian_count guardians (should be 3-5)"
    fi
    
    if [ "$threshold" -ge 3 ] && [ "$threshold" -le "$guardian_count" ]; then
        check_result "Guardian Threshold" "PASS" "Threshold $threshold is valid"
    else
        check_result "Guardian Threshold" "FAIL" "Invalid threshold: $threshold"
    fi
else
    check_result "Guardian Council Access" "FAIL" "Cannot query Guardian Council"
fi

rm -f guardian_status.tmp

# Timelock Controller Health
echo "## Timelock Controller Health" >> "$REPORT_FILE"
log_info "Checking Timelock Controller..."

if npx hardhat run --network "$NETWORK" scripts/ops/check-timelock.ts > timelock_status.tmp 2>&1; then
    delay=$(grep "Delay:" timelock_status.tmp | awk '{print $2}' || echo "0")
    pending=$(grep "Pending Operations:" timelock_status.tmp | awk '{print $3}' || echo "0")
    
    if [ "$delay" -ge 172800 ]; then  # 48 hours
        check_result "Timelock Delay" "PASS" "Delay is ${delay}s (≥48h)"
    else
        check_result "Timelock Delay" "FAIL" "Delay is ${delay}s (<48h)"
    fi
    
    if [ "$pending" -lt 10 ]; then
        check_result "Pending Operations" "PASS" "$pending pending operations"
    else
        check_result "Pending Operations" "WARN" "$pending pending operations (high)"
    fi
else
    check_result "Timelock Controller Access" "FAIL" "Cannot query Timelock Controller"
fi

rm -f timelock_status.tmp

# Governor DAO Health
echo "## Governor DAO Health" >> "$REPORT_FILE"
log_info "Checking Governor DAO..."

if npx hardhat run --network "$NETWORK" scripts/ops/check-proposals.ts > proposal_status.tmp 2>&1; then
    active_proposals=$(grep "Active:" proposal_status.tmp | awk '{print $2}' || echo "0")
    total_proposals=$(grep "Total:" proposal_status.tmp | awk '{print $2}' || echo "0")
    
    check_result "Proposal System" "PASS" "$total_proposals total, $active_proposals active"
    
    if [ "$active_proposals" -lt 5 ]; then
        check_result "Active Proposals" "PASS" "$active_proposals active proposals"
    else
        check_result "Active Proposals" "WARN" "$active_proposals active proposals (high)"
    fi
else
    check_result "Governor DAO Access" "FAIL" "Cannot query Governor DAO"
fi

rm -f proposal_status.tmp

# System Resources
echo "## System Resources" >> "$REPORT_FILE"
log_info "Checking system resources..."

# Check disk space
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    check_result "Disk Usage" "PASS" "${disk_usage}% used"
elif [ "$disk_usage" -lt 90 ]; then
    check_result "Disk Usage" "WARN" "${disk_usage}% used"
else
    check_result "Disk Usage" "FAIL" "${disk_usage}% used (critical)"
fi

# Check memory usage
if command -v free > /dev/null; then
    memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2 }')
    if [ "$memory_usage" -lt 80 ]; then
        check_result "Memory Usage" "PASS" "${memory_usage}% used"
    elif [ "$memory_usage" -lt 90 ]; then
        check_result "Memory Usage" "WARN" "${memory_usage}% used"
    else
        check_result "Memory Usage" "FAIL" "${memory_usage}% used (critical)"
    fi
fi

# Security Checks
echo "## Security Status" >> "$REPORT_FILE"
log_info "Checking security status..."

# Check for recent emergency actions
if [ -f "logs/emergency-actions.json" ]; then
    recent_emergencies=$(jq '[.[] | select(.timestamp > (now - 86400 | todate))] | length' logs/emergency-actions.json 2>/dev/null || echo "0")
    if [ "$recent_emergencies" -eq 0 ]; then
        check_result "Recent Emergencies" "PASS" "No emergency actions in last 24h"
    else
        check_result "Recent Emergencies" "WARN" "$recent_emergencies emergency actions in last 24h"
    fi
else
    check_result "Emergency Logs" "PASS" "No emergency log file (clean)"
fi

# Check for failed transactions
if [ -f "logs/failed-transactions.log" ]; then
    recent_failures=$(find logs/failed-transactions.log -mtime -1 -exec wc -l {} \; 2>/dev/null | awk '{print $1}' || echo "0")
    if [ "$recent_failures" -eq 0 ]; then
        check_result "Failed Transactions" "PASS" "No failed transactions in last 24h"
    elif [ "$recent_failures" -lt 5 ]; then
        check_result "Failed Transactions" "WARN" "$recent_failures failed transactions in last 24h"
    else
        check_result "Failed Transactions" "FAIL" "$recent_failures failed transactions in last 24h"
    fi
else
    check_result "Failed Transactions" "PASS" "No failed transaction log (clean)"
fi

# Monitoring Status
echo "## Monitoring Status" >> "$REPORT_FILE"
log_info "Checking monitoring status..."

# Check if monitoring is running
if docker-compose -f monitoring/docker-compose.monitoring.yml ps | grep -q "Up"; then
    check_result "Monitoring Stack" "PASS" "Monitoring containers are running"
    
    # Check specific services
    for service in "prometheus" "grafana" "alertmanager"; do
        if docker-compose -f monitoring/docker-compose.monitoring.yml ps "$service" | grep -q "Up"; then
            check_result "$service Service" "PASS" "Service is running"
        else
            check_result "$service Service" "FAIL" "Service is not running"
        fi
    done
else
    check_result "Monitoring Stack" "WARN" "Monitoring stack is not running"
fi

# API Health Checks
echo "## API Health" >> "$REPORT_FILE"
log_info "Checking API endpoints..."

# Check if API endpoints are defined
api_endpoints=(
    "https://api.hardcard.io/health"
    "https://dashboard.hardcard.io"
)

for endpoint in "${api_endpoints[@]}"; do
    if curl -s --max-time 10 "$endpoint" > /dev/null 2>&1; then
        check_result "API Endpoint ($endpoint)" "PASS" "Endpoint is responding"
    else
        check_result "API Endpoint ($endpoint)" "WARN" "Endpoint not responding or not configured"
    fi
done

# Generate Executive Summary
echo "## Summary Statistics" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"
echo "- **Total Checks**: $TOTAL_CHECKS" >> "$REPORT_FILE"
echo "- **Critical Issues**: $CRITICAL_ISSUES" >> "$REPORT_FILE"
echo "- **Warning Issues**: $WARNING_ISSUES" >> "$REPORT_FILE"
echo "- **Passed Checks**: $((TOTAL_CHECKS - CRITICAL_ISSUES - WARNING_ISSUES))" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

# Overall Health Status
if [ "$CRITICAL_ISSUES" -eq 0 ] && [ "$WARNING_ISSUES" -eq 0 ]; then
    OVERALL_STATUS="🟢 HEALTHY"
    exit_code=0
elif [ "$CRITICAL_ISSUES" -eq 0 ]; then
    OVERALL_STATUS="🟡 WARNING"
    exit_code=1
else
    OVERALL_STATUS="🔴 CRITICAL"
    exit_code=2
fi

echo "**Overall Status**: $OVERALL_STATUS" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

# Add recommendations
echo "## Recommendations" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

if [ "$CRITICAL_ISSUES" -gt 0 ]; then
    echo "### Critical Actions Required" >> "$REPORT_FILE"
    echo "- Address all critical issues immediately" >> "$REPORT_FILE"
    echo "- Consider emergency procedures if governance is affected" >> "$REPORT_FILE"
    echo "- Notify incident response team" >> "$REPORT_FILE"
    echo >> "$REPORT_FILE"
fi

if [ "$WARNING_ISSUES" -gt 0 ]; then
    echo "### Warning Items" >> "$REPORT_FILE"
    echo "- Review warning items and plan remediation" >> "$REPORT_FILE"
    echo "- Monitor trends to prevent escalation" >> "$REPORT_FILE"
    echo "- Update operational procedures if needed" >> "$REPORT_FILE"
    echo >> "$REPORT_FILE"
fi

echo "### General Recommendations" >> "$REPORT_FILE"
echo "- Run health checks daily" >> "$REPORT_FILE"
echo "- Monitor key metrics continuously" >> "$REPORT_FILE"
echo "- Keep guardian contact information updated" >> "$REPORT_FILE"
echo "- Practice emergency procedures regularly" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

# Add next steps
echo "## Next Steps" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"
echo "1. Review all failed and warning items" >> "$REPORT_FILE"
echo "2. Create action items for critical issues" >> "$REPORT_FILE"
echo "3. Schedule follow-up health check in 24 hours" >> "$REPORT_FILE"
echo "4. Update monitoring alerts if gaps identified" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

echo "---" >> "$REPORT_FILE"
echo "*Generated by comprehensive-health-check.sh*" >> "$REPORT_FILE"

# Update the executive summary at the top
sed -i.bak "s/## Executive Summary/## Executive Summary\n\n**Overall Status**: $OVERALL_STATUS  \n**Critical Issues**: $CRITICAL_ISSUES  \n**Warning Issues**: $WARNING_ISSUES  \n**Total Checks**: $TOTAL_CHECKS/" "$REPORT_FILE"
rm -f "$REPORT_FILE.bak"

# Display results
echo
log_info "Health check complete!"
echo
echo "📊 Results Summary:"
echo "  Overall Status: $OVERALL_STATUS"
echo "  Critical Issues: $CRITICAL_ISSUES"
echo "  Warning Issues: $WARNING_ISSUES"
echo "  Total Checks: $TOTAL_CHECKS"
echo
echo "📄 Full report: $REPORT_FILE"

# Copy report to logs directory
mkdir -p logs/health-checks
cp "$REPORT_FILE" "logs/health-checks/"

exit $exit_code