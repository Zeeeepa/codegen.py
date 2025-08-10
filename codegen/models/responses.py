"""
Response models for the Codegen API
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from .enums import SourceType


@dataclass
class UserResponse:
    """User information response"""
    id: int
    email: Optional[str]
    github_user_id: str
    github_username: str
    avatar_url: Optional[str]
    full_name: Optional[str]


@dataclass
class GithubPullRequestResponse:
    """GitHub pull request information"""
    id: int
    title: str
    url: str
    created_at: str


@dataclass
class AgentRunResponse:
    """Agent run response with comprehensive information"""
    id: int
    organization_id: int
    status: Optional[str]
    created_at: Optional[str]
    web_url: Optional[str]
    result: Optional[str]
    source_type: Optional[SourceType]
    github_pull_requests: Optional[List[GithubPullRequestResponse]]
    metadata: Optional[Dict[str, Any]]


@dataclass
class AgentRunLogResponse:
    """Individual log entry for an agent run"""
    agent_run_id: int
    created_at: str
    message_type: str
    thought: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    observation: Optional[Union[Dict[str, Any], str]] = None


@dataclass
class PaginatedResponse:
    """Base class for paginated responses"""
    total: int
    page: int
    size: int
    pages: int


@dataclass
class OrganizationResponse:
    """Organization information response"""
    id: int
    name: str
    settings: Dict[str, Any]


@dataclass
class UsersResponse(PaginatedResponse):
    """Paginated users response"""
    items: List[UserResponse]


@dataclass
class AgentRunsResponse(PaginatedResponse):
    """Paginated agent runs response"""
    items: List[AgentRunResponse]


@dataclass
class OrganizationsResponse(PaginatedResponse):
    """Paginated organizations response"""
    items: List[OrganizationResponse]


@dataclass
class AgentRunWithLogsResponse:
    """Agent run with logs response"""
    id: int
    organization_id: int
    logs: List[AgentRunLogResponse]
    status: Optional[str]
    created_at: Optional[str]
    web_url: Optional[str]
    result: Optional[str]
    metadata: Optional[Dict[str, Any]]
    total_logs: Optional[int]
    page: Optional[int]
    size: Optional[int]
    pages: Optional[int]

