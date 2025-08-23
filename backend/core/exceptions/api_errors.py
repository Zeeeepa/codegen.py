"""
API error exceptions for the Codegen application.

This module provides exception classes for API errors.
"""

from typing import Optional, Dict, Any


class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the API error.
        
        Args:
            message: The error message.
            status_code: The HTTP status code.
            response: The raw response data.
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class AuthenticationError(APIError):
    """Exception raised for authentication errors."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: Optional[int] = 401,
        response: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the authentication error.
        
        Args:
            message: The error message.
            status_code: The HTTP status code.
            response: The raw response data.
        """
        super().__init__(message, status_code, response)


class RateLimitError(APIError):
    """Exception raised for rate limit errors."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: Optional[int] = 429,
        response: Optional[Dict[str, Any]] = None,
        reset_at: Optional[int] = None,
    ):
        """Initialize the rate limit error.
        
        Args:
            message: The error message.
            status_code: The HTTP status code.
            response: The raw response data.
            reset_at: The timestamp when the rate limit resets.
        """
        self.reset_at = reset_at
        super().__init__(message, status_code, response)

