"""
Unified Codegen API Backend with FastAPI
Complete agent run management with official SDK compatibility
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from threading import Lock
from pathlib import Path

# Core imports
import requests
from dotenv import load_dotenv

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Depends, Query, Path as PathParam, Body, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI dependencies not available. Install with: pip install fastapi uvicorn")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Application configuration"""
    API_TOKEN = os.getenv("CODEGEN_API_TOKEN", "")
    ORG_ID = os.getenv("CODEGEN_ORG_ID", "")
    BASE_URL = os.getenv("CODEGEN_BASE_URL", "https://api.codegen.com/v1")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.API_TOKEN:
            raise ValueError("CODEGEN_API_TOKEN environment variable is required")
        if not cls.ORG_ID:
            raise ValueError("CODEGEN_ORG_ID environment variable is required")
        return True

# ============================================================================
# OFFICIAL SDK IMPLEMENTATION
# ============================================================================

class AgentTask:
    """Represents a running or completed agent task."""
    
    def __init__(self, task_data: Dict[str, Any], client: 'CodegenClient'):
        """Initialize an AgentTask."""
        self.id = task_data.get('id')
        self.org_id = task_data.get('org_id') or task_data.get('organization_id')
        self.status = task_data.get('status')
        self.result = task_data.get('result')
        self.web_url = task_data.get('web_url')
        self.created_at = task_data.get('created_at')
        self.prompt = task_data.get('prompt')
        self.metadata = task_data.get('metadata', {})
        self._client = client
        self._raw_data = task_data
    
    def refresh(self) -> None:
        """Refreshes the task status from the API."""
        if not self.id:
            return
        
        try:
            updated_data = self._client.get_agent_run(self.org_id, self.id)
            self.status = updated_data.get('status', self.status)
            self.result = updated_data.get('result', self.result)
            self.web_url = updated_data.get('web_url', self.web_url)
            self._raw_data = updated_data
        except Exception as e:
            logger.warning(f"Failed to refresh task status: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            'id': self.id,
            'org_id': self.org_id,
            'status': self.status,
            'result': self.result,
            'web_url': self.web_url,
            'created_at': self.created_at,
            'prompt': self.prompt,
            'metadata': self.metadata
        }


class CodegenClient:
    """Unified Codegen API client"""
    
    def __init__(self, api_token: str = None, org_id: str = None, base_url: str = None):
        """Initialize the client"""
        self.api_token = api_token or Config.API_TOKEN
        self.org_id = org_id or Config.ORG_ID
        self.base_url = base_url or Config.BASE_URL
        
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        })
        
        self.current_task: Optional[AgentTask] = None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {e}")
            raise HTTPException(status_code=500, detail=f"API request failed: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            # Simple user info call as health check
            user = self.get_current_user()
            return {"status": "healthy", "user_id": user.get("id")}
        except:
            return {"status": "unhealthy"}
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        return self._make_request("GET", "/users/me")
    
    def create_agent_run(self, prompt: str, images: List[str] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new agent run"""
        payload = {
            "prompt": prompt,
            "images": images or [],
            "metadata": metadata or {}
        }
        
        result = self._make_request("POST", f"/organizations/{self.org_id}/agent/run", json=payload)
        task = AgentTask(result, self)
        self.current_task = task
        return result
    
    def get_agent_run(self, agent_run_id: int) -> Dict[str, Any]:
        """Get agent run details"""
        return self._make_request("GET", f"/organizations/{self.org_id}/agent/run/{agent_run_id}")
    
    def list_agent_runs(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List agent runs"""
        params = {"limit": limit, "offset": offset}
        return self._make_request("GET", f"/organizations/{self.org_id}/agent/runs", params=params)
    
    def get_agent_run_logs(self, agent_run_id: int, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """Get agent run logs"""
        params = {"skip": skip, "limit": limit}
        return self._make_request("GET", f"/organizations/{self.org_id}/agent/run/{agent_run_id}/logs", params=params)
    
    def resume_agent_run(self, agent_run_id: int, prompt: str, images: List[str] = None) -> Dict[str, Any]:
        """Resume an agent run"""
        payload = {
            "prompt": prompt,
            "images": images or []
        }
        return self._make_request("POST", f"/organizations/{self.org_id}/agent/run/{agent_run_id}/resume", json=payload)
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get status of current task"""
        if self.current_task:
            self.current_task.refresh()
            return self.current_task.to_dict()
        return None
    
    def run(self, prompt: str, **kwargs) -> AgentTask:
        """Create and return an agent task (official SDK compatibility)"""
        result = self.create_agent_run(prompt, **kwargs)
        return AgentTask(result, self)


# Global client instance
_client_instance = None
_client_lock = Lock()

def get_client() -> CodegenClient:
    """Get or create the global client instance"""
    global _client_instance
    with _client_lock:
        if _client_instance is None:
            Config.validate()
            _client_instance = CodegenClient()
        return _client_instance

# ============================================================================
# FASTAPI MODELS
# ============================================================================

if FASTAPI_AVAILABLE:
    class CreateAgentRunRequest(BaseModel):
        prompt: str = Field(..., description="The instruction for the agent to execute")
        images: Optional[List[str]] = Field(None, description="List of base64 encoded data URIs")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary JSON metadata")

    class ResumeAgentRunRequest(BaseModel):
        prompt: str = Field(..., description="Additional instruction for the agent")
        images: Optional[List[str]] = Field(None, description="List of base64 encoded data URIs")

    class AgentRunCard(BaseModel):
        """UI-optimized agent run data for cards/lists"""
        id: int
        status: str
        prompt: str
        created_at: Optional[str]
        web_url: Optional[str]
        result_preview: Optional[str] = Field(None, description="First 200 characters of result")
        metadata: Optional[Dict[str, Any]]
        
        @classmethod
        def from_api_response(cls, data: Dict[str, Any]) -> 'AgentRunCard':
            """Create from API response data"""
            result_preview = None
            if data.get('result'):
                result_preview = data['result'][:200] + "..." if len(data['result']) > 200 else data['result']
            
            return cls(
                id=data['id'],
                status=data['status'],
                prompt=data.get('prompt', ''),
                created_at=data.get('created_at'),
                web_url=data.get('web_url'),
                result_preview=result_preview,
                metadata=data.get('metadata', {})
            )

    class AgentRunDetail(BaseModel):
        """Complete agent run details"""
        id: int
        organization_id: int
        status: str
        result: Optional[str]
        created_at: Optional[str]
        web_url: Optional[str]
        source_type: Optional[str]
        github_pull_requests: Optional[List[Dict[str, Any]]]
        metadata: Optional[Dict[str, Any]]

    class AgentRunLog(BaseModel):
        """Agent run log entry"""
        agent_run_id: int
        created_at: str
        message_type: str
        thought: Optional[str]
        tool_name: Optional[str]
        tool_input: Optional[Dict[str, Any]]
        tool_output: Optional[Dict[str, Any]]
        observation: Optional[Union[Dict[str, Any], str]]

    class AgentRunLogsResponse(BaseModel):
        """Paginated logs response"""
        id: int
        organization_id: int
        status: str
        created_at: Optional[str]
        web_url: Optional[str]
        result: Optional[str]
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

    class HealthCheck(BaseModel):
        """Health check response"""
        status: str
        timestamp: str
        version: str = "1.0.0"
        config: Dict[str, Any]

    class UserInfo(BaseModel):
        """User information"""
        id: int
        email: str
        name: Optional[str]

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Codegen Agent Run Management API",
        description="Complete FastAPI backend for Codegen agent run management with UI dashboard",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ========================================================================
    # API ENDPOINTS
    # ========================================================================

    @app.get("/health", response_model=HealthCheck)
    async def health_check():
        """Health check endpoint"""
        try:
            client = get_client()
            health = client.health_check()
            return HealthCheck(
                status=health.get("status", "healthy"),
                timestamp=datetime.now().isoformat(),
                config={
                    "org_id": Config.ORG_ID,
                    "base_url": Config.BASE_URL,
                    "has_token": bool(Config.API_TOKEN)
                }
            )
        except Exception as e:
            return HealthCheck(
                status="unhealthy",
                timestamp=datetime.now().isoformat(),
                config={"error": str(e)}
            )

    @app.get("/users/me", response_model=UserInfo)
    async def get_current_user():
        """Get current user information"""
        try:
            client = get_client()
            user = client.get_current_user()
            return UserInfo(
                id=user['id'],
                email=user['email'],
                name=user.get('name')
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/agent_runs", response_model=AgentRunDetail)
    async def create_agent_run(request: CreateAgentRunRequest):
        """Create a new agent run"""
        try:
            client = get_client()
            run = client.create_agent_run(
                prompt=request.prompt,
                images=request.images,
                metadata=request.metadata
            )
            return AgentRunDetail(**run)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/create_agent_run/{mode}/{query}", response_model=AgentRunDetail)
    async def create_agent_run_with_path(
        mode: str = PathParam(..., description="Mode for the agent run"),
        query: str = PathParam(..., description="Query/prompt for the agent"),
        request: Optional[CreateAgentRunRequest] = None
    ):
        """Create a new agent run with mode and query in path"""
        try:
            client = get_client()
            
            prompt = f"Mode: {mode}\nQuery: {query}"
            if request and request.prompt:
                prompt += f"\nAdditional instructions: {request.prompt}"
            
            metadata = request.metadata if request else {}
            metadata.update({"mode": mode, "original_query": query})
            
            run = client.create_agent_run(
                prompt=prompt,
                images=request.images if request else None,
                metadata=metadata
            )
            return AgentRunDetail(**run)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs/{agent_run_id}", response_model=AgentRunDetail)
    async def get_agent_run(agent_run_id: int = PathParam(..., description="ID of the agent run")):
        """Get detailed information about a specific agent run"""
        try:
            client = get_client()
            run = client.get_agent_run(agent_run_id)
            return AgentRunDetail(**run)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs", response_model=PaginatedAgentRuns)
    async def list_agent_runs(
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Number of items per page")
    ):
        """List agent runs with pagination"""
        try:
            client = get_client()
            offset = (page - 1) * limit
            runs = client.list_agent_runs(limit=limit, offset=offset)
            
            cards = [AgentRunCard.from_api_response(run) for run in runs['items']]
            
            return PaginatedAgentRuns(
                items=cards,
                total=runs['total'],
                page=page,
                limit=limit,
                has_next=offset + limit < runs['total'],
                has_prev=page > 1
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/agent_runs/{agent_run_id}/logs", response_model=AgentRunLogsResponse)
    async def get_agent_run_logs(
        agent_run_id: int = PathParam(..., description="ID of the agent run"),
        skip: int = Query(0, ge=0, description="Number of logs to skip"),
        limit: int = Query(100, ge=1, le=100, description="Maximum number of logs to return")
    ):
        """Get logs for a specific agent run"""
        try:
            client = get_client()
            logs_response = client.get_agent_run_logs(agent_run_id, skip=skip, limit=limit)
            
            logs = [AgentRunLog(**log) for log in logs_response['logs']]
            
            return AgentRunLogsResponse(
                id=logs_response['id'],
                organization_id=logs_response['organization_id'],
                status=logs_response['status'],
                created_at=logs_response.get('created_at'),
                web_url=logs_response.get('web_url'),
                result=logs_response.get('result'),
                logs=logs,
                total_logs=logs_response['total_logs'],
                page=logs_response['page'],
                size=logs_response['size'],
                pages=logs_response['pages']
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/agent_runs/{agent_run_id}/resume", response_model=AgentRunDetail)
    async def resume_agent_run(
        agent_run_id: int = PathParam(..., description="ID of the agent run to resume"),
        request: ResumeAgentRunRequest = Body(...)
    ):
        """Resume an agent run"""
        try:
            client = get_client()
            run = client.resume_agent_run(
                agent_run_id=agent_run_id,
                prompt=request.prompt,
                images=request.images
            )
            return AgentRunDetail(**run)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/resume_agent_run/{agent_run_id}/{query}", response_model=AgentRunDetail)
    async def resume_agent_run_with_path(
        agent_run_id: int = PathParam(..., description="ID of the agent run to resume"),
        query: str = PathParam(..., description="Additional query/prompt"),
        request: Optional[ResumeAgentRunRequest] = None
    ):
        """Resume an agent run with query in path"""
        try:
            client = get_client()
            
            prompt = query
            if request and request.prompt:
                prompt += f"\nAdditional instructions: {request.prompt}"
            
            run = client.resume_agent_run(
                agent_run_id=agent_run_id,
                prompt=prompt,
                images=request.images if request else None
            )
            return AgentRunDetail(**run)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/status")
    async def get_current_task_status():
        """Get status of current task"""
        try:
            client = get_client()
            status = client.get_status()
            if status:
                return status
            else:
                return {"message": "No current task"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Run the FastAPI server"""
        uvicorn.run(
            "api:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to run the server"""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI dependencies not installed")
        print("📦 Install with: pip install fastapi uvicorn python-dotenv")
        return
    
    print("🚀 Starting Codegen Agent Run Management API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Alternative docs: http://localhost:8000/redoc")
    print("🏥 Health check: http://localhost:8000/health")
    
    try:
        Config.validate()
        print(f"✅ Configuration valid - Org ID: {Config.ORG_ID}")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Create a .env file with:")
        print("   CODEGEN_API_TOKEN=your_token_here")
        print("   CODEGEN_ORG_ID=your_org_id_here")
        return
    
    run_server(reload=True)

if __name__ == "__main__":
    main()
