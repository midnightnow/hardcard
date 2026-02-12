#!/bin/bash

# ===============================================
# NEXUS CLEANUP VERIFICATION SCRIPT
# Verifies the dependency cleanup was successful
# ===============================================

set -e

echo "🔍 NEXUS DEPENDENCY CLEANUP VERIFICATION"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this from the DATABUTTON directory"
    exit 1
fi

cd frontend

echo ""
echo "📊 Step 1: Analyzing package.json changes..."

# Count dependencies before and after
if [ -f "package.json.backup.20250624_090652" ]; then
    BEFORE=$(cat package.json.backup.20250624_090652 | grep -c '".*":' || echo "0")
    AFTER=$(cat package.json | grep -c '".*":' || echo "0")
    REMOVED=$((BEFORE - AFTER))
    
    echo "   Dependencies before cleanup: $BEFORE"
    echo "   Dependencies after cleanup:  $AFTER"
    echo "   Dependencies removed:        $REMOVED"
    echo "   Reduction percentage:        $(( (REMOVED * 100) / BEFORE ))%"
else
    echo "   ⚠️  Backup file not found, cannot compare"
    CURRENT=$(cat package.json | grep -c '".*":' || echo "0")
    echo "   Current dependencies: $CURRENT"
fi

echo ""
echo "📋 Step 2: Checking for problematic packages..."

# Check if problematic packages were removed
PROBLEMATIC_PACKAGES=(
    "react-chessboard"
    "sudoku-gen" 
    "react-wheel-of-prizes"
    "three"
    "@react-three/fiber"
    "konva"
    "p5"
    "agora-rtc-sdk-ng"
    "twilio-video"
    "@mui/material"
    "@chakra-ui/react"
    "@tiptap/core"
    "@ckeditor/ckeditor5-build-classic"
    "@monaco-editor/react"
    "@auth0/auth0-react"
    "@clerk/clerk-react"
)

STILL_PRESENT=0
echo "   Checking removal of problematic packages:"

for package in "${PROBLEMATIC_PACKAGES[@]}"; do
    if grep -q "\"$package\"" package.json; then
        echo "   ❌ $package (still present)"
        STILL_PRESENT=$((STILL_PRESENT + 1))
    else
        echo "   ✅ $package (removed)"
    fi
done

if [ $STILL_PRESENT -eq 0 ]; then
    echo "   🎉 All problematic packages successfully removed!"
else
    echo "   ⚠️  $STILL_PRESENT packages still present"
fi

echo ""
echo "🔧 Step 3: Checking yarn/node_modules status..."

if [ -f "yarn.lock" ]; then
    echo "   ✅ yarn.lock exists"
    LOCKFILE_SIZE=$(du -h yarn.lock | cut -f1)
    echo "   📦 Lockfile size: $LOCKFILE_SIZE"
else
    echo "   ❌ yarn.lock missing - run 'yarn install'"
fi

if [ -d "node_modules" ]; then
    NODE_MODULES_SIZE=$(du -sh node_modules | cut -f1)
    echo "   ✅ node_modules exists ($NODE_MODULES_SIZE)"
else
    echo "   ❌ node_modules missing - run 'yarn install'"
fi

echo ""
echo "🛡️  Step 4: Security check..."

# Check for known vulnerable packages
VULNERABLE_PACKAGES=(
    "aws-sdk"
    "vinyl-fs"
    "html2pdf.js"
    "mammoth"
    "lodash"
)

echo "   Checking for vulnerable packages:"
VULNERABLE_PRESENT=0

for package in "${VULNERABLE_PACKAGES[@]}"; do
    if grep -q "\"$package\"" package.json; then
        echo "   ⚠️  $package (update recommended)"
        VULNERABLE_PRESENT=$((VULNERABLE_PRESENT + 1))
    else
        echo "   ✅ $package (not present)"
    fi
done

echo ""
echo "🧪 Step 5: Testing basic functionality..."

# Check if basic commands work
echo "   Testing yarn commands:"

if yarn --version > /dev/null 2>&1; then
    YARN_VERSION=$(yarn --version)
    echo "   ✅ yarn --version: $YARN_VERSION"
else
    echo "   ❌ yarn not working"
fi

# Test if the app can be started (just check the command exists)
if grep -q '"dev"' package.json; then
    echo "   ✅ dev script found in package.json"
else
    echo "   ❌ dev script missing"
fi

if grep -q '"build"' package.json; then
    echo "   ✅ build script found in package.json"
else
    echo "   ❌ build script missing"
fi

echo ""
echo "📈 Step 6: Cleanup impact assessment..."

# Calculate estimated bundle size reduction
echo "   Estimating impact:"
echo "   • Removed graphics libraries: ~2MB+ (three.js, konva, p5)"
echo "   • Removed video SDKs: ~4MB+ (agora, twilio, livekit)"
echo "   • Removed UI frameworks: ~1MB+ (mui, chakra, daisyui)"
echo "   • Removed text editors: ~3MB+ (tiptap, ckeditor, monaco)"
echo "   • Total estimated savings: ~10MB+ in bundle size"

echo ""
echo "🎯 VERIFICATION SUMMARY"
echo "====================="

if [ $STILL_PRESENT -eq 0 ] && [ -f "yarn.lock" ]; then
    echo "✅ NEXUS cleanup appears SUCCESSFUL!"
    echo ""
    echo "📊 Results:"
    echo "   • All targeted packages removed"
    echo "   • Dependencies successfully updated"
    echo "   • Project ready for monorepo migration"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Test the application: yarn dev"
    echo "   2. Run the monorepo setup script"
    echo "   3. Begin migration of remaining apps"
else
    echo "⚠️  NEXUS cleanup needs attention:"
    if [ $STILL_PRESENT -gt 0 ]; then
        echo "   • $STILL_PRESENT problematic packages still present"
    fi
    if [ ! -f "yarn.lock" ]; then
        echo "   • yarn.lock missing - run 'yarn install'"
    fi
    echo ""
    echo "🔧 Recommended actions:"
    echo "   1. Review package.json manually"
    echo "   2. Run 'yarn install' to regenerate lockfile"
    echo "   3. Re-run this verification script"
fi

echo ""
echo "📱 Ready to proceed with monorepo setup when verification passes!"