#!/bin/bash
# Safe TypeScript Migration Script
# Enables TypeScript strict mode incrementally without breaking functionality

set -e
echo "🔐 Safe TypeScript Migration Tool"
echo "================================"
echo "This script enables TypeScript strict mode incrementally"
echo ""

# Check current state
cd frontend
echo "📊 Current TypeScript Configuration:"
grep -E '"strict"|"noImplicitAny"|"strictNullChecks"' tsconfig.json | sed 's/^/  /'
echo ""

# Create backup
cp tsconfig.json tsconfig.json.backup
echo "✅ Backup created: tsconfig.json.backup"
echo ""

# Function to test build after changes
test_build() {
    echo -n "  Testing build... "
    if npm run build > /dev/null 2>&1; then
        echo "✅ Build successful"
        return 0
    else
        echo "❌ Build failed"
        return 1
    fi
}

# Function to count errors
count_errors() {
    local count=$(npx tsc --noEmit 2>&1 | grep -c "error TS" || echo "0")
    echo "$count"
}

# Phase selection
echo "🎯 Select migration phase:"
echo "1. Phase 1: Enable noImplicitAny only (safest)"
echo "2. Phase 2: Add strictNullChecks (after Phase 1 complete)"
echo "3. Phase 3: Add strictFunctionTypes (after Phase 2 complete)"
echo "4. Phase 4: Enable full strict mode (final phase)"
echo "5. Check current status only"
echo "6. Rollback to backup"
echo ""
read -p "Enter choice (1-6): " PHASE

case $PHASE in
    1)
        echo ""
        echo "🔧 Phase 1: Enabling noImplicitAny..."
        
        # Check baseline errors
        BEFORE_ERRORS=$(count_errors)
        echo "  Current errors: $BEFORE_ERRORS"
        
        # Update tsconfig.json
        node -e "
        const fs = require('fs');
        const config = JSON.parse(fs.readFileSync('tsconfig.json', 'utf8'));
        config.compilerOptions.noImplicitAny = true;
        fs.writeFileSync('tsconfig.json', JSON.stringify(config, null, 2));
        "
        
        # Check new error count
        AFTER_ERRORS=$(count_errors)
        echo "  New errors: $AFTER_ERRORS"
        echo "  Additional errors: $((AFTER_ERRORS - BEFORE_ERRORS))"
        
        # Test build
        if test_build; then
            echo ""
            echo "✅ Phase 1 enabled successfully!"
            echo ""
            echo "📋 Next steps:"
            echo "1. Fix the $((AFTER_ERRORS - BEFORE_ERRORS)) new type errors"
            echo "2. Use any-fix.sh script to help fix them safely"
            echo "3. Commit changes when all errors are resolved"
        else
            echo ""
            echo "❌ Build failed! Rolling back..."
            cp tsconfig.json.backup tsconfig.json
            echo "✅ Rolled back to previous configuration"
            exit 1
        fi
        ;;
        
    2)
        echo ""
        echo "🔧 Phase 2: Enabling strictNullChecks..."
        
        # First check if Phase 1 is complete
        if ! grep -q '"noImplicitAny": true' tsconfig.json; then
            echo "❌ Error: Phase 1 (noImplicitAny) must be completed first!"
            exit 1
        fi
        
        BEFORE_ERRORS=$(count_errors)
        echo "  Current errors: $BEFORE_ERRORS"
        
        if [ "$BEFORE_ERRORS" -gt "0" ]; then
            echo "⚠️  Warning: You still have $BEFORE_ERRORS errors from Phase 1"
            read -p "Continue anyway? (y/n): " CONTINUE
            if [ "$CONTINUE" != "y" ]; then
                exit 0
            fi
        fi
        
        # Update tsconfig.json
        node -e "
        const fs = require('fs');
        const config = JSON.parse(fs.readFileSync('tsconfig.json', 'utf8'));
        config.compilerOptions.strictNullChecks = true;
        fs.writeFileSync('tsconfig.json', JSON.stringify(config, null, 2));
        "
        
        AFTER_ERRORS=$(count_errors)
        echo "  New errors: $AFTER_ERRORS"
        echo "  Additional errors: $((AFTER_ERRORS - BEFORE_ERRORS))"
        
        if test_build; then
            echo "✅ Phase 2 enabled successfully!"
        else
            echo "❌ Build failed! Rolling back..."
            cp tsconfig.json.backup tsconfig.json
            exit 1
        fi
        ;;
        
    3)
        echo ""
        echo "🔧 Phase 3: Enabling strictFunctionTypes..."
        # Similar pattern...
        ;;
        
    4)
        echo ""
        echo "🔧 Phase 4: Enabling full strict mode..."
        echo "⚠️  This is a big step! Make sure all previous phases are complete."
        read -p "Are you sure? (y/n): " CONFIRM
        if [ "$CONFIRM" != "y" ]; then
            exit 0
        fi
        
        # Update to full strict
        node -e "
        const fs = require('fs');
        const config = JSON.parse(fs.readFileSync('tsconfig.json', 'utf8'));
        config.compilerOptions.strict = true;
        // Remove individual flags as strict includes them all
        delete config.compilerOptions.noImplicitAny;
        delete config.compilerOptions.strictNullChecks;
        delete config.compilerOptions.strictFunctionTypes;
        fs.writeFileSync('tsconfig.json', JSON.stringify(config, null, 2));
        "
        
        ERRORS=$(count_errors)
        echo "  Total errors with full strict: $ERRORS"
        
        if test_build && [ "$ERRORS" -eq "0" ]; then
            echo "🎉 CONGRATULATIONS! Full strict mode enabled with zero errors!"
        else
            echo "❌ Not ready for full strict mode yet"
            cp tsconfig.json.backup tsconfig.json
        fi
        ;;
        
    5)
        echo ""
        echo "📊 Current TypeScript Status:"
        echo ""
        echo "Configuration:"
        grep -E '"strict"|"noImplicitAny"|"strictNullChecks"' tsconfig.json | sed 's/^/  /'
        echo ""
        echo "Error count: $(count_errors)"
        echo ""
        
        # Detailed error breakdown
        echo "Error types:"
        npx tsc --noEmit 2>&1 | grep "error TS" | sed 's/.*error TS/TS/' | cut -d: -f1 | sort | uniq -c | sort -nr | head -10
        ;;
        
    6)
        echo ""
        echo "🔄 Rolling back to backup..."
        cp tsconfig.json.backup tsconfig.json
        echo "✅ Restored tsconfig.json from backup"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "💡 Tips for fixing TypeScript errors safely:"
echo "1. Add type annotations without changing logic"
echo "2. Use 'as any' temporarily for complex cases"
echo "3. Fix one file at a time"
echo "4. Run tests after each fix"
echo "5. Commit working code frequently"

cd ..