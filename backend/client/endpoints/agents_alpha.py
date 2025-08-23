"""
Client for the Agents Alpha API endpoints.
"""

from typing import Any, Dict, Optional

from codegen_client.models.agents import AgentRunResponse


class AgentsAlphaClient:
    """
    Client for the Agents Alpha API endpoints.

    This client provides methods for interacting with experimental agent-related endpoints,
    such as getting agent run logs.
    """

    def __init__(self, client: Any):
        """
        Initialize the Agents Alpha API client.

        Args:
            client: The base API client
        """
        self.client = client

    def get_agent_run_logs(
        self,
        org_id: int,
        agent_run_id: int,
        skip: int = 0,
        limit: int = 100,
        reverse: bool = False,
    ) -> AgentRunResponse:
        """
        Get logs for a specific agent run.

        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return (for pagination)
            reverse: Whether to reverse the order of the logs

        Returns:
            AgentRunResponse: Agent run logs

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the agent run is not found
        """
        response_data = self.client.get(
            f"/alpha/organizations/{org_id}/agent/run/{agent_run_id}/logs",
            params={
                "skip": skip,
                "limit": limit,
                "reverse": reverse,
            },
        )
        
        return AgentRunResponse.parse_obj(response_data)

