#!/bin/bash

# 📅 Calendar Trigger Setup Script for IBKR Trading Bot
# This script deploys the Google Apps Script and sets up calendar-driven triggers

set -e

echo "🚀 Setting up calendar-driven trading triggers..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "google-apps-script/Code.gs" ]; then
    echo -e "${RED}❌ Error: Run this script from the project root directory${NC}"
    exit 1
fi

# Navigate to Google Apps Script directory
cd google-apps-script

echo -e "${BLUE}📁 Entering Google Apps Script directory...${NC}"

# Check if clasp is installed
if ! command -v clasp &> /dev/null; then
    echo -e "${RED}❌ Error: clasp is not installed${NC}"
    echo -e "${YELLOW}💡 Install it with: npm install -g @google/clasp${NC}"
    exit 1
fi

# Check if user is logged into clasp
if ! clasp list &> /dev/null; then
    echo -e "${YELLOW}🔐 Please log into clasp first...${NC}"
    clasp login
fi

echo -e "${BLUE}📤 Pushing Google Apps Script files...${NC}"

# Push the latest code to Google Apps Script
clasp push --force

echo -e "${BLUE}⚙️ Setting up calendar triggers...${NC}"

# Execute the trigger setup function
clasp run installTradingTriggers

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Calendar triggers installed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📋 What was set up:${NC}"
    echo "  1. 📅 Calendar Event Trigger - Fires when events are created/modified"
    echo "  2. ⏰ Time-based Trigger - Checks every minute for upcoming events"
    echo ""
    echo -e "${YELLOW}🎯 How to use:${NC}"
    echo "  • Create calendar event: 'BUY 1 BYD'"
    echo "  • Create calendar event: 'SELL 5 AAPL'"
    echo "  • Create calendar event: 'Trade: BUY 10 TSLA'"
    echo ""
    echo -e "${YELLOW}📊 Monitoring:${NC}"
    echo "  • Check Apps Script execution logs"
    echo "  • Monitor Discord notifications"
    echo "  • View email notifications"
    echo ""
    echo -e "${GREEN}🎉 Calendar-driven trading is now active!${NC}"
else
    echo -e "${RED}❌ Failed to set up triggers${NC}"
    echo -e "${YELLOW}💡 Try running manually in Apps Script editor:${NC}"
    echo "     1. Open your Apps Script project"
    echo "     2. Run the 'installTradingTriggers' function"
    exit 1
fi

# List current triggers to verify
echo -e "${BLUE}📋 Listing current triggers...${NC}"
clasp run listCurrentTriggers

echo ""
echo -e "${GREEN}🎊 Setup complete! Your calendar is now connected to your trading bot.${NC}"
