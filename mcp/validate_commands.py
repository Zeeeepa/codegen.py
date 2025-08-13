#!/usr/bin/env python3
"""
Validation script to test all MCP server commands with real API calls
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(command, input_data=None):
    """Run a command and return the output"""
    print(f"\n🔄 Running command: {command}")
    
    if input_data:
        print(f"📤 Input: {json.dumps(input_data, indent=2)}")
    
    try:
        if input_data:
            # For commands that need input
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            stdout, stderr = process.communicate(input=json.dumps(input_data))
        else:
            # For commands that don't need input
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"❌ Command failed with return code {process.returncode}")
            print(f"Error: {stderr}")
            return None
        
        print(f"✅ Command completed successfully")
        return stdout
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return None

def validate_config():
    """Validate configuration settings"""
    print("\n🔍 Validating configuration...")
    
    # Check environment variables
    api_token = os.environ.get('CODEGEN_API_TOKEN')
    org_id = os.environ.get('CODEGEN_ORG_ID')
    
    if not api_token:
        print("❌ CODEGEN_API_TOKEN environment variable not set")
        return False
    
    if not org_id:
        print("❌ CODEGEN_ORG_ID environment variable not set")
        return False
    
    print(f"✅ Found API token: {api_token[:8]}...{api_token[-4:]}")
    print(f"✅ Found organization ID: {org_id}")
    
    return True

def main():
    """Run validation tests for all commands"""
    print("🧪 Validating Codegen MCP Server Commands\n")
    
    # Validate configuration
    if not validate_config():
        print("\n❌ Configuration validation failed. Please set the required environment variables.")
        return
    
    # Start the server in the background
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(Path(__file__).parent)
    )
    
    # Wait for server to start
    print("\n🚀 Starting MCP server...")
    time.sleep(2)
    
    try:
        # Test results
        results = {
            "config": False,
            "new": False,
            "resume": False,
            "list": False,
            "orchestration": False
        }
        
        # Test config command
        print("\n\n📝 Testing codegenapi_config command...")
        
        # Create a simple MCP client script
        mcp_client = """
import json
import sys

def send_jsonrpc_request(method, params=None):
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    # Write request with content length header
    request_str = json.dumps(request)
    content_length = len(request_str)
    header = f"Content-Length: {content_length}\\r\\n\\r\\n"
    
    sys.stdout.write(header + request_str)
    sys.stdout.flush()
    
    # Read response
    header = sys.stdin.readline()
    if not header:
        return None
    
    content_length = int(header.strip().split(": ")[1])
    sys.stdin.readline()  # Empty line
    response_data = sys.stdin.read(content_length)
    
    return json.loads(response_data)

# Initialize
response = send_jsonrpc_request("initialize", {
    "capabilities": {},
    "initializationOptions": {
        "server_name": "codegenapi",
        "server_version": "0.1.0"
    }
})

# List tools
response = send_jsonrpc_request("listTools")

# Call the tool
tool_name = sys.argv[1]
arguments = json.loads(sys.argv[2])

response = send_jsonrpc_request("callTool", {
    "name": tool_name,
    "arguments": arguments
})

print(json.dumps(response, indent=2))
"""
        
        with open("mcp_client.py", "w") as f:
            f.write(mcp_client)
        
        # Test config list command
        config_list_args = json.dumps({"action": "list"})
        config_output = run_command(f"{sys.executable} mcp_client.py codegenapi_config '{config_list_args}'")
        
        if config_output and "result" in config_output:
            print("✅ Config command successful")
            results["config"] = True
        
        # Test new command
        print("\n\n🆕 Testing codegenapi_new command...")
        new_args = json.dumps({
            "repo": "Zeeeepa/codegen.py",
            "task": "VALIDATE",
            "query": "Validate the MCP server implementation"
        })
        
        new_output = run_command(f"{sys.executable} mcp_client.py codegenapi_new '{new_args}'")
        
        agent_run_id = None
        if new_output:
            try:
                response = json.loads(new_output)
                if "result" in response:
                    content = response["result"]["content"][0]["text"]
                    content_json = json.loads(content)
                    if "agent_run_id" in content_json:
                        agent_run_id = content_json["agent_run_id"]
                        print(f"✅ New command successful, created agent run {agent_run_id}")
                        results["new"] = True
            except Exception as e:
                print(f"❌ Error parsing new command output: {e}")
        
        # Test list command
        print("\n\n📋 Testing codegenapi_list command...")
        list_args = json.dumps({"limit": 5})
        list_output = run_command(f"{sys.executable} mcp_client.py codegenapi_list '{list_args}'")
        
        if list_output and "result" in list_output:
            print("✅ List command successful")
            results["list"] = True
        
        # Test resume command if we have an agent run ID
        if agent_run_id:
            print("\n\n▶️ Testing codegenapi_resume command...")
            resume_args = json.dumps({
                "agent_run_id": agent_run_id,
                "query": "Add validation for the orchestration functionality"
            })
            
            resume_output = run_command(f"{sys.executable} mcp_client.py codegenapi_resume '{resume_args}'")
            
            if resume_output and "result" in resume_output:
                print("✅ Resume command successful")
                results["resume"] = True
            
            # Test orchestration
            print("\n\n🔄 Testing orchestration functionality...")
            
            # Create a child agent with parent ID
            orchestration_args = json.dumps({
                "repo": "Zeeeepa/codegen.py",
                "task": "VALIDATE",
                "query": "Validate the orchestration functionality",
                "parent_id": agent_run_id,
                "wait_for_completion": True
            })
            
            orchestration_output = run_command(f"{sys.executable} mcp_client.py codegenapi_new '{orchestration_args}'")
            
            if orchestration_output and "result" in orchestration_output:
                print("✅ Orchestration functionality successful")
                results["orchestration"] = True
        
        # Print summary
        print("\n\n📊 Validation Summary:")
        for command, success in results.items():
            status = "✅ Passed" if success else "❌ Failed"
            print(f"{command.capitalize()}: {status}")
        
        overall_success = all(results.values())
        if overall_success:
            print("\n🎉 All commands validated successfully!")
        else:
            print("\n⚠️ Some commands failed validation.")
        
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
    finally:
        # Clean up
        if os.path.exists("mcp_client.py"):
            os.remove("mcp_client.py")
        
        # Terminate the server process
        print("\n🛑 Terminating server process...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()

