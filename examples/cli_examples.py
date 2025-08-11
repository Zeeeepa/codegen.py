#!/usr/bin/env python3
"""
CLI usage examples and automation scripts
"""

import subprocess
import sys
import time
import json


def run_cli_command(command):
    """Run a CLI command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def cli_basic_workflow():
    """Demonstrate basic CLI workflow"""
    print("🚀 CLI Basic Workflow Example")
    
    # Check if CLI is available
    returncode, stdout, stderr = run_cli_command("codegen --help")
    if returncode != 0:
        print("❌ Codegen CLI not found. Please install with: pip install codegen-py")
        return
    
    print("✅ Codegen CLI is available")
    
    # Show current configuration
    print("\\n🔧 Current configuration:")
    returncode, stdout, stderr = run_cli_command("codegen config show")
    if returncode == 0:
        print(stdout)
    else:
        print("⚠️ No configuration found. Run 'codegen config init' to set up.")
    
    # List recent tasks
    print("\\n📋 Recent tasks:")
    returncode, stdout, stderr = run_cli_command("codegen status --limit 5")
    if returncode == 0:
        print(stdout)
    else:
        print(f"❌ Failed to get task status: {stderr}")


def cli_task_automation():
    """Demonstrate task automation with CLI"""
    print("\\n🤖 CLI Task Automation Example")
    
    # Run a simple task
    print("Running automated task...")
    command = 'codegen run "What is the current date and time?" --wait --timeout 60'
    returncode, stdout, stderr = run_cli_command(command)
    
    if returncode == 0:
        print("✅ Task completed successfully:")
        print(stdout)
    else:
        print(f"❌ Task failed: {stderr}")


def cli_monitoring_script():
    """Demonstrate monitoring script"""
    print("\\n📊 CLI Monitoring Script Example")
    
    # Get statistics
    print("Getting client statistics...")
    returncode, stdout, stderr = run_cli_command("codegen stats")
    
    if returncode == 0:
        print("📊 Statistics:")
        print(stdout)
    else:
        print(f"⚠️ Could not get statistics: {stderr}")
    
    # Monitor tasks for a short period
    print("\\n🔍 Monitoring tasks (5 seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < 5:
        returncode, stdout, stderr = run_cli_command("codegen status --limit 3")
        if returncode == 0:
            print(f"\\r📋 Current tasks: {len(stdout.splitlines())} entries", end="")
        time.sleep(1)
    
    print("\\n✅ Monitoring complete")


def cli_configuration_management():
    """Demonstrate configuration management"""
    print("\\n🔧 CLI Configuration Management Example")
    
    # Show available presets
    presets = ["development", "production", "high_throughput", "low_latency"]
    print(f"📋 Available presets: {', '.join(presets)}")
    
    # Set a configuration value
    print("\\nSetting custom timeout...")
    returncode, stdout, stderr = run_cli_command("codegen config set --key default_timeout --value 600")
    
    if returncode == 0:
        print("✅ Configuration updated")
    else:
        print(f"❌ Failed to update configuration: {stderr}")
    
    # Show updated configuration
    print("\\n📋 Updated configuration:")
    returncode, stdout, stderr = run_cli_command("codegen config show")
    if returncode == 0:
        print(stdout)


def cli_log_analysis():
    """Demonstrate log analysis"""
    print("\\n📜 CLI Log Analysis Example")
    
    # Get recent tasks to find one with logs
    returncode, stdout, stderr = run_cli_command("codegen status --limit 1")
    
    if returncode != 0:
        print("⚠️ No tasks found for log analysis")
        return
    
    # Try to extract task ID from output (simplified)
    lines = stdout.strip().split('\\n')
    task_id = None
    
    for line in lines:
        if "Task" in line and ":" in line:
            try:
                # Extract task ID (this is a simplified approach)
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        task_id = part
                        break
            except:
                pass
    
    if task_id:
        print(f"📜 Analyzing logs for task {task_id}...")
        command = f"codegen logs {task_id} --limit 5"
        returncode, stdout, stderr = run_cli_command(command)
        
        if returncode == 0:
            print("📊 Log analysis:")
            print(stdout)
        else:
            print(f"⚠️ Could not get logs: {stderr}")
    else:
        print("⚠️ No task ID found for log analysis")


def main():
    """Main function to run all CLI examples"""
    print("🚀 Codegen CLI Examples\\n")
    
    try:
        cli_basic_workflow()
        cli_task_automation()
        cli_monitoring_script()
        cli_configuration_management()
        cli_log_analysis()
        
        print("\\n✅ All CLI examples completed!")
        
    except KeyboardInterrupt:
        print("\\n🛑 Examples interrupted by user")
    except Exception as e:
        print(f"\\n❌ Example failed: {e}")


if __name__ == "__main__":
    main()

