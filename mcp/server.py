#!/usr/bin/env python3
"""
Codegen MCP Server

This module provides a Model Context Protocol (MCP) server for the Codegen API.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, Optional, List, Tuple, Callable
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import handlers
from .handlers import (
    handle_new_command,
    handle_resume_command,
    handle_config_command,
    handle_list_command,
    handle_task_status_command
)

# Command handlers mapping
COMMAND_HANDLERS = {
    "new": handle_new_command,
    "resume": handle_resume_command,
    "config": handle_config_command,
    "list": handle_list_command,
    "task_status": handle_task_status_command
}

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
        """Handle OPTIONS requests for CORS."""
        self._set_headers()
    
    def do_POST(self):
        """Handle POST requests."""
        # Get content length
        content_length = int(self.headers.get("Content-Length", 0))
        
        # Read request body
        request_body = self.rfile.read(content_length).decode("utf-8")
        
        try:
            # Parse request JSON
            request_data = json.loads(request_body)
            
            # Log request
            logger.info(f"Received request: {json.dumps(request_data)}")
            
            # Process request
            response_data = self._process_request(request_data)
            
            # Send response
            self._set_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
            
        except json.JSONDecodeError:
            # Invalid JSON
            self._set_headers()
            error_response = {
                "status": "error",
                "error": "Invalid JSON",
                "details": "The request body is not valid JSON."
            }
            self.wfile.write(json.dumps(error_response).encode("utf-8"))
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Error processing request: {e}")
            logger.error(traceback.format_exc())
            
            self._set_headers()
            error_response = {
                "status": "error",
                "error": "Internal server error",
                "details": str(e)
            }
            self.wfile.write(json.dumps(error_response).encode("utf-8"))
    
    def _process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP request and return response."""
        # Validate request format
        if "command" not in request_data:
            return {
                "status": "error",
                "error": "Missing command",
                "details": "The 'command' field is required in the request."
            }
        
        # Get command and arguments
        command = request_data["command"]
        args = request_data.get("args", {})
        
        # Check if command is supported
        if command not in COMMAND_HANDLERS:
            return {
                "status": "error",
                "error": "Unsupported command",
                "details": f"The command '{command}' is not supported. Supported commands: {', '.join(COMMAND_HANDLERS.keys())}"
            }
        
        # Handle command
        handler = COMMAND_HANDLERS[command]
        return handler(args)


def run_server(host="localhost", port=8080):
    """Run the MCP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPRequestHandler)
    
    logger.info(f"Starting Codegen MCP server on {host}:{port}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        httpd.server_close()
        logger.info("Server closed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Codegen MCP Server")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8080, help="Server port (default: 8080)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run server
    run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()

