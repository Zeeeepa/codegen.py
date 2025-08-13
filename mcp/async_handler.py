"""
Async handler for managing long-running agent operations
"""

import time
import logging
from threading import Thread
from queue import Queue, Empty
from typing import Dict, Any, Optional, Callable, TypedDict, cast

# Import from the same directory
from codegen_client import CodegenClient
from state_manager import StateManager

logger = logging.getLogger(__name__)

class TaskDict(TypedDict, total=False):
    """Type definition for task dictionary"""
    type: str
    prompt: str
    orchestrator_id: Optional[str]
    metadata: Dict[str, Any]
    callback: Optional[Callable[..., Any]]
    agent_run_id: str

class AsyncHandler:
    """
    Handles async agent operations with orchestrator tracking
    """
    
    def __init__(self, client: CodegenClient, state_manager: StateManager):
        self.client = client
        self.state_manager = state_manager
        self.poll_interval = 5.0  # seconds
        self.running = False
        self.worker_thread: Optional[Thread] = None
        self.task_queue: Queue[TaskDict] = Queue()
    
    def start(self) -> None:
        """Start the async handler"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("Async handler started")
    
    def stop(self) -> None:
        """Stop the async handler"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=10)
            logger.info("Async handler stopped")
    
    def _worker_loop(self) -> None:
        """Main worker loop for processing async tasks"""
        while self.running:
            try:
                # Process any queued tasks
                try:
                    task = self.task_queue.get(block=False)
                    self._process_task(task)
                    self.task_queue.task_done()
                except Empty:
                    pass
                
                # Check for completed agent runs
                self._check_pending_runs()
                
                # Sleep before next iteration
                time.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in async worker loop: {e}")
    
    def _process_task(self, task: TaskDict) -> None:
        """Process a queued task"""
        task_type = task.get("type")
        
        if task_type == "create_run":
            self._handle_create_run(task)
        elif task_type == "resume_run":
            self._handle_resume_run(task)
        else:
            logger.warning(f"Unknown task type: {task_type}")
    
    def _handle_create_run(self, task: TaskDict) -> None:
        """Handle creating a new agent run"""
        try:
            prompt = task.get("prompt", "")
            orchestrator_id = task.get("orchestrator_id")
            metadata = task.get("metadata", {})
            
            # Create the agent run
            result = self.client.create_agent_run(
                prompt=prompt,
                metadata=metadata,
                orchestrator_id=orchestrator_id
            )
            
            run_id = result.get("id")
            if not run_id:
                logger.error("Failed to get run ID from create_agent_run response")
                return
            
            # Register the run with the state manager
            self.state_manager.register_run(
                run_id=str(run_id),
                orchestrator_id=orchestrator_id,
                metadata=metadata
            )
            
            # If this run has an orchestrator, add it as a child
            if orchestrator_id:
                self.state_manager.add_child_to_orchestrator(
                    orchestrator_id=orchestrator_id,
                    child_run_id=str(run_id)
                )
            
            logger.info(f"Created agent run {run_id} with orchestrator {orchestrator_id}")
            
            # Store the callback if provided
            if "callback" in task and task.get("callback") is not None:
                callback_metadata = metadata.copy()
                # We can't store the callback function directly in metadata
                # Just note that a callback exists
                callback_metadata["has_callback"] = True
                self.state_manager.update_run_status(
                    run_id=str(run_id),
                    status="running",
                    result=None
                )
        
        except Exception as e:
            logger.error(f"Error creating agent run: {e}")
    
    def _handle_resume_run(self, task: TaskDict) -> None:
        """Handle resuming an agent run"""
        try:
            agent_run_id = task.get("agent_run_id", "")
            prompt = task.get("prompt", "")
            
            # Resume the agent run
            self.client.resume_agent_run(
                agent_run_id=agent_run_id,
                prompt=prompt
            )
            
            logger.info(f"Resumed agent run {agent_run_id}")
        
        except Exception as e:
            logger.error(f"Error resuming agent run: {e}")
    
    def _check_pending_runs(self) -> None:
        """Check for completed agent runs and handle orchestrator notifications"""
        try:
            # Get all runs
            runs = self.state_manager.get_all_runs()
            
            for run_id, run in runs.items():
                # Skip runs that are not in running state
                if run.get("status") != "running":
                    continue
                
                try:
                    # Check the current status
                    result = self.client.get_agent_run(agent_run_id=run_id)
                    status = result.get("status")
                    
                    # If the run is complete, handle the result
                    if status in ["completed", "failed", "cancelled"]:
                        self._handle_completed_run(run_id, result)
                
                except Exception as e:
                    logger.error(f"Error checking run {run_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error checking pending runs: {e}")
    
    def _handle_completed_run(self, run_id: str, result: Dict[str, Any]) -> None:
        """Handle a completed agent run"""
        try:
            # Update the run status
            self.state_manager.update_run_status(
                run_id=run_id,
                status=result.get("status", ""),
                result=result.get("result")
            )
            
            # Get the orchestrator ID
            run = self.state_manager.get_run(run_id)
            if not run:
                logger.error(f"Run {run_id} not found in state manager")
                return
            
            orchestrator_id = run.get("orchestrator_id")
            if not orchestrator_id:
                logger.info(f"Run {run_id} completed with no orchestrator")
                return
            
            # Check if the orchestrator is still running
            is_orchestrator_active = self.client.check_orchestrator_status(orchestrator_id)
            
            if is_orchestrator_active:
                logger.info(f"Orchestrator {orchestrator_id} is active, sending result directly")
                # Orchestrator is active, no need to resume it
                # The result will be returned directly to the tool call
            else:
                logger.info(f"Orchestrator {orchestrator_id} is not active, resuming with result")
                # Orchestrator is not active, resume it with the result
                self._resume_orchestrator_with_result(orchestrator_id, run_id, result)
        
        except Exception as e:
            logger.error(f"Error handling completed run {run_id}: {e}")
    
    def _resume_orchestrator_with_result(self, orchestrator_id: str, run_id: str, result: Dict[str, Any]) -> None:
        """Resume an orchestrator with the result of a completed run"""
        try:
            # Format the result message
            result_text = result.get("result", "No result available")
            prompt = f"Agent run {run_id} completed with result: {result_text}"
            
            # Queue the resume task
            self.queue_resume_run(
                agent_run_id=orchestrator_id,
                prompt=prompt
            )
            
            logger.info(f"Queued resume for orchestrator {orchestrator_id} with result from {run_id}")
        
        except Exception as e:
            logger.error(f"Error resuming orchestrator {orchestrator_id}: {e}")
    
    def queue_create_run(
        self, 
        prompt: str, 
        orchestrator_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable[..., Any]] = None
    ) -> None:
        """Queue a task to create a new agent run"""
        task: TaskDict = {
            "type": "create_run",
            "prompt": prompt,
            "orchestrator_id": orchestrator_id,
            "metadata": metadata or {}
        }
        
        if callback:
            task["callback"] = callback
        
        self.task_queue.put(task)
    
    def queue_resume_run(
        self, 
        agent_run_id: str, 
        prompt: str
    ) -> None:
        """Queue a task to resume an agent run"""
        task: TaskDict = {
            "type": "resume_run",
            "agent_run_id": agent_run_id,
            "prompt": prompt
        }
        
        self.task_queue.put(task)
    
    def create_run_sync(
        self, 
        prompt: str, 
        orchestrator_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        wait_for_completion: bool = False,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create a new agent run synchronously"""
        try:
            # Create the agent run
            result = self.client.create_agent_run(
                prompt=prompt,
                metadata=metadata,
                orchestrator_id=orchestrator_id
            )
            
            run_id = result.get("id")
            if not run_id:
                raise ValueError("Failed to get run ID from create_agent_run response")
            
            # Register the run with the state manager
            self.state_manager.register_run(
                run_id=str(run_id),
                orchestrator_id=orchestrator_id,
                metadata=metadata
            )
            
            # If this run has an orchestrator, add it as a child
            if orchestrator_id:
                self.state_manager.add_child_to_orchestrator(
                    orchestrator_id=orchestrator_id,
                    child_run_id=str(run_id)
                )
            
            logger.info(f"Created agent run {run_id} with orchestrator {orchestrator_id}")
            
            # Wait for completion if requested
            if wait_for_completion:
                result = self.client.wait_for_completion(
                    agent_run_id=run_id,
                    timeout=timeout
                )
                
                # Update the run status
                self.state_manager.update_run_status(
                    run_id=str(run_id),
                    status=result.get("status", ""),
                    result=result.get("result")
                )
            
            return cast(Dict[str, Any], result)
        
        except Exception as e:
            logger.error(f"Error creating agent run: {e}")
            raise

