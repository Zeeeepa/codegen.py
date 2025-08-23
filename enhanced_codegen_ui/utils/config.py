"""
Configuration management for the Enhanced Codegen UI.

This module provides configuration management for the Enhanced Codegen UI,
allowing settings to be saved and loaded from a configuration file.
"""

import os
import json
import logging
from typing import Any, Dict, Optional


class ConfigManager:
    """
    Configuration manager for the Enhanced Codegen UI.
    
    This class provides methods for loading and saving configuration settings
    to a JSON file, with support for different configuration profiles.
    """
    
    def __init__(self, config_dir: Optional[str] = None, profile: str = "default"):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory to store configuration files (default: ~/.codegen)
            profile: Configuration profile to use (default: default)
        """
        self.logger = logging.getLogger(__name__)
        
        # Set configuration directory
        self.config_dir = config_dir or os.path.expanduser("~/.codegen")
        
        # Set profile
        self.profile = profile
        
        # Set configuration file path
        self.config_file = os.path.join(self.config_dir, f"{profile}.json")
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        if not os.path.exists(self.config_file):
            self.logger.info(f"Configuration file {self.config_file} not found, creating empty configuration")
            return {}
            
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.logger.info(f"Loaded configuration from {self.config_file}")
                return config
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"Error loading configuration from {self.config_file}: {str(e)}")
            return {}
            
    def _save_config(self):
        """Save configuration to file."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
                self.logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration to {self.config_file}: {str(e)}")
            
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
        
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dict[str, Any]: All configuration values
        """
        return self.config.copy()
        
    def set_profile(self, profile: str):
        """
        Set the configuration profile.
        
        Args:
            profile: Configuration profile to use
        """
        self.profile = profile
        self.config_file = os.path.join(self.config_dir, f"{profile}.json")
        self.config = self._load_config()
        
    def get_profiles(self) -> List[str]:
        """
        Get available configuration profiles.
        
        Returns:
            List[str]: Available configuration profiles
        """
        if not os.path.exists(self.config_dir):
            return []
            
        profiles = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith(".json"):
                profiles.append(filename[:-5])
                
        return profiles

