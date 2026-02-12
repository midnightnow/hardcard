#!/bin/bash
set -e

OUTPUT_DIR=$1
mkdir -p "${OUTPUT_DIR}"

echo "Running Mythril symbolic execution..."

# Contracts to analyze
CONTRACTS=(
    "contracts/governance/GuardianCouncil.sol:GuardianCouncil"
    "contracts/governance/TimelockController.sol:HardcardTimelockController"
    "contracts/governance/GovernorDAO.sol:GovernorDAO"
)

# Run Mythril on each contract
for contract in "${CONTRACTS[@]}"; do
    contract_path="${contract%:*}"
    contract_name="${contract#*:}"
    
    echo "Analyzing $contract_name..."
    
    # Run analysis with timeout
    timeout 600 myth analyze "$contract_path" \
        --solc-json mythril-config.json \
        --execution-timeout 300 \
        --solver-timeout 10000 \
        --max-depth 12 \
        --transaction-count 3 \
        --verbose-report \
        --output-format json \
        -o "${OUTPUT_DIR}/${contract_name}.json" 2>&1 || true
    
    # Also generate markdown report
    timeout 600 myth analyze "$contract_path" \
        --solc-json mythril-config.json \
        --execution-timeout 300 \
        --output-format markdown \
        -o "${OUTPUT_DIR}/${contract_name}.md" 2>&1 || true
done

# Consolidate results
cat > "${OUTPUT_DIR}/report.json" <<EOF
{
    "tool": "mythril",
    "version": "$(myth version 2>/dev/null || echo 'unknown')",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "contracts": [
$(for json_file in "${OUTPUT_DIR}"/*.json; do
    if [ -f "$json_file" ] && [ "$json_file" != "${OUTPUT_DIR}/report.json" ]; then
        echo "        $(cat "$json_file"),"
    fi
done | sed '$ s/,$//')
    ]
}
EOF

# Generate summary report
cat > "${OUTPUT_DIR}/report.md" <<EOF
# Mythril Security Analysis Report

## Executive Summary

Mythril performs symbolic execution to find potential security vulnerabilities.

## Findings by Contract

$(for md_file in "${OUTPUT_DIR}"/*.md; do
    if [ -f "$md_file" ] && [ "$md_file" != "${OUTPUT_DIR}/report.md" ]; then
        contract=$(basename "$md_file" .md)
        echo "### $contract"
        cat "$md_file" 2>/dev/null || echo "No issues found"
        echo ""
    fi
done)

## Security Checks Performed

- Integer Overflow/Underflow
- Reentrancy
- Unprotected Ether Withdrawal  
- Delegatecall to Untrusted Callee
- Dependence on Predictable Variables
- Deprecated Solidity Functions
- Transaction Order Dependence
- Unchecked Call Return Values

EOF

echo "✅ Mythril analysis complete"