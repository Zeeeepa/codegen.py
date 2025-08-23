"""
Tests for the unified backend package.

This module provides tests for the unified backend package,
ensuring that all functionality works as expected.
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unified_backend import APIClient, Config, Storage, NotificationManager

class TestConfig(unittest.TestCase):
    """Tests for the Config class."""
    
    def setUp(self):
        """Set up the test."""
        # Create a temporary config file
        self.config_file = "test_config.json"
        
        # Create a config object
        self.config = Config(self.config_file)
    
    def tearDown(self):
        """Tear down the test."""
        # Remove the temporary config file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    def test_get_set(self):
        """Test get and set methods."""
        # Set a value
        self.config.set("test", "key", "value")
        
        # Get the value
        value = self.config.get("test", "key")
        
        # Check the value
        self.assertEqual(value, "value")
    
    def test_get_default(self):
        """Test get method with default value."""
        # Get a non-existent value
        value = self.config.get("test", "non_existent", "default")
        
        # Check the value
        self.assertEqual(value, "default")
    
    def test_save_load(self):
        """Test save and load methods."""
        # Set a value
        self.config.set("test", "key", "value")
        
        # Save the config
        self.config.save()
        
        # Create a new config object
        config2 = Config(self.config_file)
        
        # Get the value
        value = config2.get("test", "key")
        
        # Check the value
        self.assertEqual(value, "value")
    
    def test_get_api_token(self):
        """Test get_api_token method."""
        # Set an API token
        self.config.set("api", "codegen_api_token", "token")
        
        # Get the API token
        token = self.config.get_api_token()
        
        # Check the token
        self.assertEqual(token, "token")
    
    def test_get_org_id(self):
        """Test get_org_id method."""
        # Set an organization ID
        self.config.set("api", "codegen_org_id", "org_id")
        
        # Get the organization ID
        org_id = self.config.get_org_id()
        
        # Check the organization ID
        self.assertEqual(org_id, "org_id")

class TestStorage(unittest.TestCase):
    """Tests for the Storage class."""
    
    def setUp(self):
        """Set up the test."""
        # Create a temporary storage file
        self.storage_file = "test_storage.json"
        
        # Create a storage object
        self.storage = Storage(self.storage_file)
    
    def tearDown(self):
        """Tear down the test."""
        # Remove the temporary storage file
        if os.path.exists(self.storage_file):
            os.remove(self.storage_file)
    
    def test_save_load(self):
        """Test save and load methods."""
        # Save a value
        self.storage.save("key", "value")
        
        # Load the value
        value = self.storage.load("key")
        
        # Check the value
        self.assertEqual(value, "value")
    
    def test_load_default(self):
        """Test load method with default value."""
        # Load a non-existent value
        value = self.storage.load("non_existent", "default")
        
        # Check the value
        self.assertEqual(value, "default")
    
    def test_delete(self):
        """Test delete method."""
        # Save a value
        self.storage.save("key", "value")
        
        # Delete the value
        self.storage.delete("key")
        
        # Load the value
        value = self.storage.load("key", "default")
        
        # Check the value
        self.assertEqual(value, "default")
    
    def test_clear(self):
        """Test clear method."""
        # Save some values
        self.storage.save("key1", "value1")
        self.storage.save("key2", "value2")
        
        # Clear the storage
        self.storage.clear()
        
        # Load the values
        value1 = self.storage.load("key1", "default")
        value2 = self.storage.load("key2", "default")
        
        # Check the values
        self.assertEqual(value1, "default")
        self.assertEqual(value2, "default")

class TestAPIClient(unittest.TestCase):
    """Tests for the APIClient class."""
    
    def setUp(self):
        """Set up the test."""
        # Create a mock config
        self.config = MagicMock()
        self.config.get_api_token.return_value = "token"
        
        # Create an API client
        self.api_client = APIClient(self.config)
    
    @patch("unified_backend.client.requests.get")
    def test_get_organizations(self, mock_get):
        """Test get_organizations method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "org_id", "name": "org_name"}]}
        mock_get.return_value = mock_response
        
        # Call the method
        orgs = self.api_client.get_organizations()
        
        # Check the result
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0]["id"], "org_id")
        self.assertEqual(orgs[0]["name"], "org_name")
        
        # Check the mock
        mock_get.assert_called_once_with(
            "https://api.codegen.com/v1/organizations",
            headers={"Authorization": "Bearer token"}
        )
    
    @patch("unified_backend.client.requests.get")
    def test_get_repositories(self, mock_get):
        """Test get_repositories method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "repo_id", "name": "repo_name"}]}
        mock_get.return_value = mock_response
        
        # Call the method
        repos = self.api_client.get_repositories("org_id")
        
        # Check the result
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["id"], "repo_id")
        self.assertEqual(repos[0]["name"], "repo_name")
        
        # Check the mock
        mock_get.assert_called_once_with(
            "https://api.codegen.com/v1/repositories?organization_id=org_id",
            headers={"Authorization": "Bearer token"}
        )
    
    @patch("unified_backend.client.requests.get")
    def test_list_agent_runs(self, mock_get):
        """Test list_agent_runs method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": "run_id", "status": "RUNNING"}]}
        mock_get.return_value = mock_response
        
        # Call the method
        response = self.api_client.list_agent_runs("org_id")
        
        # Check the result
        self.assertEqual(len(response["items"]), 1)
        self.assertEqual(response["items"][0]["id"], "run_id")
        self.assertEqual(response["items"][0]["status"], "RUNNING")
        
        # Check the mock
        mock_get.assert_called_once_with(
            "https://api.codegen.com/v1/agents?organization_id=org_id",
            headers={"Authorization": "Bearer token"}
        )
    
    @patch("unified_backend.client.requests.get")
    def test_get_agent_run(self, mock_get):
        """Test get_agent_run method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "run_id", "status": "RUNNING"}
        mock_get.return_value = mock_response
        
        # Call the method
        run = self.api_client.get_agent_run("org_id", "run_id")
        
        # Check the result
        self.assertEqual(run["id"], "run_id")
        self.assertEqual(run["status"], "RUNNING")
        
        # Check the mock
        mock_get.assert_called_once_with(
            "https://api.codegen.com/v1/agents/run_id?organization_id=org_id",
            headers={"Authorization": "Bearer token"}
        )
    
    @patch("unified_backend.client.requests.post")
    def test_create_agent_run(self, mock_post):
        """Test create_agent_run method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "run_id", "status": "RUNNING"}
        mock_post.return_value = mock_response
        
        # Call the method
        run = self.api_client.create_agent_run("org_id", "prompt")
        
        # Check the result
        self.assertEqual(run["id"], "run_id")
        self.assertEqual(run["status"], "RUNNING")
        
        # Check the mock
        mock_post.assert_called_once_with(
            "https://api.codegen.com/v1/agents",
            headers={"Authorization": "Bearer token"},
            json={
                "organization_id": "org_id",
                "prompt": "prompt",
                "model": None,
                "repo_id": None,
                "prorun": False,
                "candidates": 10,
                "agent_models": None,
                "synthesis_template": None
            }
        )
    
    @patch("unified_backend.client.requests.post")
    def test_resume_agent_run(self, mock_post):
        """Test resume_agent_run method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Call the method
        self.api_client.resume_agent_run("org_id", "run_id")
        
        # Check the mock
        mock_post.assert_called_once_with(
            "https://api.codegen.com/v1/agents/run_id/resume",
            headers={"Authorization": "Bearer token"},
            json={"organization_id": "org_id"}
        )
    
    @patch("unified_backend.client.requests.post")
    def test_ban_all_checks_for_agent_run(self, mock_post):
        """Test ban_all_checks_for_agent_run method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Call the method
        self.api_client.ban_all_checks_for_agent_run("org_id", "run_id")
        
        # Check the mock
        mock_post.assert_called_once_with(
            "https://api.codegen.com/v1/agents/run_id/ban_all_checks",
            headers={"Authorization": "Bearer token"},
            json={"organization_id": "org_id"}
        )
    
    @patch("unified_backend.client.requests.post")
    def test_unban_all_checks_for_agent_run(self, mock_post):
        """Test unban_all_checks_for_agent_run method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Call the method
        self.api_client.unban_all_checks_for_agent_run("org_id", "run_id")
        
        # Check the mock
        mock_post.assert_called_once_with(
            "https://api.codegen.com/v1/agents/run_id/unban_all_checks",
            headers={"Authorization": "Bearer token"},
            json={"organization_id": "org_id"}
        )
    
    @patch("unified_backend.client.requests.post")
    def test_remove_codegen_from_pr(self, mock_post):
        """Test remove_codegen_from_pr method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Call the method
        self.api_client.remove_codegen_from_pr("org_id", "run_id")
        
        # Check the mock
        mock_post.assert_called_once_with(
            "https://api.codegen.com/v1/agents/run_id/remove_codegen_from_pr",
            headers={"Authorization": "Bearer token"},
            json={"organization_id": "org_id"}
        )
    
    @patch("unified_backend.client.requests.post")
    def test_generate_setup_commands(self, mock_post):
        """Test generate_setup_commands method."""
        # Set up the mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"commands": ["command1", "command2"]}
        mock_post.return_value = mock_response
        
        # Call the method
        commands = self.api_client.generate_setup_commands("org_id", "repo_id")
        
        # Check the result
        self.assertEqual(len(commands["commands"]), 2)
        self.assertEqual(commands["commands"][0], "command1")
        self.assertEqual(commands["commands"][1], "command2")
        
        # Check the mock
        mock_post.assert_called_once_with(
            "https://api.codegen.com/v1/setup-commands",
            headers={"Authorization": "Bearer token"},
            json={"organization_id": "org_id", "repo_id": "repo_id"}
        )

class TestNotificationManager(unittest.TestCase):
    """Tests for the NotificationManager class."""
    
    def setUp(self):
        """Set up the test."""
        # Create a notification manager
        self.notification_manager = NotificationManager()
    
    @patch("unified_backend.utils.notification.threading.Thread")
    def test_start_polling(self, mock_thread):
        """Test start_polling method."""
        # Create a mock API client
        api_client = MagicMock()
        
        # Call the method
        self.notification_manager.start_polling(api_client, "org_id")
        
        # Check the mock
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
    
    def test_stop_polling(self):
        """Test stop_polling method."""
        # Set is_polling to True
        self.notification_manager.is_polling = True
        
        # Call the method
        self.notification_manager.stop_polling()
        
        # Check the result
        self.assertFalse(self.notification_manager.is_polling)

if __name__ == "__main__":
    unittest.main()

