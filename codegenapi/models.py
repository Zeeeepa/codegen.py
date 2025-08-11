"""
Data Structures

Simple data models for tasks, status, and configuration.
Clean separation between data models and API integration.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime


class TaskType(Enum):
    """Task types from templates"""
    PLAN_CREATION = "PLAN_CREATION"
    CODE_RESTRUCTURE = "CODE_RESTRUCTURE"
    FEATURE_IMPLEMENTATION = "FEATURE_IMPLEMENTATION"
    BUG_FIX = "BUG_FIX"
    CODEBASE_ANALYSIS = "CODEBASE_ANALYSIS"
    TEST_GENERATION = "TEST_GENERATION"


class TaskStatus(Enum):
    """Task status types"""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    PAUSED = "PAUSED"


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """Task data model"""
    id: int
    task_type: TaskType
    status: TaskStatus
    repository: str
    prompt: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None
    workspace: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    template_vars: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if task is currently active"""
        return self.status == TaskStatus.ACTIVE
    
    @property
    def is_complete(self) -> bool:
        """Check if task is complete"""
        return self.status == TaskStatus.COMPLETE
    
    @property
    def is_failed(self) -> bool:
        """Check if task failed"""
        return self.status == TaskStatus.FAILED
    
    @property
    def can_resume(self) -> bool:
        """Check if task can be resumed"""
        return self.status == TaskStatus.PAUSED


@dataclass
class TaskLog:
    """Task log entry"""
    timestamp: datetime
    message_type: str
    content: str
    tool_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRun:
    """Agent run data from Codegen API"""
    id: int
    organization_id: int
    status: Optional[str]
    prompt: Optional[str]
    result: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    web_url: Optional[str]
    cost: Optional[float] = 0.0
    tokens_used: Optional[int] = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_task(self, task_type: TaskType, repository: str, workspace: Optional[str] = None) -> Task:
        """Convert AgentRun to Task"""
        # Map API status to TaskStatus
        status_mapping = {
            "PENDING": TaskStatus.PENDING,
            "ACTIVE": TaskStatus.ACTIVE,
            "COMPLETE": TaskStatus.COMPLETE,
            "COMPLETED": TaskStatus.COMPLETE,
            "FAILED": TaskStatus.FAILED,
            "CANCELLED": TaskStatus.CANCELLED,
            "PAUSED": TaskStatus.PAUSED
        }
        
        task_status = status_mapping.get(self.status, TaskStatus.PENDING) if self.status else TaskStatus.PENDING
        
        return Task(
            id=self.id,
            task_type=task_type,
            status=task_status,
            repository=repository,
            prompt=self.prompt or "",
            created_at=self.created_at or datetime.now(),
            updated_at=self.updated_at,
            completed_at=self.completed_at,
            result=self.result,
            workspace=workspace,
            metadata=self.metadata
        )


@dataclass
class Template:
    """Task template"""
    name: str
    task_type: TaskType
    content: str
    description: str
    variables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def render(self, variables: Dict[str, Any]) -> str:
        """Render template with variables"""
        rendered = self.content
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            rendered = rendered.replace(placeholder, str(var_value))
        return rendered


@dataclass
class WorkspaceConfig:
    """Workspace configuration"""
    name: str
    repositories: List[str]
    description: Optional[str] = None
    default_task_type: Optional[TaskType] = None
    template_vars: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

