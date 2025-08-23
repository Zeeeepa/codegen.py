"""
Webhook models for the Codegen API.

This module contains dataclasses representing webhook events and related data.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class WebhookEvent:
    """Model for webhook events."""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    signature: Optional[str] = None

