"""
Unit tests for Codegen MCP server
"""

import os
import json
import unittest
import tempfile
from unittest import mock
from typing import Dict, Any, Optional

# Set up test environment
os.environ["CODEGEN_API_TOKEN"] = "test_token"
os.environ["CODEGEN_ORG_ID"] = "test_org_id"

# Import server components
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from codegen_client import CodegenClient
from state_manager import StateManager

class TestConfig(unittest.TestCase):
    """Test the Config class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="codegen_test")
        self.config_file = os.path.join(self.test_dir, "config.json")
    
    def test_init(self):
        """Test initialization"""
        config = Config(self.config_file)
        self.assertIsNotNone(config)
    
    def test_get_set(self):
        """Test get and set methods"""
        config = Config(self.config_file)
        config.set("test_key", "test_value")
        self.assertEqual(config.get("test_key"), "test_value")
    
    def test_validate(self):
        """Test validate method"""
        config = Config(self.config_file)
        config.set("api_token", "test_token")
        config.set("org_id", "test_org_id")
        self.assertTrue(config.validate())

class TestCodegenClient(unittest.TestCase):
    """Test the CodegenClient class"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = CodegenClient(
            org_id="test_org_id",
            api_token="test_token",
            base_url="https://api.codegen.com"
        )
    
    @mock.patch("requests.get")
    def test_get_users(self, mock_get):
        """Test get_users method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": "user1", "name": "User 1"},
                {"id": "user2", "name": "User 2"}
            ],
            "total": 2
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_users()
        
        # Verify result
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0]["id"], "user1")
        
        # Verify request
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["limit"], 100)
    
    @mock.patch("requests.get")
    def test_get_user(self, mock_get):
        """Test get_user method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "user1",
            "name": "User 1",
            "email": "user1@example.com"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_user("user1")
        
        # Verify result
        self.assertEqual(result["id"], "user1")
        self.assertEqual(result["name"], "User 1")
        
        # Verify request
        mock_get.assert_called_once()
    
    @mock.patch("requests.get")
    def test_get_current_user(self, mock_get):
        """Test get_current_user method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "current_user",
            "name": "Current User",
            "email": "current@example.com"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_current_user()
        
        # Verify result
        self.assertEqual(result["id"], "current_user")
        self.assertEqual(result["name"], "Current User")
        
        # Verify request
        mock_get.assert_called_once()
    
    @mock.patch("requests.get")
    def test_get_organizations(self, mock_get):
        """Test get_organizations method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": "org1", "name": "Organization 1"},
                {"id": "org2", "name": "Organization 2"}
            ],
            "total": 2
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_organizations()
        
        # Verify result
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0]["id"], "org1")
        
        # Verify request
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["limit"], 100)
    
    @mock.patch("requests.post")
    def test_create_agent_run(self, mock_post):
        """Test create_agent_run method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "run1",
            "status": "running",
            "web_url": "https://codegen.com/runs/run1"
        }
        mock_post.return_value = mock_response
        
        # Call method
        result = self.client.create_agent_run(
            prompt="Test prompt",
            repo="test/repo",
            branch="main",
            task="TEST"
        )
        
        # Verify result
        self.assertEqual(result["id"], "run1")
        self.assertEqual(result["status"], "running")
        
        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["prompt"], "Test prompt")
        self.assertEqual(kwargs["json"]["metadata"]["repo"], "test/repo")
    
    @mock.patch("requests.get")
    def test_get_agent_run(self, mock_get):
        """Test get_agent_run method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "run1",
            "status": "running",
            "web_url": "https://codegen.com/runs/run1"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_agent_run("run1")
        
        # Verify result
        self.assertEqual(result["id"], "run1")
        self.assertEqual(result["status"], "running")
        
        # Verify request
        mock_get.assert_called_once()
    
    @mock.patch("requests.post")
    def test_resume_agent_run(self, mock_post):
        """Test resume_agent_run method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "run1",
            "status": "running",
            "web_url": "https://codegen.com/runs/run1"
        }
        mock_post.return_value = mock_response
        
        # Call method
        result = self.client.resume_agent_run(
            agent_run_id="run1",
            prompt="Resume prompt",
            task="TEST"
        )
        
        # Verify result
        self.assertEqual(result["id"], "run1")
        self.assertEqual(result["status"], "running")
        
        # Verify request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["agent_run_id"], "run1")
        self.assertEqual(kwargs["json"]["prompt"], "Resume prompt")
    
    @mock.patch("requests.get")
    def test_get_agent_run_logs(self, mock_get):
        """Test get_agent_run_logs method"""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"id": "log1", "message": "Log 1"},
                {"id": "log2", "message": "Log 2"}
            ],
            "total": 2
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_agent_run_logs("run1")
        
        # Verify result
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0]["id"], "log1")
        
        # Verify request
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["limit"], 100)

class TestStateManager(unittest.TestCase):
    """Test the StateManager class"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp(prefix="codegen_test")
        self.state_manager = StateManager(self.test_dir)
    
    def test_register_run(self):
        """Test register_run method"""
        self.state_manager.register_run(
            run_id="run1",
            orchestrator_id="orch1",
            metadata={"test": "value"}
        )
        
        run = self.state_manager.get_run("run1")
        self.assertEqual(run["id"], "run1")
        self.assertEqual(run["orchestrator_id"], "orch1")
        self.assertEqual(run["metadata"]["test"], "value")
    
    def test_update_run_status(self):
        """Test update_run_status method"""
        self.state_manager.register_run(run_id="run1")
        self.state_manager.update_run_status(
            run_id="run1",
            status="completed",
            result={"output": "test"}
        )
        
        run = self.state_manager.get_run("run1")
        self.assertEqual(run["status"], "completed")
        self.assertEqual(run["result"]["output"], "test")

if __name__ == "__main__":
    unittest.main()

