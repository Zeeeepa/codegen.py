"""
Utility functions for the Unified Backend.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for the Codegen UI."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses the default path.
        """
        if config_path is None:
            # Use default path in user's home directory
            home_dir = Path.home()
            config_dir = home_dir / ".codegen"
            config_dir.mkdir(exist_ok=True)
            self.config_path = config_dir / "config.json"
        else:
            self.config_path = Path(config_path)
        
        # Load or create configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default configuration.
        
        Returns:
            Configuration dictionary
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                return config
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                return {}
        else:
            return {}
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            default: Default value if not found
            
        Returns:
            Configuration value or default if not found
        """
        if section in self.config and key in self.config[section]:
            return self.config[section][key]
        return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.save_config()
    
    def get_api_token(self) -> str:
        """
        Get the Codegen API token.
        
        Returns:
            Codegen API token
        """
        # First check environment variable
        token = os.environ.get("CODEGEN_API_TOKEN")
        if token:
            return token
        
        # Then check configuration
        return self.get("api", "codegen_api_token", "")
    
    def get_org_id(self) -> str:
        """
        Get the Codegen organization ID.
        
        Returns:
            Codegen organization ID
        """
        # First check environment variable
        org_id = os.environ.get("CODEGEN_ORG_ID")
        if org_id:
            return org_id
        
        # Then check configuration
        return self.get("api", "codegen_org_id", "")
    
    def get_github_token(self) -> str:
        """
        Get the GitHub token.
        
        Returns:
            GitHub token
        """
        # First check environment variable
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            return token
        
        # Then check configuration
        return self.get("api", "github_token", "")

