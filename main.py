#!/usr/bin/env python3
"""
Main entry point for the Codegen CLI
This file serves as the primary executable entry point
"""

import os
import sys

# Add the current directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codegen.cli import main

if __name__ == "__main__":
    main()
