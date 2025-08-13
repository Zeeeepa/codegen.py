#!/usr/bin/env python3
"""
Test script for the Codegen MCP Server
"""

import subprocess
import sys
from pathlib import Path

def test_server_startup():
    """Test that the server can start up without errors"""
    print("Testing server startup...")
    
    try:
        # Try to import the server module
        sys.path.insert(0, str(Path(__file__).parent))
        from codegenapi_server import CodegenMCPServer
        
        # Create server instance
        server = CodegenMCPServer()
        print("✅ Server instance created successfully")
        
        # Test config loading
        config = server._load_config()
        print(f"✅ Config loaded: {len(config)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

def test_uv_command():
    """Test that the uv command works"""
    print("\nTesting uv command...")
    
    try:
        # Check if uv is available
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ uv is available: {result.stdout.strip()}")
        else:
            print("❌ uv is not available")
            return False
        
        # Test the directory structure
        mcp_dir = Path(__file__).parent
        server_py = mcp_dir / "server.py"
        pyproject_toml = mcp_dir / "pyproject.toml"
        
        if server_py.exists():
            print("✅ server.py exists")
        else:
            print("❌ server.py not found")
            return False
            
        if pyproject_toml.exists():
            print("✅ pyproject.toml exists")
        else:
            print("❌ pyproject.toml not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ uv command test failed: {e}")
        return False

def test_dependencies():
    """Test that required dependencies can be imported"""
    print("\nTesting dependencies...")
    
    try:
        # Test MCP import
        try:
            import importlib.util
            if importlib.util.find_spec("mcp"):
                print("✅ mcp library available")
            else:
                print("❌ mcp library not available - run: uv add mcp")
                return False
        except ImportError:
            print("❌ mcp library not available - run: uv add mcp")
            return False
        
        # Test requests import
        try:
            if importlib.util.find_spec("requests"):
                print("✅ requests library available")
            else:
                print("❌ requests library not available")
                return False
        except ImportError:
            print("❌ requests library not available")
            return False
        
        # Test codegen_api import
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent))
            if importlib.util.find_spec("codegen_api"):
                print("✅ codegen_api available")
            else:
                print("❌ codegen_api not available")
                return False
        except ImportError as e:
            print(f"❌ codegen_api not available: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Dependency test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Codegen MCP Server\n")
    
    tests = [
        test_dependencies,
        test_server_startup,
        test_uv_command,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The MCP server should work correctly.")
        print("\n📋 Usage:")
        print("1. Configure your API token:")
        print("   codegenapi config set api-token YOUR_TOKEN")
        print("\n2. Use the commands:")
        print("   codegenapi new --repo user/repo --task CREATE_PLAN --query 'Create a plan'")
        print("   codegenapi resume --agent_run_id 12345 --query 'Continue with analysis'")
        print("   codegenapi list --status running")
    else:
        print("❌ Some tests failed. Please fix the issues before using the server.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
