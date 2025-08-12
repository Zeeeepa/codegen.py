"""
Task Manager

This module provides a task manager for handling asynchronous agent runs.
"""

import os
import sys
import time
import json
import threading
import uuid
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from datetime import datetime
import logging

# Add parent directory to path to import codegen_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from codegen_api import Agent, Task, AgentRunStatus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Task storage directory
TASKS_DIR = Path.home() / ".codegen" / "tasks"

class TaskInfo:
    """Information about a task."""
    
    def __init__(
        self, 
        task_id: str, 
        agent_run_id: Optional[int] = None,
        status: str = "pending",
        result: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        web_url: Optional[str] = None
    ):
        self.task_id = task_id
        self.agent_run_id = agent_run_id
        self.status = status
        self.result = result
        self.error = error
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = completed_at
        self.web_url = web_url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_run_id": self.agent_run_id,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "web_url": self.web_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskInfo':
        """Create from dictionary."""
        return cls(
            task_id=data["task_id"],
            agent_run_id=data.get("agent_run_id"),
            status=data.get("status", "pending"),
            result=data.get("result"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            web_url=data.get("web_url")
        )


class TaskManager:
    """Manager for asynchronous tasks."""
    
    def __init__(self):
        """Initialize the task manager."""
        self.tasks: Dict[str, TaskInfo] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.callbacks: Dict[str, List[Callable[[TaskInfo], None]]] = {}
        self.lock = threading.Lock()
        
        # Ensure tasks directory exists
        TASKS_DIR.parent.mkdir(exist_ok=True)
        TASKS_DIR.mkdir(exist_ok=True)
        
        # Load existing tasks
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load existing tasks from disk."""
        try:
            for task_file in TASKS_DIR.glob("*.json"):
                try:
                    with open(task_file, "r") as f:
                        task_data = json.load(f)
                        task_info = TaskInfo.from_dict(task_data)
                        self.tasks[task_info.task_id] = task_info
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error loading task from {task_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
    
    def _save_task(self, task_info: TaskInfo) -> None:
        """Save task information to disk."""
        try:
            task_file = TASKS_DIR / f"{task_info.task_id}.json"
            with open(task_file, "w") as f:
                json.dump(task_info.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving task {task_info.task_id}: {e}")
    
    def create_task(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(task_id=task_id, metadata=metadata)
        
        with self.lock:
            self.tasks[task_id] = task_info
            self.callbacks[task_id] = []
            self._save_task(task_info)
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Get task information by ID."""
        with self.lock:
            return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> Optional[TaskInfo]:
        """Update task information."""
        with self.lock:
            task_info = self.tasks.get(task_id)
            if not task_info:
                return None
            
            for key, value in kwargs.items():
                if hasattr(task_info, key):
                    setattr(task_info, key, value)
            
            self._save_task(task_info)
            
            # Notify callbacks
            for callback in self.callbacks.get(task_id, []):
                try:
                    callback(task_info)
                except Exception as e:
                    logger.error(f"Error in callback for task {task_id}: {e}")
            
            return task_info
    
    def list_tasks(self, 
                  status: Optional[str] = None, 
                  limit: int = 10, 
                  offset: int = 0) -> List[TaskInfo]:
        """List tasks with optional filtering."""
        with self.lock:
            tasks = list(self.tasks.values())
            
            # Filter by status if provided
            if status:
                tasks = [t for t in tasks if t.status == status]
            
            # Sort by creation time (newest first)
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            
            # Apply pagination
            return tasks[offset:offset + limit]
    
    def register_callback(self, task_id: str, callback: Callable[[TaskInfo], None]) -> bool:
        """Register a callback for task updates."""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            if task_id not in self.callbacks:
                self.callbacks[task_id] = []
            
            self.callbacks[task_id].append(callback)
            return True
    
    def run_agent_task(self, 
                      task_id: str, 
                      api_token: str,
                      org_id: str,
                      prompt: str,
                      repo: Optional[str] = None,
                      branch: Optional[str] = None,
                      pr: Optional[int] = None,
                      task_type: Optional[str] = None,
                      timeout: int = 3600) -> None:
        """Run an agent task asynchronously."""
        def _run_task():
            try:
                # Update task status to running
                self.update_task(task_id, status="running")
                
                # Create metadata
                metadata = {
                    "repo": repo,
                    "branch": branch,
                    "pr": pr,
                    "task_type": task_type
                }
                
                # Filter out None values
                metadata = {k: v for k, v in metadata.items() if v is not None}
                
                # Initialize agent
                agent = Agent(org_id=org_id, token=api_token)
                
                # Run agent
                agent_task = agent.run(prompt=prompt, metadata=metadata)
                
                # Update task with agent run ID
                self.update_task(
                    task_id, 
                    agent_run_id=agent_task.id,
                    web_url=agent_task.web_url,
                    status="running"
                )
                
                # Wait for completion
                try:
                    completed_task = agent_task.wait_for_completion(timeout=timeout)
                    
                    # Update task with result
                    self.update_task(
                        task_id,
                        status="completed",
                        result=completed_task.result,
                        completed_at=datetime.now().isoformat()
                    )
                except Exception as e:
                    # Check if task is still running
                    agent_task.refresh()
                    if agent_task.status == AgentRunStatus.RUNNING.value:
                        # Task is still running, update status
                        self.update_task(
                            task_id,
                            status="running"
                        )
                    else:
                        # Task failed
                        self.update_task(
                            task_id,
                            status="failed",
                            error=str(e),
                            completed_at=datetime.now().isoformat()
                        )
            except Exception as e:
                # Update task with error
                self.update_task(
                    task_id,
                    status="failed",
                    error=str(e),
                    completed_at=datetime.now().isoformat()
                )
        
        # Start task in a new thread
        thread = threading.Thread(target=_run_task)
        thread.daemon = True
        
        with self.lock:
            self.threads[task_id] = thread
        
        thread.start()
    
    def resume_agent_task(self,
                         task_id: str,
                         api_token: str,
                         org_id: str,
                         agent_run_id: int,
                         prompt: str,
                         task_type: Optional[str] = None,
                         timeout: int = 3600) -> None:
        """Resume an agent task asynchronously."""
        def _resume_task():
            try:
                # Update task status to running
                self.update_task(task_id, status="running")
                
                # Initialize agent
                agent = Agent(org_id=org_id, token=api_token)
                
                # Get existing task
                agent_task = agent.get_task(agent_run_id)
                
                # Resume task
                resumed_task = agent_task.resume(prompt=prompt)
                
                # Update task with agent run ID
                self.update_task(
                    task_id, 
                    agent_run_id=agent_run_id,
                    web_url=resumed_task.web_url,
                    status="running"
                )
                
                # Wait for completion
                try:
                    completed_task = agent_task.wait_for_completion(timeout=timeout)
                    
                    # Update task with result
                    self.update_task(
                        task_id,
                        status="completed",
                        result=completed_task.result,
                        completed_at=datetime.now().isoformat()
                    )
                except Exception as e:
                    # Check if task is still running
                    agent_task.refresh()
                    if agent_task.status == AgentRunStatus.RUNNING.value:
                        # Task is still running, update status
                        self.update_task(
                            task_id,
                            status="running"
                        )
                    else:
                        # Task failed
                        self.update_task(
                            task_id,
                            status="failed",
                            error=str(e),
                            completed_at=datetime.now().isoformat()
                        )
            except Exception as e:
                # Update task with error
                self.update_task(
                    task_id,
                    status="failed",
                    error=str(e),
                    completed_at=datetime.now().isoformat()
                )
        
        # Start task in a new thread
        thread = threading.Thread(target=_resume_task)
        thread.daemon = True
        
        with self.lock:
            self.threads[task_id] = thread
        
        thread.start()


# Singleton instance
_task_manager = None

def get_task_manager() -> TaskManager:
    """Get the singleton task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager

