"""
Base client for the Codegen API.

This module contains the base client class for the Codegen API.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List, Callable, Union

from backend.core.config.client_config import ClientConfig
from backend.core.utils.caching import ResponseCache
from backend.core.utils.metrics import MetricsTracker
from backend.core.utils.webhooks import WebhookHandler
from backend.core.exceptions.api_exceptions import (
    ValidationError,
    CodegenAPIError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ConflictError,
    ServerError,
    TimeoutError,
    NetworkError,
    WebhookError,
    BulkOperationError,
)

# Configure logging
logger = logging.getLogger(__name__)


class BaseCodegenClient:
    """Base client for the Codegen API."""
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """Initialize the base client.
        
        Args:
            config: Client configuration. If None, uses default configuration.
        """
        self.config = config or ClientConfig()
        
        # Set up caching if enabled
        self.cache = ResponseCache(
            max_size=self.config.max_cache_size,
            ttl=self.config.cache_ttl,
        ) if self.config.use_cache else None
        
        # Set up metrics tracking
        self.metrics = MetricsTracker()
        
        # Set up webhook handler if secret is configured
        self.webhook_handler = WebhookHandler(self.config.webhook_secret) if self.config.webhook_secret else None
        
        logger.debug(f"Initialized BaseCodegenClient with base URL: {self.config.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.
        
        Returns:
            A dictionary of HTTP headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"codegen-python-client/{self._get_version()}",
        }
        
        # Add API token if available
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"
        
        # Add custom headers
        headers.update(self.config.headers)
        
        return headers
    
    def _get_version(self) -> str:
        """Get the client version.
        
        Returns:
            The client version string.
        """
        try:
            from backend import __version__
            return __version__
        except ImportError:
            return "0.1.0"
    
    def _validate_org_id(self, org_id: Union[int, str]) -> int:
        """Validate and convert organization ID.
        
        Args:
            org_id: Organization ID as int or string.
            
        Returns:
            Organization ID as int.
            
        Raises:
            ValidationError: If org_id is invalid.
        """
        try:
            return int(org_id)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid organization ID: {org_id}")
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID.
        
        Returns:
            A unique request ID string.
        """
        return str(uuid.uuid4())
    
    def _handle_bulk_operation(
        self,
        items: List[Any],
        operation: Callable,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """Handle a bulk operation with progress tracking.
        
        Args:
            items: List of items to process.
            operation: Function to call for each item.
            progress_callback: Function to call with progress updates.
            
        Returns:
            A dictionary with operation results.
        """
        results = []
        errors = []
        start_time = self._get_current_time()
        
        for i, item in enumerate(items):
            try:
                result = operation(item)
                results.append(result)
            except Exception as e:
                errors.append({
                    "index": i,
                    "item": item,
                    "error": str(e),
                })
            
            # Call progress callback if provided
            if progress_callback:
                progress_callback(i + 1, len(items))
        
        # Calculate statistics
        duration = self._get_current_time() - start_time
        total_items = len(items)
        successful_items = len(results)
        failed_items = len(errors)
        success_rate = successful_items / total_items if total_items > 0 else 0
        
        return {
            "total_items": total_items,
            "successful_items": successful_items,
            "failed_items": failed_items,
            "success_rate": success_rate,
            "duration_seconds": duration,
            "errors": errors,
            "results": results,
        }
    
    def _get_current_time(self) -> float:
        """Get the current time in seconds.
        
        Returns:
            Current time in seconds.
        """
        import time
        return time.time()
    
    def close(self) -> None:
        """Close the client and release resources."""
        logger.debug("Closing BaseCodegenClient")
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()
