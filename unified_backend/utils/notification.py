"""
Notification utilities for the Unified Backend.
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

class NotificationManager:
    """Notification manager for the Codegen UI."""
    
    def __init__(self):
        """Initialize the notification manager."""
        self.notifications = []
        self.callbacks = []
        self.lock = threading.Lock()
    
    def add_notification(self, notification: Dict[str, Any]) -> None:
        """
        Add a notification.
        
        Args:
            notification: Notification data
        """
        with self.lock:
            self.notifications.append(notification)
            
        # Call callbacks
        for callback in self.callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Error in notification callback: {e}")
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """
        Get all notifications.
        
        Returns:
            List of notifications
        """
        with self.lock:
            return self.notifications.copy()
    
    def clear_notifications(self) -> None:
        """Clear all notifications."""
        with self.lock:
            self.notifications = []
    
    def register_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback for new notifications.
        
        Args:
            callback: Callback function
        """
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Unregister a callback.
        
        Args:
            callback: Callback function
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_polling(self, api_client, org_id: str, interval: int = 60) -> None:
        """
        Start polling for new agent run notifications.
        
        Args:
            api_client: API client
            org_id: Organization ID
            interval: Polling interval in seconds
        """
        def _poll_thread():
            last_check = time.time()
            
            while True:
                try:
                    # Get agent runs
                    runs = api_client.list_agent_runs(org_id)
                    
                    # Check for completed or failed runs
                    for run in runs.get("items", []):
                        if run.get("status") in ["COMPLETED", "ERROR"]:
                            # Check if run was updated since last check
                            updated_at = run.get("updated_at")
                            if updated_at and updated_at > last_check:
                                # Add notification
                                self.add_notification({
                                    "type": "agent_run",
                                    "status": run.get("status"),
                                    "id": run.get("id"),
                                    "prompt": run.get("prompt"),
                                    "timestamp": time.time()
                                })
                    
                    # Update last check time
                    last_check = time.time()
                    
                    # Sleep
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Error polling for notifications: {e}")
                    time.sleep(interval)
        
        # Start polling thread
        threading.Thread(target=_poll_thread, daemon=True).start()

