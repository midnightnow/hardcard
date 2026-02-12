#!/bin/bash
# Large Component Analysis & Refactoring Script with Gemini CLI
# Part of HardCard Suite Repair Plan

set -e

echo "🧱 Analyzing Large Components for Refactoring..."
echo "⏰ Started at: $(date)"

# Create reports directory
mkdir -p ./reports

# Find all TypeScript React components
echo "🔍 Scanning for React components..."

if [ ! -d "frontend/src" ]; then
    echo "❌ Frontend source directory not found!"
    echo "Expected: frontend/src"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Find all TSX files and analyze their sizes
echo "📊 Analyzing component sizes..."
find frontend/src -name "*.tsx" -type f -exec wc -l {} \; | sort -nr > reports/all-components-$(date +%Y%m%d).txt

# Get statistics
TOTAL_COMPONENTS=$(wc -l < reports/all-components-$(date +%Y%m%d).txt)
LARGE_COMPONENTS=$(awk '$1 > 200' reports/all-components-$(date +%Y%m%d).txt | wc -l)
HUGE_COMPONENTS=$(awk '$1 > 400' reports/all-components-$(date +%Y%m%d).txt | wc -l)
LARGEST_SIZE=$(head -1 reports/all-components-$(date +%Y%m%d).txt | awk '{print $1}')

echo "📈 Component Statistics:"
echo "  - Total components: $TOTAL_COMPONENTS"
echo "  - Large components (>200 lines): $LARGE_COMPONENTS"
echo "  - Huge components (>400 lines): $HUGE_COMPONENTS"
echo "  - Largest component: $LARGEST_SIZE lines"

# Extract top 15 largest components for detailed analysis
head -15 reports/all-components-$(date +%Y%m%d).txt > reports/largest-components-$(date +%Y%m%d).txt

echo "🔍 Top 15 Largest Components:"
cat reports/largest-components-$(date +%Y%m%d).txt

# Extract components that definitely need refactoring (>300 lines)
awk '$1 > 300' reports/all-components-$(date +%Y%m%d).txt > reports/components-needing-refactor-$(date +%Y%m%d).txt
REFACTOR_COUNT=$(wc -l < reports/components-needing-refactor-$(date +%Y%m%d).txt)

if [ "$REFACTOR_COUNT" -gt 0 ]; then
    echo "⚠️  Found $REFACTOR_COUNT components requiring immediate refactoring (>300 lines)"
else
    echo "✅ No components found requiring immediate refactoring"
fi

# Use Gemini CLI for comprehensive component analysis
echo "🤖 Running Gemini CLI analysis on large components..."

for i in {1..3}; do
    if gemini -p "Analyze these React component sizes and provide comprehensive refactoring strategy:

## PROJECT CONTEXT
- React TypeScript frontend
- Target: Components should be <200 lines
- Critical: Components >400 lines need immediate refactoring
- Components >300 lines need planning for refactoring

## COMPONENT SIZE ANALYSIS
Total Components: $TOTAL_COMPONENTS
Large Components (>200 lines): $LARGE_COMPONENTS  
Huge Components (>400 lines): $HUGE_COMPONENTS
Largest Component: $LARGEST_SIZE lines

## TOP 15 LARGEST COMPONENTS
$(cat reports/largest-components-$(date +%Y%m%d).txt)

## COMPONENTS REQUIRING IMMEDIATE REFACTORING (>300 lines)
$(cat reports/components-needing-refactor-$(date +%Y%m%d).txt)

Please provide:

### 1. PRIORITY CLASSIFICATION
Classify each large component by refactoring priority:
- **CRITICAL** (>400 lines): Must refactor immediately
- **HIGH** (300-400 lines): Refactor within 2 weeks
- **MEDIUM** (200-300 lines): Refactor when touching the code
- **LOW** (<200 lines): Monitor for growth

### 2. REFACTORING STRATEGIES
For each component needing refactoring, suggest:
- Specific smaller components to extract
- Shared logic that could become custom hooks
- State management that could be externalized
- UI patterns that could be componentized

### 3. IMPLEMENTATION PLAN
- Order of refactoring (start with highest impact/lowest risk)
- Estimated effort for each component (hours)
- Dependencies between components
- Testing strategy for each refactoring

### 4. COMPONENT EXTRACTION PATTERNS
Common patterns to look for:
- Form sections that could be separate components
- Modal/dialog content extraction
- List item components
- Header/footer/sidebar extractions
- Conditional rendering blocks

### 5. ARCHITECTURE IMPROVEMENTS
- Consistent prop interface patterns
- Component composition opportunities
- State management consolidation
- Performance optimization opportunities

### 6. PREVENTION STRATEGIES
- ESLint rules to prevent large components
- Component development guidelines
- Code review checklist items
- Automated monitoring for component growth

Focus on practical, step-by-step refactoring plans with specific code extraction recommendations." \
    --model gemini-2.5-pro \
    > reports/component-refactoring-analysis-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Comprehensive component analysis complete"
        break
    else
        echo "⚠️  Attempt $i failed, retrying in 60 seconds..."
        sleep 60
    fi
done

# Generate quick wins for component refactoring
echo "🚀 Identifying component refactoring quick wins..."

for i in {1..3}; do
    if gemini -p "From the component analysis, identify QUICK WINS for component refactoring - changes that can be completed in 1-2 hours each:

LARGE COMPONENTS:
$(head -10 reports/largest-components-$(date +%Y%m%d).txt)

Focus on:
1. **Simple Extractions**: UI elements that can be moved to separate files with minimal changes
2. **Hook Extractions**: Business logic that can become custom hooks
3. **Constant Extractions**: Large objects/arrays that can be moved to separate files
4. **Type Extractions**: Interface definitions that can be moved to types files
5. **Utility Extractions**: Helper functions that can be moved to utils

For each quick win provide:
- Component file to modify
- Specific code to extract
- New file name and location
- Estimated time (15min, 30min, 1hr, 2hr)
- Risk level (Low/Medium)
- Testing requirements

Only include refactoring that:
- Takes <2 hours to complete
- Has low risk of breaking functionality
- Doesn't require major prop interface changes
- Can be tested easily

Format as actionable checklist with priority order." \
    --model gemini-2.5-pro \
    > reports/component-quickwins-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Quick wins analysis complete"
        break
    else
        echo "⚠️  Quick wins attempt $i failed, retrying..."
        sleep 30
    fi
done

# Analyze specific patterns in large components
echo "🔍 Analyzing common anti-patterns in large components..."

ANTI_PATTERNS_FOUND=""

# Check for common issues in the largest components
for component_file in $(head -5 reports/largest-components-$(date +%Y%m%d).txt | awk '{print $2}'); do
    if [ -f "$component_file" ]; then
        echo "  📄 Analyzing $component_file..."
        
        # Check for multiple useState calls (could be consolidated)
        usestate_count=$(grep -c "useState(" "$component_file" || echo "0")
        if [ "$usestate_count" -gt 5 ]; then
            ANTI_PATTERNS_FOUND="$ANTI_PATTERNS_FOUND\n- $component_file: $usestate_count useState calls (consider useReducer)"
        fi
        
        # Check for inline styles
        if grep -q "style={{" "$component_file"; then
            ANTI_PATTERNS_FOUND="$ANTI_PATTERNS_FOUND\n- $component_file: Inline styles detected (extract to classes)"
        fi
        
        # Check for long useEffect dependencies
        long_deps=$(grep -o "useEffect([^,]*\[[^]]\{50,\}" "$component_file" | wc -l || echo "0")
        if [ "$long_deps" -gt 0 ]; then
            ANTI_PATTERNS_FOUND="$ANTI_PATTERNS_FOUND\n- $component_file: Long useEffect dependency arrays detected"
        fi
        
        # Check for deeply nested JSX (potential for extraction)
        deep_nesting=$(grep -o "^\s\{20,\}" "$component_file" | wc -l || echo "0")
        if [ "$deep_nesting" -gt 10 ]; then
            ANTI_PATTERNS_FOUND="$ANTI_PATTERNS_FOUND\n- $component_file: Deep JSX nesting detected (extract components)"
        fi
    fi
done

# Generate specific refactoring recommendations for top 3 components
echo "📋 Generating specific refactoring plans for top 3 components..."

TOP_3_COMPONENTS=$(head -3 reports/largest-components-$(date +%Y%m%d).txt)

for i in {1..3}; do
    if gemini -p "Generate specific, actionable refactoring plans for these top 3 largest components:

$TOP_3_COMPONENTS

For EACH component, provide a detailed refactoring plan including:

## Component-Specific Analysis
1. **Current Structure**: What makes this component large
2. **Extraction Opportunities**: Specific sections to extract
3. **New Component Names**: Suggested names for extracted components
4. **Props Interface**: How extracted components should communicate
5. **Testing Strategy**: How to ensure refactoring doesn't break functionality

## Step-by-Step Plan
1. **Phase 1**: Safest extractions first (15-30 min each)
2. **Phase 2**: Medium complexity extractions (1-2 hours each)  
3. **Phase 3**: Complex extractions requiring interface changes
4. **Validation**: Testing and verification steps

## Code Examples
- Show before/after code snippets for key extractions
- Include proper TypeScript interfaces
- Show how parent component will use extracted components

Focus on practical, implementable steps that reduce component size while improving maintainability." \
    --model gemini-2.5-pro \
    > reports/top-components-refactor-plan-$(date +%Y%m%d).md 2>/dev/null; then
        echo "✅ Specific refactoring plans complete"
        break
    else
        echo "⚠️  Specific plans attempt $i failed, retrying..."
        sleep 30
    fi
done

# Generate comprehensive status report
echo "📊 Generating component analysis status report..."

# Determine health score
HEALTH_SCORE="POOR"
if [ "$HUGE_COMPONENTS" -eq 0 ] && [ "$LARGE_COMPONENTS" -lt 5 ]; then
    HEALTH_SCORE="EXCELLENT"
elif [ "$HUGE_COMPONENTS" -eq 0 ] && [ "$LARGE_COMPONENTS" -lt 10 ]; then
    HEALTH_SCORE="GOOD"
elif [ "$HUGE_COMPONENTS" -lt 3 ] && [ "$LARGE_COMPONENTS" -lt 20 ]; then
    HEALTH_SCORE="FAIR"
fi

cat > reports/component-analysis-status-$(date +%Y%m%d).md << EOF
# Component Size Analysis Report

**Generated:** $(date)
**Total Components:** $TOTAL_COMPONENTS
**Health Score:** $(case $HEALTH_SCORE in
    "EXCELLENT") echo "🏆 EXCELLENT";;
    "GOOD") echo "✅ GOOD";;
    "FAIR") echo "🟡 FAIR";;
    "POOR") echo "🔴 POOR";;
esac)

## Component Size Distribution
- **Total Components:** $TOTAL_COMPONENTS
- **Small (<200 lines):** $((TOTAL_COMPONENTS - LARGE_COMPONENTS))
- **Large (200-400 lines):** $((LARGE_COMPONENTS - HUGE_COMPONENTS))
- **Huge (>400 lines):** $HUGE_COMPONENTS

## Largest Component
**Size:** $LARGEST_SIZE lines
$(head -1 reports/largest-components-$(date +%Y%m%d).txt | awk '{print "**File:** " $2}')

## Health Assessment
$(case $HEALTH_SCORE in
    "EXCELLENT") echo "Component sizes are well-managed. Continue monitoring for growth.";;
    "GOOD") echo "Most components are reasonable size. Some optimization opportunities exist.";;
    "FAIR") echo "Several large components need attention. Plan refactoring for largest ones.";;
    "POOR") echo "Multiple huge components require immediate refactoring to improve maintainability.";;
esac)

## Anti-Patterns Detected
$([ -n "$ANTI_PATTERNS_FOUND" ] && echo -e "$ANTI_PATTERNS_FOUND" || echo "No obvious anti-patterns detected in sample analysis ✅")

## Priority Actions
$(if [ "$HUGE_COMPONENTS" -gt 0 ]; then
    echo "🔥 **CRITICAL:** Refactor $HUGE_COMPONENTS components over 400 lines immediately"
elif [ "$LARGE_COMPONENTS" -gt 10 ]; then
    echo "⚠️ **HIGH:** Plan refactoring for $LARGE_COMPONENTS large components"
else
    echo "✅ **MAINTENANCE:** Monitor component growth and prevent large components"
fi)

## Immediate Next Steps
1. **Quick Wins:** Implement changes from component-quickwins-$(date +%Y%m%d).md
2. **Detailed Plans:** Follow top-components-refactor-plan-$(date +%Y%m%d).md for largest components  
3. **Architecture:** Review component-refactoring-analysis-$(date +%Y%m%d).md for strategy
4. **Prevention:** Set up ESLint rules to prevent large components

## Components Requiring Immediate Refactoring (>300 lines)
$(if [ "$REFACTOR_COUNT" -gt 0 ]; then
    cat reports/components-needing-refactor-$(date +%Y%m%d).txt
else
    echo "✅ No components require immediate refactoring"
fi)

## Files Generated
- **component-refactoring-analysis-$(date +%Y%m%d).md** - Comprehensive analysis and strategy
- **component-quickwins-$(date +%Y%m%d).md** - Quick, safe refactoring opportunities
- **top-components-refactor-plan-$(date +%Y%m%d).md** - Detailed plans for largest components
- **largest-components-$(date +%Y%m%d).txt** - Top 15 largest components by line count
- **components-needing-refactor-$(date +%Y%m%d).txt** - Components >300 lines requiring attention

## Trend Tracking
Monitor component size trends over time:
\`\`\`bash
# Compare largest component sizes
grep "Largest Component" reports/component-analysis-status-*.md

# Track refactoring progress  
grep "Huge (>400 lines)" reports/component-analysis-status-*.md
\`\`\`

## ESLint Rule Recommendation
Add to .eslintrc.js to prevent large components:
\`\`\`javascript
{
  "rules": {
    "max-lines-per-function": ["warn", { "max": 200, "skipBlankLines": true }],
    "max-lines": ["error", { "max": 300, "skipBlankLines": true, "skipComments": true }]
  }
}
\`\`\`

EOF

echo ""
echo "🧱 Component Analysis Complete!"
echo "📊 Final Statistics:"
echo "  - Health Score: $HEALTH_SCORE"
echo "  - Total components: $TOTAL_COMPONENTS"
echo "  - Large components (>200 lines): $LARGE_COMPONENTS"
echo "  - Huge components (>400 lines): $HUGE_COMPONENTS"
echo "  - Largest component: $LARGEST_SIZE lines"
echo ""
echo "📋 Reports generated:"
echo "  - reports/component-analysis-status-$(date +%Y%m%d).md (📊 Executive summary)"
echo "  - reports/component-refactoring-analysis-$(date +%Y%m%d).md (🔍 Strategy & analysis)"
echo "  - reports/component-quickwins-$(date +%Y%m%d).md (🚀 Quick improvements)"
echo "  - reports/top-components-refactor-plan-$(date +%Y%m%d).md (📋 Detailed plans)"
echo ""

if [ "$HUGE_COMPONENTS" -gt 0 ]; then
    echo "🚨 **CRITICAL:** $HUGE_COMPONENTS components over 400 lines found!"
    echo "🎯 **Next Action:** Review top-components-refactor-plan-$(date +%Y%m%d).md and start refactoring"
    exit 1
elif [ "$LARGE_COMPONENTS" -gt 15 ]; then
    echo "⚠️  **Warning:** $LARGE_COMPONENTS large components need attention"
    echo "🎯 **Next Action:** Implement quick wins and plan systematic refactoring"
    exit 1
else
    echo "🎉 **Success:** Component sizes are well-managed!"
    echo "🎯 **Next Action:** Continue monitoring and implement prevention measures"
    exit 0
fi