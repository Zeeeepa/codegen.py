"""
Simplified Configuration for Dashboard
"""

import os
from dataclasses import dataclass
from .exceptions import CodegenError


@dataclass
class Config:
    """Simple configuration class"""
    
    def __init__(self):
        self.api_token = os.getenv("CODEGEN_API_TOKEN")
        self.org_id = os.getenv("CODEGEN_ORG_ID")
        self.base_url = os.getenv("CODEGEN_BASE_URL", "https://api.codegen.com/v1")
        
        if not self.api_token:
            raise CodegenError("CODEGEN_API_TOKEN environment variable is required")
        
        if not self.org_id:
            raise CodegenError("CODEGEN_ORG_ID environment variable is required")
        
        try:
            self.org_id = int(self.org_id)
        except ValueError:
            raise CodegenError("CODEGEN_ORG_ID must be a valid integer")

