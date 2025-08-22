import os
import requests
import urllib3
import base64
import tempfile
from datetime import datetime, UTC
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from ibind import IbkrClient, ibind_logs_initialize, StockQuery
from ibind.oauth.oauth1a import OAuth1aConfig
from typing import Optional

# Disable SSL warnings for development (fix Discord webhook SSL issue)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables (local development only)
if os.path.exists("config.env"):
    load_dotenv("config.env")
    print("📁 Loaded local config.env")
else:
    print("☁️ Running in production - using environment variables")

# Initialize ibind logging
ibind_logs_initialize(log_to_file=False)

app = FastAPI(title="IBKR Trading Bot", version="1.0.0")

# Request models
class TradeRequest(BaseModel):
    symbol: str
    action: str  # "BUY" or "SELL"
    quantity: Optional[int] = None

# Initialize IBKR client (we'll test this step by step)
ibkr_client = None

def get_pem_file_path(env_var_name: str, temp_filename: str):
    """Get PEM file path, handling both local files and base64-encoded secrets"""
    if os.path.exists("config.env"):
        # Local development - use direct file paths
        return os.getenv(env_var_name)
    else:
        # Production - decode base64 secret to temporary file
        base64_content = os.getenv(env_var_name)
        if base64_content:
            pem_content = base64.b64decode(base64_content).decode('utf-8')
            temp_file = f"/tmp/{temp_filename}"
            with open(temp_file, 'w') as f:
                f.write(pem_content)
            return temp_file
        return None

def get_ibkr_client():
    """Get or create IBKR client with OAuth 1.0a following ibind best practices"""
    global ibkr_client
    if ibkr_client is None:
        try:
            if os.getenv("IBIND_USE_OAUTH", "").lower() == "true":
                # Handle PEM files (local vs production)
                encryption_key_fp = get_pem_file_path('IBIND_OAUTH1A_ENCRYPTION_KEY_FP', 'encryption.pem')
                signature_key_fp = get_pem_file_path('IBIND_OAUTH1A_SIGNATURE_KEY_FP', 'signature.pem')
                
                # Create OAuth config explicitly (ibind doesn't auto-read env vars)
                oauth_config = OAuth1aConfig(
                    access_token=os.getenv('IBIND_OAUTH1A_ACCESS_TOKEN'),
                    access_token_secret=os.getenv('IBIND_OAUTH1A_ACCESS_TOKEN_SECRET'),
                    consumer_key=os.getenv('IBIND_OAUTH1A_CONSUMER_KEY'),
                    dh_prime=os.getenv('IBIND_OAUTH1A_DH_PRIME'),
                    encryption_key_fp=encryption_key_fp,
                    signature_key_fp=signature_key_fp,
                    realm=os.getenv('IBIND_OAUTH1A_REALM', 'limited_poa')
                )
                
                cacert = os.getenv('IBIND_CACERT', False)
                ibkr_client = IbkrClient(
                    cacert=cacert,
                    use_oauth=True,
                    oauth_config=oauth_config
                )
                print("✅ IBKR OAuth client initialized")
                
                # Set account_id following best practices
                accounts = ibkr_client.portfolio_accounts().data
                if accounts and len(accounts) > 0:
                    ibkr_client.account_id = accounts[0]['accountId']
                    print(f"✅ Account set: {ibkr_client.account_id}")
                
            else:
                print("❌ OAuth not enabled in config")
                return None
        except Exception as e:
            print(f"❌ Failed to initialize IBKR client: {e}")
            return None
    return ibkr_client

def lookup_stock_conid(symbol: str):
    """Look up contract ID (conid) for a stock symbol following ibind best practices"""
    client = get_ibkr_client()
    if not client:
        return None
    
    try:
        # For BYD, we need to specify the Hong Kong exchange
        # Following rest_03_stock_querying.py patterns
        if symbol.upper() == 'BYD':
            # BYD Company Limited trades on Hong Kong Stock Exchange as 1211.HK
            stock_query = StockQuery('1211', contract_conditions={'exchange': 'SEHK'})
            search_result = client.stock_conid_by_symbol(stock_query, default_filtering=False)
        else:
            # For other stocks, use default behavior
            search_result = client.stock_conid_by_symbol(symbol)
            
        if search_result and hasattr(search_result, 'data') and search_result.data:
            conid = search_result.data
            print(f"✅ Found conid for {symbol}: {conid}")
            return conid
        else:
            print(f"❌ No contract found for symbol: {symbol}")
            return None
    except Exception as e:
        print(f"❌ Error looking up {symbol}: {e}")
        return None

def send_discord_notification(message: str, status: str = "info"):
    """Send notification to Discord webhook"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print(f"No Discord webhook configured. Message: {message}")
        return
    
    # Color coding for different statuses
    colors = {
        "success": 0x00ff00,  # Green
        "error": 0xff0000,    # Red
        "info": 0x0099ff,     # Blue
        "warning": 0xffaa00   # Orange
    }
    
    embed = {
        "title": "🤖 Trading Bot Notification",
        "description": message,
        "color": colors.get(status, colors["info"]),
        "timestamp": datetime.now(UTC).isoformat()
    }
    
    payload = {"embeds": [embed]}
    
    try:
        # Use proper SSL verification in production, disable only in dev
        verify_ssl = not os.path.exists("config.env")  # Verify SSL in production
        response = requests.post(webhook_url, json=payload, verify=verify_ssl)
        response.raise_for_status()
        print(f"Discord notification sent: {message}")
    except Exception as e:
        print(f"Failed to send Discord notification: {e}")

@app.get("/")
async def root():
    return {"message": "IBKR Trading Bot is running!", "timestamp": datetime.now(UTC)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Discord notification
        send_discord_notification("Health check - Trading bot is online", "info")
        
        # Test IBKR connection
        client = get_ibkr_client()
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
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC),
            "discord_configured": bool(os.getenv("DISCORD_WEBHOOK_URL")),
            "ibkr_configured": bool(os.getenv("IBIND_OAUTH1A_CONSUMER_KEY")),
            "ibkr_status": ibkr_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/trade")
async def execute_trade(trade_request: TradeRequest):
    """Execute a trade order"""
    try:
        symbol = trade_request.symbol.upper()
        action = trade_request.action.upper()
        quantity = trade_request.quantity or int(os.getenv("DEFAULT_QUANTITY", 100))
        dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        
        # Validate action
        if action not in ["BUY", "SELL"]:
            raise HTTPException(status_code=400, detail="Action must be 'BUY' or 'SELL'")
        
        # Look up the contract ID (conid) for the symbol
        conid = lookup_stock_conid(symbol)
        
        if dry_run:
            if conid:
                message = f"🔍 DRY RUN: Would {action} {quantity} shares of {symbol} (conid: {conid})"
            else:
                message = f"❌ DRY RUN FAILED: Could not find contract for {symbol}"
            
            send_discord_notification(message, "info" if conid else "warning")
            
            return {
                "status": "simulated",
                "message": message,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "conid": conid,
                "timestamp": datetime.now(UTC)
            }
        
        # TODO: Implement actual IBKR trading logic here
        message = f"❌ Live trading not yet implemented. Set DRY_RUN=true for testing."
        send_discord_notification(message, "warning")
        
        raise HTTPException(status_code=501, detail="Live trading not yet implemented")
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"❌ Trade execution failed: {str(e)}"
        send_discord_notification(error_msg, "error")
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    # Use port 8080 for Cloud Run, 8000 for local development
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
