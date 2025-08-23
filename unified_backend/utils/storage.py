"""
Storage utilities for the Unified Backend.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class Storage:
    """Storage manager for the Codegen UI."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the storage manager.
        
        Args:
            storage_dir: Path to the storage directory. If None, uses the default path.
        """
        if storage_dir is None:
            # Use default path in user's home directory
            home_dir = Path.home()
            storage_dir = home_dir / ".codegen" / "storage"
            storage_dir.mkdir(exist_ok=True, parents=True)
            self.storage_dir = storage_dir
        else:
            self.storage_dir = Path(storage_dir)
            self.storage_dir.mkdir(exist_ok=True, parents=True)
    
    def save(self, key: str, data: Any) -> None:
        """
        Save data to storage.
        
        Args:
            key: Storage key
            data: Data to save
        """
        try:
            file_path = self.storage_dir / f"{key}.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def load(self, key: str, default: Any = None) -> Any:
        """
        Load data from storage.
        
        Args:
            key: Storage key
            default: Default value if not found
            
        Returns:
            Loaded data or default if not found
        """
        try:
            file_path = self.storage_dir / f"{key}.json"
            if file_path.exists():
                with open(file_path, "r") as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return default
    
    def delete(self, key: str) -> None:
        """
        Delete data from storage.
        
        Args:
            key: Storage key
        """
        try:
            file_path = self.storage_dir / f"{key}.json"
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.error(f"Error deleting data: {e}")
    
    def list_keys(self) -> List[str]:
        """
        List all storage keys.
        
        Returns:
            List of storage keys
        """
        try:
            return [f.stem for f in self.storage_dir.glob("*.json")]
        except Exception as e:
            logger.error(f"Error listing keys: {e}")
            return []
    
    def clear(self) -> None:
        """Clear all storage."""
        try:
            for f in self.storage_dir.glob("*.json"):
                f.unlink()
        except Exception as e:
            logger.error(f"Error clearing storage: {e}")
    
    def save_prorun_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        Save a ProRun configuration.
        
        Args:
            name: Configuration name
            config: Configuration data
        """
        self.save(f"prorun_config_{name}", config)
    
    def load_prorun_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a ProRun configuration.
        
        Args:
            name: Configuration name
            
        Returns:
            Configuration data or None if not found
        """
        return self.load(f"prorun_config_{name}")
    
    def list_prorun_configs(self) -> List[str]:
        """
        List all ProRun configurations.
        
        Returns:
            List of configuration names
        """
        return [k.replace("prorun_config_", "") for k in self.list_keys() if k.startswith("prorun_config_")]
    
    def delete_prorun_config(self, name: str) -> None:
        """
        Delete a ProRun configuration.
        
        Args:
            name: Configuration name
        """
        self.delete(f"prorun_config_{name}")
    
    def save_template(self, name: str, template: Dict[str, Any]) -> None:
        """
        Save a template.
        
        Args:
            name: Template name
            template: Template data
        """
        self.save(f"template_{name}", template)
    
    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a template.
        
        Args:
            name: Template name
            
        Returns:
            Template data or None if not found
        """
        return self.load(f"template_{name}")
    
    def list_templates(self) -> List[str]:
        """
        List all templates.
        
        Returns:
            List of template names
        """
        return [k.replace("template_", "") for k in self.list_keys() if k.startswith("template_")]
    
    def delete_template(self, name: str) -> None:
        """
        Delete a template.
        
        Args:
            name: Template name
        """
        self.delete(f"template_{name}")

