"""
Webhook utilities for the Codegen API client.

This module contains classes for handling webhook events.
"""

import hmac
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional

from codegen.models.webhooks import WebhookEvent
from codegen.exceptions.api_exceptions import WebhookError

# Configure logging
logger = logging.getLogger(__name__)


class WebhookHandler:
    """Handles webhook events from the Codegen API."""
    
    def __init__(self, webhook_secret: Optional[str] = None):
        """Initialize the webhook handler.
        
        Args:
            webhook_secret: Secret key for verifying webhook signatures.
        """
        self.webhook_secret = webhook_secret
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.middleware: List[Callable] = []
    
    def register_handler(self, event_type: str, handler: Callable) -> Callable:
        """Register a handler for a specific event type.
        
        Args:
            event_type: The type of event to handle.
            handler: Function to call when the event is received.
            
        Returns:
            The handler function for chaining.
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event type: {event_type}")
        return handler
    
    def register_middleware(self, middleware: Callable) -> Callable:
        """Register middleware to process webhook payloads.
        
        Args:
            middleware: Function to process the webhook payload.
            
        Returns:
            The middleware function for chaining.
        """
        self.middleware.append(middleware)
        logger.debug("Registered webhook middleware")
        return middleware
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify the webhook signature.
        
        Args:
            payload: The raw webhook payload.
            signature: The signature from the webhook header.
            
        Returns:
            True if the signature is valid, False otherwise.
        """
        if not self.webhook_secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            return True
        
        # Calculate expected signature
        expected_signature = hmac.new(
            key=self.webhook_secret.encode(),
            msg=payload.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(expected_signature, signature)
    
    def handle_webhook(self, payload: Dict[str, Any], signature: Optional[str] = None) -> None:
        """Handle a webhook event.
        
        Args:
            payload: The webhook payload.
            signature: The signature from the webhook header.
            
        Raises:
            WebhookError: If the webhook cannot be processed.
        """
        # Verify signature if provided
        if signature and not self.verify_signature(json.dumps(payload), signature):
            raise WebhookError("Invalid webhook signature")
        
        # Apply middleware
        processed_payload = payload
        for middleware_func in self.middleware:
            try:
                processed_payload = middleware_func(processed_payload)
            except Exception as e:
                logger.error(f"Error in webhook middleware: {e}")
                raise WebhookError(f"Middleware error: {str(e)}")
        
        # Extract event information
        event_type = processed_payload.get("event_type")
        if not event_type:
            raise WebhookError("Missing event_type in webhook payload")
        
        # Create webhook event
        webhook_event = WebhookEvent(
            event_type=event_type,
            data=processed_payload.get("data", {}),
            timestamp=datetime.fromisoformat(processed_payload.get("timestamp", datetime.now().isoformat())),
            signature=signature,
        )
        
        # Call handlers
        handlers = self.event_handlers.get(event_type, [])
        if not handlers:
            logger.warning(f"No handlers registered for event type: {event_type}")
            return
        
        for handler in handlers:
            try:
                handler(processed_payload)
            except Exception as e:
                logger.error(f"Error in webhook handler for {event_type}: {e}")
                # Continue processing other handlers
        
        logger.info(f"Processed webhook event: {event_type}")
    
    def clear_handlers(self) -> None:
        """Clear all registered event handlers."""
        self.event_handlers.clear()
        logger.debug("Cleared all webhook handlers")
    
    def clear_middleware(self) -> None:
        """Clear all registered middleware."""
        self.middleware.clear()
        logger.debug("Cleared all webhook middleware")

