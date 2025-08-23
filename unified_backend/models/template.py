"""
Template model for prompt templates.

This module provides the template model for prompt templates.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class Template:
    """Template model for prompt templates."""
    
    id: str
    name: str
    content: str
    category: str
    created_at: str
    created_by: Optional[str] = None
    description: Optional[str] = None
    variables: List[Dict[str, str]] = field(default_factory=list)
    is_shared: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """
        Create a template from a dictionary.
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            Template
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            content=data.get("content", ""),
            category=data.get("category", ""),
            created_at=data.get("created_at", datetime.now().isoformat()),
            created_by=data.get("created_by"),
            description=data.get("description"),
            variables=data.get("variables", []),
            is_shared=data.get("is_shared", False)
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the template to a dictionary.
        
        Returns:
            Dictionary representation of the template
        """
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "description": self.description,
            "variables": self.variables,
            "is_shared": self.is_shared
        }

