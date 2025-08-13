#!/usr/bin/env python3
"""
MCP Server for AI Assistants

This module provides a simple HTTP server that implements the Model Context Protocol (MCP)
for AI assistants like Cursor and Claude Code.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler

from .server import handle_command
from .config import get_api_token, get_org_id, get_base_url

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server."""
    
    def _set_headers(self, content_type="application/json"):
        """Set response headers."""
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests."""
        self._set_headers()
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._set_headers()
            self.wfile.write(json.dumps({"error": "Empty request body"}).encode())
            return
        
        try:
            # Parse request body
            request_body = self.rfile.read(content_length).decode("utf-8")
            request_data = json.loads(request_body)
            
            # Extract command and arguments
            command = request_data.get("command")
            args = request_data.get("args", {})
            
            # Handle command
            response = handle_command(command, args)
            
            # Send response
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        
        except json.JSONDecodeError:
            self._set_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        
        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            self._set_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run_server(host: str, port: int):
    """Run the MCP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    
    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info(f"API Token: {get_api_token()[:4]}...{get_api_token()[-4:] if get_api_token() else ''}")
    logger.info(f"Org ID: {get_org_id()}")
    logger.info(f"Base URL: {get_base_url()}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Stopping MCP server")
        httpd.server_close()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Codegen MCP Server for AI Assistants")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    args = parser.parse_args()
    
    run_server(args.host, args.port)

if __name__ == "__main__":
    main()
