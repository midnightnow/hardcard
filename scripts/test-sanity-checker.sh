#!/bin/bash
# Test Sanity Checker - Ensures tests actually test something meaningful
# This script audits your tests for common anti-patterns

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🔍 Test Sanity Checker${NC}"
echo "======================="
echo "Detecting meaningless tests that always pass"
echo ""

# Create results directory
RESULTS_DIR="test-sanity-results/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

# Initialize report
cat > "$RESULTS_DIR/SANITY_REPORT.md" << 'EOF'
# 🔍 Test Sanity Check Report

## Summary
This report identifies tests that may not be testing anything meaningful.

## Red Flags Found

### 🚩 Always-Passing Tests
Tests that check for existence without verifying behavior or content.

### 🚩 Missing Assertions
Tests without proper expect/assert statements.

### 🚩 Overly Permissive Tests
Tests that pass with any non-null value.

### 🚩 No Negative Tests
Suites without any failure scenarios.

---

EOF

# Counters
TOTAL_FILES=0
SUSPICIOUS_FILES=0
RED_FLAGS=0

echo -e "${BLUE}Scanning test files...${NC}"
echo ""

# Function to check test file
check_test_file() {
    local file=$1
    local filename=$(basename "$file")
    ((TOTAL_FILES++))
    
    echo -n "Checking $filename... "
    
    local issues=()
    local file_red_flags=0
    
    # Check 1: Tests that only check existence
    if grep -E "toBeTruthy\(\)|\.exists\(\)|!== null|!= null|length > 0" "$file" > /dev/null 2>&1; then
        issues+=("Uses weak existence checks")
        ((file_red_flags++))
    fi
    
    # Check 2: Tests without assertions
    if ! grep -E "expect\(|assert\(|should\.|\.to\." "$file" > /dev/null 2>&1; then
        issues+=("No assertions found")
        ((file_red_flags++))
    fi
    
    # Check 3: Tests that catch all errors
    if grep -E "catch.*\{\s*\}" "$file" > /dev/null 2>&1; then
        issues+=("Empty catch blocks")
        ((file_red_flags++))
    fi
    
    # Check 4: Tests with no specific values
    if ! grep -E "toBe\(.*['\"].*['\"]\)|toEqual\(.*['\"].*['\"]\)|toContain\(.*['\"].*['\"]\)" "$file" > /dev/null 2>&1; then
        if grep -E "test\(|it\(|describe\(" "$file" > /dev/null 2>&1; then
            issues+=("No specific value assertions")
            ((file_red_flags++))
        fi
    fi
    
    # Check 5: Always true conditions
    if grep -E "expect\(true\)\.toBe\(true\)|assert.*true.*true" "$file" > /dev/null 2>&1; then
        issues+=("Tautological assertions")
        ((file_red_flags++))
    fi
    
    # Check 6: No negative test cases
    if ! grep -E "\.not\.|should.*not|expect.*throw|rejects|\.catch" "$file" > /dev/null 2>&1; then
        issues+=("No negative test cases")
        ((file_red_flags++))
    fi
    
    if [ $file_red_flags -gt 0 ]; then
        echo -e "${RED}❌ $file_red_flags issues${NC}"
        ((SUSPICIOUS_FILES++))
        ((RED_FLAGS += file_red_flags))
        
        # Add to report
        echo "### $filename" >> "$RESULTS_DIR/SANITY_REPORT.md"
        echo "**Issues found:**" >> "$RESULTS_DIR/SANITY_REPORT.md"
        for issue in "${issues[@]}"; do
            echo "- 🚩 $issue" >> "$RESULTS_DIR/SANITY_REPORT.md"
        done
        echo "" >> "$RESULTS_DIR/SANITY_REPORT.md"
        
        # Extract suspicious patterns
        echo "**Suspicious patterns:**" >> "$RESULTS_DIR/SANITY_REPORT.md"
        echo '```javascript' >> "$RESULTS_DIR/SANITY_REPORT.md"
        grep -n -E "toBeTruthy\(\)|\.exists\(\)|!== null|length > 0|expect\(true\)" "$file" | head -5 >> "$RESULTS_DIR/SANITY_REPORT.md" 2>/dev/null || true
        echo '```' >> "$RESULTS_DIR/SANITY_REPORT.md"
        echo "" >> "$RESULTS_DIR/SANITY_REPORT.md"
    else
        echo -e "${GREEN}✅ OK${NC}"
    fi
}

# Find and check all test files
for file in $(find . -name "*.test.*" -o -name "*.spec.*" | grep -E "\.(ts|tsx|js|jsx)$" | grep -v node_modules); do
    check_test_file "$file"
done

# Check for test files that might be too simple
echo ""
echo -e "${BLUE}Checking for overly simple tests...${NC}"

# Look for test files with very few lines
for file in $(find . -name "*.test.*" -o -name "*.spec.*" | grep -E "\.(ts|tsx|js|jsx)$" | grep -v node_modules); do
    lines=$(wc -l < "$file")
    if [ "$lines" -lt 20 ]; then
        echo -e "${YELLOW}⚠️  $(basename $file) has only $lines lines${NC}"
        echo "### ⚠️ $(basename $file) - Suspiciously Short" >> "$RESULTS_DIR/SANITY_REPORT.md"
        echo "Only $lines lines - may not be comprehensive" >> "$RESULTS_DIR/SANITY_REPORT.md"
        echo "" >> "$RESULTS_DIR/SANITY_REPORT.md"
    fi
done

# Generate recommendations
cat >> "$RESULTS_DIR/SANITY_REPORT.md" << 'EOF'

---

## 📋 Recommendations

### 1. Replace Weak Assertions
Instead of:
```javascript
expect(element).toBeTruthy();
expect(result !== null).toBe(true);
```

Use:
```javascript
expect(element).toHaveTextContent('Expected Text');
expect(result).toEqual({ specific: 'values' });
```

### 2. Add Negative Test Cases
```javascript
it('should throw error for invalid input', () => {
    expect(() => myFunction(null)).toThrow('Input cannot be null');
});
```

### 3. Test Specific Behavior
```javascript
// Bad
expect(page.title).toBeTruthy();

// Good
expect(page.title).toBe('VetSorcery - Appointments');
```

### 4. Use Snapshot Testing for UI
```javascript
expect(component).toMatchSnapshot();
```

### 5. Add Visual Regression Tests
Use tools like Percy or Chromatic for visual testing.

EOF

# Summary
echo ""
echo -e "${PURPLE}========================================${NC}"
echo -e "${PURPLE}Test Sanity Check Complete${NC}"
echo -e "${PURPLE}========================================${NC}"
echo ""
echo "Total test files scanned: $TOTAL_FILES"
echo -e "Suspicious files found: ${RED}$SUSPICIOUS_FILES${NC}"
echo -e "Total red flags: ${RED}$RED_FLAGS${NC}"
echo ""

if [ $RED_FLAGS -gt 0 ]; then
    echo -e "${RED}⚠️  Your tests may not be testing anything meaningful!${NC}"
    echo ""
    echo "Common issues found:"
    grep "^- 🚩" "$RESULTS_DIR/SANITY_REPORT.md" | sort | uniq -c | sort -nr | head -5
else
    echo -e "${GREEN}✅ Tests appear to have meaningful assertions${NC}"
fi

echo ""
echo -e "📄 Full report: ${BLUE}$RESULTS_DIR/SANITY_REPORT.md${NC}"