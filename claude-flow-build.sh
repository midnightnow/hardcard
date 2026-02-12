#!/bin/bash
echo "🚀 Claude Flow: Optimized HardCard Build Process"

cd /Users/studio/hardcard/frontend

# Strategy 1: Use yarn instead of npm for faster installs
if command -v yarn &> /dev/null; then
    echo "📦 Using Yarn for faster dependency resolution..."
    yarn install --ignore-engines
    yarn build
else
    # Strategy 2: npm with optimizations
    echo "📦 Using npm with optimizations..."
    npm ci --legacy-peer-deps --no-audit --no-fund --timeout=600000
    npm run build
fi

# Strategy 3: Verify build output
if [ -d "dist" ]; then
    echo "✅ Build successful - dist folder created"
    ls -la dist/
    echo "📊 Build size analysis:"
    du -sh dist/
    echo "📁 Main files:"
    find dist -name "*.js" -o -name "*.css" -o -name "*.html" | head -10
else
    echo "❌ Build failed - no dist folder"
    echo "🔍 Checking for errors..."
    npm run build 2>&1 | tail -20
    exit 1
fi

echo "🎯 Build process complete - ready for deployment"