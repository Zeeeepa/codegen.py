"""
Command line interface for CodegenAPI
"""

import argparse
import sys
from typing import List, Optional
from .commands.new import execute_new_command
from .commands.status import execute_status_command
from .commands.resume import execute_resume_command
from .commands.list import execute_list_command


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="codegenapi",
        description="Agent-to-Agent Task Execution Tool for Codegen API"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # New command
    new_parser = subparsers.add_parser("new", help="Create a new task")
    new_parser.add_argument("--repo", required=True, help="Repository URL")
    new_parser.add_argument("--task", required=True, help="Task type")
    new_parser.add_argument("--query", required=True, help="Task description")
    new_parser.add_argument("--pr", help="PR number or branch name")
    new_parser.add_argument("--branch", help="Branch name")
    new_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    new_parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check task status")
    status_parser.add_argument("task_id", help="Task ID")
    status_parser.add_argument("--watch", action="store_true", help="Watch for changes")
    status_parser.add_argument("--interval", type=int, default=5, help="Watch interval in seconds")
    
    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a task")
    resume_parser.add_argument("--task-id", required=True, help="Task ID")
    resume_parser.add_argument("--repo", help="Repository URL")
    resume_parser.add_argument("--pr", help="PR number or branch name")
    resume_parser.add_argument("--message", help="Additional instructions")
    resume_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    resume_parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List recent tasks")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of tasks to show")
    list_parser.add_argument("--status", help="Filter by status")
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    try:
        if parsed_args.command == "new":
            return execute_new_command(
                repo=parsed_args.repo,
                task=parsed_args.task,
                query=parsed_args.query,
                pr=parsed_args.pr,
                branch=parsed_args.branch,
                wait=parsed_args.wait,
                timeout=parsed_args.timeout
            )
        
        elif parsed_args.command == "status":
            return execute_status_command(
                task_id=parsed_args.task_id,
                watch=parsed_args.watch,
                interval=parsed_args.interval
            )
        
        elif parsed_args.command == "resume":
            return execute_resume_command(
                task_id=parsed_args.task_id,
                repo=parsed_args.repo,
                pr=parsed_args.pr,
                message=parsed_args.message,
                wait=parsed_args.wait,
                timeout=parsed_args.timeout
            )
        
        elif parsed_args.command == "list":
            return execute_list_command(
                limit=parsed_args.limit,
                status=parsed_args.status
            )
        
        else:
            print(f"Unknown command: {parsed_args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

