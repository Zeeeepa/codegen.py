#!/usr/bin/env python3
"""
Mock API Service for Dashboard Development
Provides realistic mock data and behavior for dashboard development and testing.
This can be easily replaced with real API calls once endpoints are confirmed.
"""

import json
import time
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class AgentRunStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class SourceType(Enum):
    LOCAL = "LOCAL"
    SLACK = "SLACK"
    GITHUB = "GITHUB"
    GITHUB_CHECK_SUITE = "GITHUB_CHECK_SUITE"
    LINEAR = "LINEAR"
    API = "API"
    CHAT = "CHAT"
    JIRA = "JIRA"

@dataclass
class MockUser:
    id: int
    github_username: str
    email: str
    name: str
    avatar_url: str
    created_at: str

@dataclass
class MockOrganization:
    id: int
    name: str
    slug: str
    created_at: str
    member_count: int

@dataclass
class MockAgentRun:
    id: int
    organization_id: int
    user_id: int
    status: str
    prompt: str
    result: Optional[str]
    created_at: str
    updated_at: str
    completed_at: Optional[str]
    web_url: str
    source_type: str
    metadata: Dict[str, Any]
    progress: int
    estimated_completion: Optional[str]
    cost: float
    tokens_used: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None

@dataclass
class MockLogEntry:
    id: int
    agent_run_id: int
    timestamp: str
    level: str
    message: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class MockProject:
    id: int
    name: str
    description: str
    organization_id: int
    created_at: str
    run_count: int
    status: str

class MockCodegenAPI:
    """Mock API service that simulates Codegen API behavior"""
    
    def __init__(self, org_id: int = 323):
        self.org_id = org_id
        self.authenticated = True
        self.current_user = MockUser(
            id=1,
            github_username="testuser",
            email="test@example.com",
            name="Test User",
            avatar_url="https://github.com/testuser.png",
            created_at=datetime.now().isoformat()
        )
        
        # Initialize mock data
        self._init_mock_data()
        
        # Background thread to simulate run progress
        self._running = True
        self._progress_thread = threading.Thread(target=self._simulate_progress, daemon=True)
        self._progress_thread.start()
    
    def _init_mock_data(self):
        """Initialize mock data for testing"""
        
        # Mock organizations
        self.organizations = [
            MockOrganization(
                id=323,
                name="Test Organization",
                slug="test-org",
                created_at=datetime.now().isoformat(),
                member_count=5
            )
        ]
        
        # Mock projects
        self.projects = [
            MockProject(
                id=1,
                name="Web Development",
                description="Frontend and backend web development tasks",
                organization_id=323,
                created_at=(datetime.now() - timedelta(days=30)).isoformat(),
                run_count=45,
                status="active"
            ),
            MockProject(
                id=2,
                name="Data Analysis",
                description="Data processing and analysis workflows",
                organization_id=323,
                created_at=(datetime.now() - timedelta(days=20)).isoformat(),
                run_count=23,
                status="active"
            ),
            MockProject(
                id=3,
                name="API Development",
                description="REST API and microservices development",
                organization_id=323,
                created_at=(datetime.now() - timedelta(days=15)).isoformat(),
                run_count=12,
                status="active"
            )
        ]
        
        # Mock agent runs with realistic data
        self.agent_runs = []
        self._generate_mock_runs(50)  # Generate 50 mock runs
        
        # Mock logs
        self.logs = {}
        for run in self.agent_runs:
            self.logs[run.id] = self._generate_mock_logs(run.id)
    
    def _generate_mock_runs(self, count: int):
        """Generate realistic mock agent runs"""
        
        statuses = [
            (AgentRunStatus.COMPLETED, 0.4),
            (AgentRunStatus.RUNNING, 0.2),
            (AgentRunStatus.PENDING, 0.1),
            (AgentRunStatus.FAILED, 0.15),
            (AgentRunStatus.CANCELLED, 0.1),
            (AgentRunStatus.PAUSED, 0.05)
        ]
        
        prompts = [
            "Create a REST API for user authentication",
            "Build a React dashboard with charts",
            "Implement database migration scripts",
            "Add unit tests for payment processing",
            "Create Docker configuration for deployment",
            "Build a data visualization component",
            "Implement OAuth2 authentication",
            "Create API documentation with Swagger",
            "Build a file upload system",
            "Implement real-time notifications",
            "Create a search functionality",
            "Build a user management interface",
            "Implement caching layer with Redis",
            "Create automated testing pipeline",
            "Build a monitoring dashboard"
        ]
        
        source_types = [SourceType.API, SourceType.SLACK, SourceType.GITHUB, SourceType.LINEAR]
        
        for i in range(count):
            # Weighted random status selection
            status_weights = [w for _, w in statuses]
            status = random.choices([s.value for s, _ in statuses], weights=status_weights)[0]
            
            created_time = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Determine completion time based on status
            completed_at = None
            if status in [AgentRunStatus.COMPLETED.value, AgentRunStatus.FAILED.value, AgentRunStatus.CANCELLED.value]:
                completed_at = (created_time + timedelta(
                    minutes=random.randint(5, 120)
                )).isoformat()
            
            # Progress based on status
            if status == AgentRunStatus.COMPLETED.value:
                progress = 100
            elif status == AgentRunStatus.FAILED.value or status == AgentRunStatus.CANCELLED.value:
                progress = random.randint(10, 90)
            elif status == AgentRunStatus.RUNNING.value:
                progress = random.randint(20, 80)
            else:
                progress = random.randint(0, 20)
            
            # Select project
            project = random.choice(self.projects)
            
            run = MockAgentRun(
                id=1000 + i,
                organization_id=self.org_id,
                user_id=self.current_user.id,
                status=status,
                prompt=random.choice(prompts),
                result=self._generate_result(status) if status == AgentRunStatus.COMPLETED.value else None,
                created_at=created_time.isoformat(),
                updated_at=(created_time + timedelta(minutes=random.randint(1, 60))).isoformat(),
                completed_at=completed_at,
                web_url=f"https://codegen.com/runs/{1000 + i}",
                source_type=random.choice(source_types).value,
                metadata={
                    "priority": random.choice(["low", "medium", "high"]),
                    "tags": random.sample(["frontend", "backend", "api", "database", "testing", "deployment"], k=random.randint(1, 3)),
                    "estimated_duration": random.randint(10, 180),
                    "complexity": random.choice(["simple", "medium", "complex"])
                },
                progress=progress,
                estimated_completion=(datetime.now() + timedelta(minutes=random.randint(5, 60))).isoformat() if status == AgentRunStatus.RUNNING.value else None,
                cost=round(random.uniform(0.05, 2.50), 2),
                tokens_used=random.randint(100, 5000),
                project_id=project.id,
                project_name=project.name
            )
            
            self.agent_runs.append(run)
        
        # Sort by created_at descending (newest first)
        self.agent_runs.sort(key=lambda x: x.created_at, reverse=True)
    
    def _generate_result(self, status: str) -> str:
        """Generate realistic result text"""
        if status == AgentRunStatus.COMPLETED.value:
            results = [
                "Successfully created REST API with authentication endpoints. Added JWT token validation and user registration/login functionality.",
                "Built React dashboard with interactive charts using Chart.js. Implemented real-time data updates and responsive design.",
                "Created database migration scripts for user table updates. Added indexes for improved query performance.",
                "Implemented comprehensive unit tests with 95% code coverage. Added integration tests for payment workflows.",
                "Created Docker configuration with multi-stage builds. Optimized image size and added health checks."
            ]
            return random.choice(results)
        return None
    
    def _generate_mock_logs(self, run_id: int) -> List[MockLogEntry]:
        """Generate realistic log entries for a run"""
        logs = []
        base_time = datetime.now() - timedelta(minutes=random.randint(10, 120))
        
        log_messages = [
            ("INFO", "Starting agent run execution"),
            ("INFO", "Analyzing prompt and requirements"),
            ("INFO", "Setting up development environment"),
            ("INFO", "Installing required dependencies"),
            ("INFO", "Generating code structure"),
            ("INFO", "Implementing core functionality"),
            ("INFO", "Running tests and validation"),
            ("INFO", "Optimizing and refactoring code"),
            ("INFO", "Generating documentation"),
            ("INFO", "Finalizing implementation")
        ]
        
        for i, (level, message) in enumerate(log_messages):
            if random.random() < 0.8:  # 80% chance to include each log
                logs.append(MockLogEntry(
                    id=i + 1,
                    agent_run_id=run_id,
                    timestamp=(base_time + timedelta(minutes=i * 2)).isoformat(),
                    level=level,
                    message=message,
                    details={"step": i + 1, "total_steps": len(log_messages)}
                ))
        
        return logs
    
    def _simulate_progress(self):
        """Background thread to simulate progress on running tasks"""
        while self._running:
            time.sleep(5)  # Update every 5 seconds
            
            for run in self.agent_runs:
                if run.status == AgentRunStatus.RUNNING.value:
                    # Simulate progress
                    if run.progress < 100:
                        run.progress = min(100, run.progress + random.randint(1, 5))
                        run.updated_at = datetime.now().isoformat()
                        
                        # Chance to complete
                        if run.progress >= 100 or random.random() < 0.05:  # 5% chance to complete each cycle
                            run.status = AgentRunStatus.COMPLETED.value
                            run.progress = 100
                            run.completed_at = datetime.now().isoformat()
                            run.result = self._generate_result(AgentRunStatus.COMPLETED.value)
                
                elif run.status == AgentRunStatus.PENDING.value:
                    # Chance to start running
                    if random.random() < 0.1:  # 10% chance to start each cycle
                        run.status = AgentRunStatus.RUNNING.value
                        run.progress = random.randint(5, 15)
                        run.updated_at = datetime.now().isoformat()
    
    # API Methods
    
    def get_current_user(self) -> MockUser:
        """Get current authenticated user"""
        return self.current_user
    
    def get_organizations(self, limit: int = 10) -> List[MockOrganization]:
        """Get user's organizations"""
        return self.organizations[:limit]
    
    def list_agent_runs(self, org_id: int, limit: int = 10, skip: int = 0, 
                       status: Optional[str] = None, user_id: Optional[int] = None,
                       project_id: Optional[int] = None) -> Dict[str, Any]:
        """List agent runs with filtering"""
        
        filtered_runs = self.agent_runs
        
        # Apply filters
        if status:
            filtered_runs = [r for r in filtered_runs if r.status == status]
        if user_id:
            filtered_runs = [r for r in filtered_runs if r.user_id == user_id]
        if project_id:
            filtered_runs = [r for r in filtered_runs if r.project_id == project_id]
        
        # Apply pagination
        total = len(filtered_runs)
        items = filtered_runs[skip:skip + limit]
        
        return {
            "items": [asdict(run) for run in items],
            "total": total,
            "page": (skip // limit) + 1,
            "size": len(items),
            "pages": (total + limit - 1) // limit
        }
    
    def get_agent_run(self, org_id: int, run_id: int) -> Optional[MockAgentRun]:
        """Get specific agent run"""
        for run in self.agent_runs:
            if run.id == run_id:
                return run
        return None
    
    def create_agent_run(self, org_id: int, prompt: str, metadata: Optional[Dict] = None,
                        images: Optional[List[str]] = None, project_id: Optional[int] = None) -> MockAgentRun:
        """Create new agent run"""
        
        # Select project
        project = None
        if project_id:
            project = next((p for p in self.projects if p.id == project_id), None)
        if not project:
            project = random.choice(self.projects)
        
        new_run = MockAgentRun(
            id=max([r.id for r in self.agent_runs]) + 1 if self.agent_runs else 1001,
            organization_id=org_id,
            user_id=self.current_user.id,
            status=AgentRunStatus.PENDING.value,
            prompt=prompt,
            result=None,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            completed_at=None,
            web_url=f"https://codegen.com/runs/{max([r.id for r in self.agent_runs]) + 1 if self.agent_runs else 1001}",
            source_type=SourceType.API.value,
            metadata=metadata or {},
            progress=0,
            estimated_completion=(datetime.now() + timedelta(minutes=random.randint(10, 60))).isoformat(),
            cost=0.0,
            tokens_used=0,
            project_id=project.id,
            project_name=project.name
        )
        
        self.agent_runs.insert(0, new_run)  # Add to beginning (newest first)
        self.logs[new_run.id] = []  # Initialize empty logs
        
        return new_run
    
    def cancel_agent_run(self, org_id: int, run_id: int) -> bool:
        """Cancel an agent run"""
        run = self.get_agent_run(org_id, run_id)
        if run and run.status in [AgentRunStatus.PENDING.value, AgentRunStatus.RUNNING.value, AgentRunStatus.PAUSED.value]:
            run.status = AgentRunStatus.CANCELLED.value
            run.updated_at = datetime.now().isoformat()
            run.completed_at = datetime.now().isoformat()
            return True
        return False
    
    def resume_agent_run(self, org_id: int, run_id: int, prompt: str) -> bool:
        """Resume a paused agent run"""
        run = self.get_agent_run(org_id, run_id)
        if run and run.status == AgentRunStatus.PAUSED.value:
            run.status = AgentRunStatus.RUNNING.value
            run.updated_at = datetime.now().isoformat()
            # Add resume prompt to metadata
            if 'resume_prompts' not in run.metadata:
                run.metadata['resume_prompts'] = []
            run.metadata['resume_prompts'].append({
                'prompt': prompt,
                'timestamp': datetime.now().isoformat()
            })
            return True
        return False
    
    def pause_agent_run(self, org_id: int, run_id: int) -> bool:
        """Pause a running agent run"""
        run = self.get_agent_run(org_id, run_id)
        if run and run.status == AgentRunStatus.RUNNING.value:
            run.status = AgentRunStatus.PAUSED.value
            run.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def get_agent_run_logs(self, org_id: int, run_id: int, limit: int = 100) -> List[MockLogEntry]:
        """Get logs for an agent run"""
        return self.logs.get(run_id, [])[-limit:]
    
    def get_projects(self, org_id: int, limit: int = 10) -> List[MockProject]:
        """Get projects for organization"""
        return self.projects[:limit]
    
    def get_run_statistics(self, org_id: int, days: int = 30) -> Dict[str, Any]:
        """Get run statistics for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_runs = [r for r in self.agent_runs 
                      if datetime.fromisoformat(r.created_at.replace('Z', '+00:00').replace('+00:00', '')) > cutoff_date]
        
        status_counts = {}
        for status in AgentRunStatus:
            status_counts[status.value] = len([r for r in recent_runs if r.status == status.value])
        
        total_cost = sum(r.cost for r in recent_runs)
        total_tokens = sum(r.tokens_used for r in recent_runs)
        
        return {
            "total_runs": len(recent_runs),
            "status_breakdown": status_counts,
            "total_cost": round(total_cost, 2),
            "total_tokens": total_tokens,
            "average_cost_per_run": round(total_cost / len(recent_runs), 2) if recent_runs else 0,
            "success_rate": round((status_counts.get("completed", 0) / len(recent_runs)) * 100, 1) if recent_runs else 0,
            "period_days": days
        }
    
    def search_runs(self, org_id: int, query: str, limit: int = 10) -> List[MockAgentRun]:
        """Search agent runs by prompt content"""
        query_lower = query.lower()
        matching_runs = [
            r for r in self.agent_runs 
            if query_lower in r.prompt.lower() or 
               query_lower in (r.result or "").lower() or
               any(query_lower in str(v).lower() for v in r.metadata.values())
        ]
        return matching_runs[:limit]
    
    def bulk_cancel_runs(self, org_id: int, run_ids: List[int]) -> Dict[str, List[int]]:
        """Cancel multiple runs"""
        cancelled = []
        failed = []
        
        for run_id in run_ids:
            if self.cancel_agent_run(org_id, run_id):
                cancelled.append(run_id)
            else:
                failed.append(run_id)
        
        return {"cancelled": cancelled, "failed": failed}
    
    def close(self):
        """Clean up resources"""
        self._running = False

# Global instance for easy access
mock_api = MockCodegenAPI()

def get_mock_api() -> MockCodegenAPI:
    """Get the global mock API instance"""
    return mock_api

