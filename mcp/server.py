#!/usr/bin/env python3
"""
Entry point for the Codegen MCP Server
"""

from codegenapi_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

