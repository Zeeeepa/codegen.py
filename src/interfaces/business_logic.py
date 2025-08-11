"""
Business Logic Layer Interfaces

Defines the contracts for the middle layer that implements workspace management,
templates, workflows, and AI-powered features. This layer is UI-agnostic and
uses the integration layer for API operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Iterator
from dataclasses import dataclass
from enum import Enum
import datetime
from pathlib import Path

from .codegen_integration import AgentRun, Organization


class WorkspaceStatus(Enum):
    """Workspace status types"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SYNCING = "SYNCING"
    ERROR = "ERROR"


class TemplateType(Enum):
    """Template types from PR 9"""
    PLAN_CREATION = "PLAN_CREATION"
    FEATURE_IMPLEMENTATION = "FEATURE_IMPLEMENTATION"
    BUG_FIX = "BUG_FIX"
    API_CREATION = "API_CREATION"
    CODE_REVIEW = "CODE_REVIEW"
    DOCUMENTATION = "DOCUMENTATION"
    TESTING = "TESTING"
    REFACTORING = "REFACTORING"
    CUSTOM = "CUSTOM"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Priority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Workspace:
    """Workspace data model"""
    name: str
    description: Optional[str]
    repositories: List[str]
    status: WorkspaceStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    config: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class Template:
    """Template data model"""
    name: str
    type: TemplateType
    description: str
    content: str
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    author: Optional[str]
    version: str
    tags: List[str]


@dataclass
class WorkflowStep:
    """Individual workflow step"""
    id: str
    name: str
    type: str
    config: Dict[str, Any]
    dependencies: List[str]
    timeout: Optional[int]
    retry_count: int
    max_retries: int


@dataclass
class Workflow:
    """Workflow data model"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    metadata: Dict[str, Any]
    variables: Dict[str, Any]


@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str]
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    results: Dict[str, Any]
    error_message: Optional[str]


@dataclass
class AnalyticsReport:
    """Analytics report data model"""
    title: str
    description: str
    generated_at: datetime.datetime
    time_range: Dict[str, datetime.datetime]
    metrics: Dict[str, Any]
    charts: List[Dict[str, Any]]
    insights: List[str]


class IWorkspaceManager(ABC):
    """
    Interface for workspace management.
    
    Handles multi-repository project workspaces as proposed in PR 9.
    """
    
    @abstractmethod
    def create_workspace(
        self,
        name: str,
        repositories: List[str],
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Workspace:
        """Create a new workspace"""
        pass
    
    @abstractmethod
    def get_workspace(self, name: str) -> Optional[Workspace]:
        """Get workspace by name"""
        pass
    
    @abstractmethod
    def list_workspaces(self) -> List[Workspace]:
        """List all workspaces"""
        pass
    
    @abstractmethod
    def switch_workspace(self, name: str) -> bool:
        """Switch to a different workspace"""
        pass
    
    @abstractmethod
    def get_current_workspace(self) -> Optional[Workspace]:
        """Get currently active workspace"""
        pass
    
    @abstractmethod
    def sync_workspace(self, name: str, force: bool = False) -> bool:
        """Sync workspace repositories"""
        pass
    
    @abstractmethod
    def delete_workspace(self, name: str, force: bool = False) -> bool:
        """Delete a workspace"""
        pass
    
    @abstractmethod
    def add_repository(self, workspace_name: str, repo_url: str) -> bool:
        """Add repository to workspace"""
        pass
    
    @abstractmethod
    def remove_repository(self, workspace_name: str, repo_url: str) -> bool:
        """Remove repository from workspace"""
        pass


class ITemplateEngine(ABC):
    """
    Interface for template management.
    
    Handles reusable task templates as proposed in PR 9.
    """
    
    @abstractmethod
    def create_template(
        self,
        name: str,
        template_type: TemplateType,
        content: str,
        description: str,
        variables: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Template:
        """Create a new template"""
        pass
    
    @abstractmethod
    def get_template(self, name: str) -> Optional[Template]:
        """Get template by name"""
        pass
    
    @abstractmethod
    def list_templates(
        self,
        template_type: Optional[TemplateType] = None,
        tags: Optional[List[str]] = None
    ) -> List[Template]:
        """List templates with optional filtering"""
        pass
    
    @abstractmethod
    def apply_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
        target_repo: str
    ) -> str:
        """Apply template with variables to generate prompt"""
        pass
    
    @abstractmethod
    def validate_template(self, template: Template) -> List[str]:
        """Validate template and return any errors"""
        pass
    
    @abstractmethod
    def delete_template(self, name: str) -> bool:
        """Delete a template"""
        pass
    
    @abstractmethod
    def export_template(self, name: str, output_path: Path) -> bool:
        """Export template to file"""
        pass
    
    @abstractmethod
    def import_template(self, file_path: Path, name: Optional[str] = None) -> Template:
        """Import template from file"""
        pass


class IWorkflowOrchestrator(ABC):
    """
    Interface for workflow orchestration.
    
    Handles multi-step task workflows as proposed in PR 9.
    """
    
    @abstractmethod
    def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> Workflow:
        """Create a new workflow"""
        pass
    
    @abstractmethod
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        pass
    
    @abstractmethod
    def list_workflows(self, category: Optional[str] = None) -> List[Workflow]:
        """List workflows with optional category filter"""
        pass
    
    @abstractmethod
    def execute_workflow(
        self,
        workflow_id: str,
        variables: Dict[str, Any],
        repo_url: str
    ) -> WorkflowExecution:
        """Execute a workflow"""
        pass
    
    @abstractmethod
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status"""
        pass
    
    @abstractmethod
    def pause_execution(self, execution_id: str) -> bool:
        """Pause workflow execution"""
        pass
    
    @abstractmethod
    def resume_execution(self, execution_id: str) -> bool:
        """Resume paused workflow execution"""
        pass
    
    @abstractmethod
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel workflow execution"""
        pass
    
    @abstractmethod
    def get_execution_logs(self, execution_id: str) -> List[Dict[str, Any]]:
        """Get execution logs"""
        pass


class IAnalyticsEngine(ABC):
    """
    Interface for analytics and reporting.
    
    Provides insights and metrics as proposed in PR 9.
    """
    
    @abstractmethod
    def generate_report(
        self,
        report_type: str,
        time_range: Dict[str, datetime.datetime],
        filters: Optional[Dict[str, Any]] = None
    ) -> AnalyticsReport:
        """Generate analytics report"""
        pass
    
    @abstractmethod
    def get_task_metrics(
        self,
        workspace: Optional[str] = None,
        time_range: Optional[Dict[str, datetime.datetime]] = None
    ) -> Dict[str, Any]:
        """Get task performance metrics"""
        pass
    
    @abstractmethod
    def get_cost_analysis(
        self,
        time_range: Dict[str, datetime.datetime]
    ) -> Dict[str, Any]:
        """Get cost analysis and breakdown"""
        pass
    
    @abstractmethod
    def get_productivity_insights(
        self,
        workspace: Optional[str] = None
    ) -> List[str]:
        """Get productivity insights and recommendations"""
        pass
    
    @abstractmethod
    def export_metrics(
        self,
        format_type: str,
        output_path: Path,
        filters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Export metrics to file"""
        pass


class IAIFeatures(ABC):
    """
    Interface for AI-powered features.
    
    Implements smart context extraction, predictive scheduling, and other
    AI capabilities proposed in PR 9.
    """
    
    @abstractmethod
    def extract_context(
        self,
        repo_url: str,
        task_description: str
    ) -> Dict[str, Any]:
        """Smart context extraction from repository"""
        pass
    
    @abstractmethod
    def predict_task_duration(
        self,
        task_type: TemplateType,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict task duration and complexity"""
        pass
    
    @abstractmethod
    def suggest_dependencies(
        self,
        task_description: str,
        workspace: str
    ) -> List[str]:
        """Suggest task dependencies"""
        pass
    
    @abstractmethod
    def analyze_code_quality(
        self,
        repo_url: str,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze code quality and suggest improvements"""
        pass
    
    @abstractmethod
    def detect_security_issues(
        self,
        repo_url: str,
        files: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Detect potential security vulnerabilities"""
        pass
    
    @abstractmethod
    def optimize_workflow(
        self,
        workflow: Workflow,
        historical_data: List[Dict[str, Any]]
    ) -> Workflow:
        """Optimize workflow based on historical performance"""
        pass
    
    @abstractmethod
    def generate_insights(
        self,
        data: Dict[str, Any]
    ) -> List[str]:
        """Generate AI-powered insights from data"""
        pass

