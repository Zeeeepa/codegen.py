"""
Main CLI Application

This module defines the main CLI application structure using Click.
"""

import os
from typing import Optional

import click
from rich.console import Console

from .config import get_config, ConfigManager
from .logging import get_logger, set_verbosity_level


# Global console for consistent output
console = Console()
logger = get_logger(__name__)


def common_options(f):
    """Common options decorator for all commands."""
    f = click.option(
        "--config", 
        "-c",
        type=click.Path(exists=True),
        help="Path to configuration file"
    )(f)
    f = click.option(
        "--verbose", 
        "-v", 
        count=True,
        help="Increase verbosity (use -v, -vv, or -vvv)"
    )(f)
    f = click.option(
        "--quiet", 
        "-q", 
        is_flag=True,
        help="Suppress non-essential output"
    )(f)
    f = click.option(
        "--output-format",
        type=click.Choice(["json", "yaml", "table", "text"]),
        default="table",
        help="Output format"
    )(f)
    return f


@click.group()
@click.version_option(version="0.1.0", prog_name="codegen")
@click.option(
    "--api-token",
    envvar="CODEGEN_API_TOKEN",
    help="Codegen API token (can also be set via CODEGEN_API_TOKEN env var)"
)
@click.option(
    "--org-id",
    envvar="CODEGEN_ORG_ID", 
    type=int,
    help="Organization ID (can also be set via CODEGEN_ORG_ID env var)"
)
@click.option(
    "--base-url",
    envvar="CODEGEN_BASE_URL",
    default="https://api.codegen.com",
    help="API base URL"
)
@common_options
@click.pass_context
def cli(
    ctx: click.Context,
    api_token: Optional[str],
    org_id: Optional[int],
    base_url: str,
    config: Optional[str],
    verbose: int,
    quiet: bool,
    output_format: str,
) -> None:
    """
    Codegen CLI - Intelligent Code Generation Platform
    
    A comprehensive command-line interface for the Codegen API that enables
    you to create, manage, and monitor AI-powered code generation tasks.
    
    Examples:
        codegen agent run "Create a REST API for user management"
        codegen status --watch
        codegen config set api-token YOUR_TOKEN
    
    For more information, visit: https://docs.codegen.com
    """
    # Set up logging verbosity
    if quiet:
        set_verbosity_level(0)
    else:
        set_verbosity_level(verbose)
    
    # Initialize configuration
    config_manager = ConfigManager(config_file=config)
    
    # Override config with CLI options
    if api_token:
        config_manager.set("api.token", api_token)
    if org_id:
        config_manager.set("api.org_id", org_id)
    if base_url:
        config_manager.set("api.base_url", base_url)
    
    config_manager.set("output.format", output_format)
    
    # Store config in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config"] = config_manager
    ctx.obj["console"] = console
    
    logger.debug(f"CLI initialized with verbosity level: {verbose}")
    logger.debug(f"Configuration loaded from: {config_manager.config_file or 'defaults'}")


# Import and register command groups
from ..commands.agent import agent_group
from ..commands.auth import auth_group  
from ..commands.config import config_group
from ..commands.org import org_group
from ..commands.status import status_group

cli.add_command(agent_group, name="agent")
cli.add_command(auth_group, name="auth")
cli.add_command(config_group, name="config") 
cli.add_command(org_group, name="org")
cli.add_command(status_group, name="status")


if __name__ == "__main__":
    cli()
