"""
Type stub file for config.py
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path

class Config:
    """Configuration manager for Codegen API"""
    def __init__(self, config_file: Optional[Union[str, Path]] = None) -> None: ...
    
    def get(self, key: str, default: Any = None) -> Any: ...
    
    def set(self, key: str, value: Any) -> None: ...
    
    def validate(self) -> bool: ...
    
    def get_config(self) -> Dict[str, Any]: ...
    
    def save(self) -> None: ...

