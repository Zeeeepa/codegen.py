"""
Configuration presets for the Codegen API client.

This module contains predefined configuration presets for common use cases.
"""

from codegen.config.client_config import ClientConfig


class ConfigPresets:
    """Predefined configuration presets for the Codegen API client."""
    
    @staticmethod
    def default() -> ClientConfig:
        """Default configuration with balanced settings."""
        return ClientConfig()
    
    @staticmethod
    def minimal() -> ClientConfig:
        """Minimal configuration with no caching or retries."""
        return ClientConfig(
            max_retries=0,
            use_cache=False,
            log_requests=False,
        )
    
    @staticmethod
    def development() -> ClientConfig:
        """Development configuration with verbose logging and shorter timeouts."""
        return ClientConfig(
            timeout=30,
            log_requests=True,
            log_level="DEBUG",
            cache_ttl=60,  # 1 minute
        )
    
    @staticmethod
    def production() -> ClientConfig:
        """Production configuration with robust error handling and caching."""
        return ClientConfig(
            timeout=120,
            max_retries=5,
            retry_delay=2,
            retry_backoff=2.5,
            log_requests=False,
            log_level="WARNING",
            cache_ttl=600,  # 10 minutes
            max_cache_size=500,
        )
    
    @staticmethod
    def high_throughput() -> ClientConfig:
        """Configuration optimized for high throughput."""
        return ClientConfig(
            timeout=30,
            max_retries=2,
            retry_delay=1,
            retry_backoff=1.5,
            log_requests=False,
            use_cache=True,
            cache_ttl=300,  # 5 minutes
            max_cache_size=1000,
        )
    
    @staticmethod
    def high_reliability() -> ClientConfig:
        """Configuration optimized for high reliability."""
        return ClientConfig(
            timeout=180,
            max_retries=10,
            retry_delay=3,
            retry_backoff=2.0,
            log_requests=True,
            log_level="INFO",
            use_cache=True,
            cache_ttl=600,  # 10 minutes
            max_cache_size=200,
        )

