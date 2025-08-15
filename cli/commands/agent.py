"""
Agent Commands

Commands for managing and running AI agents.
"""

import click
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.errors import CLIError, translate_sdk_error, ErrorHandler
from ..core.logging import get_logger, log_cli_command
from ..utils.output import format_output, create_table
from ..utils.progress import create_progress_bar

logger = get_logger(__name__)


@click.group()
def agent_group():
    """Manage and run AI agents."""
    pass


@agent_group.command("run")
@click.argument("prompt", required=True)
@click.option(
    "--org-id", 
    type=int,
    help="Organization ID (overrides config)"
)
@click.option(
    "--wait", 
    is_flag=True,
    help="Wait for completion and show result"
)
@click.option(
    "--timeout",
    type=int,
    default=300,
    help="Timeout in seconds for waiting (default: 300)"
)
@click.option(
    "--metadata",
    multiple=True,
    help="Metadata key=value pairs (can be used multiple times)"
)
@click.option(
    "--images",
    multiple=True,
    type=click.Path(exists=True),
    help="Image files to include (can be used multiple times)"
)
@click.pass_context
def run_agent(
    ctx: click.Context,
    prompt: str,
    org_id: Optional[int],
    wait: bool,
    timeout: int,
    metadata: List[str],
    images: List[str]
):
    """
    Run an AI agent with the given prompt.
    
    PROMPT: The task description for the agent
    
    Examples:
        codegen agent run "Create a REST API for user management"
        codegen agent run "Fix the bug in auth.py" --wait
        codegen agent run "Add tests" --metadata priority=high --metadata team=backend
    """
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    # Log command execution
    log_cli_command("agent run", {
        "prompt_length": len(prompt),
        "org_id": org_id,
        "wait": wait,
        "timeout": timeout,
        "metadata_count": len(metadata),
        "images_count": len(images)
    })
    
    with ErrorHandler(verbose=config.get("log.level") == "DEBUG"):
        try:
            # Import SDK here to avoid circular imports
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from codegen_api import Agent
            
            # Parse metadata
            metadata_dict = {}
            for item in metadata:
                if "=" in item:
                    key, value = item.split("=", 1)
                    metadata_dict[key] = value
                else:
                    raise CLIError(f"Invalid metadata format: {item}. Use key=value format.")
            
            # Initialize agent
            agent_config = {
                "api_token": config.get("api.token"),
                "base_url": config.get("api.base_url"),
                "timeout": config.get("api.timeout"),
            }
            
            if org_id:
                agent_config["org_id"] = org_id
            elif config.get("api.org_id"):
                agent_config["org_id"] = config.get("api.org_id")
            
            with Agent(**agent_config) as agent:
                # Create agent run
                console.print(f"[blue]Creating agent run...[/blue]")
                
                task = agent.run(
                    prompt=prompt,
                    metadata=metadata_dict if metadata_dict else None,
                    images=list(images) if images else None
                )
                
                console.print(f"[green]✓[/green] Agent run created: [bold]{task.id}[/bold]")
                console.print(f"[dim]Web URL: {task.web_url}[/dim]")
                
                if wait:
                    console.print(f"[blue]Waiting for completion (timeout: {timeout}s)...[/blue]")
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                        transient=True
                    ) as progress:
                        progress_task = progress.add_task("Running agent...", total=None)
                        
                        try:
                            completed_task = task.wait_for_completion(timeout=timeout)
                            progress.update(progress_task, description="Completed!")
                            
                            console.print(f"[green]✓[/green] Task completed with status: [bold]{completed_task.status}[/bold]")
                            
                            if completed_task.result:
                                console.print("\n[bold]Result:[/bold]")
                                console.print(completed_task.result)
                            
                        except Exception as e:
                            progress.update(progress_task, description="Failed!")
                            if "timeout" in str(e).lower():
                                console.print(f"[yellow]⚠[/yellow] Task did not complete within {timeout} seconds")
                                console.print(f"[dim]Check status with: codegen status {task.id}[/dim]")
                            else:
                                raise translate_sdk_error(e)
                else:
                    console.print(f"[dim]Check status with: codegen status {task.id}[/dim]")
                    
        except Exception as e:
            if not isinstance(e, CLIError):
                raise translate_sdk_error(e)
            raise


@agent_group.command("list")
@click.option(
    "--org-id",
    type=int,
    help="Organization ID (overrides config)"
)
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Number of runs to show (default: 10)"
)
@click.option(
    "--status",
    type=click.Choice(["pending", "running", "completed", "failed", "cancelled"]),
    help="Filter by status"
)
@click.pass_context
def list_agents(
    ctx: click.Context,
    org_id: Optional[int],
    limit: int,
    status: Optional[str]
):
    """List recent agent runs."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("agent list", {
        "org_id": org_id,
        "limit": limit,
        "status": status
    })
    
    with ErrorHandler(verbose=config.get("log.level") == "DEBUG"):
        try:
            # Import SDK
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from codegen_api import CodegenClient, ClientConfig
            
            # Initialize client
            client_config = ClientConfig(
                api_token=config.get("api.token"),
                base_url=config.get("api.base_url"),
                timeout=config.get("api.timeout"),
            )
            
            target_org_id = org_id or config.get("api.org_id")
            if not target_org_id:
                raise CLIError(
                    "Organization ID is required",
                    suggestions=[
                        "Set org ID with --org-id option",
                        "Configure default org with 'codegen config set api.org_id YOUR_ORG_ID'",
                        "Set CODEGEN_ORG_ID environment variable"
                    ]
                )
            
            with CodegenClient(client_config) as client:
                console.print("[blue]Fetching agent runs...[/blue]")
                
                # Get agent runs (this would need to be implemented in the SDK)
                # For now, show a placeholder
                table = Table(title="Recent Agent Runs")
                table.add_column("ID", style="cyan")
                table.add_column("Status", style="green")
                table.add_column("Created", style="dim")
                table.add_column("Prompt", style="white", max_width=50)
                
                # Placeholder data - in real implementation, this would come from the API
                table.add_row("12345", "completed", "2024-01-15 10:30", "Create a REST API for user management")
                table.add_row("12346", "running", "2024-01-15 11:15", "Fix authentication bug in login system")
                table.add_row("12347", "pending", "2024-01-15 11:45", "Add unit tests for payment processing")
                
                console.print(table)
                
        except Exception as e:
            if not isinstance(e, CLIError):
                raise translate_sdk_error(e)
            raise


@agent_group.command("status")
@click.argument("run_id", required=True)
@click.option(
    "--watch",
    is_flag=True,
    help="Watch for status changes"
)
@click.option(
    "--logs",
    is_flag=True,
    help="Show execution logs"
)
@click.pass_context
def agent_status(
    ctx: click.Context,
    run_id: str,
    watch: bool,
    logs: bool
):
    """
    Check the status of an agent run.
    
    RUN_ID: The agent run ID to check
    """
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("agent status", {
        "run_id": run_id,
        "watch": watch,
        "logs": logs
    })
    
    with ErrorHandler(verbose=config.get("log.level") == "DEBUG"):
        console.print(f"[blue]Checking status for run: {run_id}[/blue]")
        
        # Placeholder implementation
        console.print(f"[green]Status:[/green] running")
        console.print(f"[green]Progress:[/green] 75% complete")
        console.print(f"[green]Started:[/green] 2024-01-15 10:30:00")
        console.print(f"[green]Web URL:[/green] https://codegen.com/runs/{run_id}")
        
        if logs:
            console.print("\n[bold]Recent Logs:[/bold]")
            console.print("[dim]2024-01-15 10:30:15[/dim] Starting code analysis...")
            console.print("[dim]2024-01-15 10:31:22[/dim] Generating API endpoints...")
            console.print("[dim]2024-01-15 10:32:45[/dim] Creating test files...")
        
        if watch:
            console.print("\n[yellow]Watching for changes... (Press Ctrl+C to stop)[/yellow]")
            # In real implementation, this would poll for updates
