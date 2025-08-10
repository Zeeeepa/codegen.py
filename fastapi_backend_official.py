"""
FastAPI Backend for Codegen API - Official SDK Compatible
Supports both official SDK patterns and working API endpoints
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from threading import Lock

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI dependencies not available. Install with: pip install fastapi uvicorn")

# Import both SDK implementations
try:
    from codegen_api import CodegenClient, ClientConfig, AgentRunResponse
    COMPREHENSIVE_SDK_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_SDK_AVAILABLE = False

try:
    from codegen_official_sdk import Agent as OfficialAgent, AgentTask
    OFFICIAL_SDK_AVAILABLE = True
except ImportError:
    OFFICIAL_SDK_AVAILABLE = False

if FASTAPI_AVAILABLE:
    # Pydantic Models for API
    class CreateAgentRunRequest(BaseModel):
        prompt: str = Field(..., description="The instruction for the agent to execute")
        images: Optional[List[str]] = Field(None, description="List of base64 encoded data URIs representing images")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary JSON metadata to be stored with the agent run")
        repo_name: Optional[str] = Field(None, description="Repository name")
        branch_name: Optional[str] = Field(None, description="Branch name")

    class AgentRunCard(BaseModel):
        """UI-optimized agent run data for cards/lists"""
        id: int
        status: str
        prompt: str
        created_at: Optional[datetime]
        web_url: Optional[str]
        result_preview: Optional[str] = Field(None, description="First 200 characters of result")
        metadata: Optional[Dict[str, Any]]
        org_id: Optional[int]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    class AgentRunDetail(BaseModel):
        """Complete agent run details"""
        id: int
        org_id: int
        status: str
        prompt: str
        result: Optional[str]
        created_at: Optional[datetime]
        web_url: Optional[str]
        metadata: Optional[Dict[str, Any]]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    class UserInfo(BaseModel):
        """User information"""
        id: int
        email: str
        name: Optional[str]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    class HealthCheck(BaseModel):
        """Health check response"""
        status: str
        timestamp: datetime
        version: str = "1.0.0"
        sdk_available: Dict[str, bool]
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat() if v else None
            }

    # Initialize FastAPI app
    app = FastAPI(
        title="Codegen API Backend - Official SDK Compatible",
        description="FastAPI backend supporting both official SDK patterns and comprehensive API access",
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

    # Global instances
    _comprehensive_client = None
    _official_agent = None
    _client_lock = Lock()

    def get_comprehensive_client():
        """Get or create comprehensive SDK client"""
        global _comprehensive_client
        with _client_lock:
            if _comprehensive_client is None and COMPREHENSIVE_SDK_AVAILABLE:
                config = ClientConfig()
                if config.api_token and config.org_id:
                    _comprehensive_client = CodegenClient(config)
            return _comprehensive_client

    def get_official_agent():
        """Get or create official SDK agent"""
        global _official_agent
        with _client_lock:
            if _official_agent is None and OFFICIAL_SDK_AVAILABLE:
                token = os.getenv("CODEGEN_API_TOKEN")
                org_id = os.getenv("CODEGEN_ORG_ID")
                if token and org_id:
                    # Use working base URL instead of official one
                    _official_agent = OfficialAgent(
                        token=token,
                        org_id=org_id,
                        base_url="https://api.codegen.com/v1"
                    )
            return _official_agent

    def get_credentials():
        """Get API credentials from environment"""
        token = os.getenv("CODEGEN_API_TOKEN")
        org_id = os.getenv("CODEGEN_ORG_ID")
        
        if not token:
            raise HTTPException(
                status_code=401,
                detail="CODEGEN_API_TOKEN environment variable is required"
            )
        if not org_id:
            raise HTTPException(
                status_code=401,
                detail="CODEGEN_ORG_ID environment variable is required"
            )
        
        return token, org_id

    def convert_task_to_card(task: Any) -> AgentRunCard:
        """Convert various task types to UI card format"""
        if hasattr(task, 'to_dict'):
            # Official SDK AgentTask
            data = task.to_dict()
            return AgentRunCard(
                id=data.get('id'),
                status=data.get('status'),
                prompt=data.get('prompt', ''),
                created_at=data.get('created_at'),
                web_url=data.get('web_url'),
                result_preview=data.get('result', '')[:200] if data.get('result') else None,
                metadata={},
                org_id=data.get('org_id')
            )
        elif hasattr(task, 'id'):
            # Comprehensive SDK AgentRunResponse
            return AgentRunCard(
                id=task.id,
                status=task.status,
                prompt=getattr(task, 'prompt', ''),
                created_at=getattr(task, 'created_at', None),
                web_url=getattr(task, 'web_url', None),
                result_preview=task.result[:200] if task.result else None,
                metadata=getattr(task, 'metadata', {}),
                org_id=getattr(task, 'organization_id', None)
            )
        else:
            # Fallback for dict-like objects
            return AgentRunCard(
                id=task.get('id'),
                status=task.get('status', 'unknown'),
                prompt=task.get('prompt', ''),
                created_at=task.get('created_at'),
                web_url=task.get('web_url'),
                result_preview=task.get('result', '')[:200] if task.get('result') else None,
                metadata=task.get('metadata', {}),
                org_id=task.get('org_id') or task.get('organization_id')
            )

    # ========================================================================
    # ENDPOINTS
    # ========================================================================

    @app.get("/health", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint showing SDK availability"""
        return HealthCheck(
            status="healthy",
            timestamp=datetime.now(),
            sdk_available={
                "comprehensive_sdk": COMPREHENSIVE_SDK_AVAILABLE,
                "official_sdk": OFFICIAL_SDK_AVAILABLE,
                "fastapi": FASTAPI_AVAILABLE
            }
        )

    @app.get("/users/me", response_model=UserInfo)
    async def get_current_user():
        """Get current user information"""
        try:
            # Try comprehensive SDK first
            client = get_comprehensive_client()
            if client:
                user = client.get_current_user()
                return UserInfo(
                    id=user.id,
                    email=user.email,
                    name=getattr(user, 'name', None)
                )
            
            # Fallback: manual API call
            token, org_id = get_credentials()
            import requests
            
            response = requests.get(
                "https://api.codegen.com/v1/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            
            user_data = response.json()
            return UserInfo(
                id=user_data['id'],
                email=user_data['email'],
                name=user_data.get('name')
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/create_agent_run/{mode}/{query}", response_model=AgentRunDetail)
    async def create_agent_run_with_path(
        mode: str = Path(..., description="Mode for the agent run"),
        query: str = Path(..., description="Query/prompt for the agent"),
        request: Optional[CreateAgentRunRequest] = None
    ):
        """Create a new agent run with mode and query in path - Official SDK Compatible"""
        try:
            # Combine path parameters with request
            prompt = f"Mode: {mode}\nQuery: {query}"
            if request and request.prompt:
                prompt += f"\nAdditional instructions: {request.prompt}"
            
            # Try official SDK first
            agent = get_official_agent()
            if agent:
                task = agent.run(prompt=prompt)
                return AgentRunDetail(
                    id=task.id,
                    org_id=int(task.org_id),
                    status=task.status,
                    prompt=prompt,
                    result=task.result,
                    created_at=task.created_at,
                    web_url=task.web_url,
                    metadata={"mode": mode, "original_query": query}
                )
            
            # Fallback to comprehensive SDK
            client = get_comprehensive_client()
            if client:
                token, org_id = get_credentials()
                run = client.create_agent_run(
                    org_id=int(org_id),
                    prompt=prompt,
                    metadata={"mode": mode, "original_query": query}
                )
                return AgentRunDetail(
                    id=run.id,
                    org_id=run.organization_id,
                    status=run.status,
                    prompt=prompt,
                    result=run.result,
                    created_at=run.created_at,
                    web_url=run.web_url,
                    metadata={"mode": mode, "original_query": query}
                )
            
            raise HTTPException(status_code=500, detail="No SDK available")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/agent_runs", response_model=AgentRunDetail)
    async def create_agent_run(request: CreateAgentRunRequest):
        """Create a new agent run - Official SDK Compatible"""
        try:
            # Try official SDK first
            agent = get_official_agent()
            if agent:
                task = agent.run(prompt=request.prompt)
                return AgentRunDetail(
                    id=task.id,
                    org_id=int(task.org_id),
                    status=task.status,
                    prompt=request.prompt,
                    result=task.result,
                    created_at=task.created_at,
                    web_url=task.web_url,
                    metadata=request.metadata or {}
                )
            
            # Fallback to comprehensive SDK
            client = get_comprehensive_client()
            if client:
                token, org_id = get_credentials()
                run = client.create_agent_run(
                    org_id=int(org_id),
                    prompt=request.prompt,
                    metadata=request.metadata
                )
                return AgentRunDetail(
                    id=run.id,
                    org_id=run.organization_id,
                    status=run.status,
                    prompt=request.prompt,
                    result=run.result,
                    created_at=run.created_at,
                    web_url=run.web_url,
                    metadata=request.metadata or {}
                )
            
            raise HTTPException(status_code=500, detail="No SDK available")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs/{agent_run_id}", response_model=AgentRunDetail)
    async def get_agent_run(agent_run_id: int = Path(..., description="ID of the agent run")):
        """Get detailed information about a specific agent run"""
        try:
            # Try comprehensive SDK first for detailed info
            client = get_comprehensive_client()
            if client:
                token, org_id = get_credentials()
                run = client.get_agent_run(int(org_id), agent_run_id)
                return AgentRunDetail(
                    id=run.id,
                    org_id=run.organization_id,
                    status=run.status,
                    prompt=getattr(run, 'prompt', ''),
                    result=run.result,
                    created_at=run.created_at,
                    web_url=run.web_url,
                    metadata=getattr(run, 'metadata', {})
                )
            
            raise HTTPException(status_code=500, detail="Comprehensive SDK not available")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs")
    async def list_agent_runs(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Number of items per page")
    ):
        """List agent runs with pagination"""
        try:
            # Use comprehensive SDK for listing
            client = get_comprehensive_client()
            if client:
                token, org_id = get_credentials()
                offset = (page - 1) * limit
                runs = client.list_agent_runs(int(org_id), limit=limit, offset=offset)
                
                cards = [convert_task_to_card(run) for run in runs.items]
                
                return {
                    "items": cards,
                    "total": runs.total,
                    "page": page,
                    "limit": limit,
                    "has_next": offset + limit < runs.total,
                    "has_prev": page > 1
                }
            
            raise HTTPException(status_code=500, detail="Comprehensive SDK not available")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/status")
    async def get_current_task_status():
        """Get status of current task - Official SDK Compatible"""
        try:
            agent = get_official_agent()
            if agent:
                status = agent.get_status()
                if status:
                    return status
                else:
                    return {"message": "No current task"}
            
            raise HTTPException(status_code=500, detail="Official SDK not available")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Run the FastAPI server"""
        uvicorn.run(
            "fastapi_backend_official:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        print("🚀 Starting Official SDK Compatible FastAPI Backend...")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔧 Alternative docs: http://localhost:8000/redoc")
        print(f"✅ Comprehensive SDK: {'Available' if COMPREHENSIVE_SDK_AVAILABLE else 'Not Available'}")
        print(f"✅ Official SDK: {'Available' if OFFICIAL_SDK_AVAILABLE else 'Not Available'}")
        print("\n💡 Set environment variables:")
        print("   export CODEGEN_API_TOKEN=your_token")
        print("   export CODEGEN_ORG_ID=your_org_id")
        run_server(reload=True)
    else:
        print("❌ FastAPI dependencies not installed")
        print("📦 Install with: pip install fastapi uvicorn")
