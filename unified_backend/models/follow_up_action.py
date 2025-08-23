"""
Follow-up action model for agent runs.

This module provides the follow-up action model for agent runs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class FollowUpAction:
    """Follow-up action model for agent runs."""
    
    id: str
    agent_run_id: str
    action_type: str
    status: str
    created_at: str
    details: Dict[str, Any] = field(default_factory=dict)
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    executed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FollowUpAction':
        """
        Create a follow-up action from a dictionary.
        
        Args:
            data: Dictionary containing follow-up action data
            
        Returns:
            Follow-up action
        """
        return cls(
            id=data.get("id", ""),
            agent_run_id=data.get("agent_run_id", ""),
            action_type=data.get("action_type", ""),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            details=data.get("details", {}),
            trigger_conditions=data.get("trigger_conditions", {}),
            executed_at=data.get("executed_at"),
            result=data.get("result")
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the follow-up action to a dictionary.
        
        Returns:
            Dictionary representation of the follow-up action
        """
        return {
            "id": self.id,
            "agent_run_id": self.agent_run_id,
            "action_type": self.action_type,
            "status": self.status,
            "created_at": self.created_at,
            "details": self.details,
            "trigger_conditions": self.trigger_conditions,
            "executed_at": self.executed_at,
            "result": self.result
        }

