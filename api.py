#!/usr/bin/env python3
"""
Codegen FastAPI Server
======================

A single-file FastAPI server for Codegen agent management with real-time monitoring.

Usage:
    python api.py                    # Start server
    python api.py --port 8080        # Custom port
    python api.py --host 0.0.0.0     # Custom host

Features:
    • Complete agent run management (create, list, get, resume)
    • Real-time log streaming with Server-Sent Events
    • Auto-generated API documentation at /docs
    • Bearer token authentication
    • CORS support for web UIs
    • Production-ready error handling

Environment Variables:
    CODEGEN_API_TOKEN    - Your Codegen API token
    CODEGEN_ORG_ID       - Your organization ID (default: 323)
"""

import os
import sys
import json
import time
import asyncio
import argparse
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# ============================================================================
# CONFIGURATION
# ============================================================================

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Install python-dotenv for .env file support: pip install python-dotenv")

# Default configuration
DEFAULT_ORG_ID = "323"
DEFAULT_API_TOKEN = "your_api_token_here"
CODEGEN_BASE_URL = "https://api.codegen.com/v1"

# Get configuration from environment or use defaults
ORG_ID = os.getenv("CODEGEN_ORG_ID", DEFAULT_ORG_ID)
API_TOKEN = os.getenv("CODEGEN_API_TOKEN", DEFAULT_API_TOKEN)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CreateAgentRunRequest(BaseModel):
    prompt: str = Field(..., description="The instruction for the agent to execute")
    images: Optional[List[str]] = Field(None, description="List of base64 encoded data URIs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary JSON metadata")

class ResumeAgentRunRequest(BaseModel):
    prompt: str = Field(..., description="Additional instruction for the agent")
    images: Optional[List[str]] = Field(None, description="List of base64 encoded data URIs")

class AgentRunResponse(BaseModel):
    id: int
    organization_id: int
    status: str
    created_at: str
    web_url: str
    result: Optional[str] = None
    source_type: Optional[str] = None
    github_pull_requests: List[Dict[str, Any]] = []
    metadata: Optional[Dict[str, Any]] = None

class AgentRunsListResponse(BaseModel):
    items: List[AgentRunResponse]
    total: int
    page: int
    size: int
    pages: int

class AgentRunLog(BaseModel):
    agent_run_id: int
    created_at: str
    message_type: str
    thought: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    observation: Optional[Any] = None

class AgentRunLogsResponse(BaseModel):
    id: int
    organization_id: int
    status: str
    created_at: str
    web_url: str
    result: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    logs: List[AgentRunLog]
    total_logs: int
    page: int
    size: int
    pages: int

class UserResponse(BaseModel):
    id: int
    email: str
    github_username: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str

class OrganizationsListResponse(BaseModel):
    items: List[OrganizationResponse]

class HealthResponse(BaseModel):
    status: str
    response_time_seconds: float
    user_id: int
    timestamp: str
    version: str = "1.0.0"

# ============================================================================
# HTTP CLIENT
# ============================================================================

class CodegenAPIClient:
    """HTTP client for Codegen API"""
    
    def __init__(self, api_token: str, org_id: str, base_url: str = CODEGEN_BASE_URL):
        self.api_token = api_token
        self.org_id = int(org_id)
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "User-Agent": "Codegen-FastAPI-Server/1.0.0"
        }
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Codegen API"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    raise HTTPException(status_code=401, detail="Invalid API token")
                elif e.response.status_code == 403:
                    raise HTTPException(status_code=403, detail="Insufficient permissions")
                elif e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Resource not found")
                else:
                    raise HTTPException(
                        status_code=e.response.status_code,
                        detail=f"API error: {e.response.text}"
                    )
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="API request timeout")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    
    async def get_current_user(self) -> UserResponse:
        """Get current user information"""
        data = await self._request("GET", "/users/me")
        return UserResponse(**data)
    
    async def get_organizations(self) -> OrganizationsListResponse:
        """Get user's organizations"""
        data = await self._request("GET", "/organizations")
        return OrganizationsListResponse(**data)
    
    async def create_agent_run(self, request: CreateAgentRunRequest) -> AgentRunResponse:
        """Create a new agent run"""
        payload = request.dict(exclude_none=True)
        data = await self._request(
            "POST", 
            f"/organizations/{self.org_id}/agent/run",
            json=payload
        )
        return AgentRunResponse(**data)
    
    async def get_agent_run(self, agent_run_id: int) -> AgentRunResponse:
        """Get specific agent run"""
        data = await self._request(
            "GET", 
            f"/organizations/{self.org_id}/agent/run/{agent_run_id}"
        )
        return AgentRunResponse(**data)
    
    async def list_agent_runs(self, skip: int = 0, limit: int = 10) -> AgentRunsListResponse:
        """List agent runs with pagination"""
        params = {"skip": skip, "limit": limit}
        data = await self._request(
            "GET", 
            f"/organizations/{self.org_id}/agent/runs",
            params=params
        )
        
        # Calculate pagination info
        total = data.get("total_count", len(data.get("items", [])))
        page = (skip // limit) + 1
        pages = (total + limit - 1) // limit
        
        return AgentRunsListResponse(
            items=[AgentRunResponse(**item) for item in data.get("items", [])],
            total=total,
            page=page,
            size=limit,
            pages=pages
        )
    
    async def resume_agent_run(self, agent_run_id: int, request: ResumeAgentRunRequest) -> AgentRunResponse:
        """Resume an agent run"""
        payload = {
            "agent_run_id": agent_run_id,
            **request.dict(exclude_none=True)
        }
        data = await self._request(
            "POST",
            f"/organizations/{self.org_id}/agent/run/resume",
            json=payload
        )
        return AgentRunResponse(**data)
    
    async def get_agent_run_logs(self, agent_run_id: int, skip: int = 0, limit: int = 100) -> AgentRunLogsResponse:
        """Get agent run logs"""
        params = {"skip": skip, "limit": limit}
        data = await self._request(
            "GET",
            f"/alpha/organizations/{self.org_id}/agent/run/{agent_run_id}/logs",
            params=params
        )
        
        # Calculate pagination
        total_logs = data.get("total_logs", 0)
        page = (skip // limit) + 1
        pages = (total_logs + limit - 1) // limit if total_logs > 0 else 1
        
        return AgentRunLogsResponse(
            id=data["id"],
            organization_id=data["organization_id"],
            status=data["status"],
            created_at=data["created_at"],
            web_url=data["web_url"],
            result=data.get("result"),
            metadata=data.get("metadata"),
            logs=[AgentRunLog(**log) for log in data.get("logs", [])],
            total_logs=total_logs,
            page=page,
            size=limit,
            pages=pages
        )

# ============================================================================
# GLOBAL CLIENT INSTANCE
# ============================================================================

# Global client instance
api_client = CodegenAPIClient(API_TOKEN, ORG_ID)

# ============================================================================
# AUTHENTICATION
# ============================================================================

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Validate API token and return user info"""
    # Create a temporary client with the provided token
    temp_client = CodegenAPIClient(credentials.credentials, ORG_ID)
    try:
        user = await temp_client.get_current_user()
        return user
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print(f"🚀 Starting Codegen FastAPI Server...")
    print(f"📊 Organization ID: {ORG_ID}")
    print(f"🔑 API Token: {API_TOKEN[:20]}...")
    print(f"📖 API Documentation: http://localhost:8000/docs")
    print(f"🔄 Alternative docs: http://localhost:8000/redoc")
    print(f"❤️  Health check: http://localhost:8000/health")
    yield
    print("🛑 Shutting down Codegen FastAPI Server...")

# Create FastAPI app
app = FastAPI(
    title="Codegen API Server",
    description="FastAPI server for Codegen agent management with real-time monitoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check(user: UserResponse = Depends(get_current_user)):
    """Health check endpoint"""
    start_time = time.time()
    duration = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        response_time_seconds=duration,
        user_id=user.id,
        timestamp=datetime.now().isoformat()
    )

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(user: UserResponse = Depends(get_current_user)):
    """Get current user information"""
    return user

@app.get("/organizations", response_model=OrganizationsListResponse)
async def get_organizations(user: UserResponse = Depends(get_current_user)):
    """Get user's organizations"""
    temp_client = CodegenAPIClient(API_TOKEN, ORG_ID)
    return await temp_client.get_organizations()

@app.post("/agent-runs", response_model=AgentRunResponse)
async def create_agent_run(
    request: CreateAgentRunRequest,
    user: UserResponse = Depends(get_current_user)
):
    """Create a new agent run"""
    temp_client = CodegenAPIClient(API_TOKEN, ORG_ID)
    return await temp_client.create_agent_run(request)

@app.get("/agent-runs", response_model=AgentRunsListResponse)
async def list_agent_runs(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    user: UserResponse = Depends(get_current_user)
):
    """List agent runs with pagination"""
    temp_client = CodegenAPIClient(API_TOKEN, ORG_ID)
    return await temp_client.list_agent_runs(skip=skip, limit=limit)

@app.get("/agent-runs/{agent_run_id}", response_model=AgentRunResponse)
async def get_agent_run(
    agent_run_id: int,
    user: UserResponse = Depends(get_current_user)
):
    """Get specific agent run"""
    temp_client = CodegenAPIClient(API_TOKEN, ORG_ID)
    return await temp_client.get_agent_run(agent_run_id)

@app.post("/agent-runs/{agent_run_id}/resume", response_model=AgentRunResponse)
async def resume_agent_run(
    agent_run_id: int,
    request: ResumeAgentRunRequest,
    user: UserResponse = Depends(get_current_user)
):
    """Resume an agent run"""
    temp_client = CodegenAPIClient(API_TOKEN, ORG_ID)
    return await temp_client.resume_agent_run(agent_run_id, request)

@app.get("/agent-runs/{agent_run_id}/logs", response_model=AgentRunLogsResponse)
async def get_agent_run_logs(
    agent_run_id: int,
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of logs to return"),
    user: UserResponse = Depends(get_current_user)
):
    """Get agent run logs with pagination"""
    temp_client = CodegenAPIClient(API_TOKEN, ORG_ID)
    return await temp_client.get_agent_run_logs(agent_run_id, skip=skip, limit=limit)

@app.get("/agent-runs/{agent_run_id}/logs/stream")
async def stream_agent_run_logs(
    agent_run_id: int,
    user: UserResponse = Depends(get_current_user)
):
    """Stream agent run logs in real-time using Server-Sent Events"""
    
    async def generate_log_stream() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events stream of logs"""
        temp_client = CodegenAPIClient(API_TOKEN, ORG_ID)
        last_log_count = 0
        
        while True:
            try:
                # Get latest logs
                logs_response = await temp_client.get_agent_run_logs(
                    agent_run_id, 
                    skip=last_log_count, 
                    limit=100
                )
                
                # Send new logs
                for log in logs_response.logs:
                    log_data = log.dict()
                    yield f"data: {json.dumps(log_data)}\n\n"
                
                # Update counter
                last_log_count = logs_response.total_logs
                
                # Check if run is complete
                agent_run = await temp_client.get_agent_run(agent_run_id)
                if agent_run.status in ["COMPLETE", "FAILED", "CANCELLED"]:
                    yield f"data: {json.dumps({'status': 'complete', 'final_status': agent_run.status})}\n\n"
                    break
                
                # Wait before next poll
                await asyncio.sleep(2)
                
            except Exception as e:
                error_data = {"error": str(e), "timestamp": datetime.now().isoformat()}
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    return StreamingResponse(
        generate_log_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Codegen FastAPI Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Validate configuration
    if not API_TOKEN or API_TOKEN == "your_api_token_here":
        print("❌ Error: CODEGEN_API_TOKEN environment variable not set")
        print("   Set it with: export CODEGEN_API_TOKEN=your_token_here")
        sys.exit(1)
    
    if not ORG_ID:
        print("❌ Error: CODEGEN_ORG_ID environment variable not set")
        print("   Set it with: export CODEGEN_ORG_ID=your_org_id")
        sys.exit(1)
    
    # Start server
    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()
