"""
Controller for the Codegen UI.

This module provides the controller for the Codegen UI,
handling business logic and communication with the API.
"""

import logging
import threading
from typing import Any, Dict, List, Optional, Callable

from codegen_client import CodegenClient, CodegenApiError
from ui.core.events import EventBus, Event, EventType
from ui.core.state import AppState

logger = logging.getLogger(__name__)


class Controller:
    """Controller for the Codegen UI."""
    
    def __init__(self):
        """Initialize the controller."""
        self.event_bus = EventBus()
        self.state = AppState()
        self.client = None
        
        # Register event handlers
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers."""
        self.event_bus.subscribe(EventType.LOGIN, self._handle_login)
        self.event_bus.subscribe(EventType.LOGOUT, self._handle_logout)
        self.event_bus.subscribe(EventType.AGENT_RUN_CREATED, self._handle_agent_run_created)
    
    def _handle_login(self, event: Event):
        """
        Handle login event.
        
        Args:
            event: The login event.
        """
        api_key = event.data.get("api_key")
        if not api_key:
            self.event_bus.publish(
                Event(
                    EventType.LOGIN_FAILURE,
                    {"error": "API key is required"}
                )
            )
            return
        
        # Start login thread
        threading.Thread(
            target=self._login_thread,
            args=(api_key,),
            daemon=True
        ).start()
    
    def _login_thread(self, api_key: str):
        """
        Login thread.
        
        Args:
            api_key: The API key to use for authentication.
        """
        try:
            # Initialize client
            self.client = CodegenClient(api_key=api_key)
            
            # Test connection by getting organizations
            orgs = self.client.organizations.get_organizations()
            
            # Update state
            self.state.api_key = api_key
            if orgs.items:
                self.state.current_org_id = orgs.items[0].id
            
            # Publish success event
            self.event_bus.publish(
                Event(
                    EventType.LOGIN_SUCCESS,
                    {"organizations": orgs.items}
                )
            )
            
        except Exception as e:
            logger.exception(f"Login failed: {e}")
            
            # Publish failure event
            self.event_bus.publish(
                Event(
                    EventType.LOGIN_FAILURE,
                    {"error": str(e)}
                )
            )
    
    def _handle_logout(self, event: Event):
        """
        Handle logout event.
        
        Args:
            event: The logout event.
        """
        # Clear state
        self.state.api_key = None
        self.state.current_org_id = None
        
        # Clear client
        self.client = None
        
        # Publish UI refresh event
        self.event_bus.publish(Event(EventType.UI_REFRESH))
    
    def _handle_agent_run_created(self, event: Event):
        """
        Handle agent run created event.
        
        Args:
            event: The agent run created event.
        """
        # Start agent run thread
        threading.Thread(
            target=self._agent_run_thread,
            args=(event.data,),
            daemon=True
        ).start()
    
    def _agent_run_thread(self, data: Dict[str, Any]):
        """
        Agent run thread.
        
        Args:
            data: The agent run data.
        """
        try:
            # Get agent run parameters
            prompt = data.get("prompt")
            org_id = self.state.current_org_id
            
            if not prompt:
                self.event_bus.publish(
                    Event(
                        EventType.UI_ERROR,
                        {"error": "Prompt is required"}
                    )
                )
                return
            
            if not org_id:
                self.event_bus.publish(
                    Event(
                        EventType.UI_ERROR,
                        {"error": "Organization ID is required"}
                    )
                )
                return
            
            # Create agent run
            run = self.client.create_agent_run(
                org_id=org_id,
                prompt=prompt
            )
            
            # Publish agent run updated event
            self.event_bus.publish(
                Event(
                    EventType.AGENT_RUN_UPDATED,
                    {"run": run}
                )
            )
            
            # Wait for agent run to complete
            run = self.client.wait_for_agent_run(
                org_id=org_id,
                run_id=run.id,
                timeout=300
            )
            
            # Publish agent run completed event
            self.event_bus.publish(
                Event(
                    EventType.AGENT_RUN_COMPLETED,
                    {"run": run}
                )
            )
            
        except Exception as e:
            logger.exception(f"Agent run failed: {e}")
            
            # Publish agent run failed event
            self.event_bus.publish(
                Event(
                    EventType.AGENT_RUN_FAILED,
                    {"error": str(e)}
                )
            )
    
    def get_agent_runs(self, limit: int = 20):
        """
        Get agent runs.
        
        Args:
            limit: The maximum number of agent runs to return.
        
        Returns:
            A list of agent runs.
        """
        if not self.client or not self.state.current_org_id:
            return []
        
        try:
            runs = self.client.list_agent_runs(
                org_id=self.state.current_org_id,
                limit=limit
            )
            return runs.items
        except Exception as e:
            logger.exception(f"Failed to get agent runs: {e}")
            return []
    
    def get_agent_run_logs(self, run_id: int, skip: int = 0, limit: int = 100):
        """
        Get agent run logs.
        
        Args:
            run_id: The agent run ID.
            skip: The number of logs to skip.
            limit: The maximum number of logs to return.
        
        Returns:
            The agent run with logs.
        """
        if not self.client or not self.state.current_org_id:
            return None
        
        try:
            return self.client.get_agent_run_logs(
                org_id=self.state.current_org_id,
                run_id=run_id,
                skip=skip,
                limit=limit
            )
        except Exception as e:
            logger.exception(f"Failed to get agent run logs: {e}")
            return None

