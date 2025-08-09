#!/usr/bin/env python3
"""
Real-time Monitoring Example

This example demonstrates how to monitor agent runs in real-time,
showing live updates of status, logs, and progress.
"""

import os
import sys
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.api import CodegenClient, ClientConfig

def monitor_agent_run(client, org_id, run_id, poll_interval=1.0, max_wait=300):
    """
    Monitor an agent run in real-time with detailed progress tracking
    
    Args:
        client: CodegenClient instance
        org_id: Organization ID
        run_id: Agent run ID to monitor
        poll_interval: How often to check for updates (seconds)
        max_wait: Maximum time to wait (seconds)
    
    Returns:
        Final agent run state
    """
    print(f"🔍 Starting real-time monitoring of agent run {run_id}")
    print(f"⏱️  Polling every {poll_interval}s, max wait time: {max_wait}s")
    
    start_time = time.time()
    last_status = None
    last_log_count = 0
    status_changes = []
    
    while time.time() - start_time < max_wait:
        try:
            # Get current run state
            current_run = client.get_agent_run(org_id, run_id)
            elapsed = time.time() - start_time
            
            # Track status changes
            if current_run.status != last_status:
                status_changes.append({
                    "time": elapsed,
                    "status": current_run.status,
                    "previous": last_status
                })
                print(f"🔄 [{elapsed:.1f}s] Status changed: {last_status} → {current_run.status}")
                last_status = current_run.status
            
            # Get current logs
            try:
                logs = client.get_agent_run_logs(org_id, run_id, limit=100)
                current_log_count = logs.total_logs or 0
                
                # Show new logs
                if current_log_count > last_log_count:
                    new_logs = current_log_count - last_log_count
                    print(f"📝 [{elapsed:.1f}s] Found {new_logs} new logs (total: {current_log_count})")
                    
                    # Show details of new logs
                    if logs.logs:
                        for log in logs.logs[-(new_logs):]:  # Show only new logs
                            log_time = log.created_at.split('T')[1][:8] if 'T' in log.created_at else log.created_at
                            tool_info = f" - {log.tool_name}" if log.tool_name else ""
                            print(f"    📋 [{log_time}] {log.message_type}{tool_info}")
                            
                            if log.thought:
                                thought_preview = log.thought[:80] + "..." if len(log.thought) > 80 else log.thought
                                print(f"       💭 {thought_preview}")
                    
                    last_log_count = current_log_count
                
            except Exception as e:
                print(f"    ❌ Error getting logs: {str(e)}")
            
            # Check if completed
            if current_run.status in ["COMPLETE", "completed", "failed", "cancelled"]:
                print(f"🏁 [{elapsed:.1f}s] Agent run finished: {current_run.status}")
                
                # Show final result
                if current_run.result:
                    result_length = len(current_run.result)
                    print(f"📝 Final result ({result_length} chars):")
                    
                    # Show preview of result
                    if result_length > 200:
                        preview = current_run.result[:200] + "..."
                        print(f"    {preview}")
                        print(f"    ... (truncated, full result available)")
                    else:
                        print(f"    {current_run.result}")
                else:
                    print("    ⚠️  No result available")
                
                return current_run
            
            # Show periodic progress updates
            if int(elapsed) % 10 == 0 and elapsed > 0:  # Every 10 seconds
                print(f"⏳ [{elapsed:.1f}s] Still monitoring... Status: {current_run.status}, Logs: {current_log_count}")
            
            time.sleep(poll_interval)
            
        except Exception as e:
            print(f"❌ Error during monitoring: {str(e)}")
            time.sleep(poll_interval)
    
    # Timeout reached
    final_run = client.get_agent_run(org_id, run_id)
    print(f"⏰ Monitoring timeout reached after {max_wait}s")
    print(f"   Final status: {final_run.status}")
    
    return final_run

def main():
    """Real-time monitoring example"""
    print("⏱️  Real-time Agent Run Monitoring Example")
    print("=" * 60)
    
    # Configuration
    org_id = int(os.getenv("CODEGEN_ORG_ID", "323"))
    api_token = os.getenv("CODEGEN_API_TOKEN", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
    
    try:
        config = ClientConfig(
            api_token=api_token,
            org_id=str(org_id),
            log_level="INFO"
        )
        
        with CodegenClient(config) as client:
            print("✅ CodegenClient initialized successfully")
            
            # Create a task that will take some time
            print(f"\n🚀 Creating agent run for monitoring...")
            run = client.create_agent_run(
                org_id=org_id,
                prompt="""Create a comprehensive Python web scraping tutorial that covers:
1. Setting up the environment (requests, BeautifulSoup, selenium)
2. Basic HTML parsing techniques
3. Handling forms and authentication
4. Dealing with JavaScript-rendered content
5. Best practices and ethical considerations
6. Error handling and rate limiting
7. Example project: scraping a news website

Please provide detailed code examples and explanations for each section.""",
                metadata={
                    "example": "real_time_monitoring",
                    "timestamp": datetime.now().isoformat(),
                    "expected_duration": "long"
                }
            )
            
            print(f"✅ Agent run created: {run.id}")
            print(f"🌐 Web URL: {run.web_url}")
            print(f"📊 Initial status: {run.status}")
            
            # Start real-time monitoring
            final_run = monitor_agent_run(
                client=client,
                org_id=org_id,
                run_id=run.id,
                poll_interval=1.0,  # Check every second
                max_wait=300  # Wait up to 5 minutes
            )
            
            # Final summary
            print(f"\n📊 Monitoring Summary:")
            print(f"   Final status: {final_run.status}")
            print(f"   Result available: {'Yes' if final_run.result else 'No'}")
            
            if final_run.result:
                print(f"   Result length: {len(final_run.result)} characters")
            
            # Get final log count
            try:
                final_logs = client.get_agent_run_logs(org_id, run.id, limit=100)
                print(f"   Total logs generated: {final_logs.total_logs}")
                
                # Analyze log types
                if final_logs.logs:
                    log_types = {}
                    tools_used = set()
                    
                    for log in final_logs.logs:
                        log_types[log.message_type] = log_types.get(log.message_type, 0) + 1
                        if log.tool_name:
                            tools_used.add(log.tool_name)
                    
                    print(f"   Log types: {dict(log_types)}")
                    print(f"   Tools used: {', '.join(sorted(tools_used)) if tools_used else 'None'}")
                
            except Exception as e:
                print(f"   ❌ Error getting final logs: {str(e)}")
            
            print(f"\n✅ Real-time monitoring example completed!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

