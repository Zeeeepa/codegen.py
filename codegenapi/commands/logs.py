"""
Real task execution logs command
"""

import argparse
import json
import time
from datetime import datetime
from typing import List, Dict, Any
from ..codegen_client import CodegenClient
from ..config import Config

def execute_logs_command(args: argparse.Namespace) -> int:
    """Execute real logs command"""
    
    print(f"📜 **Real Task Execution Logs**")
    print(f"🎯 Task ID: {args.task_id}")
    
    # Initialize real client
    try:
        config = Config()
        client = CodegenClient(config)
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        print("💡 Make sure CODEGEN_API_TOKEN and CODEGEN_ORG_ID are set")
        return 1
    
    try:
        # Get real logs from API
        logs = client.get_agent_run_logs(int(args.task_id))
        
        if not logs:
            print("📭 No logs found for this task")
            return 0
        
        # Filter logs
        filtered_logs = filter_logs(logs, args)
        
        if not filtered_logs:
            print("📭 No logs match the specified filters")
            return 0
        
        # Display logs
        display_logs(filtered_logs, args)
        
        # Follow mode
        if args.follow:
            follow_logs(client, int(args.task_id), args)
        
        # Export if requested
        if args.export:
            export_logs(filtered_logs, args.export, args.format)
        
        return 0
        
    except ValueError:
        print(f"❌ Invalid task ID: {args.task_id}")
        return 1
    except Exception as e:
        print(f"❌ Failed to fetch logs: {e}")
        return 1

def filter_logs(logs: List[Dict], args: argparse.Namespace) -> List[Dict]:
    """Filter logs based on arguments"""
    
    filtered = logs
    
    # Filter by level
    if args.level:
        filtered = [log for log in filtered if log.get('level', '').lower() == args.level.lower()]
    
    # Filter by pattern
    if args.grep:
        filtered = [log for log in filtered if args.grep.lower() in log.get('message', '').lower()]
    
    # Limit number of lines
    if args.lines and args.lines < len(filtered):
        filtered = filtered[-args.lines:]  # Get last N lines
    
    return filtered

def display_logs(logs: List[Dict], args: argparse.Namespace) -> None:
    """Display logs in specified format"""
    
    print(f"\n📊 **REAL LOGS** ({len(logs)} entries)")
    print("=" * 80)
    
    for log in logs:
        if args.format == "json":
            print(json.dumps(log, indent=2))
        else:
            timestamp = log.get('timestamp', 'N/A')
            level = log.get('level', 'INFO').ljust(7)
            component = log.get('component', 'system').ljust(12)
            message = log.get('message', 'No message')
            
            print(f"{timestamp} {level} [{component}] {message}")

def follow_logs(client: CodegenClient, task_id: int, args: argparse.Namespace) -> None:
    """Follow logs in real-time"""
    
    print(f"\n👀 **Following logs for task {task_id}** (Ctrl+C to stop)")
    print("=" * 60)
    
    last_log_count = 0
    
    try:
        while True:
            # Get updated logs
            logs = client.get_agent_run_logs(task_id)
            
            if len(logs) > last_log_count:
                # Display new logs
                new_logs = logs[last_log_count:]
                filtered_new_logs = filter_logs(new_logs, args)
                
                for log in filtered_new_logs:
                    if args.format == "json":
                        print(json.dumps(log, indent=2))
                    else:
                        timestamp = log.get('timestamp', datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))
                        level = log.get('level', 'INFO').ljust(7)
                        component = log.get('component', 'system').ljust(12)
                        message = log.get('message', 'No message')
                        
                        print(f"{timestamp} {level} [{component}] {message}")
                
                last_log_count = len(logs)
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️  Log following stopped")

def export_logs(logs: List[Dict], filename: str, format: str) -> None:
    """Export logs to file"""
    
    print(f"\n💾 Exporting {len(logs)} log entries to: {filename}")
    
    try:
        with open(filename, 'w') as f:
            if format == "json":
                json.dump(logs, f, indent=2)
            else:
                for log in logs:
                    timestamp = log.get('timestamp', 'N/A')
                    level = log.get('level', 'INFO').ljust(7)
                    component = log.get('component', 'system').ljust(12)
                    message = log.get('message', 'No message')
                    
                    f.write(f"{timestamp} {level} [{component}] {message}\n")
        
        print("✅ Log export completed")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

