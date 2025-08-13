"""
State manager for tracking agent runs and orchestrators
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, cast

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages state for agent runs and orchestrators
    """
    
    def __init__(self, state_dir: Optional[Union[str, Path]] = None):
        """Initialize the state manager"""
        if state_dir is None:
            # Use default state directory
            home_dir = Path.home()
            state_dir = home_dir / ".codegen" / "state"
        
        if isinstance(state_dir, str):
            state_dir = Path(state_dir)
        
        self.state_dir = state_dir
        self.runs_file = self.state_dir / "runs.json"
        self.orchestrators_file = self.state_dir / "orchestrators.json"
        
        # Create state directory if it doesn't exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize state
        self._runs: Dict[str, Dict[str, Any]] = {}
        self._orchestrators: Dict[str, Dict[str, Any]] = {}
        
        # Load state from disk
        self._load_state()
    
    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get a run by ID"""
        return cast(Dict[str, Any], self._runs.get(run_id, {}))
    
    def get_orchestrator(self, orchestrator_id: str) -> Dict[str, Any]:
        """Get an orchestrator by ID"""
        return cast(Dict[str, Any], self._orchestrators.get(orchestrator_id, {}))
    
    def get_orchestrator_for_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the orchestrator for a run"""
        run = self.get_run(run_id)
        if not run:
            return None
        
        orchestrator_id = run.get("orchestrator_id")
        if not orchestrator_id:
            return None
        
        return self.get_orchestrator(orchestrator_id)
    
    def get_all_runs(self) -> Dict[str, Dict[str, Any]]:
        """Get all runs"""
        return self._runs
    
    def get_all_orchestrators(self) -> Dict[str, Dict[str, Any]]:
        """Get all orchestrators"""
        return self._orchestrators
    
    def register_run(
        self, 
        run_id: str, 
        orchestrator_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new run"""
        self._runs[run_id] = {
            "id": run_id,
            "orchestrator_id": orchestrator_id,
            "created_at": time.time(),
            "status": "running",
            "metadata": metadata or {}
        }
        
        self._save_runs()
    
    def register_orchestrator(self, orchestrator_id: str) -> None:
        """Register a new orchestrator"""
        self._orchestrators[orchestrator_id] = {
            "id": orchestrator_id,
            "created_at": time.time(),
            "status": "running",
            "child_runs": []
        }
        
        self._save_orchestrators()
    
    def add_child_to_orchestrator(self, orchestrator_id: str, child_run_id: str) -> None:
        """Add a child run to an orchestrator"""
        orchestrator = self._orchestrators.get(orchestrator_id)
        if not orchestrator:
            # Create the orchestrator if it doesn't exist
            self.register_orchestrator(orchestrator_id)
            orchestrator = self._orchestrators.get(orchestrator_id, {})
        
        child_runs = orchestrator.get("child_runs", [])
        if child_run_id not in child_runs:
            child_runs.append(child_run_id)
            orchestrator["child_runs"] = child_runs
            
            self._save_orchestrators()
    
    def update_run_status(
        self, 
        run_id: str, 
        status: str,
        result: Optional[Any] = None
    ) -> None:
        """Update the status of a run"""
        run = self._runs.get(run_id)
        if not run:
            logger.warning(f"Run {run_id} not found in state manager")
            return
        
        run["status"] = status
        run["result"] = result
        run["updated_at"] = time.time()
        
        self._save_runs()
    
    def update_orchestrator_status(
        self, 
        orchestrator_id: str, 
        status: str
    ) -> None:
        """Update the status of an orchestrator"""
        orchestrator = self._orchestrators.get(orchestrator_id)
        if not orchestrator:
            logger.warning(f"Orchestrator {orchestrator_id} not found in state manager")
            return
        
        orchestrator["status"] = status
        orchestrator["updated_at"] = time.time()
        
        self._save_orchestrators()
    
    def _load_state(self) -> None:
        """Load state from disk"""
        # Load runs
        if self.runs_file.exists():
            try:
                with open(self.runs_file, "r") as f:
                    self._runs = json.load(f)
            except Exception as e:
                logger.error(f"Error loading runs: {e}")
                self._runs = {}
        
        # Load orchestrators
        if self.orchestrators_file.exists():
            try:
                with open(self.orchestrators_file, "r") as f:
                    self._orchestrators = json.load(f)
            except Exception as e:
                logger.error(f"Error loading orchestrators: {e}")
                self._orchestrators = {}
    
    def _save_runs(self) -> None:
        """Save runs to disk"""
        try:
            with open(self.runs_file, "w") as f:
                json.dump(self._runs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving runs: {e}")
    
    def _save_orchestrators(self) -> None:
        """Save orchestrators to disk"""
        try:
            with open(self.orchestrators_file, "w") as f:
                json.dump(self._orchestrators, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving orchestrators: {e}")
    
    def cleanup_old_runs(self, max_age_days: int = 7) -> int:
        """Clean up old runs"""
        now = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        runs_to_remove = []
        for run_id, run in self._runs.items():
            created_at = run.get("created_at", 0)
            if now - created_at > max_age_seconds:
                runs_to_remove.append(run_id)
        
        for run_id in runs_to_remove:
            del self._runs[run_id]
        
        if runs_to_remove:
            self._save_runs()
        
        return len(runs_to_remove)

