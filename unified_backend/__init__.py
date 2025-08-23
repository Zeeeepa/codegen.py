"""
Unified Backend for the Codegen UI.

This module provides a unified backend for the Codegen UI,
consolidating functionality from multiple existing implementations.
"""

from unified_backend.client import APIClient
from unified_backend.utils import Config
from unified_backend.utils.notification import NotificationManager
from unified_backend.utils.storage import Storage

__all__ = ["APIClient", "Config", "NotificationManager", "Storage"]

