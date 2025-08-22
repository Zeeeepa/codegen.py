"""
Codegen API Client Library

A Python client for interacting with the Codegen API.
"""

from codegen_client.client import CodegenClient
from codegen_client.exceptions import (
    CodegenApiError,
    CodegenAuthError,
    CodegenRateLimitError,
    CodegenResourceNotFoundError,
    CodegenValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "CodegenClient",
    "CodegenApiError",
    "CodegenAuthError",
    "CodegenRateLimitError",
    "CodegenResourceNotFoundError",
    "CodegenValidationError",
]

