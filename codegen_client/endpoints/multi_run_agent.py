"""
Client for the MultiRunAgent API endpoints.

This module provides functionality to run multiple agent instances concurrently
and then synthesize their outputs using a meta-agent.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union

from codegen_client.models.agents import AgentRun, AgentRunResponse
from codegen_client.exceptions import CodegenApiError


class MultiRunAgentClient:
    """
    Client for the MultiRunAgent API endpoints.

    This client provides methods for running multiple agent instances concurrently
    and synthesizing their outputs using a meta-agent.
    """

    def __init__(self, client: Any):
        """
        Initialize the MultiRunAgent API client.

        Args:
            client: The base API client
        """
        self.client = client

    async def _create_agent_run_async(
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
        # In a real implementation, this would use an async HTTP client
        loop = asyncio.get_event_loop()
        response_data = await loop.run_in_executor(
            None,
            lambda: self.client.post(
                f"/organizations/{org_id}/agent-runs",
                data=data,
            )
        )
        
        return AgentRun.parse_obj(response_data)

    async def _wait_for_agent_run_async(
        self,
        org_id: int,
        agent_run_id: str,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> AgentRun:
        """
        Wait for an agent run to complete asynchronously.

        Args:
            org_id: Organization ID
            agent_run_id: Agent run ID
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
            response_data = await loop.run_in_executor(
                None,
                lambda: self.client.get(
                    f"/organizations/{org_id}/agent-runs/{agent_run_id}",
                )
            )
            
            agent_run = AgentRun.parse_obj(response_data)
            
            if agent_run.status in ["completed", "failed", "cancelled"]:
                return agent_run
                
            if time.time() - start_time > timeout:
                raise CodegenApiError(
                    f"Timeout waiting for agent run {agent_run_id} to complete"
                )
                
            await asyncio.sleep(poll_interval)

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
    ) -> Dict[str, Any]:
        """
        Create multiple agent runs concurrently and synthesize the results.

        Args:
            org_id: Organization ID
            prompt: Prompt for the agents
            concurrency: Number of concurrent agent runs (1-20)
            repo_id: Optional repository ID
            model: Optional model to use
            metadata: Optional metadata
            synthesis_prompt: Optional custom prompt for synthesis
            temperature: Temperature for generation (0.0-1.0)
            synthesis_temperature: Temperature for synthesis (0.0-1.0)
            timeout: Maximum seconds to wait for completion

        Returns:
            Dict[str, Any]: Results containing final synthesis and all candidate outputs

        Raises:
            CodegenApiError: If the API request fails
            ValueError: If concurrency is out of range
        """
        if not 1 <= concurrency <= 20:
            raise ValueError("Concurrency must be between 1 and 20")

        # Run the async implementation in the synchronous context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._create_multi_run_async(
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
                )
            )
        finally:
            loop.close()

    async def _create_multi_run_async(
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

        Returns:
            Dict[str, Any]: Results containing final synthesis and all candidate outputs

        Raises:
            CodegenApiError: If the API request fails
        """
        # Step 1: Create multiple agent runs concurrently
        agent_run_tasks = []
        for i in range(concurrency):
            run_metadata = metadata.copy() if metadata else {}
            run_metadata["multi_run_index"] = i
            run_metadata["multi_run_total"] = concurrency
            
            task = self._create_agent_run_async(
                org_id=org_id,
                prompt=prompt,
                repo_id=repo_id,
                model=model,
                metadata=run_metadata,
                temperature=temperature,
            )
            agent_run_tasks.append(task)
            
        agent_runs = await asyncio.gather(*agent_run_tasks)
        
        # Step 2: Wait for all agent runs to complete
        wait_tasks = []
        for agent_run in agent_runs:
            task = self._wait_for_agent_run_async(
                org_id=org_id,
                agent_run_id=agent_run.id,
                timeout=timeout,
            )
            wait_tasks.append(task)
            
        completed_runs = await asyncio.gather(*wait_tasks)
        
        # Step 3: Extract outputs from completed runs
        candidate_outputs = []
        for run in completed_runs:
            if run.status == "completed" and run.output:
                candidate_outputs.append(run.output)
        
        if not candidate_outputs:
            raise CodegenApiError("All agent runs failed to produce output")
            
        # Step 4: Create a synthesis agent run
        if len(candidate_outputs) == 1:
            # If only one successful run, no need for synthesis
            return {
                "final": candidate_outputs[0],
                "candidates": candidate_outputs,
                "agent_runs": [run.dict() for run in completed_runs],
            }
            
        # Build synthesis prompt
        if not synthesis_prompt:
            synthesis_prompt = self._build_synthesis_prompt(candidate_outputs)
        
        synthesis_metadata = metadata.copy() if metadata else {}
        synthesis_metadata["multi_run_synthesis"] = True
        synthesis_metadata["multi_run_candidates"] = len(candidate_outputs)
        
        synthesis_run = await self._create_agent_run_async(
            org_id=org_id,
            prompt=synthesis_prompt,
            repo_id=repo_id,
            model=model,
            metadata=synthesis_metadata,
            temperature=synthesis_temperature,
        )
        
        # Wait for synthesis to complete
        synthesis_result = await self._wait_for_agent_run_async(
            org_id=org_id,
            agent_run_id=synthesis_run.id,
            timeout=timeout,
        )
        
        if synthesis_result.status != "completed" or not synthesis_result.output:
            raise CodegenApiError("Synthesis agent run failed to produce output")
            
        return {
            "final": synthesis_result.output,
            "candidates": candidate_outputs,
            "agent_runs": [run.dict() for run in completed_runs] + [synthesis_result.dict()],
        }
        
    def _build_synthesis_prompt(self, candidate_outputs: List[str]) -> str:
        """
        Build a prompt for synthesizing multiple candidate outputs.

        Args:
            candidate_outputs: List of candidate outputs to synthesize

        Returns:
            str: Synthesis prompt
        """
        numbered_candidates = "\n\n".join(
            f"<candidate {i+1}>\n{output}\n</candidate {i+1}>"
            for i, output in enumerate(candidate_outputs)
        )
        
        return (
            f"You are an expert editor. You have been given {len(candidate_outputs)} "
            f"candidate solutions to the same problem. Your task is to synthesize "
            f"these solutions into a single, coherent, and comprehensive solution "
            f"that combines the strengths of each candidate while eliminating any "
            f"errors or redundancies.\n\n"
            f"Here are the candidate solutions:\n\n"
            f"{numbered_candidates}\n\n"
            f"Please provide a single, unified solution that represents the best "
            f"combination of these candidates. Do not mention the candidates or "
            f"the synthesis process in your response. Be decisive and clear."
        )

