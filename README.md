# 🤖 IBKR Calendar Trading Bot

A production-ready, open-source trading bot for Interactive Brokers that executes trades automatically based on Google Calendar events. Built with the [Voyz ibind](https://github.com/Voyz/ibind) library and deployed on Google Cloud Run.

## 🚀 Features

- **📅 Calendar-Driven Trading** - Create calendar events like "BUY 1 BYD" and trades execute automatically
- **🔐 OAuth 1.0a Authentication** - Secure IBKR API access using proper authentication
- **☁️ Cloud-Native** - Deploys to Google Cloud Run with auto-scaling
- **📱 Smart Notifications** - Discord webhooks and email alerts for all trades
- **🛡️ Safety First** - Dry-run mode for testing, comprehensive error handling
- **⚡ Real-Time** - Dual trigger system (immediate + scheduled execution)
- **🔧 Production Ready** - Proper secret management, monitoring, and logging

## 🏗️ Architecture

```
Google Calendar → Apps Script → Cloud Run → IBKR API → Notifications
     ↓              ↓            ↓          ↓           ↓
"BUY 1 BYD"    → Triggers  → FastAPI → ibind → Discord/Email
```

## 📋 Prerequisites

- **Interactive Brokers Account** with Client Portal API access
- **Google Cloud Platform** account (free tier works)
- **Google Apps Script** access
- **Discord Webhook** (optional, for notifications)

## ⚡ Quick Start

### 1. **Clone & Setup**

```bash
git clone https://github.com/your-username/ibkr-calendar-trading-bot.git
cd ibkr-calendar-trading-bot

# Create your local config
cp config.env.template config.env
# Edit config.env with your credentials (see setup guide below)
```

### 2. **Get IBKR OAuth Credentials**

Follow the [IBKR OAuth Setup Guide](https://ibkrcampus.com/ibkr-api-page/cpapi-v1/#oauth-setup) to get:
- Access Token
- Access Token Secret  
- Consumer Key
- DH Prime
- Private Keys (encryption.pem, signature.pem)

### 3. **Deploy to Google Cloud**

```bash
# Enable required services
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com

# Create secrets (replace with your actual values)
echo "YOUR_ACCESS_TOKEN" | gcloud secrets create ibind-access-token --data-file=-
echo "YOUR_ACCESS_TOKEN_SECRET" | gcloud secrets create ibind-access-token-secret --data-file=-
echo "YOUR_CONSUMER_KEY" | gcloud secrets create ibind-consumer-key --data-file=-
echo "YOUR_DH_PRIME" | gcloud secrets create ibind-dh-prime --data-file=-

# Store PEM files (base64 encoded)
base64 -i private_encryption.pem | gcloud secrets create ibind-encryption-key --data-file=-
base64 -i private_signature.pem | gcloud secrets create ibind-signature-key --data-file=-

# Optional: Discord webhook
echo "YOUR_DISCORD_WEBHOOK_URL" | gcloud secrets create discord-webhook-url --data-file=-

# Deploy using our script
./scripts/deploy.sh
```

### 4. **Setup Google Apps Script**

```bash
# Deploy the Apps Script
cd google-apps-script
npm install -g @google/clasp
clasp login
clasp create --title "IBKR Trading Bot" --type standalone
clasp push

# Set up calendar triggers (run in Apps Script editor)
installTradingTriggers()
```

### 5. **Test the System**

1. **Create a calendar event**: "BUY 1 BYD"
2. **Watch it execute automatically**
3. **Check Discord/email for notifications**

## 📚 Detailed Documentation

- **[📖 Complete Setup Guide](docs/DEPLOYMENT.md)** - Step-by-step deployment
- **[📅 Calendar Triggers Guide](docs/CALENDAR_TRIGGERS_GUIDE.md)** - Calendar automation setup
- **[🚀 Live Trading Setup](docs/LIVE_TRADING_SETUP.md)** - Enable real trading
- **[🔧 Google Apps Script Guide](google-apps-script/README.md)** - Apps Script configuration

## 🎯 Supported Calendar Event Formats

Your system recognizes these calendar event patterns:

```
✅ "BUY 1 BYD"           → Buy 1 share of BYD
✅ "SELL 5 AAPL"         → Sell 5 shares of AAPL  
✅ "Trade: BUY 10 TSLA"  → Buy 10 shares of TSLA
✅ "AAPL BUY 3"          → Buy 3 shares of AAPL
✅ "Just BUY"            → Buy 1 share of default symbol

❌ "Random meeting"      → Ignored (no trading keywords)
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `IBIND_USE_OAUTH` | Enable OAuth authentication | Yes | `true` |
| `IBIND_OAUTH1A_ACCESS_TOKEN` | IBKR access token | Yes | `your_token` |
| `IBIND_OAUTH1A_ACCESS_TOKEN_SECRET` | IBKR access token secret | Yes | `your_secret` |
| `IBIND_OAUTH1A_CONSUMER_KEY` | IBKR consumer key | Yes | `your_key` |
| `IBIND_OAUTH1A_DH_PRIME` | IBKR DH prime | Yes | `your_prime` |
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | No | `https://discord.com/...` |
| `DEFAULT_QUANTITY` | Default trade quantity | No | `1` |
| `DRY_RUN` | Enable dry run mode | No | `true` |

## 🛡️ Security Features

- **🔐 Secret Management** - All credentials stored in Google Secret Manager
- **🚫 No Hardcoded Secrets** - Template-based configuration
- **🛡️ OAuth Authentication** - Secure IBKR API access
- **📝 Audit Logging** - Complete trade and error logging
- **🧪 Dry Run Mode** - Test safely before live trading

## 📊 API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "discord": {"status": "configured"},
    "ibkr": {"status": "initialized", "message": "OAuth client ready"}
  }
}
```

### Execute Trade
```http
POST /trade
Content-Type: application/json

{
  "symbol": "BYD",
  "action": "BUY", 
  "quantity": 1
}
```

**Response (Dry Run):**
```json
{
  "status": "simulated",
  "message": "🔍 DRY RUN: Would BUY 1 shares of BYD (conid: {'1211': 46652429})",
  "symbol": "BYD",
  "action": "BUY",
  "quantity": 1,
  "conid": {"1211": 46652429}
}
```

**Response (Live Trading):**
```json
{
  "status": "executed",
  "message": "✅ LIVE ORDER PLACED: BUY 1 shares of BYD",
  "order_id": "ibind_bot_BYD_20250122142530"
}
```

## 🚀 Going Live

To enable real trading (disable dry run):

```bash
gcloud run services update ibkr-trading-bot \
  --region us-central1 \
  --set-env-vars DRY_RUN=false
```

⚠️ **Start with small quantities and test thoroughly!**

## 🐛 Troubleshooting

### Common Issues

1. **"IBKR status: failed"**
   - Check OAuth credentials in Secret Manager
   - Verify IBKR Client Portal API is enabled
   - Ensure account has market data permissions

2. **"Discord notifications not working"**
   - Verify webhook URL is correct
   - Check Discord server permissions

3. **"Calendar triggers not firing"**
   - Verify triggers are installed in Apps Script
   - Check Apps Script execution permissions
   - Review execution logs in Apps Script

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read ibkr-trading-bot --region=us-central1 --limit=50

# Apps Script logs
# Check execution log in Apps Script editor
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes. Trading involves risk, and you should never trade with money you cannot afford to lose. The authors are not responsible for any financial losses.

Always test thoroughly in dry-run mode before enabling live trading.

## 🙏 Acknowledgments

- [Voyz ibind](https://github.com/Voyz/ibind) - Excellent IBKR API wrapper
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework  
- [Google Cloud Run](https://cloud.google.com/run) - Serverless container platform

---

**🎉 Ready to automate your trading with calendar events? Follow the [setup guide](docs/DEPLOYMENT.md) to get started!**