"""
Authentication Commands

Commands for managing authentication and API tokens.
"""

import click
from rich.console import Console
from rich.table import Table

from ..core.errors import CLIError, ErrorHandler, translate_sdk_error
from ..core.logging import get_logger, log_cli_command

logger = get_logger(__name__)


@click.group()
def auth_group():
    """Manage authentication and API tokens."""
    pass


@auth_group.command("status")
@click.pass_context
def auth_status(ctx: click.Context):
    """Check authentication status."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("auth status", {})
    
    with ErrorHandler():
        api_token = config.get("api.token")
        
        if not api_token:
            console.print("[red]✗[/red] No API token configured")
            console.print("\n[dim]Set your token with:[/dim]")
            console.print("  codegen config set api.token YOUR_TOKEN")
            console.print("  or set CODEGEN_API_TOKEN environment variable")
            return
        
        console.print("[green]✓[/green] API token is configured")
        console.print(f"[dim]Token: {api_token[:8]}...{api_token[-4:]}[/dim]")
        
        # Test the token by making a simple API call
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from codegen_api import CodegenClient, ClientConfig
            
            client_config = ClientConfig(
                api_token=api_token,
                base_url=config.get("api.base_url"),
                timeout=config.get("api.timeout"),
            )
            
            with CodegenClient(client_config) as client:
                console.print("[blue]Testing API connection...[/blue]")
                
                # Try to get current user
                user = client.get_current_user()
                console.print(f"[green]✓[/green] Connected as: {user.github_username}")
                
                # Get organizations
                orgs = client.get_organizations(limit=5)
                if orgs.items:
                    console.print(f"[green]✓[/green] Access to {len(orgs.items)} organization(s)")
                    
                    table = Table(title="Available Organizations")
                    table.add_column("ID", style="cyan")
                    table.add_column("Name", style="white")
                    table.add_column("Role", style="dim")
                    
                    for org in orgs.items:
                        table.add_row(str(org.id), org.name, "member")  # Role would come from API
                    
                    console.print(table)
                else:
                    console.print("[yellow]⚠[/yellow] No organizations found")
                
        except Exception as e:
            console.print(f"[red]✗[/red] Authentication failed: {str(e)}")
            console.print("\n[dim]Suggestions:[/dim]")
            console.print("  • Check if your token is valid and active")
            console.print("  • Verify network connectivity")
            console.print("  • Generate a new token at https://codegen.com/settings")


@auth_group.command("login")
@click.option(
    "--token",
    help="API token (will prompt if not provided)"
)
@click.pass_context
def auth_login(ctx: click.Context, token: str):
    """Set up authentication with API token."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("auth login", {})
    
    with ErrorHandler():
        if not token:
            console.print("[blue]Get your API token from: https://codegen.com/settings[/blue]")
            token = click.prompt("API Token", hide_input=True)
        
        if not token:
            raise CLIError("API token is required")
        
        # Test the token
        console.print("[blue]Validating token...[/blue]")
        
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from codegen_api import CodegenClient, ClientConfig
            
            client_config = ClientConfig(
                api_token=token,
                base_url=config.get("api.base_url"),
                timeout=config.get("api.timeout"),
            )
            
            with CodegenClient(client_config) as client:
                user = client.get_current_user()
                console.print(f"[green]✓[/green] Token is valid for user: {user.github_username}")
                
                # Save the token
                config.set("api.token", token)
                config.save()
                
                console.print("[green]✓[/green] Authentication configured successfully")
                
                # Show available organizations
                orgs = client.get_organizations(limit=5)
                if orgs.items:
                    console.print(f"\n[blue]Available organizations:[/blue]")
                    for org in orgs.items:
                        console.print(f"  • {org.name} (ID: {org.id})")
                    
                    if len(orgs.items) == 1:
                        # Auto-configure single org
                        config.set("api.org_id", orgs.items[0].id)
                        config.save()
                        console.print(f"[green]✓[/green] Default organization set to: {orgs.items[0].name}")
                    else:
                        console.print(f"\n[dim]Set default org with:[/dim]")
                        console.print("  codegen config set api.org_id ORG_ID")
                
        except Exception as e:
            raise translate_sdk_error(e)


@auth_group.command("logout")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt"
)
@click.pass_context
def auth_logout(ctx: click.Context, confirm: bool):
    """Remove stored authentication."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("auth logout", {"confirm": confirm})
    
    with ErrorHandler():
        if not confirm:
            if not click.confirm("This will remove your stored API token. Continue?"):
                console.print("[yellow]Logout cancelled[/yellow]")
                return
        
        config.set("api.token", None)
        config.save()
        
        console.print("[green]✓[/green] Authentication removed")
        console.print("[dim]Use 'codegen auth login' to authenticate again[/dim]")
