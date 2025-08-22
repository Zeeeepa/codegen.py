"""
Configuration management for the Codegen API client.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class CodegenConfig:
    """Configuration for the Codegen API client."""

    api_key: Optional[str] = None
    base_url: str = "https://api.codegen.com/v1"
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = "codegen-python-client"

    @classmethod
    def from_env(cls) -> "CodegenConfig":
        """
        Create a configuration object from environment variables.

        Environment variables:
            CODEGEN_API_KEY: API key for authentication
            CODEGEN_BASE_URL: Base URL for the API (default: https://api.codegen.com/v1)
            CODEGEN_TIMEOUT: Request timeout in seconds (default: 30)
            CODEGEN_MAX_RETRIES: Maximum number of retries for failed requests (default: 3)
            CODEGEN_USER_AGENT: User agent string (default: codegen-python-client)

        Returns:
            CodegenConfig: Configuration object with values from environment variables
        """
        return cls(
            api_key=os.environ.get("CODEGEN_API_KEY"),
            base_url=os.environ.get("CODEGEN_BASE_URL", cls.base_url),
            timeout=int(os.environ.get("CODEGEN_TIMEOUT", cls.timeout)),
            max_retries=int(os.environ.get("CODEGEN_MAX_RETRIES", cls.max_retries)),
            user_agent=os.environ.get("CODEGEN_USER_AGENT", cls.user_agent),
        )

