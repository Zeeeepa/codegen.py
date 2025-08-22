"""
Models for agent-related API endpoints.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from codegen_client.models.base import PaginatedResponse


class AgentRunStatus(str, Enum):
    """
    Enum for agent run status values.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class GithubPullRequest(BaseModel):
    """
    Model representing a GitHub pull request created by an agent run.

    Attributes:
        id: Pull request ID
        title: Pull request title
        url: URL to the pull request
        created_at: Creation timestamp
        head_branch_name: Name of the head branch
    """

    id: int
    title: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    head_branch_name: Optional[str] = None


class AgentRunCreate(BaseModel):
    """
    Model for creating a new agent run.

    Attributes:
        prompt: The prompt to send to the agent
        images: List of image URLs to include with the prompt
        metadata: Additional metadata for the agent run
        repo_id: Repository ID to associate with the agent run
        model: Model to use for the agent run
    """

    prompt: str
    images: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    repo_id: Optional[int] = None
    model: Optional[str] = None


class AgentRun(BaseModel):
    """
    Model representing an agent run.

    Attributes:
        id: Agent run ID
        organization_id: Organization ID
        status: Current status of the agent run
        created_at: Creation timestamp
        web_url: URL to view the agent run in the web UI
        result: Result of the agent run
        summary: Summary of the agent run
        source_type: Source type of the agent run
        github_pull_requests: List of GitHub pull requests created by the agent run
        metadata: Additional metadata for the agent run
    """

    id: int
    organization_id: int
    status: str
    created_at: str
    web_url: Optional[str] = None
    result: Optional[str] = None
    summary: Optional[str] = None
    source_type: str = "LOCAL"
    github_pull_requests: List[GithubPullRequest] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRunLog(BaseModel):
    """
    Model representing a log entry for an agent run.

    Attributes:
        agent_run_id: Agent run ID
        created_at: Creation timestamp
        tool_name: Name of the tool used
        message_type: Type of message
        thought: Thought process of the agent
        observation: Observation from the tool
        tool_input: Input to the tool
        tool_output: Output from the tool
    """

    agent_run_id: int
    created_at: str
    tool_name: Optional[str] = None
    message_type: Optional[str] = None
    thought: Optional[str] = None
    observation: Dict[str, Any] = Field(default_factory=dict)
    tool_input: Dict[str, Any] = Field(default_factory=dict)
    tool_output: Dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    """
    Model for agent run response with logs.

    Attributes:
        id: Agent run ID
        organization_id: Organization ID
        status: Current status of the agent run
        created_at: Creation timestamp
        web_url: URL to view the agent run in the web UI
        result: Result of the agent run
        metadata: Additional metadata for the agent run
        logs: List of log entries for the agent run
        total_logs: Total number of log entries
        page: Current page number
        size: Number of log entries per page
        pages: Total number of pages
    """

    id: int
    organization_id: int
    status: str
    created_at: str
    web_url: Optional[str] = None
    result: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    logs: List[AgentRunLog] = Field(default_factory=list)
    total_logs: int
    page: int
    size: int
    pages: int

