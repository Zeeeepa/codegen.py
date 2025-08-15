#!/usr/bin/env python3
"""
Simple Agent Interface Example

This example demonstrates the easiest way to use the Codegen SDK
with the simplified Agent interface.
"""

import os
import sys
import time

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.api import Agent, ClientConfig

def main():
    """Simple Agent interface example"""
    print("🤖 Simple Agent Interface Example")
    print("=" * 50)
    
    # Configuration
    org_id = int(os.getenv("CODEGEN_ORG_ID", "323"))
    api_token = os.getenv("CODEGEN_API_TOKEN", "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99")
    
    try:
        # Create agent with configuration
        config = ClientConfig(
            api_token=api_token,
            org_id=str(org_id),
            log_level="INFO"
        )
        
        with Agent(org_id=org_id, token=api_token, config=config) as agent:
            print("✅ Agent initialized successfully")
            
            # Create a simple task
            print("\n📝 Creating task...")
            task = agent.run("What are the benefits of using Python for web development? List 3 key points.")
            
            print(f"✅ Task created: {task.id}")
            print(f"🌐 Web URL: {task.web_url}")
            print(f"📊 Initial status: {task.status}")
            
            # Monitor task progress
            print("\n⏱️  Monitoring task progress...")
            max_wait = 60  # 1 minute
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                task.refresh()
                elapsed = time.time() - start_time
                print(f"   [{elapsed:.1f}s] Status: {task.status}")
                
                if task.status in ["COMPLETE", "completed", "failed", "cancelled"]:
                    print(f"🏁 Task finished: {task.status}")
                    break
                
                time.sleep(3)  # Check every 3 seconds
            
            # Get final result
            print(f"\n📝 Final Result:")
            if task.result:
                print(f"   {task.result}")
                print("✅ Task completed successfully!")
            else:
                print("   ⚠️  No result available")
            
            # Get logs
            try:
                logs = task.get_logs()
                print(f"\n📋 Log Summary:")
                print(f"   Total logs: {logs.total_logs}")
                
                if logs.logs:
                    log_types = {}
                    for log in logs.logs:
                        log_types[log.message_type] = log_types.get(log.message_type, 0) + 1
                    
                    print(f"   Log types: {dict(log_types)}")
                
            except Exception as e:
                print(f"   ❌ Error getting logs: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

