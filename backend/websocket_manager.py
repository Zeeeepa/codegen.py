"""
WebSocket manager for the Enhanced Codegen UI.

This module provides WebSocket functionality for real-time updates.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Set, Any, Optional, Callable

from fastapi import WebSocket, WebSocketDisconnect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket connection manager.
    
    This class manages WebSocket connections and provides methods for
    sending messages to connected clients.
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_groups: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket) -> str:
        """
        Connect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
            
        Returns:
            str: Connection ID
        """
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        return connection_id
        
    def disconnect(self, connection_id: str):
        """
        Disconnect a WebSocket client.
        
        Args:
            connection_id: Connection ID
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
        # Remove from all groups
        for group in self.connection_groups.values():
            if connection_id in group:
                group.remove(connection_id)
                
    def add_to_group(self, connection_id: str, group: str):
        """
        Add a connection to a group.
        
        Args:
            connection_id: Connection ID
            group: Group name
        """
        if group not in self.connection_groups:
            self.connection_groups[group] = set()
            
        self.connection_groups[group].add(connection_id)
        
    def remove_from_group(self, connection_id: str, group: str):
        """
        Remove a connection from a group.
        
        Args:
            connection_id: Connection ID
            group: Group name
        """
        if group in self.connection_groups and connection_id in self.connection_groups[group]:
            self.connection_groups[group].remove(connection_id)
            
    async def send_personal_message(self, message: Any, connection_id: str):
        """
        Send a message to a specific connection.
        
        Args:
            message: Message to send
            connection_id: Connection ID
        """
        if connection_id not in self.active_connections:
            return
            
        websocket = self.active_connections[connection_id]
        
        if isinstance(message, str):
            await websocket.send_text(message)
        elif isinstance(message, bytes):
            await websocket.send_bytes(message)
        else:
            await websocket.send_json(message)
            
    async def broadcast(self, message: Any):
        """
        Broadcast a message to all connections.
        
        Args:
            message: Message to broadcast
        """
        for connection_id in list(self.active_connections.keys()):
            try:
                await self.send_personal_message(message, connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {str(e)}")
                self.disconnect(connection_id)
                
    async def broadcast_to_group(self, message: Any, group: str):
        """
        Broadcast a message to a group.
        
        Args:
            message: Message to broadcast
            group: Group name
        """
        if group not in self.connection_groups:
            return
            
        for connection_id in list(self.connection_groups[group]):
            try:
                await self.send_personal_message(message, connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id} in group {group}: {str(e)}")
                self.disconnect(connection_id)
                
    async def broadcast_to_groups(self, message: Any, groups: List[str]):
        """
        Broadcast a message to multiple groups.
        
        Args:
            message: Message to broadcast
            groups: List of group names
        """
        for group in groups:
            await self.broadcast_to_group(message, group)


class MultiRunStatusManager:
    """
    Multi-run status manager.
    
    This class manages multi-run status updates and provides methods for
    sending updates to connected clients.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize the multi-run status manager.
        
        Args:
            connection_manager: WebSocket connection manager
        """
        self.connection_manager = connection_manager
        self.multi_run_statuses: Dict[str, Dict[str, Any]] = {}
        
    def update_status(self, multi_run_id: str, status: Dict[str, Any]):
        """
        Update multi-run status.
        
        Args:
            multi_run_id: Multi-run ID
            status: Status update
        """
        self.multi_run_statuses[multi_run_id] = status
        
        # Broadcast status update
        asyncio.create_task(
            self.connection_manager.broadcast_to_group(
                {
                    "type": "multi_run_status",
                    "multi_run_id": multi_run_id,
                    "status": status
                },
                f"multi_run_{multi_run_id}"
            )
        )
        
    def get_status(self, multi_run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get multi-run status.
        
        Args:
            multi_run_id: Multi-run ID
            
        Returns:
            Optional[Dict[str, Any]]: Status or None if not found
        """
        return self.multi_run_statuses.get(multi_run_id)
        
    def register_connection(self, connection_id: str, multi_run_id: str):
        """
        Register a connection for multi-run status updates.
        
        Args:
            connection_id: Connection ID
            multi_run_id: Multi-run ID
        """
        self.connection_manager.add_to_group(connection_id, f"multi_run_{multi_run_id}")
        
        # Send current status if available
        status = self.get_status(multi_run_id)
        if status:
            asyncio.create_task(
                self.connection_manager.send_personal_message(
                    {
                        "type": "multi_run_status",
                        "multi_run_id": multi_run_id,
                        "status": status
                    },
                    connection_id
                )
            )
            
    def unregister_connection(self, connection_id: str, multi_run_id: str):
        """
        Unregister a connection from multi-run status updates.
        
        Args:
            connection_id: Connection ID
            multi_run_id: Multi-run ID
        """
        self.connection_manager.remove_from_group(connection_id, f"multi_run_{multi_run_id}")


# Create global instances
connection_manager = ConnectionManager()
multi_run_status_manager = MultiRunStatusManager(connection_manager)

