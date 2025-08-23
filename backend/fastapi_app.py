"""
FastAPI backend for the Enhanced Codegen UI.

This module provides a FastAPI application with CORS support and
endpoints for interacting with the Codegen API.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from codegen_client import CodegenClient, CodegenApiError
from codegen_client.models.agents import AgentRun, AgentRunResponse
from codegen_client.models.multi_run import MultiRunRequest, MultiRunResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Enhanced Codegen UI API",
    description="API for the Enhanced Codegen UI",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thread pool for concurrent operations
thread_pool = ThreadPoolExecutor(max_workers=10)

# API key dependency
async def get_api_key(api_key: str = Query(..., description="Codegen API key")):
    """
    Get API key from query parameter.
    
    Args:
        api_key: Codegen API key
        
    Returns:
        str: API key
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    return api_key

# Client dependency
async def get_client(api_key: str = Depends(get_api_key)):
    """
    Get Codegen client.
    
    Args:
        api_key: Codegen API key
        
    Returns:
        CodegenClient: Codegen client
    """
    try:
        client = CodegenClient(api_key=api_key)
        return client
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating client: {str(e)}")

# Models
class AgentRunRequest(BaseModel):
    """
    Request model for creating an agent run.
    """
    
    prompt: str = Field(..., description="Prompt for the agent")
    repo_id: Optional[int] = Field(None, description="Repository ID")
    model: Optional[str] = Field(None, description="Model to use")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation")

class StarredRunRequest(BaseModel):
    """
    Request model for starring an agent run.
    """
    
    agent_run_id: str = Field(..., description="Agent run ID")
    starred: bool = Field(..., description="Starred status")

class StarredRunResponse(BaseModel):
    """
    Response model for starred agent runs.
    """
    
    agent_run_ids: List[str] = Field(..., description="Starred agent run IDs")

# Routes
@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns:
        dict: API information
    """
    return {
        "name": "Enhanced Codegen UI API",
        "version": "0.1.0",
        "description": "API for the Enhanced Codegen UI",
    }

@app.get("/health")
async def health():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {"status": "ok"}

# Organizations
@app.get("/organizations")
async def get_organizations(
    client: CodegenClient = Depends(get_client),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Number of items to return"),
):
    """
    Get organizations.
    
    Args:
        client: Codegen client
        skip: Number of items to skip
        limit: Number of items to return
        
    Returns:
        dict: Organizations
    """
    try:
        orgs = client.organizations.get_organizations(skip=skip, limit=limit)
        return orgs.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting organizations: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting organizations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Repositories
@app.get("/organizations/{org_id}/repos")
async def get_repositories(
    org_id: int = Path(..., description="Organization ID"),
    client: CodegenClient = Depends(get_client),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Number of items to return"),
):
    """
    Get repositories.
    
    Args:
        org_id: Organization ID
        client: Codegen client
        skip: Number of items to skip
        limit: Number of items to return
        
    Returns:
        dict: Repositories
    """
    try:
        repos = client.repositories.get_repositories(org_id=org_id, skip=skip, limit=limit)
        return repos.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting repositories: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent runs
@app.get("/organizations/{org_id}/agent/runs")
async def get_agent_runs(
    org_id: int = Path(..., description="Organization ID"),
    client: CodegenClient = Depends(get_client),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Number of items to return"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
):
    """
    Get agent runs.
    
    Args:
        org_id: Organization ID
        client: Codegen client
        skip: Number of items to skip
        limit: Number of items to return
        user_id: Filter by user ID
        
    Returns:
        dict: Agent runs
    """
    try:
        runs = client.agents.list_agent_runs(
            org_id=org_id, 
            skip=skip, 
            limit=limit,
            user_id=user_id,
        )
        return runs.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting agent runs: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting agent runs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}/agent/run/{agent_run_id}")
async def get_agent_run(
    org_id: int = Path(..., description="Organization ID"),
    agent_run_id: str = Path(..., description="Agent run ID"),
    client: CodegenClient = Depends(get_client),
):
    """
    Get agent run.
    
    Args:
        org_id: Organization ID
        agent_run_id: Agent run ID
        client: Codegen client
        
    Returns:
        dict: Agent run
    """
    try:
        run = client.agents.get_agent_run(org_id=org_id, agent_run_id=agent_run_id)
        return run.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting agent run: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting agent run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/organizations/{org_id}/agent/run")
async def create_agent_run(
    request: AgentRunRequest,
    org_id: int = Path(..., description="Organization ID"),
    client: CodegenClient = Depends(get_client),
):
    """
    Create agent run.
    
    Args:
        request: Agent run request
        org_id: Organization ID
        client: Codegen client
        
    Returns:
        dict: Created agent run
    """
    try:
        data = {
            "prompt": request.prompt,
            "temperature": request.temperature,
        }
        
        if request.repo_id is not None:
            data["repo_id"] = request.repo_id
            
        if request.model is not None:
            data["model"] = request.model
            
        if request.metadata is not None:
            data["metadata"] = request.metadata
            
        run = client.agents.create_agent_run(org_id=org_id, **data)
        return run.dict()
    except CodegenApiError as e:
        logger.error(f"Error creating agent run: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating agent run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/organizations/{org_id}/agent/run/{agent_run_id}/resume")
async def resume_agent_run(
    org_id: int = Path(..., description="Organization ID"),
    agent_run_id: str = Path(..., description="Agent run ID"),
    client: CodegenClient = Depends(get_client),
):
    """
    Resume agent run.
    
    Args:
        org_id: Organization ID
        agent_run_id: Agent run ID
        client: Codegen client
        
    Returns:
        dict: Resumed agent run
    """
    try:
        run = client.agents.resume_agent_run(org_id=org_id, agent_run_id=agent_run_id)
        return run.dict()
    except CodegenApiError as e:
        logger.error(f"Error resuming agent run: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming agent run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}/agent/run/{agent_run_id}/logs")
async def get_agent_run_logs(
    org_id: int = Path(..., description="Organization ID"),
    agent_run_id: str = Path(..., description="Agent run ID"),
    client: CodegenClient = Depends(get_client),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Number of items to return"),
):
    """
    Get agent run logs.
    
    Args:
        org_id: Organization ID
        agent_run_id: Agent run ID
        client: Codegen client
        skip: Number of items to skip
        limit: Number of items to return
        
    Returns:
        dict: Agent run logs
    """
    try:
        logs = client.agents.get_agent_run_logs(
            org_id=org_id, 
            agent_run_id=agent_run_id,
            skip=skip,
            limit=limit,
        )
        return logs.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting agent run logs: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting agent run logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}/agent/run/{agent_run_id}/logs/stream")
async def stream_agent_run_logs(
    org_id: int = Path(..., description="Organization ID"),
    agent_run_id: str = Path(..., description="Agent run ID"),
    client: CodegenClient = Depends(get_client),
    poll_interval: float = Query(2.0, description="Polling interval in seconds"),
):
    """
    Stream agent run logs.
    
    Args:
        org_id: Organization ID
        agent_run_id: Agent run ID
        client: Codegen client
        poll_interval: Polling interval in seconds
        
    Returns:
        StreamingResponse: Streaming response with agent run logs
    """
    async def log_generator():
        """Generate log events."""
        last_log_id = None
        run_complete = False
        
        while not run_complete:
            try:
                # Get agent run status
                run = client.agents.get_agent_run(org_id=org_id, agent_run_id=agent_run_id)
                
                # Check if run is complete
                if run.status in ["completed", "failed", "cancelled"]:
                    run_complete = True
                
                # Get logs since last log
                logs_response = client.agents.get_agent_run_logs(
                    org_id=org_id,
                    agent_run_id=agent_run_id,
                    limit=100,
                )
                
                logs = logs_response.logs
                
                # Filter logs since last log
                if last_log_id and logs:
                    for i, log in enumerate(logs):
                        if log.id == last_log_id:
                            logs = logs[i+1:]
                            break
                
                # Update last log ID
                if logs:
                    last_log_id = logs[-1].id
                
                # Yield logs
                for log in logs:
                    yield f"data: {log.json()}\n\n"
                
                # If run is complete, yield end event
                if run_complete:
                    yield f"data: {{'event': 'end', 'status': '{run.status}'}}\n\n"
                    break
                
                # Wait for next poll
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error streaming logs: {str(e)}")
                yield f"data: {{'event': 'error', 'message': '{str(e)}'}}\n\n"
                break
    
    return StreamingResponse(
        log_generator(),
        media_type="text/event-stream",
    )

# Multi-run agent
@app.post("/organizations/{org_id}/multi-run")
async def create_multi_run(
    request: MultiRunRequest,
    org_id: int = Path(..., description="Organization ID"),
    client: CodegenClient = Depends(get_client),
    background_tasks: BackgroundTasks = None,
):
    """
    Create multi-run agent.
    
    Args:
        request: Multi-run request
        org_id: Organization ID
        client: Codegen client
        background_tasks: Background tasks
        
    Returns:
        dict: Multi-run response
    """
    try:
        result = client.multi_run_agent.create_multi_run(
            org_id=org_id,
            prompt=request.prompt,
            concurrency=request.concurrency,
            repo_id=request.repo_id,
            model=request.model,
            metadata=request.metadata,
            synthesis_prompt=request.synthesis_prompt,
            temperature=request.temperature,
            synthesis_temperature=request.synthesis_temperature,
            timeout=request.timeout,
        )
        
        return result
    except CodegenApiError as e:
        logger.error(f"Error creating multi-run: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating multi-run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Starred runs
@app.get("/starred-runs")
async def get_starred_runs(
    client: CodegenClient = Depends(get_client),
):
    """
    Get starred agent runs.
    
    Args:
        client: Codegen client
        
    Returns:
        StarredRunResponse: Starred agent runs
    """
    # In a real implementation, this would be stored in a database
    # For now, we'll use a simple in-memory store
    return StarredRunResponse(agent_run_ids=[])

@app.post("/starred-runs")
async def update_starred_run(
    request: StarredRunRequest,
    client: CodegenClient = Depends(get_client),
):
    """
    Update starred agent run.
    
    Args:
        request: Starred run request
        client: Codegen client
        
    Returns:
        StarredRunResponse: Updated starred agent runs
    """
    # In a real implementation, this would be stored in a database
    # For now, we'll use a simple in-memory store
    return StarredRunResponse(agent_run_ids=[request.agent_run_id] if request.starred else [])

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

