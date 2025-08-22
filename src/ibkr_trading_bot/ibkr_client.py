"""IBKR client management for trading operations."""

import os
import base64
import tempfile
from typing import Optional, Dict, Any
from ibind import IbkrClient, StockQuery
from ibind.oauth.oauth1a import OAuth1aConfig
from .config import get_settings


class IBKRClientManager:
    """Manages IBKR client lifecycle and operations."""
    
    def __init__(self):
        self.client: Optional[IbkrClient] = None
        self.settings = get_settings()
    
    def _get_pem_file_path(self, env_var_name: str, temp_filename: str) -> Optional[str]:
        """Get PEM file path, handling both local files and base64-encoded secrets."""
        if os.path.exists("config.env"):
            # Local development - use direct file paths
            return getattr(self.settings, env_var_name.lower().replace('ibind_oauth1a_', ''))
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
    
    def get_client(self) -> Optional[IbkrClient]:
        """Get or create IBKR client with OAuth 1.0a following ibind best practices."""
        if self.client is None:
            try:
                if self.settings.ibind_use_oauth:
                    # Handle PEM files (local vs production)
                    encryption_key_fp = self._get_pem_file_path(
                        'IBIND_OAUTH1A_ENCRYPTION_KEY_FP', 'encryption.pem'
                    )
                    signature_key_fp = self._get_pem_file_path(
                        'IBIND_OAUTH1A_SIGNATURE_KEY_FP', 'signature.pem'
                    )
                    
                    # Create OAuth config explicitly
                    oauth_config = OAuth1aConfig(
                        access_token=self.settings.ibind_oauth1a_access_token,
                        access_token_secret=self.settings.ibind_oauth1a_access_token_secret,
                        consumer_key=self.settings.ibind_oauth1a_consumer_key,
                        dh_prime=self.settings.ibind_oauth1a_dh_prime,
                        encryption_key_fp=encryption_key_fp,
                        signature_key_fp=signature_key_fp,
                        realm=self.settings.ibind_oauth1a_realm
                    )
                    
                    self.client = IbkrClient(
                        cacert=self.settings.ibind_cacert,
                        use_oauth=True,
                        oauth_config=oauth_config
                    )
                    print("✅ IBKR OAuth client initialized")
                    
                    # Set account_id following best practices
                    accounts = self.client.portfolio_accounts().data
                    if accounts and len(accounts) > 0:
                        self.client.account_id = accounts[0]['accountId']
                        print(f"✅ Account set: {self.client.account_id}")
                    
                else:
                    print("❌ OAuth not enabled in config")
                    return None
            except Exception as e:
                print(f"❌ Failed to initialize IBKR client: {e}")
                return None
        return self.client
    
    def lookup_stock_conid(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Look up contract ID (conid) for a stock symbol following ibind best practices."""
        client = self.get_client()
        if not client:
            return None
        
        try:
            # For BYD, we need to specify the Hong Kong exchange
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
