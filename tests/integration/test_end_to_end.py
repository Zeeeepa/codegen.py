"""
End-to-end integration tests
These tests require actual API credentials and should be run separately
"""

import pytest
import os
from codegen import Agent, Task
from codegen.core import ConfigPresets


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("CODEGEN_API_TOKEN") or not os.getenv("CODEGEN_ORG_ID"),
    reason="Integration tests require CODEGEN_API_TOKEN and CODEGEN_ORG_ID environment variables"
)
class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_agent_creation_and_basic_operations(self):
        """Test creating an agent and performing basic operations"""
        # Use development preset for integration tests
        config = ConfigPresets.development()
        
        with Agent(config=config) as agent:
            # Test getting stats
            stats = agent.get_stats()
            assert stats is not None
            
            # Test listing tasks (should not fail even if empty)
            tasks = agent.list_tasks(limit=5)
            assert isinstance(tasks, list)
    
    def test_agent_run_simple_task(self):
        """Test running a simple agent task"""
        config = ConfigPresets.development()
        
        with Agent(config=config) as agent:
            # Run a simple task
            task = agent.run("What is 2 + 2?")
            
            assert isinstance(task, Task)
            assert task.id is not None
            assert task.status is not None
            
            # Test task properties
            assert task.created_at is not None
            assert task.is_running or task.is_completed
    
    def test_task_status_and_logs(self):
        """Test task status checking and log retrieval"""
        config = ConfigPresets.development()
        
        with Agent(config=config) as agent:
            # Get recent tasks
            tasks = agent.list_tasks(limit=1)
            
            if tasks:
                task = tasks[0]
                
                # Test status refresh
                task.refresh()
                assert task.status is not None
                
                # Test log retrieval
                logs = task.get_logs(limit=5)
                assert logs is not None
                assert hasattr(logs, 'logs')
                assert isinstance(logs.logs, list)

