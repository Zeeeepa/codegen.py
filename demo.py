#!/usr/bin/env python3
"""
Demo script for Codegen FastAPI Backend
Shows how to use the API endpoints
"""

import os
import json
import time
import requests
from datetime import datetime

# Set environment variables
os.environ["CODEGEN_ORG_ID"] = "323"
os.environ["CODEGEN_API_TOKEN"] = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']} at {data['timestamp']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_user_info():
    """Test the user info endpoint"""
    print("\n👤 Testing user info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/users/me")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User: {data['email']} (ID: {data['id']})")
            return True
        else:
            print(f"❌ User info failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ User info error: {e}")
        return False

def test_create_agent_run():
    """Test creating an agent run"""
    print("\n🤖 Testing agent run creation...")
    try:
        # Test the path-based endpoint
        payload = {
            "prompt": "Write a simple Python function that calculates the factorial of a number",
            "metadata": {
                "demo": True,
                "created_at": datetime.now().isoformat(),
                "test_type": "demo_script"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/create_agent_run/demo/factorial-function",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent run created: ID {data['id']}")
            print(f"   Status: {data['status']}")
            print(f"   Web URL: {data['web_url']}")
            return data['id']
        else:
            print(f"❌ Agent run creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Agent run creation error: {e}")
        return None

def test_get_agent_run(agent_run_id):
    """Test getting agent run details"""
    if not agent_run_id:
        return
    
    print(f"\n📋 Testing agent run details for ID {agent_run_id}...")
    try:
        response = requests.get(f"{BASE_URL}/agent_runs/{agent_run_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent run details retrieved")
            print(f"   Status: {data['status']}")
            print(f"   Prompt: {data['prompt'][:50]}...")
            if data.get('result'):
                print(f"   Result: {data['result'][:100]}...")
            return True
        else:
            print(f"❌ Get agent run failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get agent run error: {e}")
        return False

def test_list_agent_runs():
    """Test listing agent runs"""
    print("\n📝 Testing agent runs list...")
    try:
        response = requests.get(f"{BASE_URL}/agent_runs?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent runs listed: {len(data['items'])} items")
            print(f"   Total: {data['total']}, Page: {data['page']}")
            
            for item in data['items'][:3]:  # Show first 3
                print(f"   - ID {item['id']}: {item['status']} - {item['prompt'][:40]}...")
            
            return True
        else:
            print(f"❌ List agent runs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ List agent runs error: {e}")
        return False

def test_agent_run_logs(agent_run_id):
    """Test getting agent run logs"""
    if not agent_run_id:
        return
    
    print(f"\n📊 Testing logs for agent run {agent_run_id}...")
    try:
        response = requests.get(f"{BASE_URL}/agent_runs/{agent_run_id}/logs?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Logs retrieved: {data['total_logs']} total logs")
            
            for log in data['logs'][:3]:  # Show first 3
                print(f"   - {log['message_type']}: {log.get('thought', 'No thought')[:50]}...")
            
            return True
        else:
            print(f"❌ Get logs failed: {response.status_code}")
            print(f"   This might be expected for new runs with no logs yet")
            return False
    except Exception as e:
        print(f"❌ Get logs error: {e}")
        return False

def main():
    """Run the demo"""
    print("🚀 Codegen FastAPI Backend Demo")
    print("=" * 50)
    print("Make sure the FastAPI server is running:")
    print("  python fastapi_backend.py")
    print("=" * 50)
    
    # Test all endpoints
    success_count = 0
    total_tests = 6
    
    if test_health():
        success_count += 1
    
    if test_user_info():
        success_count += 1
    
    agent_run_id = test_create_agent_run()
    if agent_run_id:
        success_count += 1
        
        # Wait a moment for the run to process
        print("\n⏳ Waiting 3 seconds for agent run to process...")
        time.sleep(3)
        
        if test_get_agent_run(agent_run_id):
            success_count += 1
        
        if test_agent_run_logs(agent_run_id):
            success_count += 1
    else:
        print("⏭️  Skipping dependent tests due to creation failure")
    
    if test_list_agent_runs():
        success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Demo Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! FastAPI backend is working correctly.")
    elif success_count >= total_tests - 1:
        print("✅ Most tests passed! Backend is mostly functional.")
    else:
        print("⚠️  Some tests failed. Check the server logs and configuration.")
    
    print("\n💡 Next steps:")
    print("  - Visit http://localhost:8000/docs for interactive API documentation")
    print("  - Run the full test suite: python test_api_validation.py")
    print("  - Build your frontend using these API endpoints!")

if __name__ == "__main__":
    main()
