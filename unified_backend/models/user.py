"""
User model for the Codegen Agent API.

This module provides the user model for the Codegen Agent API.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class User:
    """User model."""
    
    id: str
    email: Optional[str] = None
    github_user_id: Optional[str] = None
    github_username: Optional[str] = None
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_admin: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a user from a dictionary.
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            User
        """
        return cls(
            id=data.get("id", ""),
            email=data.get("email"),
            github_user_id=data.get("github_user_id"),
            github_username=data.get("github_username"),
            avatar_url=data.get("avatar_url"),
            full_name=data.get("full_name"),
            role=data.get("role"),
            is_admin=data.get("is_admin", False)
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the user to a dictionary.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            "id": self.id,
            "email": self.email,
            "github_user_id": self.github_user_id,
            "github_username": self.github_username,
            "avatar_url": self.avatar_url,
            "full_name": self.full_name,
            "role": self.role,
            "is_admin": self.is_admin
        }

