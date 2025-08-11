"""
Resume task command
"""

import sys
from typing import Optional
from ..task_manager import TaskManager
from ..config import Config
from ..exceptions import CodegenAPIError


def execute_resume_command(task_id: str, repo: Optional[str] = None, 
                          pr: Optional[str] = None, message: Optional[str] = None,
                          wait: bool = False, timeout: int = 300) -> int:
    """Execute resume task command"""
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
        
        # Load existing task
        task = task_manager.get_task_status(task_id)
        if not task:
            print(f"Task {task_id} not found")
            return 1
        
        print(f"Resuming task: {task_id}")
        print(f"Current status: {task.status.value}")
        
        # Create resume message
        resume_parts = []
        
        if message:
            resume_parts.append(f"Additional instructions: {message}")
        
        if repo and repo != task.repo_url:
            resume_parts.append(f"Updated repository: {repo}")
        
        if pr and pr != task.pr_number:
            resume_parts.append(f"Updated PR: {pr}")
        
        if not resume_parts:
            resume_parts.append("Please continue with the previous task.")
        
        resume_message = "\n".join(resume_parts)
        
        print(f"Resume message: {resume_message}")
        
        # Resume task
        resumed_task = task_manager.resume_task(task_id, resume_message)
        
        print(f"Task resumed: {resumed_task.id}")
        print(f"Status: {resumed_task.status.value}")
        
        # Wait for completion if requested
        if wait:
            print(f"Waiting for completion (timeout: {timeout}s)...")
            try:
                completed_task = task_manager.wait_for_completion(task_id, timeout)
                print(f"Task completed with status: {completed_task.status.value}")
                
                if completed_task.result:
                    print("\nResult:")
                    print(completed_task.result)
                elif completed_task.error_message:
                    print(f"\nError: {completed_task.error_message}")
                    
            except Exception as e:
                print(f"Error waiting for completion: {e}")
                print(f"Task ID: {task_id} (use 'codegenapi status {task_id}' to check)")
        else:
            print(f"\nUse 'codegenapi status {task_id}' to check progress")
        
        task_manager.close()
        return 0
        
    except CodegenAPIError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

