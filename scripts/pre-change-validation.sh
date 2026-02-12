#!/bin/bash
# Pre-Change Validation Script
# Run this BEFORE making any code changes to establish baseline

set -e
echo "🛡️ HardCard Pre-Change Validation"
echo "================================="
echo "This script creates a baseline of current functionality"
echo ""

# Create validation directory
VALIDATION_DIR="reports/validation/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$VALIDATION_DIR"

echo "📸 Creating functionality baseline in: $VALIDATION_DIR"
echo ""

# 1. Capture current git state
echo "1. Capturing git state..."
git status > "$VALIDATION_DIR/git-status.txt"
git log --oneline -10 > "$VALIDATION_DIR/git-history.txt"
git diff > "$VALIDATION_DIR/uncommitted-changes.diff"
echo "✅ Git state captured"

# 2. Run feature inventory
echo ""
echo "2. Running feature inventory..."
./scripts/feature-inventory.sh
cp reports/feature-checks/latest.md "$VALIDATION_DIR/feature-inventory.md"
echo "✅ Feature inventory captured"

# 3. Capture current TypeScript errors (baseline)
echo ""
echo "3. Capturing TypeScript baseline..."
cd frontend
npx tsc --noEmit > "$VALIDATION_DIR/typescript-errors-baseline.txt" 2>&1 || true
TS_COUNT=$(grep -c "error TS" "$VALIDATION_DIR/typescript-errors-baseline.txt" || echo "0")
echo "✅ Current TypeScript errors: $TS_COUNT (baseline)"
cd ..

# 4. Run tests and capture results
echo ""
echo "4. Running existing tests..."
cd frontend
if npm test -- --passWithNoTests > "$VALIDATION_DIR/test-results.txt" 2>&1; then
    echo "✅ Tests passed (or no tests found)"
else
    echo "⚠️  Some tests failed (captured in report)"
fi
cd ..

# 5. Check bundle size
echo ""
echo "5. Checking bundle size..."
cd frontend
if npm run build > "$VALIDATION_DIR/build-log.txt" 2>&1; then
    echo "✅ Build successful"
    find dist -name "*.js" -exec du -h {} \; > "$VALIDATION_DIR/bundle-sizes.txt"
    TOTAL_SIZE=$(du -sh dist | awk '{print $1}')
    echo "   Total bundle size: $TOTAL_SIZE"
else
    echo "❌ Build failed - see build-log.txt"
fi
cd ..

# 6. Create E2E test template
echo ""
echo "6. Creating E2E test templates..."
cat > "$VALIDATION_DIR/critical-paths-template.spec.ts" << 'EOF'
import { test, expect } from '@playwright/test';

test.describe('Critical E-Commerce Paths - DO NOT BREAK', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('Homepage loads', async ({ page }) => {
    await expect(page).toHaveTitle(/HardCard|Hempex/);
    await expect(page.locator('nav')).toBeVisible();
  });

  test('Product catalog displays', async ({ page }) => {
    await page.goto('/products');
    await expect(page.locator('[data-testid="product-card"]').first()).toBeVisible();
  });

  test('Add to cart flow', async ({ page }) => {
    await page.goto('/products');
    await page.locator('[data-testid="add-to-cart"]').first().click();
    // Verify cart updated
    await expect(page.locator('[data-testid="cart-count"]')).not.toHaveText('0');
  });

  test('Checkout flow (smoke test)', async ({ page }) => {
    // Add item to cart first
    await page.goto('/products');
    await page.locator('[data-testid="add-to-cart"]').first().click();
    
    // Go to checkout
    await page.goto('/checkout');
    await expect(page.locator('h1')).toContainText(/Checkout|Payment/);
  });

  test('User login', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });
});

test.describe('Admin Features - Can have brief downtime', () => {
  test('Admin dashboard accessible', async ({ page }) => {
    await page.goto('/admin');
    // Should redirect to login or show dashboard
    await expect(page).toHaveURL(/admin|login/);
  });
});
EOF
echo "✅ E2E test template created"

# 7. Create validation summary
echo ""
echo "7. Creating validation summary..."
cat > "$VALIDATION_DIR/VALIDATION_SUMMARY.md" << EOF
# Pre-Change Validation Summary
Date: $(date)

## Current State
- TypeScript Errors: $TS_COUNT
- Bundle Size: $TOTAL_SIZE
- Git Branch: $(git rev-parse --abbrev-ref HEAD)
- Last Commit: $(git log --oneline -1)

## Critical Features Status
See feature-inventory.md for detailed status

## Next Steps
1. Review all files in this directory
2. Fix any ❌ items in feature-inventory.md
3. Run E2E tests based on template
4. Create git branch for changes
5. Make INCREMENTAL changes only

## Rollback Point
- Git Commit: $(git rev-parse HEAD)
- Validation Dir: $VALIDATION_DIR

## Safety Checklist Before Changes
- [ ] All critical features working
- [ ] Baseline captured
- [ ] Rollback plan ready
- [ ] Staging environment prepared
- [ ] Team notified
EOF

# 8. Create quick rollback script
cat > "$VALIDATION_DIR/emergency-rollback.sh" << EOF
#!/bin/bash
# Emergency Rollback Script
echo "🚨 EMERGENCY ROLLBACK INITIATED"
git checkout $(git rev-parse HEAD)
cd frontend && npm install && npm run build
echo "✅ Rolled back to commit: $(git rev-parse HEAD)"
echo "⚠️  Restart services and verify functionality!"
EOF
chmod +x "$VALIDATION_DIR/emergency-rollback.sh"

# Final summary
echo ""
echo "================================="
echo "✅ Pre-Change Validation Complete!"
echo ""
echo "📁 Validation saved to: $VALIDATION_DIR"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "1. Review $VALIDATION_DIR/VALIDATION_SUMMARY.md"
echo "2. Fix any broken features BEFORE making changes"
echo "3. Keep $VALIDATION_DIR as your rollback reference"
echo ""
echo "🛡️ Safety Command:"
echo "   cp -r $VALIDATION_DIR reports/validation/GOLDEN_BASELINE"
echo ""

# Create symlink to latest validation
ln -sf "$(basename "$VALIDATION_DIR")" reports/validation/latest

# Exit with warning if any issues found
if [ "$TS_COUNT" -gt "200" ]; then
    echo "⚠️  WARNING: High number of TypeScript errors. Consider addressing critical ones first."
fi

if grep -q "❌\|⚠️" "$VALIDATION_DIR/feature-inventory.md"; then
    echo "🚨 CRITICAL: Some features are not working! Fix these BEFORE proceeding!"
    exit 1
fi