"""
Real-time agent monitoring dashboard
"""

import argparse
import time
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from ..codegen_client import CodegenClient
from ..config import Config

def execute_monitor_command(args: argparse.Namespace) -> int:
    """Execute real agent monitoring command"""
    
    print(f"📈 **Real-Time Agent Management Dashboard**")
    
    # Initialize real client
    try:
        config = Config()
        client = CodegenClient(config)
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        print("💡 Make sure CODEGEN_API_TOKEN and CODEGEN_ORG_ID are set")
        return 1
    
    if args.dashboard:
        return launch_dashboard(client, args)
    
    if args.tasks:
        task_ids = [task.strip() for task in args.tasks.split(',')]
        return monitor_specific_tasks(client, task_ids, args)
    
    return monitor_all_tasks(client, args)

def launch_dashboard(client: CodegenClient, args: argparse.Namespace) -> int:
    """Launch interactive dashboard"""
    
    print("🖥️  **AGENT MANAGEMENT DASHBOARD**")
    print("=" * 60)
    
    try:
        while True:
            # Clear screen (works on most terminals)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🤖 **CODEGEN AGENT MANAGEMENT DASHBOARD**")
            print("=" * 60)
            print(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Get real agent runs
            try:
                runs = client.list_agent_runs(limit=20)
                
                if not runs:
                    print("📭 No agent runs found")
                else:
                    print(f"📊 **ACTIVE AGENT RUNS** ({len(runs)} total)")
                    print("-" * 60)
                    
                    # Group by status
                    status_counts = {}
                    for run in runs:
                        status = run.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Display status summary
                    print("📈 **STATUS SUMMARY:**")
                    for status, count in status_counts.items():
                        emoji = get_status_emoji(status)
                        print(f"   {emoji} {status.upper()}: {count}")
                    print()
                    
                    # Display recent runs
                    print("📋 **RECENT AGENT RUNS:**")
                    print(f"{'ID':<8} {'STATUS':<12} {'CREATED':<20} {'RESULT':<30}")
                    print("-" * 70)
                    
                    for run in runs[:10]:  # Show top 10
                        run_id = str(run.get('id', 'N/A'))[:7]
                        status = run.get('status', 'unknown')[:11]
                        created = run.get('created_at', 'N/A')[:19]
                        result = (run.get('result', 'No result') or 'In progress')[:29]
                        
                        emoji = get_status_emoji(status)
                        print(f"{run_id:<8} {emoji} {status:<10} {created:<20} {result:<30}")
                
            except Exception as e:
                print(f"❌ Failed to fetch agent runs: {e}")
            
            print()
            print("🔄 Press Ctrl+C to exit | Refreshing every 5 seconds...")
            print("=" * 60)
            
            time.sleep(args.refresh)
            
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed")
        return 0

def monitor_specific_tasks(client: CodegenClient, task_ids: List[str], args: argparse.Namespace) -> int:
    """Monitor specific tasks"""
    
    print(f"🎯 **Monitoring specific tasks: {', '.join(task_ids)}**")
    
    try:
        while True:
            print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - Checking task status...")
            
            for task_id in task_ids:
                try:
                    run = client.get_agent_run(int(task_id))
                    status = run.get('status', 'unknown')
                    emoji = get_status_emoji(status)
                    
                    print(f"   {emoji} Task {task_id}: {status}")
                    
                    if status in ['completed', 'failed']:
                        result = run.get('result', 'No result')
                        print(f"      Result: {result[:100]}...")
                        
                except Exception as e:
                    print(f"   ❌ Task {task_id}: Error - {e}")
            
            time.sleep(args.refresh)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
        return 0

def monitor_all_tasks(client: CodegenClient, args: argparse.Namespace) -> int:
    """Monitor all active tasks"""
    
    print("🌐 **Monitoring all active tasks**")
    
    try:
        while True:
            print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - Checking all tasks...")
            
            try:
                runs = client.list_agent_runs(limit=50)
                
                # Filter active runs
                active_runs = [run for run in runs if run.get('status') in ['running', 'pending']]
                
                if not active_runs:
                    print("   📭 No active tasks")
                else:
                    print(f"   📊 {len(active_runs)} active tasks:")
                    
                    for run in active_runs[:10]:  # Show top 10
                        run_id = run.get('id', 'N/A')
                        status = run.get('status', 'unknown')
                        emoji = get_status_emoji(status)
                        created = run.get('created_at', 'N/A')
                        
                        print(f"      {emoji} #{run_id} - {status} (created: {created})")
                
            except Exception as e:
                print(f"   ❌ Error fetching tasks: {e}")
            
            if args.export:
                # Export current state
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "active_runs": active_runs if 'active_runs' in locals() else []
                }
                
                with open(args.export, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                print(f"   💾 Data exported to {args.export}")
            
            time.sleep(args.refresh)
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
        return 0

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    status_emojis = {
        'running': '🔄',
        'pending': '⏳',
        'completed': '✅',
        'failed': '❌',
        'cancelled': '⏹️',
        'paused': '⏸️'
    }
    return status_emojis.get(status.lower(), '❓')

