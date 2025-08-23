"""
Client for the Sandbox API endpoints.
"""

from typing import Any, Dict, Optional

from codegen_client.models.agents import AgentRun


class SandboxClient:
    """
    Client for the Sandbox API endpoints.

    This client provides methods for interacting with sandbox-related endpoints,
    such as analyzing sandbox logs.
    """

    def __init__(self, client: Any):
        """
        Initialize the Sandbox API client.

        Args:
            client: The base API client
        """
        self.client = client

    def analyze_sandbox_logs(
        self,
        org_id: int,
        repo_id: int,
        logs: str,
        model: Optional[str] = None,
    ) -> AgentRun:
        """
        Analyze sandbox setup logs using an AI agent.

        Args:
            org_id: Organization ID
            repo_id: Repository ID
            logs: Sandbox logs to analyze
            model: Model to use for analysis

        Returns:
            AgentRun: Created agent run for log analysis

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the organization or repository is not found
        """
        data = {
            "logs": logs,
        }
        
        if model:
            data["model"] = model
            
        response_data = self.client.post(
            f"/organizations/{org_id}/repos/{repo_id}/sandbox/analyze-logs",
            data=data,
        )
        
        return AgentRun.parse_obj(response_data)

