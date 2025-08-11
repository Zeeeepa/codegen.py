"""
Status command
"""

import sys
from ..task_manager import TaskManager
from ..config import Config
from ..exceptions import CodegenAPIError


def execute_status_command(task_id: str, watch: bool = False, interval: int = 5) -> int:
    """Execute status command"""
    try:
        config = Config()
        
        # Validate configuration
        errors = config.validate()
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return 1
        
        task_manager = TaskManager(config)
        
        if watch:
            import time
            print(f"Watching task {task_id} (press Ctrl+C to stop)...")
            try:
                while True:
                    task = task_manager.get_task_status(task_id)
                    if not task:
                        print(f"Task {task_id} not found")
                        return 1
                    
                    print(f"\rStatus: {task.status.value}", end="", flush=True)
                    
                    if task.status.value in ["completed", "failed", "cancelled"]:
                        print()  # New line
                        break
                    
                    time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopped watching")
        else:
            task = task_manager.get_task_status(task_id)
            if not task:
                print(f"Task {task_id} not found")
                return 1
        
        # Display task details
        print(f"Task ID: {task.id}")
        print(f"Status: {task.status.value}")
        print(f"Repository: {task.repo_url}")
        print(f"Task Type: {task.task_type}")
        print(f"Query: {task.query}")
        print(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if task.pr_number:
            print(f"PR: {task.pr_number}")
        if task.branch:
            print(f"Branch: {task.branch}")
        if task.agent_run_id:
            print(f"Agent Run ID: {task.agent_run_id}")
        
        if task.result:
            print("\nResult:")
            print(task.result)
        elif task.error_message:
            print(f"\nError: {task.error_message}")
        
        task_manager.close()
        return 0
        
    except CodegenAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

