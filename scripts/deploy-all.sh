#!/bin/bash

# 🚀 IBKR Trading Bot - Unified Deployment Script
# This script follows CI/CD best practices to deploy across:
# 1. Git (version control)
# 2. Google Apps Script (clasp)
# 3. Google Cloud Run (automatic via GitHub)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SERVICE_NAME="ibkr-trading-bot"
REGION="us-central1"

echo -e "${PURPLE}🚀 IBKR Trading Bot - Unified Deployment${NC}"
echo "========================================"
echo ""

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_step() {
    echo -e "${PURPLE}🔄 $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check git status
check_git_status() {
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes:"
        git status --short
        echo ""
        read -p "Do you want to commit these changes? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter commit message: " commit_message
            if [ -z "$commit_message" ]; then
                commit_message="🔄 Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
            fi
            git add -A
            git commit -m "$commit_message"
            print_status "Changes committed"
        else
            print_warning "Proceeding with uncommitted changes"
        fi
    else
        print_status "Git working directory is clean"
    fi
}

# Function to deploy Apps Script
deploy_apps_script() {
    print_step "STEP 2: Deploying Google Apps Script"
    
    # Check if clasp is installed
    if ! command_exists clasp; then
        print_error "clasp is not installed. Installing now..."
        npm install -g @google/clasp
        print_status "clasp installed successfully"
    fi
    
    # Check if user is logged in to clasp
    if ! clasp login --status &> /dev/null; then
        print_error "Not logged in to Google Apps Script"
        echo "Please run: clasp login"
        echo "Then enable Apps Script API at: https://script.google.com/home/usersettings"
        exit 1
    fi
    
    print_status "clasp authentication verified"
    
    # Navigate to google-apps-script directory
    cd google-apps-script
    
    # Get the service URL from gcloud (if available)
    print_info "Getting Cloud Run service URL..."
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")
    
    if [ -n "$SERVICE_URL" ]; then
        print_status "Found service URL: $SERVICE_URL"
        
        # Update the SERVICE_URL in Code.js
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s|SERVICE_URL: '.*'|SERVICE_URL: '${SERVICE_URL}'|g" Code.js
        else
            # Linux
            sed -i "s|SERVICE_URL: '.*'|SERVICE_URL: '${SERVICE_URL}'|g" Code.js
        fi
        print_status "Updated SERVICE_URL in Code.js"
    else
        print_warning "Could not detect Cloud Run service URL"
        print_info "You may need to update SERVICE_URL manually in Code.js"
    fi
    
    # Push the code to Apps Script
    print_info "Pushing code to Google Apps Script..."
    clasp push
    print_status "Apps Script deployed successfully"
    
    # Go back to root directory
    cd ..
}

# Function to deploy to Git and trigger Cloud Run
deploy_git_and_cloud() {
    print_step "STEP 3: Deploying to Git (triggers Cloud Run)"
    
    # Push to GitHub (this triggers Cloud Run deployment)
    print_info "Pushing to GitHub..."
    git push origin main
    print_status "Code pushed to GitHub"
    
    print_info "Cloud Run deployment will start automatically via GitHub Actions"
    print_info "Monitor deployment at: https://console.cloud.google.com/run"
    
    # Wait a moment and check deployment status
    print_info "Waiting 30 seconds for deployment to start..."
    sleep 30
    
    # Check if service is healthy
    if [ -n "$SERVICE_URL" ]; then
        print_info "Testing service health..."
        if curl -s -f "$SERVICE_URL/health" > /dev/null; then
            print_status "Service is healthy!"
        else
            print_warning "Service health check failed. Check Cloud Run logs."
        fi
    fi
}

# Function to show deployment summary
show_summary() {
    echo ""
    echo -e "${PURPLE}📋 DEPLOYMENT SUMMARY${NC}"
    echo "====================="
    echo ""
    
    if [ -n "$SERVICE_URL" ]; then
        echo -e "${BLUE}🌐 Cloud Run Service:${NC}"
        echo "   URL: $SERVICE_URL"
        echo "   Health: $SERVICE_URL/health"
        echo "   API Docs: $SERVICE_URL/docs"
        echo ""
    fi
    
    echo -e "${BLUE}📅 Google Apps Script:${NC}"
    echo "   Open with: clasp open"
    echo "   Logs: Check Executions tab in Apps Script editor"
    echo ""
    
    echo -e "${BLUE}📊 Monitoring:${NC}"
    echo "   Cloud Run Logs: gcloud run services logs tail $SERVICE_NAME --region=$REGION"
    echo "   Apps Script: https://script.google.com/home"
    echo ""
    
    echo -e "${BLUE}🔧 Next Steps:${NC}"
    echo "   1. Test Apps Script: Run testServiceHealth() function"
    echo "   2. Create calendar event: 'TEST BUY 1 BYD'"
    echo "   3. Monitor Discord for notifications"
    echo "   4. Check calendar event for execution status"
    echo ""
}

# Main deployment flow
main() {
    print_step "STEP 1: Checking Git Status"
    check_git_status
    echo ""
    
    deploy_apps_script
    echo ""
    
    deploy_git_and_cloud
    echo ""
    
    show_summary
    
    print_status "🎉 Unified deployment completed successfully!"
    echo ""
    print_info "All components are now synchronized:"
    print_info "✅ Git repository (latest code)"
    print_info "✅ Google Apps Script (latest triggers)"
    print_info "✅ Google Cloud Run (auto-deployed from GitHub)"
}

# Pre-flight checks
echo -e "${BLUE}🔍 Pre-flight Checks${NC}"
echo "==================="

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "google-apps-script" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if git is installed and repo is initialized
if ! command_exists git; then
    print_error "Git is not installed"
    exit 1
fi

if [ ! -d ".git" ]; then
    print_error "Not a git repository. Run 'git init' first."
    exit 1
fi

# Check if gcloud is installed and authenticated
if ! command_exists gcloud; then
    print_error "Google Cloud CLI is not installed"
    exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_error "Not authenticated with Google Cloud. Run 'gcloud auth login' first."
    exit 1
fi

print_status "All pre-flight checks passed"
echo ""

# Run main deployment
main
