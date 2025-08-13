#!/usr/bin/env python3
"""
MCP Client

This module provides a client for the MCP server.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, List, Callable

from .server import handle_command

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPClient:
    """Client for the MCP server."""
    
    def __init__(self):
        """Initialize the client."""
        pass
    
    def execute(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command on the MCP server.
        
        Args:
            command: The command to execute
            args: The command arguments
            
        Returns:
            The command response
        """
        return handle_command(command, args)
    
    def new(self, query: str, repo: Optional[str] = None, branch: Optional[str] = None, 
            pr: Optional[int] = None, task: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new agent run.
        
        Args:
            query: The prompt/description for the agent run
            repo: Repository name (e.g., 'Zeeeepa/codegen.py')
            branch: Branch name
            pr: PR number
            task: Task type (e.g., 'CREATE_PLAN', 'ANALYZE')
            
        Returns:
            The command response
        """
        args = {"query": query}
        
        if repo:
            args["repo"] = repo
        
        if branch:
            args["branch"] = branch
        
        if pr:
            args["pr"] = pr
        
        if task:
            args["task"] = task
        
        return self.execute("new", args)
    
    def resume(self, agent_run_id: int, query: str, task: Optional[str] = None) -> Dict[str, Any]:
        """
        Resume an existing agent run.
        
        Args:
            agent_run_id: ID of the agent run to resume
            query: The prompt/description for the resumed run
            task: Task type (e.g., 'ANALYZE')
            
        Returns:
            The command response
        """
        args = {
            "agent_run_id": agent_run_id,
            "query": query
        }
        
        if task:
            args["task"] = task
        
        return self.execute("resume", args)
    
    def list(self, limit: int = 20, status: Optional[str] = None, repo: Optional[str] = None) -> Dict[str, Any]:
        """
        List agent runs.
        
        Args:
            limit: Maximum number of runs to return
            status: Filter by status (e.g., 'ACTIVE', 'COMPLETE', 'ERROR')
            repo: Filter by repository name
            
        Returns:
            The command response
        """
        args = {"limit": limit}
        
        if status:
            args["status"] = status
        
        if repo:
            args["repo"] = repo
        
        return self.execute("list", args)
    
    def config_set(self, key: str, value: str) -> Dict[str, Any]:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (e.g., 'api_token', 'org_id')
            value: Value to set
            
        Returns:
            The command response
        """
        args = {
            "action": "set",
            "key": key,
            "value": value
        }
        
        return self.execute("config", args)
    
    def config_get(self, key: str) -> Dict[str, Any]:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (e.g., 'api_token', 'org_id')
            
        Returns:
            The command response
        """
        args = {
            "action": "get",
            "key": key
        }
        
        return self.execute("config", args)
    
    def logs(self, agent_run_id: int, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Get logs for an agent run.
        
        Args:
            agent_run_id: ID of the agent run
            skip: Number of logs to skip
            limit: Maximum number of logs to return
            
        Returns:
            The command response
        """
        args = {
            "agent_run_id": agent_run_id,
            "skip": skip,
            "limit": limit
        }
        
        return self.execute("logs", args)
