# 📱 Google Apps Script Integration

This directory contains the Google Apps Script code that enables calendar-driven trading automation.

## 🎯 What It Does

- **📅 Monitors Google Calendar** for trading events
- **🔍 Parses event titles** like "BUY 1 BYD" into trade instructions  
- **🚀 Calls Cloud Run service** to execute trades
- **📧 Sends email notifications** for all trades
- **⏰ Supports both immediate and scheduled execution**

## 📁 Files

| File | Purpose |
|------|---------|
| `Code.js` | Main trading bot logic and calendar integration |
| `setup-triggers.js` | Advanced trigger management functions |
| `appsscript.json` | Apps Script project configuration |

## 🚀 Quick Setup

### 1. Deploy to Apps Script

```bash
# Install clasp if you haven't already
npm install -g @google/clasp

# Login to Google Apps Script
clasp login

# Create new project
clasp create --title "IBKR Trading Bot" --type standalone

# Push code
clasp push
```

### 2. Configure Service URL

1. **Open Apps Script Editor**: `clasp open`
2. **Update CONFIG** in `Code.js`:
   ```javascript
   const CONFIG = {
     SERVICE_URL: 'https://your-service.run.app',  // Your Cloud Run URL
     EMAIL_RECIPIENT: 'your-email@example.com',    // Your email
     // ... other settings
   };
   ```

### 3. Setup Calendar Triggers

**Option A: Automated (Recommended)**
```javascript
// Run this function in Apps Script editor:
installTradingTriggers()
```

**Option B: Manual Setup**
1. Go to **Triggers** tab (⏰ icon)
2. **Add Calendar Trigger**:
   - Function: `onCalendarEventUpdated`
   - Event source: `From calendar`
   - Event type: `Calendar updated`
3. **Add Time Trigger**:
   - Function: `checkUpcomingTradingEvents`
   - Event source: `Time-driven`
   - Type: `Minutes timer`
   - Interval: `Every minute`

## 🎯 Supported Calendar Event Formats

The system recognizes these patterns in calendar event titles:

```javascript
✅ "BUY 1 BYD"           → {action: "BUY", quantity: 1, symbol: "BYD"}
✅ "SELL 5 AAPL"         → {action: "SELL", quantity: 5, symbol: "AAPL"}  
✅ "Trade: BUY 10 TSLA"  → {action: "BUY", quantity: 10, symbol: "TSLA"}
✅ "AAPL BUY 3"          → {action: "BUY", quantity: 3, symbol: "AAPL"}
✅ "Just BUY"            → {action: "BUY", quantity: 1, symbol: "BYD"} (default)

❌ "Random meeting"      → null (ignored)
```

## 🔧 Configuration Options

### CONFIG Object

```javascript
const CONFIG = {
  // Your Cloud Run service URL (REQUIRED)
  SERVICE_URL: 'https://your-service.run.app',
  
  // Optional: API key for authentication
  API_KEY: '', // Leave empty if not using API key auth
  
  // Default trading settings
  DEFAULT_SYMBOL: 'BYD',     // Default stock symbol
  DEFAULT_ACTION: 'BUY',     // Default action
  DEFAULT_QUANTITY: 1,       // Default quantity
  
  // Notification settings
  SEND_EMAIL_NOTIFICATIONS: true,
  EMAIL_RECIPIENT: 'your-email@example.com'
};
```

## 🧪 Testing Functions

Use these functions to test your setup:

```javascript
// Test individual components
testBuyBYD()              // Test BUY trade execution
testSellBYD()             // Test SELL trade execution
testHealthCheck()         // Test Cloud Run connectivity
testCalendarParser()      // Test event parsing logic

// Trigger management
installTradingTriggers()  // Install calendar triggers
listCurrentTriggers()     // View active triggers
removeAllTriggers()       // Remove all triggers (cleanup)
```

## 📊 How It Works

### Calendar Event Trigger Flow

```
Calendar Event Created → onCalendarEventUpdated() → getRecentTradingEvents() → 
parseTradeFromCalendarEvent() → executeTrade() → Cloud Run API → Notifications
```

### Time-Based Trigger Flow

```
Every Minute → checkUpcomingTradingEvents() → getEvents(now, +2min) → 
parseTradeFromCalendarEvent() → executeTrade() → Cloud Run API → Notifications
```

## 🔍 Function Reference

### Main Functions

| Function | Purpose | Trigger |
|----------|---------|---------|
| `executeTrade(symbol, action, quantity)` | Execute a trade via Cloud Run | Manual/Calendar |
| `onCalendarEventUpdated(e)` | Handle calendar event changes | Calendar trigger |
| `checkUpcomingTradingEvents()` | Check for scheduled trades | Time trigger |
| `parseTradeFromCalendarEvent(title, desc)` | Parse calendar event into trade | Internal |

### Setup Functions

| Function | Purpose |
|----------|---------|
| `installTradingTriggers()` | Install both calendar and time triggers |
| `listCurrentTriggers()` | List all active triggers |
| `removeExistingTriggers()` | Remove trading-related triggers |
| `removeAllTriggers()` | Remove all triggers (cleanup) |

### Test Functions

| Function | Purpose |
|----------|---------|
| `testBuyBYD()` | Test BUY 1 BYD trade |
| `testSellBYD()` | Test SELL 1 BYD trade |
| `testHealthCheck()` | Test Cloud Run connectivity |
| `testCalendarParser()` | Test event parsing with examples |

## 📱 Usage Examples

### Create Trading Events

1. **Immediate Execution**:
   - Create event: "BUY 1 BYD"
   - Executes immediately when event is created

2. **Scheduled Execution**:
   - Create event: "SELL 5 AAPL" at 2:30 PM
   - Executes at 2:30 PM when time trigger detects it

3. **Complex Trades**:
   - "Trade: BUY 100 TSLA" → Executes BUY 100 TSLA
   - "AAPL SELL 50" → Executes SELL 50 AAPL

### Monitor Execution

1. **Apps Script Logs**:
   - View → Execution log
   - Shows all trigger activations and trade attempts

2. **Email Notifications**:
   - Automatic emails for all trades
   - Includes trade details and results

3. **Discord Notifications**:
   - Real-time Discord messages (if configured)
   - Color-coded by trade status

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Triggers not firing** | Check trigger permissions, re-run `installTradingTriggers()` |
| **"Service not found" error** | Verify SERVICE_URL is correct in CONFIG |
| **Email not sending** | Check EMAIL_RECIPIENT setting and Gmail permissions |
| **Calendar events ignored** | Verify event title format matches supported patterns |

### Debug Steps

1. **Test connectivity**:
   ```javascript
   testHealthCheck()  // Should return service status
   ```

2. **Test parsing**:
   ```javascript
   testCalendarParser()  // Shows parsing examples
   ```

3. **Check triggers**:
   ```javascript
   listCurrentTriggers()  // Shows active triggers
   ```

4. **Manual trade test**:
   ```javascript
   testBuyBYD()  // Direct trade test
   ```

## 🔒 Security Notes

- **No secrets in code** - All credentials stored in Cloud Run
- **HTTPS only** - All API calls use secure connections
- **Email notifications** - Trade confirmations sent to your email
- **Execution logging** - All actions logged in Apps Script

## 📈 Advanced Features

### Custom Event Parsing

Modify `parseTradeFromCalendarEvent()` to support custom formats:

```javascript
// Add custom pattern
const customPattern = /\bTRADE\s+([A-Z]+)\s+(BUY|SELL)\s+(\d+)\b/;
const customMatch = text.match(customPattern);
if (customMatch) {
  return {
    symbol: customMatch[1],
    action: customMatch[2], 
    quantity: parseInt(customMatch[3])
  };
}
```

### API Key Authentication

If you add API key auth to your Cloud Run service:

```javascript
const CONFIG = {
  API_KEY: 'your-api-key-here',
  // ... other config
};
```

### Multiple Calendars

To monitor multiple calendars, modify `getRecentTradingEvents()`:

```javascript
// Monitor specific calendar
const calendar = CalendarApp.getCalendarById('calendar-id@gmail.com');
const events = calendar.getEvents(past, future);
```

---

**🎉 Your Google Apps Script is now ready to automate trades from calendar events!**

**Next Steps:**
- Create a test calendar event: "BUY 1 BYD"
- Check the execution log for activity
- Monitor your email for trade notifications