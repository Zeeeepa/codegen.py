"""
Codegen API Client

This module provides a client for the Codegen API with all endpoints.
"""

import time
import enum
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass, field

import requests
from pydantic import BaseModel, Field, HttpUrl, validator, root_validator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enums
class AgentRunStatus(enum.Enum):
    """Agent run status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    ERROR = "ERROR"

class SourceType(enum.Enum):
    """Source type for agent runs."""
    LOCAL = "LOCAL"
    SLACK = "SLACK"
    GITHUB = "GITHUB"
    GITHUB_CHECK_SUITE = "GITHUB_CHECK_SUITE"
    LINEAR = "LINEAR"
    API = "API"
    CHAT = "CHAT"
    JIRA = "JIRA"

# Pydantic Models for Requests and Responses
class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=100)

class GithubPullRequest(BaseModel):
    """GitHub pull request information."""
    id: int
    title: str
    url: str
    created_at: str

class AgentRunResponse(BaseModel):
    """Agent run response."""
    id: int
    organization_id: int
    status: str
    created_at: str
    web_url: str
    result: Optional[str] = None
    source_type: str = "LOCAL"
    github_pull_requests: List[GithubPullRequest] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentRunsResponse(BaseModel):
    """Paginated list of agent runs."""
    items: List[AgentRunResponse]
    total: int
    page: int
    size: int
    pages: int

class CreateAgentRunRequest(BaseModel):
    """Request to create an agent run."""
    prompt: str
    images: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ResumeAgentRunRequest(BaseModel):
    """Request to resume an agent run."""
    prompt: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class User(BaseModel):
    """User information."""
    id: int
    email: str
    github_user_id: Optional[str] = None
    github_username: Optional[str] = None
    avatar_url: Optional[str] = None
    full_name: Optional[str] = None

class UsersResponse(BaseModel):
    """Paginated list of users."""
    items: List[User]
    total: int
    page: int
    size: int
    pages: int

class Organization(BaseModel):
    """Organization information."""
    id: int
    name: str
    slug: str
    created_at: str
    avatar_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class OrganizationsResponse(BaseModel):
    """Paginated list of organizations."""
    items: List[Organization]
    total: int
    page: int
    size: int
    pages: int

class AgentRunLog(BaseModel):
    """Agent run log entry."""
    agent_run_id: int
    created_at: str
    tool_name: Optional[str] = None
    message_type: str
    thought: Optional[str] = None
    observation: Optional[Dict[str, Any]] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None

class AgentRunLogsResponse(BaseModel):
    """Agent run with logs."""
    id: int
    organization_id: int
    status: str
    created_at: str
    web_url: str
    result: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    logs: List[AgentRunLog]
    total_logs: int
    page: int
    size: int
    pages: int

# Client Configuration
class ClientConfig:
    """Client configuration."""
    
    def __init__(self, api_token: str, org_id: str, base_url: str = "https://api.codegen.com/v1"):
        """Initialize client configuration."""
        self.api_token = api_token
        self.org_id = org_id
        self.base_url = base_url

# Codegen API Client
class CodegenClient:
    """Codegen API client."""
    
    def __init__(self, config: ClientConfig):
        """Initialize client."""
        self.config = config
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 402:
            raise Exception("Payment required")
        elif response.status_code == 403:
            raise Exception("Forbidden")
        elif response.status_code == 404:
            raise Exception("Not found")
        elif response.status_code == 422:
            raise Exception("Validation error")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded")
        else:
            raise Exception(f"Unexpected status code: {response.status_code}")
    
    # Users Endpoints
    def get_users(self, skip: int = 0, limit: int = 100) -> UsersResponse:
        """
        Get users in an organization.
        
        Args:
            skip: Number of users to skip (for pagination)
            limit: Maximum number of users to return (1-100)
        
        Returns:
            Paginated list of users
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/users"
        params = {"skip": skip, "limit": limit}
        
        response = requests.get(url, headers=self.get_headers(), params=params)
        data = self._handle_response(response)
        
        return UsersResponse(**data)
    
    def get_user(self, user_id: int) -> User:
        """
        Get details for a specific user in an organization.
        
        Args:
            user_id: ID of the user to retrieve
        
        Returns:
            User details
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/user/{user_id}"
        
        response = requests.get(url, headers=self.get_headers())
        data = self._handle_response(response)
        
        return User(**data)
    
    def get_current_user(self) -> User:
        """
        Get information about the current user.
        
        Returns:
            Current user details
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/user/current"
        
        response = requests.get(url, headers=self.get_headers())
        data = self._handle_response(response)
        
        return User(**data)
    
    # Agents Endpoints
    def create_agent_run(self, prompt: str, images: List[str] = None, metadata: Dict[str, Any] = None) -> AgentRunResponse:
        """
        Create a new agent run.
        
        Args:
            prompt: The prompt for the agent
            images: Optional list of image URLs
            metadata: Optional metadata for the agent run
        
        Returns:
            Created agent run
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/agent/run"
        
        request_data = CreateAgentRunRequest(
            prompt=prompt,
            images=images or [],
            metadata=metadata or {}
        )
        
        response = requests.post(url, headers=self.get_headers(), json=request_data.dict())
        data = self._handle_response(response)
        
        return AgentRunResponse(**data)
    
    def get_agent_run(self, agent_run_id: int) -> AgentRunResponse:
        """
        Get details for a specific agent run.
        
        Args:
            agent_run_id: ID of the agent run to retrieve
        
        Returns:
            Agent run details
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/agent/run/{agent_run_id}"
        
        response = requests.get(url, headers=self.get_headers())
        data = self._handle_response(response)
        
        return AgentRunResponse(**data)
    
    def list_agent_runs(
        self, 
        user_id: Optional[int] = None, 
        source_type: Optional[SourceType] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> AgentRunsResponse:
        """
        List agent runs for an organization.
        
        Args:
            user_id: Optional user ID to filter by
            source_type: Optional source type to filter by
            skip: Number of runs to skip (for pagination)
            limit: Maximum number of runs to return (1-100)
        
        Returns:
            Paginated list of agent runs
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/agent/runs"
        
        params = {"skip": skip, "limit": limit}
        if user_id is not None:
            params["user_id"] = user_id
        if source_type is not None:
            params["source_type"] = source_type.value
        
        response = requests.get(url, headers=self.get_headers(), params=params)
        data = self._handle_response(response)
        
        return AgentRunsResponse(**data)
    
    def resume_agent_run(self, agent_run_id: int, prompt: str, metadata: Dict[str, Any] = None) -> AgentRunResponse:
        """
        Resume a paused agent run.
        
        Args:
            agent_run_id: ID of the agent run to resume
            prompt: Additional instructions for the agent
            metadata: Optional metadata for the agent run
        
        Returns:
            Resumed agent run
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/agent/run/{agent_run_id}/resume"
        
        request_data = ResumeAgentRunRequest(
            prompt=prompt,
            metadata=metadata or {}
        )
        
        response = requests.post(url, headers=self.get_headers(), json=request_data.dict())
        data = self._handle_response(response)
        
        return AgentRunResponse(**data)
    
    # Organizations Endpoints
    def get_organizations(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get organizations the user has access to.
        
        Args:
            skip: Number of organizations to skip (for pagination)
            limit: Maximum number of organizations to return (1-100)
        
        Returns:
            List of organizations
        """
        url = f"{self.config.base_url}/organizations"
        
        params = {"skip": skip, "limit": limit}
        
        response = requests.get(url, headers=self.get_headers(), params=params)
        data = self._handle_response(response)
        
        # Return raw data since the API response doesn't match our model
        return data
    
    # Agents-Alpha Endpoints
    def get_agent_run_logs(
        self, 
        agent_run_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get logs for a specific agent run.
        
        Args:
            agent_run_id: ID of the agent run to retrieve logs for
            skip: Number of logs to skip (for pagination)
            limit: Maximum number of logs to return (1-100)
        
        Returns:
            Agent run with logs
        """
        url = f"{self.config.base_url}/organizations/{self.config.org_id}/agent/run/{agent_run_id}/logs"
        
        params = {"skip": skip, "limit": limit}
        
        response = requests.get(url, headers=self.get_headers(), params=params)
        data = self._handle_response(response)
        
        # Return raw data since the API response doesn't match our model
        return data

# Task class for backward compatibility
class Task:
    """Agent task."""
    
    def __init__(
        self, 
        id: int, 
        agent: 'Agent', 
        status: str = "pending", 
        result: Optional[str] = None, 
        web_url: Optional[str] = None
    ):
        """Initialize task."""
        self.id = id
        self.agent = agent
        self.status = status
        self.result = result
        self.web_url = web_url
    
    def refresh(self) -> 'Task':
        """Refresh task status."""
        agent_run = self.agent.client.get_agent_run(self.id)
        self.status = agent_run.status
        self.result = agent_run.result
        self.web_url = agent_run.web_url
        return self
    
    def wait_for_completion(self, timeout: int = 3600) -> 'Task':
        """Wait for task completion."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.refresh()
            if self.status in [
                AgentRunStatus.COMPLETED.value, 
                AgentRunStatus.FAILED.value, 
                AgentRunStatus.CANCELLED.value,
                AgentRunStatus.COMPLETE.value,
                AgentRunStatus.ERROR.value
            ]:
                return self
            time.sleep(5)  # Poll every 5 seconds
        
        raise TimeoutError(f"Task {self.id} did not complete within {timeout} seconds")
    
    def resume(self, prompt: str) -> 'Task':
        """Resume task."""
        try:
            agent_run = self.agent.client.resume_agent_run(self.id, prompt)
            self.status = agent_run.status
            self.result = agent_run.result
            self.web_url = agent_run.web_url
        except Exception as e:
            logger.warning(f"Error resuming task: {e}")
            # If resume fails, just refresh the task
            self.refresh()
        return self

# Agent class for backward compatibility
class Agent:
    """Codegen agent."""
    
    def __init__(self, org_id: str, token: str, base_url: str = "https://api.codegen.com/v1"):
        """Initialize agent."""
        self.org_id = org_id
        self.token = token
        self.base_url = base_url
        self.client = CodegenClient(ClientConfig(token, org_id, base_url))
    
    def run(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Task:
        """Run agent."""
        agent_run = self.client.create_agent_run(prompt, metadata=metadata)
        return Task(
            id=agent_run.id,
            agent=self,
            status=agent_run.status,
            result=agent_run.result,
            web_url=agent_run.web_url
        )
    
    def get_task(self, task_id: int) -> Task:
        """Get task by ID."""
        agent_run = self.client.get_agent_run(task_id)
        return Task(
            id=agent_run.id,
            agent=self,
            status=agent_run.status,
            result=agent_run.result,
            web_url=agent_run.web_url
        )

