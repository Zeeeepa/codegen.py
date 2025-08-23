"""
State management for the Codegen UI.

This module provides state management for the Codegen UI.
"""

from typing import Any, Dict, List, Optional


class AppState:
    """Application state for the Codegen UI."""
    
    def __init__(self):
        """Initialize the application state."""
        # Authentication state
        self.api_key: Optional[str] = None
        self.current_org_id: Optional[str] = None
        
        # UI state
        self.current_view: str = "login"
        self.loading: bool = False
        self.error: Optional[str] = None
        
        # Data state
        self.agent_runs: List[Dict[str, Any]] = []
        self.projects: List[Dict[str, Any]] = []
        self.current_agent_run_id: Optional[int] = None

