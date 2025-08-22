"""
Codegen API Client.

A Python client for interacting with the Codegen API.
"""

from codegen_client.client import CodegenClient
from codegen_client.exceptions import (
    CodegenApiError,
    CodegenAuthError,
    CodegenRateLimitError,
    CodegenResourceNotFoundError,
    CodegenValidationError,
)
from codegen_client.models.agents import AgentRun, AgentRunResponse
from codegen_client.models.multi_run import MultiRunRequest, MultiRunResponse
from codegen_client.models.organizations import Organization, OrganizationResponse
from codegen_client.models.repositories import Repository, RepositoryResponse
from codegen_client.models.users import User, UserResponse

__all__ = [
    "CodegenClient",
    "CodegenApiError",
    "CodegenAuthError",
    "CodegenRateLimitError",
    "CodegenResourceNotFoundError",
    "CodegenValidationError",
    "AgentRun",
    "AgentRunResponse",
    "MultiRunRequest",
    "MultiRunResponse",
    "Organization",
    "OrganizationResponse",
    "Repository",
    "RepositoryResponse",
    "User",
    "UserResponse",
]

__version__ = "0.1.0"

