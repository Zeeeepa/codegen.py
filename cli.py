#!/usr/bin/env python3
"""
CodegenAPI CLI - Command Line Interface for Codegen Agents
"""

import os
import sys
import time
import argparse
import json
from typing import Optional, Dict, Any
from codegen_api import Agent, AgentTask, CodegenAPIError

# Task types with descriptions
TASK_TYPES = {
    # Planning & Analysis
    "PLAN_CREATION": "Create comprehensive development plans",
    "PLAN_EVALUATION": "Evaluate and assess existing plans",
    "PLAN_MODIFICATION": "Modify and update development plans",
    "CODEBASE_ANALYSIS": "Deep codebase structure analysis (includes code quality review)",
    
    # Development & Implementation
    "FEATURE_IMPLEMENTATION": "Implement new features from requirements",
    "BUG_FIX": "Fix identified bugs and issues",
    "CODE_RESTRUCTURE": "Refactor code for better structure/performance",
    "CODE_OPTIMIZATION": "Optimize code for performance",
    "API_CREATION": "Create REST/GraphQL APIs",
    "DATABASE_SCHEMA_DESIGN": "Design and modify database schemas",
    "CODEMOD_RUN": "Run large-scale code transformations",
    
    # Testing & Quality
    "TEST_GENERATION": "Generate unit, integration, and e2e tests",
    "TEST_COVERAGE_IMPROVEMENT": "Improve test coverage",
    
    # Documentation
    "DOCUMENTATION_GENERATION": "Generate API docs, README files, etc.",
    "CODE_COMMENTS": "Add meaningful code comments and docstrings",
    "CHANGELOG_GENERATION": "Generate changelogs from commits",
    "TECHNICAL_SPECIFICATION": "Create technical specifications",
    
    # DevOps & Infrastructure
    "CI_CD_SETUP": "Set up CI/CD pipelines",
    "GITHUB_WORKFLOW_CREATION": "Create GitHub Actions workflows",
    "GITHUB_WORKFLOW_EVALUATION": "Evaluate existing workflows",
    "GITHUB_WORKFLOW_MODIFICATION": "Modify GitHub workflows",
    "DOCKER_CONFIGURATION": "Create/modify Docker configurations",
    "DEPLOYMENT_SCRIPTS": "Create deployment automation",
    
    # Integration
    "THIRD_PARTY_INTEGRATION": "Integrate external services/APIs"
}

class CodegenCLI:
    def __init__(self):
        self.agent = None
        self.config_file = os.path.expanduser("~/.codegenapi.json")
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or environment variables"""
        config = {}
        
        # Try to load from config file
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load config file: {e}")
        
        # Get from environment variables or config file
        self.token = config.get('token') or os.getenv('CODEGEN_API_TOKEN')
        self.org_id = config.get('org_id') or os.getenv('CODEGEN_ORG_ID')
        self.base_url = config.get('base_url') or "https://api.codegen.com"
        
        # Initialize agent if we have credentials
        if self.token and self.org_id:
            try:
                self.agent = Agent(
                    token=self.token,
                    org_id=int(self.org_id),
                    base_url=self.base_url
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize agent: {e}")
    
    def save_config(self, token: str, org_id: str, base_url: Optional[str] = None):
        """Save configuration to file"""
        config = {
            'token': token,
            'org_id': org_id,
            'base_url': base_url or "https://api.codegen.com"
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def build_prompt(self, repo_url: str, task_type: str, query: str, branch: Optional[str] = None, pr: Optional[int] = None) -> str:
        """Build a comprehensive prompt for the agent"""
        
        # Get task description
        task_description = TASK_TYPES.get(task_type, "Perform the requested task")
        
        # Build context
        context_parts = [f"Repository: {repo_url}"]
        
        if pr:
            context_parts.append(f"Target: Pull Request #{pr}")
        elif branch:
            context_parts.append(f"Target: Branch '{branch}'")
        else:
            context_parts.append("Target: Default branch")
        
        context = " | ".join(context_parts)
        
        # Build the full prompt
        prompt = f"""Task Type: {task_type} - {task_description}

Context: {context}

Request: {query}

Please analyze the repository and {task_description.lower()}. Provide detailed results and create any necessary pull requests or documentation."""
        
        return prompt
    
    def run_task(self, repo_url: str, task_type: str, query: str, branch: Optional[str] = None, pr: Optional[int] = None, test_mode: bool = False) -> Optional[AgentTask]:
        """Run a new task"""
        if not self.agent and not test_mode:
            print("❌ Error: Agent not initialized. Please run 'codegenapi config' first.")
            sys.exit(1)
        
        if task_type not in TASK_TYPES:
            print(f"❌ Error: Unknown task type '{task_type}'")
            print(f"Available task types: {', '.join(TASK_TYPES.keys())}")
            sys.exit(1)
        
        # Build the prompt
        prompt = self.build_prompt(repo_url, task_type, query, branch, pr)
        
        print(f"🚀 Starting task: {task_type}")
        print(f"📂 Repository: {repo_url}")
        if pr:
            print(f"🔀 Pull Request: #{pr}")
        elif branch:
            print(f"🌿 Branch: {branch}")
        print(f"📝 Query: {query}")
        print()
        
        if test_mode:
            print("🧪 TEST MODE: Simulating task execution...")
            print(f"📋 Task ID: 12345 (simulated)")
            print(f"📊 Initial Status: queued")
            print("⏳ Waiting for completion...")
            
            # Simulate task progression
            statuses = ["queued", "in_progress", "in_progress", "completed"]
            for i, status in enumerate(statuses):
                print(f"   Status: {status}")
                if i < len(statuses) - 1:
                    time.sleep(1)  # Shorter delay for demo
            
            print()
            print(f"✅ Final Status: completed")
            print(f"🎉 Task completed successfully!")
            print(f"🔗 View details: https://codegen.com/agent/run/12345")
            print("📋 Pull Requests created:")
            print(f"   - PR #456: Implement {task_type.lower().replace('_', ' ')}")
            print(f"     URL: https://github.com/example/repo/pull/456")
            print(f"📄 Result:")
            print(f"Successfully completed {TASK_TYPES[task_type].lower()} for {repo_url}")
            print(f"Generated comprehensive solution based on: {query}")
            
            return None
        
        try:
            # Run the task
            task = self.agent.run(prompt=prompt)
            
            print(f"📋 Task ID: {task.id}")
            print(f"📊 Initial Status: {task.status}")
            
            # Poll for completion
            print("⏳ Waiting for completion...")
            while task.status in ["queued", "in_progress", "ACTIVE", "PENDING"]:
                print(f"   Status: {task.status}")
                time.sleep(5)
                task.refresh()
            
            # Final result
            print()
            print(f"✅ Final Status: {task.status}")
            
            if task.status in ["completed", "COMPLETED"]:
                print(f"🎉 Task completed successfully!")
                if task.web_url:
                    print(f"🔗 View details: {task.web_url}")
                if task.github_pull_requests:
                    print("📋 Pull Requests created:")
                    for pr in task.github_pull_requests:
                        print(f"   - PR #{pr.id}: {pr.title}")
                        print(f"     URL: {pr.url}")
                if task.result:
                    print(f"📄 Result:")
                    print(task.result)
            else:
                print(f"❌ Task failed with status: {task.status}")
                if task.result:
                    print(f"Error details: {task.result}")
            
            return task
            
        except CodegenAPIError as e:
            print(f"❌ API Error: {e.message}")
            if e.status_code:
                print(f"Status Code: {e.status_code}")
            print()
            print("💡 Tip: If you're testing the CLI, try using --test-mode flag")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print()
            print("💡 Tip: If you're testing the CLI, try using --test-mode flag")
            sys.exit(1)
    
    def get_task_status(self, task_id: int):
        """Get status of a specific task"""
        if not self.agent:
            print("❌ Error: Agent not initialized. Please run 'codegenapi config' first.")
            sys.exit(1)
        
        try:
            # Get the task
            agent_run = self.agent.client.get_agent_run(self.agent.org_id, task_id)
            task = AgentTask(self.agent.client, self.agent.org_id, task_id, agent_run)
            
            print(f"📋 Task ID: {task.id}")
            print(f"📊 Status: {task.status}")
            if task.web_url:
                print(f"🔗 View details: {task.web_url}")
            if task.result and task.status == "completed":
                print(f"📄 Result:")
                print(task.result)
                
        except CodegenAPIError as e:
            print(f"❌ API Error: {e.message}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def resume_task(self, task_id: int, message: str):
        """Resume a paused task"""
        if not self.agent:
            print("❌ Error: Agent not initialized. Please run 'codegenapi config' first.")
            sys.exit(1)
        
        try:
            # Get the task
            agent_run = self.agent.client.get_agent_run(self.agent.org_id, task_id)
            task = AgentTask(self.agent.client, self.agent.org_id, task_id, agent_run)
            
            print(f"🔄 Resuming task {task_id} with message: {message}")
            
            # Resume the task
            result = task.resume(message)
            
            print(f"✅ Task resumed successfully")
            print(f"📊 Status: {result.status}")
            
        except CodegenAPIError as e:
            print(f"❌ API Error: {e.message}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def list_tasks(self, limit: int = 10):
        """List recent tasks"""
        if not self.agent:
            print("❌ Error: Agent not initialized. Please run 'codegenapi config' first.")
            sys.exit(1)
        
        try:
            runs = self.agent.client.list_agent_runs(self.agent.org_id, limit=limit)
            
            if not runs.items:
                print("📭 No tasks found")
                return
            
            print(f"📋 Recent tasks (showing {len(runs.items)} of {runs.total}):")
            print()
            
            for run in runs.items:
                print(f"ID: {run.id} | Status: {run.status} | Created: {run.created_at}")
                if run.web_url:
                    print(f"   🔗 {run.web_url}")
                print()
                
        except CodegenAPIError as e:
            print(f"❌ API Error: {e.message}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def get_task_logs(self, task_id: int):
        """Get logs for a specific task with comprehensive analysis"""
        if not self.agent:
            print("❌ Error: Agent not initialized. Please run 'codegenapi config' first.")
            sys.exit(1)
        
        try:
            logs = self.agent.client.get_agent_run_logs(self.agent.org_id, task_id)
            
            # Display header with outcome detection
            print(f"📋 Logs for task {task_id}:")
            print(f"📊 Status: {logs.status}")
            print(f"📄 Total logs: {logs.total_logs}")
            
            # Show detected outcomes
            outcomes = logs.detected_outcomes
            if outcomes.outcome_markers:
                print(f"🎯 Outcomes: {outcomes.summary}")
                
                # Show specific details
                if outcomes.pr_created and outcomes.pr_urls:
                    print(f"   📋 PRs: {', '.join(outcomes.pr_urls)}")
                if outcomes.plan_created and outcomes.plan_files:
                    print(f"   📝 Plans: {', '.join(outcomes.plan_files)}")
                if outcomes.code_generated and outcomes.code_files:
                    print(f"   💻 Code: {', '.join(outcomes.code_files[:3])}{'...' if len(outcomes.code_files) > 3 else ''}")
                if outcomes.documentation_created and outcomes.doc_files:
                    print(f"   📚 Docs: {', '.join(outcomes.doc_files[:3])}{'...' if len(outcomes.doc_files) > 3 else ''}")
                if outcomes.errors_encountered:
                    print(f"   ❌ Errors: {len(outcomes.error_messages)} found")
            else:
                print(f"🎯 Outcomes: {outcomes.summary}")
            
            print(f"🔧 Tools used: {', '.join(outcomes.tools_used[:5])}{'...' if len(outcomes.tools_used) > 5 else ''}")
            print()
            
            # Display logs with enhanced formatting
            for i, log in enumerate(logs.logs, 1):
                # Format timestamp
                timestamp = log.created_at.split('T')[1][:8] if 'T' in log.created_at else log.created_at
                
                # Message type with emoji
                type_emoji = self._get_message_type_emoji(log.message_type)
                print(f"{i:2d}. [{timestamp}] {type_emoji} {log.message_type}")
                
                # Agent thought
                if log.thought:
                    thought_preview = log.thought[:100] + "..." if len(log.thought) > 100 else log.thought
                    print(f"    💭 {thought_preview}")
                
                # Tool execution
                if log.tool_name:
                    print(f"    🔧 Tool: {log.tool_name}")
                    
                    # Show key tool inputs
                    if log.tool_input:
                        key_inputs = self._extract_key_inputs(log.tool_input)
                        if key_inputs:
                            print(f"    📥 Input: {key_inputs}")
                    
                    # Show tool results
                    if log.tool_output:
                        result_summary = self._extract_tool_result(log.tool_output)
                        if result_summary:
                            print(f"    📤 Output: {result_summary}")
                
                # Observation
                if log.observation:
                    obs_text = str(log.observation)
                    if len(obs_text) > 150:
                        obs_text = obs_text[:150] + "..."
                    print(f"    👁️  Observation: {obs_text}")
                
                print()
                
        except CodegenAPIError as e:
            print(f"❌ API Error: {e.message}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _get_message_type_emoji(self, message_type: str) -> str:
        """Get emoji for message type"""
        emoji_map = {
            "ACTION": "⚡",
            "PLAN_EVALUATION": "🧠",
            "FINAL_ANSWER": "✅",
            "ERROR": "❌",
            "USER_MESSAGE": "💬",
            "USER_GITHUB_ISSUE_COMMENT": "💬",
            "INITIAL_PR_GENERATION": "🔄",
            "DETECT_PR_ERRORS": "🔍",
            "FIX_PR_ERRORS": "🔧",
            "PR_CREATION_FAILED": "❌",
            "PR_EVALUATION": "📋",
            "COMMIT_EVALUATION": "📝",
            "AGENT_RUN_LINK": "🔗"
        }
        return emoji_map.get(message_type, "📝")
    
    def _extract_key_inputs(self, tool_input: dict) -> str:
        """Extract key information from tool input"""
        if not tool_input:
            return ""
        
        # Common important fields
        key_fields = ['path', 'filepath', 'file', 'query', 'prompt', 'message', 'title', 'url']
        
        for field in key_fields:
            if field in tool_input:
                value = str(tool_input[field])
                if len(value) > 50:
                    value = value[:50] + "..."
                return f"{field}={value}"
        
        # If no key fields, show first key-value pair
        if tool_input:
            key, value = next(iter(tool_input.items()))
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:50] + "..."
            return f"{key}={value_str}"
        
        return ""
    
    def _extract_tool_result(self, tool_output: dict) -> str:
        """Extract key information from tool output"""
        if not tool_output:
            return ""
        
        # Look for success indicators
        if 'status' in tool_output:
            status = tool_output['status']
            if status == 'success':
                return "✅ Success"
            elif status == 'error':
                return "❌ Error"
        
        # Look for URLs (PR creation, etc.)
        url_fields = ['url', 'html_url', 'web_url']
        for field in url_fields:
            if field in tool_output:
                return f"🔗 {tool_output[field]}"
        
        # Look for file paths
        if 'path' in tool_output or 'filepath' in tool_output:
            path = tool_output.get('path') or tool_output.get('filepath')
            return f"📁 {path}"
        
        # Look for counts or numbers
        if 'count' in tool_output:
            return f"📊 {tool_output['count']} items"
        
        # Generic success if we have output
        return "✅ Completed"

def main():
    cli = CodegenCLI()
    
    parser = argparse.ArgumentParser(
        description="CodegenAPI CLI - Command Line Interface for Codegen Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available Task Types:
{chr(10).join([f"  {k}: {v}" for k, v in TASK_TYPES.items()])}

Examples:
  codegenapi config --token YOUR_TOKEN --org-id YOUR_ORG_ID
  codegenapi new --repo https://github.com/user/repo --task PLAN_CREATION --query "Create a plan to add user authentication"
  codegenapi new --repo https://github.com/user/repo --branch feature/auth --task FEATURE_IMPLEMENTATION --query "Implement JWT authentication"
  codegenapi status --task-id 12345
  codegenapi resume --task-id 12345 --message "Please also include error handling"
  codegenapi list --limit 10
  codegenapi logs --task-id 12345
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configure API credentials')
    config_parser.add_argument('--token', help='API token')
    config_parser.add_argument('--org-id', help='Organization ID')
    config_parser.add_argument('--base-url', help='Base URL (optional)')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    
    # New task command
    new_parser = subparsers.add_parser('new', help='Start a new task')
    new_parser.add_argument('--repo', required=True, help='Repository URL')
    new_parser.add_argument('--branch', help='Target branch (optional)')
    new_parser.add_argument('--pr', type=int, help='Target PR number (optional)')
    new_parser.add_argument('--task', required=True, choices=list(TASK_TYPES.keys()), help='Task type')
    new_parser.add_argument('--query', required=True, help='Task description/query')
    new_parser.add_argument('--test-mode', action='store_true', help='Run in test mode (simulate execution)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check task status')
    status_parser.add_argument('--task-id', type=int, required=True, help='Task ID')
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume a paused task')
    resume_parser.add_argument('--task-id', type=int, required=True, help='Task ID')
    resume_parser.add_argument('--message', required=True, help='Resume message')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent tasks')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of tasks to show')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='View task logs')
    logs_parser.add_argument('--task-id', type=int, required=True, help='Task ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle commands
    if args.command == 'config':
        if args.show:
            print(f"📋 Current Configuration:")
            print(f"   Token: {'***' + cli.token[-4:] if cli.token else 'Not set'}")
            print(f"   Org ID: {cli.org_id or 'Not set'}")
            print(f"   Base URL: {cli.base_url}")
            print(f"   Config file: {cli.config_file}")
        elif args.token and args.org_id:
            cli.save_config(args.token, args.org_id, args.base_url)
            cli.load_config()  # Reload to initialize agent
        else:
            print("❌ Error: Both --token and --org-id are required")
            sys.exit(1)
    
    elif args.command == 'new':
        if args.branch and args.pr:
            print("❌ Error: Cannot specify both --branch and --pr")
            sys.exit(1)
        cli.run_task(args.repo, args.task, args.query, args.branch, args.pr, getattr(args, 'test_mode', False))
    
    elif args.command == 'status':
        cli.get_task_status(args.task_id)
    
    elif args.command == 'resume':
        cli.resume_task(args.task_id, args.message)
    
    elif args.command == 'list':
        cli.list_tasks(args.limit)
    
    elif args.command == 'logs':
        cli.get_task_logs(args.task_id)

if __name__ == '__main__':
    main()
