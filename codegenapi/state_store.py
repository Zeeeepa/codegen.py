"""
Local Task Storage

Manages local persistence of task state and metadata.
Provides caching and offline access to task information.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .models import Task, TaskType, TaskStatus, Priority
from .exceptions import TaskError

logger = logging.getLogger(__name__)


class StateStore:
    """
    Local state storage for tasks.
    
    Provides persistence for task metadata, state, and offline access.
    """
    
    def __init__(self, state_file: Path):
        """Initialize state store"""
        self.state_file = Path(state_file)
        self._tasks: Dict[int, Dict[str, Any]] = {}
        
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing state
        self._load_state()
        
        logger.info(f"Initialized StateStore with file: {self.state_file}")
    
    def _load_state(self) -> None:
        """Load state from file"""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self._tasks = data.get("tasks", {})
                
                # Convert string keys to int
                self._tasks = {int(k): v for k, v in self._tasks.items()}
                
            logger.debug(f"Loaded {len(self._tasks)} tasks from state file")
            
        except Exception as e:
            logger.error(f"Failed to load state file: {e}")
            self._tasks = {}
    
    def _save_state(self) -> None:
        """Save state to file"""
        try:
            data = {
                "tasks": {str(k): v for k, v in self._tasks.items()},
                "last_updated": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            # Write to temporary file first
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Atomic move
            temp_file.replace(self.state_file)
            
            logger.debug(f"Saved {len(self._tasks)} tasks to state file")
            
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")
    
    def save_task(self, task: Task) -> None:
        """Save task to state store"""
        task_data = {
            "id": task.id,
            "task_type": task.task_type.value,
            "status": task.status.value,
            "repository": task.repository,
            "prompt": task.prompt,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error_message": task.error_message,
            "workspace": task.workspace,
            "priority": task.priority.value,
            "metadata": task.metadata,
            "template_vars": task.template_vars
        }
        
        self._tasks[task.id] = task_data
        self._save_state()
        
        logger.debug(f"Saved task {task.id} to state store")
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task from state store"""
        task_data = self._tasks.get(task_id)
        if not task_data:
            return None
        
        try:
            return Task(
                id=task_data["id"],
                task_type=TaskType(task_data["task_type"]),
                status=TaskStatus(task_data["status"]),
                repository=task_data["repository"],
                prompt=task_data["prompt"],
                created_at=datetime.fromisoformat(task_data["created_at"]),
                updated_at=datetime.fromisoformat(task_data["updated_at"]) if task_data.get("updated_at") else None,
                completed_at=datetime.fromisoformat(task_data["completed_at"]) if task_data.get("completed_at") else None,
                result=task_data.get("result"),
                error_message=task_data.get("error_message"),
                workspace=task_data.get("workspace"),
                priority=Priority(task_data.get("priority", Priority.MEDIUM.value)),
                metadata=task_data.get("metadata", {}),
                template_vars=task_data.get("template_vars", {})
            )
        except Exception as e:
            logger.error(f"Failed to parse task {task_id} from state store: {e}")
            return None
    
    def list_tasks(
        self,
        status_filter: Optional[TaskStatus] = None,
        workspace_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Task]:
        """List tasks from state store with optional filtering"""
        tasks = []
        
        for task_data in self._tasks.values():
            try:
                task = Task(
                    id=task_data["id"],
                    task_type=TaskType(task_data["task_type"]),
                    status=TaskStatus(task_data["status"]),
                    repository=task_data["repository"],
                    prompt=task_data["prompt"],
                    created_at=datetime.fromisoformat(task_data["created_at"]),
                    updated_at=datetime.fromisoformat(task_data["updated_at"]) if task_data.get("updated_at") else None,
                    completed_at=datetime.fromisoformat(task_data["completed_at"]) if task_data.get("completed_at") else None,
                    result=task_data.get("result"),
                    error_message=task_data.get("error_message"),
                    workspace=task_data.get("workspace"),
                    priority=Priority(task_data.get("priority", Priority.MEDIUM.value)),
                    metadata=task_data.get("metadata", {}),
                    template_vars=task_data.get("template_vars", {})
                )
                
                # Apply filters
                if status_filter and task.status != status_filter:
                    continue
                
                if workspace_filter and task.workspace != workspace_filter:
                    continue
                
                tasks.append(task)
                
            except Exception as e:
                logger.warning(f"Failed to parse task from state store: {e}")
                continue
        
        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Apply limit
        if limit:
            tasks = tasks[:limit]
        
        return tasks
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task from state store"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save_state()
            logger.debug(f"Deleted task {task_id} from state store")
            return True
        return False
    
    def clear_completed_tasks(self, older_than_days: int = 30) -> int:
        """Clear completed tasks older than specified days"""
        cutoff_date = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
        
        tasks_to_remove = []
        for task_id, task_data in self._tasks.items():
            try:
                if task_data["status"] in ["COMPLETE", "FAILED", "CANCELLED"]:
                    completed_at = task_data.get("completed_at")
                    if completed_at:
                        completed_timestamp = datetime.fromisoformat(completed_at).timestamp()
                        if completed_timestamp < cutoff_date:
                            tasks_to_remove.append(task_id)
            except Exception as e:
                logger.warning(f"Error checking task {task_id} for cleanup: {e}")
        
        # Remove old tasks
        for task_id in tasks_to_remove:
            del self._tasks[task_id]
        
        if tasks_to_remove:
            self._save_state()
            logger.info(f"Cleaned up {len(tasks_to_remove)} old completed tasks")
        
        return len(tasks_to_remove)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored tasks"""
        if not self._tasks:
            return {"total": 0}
        
        stats = {
            "total": len(self._tasks),
            "by_status": {},
            "by_type": {},
            "by_workspace": {}
        }
        
        for task_data in self._tasks.values():
            # Count by status
            status = task_data.get("status", "UNKNOWN")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by type
            task_type = task_data.get("task_type", "UNKNOWN")
            stats["by_type"][task_type] = stats["by_type"].get(task_type, 0) + 1
            
            # Count by workspace
            workspace = task_data.get("workspace", "default")
            stats["by_workspace"][workspace] = stats["by_workspace"].get(workspace, 0) + 1
        
        return stats

