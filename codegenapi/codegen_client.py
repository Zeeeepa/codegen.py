"""
Real Codegen API client for agent management
"""

import requests
import json
from typing import Dict, List, Any, Optional
from .config import Config

class CodegenClient:
    """Real client for Codegen API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.base_url
        self.headers = {
            'Authorization': f'Bearer {config.api_token}',
            'Content-Type': 'application/json'
        }
        self.org_id = config.org_id
    
    def list_agent_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List agent runs from the API"""
        
        try:
            url = f"{self.base_url}/agent-runs"
            params = {
                'org_id': self.org_id,
                'limit': limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('runs', [])
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def get_agent_run(self, run_id: int) -> Dict[str, Any]:
        """Get specific agent run"""
        
        try:
            url = f"{self.base_url}/agent-runs/{run_id}"
            params = {'org_id': self.org_id}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {}
    
    def create_agent_run(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Create new agent run"""
        
        try:
            url = f"{self.base_url}/agent-runs"
            
            payload = {
                'org_id': self.org_id,
                'prompt': prompt,
                **kwargs
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {}
    
    def cancel_agent_run(self, run_id: int) -> bool:
        """Cancel agent run"""
        
        try:
            url = f"{self.base_url}/agent-runs/{run_id}/cancel"
            params = {'org_id': self.org_id}
            
            response = requests.post(url, headers=self.headers, params=params, timeout=30)
            
            return response.status_code in [200, 204]
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def get_agent_run_logs(self, run_id: int) -> List[Dict[str, Any]]:
        """Get logs for agent run"""
        
        try:
            url = f"{self.base_url}/agent-runs/{run_id}/logs"
            params = {'org_id': self.org_id}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('logs', [])
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

