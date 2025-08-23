#!/usr/bin/env python3
"""
Codegen CLI.

A command-line interface for interacting with the Codegen API.
"""

import os
import sys
import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from codegen_client import CodegenClient, CodegenApiError

app = typer.Typer(help="Codegen CLI")
console = Console()


def get_client() -> CodegenClient:
    """
    Get a Codegen API client.

    Returns:
        CodegenClient: Codegen API client
    """
    api_key = os.environ.get("CODEGEN_API_KEY")
    if not api_key:
        console.print("[bold red]Error:[/bold red] CODEGEN_API_KEY environment variable is not set")
        sys.exit(1)
    return CodegenClient(api_key=api_key)


@app.command()
def organizations():
    """
    List organizations.
    """
    client = get_client()
    try:
        orgs = client.organizations.get_organizations()
        table = Table(title="Organizations")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Slug", style="blue")
        
        for org in orgs.items:
            table.add_row(str(org.id), org.name, org.slug)
            
        console.print(table)
    except CodegenApiError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def repositories(org_id: int):
    """
    List repositories for an organization.
    """
    client = get_client()
    try:
        repos = client.repositories.get_repositories(org_id=org_id)
        table = Table(title=f"Repositories for Organization {org_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Full Name", style="blue")
        
        for repo in repos.items:
            table.add_row(str(repo.id), repo.name, repo.full_name)
            
        console.print(table)
    except CodegenApiError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def users(org_id: int):
    """
    List users for an organization.
    """
    client = get_client()
    try:
        users = client.users.get_users(org_id=org_id)
        table = Table(title=f"Users for Organization {org_id}")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Email", style="blue")
        
        for user in users.items:
            table.add_row(str(user.id), user.name, user.email)
            
        console.print(table)
    except CodegenApiError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def agent_run(
    org_id: int,
    prompt: str,
    repo_id: Optional[int] = None,
    model: Optional[str] = None,
):
    """
    Create an agent run.
    """
    client = get_client()
    try:
        agent_run = client.agents.create_agent_run(
            org_id=org_id,
            prompt=prompt,
            repo_id=repo_id,
            model=model,
        )
        
        console.print(Panel(f"Created agent run with ID: [bold green]{agent_run.id}[/bold green]"))
        console.print("Status:", agent_run.status)
        console.print("Created at:", agent_run.created_at)
        
        # Wait for the agent run to complete
        console.print("\nWaiting for agent run to complete...")
        with console.status("[bold green]Running agent...[/bold green]"):
            agent_run = client.agents.wait_for_agent_run(
                org_id=org_id,
                agent_run_id=agent_run.id,
            )
        
        console.print(f"\nAgent run [bold green]completed[/bold green] with status: {agent_run.status}")
        if agent_run.output:
            console.print("\n[bold]Output:[/bold]")
            console.print(Panel(agent_run.output, expand=False))
    except CodegenApiError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@app.command()
def multi_run_agent(
    org_id: int,
    prompt: str,
    concurrency: int = typer.Option(3, "--concurrency", "-c", help="Number of concurrent agent runs (1-20)"),
    repo_id: Optional[int] = typer.Option(None, "--repo-id", "-r", help="Repository ID"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="Temperature for generation (0.0-1.0)"),
    synthesis_temperature: float = typer.Option(0.2, "--synthesis-temperature", "-st", help="Temperature for synthesis (0.0-1.0)"),
    timeout: float = typer.Option(600.0, "--timeout", help="Maximum seconds to wait for completion"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results (JSON)"),
    show_candidates: bool = typer.Option(False, "--show-candidates", help="Show all candidate outputs"),
):
    """
    Run multiple agent instances concurrently and synthesize their outputs.
    """
    if not 1 <= concurrency <= 20:
        console.print("[bold red]Error:[/bold red] Concurrency must be between 1 and 20")
        sys.exit(1)
        
    client = get_client()
    try:
        console.print(f"Running [bold cyan]{concurrency}[/bold cyan] agent instances concurrently...")
        
        with console.status(f"[bold green]Running {concurrency} agents...[/bold green]"):
            result = client.multi_run_agent.create_multi_run(
                org_id=org_id,
                prompt=prompt,
                concurrency=concurrency,
                repo_id=repo_id,
                model=model,
                temperature=temperature,
                synthesis_temperature=synthesis_temperature,
                timeout=timeout,
            )
        
        console.print(f"\n[bold green]Success![/bold green] Completed multi-run agent with {len(result['candidates'])} successful runs")
        
        # Display the final synthesized output
        console.print("\n[bold]Final Synthesized Output:[/bold]")
        console.print(Panel(result["final"], expand=False))
        
        # Optionally show all candidate outputs
        if show_candidates:
            console.print("\n[bold]Candidate Outputs:[/bold]")
            for i, candidate in enumerate(result["candidates"]):
                console.print(f"\n[bold cyan]Candidate {i+1}:[/bold cyan]")
                console.print(Panel(candidate, expand=False))
        
        # Save results to file if requested
        if output_file:
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            console.print(f"\nResults saved to [bold blue]{output_file}[/bold blue]")
            
    except CodegenApiError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    app()

