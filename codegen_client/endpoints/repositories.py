"""
Client for the Repositories API endpoints.
"""

from typing import Any, Dict, List, Optional

from codegen_client.models.repositories import Repository, RepositoryResponse
from codegen_client.utils.pagination import get_paginated_results


class RepositoriesClient:
    """
    Client for the Repositories API endpoints.

    This client provides methods for interacting with repository-related endpoints,
    such as listing repositories.
    """

    def __init__(self, client: Any):
        """
        Initialize the Repositories API client.

        Args:
            client: The base API client
        """
        self.client = client

    def get_repositories(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> RepositoryResponse:
        """
        Get a list of repositories for an organization.

        Args:
            org_id: Organization ID
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return (for pagination)

        Returns:
            RepositoryResponse: Paginated response with repository data

        Raises:
            CodegenApiError: If the API request fails
        """
        response_data = self.client.get(
            f"/organizations/{org_id}/repos",
            params={"skip": skip, "limit": limit},
        )
        return RepositoryResponse.parse_obj(response_data)

    def get_all_repositories(
        self,
        org_id: int,
        limit: Optional[int] = None,
    ) -> List[Repository]:
        """
        Get all repositories for an organization.

        This method automatically handles pagination to retrieve all repositories.

        Args:
            org_id: Organization ID
            limit: Maximum number of repositories to return (None for all)

        Returns:
            List[Repository]: List of all repositories in the organization

        Raises:
            CodegenApiError: If the API request fails
        """
        return get_paginated_results(
            lambda page, page_size: self.get_repositories(
                org_id=org_id,
                skip=(page - 1) * page_size,
                limit=page_size,
            ),
            Repository,
            limit=limit,
        )

