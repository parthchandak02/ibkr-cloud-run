# 📅 Calendar-Driven Trading Setup Guide

## 🎯 **What You Asked For: Automatic Calendar Event Triggers**

Based on your screenshots, I can see you want to set up **calendar event triggers** instead of just time-driven triggers. Here's the complete solution with both **manual** and **automated CLASP** setup options.

## 🔍 **Research Summary: Calendar Triggers in Google Apps Script**

### **Types of Calendar Triggers Available:**

| Trigger Type | When It Fires | Best For | Setup Method |
|-------------|---------------|----------|--------------|
| **Calendar Event** | When events are created/modified/deleted | Immediate response to new events | Manual UI or CLASP |
| **Time-Based** | Every X minutes to check for upcoming events | Executing trades at event start time | Manual UI or CLASP |
| **Hybrid** | Both triggers working together | Most reliable calendar trading | **⭐ RECOMMENDED** |

## 🛠️ **Implementation: We Already Have Calendar Parsing!**

Your Apps Script already includes sophisticated calendar parsing:

```javascript
// Already implemented in your Code.gs:
function parseTradeFromCalendarEvent(title, description = '') {
  // Supports formats like:
  // - "BUY 5 AAPL"
  // - "SELL 10 BYD" 
  // - "Trade: BUY 1 TSLA"
  // - "AAPL BUY 3"
}
```

## 🚀 **Setup Methods: Choose Your Approach**

### **Option 1: 🖱️ Manual Setup (Via Apps Script UI)**

**Follow your screenshot process:**

1. **Open Apps Script** → Your IBKR Trading Bot project
2. **Click Triggers** (⏰ icon in left sidebar)
3. **Add Trigger** → Choose these settings:
   - **Function to run**: `onCalendarEventUpdated`
   - **Event source**: `From calendar` 
   - **Event type**: `Calendar updated`
   - **Failure notification**: `Notify me daily`

4. **Add Second Trigger**:
   - **Function to run**: `checkUpcomingTradingEvents`
   - **Event source**: `Time-driven`
   - **Type of time based trigger**: `Minutes timer`
   - **Select minute interval**: `Every minute`

### **Option 2: 🚀 Automated CLASP Setup (Recommended)**

**Run our automated script:**

```bash
# From your project root:
./scripts/setup-calendar-triggers.sh
```

**Or manually in Apps Script:**

```javascript
// Run this function once in Apps Script editor:
installTradingTriggers()
```

This installs **both triggers** automatically:
- 📅 Calendar event trigger (immediate response)
- ⏰ Time-based trigger (event start timing)

## 📋 **How the Calendar Triggers Work**

### **Calendar Event Trigger** (`onCalendarEventUpdated`)
- **Fires when**: ANY calendar event is created, modified, or deleted
- **Does**: Scans recent events for trading keywords (BUY, SELL, TRADE)
- **Executes**: Immediate trades when events are created

### **Time-Based Trigger** (`checkUpcomingTradingEvents`)  
- **Fires when**: Every minute
- **Does**: Checks for events starting in next 2 minutes
- **Executes**: Scheduled trades at event start time

## 🎯 **Calendar Event Examples**

### **Immediate Execution** (via Calendar Event Trigger)
```
Create calendar event: "BUY 1 BYD"
→ Triggers immediately when event is created
→ Executes trade right away
```

### **Scheduled Execution** (via Time-Based Trigger)
```
Create calendar event: "BUY 1 BYD" at 2:30 PM
→ Time trigger detects at 2:28 PM
→ Executes trade at 2:30 PM
```

## 📊 **Supported Calendar Event Formats**

Your system recognizes these patterns:

```javascript
✅ "BUY 5 AAPL"          → BUY 5 shares of AAPL
✅ "SELL 10 BYD"         → SELL 10 shares of BYD  
✅ "Trade: BUY 1 TSLA"   → BUY 1 share of TSLA
✅ "AAPL BUY 3"          → BUY 3 shares of AAPL
✅ "Just BUY"            → BUY 1 share of default symbol (BYD)

❌ "Random meeting"      → Ignored (no trading keywords)
```

## 🔧 **Advanced Setup via CLASP (What We Built)**

We created a complete automation system:

### **Files Added:**
- `google-apps-script/setup-triggers.js` - Trigger management functions
- `scripts/setup-calendar-triggers.sh` - Automated deployment script
- `CALENDAR_TRIGGERS_GUIDE.md` - This guide

### **Functions Added to Code.gs:**
- `installTradingTriggers()` - One-click trigger setup
- `onCalendarEventUpdated()` - Calendar event handler
- `checkUpcomingTradingEvents()` - Time-based event checker
- `listCurrentTriggers()` - View all active triggers
- `removeExistingTriggers()` - Clean up for fresh install

## 🧪 **Testing Your Calendar Triggers**

### **Test Calendar Event Trigger:**
1. Create calendar event: **"BUY 1 BYD"**
2. Check Apps Script execution log
3. Verify Discord notification
4. Confirm trade execution

### **Test Time-Based Trigger:**
1. Create calendar event: **"SELL 1 AAPL"** scheduled 2 minutes from now
2. Wait for execution time
3. Check logs and notifications

## 📱 **Quick Setup Commands**

### **Deploy with CLASP:**
```bash
cd google-apps-script
clasp push
clasp run installTradingTriggers
```

### **Or use our script:**
```bash
./scripts/setup-calendar-triggers.sh
```

### **Manual in Apps Script:**
1. Open your Apps Script project
2. Run function: `installTradingTriggers`
3. Check triggers with: `listCurrentTriggers`

## 🎊 **What You Get After Setup**

### **✅ Calendar Event Trigger**
- **Monitors**: Your Google Calendar for new/modified events
- **Responds**: Immediately when events with trading keywords are created
- **Executes**: Trades based on event title/description

### **✅ Time-Based Trigger**  
- **Checks**: Every minute for upcoming events
- **Executes**: Trades at scheduled event start times
- **Ensures**: No missed trades due to timing

### **✅ Email & Discord Notifications**
- **Reports**: All trigger activations and trade executions
- **Logs**: Detailed execution information
- **Alerts**: Success and error notifications

## 🎯 **Answer to Your Question**

> "Should I do something such that every time a calendar event is triggered, can it automatically do this?"

**YES! We implemented exactly what you asked for:**

1. **✅ Calendar Event Triggers** - Auto-fire when events are created
2. **✅ CLASP Automation** - Backend setup using the CLASP tool you have
3. **✅ Multiple Setup Options** - Manual UI or automated script
4. **✅ Already Implemented** - Calendar parsing logic was already in your Code.gs

**You can now:**
- Create calendar events with "BUY 1 BYD" and they'll execute automatically
- Set up triggers manually (via UI) or automatically (via our script)
- Use both immediate and scheduled trading execution

Your system is ready for full calendar-driven automation! 🚀
