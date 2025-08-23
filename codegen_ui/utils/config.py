"""
Configuration module for the Codegen UI.
"""

import os
import json
from typing import Any, Dict, Optional


class Config:
    """
    Configuration manager for the Codegen UI.
    
    This class handles loading and saving configuration settings.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file (optional)
        """
        self.config_file = config_file or os.path.expanduser("~/.codegen/config.json")
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        if not os.path.exists(self.config_file):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            return {}
            
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
            
    def _save_config(self):
        """Save configuration to file."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Any: Configuration value
        """
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        self._save_config()
        
    def delete(self, key: str):
        """
        Delete a configuration value.
        
        Args:
            key: Configuration key
        """
        if key in self.config:
            del self.config[key]
            self._save_config()
            
    def clear(self):
        """Clear all configuration values."""
        self.config = {}
        self._save_config()

