# IBKR Trading Bot

A production-ready trading bot for Interactive Brokers using the [Voyz ibind](https://github.com/Voyz/ibind) library. Supports OAuth 1.0a authentication and can be deployed to Google Cloud Run with calendar-triggered trades.

## 🚀 Features

- **FastAPI** web service with REST API
- **Interactive Brokers** integration via Voyz ibind
- **OAuth 1.0a authentication** for secure IBKR access
- **Google Cloud Run** deployment ready
- **Discord notifications** for trade alerts
- **Calendar-triggered trades** via Google Apps Script
- **Docker containerization** with optimized builds using `uv`
- **Comprehensive health checks** and monitoring

## 📋 Prerequisites

- Interactive Brokers account with Client Portal API access
- Google Cloud Platform account
- Discord webhook (optional, for notifications)
- Python 3.12+ (for local development)

## 🏗️ Architecture

```
Calendar Event → Google Apps Script → Cloud Run → IBKR API → Discord Notification
```

- **Trigger**: Google Calendar events
- **Processor**: FastAPI service on Cloud Run
- **Broker**: Interactive Brokers via ibind
- **Notifications**: Discord webhooks

## 🔧 Local Development Setup

### 1. Clone and Setup

```bash
git clone https://github.com/parthchandak02/ibkr-cloud-run.git
cd ibkr-cloud-run

# Create virtual environment using uv (recommended)
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Configure Environment

Create a `config.env` file with your credentials:

```env
# Discord Webhook for notifications
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL

# IBKR OAuth 1.0a Configuration
IBIND_USE_OAUTH=true
IBIND_OAUTH1A_ACCESS_TOKEN=your_access_token
IBIND_OAUTH1A_ACCESS_TOKEN_SECRET=your_access_token_secret
IBIND_OAUTH1A_CONSUMER_KEY=your_consumer_key
IBIND_OAUTH1A_DH_PRIME=your_dh_prime
IBIND_OAUTH1A_ENCRYPTION_KEY_FP=/path/to/private_encryption.pem
IBIND_OAUTH1A_SIGNATURE_KEY_FP=/path/to/private_signature.pem
IBIND_OAUTH1A_REALM=limited_poa

# Trading settings
DEFAULT_QUANTITY=1
DRY_RUN=true
```

### 3. Run Locally

```bash
python main.py
```

The service will be available at `http://localhost:8000`

- Health check: `GET /health`
- API docs: `GET /docs`
- Place trade: `POST /trade`

## ☁️ Cloud Deployment

### Prerequisites

1. **Google Cloud Setup**:
   ```bash
   # Install Google Cloud CLI
   # https://cloud.google.com/sdk/docs/install
   
   # Authenticate
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable required APIs
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com
   ```

2. **Store Secrets in Secret Manager**:
   ```bash
   # Store IBKR credentials
   echo "your_access_token" | gcloud secrets create ibind-access-token --data-file=-
   echo "your_access_token_secret" | gcloud secrets create ibind-access-token-secret --data-file=-
   echo "your_consumer_key" | gcloud secrets create ibind-consumer-key --data-file=-
   echo "your_dh_prime" | gcloud secrets create ibind-dh-prime --data-file=-
   
   # Store PEM files (base64 encoded)
   base64 -i private_encryption.pem | gcloud secrets create ibind-encryption-key --data-file=-
   base64 -i private_signature.pem | gcloud secrets create ibind-signature-key --data-file=-
   
   # Store Discord webhook
   echo "your_discord_webhook_url" | gcloud secrets create discord-webhook-url --data-file=-
   ```

3. **Grant Permissions**:
   ```bash
   # Grant Cloud Run service account access to secrets
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

### Deploy to Cloud Run

```bash
gcloud run deploy ibkr-trading-bot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars IBIND_USE_OAUTH=true \
  --set-env-vars DEFAULT_QUANTITY=1 \
  --set-env-vars DRY_RUN=true \
  --set-env-vars IBIND_OAUTH1A_REALM=limited_poa \
  --update-secrets IBIND_OAUTH1A_ACCESS_TOKEN=ibind-access-token:latest \
  --update-secrets IBIND_OAUTH1A_ACCESS_TOKEN_SECRET=ibind-access-token-secret:latest \
  --update-secrets IBIND_OAUTH1A_CONSUMER_KEY=ibind-consumer-key:latest \
  --update-secrets IBIND_OAUTH1A_DH_PRIME=ibind-dh-prime:latest \
  --update-secrets IBIND_OAUTH1A_ENCRYPTION_KEY_FP=ibind-encryption-key:latest \
  --update-secrets IBIND_OAUTH1A_SIGNATURE_KEY_FP=ibind-signature-key:latest \
  --update-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest
```

## 📅 Calendar Integration

### Google Apps Script Setup

1. **Create Apps Script Project**:
   - Go to [Google Apps Script](https://script.google.com/)
   - Create new project

2. **Add Code**:
   ```javascript
   function onCalendarEvent() {
     const response = UrlFetchApp.fetch('https://your-service.run.app/trade', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         'X-API-Key': 'your-api-key'  // Optional: for authentication
       },
       payload: JSON.stringify({
         symbol: 'BYD',
         action: 'BUY',
         quantity: 1
       })
     });
     
     console.log('Trade response:', response.getContentText());
   }
   ```

3. **Set Up Trigger**:
   - Click the clock icon in Apps Script
   - Add time-driven trigger or calendar event trigger

## 🔒 Security

- **OAuth 1.0a**: Secure IBKR authentication
- **Google Secret Manager**: Encrypted credential storage
- **HTTPS**: All communications encrypted
- **IAM**: Fine-grained access control

## 📊 API Reference

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "discord_configured": true,
  "ibkr_configured": true,
  "ibkr_status": "connected (1 accounts)"
}
```

### Place Trade
```http
POST /trade
```

**Request:**
```json
{
  "symbol": "BYD",
  "action": "BUY",
  "quantity": 1
}
```

**Response:**
```json
{
  "status": "simulated",
  "message": "🔍 DRY RUN: Would BUY 1 shares of BYD (conid: {'1211': 46652429})",
  "symbol": "BYD",
  "action": "BUY",
  "quantity": 1,
  "conid": {"1211": 46652429},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **IBKR Connection Failed**: Check OAuth credentials and ensure Client Portal API is enabled
2. **Discord Notifications Not Working**: Verify webhook URL and network connectivity
3. **BYD Symbol Not Found**: Ensure IBKR client is properly initialized and account has HK market access

### Logs

```bash
# View Cloud Run logs
gcloud run services logs read ibkr-trading-bot --region=us-central1 --limit=50

# Local debugging
python main.py  # Check console output
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please ensure compliance with Interactive Brokers terms of service and relevant financial regulations.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Trading involves risk, and you should never trade with money you cannot afford to lose. The authors are not responsible for any financial losses.

## 🙏 Acknowledgments

- [Voyz ibind](https://github.com/Voyz/ibind) - Excellent IBKR API wrapper
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Google Cloud Run](https://cloud.google.com/run) - Serverless container platform
