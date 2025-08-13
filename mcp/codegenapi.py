#!/usr/bin/env python3
"""
Command-line interface for Codegen API
"""

import os
import sys
import json
import argparse

from codegen_client import CodegenClient, ValidationError


def new_command(args):
    """Create a new agent run"""
    client = CodegenClient()

    # Create metadata if provided
    metadata = {}
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON metadata: {args.metadata}")
            sys.exit(1)

    try:
        result = client.create_agent_run(
            prompt=args.query,
            repo=args.repo,
            branch=args.branch,
            pr=args.pr,
            task=args.task,
            metadata=metadata
        )

        print(f"Created agent run with ID: {result.get('id')}")
        print(f"Status: {result.get('status')}")
        print(f"Web URL: {result.get('web_url')}")

        # Wait for completion if requested
        if args.wait:
            print(f"Waiting for completion (timeout: {args.timeout}s)...")
            try:
                result = client.wait_for_completion(
                    agent_run_id=result.get('id'),
                    timeout=args.timeout
                )
                print(f"Run completed with status: {result.get('status')}")
                if result.get('result'):
                    print("\nResult:")
                    print(result.get('result'))
            except TimeoutError:
                print(f"Timeout waiting for completion after {args.timeout}s")

        return result.get('id')
    except ValidationError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def resume_command(args):
    """Resume an agent run"""
    client = CodegenClient()

    try:
        result = client.resume_agent_run(
            agent_run_id=args.agent_run_id,
            prompt=args.query,
            task=args.task
        )

        print(f"Resumed agent run with ID: {result.get('id')}")
        print(f"Status: {result.get('status')}")
        print(f"Web URL: {result.get('web_url')}")

        # Wait for completion if requested
        if args.wait:
            print(f"Waiting for completion (timeout: {args.timeout}s)...")
            try:
                result = client.wait_for_completion(
                    agent_run_id=result.get('id'),
                    timeout=args.timeout
                )
                print(f"Run completed with status: {result.get('status')}")
                if result.get('result'):
                    print("\nResult:")
                    print(result.get('result'))
            except TimeoutError:
                print(f"Timeout waiting for completion after {args.timeout}s")

        return result.get('id')
    except ValidationError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def list_command(args):
    """List agent runs"""
    client = CodegenClient()

    try:
        result = client.list_agent_runs(
            status=args.status,
            repo=args.repo,
            limit=args.limit
        )

        runs = result.get('items', [])
        total = result.get('total', 0)

        print(f"Found {len(runs)} agent runs (total: {total})")
        print("\nID\tStatus\tCreated\t\t\tRepo\t\tTask")
        print("-" * 80)

        for run in runs:
            repo = run.get('metadata', {}).get('repo', '') if run.get('metadata') else ''
            task = run.get('metadata', {}).get('task_type', '') if run.get('metadata') else ''
            print(f"{run.get('id')}\t{run.get('status')}\t{run.get('created_at')}\t{repo}\t{task}")

        return runs
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_command(args):
    """Get agent run details"""
    client = CodegenClient()

    try:
        result = client.get_agent_run(args.agent_run_id)

        print(f"Agent run ID: {result.get('id')}")
        print(f"Status: {result.get('status')}")
        print(f"Created at: {result.get('created_at')}")
        print(f"Web URL: {result.get('web_url')}")

        if result.get('result'):
            print("\nResult:")
            print(result.get('result'))

        if result.get('github_pull_requests'):
            print("\nGitHub Pull Requests:")
            for pr in result.get('github_pull_requests'):
                print(f"- {pr.get('title')}: {pr.get('url')}")

        if result.get('metadata'):
            print("\nMetadata:")
            for key, value in result.get('metadata').items():
                print(f"- {key}: {value}")

        return result
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def logs_command(args):
    """Get agent run logs"""
    client = CodegenClient()

    try:
        result = client.get_agent_run_logs(
            agent_run_id=args.agent_run_id,
            skip=args.skip,
            limit=args.limit
        )

        logs = result.get('logs', [])
        total = result.get('total_logs', 0)

        print(f"Found {len(logs)} logs (total: {total})")

        for log in logs:
            created_at = log.get('created_at', '')
            message_type = log.get('message_type', '')
            tool_name = log.get('tool_name', '')
            thought = log.get('thought', '')

            print(f"\n[{created_at}] {message_type}")
            if tool_name:
                print(f"Tool: {tool_name}")
            if thought:
                print(f"Thought: {thought}")

        return logs
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def config_command(args):
    """Manage configuration"""
    # We don't need the client for config operations
    try:
        if args.action == "list":
            # Get the config file path
            config_dir = os.path.expanduser("~/.config/codegen")
            config_file = os.path.join(config_dir, "config.json")

            if not os.path.exists(config_file):
                print("No configuration found")
                return {}

            with open(config_file, "r") as f:
                config = json.load(f)

            print("Configuration:")
            for key, value in config.items():
                print(f"- {key}: {value}")

            return config
        elif args.action == "get":
            if not args.key:
                print("Error: Key is required for get action")
                sys.exit(1)

            # Get the config file path
            config_dir = os.path.expanduser("~/.config/codegen")
            config_file = os.path.join(config_dir, "config.json")

            if not os.path.exists(config_file):
                print(f"No configuration found for key: {args.key}")
                return None

            with open(config_file, "r") as f:
                config = json.load(f)

            value = config.get(args.key)
            print(f"{args.key}: {value}")

            return value
        elif args.action == "set":
            if not args.key:
                print("Error: Key is required for set action")
                sys.exit(1)
            if not args.value:
                print("Error: Value is required for set action")
                sys.exit(1)

            # Get the config file path
            config_dir = os.path.expanduser("~/.config/codegen")
            config_file = os.path.join(config_dir, "config.json")

            # Create the config directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)

            # Load the config
            config = {}
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = json.load(f)

            # Set the value
            config[args.key] = args.value

            # Save the config
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)

            print(f"Set {args.key} to {args.value}")

            return {args.key: args.value}
        else:
            print(f"Error: Invalid action: {args.action}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Command-line interface for Codegen API")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # New command
    new_parser = subparsers.add_parser("new", help="Create a new agent run")
    new_parser.add_argument("--repo", required=True, help="Repository name (e.g., 'user/repo')")
    new_parser.add_argument("--branch", help="Branch name")
    new_parser.add_argument("--pr", type=int, help="PR number")
    new_parser.add_argument("--task", help="Task type (e.g., 'CREATE_PLAN', 'ANALYZE', 'TEST')")
    new_parser.add_argument("--query", required=True, help="The prompt to send to the agent")
    new_parser.add_argument("--metadata", help="Additional metadata for the agent run (JSON)")
    new_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    new_parser.add_argument("--timeout", type=float, default=300, help="Timeout for wait (seconds)")

    # Resume command
    resume_parser = subparsers.add_parser("resume", help="Resume a paused agent run")
    resume_parser.add_argument("--agent_run_id", required=True, help="Agent run ID to resume")
    resume_parser.add_argument("--task", help="Task type (e.g., 'CREATE_PLAN', 'ANALYZE', 'TEST')")
    resume_parser.add_argument("--query", required=True, help="The prompt to send to the agent")
    resume_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    resume_parser.add_argument("--timeout", type=float, default=300, help="Timeout for wait (seconds)")

    # List command
    list_parser = subparsers.add_parser("list", help="List agent runs")
    list_parser.add_argument("--status", help="Filter by status (e.g., 'ACTIVE', 'COMPLETE', 'ERROR')")
    list_parser.add_argument("--repo", help="Filter by repository")
    list_parser.add_argument("--limit", type=int, default=10, help="Maximum number of runs to return")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get agent run details")
    get_parser.add_argument("--agent_run_id", required=True, help="Agent run ID to retrieve")

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="Get agent run logs")
    logs_parser.add_argument("--agent_run_id", required=True, help="Agent run ID to get logs for")
    logs_parser.add_argument("--skip", type=int, default=0, help="Number of logs to skip (for pagination)")
    logs_parser.add_argument("--limit", type=int, default=10, help="Maximum number of logs to return")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("action", choices=["list", "get", "set"], help="Action to perform")
    config_parser.add_argument("key", nargs="?", help="Configuration key")
    config_parser.add_argument("value", nargs="?", help="Configuration value")

    args = parser.parse_args()

    if args.command == "new":
        new_command(args)
    elif args.command == "resume":
        resume_command(args)
    elif args.command == "list":
        list_command(args)
    elif args.command == "get":
        get_command(args)
    elif args.command == "logs":
        logs_command(args)
    elif args.command == "config":
        config_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

