#!/usr/bin/env python3
"""
Unit tests for MCP server components
"""

import os
import sys
import unittest
from unittest import mock
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import components
from config import Config
from codegen_client import CodegenClient
from state_manager import StateManager

class TestConfig(unittest.TestCase):
    """Test the Config class"""
    
    def setUp(self):
        """Set up test environment"""
        # Use a temporary config file
        self.test_config_dir = Path("/tmp/codegen_test")
        self.test_config_dir.mkdir(parents=True, exist_ok=True)
        self.test_config_file = self.test_config_dir / "config.json"
        
        # Create a test config
        self.config = Config(config_file=self.test_config_file)
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove the test config file
        if self.test_config_file.exists():
            self.test_config_file.unlink()
        
        # Remove the test config directory
        if self.test_config_dir.exists():
            self.test_config_dir.rmdir()
    
    def test_set_get_config(self):
        """Test setting and getting config values"""
        # Set a config value
        self.config.set("test_key", "test_value")
        
        # Get the config value
        value = self.config.get("test_key")
        
        # Check the value
        self.assertEqual(value, "test_value")
    
    def test_validate_config(self):
        """Test validating config"""
        # Set required config values
        self.config.set("org_id", "123")
        self.config.set("api_token", "test_token")
        
        # Validate the config
        is_valid = self.config.validate()
        
        # Check the result
        self.assertTrue(is_valid)
    
    def test_validate_config_missing_values(self):
        """Test validating config with missing values"""
        # Clear the config
        self.config.set("org_id", None)
        self.config.set("api_token", None)
        
        # Validate the config
        is_valid = self.config.validate()
        
        # Check the result
        self.assertFalse(is_valid)

class TestCodegenClient(unittest.TestCase):
    """Test the CodegenClient class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a test client
        self.client = CodegenClient(
            org_id="123",
            api_token="test_token",
            base_url="https://api.example.com"
        )
    
    @mock.patch("codegen_client.requests.get")
    def test_get_organizations(self, mock_get):
        """Test getting organizations"""
        # Mock the response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": 123,
                    "name": "Test Org",
                    "settings": {
                        "enable_pr_creation": True,
                        "enable_rules_detection": True
                    }
                }
            ],
            "total": 1,
            "page": 1,
            "size": 100,
            "pages": 1
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.client.get_organizations()
        
        # Check the result
        self.assertEqual(result["items"][0]["id"], 123)
        self.assertEqual(result["items"][0]["name"], "Test Org")
    
    @mock.patch("codegen_client.requests.post")
    def test_create_agent_run(self, mock_post):
        """Test creating an agent run"""
        # Mock the response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 456,
            "organization_id": 123,
            "status": "ACTIVE",
            "created_at": "2025-08-13 00:00:00.000000",
            "web_url": "https://codegen.com/agent/trace/456",
            "result": None,
            "source_type": "API",
            "github_pull_requests": [],
            "metadata": {}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.client.create_agent_run(
            prompt="Test prompt",
            metadata={"test": True}
        )
        
        # Check the result
        self.assertEqual(result["id"], 456)
        self.assertEqual(result["status"], "ACTIVE")
    
    @mock.patch("codegen_client.requests.post")
    def test_resume_agent_run(self, mock_post):
        """Test resuming an agent run"""
        # Mock the response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 456,
            "organization_id": 123,
            "status": "ACTIVE",
            "created_at": "2025-08-13 00:00:00.000000",
            "web_url": "https://codegen.com/agent/trace/456",
            "result": None,
            "source_type": "API",
            "github_pull_requests": [],
            "metadata": {}
        }
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.client.resume_agent_run(
            agent_run_id=456,
            prompt="Test prompt"
        )
        
        # Check the result
        self.assertEqual(result["id"], 456)
        self.assertEqual(result["status"], "ACTIVE")

class TestStateManager(unittest.TestCase):
    """Test the StateManager class"""
    
    def setUp(self):
        """Set up test environment"""
        # Use a temporary state directory
        self.test_state_dir = Path("/tmp/codegen_test_state")
        self.test_state_dir.mkdir(parents=True, exist_ok=True)
        self.test_runs_file = self.test_state_dir / "runs.json"
        self.test_orchestrators_file = self.test_state_dir / "orchestrators.json"
        
        # Create a test state manager
        self.state_manager = StateManager(state_dir=self.test_state_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove the test state files
        if self.test_runs_file.exists():
            self.test_runs_file.unlink()
        
        if self.test_orchestrators_file.exists():
            self.test_orchestrators_file.unlink()
        
        # Remove the test state directory
        if self.test_state_dir.exists():
            self.test_state_dir.rmdir()
    
    def test_register_run(self):
        """Test registering a run"""
        # Register a run
        self.state_manager.register_run(
            run_id="test-run-123",
            orchestrator_id="test-orchestrator-456",
            metadata={"test": True}
        )
        
        # Get the run
        run = self.state_manager.get_run("test-run-123")
        
        # Check the run
        self.assertEqual(run["id"], "test-run-123")
        self.assertEqual(run["orchestrator_id"], "test-orchestrator-456")
        self.assertEqual(run["status"], "running")
        self.assertEqual(run["metadata"]["test"], True)
    
    def test_register_orchestrator(self):
        """Test registering an orchestrator"""
        # Register an orchestrator
        self.state_manager.register_orchestrator("test-orchestrator-456")
        
        # Get the orchestrator
        orchestrator = self.state_manager.get_orchestrator("test-orchestrator-456")
        
        # Check the orchestrator
        self.assertEqual(orchestrator["id"], "test-orchestrator-456")
        self.assertEqual(orchestrator["status"], "running")
        self.assertEqual(orchestrator["child_runs"], [])
    
    def test_add_child_to_orchestrator(self):
        """Test adding a child to an orchestrator"""
        # Register an orchestrator
        self.state_manager.register_orchestrator("test-orchestrator-456")
        
        # Add a child to the orchestrator
        self.state_manager.add_child_to_orchestrator(
            orchestrator_id="test-orchestrator-456",
            child_run_id="test-run-123"
        )
        
        # Get the orchestrator
        orchestrator = self.state_manager.get_orchestrator("test-orchestrator-456")
        
        # Check the orchestrator
        self.assertEqual(orchestrator["child_runs"], ["test-run-123"])

if __name__ == "__main__":
    unittest.main()

