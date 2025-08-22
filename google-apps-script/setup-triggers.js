/**
 * Calendar Trigger Setup for IBKR Trading Bot
 * 
 * This script sets up automatic calendar event triggers for trading automation.
 * Run this once to install triggers for calendar-driven trading.
 */

/**
 * Install all required triggers for calendar-driven trading
 * Call this function once to set up automation
 */
function installTradingTriggers() {
  try {
    console.log('🔧 Installing trading triggers...');
    
    // Remove any existing triggers first to avoid duplicates
    removeExistingTriggers();
    
    // Option 1: Calendar event trigger (fires when events are created/modified)
    const calendarTrigger = installCalendarEventTrigger();
    
    // Option 2: Time-driven trigger (checks for events about to start)
    const timeTrigger = installTimeBasedTrigger();
    
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
 * Install calendar event trigger
 * Fires when calendar events are created, modified, or deleted
 */
function installCalendarEventTrigger() {
  try {
    const trigger = ScriptApp.newTrigger('onCalendarEventUpdated')
      .forUserCalendar(Session.getActiveUser().getEmail())
      .onEventUpdated()
      .create();
    
    console.log('📅 Calendar event trigger installed');
    return trigger;
    
  } catch (error) {
    console.error('❌ Failed to install calendar trigger:', error);
    throw error;
  }
}

/**
 * Install time-based trigger
 * Checks every minute for events about to start
 */
function installTimeBasedTrigger() {
  try {
    const trigger = ScriptApp.newTrigger('checkUpcomingTradingEvents')
      .timeBased()
      .everyMinutes(1)
      .create();
    
    console.log('⏰ Time-based trigger installed (every 1 minute)');
    return trigger;
    
  } catch (error) {
    console.error('❌ Failed to install time trigger:', error);
    throw error;
  }
}

/**
 * Calendar event updated trigger handler
 * Fires when ANY calendar event is created/modified/deleted
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
 * Time-based trigger handler
 * Checks for events starting soon that contain trading instructions
 */
function checkUpcomingTradingEvents() {
  try {
    console.log('⏰ Checking for upcoming trading events...');
    
    // Look for events starting in the next 2 minutes
    const now = new Date();
    const soon = new Date(now.getTime() + 2 * 60 * 1000); // 2 minutes from now
    
    const calendar = CalendarApp.getDefaultCalendar();
    const upcomingEvents = calendar.getEvents(now, soon);
    
    upcomingEvents.forEach(event => {
      const title = event.getTitle();
      const description = event.getDescription();
      const startTime = event.getStartTime();
      
      // Check if this event contains trading instructions
      const tradeDetails = parseTradeFromCalendarEvent(title, description);
      if (tradeDetails) {
        console.log(`📈 Executing scheduled trade: ${title} at ${startTime}`);
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
  const past = new Date(now.getTime() - 24 * 60 * 60 * 1000); // 24 hours ago
  const future = new Date(now.getTime() + 24 * 60 * 60 * 1000); // 24 hours from now
  
  // Get all events from past 24h to next 24h
  const events = calendar.getEvents(past, future);
  
  // Filter for events that might contain trading keywords
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
  
  return triggers.map(t => ({
    id: t.getUniqueId(),
    handler: t.getHandlerFunction(),
    source: t.getTriggerSource(),
    sourceString: t.getTriggerSourceId()
  }));
}

/**
 * Remove all triggers (for cleanup)
 */
function removeAllTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  
  triggers.forEach(trigger => {
    ScriptApp.deleteTrigger(trigger);
    console.log(`🗑️ Removed trigger: ${trigger.getHandlerFunction()}`);
  });
  
  console.log('✅ All triggers removed');
}

/**
 * Test the calendar parsing function
 */
function testCalendarParsing() {
  const testEvents = [
    'BUY 1 BYD',
    'SELL 5 AAPL',
    'Trade: BUY 10 TSLA',
    'Meeting with client',
    'BYD BUY 3',
    'Just BUY today'
  ];
  
  console.log('🧪 Testing calendar event parsing:');
  testEvents.forEach(eventTitle => {
    const result = parseTradeFromCalendarEvent(eventTitle);
    console.log(`"${eventTitle}" → ${JSON.stringify(result)}`);
  });
}
