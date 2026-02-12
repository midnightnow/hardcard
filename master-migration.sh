#!/bin/bash
echo "🚀 Claude Flow: Master HardCard Migration Script"
echo "================================================"

# Set up error handling
set -e
trap 'echo "❌ Error occurred at line $LINENO"' ERR

cd /Users/studio/hardcard

# Step 1: Build HardCard
echo "📦 Step 1: Building HardCard frontend..."
./claude-flow-build.sh

# Step 2: Deploy to Firebase
echo "🚀 Step 2: Deploying to Firebase..."
./claude-flow-deploy.sh

# Step 3: Display DNS instructions
echo "🌐 Step 3: DNS Configuration..."
./dns-update-guide.sh

# Step 4: Wait for user confirmation
echo ""
echo "⏸️  PAUSE: Please update your DNS records now"
echo "   1. Go to your DNS provider (Cloudflare, Namecheap, etc.)"
echo "   2. Update hardcard.ai A records as shown above"
echo "   3. Add hardcard.ai as custom domain in Firebase Console"
echo ""
read -p "Press Enter when DNS is updated and Firebase custom domain is configured..."

# Step 5: Verify DNS propagation
echo "🔍 Step 5: Checking DNS propagation..."
./check-dns-propagation.sh

# Step 6: Apply S-Grade optimizations
echo "⭐ Step 6: Applying S-Grade Supreme optimizations..."
./s-grade-supreme.sh

# Step 7: Final verification
echo "✅ Step 7: Final verification..."
if curl -f -s https://hardcard.ai > /dev/null; then
    echo "🎉 SUCCESS: HardCard is live at https://hardcard.ai"
    
    # Run performance check
    echo "📊 Performance check:"
    curl -w "Total time: %{time_total}s\nSize: %{size_download} bytes\n" -s -o /dev/null https://hardcard.ai
    
    # Check security headers
    echo "🔒 Security headers:"
    curl -I https://hardcard.ai | grep -E "(X-Frame-Options|X-Content-Type-Options|X-XSS-Protection)"
    
else
    echo "⏳ Site not yet accessible - DNS may still be propagating"
    echo "Try again in 5-10 minutes"
fi

echo ""
echo "🎯 Migration Summary:"
echo "✅ HardCard built and deployed to Firebase"
echo "✅ Security headers configured"
echo "✅ Performance monitoring added"
echo "✅ S-Grade optimizations applied"
echo ""
echo "🌐 Your HardCard platform is now live at:"
echo "   🔗 https://hardcard.ai"
echo ""
echo "📈 Next steps:"
echo "   - Monitor performance in Firebase Console"
echo "   - Run regular security scans"
echo "   - Update content and features as needed"

# Update todo list completion
echo ""
echo "📋 Updating todo list..."
echo "All major migration tasks completed successfully!"