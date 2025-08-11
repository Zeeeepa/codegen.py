"""
User Interface Layer Interfaces

Defines the contracts for the presentation layer that handles user interaction,
command parsing, output formatting, and progress display. This layer is
completely independent of business logic and API integration.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Iterator, Callable
from dataclasses import dataclass
from enum import Enum
import datetime

from .business_logic import Workspace, Template, Workflow, WorkflowExecution
from .codegen_integration import AgentRun, Organization, User


class OutputFormat(Enum):
    """Output format types"""
    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    TABLE = "table"
    CSV = "csv"
    HTML = "html"


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Command:
    """Parsed command data model"""
    action: str
    target: Optional[str]
    arguments: Dict[str, Any]
    options: Dict[str, Any]
    raw_input: str


@dataclass
class ProgressInfo:
    """Progress information for display"""
    current: int
    total: int
    message: str
    percentage: float
    elapsed_time: datetime.timedelta
    estimated_remaining: Optional[datetime.timedelta]


@dataclass
class FormattedOutput:
    """Formatted output data"""
    content: str
    format_type: OutputFormat
    metadata: Dict[str, Any]


class ICommandParser(ABC):
    """
    Interface for command parsing.
    
    Handles parsing of user commands into structured data that can be
    processed by the business logic layer.
    """
    
    @abstractmethod
    def parse_command(self, command_line: str) -> Command:
        """Parse command line input into structured command"""
        pass
    
    @abstractmethod
    def validate_command(self, command: Command) -> List[str]:
        """Validate command and return any errors"""
        pass
    
    @abstractmethod
    def get_command_help(self, action: Optional[str] = None) -> str:
        """Get help text for commands"""
        pass
    
    @abstractmethod
    def suggest_commands(self, partial_input: str) -> List[str]:
        """Suggest command completions"""
        pass
    
    @abstractmethod
    def register_command(
        self,
        action: str,
        handler: Callable,
        description: str,
        arguments: List[Dict[str, Any]],
        options: List[Dict[str, Any]]
    ) -> None:
        """Register a new command"""
        pass


class IOutputFormatter(ABC):
    """
    Interface for output formatting.
    
    Handles formatting of data for display in various formats (text, JSON, tables, etc.).
    """
    
    @abstractmethod
    def format_agent_run(
        self,
        run: AgentRun,
        format_type: OutputFormat = OutputFormat.TEXT,
        detailed: bool = False
    ) -> FormattedOutput:
        """Format agent run for display"""
        pass
    
    @abstractmethod
    def format_agent_runs_list(
        self,
        runs: List[AgentRun],
        format_type: OutputFormat = OutputFormat.TABLE
    ) -> FormattedOutput:
        """Format list of agent runs"""
        pass
    
    @abstractmethod
    def format_workspace(
        self,
        workspace: Workspace,
        format_type: OutputFormat = OutputFormat.TEXT
    ) -> FormattedOutput:
        """Format workspace for display"""
        pass
    
    @abstractmethod
    def format_template(
        self,
        template: Template,
        format_type: OutputFormat = OutputFormat.TEXT
    ) -> FormattedOutput:
        """Format template for display"""
        pass
    
    @abstractmethod
    def format_workflow(
        self,
        workflow: Workflow,
        format_type: OutputFormat = OutputFormat.TEXT
    ) -> FormattedOutput:
        """Format workflow for display"""
        pass
    
    @abstractmethod
    def format_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> FormattedOutput:
        """Format error for display"""
        pass
    
    @abstractmethod
    def format_success_message(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> FormattedOutput:
        """Format success message"""
        pass
    
    @abstractmethod
    def format_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        title: Optional[str] = None
    ) -> FormattedOutput:
        """Format data as table"""
        pass


class IProgressDisplay(ABC):
    """
    Interface for progress display.
    
    Handles display of progress bars, status updates, and real-time information.
    """
    
    @abstractmethod
    def start_progress(
        self,
        task_id: str,
        message: str,
        total_steps: Optional[int] = None
    ) -> None:
        """Start displaying progress for a task"""
        pass
    
    @abstractmethod
    def update_progress(
        self,
        task_id: str,
        current_step: int,
        message: Optional[str] = None
    ) -> None:
        """Update progress for a task"""
        pass
    
    @abstractmethod
    def complete_progress(
        self,
        task_id: str,
        success: bool = True,
        message: Optional[str] = None
    ) -> None:
        """Complete progress display"""
        pass
    
    @abstractmethod
    def show_spinner(
        self,
        task_id: str,
        message: str
    ) -> None:
        """Show spinner for indeterminate progress"""
        pass
    
    @abstractmethod
    def hide_spinner(self, task_id: str) -> None:
        """Hide spinner"""
        pass
    
    @abstractmethod
    def display_status(
        self,
        run: AgentRun,
        watch: bool = False,
        refresh_interval: int = 5
    ) -> None:
        """Display agent run status with optional watching"""
        pass


class IInteractivePrompts(ABC):
    """
    Interface for interactive user prompts.
    
    Handles user input collection, confirmations, and interactive workflows.
    """
    
    @abstractmethod
    def prompt_text(
        self,
        message: str,
        default: Optional[str] = None,
        required: bool = True
    ) -> str:
        """Prompt user for text input"""
        pass
    
    @abstractmethod
    def prompt_choice(
        self,
        message: str,
        choices: List[str],
        default: Optional[str] = None
    ) -> str:
        """Prompt user to choose from options"""
        pass
    
    @abstractmethod
    def prompt_confirm(
        self,
        message: str,
        default: bool = False
    ) -> bool:
        """Prompt user for yes/no confirmation"""
        pass
    
    @abstractmethod
    def prompt_multiline(
        self,
        message: str,
        default: Optional[str] = None
    ) -> str:
        """Prompt user for multiline text input"""
        pass
    
    @abstractmethod
    def prompt_password(
        self,
        message: str,
        confirm: bool = False
    ) -> str:
        """Prompt user for password input"""
        pass
    
    @abstractmethod
    def prompt_file_path(
        self,
        message: str,
        must_exist: bool = True,
        file_type: Optional[str] = None
    ) -> str:
        """Prompt user for file path"""
        pass
    
    @abstractmethod
    def show_menu(
        self,
        title: str,
        options: List[Dict[str, Any]],
        allow_back: bool = True
    ) -> Dict[str, Any]:
        """Show interactive menu"""
        pass


class IUserInterface(ABC):
    """
    Interface for complete user interface.
    
    Combines all UI components into a cohesive interface that can be
    implemented by different presentation layers (CLI, web, etc.).
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the user interface"""
        pass
    
    @abstractmethod
    def display_welcome(self) -> None:
        """Display welcome message"""
        pass
    
    @abstractmethod
    def display_help(self, topic: Optional[str] = None) -> None:
        """Display help information"""
        pass
    
    @abstractmethod
    def handle_command(self, command: Command) -> Any:
        """Handle a parsed command"""
        pass
    
    @abstractmethod
    def display_output(self, output: FormattedOutput) -> None:
        """Display formatted output"""
        pass
    
    @abstractmethod
    def display_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Display error message"""
        pass
    
    @abstractmethod
    def log_message(self, level: LogLevel, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log message with specified level"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources before exit"""
        pass
    
    @abstractmethod
    def run_interactive_mode(self) -> None:
        """Run in interactive mode"""
        pass
    
    @abstractmethod
    def run_command_mode(self, command_line: str) -> int:
        """Run single command and return exit code"""
        pass

