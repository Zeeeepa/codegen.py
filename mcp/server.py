#!/usr/bin/env python3
"""
Codegen API MCP Server

This is the main entry point for the Codegen API MCP Server.
It initializes and runs the server using stdio communication.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import codegen_api
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.stdio import stdio_server
from codegenapi_server import CodegenMCPServer

def main():
    """Main entry point for the MCP server"""
    # Get API token and org ID from environment variables
    api_token = os.environ.get("CODEGEN_API_TOKEN")
    org_id = os.environ.get("CODEGEN_ORG_ID")
    
    if not api_token:
        print("Error: CODEGEN_API_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    if not org_id:
        print("Error: CODEGEN_ORG_ID environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    try:
        org_id = int(org_id)
    except ValueError:
        print(f"Error: CODEGEN_ORG_ID must be an integer, got '{org_id}'", file=sys.stderr)
        sys.exit(1)
    
    # Create and run the server
    server = CodegenMCPServer(api_token=api_token, org_id=org_id)
    stdio_server(server.server)

if __name__ == "__main__":
    main()
