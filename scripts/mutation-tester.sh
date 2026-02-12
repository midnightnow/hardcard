#!/bin/bash
# Simple Mutation Testing - Verify tests fail when code is broken
# This script introduces small changes to code and verifies tests catch them

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🧬 Mutation Testing Suite${NC}"
echo "================================"
echo "Verifying tests catch broken code"
echo ""

# Configuration
BACKUP_DIR="mutation-backups/$(date +%Y%m%d-%H%M%S)"
RESULTS_FILE="$BACKUP_DIR/mutation-results.md"
TEST_COMMAND="npm test"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Initialize results
cat > "$RESULTS_FILE" << 'EOF'
# 🧬 Mutation Testing Results

## Overview
This report shows which mutations were caught by tests.

## Mutations Tested
EOF

# Mutation patterns
declare -A MUTATIONS=(
    ["toBe(true)"]="toBe(false)"
    ["toBe(false)"]="toBe(true)"
    ["=== 'success'"]="=== 'failure'"
    ["status: 200"]="status: 404"
    ["'Appointments'"]="'Broken Page'"
    ["'Dashboard'"]="'Error Page'"
    ["children.length > 0"]="children.length > 999"
    ["!== null"]="=== null"
    [".toBeTruthy()"]".toBeFalsy()"
    ["expect(true)"]="expect(false)"
)

# Function to run mutation test
run_mutation() {
    local file="$1"
    local original="$2"
    local mutated="$3"
    local mutation_name="$4"
    
    echo -n "Testing mutation: $mutation_name in $(basename $file)... "
    
    # Create backup
    cp "$file" "$BACKUP_DIR/$(basename $file).original"
    
    # Apply mutation
    sed -i.bak "s|$original|$mutated|g" "$file"
    
    # Run tests
    local test_result=0
    if $TEST_COMMAND > /dev/null 2>&1; then
        test_result=1  # Tests passed - BAD (should have failed)
        echo -e "${RED}❌ SURVIVED${NC}"
    else
        test_result=0  # Tests failed - GOOD (caught the bug)
        echo -e "${GREEN}✅ KILLED${NC}"
    fi
    
    # Restore original
    mv "$file.bak" "$file" 2>/dev/null || cp "$BACKUP_DIR/$(basename $file).original" "$file"
    
    # Log result
    local status="KILLED"
    if [ $test_result -eq 1 ]; then
        status="SURVIVED"
    fi
    
    cat >> "$RESULTS_FILE" << EOF

### $mutation_name
- **File**: $(basename $file)
- **Original**: \`$original\`
- **Mutated**: \`$mutated\`
- **Status**: $status
- **Result**: $([ $test_result -eq 0 ] && echo "✅ Tests caught the bug" || echo "❌ Tests didn't catch the bug")

EOF
    
    return $test_result
}

# Function to find and mutate files
mutate_files() {
    local pattern="$1"
    local files_found=0
    local mutations_tested=0
    local mutations_survived=0
    
    echo -e "${BLUE}Looking for files matching: $pattern${NC}"
    
    # Find test files and source files
    for file in $(find . -name "$pattern" -not -path "./node_modules/*" -not -path "./.git/*"); do
        ((files_found++))
        echo "Found: $file"
        
        # Check each mutation pattern
        for original in "${!MUTATIONS[@]}"; do
            mutated="${MUTATIONS[$original]}"
            
            # Check if file contains the pattern
            if grep -q "$original" "$file" 2>/dev/null; then
                ((mutations_tested++))
                if run_mutation "$file" "$original" "$mutated" "$(basename $file):$original"; then
                    ((mutations_survived++))
                fi
            fi
        done
    done
    
    echo ""
    echo "Files processed: $files_found"
    echo "Mutations tested: $mutations_tested"
    echo "Mutations survived: $mutations_survived"
    
    return $mutations_survived
}

# Main execution
echo -e "${YELLOW}Step 1: Running original tests to ensure they pass${NC}"
if ! $TEST_COMMAND > /dev/null 2>&1; then
    echo -e "${RED}❌ Original tests are failing! Fix tests first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Original tests pass${NC}"
echo ""

# Track totals
total_mutations=0
total_survived=0

# Test JavaScript/TypeScript files
echo -e "${BLUE}Step 2: Testing JavaScript/TypeScript files${NC}"
if mutate_files "*.js" || mutate_files "*.ts" || mutate_files "*.jsx" || mutate_files "*.tsx"; then
    total_survived=$?
fi

# Test specific test files
echo -e "${BLUE}Step 3: Testing test files specifically${NC}"
if mutate_files "*.test.*" || mutate_files "*.spec.*"; then
    ((total_survived+=$?))
fi

# Generate summary
cat >> "$RESULTS_FILE" << EOF

---

## Summary

- **Total Mutations**: $total_mutations
- **Survived (Bad)**: $total_survived
- **Killed (Good)**: $((total_mutations - total_survived))
- **Mutation Score**: $(echo "scale=1; (($total_mutations - $total_survived) * 100) / $total_mutations" | bc -l 2>/dev/null || echo "N/A")%

## Recommendations

EOF

if [ $total_survived -gt 0 ]; then
    cat >> "$RESULTS_FILE" << EOF
⚠️  **Some mutations survived!** This means your tests are not catching all bugs.

### Next Steps:
1. Review the SURVIVED mutations above
2. Add specific tests for those scenarios
3. Use stronger assertions (e.g., exact values instead of toBeTruthy)
4. Add negative test cases
5. Run mutation testing regularly

EOF
else
    cat >> "$RESULTS_FILE" << EOF
✅ **All mutations were killed!** Your tests are effectively catching bugs.

### Maintain Quality:
1. Run mutation testing before releases
2. Add new tests for new features
3. Keep mutation score above 80%

EOF
fi

# Final report
echo ""
echo -e "${PURPLE}========================================${NC}"
echo -e "${PURPLE}Mutation Testing Complete${NC}"
echo -e "${PURPLE}========================================${NC}"
echo ""

if [ $total_survived -eq 0 ]; then
    echo -e "${GREEN}🎉 Excellent! All mutations were killed.${NC}"
    echo -e "${GREEN}Your tests are effectively catching bugs.${NC}"
else
    echo -e "${RED}⚠️  $total_survived mutations survived.${NC}"
    echo -e "${RED}Your tests may not be catching all bugs.${NC}"
fi

echo ""
echo -e "${BLUE}📄 Full report: $RESULTS_FILE${NC}"
echo ""

# Suggest next steps
if [ $total_survived -gt 0 ]; then
    echo -e "${YELLOW}💡 Next Steps:${NC}"
    echo "1. Review survived mutations in the report"
    echo "2. Add specific tests for those scenarios"
    echo "3. Use the improved test file: comprehensive-vetsorcery-test-improved.js"
    echo "4. Follow the guide: docs/TEST_QUALITY_GUIDE.md"
fi

# Exit with error code if mutations survived
exit $total_survived