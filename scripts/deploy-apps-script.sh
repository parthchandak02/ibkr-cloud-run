#!/bin/bash

# Google Apps Script Deployment Script
# This script sets up and deploys the calendar integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📅 Google Apps Script Deployment${NC}"
echo "=================================="

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

# Check if clasp is installed
if ! command -v clasp &> /dev/null; then
    print_error "clasp is not installed. Installing now..."
    npm install -g @google/clasp
    print_status "clasp installed successfully"
fi

# Check if user is logged in to clasp
if ! clasp login --status &> /dev/null; then
    print_warning "Not logged in to Google Apps Script"
    echo "Please run: clasp login"
    echo "Then enable Apps Script API at: https://script.google.com/home/usersettings"
    exit 1
fi

print_status "clasp authentication verified"

# Navigate to google-apps-script directory
cd google-apps-script

# Check if .clasp.json exists (project already created)
if [ ! -f ".clasp.json" ]; then
    print_status "Creating new Google Apps Script project..."
    clasp create --title "IBKR Trading Bot" --type standalone
    print_status "Project created successfully"
else
    print_status "Using existing Apps Script project"
fi

# Get the service URL from gcloud
print_status "Getting Cloud Run service URL..."
SERVICE_URL=$(gcloud run services describe ibkr-trading-bot --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
    print_warning "Could not automatically detect Cloud Run service URL"
    echo "Please update the SERVICE_URL in Code.gs manually"
    SERVICE_URL="https://your-service-url.run.app"
else
    print_status "Found service URL: $SERVICE_URL"
    
    # Update the SERVICE_URL in Code.gs
    sed -i.bak "s|SERVICE_URL: '.*'|SERVICE_URL: '${SERVICE_URL}'|g" Code.gs
    print_status "Updated SERVICE_URL in Code.gs"
fi

# Push the code to Apps Script
print_status "Pushing code to Google Apps Script..."
clasp push --force

# Get the Apps Script URL
SCRIPT_URL=$(clasp open --webapp 2>/dev/null | grep -o 'https://script.google.com/[^[:space:]]*' || echo "")

print_status "Deployment completed!"
echo ""
echo -e "${BLUE}📋 Next Steps${NC}"
echo "=============="
echo "1. Open your Apps Script project:"
if [ -n "$SCRIPT_URL" ]; then
    echo "   $SCRIPT_URL"
else
    echo "   Run: clasp open"
fi
echo ""
echo "2. Update configuration in Code.gs:"
echo "   - SERVICE_URL: $SERVICE_URL"
echo "   - EMAIL_RECIPIENT: your-email@example.com"
echo ""
echo "3. Set up triggers:"
echo "   - Click the clock icon (Triggers)"
echo "   - Add calendar or time-based triggers"
echo ""
echo "4. Test the integration:"
echo "   - Run testHealthCheck() function"
echo "   - Run testBuyBYD() function"
echo ""
echo "5. Enable Apps Script API if not done:"
echo "   - https://script.google.com/home/usersettings"
echo ""

# Test the health check
print_status "Testing service health from Apps Script..."
echo "You can run this test in the Apps Script editor:"
echo ""
echo -e "${YELLOW}function quickTest() {"
echo "  console.log('Testing service...');"
echo "  const result = testHealthCheck();"
echo "  console.log('Result:', result);"
echo "}${NC}"
echo ""

print_status "Apps Script deployment completed!"
