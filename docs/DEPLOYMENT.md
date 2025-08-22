# Deployment Guide

## Quick Deployment Checklist

### ✅ Prerequisites
- [ ] Google Cloud Platform account
- [ ] Interactive Brokers account with Client Portal API enabled
- [ ] OAuth 1.0a credentials from IBKR
- [ ] Discord webhook URL (optional)
- [ ] Google Cloud CLI installed and authenticated

### ✅ Google Cloud Setup

1. **Create Project and Enable APIs**:
   ```bash
   # Set your project
   gcloud config set project YOUR_PROJECT_ID
   
   # Enable required APIs
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com
   ```

2. **Create Secrets**:
   ```bash
   # IBKR credentials
   echo "YOUR_ACCESS_TOKEN" | gcloud secrets create ibind-access-token --data-file=-
   cat access_token_secret.txt | gcloud secrets create ibind-access-token-secret --data-file=-
   cat consumer_key.txt | gcloud secrets create ibind-consumer-key --data-file=-
   echo "YOUR_DH_PRIME" | gcloud secrets create ibind-dh-prime --data-file=-
   
   # PEM files (base64 encoded for Cloud Run)
   base64 -i private_encryption.pem | gcloud secrets create ibind-encryption-key --data-file=-
   base64 -i private_signature.pem | gcloud secrets create ibind-signature-key --data-file=-
   
   # Discord webhook (optional)
   echo "YOUR_DISCORD_WEBHOOK_URL" | gcloud secrets create discord-webhook-url --data-file=-
   ```

3. **Grant Permissions**:
   ```bash
   # Get your project number
   PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
   
   # Grant Cloud Run service account access to secrets
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

### ✅ Deploy to Cloud Run

**One-command deployment**:
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

### ✅ Test Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe ibkr-trading-bot --region=us-central1 --format="value(status.url)")

# Test health check
curl $SERVICE_URL/health

# Test trade endpoint (dry run)
curl -X POST $SERVICE_URL/trade \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BYD", "action": "BUY", "quantity": 1}'
```

### ✅ Monitor Deployment

```bash
# View logs
gcloud run services logs read ibkr-trading-bot --region=us-central1 --limit=50

# Check service status
gcloud run services describe ibkr-trading-bot --region=us-central1
```

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `IBIND_USE_OAUTH` | Enable OAuth 1.0a authentication | Yes | `true` |
| `IBIND_OAUTH1A_ACCESS_TOKEN` | IBKR access token | Yes | - |
| `IBIND_OAUTH1A_ACCESS_TOKEN_SECRET` | IBKR access token secret | Yes | - |
| `IBIND_OAUTH1A_CONSUMER_KEY` | IBKR consumer key | Yes | - |
| `IBIND_OAUTH1A_DH_PRIME` | IBKR DH prime parameter | Yes | - |
| `IBIND_OAUTH1A_ENCRYPTION_KEY_FP` | Path to encryption key (base64 in cloud) | Yes | - |
| `IBIND_OAUTH1A_SIGNATURE_KEY_FP` | Path to signature key (base64 in cloud) | Yes | - |
| `IBIND_OAUTH1A_REALM` | OAuth realm | No | `limited_poa` |
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | No | - |
| `DEFAULT_QUANTITY` | Default trade quantity | No | `1` |
| `DRY_RUN` | Enable dry run mode | No | `true` |
| `PORT` | Server port | No | `8000` (Cloud Run uses `8080`) |

## Troubleshooting

### Common Issues

1. **Permission Denied on Secrets**:
   - Ensure service account has `secretmanager.secretAccessor` role
   - Check project number is correct in IAM binding

2. **IBKR Connection Failed**:
   - Verify OAuth credentials are correct
   - Check that Client Portal API is enabled in IBKR account
   - Ensure proper base64 encoding for PEM files in Cloud Run

3. **Container Failed to Start**:
   - Check build logs for dependency issues
   - Verify Dockerfile syntax
   - Ensure all required files are copied

4. **API Errors**:
   - Check Cloud Run logs for detailed error messages
   - Test endpoints individually
   - Verify request format matches API documentation

### Logs and Debugging

```bash
# Stream live logs
gcloud run services logs tail ibkr-trading-bot --region=us-central1

# Get build logs
gcloud builds list --limit=5
gcloud builds log BUILD_ID

# Test locally before deploying
python main.py
```
