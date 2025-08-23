#!/usr/bin/env python3
"""
Codegen Application Entry Point.

This module serves as the main entry point for the Codegen application.
It provides a unified interface to both the API and UI components.
"""

import argparse
import sys
from typing import List, Optional

import typer
from rich.console import Console

from backend import app as api_app
from backend.core import ClientConfig, ConfigPresets
from frontend import MainFrame


console = Console()
app = typer.Typer()


@app.command()
def api(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    workers: int = 1,
    log_level: str = "info",
):
    """Start the Codegen API server."""
    import uvicorn
    
    console.print("[bold green]Starting Codegen API server...[/bold green]")
    uvicorn.run(
        "backend.api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level=log_level,
    )


@app.command()
def ui():
    """Start the Codegen UI application."""
    import tkinter as tk
    
    console.print("[bold green]Starting Codegen UI application...[/bold green]")
    root = tk.Tk()
    root.title("Codegen UI")
    app = MainFrame(root)
    root.mainloop()


@app.command()
def config(
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    preset: Optional[str] = None,
):
    """Configure Codegen client settings."""
    config = ClientConfig()
    
    if preset:
        if preset.lower() == "default":
            config.load_preset(ConfigPresets.DEFAULT)
            console.print("[bold green]Loaded default configuration preset.[/bold green]")
        elif preset.lower() == "development":
            config.load_preset(ConfigPresets.DEVELOPMENT)
            console.print("[bold green]Loaded development configuration preset.[/bold green]")
        elif preset.lower() == "production":
            config.load_preset(ConfigPresets.PRODUCTION)
            console.print("[bold green]Loaded production configuration preset.[/bold green]")
        else:
            console.print(f"[bold red]Unknown preset: {preset}[/bold red]")
            return
    
    if api_key:
        config.api_key = api_key
        console.print("[bold green]API key updated.[/bold green]")
    
    if api_url:
        config.api_url = api_url
        console.print("[bold green]API URL updated.[/bold green]")
    
    config.save()
    console.print("[bold green]Configuration saved.[/bold green]")


def main(args: Optional[List[str]] = None):
    """Run the Codegen application with the given arguments."""
    if args is None:
        args = sys.argv[1:]
    
    if not args:
        # Default to UI if no arguments provided
        ui()
        return
    
    app()


if __name__ == "__main__":
    main()

