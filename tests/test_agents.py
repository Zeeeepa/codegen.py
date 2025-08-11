"""
Unit tests for agent functionality
"""

import pytest
from unittest.mock import Mock, patch
from codegen.agents import Agent
from codegen.tasks import Task
from codegen.core import AgentRunResponse, AgentRunsResponse


class TestAgent:
    """Test Agent class"""
    
    @patch('codegen.agents.CodegenClient')
    def test_agent_creation(self, mock_client_class):
        """Test agent creation"""
        mock_client = Mock()
        mock_client.org_id = "test-org-123"
        mock_client_class.return_value = mock_client
        
        agent = Agent(org_id="test-org-123", token="test-token")
        
        assert agent.client == mock_client
        assert agent.org_id == "test-org-123"
        mock_client_class.assert_called_once_with(
            org_id="test-org-123", 
            token="test-token", 
            config=None
        )
    
    def test_agent_run(self, mock_agent, sample_agent_run_response):
        """Test agent run method"""
        mock_agent.client.run_agent.return_value = sample_agent_run_response
        
        # Create real agent with mocked client
        agent = Agent.__new__(Agent)
        agent.client = mock_agent.client
        agent.org_id = mock_agent.org_id
        
        task = agent.run("Test prompt")
        
        assert isinstance(task, Task)
        assert task.id == 123
        mock_agent.client.run_agent.assert_called_once_with(prompt="Test prompt")
    
    def test_agent_get_task(self, mock_agent, sample_agent_run_response):
        """Test agent get_task method"""
        mock_agent.client.get_agent_run.return_value = sample_agent_run_response
        
        # Create real agent with mocked client
        agent = Agent.__new__(Agent)
        agent.client = mock_agent.client
        agent.org_id = mock_agent.org_id
        
        task = agent.get_task(123)
        
        assert isinstance(task, Task)
        assert task.id == 123
        mock_agent.client.get_agent_run.assert_called_once_with(123)
    
    def test_agent_list_tasks(self, mock_agent, sample_agent_run_response):
        """Test agent list_tasks method"""
        runs_response = AgentRunsResponse(
            agent_runs=[sample_agent_run_response],
            total=1,
            skip=0,
            limit=10
        )
        mock_agent.client.list_agent_runs.return_value = runs_response
        
        # Create real agent with mocked client
        agent = Agent.__new__(Agent)
        agent.client = mock_agent.client
        agent.org_id = mock_agent.org_id
        
        tasks = agent.list_tasks(limit=10)
        
        assert len(tasks) == 1
        assert isinstance(tasks[0], Task)
        assert tasks[0].id == 123
        mock_agent.client.list_agent_runs.assert_called_once_with(limit=10)
    
    def test_agent_context_manager(self, mock_agent):
        """Test agent as context manager"""
        # Create real agent with mocked client
        agent = Agent.__new__(Agent)
        agent.client = mock_agent.client
        agent.org_id = mock_agent.org_id
        
        with agent as a:
            assert a == agent
        
        # Context manager should not raise any exceptions
    
    def test_agent_get_stats(self, mock_agent):
        """Test agent get_stats method"""
        mock_stats = Mock()
        mock_agent.client.get_stats.return_value = mock_stats
        
        # Create real agent with mocked client
        agent = Agent.__new__(Agent)
        agent.client = mock_agent.client
        agent.org_id = mock_agent.org_id
        
        stats = agent.get_stats()
        
        assert stats == mock_stats
        mock_agent.client.get_stats.assert_called_once()
    
    def test_agent_clear_cache(self, mock_agent):
        """Test agent clear_cache method"""
        # Create real agent with mocked client
        agent = Agent.__new__(Agent)
        agent.client = mock_agent.client
        agent.org_id = mock_agent.org_id
        
        agent.clear_cache()
        
        mock_agent.client.clear_cache.assert_called_once()

