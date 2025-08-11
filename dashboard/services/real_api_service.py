#!/usr/bin/env python3
"""
Real Codegen API Service
Direct integration with the actual Codegen API using real credentials and endpoints.
"""

import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path to import codegen_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from codegen_api import CodegenClient, ClientConfig, Agent, AgentRunStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealCodegenAPI:
    """Real Codegen API service using actual API endpoints"""
    
    def __init__(self, api_token: str = None, org_id: int = None, base_url: str = None):
        # Use provided credentials or environment variables
        self.api_token = api_token or os.getenv('CODEGEN_API_TOKEN', 'sk-ce027fa7-3c8d-4beb-8c86-ed8ae982ac99')
        self.org_id = org_id or int(os.getenv('CODEGEN_ORG_ID', '323'))
        self.base_url = base_url or os.getenv('CODEGEN_BASE_URL', 'https://api.codegen.com/v1')
        
        logger.info(f"Initializing Real Codegen API")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Organization ID: {self.org_id}")
        logger.info(f"API Token: {self.api_token[:8]}...{self.api_token[-4:]}")
        
        # Initialize SDK client
        self.config = ClientConfig(
            api_token=self.api_token,
            org_id=self.org_id,
            base_url=self.base_url
        )
        self.client = CodegenClient(self.config)
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self):
        """Test API connection and log results"""
        try:
            logger.info("Testing API connection...")
            user = self.client.get_current_user()
            logger.info(f"✅ Successfully connected as: {user.github_username}")
            return True
        except Exception as e:
            logger.error(f"❌ API connection failed: {str(e)}")
            # Don't raise exception, let individual methods handle errors
            return False
    
    def get_current_user(self):
        """Get current authenticated user"""
        try:
            return self.client.get_current_user()
        except Exception as e:
            logger.error(f"Failed to get current user: {str(e)}")
            raise
    
    def get_organizations(self, limit: int = 10):
        """Get user's organizations"""
        try:
            orgs = self.client.get_organizations(limit=limit)
            return orgs.items
        except Exception as e:
            logger.error(f"Failed to get organizations: {str(e)}")
            raise
    
    def list_agent_runs(self, org_id: int = None, limit: int = 10, skip: int = 0, 
                       status: Optional[str] = None, user_id: Optional[int] = None,
                       project_id: Optional[int] = None):
        """List agent runs with filtering"""
        try:
            target_org_id = org_id or self.org_id
            
            # Convert status string to SourceType if needed
            source_type = None
            if status:
                # Map status to source type if applicable
                pass
            
            runs = self.client.list_agent_runs(
                org_id=target_org_id,
                user_id=user_id,
                source_type=source_type,
                skip=skip,
                limit=limit
            )
            
            # Convert to dictionary format for compatibility
            result = {
                'items': [],
                'total': runs.total,
                'page': runs.page,
                'size': runs.size,
                'pages': runs.pages
            }
            
            # Convert each run to dictionary
            for run in runs.items:
                run_dict = {
                    'id': run.id,
                    'organization_id': run.organization_id,
                    'status': run.status or 'unknown',
                    'prompt': getattr(run, 'prompt', None) or "No prompt available",
                    'result': run.result,
                    'created_at': run.created_at,
                    'updated_at': getattr(run, 'updated_at', run.created_at),
                    'completed_at': getattr(run, 'completed_at', None),
                    'web_url': run.web_url,
                    'source_type': run.source_type,
                    'metadata': run.metadata or {},
                    'progress': self._calculate_progress(run.status or 'unknown'),
                    'cost': getattr(run, 'cost', 0.0),
                    'tokens_used': getattr(run, 'tokens_used', 0),
                    'project_id': getattr(run, 'project_id', None),
                    'project_name': getattr(run, 'project_name', 'Default Project'),
                    'github_pull_requests': run.github_pull_requests or []
                }
                result['items'].append(run_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list agent runs: {str(e)}")
            raise
    
    def get_agent_run(self, org_id: int = None, run_id: int = None):
        """Get specific agent run"""
        try:
            target_org_id = org_id or self.org_id
            run = self.client.get_agent_run(target_org_id, run_id)
            
            # Convert to dictionary format
            return {
                'id': run.id,
                'organization_id': run.organization_id,
                'status': run.status or 'unknown',
                'prompt': getattr(run, 'prompt', None) or "No prompt available",
                'result': run.result,
                'created_at': run.created_at,
                'updated_at': getattr(run, 'updated_at', run.created_at),
                'completed_at': getattr(run, 'completed_at', None),
                'web_url': run.web_url,
                'source_type': run.source_type,
                'metadata': run.metadata or {},
                'progress': self._calculate_progress(run.status or 'unknown'),
                'cost': getattr(run, 'cost', 0.0),
                'tokens_used': getattr(run, 'tokens_used', 0),
                'project_id': getattr(run, 'project_id', None),
                'project_name': getattr(run, 'project_name', 'Default Project'),
                'github_pull_requests': run.github_pull_requests or []
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent run {run_id}: {str(e)}")
            raise
    
    def create_agent_run(self, org_id: int = None, prompt: str = None, 
                        metadata: Optional[Dict] = None, images: Optional[List[str]] = None,
                        project_id: Optional[int] = None):
        """Create new agent run"""
        try:
            target_org_id = org_id or self.org_id
            
            if not prompt:
                raise ValueError("Prompt is required")
            
            run = self.client.create_agent_run(
                org_id=target_org_id,
                prompt=prompt,
                images=images,
                metadata=metadata
            )
            
            # Convert to dictionary format
            return {
                'id': run.id,
                'organization_id': run.organization_id,
                'status': run.status or 'unknown',
                'prompt': getattr(run, 'prompt', None) or "No prompt available",
                'result': run.result,
                'created_at': run.created_at,
                'updated_at': getattr(run, 'updated_at', run.created_at),
                'completed_at': getattr(run, 'completed_at', None),
                'web_url': run.web_url,
                'source_type': run.source_type,
                'metadata': run.metadata or {},
                'progress': self._calculate_progress(run.status or 'unknown'),
                'cost': getattr(run, 'cost', 0.0),
                'tokens_used': getattr(run, 'tokens_used', 0),
                'project_id': getattr(run, 'project_id', None),
                'project_name': getattr(run, 'project_name', 'Default Project'),
                'github_pull_requests': run.github_pull_requests or []
            }
            
        except Exception as e:
            logger.error(f"Failed to create agent run: {str(e)}")
            raise
    
    def cancel_agent_run(self, org_id: int = None, run_id: int = None):
        """Cancel an agent run - try different methods"""
        try:
            target_org_id = org_id or self.org_id
            
            # Try different potential cancel endpoints
            cancel_methods = [
                # Method 1: Direct API call to cancel endpoint
                lambda: self._make_api_request('POST', f'/organizations/{target_org_id}/agent/run/{run_id}/cancel'),
                # Method 2: Try stop endpoint
                lambda: self._make_api_request('POST', f'/organizations/{target_org_id}/agent/run/{run_id}/stop'),
                # Method 3: Try DELETE method
                lambda: self._make_api_request('DELETE', f'/organizations/{target_org_id}/agent/run/{run_id}'),
            ]
            
            for i, method in enumerate(cancel_methods, 1):
                try:
                    result = method()
                    logger.info(f"✅ Cancel method {i} succeeded for run {run_id}")
                    return True
                except Exception as e:
                    logger.warning(f"Cancel method {i} failed for run {run_id}: {str(e)}")
                    continue
            
            logger.error(f"All cancel methods failed for run {run_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to cancel agent run {run_id}: {str(e)}")
            return False
    
    def resume_agent_run(self, org_id: int = None, run_id: int = None, prompt: str = None):
        """Resume a paused agent run"""
        try:
            target_org_id = org_id or self.org_id
            
            if not prompt:
                raise ValueError("Resume prompt is required")
            
            result = self.client.resume_agent_run(target_org_id, run_id, prompt)
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume agent run {run_id}: {str(e)}")
            return False
    
    def pause_agent_run(self, org_id: int = None, run_id: int = None):
        """Pause a running agent run"""
        try:
            target_org_id = org_id or self.org_id
            
            # Try pause endpoint
            result = self._make_api_request('POST', f'/organizations/{target_org_id}/agent/run/{run_id}/pause')
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause agent run {run_id}: {str(e)}")
            return False
    
    def get_agent_run_logs(self, org_id: int = None, run_id: int = None, limit: int = 100):
        """Get logs for an agent run"""
        try:
            target_org_id = org_id or self.org_id
            
            logs = self.client.get_agent_run_logs(target_org_id, run_id, limit=limit)
            
            # Convert to list of dictionaries
            result = []
            for log in logs.logs:
                result.append({
                    'id': getattr(log, 'id', len(result) + 1),
                    'agent_run_id': run_id,
                    'timestamp': log.timestamp,
                    'level': getattr(log, 'level', 'INFO'),
                    'message': log.message,
                    'details': getattr(log, 'details', None)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get logs for run {run_id}: {str(e)}")
            return []
    
    def get_projects(self, org_id: int = None, limit: int = 10):
        """Get projects for organization - try to discover project endpoints"""
        try:
            target_org_id = org_id or self.org_id
            
            # Try different potential project endpoints
            project_endpoints = [
                f'/organizations/{target_org_id}/projects',
                f'/organizations/{target_org_id}/repos',
                f'/projects'
            ]
            
            for endpoint in project_endpoints:
                try:
                    result = self._make_api_request('GET', endpoint, params={'limit': limit})
                    if result and 'items' in result:
                        projects = []
                        for item in result['items']:
                            projects.append({
                                'id': item.get('id', 1),
                                'name': item.get('name', 'Default Project'),
                                'description': item.get('description', 'Project description'),
                                'organization_id': target_org_id,
                                'created_at': item.get('created_at', datetime.now().isoformat()),
                                'run_count': item.get('run_count', 0),
                                'status': item.get('status', 'active')
                            })
                        return projects
                except Exception as e:
                    logger.debug(f"Project endpoint {endpoint} failed: {str(e)}")
                    continue
            
            # If no project endpoints work, return a default project
            logger.info("No project endpoints found, using default project")
            return [{
                'id': 1,
                'name': 'Default Project',
                'description': 'Default project for agent runs',
                'organization_id': target_org_id,
                'created_at': datetime.now().isoformat(),
                'run_count': 0,
                'status': 'active'
            }]
            
        except Exception as e:
            logger.error(f"Failed to get projects: {str(e)}")
            return []
    
    def get_run_statistics(self, org_id: int = None, days: int = 30):
        """Get run statistics for the last N days"""
        try:
            target_org_id = org_id or self.org_id
            
            # Get recent runs
            runs_data = self.list_agent_runs(target_org_id, limit=100)  # Get runs for statistics (API limit is 100)
            
            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_runs = []
            
            for run in runs_data['items']:
                try:
                    created_at = datetime.fromisoformat(run['created_at'].replace('Z', '+00:00').replace('+00:00', ''))
                    if created_at > cutoff_date:
                        recent_runs.append(run)
                except:
                    # If date parsing fails, include the run
                    recent_runs.append(run)
            
            # Calculate statistics
            total_runs = len(recent_runs)
            if total_runs == 0:
                return {
                    "total_runs": 0,
                    "status_breakdown": {},
                    "total_cost": 0.0,
                    "total_tokens": 0,
                    "average_cost_per_run": 0.0,
                    "success_rate": 0.0,
                    "period_days": days
                }
            
            # Status breakdown
            status_counts = {}
            for run in recent_runs:
                status = run['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Cost and token calculations
            total_cost = sum(run['cost'] for run in recent_runs)
            total_tokens = sum(run['tokens_used'] for run in recent_runs)
            
            # Success rate
            completed_runs = status_counts.get('completed', 0)
            success_rate = (completed_runs / total_runs) * 100 if total_runs > 0 else 0
            
            return {
                "total_runs": total_runs,
                "status_breakdown": status_counts,
                "total_cost": round(total_cost, 2),
                "total_tokens": total_tokens,
                "average_cost_per_run": round(total_cost / total_runs, 2) if total_runs > 0 else 0,
                "success_rate": round(success_rate, 1),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Failed to get run statistics: {str(e)}")
            raise
    
    def search_runs(self, org_id: int = None, query: str = None, limit: int = 10):
        """Search agent runs by prompt content"""
        try:
            target_org_id = org_id or self.org_id
            
            # Get all runs and filter locally (since we don't know if there's a search endpoint)
            all_runs = self.list_agent_runs(target_org_id, limit=100)
            
            if not query:
                return all_runs['items'][:limit]
            
            query_lower = query.lower()
            matching_runs = []
            
            for run in all_runs['items']:
                if (query_lower in run['prompt'].lower() or 
                    query_lower in (run.get('result', '') or '').lower() or
                    any(query_lower in str(v).lower() for v in run.get('metadata', {}).values())):
                    matching_runs.append(run)
                    
                    if len(matching_runs) >= limit:
                        break
            
            return matching_runs
            
        except Exception as e:
            logger.error(f"Failed to search runs: {str(e)}")
            return []
    
    def bulk_cancel_runs(self, org_id: int = None, run_ids: List[int] = None):
        """Cancel multiple runs"""
        if not run_ids:
            return {"cancelled": [], "failed": []}
        
        cancelled = []
        failed = []
        
        for run_id in run_ids:
            if self.cancel_agent_run(org_id, run_id):
                cancelled.append(run_id)
            else:
                failed.append(run_id)
        
        return {"cancelled": cancelled, "failed": failed}
    
    def _calculate_progress(self, status: str) -> int:
        """Calculate progress percentage based on status"""
        progress_map = {
            'pending': 0,
            'running': 50,
            'completed': 100,
            'failed': 0,
            'cancelled': 0,
            'paused': 25
        }
        return progress_map.get(status, 0)
    
    def _make_api_request(self, method: str, endpoint: str, **kwargs):
        """Make direct API request"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code >= 400:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        try:
            return response.json()
        except:
            return response.text
    
    def close(self):
        """Clean up resources"""
        if hasattr(self.client, 'close'):
            self.client.close()

# Global instance
_api_instance = None

def get_real_api() -> RealCodegenAPI:
    """Get the global real API instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = RealCodegenAPI()
    return _api_instance
