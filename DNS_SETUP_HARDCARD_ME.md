# 🔧 DNS Setup for hardcard.me

## Current Status
- ✅ **Site Deployed**: https://hardcard-me.web.app is LIVE
- ❌ **Domain Not Connected**: hardcard.me needs DNS configuration

## Step-by-Step Setup

### Option 1: If You Own hardcard.me

#### Step 1: Configure DNS at Your Registrar/Cloudflare
```
Type: CNAME
Name: @ (or hardcard.me)
Target: hardcard-me.web.app
Proxy: DNS Only (if using Cloudflare)
TTL: Auto
```

For www subdomain:
```
Type: CNAME
Name: www
Target: hardcard-me.web.app
Proxy: DNS Only
TTL: Auto
```

#### Step 2: Add Custom Domain in Firebase
1. Go to: https://console.firebase.google.com/project/hardcard/hosting/sites
2. Click on `hardcard-me` site
3. Click "Add custom domain"
4. Enter: `hardcard.me`
5. Follow verification steps
6. Wait for SSL certificate (5-10 minutes)

### Option 2: If You DON'T Own hardcard.me Yet

#### Available Alternatives:
1. **Register hardcard.me** (~$15/year)
   - Namecheap: https://www.namecheap.com
   - Cloudflare: https://www.cloudflare.com/products/registrar/
   - Google Domains: https://domains.google

2. **Use Alternative Domains You Own**:
   - hardcard.io
   - hardcard.dev
   - masterenterprise.com
   - [yourname].me

3. **Use the Firebase URL Directly**:
   - Access at: https://hardcard-me.web.app
   - Works immediately, no DNS needed

## 🚀 Quick Access (Works Now!)

While DNS propagates, you can access your MasterEnterprise portal at:

### **https://hardcard-me.web.app**

This URL works immediately! Sign in with dallasm@gmail.com

## 📊 Check Domain Availability

Let me check if hardcard.me is available for registration: