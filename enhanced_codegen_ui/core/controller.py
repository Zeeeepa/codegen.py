"""
Controller for the Enhanced Codegen UI.

This module provides a controller for the Enhanced Codegen UI,
coordinating between the UI and the API.
"""

import logging
import threading
import queue
import json
import os
from typing import Dict, Any, Optional, List, Callable, Tuple

from enhanced_codegen_ui.core.events import EventBus, Event, EventType
from enhanced_codegen_ui.core.state import State
from enhanced_codegen_ui.utils.constants import API_ENDPOINTS, DEFAULTS


class Controller:
    """Controller for the Enhanced Codegen UI."""
    
    def __init__(self, api_url: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize the controller.
        
        Args:
            api_url: API URL
            config_file: Configuration file path
        """
        self.logger = logging.getLogger(__name__)
        self.event_bus = EventBus()
        self.state = State()
        self.api_url = api_url or DEFAULTS["api_url"]
        self.config_file = config_file or DEFAULTS["config_file"]
        self.api_key = None
        self.task_queue = queue.Queue()
        self.worker_thread = None
        self.running = False
        
        # Load configuration
        self._load_config()
        
        # Register event handlers
        self._register_event_handlers()
        
    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    
                # Update configuration
                if "api_url" in config:
                    self.api_url = config["api_url"]
                if "api_key" in config:
                    self.api_key = config["api_key"]
                    
                self.logger.info(f"Loaded configuration from {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            
    def _save_config(self):
        """Save configuration to file."""
        try:
            config = {
                "api_url": self.api_url,
                "api_key": self.api_key
            }
            
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
                
            self.logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            
    def _register_event_handlers(self):
        """Register event handlers."""
        # Authentication events
        self.event_bus.subscribe(
            EventType.LOGIN_REQUESTED,
            self._handle_login_requested
        )
        
        self.event_bus.subscribe(
            EventType.LOGOUT_REQUESTED,
            self._handle_logout_requested
        )
        
        # Agent run events
        self.event_bus.subscribe(
            EventType.AGENT_RUN_REQUESTED,
            self._handle_agent_run_requested
        )
        
        self.event_bus.subscribe(
            EventType.AGENT_RUN_CANCELLED,
            self._handle_agent_run_cancelled
        )
        
        self.event_bus.subscribe(
            EventType.AGENT_RUN_CONTINUED,
            self._handle_agent_run_continued
        )
        
        # Data events
        self.event_bus.subscribe(
            EventType.DATA_REQUESTED,
            self._handle_data_requested
        )
        
        # Refresh events
        self.event_bus.subscribe(
            EventType.REFRESH_REQUESTED,
            self._handle_refresh_requested
        )
        
    def _handle_login_requested(self, event: Event):
        """
        Handle login requested event.
        
        Args:
            event: Event object
        """
        api_key = event.data.get("api_key")
        if not api_key:
            self.event_bus.publish(
                Event(EventType.LOGIN_FAILED, {"error": "API key is required"})
            )
            return
            
        # Queue login task
        self._queue_task(
            self._login,
            api_key,
            lambda result: self._handle_login_result(result, api_key)
        )
        
    def _login(self, api_key: str) -> Dict[str, Any]:
        """
        Login to the API.
        
        Args:
            api_key: API key
            
        Returns:
            API response
        """
        # TODO: Implement API login
        # For now, just return success
        return {"status": "success", "user": {"id": "test-user", "name": "Test User"}}
        
    def _handle_login_result(self, result: Dict[str, Any], api_key: str):
        """
        Handle login result.
        
        Args:
            result: API response
            api_key: API key
        """
        if result.get("status") == "success":
            # Update state
            self.api_key = api_key
            self.state.set("user", result.get("user"))
            self.state.set("authenticated", True)
            
            # Save configuration
            self._save_config()
            
            # Publish event
            self.event_bus.publish(
                Event(EventType.LOGIN_SUCCEEDED, {"user": result.get("user")})
            )
        else:
            # Publish event
            self.event_bus.publish(
                Event(EventType.LOGIN_FAILED, {"error": result.get("error", "Login failed")})
            )
            
    def _handle_logout_requested(self, event: Event):
        """
        Handle logout requested event.
        
        Args:
            event: Event object
        """
        # Update state
        self.api_key = None
        self.state.set("user", None)
        self.state.set("authenticated", False)
        
        # Save configuration
        self._save_config()
        
    def _handle_agent_run_requested(self, event: Event):
        """
        Handle agent run requested event.
        
        Args:
            event: Event object
        """
        # Queue agent run task
        self._queue_task(
            self._create_agent_run,
            event.data,
            self._handle_agent_run_result
        )
        
    def _create_agent_run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an agent run.
        
        Args:
            data: Agent run data
            
        Returns:
            API response
        """
        # TODO: Implement API call
        # For now, just return success
        return {
            "status": "success",
            "agent_run": {
                "id": "test-agent-run",
                "status": "running",
                "prompt": data.get("prompt"),
                "repo_id": data.get("repo_id"),
                "model": data.get("model")
            }
        }
        
    def _handle_agent_run_result(self, result: Dict[str, Any]):
        """
        Handle agent run result.
        
        Args:
            result: API response
        """
        if result.get("status") == "success":
            # Publish event
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_STARTED, {"agent_run": result.get("agent_run")})
            )
        else:
            # Publish event
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_FAILED, {"error": result.get("error", "Agent run failed")})
            )
            
    def _handle_agent_run_cancelled(self, event: Event):
        """
        Handle agent run cancelled event.
        
        Args:
            event: Event object
        """
        agent_run_id = event.data.get("agent_run_id")
        if not agent_run_id:
            self.event_bus.publish(
                Event(EventType.ERROR_OCCURRED, {"error": "Agent run ID is required"})
            )
            return
            
        # Queue cancel task
        self._queue_task(
            self._cancel_agent_run,
            agent_run_id,
            lambda result: self._handle_cancel_agent_run_result(result, agent_run_id)
        )
        
    def _cancel_agent_run(self, agent_run_id: str) -> Dict[str, Any]:
        """
        Cancel an agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            API response
        """
        # TODO: Implement API call
        # For now, just return success
        return {"status": "success"}
        
    def _handle_cancel_agent_run_result(self, result: Dict[str, Any], agent_run_id: str):
        """
        Handle cancel agent run result.
        
        Args:
            result: API response
            agent_run_id: Agent run ID
        """
        if result.get("status") == "success":
            # Publish event
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_CANCELLED, {"agent_run_id": agent_run_id})
            )
        else:
            # Publish event
            self.event_bus.publish(
                Event(EventType.ERROR_OCCURRED, {"error": result.get("error", "Cancel agent run failed")})
            )
            
    def _handle_agent_run_continued(self, event: Event):
        """
        Handle agent run continued event.
        
        Args:
            event: Event object
        """
        agent_run_id = event.data.get("agent_run_id")
        if not agent_run_id:
            self.event_bus.publish(
                Event(EventType.ERROR_OCCURRED, {"error": "Agent run ID is required"})
            )
            return
            
        # Queue continue task
        self._queue_task(
            self._continue_agent_run,
            agent_run_id,
            lambda result: self._handle_continue_agent_run_result(result, agent_run_id)
        )
        
    def _continue_agent_run(self, agent_run_id: str) -> Dict[str, Any]:
        """
        Continue an agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            API response
        """
        # TODO: Implement API call
        # For now, just return success
        return {"status": "success"}
        
    def _handle_continue_agent_run_result(self, result: Dict[str, Any], agent_run_id: str):
        """
        Handle continue agent run result.
        
        Args:
            result: API response
            agent_run_id: Agent run ID
        """
        if result.get("status") == "success":
            # Publish event
            self.event_bus.publish(
                Event(EventType.AGENT_RUN_CONTINUED, {"agent_run_id": agent_run_id})
            )
        else:
            # Publish event
            self.event_bus.publish(
                Event(EventType.ERROR_OCCURRED, {"error": result.get("error", "Continue agent run failed")})
            )
            
    def _handle_data_requested(self, event: Event):
        """
        Handle data requested event.
        
        Args:
            event: Event object
        """
        data_type = event.data.get("type")
        if not data_type:
            self.event_bus.publish(
                Event(EventType.ERROR_OCCURRED, {"error": "Data type is required"})
            )
            return
            
        # Queue data task
        self._queue_task(
            self._get_data,
            data_type,
            lambda result: self._handle_data_result(result, data_type)
        )
        
    def _get_data(self, data_type: str) -> Dict[str, Any]:
        """
        Get data from the API.
        
        Args:
            data_type: Data type
            
        Returns:
            API response
        """
        # TODO: Implement API call
        # For now, just return mock data
        if data_type == "agent_runs":
            return {
                "status": "success",
                "agent_runs": [
                    {
                        "id": "agent-run-1",
                        "status": "completed",
                        "prompt": "Test prompt 1",
                        "repo_id": "repo-1",
                        "model": "gpt-4",
                        "created_at": "2023-01-01T00:00:00Z"
                    },
                    {
                        "id": "agent-run-2",
                        "status": "running",
                        "prompt": "Test prompt 2",
                        "repo_id": "repo-2",
                        "model": "gpt-4",
                        "created_at": "2023-01-02T00:00:00Z"
                    }
                ]
            }
        elif data_type == "repositories":
            return {
                "status": "success",
                "repositories": [
                    {
                        "id": "repo-1",
                        "name": "Repository 1",
                        "description": "Test repository 1",
                        "url": "https://github.com/test/repo1"
                    },
                    {
                        "id": "repo-2",
                        "name": "Repository 2",
                        "description": "Test repository 2",
                        "url": "https://github.com/test/repo2"
                    }
                ]
            }
        elif data_type == "organizations":
            return {
                "status": "success",
                "organizations": [
                    {
                        "id": "org-1",
                        "name": "Organization 1",
                        "description": "Test organization 1"
                    },
                    {
                        "id": "org-2",
                        "name": "Organization 2",
                        "description": "Test organization 2"
                    }
                ]
            }
        else:
            return {"status": "error", "error": f"Unknown data type: {data_type}"}
            
    def _handle_data_result(self, result: Dict[str, Any], data_type: str):
        """
        Handle data result.
        
        Args:
            result: API response
            data_type: Data type
        """
        if result.get("status") == "success":
            # Publish event
            self.event_bus.publish(
                Event(EventType.DATA_LOADED, {
                    "type": data_type,
                    data_type: result.get(data_type, [])
                })
            )
        else:
            # Publish event
            self.event_bus.publish(
                Event(EventType.DATA_LOAD_FAILED, {
                    "type": data_type,
                    "error": result.get("error", f"Failed to load {data_type}")
                })
            )
            
    def _handle_refresh_requested(self, event: Event):
        """
        Handle refresh requested event.
        
        Args:
            event: Event object
        """
        # Just forward to data requested
        self._handle_data_requested(event)
        
    def _queue_task(self, task_func: Callable, *args, callback: Optional[Callable] = None):
        """
        Queue a task for the worker thread.
        
        Args:
            task_func: Task function
            *args: Task arguments
            callback: Callback function for the result
        """
        self.task_queue.put((task_func, args, callback))
        
        # Start worker thread if not running
        if not self.running:
            self._start_worker()
            
    def _start_worker(self):
        """Start the worker thread."""
        if self.worker_thread and self.worker_thread.is_alive():
            return
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
    def _worker_loop(self):
        """Worker thread loop."""
        while self.running:
            try:
                # Get task from queue with timeout
                try:
                    task_func, args, callback = self.task_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                    
                # Execute task
                try:
                    result = task_func(*args)
                    
                    # Call callback with result
                    if callback:
                        callback(result)
                except Exception as e:
                    self.logger.error(f"Error executing task: {str(e)}")
                    
                    # Publish error event
                    self.event_bus.publish(
                        Event(EventType.ERROR_OCCURRED, {"error": str(e)})
                    )
                    
                # Mark task as done
                self.task_queue.task_done()
            except Exception as e:
                self.logger.error(f"Error in worker loop: {str(e)}")
                
    def stop(self):
        """Stop the controller."""
        self.running = False
        
        # Wait for worker thread to finish
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
            
    def get_agent_run(self, agent_run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            Agent run data or None if not found
        """
        # TODO: Implement API call
        # For now, just return mock data
        return {
            "id": agent_run_id,
            "status": "completed",
            "prompt": "Test prompt",
            "repo_id": "repo-1",
            "model": "gpt-4",
            "created_at": "2023-01-01T00:00:00Z",
            "completed_at": "2023-01-01T00:05:00Z",
            "output": "Test output"
        }
        
    def get_agent_run_logs(self, agent_run_id: str) -> List[Dict[str, Any]]:
        """
        Get agent run logs.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            Agent run logs
        """
        # TODO: Implement API call
        # For now, just return mock data
        return [
            {
                "timestamp": "2023-01-01T00:00:00Z",
                "level": "INFO",
                "message": "Agent run started"
            },
            {
                "timestamp": "2023-01-01T00:01:00Z",
                "level": "INFO",
                "message": "Processing prompt"
            },
            {
                "timestamp": "2023-01-01T00:05:00Z",
                "level": "INFO",
                "message": "Agent run completed"
            }
        ]
        
    def get_repository(self, repository_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a repository.
        
        Args:
            repository_id: Repository ID
            
        Returns:
            Repository data or None if not found
        """
        # TODO: Implement API call
        # For now, just return mock data
        return {
            "id": repository_id,
            "name": "Test Repository",
            "description": "Test repository description",
            "url": "https://github.com/test/repo"
        }
        
    def get_organization(self, organization_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an organization.
        
        Args:
            organization_id: Organization ID
            
        Returns:
            Organization data or None if not found
        """
        # TODO: Implement API call
        # For now, just return mock data
        return {
            "id": organization_id,
            "name": "Test Organization",
            "description": "Test organization description"
        }

