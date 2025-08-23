"""
Configuration for the Codegen UI.

This module provides configuration management for the Codegen UI.
"""

import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration for the Codegen UI."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration.
        
        Args:
            config_file: Path to the configuration file.
        """
        self.config_file = config_file or os.path.expanduser("~/.codegen/config.json")
        self.config: Dict[str, Any] = {}
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load the configuration from the configuration file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Load configuration
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            else:
                # Create default configuration
                self.config = {}
                self._save_config()
        except Exception as e:
            logger.exception(f"Failed to load configuration: {e}")
    
    def _save_config(self):
        """Save the configuration to the configuration file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Save configuration
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.exception(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key.
            default: The default value to return if the key doesn't exist.
        
        Returns:
            The configuration value.
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: The configuration key.
            value: The configuration value.
        """
        self.config[key] = value
        self._save_config()

