"""
State management for Codegen MCP server
Tracks agent runs and orchestrator relationships
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from threading import Lock

logger = logging.getLogger(__name__)

# Default state directory
STATE_DIR = Path.home() / ".codegen" / "state"
RUNS_FILE = STATE_DIR / "runs.json"
ORCHESTRATORS_FILE = STATE_DIR / "orchestrators.json"

class StateManager:
    """Manages state for agent runs and orchestrator relationships"""
    
    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or STATE_DIR
        self.runs_file = self.state_dir / "runs.json"
        self.orchestrators_file = self.state_dir / "orchestrators.json"
        self.lock = Lock()
        
        # Create state directory if it doesn't exist
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize state files if they don't exist
        if not self.runs_file.exists():
            self._save_runs({})
        
        if not self.orchestrators_file.exists():
            self._save_orchestrators({})
        
        # Load initial state
        self.runs = self._load_runs()
        self.orchestrators = self._load_orchestrators()
    
    def _load_runs(self) -> Dict[str, Any]:
        """Load runs from file"""
        try:
            with open(self.runs_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading runs file: {e}")
            return {}
    
    def _save_runs(self, runs: Dict[str, Any]) -> None:
        """Save runs to file"""
        try:
            with open(self.runs_file, 'w') as f:
                json.dump(runs, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving runs file: {e}")
    
    def _load_orchestrators(self) -> Dict[str, Any]:
        """Load orchestrators from file"""
        try:
            with open(self.orchestrators_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading orchestrators file: {e}")
            return {}
    
    def _save_orchestrators(self, orchestrators: Dict[str, Any]) -> None:
        """Save orchestrators to file"""
        try:
            with open(self.orchestrators_file, 'w') as f:
                json.dump(orchestrators, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving orchestrators file: {e}")
    
    def register_run(self, run_id: str, orchestrator_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a new agent run"""
        with self.lock:
            self.runs = self._load_runs()
            
            self.runs[run_id] = {
                "id": run_id,
                "orchestrator_id": orchestrator_id,
                "created_at": time.time(),
                "status": "running",
                "metadata": metadata or {}
            }
            
            self._save_runs(self.runs)
            
            # If this is an orchestrator, register it
            if not orchestrator_id:  # This run is itself an orchestrator
                self.register_orchestrator(run_id)
    
    def register_orchestrator(self, orchestrator_id: str) -> None:
        """Register a new orchestrator"""
        with self.lock:
            self.orchestrators = self._load_orchestrators()
            
            self.orchestrators[orchestrator_id] = {
                "id": orchestrator_id,
                "created_at": time.time(),
                "status": "running",
                "child_runs": []
            }
            
            self._save_orchestrators(self.orchestrators)
    
    def add_child_to_orchestrator(self, orchestrator_id: str, child_run_id: str) -> None:
        """Add a child run to an orchestrator"""
        with self.lock:
            self.orchestrators = self._load_orchestrators()
            
            if orchestrator_id not in self.orchestrators:
                self.register_orchestrator(orchestrator_id)
            
            if "child_runs" not in self.orchestrators[orchestrator_id]:
                self.orchestrators[orchestrator_id]["child_runs"] = []
            
            self.orchestrators[orchestrator_id]["child_runs"].append(child_run_id)
            self._save_orchestrators(self.orchestrators)
    
    def update_run_status(self, run_id: str, status: str, result: Optional[str] = None) -> None:
        """Update the status of a run"""
        with self.lock:
            self.runs = self._load_runs()
            
            if run_id in self.runs:
                self.runs[run_id]["status"] = status
                self.runs[run_id]["updated_at"] = time.time()
                
                if result:
                    self.runs[run_id]["result"] = result
                
                self._save_runs(self.runs)
    
    def update_orchestrator_status(self, orchestrator_id: str, status: str) -> None:
        """Update the status of an orchestrator"""
        with self.lock:
            self.orchestrators = self._load_orchestrators()
            
            if orchestrator_id in self.orchestrators:
                self.orchestrators[orchestrator_id]["status"] = status
                self.orchestrators[orchestrator_id]["updated_at"] = time.time()
                self._save_orchestrators(self.orchestrators)
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run details"""
        with self.lock:
            self.runs = self._load_runs()
            return self.runs.get(run_id)
    
    def get_orchestrator(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator details"""
        with self.lock:
            self.orchestrators = self._load_orchestrators()
            return self.orchestrators.get(orchestrator_id)
    
    def get_orchestrator_for_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get the orchestrator for a run"""
        run = self.get_run(run_id)
        if not run or not run.get("orchestrator_id"):
            return None
        
        return self.get_orchestrator(run["orchestrator_id"])
    
    def get_all_runs(self) -> Dict[str, Any]:
        """Get all runs"""
        with self.lock:
            return self._load_runs()
    
    def get_all_orchestrators(self) -> Dict[str, Any]:
        """Get all orchestrators"""
        with self.lock:
            return self._load_orchestrators()
    
    def clean_old_runs(self, max_age_days: int = 7) -> None:
        """Clean up old runs"""
        with self.lock:
            self.runs = self._load_runs()
            self.orchestrators = self._load_orchestrators()
            
            now = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            # Clean up runs
            runs_to_remove = []
            for run_id, run in self.runs.items():
                if now - run.get("created_at", 0) > max_age_seconds:
                    runs_to_remove.append(run_id)
            
            for run_id in runs_to_remove:
                del self.runs[run_id]
            
            # Clean up orchestrators
            orchestrators_to_remove = []
            for orchestrator_id, orchestrator in self.orchestrators.items():
                if now - orchestrator.get("created_at", 0) > max_age_seconds:
                    orchestrators_to_remove.append(orchestrator_id)
            
            for orchestrator_id in orchestrators_to_remove:
                del self.orchestrators[orchestrator_id]
            
            self._save_runs(self.runs)
            self._save_orchestrators(self.orchestrators)

