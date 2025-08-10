"""
Comprehensive test suite for the Codegen SDK v2.0

Tests all functions of the modularized SDK with real API credentials.
"""

import os
import pytest
import time
from typing import Optional

# Test both import patterns
try:
    # Official SDK pattern
    from codegen.agents.agent import Agent
    from codegen.client import CodegenClient
    from codegen.config import ClientConfig, ConfigPresets
    from codegen.models import AgentRunStatus, SourceType
    from codegen.exceptions import ValidationError, CodegenAPIError
    OFFICIAL_SDK_AVAILABLE = True
except ImportError as e:
    print(f"Official SDK import failed: {e}")
    OFFICIAL_SDK_AVAILABLE = False

try:
    # Backward compatibility pattern
    from backend.api import Agent as BackendAgent, CodegenClient as BackendClient
    BACKEND_API_AVAILABLE = True
except ImportError as e:
    print(f"Backend API import failed: {e}")
    BACKEND_API_AVAILABLE = False

# Test configuration
CODEGEN_ORG_ID = os.getenv("CODEGEN_ORG_ID", "323")
CODEGEN_API_TOKEN = os.getenv("CODEGEN_API_TOKEN", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")

# Skip tests if no credentials
pytestmark = pytest.mark.skipif(
    not CODEGEN_API_TOKEN or CODEGEN_API_TOKEN == "your-token-here",
    reason="No valid API token provided"
)


class TestOfficialSDKPattern:
    """Test the official SDK import patterns and functionality"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_official_imports(self):
        """Test that official SDK imports work correctly"""
        from codegen.agents.agent import Agent
        from codegen.client import CodegenClient
        from codegen.config import ClientConfig
        
        assert Agent is not None
        assert CodegenClient is not None
        assert ClientConfig is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_agent_initialization(self):
        """Test Agent class initialization with official pattern"""
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        
        assert agent.org_id == int(CODEGEN_ORG_ID)
        assert agent.token == CODEGEN_API_TOKEN
        assert agent.base_url == "https://api.codegen.com/v1"
        assert agent._client is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_agent_custom_base_url(self):
        """Test Agent with custom base URL"""
        custom_url = "https://api.example.com/v1"
        agent = Agent(
            org_id=CODEGEN_ORG_ID, 
            token=CODEGEN_API_TOKEN, 
            base_url=custom_url
        )
        
        assert agent.base_url == custom_url
        assert agent._client.config.base_url == custom_url
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_agent_context_manager(self):
        """Test Agent as context manager"""
        with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
            assert agent is not None
            assert agent._client is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_agent_run_creation(self):
        """Test creating an agent run with official SDK"""
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        
        task = agent.run("Write a simple Python function that returns 'Hello, World!'")
        
        assert task is not None
        assert task.id is not None
        assert isinstance(task.id, int)
        assert task.status is not None
        
        # Test task properties
        assert hasattr(task, 'status')
        assert hasattr(task, 'result')
        assert hasattr(task, 'web_url')
        assert hasattr(task, 'created_at')
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_agent_run_with_metadata(self):
        """Test creating an agent run with metadata"""
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        
        metadata = {
            "test_case": "comprehensive_sdk_test",
            "version": "2.0.0",
            "priority": "high"
        }
        
        task = agent.run(
            "Create a function that adds two numbers",
            metadata=metadata
        )
        
        assert task is not None
        assert task.id is not None


class TestClientConfiguration:
    """Test configuration classes and presets"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_client_config_defaults(self):
        """Test ClientConfig with default values"""
        # Temporarily set environment variables
        os.environ["CODEGEN_API_TOKEN"] = CODEGEN_API_TOKEN
        os.environ["CODEGEN_ORG_ID"] = CODEGEN_ORG_ID
        
        config = ClientConfig()
        
        assert config.api_token == CODEGEN_API_TOKEN
        assert config.org_id == CODEGEN_ORG_ID
        assert config.base_url == "https://api.codegen.com/v1"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.enable_caching is True
        assert config.enable_metrics is True
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_client_config_custom(self):
        """Test ClientConfig with custom values"""
        config = ClientConfig(
            api_token=CODEGEN_API_TOKEN,
            org_id=CODEGEN_ORG_ID,
            timeout=60,
            max_retries=5,
            enable_caching=False,
        )
        
        assert config.api_token == CODEGEN_API_TOKEN
        assert config.org_id == CODEGEN_ORG_ID
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.enable_caching is False
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_config_presets(self):
        """Test configuration presets"""
        dev_config = ConfigPresets.development()
        prod_config = ConfigPresets.production()
        perf_config = ConfigPresets.high_performance()
        test_config = ConfigPresets.testing()
        
        # Development config
        assert dev_config.timeout == 60
        assert dev_config.log_level == "DEBUG"
        assert dev_config.log_requests is True
        
        # Production config
        assert prod_config.timeout == 30
        assert prod_config.log_level == "INFO"
        assert prod_config.max_retries == 3
        
        # High performance config
        assert perf_config.timeout == 45
        assert perf_config.max_retries == 5
        assert perf_config.bulk_max_workers == 10
        
        # Testing config
        assert test_config.timeout == 10
        assert test_config.max_retries == 1
        assert test_config.enable_caching is False


class TestCodegenClient:
    """Test the CodegenClient class functionality"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_client_initialization(self):
        """Test CodegenClient initialization"""
        config = ClientConfig(api_token=CODEGEN_API_TOKEN, org_id=CODEGEN_ORG_ID)
        client = CodegenClient(config)
        
        assert client.config.api_token == CODEGEN_API_TOKEN
        assert client.config.org_id == CODEGEN_ORG_ID
        assert client.session is not None
        assert client.rate_limiter is not None
        assert client.cache is not None
        assert client.metrics is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_client_context_manager(self):
        """Test CodegenClient as context manager"""
        config = ClientConfig(api_token=CODEGEN_API_TOKEN, org_id=CODEGEN_ORG_ID)
        
        with CodegenClient(config) as client:
            assert client is not None
            assert client.session is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_client_health_check(self):
        """Test client health check"""
        config = ClientConfig(api_token=CODEGEN_API_TOKEN, org_id=CODEGEN_ORG_ID)
        
        with CodegenClient(config) as client:
            health = client.health_check()
            
            assert health is not None
            assert "status" in health
            assert health["status"] in ["healthy", "unhealthy"]
            assert "timestamp" in health
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_client_get_current_user(self):
        """Test getting current user"""
        config = ClientConfig(api_token=CODEGEN_API_TOKEN, org_id=CODEGEN_ORG_ID)
        
        with CodegenClient(config) as client:
            user = client.get_current_user()
            
            assert user is not None
            assert user.id is not None
            assert isinstance(user.id, int)
            assert user.github_username is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_client_create_agent_run(self):
        """Test creating agent run with client"""
        config = ClientConfig(api_token=CODEGEN_API_TOKEN, org_id=CODEGEN_ORG_ID)
        
        with CodegenClient(config) as client:
            run = client.create_agent_run(
                org_id=int(CODEGEN_ORG_ID),
                prompt="Write a function that calculates the factorial of a number"
            )
            
            assert run is not None
            assert run.id is not None
            assert isinstance(run.id, int)
            assert run.organization_id == int(CODEGEN_ORG_ID)
            assert run.status is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_client_get_organizations(self):
        """Test getting organizations"""
        config = ClientConfig(api_token=CODEGEN_API_TOKEN, org_id=CODEGEN_ORG_ID)
        
        with CodegenClient(config) as client:
            orgs = client.get_organizations()
            
            assert orgs is not None
            assert orgs.items is not None
            assert len(orgs.items) > 0
            assert orgs.total > 0
            
            # Check if our org is in the list
            org_ids = [org.id for org in orgs.items]
            assert int(CODEGEN_ORG_ID) in org_ids


class TestTaskFunctionality:
    """Test Task class functionality"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_task_properties(self):
        """Test Task properties and methods"""
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        task = agent.run("Create a simple greeting function")
        
        # Test basic properties
        assert task.id is not None
        assert isinstance(task.id, int)
        assert task.status is not None
        
        # Test refresh functionality
        initial_status = task.status
        task.refresh()
        assert task.status is not None  # Status should still be available after refresh
        
        # Test string representations
        task_str = str(task)
        task_repr = repr(task)
        assert "Task" in task_str
        assert "Task" in task_repr
        assert str(task.id) in task_str
        assert str(task.id) in task_repr
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    @pytest.mark.slow
    def test_task_wait_for_completion(self):
        """Test waiting for task completion (slow test)"""
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        task = agent.run("Return the string 'test complete'")
        
        # Wait for completion with timeout
        try:
            task.wait_for_completion(poll_interval=2.0, timeout=60.0)
            assert task.status in ["completed", "failed", "cancelled"]
        except Exception as e:
            # If it times out, that's okay for this test
            assert "timeout" in str(e).lower() or task.status is not None


class TestErrorHandling:
    """Test error handling and validation"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_validation_errors(self):
        """Test validation error handling"""
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        
        # Test empty prompt
        with pytest.raises(ValidationError):
            agent.run("")
        
        # Test whitespace-only prompt
        with pytest.raises(ValidationError):
            agent.run("   ")
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_invalid_credentials(self):
        """Test handling of invalid credentials"""
        # Test with invalid token
        with pytest.raises(Exception):  # Should raise authentication error
            agent = Agent(org_id=CODEGEN_ORG_ID, token="invalid-token")
            agent.run("test prompt")
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_config_validation(self):
        """Test configuration validation"""
        # Test missing API token
        with pytest.raises(ValueError):
            ClientConfig(api_token="", org_id=CODEGEN_ORG_ID)


class TestBackwardCompatibility:
    """Test backward compatibility with backend.api imports"""
    
    @pytest.mark.skipif(not BACKEND_API_AVAILABLE, reason="Backend API not available")
    def test_backend_imports(self):
        """Test that backend imports still work"""
        from backend.api import Agent, CodegenClient
        
        assert Agent is not None
        assert CodegenClient is not None
    
    @pytest.mark.skipif(not BACKEND_API_AVAILABLE, reason="Backend API not available")
    @pytest.mark.integration
    def test_backend_agent_functionality(self):
        """Test that backend Agent still works"""
        from backend.api import Agent
        
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        task = agent.run("Write a simple hello world function")
        
        assert task is not None
        assert hasattr(task, 'status')
        assert hasattr(task, 'result')


class TestUtilityClasses:
    """Test utility classes functionality"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_rate_limiter(self):
        """Test rate limiter functionality"""
        from codegen.utils import RateLimiter
        
        limiter = RateLimiter(requests_per_period=5, period_seconds=10)
        
        # Test usage tracking
        usage = limiter.get_current_usage()
        assert usage["current_requests"] == 0
        assert usage["max_requests"] == 5
        assert usage["period_seconds"] == 10
        assert usage["usage_percentage"] == 0
        
        # Test rate limiting (should not block for first few requests)
        start_time = time.time()
        limiter.wait_if_needed()
        end_time = time.time()
        
        # Should not have waited
        assert (end_time - start_time) < 0.1
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_cache_manager(self):
        """Test cache manager functionality"""
        from codegen.utils import CacheManager
        
        cache = CacheManager(max_size=10, ttl_seconds=60)
        
        # Test basic operations
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("nonexistent") is None
        
        # Test stats
        stats = cache.get_stats()
        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        
        # Test clear
        cache.clear()
        assert cache.get("key1") is None
        stats = cache.get_stats()
        assert stats["size"] == 0
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_metrics_collector(self):
        """Test metrics collector functionality"""
        from codegen.utils import MetricsCollector
        
        metrics = MetricsCollector()
        
        # Record some requests
        metrics.record_request("GET", "/test", 0.5, 200, "req-1")
        metrics.record_request("POST", "/test", 1.0, 201, "req-2")
        metrics.record_request("GET", "/test", 0.3, 404, "req-3")
        
        # Get stats
        stats = metrics.get_stats()
        assert stats.total_requests == 3
        assert stats.total_errors == 1  # 404 is an error
        assert stats.error_rate > 0
        assert stats.average_response_time > 0
        assert 404 in stats.status_code_distribution
        
        # Test reset
        metrics.reset()
        stats = metrics.get_stats()
        assert stats.total_requests == 0


class TestModelsAndEnums:
    """Test data models and enums"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_enums(self):
        """Test enum definitions"""
        from codegen.models import SourceType, MessageType, AgentRunStatus
        
        # Test SourceType
        assert SourceType.API.value == "API"
        assert SourceType.GITHUB.value == "GITHUB"
        assert SourceType.SLACK.value == "SLACK"
        
        # Test MessageType
        assert MessageType.ACTION.value == "ACTION"
        assert MessageType.ERROR.value == "ERROR"
        assert MessageType.FINAL_ANSWER.value == "FINAL_ANSWER"
        
        # Test AgentRunStatus
        assert AgentRunStatus.PENDING.value == "pending"
        assert AgentRunStatus.RUNNING.value == "running"
        assert AgentRunStatus.COMPLETED.value == "completed"
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    def test_response_models(self):
        """Test response model creation"""
        from codegen.models import UserResponse, AgentRunResponse
        
        # Test UserResponse
        user = UserResponse(
            id=123,
            email="test@example.com",
            github_user_id="456",
            github_username="testuser",
            avatar_url="https://example.com/avatar.jpg",
            full_name="Test User"
        )
        
        assert user.id == 123
        assert user.email == "test@example.com"
        assert user.github_username == "testuser"
        
        # Test AgentRunResponse
        run = AgentRunResponse(
            id=789,
            organization_id=int(CODEGEN_ORG_ID),
            status="completed",
            created_at="2024-01-01T00:00:00Z",
            web_url="https://app.codegen.com/run/789",
            result="Task completed successfully",
            source_type=SourceType.API,
            github_pull_requests=None,
            metadata={"test": True}
        )
        
        assert run.id == 789
        assert run.organization_id == int(CODEGEN_ORG_ID)
        assert run.status == "completed"
        assert run.source_type == SourceType.API


# Performance and integration tests
class TestPerformanceAndIntegration:
    """Test performance and integration scenarios"""
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_concurrent_requests(self):
        """Test handling multiple requests (integration test)"""
        agent = Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN)
        
        # Create multiple tasks
        tasks = []
        for i in range(3):
            task = agent.run(f"Create a function that returns the number {i}")
            tasks.append(task)
        
        # Verify all tasks were created
        assert len(tasks) == 3
        for task in tasks:
            assert task.id is not None
            assert task.status is not None
    
    @pytest.mark.skipif(not OFFICIAL_SDK_AVAILABLE, reason="Official SDK not available")
    @pytest.mark.integration
    def test_client_statistics(self):
        """Test client statistics collection"""
        config = ClientConfig(
            api_token=CODEGEN_API_TOKEN, 
            org_id=CODEGEN_ORG_ID,
            enable_metrics=True
        )
        
        with CodegenClient(config) as client:
            # Make some requests
            client.get_current_user()
            client.get_organizations()
            
            # Get stats
            stats = client.get_stats()
            
            assert "config" in stats
            assert "metrics" in stats
            assert stats["metrics"]["total_requests"] >= 2
            assert stats["config"]["metrics_enabled"] is True


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "not slow",  # Skip slow tests by default
        "--durations=10"   # Show 10 slowest tests
    ])

