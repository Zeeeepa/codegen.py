"""
Client for the Organizations API endpoints.
"""

from typing import Any, Dict, List, Optional

from codegen_client.models.organizations import Organization, OrganizationResponse
from codegen_client.utils.pagination import get_paginated_results


class OrganizationsClient:
    """
    Client for the Organizations API endpoints.

    This client provides methods for interacting with organization-related endpoints,
    such as listing organizations.
    """

    def __init__(self, client: Any):
        """
        Initialize the Organizations API client.

        Args:
            client: The base API client
        """
        self.client = client

    def get_organizations(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> OrganizationResponse:
        """
        Get a list of organizations.

        Args:
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return (for pagination)

        Returns:
            OrganizationResponse: Paginated response with organization data

        Raises:
            CodegenApiError: If the API request fails
        """
        response_data = self.client.get(
            "/organizations",
            params={"skip": skip, "limit": limit},
        )
        return OrganizationResponse.parse_obj(response_data)

    def get_all_organizations(
        self,
        limit: Optional[int] = None,
    ) -> List[Organization]:
        """
        Get all organizations.

        This method automatically handles pagination to retrieve all organizations.

        Args:
            limit: Maximum number of organizations to return (None for all)

        Returns:
            List[Organization]: List of all organizations

        Raises:
            CodegenApiError: If the API request fails
        """
        return get_paginated_results(
            lambda page, page_size: self.get_organizations(
                skip=(page - 1) * page_size,
                limit=page_size,
            ),
            Organization,
            limit=limit,
        )

