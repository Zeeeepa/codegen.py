"""
MCP Types for Codegen API

This module defines the data types used by the MCP server for the Codegen API.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union


class ContentType(str, Enum):
    """Content type for tool responses"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


@dataclass
class TextContent:
    """Text content for tool responses"""
    text: str
    type: str = ContentType.TEXT


@dataclass
class ImageContent:
    """Image content for tool responses"""
    url: str
    type: str = ContentType.IMAGE


@dataclass
class FileContent:
    """File content for tool responses"""
    name: str
    content: bytes
    type: str = ContentType.FILE


@dataclass
class Tool:
    """Tool definition for MCP"""
    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class ListToolsResult:
    """Result of listing tools"""
    tools: List[Tool]


@dataclass
class CallToolRequest:
    """Request to call a tool"""
    name: str
    parameters: Dict[str, Any]


@dataclass
class CallToolResponse:
    """Response from calling a tool"""
    content: List[Union[TextContent, ImageContent, FileContent]] = field(default_factory=list)

