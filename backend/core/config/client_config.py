"""
Configuration for the Codegen API client.

This module contains classes for configuring the Codegen API client.
"""

import os
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)


class ConfigPresets(Enum):
    """Predefined configuration presets."""
    
    DEFAULT = {
        "base_url": "https://api.codegen.com/v1",
        "timeout": 60,
        "max_retries": 3,
        "retry_delay": 1,
        "retry_backoff": 2.0,
        "log_requests": False,
        "log_level": "INFO",
        "use_cache": True,
        "cache_ttl": 300,
        "max_cache_size": 100,
    }
    
    DEVELOPMENT = {
        "base_url": "http://localhost:8000/v1",
        "timeout": 120,
        "max_retries": 5,
        "retry_delay": 0.5,
        "retry_backoff": 1.5,
        "log_requests": True,
        "log_level": "DEBUG",
        "use_cache": False,
        "cache_ttl": 60,
        "max_cache_size": 50,
    }
    
    PRODUCTION = {
        "base_url": "https://api.codegen.com/v1",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 1,
        "retry_backoff": 2.0,
        "log_requests": False,
        "log_level": "WARNING",
        "use_cache": True,
        "cache_ttl": 600,
        "max_cache_size": 200,
    }


@dataclass
class ClientConfig:
    """Configuration for the Codegen API client."""
    
    # API connection settings
    api_token: Optional[str] = None
    base_url: str = "https://api.codegen.com/v1"
    timeout: int = 60
    
    # Organization settings
    org_id: Optional[str] = None
    
    # Client behavior settings
    max_retries: int = 3
    retry_delay: int = 1
    retry_backoff: float = 2.0
    log_requests: bool = False
    log_level: str = "INFO"
    
    # Cache settings
    use_cache: bool = True
    cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 100
    
    # Webhook settings
    webhook_secret: Optional[str] = None
    
    # Additional headers
    headers: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize configuration from environment variables if not provided."""
        # API token
        if not self.api_token:
            self.api_token = os.environ.get("CODEGEN_API_TOKEN")
        
        # Organization ID
        if not self.org_id:
            self.org_id = os.environ.get("CODEGEN_ORG_ID")
        
        # Base URL
        env_base_url = os.environ.get("CODEGEN_API_URL")
        if env_base_url:
            self.base_url = env_base_url
        
        # Webhook secret
        if not self.webhook_secret:
            self.webhook_secret = os.environ.get("CODEGEN_WEBHOOK_SECRET")
        
        # Set up logging
        log_level_name = os.environ.get("CODEGEN_LOG_LEVEL", self.log_level)
        numeric_level = getattr(logging, log_level_name.upper(), None)
        if isinstance(numeric_level, int):
            logging.basicConfig(level=numeric_level)
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate the configuration."""
        if not self.base_url:
            raise ValueError("Base URL is required")
        
        if self.timeout <= 0:
            raise ValueError("Timeout must be greater than 0")
        
        if self.max_retries < 0:
            raise ValueError("Max retries must be greater than or equal to 0")
        
        if self.retry_delay <= 0:
            raise ValueError("Retry delay must be greater than 0")
        
        if self.retry_backoff <= 0:
            raise ValueError("Retry backoff must be greater than 0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {
            "api_token": "***" if self.api_token else None,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "org_id": self.org_id,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "retry_backoff": self.retry_backoff,
            "log_requests": self.log_requests,
            "log_level": self.log_level,
            "use_cache": self.use_cache,
            "cache_ttl": self.cache_ttl,
            "max_cache_size": self.max_cache_size,
            "webhook_secret": "***" if self.webhook_secret else None,
            "headers": {k: v for k, v in self.headers.items() if k.lower() != "authorization"},
        }
    
    def load_preset(self, preset: ConfigPresets):
        """Load a predefined configuration preset."""
        preset_dict = preset.value
        for key, value in preset_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Re-validate after loading preset
        self._validate()
    
    def save(self):
        """Save the configuration to environment variables."""
        if self.api_token:
            os.environ["CODEGEN_API_TOKEN"] = self.api_token
        
        if self.org_id:
            os.environ["CODEGEN_ORG_ID"] = self.org_id
        
        os.environ["CODEGEN_API_URL"] = self.base_url
        
        if self.webhook_secret:
            os.environ["CODEGEN_WEBHOOK_SECRET"] = self.webhook_secret
        
        os.environ["CODEGEN_LOG_LEVEL"] = self.log_level
        
        logger.info("Configuration saved to environment variables")

