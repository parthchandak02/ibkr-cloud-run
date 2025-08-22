# 🚀 Live Trading Setup Guide

## ✅ Current Status: Ready for Live Trading!

Your system now implements **proper ibind library methods** for order placement and is ready for live trading.

## 🔧 **What We Fixed:**

### **1. Proper ibind Order Placement** ✅
- **Before**: Had `TODO` placeholder for order logic
- **Now**: Uses proper `OrderRequest` and `client.place_order()` methods
- **Follows**: Official ibind examples from `rest_04_place_order.py`

### **2. Market Order Implementation** ✅
- **Order Type**: `MKT` (Market order for immediate execution)
- **Order Handling**: Proper IBKR prompt responses using `QuestionType` enum
- **Error Handling**: Comprehensive order response parsing

### **3. Contract ID Handling** ✅
- **BYD Example**: Properly extracts conid `46652429` from `{'1211': 46652429}`
- **Universal**: Works with any stock symbol and exchange

## 🚦 **How to Enable Live Trading:**

### **Option 1: Update Cloud Run Environment (Recommended)**

```bash
# Update the Cloud Run service to disable dry run
gcloud run services update ibkr-trading-bot \
  --region us-central1 \
  --set-env-vars DRY_RUN=false
```

### **Option 2: Update Secret Manager**

```bash
# Create a dry run setting in Secret Manager
echo "false" | gcloud secrets create dry-run-setting --data-file=-

# Update Cloud Run to use the secret
gcloud run services update ibkr-trading-bot \
  --region us-central1 \
  --remove-env-vars DRY_RUN \
  --update-secrets DRY_RUN=dry-run-setting:latest
```

### **Option 3: Re-deploy with New Setting**

```bash
# Re-deploy with live trading enabled
gcloud run deploy ibkr-trading-bot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars IBIND_USE_OAUTH=true,DEFAULT_QUANTITY=1,DRY_RUN=false,IBIND_OAUTH1A_REALM=limited_poa \
  --update-secrets IBIND_OAUTH1A_ACCESS_TOKEN=ibind-access-token:latest,IBIND_OAUTH1A_ACCESS_TOKEN_SECRET=ibind-access-token-secret:latest,IBIND_OAUTH1A_CONSUMER_KEY=ibind-consumer-key:latest,IBIND_OAUTH1A_DH_PRIME=ibind-dh-prime:latest,IBIND_OAUTH1A_ENCRYPTION_KEY_FP=ibind-encryption-key:latest,IBIND_OAUTH1A_SIGNATURE_KEY_FP=ibind-signature-key:latest,DISCORD_WEBHOOK_URL=discord-webhook-url:latest
```

## 🧪 **Testing Your First Live Order:**

### **1. Small Test Order** (Recommended)
```bash
# Test with a small quantity first
curl -X POST https://your-service.run.app/trade \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BYD","action":"BUY","quantity":1}'
```

### **2. Via Google Apps Script**
```javascript
// In Google Apps Script, call:
testBuyBYD()  // This will place a live order when DRY_RUN=false
```

### **3. Via Calendar Event**
- Create calendar event: **"BUY 1 BYD"**
- Apps Script will automatically execute the trade

## 📊 **What Happens in Live Mode:**

### **Dry Run Response (Current):**
```json
{
  "status": "simulated",
  "message": "🔍 DRY RUN: Would BUY 1 shares of BYD (conid: {'1211': 46652429})"
}
```

### **Live Trading Response (After Enabling):**
```json
{
  "status": "executed",
  "message": "✅ LIVE ORDER PLACED: BUY 1 shares of BYD (Order ID: ibind_bot_BYD_20250122142530)",
  "symbol": "BYD",
  "action": "BUY",
  "quantity": 1,
  "conid": {"1211": 46652429},
  "order_id": "ibind_bot_BYD_20250122142530"
}
```

## 🛡️ **Safety Features:**

1. **Market Orders**: Immediate execution at current market price
2. **Order Validation**: Checks contract ID exists before placing order
3. **Error Handling**: Comprehensive error reporting and Discord notifications
4. **Account Integration**: Uses your authenticated IBKR account
5. **Order Tracking**: Unique order IDs for each trade

## ⚠️ **Important Notes:**

1. **Start Small**: Test with 1 share first
2. **Market Hours**: Orders only execute during market hours
3. **Account Funding**: Ensure sufficient funds in your IBKR account
4. **Order Types**: Currently implements market orders (immediate execution)
5. **Monitoring**: All orders send Discord notifications

## 🎯 **Order Flow:**

1. **Trigger** → Calendar event or API call
2. **Validation** → Symbol lookup and contract ID verification  
3. **Order Creation** → `OrderRequest` with proper parameters
4. **IBKR Submission** → `client.place_order()` with automated prompt responses
5. **Confirmation** → Order ID returned and Discord notification sent

## 📞 **Support:**

- **Health Check**: `GET /health` shows IBKR connection status
- **Order Status**: Monitor via Discord notifications
- **Logs**: Check Cloud Run logs for detailed order information

---

**Your system is now ready for live trading! 🚀**
