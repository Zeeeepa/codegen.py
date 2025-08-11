"""
Unit tests for task functionality
"""

import pytest
import time
from unittest.mock import Mock, patch
from codegen.tasks import Task, TaskStatus
from codegen.core import AgentRunResponse, AgentRunWithLogsResponse, AgentRunLogResponse


class TestTaskStatus:
    """Test TaskStatus constants"""
    
    def test_task_status_constants(self):
        """Test task status constants are defined"""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled"


class TestTask:
    """Test Task class"""
    
    def test_task_creation(self, mock_client, sample_agent_run_response):
        """Test task creation"""
        task = Task(mock_client, 123, sample_agent_run_response)
        
        assert task.client == mock_client
        assert task.id == 123
        assert task._data == sample_agent_run_response
    
    def test_task_status_property(self, mock_client, sample_agent_run_response):
        """Test task status property"""
        task = Task(mock_client, 123, sample_agent_run_response)
        
        assert task.status == "completed"
    
    def test_task_status_refresh_when_running(self, mock_client):
        """Test task status refreshes when running"""
        # Create task with running status
        running_response = AgentRunResponse(
            id=123,
            status="running",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:01:00Z",
            source_type="API",
            message="Test prompt"
        )
        
        completed_response = AgentRunResponse(
            id=123,
            status="completed",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:05:00Z",
            source_type="API",
            message="Test prompt",
            result="Test result"
        )
        
        mock_client.get_agent_run.return_value = completed_response
        
        task = Task(mock_client, 123, running_response)
        
        # Accessing status should trigger refresh
        status = task.status
        
        assert status == "completed"
        mock_client.get_agent_run.assert_called_once_with(123)
    
    def test_task_result_property(self, mock_client, sample_agent_run_response):
        """Test task result property"""
        task = Task(mock_client, 123, sample_agent_run_response)
        
        assert task.result == "Test result"
    
    def test_task_error_property(self, mock_client):
        """Test task error property"""
        error_response = AgentRunResponse(
            id=123,
            status="failed",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:05:00Z",
            source_type="API",
            message="Test prompt",
            error="Test error"
        )
        
        task = Task(mock_client, 123, error_response)
        
        assert task.error == "Test error"
    
    def test_task_is_completed_property(self, mock_client, sample_agent_run_response):
        """Test task is_completed property"""
        task = Task(mock_client, 123, sample_agent_run_response)
        
        assert task.is_completed is True
    
    def test_task_is_running_property(self, mock_client):
        """Test task is_running property"""
        running_response = AgentRunResponse(
            id=123,
            status="running",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:01:00Z",
            source_type="API",
            message="Test prompt"
        )
        
        task = Task(mock_client, 123, running_response)
        
        assert task.is_running is True
    
    def test_task_refresh(self, mock_client, sample_agent_run_response):
        """Test task refresh method"""
        task = Task(mock_client, 123)
        mock_client.get_agent_run.return_value = sample_agent_run_response
        
        task.refresh()
        
        assert task._data == sample_agent_run_response
        mock_client.get_agent_run.assert_called_once_with(123)
    
    def test_task_get_logs(self, mock_client, sample_agent_run_response):
        """Test task get_logs method"""
        log_response = AgentRunLogResponse(
            id=1,
            agent_run_id=123,
            message_type="ACTION",
            content="Test log entry",
            created_at="2024-01-01T00:00:00Z"
        )
        
        logs_response = AgentRunWithLogsResponse(
            agent_run=sample_agent_run_response,
            logs=[log_response],
            total_logs=1,
            skip=0,
            limit=100
        )
        
        mock_client.get_agent_run_logs.return_value = logs_response
        
        task = Task(mock_client, 123, sample_agent_run_response)
        logs = task.get_logs(skip=0, limit=10)
        
        assert logs == logs_response
        mock_client.get_agent_run_logs.assert_called_once_with(123, skip=0, limit=10)
    
    @patch('time.sleep')
    def test_task_wait_for_completion_success(self, mock_sleep, mock_client):
        """Test task wait_for_completion with successful completion"""
        # Start with running task
        running_response = AgentRunResponse(
            id=123,
            status="running",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:01:00Z",
            source_type="API",
            message="Test prompt"
        )
        
        completed_response = AgentRunResponse(
            id=123,
            status="completed",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:05:00Z",
            source_type="API",
            message="Test prompt",
            result="Test result"
        )
        
        # Mock get_agent_run to return completed on second call
        mock_client.get_agent_run.side_effect = [running_response, completed_response]
        
        task = Task(mock_client, 123, running_response)
        result = task.wait_for_completion(timeout=30, poll_interval=1)
        
        assert result == completed_response
        assert task._data == completed_response
        mock_sleep.assert_called_with(1)
    
    @patch('time.sleep')
    @patch('time.time')
    def test_task_wait_for_completion_timeout(self, mock_time, mock_sleep, mock_client):
        """Test task wait_for_completion with timeout"""
        # Mock time to simulate timeout
        mock_time.side_effect = [0, 0, 31]  # Start, first check, timeout
        
        running_response = AgentRunResponse(
            id=123,
            status="running",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:01:00Z",
            source_type="API",
            message="Test prompt"
        )
        
        mock_client.get_agent_run.return_value = running_response
        
        task = Task(mock_client, 123, running_response)
        
        with pytest.raises(TimeoutError, match="Task 123 did not complete within 30 seconds"):
            task.wait_for_completion(timeout=30, poll_interval=1)
    
    def test_task_string_representation(self, mock_client, sample_agent_run_response):
        """Test task string representation"""
        task = Task(mock_client, 123, sample_agent_run_response)
        
        assert str(task) == "Task(id=123, status=completed)"
        assert "Task(id=123, status=completed, created_at=2024-01-01T00:00:00Z)" in repr(task)

