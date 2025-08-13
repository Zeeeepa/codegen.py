"""
Configuration module for the MCP server.

This module provides functions for getting and setting configuration values.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration directory
CONFIG_DIR = Path.home() / ".codegen"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "api_token": None,
    "org_id": None,
    "base_url": "https://api.codegen.com/v1"
}

def _ensure_config_dir():
    """Ensure the configuration directory exists."""
    CONFIG_DIR.mkdir(exist_ok=True)

def _load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    _ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        # Ensure all required keys are present
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        
        return config
    
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG.copy()

def _save_config(config: Dict[str, Any]):
    """Save configuration to file."""
    _ensure_config_dir()
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")

def get_config_value(key: str) -> Any:
    """Get a configuration value."""
    # Check environment variables first
    env_key = f"CODEGEN_{key.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    
    # Then check configuration file
    config = _load_config()
    return config.get(key)

def set_config_value(key: str, value: Any):
    """Set a configuration value."""
    config = _load_config()
    config[key] = value
    _save_config(config)

def get_api_token() -> Optional[str]:
    """Get the API token."""
    return get_config_value("api_token")

def get_org_id() -> Optional[str]:
    """Get the organization ID."""
    return get_config_value("org_id")

def get_base_url() -> str:
    """Get the base URL."""
    return get_config_value("base_url") or DEFAULT_CONFIG["base_url"]

