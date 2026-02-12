#!/bin/bash
echo "🌐 Claude Flow: DNS Configuration Guide"

echo "📋 DNS Update Instructions for hardcard.ai"
echo "=========================================="

# Step 1: Get current DNS info
echo "🔍 Current DNS configuration:"
dig hardcard.ai +short

# Step 2: Firebase hosting verification
echo ""
echo "🔧 Firebase hosting setup:"
firebase hosting:sites:list

# Step 3: DNS update commands
echo ""
echo "📝 DNS Records to Update:"
echo "-------------------------"
echo "Remove current A record:"
echo "  A    hardcard.ai    199.36.158.100"
echo ""
echo "Add Firebase hosting records:"
echo "  A    hardcard.ai    151.101.1.195"
echo "  A    hardcard.ai    151.101.65.195"
echo ""
echo "OR use CNAME (recommended):"
echo "  CNAME hardcard.ai   hardcard.web.app"

# Step 4: Firebase custom domain setup
echo ""
echo "🚀 Firebase Console Steps:"
echo "1. Go to: https://console.firebase.google.com/project/hardcard/hosting"
echo "2. Click 'Add custom domain'"
echo "3. Enter: hardcard.ai"
echo "4. Follow DNS verification steps"
echo "5. Wait for SSL certificate provisioning"

# Step 5: Verification commands
echo ""
echo "✅ Verification commands:"
echo "nslookup hardcard.ai"
echo "curl -I https://hardcard.ai"
echo ""

# Step 6: Automated DNS check
cat > check-dns-propagation.sh << 'EOF'
#!/bin/bash
echo "🔍 Checking DNS propagation for hardcard.ai..."

FIREBASE_IPS=("151.101.1.195" "151.101.65.195")
CURRENT_IP=$(dig hardcard.ai +short | head -1)

echo "Current IP: $CURRENT_IP"

for ip in "${FIREBASE_IPS[@]}"; do
    if [[ "$CURRENT_IP" == "$ip" ]]; then
        echo "✅ DNS correctly points to Firebase ($ip)"
        exit 0
    fi
done

echo "⏳ DNS not yet propagated to Firebase IPs"
echo "Expected IPs: ${FIREBASE_IPS[*]}"
echo "Run this script again in 5-10 minutes"
EOF

chmod +x check-dns-propagation.sh

echo ""
echo "🎯 DNS configuration guide created!"
echo "📁 Files created:"
echo "   - dns-update-guide.sh (this file)"
echo "   - check-dns-propagation.sh (verification tool)"
echo ""
echo "▶️  Next: Update your DNS records manually, then run:"
echo "   ./check-dns-propagation.sh"