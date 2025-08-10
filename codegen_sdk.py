"""
Official Codegen SDK - Aligned with official documentation
"""

import os
from typing import Any, Optional

from codegen_api_client.api.agents_api import AgentsApi
from codegen_api_client.api_client import ApiClient
from codegen_api_client.configuration import Configuration
from codegen_api_client.models.agent_run_response import AgentRunResponse
from codegen_api_client.models.create_agent_run_input import CreateAgentRunInput


class AgentTask:
    """Represents an agent run job."""

    def __init__(self, task_data: AgentRunResponse, api_client: ApiClient, org_id: int):
        self.id = task_data.id
        self.org_id = org_id
        self.status = task_data.status
        self.result = task_data.result
        self.web_url = task_data.web_url
        self.created_at = task_data.created_at
        self.updated_at = task_data.updated_at
        self.prompt = task_data.prompt
        self.repo_name = task_data.repo_name
        self.branch_name = task_data.branch_name
        self._api_client = api_client
        self._agents_api = AgentsApi(api_client)

    def refresh(self) -> None:
        """Refresh the job status from the API."""
        if self.id is None:
            return

        job_data = self._agents_api.get_agent_run_v1_organizations_org_id_agent_run_agent_run_id_get(
            agent_run_id=int(self.id), 
            org_id=int(self.org_id), 
            authorization=f"Bearer {self._api_client.configuration.access_token}"
        )

        # Update all attributes from the refreshed data
        self.status = job_data.status
        self.result = job_data.result
        self.updated_at = job_data.updated_at
        self.web_url = job_data.web_url

    def to_dict(self) -> dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            "id": self.id,
            "org_id": self.org_id,
            "status": self.status,
            "result": self.result,
            "web_url": self.web_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "prompt": self.prompt,
            "repo_name": self.repo_name,
            "branch_name": self.branch_name,
        }


class Agent:
    """API client for interacting with Codegen AI agents."""

    def __init__(
        self, 
        token: Optional[str] = None, 
        org_id: Optional[int] = None, 
        base_url: str = "https://api.codegen.com"
    ):
        """Initialize a new Agent client.

        Args:
            token: API authentication token. If not provided, will use CODEGEN_API_TOKEN env var.
            org_id: Organization ID. If not provided, will use CODEGEN_ORG_ID env var.
            base_url: Base URL for the API. Defaults to official API URL.
        """
        self.token = token or os.environ.get("CODEGEN_API_TOKEN")
        if not self.token:
            raise ValueError("API token is required. Provide it directly or set CODEGEN_API_TOKEN environment variable.")
        
        self.org_id = org_id or int(os.environ.get("CODEGEN_ORG_ID", "0"))
        if not self.org_id:
            raise ValueError("Organization ID is required. Provide it directly or set CODEGEN_ORG_ID environment variable.")

        # Configure API client
        config = Configuration(host=base_url, access_token=self.token)
        self.api_client = ApiClient(configuration=config)
        self.agents_api = AgentsApi(self.api_client)

        # Current job
        self.current_job: Optional[AgentTask] = None

    def run(self, prompt: str, repo_name: Optional[str] = None, branch_name: Optional[str] = None) -> AgentTask:
        """Run an agent with the given prompt.

        Args:
            prompt: The instruction for the agent to execute
            repo_name: Optional repository name
            branch_name: Optional branch name

        Returns:
            AgentTask: A task object representing the agent run
        """
        run_input = CreateAgentRunInput(
            prompt=prompt,
            repo_name=repo_name,
            branch_name=branch_name
        )
        
        agent_run_response = self.agents_api.create_agent_run_v1_organizations_org_id_agent_run_post(
            org_id=int(self.org_id), 
            create_agent_run_input=run_input, 
            authorization=f"Bearer {self.token}",
            _headers={"Content-Type": "application/json"}
        )

        job = AgentTask(agent_run_response, self.api_client, self.org_id)
        self.current_job = job
        return job

    def get_agent_run(self, agent_run_id: int) -> AgentTask:
        """Get a specific agent run by ID.

        Args:
            agent_run_id: The ID of the agent run to retrieve

        Returns:
            AgentTask: The agent run task
        """
        agent_run_response = self.agents_api.get_agent_run_v1_organizations_org_id_agent_run_agent_run_id_get(
            agent_run_id=agent_run_id,
            org_id=int(self.org_id),
            authorization=f"Bearer {self.token}"
        )
        
        return AgentTask(agent_run_response, self.api_client, self.org_id)

    def get_status(self) -> Optional[dict[str, Any]]:
        """Get the status of the current job.

        Returns:
            dict: A dictionary containing job status information,
                  or None if no job has been run.
        """
        if self.current_job:
            self.current_job.refresh()
            return self.current_job.to_dict()
        return None

    def list_agent_runs(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """List agent runs for the organization.

        Args:
            limit: Maximum number of runs to return
            offset: Number of runs to skip

        Returns:
            list: List of agent run dictionaries
        """
        # Note: This would need to be implemented based on the actual API
        # For now, returning empty list as placeholder
        return []

    def cancel_agent_run(self, agent_run_id: int) -> bool:
        """Cancel a running agent run.

        Args:
            agent_run_id: The ID of the agent run to cancel

        Returns:
            bool: True if cancellation was successful
        """
        # Note: This would need to be implemented based on the actual API
        # For now, returning False as placeholder
        return False
