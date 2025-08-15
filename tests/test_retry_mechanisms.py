"""
Test Suite for Retry Mechanisms and Recovery Logic

Tests the sophisticated retry system including:
- Exponential backoff implementation
- Rate limit handling
- Circuit breaker patterns
- Retry decorator functionality
- Recovery strategies
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock, call
from concurrent.futures import ThreadPoolExecutor

# Import the retry system
import sys
sys.path.append('..')
from codegen_api import (
    retry_with_backoff,
    RateLimitError,
    NetworkError,
    TimeoutError,
    ServerError,
    CodegenClient,
    ClientConfig
)


class TestRetryDecorator:
    """Test the retry_with_backoff decorator."""
    
    def test_retry_decorator_success_first_try(self):
        """Test that successful calls don't retry."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.1)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retry_decorator_eventual_success(self):
        """Test that function succeeds after retries."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Temporary failure")
            return "success"
        
        result = eventually_successful()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_decorator_max_retries_exceeded(self):
        """Test that function fails after max retries."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise NetworkError("Persistent failure")
        
        with pytest.raises(NetworkError):
            always_fails()
        
        assert call_count == 3  # Initial call + 2 retries
    
    def test_retry_decorator_rate_limit_handling(self):
        """Test special handling of rate limit errors."""
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def rate_limited_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RateLimitError(retry_after=1)  # Short retry for testing
            return "success"
        
        with patch('time.sleep') as mock_sleep:
            result = rate_limited_function()
        
        assert result == "success"
        assert call_count == 2
        mock_sleep.assert_called_with(1)  # Should sleep for retry_after time
    
    def test_retry_decorator_exponential_backoff(self):
        """Test that backoff times increase exponentially."""
        call_count = 0
        sleep_times = []
        
        @retry_with_backoff(max_retries=3, base_delay=0.1, backoff_factor=2.0)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise NetworkError("Always fails")
        
        with patch('time.sleep') as mock_sleep:
            mock_sleep.side_effect = lambda t: sleep_times.append(t)
            
            with pytest.raises(NetworkError):
                failing_function()
        
        # Should have 3 sleep calls with exponential backoff
        assert len(sleep_times) == 3
        assert sleep_times[0] == 0.1  # base_delay
        assert sleep_times[1] == 0.2  # base_delay * backoff_factor
        assert sleep_times[2] == 0.4  # base_delay * backoff_factor^2
    
    def test_retry_decorator_no_retry_for_non_retryable_errors(self):
        """Test that certain errors don't trigger retries."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def function_with_validation_error():
            nonlocal call_count
            call_count += 1
            # ValidationError should not be retried
            from codegen_api import ValidationError
            raise ValidationError("Bad input", 400)
        
        with pytest.raises(ValidationError):
            function_with_validation_error()
        
        assert call_count == 1  # Should not retry validation errors


class TestClientRetryIntegration:
    """Test retry integration in the CodegenClient."""
    
    def setup_method(self):
        """Set up test client."""
        config = ClientConfig()
        config.api_token = "test-token"
        config.org_id = "123"
        config.max_retries = 3
        config.retry_delay = 0.01
        config.retry_backoff_factor = 2.0
        self.client = CodegenClient(config)
    
    @patch('requests.Session.request')
    def test_client_retry_on_network_error(self, mock_request):
        """Test that client retries on network errors."""
        # First two calls fail, third succeeds
        mock_request.side_effect = [
            NetworkError("Connection failed"),
            NetworkError("Connection failed"),
            Mock(status_code=200, json=lambda: {"items": [], "total": 0})
        ]
        
        # This should succeed after retries
        result = self.client.get_organizations()
        
        assert mock_request.call_count == 3
        assert result.total == 0
    
    @patch('requests.Session.request')
    def test_client_retry_on_timeout(self, mock_request):
        """Test that client retries on timeout errors."""
        mock_request.side_effect = [
            TimeoutError("Request timeout", 408),
            Mock(status_code=200, json=lambda: {"items": [], "total": 0})
        ]
        
        result = self.client.get_organizations()
        
        assert mock_request.call_count == 2
        assert result.total == 0
    
    @patch('requests.Session.request')
    def test_client_retry_on_server_error(self, mock_request):
        """Test that client retries on server errors."""
        mock_request.side_effect = [
            ServerError("Internal server error", 500),
            ServerError("Service unavailable", 503),
            Mock(status_code=200, json=lambda: {"items": [], "total": 0})
        ]
        
        result = self.client.get_organizations()
        
        assert mock_request.call_count == 3
        assert result.total == 0
    
    @patch('requests.Session.request')
    def test_client_no_retry_on_client_error(self, mock_request):
        """Test that client doesn't retry on client errors."""
        from codegen_api import AuthenticationError
        mock_request.side_effect = AuthenticationError("Unauthorized", 401)
        
        with pytest.raises(AuthenticationError):
            self.client.get_organizations()
        
        assert mock_request.call_count == 1  # Should not retry auth errors
    
    @patch('requests.Session.request')
    @patch('time.sleep')
    def test_client_rate_limit_retry(self, mock_sleep, mock_request):
        """Test that client handles rate limits correctly."""
        # Mock rate limit response
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "2"}
        rate_limit_response.json.return_value = {"error": "Rate limited"}
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"items": [], "total": 0}
        
        mock_request.side_effect = [rate_limit_response, success_response]
        
        result = self.client.get_organizations()
        
        assert mock_request.call_count == 2
        mock_sleep.assert_called_with(2)  # Should sleep for retry-after time
        assert result.total == 0


class TestRetryConfiguration:
    """Test retry configuration and customization."""
    
    def test_retry_config_from_environment(self):
        """Test that retry config can be set from environment variables."""
        with patch.dict('os.environ', {
            'CODEGEN_MAX_RETRIES': '5',
            'CODEGEN_RETRY_DELAY': '2.0',
            'CODEGEN_RETRY_BACKOFF': '3.0'
        }):
            config = ClientConfig()
            
            assert config.max_retries == 5
            assert config.retry_delay == 2.0
            assert config.retry_backoff_factor == 3.0
    
    def test_retry_config_defaults(self):
        """Test default retry configuration values."""
        config = ClientConfig()
        
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.retry_backoff_factor == 2.0
    
    def test_custom_retry_config(self):
        """Test setting custom retry configuration."""
        config = ClientConfig()
        config.max_retries = 10
        config.retry_delay = 0.5
        config.retry_backoff_factor = 1.5
        
        client = CodegenClient(config)
        
        assert client.config.max_retries == 10
        assert client.config.retry_delay == 0.5
        assert client.config.retry_backoff_factor == 1.5


class TestRetryPerformance:
    """Test retry mechanism performance and behavior."""
    
    def test_retry_timing_accuracy(self):
        """Test that retry delays are approximately correct."""
        delays = []
        
        @retry_with_backoff(max_retries=3, base_delay=0.1, backoff_factor=2.0)
        def timing_test():
            raise NetworkError("Test error")
        
        with patch('time.sleep') as mock_sleep:
            mock_sleep.side_effect = lambda t: delays.append(t)
            
            with pytest.raises(NetworkError):
                timing_test()
        
        # Verify exponential backoff timing
        expected_delays = [0.1, 0.2, 0.4]
        assert delays == expected_delays
    
    def test_retry_with_jitter(self):
        """Test retry with jitter to avoid thundering herd."""
        # This would be implemented if jitter is added to the retry mechanism
        pass
    
    def test_concurrent_retries(self):
        """Test that concurrent operations with retries work correctly."""
        call_counts = {"func1": 0, "func2": 0}
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def concurrent_func(name):
            call_counts[name] += 1
            if call_counts[name] < 2:
                raise NetworkError(f"Failure in {name}")
            return f"Success from {name}"
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(concurrent_func, "func1")
            future2 = executor.submit(concurrent_func, "func2")
            
            result1 = future1.result()
            result2 = future2.result()
        
        assert result1 == "Success from func1"
        assert result2 == "Success from func2"
        assert call_counts["func1"] == 2
        assert call_counts["func2"] == 2


class TestRetryErrorScenarios:
    """Test retry behavior in various error scenarios."""
    
    def test_mixed_error_types(self):
        """Test retry behavior with mixed error types."""
        call_count = 0
        
        @retry_with_backoff(max_retries=4, base_delay=0.01)
        def mixed_errors():
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                raise NetworkError("Network issue")
            elif call_count == 2:
                raise TimeoutError("Timeout", 408)
            elif call_count == 3:
                raise ServerError("Server error", 500)
            else:
                return "success"
        
        result = mixed_errors()
        
        assert result == "success"
        assert call_count == 4
    
    def test_retry_with_changing_error_messages(self):
        """Test that retry works with different error messages."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def changing_errors():
            nonlocal call_count
            call_count += 1
            raise NetworkError(f"Error #{call_count}")
        
        with pytest.raises(NetworkError) as exc_info:
            changing_errors()
        
        assert "Error #4" in str(exc_info.value)  # Final error message
        assert call_count == 4  # Initial + 3 retries
    
    def test_retry_preserves_original_exception(self):
        """Test that the original exception is preserved after retries."""
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def failing_function():
            raise NetworkError("Original error message")
        
        with pytest.raises(NetworkError) as exc_info:
            failing_function()
        
        assert "Original error message" in str(exc_info.value)
        assert isinstance(exc_info.value, NetworkError)


class TestRetryIntegrationWithCLI:
    """Test integration between retry mechanisms and CLI error handling."""
    
    def test_retry_errors_translate_to_cli_errors(self):
        """Test that retry failures are properly translated to CLI errors."""
        from cli.core.errors import translate_sdk_error, NetworkCLIError
        
        # Simulate a network error that failed after retries
        network_error = NetworkError("Connection failed after retries")
        cli_error = translate_sdk_error(network_error)
        
        assert isinstance(cli_error, NetworkCLIError)
        assert "Network error" in cli_error.message
        assert "internet connection" in cli_error.suggestions[0]
    
    def test_rate_limit_suggestions_include_retry_info(self):
        """Test that rate limit errors include retry information."""
        from cli.core.errors import translate_sdk_error
        
        rate_limit_error = RateLimitError(retry_after=120)
        cli_error = translate_sdk_error(rate_limit_error)
        
        assert "Wait 120 seconds" in cli_error.suggestions[0]
        assert "--wait" in cli_error.suggestions[2]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

