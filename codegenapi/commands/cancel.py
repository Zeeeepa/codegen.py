"""
Real task cancellation command
"""

import argparse
from typing import List
from ..codegen_client import CodegenClient
from ..config import Config

def execute_cancel_command(args: argparse.Namespace) -> int:
    """Execute real task cancellation command"""
    
    print(f"❌ **Real Task Cancellation**")
    print(f"🎯 Task IDs: {args.task_ids}")
    
    # Initialize real client
    try:
        config = Config()
        client = CodegenClient(config)
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        print("💡 Make sure CODEGEN_API_TOKEN and CODEGEN_ORG_ID are set")
        return 1
    
    if args.reason:
        print(f"📝 Reason: {args.reason}")
    
    if args.force:
        print("⚠️  Force cancellation enabled")
    
    success_count = 0
    failed_count = 0
    
    print("\n🔄 **Cancelling Tasks:**")
    
    for task_id in args.task_ids:
        try:
            print(f"📋 Processing task {task_id}...")
            
            # Get task info first
            run_info = client.get_agent_run(int(task_id))
            
            if not run_info:
                print(f"   ❌ Task {task_id} not found")
                failed_count += 1
                continue
            
            current_status = run_info.get('status', 'unknown')
            
            if current_status in ['completed', 'failed', 'cancelled']:
                print(f"   ⚠️  Task {task_id} is already {current_status}")
                continue
            
            # Attempt cancellation
            if client.cancel_agent_run(int(task_id)):
                print(f"   ✅ Task {task_id} cancelled successfully")
                success_count += 1
            else:
                print(f"   ❌ Failed to cancel task {task_id}")
                failed_count += 1
                
        except ValueError:
            print(f"   ❌ Invalid task ID: {task_id}")
            failed_count += 1
        except Exception as e:
            print(f"   ❌ Error cancelling task {task_id}: {e}")
            failed_count += 1
    
    print(f"\n📊 **Cancellation Summary:**")
    print(f"   ✅ Successfully cancelled: {success_count}")
    print(f"   ❌ Failed to cancel: {failed_count}")
    print(f"   📊 Total processed: {len(args.task_ids)}")
    
    if failed_count > 0:
        print("\n💡 Some cancellations failed. Possible reasons:")
        print("   - Task ID doesn't exist")
        print("   - Task already completed/failed")
        print("   - Network/API issues")
        print("   - Insufficient permissions")
    
    return 0 if failed_count == 0 else 1

