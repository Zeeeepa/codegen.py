#!/usr/bin/env python3
"""
CodegenAPI - Agent Orchestration Tool

Main entry point for the CodegenAPI agent orchestration system.
This tool enables AI agents to efficiently delegate tasks to other Codegen agents.
"""

import sys
import os

# Add the package to the path for development
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codegenapi.main import main

if __name__ == "__main__":
    sys.exit(main())

