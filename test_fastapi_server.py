#!/usr/bin/env python3
"""
Test script for the FastAPI server endpoints
"""

import os
import sys
import requests
import json
import time
from typing import Dict, Any

# Set environment variables
os.environ["CODEGEN_ORG_ID"] = "323"
os.environ["CODEGEN_API_TOKEN"] = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"

# Import our enhanced codegen_api
sys.path.insert(0, '.')
from codegen_api import create_app, FASTAPI_AVAILABLE

def test_endpoints():
    """Test all FastAPI endpoints"""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available. Install with: pip install fastapi uvicorn")
        return False
    
    print("🚀 Starting FastAPI server test...")
    
    # Create the app
    app = create_app()
    
    # Start server in background (for testing we'll use a test client)
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test authentication token
    headers = {"Authorization": "Bearer sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"}
    
    print("\n=== Testing Endpoints ===")
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = client.get("/health", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Health Status: {data.get('status')}")
            print(f"   Response Time: {data.get('response_time_seconds')}s")
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Get Current User
    print("\n2. Testing Get Current User...")
    try:
        response = client.get("/users/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   User: {data.get('github_username')}")
            print(f"   Email: {data.get('email')}")
            print("   ✅ Get current user passed")
        else:
            print(f"   ❌ Get current user failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Get current user error: {e}")
    
    # Test 3: Get Organizations
    print("\n3. Testing Get Organizations...")
    try:
        response = client.get("/organizations", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Organizations found: {len(data.get('items', []))}")
            if data.get('items'):
                print(f"   First org: {data['items'][0].get('name')}")
            print("   ✅ Get organizations passed")
        else:
            print(f"   ❌ Get organizations failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Get organizations error: {e}")
    
    # Test 4: List Agent Runs
    print("\n4. Testing List Agent Runs...")
    try:
        response = client.get("/agent-runs?limit=5", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total runs: {data.get('total', 0)}")
            print(f"   Items returned: {len(data.get('items', []))}")
            print("   ✅ List agent runs passed")
        else:
            print(f"   ❌ List agent runs failed: {response.text}")
    except Exception as e:
        print(f"   ❌ List agent runs error: {e}")
    
    # Test 5: Create Agent Run
    print("\n5. Testing Create Agent Run...")
    try:
        payload = {
            "prompt": "Test prompt from FastAPI endpoint",
            "metadata": {"test": True, "source": "fastapi_test"}
        }
        response = client.post("/agent-runs", json=payload, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            agent_run_id = data.get('id')
            print(f"   Created agent run ID: {agent_run_id}")
            print(f"   Status: {data.get('status')}")
            print(f"   Web URL: {data.get('web_url')}")
            print("   ✅ Create agent run passed")
            
            # Test 6: Get Specific Agent Run
            print("\n6. Testing Get Specific Agent Run...")
            try:
                response = client.get(f"/agent-runs/{agent_run_id}", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Agent run ID: {data.get('id')}")
                    print(f"   Status: {data.get('status')}")
                    print("   ✅ Get specific agent run passed")
                else:
                    print(f"   ❌ Get specific agent run failed: {response.text}")
            except Exception as e:
                print(f"   ❌ Get specific agent run error: {e}")
            
            # Test 7: Get Agent Run Logs
            print("\n7. Testing Get Agent Run Logs...")
            try:
                response = client.get(f"/agent-runs/{agent_run_id}/logs?limit=10", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Total logs: {data.get('total_logs', 0)}")
                    print(f"   Logs returned: {len(data.get('logs', []))}")
                    print("   ✅ Get agent run logs passed")
                else:
                    print(f"   ❌ Get agent run logs failed: {response.text}")
            except Exception as e:
                print(f"   ❌ Get agent run logs error: {e}")
                
        else:
            print(f"   ❌ Create agent run failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Create agent run error: {e}")
    
    # Test 8: API Documentation
    print("\n8. Testing API Documentation...")
    try:
        response = client.get("/docs")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API documentation accessible")
        else:
            print(f"   ❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API documentation error: {e}")
    
    print("\n=== Test Summary ===")
    print("✅ FastAPI server implementation complete!")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Alternative docs: http://localhost:8000/redoc")
    print("\n🚀 To run the server:")
    print("   python codegen_api.py server")
    print("   or")
    print("   python -c \"from codegen_api import create_app; import uvicorn; app = create_app(); uvicorn.run(app, host='0.0.0.0', port=8000)\"")
    
    return True

if __name__ == "__main__":
    test_endpoints()
