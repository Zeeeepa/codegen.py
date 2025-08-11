"""
Authentication Manager Implementation

Handles API token validation, storage, and user session management.
"""

import os
import json
import logging
from typing import Optional
from pathlib import Path

from ..interfaces.codegen_integration import IAuthManager
from .error_handling import CodegenAuthError

logger = logging.getLogger(__name__)


class AuthManager(IAuthManager):
    """
    Authentication manager for Codegen API tokens.
    
    Handles token storage, validation, and session management.
    """
    
    def __init__(self, token: Optional[str] = None):
        """Initialize auth manager with optional token"""
        self._token: Optional[str] = None
        self._config_dir = Path.home() / ".codegen"
        self._token_file = self._config_dir / "token"
        
        # Set token from parameter, environment, or stored file
        if token:
            self.set_token(token)
        else:
            # Try environment variable
            env_token = os.getenv("CODEGEN_API_TOKEN")
            if env_token:
                self.set_token(env_token)
            else:
                # Try loading from stored file
                self._load_stored_token()
    
    def _load_stored_token(self) -> None:
        """Load token from stored file"""
        try:
            if self._token_file.exists():
                with open(self._token_file, 'r') as f:
                    data = json.load(f)
                    self._token = data.get("token")
                    if self._token:
                        logger.debug("Loaded stored authentication token")
        except Exception as e:
            logger.warning(f"Failed to load stored token: {e}")
    
    def _save_token(self) -> None:
        """Save token to file"""
        try:
            self._config_dir.mkdir(exist_ok=True)
            with open(self._token_file, 'w') as f:
                json.dump({"token": self._token}, f)
            
            # Set restrictive permissions
            os.chmod(self._token_file, 0o600)
            logger.debug("Saved authentication token")
        except Exception as e:
            logger.warning(f"Failed to save token: {e}")
    
    def validate_token(self, token: str) -> bool:
        """Validate an API token format"""
        if not token:
            return False
        
        # Basic format validation for Codegen tokens
        # Tokens typically start with 'sk-' and are followed by alphanumeric characters
        if not token.startswith('sk-'):
            return False
        
        if len(token) < 20:  # Minimum reasonable length
            return False
        
        # Check for valid characters (alphanumeric and hyphens)
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-')
        if not all(c in allowed_chars for c in token):
            return False
        
        return True
    
    def get_current_token(self) -> Optional[str]:
        """Get the current active token"""
        return self._token
    
    def set_token(self, token: str) -> None:
        """Set the API token"""
        if not self.validate_token(token):
            raise CodegenAuthError("Invalid token format")
        
        self._token = token
        self._save_token()
        logger.info("Authentication token updated")
    
    def clear_token(self) -> None:
        """Clear the stored token"""
        self._token = None
        
        # Remove stored token file
        try:
            if self._token_file.exists():
                self._token_file.unlink()
                logger.info("Authentication token cleared")
        except Exception as e:
            logger.warning(f"Failed to remove token file: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self._token is not None and self.validate_token(self._token)
    
    def get_token_info(self) -> dict:
        """Get information about the current token (for debugging)"""
        if not self._token:
            return {"authenticated": False}
        
        return {
            "authenticated": True,
            "token_prefix": self._token[:8] + "..." if len(self._token) > 8 else self._token,
            "token_length": len(self._token),
            "stored_file_exists": self._token_file.exists()
        }

