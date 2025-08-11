"""
Simplified Data Models for Dashboard
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class AgentRun:
    """Agent run data from Codegen API"""
    id: int
    organization_id: int
    status: Optional[str]
    prompt: Optional[str]
    result: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    web_url: Optional[str]
    cost: Optional[float] = 0.0
    tokens_used: Optional[int] = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_active(self) -> bool:
        """Check if run is currently active"""
        return self.status == "ACTIVE"
    
    @property
    def is_complete(self) -> bool:
        """Check if run is complete"""
        return self.status in ["COMPLETE", "COMPLETED"]
    
    @property
    def can_cancel(self) -> bool:
        """Check if run can be cancelled"""
        return self.status in ["ACTIVE", "PENDING"]

