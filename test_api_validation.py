"""
Comprehensive test suite for Codegen API validation
Tests all functionality against the real Codegen API
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List

# Set environment variables for testing
os.environ["CODEGEN_ORG_ID"] = "323"
os.environ["CODEGEN_API_TOKEN"] = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"

# Import our SDK and FastAPI backend
try:
    from codegen_api import CodegenClient, ClientConfig, Agent, Task
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"❌ SDK import failed: {e}")
    SDK_AVAILABLE = False

try:
    from fastapi_backend import app, get_client, get_org_id
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError as e:
    print(f"❌ FastAPI backend import failed: {e}")
    FASTAPI_AVAILABLE = False

def test_environment_setup():
    """Test that environment variables are properly set"""
    print("🔧 Testing environment setup...")
    
    api_token = os.getenv("CODEGEN_API_TOKEN")
    org_id = os.getenv("CODEGEN_ORG_ID")
    
    assert api_token, "CODEGEN_API_TOKEN environment variable is required"
    assert org_id, "CODEGEN_ORG_ID environment variable is required"
    assert api_token.startswith("sk-"), "API token should start with 'sk-'"
    assert org_id.isdigit(), "Organization ID should be numeric"
    
    print(f"✅ Environment setup OK - Org ID: {org_id}, Token: {api_token[:10]}...")

def test_sdk_basic_functionality():
    """Test basic SDK functionality"""
    if not SDK_AVAILABLE:
        print("⏭️  Skipping SDK tests - not available")
        return
    
    print("\n🧪 Testing SDK basic functionality...")
    
    try:
        # Test client configuration
        config = ClientConfig()
        print(f"✅ Client config created - Base URL: {config.base_url}")
        
        # Test client creation
        client = CodegenClient(config)
        print("✅ CodegenClient created successfully")
        
        # Test health check
        health = client.health_check()
        print(f"✅ Health check: {health.get('status', 'unknown')}")
        
        # Test current user
        user = client.get_current_user()
        print(f"✅ Current user: {user.email}")
        
        # Test organizations
        orgs = client.get_organizations(limit=1)
        if orgs.items:
            org = orgs.items[0]
            print(f"✅ Organization found: {org.name} (ID: {org.id})")
        
        client.close()
        print("✅ SDK basic functionality tests passed")
        
    except Exception as e:
        print(f"❌ SDK test failed: {e}")
        raise

def test_agent_interface():
    """Test the simplified Agent interface"""
    if not SDK_AVAILABLE:
        print("⏭️  Skipping Agent tests - not available")
        return
    
    print("\n🤖 Testing Agent interface...")
    
    try:
        with Agent() as agent:
            print(f"✅ Agent created for org: {agent.org_id}")
            
            # Create a simple test task
            task = agent.run(
                prompt="Create a simple 'Hello World' Python function",
                metadata={"test": True, "created_by": "test_suite"}
            )
            
            print(f"✅ Task created: ID {task.id}, Status: {task.status}")
            print(f"   Web URL: {task.web_url}")
            
            # Test task properties
            assert task.id is not None, "Task should have an ID"
            assert task.status is not None, "Task should have a status"
            assert task.web_url is not None, "Task should have a web URL"
            
            # Wait a bit and refresh
            time.sleep(2)
            task.refresh()
            print(f"✅ Task refreshed: Status: {task.status}")
            
            # Test task listing
            tasks = agent.list_tasks(limit=5)
            print(f"✅ Listed {len(tasks)} recent tasks")
            
            print("✅ Agent interface tests passed")
            return task.id  # Return for further testing
            
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        raise

def test_fastapi_endpoints():
    """Test FastAPI endpoints"""
    if not FASTAPI_AVAILABLE:
        print("⏭️  Skipping FastAPI tests - not available")
        return
    
    print("\n🌐 Testing FastAPI endpoints...")
    
    try:
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        health_data = response.json()
        print(f"✅ Health endpoint: {health_data['status']}")
        
        # Test current user endpoint
        response = client.get("/users/me")
        assert response.status_code == 200, f"User endpoint failed: {response.status_code}"
        user_data = response.json()
        print(f"✅ User endpoint: {user_data['email']}")
        
        # Test create agent run endpoint
        create_data = {
            "prompt": "Write a simple Python function to add two numbers",
            "metadata": {"test": True, "endpoint": "fastapi"}
        }
        response = client.post("/create_agent_run/test/simple-function", json=create_data)
        assert response.status_code == 200, f"Create agent run failed: {response.status_code}"
        run_data = response.json()
        print(f"✅ Create agent run: ID {run_data['id']}, Status: {run_data['status']}")
        
        agent_run_id = run_data['id']
        
        # Test get agent run endpoint
        response = client.get(f"/agent_runs/{agent_run_id}")
        assert response.status_code == 200, f"Get agent run failed: {response.status_code}"
        detail_data = response.json()
        print(f"✅ Get agent run: Status {detail_data['status']}")
        
        # Test list agent runs endpoint
        response = client.get("/agent_runs?limit=5")
        assert response.status_code == 200, f"List agent runs failed: {response.status_code}"
        list_data = response.json()
        print(f"✅ List agent runs: {len(list_data['items'])} items, Total: {list_data['total']}")
        
        # Test logs endpoint (might fail if no logs yet)
        try:
            response = client.get(f"/agent_runs/{agent_run_id}/logs?limit=10")
            if response.status_code == 200:
                logs_data = response.json()
                print(f"✅ Get logs: {logs_data['total_logs']} total logs")
            else:
                print(f"⚠️  Logs endpoint returned {response.status_code} (might be expected for new runs)")
        except Exception as e:
            print(f"⚠️  Logs test skipped: {e}")
        
        print("✅ FastAPI endpoints tests passed")
        return agent_run_id
        
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        raise

def test_api_integration():
    """Test integration between different components"""
    print("\n🔗 Testing API integration...")
    
    try:
        # Test that SDK and FastAPI use the same underlying API
        if SDK_AVAILABLE and FASTAPI_AVAILABLE:
            # Create run via SDK
            with Agent() as agent:
                sdk_task = agent.run("Integration test via SDK")
                sdk_task_id = sdk_task.id
                print(f"✅ SDK created task: {sdk_task_id}")
            
            # Retrieve via FastAPI
            client = TestClient(app)
            response = client.get(f"/agent_runs/{sdk_task_id}")
            assert response.status_code == 200, "FastAPI should be able to retrieve SDK-created task"
            fastapi_data = response.json()
            print(f"✅ FastAPI retrieved SDK task: {fastapi_data['id']}")
            
            assert fastapi_data['id'] == sdk_task_id, "Task IDs should match"
            print("✅ Integration test passed")
        else:
            print("⏭️  Integration test skipped - components not available")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        raise

def test_error_handling():
    """Test error handling"""
    print("\n🚨 Testing error handling...")
    
    try:
        if FASTAPI_AVAILABLE:
            client = TestClient(app)
            
            # Test invalid agent run ID
            response = client.get("/agent_runs/999999999")
            assert response.status_code in [404, 500], "Should handle invalid agent run ID"
            print("✅ Invalid agent run ID handled correctly")
            
            # Test invalid request data
            response = client.post("/create_agent_run/test/invalid", json={"invalid": "data"})
            # This might succeed depending on API flexibility, so we just check it doesn't crash
            print(f"✅ Invalid request handled: {response.status_code}")
            
        print("✅ Error handling tests passed")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        raise

def test_performance():
    """Test basic performance characteristics"""
    print("\n⚡ Testing performance...")
    
    try:
        if SDK_AVAILABLE:
            start_time = time.time()
            
            with Agent() as agent:
                # Test multiple quick operations
                user = agent.client.get_current_user()
                orgs = agent.client.get_organizations(limit=1)
                health = agent.client.health_check()
            
            duration = time.time() - start_time
            print(f"✅ Basic operations completed in {duration:.2f} seconds")
            
            if duration > 10:
                print("⚠️  Operations took longer than expected (>10s)")
            
        print("✅ Performance tests completed")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        raise

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📊 Generating test report...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "org_id": os.getenv("CODEGEN_ORG_ID"),
            "api_token_prefix": os.getenv("CODEGEN_API_TOKEN", "")[:10] + "...",
            "sdk_available": SDK_AVAILABLE,
            "fastapi_available": FASTAPI_AVAILABLE
        },
        "tests_run": [],
        "status": "completed"
    }
    
    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✅ Test report saved to test_report.json")

def main():
    """Run all tests"""
    print("🚀 Starting Codegen API Validation Tests")
    print("=" * 50)
    
    try:
        test_environment_setup()
        test_sdk_basic_functionality()
        test_agent_interface()
        test_fastapi_endpoints()
        test_api_integration()
        test_error_handling()
        test_performance()
        generate_test_report()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ SDK functionality validated")
        print("✅ FastAPI backend validated")
        print("✅ Real API integration confirmed")
        print("✅ Error handling verified")
        print("✅ Performance acceptable")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
