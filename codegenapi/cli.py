"""
Comprehensive CLI for Agent Orchestration using CodegenAPI

This CLI is designed specifically for AI agents to orchestrate and delegate tasks
to other Codegen agents efficiently.
"""

import argparse
import sys
from typing import List, Optional

def create_parser() -> argparse.ArgumentParser:
    """Create the comprehensive agent orchestration argument parser"""
    parser = argparse.ArgumentParser(
        prog="codegenapi",
        description="🤖 Agent Orchestration Tool for Codegen API - Delegate tasks between AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 AGENT ORCHESTRATION EXAMPLES:

📝 TASK CREATION:
  # Feature development
  codegenapi new --repo https://github.com/user/repo --task FEATURE_IMPLEMENTATION \\
    --query "Implement OAuth2 authentication with Google and GitHub providers"
  
  # Bug fixing with PR context
  codegenapi new --repo https://github.com/user/repo --pr 123 --task BUG_FIX \\
    --query "Fix memory leak in user session management"
  
  # Code analysis and refactoring
  codegenapi new --repo https://github.com/user/repo --task CODE_RESTRUCTURE \\
    --query "Refactor authentication module for better maintainability"

📊 MONITORING & CONTROL:
  # Real-time task monitoring
  codegenapi status 12345 --watch --interval 10
  
  # Resume with additional context
  codegenapi resume --task-id 12345 --message "Also add password reset functionality"
  
  # Batch task management
  codegenapi list --status running --limit 20

🔧 ORCHESTRATION WORKFLOWS:
  # Sequential task execution
  codegenapi workflow --file tasks.yaml --mode sequential
  
  # Parallel task execution
  codegenapi workflow --file tasks.yaml --mode parallel --max-concurrent 3
  
  # Task dependency management
  codegenapi deps --task-id 12345 --depends-on 12344,12343

🎯 AGENT COORDINATION:
  # Assign task to specific agent type
  codegenapi new --repo https://github.com/user/repo --task FEATURE_IMPLEMENTATION \\
    --query "Add API endpoints" --agent-type backend --priority high
  
  # Multi-agent collaboration
  codegenapi collaborate --tasks 12345,12346 --strategy divide-and-conquer
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="🤖 Agent Orchestration Commands")
    
    # ========================================================================
    # CORE TASK MANAGEMENT
    # ========================================================================
    
    # New task command - Enhanced for agent orchestration
    new_parser = subparsers.add_parser("new", help="🆕 Create a new agent task")
    new_parser.add_argument("--repo", required=True, help="Repository URL")
    new_parser.add_argument("--task", required=True, help="Task type (FEATURE_IMPLEMENTATION, BUG_FIX, etc.)")
    new_parser.add_argument("--query", required=True, help="Detailed task description")
    new_parser.add_argument("--pr", help="PR number to work on")
    new_parser.add_argument("--branch", help="Branch name to work on")
    new_parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], 
                          default="medium", help="Task priority level")
    new_parser.add_argument("--agent-type", choices=["frontend", "backend", "fullstack", "devops", "qa"], 
                          help="Preferred agent specialization")
    new_parser.add_argument("--tags", help="Comma-separated tags for task categorization")
    new_parser.add_argument("--depends-on", help="Comma-separated list of task IDs this task depends on")
    new_parser.add_argument("--timeout", type=int, default=3600, help="Task timeout in seconds")
    new_parser.add_argument("--wait", action="store_true", help="Wait for task completion")
    new_parser.add_argument("--notify", help="Webhook URL for task completion notifications")
    
    # Status command - Enhanced monitoring
    status_parser = subparsers.add_parser("status", help="📊 Check task status and progress")
    status_parser.add_argument("task_id", help="Task ID to check")
    status_parser.add_argument("--watch", action="store_true", help="Real-time status monitoring")
    status_parser.add_argument("--interval", type=int, default=5, help="Watch interval (seconds)")
    status_parser.add_argument("--detailed", action="store_true", help="Show detailed execution logs")
    status_parser.add_argument("--metrics", action="store_true", help="Show performance metrics")
    
    # Resume command - Enhanced with context
    resume_parser = subparsers.add_parser("resume", help="▶️ Resume a paused task")
    resume_parser.add_argument("--task-id", required=True, help="Task ID to resume")
    resume_parser.add_argument("--repo", help="Updated repository URL")
    resume_parser.add_argument("--pr", help="Updated PR number")
    resume_parser.add_argument("--message", help="Additional instructions or context")
    resume_parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], 
                             help="Update task priority")
    resume_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    resume_parser.add_argument("--timeout", type=int, default=300, help="Timeout for waiting (seconds)")
    
    # List command - Enhanced filtering and sorting
    list_parser = subparsers.add_parser("list", help="📋 List and filter tasks")
    list_parser.add_argument("--limit", type=int, default=10, help="Number of tasks to show")
    list_parser.add_argument("--status", choices=["pending", "running", "completed", "failed", "cancelled"], 
                           help="Filter by status")
    list_parser.add_argument("--priority", choices=["low", "medium", "high", "critical"], 
                           help="Filter by priority")
    list_parser.add_argument("--agent-type", choices=["frontend", "backend", "fullstack", "devops", "qa"], 
                           help="Filter by agent type")
    list_parser.add_argument("--tags", help="Filter by tags (comma-separated)")
    list_parser.add_argument("--repo", help="Filter by repository")
    list_parser.add_argument("--sort", choices=["created", "updated", "priority", "status"], 
                           default="updated", help="Sort order")
    list_parser.add_argument("--format", choices=["table", "json", "yaml"], 
                           default="table", help="Output format")
    
    # ========================================================================
    # WORKFLOW ORCHESTRATION
    # ========================================================================
    
    # Workflow command - Multi-task orchestration
    workflow_parser = subparsers.add_parser("workflow", help="🔄 Execute multi-task workflows")
    workflow_parser.add_argument("--file", required=True, help="Workflow definition file (YAML/JSON)")
    workflow_parser.add_argument("--mode", choices=["sequential", "parallel", "dag"], 
                               default="sequential", help="Execution mode")
    workflow_parser.add_argument("--max-concurrent", type=int, default=3, 
                                help="Maximum concurrent tasks (parallel mode)")
    workflow_parser.add_argument("--dry-run", action="store_true", help="Validate workflow without execution")
    workflow_parser.add_argument("--watch", action="store_true", help="Monitor workflow progress")
    workflow_parser.add_argument("--save-state", help="File to save workflow state")
    workflow_parser.add_argument("--resume-from", help="Resume workflow from saved state")
    
    # Dependencies command - Task dependency management
    deps_parser = subparsers.add_parser("deps", help="🔗 Manage task dependencies")
    deps_parser.add_argument("--task-id", required=True, help="Task ID to manage dependencies for")
    deps_parser.add_argument("--depends-on", help="Comma-separated list of dependency task IDs")
    deps_parser.add_argument("--remove-deps", help="Comma-separated list of dependencies to remove")
    deps_parser.add_argument("--show", action="store_true", help="Show current dependencies")
    deps_parser.add_argument("--graph", action="store_true", help="Show dependency graph")
    
    # Collaborate command - Multi-agent coordination
    collab_parser = subparsers.add_parser("collaborate", help="🤝 Multi-agent collaboration")
    collab_parser.add_argument("--tasks", required=True, help="Comma-separated list of task IDs")
    collab_parser.add_argument("--strategy", choices=["divide-and-conquer", "peer-review", "master-worker"], 
                             default="divide-and-conquer", help="Collaboration strategy")
    collab_parser.add_argument("--lead-agent", help="Lead agent for coordination")
    collab_parser.add_argument("--sync-interval", type=int, default=60, 
                             help="Synchronization interval (seconds)")
    
    # ========================================================================
    # MONITORING & ANALYTICS
    # ========================================================================
    
    # Monitor command - Real-time monitoring dashboard
    monitor_parser = subparsers.add_parser("monitor", help="📈 Real-time task monitoring")
    monitor_parser.add_argument("--dashboard", action="store_true", help="Launch monitoring dashboard")
    monitor_parser.add_argument("--tasks", help="Comma-separated list of task IDs to monitor")
    monitor_parser.add_argument("--refresh", type=int, default=5, help="Refresh interval (seconds)")
    monitor_parser.add_argument("--alerts", action="store_true", help="Enable alerts for failures")
    monitor_parser.add_argument("--export", help="Export monitoring data to file")
    
    # Analytics command - Task performance analytics
    analytics_parser = subparsers.add_parser("analytics", help="📊 Task performance analytics")
    analytics_parser.add_argument("--period", choices=["hour", "day", "week", "month"], 
                                 default="day", help="Analysis period")
    analytics_parser.add_argument("--metrics", choices=["success-rate", "avg-duration", "resource-usage"], 
                                 help="Specific metrics to analyze")
    analytics_parser.add_argument("--repo", help="Filter by repository")
    analytics_parser.add_argument("--agent-type", help="Filter by agent type")
    analytics_parser.add_argument("--export", help="Export analytics to file")
    analytics_parser.add_argument("--format", choices=["json", "csv", "html"], 
                                 default="json", help="Export format")
    
    # ========================================================================
    # CONFIGURATION & MANAGEMENT
    # ========================================================================
    
    # Config command - Configuration management
    config_parser = subparsers.add_parser("config", help="⚙️ Configuration management")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), 
                              help="Set configuration value")
    config_parser.add_argument("--get", help="Get configuration value")
    config_parser.add_argument("--reset", action="store_true", help="Reset to default configuration")
    config_parser.add_argument("--validate", action="store_true", help="Validate configuration")
    config_parser.add_argument("--export", help="Export configuration to file")
    config_parser.add_argument("--import", dest="import_file", help="Import configuration from file")
    
    # Templates command - Task template management
    templates_parser = subparsers.add_parser("templates", help="📝 Task template management")
    templates_parser.add_argument("--list", action="store_true", help="List available templates")
    templates_parser.add_argument("--show", help="Show template content")
    templates_parser.add_argument("--create", help="Create new template")
    templates_parser.add_argument("--edit", help="Edit existing template")
    templates_parser.add_argument("--delete", help="Delete template")
    templates_parser.add_argument("--validate", help="Validate template syntax")
    templates_parser.add_argument("--export", help="Export template to file")
    templates_parser.add_argument("--import", dest="import_file", help="Import template from file")
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    # Logs command - Enhanced log management
    logs_parser = subparsers.add_parser("logs", help="📜 Task execution logs")
    logs_parser.add_argument("task_id", help="Task ID to get logs for")
    logs_parser.add_argument("--follow", "-f", action="store_true", help="Follow log output")
    logs_parser.add_argument("--lines", "-n", type=int, default=100, help="Number of lines to show")
    logs_parser.add_argument("--level", choices=["debug", "info", "warning", "error"], 
                           help="Filter by log level")
    logs_parser.add_argument("--grep", help="Filter logs by pattern")
    logs_parser.add_argument("--export", help="Export logs to file")
    logs_parser.add_argument("--format", choices=["text", "json"], default="text", help="Log format")
    
    # Cancel command - Task cancellation
    cancel_parser = subparsers.add_parser("cancel", help="❌ Cancel running tasks")
    cancel_parser.add_argument("task_ids", nargs="+", help="Task IDs to cancel")
    cancel_parser.add_argument("--force", action="store_true", help="Force cancellation")
    cancel_parser.add_argument("--reason", help="Cancellation reason")
    
    # Cleanup command - Resource cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="🧹 Cleanup resources")
    cleanup_parser.add_argument("--completed", action="store_true", help="Clean up completed tasks")
    cleanup_parser.add_argument("--failed", action="store_true", help="Clean up failed tasks")
    cleanup_parser.add_argument("--older-than", help="Clean up tasks older than (e.g., '7d', '1w', '1m')")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned")
    cleanup_parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    try:
        # Import command handlers dynamically to avoid circular imports
        if parsed_args.command == "new":
            from .commands.new import execute_new_command
            return execute_new_command(parsed_args)
        elif parsed_args.command == "status":
            from .commands.status import execute_status_command
            return execute_status_command(parsed_args)
        elif parsed_args.command == "resume":
            from .commands.resume import execute_resume_command
            return execute_resume_command(parsed_args)
        elif parsed_args.command == "list":
            from .commands.list import execute_list_command
            return execute_list_command(parsed_args)
        elif parsed_args.command == "workflow":
            from .commands.workflow import execute_workflow_command
            return execute_workflow_command(parsed_args)
        elif parsed_args.command == "deps":
            from .commands.deps import execute_deps_command
            return execute_deps_command(parsed_args)
        elif parsed_args.command == "collaborate":
            from .commands.collaborate import execute_collaborate_command
            return execute_collaborate_command(parsed_args)
        elif parsed_args.command == "monitor":
            from .commands.monitor import execute_monitor_command
            return execute_monitor_command(parsed_args)
        elif parsed_args.command == "analytics":
            from .commands.analytics import execute_analytics_command
            return execute_analytics_command(parsed_args)
        elif parsed_args.command == "config":
            from .commands.config import execute_config_command
            return execute_config_command(parsed_args)
        elif parsed_args.command == "templates":
            from .commands.templates import execute_templates_command
            return execute_templates_command(parsed_args)
        elif parsed_args.command == "logs":
            from .commands.logs import execute_logs_command
            return execute_logs_command(parsed_args)
        elif parsed_args.command == "cancel":
            from .commands.cancel import execute_cancel_command
            return execute_cancel_command(parsed_args)
        elif parsed_args.command == "cleanup":
            from .commands.cleanup import execute_cleanup_command
            return execute_cleanup_command(parsed_args)
        else:
            print(f"❌ Unknown command: {parsed_args.command}")
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n⏸️  Operation cancelled by user")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

