"""
Application controller for the Enhanced Codegen UI.

This module provides the main controller for the Enhanced Codegen UI,
coordinating between the UI components and the Codegen API client.
"""

import logging
import threading
import queue
from typing import Any, Dict, List, Optional, Callable, Union, TypeVar, Generic

from codegen_client import CodegenClient, CodegenApiError
from enhanced_codegen_ui.core.events import EventBus, Event, EventType
from enhanced_codegen_ui.core.state import ApplicationState
from enhanced_codegen_ui.utils.config import ConfigManager
from enhanced_codegen_ui.utils.logging_config import setup_logging

# Type variable for generic methods
T = TypeVar('T')


class Controller:
    """
    Main controller for the Enhanced Codegen UI.
    
    This class coordinates between the UI components and the Codegen API client,
    managing application state, events, and background tasks.
    """
    
    def __init__(self):
        """Initialize the controller."""
        # Set up logging
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Controller")
        
        # Initialize configuration
        self.config = ConfigManager()
        
        # Initialize state
        self.state = ApplicationState()
        
        # Initialize event bus
        self.event_bus = EventBus()
        
        # Initialize client
        self.client = None
        
        # Initialize task queue and worker thread
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.worker_thread.start()
        
        # Register event handlers
        self._register_event_handlers()
        
        # Try to initialize client from saved config
        self._init_client_from_config()
        
    def _register_event_handlers(self):
        """Register event handlers for application events."""
        self.event_bus.subscribe(EventType.LOGIN_REQUESTED, self._handle_login_requested)
        self.event_bus.subscribe(EventType.LOGOUT_REQUESTED, self._handle_logout_requested)
        self.event_bus.subscribe(EventType.AGENT_RUN_REQUESTED, self._handle_agent_run_requested)
        self.event_bus.subscribe(EventType.AGENT_RUN_CANCEL_REQUESTED, self._handle_agent_run_cancel_requested)
        self.event_bus.subscribe(EventType.AGENT_RUN_CONTINUE_REQUESTED, self._handle_agent_run_continue_requested)
        self.event_bus.subscribe(EventType.REFRESH_REQUESTED, self._handle_refresh_requested)
        
    def _init_client_from_config(self):
        """Initialize the client from saved configuration."""
        api_key = self.config.get("api_key")
        if api_key:
            self.logger.info("Initializing client from saved API key")
            self.submit_task(
                self._initialize_client,
                api_key,
                on_success=lambda result: self.event_bus.publish(
                    Event(EventType.LOGIN_SUCCEEDED, {"client": self.client})
                ),
                on_error=lambda error: self.event_bus.publish(
                    Event(EventType.LOGIN_FAILED, {"error": str(error)})
                )
            )
    
    def _initialize_client(self, api_key: str) -> CodegenClient:
        """
        Initialize the Codegen API client.
        
        Args:
            api_key: API key for authentication
            
        Returns:
            CodegenClient: Initialized client
            
        Raises:
            CodegenApiError: If client initialization fails
        """
        self.client = CodegenClient(api_key=api_key)
        
        # Test connection by getting organizations
        orgs = self.client.organizations.get_organizations()
        
        # Set current organization
        if orgs.items:
            self.state.current_org_id = orgs.items[0].id
            self.state.organizations = orgs.items
            
        return self.client
    
    def submit_task(
        self,
        task: Callable[..., T],
        *args,
        on_success: Optional[Callable[[T], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        **kwargs
    ) -> None:
        """
        Submit a task to be executed in the background.
        
        Args:
            task: Task function to execute
            *args: Arguments to pass to the task function
            on_success: Callback to execute on success
            on_error: Callback to execute on error
            **kwargs: Keyword arguments to pass to the task function
        """
        self.task_queue.put((task, args, kwargs, on_success, on_error))
        
    def _process_tasks(self):
        """Process tasks from the task queue."""
        while True:
            try:
                # Get task from queue
                task, args, kwargs, on_success, on_error = self.task_queue.get()
                
                try:
                    # Execute task
                    result = task(*args, **kwargs)
                    
                    # Call success callback
                    if on_success:
                        on_success(result)
                        
                except Exception as e:
                    # Log error
                    self.logger.exception(f"Error executing task {task.__name__}: {str(e)}")
                    
                    # Call error callback
                    if on_error:
                        on_error(e)
                        
                finally:
                    # Mark task as done
                    self.task_queue.task_done()
                    
            except Exception as e:
                # Log error
                self.logger.exception(f"Error in task processor: {str(e)}")
    
    def _handle_login_requested(self, event: Event):
        """
        Handle login requested event.
        
        Args:
            event: Event object with api_key in data
        """
        api_key = event.data.get("api_key")
        if not api_key:
            self.event_bus.publish(
                Event(EventType.LOGIN_FAILED, {"error": "API key is required"})
            )
            return
            
        self.submit_task(
            self._initialize_client,
            api_key,
            on_success=lambda result: self._handle_login_success(api_key),
            on_error=lambda error: self.event_bus.publish(
                Event(EventType.LOGIN_FAILED, {"error": str(error)})
            )
        )
        
    def _handle_login_success(self, api_key: str):
        """
        Handle successful login.
        
        Args:
            api_key: API key used for login
        """
        # Save API key
        self.config.set("api_key", api_key)
        
        # Publish login succeeded event
        self.event_bus.publish(
            Event(EventType.LOGIN_SUCCEEDED, {
                "client": self.client,
                "org_id": self.state.current_org_id,
                "organizations": self.state.organizations
            })
        )
        
        # Load initial data
        self._load_initial_data()
        
    def _load_initial_data(self):
        """Load initial data after login."""
        if not self.client or not self.state.current_org_id:
            return
            
        # Load agent runs
        self.submit_task(
            self._load_agent_runs,
            on_success=lambda result: self.event_bus.publish(
                Event(EventType.AGENT_RUNS_LOADED, {"agent_runs": result})
            ),
            on_error=lambda error: self.event_bus.publish(
                Event(EventType.LOAD_ERROR, {"error": str(error), "type": "agent_runs"})
            )
        )
        
        # Load repositories
        self.submit_task(
            self._load_repositories,
            on_success=lambda result: self.event_bus.publish(
                Event(EventType.REPOSITORIES_LOADED, {"repositories": result})
            ),
            on_error=lambda error: self.event_bus.publish(
                Event(EventType.LOAD_ERROR, {"error": str(error), "type": "repositories"})
            )
        )
        
        # Load models
        self.submit_task(
            self._load_models,
            on_success=lambda result: self.event_bus.publish(
                Event(EventType.MODELS_LOADED, {"models": result})
            ),
            on_error=lambda error: self.event_bus.publish(
                Event(EventType.LOAD_ERROR, {"error": str(error), "type": "models"})
            )
        )
        
    def _load_agent_runs(self, limit: int = 50, status: Optional[str] = None):
        """
        Load agent runs from the API.
        
        Args:
            limit: Maximum number of agent runs to load
            status: Optional status filter
            
        Returns:
            List of agent runs
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
            
        agent_runs = self.client.agents.get_agent_runs(
            org_id=self.state.current_org_id,
            **params
        )
        
        return agent_runs.items
        
    def _load_repositories(self, limit: int = 50):
        """
        Load repositories from the API.
        
        Args:
            limit: Maximum number of repositories to load
            
        Returns:
            List of repositories
        """
        repositories = self.client.repositories.get_repositories(
            org_id=self.state.current_org_id,
            limit=limit
        )
        
        return repositories.items
        
    def _load_models(self):
        """
        Load available models.
        
        Returns:
            List of available models
        """
        # In a real implementation, this would fetch models from the API
        # For now, return a default list
        return [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-2",
            "claude-instant",
        ]
        
    def _handle_logout_requested(self, event: Event):
        """
        Handle logout requested event.
        
        Args:
            event: Event object
        """
        # Clear API key
        self.config.set("api_key", "")
        
        # Clear client and state
        self.client = None
        self.state.reset()
        
        # Publish logout succeeded event
        self.event_bus.publish(Event(EventType.LOGOUT_SUCCEEDED, {}))
        
    def _handle_agent_run_requested(self, event: Event):
        """
        Handle agent run requested event.
        
        Args:
            event: Event object with agent run parameters
        """
        if not self.client or not self.state.current_org_id:
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_FAILED, {"error": "Not logged in"})
            )
            return
            
        # Get parameters
        prompt = event.data.get("prompt")
        repo_id = event.data.get("repo_id")
        model = event.data.get("model")
        temperature = event.data.get("temperature", 0.7)
        metadata = event.data.get("metadata")
        
        # Validate parameters
        if not prompt:
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_FAILED, {"error": "Prompt is required"})
            )
            return
            
        # Create agent run
        self.submit_task(
            self._create_agent_run,
            prompt, repo_id, model, temperature, metadata,
            on_success=lambda result: self.event_bus.publish(
                Event(EventType.AGENT_RUN_SUCCEEDED, {"agent_run": result})
            ),
            on_error=lambda error: self.event_bus.publish(
                Event(EventType.AGENT_RUN_FAILED, {"error": str(error)})
            )
        )
        
    def _create_agent_run(
        self,
        prompt: str,
        repo_id: Optional[int] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Create an agent run.
        
        Args:
            prompt: Prompt for the agent
            repo_id: Optional repository ID
            model: Optional model to use
            temperature: Temperature for generation
            metadata: Optional metadata
            
        Returns:
            Created agent run
        """
        return self.client.agents.create_agent_run(
            org_id=self.state.current_org_id,
            prompt=prompt,
            repo_id=repo_id,
            model=model,
            temperature=temperature,
            metadata=metadata
        )
        
    def _handle_agent_run_cancel_requested(self, event: Event):
        """
        Handle agent run cancel requested event.
        
        Args:
            event: Event object with agent_run_id in data
        """
        if not self.client or not self.state.current_org_id:
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_CANCEL_FAILED, {"error": "Not logged in"})
            )
            return
            
        # Get agent run ID
        agent_run_id = event.data.get("agent_run_id")
        if not agent_run_id:
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_CANCEL_FAILED, {"error": "Agent run ID is required"})
            )
            return
            
        # Cancel agent run
        self.submit_task(
            self._cancel_agent_run,
            agent_run_id,
            on_success=lambda result: self.event_bus.publish(
                Event(EventType.AGENT_RUN_CANCEL_SUCCEEDED, {"agent_run_id": agent_run_id})
            ),
            on_error=lambda error: self.event_bus.publish(
                Event(EventType.AGENT_RUN_CANCEL_FAILED, {"error": str(error)})
            )
        )
        
    def _cancel_agent_run(self, agent_run_id: str):
        """
        Cancel an agent run.
        
        Args:
            agent_run_id: ID of the agent run to cancel
            
        Returns:
            Cancelled agent run
        """
        return self.client.agents.cancel_agent_run(
            org_id=self.state.current_org_id,
            agent_run_id=agent_run_id
        )
        
    def _handle_agent_run_continue_requested(self, event: Event):
        """
        Handle agent run continue requested event.
        
        Args:
            event: Event object with agent_run_id in data
        """
        if not self.client or not self.state.current_org_id:
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_CONTINUE_FAILED, {"error": "Not logged in"})
            )
            return
            
        # Get agent run ID
        agent_run_id = event.data.get("agent_run_id")
        if not agent_run_id:
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_CONTINUE_FAILED, {"error": "Agent run ID is required"})
            )
            return
            
        # Continue agent run
        self.submit_task(
            self._continue_agent_run,
            agent_run_id,
            on_success=lambda result: self.event_bus.publish(
                Event(EventType.AGENT_RUN_CONTINUE_SUCCEEDED, {"agent_run": result})
            ),
            on_error=lambda error: self.event_bus.publish(
                Event(EventType.AGENT_RUN_CONTINUE_FAILED, {"error": str(error)})
            )
        )
        
    def _continue_agent_run(self, agent_run_id: str):
        """
        Continue an agent run.
        
        Args:
            agent_run_id: ID of the agent run to continue
            
        Returns:
            Continued agent run
        """
        return self.client.agents.resume_agent_run(
            org_id=self.state.current_org_id,
            agent_run_id=agent_run_id,
            prompt="Continue from previous output"
        )
        
    def _handle_refresh_requested(self, event: Event):
        """
        Handle refresh requested event.
        
        Args:
            event: Event object with type in data
        """
        refresh_type = event.data.get("type", "all")
        
        if refresh_type == "agent_runs" or refresh_type == "all":
            self.submit_task(
                self._load_agent_runs,
                on_success=lambda result: self.event_bus.publish(
                    Event(EventType.AGENT_RUNS_LOADED, {"agent_runs": result})
                ),
                on_error=lambda error: self.event_bus.publish(
                    Event(EventType.LOAD_ERROR, {"error": str(error), "type": "agent_runs"})
                )
            )
            
        if refresh_type == "repositories" or refresh_type == "all":
            self.submit_task(
                self._load_repositories,
                on_success=lambda result: self.event_bus.publish(
                    Event(EventType.REPOSITORIES_LOADED, {"repositories": result})
                ),
                on_error=lambda error: self.event_bus.publish(
                    Event(EventType.LOAD_ERROR, {"error": str(error), "type": "repositories"})
                )
            )
            
        if refresh_type == "models" or refresh_type == "all":
            self.submit_task(
                self._load_models,
                on_success=lambda result: self.event_bus.publish(
                    Event(EventType.MODELS_LOADED, {"models": result})
                ),
                on_error=lambda error: self.event_bus.publish(
                    Event(EventType.LOAD_ERROR, {"error": str(error), "type": "models"})
                )
            )
            
    def get_agent_run(self, agent_run_id: str, callback: Callable[[Any], None]):
        """
        Get an agent run by ID.
        
        Args:
            agent_run_id: ID of the agent run to get
            callback: Callback to execute with the agent run
        """
        if not self.client or not self.state.current_org_id:
            callback(None)
            return
            
        self.submit_task(
            self._get_agent_run,
            agent_run_id,
            on_success=callback,
            on_error=lambda error: callback(None)
        )
        
    def _get_agent_run(self, agent_run_id: str):
        """
        Get an agent run by ID.
        
        Args:
            agent_run_id: ID of the agent run to get
            
        Returns:
            Agent run
        """
        return self.client.agents.get_agent_run(
            org_id=self.state.current_org_id,
            agent_run_id=agent_run_id
        )
        
    def get_agent_run_logs(self, agent_run_id: str, callback: Callable[[List[Dict[str, Any]]], None]):
        """
        Get logs for an agent run.
        
        Args:
            agent_run_id: ID of the agent run to get logs for
            callback: Callback to execute with the logs
        """
        if not self.client or not self.state.current_org_id:
            callback([])
            return
            
        self.submit_task(
            self._get_agent_run_logs,
            agent_run_id,
            on_success=lambda result: callback(result.get("logs", [])),
            on_error=lambda error: callback([])
        )
        
    def _get_agent_run_logs(self, agent_run_id: str):
        """
        Get logs for an agent run.
        
        Args:
            agent_run_id: ID of the agent run to get logs for
            
        Returns:
            Agent run logs
        """
        return self.client.agents_alpha.get_agent_run_logs(
            org_id=self.state.current_org_id,
            agent_run_id=agent_run_id
        )
        
    def get_organizations(self, callback: Callable[[List[Any]], None]):
        """
        Get organizations.
        
        Args:
            callback: Callback to execute with the organizations
        """
        if not self.client:
            callback([])
            return
            
        self.submit_task(
            self._get_organizations,
            on_success=lambda result: callback(result.items),
            on_error=lambda error: callback([])
        )
        
    def _get_organizations(self):
        """
        Get organizations.
        
        Returns:
            Organizations
        """
        return self.client.organizations.get_organizations()
        
    def set_current_organization(self, org_id: int):
        """
        Set the current organization.
        
        Args:
            org_id: Organization ID
        """
        self.state.current_org_id = org_id
        
        # Refresh data
        self.event_bus.publish(Event(EventType.REFRESH_REQUESTED, {"type": "all"}))

