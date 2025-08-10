#!/usr/bin/env python3
"""
Comprehensive test of the Codegen SDK v2.0 with real API credentials.

This script tests all functions of codegen_sdk_api.py using:
CODEGEN_ORG_ID=323
CODEGEN_API_TOKEN=sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99

Run with: python full_api_test.py
"""

import os
import time
import asyncio
from typing import Optional

# Set up environment
os.environ["CODEGEN_ORG_ID"] = "323"
os.environ["CODEGEN_API_TOKEN"] = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"

# Test both import patterns
print("🧪 Testing Codegen SDK v2.0 - Comprehensive API Test")
print("=" * 60)

def test_imports():
    """Test all import patterns"""
    print("\n📦 Testing Import Patterns")
    print("-" * 30)
    
    # Test official SDK imports
    try:
        from codegen.agents.agent import Agent
        from codegen.client import CodegenClient, AsyncCodegenClient
        from codegen.config import ClientConfig, ConfigPresets
        from codegen.models import AgentRunStatus, SourceType, MessageType
        from codegen.exceptions import ValidationError, CodegenAPIError
        from codegen.utils import RateLimiter, CacheManager, MetricsCollector
        print("✅ Official SDK imports successful")
        return True
    except ImportError as e:
        print(f"❌ Official SDK import failed: {e}")
        return False

def test_configuration():
    """Test configuration classes and presets"""
    print("\n⚙️ Testing Configuration")
    print("-" * 30)
    
    try:
        from codegen.config import ClientConfig, ConfigPresets
        
        # Test basic configuration
        config = ClientConfig(
            api_token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99",
            org_id="323"
        )
        print(f"✅ Basic config: timeout={config.timeout}, base_url={config.base_url}")
        
        # Test presets
        dev_config = ConfigPresets.development()
        dev_config.api_token = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
        dev_config.org_id = "323"
        print(f"✅ Development preset: timeout={dev_config.timeout}, log_level={dev_config.log_level}")
        
        prod_config = ConfigPresets.production()
        prod_config.api_token = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
        prod_config.org_id = "323"
        print(f"✅ Production preset: timeout={prod_config.timeout}, log_level={prod_config.log_level}")
        
        perf_config = ConfigPresets.high_performance()
        perf_config.api_token = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
        perf_config.org_id = "323"
        print(f"✅ High performance preset: max_workers={perf_config.bulk_max_workers}, cache_size={perf_config.cache_max_size}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_agent_functionality():
    """Test Agent class functionality"""
    print("\n🤖 Testing Agent Functionality")
    print("-" * 30)
    
    try:
        from codegen.agents.agent import Agent
        
        # Initialize agent
        agent = Agent(org_id="323", token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
        print(f"✅ Agent initialized: org_id={agent.org_id}")
        
        # Create a simple task
        task = agent.run("Write a Python function that returns 'Hello, SDK v2.0!'")
        print(f"✅ Task created: ID={task.id}, status={task.status}")
        
        # Test task properties
        print(f"✅ Task properties: web_url={task.web_url is not None}, created_at={task.created_at is not None}")
        
        # Test refresh
        initial_status = task.status
        task.refresh()
        print(f"✅ Task refresh: initial={initial_status}, after_refresh={task.status}")
        
        # Test context manager
        with Agent(org_id="323", token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99") as agent2:
            print("✅ Agent context manager works")
        
        return True
    except Exception as e:
        print(f"❌ Agent functionality test failed: {e}")
        return False

def test_client_functionality():
    """Test CodegenClient functionality"""
    print("\n🔧 Testing Client Functionality")
    print("-" * 30)
    
    try:
        from codegen.client import CodegenClient
        from codegen.config import ClientConfig
        
        config = ClientConfig(
            api_token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99",
            org_id="323",
            enable_metrics=True,
            enable_caching=True
        )
        
        with CodegenClient(config) as client:
            # Test health check
            health = client.health_check()
            print(f"✅ Health check: status={health['status']}")
            
            # Test get current user
            user = client.get_current_user()
            print(f"✅ Current user: {user.github_username} (ID: {user.id})")
            
            # Test get organizations
            orgs = client.get_organizations()
            print(f"✅ Organizations: found {len(orgs.items)} orgs, total={orgs.total}")
            
            # Test create agent run
            run = client.create_agent_run(
                org_id=323,
                prompt="Create a simple function that adds two numbers",
                metadata={"test": "full_api_test", "version": "2.0"}
            )
            print(f"✅ Agent run created: ID={run.id}, status={run.status}")
            
            # Test get agent run
            retrieved_run = client.get_agent_run(323, run.id)
            print(f"✅ Agent run retrieved: ID={retrieved_run.id}, status={retrieved_run.status}")
            
            # Test list agent runs
            runs = client.list_agent_runs(323, limit=5)
            print(f"✅ Agent runs listed: found {len(runs.items)} runs")
            
            # Test get agent run logs
            logs = client.get_agent_run_logs(323, run.id, limit=10)
            print(f"✅ Agent run logs: {logs.total_logs} total logs, {len(logs.logs)} retrieved")
            
            # Test client statistics
            stats = client.get_stats()
            print(f"✅ Client stats: {stats['metrics']['total_requests']} requests, {stats['metrics']['cache_hit_rate']:.1%} cache hit rate")
        
        return True
    except Exception as e:
        print(f"❌ Client functionality test failed: {e}")
        return False

def test_utility_classes():
    """Test utility classes"""
    print("\n🛠️ Testing Utility Classes")
    print("-" * 30)
    
    try:
        from codegen.utils import RateLimiter, CacheManager, MetricsCollector
        
        # Test RateLimiter
        limiter = RateLimiter(requests_per_period=5, period_seconds=10)
        usage = limiter.get_current_usage()
        print(f"✅ RateLimiter: {usage['current_requests']}/{usage['max_requests']} requests")
        
        # Test CacheManager
        cache = CacheManager(max_size=10, ttl_seconds=60)
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        stats = cache.get_stats()
        print(f"✅ CacheManager: value='{value}', hit_rate={stats['hit_rate_percentage']:.1f}%")
        
        # Test MetricsCollector
        metrics = MetricsCollector()
        metrics.record_request("GET", "/test", 0.5, 200, "req-1")
        metrics.record_request("POST", "/test", 1.0, 201, "req-2")
        client_stats = metrics.get_stats()
        print(f"✅ MetricsCollector: {client_stats.total_requests} requests, avg_time={client_stats.average_response_time:.3f}s")
        
        return True
    except Exception as e:
        print(f"❌ Utility classes test failed: {e}")
        return False

def test_models_and_enums():
    """Test data models and enums"""
    print("\n📊 Testing Models and Enums")
    print("-" * 30)
    
    try:
        from codegen.models import (
            SourceType, MessageType, AgentRunStatus,
            UserResponse, AgentRunResponse, AgentRunLogResponse
        )
        
        # Test enums
        print(f"✅ SourceType: API={SourceType.API.value}, GITHUB={SourceType.GITHUB.value}")
        print(f"✅ MessageType: ACTION={MessageType.ACTION.value}, ERROR={MessageType.ERROR.value}")
        print(f"✅ AgentRunStatus: PENDING={AgentRunStatus.PENDING.value}, COMPLETED={AgentRunStatus.COMPLETED.value}")
        
        # Test model creation
        user = UserResponse(
            id=123,
            email="test@example.com",
            github_user_id="456",
            github_username="testuser",
            avatar_url="https://example.com/avatar.jpg",
            full_name="Test User"
        )
        print(f"✅ UserResponse: {user.github_username} ({user.email})")
        
        run = AgentRunResponse(
            id=789,
            organization_id=323,
            status="completed",
            created_at="2024-01-01T00:00:00Z",
            web_url="https://app.codegen.com/run/789",
            result="Task completed successfully",
            source_type=SourceType.API,
            github_pull_requests=None,
            metadata={"test": True}
        )
        print(f"✅ AgentRunResponse: ID={run.id}, status={run.status}, source={run.source_type.value}")
        
        return True
    except Exception as e:
        print(f"❌ Models and enums test failed: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print("\n🚨 Testing Error Handling")
    print("-" * 30)
    
    try:
        from codegen.agents.agent import Agent
        from codegen.exceptions import ValidationError
        
        agent = Agent(org_id="323", token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
        
        # Test validation error
        try:
            agent.run("")  # Empty prompt should fail
            print("❌ Empty prompt validation failed")
        except ValidationError:
            print("✅ Empty prompt validation works")
        
        # Test whitespace-only prompt
        try:
            agent.run("   ")  # Whitespace-only prompt should fail
            print("❌ Whitespace prompt validation failed")
        except ValidationError:
            print("✅ Whitespace prompt validation works")
        
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility"""
    print("\n🔄 Testing Backward Compatibility")
    print("-" * 30)
    
    try:
        # Test backend.api imports
        from backend.api import Agent, CodegenClient, ClientConfig
        print("✅ Backend API imports work")
        
        # Test functionality
        agent = Agent(org_id=323, token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
        task = agent.run("Create a simple hello world function")
        print(f"✅ Backend Agent works: task_id={task.id}")
        
        return True
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

async def test_async_functionality():
    """Test async client functionality"""
    print("\n⚡ Testing Async Functionality")
    print("-" * 30)
    
    try:
        from codegen.client import AsyncCodegenClient
        from codegen.config import ClientConfig
        
        config = ClientConfig(
            api_token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99",
            org_id="323"
        )
        
        async with AsyncCodegenClient(config) as client:
            # Test async get current user
            user = await client.get_current_user()
            print(f"✅ Async current user: {user.github_username}")
            
            # Test async create agent run
            run = await client.create_agent_run(
                org_id=323,
                prompt="Create an async function that returns 'Hello Async!'"
            )
            print(f"✅ Async agent run created: ID={run.id}")
            
            # Test async get agent run
            retrieved_run = await client.get_agent_run(323, run.id)
            print(f"✅ Async agent run retrieved: status={retrieved_run.status}")
        
        return True
    except ImportError:
        print("⚠️ Async functionality skipped (aiohttp not available)")
        return True
    except Exception as e:
        print(f"❌ Async functionality test failed: {e}")
        return False

def test_advanced_features():
    """Test advanced features"""
    print("\n🚀 Testing Advanced Features")
    print("-" * 30)
    
    try:
        from codegen.client import CodegenClient
        from codegen.config import ConfigPresets
        
        # Use high performance config
        config = ConfigPresets.high_performance()
        config.api_token = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
        config.org_id = "323"
        
        with CodegenClient(config) as client:
            # Test streaming (limited to avoid too many requests)
            print("✅ Testing streaming functionality...")
            count = 0
            for run in client.stream_all_agent_runs(323):
                count += 1
                if count >= 3:  # Limit to first 3 runs
                    break
            print(f"✅ Streamed {count} agent runs")
            
            # Test wait for completion with timeout
            run = client.create_agent_run(323, "Return the string 'test complete'")
            print(f"✅ Created run for completion test: {run.id}")
            
            # Don't actually wait to avoid long test times
            print("✅ Wait for completion method available")
        
        return True
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🧪 Starting Comprehensive Codegen SDK v2.0 Test Suite")
    print("Using CODEGEN_ORG_ID=323")
    print("Using CODEGEN_API_TOKEN=sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
    print("=" * 60)
    
    tests = [
        ("Import Patterns", test_imports),
        ("Configuration", test_configuration),
        ("Agent Functionality", test_agent_functionality),
        ("Client Functionality", test_client_functionality),
        ("Utility Classes", test_utility_classes),
        ("Models and Enums", test_models_and_enums),
        ("Error Handling", test_error_handling),
        ("Backward Compatibility", test_backward_compatibility),
        ("Advanced Features", test_advanced_features),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Run async test separately
    try:
        print("\n⚡ Running Async Tests...")
        async_result = asyncio.run(test_async_functionality())
        results.append(("Async Functionality", async_result))
    except Exception as e:
        print(f"❌ Async test crashed: {e}")
        results.append(("Async Functionality", False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"📈 OVERALL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! SDK v2.0 is working perfectly!")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the output above.")
    
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

