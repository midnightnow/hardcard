#!/bin/bash
# Daily Code Review Script with Gemini CLI
# Part of HardCard Suite Repair Plan

set -e

echo "🔍 Daily Gemini CLI Code Review - $(date)"

# Initialize git if needed and get changed files
if [ -d ".git" ]; then
    # Get changed files from last commit
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep -E '\.(ts|tsx|js|jsx|py|sol)$' || echo "")
    
    # If no changes from last commit, check working directory
    if [ -z "$CHANGED_FILES" ]; then
        CHANGED_FILES=$(git diff --name-only | grep -E '\.(ts|tsx|js|jsx|py|sol)$' || echo "")
    fi
    
    # If still no changes, check staged files
    if [ -z "$CHANGED_FILES" ]; then
        CHANGED_FILES=$(git diff --cached --name-only | grep -E '\.(ts|tsx|js|jsx|py|sol)$' || echo "")
    fi
else
    echo "⚠️ Not a git repository - checking for recently modified files..."
    # Find files modified in last 24 hours
    CHANGED_FILES=$(find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.sol" | xargs ls -lt | head -10 | awk '{print $9}' || echo "")
fi

if [ -n "$CHANGED_FILES" ]; then
    echo "📁 Files to review:"
    echo "$CHANGED_FILES" | while read -r file; do
        echo "  - $file"
    done
    
    FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l)
    echo "📊 Total files: $FILE_COUNT"
    
    # Limit to first 5 files to avoid overwhelming Gemini CLI
    if [ "$FILE_COUNT" -gt 5 ]; then
        echo "⚠️ Too many files ($FILE_COUNT), reviewing first 5..."
        CHANGED_FILES=$(echo "$CHANGED_FILES" | head -5)
    fi
    
    echo "🤖 Analyzing changes with Gemini CLI..."
    
    # Create combined content for analysis
    COMBINED_CONTENT=""
    for file in $CHANGED_FILES; do
        if [ -f "$file" ]; then
            echo "📄 Including $file in analysis..."
            COMBINED_CONTENT="$COMBINED_CONTENT\n\n=== FILE: $file ===\n$(cat "$file")"
        fi
    done
    
    # Use Gemini CLI for analysis with retry mechanism
    for i in {1..3}; do
        if gemini -p "Perform a daily code review of these changed files. Focus on:

## Files Changed:
$(echo "$CHANGED_FILES" | tr '\n' ',' | sed 's/,$//')

## Review Criteria:

### 🔒 Security & Safety
- Potential security vulnerabilities
- Input validation issues
- Authentication/authorization problems
- Data exposure risks

### 🚀 Performance & Efficiency  
- Performance bottlenecks
- Unnecessary re-renders (React)
- Memory leaks
- Inefficient algorithms

### 🧹 Code Quality
- TypeScript usage and type safety
- Code organization and clarity
- Naming conventions
- Error handling

### 🎯 Best Practices
- Framework-specific patterns (React, FastAPI, Solidity)
- Testing considerations
- Documentation needs
- Accessibility (for frontend)

### 🔧 Quick Wins
- Simple improvements that can be made immediately
- Low-effort, high-impact changes

## File Contents:
$COMBINED_CONTENT

Provide:
1. **Critical Issues** (must fix immediately)
2. **Important Improvements** (should fix this week) 
3. **Nice to Have** (future improvements)
4. **Positive Highlights** (what's working well)
5. **Specific Action Items** with priority levels

Keep recommendations actionable and specific." \
        --model gemini-2.5-pro \
        > "reports/daily-review-$(date +%Y%m%d).md" 2>/dev/null; then
            echo "✅ Daily review complete"
            break
        else
            echo "⚠️ Attempt $i failed, retrying in 60 seconds..."
            sleep 60
        fi
    done
    
    # Generate quick summary for team standup
    echo "📋 Generating standup summary..."
    
    # Extract key points for standup
    CRITICAL_COUNT=$(grep -c "CRITICAL\|must fix" "reports/daily-review-$(date +%Y%m%d).md" 2>/dev/null || echo "0")
    IMPROVEMENT_COUNT=$(grep -c "IMPORTANT\|should fix" "reports/daily-review-$(date +%Y%m%d).md" 2>/dev/null || echo "0")
    
    cat > "reports/standup-summary-$(date +%Y%m%d).md" << EOF
# Daily Standup Summary - $(date +%Y-%m-%d)

## Code Changes Reviewed
- Files changed: $FILE_COUNT
- Files analyzed: $(echo "$CHANGED_FILES" | wc -l)

## Review Results
- 🔴 Critical issues: $CRITICAL_COUNT
- 🟡 Important improvements: $IMPROVEMENT_COUNT
- 📊 Overall status: $([ "$CRITICAL_COUNT" -eq 0 ] && echo "✅ No critical issues" || echo "⚠️ Needs attention")

## Today's Focus
$([ "$CRITICAL_COUNT" -gt 0 ] && echo "1. Address critical issues found in review
2. Implement high-priority improvements" || echo "1. Continue with planned development
2. Consider implementing suggested improvements")

## Files Reviewed
$(echo "$CHANGED_FILES" | sed 's/^/- /')

📖 **Full Review:** reports/daily-review-$(date +%Y%m%d).md

EOF

    # Check for patterns that need attention
    echo "🔍 Checking for concerning patterns..."
    
    PATTERNS_FOUND=""
    
    # Check for console.log usage
    if echo "$CHANGED_FILES" | xargs grep -l "console\.log" 2>/dev/null; then
        PATTERNS_FOUND="$PATTERNS_FOUND\n- Console.log statements found (should use proper logging)"
    fi
    
    # Check for TODO/FIXME comments
    if echo "$CHANGED_FILES" | xargs grep -l "TODO\|FIXME" 2>/dev/null; then
        PATTERNS_FOUND="$PATTERNS_FOUND\n- TODO/FIXME comments found (track in issue tracker)"
    fi
    
    # Check for direct DOM manipulation in React files
    if echo "$CHANGED_FILES" | grep "\.tsx\?\$" | xargs grep -l "document\." 2>/dev/null; then
        PATTERNS_FOUND="$PATTERNS_FOUND\n- Direct DOM manipulation in React components"
    fi
    
    if [ -n "$PATTERNS_FOUND" ]; then
        echo -e "⚠️ Patterns requiring attention:$PATTERNS_FOUND"
        echo -e "\n## Patterns Requiring Attention$PATTERNS_FOUND" >> "reports/daily-review-$(date +%Y%m%d).md"
    fi
    
    echo "📊 Daily review complete!"
    echo "📋 Reports generated:"
    echo "  - reports/daily-review-$(date +%Y%m%d).md (Full analysis)"
    echo "  - reports/standup-summary-$(date +%Y%m%d).md (Team summary)"
    
else
    echo "📝 No code changes detected"
    
    # Still generate a summary
    cat > "reports/daily-review-$(date +%Y%m%d).md" << EOF
# Daily Code Review - $(date)

## Status
No code changes detected in the last 24 hours.

## Suggested Actions
1. Continue with planned development tasks
2. Consider running component analysis on existing code
3. Review and implement previous review recommendations

## Available Scripts
- \`./scripts/analyze-component.sh <component>\` - Analyze specific component
- \`./scripts/analyze-types.sh\` - Check TypeScript compliance  
- \`./scripts/analyze-dependencies.sh\` - Review package dependencies

EOF

    echo "📄 Generated placeholder report: reports/daily-review-$(date +%Y%m%d).md"
fi

# Always check overall project health
echo "🏥 Quick project health check..."

HEALTH_ISSUES=""

# Check if TypeScript strict mode is enabled
if [ -f "frontend/tsconfig.json" ]; then
    if grep -q '"strict": false' frontend/tsconfig.json; then
        HEALTH_ISSUES="$HEALTH_ISSUES\n- ⚠️ TypeScript strict mode is disabled"
    fi
fi

# Check for high dependency count
if [ -f "frontend/package.json" ]; then
    DEP_COUNT=$(jq '.dependencies | length' frontend/package.json 2>/dev/null || echo "0")
    if [ "$DEP_COUNT" -gt 200 ]; then
        HEALTH_ISSUES="$HEALTH_ISSUES\n- ⚠️ High dependency count ($DEP_COUNT packages)"
    fi
fi

# Check for large components
LARGE_COMPONENTS=$(find frontend/src/components -name "*.tsx" -exec wc -l {} + 2>/dev/null | awk '$1 > 150 {print $2" ("$1" lines)"}' | head -3)
if [ -n "$LARGE_COMPONENTS" ]; then
    HEALTH_ISSUES="$HEALTH_ISSUES\n- ⚠️ Large components detected:\n$(echo "$LARGE_COMPONENTS" | sed 's/^/  /')"
fi

if [ -n "$HEALTH_ISSUES" ]; then
    echo -e "🏥 Project Health Issues:$HEALTH_ISSUES"
    echo -e "\n## Project Health Issues$HEALTH_ISSUES" >> "reports/daily-review-$(date +%Y%m%d).md"
else
    echo "✅ No major project health issues detected"
fi

echo "🎉 Daily review workflow complete!"