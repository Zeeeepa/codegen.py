"""
Models for user-related API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from codegen_client.models.base import PaginatedResponse


class User(BaseModel):
    """
    Model representing a user.

    Attributes:
        id: User ID
        email: User email address
        github_user_id: GitHub user ID
        github_username: GitHub username
        avatar_url: URL to the user's avatar
        full_name: User's full name
    """

    id: int
    email: Optional[str] = None
    github_user_id: Optional[str] = None
    github_username: Optional[str] = None
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None


class UserResponse(PaginatedResponse[User]):
    """
    Paginated response for user listings.
    """

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "UserResponse":
        """
        Parse a user response from the API.

        Args:
            obj: Raw response data from the API

        Returns:
            UserResponse: Parsed user response
        """
        return cls.parse_response(obj, User)

