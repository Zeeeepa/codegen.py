"""
Unit tests for core functionality
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from codegen.core import (
    CodegenClient, ClientConfig, ConfigPresets, RateLimiter, CacheManager,
    CodegenAPIError, AuthenticationError, NotFoundError, RateLimitError
)


class TestClientConfig:
    """Test ClientConfig class"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ClientConfig()
        assert config.base_url == "https://api.codegen.com"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.enable_metrics is True
    
    def test_config_validation(self):
        """Test configuration validation"""
        with pytest.raises(ValueError, match="timeout must be positive"):
            ClientConfig(timeout=0)
        
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            ClientConfig(max_retries=-1)


class TestConfigPresets:
    """Test configuration presets"""
    
    def test_development_preset(self):
        """Test development preset"""
        config = ConfigPresets.development()
        assert config.timeout == 10
        assert config.max_retries == 1
        assert config.enable_caching is False
    
    def test_production_preset(self):
        """Test production preset"""
        config = ConfigPresets.production()
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.enable_caching is True
    
    def test_high_throughput_preset(self):
        """Test high throughput preset"""
        config = ConfigPresets.high_throughput()
        assert config.bulk_batch_size == 100
        assert config.bulk_max_workers == 10


class TestRateLimiter:
    """Test RateLimiter class"""
    
    def test_rate_limiter_creation(self):
        """Test rate limiter creation"""
        limiter = RateLimiter(10, 60)
        assert limiter.requests_per_period == 10
        assert limiter.period_seconds == 60
        assert len(limiter.requests) == 0
    
    def test_rate_limiter_allows_requests(self):
        """Test that rate limiter allows requests within limit"""
        limiter = RateLimiter(10, 60)
        
        # Should not block for requests within limit
        for _ in range(5):
            limiter.wait_if_needed()
        
        usage = limiter.get_current_usage()
        assert usage["current_requests"] == 5
        assert usage["max_requests"] == 10
    
    @patch('time.sleep')
    def test_rate_limiter_blocks_excess_requests(self, mock_sleep):
        """Test that rate limiter blocks excess requests"""
        limiter = RateLimiter(2, 10)  # 2 requests per 10 seconds
        
        # Fill up the limit
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        
        # This should trigger rate limiting
        limiter.wait_if_needed()
        
        # Should have called sleep
        mock_sleep.assert_called_once()


class TestCacheManager:
    """Test CacheManager class"""
    
    def test_cache_creation(self):
        """Test cache creation"""
        cache = CacheManager(max_size=100, ttl_seconds=300)
        assert cache.max_size == 100
        assert cache.ttl_seconds == 300
    
    def test_cache_set_get(self):
        """Test cache set and get operations"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("nonexistent") is None
    
    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        cache = CacheManager(ttl_seconds=1)
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Mock time to simulate TTL expiration
        with patch('time.time', return_value=time.time() + 2):
            assert cache.get("key1") is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("nonexistent")  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0


class TestCodegenClient:
    """Test CodegenClient class"""
    
    def test_client_creation_with_params(self):
        """Test client creation with parameters"""
        config = ClientConfig(enable_rate_limiting=False, enable_caching=False, enable_metrics=False)
        client = CodegenClient(org_id="test-org", token="test-token", config=config)
        
        assert client.org_id == "test-org"
        assert client.token == "test-token"
        assert client.config == config
    
    def test_client_creation_missing_params(self):
        """Test client creation with missing parameters"""
        with pytest.raises(ValueError, match="Organization ID is required"):
            CodegenClient(token="test-token")
        
        with pytest.raises(ValueError, match="API token is required"):
            CodegenClient(org_id="test-org")
    
    @patch('codegen.core.requests.Session.request')
    def test_successful_request(self, mock_request):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "status": "completed"}
        mock_request.return_value = mock_response
        
        config = ClientConfig(enable_rate_limiting=False, enable_caching=False, enable_metrics=False)
        client = CodegenClient(org_id="test-org", token="test-token", config=config)
        
        response = client._make_request("GET", "/test")
        assert response.status_code == 200
    
    @patch('codegen.core.requests.Session.request')
    def test_authentication_error(self, mock_request):
        """Test authentication error handling"""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_request.return_value = mock_response
        
        config = ClientConfig(enable_rate_limiting=False, enable_caching=False, enable_metrics=False)
        client = CodegenClient(org_id="test-org", token="test-token", config=config)
        
        with pytest.raises(AuthenticationError):
            client._make_request("GET", "/test")
    
    @patch('codegen.core.requests.Session.request')
    def test_not_found_error(self, mock_request):
        """Test not found error handling"""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not found"}
        mock_request.return_value = mock_response
        
        config = ClientConfig(enable_rate_limiting=False, enable_caching=False, enable_metrics=False)
        client = CodegenClient(org_id="test-org", token="test-token", config=config)
        
        with pytest.raises(NotFoundError):
            client._make_request("GET", "/test")
    
    @patch('codegen.core.requests.Session.request')
    def test_rate_limit_error(self, mock_request):
        """Test rate limit error handling"""
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        mock_request.return_value = mock_response
        
        config = ClientConfig(enable_rate_limiting=False, enable_caching=False, enable_metrics=True)
        client = CodegenClient(org_id="test-org", token="test-token", config=config)
        
        with pytest.raises(RateLimitError):
            client._make_request("GET", "/test")

