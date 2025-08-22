"""
IBKR Trading Bot - FastAPI Application

A production-ready trading bot for Interactive Brokers using the Voyz ibind library.
Supports OAuth 1.0a authentication and can be deployed to Google Cloud Run.
"""

import os
from datetime import datetime, UTC
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from ibind import ibind_logs_initialize

# Import our organized modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ibkr_trading_bot.config import get_settings
from ibkr_trading_bot.models import TradeRequest, TradeResponse, HealthResponse
from ibkr_trading_bot.ibkr_client import IBKRClientManager
from ibkr_trading_bot.notifications import discord_notifier

# Load environment variables (local development only)
if os.path.exists("config.env"):
    load_dotenv("config.env")
    print("📁 Loaded local config.env")
else:
    print("☁️ Running in production - using environment variables")

# Initialize ibind logging
ibind_logs_initialize(log_to_file=False)

# Initialize FastAPI app
app = FastAPI(
    title="IBKR Trading Bot",
    description="A FastAPI-based trading bot for Interactive Brokers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize services
settings = get_settings()
ibkr_manager = IBKRClientManager()


@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint returning basic service information."""
    return {
        "message": "IBKR Trading Bot is running!",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC),
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Health check endpoint with comprehensive service status."""
    try:
        # Test Discord notification
        discord_notifier.send_notification("Health check - Trading bot is online", "info")
        
        # Test IBKR connection
        client = ibkr_manager.get_client()
        ibkr_status = "connected" if client else "failed"
        
        if client:
            try:
                # Test connection by getting portfolio accounts
                accounts = client.portfolio_accounts().data
                print(f"✅ IBKR connected successfully. Found {len(accounts)} accounts.")
                ibkr_status = f"connected ({len(accounts)} accounts)"
            except Exception as e:
                print(f"❌ IBKR connection test failed: {e}")
                ibkr_status = f"auth_error: {str(e)[:50]}..."
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(UTC),
            discord_configured=bool(settings.discord_webhook_url),
            ibkr_configured=bool(settings.ibind_oauth1a_consumer_key),
            ibkr_status=ibkr_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/trade", response_model=TradeResponse, summary="Place a trade")
async def place_trade(request: TradeRequest):
    """Endpoint to place a trade (dry run or live)."""
    symbol = request.symbol.upper()
    action = request.action.upper()
    quantity = request.quantity if request.quantity is not None else settings.default_quantity
    dry_run = settings.dry_run
    
    # Validate action
    if action not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Action must be 'BUY' or 'SELL'")
    
    # Look up the contract ID (conid) for the symbol
    conid = ibkr_manager.lookup_stock_conid(symbol)
    
    if dry_run:
        if conid:
            message = f"🔍 DRY RUN: Would {action} {quantity} shares of {symbol} (conid: {conid})"
            status = "info"
        else:
            message = f"❌ DRY RUN FAILED: Could not find contract for {symbol}"
            status = "warning"
        
        discord_notifier.send_notification(message, status)
        
        return TradeResponse(
            status="simulated",
            message=message,
            symbol=symbol,
            action=action,
            quantity=quantity,
            conid=conid,
            timestamp=datetime.now(UTC)
        )
    
    # TODO: Implement actual IBKR trading logic here
    message = f"❌ Live trading not yet implemented. Set DRY_RUN=true for testing."
    discord_notifier.send_notification(message, "warning")
    
    raise HTTPException(status_code=501, detail="Live trading not yet implemented.")


if __name__ == "__main__":
    import uvicorn
    # Use port from settings, fallback to environment variable
    port = int(os.getenv("PORT", settings.port))
    uvicorn.run(app, host="0.0.0.0", port=port)
