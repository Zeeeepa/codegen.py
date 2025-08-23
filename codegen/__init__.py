"""
Codegen API - Python client for the Codegen Agent API.
"""

__version__ = "0.1.0"

# Import main components for easier access
from codegen_api import (
    CodegenClient,
    ClientConfig,
    CodegenAPIError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    NetworkError,
)

# Import from config module
from codegen.config.client_config import ClientConfig, ConfigPresets

