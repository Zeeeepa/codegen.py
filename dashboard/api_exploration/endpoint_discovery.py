#!/usr/bin/env python3
"""
Comprehensive API Endpoint Discovery and Testing Tool
Systematically explores the Codegen API to discover all available endpoints and capabilities.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Add parent directory to path to import codegen_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from codegen_api import CodegenClient, ClientConfig, Agent, AgentRunStatus

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EndpointTest:
    """Represents a test of an API endpoint"""
    method: str
    path: str
    description: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    headers: Optional[Dict] = None

@dataclass
class APICapabilities:
    """Comprehensive API capabilities analysis"""
    base_url: str
    organization_id: int
    authenticated: bool
    available_endpoints: List[EndpointTest]
    rate_limits: Dict[str, Any]
    pagination_limits: Dict[str, int]
    supported_operations: List[str]
    missing_operations: List[str]
    performance_metrics: Dict[str, float]
    discovered_features: List[str]

class CodegenAPIExplorer:
    """Comprehensive API exploration and testing tool"""
    
    def __init__(self, api_token: str, org_id: int, base_url: str = "https://api.codegen.com"):
        self.api_token = api_token
        self.org_id = org_id
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'CodegenDashboard/1.0 API-Explorer'
        })
        
        # Initialize SDK client for comparison
        config = ClientConfig(
            api_token=api_token,
            org_id=org_id,
            base_url=base_url
        )
        self.client = CodegenClient(config)
        
        self.test_results: List[EndpointTest] = []
        self.capabilities = APICapabilities(
            base_url=base_url,
            organization_id=org_id,
            authenticated=False,
            available_endpoints=[],
            rate_limits={},
            pagination_limits={},
            supported_operations=[],
            missing_operations=[],
            performance_metrics={},
            discovered_features=[]
        )
    
    def test_endpoint(self, method: str, path: str, description: str, 
                     data: Optional[Dict] = None, params: Optional[Dict] = None) -> EndpointTest:
        """Test a specific API endpoint"""
        url = f"{self.base_url}{path}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response_time = time.time() - start_time
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:1000]}  # Truncate long responses
            
            test_result = EndpointTest(
                method=method.upper(),
                path=path,
                description=description,
                status_code=response.status_code,
                response_time=response_time,
                success=200 <= response.status_code < 300,
                response_data=response_data,
                headers=dict(response.headers)
            )
            
            if not test_result.success:
                test_result.error_message = f"HTTP {response.status_code}: {response.text[:200]}"
            
        except Exception as e:
            response_time = time.time() - start_time
            test_result = EndpointTest(
                method=method.upper(),
                path=path,
                description=description,
                status_code=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
        
        self.test_results.append(test_result)
        logger.info(f"{method.upper()} {path}: {'✓' if test_result.success else '✗'} ({test_result.status_code}) - {response_time:.3f}s")
        return test_result
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        logger.info("Testing authentication...")
        
        try:
            # Test with SDK first
            user = self.client.get_current_user()
            logger.info(f"✓ Authenticated as: {user.github_username}")
            self.capabilities.authenticated = True
            self.capabilities.discovered_features.append(f"User: {user.github_username}")
            return True
        except Exception as e:
            logger.error(f"✗ Authentication failed: {e}")
            self.capabilities.authenticated = False
            return False
    
    def discover_organizations(self):
        """Discover available organizations"""
        logger.info("Discovering organizations...")
        
        try:
            orgs = self.client.get_organizations(limit=10)
            logger.info(f"✓ Found {len(orgs.items)} organizations")
            
            for org in orgs.items:
                logger.info(f"  - {org.name} (ID: {org.id})")
                self.capabilities.discovered_features.append(f"Organization: {org.name} (ID: {org.id})")
            
            # Test direct API call
            self.test_endpoint('GET', '/organizations', 'List organizations')
            
        except Exception as e:
            logger.error(f"✗ Failed to discover organizations: {e}")
    
    def test_agent_run_operations(self):
        """Test all agent run related operations"""
        logger.info("Testing agent run operations...")
        
        # Test listing agent runs
        self.test_endpoint('GET', f'/organizations/{self.org_id}/agent/runs', 
                          'List agent runs', params={'limit': 5})
        
        # Test creating an agent run
        test_prompt = "Test prompt for API exploration - please respond with a simple acknowledgment"
        create_data = {
            'prompt': test_prompt,
            'metadata': {'source': 'api_exploration', 'test': True}
        }
        
        create_result = self.test_endpoint('POST', f'/organizations/{self.org_id}/agent/run', 
                                         'Create agent run', data=create_data)
        
        if create_result.success and create_result.response_data:
            run_id = create_result.response_data.get('id')
            if run_id:
                logger.info(f"✓ Created test agent run: {run_id}")
                
                # Test getting specific run
                self.test_endpoint('GET', f'/organizations/{self.org_id}/agent/run/{run_id}', 
                                 f'Get agent run {run_id}')
                
                # Test getting run logs
                self.test_endpoint('GET', f'/organizations/{self.org_id}/agent/run/{run_id}/logs', 
                                 f'Get agent run logs {run_id}')
                
                # Test resume operation (might fail if run is not paused)
                resume_data = {'prompt': 'Resume test', 'agent_run_id': run_id}
                self.test_endpoint('POST', f'/organizations/{self.org_id}/agent/run/resume', 
                                 f'Resume agent run {run_id}', data=resume_data)
                
                # Try to discover cancel endpoint
                self.test_endpoint('POST', f'/organizations/{self.org_id}/agent/run/{run_id}/cancel', 
                                 f'Cancel agent run {run_id}')
                
                self.test_endpoint('DELETE', f'/organizations/{self.org_id}/agent/run/{run_id}', 
                                 f'Delete agent run {run_id}')
                
                # Try other potential endpoints
                self.test_endpoint('POST', f'/organizations/{self.org_id}/agent/run/{run_id}/stop', 
                                 f'Stop agent run {run_id}')
                
                self.test_endpoint('POST', f'/organizations/{self.org_id}/agent/run/{run_id}/pause', 
                                 f'Pause agent run {run_id}')
    
    def test_pagination_limits(self):
        """Test pagination limits and behavior"""
        logger.info("Testing pagination limits...")
        
        # Test different limit values
        for limit in [1, 10, 50, 100, 500, 1000]:
            result = self.test_endpoint('GET', f'/organizations/{self.org_id}/agent/runs', 
                                      f'Test pagination limit {limit}', 
                                      params={'limit': limit})
            
            if result.success and result.response_data:
                actual_count = len(result.response_data.get('items', []))
                self.capabilities.pagination_limits[f'limit_{limit}'] = actual_count
                logger.info(f"  Limit {limit}: returned {actual_count} items")
    
    def test_rate_limits(self):
        """Test rate limiting behavior"""
        logger.info("Testing rate limits...")
        
        # Make rapid requests to test rate limiting
        start_time = time.time()
        request_count = 0
        
        for i in range(20):  # Make 20 rapid requests
            result = self.test_endpoint('GET', f'/organizations/{self.org_id}/agent/runs', 
                                      f'Rate limit test {i+1}', params={'limit': 1})
            request_count += 1
            
            if result.status_code == 429:  # Rate limited
                self.capabilities.rate_limits['hit_limit_at_request'] = request_count
                self.capabilities.rate_limits['time_to_limit'] = time.time() - start_time
                
                if result.headers and 'retry-after' in result.headers:
                    self.capabilities.rate_limits['retry_after'] = result.headers['retry-after']
                
                logger.info(f"✓ Rate limit hit at request {request_count}")
                break
            
            time.sleep(0.1)  # Small delay between requests
        
        if request_count == 20:
            self.capabilities.rate_limits['no_limit_detected'] = True
            logger.info("✓ No rate limit detected in 20 requests")
    
    def discover_hidden_endpoints(self):
        """Try to discover undocumented endpoints"""
        logger.info("Discovering potential hidden endpoints...")
        
        # Common REST patterns to try
        potential_endpoints = [
            ('GET', f'/organizations/{self.org_id}/projects', 'List projects'),
            ('GET', f'/organizations/{self.org_id}/users', 'List users'),
            ('GET', f'/organizations/{self.org_id}/settings', 'Get settings'),
            ('GET', f'/organizations/{self.org_id}/billing', 'Get billing info'),
            ('GET', f'/organizations/{self.org_id}/usage', 'Get usage stats'),
            ('GET', f'/organizations/{self.org_id}/metrics', 'Get metrics'),
            ('GET', f'/organizations/{self.org_id}/webhooks', 'List webhooks'),
            ('GET', f'/organizations/{self.org_id}/integrations', 'List integrations'),
            ('GET', '/health', 'Health check'),
            ('GET', '/version', 'API version'),
            ('GET', '/status', 'API status'),
        ]
        
        for method, path, description in potential_endpoints:
            self.test_endpoint(method, path, description)
    
    def analyze_performance(self):
        """Analyze API performance characteristics"""
        logger.info("Analyzing API performance...")
        
        response_times = [test.response_time for test in self.test_results if test.success]
        
        if response_times:
            self.capabilities.performance_metrics = {
                'avg_response_time': sum(response_times) / len(response_times),
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'total_requests': len(self.test_results),
                'successful_requests': len([t for t in self.test_results if t.success]),
                'failed_requests': len([t for t in self.test_results if not t.success])
            }
            
            logger.info(f"✓ Performance analysis complete:")
            logger.info(f"  Average response time: {self.capabilities.performance_metrics['avg_response_time']:.3f}s")
            logger.info(f"  Success rate: {self.capabilities.performance_metrics['successful_requests']}/{self.capabilities.performance_metrics['total_requests']}")
    
    def categorize_operations(self):
        """Categorize supported and missing operations"""
        logger.info("Categorizing API operations...")
        
        # Check which operations are supported based on test results
        operation_tests = {
            'create_agent_run': any(t.path.endswith('/agent/run') and t.method == 'POST' and t.success for t in self.test_results),
            'get_agent_run': any('/agent/run/' in t.path and t.method == 'GET' and t.success for t in self.test_results),
            'list_agent_runs': any(t.path.endswith('/agent/runs') and t.method == 'GET' and t.success for t in self.test_results),
            'resume_agent_run': any('resume' in t.path and t.method == 'POST' and t.success for t in self.test_results),
            'cancel_agent_run': any('cancel' in t.path and t.method == 'POST' and t.success for t in self.test_results),
            'delete_agent_run': any('/agent/run/' in t.path and t.method == 'DELETE' and t.success for t in self.test_results),
            'stop_agent_run': any('stop' in t.path and t.method == 'POST' and t.success for t in self.test_results),
            'pause_agent_run': any('pause' in t.path and t.method == 'POST' and t.success for t in self.test_results),
            'get_agent_logs': any('logs' in t.path and t.method == 'GET' and t.success for t in self.test_results),
        }
        
        self.capabilities.supported_operations = [op for op, supported in operation_tests.items() if supported]
        self.capabilities.missing_operations = [op for op, supported in operation_tests.items() if not supported]
        
        logger.info(f"✓ Supported operations: {', '.join(self.capabilities.supported_operations)}")
        logger.info(f"✗ Missing operations: {', '.join(self.capabilities.missing_operations)}")
    
    def run_comprehensive_exploration(self) -> APICapabilities:
        """Run comprehensive API exploration"""
        logger.info("Starting comprehensive API exploration...")
        logger.info(f"Target: {self.base_url}")
        logger.info(f"Organization ID: {self.org_id}")
        
        # Test authentication first
        if not self.test_authentication():
            logger.error("Authentication failed - stopping exploration")
            return self.capabilities
        
        # Run all discovery tests
        self.discover_organizations()
        self.test_agent_run_operations()
        self.test_pagination_limits()
        self.discover_hidden_endpoints()
        
        # Analyze results
        self.analyze_performance()
        self.categorize_operations()
        
        # Test rate limits last (might temporarily block requests)
        self.test_rate_limits()
        
        # Store test results
        self.capabilities.available_endpoints = self.test_results
        
        logger.info("✓ API exploration complete!")
        return self.capabilities
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate comprehensive API analysis report"""
        report = f"""
# Codegen API Analysis Report
Generated: {datetime.now().isoformat()}

## Authentication Status
- **Authenticated**: {'✓ Yes' if self.capabilities.authenticated else '✗ No'}
- **Base URL**: {self.capabilities.base_url}
- **Organization ID**: {self.capabilities.organization_id}

## Discovered Features
{chr(10).join(f'- {feature}' for feature in self.capabilities.discovered_features)}

## Supported Operations
{chr(10).join(f'- ✓ {op}' for op in self.capabilities.supported_operations)}

## Missing Operations
{chr(10).join(f'- ✗ {op}' for op in self.capabilities.missing_operations)}

## Performance Metrics
- **Average Response Time**: {self.capabilities.performance_metrics.get('avg_response_time', 0):.3f}s
- **Min Response Time**: {self.capabilities.performance_metrics.get('min_response_time', 0):.3f}s
- **Max Response Time**: {self.capabilities.performance_metrics.get('max_response_time', 0):.3f}s
- **Success Rate**: {self.capabilities.performance_metrics.get('successful_requests', 0)}/{self.capabilities.performance_metrics.get('total_requests', 0)}

## Rate Limits
{chr(10).join(f'- **{key}**: {value}' for key, value in self.capabilities.rate_limits.items())}

## Pagination Limits
{chr(10).join(f'- **{key}**: {value}' for key, value in self.capabilities.pagination_limits.items())}

## Endpoint Test Results

| Method | Path | Status | Response Time | Success |
|--------|------|--------|---------------|---------|
"""
        
        for test in self.capabilities.available_endpoints:
            status_icon = '✓' if test.success else '✗'
            report += f"| {test.method} | {test.path} | {test.status_code} | {test.response_time:.3f}s | {status_icon} |\n"
        
        report += f"""
## Detailed Test Results

```json
{json.dumps([asdict(test) for test in self.capabilities.available_endpoints], indent=2, default=str)}
```

## Recommendations for Dashboard Implementation

### Supported Features
Based on the API exploration, the dashboard can implement:
{chr(10).join(f'- {op.replace("_", " ").title()}' for op in self.capabilities.supported_operations)}

### Missing Features to Implement
The following features may need alternative implementations:
{chr(10).join(f'- {op.replace("_", " ").title()}' for op in self.capabilities.missing_operations)}

### Performance Considerations
- Average API response time: {self.capabilities.performance_metrics.get('avg_response_time', 0):.3f}s
- Recommended polling interval for real-time updates: {max(5, self.capabilities.performance_metrics.get('avg_response_time', 1) * 2):.0f}s
- Implement caching for frequently accessed data

### Rate Limiting Strategy
{'- Implement exponential backoff for rate limit handling' if self.capabilities.rate_limits else '- No rate limits detected, but implement defensive rate limiting'}
"""
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_file}")
        
        return report

def main():
    """Main function to run API exploration"""
    # Get credentials from environment or use provided values
    api_token = os.getenv('CODEGEN_API_TOKEN', 'sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99')
    org_id = int(os.getenv('CODEGEN_ORG_ID', '323'))
    
    logger.info("Starting Codegen API exploration...")
    logger.info(f"Using organization ID: {org_id}")
    logger.info(f"Using API token: {api_token[:8]}...{api_token[-4:]}")
    
    # Create explorer and run comprehensive analysis
    explorer = CodegenAPIExplorer(api_token, org_id)
    capabilities = explorer.run_comprehensive_exploration()
    
    # Generate and save report
    report_file = os.path.join(os.path.dirname(__file__), 'api_analysis_report.md')
    report = explorer.generate_report(report_file)
    
    # Also save capabilities as JSON for programmatic use
    capabilities_file = os.path.join(os.path.dirname(__file__), 'api_capabilities.json')
    with open(capabilities_file, 'w') as f:
        json.dump(asdict(capabilities), f, indent=2, default=str)
    
    logger.info(f"Analysis complete! Reports saved:")
    logger.info(f"- Markdown report: {report_file}")
    logger.info(f"- JSON capabilities: {capabilities_file}")
    
    return capabilities

if __name__ == '__main__':
    main()

