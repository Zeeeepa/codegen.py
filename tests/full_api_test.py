#!/usr/bin/env python3
"""
Comprehensive Test Suite for Codegen SDK API
Tests all functions and features of the codegen_sdk_api.py module
"""

import os
import sys
import time
import json
import unittest
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.api import (
    # Main classes
    CodegenClient,
    Agent,
    Task,
    
    # Configuration
    ClientConfig,
    ConfigPresets,
    
    # Data models
    UserResponse,
    OrganizationResponse,
    AgentRunResponse,
    AgentRunLogResponse,
    AgentRunWithLogsResponse,
    UsersResponse,
    OrganizationsResponse,
    AgentRunsResponse,
    GithubPullRequestResponse,
    OrganizationSettings,
    BulkOperationResult,
    RequestMetrics,
    ClientStats,
    
    # Enums
    SourceType,
    MessageType,
    AgentRunStatus,
    
    # Exceptions
    CodegenAPIError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ServerError,
    TimeoutError,
    NetworkError,
    
    # Utility classes
    RateLimiter,
    CacheManager,
    BulkOperationManager,
    MetricsCollector,
)

# Test configuration using real credentials
CODEGEN_ORG_ID = "323"
CODEGEN_API_TOKEN = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"

# Set up logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCodegenSDK(unittest.TestCase):
    """Comprehensive test suite for the Codegen SDK"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Set environment variables for testing
        os.environ["CODEGEN_ORG_ID"] = CODEGEN_ORG_ID
        os.environ["CODEGEN_API_TOKEN"] = CODEGEN_API_TOKEN
        os.environ["CODEGEN_LOG_LEVEL"] = "DEBUG"
        
        # Create test configuration
        cls.config = ClientConfig(
            api_token=CODEGEN_API_TOKEN,
            org_id=CODEGEN_ORG_ID,
            timeout=30,
            max_retries=2,
            log_level="DEBUG",
            enable_caching=True,
            enable_metrics=True,
        )
        
        logger.info("Test environment set up successfully")
    
    def setUp(self):
        """Set up each test"""
        self.client = CodegenClient(self.config)
        self.org_id = int(CODEGEN_ORG_ID)
    
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'client'):
            self.client.close()

class TestClientConfiguration(TestCodegenSDK):
    """Test client configuration and presets"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        # Temporarily remove env vars to test defaults
        original_token = os.environ.get("CODEGEN_API_TOKEN")
        original_org = os.environ.get("CODEGEN_ORG_ID")
        
        try:
            os.environ["CODEGEN_API_TOKEN"] = "test-token"
            os.environ["CODEGEN_ORG_ID"] = "123"
            
            config = ClientConfig()
            self.assertEqual(config.api_token, "test-token")
            self.assertEqual(config.org_id, "123")
            self.assertEqual(config.base_url, "https://api.codegen.com/v1")
            self.assertEqual(config.timeout, 30)
            self.assertTrue(config.enable_caching)
            
        finally:
            # Restore original values
            if original_token:
                os.environ["CODEGEN_API_TOKEN"] = original_token
            if original_org:
                os.environ["CODEGEN_ORG_ID"] = original_org
    
    def test_config_presets(self):
        """Test configuration presets"""
        # Development preset
        dev_config = ConfigPresets.development()
        self.assertEqual(dev_config.timeout, 60)
        self.assertEqual(dev_config.max_retries, 1)
        self.assertEqual(dev_config.log_level, "DEBUG")
        self.assertTrue(dev_config.log_requests)
        self.assertTrue(dev_config.log_responses)
        
        # Production preset
        prod_config = ConfigPresets.production()
        self.assertEqual(prod_config.timeout, 30)
        self.assertEqual(prod_config.max_retries, 3)
        self.assertEqual(prod_config.log_level, "INFO")
        self.assertTrue(prod_config.log_requests)
        self.assertFalse(prod_config.log_responses)
        
        # Testing preset
        test_config = ConfigPresets.testing()
        self.assertEqual(test_config.timeout, 10)
        self.assertEqual(test_config.max_retries, 1)
        self.assertFalse(test_config.enable_caching)
        self.assertEqual(test_config.log_level, "DEBUG")
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test missing API token
        with self.assertRaises(ValueError):
            ClientConfig(api_token="")

class TestUtilityClasses(TestCodegenSDK):
    """Test utility classes"""
    
    def test_rate_limiter(self):
        """Test rate limiter functionality"""
        limiter = RateLimiter(requests_per_period=2, period_seconds=1)
        
        # Should allow first two requests
        start_time = time.time()
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        
        # Third request should be delayed
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        self.assertGreaterEqual(elapsed, 0.9)  # Should wait at least 0.9 seconds
        
        # Test usage stats
        usage = limiter.get_current_usage()
        self.assertIn("current_requests", usage)
        self.assertIn("max_requests", usage)
        self.assertIn("usage_percentage", usage)
    
    def test_cache_manager(self):
        """Test cache manager functionality"""
        cache = CacheManager(max_size=2, ttl_seconds=1)
        
        # Test basic set/get
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        # Test cache miss
        self.assertIsNone(cache.get("nonexistent"))
        
        # Test TTL expiration
        cache.set("key2", "value2")
        time.sleep(1.1)  # Wait for TTL to expire
        self.assertIsNone(cache.get("key2"))
        
        # Test cache size limit
        cache.set("key3", "value3")
        cache.set("key4", "value4")
        cache.set("key5", "value5")  # Should evict oldest
        
        # Test stats
        stats = cache.get_stats()
        self.assertIn("size", stats)
        self.assertIn("hits", stats)
        self.assertIn("misses", stats)
        self.assertIn("hit_rate_percentage", stats)
        
        # Test clear
        cache.clear()
        self.assertEqual(cache.get_stats()["size"], 0)
    
    def test_metrics_collector(self):
        """Test metrics collector functionality"""
        metrics = MetricsCollector()
        
        # Record some requests
        metrics.record_request("GET", "/test", 0.5, 200, "req1")
        metrics.record_request("POST", "/test", 1.0, 201, "req2")
        metrics.record_request("GET", "/error", 0.3, 404, "req3")
        
        # Get stats
        stats = metrics.get_stats()
        self.assertEqual(stats.total_requests, 3)
        self.assertEqual(stats.total_errors, 1)
        self.assertAlmostEqual(stats.error_rate, 1/3, places=2)
        self.assertGreater(stats.uptime_seconds, 0)
        self.assertIn(200, stats.status_code_distribution)
        self.assertIn(404, stats.status_code_distribution)
        
        # Test reset
        metrics.reset()
        stats = metrics.get_stats()
        self.assertEqual(stats.total_requests, 0)

class TestDataModels(TestCodegenSDK):
    """Test data model classes"""
    
    def test_user_response(self):
        """Test UserResponse data model"""
        user = UserResponse(
            id=123,
            email="test@example.com",
            github_user_id="456",
            github_username="testuser",
            avatar_url="https://example.com/avatar.jpg",
            full_name="Test User"
        )
        
        self.assertEqual(user.id, 123)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.github_username, "testuser")
    
    def test_agent_run_response(self):
        """Test AgentRunResponse data model"""
        agent_run = AgentRunResponse(
            id=789,
            organization_id=323,
            status="completed",
            created_at="2024-01-01T00:00:00Z",
            web_url="https://app.codegen.com/agent/trace/789",
            result="Task completed successfully",
            source_type=SourceType.API,
            github_pull_requests=[
                GithubPullRequestResponse(
                    id=1,
                    title="Test PR",
                    url="https://github.com/test/repo/pull/1",
                    created_at="2024-01-01T00:00:00Z"
                )
            ],
            metadata={"test": True}
        )
        
        self.assertEqual(agent_run.id, 789)
        self.assertEqual(agent_run.status, "completed")
        self.assertEqual(agent_run.source_type, SourceType.API)
        self.assertEqual(len(agent_run.github_pull_requests), 1)
        self.assertEqual(agent_run.metadata["test"], True)

class TestExceptions(TestCodegenSDK):
    """Test custom exceptions"""
    
    def test_codegen_api_error(self):
        """Test base CodegenAPIError"""
        error = CodegenAPIError("Test error", 400, {"detail": "Bad request"}, "req123")
        
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.response_data["detail"], "Bad request")
        self.assertEqual(error.request_id, "req123")
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError("Invalid input", {"field1": ["Required"]})
        
        self.assertEqual(error.status_code, 400)
        self.assertIn("field1", error.field_errors)
    
    def test_rate_limit_error(self):
        """Test RateLimitError"""
        error = RateLimitError(60, "req456")
        
        self.assertEqual(error.status_code, 429)
        self.assertEqual(error.retry_after, 60)
        self.assertIn("60 seconds", str(error))
    
    def test_authentication_error(self):
        """Test AuthenticationError"""
        error = AuthenticationError("Invalid token", "req789")
        
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.message, "Invalid token")

class TestClientBasicFunctionality(TestCodegenSDK):
    """Test basic client functionality"""
    
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertIsNotNone(self.client)
        self.assertIsNotNone(self.client.session)
        self.assertIsNotNone(self.client.rate_limiter)
        self.assertIsNotNone(self.client.cache)
        self.assertIsNotNone(self.client.metrics)
    
    def test_request_id_generation(self):
        """Test request ID generation"""
        id1 = self.client._generate_request_id()
        id2 = self.client._generate_request_id()
        
        self.assertIsInstance(id1, str)
        self.assertIsInstance(id2, str)
        self.assertNotEqual(id1, id2)
        self.assertEqual(len(id1), 36)  # UUID length
    
    def test_pagination_validation(self):
        """Test pagination parameter validation"""
        # Valid parameters
        self.client._validate_pagination(0, 50)
        self.client._validate_pagination(10, 100)
        
        # Invalid skip
        with self.assertRaises(ValidationError):
            self.client._validate_pagination(-1, 50)
        
        # Invalid limit
        with self.assertRaises(ValidationError):
            self.client._validate_pagination(0, 0)
        
        with self.assertRaises(ValidationError):
            self.client._validate_pagination(0, 101)
    
    def test_health_check(self):
        """Test API health check"""
        health = self.client.health_check()
        
        self.assertIn("status", health)
        self.assertIn("timestamp", health)
        
        if health["status"] == "healthy":
            self.assertIn("response_time_seconds", health)
            self.assertIn("user_id", health)
            self.assertGreater(health["response_time_seconds"], 0)
        else:
            self.assertIn("error", health)
    
    def test_client_stats(self):
        """Test client statistics"""
        # Make a request to generate some stats
        try:
            self.client.get_current_user()
        except Exception:
            pass  # We just want to generate metrics
        
        stats = self.client.get_stats()
        
        self.assertIn("config", stats)
        self.assertIn("base_url", stats["config"])
        self.assertIn("timeout", stats["config"])
        
        if "metrics" in stats:
            self.assertIn("total_requests", stats["metrics"])
            self.assertIn("uptime_seconds", stats["metrics"])
    
    def test_context_manager(self):
        """Test client as context manager"""
        with CodegenClient(self.config) as client:
            self.assertIsNotNone(client.session)
        
        # Session should be closed after context exit
        # Note: We can't easily test this without accessing private attributes

class TestAPIEndpoints(TestCodegenSDK):
    """Test actual API endpoints with real requests"""
    
    def test_get_current_user(self):
        """Test getting current user information"""
        try:
            user = self.client.get_current_user()
            
            self.assertIsInstance(user, UserResponse)
            self.assertIsInstance(user.id, int)
            self.assertIsInstance(user.github_username, str)
            self.assertGreater(len(user.github_username), 0)
            
            logger.info(f"Current user: {user.github_username} (ID: {user.id})")
            
        except Exception as e:
            self.fail(f"Failed to get current user: {e}")
    
    def test_get_organizations(self):
        """Test getting organizations"""
        try:
            orgs = self.client.get_organizations(limit=5)
            
            self.assertIsInstance(orgs, OrganizationsResponse)
            self.assertIsInstance(orgs.items, list)
            self.assertGreaterEqual(orgs.total, 0)
            self.assertGreaterEqual(orgs.pages, 1)
            
            if orgs.items:
                org = orgs.items[0]
                self.assertIsInstance(org, OrganizationResponse)
                self.assertIsInstance(org.id, int)
                self.assertIsInstance(org.name, str)
                self.assertIsInstance(org.settings, OrganizationSettings)
                
                logger.info(f"Found organization: {org.name} (ID: {org.id})")
            
        except Exception as e:
            self.fail(f"Failed to get organizations: {e}")
    
    def test_get_users(self):
        """Test getting users for organization"""
        try:
            users = self.client.get_users(CODEGEN_ORG_ID, limit=5)
            
            self.assertIsInstance(users, UsersResponse)
            self.assertIsInstance(users.items, list)
            self.assertGreaterEqual(users.total, 0)
            
            if users.items:
                user = users.items[0]
                self.assertIsInstance(user, UserResponse)
                self.assertIsInstance(user.id, int)
                self.assertIsInstance(user.github_username, str)
                
                logger.info(f"Found user: {user.github_username} (ID: {user.id})")
            
        except Exception as e:
            self.fail(f"Failed to get users: {e}")
    
    def test_create_and_get_agent_run(self):
        """Test creating and retrieving an agent run"""
        try:
            # Create agent run
            prompt = "Write a simple Python function that adds two numbers"
            metadata = {"test": True, "created_by": "test_suite"}
            
            agent_run = self.client.create_agent_run(
                org_id=self.org_id,
                prompt=prompt,
                metadata=metadata
            )
            
            self.assertIsInstance(agent_run, AgentRunResponse)
            self.assertIsInstance(agent_run.id, int)
            self.assertEqual(agent_run.organization_id, self.org_id)
            self.assertIsNotNone(agent_run.status)
            self.assertIsNotNone(agent_run.created_at)
            self.assertIsNotNone(agent_run.web_url)
            
            logger.info(f"Created agent run: {agent_run.id} with status: {agent_run.status}")
            
            # Get the agent run
            retrieved_run = self.client.get_agent_run(self.org_id, agent_run.id)
            
            self.assertEqual(retrieved_run.id, agent_run.id)
            self.assertEqual(retrieved_run.organization_id, self.org_id)
            
            logger.info(f"Retrieved agent run: {retrieved_run.id} with status: {retrieved_run.status}")
            
            return agent_run.id  # Return for other tests to use
            
        except Exception as e:
            self.fail(f"Failed to create/get agent run: {e}")
    
    def test_list_agent_runs(self):
        """Test listing agent runs"""
        try:
            runs = self.client.list_agent_runs(self.org_id, limit=5)
            
            self.assertIsInstance(runs, AgentRunsResponse)
            self.assertIsInstance(runs.items, list)
            self.assertGreaterEqual(runs.total, 0)
            
            if runs.items:
                run = runs.items[0]
                self.assertIsInstance(run, AgentRunResponse)
                self.assertIsInstance(run.id, int)
                self.assertEqual(run.organization_id, self.org_id)
                
                logger.info(f"Found agent run: {run.id} with status: {run.status}")
            
        except Exception as e:
            self.fail(f"Failed to list agent runs: {e}")
    
    def test_get_agent_run_logs(self):
        """Test getting agent run logs"""
        try:
            # First get a recent agent run
            runs = self.client.list_agent_runs(self.org_id, limit=1)
            
            if not runs.items:
                self.skipTest("No agent runs available for log testing")
            
            agent_run_id = runs.items[0].id
            
            # Get logs
            logs_response = self.client.get_agent_run_logs(self.org_id, agent_run_id, limit=10)
            
            self.assertIsInstance(logs_response, AgentRunWithLogsResponse)
            self.assertEqual(logs_response.id, agent_run_id)
            self.assertEqual(logs_response.organization_id, self.org_id)
            self.assertIsInstance(logs_response.logs, list)
            
            if logs_response.logs:
                log = logs_response.logs[0]
                self.assertIsInstance(log, AgentRunLogResponse)
                self.assertEqual(log.agent_run_id, agent_run_id)
                self.assertIsInstance(log.created_at, str)
                self.assertIsInstance(log.message_type, str)
                
                logger.info(f"Found {len(logs_response.logs)} logs for agent run {agent_run_id}")
            
        except Exception as e:
            self.fail(f"Failed to get agent run logs: {e}")

class TestAgentInterface(TestCodegenSDK):
    """Test the simplified Agent interface"""
    
    def test_agent_initialization(self):
        """Test Agent initialization"""
        try:
            with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
                self.assertIsNotNone(agent.client)
                self.assertEqual(agent.org_id, int(CODEGEN_ORG_ID))
                
                logger.info(f"Agent initialized with org_id: {agent.org_id}")
                
        except Exception as e:
            self.fail(f"Failed to initialize Agent: {e}")
    
    def test_agent_run_task(self):
        """Test running a task with Agent"""
        try:
            with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
                # Create a simple task
                task = agent.run("Write a Python function that returns 'Hello, World!'")
                
                self.assertIsInstance(task, Task)
                self.assertIsInstance(task.id, int)
                self.assertIsNotNone(task.status)
                self.assertIsNotNone(task.web_url)
                
                logger.info(f"Created task: {task.id} with status: {task.status}")
                logger.info(f"Task web URL: {task.web_url}")
                
                # Test task properties
                self.assertIsInstance(task.status, str)
                
                # Test task refresh
                task.refresh()
                self.assertIsNotNone(task.status)
                
        except Exception as e:
            self.fail(f"Failed to run task with Agent: {e}")
    
    def test_agent_list_tasks(self):
        """Test listing tasks with Agent"""
        try:
            with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
                tasks = agent.list_tasks(limit=3)
                
                self.assertIsInstance(tasks, list)
                
                if tasks:
                    task = tasks[0]
                    self.assertIsInstance(task, Task)
                    self.assertIsInstance(task.id, int)
                    
                    logger.info(f"Found {len(tasks)} recent tasks")
                    logger.info(f"Most recent task: {task.id} with status: {task.status}")
                
        except Exception as e:
            self.fail(f"Failed to list tasks with Agent: {e}")

class TestErrorHandling(TestCodegenSDK):
    """Test error handling and edge cases"""
    
    def test_invalid_org_id(self):
        """Test handling of invalid organization ID"""
        with self.assertRaises((NotFoundError, AuthenticationError, CodegenAPIError)):
            self.client.get_users("99999", limit=1)
    
    def test_invalid_agent_run_id(self):
        """Test handling of invalid agent run ID"""
        with self.assertRaises((NotFoundError, CodegenAPIError)):
            self.client.get_agent_run(self.org_id, 99999999)
    
    def test_empty_prompt(self):
        """Test validation of empty prompt"""
        with self.assertRaises(ValidationError):
            self.client.create_agent_run(self.org_id, "")
        
        with self.assertRaises(ValidationError):
            self.client.create_agent_run(self.org_id, "   ")
    
    def test_invalid_pagination(self):
        """Test invalid pagination parameters"""
        with self.assertRaises(ValidationError):
            self.client.get_users(CODEGEN_ORG_ID, skip=-1)
        
        with self.assertRaises(ValidationError):
            self.client.get_users(CODEGEN_ORG_ID, limit=0)
        
        with self.assertRaises(ValidationError):
            self.client.get_users(CODEGEN_ORG_ID, limit=101)

class TestPerformanceAndCaching(TestCodegenSDK):
    """Test performance features and caching"""
    
    def test_caching_behavior(self):
        """Test that caching works correctly"""
        if not self.client.cache:
            self.skipTest("Caching is disabled")
        
        # Clear cache first
        self.client.clear_cache()
        
        # Make the same request twice
        start_time = time.time()
        user1 = self.client.get_current_user()
        first_request_time = time.time() - start_time
        
        start_time = time.time()
        user2 = self.client.get_current_user()
        second_request_time = time.time() - start_time
        
        # Second request should be faster (cached)
        self.assertLess(second_request_time, first_request_time)
        self.assertEqual(user1.id, user2.id)
        
        # Check cache stats
        cache_stats = self.client.cache.get_stats()
        self.assertGreater(cache_stats["hits"], 0)
        
        logger.info(f"First request: {first_request_time:.3f}s, Second request: {second_request_time:.3f}s")
        logger.info(f"Cache stats: {cache_stats}")
    
    def test_rate_limiting(self):
        """Test rate limiting behavior"""
        # This test is tricky because we don't want to actually hit rate limits
        # We'll just verify the rate limiter is working
        
        usage_before = self.client.rate_limiter.get_current_usage()
        
        # Make a request
        try:
            self.client.get_current_user()
        except Exception:
            pass
        
        usage_after = self.client.rate_limiter.get_current_usage()
        
        # Usage should have increased
        self.assertGreaterEqual(usage_after["current_requests"], usage_before["current_requests"])
        
        logger.info(f"Rate limiter usage: {usage_after}")
    
    def test_metrics_collection(self):
        """Test metrics collection"""
        if not self.client.metrics:
            self.skipTest("Metrics collection is disabled")
        
        # Reset metrics
        self.client.reset_metrics()
        
        # Make some requests
        try:
            self.client.get_current_user()
            self.client.get_organizations(limit=1)
        except Exception:
            pass
        
        # Check metrics
        stats = self.client.get_stats()
        
        if "metrics" in stats:
            self.assertGreater(stats["metrics"]["total_requests"], 0)
            self.assertGreaterEqual(stats["metrics"]["uptime_seconds"], 0)
            
            logger.info(f"Metrics: {stats['metrics']['total_requests']} requests, "
                       f"{stats['metrics']['uptime_seconds']:.2f}s uptime")

if __name__ == "__main__":
    # Run specific test categories
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Codegen SDK tests")
    parser.add_argument("--category", choices=[
        "config", "utils", "models", "exceptions", "basic", "api", "agent", "errors", "performance", "all"
    ], default="all", help="Test category to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Configure test verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test suite based on category
    suite = unittest.TestSuite()
    
    if args.category in ["config", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestClientConfiguration))
    
    if args.category in ["utils", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestUtilityClasses))
    
    if args.category in ["models", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDataModels))
    
    if args.category in ["exceptions", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestExceptions))
    
    if args.category in ["basic", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestClientBasicFunctionality))
    
    if args.category in ["api", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAPIEndpoints))
    
    if args.category in ["agent", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAgentInterface))
    
    if args.category in ["errors", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestErrorHandling))
    
    if args.category in ["performance", "all"]:
        suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPerformanceAndCaching))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
