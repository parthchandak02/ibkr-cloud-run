"""Configuration management for IBKR Trading Bot."""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Discord Configuration
    discord_webhook_url: Optional[str] = None
    
    # IBKR OAuth Configuration
    ibind_use_oauth: bool = True
    ibind_oauth1a_access_token: Optional[str] = None
    ibind_oauth1a_access_token_secret: Optional[str] = None
    ibind_oauth1a_consumer_key: Optional[str] = None
    ibind_oauth1a_dh_prime: Optional[str] = None
    ibind_oauth1a_encryption_key_fp: Optional[str] = None
    ibind_oauth1a_signature_key_fp: Optional[str] = None
    ibind_oauth1a_realm: str = "limited_poa"
    ibind_cacert: bool = False
    
    # Trading Configuration
    default_quantity: int = 1
    dry_run: bool = True
    
    # Server Configuration
    port: int = 8000
    
    class Config:
        env_file = "config.env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
