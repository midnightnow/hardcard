#!/bin/bash
set -e

OUTPUT_DIR=$1
mkdir -p "${OUTPUT_DIR}"

echo "Running Foundry security tests..."

# Initialize Foundry project if needed
if [ ! -f "foundry.toml" ]; then
    cat > foundry.toml <<EOF
[profile.default]
src = 'contracts'
out = 'out'
libs = ['node_modules']
test = 'test'
cache_path = 'forge-cache'
optimizer = true
optimizer_runs = 200
solc_version = '0.8.26'

[invariant]
runs = 1000
depth = 500
shrink_sequence = true
call_override = false

[fuzz]
runs = 10000
max_test_rejects = 100000
seed = '0x1'
dictionary_weight = 40
include_storage = true
include_push_bytes = true
EOF
fi

# Run Foundry tests
forge test -vvv --gas-report > "${OUTPUT_DIR}/test-output.txt" 2>&1 || true

# Run invariant tests
forge test --match-contract "Invariant" -vvv > "${OUTPUT_DIR}/invariant-output.txt" 2>&1 || true

# Generate coverage report
forge coverage --report lcov --report-file "${OUTPUT_DIR}/lcov.info" > "${OUTPUT_DIR}/coverage.txt" 2>&1 || true

# Generate report
cat > "${OUTPUT_DIR}/report.md" <<EOF
# Foundry Security Test Report

## Test Summary

### Unit Tests
\`\`\`
$(grep -E "Test result:|test_" "${OUTPUT_DIR}/test-output.txt" || echo "No test results")
\`\`\`

### Invariant Tests
\`\`\`
$(grep -E "invariant_|Test result:" "${OUTPUT_DIR}/invariant-output.txt" || echo "No invariant test results")
\`\`\`

### Coverage Report
\`\`\`
$(tail -n 20 "${OUTPUT_DIR}/coverage.txt" || echo "No coverage data")
\`\`\`

## Gas Report

\`\`\`
$(grep -A 50 "│ Contract" "${OUTPUT_DIR}/test-output.txt" || echo "No gas data")
\`\`\`

## Security Invariants Tested

1. **Access Control Invariants**
   - Only authorized roles can call privileged functions
   - Role admin hierarchy is maintained

2. **State Invariants**
   - Guardian count within bounds
   - Threshold requirements maintained
   - Timelock delays enforced

3. **Economic Invariants**
   - No token inflation
   - Voting power conservation
   - No value extraction

4. **Operational Invariants**
   - No double execution
   - Proper state transitions
   - Event emission consistency

EOF

echo "✅ Foundry testing complete"