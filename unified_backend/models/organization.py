"""
Organization model for the Codegen Agent API.

This module provides the organization model for the Codegen Agent API.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Organization:
    """Organization model."""
    
    id: str
    name: str
    settings: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Organization':
        """
        Create an organization from a dictionary.
        
        Args:
            data: Dictionary containing organization data
            
        Returns:
            Organization
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            settings=data.get("settings", {}),
            description=data.get("description")
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the organization to a dictionary.
        
        Returns:
            Dictionary representation of the organization
        """
        return {
            "id": self.id,
            "name": self.name,
            "settings": self.settings,
            "description": self.description
        }

