"""
Client for the Agents API endpoints.
"""

from typing import Any, Dict, List, Optional, Union, cast

from codegen_client.models.agents import (
    AgentRun,
    AgentRunCreate,
    AgentRunResponse,
    AgentRunStatus,
)


class AgentsClient:
    """
    Client for the Agents API endpoints.

    This client provides methods for interacting with agent-related endpoints,
    such as creating agent runs, getting agent run details, and managing agent runs.
    """

    def __init__(self, client: Any):
        """
        Initialize the Agents API client.

        Args:
            client: The base API client
        """
        self.client = client

    def create_agent_run(
        self,
        org_id: int,
        prompt: str,
        repo_id: Optional[int] = None,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentRun:
        """
        Create a new agent run.

        Args:
            org_id: Organization ID
            prompt: The prompt to send to the agent
            repo_id: Repository ID to associate with the agent run
            images: List of image URLs to include with the prompt
            metadata: Additional metadata for the agent run
            model: Model to use for the agent run

        Returns:
            AgentRun: Created agent run

        Raises:
            CodegenApiError: If the API request fails
        """
        data = AgentRunCreate(
            prompt=prompt,
            repo_id=repo_id,
            images=images or [],
            metadata=metadata or {},
            model=model,
        )
        
        response_data = self.client.post(
            f"/organizations/{org_id}/agent/run",
            data=data.dict(exclude_none=True),
        )
        
        return AgentRun.parse_obj(response_data)

    def get_agent_run(self, org_id: int, agent_run_id: int) -> AgentRun:
        """
        Get details for a specific agent run.

        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID

        Returns:
            AgentRun: Agent run details

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the agent run is not found
        """
        response_data = self.client.get(
            f"/organizations/{org_id}/agent/run/{agent_run_id}"
        )
        
        return AgentRun.parse_obj(response_data)

    def list_agent_runs(
        self,
        org_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[Union[AgentRunStatus, str]] = None,
        repo_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List agent runs for an organization.

        Args:
            org_id: Organization ID
            skip: Number of items to skip (for pagination)
            limit: Maximum number of items to return (for pagination)
            status: Filter by agent run status
            repo_id: Filter by repository ID

        Returns:
            Dict[str, Any]: Paginated response with agent run data

        Raises:
            CodegenApiError: If the API request fails
        """
        params = {"skip": skip, "limit": limit}
        
        if status:
            if isinstance(status, AgentRunStatus):
                params["status"] = status.value
            else:
                params["status"] = status
        
        if repo_id:
            params["repo_id"] = repo_id
        
        return self.client.get(
            f"/organizations/{org_id}/agent/runs",
            params=params,
        )

    def resume_agent_run(
        self,
        org_id: int,
        agent_run_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
    ) -> AgentRun:
        """
        Resume an existing agent run with a new prompt.

        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            prompt: The prompt to send to the agent
            images: List of image URLs to include with the prompt

        Returns:
            AgentRun: Updated agent run

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the agent run is not found
        """
        data = {
            "prompt": prompt,
        }
        
        if images:
            data["images"] = images
        
        response_data = self.client.post(
            f"/organizations/{org_id}/agent/run/{agent_run_id}/resume",
            data=data,
        )
        
        return AgentRun.parse_obj(response_data)

    def ban_all_checks_for_agent_run(
        self,
        org_id: int,
        agent_run_id: int,
    ) -> Dict[str, Any]:
        """
        Ban all checks for an agent run.

        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID

        Returns:
            Dict[str, Any]: Response data

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the agent run is not found
        """
        return self.client.post(
            f"/organizations/{org_id}/agent/run/{agent_run_id}/ban-all-checks",
        )

    def unban_all_checks_for_agent_run(
        self,
        org_id: int,
        agent_run_id: int,
    ) -> Dict[str, Any]:
        """
        Unban all checks for an agent run.

        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID

        Returns:
            Dict[str, Any]: Response data

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the agent run is not found
        """
        return self.client.post(
            f"/organizations/{org_id}/agent/run/{agent_run_id}/unban-all-checks",
        )

    def remove_codegen_from_pr(
        self,
        org_id: int,
        repo_id: int,
        pr_number: int,
    ) -> Dict[str, Any]:
        """
        Remove Codegen from a pull request.

        Args:
            org_id: Organization ID
            repo_id: Repository ID
            pr_number: Pull request number

        Returns:
            Dict[str, Any]: Response data

        Raises:
            CodegenApiError: If the API request fails
            CodegenResourceNotFoundError: If the repository or PR is not found
        """
        return self.client.post(
            f"/organizations/{org_id}/repos/{repo_id}/pulls/{pr_number}/remove-codegen",
        )

