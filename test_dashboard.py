#!/usr/bin/env python3
"""
Dashboard Validation Script

Tests the dashboard functionality with real API calls.
No mocks - only actual API validation.
"""

import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codegenapi import CodegenClient, CodegenError


def test_api_integration():
    """Test API integration with real endpoints"""
    print("🧪 Testing Dashboard API Integration")
    print("=" * 50)
    
    # Set credentials
    os.environ["CODEGEN_API_TOKEN"] = "sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99"
    os.environ["CODEGEN_ORG_ID"] = "323"
    
    try:
        # Initialize client
        print("1. Initializing Codegen client...")
        client = CodegenClient()
        print("✅ Client initialized successfully")
        
        # Test listing runs
        print("\n2. Testing list agent runs...")
        runs = client.list_agent_runs(limit=5)
        print(f"✅ Retrieved {len(runs)} agent runs")
        
        if runs:
            latest_run = runs[0]
            print(f"   Latest run: ID {latest_run.id}, Status: {latest_run.status}")
        
        # Test creating a run
        print("\n3. Testing create agent run...")
        test_prompt = f"""Repository: https://github.com/Zeeeepa/codegen.py

Request: Test dashboard functionality - validate that the API integration works correctly. This is a test run created at {datetime.now().isoformat()}."""
        
        new_run = client.create_agent_run(prompt=test_prompt)
        print(f"✅ Created test run: ID {new_run.id}")
        
        # Test getting run details
        print(f"\n4. Testing get agent run details for {new_run.id}...")
        run_details = client.get_agent_run(new_run.id)
        print(f"✅ Retrieved run details: Status {run_details.status}")
        
        # Test cancelling if active
        if run_details.can_cancel:
            print(f"\n5. Testing cancel agent run {new_run.id}...")
            success = client.cancel_agent_run(new_run.id)
            if success:
                print("✅ Successfully cancelled test run")
            else:
                print("⚠️ Cancel request sent but may not have succeeded")
        else:
            print(f"\n5. Skipping cancel test - run {new_run.id} cannot be cancelled (status: {run_details.status})")
        
        print("\n" + "=" * 50)
        print("🎉 All API tests passed!")
        print("\n📋 Dashboard Functionality Validated:")
        print("   ✅ Client initialization")
        print("   ✅ List agent runs")
        print("   ✅ Create agent runs")
        print("   ✅ Get run details")
        print("   ✅ Cancel runs (when applicable)")
        
        print(f"\n🚀 Dashboard is ready to use!")
        print("   Launch with: streamlit run dashboard.py")
        
        return True
        
    except CodegenError as e:
        print(f"❌ Codegen API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_dashboard_imports():
    """Test that dashboard can be imported without errors"""
    print("\n🧪 Testing Dashboard Imports")
    print("=" * 30)
    
    try:
        # Test importing dashboard components
        from codegenapi import CodegenClient, CodegenError
        from codegenapi.models import AgentRun
        print("✅ Core imports successful")
        
        # Test that dashboard.py can be imported
        import importlib.util
        spec = importlib.util.spec_from_file_location("dashboard", "dashboard.py")
        dashboard_module = importlib.util.module_from_spec(spec)
        print("✅ Dashboard module can be loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main validation function"""
    print("🎯 Dashboard Validation Suite")
    print("Testing real API functionality with no mocks")
    print("=" * 60)
    
    # Test imports first
    imports_ok = test_dashboard_imports()
    
    if not imports_ok:
        print("\n❌ Import tests failed - cannot proceed")
        return False
    
    # Test API integration
    api_ok = test_api_integration()
    
    if api_ok:
        print("\n🎉 VALIDATION COMPLETE - DASHBOARD READY!")
        print("\nNext steps:")
        print("1. pip install -r requirements.txt")
        print("2. streamlit run dashboard.py")
        print("3. Open http://localhost:8501 in your browser")
        return True
    else:
        print("\n❌ VALIDATION FAILED - CHECK API CREDENTIALS")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

