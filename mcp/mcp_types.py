#!/usr/bin/env python3
"""
Type definitions for the Codegen MCP Server
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ContentType(str, Enum):
    """Content type for MCP responses"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


@dataclass
class TextContent:
    """Text content for MCP responses"""
    text: str
    type: str = ContentType.TEXT
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


@dataclass
class ImageContent:
    """Image content for MCP responses"""
    url: str
    type: str = ContentType.IMAGE
    alt_text: Optional[str] = None
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


@dataclass
class FileContent:
    """File content for MCP responses"""
    url: str
    type: str = ContentType.FILE
    filename: Optional[str] = None
    annotations: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


@dataclass
class Tool:
    """Tool definition for MCP"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Optional[Dict[str, Any]] = None
    annotations: Optional[Dict[str, Any]] = None


@dataclass
class ListToolsResult:
    """Result of listing tools"""
    tools: List[Tool]
    cursor: Optional[str] = None


@dataclass
class CallToolResponse:
    """Response from a tool call"""
    content: List[Union[TextContent, ImageContent, FileContent]]


@dataclass
class CallToolRequest:
    """Request to call a tool"""
    name: str
    arguments: Dict[str, Any]
