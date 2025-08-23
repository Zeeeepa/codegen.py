"""
Models for repository-related API endpoints.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from codegen_client.models.base import PaginatedResponse


class Repository(BaseModel):
    """
    Model representing a repository.

    Attributes:
        id: Repository ID
        name: Repository name
        full_name: Full repository name (org/repo)
        description: Repository description
        github_id: GitHub repository ID
        organization_id: Organization ID
        visibility: Repository visibility (public, private)
        archived: Whether the repository is archived
        setup_status: Setup status of the repository
        language: Primary language of the repository
    """

    id: int
    name: Optional[str] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    github_id: Optional[str] = None
    organization_id: int
    visibility: Optional[str] = None
    archived: bool = False
    setup_status: Optional[str] = None
    language: Optional[str] = None


class RepositoryResponse(PaginatedResponse[Repository]):
    """
    Paginated response for repository listings.
    """

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> "RepositoryResponse":
        """
        Parse a repository response from the API.

        Args:
            obj: Raw response data from the API

        Returns:
            RepositoryResponse: Parsed repository response
        """
        return cls.parse_response(obj, Repository)

