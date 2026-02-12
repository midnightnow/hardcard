#!/bin/bash
# Component Analysis Script with Gemini CLI
# Part of HardCard Suite Repair Plan

set -e

COMPONENT=$1
if [ -z "$COMPONENT" ]; then
    echo "Usage: ./analyze-component.sh <component-path>"
    echo "Example: ./analyze-component.sh frontend/src/components/Dashboard.tsx"
    exit 1
fi

if [ ! -f "$COMPONENT" ]; then
    echo "❌ Component file not found: $COMPONENT"
    exit 1
fi

echo "🔍 Analyzing component: $COMPONENT"

# Get component info
COMPONENT_NAME=$(basename "$COMPONENT" .tsx)
COMPONENT_DIR=$(dirname "$COMPONENT")
LINE_COUNT=$(wc -l < "$COMPONENT")

echo "📊 Component Stats:"
echo "  - Name: $COMPONENT_NAME"
echo "  - Lines: $LINE_COUNT"
echo "  - Location: $COMPONENT_DIR"

# Check if component is large
if [ "$LINE_COUNT" -gt 150 ]; then
    COMPLEXITY="HIGH"
    echo "⚠️ Large component detected (>150 lines)"
elif [ "$LINE_COUNT" -gt 75 ]; then
    COMPLEXITY="MEDIUM" 
    echo "📝 Medium-sized component (75-150 lines)"
else
    COMPLEXITY="LOW"
    echo "✅ Manageable component size (<75 lines)"
fi

# Analyze imports and dependencies
echo "🔍 Analyzing imports..."
IMPORT_COUNT=$(grep -c "^import" "$COMPONENT" || echo "0")
EXTERNAL_IMPORTS=$(grep "^import.*from.*['\"]@" "$COMPONENT" | wc -l || echo "0")
RELATIVE_IMPORTS=$(grep "^import.*from.*['\"]\\." "$COMPONENT" | wc -l || echo "0")

echo "📦 Import Analysis:"
echo "  - Total imports: $IMPORT_COUNT"
echo "  - External libraries: $EXTERNAL_IMPORTS"
echo "  - Local imports: $RELATIVE_IMPORTS"

# Use Gemini CLI for detailed analysis
echo "🤖 Running detailed Gemini CLI analysis..."

for i in {1..3}; do
    if gemini -p "Analyze this React component for comprehensive improvement opportunities:

COMPONENT: $COMPONENT_NAME ($LINE_COUNT lines)
COMPLEXITY: $COMPLEXITY

$(cat "$COMPONENT")

Please analyze and provide specific recommendations for:

## 1. TypeScript & Type Safety
- Missing type annotations
- Any usage of 'any' types
- Interface definitions needed
- Generic type opportunities

## 2. Component Structure & Organization
- Component size and complexity
- Single Responsibility Principle adherence
- Potential for breaking into smaller components
- Props interface design

## 3. React Best Practices
- Hook usage patterns
- State management approach
- Effect dependencies
- Performance optimization opportunities (memo, callback, etc.)

## 4. Accessibility & User Experience
- ARIA attributes
- Semantic HTML usage
- Keyboard navigation
- Screen reader compatibility

## 5. Performance Considerations
- Unnecessary re-renders
- Heavy computations that could be memoized
- Large dependency arrays
- Bundle size impact

## 6. Code Quality & Maintainability
- Code duplication
- Magic numbers/strings
- Error handling
- Documentation needs

## 7. Testing Recommendations
- What unit tests should be written
- Key user interactions to test
- Edge cases to consider

## 8. Refactoring Plan
If this component needs refactoring:
- Suggested smaller components to extract
- Shared logic that could become hooks
- Props interface improvements
- File organization recommendations

Provide specific, actionable code examples where possible." \
    --model gemini-2.5-pro \
    > "reports/component-analysis-$COMPONENT_NAME-$(date +%Y%m%d).md" 2>/dev/null; then
        echo "✅ Detailed analysis complete"
        break
    else
        echo "⚠️ Attempt $i failed, retrying in 60 seconds..."
        sleep 60
    fi
done

# Generate quick wins analysis
echo "🚀 Identifying quick wins..."

for i in {1..3}; do
    if gemini -p "Based on the component analysis, identify QUICK WINS - small changes that would have big impact:

Component: $COMPONENT_NAME

Focus on changes that can be made in under 30 minutes each:
1. Simple type annotations to add
2. Easy performance optimizations
3. Basic accessibility improvements
4. Simple refactoring opportunities
5. Missing error handling

Format as actionable checklist with estimated time for each task." \
    --model gemini-2.5-pro \
    > "reports/quick-wins-$COMPONENT_NAME-$(date +%Y%m%d).md" 2>/dev/null; then
        echo "✅ Quick wins analysis complete"
        break
    else
        echo "⚠️ Attempt $i failed, retrying in 60 seconds..."
        sleep 60
    fi
done

# Check for common React anti-patterns
echo "🔍 Checking for common anti-patterns..."

ANTI_PATTERNS=""

# Check for inline styles
if grep -q "style={{" "$COMPONENT"; then
    ANTI_PATTERNS="$ANTI_PATTERNS\n- Inline styles detected"
fi

# Check for missing keys in lists
if grep -q "\.map(" "$COMPONENT" && ! grep -q "key=" "$COMPONENT"; then
    ANTI_PATTERNS="$ANTI_PATTERNS\n- Potential missing keys in mapped elements"
fi

# Check for useEffect without dependencies
if grep -q "useEffect(" "$COMPONENT" && grep -q "useEffect([^,]*)" "$COMPONENT"; then
    ANTI_PATTERNS="$ANTI_PATTERNS\n- useEffect without dependency array detected"
fi

# Check for direct DOM manipulation
if grep -q "document\." "$COMPONENT"; then
    ANTI_PATTERNS="$ANTI_PATTERNS\n- Direct DOM manipulation detected"
fi

# Generate summary report
cat > "reports/component-summary-$COMPONENT_NAME-$(date +%Y%m%d).md" << EOF
# Component Analysis Summary: $COMPONENT_NAME

**Date:** $(date)
**File:** $COMPONENT
**Lines:** $LINE_COUNT
**Complexity:** $COMPLEXITY

## Quick Stats
- Total imports: $IMPORT_COUNT
- External libraries: $EXTERNAL_IMPORTS  
- Local imports: $RELATIVE_IMPORTS

## Potential Issues
$([ -n "$ANTI_PATTERNS" ] && echo -e "$ANTI_PATTERNS" || echo "No obvious anti-patterns detected ✅")

## Priority Actions
1. Review detailed analysis: component-analysis-$COMPONENT_NAME-$(date +%Y%m%d).md
2. Implement quick wins: quick-wins-$COMPONENT_NAME-$(date +%Y%m%d).md
3. $([ "$COMPLEXITY" = "HIGH" ] && echo "Plan component refactoring due to high complexity" || echo "Consider minor optimizations")

## Files Generated
- component-analysis-$COMPONENT_NAME-$(date +%Y%m%d).md (Detailed analysis)
- quick-wins-$COMPONENT_NAME-$(date +%Y%m%d).md (Immediate improvements)
- component-summary-$COMPONENT_NAME-$(date +%Y%m%d).md (This summary)

EOF

echo "📊 Component analysis complete!"
echo "📋 Generated reports:"
echo "  - reports/component-analysis-$COMPONENT_NAME-$(date +%Y%m%d).md"
echo "  - reports/quick-wins-$COMPONENT_NAME-$(date +%Y%m%d).md"
echo "  - reports/component-summary-$COMPONENT_NAME-$(date +%Y%m%d).md"