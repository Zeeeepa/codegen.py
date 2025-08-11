"""
Real agent performance analytics command
"""

import argparse
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from ..codegen_client import CodegenClient
from ..config import Config

def execute_analytics_command(args: argparse.Namespace) -> int:
    """Execute real analytics command"""
    
    print(f"📊 **Real Agent Performance Analytics**")
    print(f"📅 Analysis period: {args.period}")
    
    # Initialize real client
    try:
        config = Config()
        client = CodegenClient(config)
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        print("💡 Make sure CODEGEN_API_TOKEN and CODEGEN_ORG_ID are set")
        return 1
    
    try:
        # Get real agent runs
        runs = client.list_agent_runs(limit=1000)  # Get more data for analytics
        
        if not runs:
            print("📭 No agent runs found for analysis")
            return 0
        
        # Filter by period
        filtered_runs = filter_runs_by_period(runs, args.period)
        
        if not filtered_runs:
            print(f"📭 No agent runs found for period: {args.period}")
            return 0
        
        print(f"\n📈 **REAL ANALYTICS DATA** ({len(filtered_runs)} runs analyzed)")
        print("=" * 60)
        
        # Calculate real metrics
        analytics = calculate_real_analytics(filtered_runs)
        
        # Display summary
        print("📊 **SUMMARY:**")
        print(f"   Total runs: {analytics['total_runs']}")
        print(f"   Success rate: {analytics['success_rate']:.1%}")
        print(f"   Failed runs: {analytics['failed_runs']}")
        print(f"   Running/Pending: {analytics['active_runs']}")
        
        # Display by status
        print("\n📋 **BY STATUS:**")
        for status, count in analytics['by_status'].items():
            emoji = get_status_emoji(status)
            percentage = (count / analytics['total_runs']) * 100
            print(f"   {emoji} {status.upper()}: {count} ({percentage:.1f}%)")
        
        # Display recent activity
        print("\n🕐 **RECENT ACTIVITY:**")
        recent_runs = sorted(filtered_runs, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
        
        print(f"{'ID':<8} {'STATUS':<12} {'CREATED':<20} {'RESULT':<40}")
        print("-" * 80)
        
        for run in recent_runs:
            run_id = str(run.get('id', 'N/A'))[:7]
            status = run.get('status', 'unknown')[:11]
            created = run.get('created_at', 'N/A')[:19]
            result = (run.get('result', 'No result') or 'In progress')[:39]
            
            emoji = get_status_emoji(status)
            print(f"{run_id:<8} {emoji} {status:<10} {created:<20} {result:<40}")
        
        # Export if requested
        if args.export:
            export_analytics(analytics, filtered_runs, args.export, args.format)
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to fetch analytics: {e}")
        return 1

def filter_runs_by_period(runs: List[Dict], period: str) -> List[Dict]:
    """Filter runs by time period"""
    
    now = datetime.now()
    
    if period == "hour":
        cutoff = now - timedelta(hours=1)
    elif period == "day":
        cutoff = now - timedelta(days=1)
    elif period == "week":
        cutoff = now - timedelta(weeks=1)
    elif period == "month":
        cutoff = now - timedelta(days=30)
    else:
        return runs  # Return all if period not recognized
    
    filtered = []
    for run in runs:
        created_str = run.get('created_at', '')
        if created_str:
            try:
                # Parse ISO format datetime
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                if created >= cutoff:
                    filtered.append(run)
            except:
                # If parsing fails, include the run
                filtered.append(run)
    
    return filtered

def calculate_real_analytics(runs: List[Dict]) -> Dict[str, Any]:
    """Calculate real analytics from agent runs"""
    
    total_runs = len(runs)
    
    # Count by status
    by_status = {}
    completed_runs = 0
    failed_runs = 0
    active_runs = 0
    
    for run in runs:
        status = run.get('status', 'unknown')
        by_status[status] = by_status.get(status, 0) + 1
        
        if status == 'completed':
            completed_runs += 1
        elif status == 'failed':
            failed_runs += 1
        elif status in ['running', 'pending']:
            active_runs += 1
    
    success_rate = completed_runs / total_runs if total_runs > 0 else 0
    
    return {
        'total_runs': total_runs,
        'completed_runs': completed_runs,
        'failed_runs': failed_runs,
        'active_runs': active_runs,
        'success_rate': success_rate,
        'by_status': by_status
    }

def export_analytics(analytics: Dict, runs: List[Dict], filename: str, format: str) -> None:
    """Export analytics data"""
    
    export_data = {
        'generated_at': datetime.now().isoformat(),
        'analytics': analytics,
        'runs': runs
    }
    
    print(f"\n💾 Exporting analytics to: {filename}")
    
    if format == "json":
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print("✅ JSON export completed")
    else:
        print(f"🚧 {format.upper()} export not yet implemented")

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

