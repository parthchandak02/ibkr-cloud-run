#!/bin/bash

# IBKR Trading Bot Deployment Script
# This script automates the deployment process to Google Cloud Run

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="ibkr-trading-bot"
REGION="us-central1"

echo -e "${BLUE}🚀 IBKR Trading Bot Deployment Script${NC}"
echo "======================================"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with Google Cloud. Run 'gcloud auth login' first."
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    print_error "No Google Cloud project set. Run 'gcloud config set project PROJECT_ID' first."
    exit 1
fi

print_status "Using project: $PROJECT_ID"

# Get project number for IAM binding
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
print_status "Project number: $PROJECT_NUMBER"

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com secretmanager.googleapis.com

# Check if secrets exist
print_status "Checking if secrets exist..."
REQUIRED_SECRETS=(
    "ibind-access-token"
    "ibind-access-token-secret" 
    "ibind-consumer-key"
    "ibind-dh-prime"
    "ibind-encryption-key"
    "ibind-signature-key"
)

MISSING_SECRETS=()
for secret in "${REQUIRED_SECRETS[@]}"; do
    if ! gcloud secrets describe $secret &> /dev/null; then
        MISSING_SECRETS+=($secret)
    fi
done

if [ ${#MISSING_SECRETS[@]} -ne 0 ]; then
    print_warning "Missing secrets: ${MISSING_SECRETS[*]}"
    print_warning "Please create these secrets first using the instructions in docs/DEPLOYMENT.md"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Grant service account access to secrets
print_status "Granting service account access to Secret Manager..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet

# Deploy to Cloud Run
print_status "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
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
    --update-secrets DISCORD_WEBHOOK_URL=discord-webhook-url:latest \
    --quiet

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

print_status "Deployment completed!"
echo ""
echo -e "${BLUE}📋 Service Information${NC}"
echo "====================="
echo "Service URL: $SERVICE_URL"
echo "Health check: $SERVICE_URL/health"
echo "API docs: $SERVICE_URL/docs"
echo ""

# Test the deployment
print_status "Testing deployment..."
echo "Testing health endpoint..."
if curl -s -f "$SERVICE_URL/health" > /dev/null; then
    print_status "Health check passed!"
else
    print_warning "Health check failed. Check logs with:"
    echo "gcloud run services logs read $SERVICE_NAME --region=$REGION"
fi

echo ""
print_status "Deployment script completed!"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test the API endpoints"
echo "2. Set up Google Apps Script for calendar integration"
echo "3. Configure live trading (set DRY_RUN=false when ready)"
echo ""
echo "For monitoring: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
