"""
Codegen API - Python client for the Codegen Agent API.

This package provides a Python client for interacting with the Codegen Agent API,
allowing you to create and manage agent runs, view logs, and more.

Basic usage:
    from codegen import CodegenClient, ClientConfig
    
    # Initialize the client with default configuration
    client = CodegenClient()
    
    # Or with custom configuration
    config = ClientConfig(api_token="your-token", org_id="your-org-id")
    client = CodegenClient(config)
    
    # Create an agent run
    run = client.create_agent_run(
        org_id=123,
        prompt="Help me refactor this code for better performance"
    )
    
    # Get the run status
    run_status = client.get_agent_run(org_id=123, agent_run_id=run.id)
    
    # Get run logs
    logs = client.get_agent_run_logs(org_id=123, agent_run_id=run.id)

For async usage:
    from codegen import AsyncCodegenClient
    
    async with AsyncCodegenClient() as client:
        user = await client.get_current_user()
        # ...
"""

# Import main client classes for easy access
from codegen.client.sync import CodegenClient
from codegen.client.async_client import AsyncCodegenClient
from codegen.config.client_config import ClientConfig, ConfigPresets

# Import common models and exceptions for convenience
from codegen.models.enums import SourceType, MessageType, AgentRunStatus, LogLevel
from codegen.exceptions.api_exceptions import (
    CodegenAPIError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
)

# Define package metadata
__version__ = "0.1.0"
__author__ = "Codegen Team"
__email__ = "support@codegen.com"
__all__ = [
    "CodegenClient",
    "AsyncCodegenClient",
    "ClientConfig",
    "ConfigPresets",
    "SourceType",
    "MessageType",
    "AgentRunStatus",
    "LogLevel",
    "CodegenAPIError",
    "ValidationError",
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError",
]

