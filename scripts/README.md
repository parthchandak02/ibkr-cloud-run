# 🚀 Deployment Scripts

This directory contains deployment automation scripts following CI/CD best practices.

## 📋 Available Scripts

### 🎯 `deploy-all.sh` (Recommended)
**Unified deployment script that handles everything in the correct order:**

```bash
./scripts/deploy-all.sh
```

**What it does:**
1. ✅ **Git Status Check** - Commits any uncommitted changes
2. ✅ **Apps Script Deployment** - Uses `clasp push` to update Google Apps Script
3. ✅ **Git Push** - Triggers automatic Cloud Run deployment via GitHub
4. ✅ **Health Check** - Verifies all services are working
5. ✅ **Summary Report** - Shows URLs and next steps

### 🔧 Individual Scripts

#### `deploy.sh`
Deploys only to Google Cloud Run directly (bypasses GitHub automation):
```bash
./scripts/deploy.sh
```

#### `deploy-apps-script.sh`
Deploys only Google Apps Script:
```bash
./scripts/deploy-apps-script.sh
```

## 🔄 CI/CD Flow

```
Local Changes → Git Commit → Apps Script (clasp) → Git Push → Cloud Run (auto)
```

### **Best Practice Order:**
1. **Apps Script First** - Update triggers and calendar integration
2. **Git Push Second** - Triggers Cloud Run deployment automatically
3. **Verification** - Test all components work together

## 🛡️ Security Features

- ✅ **Pre-flight checks** - Validates authentication and environment
- ✅ **Uncommitted changes detection** - Prevents accidental deployments
- ✅ **Service URL auto-update** - Keeps Apps Script in sync with Cloud Run
- ✅ **Health verification** - Confirms deployments are working

## 📊 Monitoring

After deployment, monitor:
- **Cloud Run Logs**: `gcloud run services logs tail ibkr-trading-bot --region=us-central1`
- **Apps Script**: https://script.google.com/home (Executions tab)
- **GitHub Actions**: Repository → Actions tab

## 🎯 Quick Start

For first-time setup:
```bash
# 1. Ensure you're authenticated
gcloud auth login
clasp login

# 2. Run unified deployment
./scripts/deploy-all.sh

# 3. Test the system
# - Create calendar event: "TEST BUY 1 BYD"
# - Check Discord for notifications
# - Verify calendar event shows execution status
```

## 🔍 Troubleshooting

### Common Issues:

**"clasp not found"**
```bash
npm install -g @google/clasp
```

**"Not authenticated with Google Cloud"**
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**"Apps Script API not enabled"**
- Visit: https://script.google.com/home/usersettings
- Enable Google Apps Script API

### Verification Commands:
```bash
# Check Apps Script deployment
clasp open

# Check Cloud Run status
gcloud run services describe ibkr-trading-bot --region=us-central1

# Test service health
curl https://your-service-url.run.app/health
```

## 📚 Best Practices Implemented

Based on research and industry standards:

1. **Atomic Deployments** - All-or-nothing approach
2. **Pre-flight Validation** - Check prerequisites before deployment
3. **Automated Service Discovery** - Auto-update URLs between services
4. **Health Verification** - Confirm deployments are working
5. **Clear Logging** - Colored output with status indicators
6. **Error Handling** - Exit on any failure with clear messages
7. **Documentation** - Self-documenting with help text

This follows Google Cloud and Apps Script deployment best practices for 2025! 🎯
