#!/usr/bin/env python3
"""
Simple validation script for the MCP server
"""

import json
import os
from pathlib import Path

def main():
    """Run simple validation tests"""
    print("🧪 Simple Validation of Codegen MCP Server\n")
    
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
    
    # Validate server.py exists
    server_path = Path(__file__).parent / "server.py"
    if not server_path.exists():
        print(f"❌ Server file not found at {server_path}")
        return False
    
    print(f"✅ Found server file at {server_path}")
    
    # Validate codegenapi_server.py exists
    server_impl_path = Path(__file__).parent / "codegenapi_server.py"
    if not server_impl_path.exists():
        print(f"❌ Server implementation file not found at {server_impl_path}")
        return False
    
    print(f"✅ Found server implementation file at {server_impl_path}")
    
    # Validate example files
    examples_dir = Path(__file__).parent / "examples"
    if not examples_dir.exists():
        print(f"❌ Examples directory not found at {examples_dir}")
        return False
    
    print(f"✅ Found examples directory at {examples_dir}")
    
    # Check for specific example files
    example_files = [
        "config_examples.json",
        "new_examples.json",
        "resume_examples.json",
        "list_examples.json",
        "orchestration_examples.json"
    ]
    
    for file in example_files:
        file_path = examples_dir / file
        if not file_path.exists():
            print(f"❌ Example file not found: {file}")
            return False
        
        # Validate JSON format
        try:
            with open(file_path, 'r') as f:
                json.load(f)
            print(f"✅ Validated example file: {file}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in example file: {file}")
            return False
    
    # Validate orchestration implementation
    with open(server_impl_path, 'r') as f:
        server_code = f.read()
    
    # Check for key orchestration functions
    orchestration_functions = [
        "_register_parent_child",
        "_mark_run_completed",
        "_monitor_agent_runs",
        "_handle_completed_run",
        "wait_for_completion"
    ]
    
    for func in orchestration_functions:
        if func not in server_code:
            print(f"❌ Orchestration function not found: {func}")
            return False
        
        print(f"✅ Found orchestration function: {func}")
    
    print("\n🎉 All validation checks passed!")
    return True

if __name__ == "__main__":
    main()

