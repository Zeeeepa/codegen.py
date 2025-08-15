"""
Codegen SDK Backend Module

This module contains the core Codegen API client implementation.
"""

from .api import (
    # Core client classes
    CodegenClient,
    Agent,
    Task,
    
    # Configuration
    ClientConfig,
    ConfigPresets,
    
    # Data models
    UserResponse,
    AgentRunResponse,
    AgentRunLogResponse,
    AgentRunWithLogsResponse,
    OrganizationResponse,
    GithubPullRequestResponse,
    
    # Enums
    SourceType,
    MessageType,
    AgentRunStatus,
    
    # Exceptions
    CodegenAPIError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ServerError,
    TimeoutError,
    NetworkError,
    
    # Utility classes
    RateLimiter,
    CacheManager,
    MetricsCollector,
    BulkOperationManager,
)

__version__ = "2.0.0"
__author__ = "Codegen SDK Team"
__email__ = "support@codegen.com"

__all__ = [
    # Core classes
    "CodegenClient",
    "Agent", 
    "Task",
    
    # Configuration
    "ClientConfig",
    "ConfigPresets",
    
    # Data models
    "UserResponse",
    "AgentRunResponse", 
    "AgentRunLogResponse",
    "AgentRunWithLogsResponse",
    "OrganizationResponse",
    "GithubPullRequestResponse",
    
    # Enums
    "SourceType",
    "MessageType", 
    "AgentRunStatus",
    
    # Exceptions
    "CodegenAPIError",
    "ValidationError",
    "RateLimitError", 
    "AuthenticationError",
    "NotFoundError",
    "ServerError",
    "TimeoutError",
    "NetworkError",
    
    # Utility classes
    "RateLimiter",
    "CacheManager",
    "MetricsCollector", 
    "BulkOperationManager",
]
