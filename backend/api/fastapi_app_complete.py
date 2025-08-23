"""
Complete FastAPI application for the Codegen API.

This module provides a complete FastAPI application for the Codegen API.
"""

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional

from backend.core import ClientConfig
from backend.api.websocket_manager import WebSocketManager

# Create FastAPI app
app = FastAPI(
    title="Codegen API",
    description="API for the Codegen application",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create WebSocket manager
websocket_manager = WebSocketManager()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Codegen API"}

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint."""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.broadcast(f"Client {client_id}: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket_manager.disconnect(client_id)

