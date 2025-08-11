"""
Error Handling for Codegen Integration Layer

Defines custom exceptions and error handling utilities for the integration layer.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class CodegenAPIError(Exception):
    """Base exception for Codegen API errors"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id
        
        # Log the error
        logger.error(f"CodegenAPIError: {message} (status: {status_code}, request_id: {request_id})")
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class CodegenAuthError(CodegenAPIError):
    """Authentication-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(f"Authentication Error: {message}", **kwargs)


class CodegenConnectionError(CodegenAPIError):
    """Connection-related errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(f"Connection Error: {message}", **kwargs)


class CodegenRateLimitError(CodegenAPIError):
    """Rate limiting errors"""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(f"Rate Limit Error: {message}", **kwargs)
        self.retry_after = retry_after


class CodegenValidationError(CodegenAPIError):
    """Data validation errors"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(f"Validation Error: {message}", **kwargs)
        self.field = field
        self.value = value


class CodegenNotFoundError(CodegenAPIError):
    """Resource not found errors"""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, status_code=404, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class CodegenPermissionError(CodegenAPIError):
    """Permission/authorization errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(f"Permission Error: {message}", status_code=403, **kwargs)


def handle_api_error(
    status_code: int,
    response_data: Dict[str, Any],
    request_id: Optional[str] = None
) -> CodegenAPIError:
    """
    Create appropriate exception based on API response.
    
    Args:
        status_code: HTTP status code
        response_data: Response data from API
        request_id: Optional request ID for tracking
    
    Returns:
        Appropriate CodegenAPIError subclass
    """
    
    # Extract error message from response
    error_message = "Unknown error"
    if isinstance(response_data, dict):
        error_message = (
            response_data.get("detail") or
            response_data.get("message") or
            response_data.get("error") or
            str(response_data)
        )
    elif isinstance(response_data, str):
        error_message = response_data
    
    # Create appropriate exception based on status code
    if status_code == 400:
        return CodegenValidationError(
            error_message,
            status_code=status_code,
            response_data=response_data,
            request_id=request_id
        )
    
    elif status_code == 401:
        return CodegenAuthError(
            error_message,
            status_code=status_code,
            response_data=response_data,
            request_id=request_id
        )
    
    elif status_code == 403:
        return CodegenPermissionError(
            error_message,
            status_code=status_code,
            response_data=response_data,
            request_id=request_id
        )
    
    elif status_code == 404:
        return CodegenNotFoundError(
            "Resource",
            status_code=status_code,
            response_data=response_data,
            request_id=request_id
        )
    
    elif status_code == 429:
        retry_after = None
        if isinstance(response_data, dict):
            retry_after = response_data.get("retry_after")
        
        return CodegenRateLimitError(
            error_message,
            retry_after=retry_after,
            status_code=status_code,
            response_data=response_data,
            request_id=request_id
        )
    
    else:
        return CodegenAPIError(
            error_message,
            status_code=status_code,
            response_data=response_data,
            request_id=request_id
        )


def is_retryable_error(error: Exception) -> bool:
    """
    Check if an error is retryable.
    
    Args:
        error: Exception to check
    
    Returns:
        True if the error is retryable
    """
    
    if isinstance(error, CodegenConnectionError):
        return True
    
    if isinstance(error, CodegenRateLimitError):
        return True
    
    if isinstance(error, CodegenAPIError):
        # Retry on server errors (5xx)
        if error.status_code and 500 <= error.status_code < 600:
            return True
        
        # Retry on specific client errors
        if error.status_code in [408, 429]:  # Timeout, Rate limit
            return True
    
    return False


def get_retry_delay(error: Exception, attempt: int) -> float:
    """
    Get retry delay for an error.
    
    Args:
        error: Exception that occurred
        attempt: Current attempt number (0-based)
    
    Returns:
        Delay in seconds
    """
    
    if isinstance(error, CodegenRateLimitError) and error.retry_after:
        return float(error.retry_after)
    
    # Exponential backoff with jitter
    base_delay = 2 ** attempt
    max_delay = 60  # Maximum 60 seconds
    
    return min(base_delay, max_delay)

