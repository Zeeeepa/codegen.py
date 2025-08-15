#!/usr/bin/env python3
"""
Unit tests for the Codegen MCP Server implementation
"""

import asyncio
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

# Add parent directory to path to import codegen_api
sys.path.insert(0, str(Path(__file__).parent.parent))

from codegenapi_server import CodegenMCPServer
from mcp_types import TextContent

# Mock Task class for testing
class MockTask:
    def __init__(self, task_id, status="running"):
        self.id = task_id
        self.status = status
        self.web_url = f"https://codegen.com/tasks/{task_id}"
        self.response = None
    
    def refresh(self):
        # Simulate task completion after refresh
        if self.status == "running":
            self.status = "completed"
            self.response = "Task completed successfully"
    
    def resume(self, prompt):
        return self

# Mock Agent class for testing
class MockAgent:
    def __init__(self, *args, **kwargs):
        self.tasks = {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def run(self, prompt, metadata=None):
        task_id = len(self.tasks) + 1
        task = MockTask(task_id)
        self.tasks[task_id] = task
        return task
    
    def get_task(self, task_id):
        if task_id not in self.tasks:
            self.tasks[task_id] = MockTask(task_id)
        return self.tasks[task_id]

class TestCodegenMCPServer(unittest.TestCase):
    """Test cases for CodegenMCPServer"""
    
    def setUp(self):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["CODEGEN_API_TOKEN"] = "test_token"
        os.environ["CODEGEN_ORG_ID"] = "test_org_id"
        
        # Create server instance
        self.server = CodegenMCPServer()
        
        # Mock _get_agent method to return MockAgent
        self.server._get_agent = mock.MagicMock(return_value=MockAgent())
        
        # Mock _save_relationships to avoid file operations
        self.server._save_relationships = mock.MagicMock()
    
    def test_new_command_happy_path(self):
        """Test new command with valid inputs"""
        args = {
            "repo": "Zeeeepa/codegen.py",
            "task": "TEST",
            "query": "Test query"
        }
        
        # Run the command
        result = asyncio.run(self.server._handle_new(args))
        
        # Check result
        self.assertIsInstance(result.content[0], TextContent)
        content = json.loads(result.content[0].text)
        self.assertTrue(content["success"])
        self.assertIn("agent_run_id", content)
        self.assertEqual(content["status"], "running")
    
    def test_new_command_with_parent_id(self):
        """Test new command with parent_id for orchestration"""
        args = {
            "repo": "Zeeeepa/codegen.py",
            "task": "TEST",
            "query": "Test query",
            "parent_id": 123
        }
        
        # Mock _register_parent_child
        self.server._register_parent_child = mock.MagicMock()
        
        # Run the command
        result = asyncio.run(self.server._handle_new(args))
        
        # Check result
        content = json.loads(result.content[0].text)
        self.assertTrue(content["success"])
        
        # Check that _register_parent_child was called
        self.assertTrue(self.server._register_parent_child.called)
    
    def test_new_command_wait_for_completion(self):
        """Test new command with wait_for_completion"""
        args = {
            "repo": "Zeeeepa/codegen.py",
            "task": "TEST",
            "query": "Test query",
            "wait_for_completion": True
        }
        
        # Mock _mark_run_completed
        self.server._mark_run_completed = mock.MagicMock()
        
        # Run the command
        result = asyncio.run(self.server._handle_new(args))
        
        # Check result
        content = json.loads(result.content[0].text)
        self.assertTrue(content["success"])
        self.assertEqual(content["status"], "completed")
        
        # Check that _mark_run_completed was called
        self.assertTrue(self.server._mark_run_completed.called)
    
    def test_resume_command_happy_path(self):
        """Test resume command with valid inputs"""
        args = {
            "agent_run_id": 123,
            "query": "Resume query"
        }
        
        # Run the command
        result = asyncio.run(self.server._handle_resume(args))
        
        # Check result
        content = json.loads(result.content[0].text)
        self.assertTrue(content["success"])
        self.assertEqual(content["agent_run_id"], 123)
    
    def test_resume_command_wait_for_completion(self):
        """Test resume command with wait_for_completion"""
        args = {
            "agent_run_id": 123,
            "query": "Resume query",
            "wait_for_completion": True
        }
        
        # Mock _mark_run_completed
        self.server._mark_run_completed = mock.MagicMock()
        
        # Run the command
        result = asyncio.run(self.server._handle_resume(args))
        
        # Check result
        content = json.loads(result.content[0].text)
        self.assertTrue(content["success"])
        self.assertEqual(content["status"], "completed")
        
        # Check that _mark_run_completed was called
        self.assertTrue(self.server._mark_run_completed.called)
    
    def test_register_parent_child(self):
        """Test _register_parent_child method"""
        parent_id = 123
        child_id = 456
        
        # Call the method
        self.server._register_parent_child(parent_id, child_id)
        
        # Check relationships
        parent_id_str = str(parent_id)
        child_id_str = str(child_id)
        
        self.assertIn(parent_id_str, self.server.relationships["parent_child"])
        self.assertIn(child_id_str, self.server.relationships["parent_child"][parent_id_str])
        self.assertEqual(self.server.relationships["child_parent"][child_id_str], parent_id_str)
        self.assertIn(child_id_str, self.server.relationships["active_runs"])
    
    def test_mark_run_completed(self):
        """Test _mark_run_completed method"""
        run_id = 123
        run_id_str = str(run_id)
        
        # Add run to active runs
        self.server.relationships["active_runs"].append(run_id_str)
        
        # Call the method
        self.server._mark_run_completed(run_id)
        
        # Check relationships
        self.assertNotIn(run_id_str, self.server.relationships["active_runs"])
        self.assertIn(run_id_str, self.server.relationships["completed_runs"])
    
    def test_handle_completed_run(self):
        """Test _handle_completed_run method"""
        parent_id = 123
        child_id = 456
        
        # Set up relationships
        self.server._register_parent_child(parent_id, child_id)
        
        # Create mock task
        task = MockTask(child_id, status="completed")
        task.response = "Child task completed"
        
        # Mock agent.get_task
        mock_agent = MockAgent()
        mock_agent.get_task = mock.MagicMock(return_value=MockTask(parent_id))
        self.server._get_agent = mock.MagicMock(return_value=mock_agent)
        
        # Call the method
        self.server._handle_completed_run(task)
        
        # Check that the run was marked as completed
        self.assertIn(str(child_id), self.server.relationships["completed_runs"])
        self.assertNotIn(str(child_id), self.server.relationships["active_runs"])

if __name__ == "__main__":
    unittest.main()
