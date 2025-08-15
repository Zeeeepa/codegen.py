"""
Output Formatting Utilities

Utilities for formatting and displaying output in various formats.
"""

import json
import yaml
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel


def format_output(data: Any, format_type: str = "table", title: Optional[str] = None) -> str:
    """
    Format data for output in the specified format.
    
    Args:
        data: Data to format
        format_type: Output format (json, yaml, table, text)
        title: Optional title for the output
        
    Returns:
        Formatted string
    """
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    elif format_type == "yaml":
        return yaml.dump(data, default_flow_style=False, indent=2)
    elif format_type == "text":
        return str(data)
    else:  # table format
        if isinstance(data, dict):
            return _format_dict_as_table(data, title)
        elif isinstance(data, list):
            return _format_list_as_table(data, title)
        else:
            return str(data)


def _format_dict_as_table(data: Dict[str, Any], title: Optional[str] = None) -> str:
    """Format dictionary as a table."""
    console = Console()
    
    table = Table(title=title)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    
    for key, value in data.items():
        table.add_row(str(key), str(value))
    
    with console.capture() as capture:
        console.print(table)
    
    return capture.get()


def _format_list_as_table(data: List[Any], title: Optional[str] = None) -> str:
    """Format list as a table."""
    if not data:
        return "No data"
    
    console = Console()
    
    # If list contains dictionaries, create table with columns
    if isinstance(data[0], dict):
        table = Table(title=title)
        
        # Add columns based on first item
        for key in data[0].keys():
            table.add_column(str(key).title(), style="white")
        
        # Add rows
        for item in data:
            row = [str(item.get(key, "")) for key in data[0].keys()]
            table.add_row(*row)
        
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()
    else:
        # Simple list
        table = Table(title=title)
        table.add_column("Item", style="white")
        
        for item in data:
            table.add_row(str(item))
        
        with console.capture() as capture:
            console.print(table)
        
        return capture.get()


def create_table(
    data: List[Dict[str, Any]], 
    columns: Optional[List[str]] = None,
    title: Optional[str] = None,
    show_header: bool = True
) -> Table:
    """
    Create a Rich table from data.
    
    Args:
        data: List of dictionaries to display
        columns: Optional list of column names to include
        title: Optional table title
        show_header: Whether to show column headers
        
    Returns:
        Rich Table object
    """
    if not data:
        table = Table(title=title or "No Data")
        table.add_column("Message", style="dim")
        table.add_row("No data available")
        return table
    
    table = Table(title=title, show_header=show_header)
    
    # Determine columns
    if columns is None:
        columns = list(data[0].keys())
    
    # Add columns
    for col in columns:
        table.add_column(col.replace("_", " ").title(), style="white")
    
    # Add rows
    for item in data:
        row = []
        for col in columns:
            value = item.get(col, "")
            # Format special values
            if isinstance(value, bool):
                row.append("✓" if value else "✗")
            elif value is None:
                row.append("[dim]N/A[/dim]")
            else:
                row.append(str(value))
        table.add_row(*row)
    
    return table


def create_tree(data: Dict[str, Any], title: str = "Data") -> Tree:
    """
    Create a Rich tree from nested data.
    
    Args:
        data: Dictionary to display as tree
        title: Tree title
        
    Returns:
        Rich Tree object
    """
    tree = Tree(title)
    
    def add_to_tree(node: Tree, data: Any, key: str = ""):
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    branch = node.add(f"[cyan]{k}[/cyan]")
                    add_to_tree(branch, v, k)
                else:
                    node.add(f"[cyan]{k}[/cyan]: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    branch = node.add(f"[yellow][{i}][/yellow]")
                    add_to_tree(branch, item, f"[{i}]")
                else:
                    node.add(f"[yellow][{i}][/yellow]: {item}")
        else:
            node.add(str(data))
    
    add_to_tree(tree, data)
    return tree


def create_status_panel(
    status: str,
    details: Dict[str, Any],
    title: str = "Status"
) -> Panel:
    """
    Create a status panel with color-coded status.
    
    Args:
        status: Status string
        details: Additional details to display
        title: Panel title
        
    Returns:
        Rich Panel object
    """
    # Color code status
    status_colors = {
        "running": "blue",
        "completed": "green", 
        "failed": "red",
        "pending": "yellow",
        "cancelled": "dim"
    }
    
    status_color = status_colors.get(status.lower(), "white")
    
    content = f"[{status_color}]Status: {status}[/{status_color}]\n"
    
    for key, value in details.items():
        content += f"[cyan]{key}:[/cyan] {value}\n"
    
    return Panel(
        content.strip(),
        title=title,
        border_style=status_color
    )


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_size(bytes_size: int) -> str:
    """
    Format byte size to human-readable format.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}PB"


def colorize_status(status: str) -> str:
    """
    Add color markup to status strings.
    
    Args:
        status: Status string
        
    Returns:
        Status string with color markup
    """
    status_lower = status.lower()
    
    if status_lower in ["completed", "success", "ok", "healthy"]:
        return f"[green]{status}[/green]"
    elif status_lower in ["failed", "error", "unhealthy"]:
        return f"[red]{status}[/red]"
    elif status_lower in ["running", "in_progress", "processing"]:
        return f"[blue]{status}[/blue]"
    elif status_lower in ["pending", "waiting", "queued"]:
        return f"[yellow]{status}[/yellow]"
    elif status_lower in ["cancelled", "stopped", "disabled"]:
        return f"[dim]{status}[/dim]"
    else:
        return status
