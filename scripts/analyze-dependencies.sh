#!/bin/bash
# Dependency Analysis Script with Gemini CLI
# Part of HardCard Suite Repair Plan

set -e

echo "📦 Analyzing dependencies with Gemini CLI..."

# Ensure we're in the frontend directory
cd frontend

# Generate dependency analysis
echo "📊 Analyzing package.json..."
TOTAL_DEPS=$(jq '.dependencies | length' package.json)
TOTAL_DEV_DEPS=$(jq '.devDependencies | length' package.json)
TOTAL_ALL=$((TOTAL_DEPS + TOTAL_DEV_DEPS))

echo "📈 Found $TOTAL_DEPS dependencies and $TOTAL_DEV_DEPS dev dependencies (Total: $TOTAL_ALL)"

# Check for outdated packages
echo "🔍 Checking for outdated packages..."
npm outdated --json > ../reports/outdated-deps-$(date +%Y%m%d).json 2>/dev/null || echo "{}" > ../reports/outdated-deps-$(date +%Y%m%d).json

# Security audit
echo "🔒 Running security audit..."
npm audit --json > ../reports/security-audit-$(date +%Y%m%d).json 2>/dev/null || echo "{}" > ../reports/security-audit-$(date +%Y%m%d).json

# Bundle analysis (if build exists)
if [ -d "dist" ]; then
    echo "📦 Analyzing bundle size..."
    du -sh dist/* > ../reports/bundle-analysis-$(date +%Y%m%d).txt 2>/dev/null || echo "No build found" > ../reports/bundle-analysis-$(date +%Y%m%d).txt
fi

# Use Gemini CLI to analyze dependencies
echo "🤖 Using Gemini CLI to analyze dependency optimization opportunities..."

# Retry mechanism for rate limits
for i in {1..3}; do
    if gemini -p "Analyze this package.json for dependency optimization. Identify:

1. **Duplicate/Overlapping Libraries**: Libraries that serve similar purposes
2. **Unnecessary Dependencies**: Packages that might not be needed
3. **Size Impact**: Large packages that could be replaced with lighter alternatives
4. **Security Concerns**: Packages with known vulnerabilities
5. **Maintenance Issues**: Packages that are outdated or unmaintained

Package.json content:
$(cat package.json)

Outdated packages:
$(cat ../reports/outdated-deps-$(date +%Y%m%d).json)

Security audit:
$(cat ../reports/security-audit-$(date +%Y%m%d).json)

Provide:
- Specific packages to remove
- Recommended replacements
- Consolidation opportunities
- Priority order for changes" \
    --model gemini-2.5-pro \
    > ../reports/dependency-optimization-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Dependency analysis complete"
        break
    else
        echo "⚠️ Attempt $i failed, retrying in 60 seconds..."
        sleep 60
    fi
done

# Generate specific analysis for common issues
echo "🔍 Analyzing specific dependency categories..."

# UI Library Analysis
UI_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("ui|component|design")) | .key' package.json)
echo "🎨 UI Libraries found: $UI_LIBS" > ../reports/ui-library-analysis-$(date +%Y%m%d).txt

# Chart Library Analysis  
CHART_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("chart|graph|plot|visual")) | .key' package.json)
echo "📊 Chart Libraries found: $CHART_LIBS" > ../reports/chart-library-analysis-$(date +%Y%m%d).txt

# Form Library Analysis
FORM_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("form|validation")) | .key' package.json)
echo "📝 Form Libraries found: $FORM_LIBS" > ../reports/form-library-analysis-$(date +%Y%m%d).txt

# Generate consolidation recommendations
echo "🔧 Generating specific consolidation plan..."

for i in {1..3}; do
    if gemini -p "Based on this analysis of UI, Chart, and Form libraries, create a specific consolidation plan:

UI Libraries: $UI_LIBS
Chart Libraries: $CHART_LIBS  
Form Libraries: $FORM_LIBS

Recommend:
1. Which single UI library to keep (likely Radix UI + Tailwind)
2. Which single chart library to standardize on
3. Which form solution to use consistently
4. Step-by-step migration plan
5. Code changes needed for consolidation

Priority: Focus on removing the most redundant packages first." \
    --model gemini-2.5-pro \
    > ../reports/consolidation-plan-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Consolidation analysis complete"
        break
    else
        echo "⚠️ Attempt $i failed, retrying in 60 seconds..."
        sleep 60
    fi
done

# Generate summary report
SECURITY_ISSUES=$(jq '.metadata.vulnerabilities.total // 0' ../reports/security-audit-$(date +%Y%m%d).json)
OUTDATED_COUNT=$(jq 'length' ../reports/outdated-deps-$(date +%Y%m%d).json)

cat > ../reports/dependency-status-$(date +%Y%m%d).md << EOF
# Dependency Analysis Report

**Date:** $(date)
**Total Dependencies:** $TOTAL_ALL ($TOTAL_DEPS production + $TOTAL_DEV_DEPS dev)
**Security Issues:** $SECURITY_ISSUES
**Outdated Packages:** $OUTDATED_COUNT
**Status:** $([ "$SECURITY_ISSUES" -eq 0 ] && echo "✅ SECURE" || echo "⚠️ NEEDS ATTENTION")

## Summary
- UI Libraries: $(echo "$UI_LIBS" | wc -w) found
- Chart Libraries: $(echo "$CHART_LIBS" | wc -w) found  
- Form Libraries: $(echo "$FORM_LIBS" | wc -w) found

## Action Items
1. Review dependency-optimization-$(date +%Y%m%d).md for detailed analysis
2. Follow consolidation-plan-$(date +%Y%m%d).md for specific steps
3. Address security issues if any found
4. Update outdated packages systematically

## Files Generated
- dependency-optimization-$(date +%Y%m%d).md (Detailed analysis)
- consolidation-plan-$(date +%Y%m%d).md (Action plan)
- security-audit-$(date +%Y%m%d).json (Security details)
- outdated-deps-$(date +%Y%m%d).json (Update opportunities)

EOF

echo "📊 Dependency analysis complete!"
echo "📋 Reports generated in reports/ directory"

# Return to original directory
cd ..