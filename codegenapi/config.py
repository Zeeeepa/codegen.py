"""
Configuration management for CodegenAPI
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigError


class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config_dir = Path(self.config_file).parent
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        home = Path.home()
        return str(home / ".codegenapi" / "config.yaml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment"""
        config = {}
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
            except Exception as e:
                raise ConfigError(f"Failed to load config file: {e}")
        
        # Override with environment variables
        config.setdefault("api", {})
        config["api"]["token"] = os.getenv("CODEGEN_API_TOKEN", config["api"].get("token"))
        config["api"]["org_id"] = os.getenv("CODEGEN_ORG_ID", config["api"].get("org_id"))
        config["api"]["base_url"] = os.getenv("CODEGEN_BASE_URL", 
                                            config["api"].get("base_url", "https://codegen-sh-rest-api.modal.run"))
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            raise ConfigError(f"Failed to save config file: {e}")
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.get("api.token"):
            errors.append("API token is required (set CODEGEN_API_TOKEN or api.token in config)")
        
        if not self.get("api.org_id"):
            errors.append("Organization ID is required (set CODEGEN_ORG_ID or api.org_id in config)")
        
        return errors
    
    @property
    def tasks_dir(self) -> Path:
        """Get tasks storage directory"""
        tasks_dir = Path(self.get("storage.tasks_dir", str(self.config_dir / "tasks")))
        tasks_dir.mkdir(parents=True, exist_ok=True)
        return tasks_dir
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory"""
        logs_dir = Path(self.get("storage.logs_dir", str(self.config_dir / "logs")))
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    @property
    def api_token(self) -> Optional[str]:
        """Get API token"""
        return self.get("api.token")
    
    @property
    def org_id(self) -> Optional[str]:
        """Get organization ID"""
        return self.get("api.org_id")
    
    @property
    def base_url(self) -> str:
        """Get API base URL"""
        return self.get("api.base_url", "https://codegen-sh-rest-api.modal.run")
