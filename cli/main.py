#!/usr/bin/env python3
"""
Codegen CLI Main Entry Point

This module provides the main entry point for the Codegen CLI application.
"""

import sys
import signal
from typing import NoReturn

import click
from rich.console import Console
from rich.traceback import install

from .core.app import cli
from .core.errors import CLIError, handle_cli_error
from .core.logging import setup_logging


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""
    
    def signal_handler(signum: int, frame) -> NoReturn:
        """Handle interrupt signals gracefully."""
        console = Console(stderr=True)
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)  # Standard exit code for SIGINT
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """Main entry point for the CLI application."""
    # Install rich traceback handler for better error display
    install(show_locals=False, suppress=[click])
    
    # Set up signal handlers
    setup_signal_handlers()
    
    try:
        # Initialize logging (will be configured based on verbosity flags)
        setup_logging()
        
        # Run the CLI application
        cli()
        
    except CLIError as e:
        # Handle known CLI errors gracefully
        handle_cli_error(e)
        sys.exit(e.exit_code)
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        console = Console(stderr=True)
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
        
    except Exception as e:
        # Handle unexpected errors
        console = Console(stderr=True)
        console.print(f"[red]Unexpected error: {e}[/red]")
        console.print("[dim]Use --verbose for more details[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
