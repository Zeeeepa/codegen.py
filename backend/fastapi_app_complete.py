"""
FastAPI backend for the Enhanced Codegen UI.

This module provides a FastAPI application with CORS support and
endpoints for interacting with the Codegen API.
"""

import os
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from concurrent.futures import ThreadPoolExecutor

from codegen_client import CodegenClient, CodegenApiError
from codegen_client.models.agents import AgentRun, AgentRunResponse
from codegen_client.models.multi_run import MultiRunRequest, MultiRunResponse
from backend.multi_run_processor import MultiRunProcessor
from backend.websocket_manager import connection_manager, multi_run_status_manager

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

class SetupCommandsRequest(BaseModel):
    """
    Request model for generating setup commands.
    """
    
    repo_id: int = Field(..., description="Repository ID")
    language: Optional[str] = Field(None, description="Programming language")
    framework: Optional[str] = Field(None, description="Framework")
    additional_info: Optional[str] = Field(None, description="Additional information")

class AnalyzeSandboxLogsRequest(BaseModel):
    """
    Request model for analyzing sandbox logs.
    """
    
    logs: str = Field(..., description="Sandbox logs to analyze")
    context: Optional[str] = Field(None, description="Context for analysis")

class BanChecksRequest(BaseModel):
    """
    Request model for banning all checks for an agent run.
    """
    
    reason: Optional[str] = Field(None, description="Reason for banning checks")

class RemoveCodegenRequest(BaseModel):
    """
    Request model for removing Codegen from PR.
    """
    
    pr_number: int = Field(..., description="PR number")
    reason: Optional[str] = Field(None, description="Reason for removal")

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

# Users endpoints
@app.get("/current-user")
async def get_current_user(
    client: CodegenClient = Depends(get_client),
):
    """
    Get current user information.
    
    Args:
        client: Codegen client
        
    Returns:
        dict: Current user information
    """
    try:
        user = client.users.get_current_user()
        return user.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}/users")
async def get_users(
    org_id: int = Path(..., description="Organization ID"),
    client: CodegenClient = Depends(get_client),
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Number of items to return"),
):
    """
    Get users in an organization.
    
    Args:
        org_id: Organization ID
        client: Codegen client
        skip: Number of items to skip
        limit: Number of items to return
        
    Returns:
        dict: Users in the organization
    """
    try:
        users = client.users.get_users(org_id=org_id, skip=skip, limit=limit)
        return users.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/organizations/{org_id}/users/{user_id}")
async def get_user(
    org_id: int = Path(..., description="Organization ID"),
    user_id: int = Path(..., description="User ID"),
    client: CodegenClient = Depends(get_client),
):
    """
    Get a specific user in an organization.
    
    Args:
        org_id: Organization ID
        user_id: User ID
        client: Codegen client
        
    Returns:
        dict: User information
    """
    try:
        user = client.users.get_user(org_id=org_id, user_id=user_id)
        return user.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

# Integrations
@app.get("/organizations/{org_id}/integrations")
async def get_integrations(
    org_id: int = Path(..., description="Organization ID"),
    client: CodegenClient = Depends(get_client),
):
    """
    Get organization integrations.
    
    Args:
        org_id: Organization ID
        client: Codegen client
        
    Returns:
        dict: Organization integrations
    """
    try:
        integrations = client.integrations.get_integrations(org_id=org_id)
        return integrations.dict()
    except CodegenApiError as e:
        logger.error(f"Error getting integrations: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting integrations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Setup commands
@app.post("/setup-commands")
async def generate_setup_commands(
    request: SetupCommandsRequest,
    client: CodegenClient = Depends(get_client),
):
    """
    Generate setup commands.
    
    Args:
        request: Setup commands request
        client: Codegen client
        
    Returns:
        dict: Generated setup commands
    """
    try:
        commands = client.setup_commands.generate_setup_commands(
            repo_id=request.repo_id,
            language=request.language,
            framework=request.framework,
            additional_info=request.additional_info,
        )
        return commands.dict()
    except CodegenApiError as e:
        logger.error(f"Error generating setup commands: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating setup commands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Sandbox
@app.post("/sandbox/analyze-logs")
async def analyze_sandbox_logs(
    request: AnalyzeSandboxLogsRequest,
    client: CodegenClient = Depends(get_client),
):
    """
    Analyze sandbox logs.
    
    Args:
        request: Analyze sandbox logs request
        client: Codegen client
        
    Returns:
        dict: Analysis results
    """
    try:
        analysis = client.sandbox.analyze_logs(
            logs=request.logs,
            context=request.context,
        )
        return analysis.dict()
    except CodegenApiError as e:
        logger.error(f"Error analyzing sandbox logs: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing sandbox logs: {str(e)}")
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

@app.post("/organizations/{org_id}/agent/run/{agent_run_id}/ban-all-checks")
async def ban_all_checks_for_agent_run(
    org_id: int = Path(..., description="Organization ID"),
    agent_run_id: str = Path(..., description="Agent run ID"),
    request: BanChecksRequest = Body(...),
    client: CodegenClient = Depends(get_client),
):
    """
    Ban all checks for agent run.
    
    Args:
        org_id: Organization ID
        agent_run_id: Agent run ID
        request: Ban checks request
        client: Codegen client
        
    Returns:
        dict: Result of banning checks
    """
    try:
        result = client.agents.ban_all_checks_for_agent_run(
            org_id=org_id, 
            agent_run_id=agent_run_id,
            reason=request.reason
        )
        return result.dict()
    except CodegenApiError as e:
        logger.error(f"Error banning checks: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error banning checks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/organizations/{org_id}/agent/run/{agent_run_id}/unban-all-checks")
async def unban_all_checks_for_agent_run(
    org_id: int = Path(..., description="Organization ID"),
    agent_run_id: str = Path(..., description="Agent run ID"),
    client: CodegenClient = Depends(get_client),
):
    """
    Unban all checks for agent run.
    
    Args:
        org_id: Organization ID
        agent_run_id: Agent run ID
        client: Codegen client
        
    Returns:
        dict: Result of unbanning checks
    """
    try:
        result = client.agents.unban_all_checks_for_agent_run(
            org_id=org_id, 
            agent_run_id=agent_run_id
        )
        return result.dict()
    except CodegenApiError as e:
        logger.error(f"Error unbanning checks: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error unbanning checks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/organizations/{org_id}/agent/run/{agent_run_id}/remove-codegen-from-pr")
async def remove_codegen_from_pr(
    org_id: int = Path(..., description="Organization ID"),
    agent_run_id: str = Path(..., description="Agent run ID"),
    request: RemoveCodegenRequest = Body(...),
    client: CodegenClient = Depends(get_client),
):
    """
    Remove Codegen from PR.
    
    Args:
        org_id: Organization ID
        agent_run_id: Agent run ID
        request: Remove Codegen request
        client: Codegen client
        
    Returns:
        dict: Result of removing Codegen
    """
    try:
        result = client.agents.remove_codegen_from_pr(
            org_id=org_id, 
            agent_run_id=agent_run_id,
            pr_number=request.pr_number,
            reason=request.reason
        )
        return result.dict()
    except CodegenApiError as e:
        logger.error(f"Error removing Codegen from PR: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error removing Codegen from PR: {str(e)}")
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
        # Create multi-run processor
        processor = MultiRunProcessor(client)
        
        # Generate multi-run ID
        multi_run_id = str(uuid.uuid4())
        
        # Start multi-run in background
        background_tasks.add_task(
            processor.start_multi_run_background,
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
            multi_run_id=multi_run_id,
            callback=lambda status: multi_run_status_manager.update_status(multi_run_id, status),
        )
        
        # Return initial response
        return {
            "multi_run_id": multi_run_id,
            "status": "started",
            "message": "Multi-run started in background",
        }
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

