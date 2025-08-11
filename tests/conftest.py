"""
Pytest configuration and fixtures for Codegen tests
"""

import os
from unittest.mock import MagicMock, Mock

import pytest

from codegen.agents import Agent
from codegen.core import AgentRunResponse, ClientConfig, CodegenClient
from codegen.tasks import Task


@pytest.fixture
def mock_config():
    """Mock client configuration"""
    return ClientConfig(
        timeout=10,
        max_retries=1,
        enable_caching=False,
        enable_metrics=False,
        enable_rate_limiting=False,
    )


@pytest.fixture
def mock_client(mock_config):
    """Mock CodegenClient"""
    client = Mock(spec=CodegenClient)
    client.config = mock_config
    client.org_id = "test-org-123"
    client.token = "test-token-456"
    return client


@pytest.fixture
def mock_agent(mock_client):
    """Mock Agent"""
    agent = Mock(spec=Agent)
    agent.client = mock_client
    agent.org_id = "test-org-123"
    return agent


@pytest.fixture
def sample_agent_run_response():
    """Sample AgentRunResponse for testing"""
    return AgentRunResponse(
        id=123,
        status="completed",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:05:00Z",
        source_type="API",
        message="Test prompt",
        result="Test result",
        error=None,
        github_pull_request=None,
    )


@pytest.fixture
def mock_task(mock_client, sample_agent_run_response):
    """Mock Task"""
    task = Task(mock_client, 123, sample_agent_run_response)
    return task


@pytest.fixture
def temp_config_file(tmp_path):
    """Temporary config file for testing"""
    config_file = tmp_path / "config.json"
    return str(config_file)


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment variables before each test"""
    env_vars = ["CODEGEN_ORG_ID", "CODEGEN_API_TOKEN"]
    original_values = {}

    for var in env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]

    yield

    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value


@pytest.fixture
def set_test_env():
    """Set test environment variables"""
    os.environ["CODEGEN_ORG_ID"] = "test-org-123"
    os.environ["CODEGEN_API_TOKEN"] = "test-token-456"
    yield
    # Cleanup handled by clean_env fixture
