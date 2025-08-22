# 🚀 Complete Deployment Guide

This guide walks you through deploying the IBKR Calendar Trading Bot from scratch.

## 📋 Prerequisites Checklist

- [ ] Interactive Brokers account with Client Portal API enabled
- [ ] Google Cloud Platform account (free tier works)
- [ ] IBKR OAuth credentials (access token, consumer key, private keys)
- [ ] Discord webhook URL (optional)
- [ ] `gcloud` CLI installed and authenticated
- [ ] `clasp` CLI installed (`npm install -g @google/clasp`)

## 🔐 Step 1: Get IBKR OAuth Credentials

### 1.1 Enable Client Portal API

1. Log into your IBKR account
2. Go to **Account Management** → **Settings** → **API**
3. Enable **Client Portal API**
4. Note your **Consumer Key**

### 1.2 Generate OAuth Credentials

Follow the [IBKR OAuth Setup Guide](https://ibkrcampus.com/ibkr-api-page/cpapi-v1/#oauth-setup):

1. **Generate RSA Key Pair**:
   ```bash
   # Generate private keys
   openssl genrsa -out private_encryption.pem 2048
   openssl genrsa -out private_signature.pem 2048
   
   # Generate public keys
   openssl rsa -in private_encryption.pem -pubout -out public_encryption.pem
   openssl rsa -in private_signature.pem -pubout -out public_signature.pem
   ```

2. **Upload Public Keys** to IBKR Client Portal
3. **Get OAuth Tokens** using IBKR's OAuth flow
4. **Save credentials** securely

You should have:
- ✅ Access Token
- ✅ Access Token Secret
- ✅ Consumer Key  
- ✅ DH Prime
- ✅ `private_encryption.pem`
- ✅ `private_signature.pem`

## ☁️ Step 2: Google Cloud Setup

### 2.1 Create/Select Project

```bash
# Create new project (or use existing)
gcloud projects create your-trading-bot-project
gcloud config set project your-trading-bot-project

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com
```

### 2.2 Store Secrets in Secret Manager

```bash
# IBKR OAuth credentials
echo "YOUR_ACCESS_TOKEN" | gcloud secrets create ibind-access-token --data-file=-
echo "YOUR_ACCESS_TOKEN_SECRET" | gcloud secrets create ibind-access-token-secret --data-file=-
echo "YOUR_CONSUMER_KEY" | gcloud secrets create ibind-consumer-key --data-file=-
echo "YOUR_DH_PRIME" | gcloud secrets create ibind-dh-prime --data-file=-

# PEM files (base64 encoded for cloud storage)
base64 -i private_encryption.pem | gcloud secrets create ibind-encryption-key --data-file=-
base64 -i private_signature.pem | gcloud secrets create ibind-signature-key --data-file=-

# Optional: Discord webhook
echo "YOUR_DISCORD_WEBHOOK_URL" | gcloud secrets create discord-webhook-url --data-file=-
```

### 2.3 Grant Permissions

```bash
# Get your project number
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")

# Grant Cloud Run service account access to secrets
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## 🐳 Step 3: Deploy to Cloud Run

### 3.1 Clone and Configure

```bash
git clone https://github.com/your-username/ibkr-calendar-trading-bot.git
cd ibkr-calendar-trading-bot

# Create local config for development
cp config.env.template config.env
# Edit config.env with your credentials (for local testing only)
```

### 3.2 Deploy Using Script

```bash
# Use our automated deployment script
./scripts/deploy.sh
```

**Or deploy manually:**

```bash
gcloud run deploy ibkr-trading-bot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars IBIND_USE_OAUTH=true,DEFAULT_QUANTITY=1,DRY_RUN=true,IBIND_OAUTH1A_REALM=limited_poa \
  --update-secrets IBIND_OAUTH1A_ACCESS_TOKEN=ibind-access-token:latest \
  --update-secrets IBIND_OAUTH1A_ACCESS_TOKEN_SECRET=ibind-access-token-secret:latest \
  --update-secrets IBIND_OAUTH1A_CONSUMER_KEY=ibind-consumer-key:latest \
  --update-secrets IBIND_OAUTH1A_DH_PRIME=ibind-dh-prime:latest \
  --update-secrets IBIND_OAUTH1A_ENCRYPTION_KEY_FP=ibind-encryption-key:latest \
  --update-secrets IBIND_OAUTH1A_SIGNATURE_KEY_FP=ibind-signature-key:latest \
  --update-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest
```

### 3.3 Test Deployment

```bash
# Get your service URL
SERVICE_URL=$(gcloud run services describe ibkr-trading-bot --region=us-central1 --format="value(status.url)")

# Test health endpoint
curl $SERVICE_URL/health

# Test trade endpoint (dry run)
curl -X POST $SERVICE_URL/trade \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BYD","action":"BUY","quantity":1}'
```

Expected response:
```json
{
  "status": "simulated",
  "message": "🔍 DRY RUN: Would BUY 1 shares of BYD (conid: {'1211': 46652429})"
}
```

## 📱 Step 4: Setup Google Apps Script

### 4.1 Create Apps Script Project

```bash
cd google-apps-script

# Login to Google Apps Script
clasp login

# Create new project
clasp create --title "IBKR Trading Bot" --type standalone

# Push code
clasp push
```

### 4.2 Configure Service URL

1. **Open Apps Script Editor**: `clasp open`
2. **Update SERVICE_URL** in `Code.js`:
   ```javascript
   const CONFIG = {
     SERVICE_URL: 'YOUR_CLOUD_RUN_URL_HERE',
     // ... other config
   };
   ```
3. **Save and push**:
   ```bash
   clasp push
   ```

### 4.3 Setup Calendar Triggers

**Option 1: Automated Setup**
```javascript
// In Apps Script editor, run this function:
installTradingTriggers()
```

**Option 2: Manual Setup**
1. Go to **Triggers** tab in Apps Script
2. **Add Trigger 1**:
   - Function: `onCalendarEventUpdated`
   - Event source: `From calendar`
   - Event type: `Calendar updated`
3. **Add Trigger 2**:
   - Function: `checkUpcomingTradingEvents`
   - Event source: `Time-driven`
   - Type: `Minutes timer`
   - Interval: `Every minute`

### 4.4 Test Apps Script

```javascript
// Test functions in Apps Script editor:
testBuyBYD()           // Test trade execution
testHealthCheck()      // Test service connection
listCurrentTriggers()  // View active triggers
```

## 🧪 Step 5: Test End-to-End System

### 5.1 Test Calendar Integration

1. **Create calendar event**: "BUY 1 BYD"
2. **Check Apps Script logs** for trigger activation
3. **Verify Cloud Run logs** for trade execution
4. **Check Discord/email** for notifications

### 5.2 Test Scheduled Trading

1. **Create calendar event**: "SELL 1 AAPL" scheduled 2 minutes from now
2. **Wait for execution time**
3. **Verify automatic execution**

## 🚀 Step 6: Enable Live Trading (Optional)

⚠️ **Only after thorough testing in dry-run mode!**

```bash
# Enable live trading
gcloud run services update ibkr-trading-bot \
  --region us-central1 \
  --set-env-vars DRY_RUN=false

# Test with small quantity first
curl -X POST $SERVICE_URL/trade \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BYD","action":"BUY","quantity":1}'
```

Expected response:
```json
{
  "status": "executed",
  "message": "✅ LIVE ORDER PLACED: BUY 1 shares of BYD",
  "order_id": "ibind_bot_BYD_20250122142530"
}
```

## 📊 Step 7: Monitoring and Maintenance

### 7.1 View Logs

```bash
# Cloud Run logs
gcloud run services logs read ibkr-trading-bot --region=us-central1 --limit=50

# Follow logs in real-time
gcloud run services logs tail ibkr-trading-bot --region=us-central1
```

### 7.2 Monitor Health

```bash
# Check system health
curl $SERVICE_URL/health | python -m json.tool
```

### 7.3 Update Deployment

```bash
# After making code changes
gcloud run deploy ibkr-trading-bot --source . --region us-central1
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"Permission denied on secrets"** | Run the IAM policy binding command from Step 2.3 |
| **"IBKR status: failed"** | Verify OAuth credentials and IBKR API access |
| **"Discord notifications not working"** | Check webhook URL and Discord server permissions |
| **"Calendar triggers not firing"** | Verify triggers are installed and permissions granted |
| **"Contract not found for symbol"** | Ensure IBKR account has market data for that exchange |

### Debug Commands

```bash
# Test individual components
curl $SERVICE_URL/health                    # Service health
clasp run testHealthCheck                   # Apps Script connectivity
clasp run listCurrentTriggers              # View triggers

# Check secret access
gcloud secrets versions access latest --secret="ibind-access-token"
```

## 🔒 Security Best Practices

1. **Never commit secrets** to version control
2. **Use Secret Manager** for all credentials
3. **Enable audit logging** in Google Cloud
4. **Regularly rotate** OAuth tokens
5. **Monitor access logs** for unusual activity
6. **Start with dry-run mode** for all new deployments

## 📈 Next Steps

- **[📅 Calendar Triggers Guide](CALENDAR_TRIGGERS_GUIDE.md)** - Advanced calendar automation
- **[🚀 Live Trading Setup](LIVE_TRADING_SETUP.md)** - Production trading configuration
- **[🔧 Apps Script Guide](../google-apps-script/README.md)** - Customize Apps Script behavior

---

**🎉 Your IBKR Calendar Trading Bot is now deployed and ready to automate your trades!**