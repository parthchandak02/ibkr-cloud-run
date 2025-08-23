/**
 * IBKR Trading Bot - Google Apps Script Integration
 * 
 * This script handles calendar-triggered trades by calling our Cloud Run service.
 * Deploy this to Google Apps Script and set up calendar or time-based triggers.
 */

// Configuration - Update these values for your deployment
const CONFIG = {
  // Your Cloud Run service URL
  SERVICE_URL: 'https://ibkr-trading-bot-gl6tvkxsha-uc.a.run.app',
  
  // Optional: API key for authentication (if you add API key auth to your service)
  API_KEY: '', // Leave empty if not using API key authentication
  
  // Default trading settings
  DEFAULT_SYMBOL: 'BYD',
  DEFAULT_ACTION: 'BUY',
  DEFAULT_QUANTITY: 1,
  
  // Notification settings
  SEND_EMAIL_NOTIFICATIONS: true,
  EMAIL_RECIPIENT: 'your-email@example.com' // Update with your email
};

/**
 * Main function to execute a trade
 * This can be called manually or triggered by calendar events
 */
function executeTrade(symbol = CONFIG.DEFAULT_SYMBOL, action = CONFIG.DEFAULT_ACTION, quantity = CONFIG.DEFAULT_QUANTITY) {
  try {
    console.log(`🚀 Executing trade: ${action} ${quantity} shares of ${symbol}`);
    
    // Prepare the trade request
    const tradeRequest = {
      symbol: symbol,
      action: action.toUpperCase(),
      quantity: quantity
    };
    
    // Prepare request headers
    const headers = {
      'Content-Type': 'application/json'
    };
    
    // Add API key if configured
    if (CONFIG.API_KEY) {
      headers['X-API-Key'] = CONFIG.API_KEY;
    }
    
    // Make the API call to Cloud Run
    const response = UrlFetchApp.fetch(`${CONFIG.SERVICE_URL}/trade`, {
      method: 'POST',
      headers: headers,
      payload: JSON.stringify(tradeRequest),
      muteHttpExceptions: true // Don't throw on HTTP errors
    });
    
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    console.log(`📊 Response Code: ${responseCode}`);
    console.log(`📋 Response: ${responseText}`);
    
    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      const message = `✅ Trade executed successfully: ${result.message}`;
      console.log(message);
      
      // Send email notification if enabled
      if (CONFIG.SEND_EMAIL_NOTIFICATIONS) {
        sendEmailNotification('Trade Executed Successfully', message, result);
      }
      
      return result;
    } else {
      const errorMessage = `❌ Trade execution failed (${responseCode}): ${responseText}`;
      console.error(errorMessage);
      
      // Send error notification
      if (CONFIG.SEND_EMAIL_NOTIFICATIONS) {
        sendEmailNotification('Trade Execution Failed', errorMessage);
      }
      
      throw new Error(errorMessage);
    }
    
  } catch (error) {
    const errorMessage = `💥 Error executing trade: ${error.message}`;
    console.error(errorMessage);
    
    // Send error notification
    if (CONFIG.SEND_EMAIL_NOTIFICATIONS) {
      sendEmailNotification('Trade Script Error', errorMessage);
    }
    
    throw error;
  }
}

/**
 * Test function to check if the service is healthy
 */
function testServiceHealth() {
  try {
    console.log('🏥 Testing service health...');
    
    const response = UrlFetchApp.fetch(`${CONFIG.SERVICE_URL}/health`, {
      method: 'GET',
      muteHttpExceptions: true
    });
    
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    console.log(`📊 Health Response Code: ${responseCode}`);
    console.log(`📋 Health Response: ${responseText}`);
    
    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      console.log(`✅ Service is healthy. IBKR Status: ${result.ibkr_status}`);
      return result;
    } else {
      console.error(`❌ Service health check failed: ${responseText}`);
      return null;
    }
    
  } catch (error) {
    console.error(`💥 Health check error: ${error.message}`);
    return null;
  }
}

/**
 * Calendar event trigger function
 * Set this up as a trigger in Google Apps Script
 */
function onCalendarEvent(eventTitle, eventDescription = '') {
  try {
    console.log(`📅 Calendar event triggered: ${eventTitle}`);
    
    // Parse trade details from calendar event
    const tradeDetails = parseTradeFromCalendarEvent(eventTitle, eventDescription);
    
    if (tradeDetails) {
      console.log(`📊 Parsed trade details:`, tradeDetails);
      return executeTrade(tradeDetails.symbol, tradeDetails.action, tradeDetails.quantity);
    } else {
      console.log('ℹ️ Calendar event does not contain trade instructions');
      return null;
    }
    
  } catch (error) {
    console.error(`💥 Calendar event handler error: ${error.message}`);
    throw error;
  }
}

/**
 * Parse trade instructions from calendar event title/description
 * Supports formats like:
 * - "BUY 5 AAPL"
 * - "SELL 10 BYD"
 * - "Trade: BUY 1 TSLA"
 */
function parseTradeFromCalendarEvent(title, description = '') {
  const text = `${title} ${description}`.toUpperCase();
  
  // Pattern to match: BUY/SELL [quantity] [symbol]
  const tradePattern = /\b(BUY|SELL)\s+(\d+)\s+([A-Z]{1,5})\b/;
  const match = text.match(tradePattern);
  
  if (match) {
    return {
      action: match[1],
      quantity: parseInt(match[2]),
      symbol: match[3]
    };
  }
  
  // Alternative pattern: [symbol] BUY/SELL [quantity]
  const altPattern = /\b([A-Z]{1,5})\s+(BUY|SELL)\s+(\d+)\b/;
  const altMatch = text.match(altPattern);
  
  if (altMatch) {
    return {
      symbol: altMatch[1],
      action: altMatch[2],
      quantity: parseInt(altMatch[3])
    };
  }
  
  // Simple pattern: just BUY/SELL with default symbol and quantity
  const simplePattern = /\b(BUY|SELL)\b/;
  const simpleMatch = text.match(simplePattern);
  
  if (simpleMatch) {
    return {
      action: simpleMatch[1],
      quantity: CONFIG.DEFAULT_QUANTITY,
      symbol: CONFIG.DEFAULT_SYMBOL
    };
  }
  
  return null;
}

/**
 * Send email notification
 */
function sendEmailNotification(subject, message, details = null) {
  try {
    if (!CONFIG.EMAIL_RECIPIENT) {
      console.log('📧 Email notifications disabled (no recipient configured)');
      return;
    }
    
    let emailBody = message;
    
    if (details) {
      emailBody += '\n\nDetails:\n' + JSON.stringify(details, null, 2);
    }
    
    emailBody += '\n\n---\nSent from IBKR Trading Bot Google Apps Script';
    
    MailApp.sendEmail({
      to: CONFIG.EMAIL_RECIPIENT,
      subject: `🤖 IBKR Trading Bot: ${subject}`,
      body: emailBody
    });
    
    console.log(`📧 Email notification sent to ${CONFIG.EMAIL_RECIPIENT}`);
    
  } catch (error) {
    console.error(`💥 Failed to send email notification: ${error.message}`);
  }
}

/**
 * Manual test functions - call these from the Apps Script editor
 */

function testBuyBYD() {
  return executeTrade('BYD', 'BUY', 1);
}

function testSellBYD() {
  return executeTrade('BYD', 'SELL', 1);
}

function testHealthCheck() {
  return testServiceHealth();
}

function testCalendarParser() {
  // Test different calendar event formats
  const testEvents = [
    'BUY 5 AAPL',
    'SELL 10 BYD',
    'Trade: BUY 1 TSLA',
    'AAPL BUY 3',
    'Just BUY',
    'Random meeting title'
  ];
  
  testEvents.forEach(event => {
    const result = parseTradeFromCalendarEvent(event);
    console.log(`"${event}" -> ${JSON.stringify(result)}`);
  });
}

/**
 * Calendar Trigger Setup Functions
 * Run installTradingTriggers() once to set up automatic calendar-driven trading
 */

/**
 * Install all required triggers for calendar-driven trading
 */
function installTradingTriggers() {
  try {
    console.log('🔧 Installing trading triggers...');
    
    // Remove any existing triggers first
    removeExistingTriggers();
    
    // Install calendar event trigger
    const calendarTrigger = ScriptApp.newTrigger('onCalendarEventUpdated')
      .forUserCalendar(Session.getActiveUser().getEmail())
      .onEventUpdated()
      .create();
    
    // Install time-based trigger (checks every 5 minutes for upcoming events)
    const timeTrigger = ScriptApp.newTrigger('checkUpcomingTradingEvents')
      .timeBased()
      .everyMinutes(5)
      .create();
    
    console.log('✅ Trading triggers installed successfully!');
    console.log(`📅 Calendar trigger ID: ${calendarTrigger.getUniqueId()}`);
    console.log(`⏰ Time trigger ID: ${timeTrigger.getUniqueId()}`);
    
    return {
      calendarTriggerId: calendarTrigger.getUniqueId(),
      timeTriggerId: timeTrigger.getUniqueId(),
      status: 'success'
    };
    
  } catch (error) {
    console.error('❌ Failed to install triggers:', error);
    throw error;
  }
}

/**
 * Calendar event updated trigger handler
 */
function onCalendarEventUpdated(e) {
  try {
    console.log('📅 Calendar event updated trigger fired');
    
    // Get recent events that might contain trading instructions
    const events = getRecentTradingEvents();
    
    events.forEach(event => {
      const title = event.getTitle();
      const description = event.getDescription();
      
      console.log(`🔍 Checking event: "${title}"`);
      
      // Parse and execute if it contains trading instructions
      const tradeDetails = parseTradeFromCalendarEvent(title, description);
      if (tradeDetails) {
        console.log(`📊 Found trading event: ${JSON.stringify(tradeDetails)}`);
        executeTrade(tradeDetails.symbol, tradeDetails.action, tradeDetails.quantity);
      }
    });
    
  } catch (error) {
    console.error('💥 Calendar event trigger error:', error);
  }
}

/**
 * Time-based trigger handler with duplicate prevention
 */
function checkUpcomingTradingEvents() {
  try {
    console.log('⏰ Checking for upcoming trading events...');
    
    // Look for events starting in the next 2 minutes (not ongoing events)
    const now = new Date();
    const soon = new Date(now.getTime() + 2 * 60 * 1000);
    
    const calendar = CalendarApp.getDefaultCalendar();
    const upcomingEvents = calendar.getEvents(now, soon);
    
    upcomingEvents.forEach(event => {
      const title = event.getTitle();
      const description = event.getDescription();
      const startTime = event.getStartTime();
      const eventId = event.getId();
      
      // Only process events that are actually starting soon (not ongoing)
      const timeDiff = startTime.getTime() - now.getTime();
      if (timeDiff > 2 * 60 * 1000) {
        return; // Event is too far in the future
      }
      
      const tradeDetails = parseTradeFromCalendarEvent(title, description);
      if (tradeDetails) {
        // Check if we've already executed this event
        if (hasEventBeenExecuted(eventId)) {
          console.log(`⏭️ Skipping already executed event: ${title}`);
          return;
        }
        
        console.log(`📈 Executing scheduled trade: ${title} at ${startTime}`);
        
        // Mark event as executed BEFORE calling executeTrade
        markEventAsExecuted(eventId, title);
        
        executeTrade(tradeDetails.symbol, tradeDetails.action, tradeDetails.quantity);
      }
    });
    
  } catch (error) {
    console.error('💥 Time-based trigger error:', error);
  }
}

/**
 * Get recent calendar events that might contain trading instructions
 */
function getRecentTradingEvents() {
  const calendar = CalendarApp.getDefaultCalendar();
  const now = new Date();
  const past = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  const future = new Date(now.getTime() + 24 * 60 * 60 * 1000);
  
  const events = calendar.getEvents(past, future);
  
  return events.filter(event => {
    const text = `${event.getTitle()} ${event.getDescription()}`.toUpperCase();
    return text.includes('BUY') || text.includes('SELL') || text.includes('TRADE');
  });
}

/**
 * Remove existing triggers to avoid duplicates
 */
function removeExistingTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  
  triggers.forEach(trigger => {
    const handlerFunction = trigger.getHandlerFunction();
    if (handlerFunction === 'onCalendarEventUpdated' || 
        handlerFunction === 'checkUpcomingTradingEvents') {
      ScriptApp.deleteTrigger(trigger);
      console.log(`🗑️ Removed existing trigger: ${handlerFunction}`);
    }
  });
}

/**
 * List all current triggers
 */
function listCurrentTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  
  console.log('📋 Current triggers:');
  triggers.forEach(trigger => {
    const type = trigger.getTriggerSource();
    const handler = trigger.getHandlerFunction();
    const id = trigger.getUniqueId();
    
    console.log(`  - ${handler} (${type}) - ID: ${id}`);
  });
  
  return triggers;
}

/**
 * Execution tracking functions to prevent duplicate trades
 */

/**
 * Check if an event has already been executed
 */
function hasEventBeenExecuted(eventId) {
  try {
    const properties = PropertiesService.getScriptProperties();
    const executedEvents = properties.getProperty('EXECUTED_EVENTS');
    
    if (!executedEvents) {
      return false;
    }
    
    const executedList = JSON.parse(executedEvents);
    return executedList.includes(eventId);
    
  } catch (error) {
    console.error('Error checking execution status:', error);
    return false; // If we can't check, allow execution (fail safe)
  }
}

/**
 * Mark an event as executed
 */
function markEventAsExecuted(eventId, eventTitle) {
  try {
    const properties = PropertiesService.getScriptProperties();
    let executedEvents = properties.getProperty('EXECUTED_EVENTS');
    
    let executedList = [];
    if (executedEvents) {
      executedList = JSON.parse(executedEvents);
    }
    
    // Add this event to the executed list
    if (!executedList.includes(eventId)) {
      executedList.push(eventId);
      
      // Keep only the last 100 executed events to prevent storage bloat
      if (executedList.length > 100) {
        executedList = executedList.slice(-100);
      }
      
      properties.setProperty('EXECUTED_EVENTS', JSON.stringify(executedList));
      console.log(`✅ Marked event as executed: ${eventTitle} (ID: ${eventId})`);
    }
    
  } catch (error) {
    console.error('Error marking event as executed:', error);
  }
}

/**
 * Clear execution history (for testing/cleanup)
 */
function clearExecutionHistory() {
  try {
    const properties = PropertiesService.getScriptProperties();
    properties.deleteProperty('EXECUTED_EVENTS');
    console.log('🗑️ Execution history cleared');
  } catch (error) {
    console.error('Error clearing execution history:', error);
  }
}

/**
 * View execution history
 */
function viewExecutionHistory() {
  try {
    const properties = PropertiesService.getScriptProperties();
    const executedEvents = properties.getProperty('EXECUTED_EVENTS');
    
    if (!executedEvents) {
      console.log('📋 No execution history found');
      return [];
    }
    
    const executedList = JSON.parse(executedEvents);
    console.log(`📋 Execution history (${executedList.length} events):`);
    executedList.forEach((eventId, index) => {
      console.log(`  ${index + 1}. ${eventId}`);
    });
    
    return executedList;
    
  } catch (error) {
    console.error('Error viewing execution history:', error);
    return [];
  }
}
