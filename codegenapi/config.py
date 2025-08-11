"""
Configuration Management

Handles configuration loading from environment variables, config files,
and command line arguments with proper precedence.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field

from .exceptions import ConfigError

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Configuration class with environment and file support"""
    
    # API Configuration
    api_token: Optional[str] = None
    org_id: Optional[int] = None
    base_url: str = "https://api.codegen.com/v1"
    
    # Local Configuration
    config_dir: Path = field(default_factory=lambda: Path.home() / ".codegen")
    tasks_dir: Path = field(default_factory=lambda: Path.cwd() / "TASKS")
    state_file: Path = field(default_factory=lambda: Path.home() / ".codegen" / "state.json")
    
    # Behavior Configuration
    auto_save: bool = True
    default_timeout: int = 300
    max_retries: int = 3
    log_level: str = "INFO"
    
    # Template Configuration
    template_cache_ttl: int = 3600
    custom_templates_dir: Optional[Path] = None
    
    def __post_init__(self):
        """Initialize configuration after creation"""
        self._load_from_env()
        self._load_from_file()
        self._validate()
        self._ensure_directories()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        # API Configuration
        if os.getenv("CODEGEN_API_TOKEN"):
            self.api_token = os.getenv("CODEGEN_API_TOKEN")
        
        if os.getenv("CODEGEN_ORG_ID"):
            try:
                self.org_id = int(os.getenv("CODEGEN_ORG_ID"))
            except ValueError:
                logger.warning("Invalid CODEGEN_ORG_ID environment variable")
        
        if os.getenv("CODEGEN_BASE_URL"):
            self.base_url = os.getenv("CODEGEN_BASE_URL")
        
        # Behavior Configuration
        if os.getenv("CODEGEN_LOG_LEVEL"):
            self.log_level = os.getenv("CODEGEN_LOG_LEVEL")
        
        if os.getenv("CODEGEN_TIMEOUT"):
            try:
                self.default_timeout = int(os.getenv("CODEGEN_TIMEOUT"))
            except ValueError:
                logger.warning("Invalid CODEGEN_TIMEOUT environment variable")
    
    def _load_from_file(self, config_file: Optional[Path] = None) -> None:
        """Load configuration from file"""
        if config_file is None:
            config_file = self.config_dir / "config.json"
        
        if not config_file.exists():
            return
        
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            # Update configuration with file values (if not already set)
            for key, value in file_config.items():
                if hasattr(self, key) and getattr(self, key) is None:
                    setattr(self, key, value)
                    
        except Exception as e:
            logger.warning(f"Failed to load config file {config_file}: {e}")
    
    def _validate(self) -> None:
        """Validate configuration"""
        errors = []
        
        if not self.api_token:
            errors.append("API token is required (set CODEGEN_API_TOKEN or add to config file)")
        
        if not self.org_id:
            errors.append("Organization ID is required (set CODEGEN_ORG_ID or add to config file)")
        
        if not self.base_url:
            errors.append("Base URL is required")
        
        if errors:
            raise ConfigError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if self.custom_templates_dir:
            self.custom_templates_dir.mkdir(parents=True, exist_ok=True)
    
    def save_to_file(self, config_file: Optional[Path] = None) -> None:
        """Save configuration to file"""
        if config_file is None:
            config_file = self.config_dir / "config.json"
        
        config_data = {
            "api_token": self.api_token,
            "org_id": self.org_id,
            "base_url": self.base_url,
            "auto_save": self.auto_save,
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries,
            "log_level": self.log_level,
            "template_cache_ttl": self.template_cache_ttl
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(config_file, 0o600)
            logger.info(f"Configuration saved to {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigError(f"Failed to save configuration: {e}")
    
    def update(self, **kwargs) -> None:
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "api_token": "***" if self.api_token else None,  # Mask token
            "org_id": self.org_id,
            "base_url": self.base_url,
            "config_dir": str(self.config_dir),
            "tasks_dir": str(self.tasks_dir),
            "state_file": str(self.state_file),
            "auto_save": self.auto_save,
            "default_timeout": self.default_timeout,
            "max_retries": self.max_retries,
            "log_level": self.log_level,
            "template_cache_ttl": self.template_cache_ttl,
            "custom_templates_dir": str(self.custom_templates_dir) if self.custom_templates_dir else None
        }

