"""
Response models for the Codegen API.

This module contains dataclasses representing responses from the Codegen API.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from codegen.models.enums import SourceType


@dataclass
class UserResponse:
    """Response model for user data."""
    id: int
    email: Optional[str]
    github_user_id: str
    github_username: str
    avatar_url: Optional[str]
    full_name: Optional[str]


@dataclass
class GithubPullRequestResponse:
    """Response model for GitHub pull request data."""
    id: int
    title: str
    url: str
    created_at: str


@dataclass
class AgentRunResponse:
    """Response model for agent run data."""
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
    """Response model for agent run log data."""
    agent_run_id: int
    created_at: str
    message_type: str
    thought: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    observation: Optional[Union[Dict[str, Any], str]] = None


@dataclass
class OrganizationSettings:
    """Response model for organization settings."""
    pass


@dataclass
class OrganizationResponse:
    """Response model for organization data."""
    id: int
    name: str
    settings: OrganizationSettings


@dataclass
class PaginatedResponse:
    """Base response model for paginated data."""
    total: int
    page: int
    size: int
    pages: int


@dataclass
class UsersResponse(PaginatedResponse):
    """Response model for paginated user data."""
    items: List[UserResponse]


@dataclass
class AgentRunsResponse(PaginatedResponse):
    """Response model for paginated agent run data."""
    items: List[AgentRunResponse]


@dataclass
class OrganizationsResponse(PaginatedResponse):
    """Response model for paginated organization data."""
    items: List[OrganizationResponse]


@dataclass
class AgentRunWithLogsResponse:
    """Response model for agent run with logs data."""
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


@dataclass
class RequestMetrics:
    """Metrics for API requests."""
    method: str
    endpoint: str
    status_code: int
    duration_seconds: float
    timestamp: datetime
    request_id: str
    cached: bool = False


@dataclass
class ClientStats:
    """Statistics for the API client."""
    uptime_seconds: float
    total_requests: int
    total_errors: int
    error_rate: float
    requests_per_minute: float
    average_response_time: float
    cache_hit_rate: float
    status_code_distribution: Dict[int, int]
    recent_requests: List[RequestMetrics]


@dataclass
class BulkOperationResult:
    """Result of a bulk operation."""
    total_items: int
    successful_items: int
    failed_items: int
    success_rate: float
    duration_seconds: float
    errors: List[Dict[str, Any]]
    results: List[Any]

