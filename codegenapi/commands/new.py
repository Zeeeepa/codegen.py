"""
New Task Command

Handles creation of new tasks from templates.
"""

import json
import logging
from argparse import Namespace
from typing import Dict, Any

from ..models import TaskType, Priority
from ..task_manager import TaskManager
from ..exceptions import TaskError, TemplateError

logger = logging.getLogger(__name__)


def handle(args: Namespace, task_manager: TaskManager) -> int:
    """Handle new task command"""
    
    try:
        # Parse task type
        task_type = TaskType(args.task_type)
        
        # Parse priority
        priority = Priority(args.priority)
        
        # Parse template variables if provided
        template_vars = {}
        if args.template_vars:
            try:
                template_vars = json.loads(args.template_vars)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in template variables: {e}")
                return 1
        
        # Create task
        task = task_manager.create_task(
            task_type=task_type,
            repository=args.repo,
            message=args.message,
            template_vars=template_vars,
            workspace=args.workspace,
            priority=priority,
            dry_run=args.dry_run
        )
        
        if args.dry_run:
            print("DRY RUN - Task would be created with the following details:")
            print(f"Task Type: {task.task_type.value}")
            print(f"Repository: {task.repository}")
            print(f"Workspace: {task.workspace or 'default'}")
            print(f"Priority: {task.priority.value}")
            print(f"Prompt Preview:")
            print("-" * 50)
            print(task.prompt[:500] + "..." if len(task.prompt) > 500 else task.prompt)
            print("-" * 50)
            return 0
        
        # Display success message
        print(f"✅ Created task {task.id}")
        print(f"   Type: {task.task_type.value}")
        print(f"   Repository: {task.repository}")
        print(f"   Status: {task.status.value}")
        
        if task.workspace:
            print(f"   Workspace: {task.workspace}")
        
        print(f"   Priority: {task.priority.value}")
        
        # Show web URL if available
        # Note: We'd need to get this from the API response
        print(f"\n🔗 Track progress: https://codegen.com/runs/{task.id}")
        
        return 0
        
    except ValueError as e:
        print(f"Error: Invalid task type '{args.task_type}'. Available types:")
        for task_type in TaskType:
            print(f"  - {task_type.value}")
        return 1
        
    except TemplateError as e:
        print(f"Template Error: {e}")
        return 1
        
    except TaskError as e:
        print(f"Task Error: {e}")
        return 1
        
    except Exception as e:
        logger.exception("Unexpected error in new command")
        print(f"Unexpected error: {e}")
        return 1

