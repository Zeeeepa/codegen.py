#!/usr/bin/env python3
"""
Agent Run Analysis Summary

Based on the comprehensive lifecycle test, this script provides analysis
of the agent run behavior and validates the state management issues.
"""

import os
import json
from datetime import datetime
from codegen_sdk_api import CodegenClient, Agent, ClientConfig

# Configuration
CODEGEN_ORG_ID = int(os.getenv("CODEGEN_ORG_ID", "323"))
CODEGEN_API_TOKEN = os.getenv("CODEGEN_API_TOKEN", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")

def analyze_recent_agent_runs():
    """Analyze recent agent runs to understand state management patterns"""
    print("🔍 Analyzing Recent Agent Runs for State Management Patterns")
    print("=" * 70)
    
    config = ClientConfig(api_token=CODEGEN_API_TOKEN, org_id=str(CODEGEN_ORG_ID))
    
    with CodegenClient(config) as client:
        # Get recent agent runs
        runs = client.list_agent_runs(CODEGEN_ORG_ID, limit=10)
        
        print(f"📊 Found {len(runs.items)} recent agent runs:")
        
        for i, run in enumerate(runs.items[:5], 1):  # Analyze top 5
            print(f"\n{i}. Agent Run {run.id}")
            print(f"   Status: {run.status}")
            print(f"   Created: {run.created_at}")
            print(f"   Web URL: {run.web_url}")
            print(f"   Result Length: {len(run.result) if run.result else 0} chars")
            
            # Get logs for this run
            try:
                logs_response = client.get_agent_run_logs(CODEGEN_ORG_ID, run.id, limit=100)
                
                print(f"   Total Logs: {logs_response.total_logs}")
                
                # Analyze log types
                log_types = {}
                has_final_answer = False
                tools_used = set()
                
                for log in logs_response.logs:
                    log_types[log.message_type] = log_types.get(log.message_type, 0) + 1
                    
                    if log.message_type == "FINAL_ANSWER":
                        has_final_answer = True
                    
                    if log.tool_name:
                        tools_used.add(log.tool_name)
                
                print(f"   Log Types: {dict(log_types)}")
                print(f"   Has Final Answer: {'✅' if has_final_answer else '❌'}")
                print(f"   Tools Used: {', '.join(sorted(tools_used)) if tools_used else 'None'}")
                
                # Check for state management issues
                issues = []
                
                if run.status == "ACTIVE" and run.result:
                    issues.append("Status shows ACTIVE but has result")
                
                if run.status == "COMPLETE" and not run.result:
                    issues.append("Status shows COMPLETE but no result")
                
                if not has_final_answer and run.result:
                    issues.append("Has result but no FINAL_ANSWER log")
                
                if has_final_answer and not run.result:
                    issues.append("Has FINAL_ANSWER log but no result")
                
                if issues:
                    print(f"   ⚠️  Issues: {', '.join(issues)}")
                else:
                    print(f"   ✅ No state management issues detected")
                    
            except Exception as e:
                print(f"   ❌ Error getting logs: {str(e)}")

def test_simple_agent_interface():
    """Test the simple Agent interface with a quick task"""
    print("\n🧪 Testing Simple Agent Interface")
    print("=" * 50)
    
    try:
        with Agent(org_id=CODEGEN_ORG_ID, token=CODEGEN_API_TOKEN) as agent:
            print("✅ Agent initialized successfully")
            
            # Create a simple task
            task = agent.run("What is 2 + 2? Please provide a brief answer.")
            print(f"✅ Task created: {task.id}")
            print(f"📊 Initial status: {task.status}")
            print(f"🌐 Web URL: {task.web_url}")
            
            # Wait a bit and check status
            import time
            time.sleep(5)
            
            task.refresh()
            print(f"📊 Status after 5s: {task.status}")
            
            if task.result:
                print(f"📝 Result: {task.result[:200]}{'...' if len(task.result) > 200 else ''}")
            else:
                print("❌ No result yet")
            
            # Get logs
            try:
                logs = task.get_logs()
                print(f"📋 Total logs: {logs.total_logs}")
                
                if logs.logs:
                    print("📝 Recent logs:")
                    for log in logs.logs[-3:]:  # Show last 3 logs
                        timestamp = log.created_at.split('T')[1][:8] if 'T' in log.created_at else log.created_at
                        print(f"   [{timestamp}] {log.message_type}: {log.tool_name or 'No tool'}")
                        if log.thought:
                            print(f"      💭 {log.thought[:80]}{'...' if len(log.thought) > 80 else ''}")
                
            except Exception as e:
                print(f"❌ Error getting logs: {str(e)}")
                
    except Exception as e:
        print(f"❌ Error with Agent interface: {str(e)}")

def test_advanced_client_interface():
    """Test the advanced CodegenClient interface"""
    print("\n🔧 Testing Advanced CodegenClient Interface")
    print("=" * 50)
    
    config = ClientConfig(
        api_token=CODEGEN_API_TOKEN,
        org_id=str(CODEGEN_ORG_ID),
        log_level="INFO",
        enable_caching=True,
        enable_metrics=True
    )
    
    try:
        with CodegenClient(config) as client:
            print("✅ CodegenClient initialized successfully")
            
            # Health check
            health = client.health_check()
            print(f"🏥 Health check: {health['status']} ({health['response_time_seconds']:.3f}s)")
            
            # Get current user
            user = client.get_current_user()
            print(f"👤 Current user: {user.github_username} (ID: {user.id})")
            
            # Create a simple agent run
            run = client.create_agent_run(
                org_id=CODEGEN_ORG_ID,
                prompt="List 3 benefits of using Python for web development. Be concise.",
                metadata={"test": "advanced_client", "timestamp": datetime.now().isoformat()}
            )
            
            print(f"✅ Agent run created: {run.id}")
            print(f"📊 Status: {run.status}")
            print(f"🌐 Web URL: {run.web_url}")
            
            # Monitor for a short time
            import time
            for i in range(10):  # Check for 10 seconds
                time.sleep(1)
                current_run = client.get_agent_run(CODEGEN_ORG_ID, run.id)
                
                if current_run.status != run.status:
                    print(f"🔄 Status changed: {run.status} → {current_run.status}")
                    run = current_run
                
                if current_run.status in ["COMPLETE", "completed", "failed", "cancelled"]:
                    print(f"🏁 Run finished with status: {current_run.status}")
                    break
                
                if i == 9:
                    print(f"⏰ Still running after 10s, status: {current_run.status}")
            
            # Get final logs
            try:
                logs = client.get_agent_run_logs(CODEGEN_ORG_ID, run.id)
                print(f"📋 Final log count: {logs.total_logs}")
                
                # Analyze log types
                log_types = {}
                for log in logs.logs:
                    log_types[log.message_type] = log_types.get(log.message_type, 0) + 1
                
                print(f"📊 Log types: {dict(log_types)}")
                
                # Show final result
                final_run = client.get_agent_run(CODEGEN_ORG_ID, run.id)
                if final_run.result:
                    print(f"📝 Final result: {final_run.result[:200]}{'...' if len(final_run.result) > 200 else ''}")
                else:
                    print("❌ No final result")
                    
            except Exception as e:
                print(f"❌ Error getting final logs: {str(e)}")
            
            # Get client stats
            stats = client.get_stats()
            if "metrics" in stats:
                metrics = stats["metrics"]
                print(f"📈 Client metrics: {metrics['total_requests']} requests, {metrics['error_rate']:.1%} error rate")
                
    except Exception as e:
        print(f"❌ Error with CodegenClient: {str(e)}")

def main():
    """Run all analysis and tests"""
    print("🎯 Codegen SDK - Agent Run Analysis & Validation")
    print("=" * 80)
    
    # Validate configuration
    if not CODEGEN_API_TOKEN:
        print("❌ CODEGEN_API_TOKEN environment variable not set")
        return
    
    if not CODEGEN_ORG_ID:
        print("❌ CODEGEN_ORG_ID environment variable not set")
        return
    
    print(f"🔧 Configuration: ORG_ID={CODEGEN_ORG_ID}")
    print(f"🔑 API Token: {CODEGEN_API_TOKEN[:20]}...")
    
    try:
        # Run analysis and tests
        analyze_recent_agent_runs()
        test_simple_agent_interface()
        test_advanced_client_interface()
        
        print("\n🎉 Analysis and testing completed successfully!")
        
    except Exception as e:
        print(f"\n💥 Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

