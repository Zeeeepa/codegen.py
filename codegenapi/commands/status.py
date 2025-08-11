"""
Status Command

Handles task status checking and monitoring.
"""

import json
import time
import logging
from argparse import Namespace
from datetime import datetime
from typing import List

from ..models import Task, TaskStatus
from ..task_manager import TaskManager
from ..exceptions import TaskError, TaskNotFoundError

logger = logging.getLogger(__name__)


def handle(args: Namespace, task_manager: TaskManager) -> int:
    """Handle status command"""
    
    try:
        if args.task_id:
            # Show specific task status
            return _show_task_status(args, task_manager)
        else:
            # Show list of tasks
            return _show_tasks_list(args, task_manager)
            
    except TaskNotFoundError as e:
        print(f"Error: Task {args.task_id} not found")
        return 1
        
    except TaskError as e:
        print(f"Task Error: {e}")
        return 1
        
    except Exception as e:
        logger.exception("Unexpected error in status command")
        print(f"Unexpected error: {e}")
        return 1


def _show_task_status(args: Namespace, task_manager: TaskManager) -> int:
    """Show status for a specific task"""
    
    task = task_manager.get_task(args.task_id)
    
    if args.watch:
        return _watch_task_status(task, task_manager, args.logs)
    else:
        _display_task_details(task, show_logs=args.logs, task_manager=task_manager)
        return 0


def _show_tasks_list(args: Namespace, task_manager: TaskManager) -> int:
    """Show list of tasks"""
    
    # Parse status filter
    status_filter = None
    if args.filter_status:
        try:
            status_filter = TaskStatus(args.filter_status)
        except ValueError:
            print(f"Error: Invalid status filter '{args.filter_status}'")
            return 1
    
    # Get tasks
    tasks = task_manager.list_tasks(
        limit=args.limit,
        status_filter=status_filter,
        workspace_filter=args.workspace
    )
    
    if not tasks:
        print("No tasks found")
        return 0
    
    # Display tasks
    if args.format == "json":
        _display_tasks_json(tasks)
    elif args.format == "yaml":
        _display_tasks_yaml(tasks)
    else:
        _display_tasks_table(tasks)
    
    return 0


def _display_task_details(task: Task, show_logs: bool = False, task_manager: TaskManager = None):
    """Display detailed task information"""
    
    print(f"Task {task.id}")
    print(f"  Type: {task.task_type.value}")
    print(f"  Status: {_format_status(task.status)}")
    print(f"  Repository: {task.repository}")
    print(f"  Priority: {task.priority.value}")
    
    if task.workspace:
        print(f"  Workspace: {task.workspace}")
    
    print(f"  Created: {_format_datetime(task.created_at)}")
    
    if task.updated_at:
        print(f"  Updated: {_format_datetime(task.updated_at)}")
    
    if task.completed_at:
        print(f"  Completed: {_format_datetime(task.completed_at)}")
    
    if task.error_message:
        print(f"  Error: {task.error_message}")
    
    # Show prompt preview
    if task.prompt:
        print(f"\n  Prompt Preview:")
        preview = task.prompt[:200] + "..." if len(task.prompt) > 200 else task.prompt
        for line in preview.split('\n'):
            print(f"    {line}")
    
    # Show result preview
    if task.result:
        print(f"\n  Result Preview:")
        preview = task.result[:200] + "..." if len(task.result) > 200 else task.result
        for line in preview.split('\n'):
            print(f"    {line}")
    
    # Show logs if requested
    if show_logs and task_manager:
        try:
            logs = task_manager.get_task_logs(task.id, limit=10)
            if logs:
                print(f"\n  Recent Logs:")
                for log in logs[-5:]:  # Show last 5 logs
                    timestamp = log.get('created_at', 'Unknown')
                    message_type = log.get('message_type', 'info')
                    content = log.get('thought') or log.get('observation', 'No content')
                    
                    # Truncate long content
                    if len(content) > 100:
                        content = content[:100] + "..."
                    
                    print(f"    [{timestamp}] {message_type}: {content}")
        except Exception as e:
            print(f"    Failed to load logs: {e}")
    
    print(f"\n🔗 View in browser: https://codegen.com/runs/{task.id}")


def _display_tasks_table(tasks: List[Task]):
    """Display tasks in table format"""
    
    # Table headers
    print(f"{'ID':<8} {'Type':<20} {'Status':<12} {'Repository':<30} {'Created':<12}")
    print("-" * 82)
    
    for task in tasks:
        repo_short = task.repository[:27] + "..." if len(task.repository) > 30 else task.repository
        created_short = task.created_at.strftime("%m/%d %H:%M")
        
        print(f"{task.id:<8} {task.task_type.value:<20} {_format_status(task.status):<12} {repo_short:<30} {created_short:<12}")


def _display_tasks_json(tasks: List[Task]):
    """Display tasks in JSON format"""
    
    tasks_data = []
    for task in tasks:
        tasks_data.append({
            "id": task.id,
            "task_type": task.task_type.value,
            "status": task.status.value,
            "repository": task.repository,
            "workspace": task.workspace,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        })
    
    print(json.dumps(tasks_data, indent=2))


def _display_tasks_yaml(tasks: List[Task]):
    """Display tasks in YAML format"""
    
    print("tasks:")
    for task in tasks:
        print(f"  - id: {task.id}")
        print(f"    task_type: {task.task_type.value}")
        print(f"    status: {task.status.value}")
        print(f"    repository: {task.repository}")
        print(f"    workspace: {task.workspace or 'null'}")
        print(f"    priority: {task.priority.value}")
        print(f"    created_at: {task.created_at.isoformat()}")
        if task.updated_at:
            print(f"    updated_at: {task.updated_at.isoformat()}")
        if task.completed_at:
            print(f"    completed_at: {task.completed_at.isoformat()}")


def _watch_task_status(task: Task, task_manager: TaskManager, show_logs: bool = False) -> int:
    """Watch task status with live updates"""
    
    print(f"👀 Watching task {task.id} (Press Ctrl+C to stop)")
    print()
    
    try:
        while True:
            # Clear screen (simple version)
            print("\033[2J\033[H", end="")
            
            # Get updated task
            updated_task = task_manager.get_task(task.id)
            
            # Display current status
            _display_task_details(updated_task, show_logs=show_logs, task_manager=task_manager)
            
            # Check if task is complete
            if updated_task.status in [TaskStatus.COMPLETE, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                print(f"\n✅ Task {updated_task.id} finished with status: {updated_task.status.value}")
                break
            
            # Wait before next update
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped watching task {task.id}")
        return 0
    
    return 0


def _format_status(status: TaskStatus) -> str:
    """Format status with emoji"""
    
    status_emojis = {
        TaskStatus.PENDING: "⏳ PENDING",
        TaskStatus.ACTIVE: "🔄 ACTIVE",
        TaskStatus.COMPLETE: "✅ COMPLETE",
        TaskStatus.FAILED: "❌ FAILED",
        TaskStatus.CANCELLED: "⏹️ CANCELLED",
        TaskStatus.PAUSED: "⏸️ PAUSED"
    }
    
    return status_emojis.get(status, status.value)


def _format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "just now"

