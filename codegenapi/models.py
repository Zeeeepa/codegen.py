"""
Data models for CodegenAPI
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Task data model"""
    id: str
    repo_url: str
    task_type: str
    query: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    pr_number: Optional[str] = None
    branch: Optional[str] = None
    agent_run_id: Optional[str] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "repo_url": self.repo_url,
            "task_type": self.task_type,
            "query": self.query,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "pr_number": self.pr_number,
            "branch": self.branch,
            "agent_run_id": self.agent_run_id,
            "result": self.result,
            "error_message": self.error_message,
            "metadata": self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary"""
        return cls(
            id=data["id"],
            repo_url=data["repo_url"],
            task_type=data["task_type"],
            query=data["query"],
            status=TaskStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            pr_number=data.get("pr_number"),
            branch=data.get("branch"),
            agent_run_id=data.get("agent_run_id"),
            result=data.get("result"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {})
        )


@dataclass
class TaskTemplate:
    """Task template model"""
    name: str
    template_path: str
    description: str
    variables: list[str]
