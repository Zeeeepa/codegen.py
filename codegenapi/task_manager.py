"""
Task Lifecycle Management

Manages the complete lifecycle of tasks including creation, tracking,
resumption, and state persistence. Clean separation between task logic
and API integration.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import Task, TaskType, TaskStatus, Priority, AgentRun
from .codegen_client import CodegenClient
from .template_loader import TemplateLoader
from .state_store import StateStore
from .config import Config
from .exceptions import TaskError, TaskNotFoundError, TaskStateError

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Task lifecycle manager.
    
    Handles task creation from templates, status tracking, resumption,
    and state persistence. Provides clean interface between CLI and API.
    """
    
    def __init__(self, client: CodegenClient, config: Config):
        """Initialize task manager"""
        self.client = client
        self.config = config
        self.template_loader = TemplateLoader(config.tasks_dir)
        self.state_store = StateStore(config.state_file)
        
        logger.info("Initialized TaskManager")
    
    def create_task(
        self,
        task_type: TaskType,
        repository: str,
        message: Optional[str] = None,
        template_vars: Optional[Dict[str, Any]] = None,
        workspace: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        dry_run: bool = False
    ) -> Task:
        """Create a new task from template"""
        
        # Load and render template
        template = self.template_loader.load_template(task_type)
        
        # Prepare template variables
        vars_dict = template_vars or {}
        vars_dict.update({
            "repository": repository,
            "workspace": workspace or "default",
            "priority": priority.value,
            "timestamp": datetime.now().isoformat()
        })
        
        # Add custom message if provided
        if message:
            vars_dict["custom_message"] = message
        
        # Render template
        rendered_prompt = template.render(vars_dict)
        
        # Add custom message to prompt if provided
        if message:
            rendered_prompt = f"{rendered_prompt}\n\nAdditional instructions: {message}"
        
        if dry_run:
            # Return a mock task for dry run
            return Task(
                id=0,
                task_type=task_type,
                status=TaskStatus.PENDING,
                repository=repository,
                prompt=rendered_prompt,
                created_at=datetime.now(),
                workspace=workspace,
                priority=priority,
                template_vars=vars_dict
            )
        
        try:
            # Create agent run via API
            agent_run = self.client.create_agent_run(
                prompt=rendered_prompt,
                metadata={
                    "task_type": task_type.value,
                    "repository": repository,
                    "workspace": workspace,
                    "priority": priority.value,
                    "template_vars": vars_dict
                }
            )
            
            # Convert to task
            task = agent_run.to_task(task_type, repository, workspace)
            task.priority = priority
            task.template_vars = vars_dict
            
            # Save to state store
            self.state_store.save_task(task)
            
            logger.info(f"Created task {task.id} of type {task_type.value}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise TaskError(f"Failed to create task: {e}")
    
    def get_task(self, task_id: int) -> Task:
        """Get task by ID"""
        
        # Try to get from state store first
        task = self.state_store.get_task(task_id)
        
        if task:
            # Refresh status from API
            try:
                agent_run = self.client.get_agent_run(task_id)
                updated_task = agent_run.to_task(task.task_type, task.repository, task.workspace)
                updated_task.priority = task.priority
                updated_task.template_vars = task.template_vars
                
                # Update state store
                self.state_store.save_task(updated_task)
                return updated_task
                
            except Exception as e:
                logger.warning(f"Failed to refresh task {task_id} from API: {e}")
                return task
        
        # If not in state store, try to get from API
        try:
            agent_run = self.client.get_agent_run(task_id)
            
            # We need to infer task type from metadata or prompt
            task_type = self._infer_task_type(agent_run)
            repository = self._infer_repository(agent_run)
            
            task = agent_run.to_task(task_type, repository)
            
            # Save to state store for future reference
            self.state_store.save_task(task)
            return task
            
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise TaskNotFoundError(f"Task {task_id} not found", task_id)
    
    def list_tasks(
        self,
        limit: int = 10,
        status_filter: Optional[TaskStatus] = None,
        workspace_filter: Optional[str] = None
    ) -> List[Task]:
        """List tasks with optional filtering"""
        
        try:
            # Get tasks from API
            api_status = status_filter.value if status_filter else None
            response = self.client.list_agent_runs(limit=limit, status_filter=api_status)
            
            tasks = []
            for agent_run in response.items:
                try:
                    # Try to get task from state store first
                    stored_task = self.state_store.get_task(agent_run.id)
                    
                    if stored_task:
                        # Update with latest API data
                        task = agent_run.to_task(stored_task.task_type, stored_task.repository, stored_task.workspace)
                        task.priority = stored_task.priority
                        task.template_vars = stored_task.template_vars
                    else:
                        # Infer task details
                        task_type = self._infer_task_type(agent_run)
                        repository = self._infer_repository(agent_run)
                        task = agent_run.to_task(task_type, repository)
                    
                    # Apply workspace filter
                    if workspace_filter and task.workspace != workspace_filter:
                        continue
                    
                    tasks.append(task)
                    
                except Exception as e:
                    logger.warning(f"Failed to process agent run {agent_run.id}: {e}")
                    continue
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            raise TaskError(f"Failed to list tasks: {e}")
    
    def resume_task(
        self,
        task_id: int,
        message: str,
        images: Optional[List[str]] = None
    ) -> Task:
        """Resume a paused task"""
        
        # Get current task
        task = self.get_task(task_id)
        
        if not task.can_resume:
            raise TaskStateError(f"Task {task_id} cannot be resumed (status: {task.status.value})", task_id)
        
        try:
            # Resume via API
            agent_run = self.client.resume_agent_run(task_id, message, images)
            
            # Update task
            updated_task = agent_run.to_task(task.task_type, task.repository, task.workspace)
            updated_task.priority = task.priority
            updated_task.template_vars = task.template_vars
            
            # Save to state store
            self.state_store.save_task(updated_task)
            
            logger.info(f"Resumed task {task_id}")
            return updated_task
            
        except Exception as e:
            logger.error(f"Failed to resume task {task_id}: {e}")
            raise TaskError(f"Failed to resume task {task_id}: {e}", task_id)
    
    def get_task_logs(self, task_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get logs for a task"""
        try:
            return self.client.get_agent_run_logs(task_id, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get logs for task {task_id}: {e}")
            raise TaskError(f"Failed to get logs for task {task_id}: {e}", task_id)
    
    def cancel_task(self, task_id: int) -> bool:
        """Cancel an active task"""
        try:
            success = self.client.cancel_agent_run(task_id)
            
            if success:
                # Update task status in state store
                task = self.state_store.get_task(task_id)
                if task:
                    task.status = TaskStatus.CANCELLED
                    self.state_store.save_task(task)
                
                logger.info(f"Cancelled task {task_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def _infer_task_type(self, agent_run: AgentRun) -> TaskType:
        """Infer task type from agent run data"""
        
        # Check metadata first
        if agent_run.metadata and "task_type" in agent_run.metadata:
            try:
                return TaskType(agent_run.metadata["task_type"])
            except ValueError:
                pass
        
        # Try to infer from prompt
        if agent_run.prompt:
            prompt_lower = agent_run.prompt.lower()
            
            if "feature" in prompt_lower or "implement" in prompt_lower:
                return TaskType.FEATURE_IMPLEMENTATION
            elif "bug" in prompt_lower or "fix" in prompt_lower:
                return TaskType.BUG_FIX
            elif "test" in prompt_lower:
                return TaskType.TEST_GENERATION
            elif "plan" in prompt_lower:
                return TaskType.PLAN_CREATION
            elif "analysis" in prompt_lower or "analyze" in prompt_lower:
                return TaskType.CODEBASE_ANALYSIS
            elif "restructure" in prompt_lower or "refactor" in prompt_lower:
                return TaskType.CODE_RESTRUCTURE
        
        # Default fallback
        return TaskType.FEATURE_IMPLEMENTATION
    
    def _infer_repository(self, agent_run: AgentRun) -> str:
        """Infer repository from agent run data"""
        
        # Check metadata first
        if agent_run.metadata and "repository" in agent_run.metadata:
            return agent_run.metadata["repository"]
        
        # Try to extract from prompt
        if agent_run.prompt:
            # Look for common repository patterns
            import re
            
            # GitHub URL pattern
            github_pattern = r'https://github\.com/([^/]+/[^/\s]+)'
            match = re.search(github_pattern, agent_run.prompt)
            if match:
                return match.group(0)
            
            # Repository name pattern
            repo_pattern = r'repository[:\s]+([^\s]+)'
            match = re.search(repo_pattern, agent_run.prompt, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Default fallback
        return "unknown"

