#!/bin/bash
# TypeScript Analysis Script with Gemini CLI
# Part of HardCard Suite Repair Plan

set -e

echo "🔍 Analyzing TypeScript errors with Gemini CLI..."

# Ensure we're in the frontend directory
cd frontend

# Generate type error report
echo "📊 Generating TypeScript error report..."
npx tsc --noEmit > ../reports/type-errors-$(date +%Y%m%d).log 2>&1 || true

# Count errors
ERROR_COUNT=$(grep -c "error TS" ../reports/type-errors-$(date +%Y%m%d).log || echo "0")
echo "📈 Found $ERROR_COUNT TypeScript errors"

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "🤖 Using Gemini CLI to analyze and suggest fixes..."
    
    # Use Gemini CLI to analyze and suggest fixes
    # Note: Adding retry mechanism for rate limits
    for i in {1..3}; do
        if gemini -p "Analyze these TypeScript errors and provide specific, actionable fixes for each. Group by component and prioritize by severity:

$(head -50 ../reports/type-errors-$(date +%Y%m%d).log)

For each error, provide:
1. Root cause analysis
2. Specific code fix
3. Priority level (Critical/High/Medium/Low)
4. Impact on overall type safety

Focus on the most critical errors first." \
        --model gemini-2.5-pro \
        > ../reports/type-fixes-$(date +%Y%m%d).md 2>/dev/null; then
            echo "✅ Analysis complete"
            break
        else
            echo "⚠️ Attempt $i failed, retrying in 60 seconds..."
            sleep 60
        fi
    done
else
    echo "🎉 No TypeScript errors found!"
    echo "✅ TypeScript analysis complete - all types are valid" > ../reports/type-fixes-$(date +%Y%m%d).md
fi

# Generate summary report
echo "📋 Generating summary report..."
cat > ../reports/typescript-status-$(date +%Y%m%d).md << EOF
# TypeScript Analysis Report

**Date:** $(date)
**Total Errors:** $ERROR_COUNT
**Status:** $([ "$ERROR_COUNT" -eq 0 ] && echo "✅ CLEAN" || echo "⚠️ NEEDS ATTENTION")

## Next Steps
$([ "$ERROR_COUNT" -eq 0 ] && echo "- TypeScript is fully compliant
- Consider enabling additional strict checks" || echo "- Review detailed analysis in type-fixes-$(date +%Y%m%d).md
- Prioritize Critical and High severity issues
- Update tsconfig.json strict settings incrementally")

## Files Analyzed
- Source: frontend/src/
- Config: frontend/tsconfig.json
- Errors: $ERROR_COUNT

EOF

echo "📊 Reports generated:"
echo "  - type-errors-$(date +%Y%m%d).log"
echo "  - type-fixes-$(date +%Y%m%d).md" 
echo "  - typescript-status-$(date +%Y%m%d).md"

# Return to original directory
cd ..