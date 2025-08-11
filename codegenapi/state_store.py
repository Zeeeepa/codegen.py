"""
Task state storage and management
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from .models import Task, TaskStatus
from .exceptions import TaskError


class StateStore:
    """Manages task state persistence"""
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_task_file(self, task_id: str) -> Path:
        """Get task file path"""
        return self.storage_dir / f"{task_id}.json"
    
    def create_task(self, repo_url: str, task_type: str, query: str, 
                   pr_number: Optional[str] = None, branch: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> Task:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = Task(
            id=task_id,
            repo_url=repo_url,
            task_type=task_type,
            query=query,
            status=TaskStatus.CREATED,
            created_at=now,
            updated_at=now,
            pr_number=pr_number,
            branch=branch,
            metadata=metadata or {}
        )
        
        self.save_task(task)
        return task
    
    def save_task(self, task: Task) -> None:
        """Save task to storage"""
        task.updated_at = datetime.now()
        task_file = self._get_task_file(task.id)
        
        try:
            with open(task_file, 'w') as f:
                json.dump(task.to_dict(), f, indent=2)
        except Exception as e:
            raise TaskError(f"Failed to save task {task.id}: {e}")
    
    def load_task(self, task_id: str) -> Optional[Task]:
        """Load task from storage"""
        task_file = self._get_task_file(task_id)
        
        if not task_file.exists():
            return None
        
        try:
            with open(task_file, 'r') as f:
                data = json.load(f)
            return Task.from_dict(data)
        except Exception as e:
            raise TaskError(f"Failed to load task {task_id}: {e}")
    
    def list_tasks(self, limit: int = 50) -> List[Task]:
        """List all tasks, most recent first"""
        tasks = []
        
        for task_file in self.storage_dir.glob("*.json"):
            try:
                with open(task_file, 'r') as f:
                    data = json.load(f)
                tasks.append(Task.from_dict(data))
            except Exception:
                continue  # Skip corrupted files
        
        # Sort by updated_at descending
        tasks.sort(key=lambda t: t.updated_at, reverse=True)
        return tasks[:limit]
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          agent_run_id: Optional[str] = None,
                          result: Optional[str] = None,
                          error_message: Optional[str] = None) -> Optional[Task]:
        """Update task status"""
        task = self.load_task(task_id)
        if not task:
            return None
        
        task.status = status
        if agent_run_id:
            task.agent_run_id = agent_run_id
        if result:
            task.result = result
        if error_message:
            task.error_message = error_message
        
        self.save_task(task)
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task from storage"""
        task_file = self._get_task_file(task_id)
        
        if task_file.exists():
            try:
                task_file.unlink()
                return True
            except Exception as e:
                raise TaskError(f"Failed to delete task {task_id}: {e}")
        
        return False

