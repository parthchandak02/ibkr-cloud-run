"""Notification services for the trading bot."""

import os
import requests
import urllib3
from datetime import datetime, UTC
from typing import Literal
from .config import get_settings

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NotificationStatus = Literal["info", "warning", "error", "success"]


class DiscordNotifier:
    """Discord webhook notification service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.webhook_url = self.settings.discord_webhook_url
    
    def send_notification(self, message: str, status: NotificationStatus = "info") -> None:
        """Send notification to Discord webhook."""
        if not self.webhook_url:
            print(f"No Discord webhook configured. Message: {message}")
            return

        colors = {
            "info": 3447003,
            "warning": 16776960,
            "error": 15548997,
            "success": 3066993
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
            response = requests.post(self.webhook_url, json=payload, verify=verify_ssl)
            response.raise_for_status()
            print(f"Discord notification sent: {message}")
        except Exception as e:
            print(f"Failed to send Discord notification: {e}")


# Global notifier instance
discord_notifier = DiscordNotifier()
