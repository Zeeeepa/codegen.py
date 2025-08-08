#!/usr/bin/env python3
"""
Example Usage of Codegen SDK API
Demonstrates how to use the comprehensive Codegen API client
"""

import os
import time
from codegen_sdk_api import Agent, CodegenClient, ConfigPresets, Task

# Configuration
CODEGEN_ORG_ID = "323"
CODEGEN_API_TOKEN = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"

def example_1_simple_agent():
    """Example 1: Using the simplified Agent interface"""
    print("=== Example 1: Simple Agent Interface ===")
    
    try:
        # Initialize agent with credentials
        with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
            print(f"✅ Agent initialized for organization {agent.org_id}")
            
            # Create a simple task
            print("\n📝 Creating a task...")
            task = agent.run(
                prompt="Write a Python function that calculates the factorial of a number",
                metadata={"example": "factorial", "priority": "low"}
            )
            
            print(f"✅ Task created: {task.id}")
            print(f"📊 Status: {task.status}")
            print(f"🌐 Web URL: {task.web_url}")
            
            # Check task status
            print(f"\n🔄 Current status: {task.status}")
            
            # List recent tasks
            print("\n📋 Recent tasks:")
            recent_tasks = agent.list_tasks(limit=3)
            for i, t in enumerate(recent_tasks, 1):
                print(f"  {i}. Task {t.id}: {t.status}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_2_full_client():
    """Example 2: Using the full CodegenClient with advanced features"""
    print("\n=== Example 2: Full Client with Advanced Features ===")
    
    try:
        # Use development configuration preset
        config = ConfigPresets.development()
        config.api_token = CODEGEN_API_TOKEN
        config.org_id = CODEGEN_ORG_ID
        
        with CodegenClient(config) as client:
            print("✅ Client initialized with development configuration")
            
            # Health check
            health = client.health_check()
            print(f"🏥 Health check: {health['status']}")
            if health['status'] == 'healthy':
                print(f"⚡ Response time: {health['response_time_seconds']:.3f}s")
            
            # Get current user
            user = client.get_current_user()
            print(f"👤 Current user: {user.github_username} (ID: {user.id})")
            
            # Get organizations
            orgs = client.get_organizations(limit=2)
            print(f"🏢 Found {orgs.total} organizations:")
            for org in orgs.items:
                print(f"  - {org.name} (ID: {org.id})")
            
            # Create an agent run with detailed metadata
            print(f"\n🚀 Creating agent run...")
            agent_run = client.create_agent_run(
                org_id=int(CODEGEN_ORG_ID),
                prompt="Create a simple REST API endpoint for user management",
                metadata={
                    "example": "rest_api",
                    "complexity": "medium",
                    "estimated_time": "10-15 minutes",
                    "tags": ["api", "rest", "users"]
                }
            )
            
            print(f"✅ Agent run created: {agent_run.id}")
            print(f"📊 Status: {agent_run.status}")
            print(f"🌐 Web URL: {agent_run.web_url}")
            
            # Get client statistics
            stats = client.get_stats()
            print(f"\n📈 Client Statistics:")
            print(f"  - Base URL: {stats['config']['base_url']}")
            print(f"  - Timeout: {stats['config']['timeout']}s")
            print(f"  - Caching: {'enabled' if stats['config']['caching_enabled'] else 'disabled'}")
            
            if 'metrics' in stats:
                metrics = stats['metrics']
                print(f"  - Total requests: {metrics['total_requests']}")
                print(f"  - Average response time: {metrics['average_response_time']:.3f}s")
                print(f"  - Error rate: {metrics['error_rate']:.1%}")
            
            if 'cache' in stats:
                cache = stats['cache']
                print(f"  - Cache hit rate: {cache['hit_rate_percentage']:.1f}%")
                print(f"  - Cache size: {cache['size']}/{cache['max_size']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_3_task_monitoring():
    """Example 3: Task monitoring and waiting for completion"""
    print("\n=== Example 3: Task Monitoring ===")
    
    try:
        with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
            # Create a task
            print("📝 Creating a task for monitoring...")
            task = agent.run("Write a Python script that reads a CSV file and generates a summary report")
            
            print(f"✅ Task created: {task.id}")
            print(f"🌐 Monitor at: {task.web_url}")
            
            # Monitor task status
            print("\n🔄 Monitoring task status...")
            max_checks = 10
            check_interval = 3
            
            for i in range(max_checks):
                task.refresh()
                print(f"  Check {i+1}: {task.status}")
                
                if task.status in ['completed', 'failed', 'cancelled']:
                    break
                
                if i < max_checks - 1:  # Don't sleep on the last iteration
                    time.sleep(check_interval)
            
            # Final status
            print(f"\n✅ Final status: {task.status}")
            
            if task.result:
                print(f"📄 Result preview: {task.result[:200]}...")
            
            # Get task logs
            print(f"\n📋 Getting task logs...")
            logs = task.get_logs(limit=5)
            print(f"Found {logs.total_logs} total logs, showing first {len(logs.logs)}:")
            
            for log in logs.logs[:3]:  # Show first 3 logs
                print(f"  [{log.created_at}] {log.message_type}")
                if log.thought:
                    print(f"    💭 {log.thought[:100]}...")
                if log.tool_name:
                    print(f"    🔧 Tool: {log.tool_name}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_4_error_handling():
    """Example 4: Error handling and validation"""
    print("\n=== Example 4: Error Handling ===")
    
    try:
        with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
            # Test various error conditions
            print("🧪 Testing error handling...")
            
            # Test empty prompt
            try:
                agent.run("")
                print("❌ Should have failed with empty prompt")
            except Exception as e:
                print(f"✅ Correctly caught empty prompt error: {type(e).__name__}")
            
            # Test invalid task ID
            try:
                agent.get_task(99999999)
                print("❌ Should have failed with invalid task ID")
            except Exception as e:
                print(f"✅ Correctly caught invalid task ID error: {type(e).__name__}")
            
            print("✅ Error handling tests completed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def example_5_configuration_presets():
    """Example 5: Using different configuration presets"""
    print("\n=== Example 5: Configuration Presets ===")
    
    # Test different configuration presets
    presets = {
        "Development": ConfigPresets.development(),
        "Production": ConfigPresets.production(),
        "Testing": ConfigPresets.testing(),
    }
    
    for name, config in presets.items():
        config.api_token = CODEGEN_API_TOKEN
        config.org_id = CODEGEN_ORG_ID
        
        print(f"\n🔧 {name} Configuration:")
        print(f"  - Timeout: {config.timeout}s")
        print(f"  - Max retries: {config.max_retries}")
        print(f"  - Log level: {config.log_level}")
        print(f"  - Caching: {'enabled' if config.enable_caching else 'disabled'}")
        print(f"  - Rate limit: {config.rate_limit_requests_per_period} req/min")
        
        # Test with a quick health check
        try:
            with CodegenClient(config) as client:
                health = client.health_check()
                print(f"  - Health check: {health['status']}")
        except Exception as e:
            print(f"  - Health check failed: {e}")

def main():
    """Run all examples"""
    print("🚀 Codegen SDK API Examples")
    print("=" * 50)
    
    # Set environment variables for convenience
    os.environ["CODEGEN_ORG_ID"] = CODEGEN_ORG_ID
    os.environ["CODEGEN_API_TOKEN"] = CODEGEN_API_TOKEN
    
    # Run examples
    example_1_simple_agent()
    example_2_full_client()
    example_3_task_monitoring()
    example_4_error_handling()
    example_5_configuration_presets()
    
    print("\n✅ All examples completed!")
    print("\n💡 Tips:")
    print("  - Use the Agent class for simple use cases")
    print("  - Use CodegenClient for advanced features and configuration")
    print("  - Monitor tasks using the web_url for real-time updates")
    print("  - Check the logs for detailed execution information")
    print("  - Use different configuration presets for different environments")

if __name__ == "__main__":
    main()
