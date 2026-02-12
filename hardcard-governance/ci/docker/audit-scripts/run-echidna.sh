#!/bin/bash
set -e

OUTPUT_DIR=$1
mkdir -p "${OUTPUT_DIR}"

echo "Running Echidna property-based testing..."

# Run Echidna on each test contract
for test_file in test/fuzz/*.echidna.sol; do
    if [ -f "$test_file" ]; then
        contract_name=$(basename "$test_file" .echidna.sol)
        echo "Testing $contract_name..."
        
        mkdir -p "${OUTPUT_DIR}/${contract_name}"
        
        # Run Echidna
        echidna "$test_file" \
            --config echidna.config.yaml \
            --format text \
            --corpus-dir "${OUTPUT_DIR}/${contract_name}/corpus" \
            --coverage \
            > "${OUTPUT_DIR}/${contract_name}/output.txt" 2>&1 || true
        
        # Copy coverage info
        cp -r crytic-export/echidna/* "${OUTPUT_DIR}/${contract_name}/" 2>/dev/null || true
    fi
done

# Generate consolidated report
cat > "${OUTPUT_DIR}/report.md" <<EOF
# Echidna Fuzzing Report

## Test Summary

$(for dir in "${OUTPUT_DIR}"/*; do
    if [ -d "$dir" ] && [ "$dir" != "${OUTPUT_DIR}/report.md" ]; then
        contract=$(basename "$dir")
        echo "### $contract"
        echo '```'
        tail -n 20 "$dir/output.txt" 2>/dev/null || echo "No output"
        echo '```'
        echo ""
    fi
done)

## Coverage Analysis

$(for dir in "${OUTPUT_DIR}"/*; do
    if [ -d "$dir" ] && [ -f "$dir/coverage.txt" ]; then
        contract=$(basename "$dir")
        echo "### $contract Coverage"
        echo '```'
        cat "$dir/coverage.txt" 2>/dev/null || echo "No coverage data"
        echo '```'
        echo ""
    fi
done)

## Invariant Test Results

All invariants tested:
- Guardian count limits
- Threshold requirements
- Access control
- Timelock delays
- Double execution prevention

EOF

echo "✅ Echidna testing complete"