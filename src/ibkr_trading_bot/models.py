"""Pydantic models for API requests and responses."""

from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class TradeRequest(BaseModel):
    """Request model for placing a trade."""
    symbol: str = Field(..., description="Stock symbol to trade")
    action: Literal["BUY", "SELL"] = Field(..., description="Trade action")
    quantity: Optional[int] = Field(None, description="Number of shares to trade")


class TradeResponse(BaseModel):
    """Response model for trade execution."""
    status: str = Field(..., description="Trade status")
    message: str = Field(..., description="Human-readable message")
    symbol: str = Field(..., description="Stock symbol")
    action: str = Field(..., description="Trade action")
    quantity: int = Field(..., description="Number of shares")
    conid: Optional[dict] = Field(None, description="Contract ID lookup result")
    timestamp: datetime = Field(..., description="Execution timestamp")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    discord_configured: bool = Field(..., description="Discord webhook status")
    ibkr_configured: bool = Field(..., description="IBKR configuration status")
    ibkr_status: str = Field(..., description="IBKR connection status")
