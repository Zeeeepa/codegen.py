"""
Client configuration for the Codegen API.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


class ConfigPresets:
    """
    Predefined configuration presets for different environments.
    """
    PRODUCTION = {
        "base_url": "https://api.codegen.com/v1",
        "timeout": 60,
        "max_retries": 3,
        "log_requests": False,
    }
    
    DEVELOPMENT = {
        "base_url": "https://dev-api.codegen.com/v1",
        "timeout": 120,
        "max_retries": 5,
        "log_requests": True,
    }
    
    LOCAL = {
        "base_url": "http://localhost:8000/v1",
        "timeout": 120,
        "max_retries": 5,
        "log_requests": True,
    }


@dataclass
class ClientConfig:
    """
    Configuration for the Codegen API client.
    """
    api_key: Optional[str] = None
    org_id: Optional[str] = None
    base_url: str = "https://api.codegen.com/v1"
    timeout: int = 60
    max_retries: int = 3
    log_requests: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    user_agent: Optional[str] = None
    
    def __post_init__(self):
        """
        Initialize configuration with environment variables if not provided.
        """
        # API key from environment variable
        if not self.api_key:
            self.api_key = os.environ.get("CODEGEN_API_KEY")
            
        # Organization ID from environment variable
        if not self.org_id:
            self.org_id = os.environ.get("CODEGEN_ORG_ID")
            
        # User agent with version information
        if not self.user_agent:
            from codegen import __version__
            self.user_agent = f"CodegenPythonClient/{__version__}"
    
    @classmethod
    def from_preset(cls, preset_name: str, **overrides) -> 'ClientConfig':
        """
        Create a configuration from a predefined preset.
        
        Args:
            preset_name: Name of the preset ('production', 'development', 'local')
            **overrides: Any values to override from the preset
            
        Returns:
            ClientConfig instance with preset values and overrides
        """
        preset_name = preset_name.upper()
        if not hasattr(ConfigPresets, preset_name):
            raise ValueError(f"Unknown preset: {preset_name}")
            
        preset = getattr(ConfigPresets, preset_name)
        config_dict = {**preset, **overrides}
        
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "api_key": self.api_key,
            "org_id": self.org_id,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "log_requests": self.log_requests,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl,
            "user_agent": self.user_agent,
        }

