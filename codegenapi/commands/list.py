"""
List tasks command
"""

import sys
from ..task_manager import TaskManager
from ..config import Config
from ..exceptions import CodegenAPIError


def execute_list_command(limit: int = 10, status: str = None) -> int:
    """Execute list tasks command"""
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
        
        # Get tasks
        tasks = task_manager.list_tasks(limit)
        
        if not tasks:
            print("No tasks found")
            return 0
        
        # Filter by status if specified
        if status:
            tasks = [t for t in tasks if t.status.value == status.lower()]
            if not tasks:
                print(f"No tasks found with status: {status}")
                return 0
        
        print(f"Recent tasks (showing {len(tasks)}):")
        print()
        
        # Display tasks
        for task in tasks:
            print(f"ID: {task.id}")
            print(f"  Status: {task.status.value}")
            print(f"  Type: {task.task_type}")
            print(f"  Repository: {task.repo_url}")
            print(f"  Query: {task.query[:100]}{'...' if len(task.query) > 100 else ''}")
            print(f"  Created: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if task.pr_number:
                print(f"  PR: {task.pr_number}")
            if task.branch:
                print(f"  Branch: {task.branch}")
            
            print()
        
        task_manager.close()
        return 0
        
    except CodegenAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

