"""
Configuration management for Codegen MCP server
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = Path.home() / ".codegen"
CONFIG_FILE = CONFIG_DIR / "config.json"

class Config:
    """Configuration manager for Codegen MCP server"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or CONFIG_FILE
        self.config_dir = self.config_file.parent
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if not self.config_file.exists():
            logger.info(f"Config file not found at {self.config_file}. Using default configuration.")
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return {}
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            # Create directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        # First check environment variables
        env_key = f"CODEGEN_{key.upper()}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        
        # Then check config file
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
        self._save_config()
    
    def validate(self) -> bool:
        """Validate configuration"""
        org_id = self.get("org_id")
        api_token = self.get("api_token")
        
        if not org_id:
            logger.warning("Organization ID not configured. Use 'config set org_id YOUR_ORG_ID' or set CODEGEN_ORG_ID environment variable.")
            return False
        
        if not api_token:
            logger.warning("API token not configured. Use 'config set api_token YOUR_API_TOKEN' or set CODEGEN_API_TOKEN environment variable.")
            return False
        
        return True

