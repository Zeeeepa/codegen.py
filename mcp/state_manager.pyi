"""
Type stub file for state_manager.py
"""

from typing import Dict, Any, Optional, Union
from pathlib import Path

class StateManager:
    """Manages state for agent runs and orchestrators"""
    def __init__(self, state_dir: Optional[Union[str, Path]] = None) -> None: ...
    
    def get_run(self, run_id: str) -> Dict[str, Any]: ...
    
    def get_orchestrator(self, orchestrator_id: str) -> Dict[str, Any]: ...
    
    def get_orchestrator_for_run(self, run_id: str) -> Optional[Dict[str, Any]]: ...
    
    def get_all_runs(self) -> Dict[str, Dict[str, Any]]: ...
    
    def get_all_orchestrators(self) -> Dict[str, Dict[str, Any]]: ...
    
    def register_run(
        self, 
        run_id: str, 
        orchestrator_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None: ...
    
    def register_orchestrator(self, orchestrator_id: str) -> None: ...
    
    def add_child_to_orchestrator(self, orchestrator_id: str, child_run_id: str) -> None: ...
    
    def update_run_status(
        self, 
        run_id: str, 
        status: str,
        result: Optional[Any] = None
    ) -> None: ...
    
    def update_orchestrator_status(
        self, 
        orchestrator_id: str, 
        status: str
    ) -> None: ...
    
    def cleanup_old_runs(self, max_age_days: int = 7) -> int: ...

