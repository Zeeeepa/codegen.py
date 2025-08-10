"""
FastAPI Backend for Codegen API
Comprehensive web interface for agent run management
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from threading import Lock

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, BackgroundTasks, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse, JSONResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel, Field, validator
    import uvicorn
    from sse_starlette.sse import EventSourceResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI dependencies not available. Install with: pip install fastapi uvicorn sse-starlette")

# Import the SDK
from codegen_api import CodegenClient, ClientConfig, AgentRunResponse

if FASTAPI_AVAILABLE:
    # Pydantic Models
    class CreateAgentRunRequest(BaseModel):
        prompt: str = Field(..., description="The instruction for the agent to execute")
        images: Optional[List[str]] = Field(None, description="List of base64 encoded data URIs representing images")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary JSON metadata to be stored with the agent run")
        repo_name: Optional[str] = Field(None, description="Repository name")
        branch_name: Optional[str] = Field(None, description="Branch name")

    class ResumeAgentRunRequest(BaseModel):
        agent_run_id: int = Field(..., description="The ID of the agent run to resume")
        prompt: str = Field(..., description="Additional instruction for the agent")
        images: Optional[List[str]] = Field(None, description="List of base64 encoded data URIs representing images")

    class AgentRunCard(BaseModel):
        """UI-optimized agent run data for cards/lists"""
        id: int
        status: str
        prompt: str
        created_at: Optional[datetime]
        updated_at: Optional[datetime]
        web_url: Optional[str]
        result_preview: Optional[str] = Field(None, description="First 200 characters of result")
        duration_seconds: Optional[float] = Field(None, description="Execution duration")
        metadata: Optional[Dict[str, Any]]
        repo_name: Optional[str]
        branch_name: Optional[str]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    class AgentRunDetail(BaseModel):
        """Complete agent run details"""
        id: int
        organization_id: int
        status: str
        prompt: str
        result: Optional[str]
        created_at: Optional[datetime]
        updated_at: Optional[datetime]
        web_url: Optional[str]
        metadata: Optional[Dict[str, Any]]
        repo_name: Optional[str]
        branch_name: Optional[str]
        total_logs: Optional[int]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    class AgentRunLog(BaseModel):
        """Agent run log entry"""
        agent_run_id: int
        created_at: datetime
        message_type: str
        thought: Optional[str]
        tool_name: Optional[str]
        tool_input: Optional[Dict[str, Any]]
        tool_output: Optional[Dict[str, Any]]
        observation: Optional[Union[Dict[str, Any], str]]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    class AgentRunLogsResponse(BaseModel):
        """Paginated logs response"""
        logs: List[AgentRunLog]
        total_logs: int
        page: int
        size: int
        pages: int

    class PaginatedAgentRuns(BaseModel):
        """Paginated agent runs response"""
        items: List[AgentRunCard]
        total: int
        page: int
        limit: int
        has_next: bool
        has_prev: bool

    class UserInfo(BaseModel):
        """User information"""
        id: int
        email: str
        name: Optional[str]
        github_username: Optional[str]
        created_at: Optional[datetime]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    class HealthCheck(BaseModel):
        """Health check response"""
        status: str
        timestamp: datetime
        version: str = "1.0.0"
        uptime_seconds: Optional[float]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    # Initialize FastAPI app
    app = FastAPI(
        title="Codegen API Backend",
        description="Comprehensive FastAPI backend for Codegen agent run management",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global client instance
    _client_instance = None
    _client_lock = Lock()

    def get_client() -> CodegenClient:
        """Get or create the global client instance"""
        global _client_instance
        with _client_lock:
            if _client_instance is None:
                config = ClientConfig()
                if not config.api_token:
                    raise HTTPException(
                        status_code=401,
                        detail="CODEGEN_API_TOKEN environment variable is required"
                    )
                if not config.org_id:
                    raise HTTPException(
                        status_code=401,
                        detail="CODEGEN_ORG_ID environment variable is required"
                    )
                _client_instance = CodegenClient(config)
            return _client_instance

    def get_org_id() -> int:
        """Get organization ID from environment"""
        org_id = os.getenv("CODEGEN_ORG_ID")
        if not org_id:
            raise HTTPException(
                status_code=401,
                detail="CODEGEN_ORG_ID environment variable is required"
            )
        try:
            return int(org_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="CODEGEN_ORG_ID must be a valid integer"
            )

    def convert_to_agent_run_card(run: AgentRunResponse) -> AgentRunCard:
        """Convert AgentRunResponse to UI-optimized AgentRunCard"""
        result_preview = None
        if run.result:
            result_preview = run.result[:200] + "..." if len(run.result) > 200 else run.result
        
        duration_seconds = None
        if run.created_at and run.updated_at:
            try:
                if isinstance(run.created_at, str):
                    created = datetime.fromisoformat(run.created_at.replace('Z', '+00:00'))
                else:
                    created = run.created_at
                if isinstance(run.updated_at, str):
                    updated = datetime.fromisoformat(run.updated_at.replace('Z', '+00:00'))
                else:
                    updated = run.updated_at
                duration_seconds = (updated - created).total_seconds()
            except:
                pass

        return AgentRunCard(
            id=run.id,
            status=run.status,
            prompt=run.prompt,
            created_at=run.created_at,
            updated_at=run.updated_at,
            web_url=run.web_url,
            result_preview=result_preview,
            duration_seconds=duration_seconds,
            metadata=run.metadata,
            repo_name=getattr(run, 'repo_name', None),
            branch_name=getattr(run, 'branch_name', None)
        )

    def convert_to_agent_run_detail(run: AgentRunResponse) -> AgentRunDetail:
        """Convert AgentRunResponse to detailed view"""
        return AgentRunDetail(
            id=run.id,
            organization_id=run.organization_id,
            status=run.status,
            prompt=run.prompt,
            result=run.result,
            created_at=run.created_at,
            updated_at=run.updated_at,
            web_url=run.web_url,
            metadata=run.metadata,
            repo_name=getattr(run, 'repo_name', None),
            branch_name=getattr(run, 'branch_name', None),
            total_logs=None
        )

    # ========================================================================
    # ENDPOINTS
    # ========================================================================

    @app.get("/health", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint"""
        try:
            client = get_client()
            health = client.health_check()
            return HealthCheck(
                status=health.get("status", "healthy"),
                timestamp=datetime.now(),
                uptime_seconds=health.get("response_time_seconds")
            )
        except Exception as e:
            return HealthCheck(
                status="unhealthy",
                timestamp=datetime.now()
            )

    @app.get("/users/me", response_model=UserInfo)
    async def get_current_user():
        """Get current user information"""
        try:
            client = get_client()
            user = client.get_current_user()
            return UserInfo(
                id=user.id,
                email=user.email,
                name=getattr(user, 'name', None),
                github_username=getattr(user, 'github_username', None),
                created_at=getattr(user, 'created_at', None)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/create_agent_run/{mode}/{query}", response_model=AgentRunDetail)
    async def create_agent_run_with_path(
        mode: str = Path(..., description="Mode for the agent run"),
        query: str = Path(..., description="Query/prompt for the agent"),
        request: Optional[CreateAgentRunRequest] = None
    ):
        """Create a new agent run with mode and query in path"""
        try:
            client = get_client()
            org_id = get_org_id()
            
            prompt = f"Mode: {mode}\nQuery: {query}"
            if request and request.prompt:
                prompt += f"\nAdditional instructions: {request.prompt}"
            
            images = request.images if request else None
            metadata = request.metadata if request else {}
            metadata.update({"mode": mode, "original_query": query})
            
            run = client.create_agent_run(
                org_id=org_id,
                prompt=prompt,
                images=images,
                metadata=metadata
            )
            
            return convert_to_agent_run_detail(run)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/resume_agent_run/{agent_run_id}/{query}", response_model=AgentRunDetail)
    async def resume_agent_run_with_path(
        agent_run_id: int = Path(..., description="ID of the agent run to resume"),
        query: str = Path(..., description="Additional query/prompt"),
        request: Optional[ResumeAgentRunRequest] = None
    ):
        """Resume an agent run with query in path"""
        try:
            client = get_client()
            org_id = get_org_id()
            
            prompt = query
            if request and request.prompt:
                prompt += f"\nAdditional instructions: {request.prompt}"
            
            images = request.images if request else None
            
            run = client.resume_agent_run(
                org_id=org_id,
                agent_run_id=agent_run_id,
                prompt=prompt,
                images=images
            )
            
            return convert_to_agent_run_detail(run)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs/{agent_run_id}", response_model=AgentRunDetail)
    async def get_agent_run(agent_run_id: int = Path(..., description="ID of the agent run")):
        """Get detailed information about a specific agent run"""
        try:
            client = get_client()
            org_id = get_org_id()
            
            run = client.get_agent_run(org_id, agent_run_id)
            detail = convert_to_agent_run_detail(run)
            
            try:
                logs = client.get_agent_run_logs(org_id, agent_run_id, limit=1)
                detail.total_logs = logs.total_logs
            except:
                pass
            
            return detail
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs", response_model=PaginatedAgentRuns)
    async def list_agent_runs(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
        status: Optional[str] = Query(None, description="Filter by status")
    ):
        """List agent runs with pagination and filtering"""
        try:
            client = get_client()
            org_id = get_org_id()
            
            offset = (page - 1) * limit
            runs = client.list_agent_runs(org_id, limit=limit, offset=offset)
            
            cards = [convert_to_agent_run_card(run) for run in runs.items]
            
            if status:
                cards = [card for card in cards if card.status == status]
            
            return PaginatedAgentRuns(
                items=cards,
                total=runs.total,
                page=page,
                limit=limit,
                has_next=offset + limit < runs.total,
                has_prev=page > 1
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/agent_runs/{agent_run_id}")
    async def cancel_agent_run(agent_run_id: int = Path(..., description="ID of the agent run to cancel")):
        """Cancel/stop a running agent run"""
        try:
            # Note: Actual cancellation would depend on API support
            return {"message": f"Agent run {agent_run_id} cancellation requested"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs/{agent_run_id}/logs", response_model=AgentRunLogsResponse)
    async def get_agent_run_logs(
        agent_run_id: int = Path(..., description="ID of the agent run"),
        skip: int = Query(0, ge=0, description="Number of logs to skip"),
        limit: int = Query(100, ge=1, le=100, description="Maximum number of logs to return")
    ):
        """Get logs for a specific agent run"""
        try:
            client = get_client()
            org_id = get_org_id()
            
            logs_response = client.get_agent_run_logs(org_id, agent_run_id, skip=skip, limit=limit)
            
            logs = [
                AgentRunLog(
                    agent_run_id=log.agent_run_id,
                    created_at=log.created_at,
                    message_type=log.message_type,
                    thought=log.thought,
                    tool_name=log.tool_name,
                    tool_input=log.tool_input,
                    tool_output=log.tool_output,
                    observation=log.observation
                )
                for log in logs_response.logs
            ]
            
            return AgentRunLogsResponse(
                logs=logs,
                total_logs=logs_response.total_logs,
                page=logs_response.page,
                size=logs_response.size,
                pages=logs_response.pages
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Run the FastAPI server"""
        uvicorn.run(
            "fastapi_backend:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        print("🚀 Starting Codegen FastAPI Backend...")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔧 Alternative docs: http://localhost:8000/redoc")
        print("\n💡 Set environment variables:")
        print("   export CODEGEN_API_TOKEN=your_token")
        print("   export CODEGEN_ORG_ID=your_org_id")
        run_server(reload=True)
    else:
        print("❌ FastAPI dependencies not installed")
        print("📦 Install with: pip install fastapi uvicorn sse-starlette")
