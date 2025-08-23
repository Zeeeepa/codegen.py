"""
CLI commands for the Codegen API.

This module contains command implementations for the Codegen CLI.
"""

import sys
import time
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

from backend.core.client.sync import CodegenClient
from backend.core.config.client_config import ClientConfig
from backend.core.exceptions.api_exceptions import CodegenAPIError, NotFoundError
from backend.cli.formatters import format_log_entry

# Create Typer app
app = typer.Typer(
    name="codegen-cli",
    help="A powerful command-line interface for the Codegen Agent API.",
    add_completion=False,
)

# Create console
console = Console()


def get_client() -> CodegenClient:
    """Initialize and return the CodegenClient, handling configuration and errors.
    
    Returns:
        A configured CodegenClient.
        
    Raises:
        typer.Exit: If client initialization fails.
    """
    try:
        config = ClientConfig()
        if not config.org_id:
            console.print(
                "[bold red]Error: CODEGEN_ORG_ID environment variable is not set.[/bold red]"
            )
            raise typer.Exit(code=1)
        return CodegenClient(config)
    except (ValueError, CodegenAPIError) as e:
        console.print(f"[bold red]Error initializing API client: {e}[/bold red]")
        raise typer.Exit(code=1)


def stream_logs(client: CodegenClient, run_id: int, follow: bool):
    """Handle the logic for fetching and displaying logs, with optional following.
    
    Args:
        client: The CodegenClient instance.
        run_id: The agent run ID.
        follow: Whether to follow logs in real-time.
    """
    logs_seen_count = 0
    initial_fetch_retries = 5  # Number of retries for the initial 404 error
    
    with Live(console=console, auto_refresh=False) as live:
        while True:
            try:
                org_id_int = int(client.config.org_id)
                run_with_logs = client.get_agent_run_logs(
                    org_id_int, run_id, skip=logs_seen_count, limit=100
                )
                
                new_logs = run_with_logs.logs
                if new_logs:
                    for log in new_logs:
                        console.print(format_log_entry(log.__dict__))
                    logs_seen_count += len(new_logs)
                
                status = (
                    run_with_logs.status.upper() if run_with_logs.status else "UNKNOWN"
                )
                live.update(
                    Panel(
                        f"Run ID: {run_id} | Status: [bold]{status}[/bold]",
                        refresh=True,
                    ),
                    refresh=True,
                )
                
                if not follow or status not in ["RUNNING", "PENDING", "ACTIVE"]:
                    break
                
                time.sleep(2)
            
            # Handle the initial 404 Not Found error
            except NotFoundError:
                if initial_fetch_retries > 0:
                    live.update(
                        Panel(
                            f"Run ID: {run_id} | Status: [yellow]Waiting for logs...[/yellow] (retrying)",
                            border_style="yellow",
                        ),
                        refresh=True,
                    )
                    time.sleep(2)  # Wait 2 seconds before retrying
                    initial_fetch_retries -= 1
                    continue  # Retry the loop
                else:
                    console.print(
                        f"[bold red]Error: Could not find logs for run {run_id} after several retries.[/bold red]"
                    )
                    break
            
            except CodegenAPIError as e:
                console.print(f"[bold red]Error fetching logs: {e.message}[/bold red]")
                break
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped following logs.[/yellow]")
                break
            except ValueError:
                console.print(
                    f"[bold red]Error: The organization ID '{client.config.org_id}' is not a valid integer.[/bold red]"
                )
                break


@app.command(name="run", help="🚀 Start a new agent run and stream its logs.")
def run_agent(
    query: str = typer.Argument(..., help="The prompt or task for the agent."),
    follow: bool = typer.Option(
        True, "--follow/--no-follow", help="Stream logs live after starting."
    ),
):
    """Create a new agent run and optionally follow its progress.
    
    Args:
        query: The prompt or task for the agent.
        follow: Whether to follow logs in real-time.
    """
    client = get_client()
    try:
        console.print(f"▶️  Starting agent with query: '[cyan]{query}[/cyan]'...")
        org_id_int = int(client.config.org_id)
        run = client.create_agent_run(org_id=org_id_int, prompt=query)
        console.print(
            f"✅ Agent run created successfully! [bold]Run ID: {run.id}[/bold]"
        )
        if run.web_url:
            console.print(f"   View online: {run.web_url}")
        
        if follow:
            console.print("\n--- Streaming Logs ---")
            stream_logs(client, run.id, follow=True)
    
    except CodegenAPIError as e:
        console.print(f"[bold red]API Error: {e.message}[/bold red]")
        raise typer.Exit(code=1)
    except ValueError:
        console.print(
            f"[bold red]Error: The organization ID '{client.config.org_id}' is not a valid integer.[/bold red]"
        )
        raise typer.Exit(code=1)


@app.command(name="list", help="📋 List recent agent runs for your organization.")
def list_runs(
    limit: int = typer.Option(20, "--limit", "-l", help="Number of runs to display."),
    status: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status (e.g., running, completed)."
    ),
):
    """Fetch and display a table of recent agent runs.
    
    Args:
        limit: Number of runs to display.
        status: Filter by status.
    """
    client = get_client()
    try:
        org_id_int = int(client.config.org_id)
        runs = client.list_agent_runs(
            org_id=org_id_int, limit=limit, source_type=status
        )
        
        table = Table(title="Recent Agent Runs", box=None, padding=(0, 1))
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Created At", style="green")
        table.add_column("Result", style="yellow")
        table.add_column("Web URL", style="dim")
        
        for run in runs.items:
            table.add_row(
                str(run.id),
                run.status or "N/A",
                run.created_at or "N/A",
                (run.result or "")[:50] + "..." if run.result else "N/A",
                run.web_url or "N/A",
            )
        console.print(table)
    except CodegenAPIError as e:
        console.print(f"[bold red]API Error: {e.message}[/bold red]")
        raise typer.Exit(code=1)
    except ValueError:
        console.print(
            f"[bold red]Error: The organization ID '{client.config.org_id}' is not a valid integer.[/bold red]"
        )
        raise typer.Exit(code=1)


@app.command(name="logs", help="📄 View the logs for a specific agent run.")
def get_logs(
    run_id: int = typer.Argument(..., help="The ID of the agent run."),
    follow: bool = typer.Option(
        False,
        "--follow",
        "-f",
        help="Follow the logs in real-time if the run is active.",
    ),
):
    """Fetch and display logs for a given run ID.
    
    Args:
        run_id: The agent run ID.
        follow: Whether to follow logs in real-time.
    """
    client = get_client()
    stream_logs(client, run_id, follow)


@app.command(
    name="continue", help="💬 Send a continuation message to a paused or running agent."
)
def continue_run(
    run_id: int = typer.Argument(..., help="The ID of the agent run to continue."),
    message: str = typer.Argument(..., help="The follow-up message or instruction."),
    follow: bool = typer.Option(
        True, "--follow/--no-follow", help="Stream logs live after sending the message."
    ),
):
    """Resume an agent run with a new message.
    
    Args:
        run_id: The agent run ID.
        message: The follow-up message or instruction.
        follow: Whether to follow logs in real-time.
    """
    client = get_client()
    try:
        console.print(f"▶️  Sending message to run [cyan]{run_id}[/cyan]...")
        org_id_int = int(client.config.org_id)
        run = client.resume_agent_run(
            org_id=org_id_int, agent_run_id=run_id, prompt=message
        )
        console.print("✅ Message sent successfully!")
        
        if follow:
            console.print("\n--- Streaming Logs ---")
            stream_logs(client, run.id, follow=True)
    except CodegenAPIError as e:
        console.print(f"[bold red]API Error: {e.message}[/bold red]")
        raise typer.Exit(code=1)
    except ValueError:
        console.print(
            f"[bold red]Error: The organization ID '{client.config.org_id}' is not a valid integer.[/bold red]"
        )
        raise typer.Exit(code=1)
