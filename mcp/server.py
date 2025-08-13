#!/usr/bin/env python3
"""
Codegen API MCP Server

This is the main entry point for the Codegen API MCP Server.
It initializes and runs the server using stdio communication.
"""

import argparse
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import codegen_api
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.stdio import stdio_server
from codegenapi_server import CodegenMCPServer

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the Codegen API MCP server")
    parser.add_argument(
        "--api-token",
        help="Codegen API token (can also be set via CODEGEN_API_TOKEN env var)",
    )
    parser.add_argument(
        "--org-id",
        help="Codegen organization ID (can also be set via CODEGEN_ORG_ID env var)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose logging",
    )
    return parser.parse_args()

def main():
    """Main entry point for the MCP server"""
    args = parse_args()
    
    # Get API token from args or environment
    api_token = args.api_token or os.environ.get("CODEGEN_API_TOKEN")
    if not api_token:
        print("Error: Codegen API token is required. Set via --api-token or CODEGEN_API_TOKEN env var", file=sys.stderr)
        sys.exit(1)
    
    # Get org ID from args or environment
    org_id = args.org_id or os.environ.get("CODEGEN_ORG_ID")
    if not org_id:
        print("Error: Codegen organization ID is required. Set via --org-id or CODEGEN_ORG_ID env var", file=sys.stderr)
        sys.exit(1)
    
    try:
        org_id = int(org_id)
    except ValueError:
        print(f"Error: Organization ID must be an integer, got '{org_id}'", file=sys.stderr)
        sys.exit(1)
    
    # Create the MCP server
    server = CodegenMCPServer(
        api_token=api_token,
        org_id=org_id,
        debug=args.debug if hasattr(args, 'debug') else False
    )
    
    # Start the server
    print(f"Starting Codegen API MCP server for organization {org_id}...", file=sys.stderr)
    asyncio.run(server.start())

if __name__ == "__main__":
    main()
