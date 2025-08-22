# Google Apps Script Calendar Integration

This directory contains the Google Apps Script code for calendar-triggered trading.

## 🚀 Quick Setup

### 1. Install and Authenticate clasp

```bash
# Install clasp globally (already done if you ran our scripts)
npm install -g @google/clasp

# Login to Google Apps Script
clasp login

# Enable Apps Script API (required for clasp)
# Go to: https://script.google.com/home/usersettings
# Enable "Google Apps Script API"
```

### 2. Create New Apps Script Project

```bash
# Navigate to the google-apps-script directory
cd google-apps-script

# Create new Apps Script project
clasp create --title "IBKR Trading Bot" --type standalone

# Push the code to Apps Script
clasp push
```

### 3. Configure the Script

1. **Update SERVICE_URL** in `Code.gs`:
   ```javascript
   SERVICE_URL: 'https://your-actual-service-url.run.app'
   ```

2. **Set your email** for notifications:
   ```javascript
   EMAIL_RECIPIENT: 'your-email@example.com'
   ```

### 4. Set Up Triggers

#### Option A: Calendar Event Trigger
1. Go to [Google Apps Script](https://script.google.com)
2. Open your "IBKR Trading Bot" project
3. Click the clock icon (Triggers)
4. Add trigger:
   - Function: `onCalendarEvent`
   - Event source: From calendar
   - Calendar: Your calendar
   - Event type: Event updated

#### Option B: Time-based Trigger
1. Add trigger:
   - Function: `executeTrade` (or create a wrapper function)
   - Event source: Time-driven
   - Type: Choose your frequency (daily, weekly, etc.)

### 5. Test the Integration

Run these functions in the Apps Script editor:

```javascript
testHealthCheck()    // Test connection to Cloud Run
testBuyBYD()        // Test a BUY trade
testCalendarParser() // Test calendar event parsing
```

## 📅 Calendar Event Formats

Your calendar events can trigger trades using these formats:

- **"BUY 5 AAPL"** → Buy 5 shares of Apple
- **"SELL 10 BYD"** → Sell 10 shares of BYD  
- **"Trade: BUY 1 TSLA"** → Buy 1 share of Tesla
- **"AAPL BUY 3"** → Buy 3 shares of Apple
- **"Just BUY"** → Buy 1 share of default symbol (BYD)

## 🔧 Configuration Options

Edit the `CONFIG` object in `Code.gs`:

```javascript
const CONFIG = {
  SERVICE_URL: 'https://your-service.run.app',
  API_KEY: '', // Optional API key
  DEFAULT_SYMBOL: 'BYD',
  DEFAULT_ACTION: 'BUY', 
  DEFAULT_QUANTITY: 1,
  SEND_EMAIL_NOTIFICATIONS: true,
  EMAIL_RECIPIENT: 'your-email@example.com'
};
```

## 🛠️ Development Workflow

```bash
# Make changes to Code.gs
# Push updates
clasp push

# View logs
clasp logs

# Open in browser
clasp open
```

## 🔐 Security Notes

- Apps Script runs with your Google account permissions
- All API calls are logged in Apps Script execution logs
- Consider using API keys for additional security
- Test thoroughly with DRY_RUN=true before going live

## 🐛 Troubleshooting

### Common Issues

1. **"Apps Script API not enabled"**
   - Go to https://script.google.com/home/usersettings
   - Enable "Google Apps Script API"

2. **Authentication errors**
   - Run `clasp login` again
   - Check OAuth scopes in `appsscript.json`

3. **Service URL not found**
   - Verify your Cloud Run service URL
   - Test the URL directly in browser

4. **Calendar trigger not working**
   - Check trigger setup in Apps Script console
   - Verify calendar permissions

### Debugging

- Use `console.log()` in your Apps Script functions
- View logs with `clasp logs` or in the Apps Script console
- Test individual functions in the Apps Script editor
