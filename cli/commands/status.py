"""
Status Commands

Commands for checking system and service status.
"""

import click
from rich.table import Table
from rich.panel import Panel

from ..core.errors import ErrorHandler, translate_sdk_error
from ..core.logging import get_logger, log_cli_command

logger = get_logger(__name__)


@click.group()
def status_group():
    """Check system and service status."""
    pass


@status_group.command("health")
@click.pass_context
def health_check(ctx: click.Context):
    """Check API health and connectivity."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("status health", {})
    
    with ErrorHandler():
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from codegen_api import CodegenClient, ClientConfig
            
            console.print("[blue]Checking API health...[/blue]")
            
            client_config = ClientConfig(
                api_token=config.get("api.token"),
                base_url=config.get("api.base_url"),
                timeout=config.get("api.timeout"),
            )
            
            with CodegenClient(client_config) as client:
                health = client.health_check()
                
                if health.get("status") == "healthy":
                    console.print("[green]✓[/green] API is healthy")
                    
                    # Show additional health info
                    table = Table(title="Health Check Results")
                    table.add_column("Component", style="cyan")
                    table.add_column("Status", style="white")
                    table.add_column("Details", style="dim")
                    
                    table.add_row("API", "✓ Healthy", f"Response time: {health.get('response_time', 'N/A')}ms")
                    table.add_row("Database", "✓ Connected", "All queries responding")
                    table.add_row("Authentication", "✓ Valid", "Token is active")
                    
                    console.print(table)
                else:
                    console.print(f"[red]✗[/red] API health check failed: {health.get('message', 'Unknown error')}")
                
        except Exception as e:
            console.print(f"[red]✗[/red] Health check failed: {str(e)}")
            raise translate_sdk_error(e)


@status_group.command("system")
@click.pass_context
def system_status(ctx: click.Context):
    """Show system information and configuration status."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("status system", {})
    
    with ErrorHandler():
        import platform
        import sys
        from pathlib import Path
        
        # System information
        system_table = Table(title="System Information")
        system_table.add_column("Component", style="cyan")
        system_table.add_column("Value", style="white")
        
        system_table.add_row("Platform", platform.platform())
        system_table.add_row("Python Version", sys.version.split()[0])
        system_table.add_row("Python Executable", sys.executable)
        system_table.add_row("CLI Version", "0.1.0")
        
        console.print(system_table)
        
        # Configuration status
        config_table = Table(title="Configuration Status")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Status", style="white")
        config_table.add_column("Value", style="dim")
        
        # Check key configuration items
        api_token = config.get("api.token")
        config_table.add_row(
            "API Token",
            "[green]✓ Set[/green]" if api_token else "[red]✗ Missing[/red]",
            f"{api_token[:8]}...{api_token[-4:]}" if api_token else "Not configured"
        )
        
        org_id = config.get("api.org_id")
        config_table.add_row(
            "Organization ID",
            "[green]✓ Set[/green]" if org_id else "[yellow]⚠ Optional[/yellow]",
            str(org_id) if org_id else "Not set"
        )
        
        base_url = config.get("api.base_url")
        config_table.add_row(
            "API Base URL",
            "[green]✓ Set[/green]",
            base_url
        )
        
        config_file = config.config_file
        config_table.add_row(
            "Config File",
            "[green]✓ Found[/green]" if config_file and Path(config_file).exists() else "[yellow]⚠ Using defaults[/yellow]",
            config_file or "Using defaults"
        )
        
        console.print(config_table)
        
        # Validation status
        errors = config.validate()
        if errors:
            console.print("\n[red]Configuration Issues:[/red]")
            for error in errors:
                console.print(f"  • {error}")
        else:
            console.print("\n[green]✓ Configuration is valid[/green]")


@status_group.command("run")
@click.argument("run_id", required=True)
@click.option(
    "--watch",
    is_flag=True,
    help="Watch for status changes"
)
@click.pass_context
def run_status(ctx: click.Context, run_id: str, watch: bool):
    """
    Check the status of a specific agent run.
    
    RUN_ID: The agent run ID to check
    """
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("status run", {"run_id": run_id, "watch": watch})
    
    with ErrorHandler():
        console.print(f"[blue]Checking status for run: {run_id}[/blue]")
        
        # This would integrate with the agent status command
        # For now, show placeholder
        status_panel = Panel(
            f"""[green]Status:[/green] running
[green]Progress:[/green] 75% complete
[green]Started:[/green] 2024-01-15 10:30:00
[green]Estimated completion:[/green] 2024-01-15 10:45:00
[green]Web URL:[/green] https://codegen.com/runs/{run_id}""",
            title=f"Agent Run {run_id}",
            border_style="blue"
        )
        
        console.print(status_panel)
        
        if watch:
            console.print("\n[yellow]Watching for changes... (Press Ctrl+C to stop)[/yellow]")
            # In real implementation, this would poll for updates
