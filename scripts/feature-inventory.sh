#!/bin/bash
# Feature Inventory & Health Check Script
# Ensures all critical features are working before/after changes

set -e
echo "🔍 HardCard Feature Inventory & Health Check"
echo "============================================"
echo "Date: $(date)"
echo ""

# Create reports directory
mkdir -p reports/feature-checks

# Output file
REPORT="reports/feature-checks/inventory-$(date +%Y%m%d-%H%M%S).md"

# Start report
cat > "$REPORT" << 'EOF'
# HardCard Feature Inventory Report

## 🔴 CRITICAL REVENUE FEATURES (Must NEVER break)

### E-Commerce Core
- [ ] Product catalog loads and displays all products
- [ ] Product detail pages show correct information
- [ ] Add to cart functionality works
- [ ] Cart updates correctly (add/remove/quantity)
- [ ] Checkout flow completes successfully
- [ ] Payment processing accepts test cards
- [ ] Order confirmation emails sent
- [ ] Order history displays correctly

### User Management
- [ ] User registration with email
- [ ] User login/logout
- [ ] Password reset functionality
- [ ] User profile updates
- [ ] Address management
- [ ] Payment method storage

### Inventory Management
- [ ] Stock levels display correctly
- [ ] Low stock alerts trigger
- [ ] Out of stock products marked
- [ ] Inventory updates on purchase
- [ ] Reorder suggestions work

## 🟡 IMPORTANT FEATURES (Can have brief downtime)

### Analytics & Reporting
- [ ] Sales dashboard loads
- [ ] Revenue metrics accurate
- [ ] Customer analytics work
- [ ] Inventory reports generate

### Marketing Features
- [ ] Email campaigns functional
- [ ] Loyalty program working
- [ ] Recommendations display
- [ ] SEO metadata present

### Admin Features
- [ ] Admin login works
- [ ] Product management
- [ ] Order management
- [ ] Customer management

## 🟢 ENHANCEMENT FEATURES (Can be temporarily disabled)

### Advanced Features
- [ ] A/B testing framework
- [ ] Advanced analytics
- [ ] Third-party integrations
- [ ] Automation rules

EOF

echo "## 🧪 Automated Checks" >> "$REPORT"
echo "" >> "$REPORT"

# Check if frontend is running
echo -n "Checking frontend server... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|304"; then
    echo "✅ Running"
    echo "- [x] Frontend server responding" >> "$REPORT"
else
    echo "❌ Not responding"
    echo "- [ ] Frontend server responding ⚠️" >> "$REPORT"
fi

# Check if backend API is running
echo -n "Checking backend API... "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health | grep -q "200"; then
    echo "✅ Running"
    echo "- [x] Backend API responding" >> "$REPORT"
else
    echo "❌ Not responding"
    echo "- [ ] Backend API responding ⚠️" >> "$REPORT"
fi

# Check critical API endpoints
echo ""
echo "Checking critical endpoints..."
ENDPOINTS=(
    "http://localhost:8000/api/products"
    "http://localhost:8000/api/cart"
    "http://localhost:8000/api/auth/login"
    "http://localhost:8000/api/orders"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "  $endpoint ... "
    if curl -s -o /dev/null -w "%{http_code}" "$endpoint" | grep -q "200\|401\|404"; then
        echo "✅"
        echo "- [x] $endpoint" >> "$REPORT"
    else
        echo "❌"
        echo "- [ ] $endpoint ⚠️" >> "$REPORT"
    fi
done

# Check build status
echo ""
echo "Checking build status..."
cd frontend
if npm run build > /dev/null 2>&1; then
    echo "✅ Build successful"
    echo "- [x] Frontend builds without errors" >> "$REPORT"
    
    # Check bundle size
    BUNDLE_SIZE=$(find dist -name "*.js" -exec du -ch {} + | grep total | awk '{print $1}')
    echo "  Bundle size: $BUNDLE_SIZE"
    echo "- [x] Bundle size: $BUNDLE_SIZE" >> "$REPORT"
else
    echo "❌ Build failed"
    echo "- [ ] Frontend builds without errors ⚠️" >> "$REPORT"
fi
cd ..

# Check for TypeScript errors (non-blocking)
echo ""
echo "Checking TypeScript (informational)..."
cd frontend
TS_ERRORS=$(npx tsc --noEmit 2>&1 | grep -c "error TS" || true)
echo "  Found $TS_ERRORS TypeScript errors (currently non-blocking)"
echo "- [ ] TypeScript errors: $TS_ERRORS (non-blocking)" >> "$REPORT"
cd ..

# Summary
echo ""
echo "============================================"
echo "📋 Report saved to: $REPORT"
echo ""
echo "⚠️  CRITICAL: Review all ❌ items before proceeding with any changes!"
echo "⚠️  Create E2E tests for any unchecked features before modifying code!"
echo ""

# Create a symlink to latest report
ln -sf "$(basename "$REPORT")" reports/feature-checks/latest.md

# Exit with error if any critical features are broken
if grep -q "⚠️" "$REPORT"; then
    echo "🚨 WARNING: Some features may not be working correctly!"
    echo "🚨 DO NOT proceed with repairs until all critical features are verified!"
    exit 1
else
    echo "✅ All automated checks passed!"
fi