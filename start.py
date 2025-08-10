#!/usr/bin/env python3
"""
Simple startup script for Codegen Dashboard
===========================================

This script starts both the API server and dashboard properly.
"""

import subprocess
import sys
import time
import requests
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_api_server():
    """Check if API server is running."""
    try:
        # Get token from environment
        token = os.getenv("CODEGEN_API_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        response = requests.get("http://localhost:8000/health", headers=headers, timeout=2)
        return response.status_code == 200
    except:
        return False

def start_api_server():
    """Start the API server."""
    print("🚀 Starting API server...")
    api_process = subprocess.Popen([sys.executable, "api.py"])
    
    # Wait for it to start
    for i in range(10):
        if check_api_server():
            print("✅ API server started!")
            return api_process
        time.sleep(1)
        print(f"⏳ Waiting for API server... ({i+1}/10)")
    
    print("❌ Failed to start API server")
    api_process.terminate()
    return None

def start_dashboard():
    """Start the Reflex dashboard."""
    print("🎨 Starting Reflex dashboard...")
    dashboard_process = subprocess.Popen([sys.executable, "-m", "reflex", "run"])
    return dashboard_process

def main():
    """Main startup function."""
    print("🤖 Starting Codegen Agent Dashboard")
    print("=" * 50)
    
    # Check if API server is already running
    if check_api_server():
        print("✅ API server already running!")
        api_process = None
    else:
        api_process = start_api_server()
        if not api_process:
            print("❌ Cannot start API server. Exiting.")
            return
    
    # Start dashboard
    dashboard_process = start_dashboard()
    
    print("\n🎯 Services started!")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🎨 Dashboard UI: http://localhost:3000")
    print("\n💡 Press Ctrl+C to stop all services")
    
    try:
        # Wait for dashboard process
        dashboard_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        
        # Stop processes
        if dashboard_process:
            dashboard_process.terminate()
        if api_process:
            api_process.terminate()
        
        print("✅ All services stopped!")

if __name__ == "__main__":
    main()
