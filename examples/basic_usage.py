#!/usr/bin/env python3
"""
Basic usage examples for CodegenAPI
"""

import os
import time
from codegenapi import TaskManager, Config
from codegenapi.exceptions import CodegenAPIError


def main():
    """Demonstrate basic CodegenAPI usage"""
    
    # Check environment variables
    if not os.getenv("CODEGEN_API_TOKEN"):
        print("❌ CODEGEN_API_TOKEN environment variable not set")
        print("Please set it with: export CODEGEN_API_TOKEN='your_token'")
        return
    
    try:
        # Initialize configuration
        print("🔧 Initializing CodegenAPI...")
        config = Config()
        
        # Validate configuration
        errors = config.validate()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return
        
        # Initialize task manager
        task_manager = TaskManager(config)
        
        # Example 1: Create a simple analysis task
        print("\n📊 Example 1: Creating a codebase analysis task...")
        
        task = task_manager.create_task(
            repo_url="https://github.com/Zeeeepa/codegen.py",
            task_type="CODEBASE_ANALYSIS",
            query="Analyze the overall code structure and suggest improvements"
        )
        
        print(f"✅ Task created: {task.id}")
        print(f"📊 Status: {task.status.value}")
        print(f"🔗 Agent Run ID: {task.agent_run_id}")
        
        # Example 2: Check task status
        print(f"\n🔍 Example 2: Checking task status...")
        
        updated_task = task_manager.get_task_status(task.id)
        print(f"📊 Current status: {updated_task.status.value}")
        print(f"📅 Created: {updated_task.created_at}")
        print(f"📅 Updated: {updated_task.updated_at}")
        
        # Example 3: List recent tasks
        print(f"\n📋 Example 3: Listing recent tasks...")
        
        recent_tasks = task_manager.list_tasks(limit=5)
        print(f"Found {len(recent_tasks)} recent tasks:")
        
        for i, t in enumerate(recent_tasks, 1):
            print(f"  {i}. {t.id} - {t.status.value} - {t.task_type}")
            print(f"     Query: {t.query[:50]}{'...' if len(t.query) > 50 else ''}")
        
        # Example 4: Wait for completion (optional)
        print(f"\n⏳ Example 4: Waiting for task completion...")
        print("Note: This may take several minutes. Press Ctrl+C to skip.")
        
        try:
            # Wait up to 5 minutes for completion
            completed_task = task_manager.wait_for_completion(task.id, timeout=300)
            
            print(f"🎉 Task completed!")
            print(f"📊 Final status: {completed_task.status.value}")
            
            if completed_task.result:
                print(f"📄 Result preview: {completed_task.result[:200]}...")
            elif completed_task.error_message:
                print(f"❌ Error: {completed_task.error_message}")
                
        except KeyboardInterrupt:
            print("\n⏸️  Skipped waiting for completion")
            print(f"💡 Use 'codegenapi status {task.id}' to check progress later")
        
        # Clean up
        task_manager.close()
        
        print(f"\n✅ Examples completed successfully!")
        print(f"💡 Try the CLI: codegenapi status {task.id}")
        
    except CodegenAPIError as e:
        print(f"❌ CodegenAPI Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()

