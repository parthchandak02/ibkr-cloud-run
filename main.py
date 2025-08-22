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
            # Strip any whitespace/newlines from base64 content
            base64_content = base64_content.strip()
            pem_content = base64.b64decode(base64_content).decode('utf-8')
            temp_file = f"/tmp/{temp_filename}"
            with open(temp_file, 'w') as f:
                f.write(pem_content)
            return temp_file
        return None

def get_env_var_clean(var_name: str):
    """Get environment variable and strip any whitespace/newlines"""
    value = os.getenv(var_name)
    return value.strip() if value else None

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
                # Clean all OAuth values to remove whitespace/newlines
                oauth_config = OAuth1aConfig(
                    access_token=get_env_var_clean('IBIND_OAUTH1A_ACCESS_TOKEN'),
                    access_token_secret=get_env_var_clean('IBIND_OAUTH1A_ACCESS_TOKEN_SECRET'),
                    consumer_key=get_env_var_clean('IBIND_OAUTH1A_CONSUMER_KEY'),
                    dh_prime=get_env_var_clean('IBIND_OAUTH1A_DH_PRIME'),
                    encryption_key_fp=encryption_key_fp,
                    signature_key_fp=signature_key_fp,
                    realm=get_env_var_clean('IBIND_OAUTH1A_REALM') or 'limited_poa'
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
    webhook_url = get_env_var_clean("DISCORD_WEBHOOK_URL")
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
    """Enhanced health check endpoint with detailed status reporting"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(UTC),
        "services": {}
    }
    
    # Test Discord notification (but don't fail health check if it fails)
    discord_status = test_discord_connection()
    health_status["services"]["discord"] = discord_status
    
    # Test IBKR connection with detailed error reporting
    ibkr_status = test_ibkr_connection()
    health_status["services"]["ibkr"] = ibkr_status
    
    # Overall system health
    all_critical_services_ok = (
        ibkr_status["status"] in ["connected", "initialized"] and
        discord_status["status"] in ["connected", "configured"]
    )
    
    if not all_critical_services_ok:
        health_status["status"] = "degraded"
    
    return health_status

def test_discord_connection():
    """Test Discord webhook connection"""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return {
            "status": "not_configured",
            "message": "Discord webhook URL not set"
        }
    
    try:
        # Don't actually send a notification during health check
        # Just validate the URL format
        if webhook_url.startswith("https://discord.com/api/webhooks/"):
            return {
                "status": "configured",
                "message": "Discord webhook URL configured"
            }
        else:
            return {
                "status": "invalid_config",
                "message": "Discord webhook URL format invalid"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Discord webhook test failed: {str(e)}"
        }

def test_ibkr_connection():
    """Test IBKR connection with detailed error reporting"""
    # Check if OAuth is enabled
    if not os.getenv("IBIND_USE_OAUTH", "").lower() == "true":
        return {
            "status": "not_configured", 
            "message": "OAuth not enabled (IBIND_USE_OAUTH=false)"
        }
    
    # Check if all required OAuth credentials are present
    required_oauth_vars = [
        'IBIND_OAUTH1A_ACCESS_TOKEN',
        'IBIND_OAUTH1A_ACCESS_TOKEN_SECRET', 
        'IBIND_OAUTH1A_CONSUMER_KEY',
        'IBIND_OAUTH1A_DH_PRIME'
    ]
    
    missing_vars = []
    for var in required_oauth_vars:
        if not get_env_var_clean(var):
            missing_vars.append(var)
    
    if missing_vars:
        return {
            "status": "missing_credentials",
            "message": f"Missing OAuth credentials: {', '.join(missing_vars)}"
        }
    
    # Try to initialize the client
    try:
        client = get_ibkr_client()
        if not client:
            return {
                "status": "initialization_failed",
                "message": "Failed to initialize IBKR client"
            }
        
        # Client initialized successfully - test a lightweight endpoint
        try:
            # Use a lightweight test that doesn't require full authentication
            # If client object exists, OAuth config was successful
            return {
                "status": "initialized",
                "message": "IBKR OAuth client initialized successfully",
                "note": "Full API connectivity requires active IBKR session"
            }
        except Exception as api_error:
            return {
                "status": "auth_error",
                "message": f"IBKR API call failed: {str(api_error)[:100]}...",
                "note": "Client initialized but API calls failing"
            }
            
    except Exception as init_error:
        error_msg = str(init_error)
        
        # Provide specific error categorization
        if "Invalid leading whitespace" in error_msg:
            return {
                "status": "oauth_header_error",
                "message": "OAuth header formatting issue - credentials may contain whitespace",
                "fix": "Check OAuth tokens for trailing newlines/whitespace"
            }
        elif "401" in error_msg or "Unauthorized" in error_msg:
            return {
                "status": "auth_failed", 
                "message": "IBKR authentication failed - invalid credentials",
                "fix": "Verify OAuth credentials are correct and active"
            }
        elif "connection" in error_msg.lower():
            return {
                "status": "connection_failed",
                "message": "Network connection to IBKR failed",
                "fix": "Check network connectivity and IBKR service status"
            }
        else:
            return {
                "status": "unknown_error",
                "message": f"IBKR initialization failed: {error_msg[:100]}...",
                "fix": "Check logs for detailed error information"
            }

@app.post("/trade")
async def execute_trade(trade_request: TradeRequest):
    """Execute a trade order"""
    try:
        symbol = trade_request.symbol.upper()
        action = trade_request.action.upper()
        quantity = trade_request.quantity or int(os.getenv("DEFAULT_QUANTITY", 1))
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
