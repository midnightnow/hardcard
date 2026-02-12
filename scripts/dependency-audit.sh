#!/bin/bash
# Dependency Security & Optimization Audit with Gemini CLI
# Part of HardCard Suite Repair Plan

set -e

echo "📦 Running Comprehensive Dependency Audit..."
echo "⏰ Started at: $(date)"

# Create reports directory
mkdir -p ./reports

# Navigate to frontend directory
cd frontend

# Generate dependency tree and statistics
echo "📊 Analyzing dependency structure..."
npm ls --depth=2 > ../reports/npm-tree-$(date +%Y%m%d).txt 2>&1 || true
npm list --json > ../reports/npm-list-$(date +%Y%m%d).json 2>&1 || true

# Security audit
echo "🔒 Running security audit..."
npm audit --json > ../reports/npm-audit-$(date +%Y%m%d).json 2>&1 || echo '{"vulnerabilities": {}}' > ../reports/npm-audit-$(date +%Y%m%d).json

# Check for outdated packages
echo "📅 Checking for outdated packages..."
npm outdated --json > ../reports/npm-outdated-$(date +%Y%m%d).json 2>&1 || echo '{}' > ../reports/npm-outdated-$(date +%Y%m%d).json

# Check for duplicate packages
echo "🔍 Checking for duplicate packages..."
npx npm-check-duplicates > ../reports/npm-duplicates-$(date +%Y%m%d).txt 2>&1 || echo "No duplicates found" > ../reports/npm-duplicates-$(date +%Y%m%d).txt

# Analyze package.json for statistics
echo "📈 Gathering package statistics..."
TOTAL_DEPS=$(jq '.dependencies | length' package.json 2>/dev/null || echo "0")
TOTAL_DEV_DEPS=$(jq '.devDependencies | length' package.json 2>/dev/null || echo "0")
TOTAL_ALL=$((TOTAL_DEPS + TOTAL_DEV_DEPS))

# Extract dependency categories for analysis
UI_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("ui|component|design|styled|emotion|material|chakra|antd|semantic|bootstrap")) | .key' package.json 2>/dev/null | tr '\n' ',' || echo "")
CHART_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("chart|graph|plot|visual|d3|recharts|plotly|amcharts")) | .key' package.json 2>/dev/null | tr '\n' ',' || echo "")
FORM_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("form|validation|formik|hook-form|yup|joi|zod")) | .key' package.json 2>/dev/null | tr '\n' ',' || echo "")
DATE_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("date|moment|dayjs|fns")) | .key' package.json 2>/dev/null | tr '\n' ',' || echo "")
HTTP_LIBS=$(jq -r '.dependencies | to_entries[] | select(.key | test("axios|fetch|request|http|api")) | .key' package.json 2>/dev/null | tr '\n' ',' || echo "")

# Get security statistics
CRITICAL_VULNS=$(jq '.metadata.vulnerabilities.critical // 0' ../reports/npm-audit-$(date +%Y%m%d).json 2>/dev/null || echo "0")
HIGH_VULNS=$(jq '.metadata.vulnerabilities.high // 0' ../reports/npm-audit-$(date +%Y%m%d).json 2>/dev/null || echo "0")
MODERATE_VULNS=$(jq '.metadata.vulnerabilities.moderate // 0' ../reports/npm-audit-$(date +%Y%m%d).json 2>/dev/null || echo "0")
TOTAL_VULNS=$((CRITICAL_VULNS + HIGH_VULNS + MODERATE_VULNS))

# Get outdated count
OUTDATED_COUNT=$(jq 'length' ../reports/npm-outdated-$(date +%Y%m%d).json 2>/dev/null || echo "0")

echo "📊 Dependency Statistics:"
echo "  - Total dependencies: $TOTAL_ALL ($TOTAL_DEPS production + $TOTAL_DEV_DEPS dev)"
echo "  - Security vulnerabilities: $TOTAL_VULNS ($CRITICAL_VULNS critical, $HIGH_VULNS high, $MODERATE_VULNS moderate)"
echo "  - Outdated packages: $OUTDATED_COUNT"
echo "  - UI libraries: $(echo "$UI_LIBS" | tr ',' '\n' | wc -l)"
echo "  - Chart libraries: $(echo "$CHART_LIBS" | tr ',' '\n' | wc -l)"
echo "  - Form libraries: $(echo "$FORM_LIBS" | tr ',' '\n' | wc -l)"

# Use Gemini CLI for comprehensive analysis
echo "🤖 Running Gemini CLI dependency analysis..."

for i in {1..3}; do
    if gemini -p "Perform comprehensive dependency audit and optimization analysis for this React TypeScript project:

## DEPENDENCY STATISTICS
- Total packages: $TOTAL_ALL ($TOTAL_DEPS production + $TOTAL_DEV_DEPS dev)
- Security vulnerabilities: $TOTAL_VULNS ($CRITICAL_VULNS critical, $HIGH_VULNS high, $MODERATE_VULNS moderate)
- Outdated packages: $OUTDATED_COUNT

## PACKAGE CATEGORIES FOUND
- UI Libraries: $UI_LIBS
- Chart Libraries: $CHART_LIBS  
- Form Libraries: $FORM_LIBS
- Date Libraries: $DATE_LIBS
- HTTP Libraries: $HTTP_LIBS

## PACKAGE.JSON CONTENT
$(cat package.json)

## SECURITY AUDIT RESULTS
$(cat ../reports/npm-audit-$(date +%Y%m%d).json)

## OUTDATED PACKAGES
$(cat ../reports/npm-outdated-$(date +%Y%m%d).json)

## DUPLICATE PACKAGES
$(cat ../reports/npm-duplicates-$(date +%Y%m%d).txt)

Please provide a comprehensive analysis with:

### 1. CRITICAL SECURITY ISSUES
- Immediate security vulnerabilities to fix
- Packages to update or replace due to security
- Recommended security patches

### 2. REDUNDANCY ELIMINATION
- Duplicate functionality packages to remove
- Choose ONE library for each category (UI, charts, forms, dates, HTTP)
- Specific npm uninstall commands for packages to remove

### 3. BUNDLE SIZE OPTIMIZATION
- Largest packages that could be replaced with lighter alternatives
- Tree-shaking opportunities
- Dynamic import candidates

### 4. MAINTENANCE CONCERNS
- Unmaintained or deprecated packages
- Packages with infrequent updates
- Better-maintained alternatives

### 5. CONSOLIDATION PLAN
- Step-by-step migration plan
- Order of operations for safe removal
- Testing strategy for each change
- Breaking changes to watch for

### 6. AUTOMATION OPPORTUNITIES
- Scripts to automate dependency updates
- Tools to prevent future bloat
- Monitoring for new vulnerabilities

Provide specific, actionable npm commands and migration steps. Prioritize security fixes and biggest bundle size wins." \
    --model gemini-2.5-pro \
    > ../reports/dependency-analysis-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Comprehensive dependency analysis complete"
        break
    else
        echo "⚠️  Attempt $i failed, retrying in 60 seconds..."
        sleep 60
    fi
done

# Generate specific consolidation recommendations
echo "🔧 Generating consolidation recommendations..."

for i in {1..3}; do
    if gemini -p "Create specific consolidation recommendations for these dependency categories:

CURRENT STATE:
- UI Libraries ($UI_LIBS): $(echo "$UI_LIBS" | tr ',' '\n' | wc -l) packages
- Chart Libraries ($CHART_LIBS): $(echo "$CHART_LIBS" | tr ',' '\n' | wc -l) packages  
- Form Libraries ($FORM_LIBS): $(echo "$FORM_LIBS" | tr ',' '\n' | wc -l) packages
- Date Libraries ($DATE_LIBS): $(echo "$DATE_LIBS" | tr ',' '\n' | wc -l) packages
- HTTP Libraries ($HTTP_LIBS): $(echo "$HTTP_LIBS" | tr ',' '\n' | wc -l) packages

For each category, recommend:
1. **KEEP**: Which single package to standardize on
2. **REMOVE**: Which packages can be safely uninstalled
3. **MIGRATION**: Code changes needed for consolidation
4. **TIMELINE**: Order of operations (start with easiest wins)

Provide specific npm uninstall commands and estimated effort for each change." \
    --model gemini-2.5-pro \
    > ../reports/dependency-consolidation-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Consolidation recommendations complete"
        break
    else
        echo "⚠️  Consolidation attempt $i failed, retrying..."
        sleep 30
    fi
done

# Generate quick wins list
echo "🚀 Extracting dependency quick wins..."

for i in {1..3}; do
    if gemini -p "From the dependency analysis, identify QUICK WINS - dependency changes that can be made safely in under 30 minutes each:

Focus on:
1. Unused packages that can be removed immediately
2. Clear duplicates with easy migration paths
3. Security updates with no breaking changes
4. Dev dependencies that are no longer needed

Format as actionable checklist with:
- Specific npm command
- Estimated time
- Risk level (Low/Medium/High)
- Testing requirements

Only include changes that are safe and straightforward." \
    --model gemini-2.5-pro \
    > ../reports/dependency-quickwins-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Quick wins extraction complete"
        break
    else
        echo "⚠️  Quick wins attempt $i failed, retrying..."
        sleep 30
    fi
done

# Return to original directory  
cd ..

# Generate comprehensive status report
echo "📊 Generating dependency status report..."

# Calculate health score
HEALTH_SCORE="POOR"
if [ "$CRITICAL_VULNS" -eq 0 ] && [ "$HIGH_VULNS" -eq 0 ] && [ "$TOTAL_ALL" -lt 200 ]; then
    HEALTH_SCORE="EXCELLENT"
elif [ "$CRITICAL_VULNS" -eq 0 ] && [ "$HIGH_VULNS" -lt 3 ] && [ "$TOTAL_ALL" -lt 300 ]; then
    HEALTH_SCORE="GOOD"  
elif [ "$CRITICAL_VULNS" -eq 0 ] && [ "$TOTAL_ALL" -lt 400 ]; then
    HEALTH_SCORE="FAIR"
fi

cat > reports/dependency-status-$(date +%Y%m%d).md << EOF
# Dependency Audit Report

**Generated:** $(date)
**Total Packages:** $TOTAL_ALL ($TOTAL_DEPS production + $TOTAL_DEV_DEPS dev)
**Security Status:** $([ "$TOTAL_VULNS" -eq 0 ] && echo "✅ SECURE" || echo "⚠️ $TOTAL_VULNS VULNERABILITIES")
**Health Score:** $(case $HEALTH_SCORE in
    "EXCELLENT") echo "🏆 EXCELLENT";;
    "GOOD") echo "✅ GOOD";;
    "FAIR") echo "🟡 FAIR";;
    "POOR") echo "🔴 POOR";;
esac)

## Executive Summary
$(case $HEALTH_SCORE in
    "EXCELLENT") echo "Dependencies are well-managed with minimal security risks and reasonable package count.";;
    "GOOD") echo "Dependencies are mostly healthy but could benefit from minor cleanup and security updates.";;
    "FAIR") echo "Dependencies need attention - some security issues and package bloat present.";;
    "POOR") echo "Dependencies require immediate attention - critical security vulnerabilities and/or excessive package count.";;
esac)

## Security Overview
- **Critical vulnerabilities:** $CRITICAL_VULNS
- **High vulnerabilities:** $HIGH_VULNS  
- **Moderate vulnerabilities:** $MODERATE_VULNS
- **Outdated packages:** $OUTDATED_COUNT

## Package Categories Analysis
- **UI Libraries:** $(echo "$UI_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) packages $([ $(echo "$UI_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) -gt 3 ] && echo "⚠️ (Too many - consolidation needed)" || echo "✅")
- **Chart Libraries:** $(echo "$CHART_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) packages $([ $(echo "$CHART_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) -gt 2 ] && echo "⚠️ (Too many - choose one)" || echo "✅")
- **Form Libraries:** $(echo "$FORM_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) packages $([ $(echo "$FORM_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) -gt 2 ] && echo "⚠️ (Too many - standardize)" || echo "✅")
- **Date Libraries:** $(echo "$DATE_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) packages $([ $(echo "$DATE_LIBS" | tr ',' '\n' | grep -v '^$' | wc -l) -gt 1 ] && echo "⚠️ (Choose one)" || echo "✅")

## Priority Actions
$(if [ "$CRITICAL_VULNS" -gt 0 ]; then
    echo "🔥 **CRITICAL:** Fix $CRITICAL_VULNS critical security vulnerabilities immediately"
elif [ "$HIGH_VULNS" -gt 0 ]; then
    echo "🔥 **HIGH:** Address $HIGH_VULNS high-severity security vulnerabilities"
fi)

$(if [ "$TOTAL_ALL" -gt 300 ]; then
    echo "📦 **BLOAT:** Reduce package count from $TOTAL_ALL (target: <250)"
fi)

$(if [ "$OUTDATED_COUNT" -gt 10 ]; then
    echo "📅 **UPDATES:** Update $OUTDATED_COUNT outdated packages"
fi)

## Immediate Next Steps
1. **Security:** $([ "$TOTAL_VULNS" -eq 0 ] && echo "✅ No immediate security concerns" || echo "Review dependency-analysis-$(date +%Y%m%d).md for security fixes")
2. **Quick Wins:** Implement changes from dependency-quickwins-$(date +%Y%m%d).md  
3. **Consolidation:** Follow plan in dependency-consolidation-$(date +%Y%m%d).md
4. **Monitoring:** Set up automated dependency monitoring

## Files Generated
- **dependency-analysis-$(date +%Y%m%d).md** - Comprehensive Gemini CLI analysis
- **dependency-consolidation-$(date +%Y%m%d).md** - Specific consolidation plan
- **dependency-quickwins-$(date +%Y%m%d).md** - Quick, safe improvements
- **npm-audit-$(date +%Y%m%d).json** - Security audit raw data
- **npm-outdated-$(date +%Y%m%d).json** - Outdated packages data
- **npm-duplicates-$(date +%Y%m%d).txt** - Duplicate package analysis

## Trend Tracking
Track progress by comparing reports over time:
\`\`\`bash
grep "Total Packages" reports/dependency-status-*.md
grep "Security Status" reports/dependency-status-*.md
\`\`\`

EOF

echo ""
echo "📦 Dependency Audit Complete!"
echo "📊 Final Statistics:"
echo "  - Health Score: $HEALTH_SCORE"
echo "  - Total packages: $TOTAL_ALL"
echo "  - Security vulnerabilities: $TOTAL_VULNS"
echo "  - Outdated packages: $OUTDATED_COUNT"
echo ""
echo "📋 Reports generated:"
echo "  - reports/dependency-status-$(date +%Y%m%d).md (📊 Executive summary)"
echo "  - reports/dependency-analysis-$(date +%Y%m%d).md (🔍 Detailed analysis)"
echo "  - reports/dependency-consolidation-$(date +%Y%m%d).md (🔧 Action plan)"
echo "  - reports/dependency-quickwins-$(date +%Y%m%d).md (🚀 Quick improvements)"
echo ""

if [ "$CRITICAL_VULNS" -gt 0 ]; then
    echo "🚨 **CRITICAL:** $CRITICAL_VULNS critical security vulnerabilities found!"
    echo "🎯 **Next Action:** Review dependency-analysis-$(date +%Y%m%d).md immediately"
    exit 1
elif [ "$TOTAL_VULNS" -gt 0 ]; then
    echo "⚠️  **Warning:** $TOTAL_VULNS security vulnerabilities need attention"
    echo "🎯 **Next Action:** Address security issues and implement quick wins"
    exit 1
else
    echo "🎉 **Success:** No critical security issues found!"
    echo "🎯 **Next Action:** Optimize package count and implement consolidation plan"
    exit 0
fi