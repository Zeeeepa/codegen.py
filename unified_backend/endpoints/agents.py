"""
Agents endpoint for the Codegen Agent API.

This module provides the agents endpoint for the Codegen Agent API.
"""

from typing import Dict, List, Optional, Any, Union
from unified_backend.models.agent_run import AgentRun


class AgentsEndpoint:
    """Agents endpoint for the Codegen Agent API."""
    
    def __init__(self, client):
        """
        Initialize the agents endpoint.
        
        Args:
            client: Codegen client
        """
        self.client = client
        
    def create_agent_run(
        self,
        prompt: str,
        repo_id: Optional[str] = None,
        model: Optional[str] = None,
        org_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an agent run.
        
        Args:
            prompt: Prompt for the agent
            repo_id: Repository ID
            model: Model to use
            org_id: Organization ID (optional, uses default if not provided)
            **kwargs: Additional parameters
            
        Returns:
            Agent run creation result
        """
        return self.client.create_agent_run(
            prompt=prompt,
            repo_id=repo_id,
            model=model,
            org_id=org_id,
            **kwargs
        )
        
    def get_agent_run(
        self,
        agent_run_id: str,
        org_id: Optional[str] = None
    ) -> Optional[AgentRun]:
        """
        Get an agent run.
        
        Args:
            agent_run_id: Agent run ID
            org_id: Organization ID (optional, uses default if not provided)
            
        Returns:
            Agent run or None if not found
        """
        return self.client.get_agent_run(agent_run_id, org_id)
        
    def list_agent_runs(
        self,
        org_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AgentRun]:
        """
        List agent runs.
        
        Args:
            org_id: Organization ID (optional, uses default if not provided)
            status: Filter by status
            limit: Maximum number of runs to return
            offset: Offset for pagination
            
        Returns:
            List of agent runs
        """
        return self.client.list_agent_runs(org_id, status, limit, offset)
        
    def resume_agent_run(
        self,
        agent_run_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resume an agent run.
        
        Args:
            agent_run_id: Agent run ID
            org_id: Organization ID (optional, uses default if not provided)
            
        Returns:
            Resume result
        """
        return self.client.resume_agent_run(agent_run_id, org_id)
        
    def ban_all_checks_for_agent_run(
        self,
        agent_run_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ban all checks for an agent run.
        
        Args:
            agent_run_id: Agent run ID
            org_id: Organization ID (optional, uses default if not provided)
            
        Returns:
            Ban result
        """
        return self.client.ban_all_checks_for_agent_run(agent_run_id, org_id)
        
    def unban_all_checks_for_agent_run(
        self,
        agent_run_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unban all checks for an agent run.
        
        Args:
            agent_run_id: Agent run ID
            org_id: Organization ID (optional, uses default if not provided)
            
        Returns:
            Unban result
        """
        return self.client.unban_all_checks_for_agent_run(agent_run_id, org_id)
        
    def remove_codegen_from_pr(
        self,
        agent_run_id: str,
        org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Remove Codegen from PR.
        
        Args:
            agent_run_id: Agent run ID
            org_id: Organization ID (optional, uses default if not provided)
            
        Returns:
            Remove result
        """
        return self.client.remove_codegen_from_pr(agent_run_id, org_id)
        
    def get_agent_run_logs(
        self,
        agent_run_id: str,
        org_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get agent run logs.
        
        Args:
            agent_run_id: Agent run ID
            org_id: Organization ID (optional, uses default if not provided)
            
        Returns:
            Agent run logs
        """
        return self.client.get_agent_run_logs(agent_run_id, org_id)
        
    def star_agent_run(self, agent_run_id: str) -> Dict[str, Any]:
        """
        Star an agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            Star result
        """
        return self.client.star_agent_run(agent_run_id)
        
    def unstar_agent_run(self, agent_run_id: str) -> Dict[str, Any]:
        """
        Unstar an agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            Unstar result
        """
        return self.client.unstar_agent_run(agent_run_id)
        
    def get_starred_agent_runs(
        self,
        org_id: Optional[str] = None
    ) -> List[AgentRun]:
        """
        Get starred agent runs.
        
        Args:
            org_id: Organization ID (optional, uses default if not provided)
            
        Returns:
            List of starred agent runs
        """
        return self.client.get_starred_agent_runs(org_id)
        
    def is_agent_run_starred(self, agent_run_id: str) -> bool:
        """
        Check if an agent run is starred.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if starred, False otherwise
        """
        return self.client.is_agent_run_starred(agent_run_id)

