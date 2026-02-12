#!/bin/bash
# TypeScript Strict Mode Check with Gemini CLI Analysis
# Part of HardCard Suite Repair Plan

set -e

echo "🔍 Running TypeScript Strict Mode Check..."
echo "⏰ Started at: $(date)"

# Create reports directory
mkdir -p ./reports

# Navigate to frontend directory
cd frontend

# Check current TypeScript configuration
echo "📋 Current TypeScript Configuration:"
if grep -q '"strict": false' tsconfig.json; then
    echo "⚠️  Strict mode is currently DISABLED"
    STRICT_ENABLED=false
else
    echo "✅ Strict mode is ENABLED"
    STRICT_ENABLED=true
fi

# Run TypeScript check
echo "🔧 Running TypeScript compilation check..."
if npx tsc --noEmit --strict > ../reports/typescript-errors-$(date +%Y%m%d).log 2>&1; then
    echo "✅ No TypeScript errors found with strict mode!"
    ERROR_COUNT=0
else
    ERROR_COUNT=$(grep -c "error TS" ../reports/typescript-errors-$(date +%Y%m%d).log || echo "0")
    echo "⚠️  Found $ERROR_COUNT TypeScript errors"
fi

# If errors found, analyze with Gemini CLI
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "🤖 Analyzing TypeScript errors with Gemini CLI..."
    
    # Limit analysis to first 50 errors to avoid overwhelming Gemini
    head -50 ../reports/typescript-errors-$(date +%Y%m%d).log > ../reports/typescript-errors-sample.log
    
    # Retry mechanism for Gemini CLI
    for i in {1..3}; do
        if gemini -p "Analyze these TypeScript strict mode errors and provide actionable solutions:

CONTEXT: HardCard Suite - React TypeScript frontend with strict mode migration
ERROR COUNT: $ERROR_COUNT errors found
CURRENT STATUS: Strict mode $([ "$STRICT_ENABLED" = true ] && echo "ENABLED" || echo "DISABLED")

ERRORS TO ANALYZE:
$(cat ../reports/typescript-errors-sample.log)

Please provide:

## 1. Error Categories
Group errors by type (e.g., missing types, null safety, any usage, etc.)

## 2. Priority Fixes (Critical - fix first)
- Errors that could cause runtime issues
- Security-related type issues
- Performance-impacting problems

## 3. Batch Fix Strategies
- Patterns that can be fixed across multiple files
- Automated fixes possible with find/replace
- Common interface definitions needed

## 4. Specific Code Fixes
For the top 10 most critical errors, provide:
- File and line number
- Current problematic code
- Corrected code example
- Explanation of why the fix is needed

## 5. Migration Strategy
- Order of files to fix (least to most complex)
- Breaking changes to watch for
- Testing strategy for each fix

## 6. Automation Opportunities
- Scripts that could be written to fix repetitive issues
- ESLint rules to prevent regression
- IDE settings to help developers

Focus on practical, actionable solutions that can be implemented immediately." \
        --model gemini-2.5-pro \
        > ../reports/typescript-fixes-$(date +%Y%m%d).md 2>/dev/null; then
            echo "✅ Gemini CLI analysis complete"
            break
        else
            echo "⚠️  Attempt $i failed, retrying in 60 seconds..."
            sleep 60
        fi
    done
    
    # Create quick wins extraction
    echo "🚀 Extracting quick wins..."
    for i in {1..3}; do
        if gemini -p "From the TypeScript errors analyzed, extract QUICK WINS - fixes that can be completed in under 15 minutes each:

ERRORS:
$(head -20 ../reports/typescript-errors-sample.log)

Provide:
1. Simple type annotations to add
2. Easy interface definitions
3. Null checks that can be added quickly
4. Import fixes
5. Basic generic type additions

Format as actionable checklist with estimated time and priority for each fix." \
        --model gemini-2.5-pro \
        > ../reports/typescript-quickwins-$(date +%Y%m%d).md 2>/dev/null; then
            echo "✅ Quick wins analysis complete"
            break
        else
            echo "⚠️  Quick wins attempt $i failed, retrying..."
            sleep 30
        fi
    done
    
else
    echo "🎉 No TypeScript errors found!"
    echo "✅ TypeScript strict mode compliance achieved" > ../reports/typescript-fixes-$(date +%Y%m%d).md
    echo "✅ No quick wins needed - code is clean" > ../reports/typescript-quickwins-$(date +%Y%m%d).md
fi

# Generate comprehensive status report
echo "📊 Generating TypeScript status report..."

# Get additional stats
TOTAL_TS_FILES=$(find src -name "*.ts" -o -name "*.tsx" | wc -l)
ANY_USAGE=$(grep -r ": any\|<any>" src --include="*.ts" --include="*.tsx" | wc -l || echo "0")
INTERFACE_COUNT=$(grep -r "interface " src --include="*.ts" --include="*.tsx" | wc -l || echo "0")

cat > ../reports/typescript-status-$(date +%Y%m%d).md << EOF
# TypeScript Analysis Report

**Generated:** $(date)
**Strict Mode:** $([ "$STRICT_ENABLED" = true ] && echo "✅ ENABLED" || echo "❌ DISABLED") 
**Status:** $([ "$ERROR_COUNT" -eq 0 ] && echo "✅ CLEAN" || echo "⚠️ NEEDS ATTENTION")

## Summary Statistics
- **Total TypeScript Files:** $TOTAL_TS_FILES
- **Compilation Errors:** $ERROR_COUNT
- **Any Type Usage:** $ANY_USAGE occurrences
- **Interface Definitions:** $INTERFACE_COUNT

## Health Score
$(if [ "$ERROR_COUNT" -eq 0 ] && [ "$ANY_USAGE" -lt 10 ]; then
    echo "🏆 **EXCELLENT** - Production ready type safety"
elif [ "$ERROR_COUNT" -lt 20 ] && [ "$ANY_USAGE" -lt 50 ]; then
    echo "🟡 **GOOD** - Minor improvements needed"
elif [ "$ERROR_COUNT" -lt 100 ]; then
    echo "🟠 **FAIR** - Significant work required"
else
    echo "🔴 **POOR** - Major type safety issues"
fi)

## Priority Actions
$(if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "- ✅ TypeScript is fully compliant
- Consider enabling additional strict checks (exactOptionalPropertyTypes, noImplicitReturns)
- Review and reduce any type usage to <5 occurrences"
else
    echo "- 🔥 **IMMEDIATE:** Review typescript-fixes-$(date +%Y%m%d).md for detailed analysis
- 🚀 **QUICK WINS:** Implement fixes from typescript-quickwins-$(date +%Y%m%d).md
- 📋 **SYSTEMATIC:** Enable strict mode incrementally by directory
- 🧪 **TESTING:** Add type tests for critical interfaces"
fi)

## Next Steps
1. $([ "$STRICT_ENABLED" = false ] && echo "Enable strict mode in tsconfig.json" || echo "Maintain strict mode compliance")
2. $([ "$ERROR_COUNT" -gt 0 ] && echo "Fix critical errors identified in analysis" || echo "Focus on reducing any type usage")
3. $([ "$ANY_USAGE" -gt 20 ] && echo "Reduce any type usage through proper typing" || echo "Add additional type safety checks")
4. Set up pre-commit hooks to prevent type regressions

## Files Generated
- **typescript-errors-$(date +%Y%m%d).log** - Raw TypeScript compiler output
- **typescript-fixes-$(date +%Y%m%d).md** - Detailed Gemini CLI analysis and solutions
- **typescript-quickwins-$(date +%Y%m%d).md** - Quick fixes that can be implemented immediately
- **typescript-status-$(date +%Y%m%d).md** - This comprehensive status report

## Trend Tracking
To track progress over time, compare error counts:
\`\`\`bash
# Compare with previous reports
ls -la reports/typescript-status-*.md
grep "Compilation Errors" reports/typescript-status-*.md
\`\`\`

EOF

# Return to original directory
cd ..

echo ""
echo "📊 TypeScript Analysis Complete!"
echo "📈 Statistics:"
echo "  - TypeScript files: $TOTAL_TS_FILES"
echo "  - Compilation errors: $ERROR_COUNT"
echo "  - Any type usage: $ANY_USAGE"
echo "  - Interface definitions: $INTERFACE_COUNT"
echo ""
echo "📋 Reports generated:"
echo "  - reports/typescript-status-$(date +%Y%m%d).md (📊 Status overview)"
echo "  - reports/typescript-fixes-$(date +%Y%m%d).md (🔧 Detailed fixes)"
echo "  - reports/typescript-quickwins-$(date +%Y%m%d).md (🚀 Quick improvements)"
echo "  - reports/typescript-errors-$(date +%Y%m%d).log (📄 Raw output)"
echo ""

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "🎯 **Next Action:** Review typescript-fixes-$(date +%Y%m%d).md and start with quick wins"
    exit 1
else
    echo "🎉 **Success:** TypeScript is in excellent condition!"
    exit 0
fi