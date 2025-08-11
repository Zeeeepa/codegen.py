"""
Argument Parsing

Clean CLI argument parsing with support for all commands and options.
Based on PR 9's enhanced command structure.
"""

import argparse
from typing import List, Optional
from .models import TaskType


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        prog="codegenapi",
        description="Enhanced CLI for Codegen API with workspace and template support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codegenapi new FEATURE_IMPLEMENTATION --repo https://github.com/user/repo
  codegenapi resume 12345 --message "Continue with the implementation"
  codegenapi status --watch --org-id 123
  codegenapi status 12345 --logs
        """
    )
    
    # Global options
    parser.add_argument(
        "--org-id",
        type=int,
        help="Organization ID (overrides config/env)"
    )
    parser.add_argument(
        "--token",
        help="API token (overrides config/env)"
    )
    parser.add_argument(
        "--base-url",
        help="API base URL (overrides config/env)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--config-file",
        help="Path to configuration file"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # NEW command
    new_parser = subparsers.add_parser(
        "new",
        help="Create a new task from template",
        description="Create a new Codegen task using predefined templates"
    )
    new_parser.add_argument(
        "task_type",
        choices=[t.value for t in TaskType],
        help="Type of task to create"
    )
    new_parser.add_argument(
        "--repo",
        required=True,
        help="Repository URL or name"
    )
    new_parser.add_argument(
        "--message",
        help="Custom message/prompt for the task"
    )
    new_parser.add_argument(
        "--template-vars",
        help="Template variables as JSON string"
    )
    new_parser.add_argument(
        "--workspace",
        help="Workspace name (if using workspaces)"
    )
    new_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high", "urgent"],
        default="medium",
        help="Task priority"
    )
    new_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without actually creating"
    )
    
    # RESUME command
    resume_parser = subparsers.add_parser(
        "resume",
        help="Resume a paused task",
        description="Resume a previously paused Codegen task"
    )
    resume_parser.add_argument(
        "task_id",
        type=int,
        help="ID of the task to resume"
    )
    resume_parser.add_argument(
        "--message",
        required=True,
        help="Message to continue with"
    )
    resume_parser.add_argument(
        "--images",
        nargs="*",
        help="Image URLs to include"
    )
    
    # STATUS command
    status_parser = subparsers.add_parser(
        "status",
        help="Check task status",
        description="Check status of tasks and view progress"
    )
    status_parser.add_argument(
        "task_id",
        type=int,
        nargs="?",
        help="Specific task ID to check (optional)"
    )
    status_parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for status changes (live updates)"
    )
    status_parser.add_argument(
        "--logs",
        action="store_true",
        help="Show task logs"
    )
    status_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of tasks to show (when no task_id specified)"
    )
    status_parser.add_argument(
        "--filter-status",
        choices=["PENDING", "ACTIVE", "COMPLETE", "FAILED", "CANCELLED", "PAUSED"],
        help="Filter tasks by status"
    )
    status_parser.add_argument(
        "--workspace",
        help="Filter tasks by workspace"
    )
    status_parser.add_argument(
        "--format",
        choices=["table", "json", "yaml"],
        default="table",
        help="Output format"
    )
    
    return parser


def parse_arguments(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    # Validate arguments
    if not parsed.command:
        parser.print_help()
        raise SystemExit(1)
    
    return parsed

