"""
Organization Commands

Commands for managing organizations.
"""

import click
from rich.table import Table

from ..core.errors import ErrorHandler, translate_sdk_error
from ..core.logging import get_logger, log_cli_command

logger = get_logger(__name__)


@click.group()
def org_group():
    """Manage organizations."""
    pass


@org_group.command("list")
@click.option(
    "--limit",
    type=int,
    default=10,
    help="Number of organizations to show (default: 10)"
)
@click.pass_context
def list_orgs(ctx: click.Context, limit: int):
    """List available organizations."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("org list", {"limit": limit})
    
    with ErrorHandler():
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from codegen_api import CodegenClient, ClientConfig
            
            client_config = ClientConfig(
                api_token=config.get("api.token"),
                base_url=config.get("api.base_url"),
                timeout=config.get("api.timeout"),
            )
            
            with CodegenClient(client_config) as client:
                console.print("[blue]Fetching organizations...[/blue]")
                
                orgs = client.get_organizations(limit=limit)
                
                if not orgs.items:
                    console.print("[yellow]No organizations found[/yellow]")
                    return
                
                table = Table(title="Organizations")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="white")
                table.add_column("Role", style="dim")
                table.add_column("Created", style="dim")
                
                for org in orgs.items:
                    table.add_row(
                        str(org.id),
                        org.name,
                        "member",  # Would come from API
                        org.created_at.strftime("%Y-%m-%d") if hasattr(org, 'created_at') else "N/A"
                    )
                
                console.print(table)
                
                current_org_id = config.get("api.org_id")
                if current_org_id:
                    console.print(f"\n[dim]Current default organization: {current_org_id}[/dim]")
                
        except Exception as e:
            raise translate_sdk_error(e)


@org_group.command("show")
@click.argument("org_id", type=int, required=True)
@click.pass_context
def show_org(ctx: click.Context, org_id: int):
    """
    Show details for a specific organization.
    
    ORG_ID: The organization ID to show
    """
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("org show", {"org_id": org_id})
    
    with ErrorHandler():
        console.print(f"[blue]Fetching organization {org_id}...[/blue]")
        
        # Placeholder implementation
        console.print(f"[green]Organization ID:[/green] {org_id}")
        console.print(f"[green]Name:[/green] Example Organization")
        console.print(f"[green]Role:[/green] member")
        console.print(f"[green]Created:[/green] 2024-01-01")
        console.print(f"[green]Members:[/green] 5")
        console.print(f"[green]Agent Runs:[/green] 142")


@org_group.command("set-default")
@click.argument("org_id", type=int, required=True)
@click.pass_context
def set_default_org(ctx: click.Context, org_id: int):
    """
    Set the default organization.
    
    ORG_ID: The organization ID to set as default
    """
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("org set-default", {"org_id": org_id})
    
    with ErrorHandler():
        config.set("api.org_id", org_id)
        config.save()
        
        console.print(f"[green]✓[/green] Default organization set to: {org_id}")
        console.print("[dim]This will be used for all commands unless overridden with --org-id[/dim]")
