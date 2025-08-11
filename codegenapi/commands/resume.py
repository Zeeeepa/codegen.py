"""
Resume Task Command

Handles resumption of paused tasks.
"""

import logging
from argparse import Namespace

from ..task_manager import TaskManager
from ..exceptions import TaskError, TaskNotFoundError, TaskStateError

logger = logging.getLogger(__name__)


def handle(args: Namespace, task_manager: TaskManager) -> int:
    """Handle resume task command"""
    
    try:
        # Resume the task
        task = task_manager.resume_task(
            task_id=args.task_id,
            message=args.message,
            images=args.images
        )
        
        # Display success message
        print(f"✅ Resumed task {task.id}")
        print(f"   Type: {task.task_type.value}")
        print(f"   Repository: {task.repository}")
        print(f"   Status: {task.status.value}")
        
        if task.workspace:
            print(f"   Workspace: {task.workspace}")
        
        print(f"   Priority: {task.priority.value}")
        
        # Show web URL if available
        print(f"\n🔗 Track progress: https://codegen.com/runs/{task.id}")
        
        return 0
        
    except TaskNotFoundError as e:
        print(f"Error: Task {args.task_id} not found")
        return 1
        
    except TaskStateError as e:
        print(f"Error: {e}")
        print(f"Task {args.task_id} cannot be resumed in its current state")
        return 1
        
    except TaskError as e:
        print(f"Task Error: {e}")
        return 1
        
    except Exception as e:
        logger.exception("Unexpected error in resume command")
        print(f"Unexpected error: {e}")
        return 1

