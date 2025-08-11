"""
New task command
"""

import sys
from typing import Optional
from ..task_manager import TaskManager
from ..config import Config
from ..exceptions import CodegenAPIError


def execute_new_command(repo: str, task: str, query: str, 
                       pr: Optional[str] = None, branch: Optional[str] = None,
                       wait: bool = False, timeout: int = 300) -> int:
    """Execute new task command"""
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
        
        print(f"Creating task: {task}")
        print(f"Repository: {repo}")
        print(f"Query: {query}")
        if pr:
            print(f"PR: {pr}")
        if branch:
            print(f"Branch: {branch}")
        
        # Create task
        created_task = task_manager.create_task(
            repo_url=repo,
            task_type=task,
            query=query,
            pr_number=pr,
            branch=branch
        )
        
        print(f"Task created: {created_task.id}")
        print(f"Status: {created_task.status.value}")
        
        if created_task.agent_run_id:
            print(f"Agent run ID: {created_task.agent_run_id}")
        
        # Wait for completion if requested
        if wait:
            print(f"Waiting for completion (timeout: {timeout}s)...")
            try:
                completed_task = task_manager.wait_for_completion(created_task.id, timeout)
                print(f"Task completed with status: {completed_task.status.value}")
                
                if completed_task.result:
                    print("\nResult:")
                    print(completed_task.result)
                elif completed_task.error_message:
                    print(f"\nError: {completed_task.error_message}")
                    
            except Exception as e:
                print(f"Error waiting for completion: {e}")
                print(f"Task ID: {created_task.id} (use 'codegenapi status {created_task.id}' to check)")
        else:
            print(f"\nUse 'codegenapi status {created_task.id}' to check progress")
        
        task_manager.close()
        return 0
        
    except CodegenAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

