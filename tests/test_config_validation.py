"""
Test Suite for Configuration Validation System

Tests the sophisticated configuration management including:
- Multi-source configuration loading
- Validation rules and error reporting
- Environment variable handling
- Configuration file parsing
- Default value management
"""

import pytest
import os
import tempfile
import yaml
import toml
from pathlib import Path
from unittest.mock import patch, mock_open

# Import the configuration system
import sys
sys.path.append('..')
from cli.core.config import ConfigManager, ConfigDefaults
from cli.core.errors import ConfigurationError


class TestConfigDefaults:
    """Test the configuration defaults system."""
    
    def test_config_defaults_initialization(self):
        """Test that config defaults are properly initialized."""
        defaults = ConfigDefaults()
        
        # Test API configuration defaults
        assert defaults.defaults["api.base_url"] == "https://api.codegen.com"
        assert defaults.defaults["api.timeout"] == 30
        assert defaults.defaults["api.max_retries"] == 3
        assert defaults.defaults["api.retry_delay"] == 1.0
        
        # Test output configuration defaults
        assert defaults.defaults["output.format"] == "table"
        assert defaults.defaults["output.color"] is True
        assert defaults.defaults["output.pager"] is True
        
        # Test CLI behavior defaults
        assert defaults.defaults["cli.confirm_destructive"] is True
        assert defaults.defaults["cli.progress_bars"] is True
        assert defaults.defaults["cli.auto_update_check"] is True
        
        # Test logging defaults
        assert defaults.defaults["log.level"] == "INFO"
        assert defaults.defaults["log.file"] is None
        assert "%(asctime)s" in defaults.defaults["log.format"]
    
    def test_config_defaults_completeness(self):
        """Test that all expected configuration keys are present."""
        defaults = ConfigDefaults()
        expected_keys = {
            "api.base_url", "api.timeout", "api.max_retries", "api.retry_delay",
            "output.format", "output.color", "output.pager",
            "cli.confirm_destructive", "cli.progress_bars", "cli.auto_update_check",
            "log.level", "log.file", "log.format"
        }
        
        assert set(defaults.defaults.keys()) == expected_keys


class TestConfigManager:
    """Test the ConfigManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear environment variables that might interfere
        self.env_vars_to_clear = [
            "CODEGEN_API_TOKEN", "CODEGEN_ORG_ID", "CODEGEN_API_BASE_URL",
            "CODEGEN_API_TIMEOUT", "CODEGEN_OUTPUT_FORMAT", "CODEGEN_LOG_LEVEL"
        ]
        self.original_env = {}
        for var in self.env_vars_to_clear:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Clean up test environment."""
        # Restore original environment variables
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_config_manager_initialization_no_file(self):
        """Test ConfigManager initialization without config file."""
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            
            assert config.config_file is None
            assert isinstance(config.defaults, ConfigDefaults)
    
    def test_config_manager_get_default_values(self):
        """Test getting default configuration values."""
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            
            assert config.get("api.base_url") == "https://api.codegen.com"
            assert config.get("api.timeout") == 30
            assert config.get("output.format") == "table"
            assert config.get("log.level") == "INFO"
    
    def test_config_manager_environment_variables(self):
        """Test that environment variables override defaults."""
        os.environ["CODEGEN_API_TOKEN"] = "test-token"
        os.environ["CODEGEN_ORG_ID"] = "123"
        os.environ["CODEGEN_API_TIMEOUT"] = "60"
        os.environ["CODEGEN_OUTPUT_FORMAT"] = "json"
        
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            
            assert config.get("api.token") == "test-token"
            assert config.get("org.id") == "123"
            assert config.get("api.timeout") == 60  # Should be converted to int
            assert config.get("output.format") == "json"
    
    def test_config_manager_yaml_file_loading(self):
        """Test loading configuration from YAML file."""
        yaml_content = {
            "api": {
                "base_url": "https://custom.api.com",
                "timeout": 45
            },
            "output": {
                "format": "json",
                "color": False
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            
            assert config.get("api.base_url") == "https://custom.api.com"
            assert config.get("api.timeout") == 45
            assert config.get("output.format") == "json"
            assert config.get("output.color") is False
        finally:
            os.unlink(config_file)
    
    def test_config_manager_toml_file_loading(self):
        """Test loading configuration from TOML file."""
        toml_content = {
            "api": {
                "base_url": "https://toml.api.com",
                "timeout": 90
            },
            "cli": {
                "confirm_destructive": False
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            toml.dump(toml_content, f)
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            
            assert config.get("api.base_url") == "https://toml.api.com"
            assert config.get("api.timeout") == 90
            assert config.get("cli.confirm_destructive") is False
        finally:
            os.unlink(config_file)
    
    def test_config_manager_precedence_order(self):
        """Test configuration precedence: env vars > config file > defaults."""
        # Set up config file
        yaml_content = {
            "api": {"timeout": 45},
            "output": {"format": "yaml"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            config_file = f.name
        
        # Set environment variable that should override config file
        os.environ["CODEGEN_API_TIMEOUT"] = "120"
        
        try:
            config = ConfigManager(config_file=config_file)
            
            # Environment variable should win
            assert config.get("api.timeout") == 120
            
            # Config file should override default
            assert config.get("output.format") == "yaml"
            
            # Default should be used when not specified elsewhere
            assert config.get("api.max_retries") == 3
        finally:
            os.unlink(config_file)
    
    def test_config_manager_find_config_file(self):
        """Test config file discovery in standard locations."""
        config = ConfigManager()
        
        # Test that it searches in expected locations
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            result = config._find_config_file()
            assert result is None
            
            # Should have checked multiple locations
            assert mock_exists.call_count > 5


class TestConfigValidation:
    """Test configuration validation functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear environment variables
        self.env_vars_to_clear = [
            "CODEGEN_API_TOKEN", "CODEGEN_ORG_ID", "CODEGEN_API_BASE_URL"
        ]
        self.original_env = {}
        for var in self.env_vars_to_clear:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Clean up test environment."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_validation_missing_api_token(self):
        """Test validation fails when API token is missing."""
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            errors = config.validate()
            
            assert len(errors) > 0
            assert any("API token is required" in error for error in errors)
    
    def test_validation_invalid_base_url(self):
        """Test validation fails for invalid base URL."""
        os.environ["CODEGEN_API_TOKEN"] = "test-token"
        
        yaml_content = {"api": {"base_url": "not-a-url"}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            errors = config.validate()
            
            assert len(errors) > 0
            assert any("valid HTTP/HTTPS URL" in error for error in errors)
        finally:
            os.unlink(config_file)
    
    def test_validation_invalid_timeout(self):
        """Test validation fails for invalid timeout values."""
        os.environ["CODEGEN_API_TOKEN"] = "test-token"
        os.environ["CODEGEN_API_TIMEOUT"] = "-5"
        
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            errors = config.validate()
            
            assert len(errors) > 0
            assert any("positive integer" in error for error in errors)
    
    def test_validation_invalid_output_format(self):
        """Test validation fails for invalid output format."""
        os.environ["CODEGEN_API_TOKEN"] = "test-token"
        os.environ["CODEGEN_OUTPUT_FORMAT"] = "invalid-format"
        
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            errors = config.validate()
            
            assert len(errors) > 0
            assert any("Output format must be one of" in error for error in errors)
    
    def test_validation_invalid_log_level(self):
        """Test validation fails for invalid log level."""
        os.environ["CODEGEN_API_TOKEN"] = "test-token"
        os.environ["CODEGEN_LOG_LEVEL"] = "INVALID"
        
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            errors = config.validate()
            
            assert len(errors) > 0
            assert any("Log level must be one of" in error for error in errors)
    
    def test_validation_success_with_valid_config(self):
        """Test validation passes with valid configuration."""
        os.environ["CODEGEN_API_TOKEN"] = "test-token"
        os.environ["CODEGEN_API_BASE_URL"] = "https://api.example.com"
        os.environ["CODEGEN_API_TIMEOUT"] = "30"
        os.environ["CODEGEN_OUTPUT_FORMAT"] = "json"
        os.environ["CODEGEN_LOG_LEVEL"] = "DEBUG"
        
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            errors = config.validate()
            
            assert len(errors) == 0
    
    def test_validation_multiple_errors(self):
        """Test that validation reports multiple errors."""
        os.environ["CODEGEN_API_TIMEOUT"] = "-1"
        os.environ["CODEGEN_OUTPUT_FORMAT"] = "bad-format"
        os.environ["CODEGEN_LOG_LEVEL"] = "BAD-LEVEL"
        
        with patch.object(ConfigManager, '_find_config_file', return_value=None):
            config = ConfigManager()
            errors = config.validate()
            
            # Should have multiple validation errors
            assert len(errors) >= 3
            assert any("API token is required" in error for error in errors)
            assert any("positive integer" in error for error in errors)
            assert any("Output format must be one of" in error for error in errors)


class TestConfigurationSources:
    """Test configuration loading from different sources."""
    
    def test_config_get_all_with_sources(self):
        """Test getting all configuration with source information."""
        os.environ["CODEGEN_API_TOKEN"] = "env-token"
        
        yaml_content = {"api": {"timeout": 60}}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            all_config, sources = config.get_all_with_sources()
            
            # Check that sources are correctly identified
            assert sources["api.token"] == "environment"
            assert sources["api.timeout"] == "config_file"
            assert sources["api.max_retries"] == "default"
            
            # Check values
            assert all_config["api.token"] == "env-token"
            assert all_config["api.timeout"] == 60
            assert all_config["api.max_retries"] == 3
        finally:
            os.unlink(config_file)
            if "CODEGEN_API_TOKEN" in os.environ:
                del os.environ["CODEGEN_API_TOKEN"]
    
    def test_config_environment_variable_conversion(self):
        """Test that environment variables are properly converted to correct types."""
        os.environ["CODEGEN_API_TIMEOUT"] = "45"
        os.environ["CODEGEN_OUTPUT_COLOR"] = "false"
        os.environ["CODEGEN_CLI_PROGRESS_BARS"] = "true"
        os.environ["CODEGEN_API_RETRY_DELAY"] = "2.5"
        
        try:
            with patch.object(ConfigManager, '_find_config_file', return_value=None):
                config = ConfigManager()
                
                assert config.get("api.timeout") == 45  # int
                assert config.get("output.color") is False  # bool
                assert config.get("cli.progress_bars") is True  # bool
                assert config.get("api.retry_delay") == 2.5  # float
        finally:
            for var in ["CODEGEN_API_TIMEOUT", "CODEGEN_OUTPUT_COLOR", 
                       "CODEGEN_CLI_PROGRESS_BARS", "CODEGEN_API_RETRY_DELAY"]:
                if var in os.environ:
                    del os.environ[var]


class TestConfigurationErrors:
    """Test configuration error handling."""
    
    def test_invalid_yaml_file(self):
        """Test handling of invalid YAML files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_file = f.name
        
        try:
            with pytest.raises(Exception):  # Should raise parsing error
                ConfigManager(config_file=config_file)
        finally:
            os.unlink(config_file)
    
    def test_invalid_toml_file(self):
        """Test handling of invalid TOML files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            f.write("[invalid toml content")
            config_file = f.name
        
        try:
            with pytest.raises(Exception):  # Should raise parsing error
                ConfigManager(config_file=config_file)
        finally:
            os.unlink(config_file)
    
    def test_nonexistent_config_file(self):
        """Test handling of nonexistent config file."""
        with pytest.raises(FileNotFoundError):
            ConfigManager(config_file="/nonexistent/config.yaml")


class TestConfigurationIntegration:
    """Integration tests for configuration system."""
    
    def test_config_integration_with_cli_commands(self):
        """Test that configuration integrates properly with CLI commands."""
        # This would test integration with actual CLI commands
        # For now, we'll test the configuration manager directly
        
        os.environ["CODEGEN_API_TOKEN"] = "integration-token"
        os.environ["CODEGEN_ORG_ID"] = "456"
        
        try:
            with patch.object(ConfigManager, '_find_config_file', return_value=None):
                config = ConfigManager()
                
                # Test that required values are available
                assert config.get("api.token") == "integration-token"
                assert config.get("org.id") == "456"
                
                # Test validation passes
                errors = config.validate()
                assert len(errors) == 0
        finally:
            for var in ["CODEGEN_API_TOKEN", "CODEGEN_ORG_ID"]:
                if var in os.environ:
                    del os.environ[var]
    
    def test_config_xdg_compliance(self):
        """Test XDG Base Directory Specification compliance."""
        config = ConfigManager()
        
        # Mock XDG_CONFIG_HOME
        with patch.dict('os.environ', {'XDG_CONFIG_HOME': '/custom/config'}):
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = False
                config._find_config_file()
                
                # Should check XDG config directory
                expected_calls = [call for call in mock_exists.call_args_list 
                                if '/custom/config/codegen' in str(call)]
                assert len(expected_calls) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

