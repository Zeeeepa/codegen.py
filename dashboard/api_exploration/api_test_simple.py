#!/usr/bin/env python3
"""
Simple API test to validate credentials and basic functionality
"""

import os
import sys
import requests
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def test_api_simple():
    """Simple API test with different base URLs"""
    
    api_token = 'sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99'
    org_id = 323
    
    # Try different base URLs
    base_urls = [
        'https://api.codegen.com',
        'https://codegen.com/api',
        'https://app.codegen.com/api',
        'https://api.codegen.sh',
        'https://codegen.sh/api'
    ]
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
        'User-Agent': 'CodegenDashboard/1.0'
    }
    
    print("Testing API endpoints with different base URLs...")
    print(f"Token: {api_token[:8]}...{api_token[-4:]}")
    print(f"Org ID: {org_id}")
    print()
    
    for base_url in base_urls:
        print(f"Testing base URL: {base_url}")
        
        # Test endpoints
        endpoints = [
            '/users/me',
            '/user',
            '/auth/me',
            f'/organizations/{org_id}',
            f'/organizations/{org_id}/agent/runs',
            '/organizations',
            '/health',
            '/status'
        ]
        
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"  {endpoint}: {response.status_code} - {response.reason}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"    Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
                    except:
                        print(f"    Success! Response length: {len(response.text)}")
                elif response.status_code == 401:
                    print(f"    Authentication issue")
                elif response.status_code == 404:
                    print(f"    Endpoint not found")
                else:
                    print(f"    Error: {response.text[:100]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  {endpoint}: Connection error - {e}")
        
        print()

def test_with_sdk():
    """Test using the SDK directly"""
    print("Testing with SDK...")
    
    try:
        from codegen_api import CodegenClient, ClientConfig
        
        # Try different base URLs with SDK
        base_urls = [
            'https://api.codegen.com',
            'https://codegen.com/api', 
            'https://app.codegen.com/api'
        ]
        
        for base_url in base_urls:
            print(f"SDK test with base URL: {base_url}")
            
            config = ClientConfig(
                api_token='sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99',
                org_id=323,
                base_url=base_url
            )
            
            try:
                with CodegenClient(config) as client:
                    # Try to get current user
                    user = client.get_current_user()
                    print(f"  ✓ Success! User: {user.github_username}")
                    
                    # Try to list organizations
                    orgs = client.get_organizations(limit=5)
                    print(f"  ✓ Organizations: {len(orgs.items)}")
                    
                    # Try to list agent runs
                    runs = client.list_agent_runs(323, limit=5)
                    print(f"  ✓ Agent runs: {len(runs.items)}")
                    
                    return True
                    
            except Exception as e:
                print(f"  ✗ SDK Error: {e}")
        
    except Exception as e:
        print(f"SDK import error: {e}")
    
    return False

if __name__ == '__main__':
    print("=== Codegen API Simple Test ===\n")
    
    # Test with direct requests
    test_api_simple()
    
    # Test with SDK
    success = test_with_sdk()
    
    if success:
        print("✓ API is working! Proceeding with dashboard development...")
    else:
        print("✗ API test failed. Check credentials and endpoints.")

