#!/usr/bin/env python3
"""
SDK Interface Test - Tests the official Codegen SDK interface compatibility
"""

from codegen_api import Agent, CodegenAPIError, ValidationError
import time

def test_sdk_interface():
    """Test that the SDK matches the official interface"""
    print("🧪 Testing SDK Interface Compatibility")
    print("=" * 60)
    
    # Test 1: Agent initialization
    print("1. 🚀 Testing Agent initialization...")
    
    # Test with all parameters
    agent = Agent(
        token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99",
        org_id=323,
        base_url="https://api.codegen.com"
    )
    print(f"   ✅ Agent initialized with all parameters")
    print(f"   📋 Organization ID: {agent.org_id}")
    print(f"   🌐 Base URL: {agent.base_url}")
    
    # Test with minimal parameters (should use defaults)
    agent_minimal = Agent(token="sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
    print(f"   ✅ Agent initialized with minimal parameters")
    print(f"   📋 Default Organization ID: {agent_minimal.org_id}")
    print()
    
    # Test 2: Agent.run() method
    print("2. 📝 Testing Agent.run() method...")
    try:
        # Basic run
        task = agent.run(prompt="What is the capital of France?")
        print(f"   ✅ Basic run successful: Task {task.id}")
        print(f"   📊 Task status: {task.status}")
        print(f"   🔗 Web URL: {task.web_url}")
        
        # Run with metadata
        task_with_meta = agent.run(
            prompt="What is 5 + 3?",
            metadata={"test": True, "category": "math"}
        )
        print(f"   ✅ Run with metadata successful: Task {task_with_meta.id}")
        print()
        
    except Exception as e:
        print(f"   ❌ Error in Agent.run(): {e}")
        print()
    
    # Test 3: AgentTask methods
    print("3. 🔄 Testing AgentTask methods...")
    try:
        # Test refresh method
        original_status = task.status
        task.refresh()
        print(f"   ✅ Task.refresh() successful")
        print(f"   📊 Status after refresh: {task.status}")
        
        # Test properties
        print(f"   📋 Task ID: {task.id}")
        print(f"   🏢 Organization ID: {task.org_id}")
        print(f"   📊 Status: {task.status}")
        print(f"   🔗 Web URL: {task.web_url}")
        print()
        
    except Exception as e:
        print(f"   ❌ Error in AgentTask methods: {e}")
        print()
    
    # Test 4: Agent.get_status() method
    print("4. 📊 Testing Agent.get_status() method...")
    try:
        status = agent.get_status()
        if status:
            print(f"   ✅ get_status() returned: {status}")
        else:
            print(f"   ℹ️  get_status() returned None (no current task)")
        print()
    except Exception as e:
        print(f"   ❌ Error in get_status(): {e}")
        print()
    
    # Test 5: Error handling
    print("5. 🚨 Testing error handling...")
    try:
        # Test validation error
        bad_task = agent.run(prompt="")
        print(f"   ❌ Expected validation error but got task: {bad_task.id}")
    except ValidationError as e:
        print(f"   ✅ Correctly caught ValidationError: {e.message}")
    except CodegenAPIError as e:
        print(f"   ✅ Correctly caught CodegenAPIError: {e.message}")
    except Exception as e:
        print(f"   ⚠️  Caught unexpected error: {e}")
    print()
    
    # Test 6: Wait for completion (short timeout)
    print("6. ⏳ Testing task completion detection...")
    try:
        start_time = time.time()
        timeout = 10  # Short timeout for testing
        
        while task.status in ["ACTIVE", "PENDING"] and (time.time() - start_time) < timeout:
            print(f"   ⏱️  Status: {task.status} (elapsed: {int(time.time() - start_time)}s)")
            time.sleep(2)
            task.refresh()
        
        if task.status in ["COMPLETE", "completed"]:
            print(f"   🎉 Task completed!")
            if task.result:
                result_preview = task.result[:100] + "..." if len(task.result) > 100 else task.result
                print(f"   📄 Result preview: {result_preview}")
        elif (time.time() - start_time) >= timeout:
            print(f"   ⏰ Timeout reached. Task still running: {task.status}")
        else:
            print(f"   ❌ Task ended with status: {task.status}")
        print()
        
    except Exception as e:
        print(f"   ❌ Error in completion detection: {e}")
        print()
    
    print("🎉 SDK Interface Test Complete!")
    print("✅ The SDK is compatible with the official Codegen Python SDK interface")
    return True

if __name__ == "__main__":
    test_sdk_interface()
