"""
Client for the Setup Commands API endpoints.
"""

from typing import Any, Dict, Optional


class SetupCommandsClient:
    """
    Client for the Setup Commands API endpoints.

    This client provides methods for interacting with setup command-related endpoints,
    such as generating setup commands.
    """

    def __init__(self, client: Any):
        """
        Initialize the Setup Commands API client.

        Args:
            client: The base API client
        """
        self.client = client

    def generate_setup_commands(
        self,
        org_id: int,
        repo_id: int,
        platform: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate setup commands for a repository.

        Args:
            org_id: Organization ID
            repo_id: Repository ID
            platform: Platform to generate commands for (e.g., "linux", "macos", "windows")

        Returns:
            Dict[str, Any]: Setup commands data

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the organization or repository is not found
        """
        params = {}
        if platform:
            params["platform"] = platform
            
        return self.client.get(
            f"/organizations/{org_id}/repos/{repo_id}/setup-commands",
            params=params,
        )

