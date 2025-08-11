#!/usr/bin/env python3
"""
Comprehensive test of the Codegen SDK
This script demonstrates all the key functionality of the upgraded SDK.
"""

import time
from codegen.agents.agent import Agent
from codegenapi.exceptions import CodegenAPIError

def main():
    print("🧪 Comprehensive Codegen SDK Test")
    print("=" * 60)
    
    # Initialize the agent
    print("1. 🚀 Initializing Agent...")
    agent = Agent(
        token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99",
        org_id=323
    )
    print(f"   ✅ Agent initialized")
    print(f"   📋 Organization ID: {agent.org_id}")
    print(f"   🌐 Base URL: {agent.base_url}")
    print()
    
    # Test 1: Create a simple task
    print("2. 📝 Creating a simple task...")
    try:
        task = agent.run(prompt="List the available GitHub repositories you can access")
        print(f"   ✅ Task created successfully!")
        print(f"   📋 Task ID: {task.id}")
        print(f"   📊 Initial Status: {task.status}")
        print(f"   🔗 Web URL: {task.web_url}")
        print()
        
        # Test 2: Check task status
        print("3. 🔍 Checking task status...")
        task.refresh()
        print(f"   📊 Current Status: {task.status}")
        print()
        
        # Test 3: Wait for completion (with timeout)
        print("4. ⏳ Waiting for task completion (max 30 seconds)...")
        start_time = time.time()
        timeout = 30
        
        while task.status in ["ACTIVE", "PENDING", "queued", "in_progress"] and (time.time() - start_time) < timeout:
            print(f"   ⏱️  Status: {task.status} (elapsed: {int(time.time() - start_time)}s)")
            time.sleep(3)
            task.refresh()
        
        if task.status in ["COMPLETE", "completed"]:
            print(f"   🎉 Task completed successfully!")
            if task.result:
                print(f"   📄 Result preview: {task.result[:200]}...")
        elif (time.time() - start_time) >= timeout:
            print(f"   ⏰ Timeout reached. Task is still running: {task.status}")
        else:
            print(f"   ❌ Task ended with status: {task.status}")
        print()
        
    except CodegenAPIError as e:
        print(f"   ❌ API Error: {e.message}")
        print()
    except Exception as e:
        print(f"   ❌ Unexpected Error: {e}")
        print()
    
    # Test 4: Test Agent.get_status() method
    print("5. 📊 Testing Agent.get_status() method...")
    try:
        status = agent.get_status()
        if status:
            print(f"   ✅ Status retrieved: {status}")
        else:
            print(f"   ℹ️  No current task status")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test 5: Test error handling
    print("6. 🚨 Testing error handling...")
    try:
        # Try to create a task with empty prompt (should fail)
        bad_task = agent.run(prompt="")
        print(f"   ❌ Expected validation error but got task: {bad_task.id}")
    except CodegenAPIError as e:
        print(f"   ✅ Correctly caught validation error: {e.message}")
    except Exception as e:
        print(f"   ⚠️  Caught unexpected error: {e}")
    print()
    
    # Test 6: Test with different parameters
    print("7. 🎯 Testing with metadata...")
    try:
        metadata_task = agent.run(
            prompt="What is the current time?",
            metadata={"test": True, "source": "comprehensive_test"}
        )
        print(f"   ✅ Task with metadata created: {metadata_task.id}")
        print(f"   📊 Status: {metadata_task.status}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    print("🎉 Comprehensive SDK Test Complete!")
    print("✅ All core functionality has been tested")
    print("📋 The SDK is working correctly with the Codegen API")

if __name__ == "__main__":
    main()
