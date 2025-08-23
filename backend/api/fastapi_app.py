"""
FastAPI application for the Codegen API.

This module provides a FastAPI application for the Codegen API.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from backend.core import ClientConfig

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

