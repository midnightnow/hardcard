# DNS Configuration for HardCard Production Separation

## Current Status
✅ **hardcard.web.app** is now live with HardCard OS
⚠️ **hardcard.ai** needs to be reconfigured to point to hardcard.web.app

## Required DNS Changes in Cloudflare

### Step 1: Remove Old Configuration
1. Log into Cloudflare Dashboard
2. Select the hardcard.ai domain
3. Go to DNS settings
4. **DELETE** any TXT records with name `_acme-challenge` or containing `hosting-site`
5. **DELETE** any A records pointing to Firebase IPs (199.36.158.100)

### Step 2: Add New CNAME Configuration
Add the following DNS record:
```
Type: CNAME
Name: @ (or hardcard.ai)
Target: hardcard.web.app
Proxy: OFF (DNS only)
TTL: Auto
```

For www subdomain:
```
Type: CNAME
Name: www
Target: hardcard.web.app
Proxy: OFF (DNS only)
TTL: Auto
```

### Step 3: Configure in Firebase Console

1. Go to Firebase Console: https://console.firebase.google.com/project/hardcard/hosting/sites
2. Click on the `hardcard` site
3. Click "Add custom domain"
4. Enter `hardcard.ai`
5. Follow the verification steps (should auto-verify with CNAME)
6. Wait for SSL certificate provisioning (5-10 minutes)

### Step 4: Remove hardcard.ai from Studio Project

**CRITICAL**: This must be done AFTER adding to the hardcard project

1. Go to Firebase Console: https://console.firebase.google.com/project/hardcard-firebase-studio/hosting
2. Find the site that has `hardcard.ai` configured
3. Click on the site → Custom domains
4. Click the three dots next to `hardcard.ai`
5. Select "Delete domain"
6. Confirm deletion

## Verification Steps

After configuration:
```bash
# Check DNS propagation
dig hardcard.ai CNAME +short
# Should return: hardcard.web.app

# Test the site
curl -I https://hardcard.ai
# Should return 200 OK with HardCard OS content

# Verify site metadata
curl -s https://hardcard.ai | grep x-site-id
# Should show: content="hardcard-os"
```

## Architecture Benefits

### Clean Separation Achieved:
- **hardcard.web.app** → Core HardCard OS (Production)
- **vetsorcery.web.app** → VetSorcery Platform
- **alexandria-research.web.app** → Alexandria Research
- **macagent-pro.web.app** → MacAgent Pro
- **hardcard-firebase-studio** → Sandbox/experiments only

### Security Improvements:
- Production isolated from experimental code
- Clear deployment boundaries
- No cross-contamination risk
- Separate IAM permissions per project

## Rollback Plan

If issues occur:
1. Revert DNS to previous configuration
2. Re-add hardcard.ai to studio project temporarily
3. Debug and fix issues
4. Retry migration

## Support Contacts

- Firebase Hosting Support: https://firebase.google.com/support
- Cloudflare Support: https://support.cloudflare.com
- DNS Propagation Check: https://dnschecker.org

---

**Next Steps:**
1. Complete DNS configuration in Cloudflare
2. Add custom domain in Firebase Console
3. Remove from studio project
4. Set up monitoring and alerts
5. Create deploy guards for production