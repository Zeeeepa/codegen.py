"""
Configuration Management

This module provides functions for managing configuration settings for the Codegen MCP server.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union

# Default configuration directory
CONFIG_DIR = Path.home() / ".codegen"
CONFIG_FILE = CONFIG_DIR / "config.json"

def ensure_config_dir() -> None:
    """Ensure the configuration directory exists."""
    CONFIG_DIR.mkdir(exist_ok=True)

def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default if it doesn't exist."""
    ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        # Create default config
        default_config = {
            "api_token": os.environ.get("CODEGEN_API_TOKEN", ""),
            "org_id": os.environ.get("CODEGEN_ORG_ID", ""),
            "base_url": os.environ.get("CODEGEN_BASE_URL", "https://api.codegen.com/v1")
        }
        save_config(default_config)
        return default_config
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or can't be read, create a new one
        default_config = {
            "api_token": os.environ.get("CODEGEN_API_TOKEN", ""),
            "org_id": os.environ.get("CODEGEN_ORG_ID", ""),
            "base_url": os.environ.get("CODEGEN_BASE_URL", "https://api.codegen.com/v1")
        }
        save_config(default_config)
        return default_config

def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    config = load_config()
    
    # Check environment variables first
    env_key = f"CODEGEN_{key.upper()}"
    env_value = os.environ.get(env_key)
    if env_value is not None:
        return env_value
    
    # Then check config file
    return config.get(key, default)

def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value."""
    config = load_config()
    config[key] = value
    save_config(config)

def get_api_token() -> str:
    """Get the API token from config or environment."""
    return get_config_value("api_token", "")

def get_org_id() -> str:
    """Get the organization ID from config or environment."""
    return get_config_value("org_id", "")

def get_base_url() -> str:
    """Get the base URL from config or environment."""
    return get_config_value("base_url", "https://api.codegen.com/v1")

