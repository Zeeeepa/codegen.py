"""
Comprehensive CLI for Codegen Agent Orchestration
Provides command-line interface for managing agents, tasks, and configurations
"""

import os
import sys
import json
import time
import argparse
from typing import Optional, Dict, Any, List
from datetime import datetime

from .core import CodegenClient, ClientConfig, ConfigPresets
from .agents import Agent
from .tasks import Task, TaskStatus


class CodegenCLI:
    """Main CLI class for Codegen operations"""
    
    def __init__(self):
        self.config_file = os.path.expanduser("~/.codegen/config.json")
        self.config = self.load_config()
        self.client = None
        self.agent = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
        
        return {
            "org_id": os.getenv("CODEGEN_ORG_ID"),
            "token": os.getenv("CODEGEN_API_TOKEN"),
            "default_timeout": 300,
            "poll_interval": 5.0,
            "preset": "production"
        }
    
    def save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_client(self) -> CodegenClient:
        """Get or create a CodegenClient instance"""
        if not self.client:
            preset_name = self.config.get("preset", "production")
            if hasattr(ConfigPresets, preset_name):
                client_config = getattr(ConfigPresets, preset_name)()
            else:
                client_config = ConfigPresets.production()
            
            self.client = CodegenClient(
                org_id=self.config.get("org_id"),
                token=self.config.get("token"),
                config=client_config
            )
        return self.client
    
    def get_agent(self) -> Agent:
        """Get or create an Agent instance"""
        if not self.agent:
            self.agent = Agent(
                org_id=self.config.get("org_id"),
                token=self.config.get("token")
            )
        return self.agent
    
    def run_command(self, args):
        """Run an agent with a prompt"""
        agent = self.get_agent()
        
        print(f"🚀 Running agent with prompt: {args.prompt}")
        task = agent.run(args.prompt)
        
        print(f"📋 Task created: {task.id}")
        print(f"🔗 Status: {task.status}")
        
        if args.wait:
            print("⏳ Waiting for completion...")
            try:
                result = task.wait_for_completion(
                    timeout=args.timeout or self.config.get("default_timeout", 300),
                    poll_interval=args.poll_interval or self.config.get("poll_interval", 5.0)
                )
                
                print(f"✅ Task completed with status: {result.status}")
                if result.result:
                    print(f"📄 Result: {result.result}")
                if result.github_pull_request:
                    pr = result.github_pull_request
                    print(f"🔗 GitHub PR: {pr.title} ({pr.url})")
                    
            except TimeoutError:
                print(f"⏰ Task did not complete within {args.timeout} seconds")
                print(f"📋 Current status: {task.status}")
        
        return task
    
    def status_command(self, args):
        """Check status of a task or list recent tasks"""
        agent = self.get_agent()
        
        if args.task_id:
            # Show specific task status
            task = agent.get_task(args.task_id)
            print(f"📋 Task {task.id}")
            print(f"🔗 Status: {task.status}")
            print(f"📅 Created: {task.created_at}")
            print(f"📅 Updated: {task.updated_at}")
            
            if task.result:
                print(f"📄 Result: {task.result}")
            if task.error:
                print(f"❌ Error: {task.error}")
            if task.github_pull_request:
                pr = task.github_pull_request
                print(f"🔗 GitHub PR: {pr.title} ({pr.url})")
            
            if args.logs:
                print("\\n📜 Recent logs:")
                logs = task.get_logs(limit=args.log_limit or 10)
                for log in logs.logs:
                    timestamp = log.created_at
                    print(f"  [{timestamp}] {log.message_type}: {log.content}")
        else:
            # List recent tasks
            tasks = agent.list_tasks(limit=args.limit or 10)
            print(f"📋 Recent tasks ({len(tasks)}):")
            
            for task in tasks:
                status_emoji = {
                    TaskStatus.COMPLETED: "✅",
                    TaskStatus.RUNNING: "🔄",
                    TaskStatus.PENDING: "⏳",
                    TaskStatus.FAILED: "❌",
                    TaskStatus.CANCELLED: "🚫"
                }.get(task.status, "❓")
                
                print(f"  {status_emoji} {task.id}: {task.status} ({task.created_at})")
    
    def config_command(self, args):
        """Manage configuration"""
        if args.action == "show":
            print("🔧 Current configuration:")
            for key, value in self.config.items():
                if key == "token" and value:
                    # Mask token for security
                    masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                    print(f"  {key}: {masked_value}")
                else:
                    print(f"  {key}: {value}")
        
        elif args.action == "set":
            if not args.key or not args.value:
                print("❌ Both --key and --value are required for 'set' action")
                return
            
            self.config[args.key] = args.value
            self.save_config()
            print(f"✅ Set {args.key} = {args.value}")
        
        elif args.action == "preset":
            if not args.preset:
                print("❌ --preset is required for 'preset' action")
                return
            
            available_presets = ["development", "production", "high_throughput", "low_latency", "batch_processing"]
            if args.preset not in available_presets:
                print(f"❌ Invalid preset. Available: {', '.join(available_presets)}")
                return
            
            self.config["preset"] = args.preset
            self.save_config()
            print(f"✅ Set preset to {args.preset}")
        
        elif args.action == "init":
            print("🔧 Initializing Codegen configuration...")
            
            org_id = input("Organization ID: ").strip()
            token = input("API Token: ").strip()
            
            if org_id:
                self.config["org_id"] = org_id
            if token:
                self.config["token"] = token
            
            self.save_config()
            print("✅ Configuration saved!")
    
    def monitor_command(self, args):
        """Monitor running tasks"""
        agent = self.get_agent()
        
        print("🔍 Monitoring running tasks...")
        print("Press Ctrl+C to stop monitoring\\n")
        
        try:
            while True:
                tasks = agent.list_tasks(limit=args.limit or 20)
                running_tasks = [t for t in tasks if t.is_running]
                
                if running_tasks:
                    print(f"\\r🔄 Running tasks ({len(running_tasks)}):")
                    for task in running_tasks:
                        print(f"  📋 {task.id}: {task.status}")
                else:
                    print("\\r✅ No running tasks")
                
                time.sleep(args.interval or 10)
                
        except KeyboardInterrupt:
            print("\\n🛑 Monitoring stopped")
    
    def logs_command(self, args):
        """Show logs for a task"""
        if not args.task_id:
            print("❌ Task ID is required")
            return
        
        agent = self.get_agent()
        task = agent.get_task(args.task_id)
        
        print(f"📜 Logs for task {task.id}:")
        
        logs = task.get_logs(skip=args.skip or 0, limit=args.limit or 50)
        
        for log in logs.logs:
            timestamp = log.created_at
            message_type = log.message_type
            content = log.content
            
            # Color coding for different message types
            type_emoji = {
                "ACTION": "🎯",
                "OBSERVATION": "👁️",
                "THOUGHT": "💭",
                "TOOL_CALL": "🔧",
                "TOOL_RESULT": "📊",
                "ERROR": "❌",
                "SYSTEM": "⚙️",
                "USER": "👤",
                "ASSISTANT": "🤖"
            }.get(message_type, "📝")
            
            print(f"  {type_emoji} [{timestamp}] {message_type}: {content}")
        
        if args.follow:
            print("\\n👁️ Following logs (Press Ctrl+C to stop)...")
            try:
                last_log_count = len(logs.logs)
                while True:
                    time.sleep(2)
                    new_logs = task.get_logs(skip=last_log_count)
                    if new_logs.logs:
                        for log in new_logs.logs:
                            timestamp = log.created_at
                            message_type = log.message_type
                            content = log.content
                            type_emoji = {
                                "ACTION": "🎯",
                                "OBSERVATION": "👁️", 
                                "THOUGHT": "💭",
                                "TOOL_CALL": "🔧",
                                "TOOL_RESULT": "📊",
                                "ERROR": "❌",
                                "SYSTEM": "⚙️",
                                "USER": "👤",
                                "ASSISTANT": "🤖"
                            }.get(message_type, "📝")
                            print(f"  {type_emoji} [{timestamp}] {message_type}: {content}")
                        last_log_count += len(new_logs.logs)
            except KeyboardInterrupt:
                print("\\n🛑 Log following stopped")
    
    def stats_command(self, args):
        """Show client statistics"""
        client = self.get_client()
        stats = client.get_stats()
        
        if not stats:
            print("📊 No statistics available (metrics may be disabled)")
            return
        
        print("📊 Client Statistics:")
        print(f"  📈 Total requests: {stats.total_requests}")
        print(f"  ✅ Successful: {stats.successful_requests}")
        print(f"  ❌ Failed: {stats.failed_requests}")
        print(f"  📊 Success rate: {stats.success_rate:.1f}%")
        print(f"  ⏱️ Average response time: {stats.average_response_time:.2f}s")
        
        if hasattr(stats, 'cache_hits'):
            print(f"  💾 Cache hits: {stats.cache_hits}")
            print(f"  💾 Cache misses: {stats.cache_misses}")
        
        if hasattr(stats, 'rate_limit_hits'):
            print(f"  🚦 Rate limit hits: {stats.rate_limit_hits}")


def create_parser():
    """Create the argument parser"""
    parser = argparse.ArgumentParser(
        description="Codegen Agent Orchestration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  codegen run "Create a PR to fix the login bug"
  codegen run "Add unit tests for the user service" --wait
  codegen status --task-id 123
  codegen status --limit 20
  codegen config init
  codegen config set --key timeout --value 600
  codegen monitor --interval 5
  codegen logs 123 --follow
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run an agent with a prompt")
    run_parser.add_argument("prompt", help="The prompt to send to the agent")
    run_parser.add_argument("--wait", action="store_true", help="Wait for task completion")
    run_parser.add_argument("--timeout", type=int, help="Timeout in seconds (default: 300)")
    run_parser.add_argument("--poll-interval", type=float, help="Polling interval in seconds (default: 5.0)")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check task status or list tasks")
    status_parser.add_argument("--task-id", type=int, help="Specific task ID to check")
    status_parser.add_argument("--limit", type=int, help="Number of tasks to list (default: 10)")
    status_parser.add_argument("--logs", action="store_true", help="Show recent logs for the task")
    status_parser.add_argument("--log-limit", type=int, help="Number of log entries to show (default: 10)")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("action", choices=["show", "set", "preset", "init"], help="Configuration action")
    config_parser.add_argument("--key", help="Configuration key (for 'set' action)")
    config_parser.add_argument("--value", help="Configuration value (for 'set' action)")
    config_parser.add_argument("--preset", help="Configuration preset name (for 'preset' action)")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor running tasks")
    monitor_parser.add_argument("--limit", type=int, help="Number of tasks to monitor (default: 20)")
    monitor_parser.add_argument("--interval", type=int, help="Monitoring interval in seconds (default: 10)")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Show task logs")
    logs_parser.add_argument("task_id", type=int, help="Task ID to show logs for")
    logs_parser.add_argument("--skip", type=int, help="Number of logs to skip (default: 0)")
    logs_parser.add_argument("--limit", type=int, help="Number of logs to show (default: 50)")
    logs_parser.add_argument("--follow", action="store_true", help="Follow logs in real-time")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show client statistics")
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CodegenCLI()
    
    try:
        if args.command == "run":
            cli.run_command(args)
        elif args.command == "status":
            cli.status_command(args)
        elif args.command == "config":
            cli.config_command(args)
        elif args.command == "monitor":
            cli.monitor_command(args)
        elif args.command == "logs":
            cli.logs_command(args)
        elif args.command == "stats":
            cli.stats_command(args)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\\n🛑 Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

