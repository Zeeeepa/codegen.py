"""
Repository model for the Codegen Agent API.

This module provides the repository model for the Codegen Agent API.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Repository:
    """Repository model."""
    
    id: str
    name: str
    full_name: str
    description: Optional[str] = None
    github_id: Optional[str] = None
    organization_id: Optional[str] = None
    visibility: Optional[str] = None
    archived: bool = False
    setup_status: Optional[str] = None
    language: Optional[str] = None
    has_setup_commands: bool = False
    setup_commands: List[str] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Repository':
        """
        Create a repository from a dictionary.
        
        Args:
            data: Dictionary containing repository data
            
        Returns:
            Repository
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description"),
            github_id=data.get("github_id"),
            organization_id=data.get("organization_id"),
            visibility=data.get("visibility"),
            archived=data.get("archived", False),
            setup_status=data.get("setup_status"),
            language=data.get("language"),
            has_setup_commands=data.get("has_setup_commands", False),
            setup_commands=data.get("setup_commands", [])
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the repository to a dictionary.
        
        Returns:
            Dictionary representation of the repository
        """
        return {
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "github_id": self.github_id,
            "organization_id": self.organization_id,
            "visibility": self.visibility,
            "archived": self.archived,
            "setup_status": self.setup_status,
            "language": self.language,
            "has_setup_commands": self.has_setup_commands,
            "setup_commands": self.setup_commands
        }

