"""
Codegen Integration Layer

This layer handles all direct interactions with the Codegen API.
It provides a clean interface for the business logic layer while
handling authentication, caching, error handling, and data transformation.

Based on the enhanced SDK architecture from PR 8.
"""

from .codegen_client import CodegenClient
from .auth_manager import AuthManager
from .cache_manager import CacheManager
from .data_models import *
from .error_handling import CodegenAPIError, CodegenConnectionError, CodegenAuthError

__all__ = [
    'CodegenClient',
    'AuthManager', 
    'CacheManager',
    'CodegenAPIError',
    'CodegenConnectionError',
    'CodegenAuthError'
]

