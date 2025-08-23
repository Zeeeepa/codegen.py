"""
Exceptions for the Codegen API.

This package contains custom exception classes used by the Codegen API client.
"""

from codegen.exceptions.api_exceptions import (
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

__all__ = [
    "ValidationError",
    "CodegenAPIError",
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError",
    "ConflictError",
    "ServerError",
    "TimeoutError",
    "NetworkError",
    "WebhookError",
    "BulkOperationError",
]

