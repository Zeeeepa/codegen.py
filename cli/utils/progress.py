"""
Progress Indicators and User Experience Utilities

Utilities for showing progress, spinners, and interactive elements.
"""

import time
from typing import Optional, Callable, Any
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner


def create_progress_bar(
    description: str = "Processing...",
    total: Optional[int] = None,
    show_percentage: bool = True,
    show_time: bool = True
) -> Progress:
    """
    Create a progress bar with standard configuration.
    
    Args:
        description: Description text
        total: Total number of items (None for indeterminate)
        show_percentage: Whether to show percentage
        show_time: Whether to show time information
        
    Returns:
        Configured Progress object
    """
    columns = [
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ]
    
    if total is not None:
        columns.append(BarColumn())
        if show_percentage:
            columns.append(TaskProgressColumn())
    
    if show_time:
        from rich.progress import TimeElapsedColumn, TimeRemainingColumn
        columns.append(TimeElapsedColumn())
        if total is not None:
            columns.append(TimeRemainingColumn())
    
    return Progress(*columns)


def show_spinner(
    message: str,
    spinner_type: str = "dots",
    console: Optional[Console] = None
) -> Live:
    """
    Show a spinner with message.
    
    Args:
        message: Message to display
        spinner_type: Type of spinner animation
        console: Console to use (creates new if None)
        
    Returns:
        Live object for updating
    """
    if console is None:
        console = Console()
    
    spinner = Spinner(spinner_type, text=message)
    return Live(spinner, console=console, refresh_per_second=10)


def with_progress(
    func: Callable,
    description: str = "Processing...",
    show_result: bool = True,
    console: Optional[Console] = None
) -> Any:
    """
    Execute a function with a progress spinner.
    
    Args:
        func: Function to execute
        description: Progress description
        show_result: Whether to show success/failure result
        console: Console to use
        
    Returns:
        Function result
    """
    if console is None:
        console = Console()
    
    with show_spinner(description, console=console):
        try:
            result = func()
            if show_result:
                console.print(f"[green]✓[/green] {description}")
            return result
        except Exception as e:
            if show_result:
                console.print(f"[red]✗[/red] {description} failed: {str(e)}")
            raise


class ProgressTracker:
    """
    A progress tracker for multi-step operations.
    """
    
    def __init__(self, total_steps: int, description: str = "Progress"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.console = Console()
        self.progress = create_progress_bar(description, total_steps)
        self.task_id = None
        self.started = False
    
    def start(self) -> None:
        """Start the progress tracker."""
        if not self.started:
            self.progress.start()
            self.task_id = self.progress.add_task(self.description, total=self.total_steps)
            self.started = True
    
    def step(self, message: Optional[str] = None) -> None:
        """Advance to the next step."""
        if not self.started:
            self.start()
        
        self.current_step += 1
        
        if message:
            self.progress.update(self.task_id, description=message)
        
        self.progress.update(self.task_id, advance=1)
    
    def finish(self, message: Optional[str] = None) -> None:
        """Finish the progress tracker."""
        if self.started:
            if message:
                self.progress.update(self.task_id, description=message)
            self.progress.stop()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()


class InteractiveProgress:
    """
    Interactive progress display with user feedback.
    """
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.steps = []
        self.current_step = 0
    
    def add_step(self, name: str, description: str = "") -> None:
        """Add a step to the progress."""
        self.steps.append({
            "name": name,
            "description": description,
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "error": None
        })
    
    def start_step(self, step_index: int) -> None:
        """Start a specific step."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["status"] = "running"
            self.steps[step_index]["start_time"] = time.time()
            self.current_step = step_index
            self._update_display()
    
    def complete_step(self, step_index: int, success: bool = True, error: Optional[str] = None) -> None:
        """Complete a specific step."""
        if 0 <= step_index < len(self.steps):
            self.steps[step_index]["status"] = "completed" if success else "failed"
            self.steps[step_index]["end_time"] = time.time()
            if error:
                self.steps[step_index]["error"] = error
            self._update_display()
    
    def _update_display(self) -> None:
        """Update the progress display."""
        self.console.clear()
        self.console.print("[bold]Progress:[/bold]\n")
        
        for i, step in enumerate(self.steps):
            status_icon = {
                "pending": "[dim]○[/dim]",
                "running": "[blue]●[/blue]",
                "completed": "[green]✓[/green]",
                "failed": "[red]✗[/red]"
            }.get(step["status"], "○")
            
            name = step["name"]
            description = step["description"]
            
            line = f"{status_icon} {name}"
            if description:
                line += f" - {description}"
            
            if step["status"] == "running":
                line = f"[bold]{line}[/bold]"
            elif step["status"] == "failed" and step["error"]:
                line += f"\n    [red]Error: {step['error']}[/red]"
            
            self.console.print(line)
        
        self.console.print()


def confirm_action(
    message: str,
    default: bool = False,
    console: Optional[Console] = None
) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        message: Confirmation message
        default: Default value if user just presses Enter
        console: Console to use
        
    Returns:
        True if user confirms, False otherwise
    """
    if console is None:
        console = Console()
    
    import click
    return click.confirm(message, default=default)


def select_from_list(
    items: list,
    message: str = "Select an option:",
    console: Optional[Console] = None
) -> Any:
    """
    Let user select from a list of items.
    
    Args:
        items: List of items to choose from
        message: Selection message
        console: Console to use
        
    Returns:
        Selected item
    """
    if console is None:
        console = Console()
    
    if not items:
        console.print("[red]No items to select from[/red]")
        return None
    
    if len(items) == 1:
        console.print(f"[dim]Only one option available: {items[0]}[/dim]")
        return items[0]
    
    console.print(f"[bold]{message}[/bold]")
    for i, item in enumerate(items, 1):
        console.print(f"  {i}. {item}")
    
    while True:
        try:
            import click
            choice = click.prompt("Enter choice", type=int)
            if 1 <= choice <= len(items):
                return items[choice - 1]
            else:
                console.print(f"[red]Please enter a number between 1 and {len(items)}[/red]")
        except (ValueError, click.Abort):
            console.print("[red]Invalid input. Please enter a number.[/red]")


def wait_with_spinner(
    duration: float,
    message: str = "Waiting...",
    console: Optional[Console] = None
) -> None:
    """
    Wait for a specified duration with a spinner.
    
    Args:
        duration: Duration to wait in seconds
        message: Message to display
        console: Console to use
    """
    if console is None:
        console = Console()
    
    with show_spinner(message, console=console):
        time.sleep(duration)
