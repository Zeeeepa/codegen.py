"""
Configuration Management System

This module provides comprehensive configuration management with support for
multiple sources: CLI arguments > environment variables > config files > defaults.
"""

import os
import yaml
import toml
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass, field

from .errors import ConfigurationError
from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConfigDefaults:
    """Default configuration values."""
    
    # API Configuration
    api_base_url: str = "https://api.codegen.com"
    api_timeout: int = 30
    api_max_retries: int = 3
    api_retry_delay: float = 1.0
    
    # Output Configuration  
    output_format: str = "table"
    output_color: bool = True
    output_pager: bool = True
    
    # CLI Behavior
    cli_confirm_destructive: bool = True
    cli_progress_bars: bool = True
    cli_auto_update_check: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ConfigManager:
    """
    Manages configuration from multiple sources with proper precedence.
    
    Precedence order (highest to lowest):
    1. CLI arguments (handled by Click)
    2. Environment variables
    3. Configuration file
    4. Default values
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._find_config_file()
        self.defaults = ConfigDefaults()
        self._config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_locations = [
            # Current directory
            "./codegen.yaml",
            "./codegen.yml", 
            "./codegen.toml",
            "./.codegen.yaml",
            "./.codegen.yml",
            "./.codegen.toml",
            
            # User home directory
            Path.home() / ".codegen" / "config.yaml",
            Path.home() / ".codegen" / "config.yml",
            Path.home() / ".codegen" / "config.toml",
            Path.home() / ".codegen.yaml",
            Path.home() / ".codegen.yml", 
            Path.home() / ".codegen.toml",
            
            # XDG config directory
            Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "codegen" / "config.yaml",
            Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "codegen" / "config.yml",
            Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "codegen" / "config.toml",
        ]
        
        for location in possible_locations:
            if Path(location).exists():
                logger.debug(f"Found config file: {location}")
                return str(location)
        
        logger.debug("No config file found")
        return None
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_file or not Path(self.config_file).exists():
            logger.debug("No config file to load, using defaults")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith(('.yaml', '.yml')):
                    self._config_data = yaml.safe_load(f) or {}
                elif self.config_file.endswith('.toml'):
                    self._config_data = toml.load(f)
                else:
                    raise ConfigurationError(f"Unsupported config file format: {self.config_file}")
            
            logger.debug(f"Loaded config from: {self.config_file}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load config file {self.config_file}: {str(e)}",
                suggestions=[
                    "Check the file format (YAML or TOML)",
                    "Verify the file syntax is correct",
                    "Use 'codegen config validate' to check your config"
                ]
            )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with precedence handling.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'api.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Check environment variables first
        env_key = f"CODEGEN_{key.upper().replace('.', '_')}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return self._convert_env_value(env_value)
        
        # Check config file
        value = self._get_nested_value(self._config_data, key)
        if value is not None:
            return value
        
        # Check defaults
        default_value = self._get_nested_value(self.defaults.__dict__, key)
        if default_value is not None:
            return default_value
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value in memory.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        self._set_nested_value(self._config_data, key, value)
    
    def save(self, file_path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            file_path: Optional file path, defaults to current config file
        """
        target_file = file_path or self.config_file
        if not target_file:
            # Create default config file
            config_dir = Path.home() / ".codegen"
            config_dir.mkdir(exist_ok=True)
            target_file = str(config_dir / "config.yaml")
        
        try:
            Path(target_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, 'w') as f:
                if target_file.endswith(('.yaml', '.yml')):
                    yaml.dump(self._config_data, f, default_flow_style=False, indent=2)
                elif target_file.endswith('.toml'):
                    toml.dump(self._config_data, f)
                else:
                    # Default to YAML
                    yaml.dump(self._config_data, f, default_flow_style=False, indent=2)
            
            self.config_file = target_file
            logger.info(f"Configuration saved to: {target_file}")
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to save config to {target_file}: {str(e)}",
                suggestions=[
                    "Check file permissions",
                    "Ensure the directory exists",
                    "Verify disk space is available"
                ]
            )
    
    def validate(self) -> List[str]:
        """
        Validate current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate API configuration
        api_token = self.get("api.token")
        if not api_token:
            errors.append("API token is required (set CODEGEN_API_TOKEN or use 'codegen config set api.token')")
        
        base_url = self.get("api.base_url")
        if not base_url or not base_url.startswith(('http://', 'https://')):
            errors.append("API base URL must be a valid HTTP/HTTPS URL")
        
        timeout = self.get("api.timeout")
        if not isinstance(timeout, int) or timeout <= 0:
            errors.append("API timeout must be a positive integer")
        
        # Validate output format
        output_format = self.get("output.format")
        valid_formats = ["json", "yaml", "table", "text"]
        if output_format not in valid_formats:
            errors.append(f"Output format must be one of: {', '.join(valid_formats)}")
        
        # Validate log level
        log_level = self.get("log.level")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            errors.append(f"Log level must be one of: {', '.join(valid_levels)}")
        
        return errors
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config_data = {}
        logger.info("Configuration reset to defaults")
    
    def show(self) -> Dict[str, Any]:
        """
        Show current configuration with source information.
        
        Returns:
            Dictionary with configuration and metadata
        """
        config = {}
        sources = {}
        
        # Get all possible keys from defaults
        for key in self._flatten_dict(self.defaults.__dict__):
            value = self.get(key)
            config[key] = value
            
            # Determine source
            env_key = f"CODEGEN_{key.upper().replace('.', '_')}"
            if os.environ.get(env_key) is not None:
                sources[key] = "environment"
            elif self._get_nested_value(self._config_data, key) is not None:
                sources[key] = "config_file"
            else:
                sources[key] = "default"
        
        return {
            "config": config,
            "sources": sources,
            "config_file": self.config_file,
            "environment_variables": {
                k: v for k, v in os.environ.items() 
                if k.startswith("CODEGEN_")
            }
        }
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def _set_nested_value(self, data: Dict[str, Any], key: str, value: Any) -> None:
        """Set value in nested dictionary using dot notation."""
        keys = key.split('.')
        current = data
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Handle boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _flatten_dict(self, data: Dict[str, Any], prefix: str = '') -> List[str]:
        """Flatten nested dictionary keys with dot notation."""
        keys = []
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                keys.extend(self._flatten_dict(value, full_key))
            else:
                keys.append(full_key)
        return keys


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def init_config(config_file: Optional[str] = None) -> ConfigManager:
    """Initialize configuration manager with optional config file."""
    global _config_manager
    _config_manager = ConfigManager(config_file)
    return _config_manager
