"""
Main entry point for codegenapi CLI
"""

import sys
from .cli import main

def cli_main():
    """Entry point for console script"""
    sys.exit(main())

