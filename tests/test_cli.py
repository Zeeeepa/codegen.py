"""
Unit tests for CLI functionality
"""

import json
import os
from unittest.mock import Mock, mock_open, patch

import pytest

from codegen.cli import CodegenCLI, create_parser


class TestCodegenCLI:
    """Test CodegenCLI class"""

    def test_cli_creation(self, temp_config_file):
        """Test CLI creation"""
        with patch("codegen.cli.CodegenCLI.load_config") as mock_load:
            mock_load.return_value = {"org_id": "test", "token": "test"}
            cli = CodegenCLI()
            assert cli.config == {"org_id": "test", "token": "test"}

    def test_load_config_file_exists(self, temp_config_file):
        """Test loading config when file exists"""
        config_data = {"org_id": "test-org", "token": "test-token", "preset": "development"}

        with open(temp_config_file, "w") as f:
            json.dump(config_data, f)

        cli = CodegenCLI()
        cli.config_file = temp_config_file
        config = cli.load_config()

        assert config["org_id"] == "test-org"
        assert config["token"] == "test-token"
        assert config["preset"] == "development"

    def test_load_config_file_not_exists(self, temp_config_file):
        """Test loading config when file doesn't exist"""
        cli = CodegenCLI()
        cli.config_file = temp_config_file  # File doesn't exist
        config = cli.load_config()

        # Should return default config
        assert "default_timeout" in config
        assert config["default_timeout"] == 300

    def test_save_config(self, temp_config_file):
        """Test saving config"""
        cli = CodegenCLI()
        cli.config_file = temp_config_file
        cli.config = {"org_id": "test", "token": "test"}

        cli.save_config()

        # Verify file was created and contains correct data
        assert os.path.exists(temp_config_file)
        with open(temp_config_file, "r") as f:
            saved_config = json.load(f)

        assert saved_config["org_id"] == "test"
        assert saved_config["token"] == "test"

    @patch("codegen.cli.CodegenClient")
    def test_get_client(self, mock_client_class, temp_config_file):
        """Test get_client method"""
        cli = CodegenCLI()
        cli.config = {"org_id": "test", "token": "test", "preset": "production"}

        client = cli.get_client()

        mock_client_class.assert_called_once()
        assert cli.client is not None

    @patch("codegen.cli.Agent")
    def test_get_agent(self, mock_agent_class, temp_config_file):
        """Test get_agent method"""
        cli = CodegenCLI()
        cli.config = {"org_id": "test", "token": "test"}

        agent = cli.get_agent()

        mock_agent_class.assert_called_once_with(org_id="test", token="test")
        assert cli.agent is not None


class TestCLICommands:
    """Test CLI command implementations"""

    @patch("codegen.cli.CodegenCLI.get_agent")
    def test_run_command_basic(self, mock_get_agent):
        """Test basic run command"""
        mock_agent = Mock()
        mock_task = Mock()
        mock_task.id = 123
        mock_task.status = "running"
        mock_agent.run.return_value = mock_task
        mock_get_agent.return_value = mock_agent

        cli = CodegenCLI()
        cli.config = {"org_id": "test", "token": "test"}

        # Mock args
        args = Mock()
        args.prompt = "Test prompt"
        args.wait = False

        task = cli.run_command(args)

        assert task == mock_task
        mock_agent.run.assert_called_once_with("Test prompt")

    @patch("codegen.cli.CodegenCLI.get_agent")
    def test_run_command_with_wait(self, mock_get_agent):
        """Test run command with wait option"""
        mock_agent = Mock()
        mock_task = Mock()
        mock_task.id = 123
        mock_task.status = "completed"

        # Mock wait_for_completion result
        mock_result = Mock()
        mock_result.status = "completed"
        mock_result.result = "Test result"
        mock_result.github_pull_request = None
        mock_task.wait_for_completion.return_value = mock_result

        mock_agent.run.return_value = mock_task
        mock_get_agent.return_value = mock_agent

        cli = CodegenCLI()
        cli.config = {"org_id": "test", "token": "test", "default_timeout": 300}

        # Mock args
        args = Mock()
        args.prompt = "Test prompt"
        args.wait = True
        args.timeout = None
        args.poll_interval = None

        task = cli.run_command(args)

        assert task == mock_task
        mock_task.wait_for_completion.assert_called_once_with(timeout=300, poll_interval=5.0)

    @patch("codegen.cli.CodegenCLI.get_agent")
    def test_status_command_specific_task(self, mock_get_agent):
        """Test status command for specific task"""
        mock_agent = Mock()
        mock_task = Mock()
        mock_task.id = 123
        mock_task.status = "completed"
        mock_task.created_at = "2024-01-01T00:00:00Z"
        mock_task.updated_at = "2024-01-01T00:05:00Z"
        mock_task.result = "Test result"
        mock_task.error = None
        mock_task.github_pull_request = None

        mock_agent.get_task.return_value = mock_task
        mock_get_agent.return_value = mock_agent

        cli = CodegenCLI()

        # Mock args
        args = Mock()
        args.task_id = 123
        args.logs = False

        cli.status_command(args)

        mock_agent.get_task.assert_called_once_with(123)

    @patch("codegen.cli.CodegenCLI.get_agent")
    def test_status_command_list_tasks(self, mock_get_agent):
        """Test status command to list tasks"""
        mock_agent = Mock()
        mock_task = Mock()
        mock_task.id = 123
        mock_task.status = "completed"
        mock_task.created_at = "2024-01-01T00:00:00Z"

        mock_agent.list_tasks.return_value = [mock_task]
        mock_get_agent.return_value = mock_agent

        cli = CodegenCLI()

        # Mock args
        args = Mock()
        args.task_id = None
        args.limit = 10

        cli.status_command(args)

        mock_agent.list_tasks.assert_called_once_with(limit=10)


class TestArgumentParser:
    """Test argument parser"""

    def test_create_parser(self):
        """Test parser creation"""
        parser = create_parser()

        assert parser is not None
        assert parser.description == "Codegen Agent Orchestration CLI"

    def test_run_command_parsing(self):
        """Test run command parsing"""
        parser = create_parser()

        args = parser.parse_args(["run", "Test prompt", "--wait"])

        assert args.command == "run"
        assert args.prompt == "Test prompt"
        assert args.wait is True

    def test_status_command_parsing(self):
        """Test status command parsing"""
        parser = create_parser()

        args = parser.parse_args(["status", "--task-id", "123", "--logs"])

        assert args.command == "status"
        assert args.task_id == 123
        assert args.logs is True

    def test_config_command_parsing(self):
        """Test config command parsing"""
        parser = create_parser()

        args = parser.parse_args(["config", "set", "--key", "timeout", "--value", "600"])

        assert args.command == "config"
        assert args.action == "set"
        assert args.key == "timeout"
        assert args.value == "600"
