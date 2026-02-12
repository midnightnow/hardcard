#!/bin/bash
echo "🔧 Claude Flow: Fix hardcard.ai Redirect Issue"
echo "=============================================="

# Step 1: Diagnose the current issue
echo "🔍 Diagnosing hardcard.ai redirect issue..."
echo ""
echo "Current DNS configuration:"
dig hardcard.ai +short
echo ""
echo "Current hosting provider headers:"
curl -I https://hardcard.ai | grep -E "(server|x-served-by|cache-control)"
echo ""

# Step 2: Check Firebase hosting status
echo "📊 Firebase hosting status:"
firebase hosting:sites:list --project hardcard
echo ""

# Step 3: Firebase custom domain configuration
echo "🌐 Step 1: Configure hardcard.ai as custom domain in Firebase"
echo "Visit: https://console.firebase.google.com/project/hardcard/hosting"
echo "1. Click 'Add custom domain'"
echo "2. Enter: hardcard.ai"
echo "3. Choose 'Redirect to existing website: hardcard.web.app' OR 'Same content'"
echo ""

# Step 4: DNS Update Instructions
echo "📝 Step 2: Update DNS records for hardcard.ai"
echo "Current (WRONG):"
echo "  A    hardcard.ai    199.36.158.100  # This serves VetSorcery redirect"
echo ""
echo "New (CORRECT) - Choose ONE option:"
echo ""
echo "Option A - Firebase A records:"
echo "  A    hardcard.ai    151.101.1.195"
echo "  A    hardcard.ai    151.101.65.195"
echo ""
echo "Option B - CNAME to Firebase (recommended):"
echo "  CNAME hardcard.ai   hardcard.web.app"
echo ""

# Step 5: Create verification script
cat > verify-hardcard-ai-fix.sh << 'EOF'
#!/bin/bash
echo "🔍 Verifying hardcard.ai fix..."

# Check DNS
NEW_IP=$(dig hardcard.ai +short | head -1)
echo "Current IP: $NEW_IP"

# Check if it points to Firebase
if [[ "$NEW_IP" == "151.101.1.195" || "$NEW_IP" == "151.101.65.195" ]]; then
    echo "✅ DNS correctly points to Firebase"
else
    echo "⏳ DNS still pointing to old server: $NEW_IP"
    echo "Expected: 151.101.1.195 or 151.101.65.195"
fi

# Test the redirect
echo ""
echo "Testing hardcard.ai response..."
RESPONSE=$(curl -s https://hardcard.ai | head -5)
if [[ "$RESPONSE" == *"HardCard"* ]]; then
    echo "✅ hardcard.ai now serves HardCard platform!"
elif [[ "$RESPONSE" == *"vetsorcery"* ]]; then
    echo "❌ Still redirecting to VetSorcery"
else
    echo "⏳ Unknown response - DNS may still be propagating"
fi

echo ""
echo "Full response check:"
curl -I https://hardcard.ai
EOF

chmod +x verify-hardcard-ai-fix.sh

# Step 6: Alternative solution - Firebase redirect rule
echo "🔄 Step 3: Alternative - Create Firebase redirect rule"
echo "If you can't change DNS immediately, add this to firebase.json:"
cat << 'REDIRECT_EOF'
{
  "hosting": {
    "public": "frontend/dist",
    "redirects": [
      {
        "source": "/vetsorcery-hyperlinked-complete-v3.html",
        "destination": "/",
        "type": 301
      }
    ]
  }
}
REDIRECT_EOF

echo ""
echo "🎯 Summary of the problem:"
echo "❌ hardcard.ai DNS points to 199.36.158.100 (wrong server)"
echo "❌ That server redirects to VetSorcery content"
echo "✅ hardcard.web.app works correctly with HardCard platform"
echo ""
echo "🔧 Solution:"
echo "1. Configure hardcard.ai as custom domain in Firebase Console"
echo "2. Update DNS to point to Firebase hosting IPs"
echo "3. Wait for propagation (5-30 minutes)"
echo "4. Run ./verify-hardcard-ai-fix.sh to confirm"
echo ""
echo "📞 Need help? The issue is DNS configuration, not the HardCard platform itself."