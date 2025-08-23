"""
WebSocket manager for the Codegen API.

This module provides a manager for handling WebSocket connections.
"""

import logging
from typing import Dict, List, Any, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manager for handling WebSocket connections."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a WebSocket client.
        
        Args:
            websocket: The WebSocket connection.
            client_id: The ID of the client.
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
    
    async def disconnect(self, client_id: str):
        """Disconnect a WebSocket client.
        
        Args:
            client_id: The ID of the client.
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    async def send_message(self, client_id: str, message: Any):
        """Send a message to a specific client.
        
        Args:
            client_id: The ID of the client.
            message: The message to send.
        """
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} not found")
            return
        
        websocket = self.active_connections[client_id]
        await websocket.send_json(message)
    
    async def broadcast(self, message: Any):
        """Broadcast a message to all connected clients.
        
        Args:
            message: The message to broadcast.
        """
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {e}")
                await self.disconnect(client_id)

