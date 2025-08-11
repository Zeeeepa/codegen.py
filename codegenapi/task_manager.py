"""
Task management and execution
"""

from typing import Optional, Dict, Any
from .models import Task, TaskStatus
from .state_store import StateStore
from .codegen_client import CodegenClient
from .template_loader import TemplateLoader
from .config import Config
from .exceptions import TaskError, APIError


class TaskManager:
    """Manages task lifecycle and execution"""
    
    def __init__(self, config: Config):
        self.config = config
        self.state_store = StateStore(config.tasks_dir)
        self.client = CodegenClient(config)
        self.template_loader = TemplateLoader()
    
    def create_task(self, repo_url: str, task_type: str, query: str,
                   pr_number: Optional[str] = None, branch: Optional[str] = None) -> Task:
        """Create and start a new task"""
        # Create task record
        task = self.state_store.create_task(
            repo_url=repo_url,
            task_type=task_type,
            query=query,
            pr_number=pr_number,
            branch=branch
        )
        
        try:
            # Process template to create prompt
            template_vars = {
                "repo_url": repo_url,
                "query": query,
                "pr_number": pr_number or "",
                "branch": branch or "",
                "task_type": task_type
            }
            
            # Try to use template, fallback to direct query
            try:
                prompt = self.template_loader.process_template(task_type, template_vars)
            except Exception:
                # Fallback to direct query if template processing fails
                prompt = self._create_fallback_prompt(repo_url, task_type, query, pr_number, branch)
            
            # Create agent run
            metadata = {
                "task_id": task.id,
                "task_type": task_type,
                "repo_url": repo_url,
                "pr_number": pr_number,
                "branch": branch
            }
            
            agent_run = self.client.create_agent_run(prompt, metadata)
            agent_run_id = str(agent_run.get("id"))
            
            # Update task with agent run ID
            task = self.state_store.update_task_status(
                task.id, 
                TaskStatus.RUNNING, 
                agent_run_id=agent_run_id
            )
            
            return task
            
        except Exception as e:
            # Mark task as failed
            self.state_store.update_task_status(
                task.id, 
                TaskStatus.FAILED, 
                error_message=str(e)
            )
            raise TaskError(f"Failed to create task: {e}")
    
    def _create_fallback_prompt(self, repo_url: str, task_type: str, query: str,
                               pr_number: Optional[str], branch: Optional[str]) -> str:
        """Create fallback prompt when template is not available"""
        prompt_parts = [f"Repository: {repo_url}"]
        
        if pr_number:
            prompt_parts.append(f"PR: {pr_number}")
        if branch:
            prompt_parts.append(f"Branch: {branch}")
        
        prompt_parts.extend([
            f"Task Type: {task_type}",
            f"Request: {query}",
            "",
            "Please complete this coding task following best practices."
        ])
        
        return "\n".join(prompt_parts)
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get current task status"""
        task = self.state_store.load_task(task_id)
        if not task:
            return None
        
        # If task is running, check agent run status
        if task.status == TaskStatus.RUNNING and task.agent_run_id:
            try:
                agent_run = self.client.get_agent_run(task.agent_run_id)
                agent_status = agent_run.get("status", "").lower()
                
                if agent_status == "completed":
                    task = self.state_store.update_task_status(
                        task_id,
                        TaskStatus.COMPLETED,
                        result=agent_run.get("result")
                    )
                elif agent_status in ["failed", "cancelled"]:
                    task = self.state_store.update_task_status(
                        task_id,
                        TaskStatus.FAILED,
                        error_message=f"Agent run {agent_status}"
                    )
            except APIError:
                # If we can't check status, return current task state
                pass
        
        return task
    
    def resume_task(self, task_id: str, additional_prompt: str) -> Task:
        """Resume a task with additional instructions"""
        task = self.state_store.load_task(task_id)
        if not task:
            raise TaskError(f"Task {task_id} not found")
        
        if not task.agent_run_id:
            raise TaskError(f"Task {task_id} has no associated agent run")
        
        try:
            # Resume agent run
            agent_run = self.client.resume_agent_run(task.agent_run_id, additional_prompt)
            
            # Update task status
            task = self.state_store.update_task_status(
                task_id,
                TaskStatus.RUNNING
            )
            
            return task
            
        except Exception as e:
            # Mark task as failed
            self.state_store.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error_message=str(e)
            )
            raise TaskError(f"Failed to resume task: {e}")
    
    def list_tasks(self, limit: int = 10) -> list[Task]:
        """List recent tasks"""
        return self.state_store.list_tasks(limit)
    
    def wait_for_completion(self, task_id: str, timeout: int = 300) -> Task:
        """Wait for task to complete"""
        task = self.state_store.load_task(task_id)
        if not task:
            raise TaskError(f"Task {task_id} not found")
        
        if not task.agent_run_id:
            raise TaskError(f"Task {task_id} has no associated agent run")
        
        try:
            # Wait for agent run completion
            agent_run = self.client.wait_for_completion(task.agent_run_id, timeout)
            agent_status = agent_run.get("status", "").lower()
            
            if agent_status == "completed":
                task = self.state_store.update_task_status(
                    task_id,
                    TaskStatus.COMPLETED,
                    result=agent_run.get("result")
                )
            else:
                task = self.state_store.update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error_message=f"Agent run {agent_status}"
                )
            
            return task
            
        except Exception as e:
            self.state_store.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error_message=str(e)
            )
            raise TaskError(f"Task failed: {e}")
    
    def close(self):
        """Close resources"""
        self.client.close()


class LogAnalyzer:
    """Analyzes agent run logs for insights and outcomes"""
    
    def __init__(self):
        pass
    
    def analyze_logs(self, logs):
        """Analyze logs and extract insights"""
        # Mock implementation for testing
        return {
            "total_logs": len(logs),
            "success": True,
            "insights": ["Analysis complete"]
        }
    
    def extract_outcomes(self, logs):
        """Extract outcomes from logs"""
        # Mock implementation for testing
        return {
            "outcome": "success",
            "summary": "Task completed successfully"
        }
