"""
Application state for the Enhanced Codegen UI.

This module provides a central state management system for the Enhanced Codegen UI,
allowing components to access and modify shared state in a controlled way.
"""

from typing import Any, Dict, List, Optional, Set


class ApplicationState:
    """
    Application state for the Enhanced Codegen UI.
    
    This class provides a central state management system for the Enhanced Codegen UI,
    storing shared state like the current organization, agent runs, and repositories.
    """
    
    def __init__(self):
        """Initialize the application state."""
        # Authentication state
        self.is_authenticated = False
        
        # Organization state
        self.current_org_id = None
        self.organizations = []
        
        # Agent run state
        self.agent_runs = []
        self.current_agent_run_id = None
        
        # Repository state
        self.repositories = []
        
        # Model state
        self.models = []
        
        # UI state
        self.current_view = "login"
        
    def reset(self):
        """Reset the application state."""
        self.__init__()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the application state to a dictionary.
        
        Returns:
            Dict[str, Any]: Application state as a dictionary
        """
        return {
            "is_authenticated": self.is_authenticated,
            "current_org_id": self.current_org_id,
            "organizations": self.organizations,
            "agent_runs": self.agent_runs,
            "current_agent_run_id": self.current_agent_run_id,
            "repositories": self.repositories,
            "models": self.models,
            "current_view": self.current_view,
        }
        
    def update(self, state_dict: Dict[str, Any]):
        """
        Update the application state from a dictionary.
        
        Args:
            state_dict: Dictionary with state values to update
        """
        for key, value in state_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

