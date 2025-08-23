"""
Multi-run processor for the Codegen API.

This module provides a processor for handling multiple runs.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)


class MultiRunProcessor:
    """Processor for handling multiple runs."""
    
    def __init__(self):
        """Initialize the multi-run processor."""
        self.runs: Dict[str, Dict[str, Any]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
    
    async def start_run(
        self,
        run_id: str,
        config: Dict[str, Any],
        callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        """Start a new run.
        
        Args:
            run_id: The ID of the run.
            config: The configuration for the run.
            callback: A callback function to call when the run completes.
        """
        if run_id in self.runs:
            logger.warning(f"Run {run_id} already exists")
            return
        
        self.runs[run_id] = {
            "id": run_id,
            "config": config,
            "status": "running",
            "result": None,
            "error": None,
        }
        
        task = asyncio.create_task(self._process_run(run_id, callback))
        self.tasks[run_id] = task
    
    async def _process_run(
        self,
        run_id: str,
        callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        """Process a run.
        
        Args:
            run_id: The ID of the run.
            callback: A callback function to call when the run completes.
        """
        try:
            # Simulate processing
            await asyncio.sleep(5)
            
            # Update run status
            self.runs[run_id]["status"] = "completed"
            self.runs[run_id]["result"] = {"message": "Run completed successfully"}
            
            # Call callback if provided
            if callback:
                callback(run_id, self.runs[run_id])
        except Exception as e:
            logger.error(f"Error processing run {run_id}: {e}")
            self.runs[run_id]["status"] = "failed"
            self.runs[run_id]["error"] = str(e)
            
            # Call callback if provided
            if callback:
                callback(run_id, self.runs[run_id])
        finally:
            # Clean up task
            if run_id in self.tasks:
                del self.tasks[run_id]
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a run by ID.
        
        Args:
            run_id: The ID of the run.
        
        Returns:
            The run data, or None if the run does not exist.
        """
        return self.runs.get(run_id)
    
    def get_runs(self) -> List[Dict[str, Any]]:
        """Get all runs.
        
        Returns:
            A list of all runs.
        """
        return list(self.runs.values())
    
    def cancel_run(self, run_id: str) -> bool:
        """Cancel a run.
        
        Args:
            run_id: The ID of the run.
        
        Returns:
            True if the run was cancelled, False otherwise.
        """
        if run_id not in self.runs:
            logger.warning(f"Run {run_id} does not exist")
            return False
        
        if run_id in self.tasks:
            task = self.tasks[run_id]
            task.cancel()
            del self.tasks[run_id]
        
        self.runs[run_id]["status"] = "cancelled"
        return True

