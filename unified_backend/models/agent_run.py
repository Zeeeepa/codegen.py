"""
Agent run model for the Codegen Agent API.

This module provides the agent run model for the Codegen Agent API.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class AgentRun:
    """Agent run model."""
    
    id: str
    organization_id: str
    status: str
    created_at: str
    web_url: Optional[str] = None
    result: Optional[str] = None
    summary: Optional[str] = None
    source_type: Optional[str] = None
    github_pull_requests: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    prompt: Optional[str] = None
    repo_id: Optional[str] = None
    model: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    output: Optional[str] = None
    steps: List[str] = field(default_factory=list)
    starred: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRun':
        """
        Create an agent run from a dictionary.
        
        Args:
            data: Dictionary containing agent run data
            
        Returns:
            Agent run
        """
        return cls(
            id=data.get("id", ""),
            organization_id=data.get("organization_id", ""),
            status=data.get("status", ""),
            created_at=data.get("created_at", ""),
            web_url=data.get("web_url"),
            result=data.get("result"),
            summary=data.get("summary"),
            source_type=data.get("source_type"),
            github_pull_requests=data.get("github_pull_requests", []),
            metadata=data.get("metadata", {}),
            prompt=data.get("prompt"),
            repo_id=data.get("repo_id"),
            model=data.get("model"),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at"),
            output=data.get("output"),
            steps=data.get("steps", []),
            starred=False
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent run to a dictionary.
        
        Returns:
            Dictionary representation of the agent run
        """
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "status": self.status,
            "created_at": self.created_at,
            "web_url": self.web_url,
            "result": self.result,
            "summary": self.summary,
            "source_type": self.source_type,
            "github_pull_requests": self.github_pull_requests,
            "metadata": self.metadata,
            "prompt": self.prompt,
            "repo_id": self.repo_id,
            "model": self.model,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "output": self.output,
            "steps": self.steps,
            "starred": self.starred
        }

