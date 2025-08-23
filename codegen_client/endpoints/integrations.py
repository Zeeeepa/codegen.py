"""
Client for the Integrations API endpoints.
"""

from typing import Any, Dict


class IntegrationsClient:
    """
    Client for the Integrations API endpoints.

    This client provides methods for interacting with integration-related endpoints,
    such as getting organization integrations.
    """

    def __init__(self, client: Any):
        """
        Initialize the Integrations API client.

        Args:
            client: The base API client
        """
        self.client = client

    def get_organization_integrations(
        self,
        org_id: int,
    ) -> Dict[str, Any]:
        """
        Get all integration statuses for an organization.

        Args:
            org_id: Organization ID

        Returns:
            Dict[str, Any]: Organization integrations data

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the organization is not found
        """
        return self.client.get(
            f"/organizations/{org_id}/integrations",
        )

