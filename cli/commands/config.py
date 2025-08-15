"""
Configuration Commands

Commands for managing CLI configuration.
"""

import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..core.errors import CLIError, ErrorHandler
from ..core.logging import get_logger, log_cli_command
from ..core.config import ConfigManager

logger = get_logger(__name__)


@click.group()
def config_group():
    """Manage CLI configuration."""
    pass


@config_group.command("show")
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format"
)
@click.pass_context
def show_config(ctx: click.Context, format: str):
    """Show current configuration."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("config show", {"format": format})
    
    with ErrorHandler():
        config_data = config.show()
        
        if format == "json":
            import json
            console.print(json.dumps(config_data, indent=2))
        elif format == "yaml":
            import yaml
            console.print(yaml.dump(config_data, default_flow_style=False))
        else:
            # Table format
            table = Table(title="Current Configuration")
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Source", style="dim")
            
            for key, value in config_data["config"].items():
                source = config_data["sources"].get(key, "unknown")
                # Mask sensitive values
                if "token" in key.lower() or "secret" in key.lower():
                    display_value = "***" if value else "(not set)"
                else:
                    display_value = str(value) if value is not None else "(not set)"
                
                table.add_row(key, display_value, source)
            
            console.print(table)
            
            if config_data["config_file"]:
                console.print(f"\n[dim]Config file: {config_data['config_file']}[/dim]")


@config_group.command("set")
@click.argument("key", required=True)
@click.argument("value", required=True)
@click.option(
    "--save",
    is_flag=True,
    help="Save to config file"
)
@click.pass_context
def set_config(ctx: click.Context, key: str, value: str, save: bool):
    """
    Set a configuration value.
    
    KEY: Configuration key (e.g., api.token, output.format)
    VALUE: Configuration value
    """
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("config set", {"key": key, "save": save})
    
    with ErrorHandler():
        # Convert string values to appropriate types
        if value.lower() in ('true', 'false'):
            typed_value = value.lower() == 'true'
        elif value.isdigit():
            typed_value = int(value)
        elif value.replace('.', '').isdigit():
            typed_value = float(value)
        else:
            typed_value = value
        
        config.set(key, typed_value)
        
        if save:
            config.save()
            console.print(f"[green]✓[/green] Set {key} = {value} and saved to config file")
        else:
            console.print(f"[green]✓[/green] Set {key} = {value} (in memory only)")
            console.print("[dim]Use --save to persist to config file[/dim]")


@config_group.command("unset")
@click.argument("key", required=True)
@click.option(
    "--save",
    is_flag=True,
    help="Save to config file"
)
@click.pass_context
def unset_config(ctx: click.Context, key: str, save: bool):
    """
    Remove a configuration value.
    
    KEY: Configuration key to remove
    """
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("config unset", {"key": key, "save": save})
    
    with ErrorHandler():
        config.set(key, None)
        
        if save:
            config.save()
            console.print(f"[green]✓[/green] Removed {key} and saved to config file")
        else:
            console.print(f"[green]✓[/green] Removed {key} (in memory only)")
            console.print("[dim]Use --save to persist to config file[/dim]")


@config_group.command("validate")
@click.pass_context
def validate_config(ctx: click.Context):
    """Validate current configuration."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("config validate", {})
    
    with ErrorHandler():
        errors = config.validate()
        
        if not errors:
            console.print("[green]✓[/green] Configuration is valid")
        else:
            console.print("[red]✗[/red] Configuration has errors:")
            for error in errors:
                console.print(f"  • {error}")
            
            # Exit with error code
            raise CLIError(
                f"Configuration validation failed with {len(errors)} error(s)",
                exit_code=1
            )


@config_group.command("init")
@click.option(
    "--file",
    type=click.Path(),
    help="Config file path (default: ~/.codegen/config.yaml)"
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing config file"
)
@click.pass_context
def init_config(ctx: click.Context, file: Optional[str], force: bool):
    """Initialize a new configuration file."""
    console = ctx.obj["console"]
    
    log_cli_command("config init", {"file": file, "force": force})
    
    with ErrorHandler():
        # Create new config manager
        new_config = ConfigManager()
        
        # Set some default values
        console.print("[blue]Setting up configuration...[/blue]")
        
        # Prompt for API token
        api_token = click.prompt(
            "API Token (get from https://codegen.com/settings)",
            hide_input=True,
            default="",
            show_default=False
        )
        if api_token:
            new_config.set("api.token", api_token)
        
        # Prompt for org ID
        org_id = click.prompt(
            "Organization ID (optional)",
            type=int,
            default=None,
            show_default=False
        )
        if org_id:
            new_config.set("api.org_id", org_id)
        
        # Set output preferences
        output_format = click.prompt(
            "Preferred output format",
            type=click.Choice(["table", "json", "yaml", "text"]),
            default="table"
        )
        new_config.set("output.format", output_format)
        
        # Save configuration
        target_file = file
        if not target_file:
            from pathlib import Path
            config_dir = Path.home() / ".codegen"
            config_dir.mkdir(exist_ok=True)
            target_file = str(config_dir / "config.yaml")
        
        if Path(target_file).exists() and not force:
            if not click.confirm(f"Config file {target_file} already exists. Overwrite?"):
                console.print("[yellow]Configuration initialization cancelled[/yellow]")
                return
        
        new_config.save(target_file)
        console.print(f"[green]✓[/green] Configuration saved to: {target_file}")
        
        # Validate the new config
        errors = new_config.validate()
        if errors:
            console.print("\n[yellow]⚠[/yellow] Configuration warnings:")
            for error in errors:
                console.print(f"  • {error}")


@config_group.command("reset")
@click.option(
    "--confirm",
    is_flag=True,
    help="Skip confirmation prompt"
)
@click.pass_context
def reset_config(ctx: click.Context, confirm: bool):
    """Reset configuration to defaults."""
    console = ctx.obj["console"]
    config = ctx.obj["config"]
    
    log_cli_command("config reset", {"confirm": confirm})
    
    with ErrorHandler():
        if not confirm:
            if not click.confirm("This will reset all configuration to defaults. Continue?"):
                console.print("[yellow]Reset cancelled[/yellow]")
                return
        
        config.reset()
        console.print("[green]✓[/green] Configuration reset to defaults")
        console.print("[dim]Use 'codegen config init' to set up configuration again[/dim]")
