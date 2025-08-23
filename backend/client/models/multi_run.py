"""
Models for the MultiRunAgent API.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from codegen_client.models.agents import AgentRun
from codegen_client.models.base import PaginatedResponse


class MultiRunRequest(BaseModel):
    """
    Request model for creating a multi-run agent.
    """
    
    prompt: str = Field(..., description="Prompt for the agent")
    concurrency: int = Field(
        ..., 
        ge=1, 
        le=20, 
        description="Number of concurrent agent runs (1-20)"
    )
    repo_id: Optional[int] = Field(
        None, 
        description="Repository ID (optional)"
    )
    model: Optional[str] = Field(
        None, 
        description="Model to use (optional)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Metadata for the agent run (optional)"
    )
    synthesis_prompt: Optional[str] = Field(
        None, 
        description="Custom prompt for synthesis (optional)"
    )
    temperature: float = Field(
        0.7, 
        ge=0.0, 
        le=1.0, 
        description="Temperature for generation (0.0-1.0)"
    )
    synthesis_temperature: float = Field(
        0.2, 
        ge=0.0, 
        le=1.0, 
        description="Temperature for synthesis (0.0-1.0)"
    )
    timeout: float = Field(
        600.0, 
        gt=0.0, 
        description="Maximum seconds to wait for completion"
    )


class MultiRunResponse(BaseModel):
    """
    Response model for a multi-run agent.
    """
    
    final: str = Field(..., description="Final synthesized output")
    candidates: List[str] = Field(..., description="All candidate outputs")
    agent_runs: List[Dict[str, Any]] = Field(..., description="Details of all agent runs")


class MultiRunListResponse(PaginatedResponse):
    """
    Paginated response model for listing multi-run agents.
    """
    
    items: List[MultiRunResponse]

