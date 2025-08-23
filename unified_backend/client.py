"""
Unified API client for the Codegen Agent API.

This module provides a unified API client for the Codegen Agent API,
consolidating functionality from multiple existing implementations.
"""

import os
import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

from unified_backend.utils import Config

logger = logging.getLogger(__name__)

class APIError(Exception):
    """API error exception."""
    pass

class APIClient:
    """API client for the Codegen Agent API."""
    
    def __init__(self, config: Config):
        """
        Initialize the API client.
        
        Args:
            config: Configuration manager
        """
        self.config = config
        self.base_url = os.environ.get("CODEGEN_API_URL", "https://api.codegen.com/v1")
        self.session = requests.Session()
        self.lock = Lock()
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers.
        
        Returns:
            Request headers
        """
        token = self.config.get_api_token()
        if not token:
            raise APIError("API token not configured")
        
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        retry_count: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON data
            retry_count: Number of retries
            retry_delay: Delay between retries
            
        Returns:
            Response data
            
        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        for i in range(retry_count):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    return response.json()
                else:
                    error_message = f"API request failed: {response.status_code}"
                    try:
                        error_data = response.json()
                        if "message" in error_data:
                            error_message = f"{error_message} - {error_data['message']}"
                    except:
                        pass
                    
                    if response.status_code == 401:
                        raise APIError("Authentication failed. Check your API token.")
                    elif response.status_code == 403:
                        raise APIError("Permission denied. Check your access rights.")
                    elif response.status_code == 404:
                        raise APIError(f"Resource not found: {endpoint}")
                    elif response.status_code >= 500:
                        if i < retry_count - 1:
                            time.sleep(retry_delay * (i + 1))
                            continue
                        else:
                            raise APIError(f"Server error: {error_message}")
                    else:
                        raise APIError(error_message)
            
            except requests.exceptions.RequestException as e:
                if i < retry_count - 1:
                    time.sleep(retry_delay * (i + 1))
                    continue
                else:
                    raise APIError(f"Request failed: {str(e)}")
        
        raise APIError("Request failed after multiple retries")
    
    # User endpoints
    
    def get_users(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get users in an organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of users
        """
        response = self._make_request("GET", f"/organizations/{org_id}/users")
        return response.get("users", [])
    
    def get_user(self, org_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get details for a specific user.
        
        Args:
            org_id: Organization ID
            user_id: User ID
            
        Returns:
            User details
        """
        response = self._make_request("GET", f"/organizations/{org_id}/users/{user_id}")
        return response
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        Get current user info.
        
        Returns:
            Current user info
        """
        response = self._make_request("GET", "/current-user")
        return response
    
    # Agent endpoints
    
    def create_agent_run(
        self, 
        org_id: str, 
        prompt: str,
        model: Optional[str] = None,
        repo_id: Optional[str] = None,
        prorun: bool = False,
        candidates: int = 10,
        agent_models: Optional[List[str]] = None,
        synthesis_template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an agent run.
        
        Args:
            org_id: Organization ID
            prompt: Prompt text
            model: Model to use
            repo_id: Repository ID
            prorun: Whether to use ProRun mode
            candidates: Number of candidates for ProRun mode
            agent_models: List of agent models for ProRun mode
            synthesis_template: Synthesis template for ProRun mode
            
        Returns:
            Agent run details
        """
        metadata = {}
        
        if repo_id:
            metadata["repo_id"] = repo_id
        
        if model:
            metadata["model"] = model
        
        if prorun:
            metadata["prorun"] = True
            metadata["candidates"] = candidates
            
            if agent_models:
                metadata["agent_models"] = agent_models
            
            if synthesis_template:
                metadata["synthesis_template"] = synthesis_template
        
        data = {
            "prompt": prompt,
            "metadata": metadata
        }
        
        response = self._make_request("POST", f"/organizations/{org_id}/agent/run", json_data=data)
        return response
    
    def get_agent_run(self, org_id: str, agent_run_id: str) -> Dict[str, Any]:
        """
        Get agent run status.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            
        Returns:
            Agent run details
        """
        response = self._make_request("GET", f"/organizations/{org_id}/agent/run/{agent_run_id}")
        return response
    
    def list_agent_runs(
        self, 
        org_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List agent runs.
        
        Args:
            org_id: Organization ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of agent runs
        """
        params = {
            "skip": skip,
            "limit": limit
        }
        
        response = self._make_request("GET", f"/organizations/{org_id}/agent/runs", params=params)
        return response
    
    def resume_agent_run(self, org_id: str, agent_run_id: str) -> Dict[str, Any]:
        """
        Resume agent run.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            
        Returns:
            Agent run details
        """
        response = self._make_request("POST", f"/organizations/{org_id}/agent/run/{agent_run_id}/resume")
        return response
    
    def ban_all_checks_for_agent_run(self, org_id: str, agent_run_id: str) -> Dict[str, Any]:
        """
        Ban all checks for agent run.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            
        Returns:
            Agent run details
        """
        response = self._make_request("POST", f"/organizations/{org_id}/agent/run/{agent_run_id}/ban-all-checks")
        return response
    
    def unban_all_checks_for_agent_run(self, org_id: str, agent_run_id: str) -> Dict[str, Any]:
        """
        Unban all checks for agent run.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            
        Returns:
            Agent run details
        """
        response = self._make_request("POST", f"/organizations/{org_id}/agent/run/{agent_run_id}/unban-all-checks")
        return response
    
    def remove_codegen_from_pr(self, org_id: str, agent_run_id: str) -> Dict[str, Any]:
        """
        Remove Codegen from PR.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            
        Returns:
            Agent run details
        """
        response = self._make_request("POST", f"/organizations/{org_id}/agent/run/{agent_run_id}/remove-codegen-from-pr")
        return response
    
    def get_agent_run_logs(
        self, 
        org_id: str, 
        agent_run_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get agent run logs.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            Agent run logs
        """
        params = {
            "skip": skip,
            "limit": limit
        }
        
        response = self._make_request("GET", f"/organizations/{org_id}/agent/run/{agent_run_id}/logs", params=params)
        return response
    
    # Repository endpoints
    
    def get_repositories(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get repositories.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of repositories
        """
        response = self._make_request("GET", f"/organizations/{org_id}/repos")
        return response.get("repositories", [])
    
    # Organization endpoints
    
    def get_organizations(self) -> List[Dict[str, Any]]:
        """
        Get organizations.
        
        Returns:
            List of organizations
        """
        response = self._make_request("GET", "/organizations")
        return response.get("organizations", [])
    
    # Integration endpoints
    
    def get_organization_integrations(self, org_id: str) -> Dict[str, Any]:
        """
        Get organization integrations.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Organization integrations
        """
        response = self._make_request("GET", f"/organizations/{org_id}/integrations")
        return response
    
    # Setup commands endpoints
    
    def generate_setup_commands(self, org_id: str, repo_id: str) -> Dict[str, Any]:
        """
        Generate setup commands.
        
        Args:
            org_id: Organization ID
            repo_id: Repository ID
            
        Returns:
            Setup commands
        """
        data = {
            "repository_id": repo_id
        }
        
        response = self._make_request("POST", f"/organizations/{org_id}/setup-commands", json_data=data)
        return response
    
    # Template endpoints
    
    def get_templates(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get templates.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of templates
        """
        response = self._make_request("GET", f"/organizations/{org_id}/templates")
        return response.get("templates", [])
    
    def get_template(self, org_id: str, template_id: str) -> Dict[str, Any]:
        """
        Get template.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            
        Returns:
            Template details
        """
        response = self._make_request("GET", f"/organizations/{org_id}/templates/{template_id}")
        return response
    
    def create_template(
        self, 
        org_id: str, 
        name: str, 
        content: str, 
        category: str, 
        description: str
    ) -> Dict[str, Any]:
        """
        Create template.
        
        Args:
            org_id: Organization ID
            name: Template name
            content: Template content
            category: Template category
            description: Template description
            
        Returns:
            Template details
        """
        data = {
            "name": name,
            "content": content,
            "category": category,
            "description": description
        }
        
        response = self._make_request("POST", f"/organizations/{org_id}/templates", json_data=data)
        return response
    
    def update_template(
        self, 
        org_id: str, 
        template_id: str, 
        name: str, 
        content: str, 
        category: str, 
        description: str
    ) -> Dict[str, Any]:
        """
        Update template.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            name: Template name
            content: Template content
            category: Template category
            description: Template description
            
        Returns:
            Template details
        """
        data = {
            "name": name,
            "content": content,
            "category": category,
            "description": description
        }
        
        response = self._make_request("PUT", f"/organizations/{org_id}/templates/{template_id}", json_data=data)
        return response
    
    def delete_template(self, org_id: str, template_id: str) -> Dict[str, Any]:
        """
        Delete template.
        
        Args:
            org_id: Organization ID
            template_id: Template ID
            
        Returns:
            Response data
        """
        response = self._make_request("DELETE", f"/organizations/{org_id}/templates/{template_id}")
        return response
    
    # ProRun configuration endpoints
    
    def get_prorun_configurations(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get ProRun configurations.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of ProRun configurations
        """
        response = self._make_request("GET", f"/organizations/{org_id}/prorun-configurations")
        return response.get("configurations", [])
    
    def get_prorun_configuration(self, org_id: str, config_id: str) -> Dict[str, Any]:
        """
        Get ProRun configuration.
        
        Args:
            org_id: Organization ID
            config_id: Configuration ID
            
        Returns:
            ProRun configuration details
        """
        response = self._make_request("GET", f"/organizations/{org_id}/prorun-configurations/{config_id}")
        return response
    
    def create_prorun_configuration(
        self, 
        org_id: str, 
        name: str, 
        description: str, 
        candidates: int, 
        agent_models: List[str], 
        synthesis_template: str
    ) -> Dict[str, Any]:
        """
        Create ProRun configuration.
        
        Args:
            org_id: Organization ID
            name: Configuration name
            description: Configuration description
            candidates: Number of candidates
            agent_models: List of agent models
            synthesis_template: Synthesis template
            
        Returns:
            ProRun configuration details
        """
        data = {
            "name": name,
            "description": description,
            "candidates": candidates,
            "agent_models": agent_models,
            "synthesis_template": synthesis_template
        }
        
        response = self._make_request("POST", f"/organizations/{org_id}/prorun-configurations", json_data=data)
        return response
    
    def update_prorun_configuration(
        self, 
        org_id: str, 
        config_id: str, 
        name: str, 
        description: str, 
        candidates: int, 
        agent_models: List[str], 
        synthesis_template: str
    ) -> Dict[str, Any]:
        """
        Update ProRun configuration.
        
        Args:
            org_id: Organization ID
            config_id: Configuration ID
            name: Configuration name
            description: Configuration description
            candidates: Number of candidates
            agent_models: List of agent models
            synthesis_template: Synthesis template
            
        Returns:
            ProRun configuration details
        """
        data = {
            "name": name,
            "description": description,
            "candidates": candidates,
            "agent_models": agent_models,
            "synthesis_template": synthesis_template
        }
        
        response = self._make_request("PUT", f"/organizations/{org_id}/prorun-configurations/{config_id}", json_data=data)
        return response
    
    def delete_prorun_configuration(self, org_id: str, config_id: str) -> Dict[str, Any]:
        """
        Delete ProRun configuration.
        
        Args:
            org_id: Organization ID
            config_id: Configuration ID
            
        Returns:
            Response data
        """
        response = self._make_request("DELETE", f"/organizations/{org_id}/prorun-configurations/{config_id}")
        return response
    
    # Starred runs endpoints
    
    def get_starred_runs(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get starred runs.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of starred runs
        """
        response = self._make_request("GET", f"/organizations/{org_id}/starred-runs")
        return response.get("runs", [])
    
    def star_run(self, org_id: str, agent_run_id: str) -> Dict[str, Any]:
        """
        Star a run.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            
        Returns:
            Response data
        """
        data = {
            "agent_run_id": agent_run_id
        }
        
        response = self._make_request("POST", f"/organizations/{org_id}/starred-runs", json_data=data)
        return response
    
    def unstar_run(self, org_id: str, agent_run_id: str) -> Dict[str, Any]:
        """
        Unstar a run.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            
        Returns:
            Response data
        """
        response = self._make_request("DELETE", f"/organizations/{org_id}/starred-runs/{agent_run_id}")
        return response
    
    # Starred projects endpoints
    
    def get_starred_projects(self, org_id: str) -> List[Dict[str, Any]]:
        """
        Get starred projects.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of starred projects
        """
        response = self._make_request("GET", f"/organizations/{org_id}/starred-projects")
        return response.get("projects", [])
    
    def star_project(self, org_id: str, repo_id: str) -> Dict[str, Any]:
        """
        Star a project.
        
        Args:
            org_id: Organization ID
            repo_id: Repository ID
            
        Returns:
            Response data
        """
        data = {
            "repository_id": repo_id
        }
        
        response = self._make_request("POST", f"/organizations/{org_id}/starred-projects", json_data=data)
        return response
    
    def unstar_project(self, org_id: str, repo_id: str) -> Dict[str, Any]:
        """
        Unstar a project.
        
        Args:
            org_id: Organization ID
            repo_id: Repository ID
            
        Returns:
            Response data
        """
        response = self._make_request("DELETE", f"/organizations/{org_id}/starred-projects/{repo_id}")
        return response

