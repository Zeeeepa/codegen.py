#!/usr/bin/env python3
"""
Advanced CodegenClient Example

This example demonstrates advanced features of the Codegen SDK including:
- Real-time monitoring with detailed logging
- Configuration presets
- Client statistics and metrics
- Error handling
"""

import os
import sys
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.api import CodegenClient, ClientConfig, ConfigPresets

def main():
    """Advanced CodegenClient example"""
    print("🔧 Advanced CodegenClient Example")
    print("=" * 50)
    
    # Configuration
    org_id = int(os.getenv("CODEGEN_ORG_ID", "323"))
    api_token = os.getenv("CODEGEN_API_TOKEN", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
    
    try:
        # Use development configuration preset
        config = ClientConfig(
            api_token=api_token,
            org_id=str(org_id),
            log_level="INFO",
            enable_caching=True,
            enable_metrics=True,
            timeout=60
        )
        
        with CodegenClient(config) as client:
            print("✅ CodegenClient initialized successfully")
            
            # Health check
            health = client.health_check()
            print(f"🏥 Health check: {health['status']} ({health['response_time_seconds']:.3f}s)")
            
            # Get current user
            user = client.get_current_user()
            print(f"👤 Current user: {user.github_username} (ID: {user.id})")
            
            # Create agent run with metadata
            print(f"\n🚀 Creating agent run...")
            run = client.create_agent_run(
                org_id=org_id,
                prompt="Create a simple Python function that calculates the factorial of a number. Include docstring and example usage.",
                metadata={
                    "example": "advanced_client",
                    "timestamp": datetime.now().isoformat(),
                    "purpose": "code_generation"
                }
            )
            
            print(f"✅ Agent run created: {run.id}")
            print(f"🌐 Web URL: {run.web_url}")
            print(f"📊 Initial status: {run.status}")
            
            # Real-time monitoring with detailed logging
            print(f"\n⏱️  Real-time monitoring...")
            max_wait = 120  # 2 minutes
            start_time = time.time()
            last_log_count = 0
            
            while time.time() - start_time < max_wait:
                # Get current state
                current_run = client.get_agent_run(org_id, run.id)
                
                # Get current logs
                try:
                    logs = client.get_agent_run_logs(org_id, run.id, limit=100)
                    current_log_count = logs.total_logs or 0
                    
                    # Show progress
                    elapsed = time.time() - start_time
                    if current_log_count > last_log_count:
                        new_logs = current_log_count - last_log_count
                        print(f"   [{elapsed:.1f}s] Status: {current_run.status}, Logs: +{new_logs} (total: {current_log_count})")
                        
                        # Show latest log details
                        if logs.logs:
                            latest_log = logs.logs[-1]
                            log_time = latest_log.created_at.split('T')[1][:8] if 'T' in latest_log.created_at else latest_log.created_at
                            tool_info = f" - {latest_log.tool_name}" if latest_log.tool_name else ""
                            print(f"      Latest: [{log_time}] {latest_log.message_type}{tool_info}")
                            
                            if latest_log.thought:
                                thought_preview = latest_log.thought[:60] + "..." if len(latest_log.thought) > 60 else latest_log.thought
                                print(f"      💭 {thought_preview}")
                        
                        last_log_count = current_log_count
                    
                except Exception as e:
                    print(f"   ❌ Log retrieval error: {str(e)}")
                
                # Check completion
                if current_run.status in ["COMPLETE", "completed", "failed", "cancelled"]:
                    print(f"🏁 Run completed: {current_run.status}")
                    final_run = current_run
                    break
                
                time.sleep(2)  # Check every 2 seconds
            else:
                final_run = client.get_agent_run(org_id, run.id)
                print(f"⏰ Timeout reached, final status: {final_run.status}")
            
            # Final analysis
            print(f"\n📊 Final Analysis:")
            print(f"   Status: {final_run.status}")
            print(f"   Result length: {len(final_run.result) if final_run.result else 0} characters")
            
            if final_run.result:
                print(f"\n📝 Generated Code:")
                print("   " + "="*60)
                # Show first 500 characters of result
                result_preview = final_run.result[:500] + "..." if len(final_run.result) > 500 else final_run.result
                print("   " + result_preview.replace('\n', '\n   '))
                print("   " + "="*60)
            
            # Final log analysis
            try:
                final_logs = client.get_agent_run_logs(org_id, run.id, limit=100)
                print(f"\n📋 Log Analysis:")
                print(f"   Total logs: {final_logs.total_logs}")
                
                # Analyze log types and tools
                log_analysis = {}
                tools_used = set()
                
                for log in final_logs.logs:
                    log_analysis[log.message_type] = log_analysis.get(log.message_type, 0) + 1
                    if log.tool_name:
                        tools_used.add(log.tool_name)
                
                print(f"   Log types: {dict(log_analysis)}")
                print(f"   Tools used: {', '.join(sorted(tools_used)) if tools_used else 'None'}")
                
            except Exception as e:
                print(f"   ❌ Final log analysis failed: {str(e)}")
            
            # Client statistics
            stats = client.get_stats()
            print(f"\n📈 Client Statistics:")
            print(f"   Configuration: {stats['config']['base_url']}")
            
            if "metrics" in stats:
                metrics = stats["metrics"]
                print(f"   Total requests: {metrics['total_requests']}")
                print(f"   Average response time: {metrics['average_response_time']:.3f}s")
                print(f"   Error rate: {metrics['error_rate']:.1%}")
            
            if "cache" in stats:
                cache_stats = stats["cache"]
                print(f"   Cache hit rate: {cache_stats['hit_rate_percentage']:.1f}%")
            
            print(f"\n✅ Advanced client example completed successfully!")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

