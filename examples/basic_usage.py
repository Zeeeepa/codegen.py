#!/usr/bin/env python3
"""
Basic usage examples for the Codegen Python SDK
"""

import os

from codegen import Agent
from codegen.core import ConfigPresets


def basic_agent_usage():
    """Basic agent usage example"""
    print("🤖 Basic Agent Usage Example")

    # Initialize agent with environment variables
    agent = Agent(org_id=os.getenv("CODEGEN_ORG_ID"), token=os.getenv("CODEGEN_API_TOKEN"))

    # Run a simple task
    print("Running agent with prompt...")
    task = agent.run("What is the current time?")

    print(f"📋 Task created: {task.id}")
    print(f"🔗 Status: {task.status}")

    # Wait for completion
    print("⏳ Waiting for completion...")
    result = task.wait_for_completion(timeout=60)

    print(f"✅ Task completed: {result.status}")
    if result.result:
        print(f"📄 Result: {result.result}")


def configuration_presets_example():
    """Configuration presets example"""
    print("\\n🔧 Configuration Presets Example")

    # Use development preset for faster feedback
    dev_config = ConfigPresets.development()
    agent = Agent(
        org_id=os.getenv("CODEGEN_ORG_ID"), token=os.getenv("CODEGEN_API_TOKEN"), config=dev_config
    )

    print("Using development preset...")
    task = agent.run("List the files in the current directory")
    print(f"📋 Task {task.id} created with development config")


def task_monitoring_example():
    """Task monitoring example"""
    print("\\n📊 Task Monitoring Example")

    agent = Agent(org_id=os.getenv("CODEGEN_ORG_ID"), token=os.getenv("CODEGEN_API_TOKEN"))

    # List recent tasks
    print("📋 Recent tasks:")
    tasks = agent.list_tasks(limit=5)

    for task in tasks:
        print(f"  - Task {task.id}: {task.status} ({task.created_at})")

        # Get logs for completed tasks
        if task.is_completed:
            logs = task.get_logs(limit=3)
            print(f"    📜 Recent logs ({len(logs.logs)} entries)")
            for log in logs.logs[:2]:  # Show first 2 logs
                print(f"      [{log.created_at}] {log.message_type}: {log.content[:50]}...")


def error_handling_example():
    """Error handling example"""
    print("\\n🛡️ Error Handling Example")

    try:
        agent = Agent(org_id=os.getenv("CODEGEN_ORG_ID"), token=os.getenv("CODEGEN_API_TOKEN"))

        # This might fail if the task takes too long
        task = agent.run("Perform a complex analysis")
        result = task.wait_for_completion(timeout=5)  # Very short timeout

    except TimeoutError as e:
        print(f"⏰ Task timed out: {e}")
        print("💡 You can increase the timeout or check the task status later")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("💡 Check your credentials and network connection")


def context_manager_example():
    """Context manager example"""
    print("\\n🔄 Context Manager Example")

    # Use agent as context manager for automatic cleanup
    with Agent(org_id=os.getenv("CODEGEN_ORG_ID"), token=os.getenv("CODEGEN_API_TOKEN")) as agent:
        print("🤖 Agent created with context manager")

        # Get client statistics
        stats = agent.get_stats()
        if stats:
            print(f"📊 Total requests: {stats.total_requests}")
            print(f"✅ Success rate: {stats.success_rate:.1f}%")

        print("🧹 Agent will be cleaned up automatically")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("CODEGEN_ORG_ID") or not os.getenv("CODEGEN_API_TOKEN"):
        print("❌ Please set CODEGEN_ORG_ID and CODEGEN_API_TOKEN environment variables")
        print("💡 You can get these from https://codegen.com/settings")
        exit(1)

    print("🚀 Codegen Python SDK Examples\\n")

    try:
        basic_agent_usage()
        configuration_presets_example()
        task_monitoring_example()
        error_handling_example()
        context_manager_example()

        print("\\n✅ All examples completed successfully!")

    except KeyboardInterrupt:
        print("\\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"\\n❌ Example failed: {e}")
        print("💡 Make sure your credentials are correct and you have network access")
