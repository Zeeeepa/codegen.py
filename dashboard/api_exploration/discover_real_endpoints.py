#!/usr/bin/env python3
"""
Real API Endpoint Discovery
Systematically discover the actual Codegen API endpoints and structure.
"""

import requests
import json
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealAPIDiscovery:
    """Discover real Codegen API endpoints"""
    
    def __init__(self):
        self.api_token = 'sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99'
        self.org_id = 323
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'CodegenDashboard/1.0 Real-API-Discovery'
        })
        self.discovered_endpoints = []
    
    def test_endpoint(self, base_url: str, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Test a specific endpoint"""
        url = f"{base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                response = self.session.request(method, url, json=data)
            
            duration = time.time() - start_time
            
            result = {
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'duration': duration,
                'success': 200 <= response.status_code < 300,
                'headers': dict(response.headers),
                'response_size': len(response.content)
            }
            
            # Try to parse response
            try:
                result['response_data'] = response.json()
            except:
                result['response_text'] = response.text[:500]  # First 500 chars
            
            return result
            
        except Exception as e:
            return {
                'url': url,
                'method': method,
                'status_code': 0,
                'duration': 0,
                'success': False,
                'error': str(e)
            }
    
    def discover_base_urls(self) -> list:
        """Try different base URL patterns"""
        base_urls = [
            'https://api.codegen.com',
            'https://codegen.com/api',
            'https://app.codegen.com/api',
            'https://api.codegen.sh',
            'https://codegen.sh/api',
            'https://api-v1.codegen.com',
            'https://v1.api.codegen.com',
            'https://backend.codegen.com',
            'https://server.codegen.com/api',
            'https://prod.codegen.com/api'
        ]
        
        working_bases = []
        
        logger.info("🔍 Testing base URLs...")
        
        for base_url in base_urls:
            # Test basic endpoints
            test_endpoints = [
                '/health',
                '/status',
                '/ping',
                '/version',
                '/api/health',
                '/api/status',
                '/users/me',
                '/user',
                '/auth/me',
                f'/organizations/{self.org_id}',
                '/organizations'
            ]
            
            logger.info(f"Testing base URL: {base_url}")
            
            for endpoint in test_endpoints:
                result = self.test_endpoint(base_url, endpoint)
                
                if result['success']:
                    logger.info(f"  ✅ {endpoint}: {result['status_code']}")
                    working_bases.append(base_url)
                    self.discovered_endpoints.append(result)
                    break  # Found working endpoint for this base
                elif result['status_code'] == 401:
                    logger.info(f"  🔐 {endpoint}: 401 (auth required - endpoint exists)")
                    working_bases.append(base_url)
                    break
                elif result['status_code'] == 403:
                    logger.info(f"  🚫 {endpoint}: 403 (forbidden - endpoint exists)")
                    working_bases.append(base_url)
                    break
                elif result['status_code'] != 404:
                    logger.info(f"  ⚠️ {endpoint}: {result['status_code']}")
        
        return list(set(working_bases))  # Remove duplicates
    
    def discover_endpoints_for_base(self, base_url: str):
        """Discover endpoints for a specific base URL"""
        logger.info(f"🔍 Discovering endpoints for: {base_url}")
        
        # Common API endpoint patterns
        endpoint_patterns = [
            # Authentication
            '/auth/login',
            '/auth/logout',
            '/auth/me',
            '/auth/user',
            '/login',
            '/logout',
            '/me',
            '/user',
            '/users/me',
            '/users/current',
            
            # Organizations
            '/organizations',
            f'/organizations/{self.org_id}',
            f'/orgs/{self.org_id}',
            '/orgs',
            
            # Agent runs - try different patterns
            f'/organizations/{self.org_id}/runs',
            f'/organizations/{self.org_id}/agent-runs',
            f'/organizations/{self.org_id}/agent/runs',
            f'/organizations/{self.org_id}/agents/runs',
            f'/orgs/{self.org_id}/runs',
            f'/orgs/{self.org_id}/agent-runs',
            '/runs',
            '/agent-runs',
            '/agents/runs',
            '/agent/runs',
            
            # Projects
            f'/organizations/{self.org_id}/projects',
            f'/organizations/{self.org_id}/repos',
            f'/orgs/{self.org_id}/projects',
            '/projects',
            '/repos',
            
            # System
            '/health',
            '/status',
            '/ping',
            '/version',
            '/info',
            
            # API versioning
            '/v1/users/me',
            '/v1/organizations',
            f'/v1/organizations/{self.org_id}/runs',
            '/api/v1/users/me',
            '/api/v1/organizations',
            f'/api/v1/organizations/{self.org_id}/runs',
        ]
        
        working_endpoints = []
        
        for endpoint in endpoint_patterns:
            result = self.test_endpoint(base_url, endpoint)
            
            status_icon = "✅" if result['success'] else "❌"
            if result['status_code'] == 401:
                status_icon = "🔐"
            elif result['status_code'] == 403:
                status_icon = "🚫"
            elif result['status_code'] == 404:
                status_icon = "❓"
            
            logger.info(f"  {status_icon} {endpoint}: {result['status_code']}")
            
            if result['success'] or result['status_code'] in [401, 403]:
                working_endpoints.append(result)
                self.discovered_endpoints.append(result)
        
        return working_endpoints
    
    def test_agent_run_operations(self, base_url: str):
        """Test agent run CRUD operations"""
        logger.info(f"🧪 Testing agent run operations for: {base_url}")
        
        # Try to find the correct runs endpoint
        runs_endpoints = [
            f'/organizations/{self.org_id}/runs',
            f'/organizations/{self.org_id}/agent-runs',
            f'/organizations/{self.org_id}/agent/runs',
            f'/orgs/{self.org_id}/runs',
            '/runs',
            '/agent-runs'
        ]
        
        for endpoint in runs_endpoints:
            # Test GET (list runs)
            result = self.test_endpoint(base_url, endpoint, 'GET')
            
            if result['success']:
                logger.info(f"  ✅ Found working runs endpoint: {endpoint}")
                
                # Test POST (create run)
                create_data = {
                    'prompt': 'Test run for API discovery',
                    'metadata': {'source': 'api_discovery', 'test': True}
                }
                
                create_result = self.test_endpoint(base_url, endpoint, 'POST', create_data)
                logger.info(f"  📝 Create run: {create_result['status_code']}")
                
                if create_result['success'] and 'response_data' in create_result:
                    run_data = create_result['response_data']
                    if 'id' in run_data:
                        run_id = run_data['id']
                        logger.info(f"  ✅ Created test run: {run_id}")
                        
                        # Test individual run operations
                        run_endpoint = f"{endpoint}/{run_id}"
                        
                        # Get specific run
                        get_result = self.test_endpoint(base_url, run_endpoint, 'GET')
                        logger.info(f"  👁️ Get run {run_id}: {get_result['status_code']}")
                        
                        # Try cancel operations
                        cancel_endpoints = [
                            f"{run_endpoint}/cancel",
                            f"{run_endpoint}/stop",
                            f"{run_endpoint}/terminate"
                        ]
                        
                        for cancel_ep in cancel_endpoints:
                            cancel_result = self.test_endpoint(base_url, cancel_ep, 'POST')
                            logger.info(f"  🛑 Cancel via {cancel_ep}: {cancel_result['status_code']}")
                
                return endpoint  # Return the working endpoint
        
        return None
    
    def run_comprehensive_discovery(self):
        """Run comprehensive API discovery"""
        logger.info("🚀 Starting Comprehensive Real API Discovery")
        logger.info(f"API Token: {self.api_token[:8]}...{self.api_token[-4:]}")
        logger.info(f"Organization ID: {self.org_id}")
        logger.info("=" * 60)
        
        # Step 1: Discover working base URLs
        working_bases = self.discover_base_urls()
        
        if not working_bases:
            logger.error("❌ No working base URLs found!")
            return
        
        logger.info(f"✅ Found {len(working_bases)} working base URLs:")
        for base in working_bases:
            logger.info(f"  - {base}")
        
        # Step 2: For each working base, discover endpoints
        for base_url in working_bases:
            logger.info(f"\n{'='*60}")
            working_endpoints = self.discover_endpoints_for_base(base_url)
            
            if working_endpoints:
                logger.info(f"✅ Found {len(working_endpoints)} working endpoints for {base_url}")
                
                # Step 3: Test agent run operations
                self.test_agent_run_operations(base_url)
        
        # Generate report
        self.generate_discovery_report()
    
    def generate_discovery_report(self):
        """Generate comprehensive discovery report"""
        report = {
            'discovery_timestamp': datetime.now().isoformat(),
            'api_token_preview': f"{self.api_token[:8]}...{self.api_token[-4:]}",
            'organization_id': self.org_id,
            'total_endpoints_tested': len(self.discovered_endpoints),
            'successful_endpoints': [ep for ep in self.discovered_endpoints if ep['success']],
            'auth_required_endpoints': [ep for ep in self.discovered_endpoints if ep.get('status_code') == 401],
            'forbidden_endpoints': [ep for ep in self.discovered_endpoints if ep.get('status_code') == 403],
            'all_results': self.discovered_endpoints
        }
        
        # Save report
        report_file = 'real_api_discovery_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Generate markdown report
        md_report = f"""# Real Codegen API Discovery Report
Generated: {datetime.now().isoformat()}

## Summary
- **API Token**: {self.api_token[:8]}...{self.api_token[-4:]}
- **Organization ID**: {self.org_id}
- **Total Endpoints Tested**: {len(self.discovered_endpoints)}
- **Successful Endpoints**: {len(report['successful_endpoints'])}
- **Auth Required (401)**: {len(report['auth_required_endpoints'])}
- **Forbidden (403)**: {len(report['forbidden_endpoints'])}

## Working Endpoints
"""
        
        for ep in report['successful_endpoints']:
            md_report += f"- ✅ `{ep['method']} {ep['url']}` - {ep['status_code']} ({ep['duration']:.3f}s)\n"
        
        md_report += "\n## Auth Required Endpoints (401)\n"
        for ep in report['auth_required_endpoints']:
            md_report += f"- 🔐 `{ep['method']} {ep['url']}` - {ep['status_code']}\n"
        
        md_report += "\n## Forbidden Endpoints (403)\n"
        for ep in report['forbidden_endpoints']:
            md_report += f"- 🚫 `{ep['method']} {ep['url']}` - {ep['status_code']}\n"
        
        md_report += f"""
## Recommendations

Based on the discovery results:

1. **Working Base URLs**: {', '.join(set(ep['url'].split('/')[0:3]) for ep in report['successful_endpoints'])}
2. **Authentication**: {'Working' if report['successful_endpoints'] else 'Issues detected'}
3. **Agent Runs**: {'Endpoints found' if any('run' in ep['url'] for ep in report['successful_endpoints']) else 'No run endpoints discovered'}

## Next Steps

1. Use the working endpoints identified above
2. Implement proper authentication if 401 errors persist
3. Check API documentation for correct endpoint patterns
4. Contact API team if no working endpoints found
"""
        
        md_file = 'real_api_discovery_report.md'
        with open(md_file, 'w') as f:
            f.write(md_report)
        
        logger.info(f"\n📄 Discovery reports saved:")
        logger.info(f"  - JSON: {report_file}")
        logger.info(f"  - Markdown: {md_file}")
        
        return report

def main():
    """Main discovery function"""
    discovery = RealAPIDiscovery()
    discovery.run_comprehensive_discovery()

if __name__ == '__main__':
    main()

