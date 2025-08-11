"""
Codegen Integration Layer Interfaces

Defines the contracts for the lowest layer that handles all Codegen API interactions.
This layer is completely independent of UI concerns and business logic.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import datetime


class SourceType(Enum):
    """Source types for agent runs"""
    LOCAL = "LOCAL"
    SLACK = "SLACK"
    GITHUB = "GITHUB"
    GITHUB_CHECK_SUITE = "GITHUB_CHECK_SUITE"
    LINEAR = "LINEAR"
    API = "API"
    CHAT = "CHAT"
    JIRA = "JIRA"


class RunStatus(Enum):
    """Agent run status types"""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"


@dataclass
class AgentRun:
    """Data model for agent runs"""
    id: int
    organization_id: int
    status: Optional[RunStatus]
    prompt: Optional[str]
    result: Optional[str]
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]
    completed_at: Optional[datetime.datetime]
    web_url: Optional[str]
    source_type: Optional[SourceType]
    metadata: Optional[Dict[str, Any]]
    github_pull_requests: Optional[List[Dict[str, Any]]]
    cost: Optional[float]
    tokens_used: Optional[int]
    progress: Optional[int]


@dataclass
class Organization:
    """Data model for organizations"""
    id: int
    name: str
    settings: Dict[str, Any]


@dataclass
class User:
    """Data model for users"""
    id: int
    email: Optional[str]
    github_user_id: str
    github_username: str
    avatar_url: Optional[str]
    full_name: Optional[str]


@dataclass
class AgentRunLog:
    """Data model for agent run logs"""
    agent_run_id: int
    created_at: datetime.datetime
    message_type: str
    thought: Optional[str]
    tool_name: Optional[str]
    tool_input: Optional[Dict[str, Any]]
    tool_output: Optional[Dict[str, Any]]
    observation: Optional[Union[Dict[str, Any], str]]


@dataclass
class PaginatedResponse:
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class ICodegenClient(ABC):
    """
    Interface for Codegen API client.
    
    Handles all direct API interactions with the Codegen service.
    Provides methods for agent runs, organizations, users, and logs.
    """
    
    @abstractmethod
    def get_current_user(self) -> User:
        """Get current authenticated user information"""
        pass
    
    @abstractmethod
    def get_organizations(self, skip: int = 0, limit: int = 100) -> PaginatedResponse:
        """Get organizations for the authenticated user"""
        pass
    
    @abstractmethod
    def create_agent_run(
        self,
        org_id: int,
        prompt: str,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentRun:
        """Create a new agent run"""
        pass
    
    @abstractmethod
    def get_agent_run(self, org_id: int, agent_run_id: int) -> AgentRun:
        """Get details of a specific agent run"""
        pass
    
    @abstractmethod
    def list_agent_runs(
        self,
        org_id: int,
        user_id: Optional[int] = None,
        source_type: Optional[SourceType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse:
        """List agent runs for an organization"""
        pass
    
    @abstractmethod
    def resume_agent_run(
        self,
        org_id: int,
        agent_run_id: int,
        prompt: str,
        images: Optional[List[str]] = None
    ) -> AgentRun:
        """Resume a paused agent run"""
        pass
    
    @abstractmethod
    def get_agent_run_logs(
        self,
        org_id: int,
        agent_run_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse:
        """Get logs for an agent run"""
        pass
    
    @abstractmethod
    def cancel_agent_run(self, org_id: int, agent_run_id: int) -> bool:
        """Cancel an active agent run"""
        pass
    
    @abstractmethod
    def pause_agent_run(self, org_id: int, agent_run_id: int) -> bool:
        """Pause an active agent run"""
        pass


class IAuthManager(ABC):
    """
    Interface for authentication management.
    
    Handles API token validation, refresh, and user session management.
    """
    
    @abstractmethod
    def validate_token(self, token: str) -> bool:
        """Validate an API token"""
        pass
    
    @abstractmethod
    def get_current_token(self) -> Optional[str]:
        """Get the current active token"""
        pass
    
    @abstractmethod
    def set_token(self, token: str) -> None:
        """Set the API token"""
        pass
    
    @abstractmethod
    def clear_token(self) -> None:
        """Clear the stored token"""
        pass
    
    @abstractmethod
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        pass


class ICacheManager(ABC):
    """
    Interface for caching management.
    
    Provides caching capabilities for API responses to improve performance.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value with optional TTL"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete cached value"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass


class IDataTransformer(ABC):
    """
    Interface for data transformation.
    
    Handles conversion between API responses and internal data models.
    """
    
    @abstractmethod
    def transform_agent_run(self, api_data: Dict[str, Any]) -> AgentRun:
        """Transform API response to AgentRun model"""
        pass
    
    @abstractmethod
    def transform_organization(self, api_data: Dict[str, Any]) -> Organization:
        """Transform API response to Organization model"""
        pass
    
    @abstractmethod
    def transform_user(self, api_data: Dict[str, Any]) -> User:
        """Transform API response to User model"""
        pass
    
    @abstractmethod
    def transform_agent_run_log(self, api_data: Dict[str, Any]) -> AgentRunLog:
        """Transform API response to AgentRunLog model"""
        pass
    
    @abstractmethod
    def transform_paginated_response(
        self, 
        api_data: Dict[str, Any], 
        item_transformer: callable
    ) -> PaginatedResponse:
        """Transform paginated API response"""
        pass

