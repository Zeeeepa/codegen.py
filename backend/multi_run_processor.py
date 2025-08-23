"""
Multi-run processor for the Enhanced Codegen UI.

This module provides functionality for running multiple agent instances
concurrently and synthesizing their outputs.
"""

import asyncio
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any, Union

from codegen_client import CodegenClient, CodegenApiError
from codegen_client.models.agents import AgentRun

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class MultiRunProcessor:
    """
    Multi-run processor for running multiple agent instances concurrently.
    
    This class provides methods for running multiple agent instances concurrently
    and synthesizing their outputs using a meta-agent.
    """
    
    def __init__(self, client: CodegenClient, max_workers: int = 10):
        """
        Initialize the multi-run processor.
        
        Args:
            client: Codegen client
            max_workers: Maximum number of concurrent workers
        """
        self.client = client
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.status_listeners = {}
        
    async def create_agent_run_async(
        self,
        org_id: int,
        prompt: str,
        repo_id: Optional[int] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
    ) -> AgentRun:
        """
        Create a single agent run asynchronously.
        
        Args:
            org_id: Organization ID
            prompt: Prompt for the agent
            repo_id: Optional repository ID
            model: Optional model to use
            metadata: Optional metadata
            temperature: Temperature for generation (0.0-1.0)
            
        Returns:
            AgentRun: Created agent run
            
        Raises:
            CodegenApiError: If the API request fails
        """
        data = {
            "prompt": prompt,
            "temperature": temperature,
        }
        
        if repo_id is not None:
            data["repo_id"] = repo_id
            
        if model is not None:
            data["model"] = model
            
        if metadata is not None:
            data["metadata"] = metadata
            
        # Use the synchronous client in an async context
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            self.thread_pool,
            lambda: self.client.agents.create_agent_run(org_id=org_id, **data)
        )
        
        return response
        
    async def wait_for_agent_run_async(
        self,
        org_id: int,
        agent_run_id: str,
        run_index: int,
        total_runs: int,
        status_callback: Optional[Callable[[int, int, str], None]] = None,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> AgentRun:
        """
        Wait for an agent run to complete asynchronously.
        
        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
            run_index: Index of the run (for status reporting)
            total_runs: Total number of runs (for status reporting)
            status_callback: Optional callback for status updates
            poll_interval: Seconds between polling attempts
            timeout: Maximum seconds to wait
            
        Returns:
            AgentRun: Completed agent run
            
        Raises:
            CodegenApiError: If the API request fails or timeout occurs
        """
        start_time = time.time()
        
        while True:
            # Use the synchronous client in an async context
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.thread_pool,
                lambda: self.client.agents.get_agent_run(org_id=org_id, agent_run_id=agent_run_id)
            )
            
            # Call status callback if provided
            if status_callback:
                status_callback(run_index, total_runs, response.status)
                
            if response.status in ["completed", "failed", "cancelled"]:
                return response
                
            if time.time() - start_time > timeout:
                raise CodegenApiError(
                    f"Timeout waiting for agent run {agent_run_id} to complete"
                )
                
            await asyncio.sleep(poll_interval)
            
    def register_status_listener(self, multi_run_id: str, listener: Callable[[Dict[str, Any]], None]):
        """
        Register a status listener for a multi-run.
        
        Args:
            multi_run_id: Multi-run ID
            listener: Status listener callback
        """
        self.status_listeners[multi_run_id] = listener
        
    def unregister_status_listener(self, multi_run_id: str):
        """
        Unregister a status listener for a multi-run.
        
        Args:
            multi_run_id: Multi-run ID
        """
        if multi_run_id in self.status_listeners:
            del self.status_listeners[multi_run_id]
            
    def _update_status(self, multi_run_id: str, status: Dict[str, Any]):
        """
        Update status for a multi-run.
        
        Args:
            multi_run_id: Multi-run ID
            status: Status update
        """
        if multi_run_id in self.status_listeners:
            self.status_listeners[multi_run_id](status)
            
    async def create_multi_run_async(
        self,
        org_id: int,
        prompt: str,
        concurrency: int,
        repo_id: Optional[int] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        synthesis_prompt: Optional[str] = None,
        temperature: float = 0.7,
        synthesis_temperature: float = 0.2,
        timeout: float = 600.0,
        multi_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create multiple agent runs concurrently and synthesize the results asynchronously.
        
        Args:
            org_id: Organization ID
            prompt: Prompt for the agents
            concurrency: Number of concurrent agent runs
            repo_id: Optional repository ID
            model: Optional model to use
            metadata: Optional metadata
            synthesis_prompt: Optional custom prompt for synthesis
            temperature: Temperature for generation (0.0-1.0)
            synthesis_temperature: Temperature for synthesis (0.0-1.0)
            timeout: Maximum seconds to wait for completion
            multi_run_id: Optional multi-run ID for status updates
            
        Returns:
            Dict[str, Any]: Results containing final synthesis and all candidate outputs
            
        Raises:
            CodegenApiError: If the API request fails
            ValueError: If concurrency is out of range
        """
        if not 1 <= concurrency <= 20:
            raise ValueError("Concurrency must be between 1 and 20")
            
        # Initialize status
        if multi_run_id:
            self._update_status(multi_run_id, {
                "status": "starting",
                "completed_runs": 0,
                "total_runs": concurrency,
                "agent_runs": []
            })
            
        # Step 1: Create multiple agent runs concurrently
        agent_run_tasks = []
        for i in range(concurrency):
            run_metadata = metadata.copy() if metadata else {}
            run_metadata["multi_run_index"] = i
            run_metadata["multi_run_total"] = concurrency
            run_metadata["multi_run_id"] = multi_run_id
            
            task = self.create_agent_run_async(
                org_id=org_id,
                prompt=prompt,
                repo_id=repo_id,
                model=model,
                metadata=run_metadata,
                temperature=temperature,
            )
            agent_run_tasks.append(task)
            
        agent_runs = await asyncio.gather(*agent_run_tasks)
        
        # Update status with created runs
        if multi_run_id:
            self._update_status(multi_run_id, {
                "status": "running",
                "completed_runs": 0,
                "total_runs": concurrency,
                "agent_runs": [run.dict() for run in agent_runs]
            })
            
        # Step 2: Wait for all agent runs to complete
        wait_tasks = []
        for i, agent_run in enumerate(agent_runs):
            task = self.wait_for_agent_run_async(
                org_id=org_id,
                agent_run_id=agent_run.id,
                run_index=i,
                total_runs=concurrency,
                status_callback=lambda idx, total, status: self._update_run_status(
                    multi_run_id, idx, total, status, agent_runs
                ),
                timeout=timeout,
            )
            wait_tasks.append(task)
            
        completed_runs = await asyncio.gather(*wait_tasks)
        
        # Step 3: Extract outputs from completed runs
        candidate_outputs = []
        for run in completed_runs:
            if run.status == "completed" and run.result:
                candidate_outputs.append(run.result)
        
        if not candidate_outputs:
            raise CodegenApiError("All agent runs failed to produce output")
            
        # Step 4: Create a synthesis agent run
        if len(candidate_outputs) == 1:
            # If only one successful run, no need for synthesis
            if multi_run_id:
                self._update_status(multi_run_id, {
                    "status": "completed",
                    "completed_runs": concurrency,
                    "total_runs": concurrency,
                    "agent_runs": [run.dict() for run in completed_runs],
                    "final": candidate_outputs[0],
                    "candidates": candidate_outputs
                })
                
            return {
                "final": candidate_outputs[0],
                "candidates": candidate_outputs,
                "agent_runs": [run.dict() for run in completed_runs],
            }
            
        # Build synthesis prompt
        if not synthesis_prompt:
            synthesis_prompt = self._build_synthesis_prompt(prompt, candidate_outputs)
        
        synthesis_metadata = metadata.copy() if metadata else {}
        synthesis_metadata["multi_run_synthesis"] = True
        synthesis_metadata["multi_run_candidates"] = len(candidate_outputs)
        synthesis_metadata["multi_run_id"] = multi_run_id
        
        # Update status for synthesis
        if multi_run_id:
            self._update_status(multi_run_id, {
                "status": "synthesizing",
                "completed_runs": concurrency,
                "total_runs": concurrency + 1,  # +1 for synthesis
                "agent_runs": [run.dict() for run in completed_runs]
            })
            
        synthesis_run = await self.create_agent_run_async(
            org_id=org_id,
            prompt=synthesis_prompt,
            repo_id=repo_id,
            model=model,
            metadata=synthesis_metadata,
            temperature=synthesis_temperature,
        )
        
        # Wait for synthesis to complete
        synthesis_result = await self.wait_for_agent_run_async(
            org_id=org_id,
            agent_run_id=synthesis_run.id,
            run_index=concurrency,
            total_runs=concurrency + 1,
            status_callback=lambda idx, total, status: self._update_synthesis_status(
                multi_run_id, status, synthesis_run, completed_runs
            ),
            timeout=timeout,
        )
        
        if synthesis_result.status != "completed" or not synthesis_result.result:
            raise CodegenApiError("Synthesis agent run failed to produce output")
            
        # Final result
        result = {
            "final": synthesis_result.result,
            "candidates": candidate_outputs,
            "agent_runs": [run.dict() for run in completed_runs] + [synthesis_result.dict()],
        }
        
        # Update final status
        if multi_run_id:
            self._update_status(multi_run_id, {
                "status": "completed",
                "completed_runs": concurrency + 1,
                "total_runs": concurrency + 1,
                "agent_runs": result["agent_runs"],
                "final": result["final"],
                "candidates": result["candidates"]
            })
            
        return result
        
    def _update_run_status(
        self, 
        multi_run_id: Optional[str], 
        run_index: int, 
        total_runs: int, 
        status: str,
        agent_runs: List[AgentRun]
    ):
        """
        Update run status.
        
        Args:
            multi_run_id: Multi-run ID
            run_index: Run index
            total_runs: Total runs
            status: Run status
            agent_runs: Agent runs
        """
        if not multi_run_id:
            return
            
        # Count completed runs
        completed_runs = sum(1 for run in agent_runs if run.status in ["completed", "failed", "cancelled"])
        
        self._update_status(multi_run_id, {
            "status": "running",
            "completed_runs": completed_runs,
            "total_runs": total_runs,
            "agent_runs": [run.dict() for run in agent_runs]
        })
        
    def _update_synthesis_status(
        self,
        multi_run_id: Optional[str],
        status: str,
        synthesis_run: AgentRun,
        completed_runs: List[AgentRun]
    ):
        """
        Update synthesis status.
        
        Args:
            multi_run_id: Multi-run ID
            status: Synthesis status
            synthesis_run: Synthesis run
            completed_runs: Completed runs
        """
        if not multi_run_id:
            return
            
        self._update_status(multi_run_id, {
            "status": "synthesizing",
            "completed_runs": len(completed_runs),
            "total_runs": len(completed_runs) + 1,
            "agent_runs": [run.dict() for run in completed_runs] + [synthesis_run.dict()]
        })
        
    def _build_synthesis_prompt(self, original_prompt: str, candidate_outputs: List[str]) -> str:
        """
        Build a prompt for synthesizing multiple candidate outputs.
        
        Args:
            original_prompt: Original prompt
            candidate_outputs: List of candidate outputs to synthesize
            
        Returns:
            str: Synthesis prompt
        """
        numbered_candidates = "\n\n".join(
            f"<candidate {i+1}>\n{output}\n</candidate {i+1}>"
            for i, output in enumerate(candidate_outputs)
        )
        
        return (
            f"You are an expert editor and synthesizer. You have been given {len(candidate_outputs)} "
            f"candidate solutions to the following problem:\n\n"
            f"<original_problem>\n{original_prompt}\n</original_problem>\n\n"
            f"Your task is to synthesize these solutions into a single, coherent, and comprehensive "
            f"solution that combines the strengths of each candidate while eliminating any "
            f"errors or redundancies.\n\n"
            f"Here are the candidate solutions:\n\n"
            f"{numbered_candidates}\n\n"
            f"Please provide a single, unified solution that represents the best "
            f"combination of these candidates. Do not mention the candidates or "
            f"the synthesis process in your response. Be decisive and clear."
        )
        
    def create_multi_run(
        self,
        org_id: int,
        prompt: str,
        concurrency: int,
        repo_id: Optional[int] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        synthesis_prompt: Optional[str] = None,
        temperature: float = 0.7,
        synthesis_temperature: float = 0.2,
        timeout: float = 600.0,
        multi_run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create multiple agent runs concurrently and synthesize the results.
        
        Args:
            org_id: Organization ID
            prompt: Prompt for the agents
            concurrency: Number of concurrent agent runs
            repo_id: Optional repository ID
            model: Optional model to use
            metadata: Optional metadata
            synthesis_prompt: Optional custom prompt for synthesis
            temperature: Temperature for generation (0.0-1.0)
            synthesis_temperature: Temperature for synthesis (0.0-1.0)
            timeout: Maximum seconds to wait for completion
            multi_run_id: Optional multi-run ID for status updates
            
        Returns:
            Dict[str, Any]: Results containing final synthesis and all candidate outputs
            
        Raises:
            CodegenApiError: If the API request fails
            ValueError: If concurrency is out of range
        """
        # Run the async implementation in the synchronous context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.create_multi_run_async(
                    org_id=org_id,
                    prompt=prompt,
                    concurrency=concurrency,
                    repo_id=repo_id,
                    model=model,
                    metadata=metadata,
                    synthesis_prompt=synthesis_prompt,
                    temperature=temperature,
                    synthesis_temperature=synthesis_temperature,
                    timeout=timeout,
                    multi_run_id=multi_run_id,
                )
            )
        finally:
            loop.close()
            
    def start_multi_run_background(
        self,
        org_id: int,
        prompt: str,
        concurrency: int,
        repo_id: Optional[int] = None,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        synthesis_prompt: Optional[str] = None,
        temperature: float = 0.7,
        synthesis_temperature: float = 0.2,
        timeout: float = 600.0,
        multi_run_id: str = None,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Start a multi-run in the background.
        
        Args:
            org_id: Organization ID
            prompt: Prompt for the agents
            concurrency: Number of concurrent agent runs
            repo_id: Optional repository ID
            model: Optional model to use
            metadata: Optional metadata
            synthesis_prompt: Optional custom prompt for synthesis
            temperature: Temperature for generation (0.0-1.0)
            synthesis_temperature: Temperature for synthesis (0.0-1.0)
            timeout: Maximum seconds to wait for completion
            multi_run_id: Multi-run ID for status updates
            callback: Optional callback for result
            
        Returns:
            str: Multi-run ID
        """
        if not multi_run_id:
            multi_run_id = str(uuid.uuid4())
            
        # Register callback if provided
        if callback:
            self.register_status_listener(multi_run_id, callback)
            
        # Start background thread
        def _run_in_background():
            try:
                result = self.create_multi_run(
                    org_id=org_id,
                    prompt=prompt,
                    concurrency=concurrency,
                    repo_id=repo_id,
                    model=model,
                    metadata=metadata,
                    synthesis_prompt=synthesis_prompt,
                    temperature=temperature,
                    synthesis_temperature=synthesis_temperature,
                    timeout=timeout,
                    multi_run_id=multi_run_id,
                )
                
                # Call callback with result
                if callback:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in background multi-run: {str(e)}")
                
                # Update status with error
                self._update_status(multi_run_id, {
                    "status": "error",
                    "error": str(e)
                })
            finally:
                # Unregister listener
                self.unregister_status_listener(multi_run_id)
                
        thread = threading.Thread(target=_run_in_background)
        thread.daemon = True
        thread.start()
        
        return multi_run_id

