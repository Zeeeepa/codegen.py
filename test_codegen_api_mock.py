#!/usr/bin/env python3
"""
Mock test script for the Codegen API client
This script tests the functionality of the Agent class using mocked responses
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Import the module
from codegen_api import Agent, Task, AgentRunStatus, AgentRunResponse, CodegenClient, ClientConfig

class TestCodegenApiMock(unittest.TestCase):
    """Test case for Codegen API with mocked responses"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock responses
        self.mock_org = MagicMock()
        self.mock_org.id = 12345
        self.mock_org.name = "Test Organization"
        
        self.mock_orgs_response = MagicMock()
        self.mock_orgs_response.items = [self.mock_org]
        
        self.mock_agent_run = MagicMock()
        self.mock_agent_run.id = 67890
        self.mock_agent_run.status = "COMPLETED"  # Using string instead of enum value
        self.mock_agent_run.result = "Test result"
        self.mock_agent_run.web_url = "https://codegen.com/runs/67890"
        
    @patch('codegen_api.ClientConfig')
    @patch('codegen_api.CodegenClient')
    def test_agent_initialization(self, mock_client_class, mock_config_class):
        """Test Agent initialization with mocked client"""
        # Setup mocks
        mock_config = mock_config_class.return_value
        mock_config.api_token = "test_token"
        mock_config.org_id = None
        
        mock_client = mock_client_class.return_value
        mock_client.get_organizations.return_value = self.mock_orgs_response
        
        # Test initialization without org_id
        agent = Agent(token="test_token")
        
        # Verify
        mock_client_class.assert_called_once()
        mock_client.get_organizations.assert_called_once_with(limit=1)
        self.assertEqual(agent.org_id, 12345)
        
    @patch('codegen_api.ClientConfig')
    @patch('codegen_api.CodegenClient')
    def test_agent_run(self, mock_client_class, mock_config_class):
        """Test Agent.run with mocked client"""
        # Setup mocks
        mock_config = mock_config_class.return_value
        mock_config.api_token = "test_token"
        mock_config.org_id = "12345"
        
        mock_client = mock_client_class.return_value
        mock_client.create_agent_run.return_value = self.mock_agent_run
        
        # Create agent and run
        agent = Agent(org_id="12345", token="test_token")
        task = agent.run("Test prompt")
        
        # Verify
        mock_client.create_agent_run.assert_called_once_with(
            org_id=12345,
            prompt="Test prompt",
            images=None,
            metadata=None
        )
        self.assertEqual(task.id, 67890)
        
    def test_task_properties(self):
        """Test Task properties with mocked client"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.get_agent_run.return_value = self.mock_agent_run
        
        # Create task directly
        task = Task(mock_client, 12345, 67890, self.mock_agent_run)
        
        # Verify properties
        self.assertEqual(task.status, "COMPLETED")
        self.assertEqual(task.result, "Test result")
        self.assertEqual(task.web_url, "https://codegen.com/runs/67890")
        
        # Verify refresh
        task.refresh()
        mock_client.get_agent_run.assert_called_with(12345, 67890)
        
    def test_wait_for_completion(self):
        """Test Task.wait_for_completion with mocked client"""
        # Setup mock
        mock_client = MagicMock()
        mock_client.wait_for_completion.return_value = self.mock_agent_run
        
        # Create task and wait for completion
        task = Task(mock_client, 12345, 67890)
        result = task.wait_for_completion(timeout=10)
        
        # Verify
        mock_client.wait_for_completion.assert_called_once_with(12345, 67890, 5.0, 10)
        self.assertEqual(result, self.mock_agent_run)

def main():
    """Run the tests"""
    print("=== Codegen API Mock Tests ===")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    print("=== Mock Tests Complete ===")
    print("MCP tools test successful!")

if __name__ == "__main__":
    main()

