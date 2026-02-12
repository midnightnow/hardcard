#!/bin/bash
set -e

OUTPUT_DIR=$1
mkdir -p "${OUTPUT_DIR}"

echo "Running Slither static analysis..."

# Run Slither with multiple output formats
slither . \
    --config-file slither.config.json \
    --json "${OUTPUT_DIR}/report.json" \
    --json-types detectors,printers \
    --print human-summary \
    --print inheritance-graph \
    --print contract-summary \
    --print function-summary \
    --print vars-and-auth \
    --print call-graph \
    --markdown-root "${OUTPUT_DIR}" \
    > "${OUTPUT_DIR}/slither-output.txt" 2>&1 || true

# Generate markdown report
cat > "${OUTPUT_DIR}/report.md" <<EOF
# Slither Static Analysis Report

## Summary
$(slither . --print human-summary 2>/dev/null || echo "Analysis failed")

## Findings

### High Severity
$(jq -r '.results.detectors[] | select(.impact == "High") | "- **\(.check)**: \(.description)"' "${OUTPUT_DIR}/report.json" 2>/dev/null || echo "None found")

### Medium Severity
$(jq -r '.results.detectors[] | select(.impact == "Medium") | "- **\(.check)**: \(.description)"' "${OUTPUT_DIR}/report.json" 2>/dev/null || echo "None found")

### Low Severity
$(jq -r '.results.detectors[] | select(.impact == "Low") | "- **\(.check)**: \(.description)"' "${OUTPUT_DIR}/report.json" 2>/dev/null || echo "None found")

### Informational
$(jq -r '.results.detectors[] | select(.impact == "Informational") | "- **\(.check)**: \(.description)"' "${OUTPUT_DIR}/report.json" 2>/dev/null || echo "None found")

## Contract Metrics
$(slither . --print contract-summary 2>/dev/null || echo "Not available")
EOF

# Check for critical issues
HIGH_COUNT=$(jq '[.results.detectors[] | select(.impact == "High")] | length' "${OUTPUT_DIR}/report.json" 2>/dev/null || echo 0)
if [ "$HIGH_COUNT" -gt 0 ]; then
    echo "⚠️  Found $HIGH_COUNT high severity issues"
    exit 1
fi

echo "✅ Slither analysis complete"