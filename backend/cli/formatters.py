"""
Formatters for the Codegen CLI.

This module contains formatting functions for the Codegen CLI.
"""

from typing import Dict, Any, Union

from rich.panel import Panel


def format_log_entry(log: Dict[str, Any]) -> Union[str, Panel]:
    """Format a single log entry for clean printing.
    
    Args:
        log: The log entry to format.
        
    Returns:
        A formatted string or Panel.
    """
    log_type = log.get("message_type", "LOG")
    created_at = log.get("created_at", "")
    output = f"[dim]{created_at}[/dim] [bold cyan]{log_type:<15}[/bold cyan]"
    
    if thought := log.get("thought"):
        output += f" 🤔 {thought}"
    
    if tool_name := log.get("tool_name"):
        output += f"\n  [dim]=> Tool:[/] [bold magenta]{tool_name}[/bold magenta] | Input: {log.get('tool_input')}"
    
    if observation := log.get("observation"):
        if log_type == "FINAL_ANSWER":
            return Panel(
                f"[bold green]Final Answer:[/] {observation}",
                border_style="green",
                expand=False,
            )
        if log_type == "ERROR":
            return Panel(
                f"[bold red]Error:[/] {observation}", border_style="red", expand=False
            )
    
    return output

