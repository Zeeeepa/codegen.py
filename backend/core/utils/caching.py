"""
Caching utilities for the Codegen API client.

This module contains classes for caching API responses.
"""

import time
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from threading import Lock


class ResponseCache:
    """Simple in-memory cache for API responses."""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        """Initialize the cache.
        
        Args:
            max_size: Maximum number of items to store in the cache.
            ttl: Time-to-live in seconds for cached items.
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.lock = Lock()
    
    def _generate_key(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     json_data: Optional[Dict] = None) -> str:
        """Generate a cache key from request parameters.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint.
            params: Query parameters.
            json_data: JSON request body.
            
        Returns:
            A string key for the cache.
        """
        key_parts = [method.upper(), endpoint]
        
        if params:
            # Sort params to ensure consistent keys
            sorted_params = json.dumps(params, sort_keys=True)
            key_parts.append(sorted_params)
        
        if json_data:
            # Sort json data to ensure consistent keys
            sorted_json = json.dumps(json_data, sort_keys=True)
            key_parts.append(sorted_json)
        
        # Join parts and create a hash
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, method: str, endpoint: str, params: Optional[Dict] = None, 
           json_data: Optional[Dict] = None) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint.
            params: Query parameters.
            json_data: JSON request body.
            
        Returns:
            The cached value, or None if not found or expired.
        """
        key = self._generate_key(method, endpoint, params, json_data)
        
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp <= self.ttl:
                    return value
                else:
                    # Remove expired item
                    del self.cache[key]
        
        return None
    
    def set(self, method: str, endpoint: str, value: Any, params: Optional[Dict] = None, 
           json_data: Optional[Dict] = None) -> None:
        """Set a value in the cache.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint.
            value: Value to cache.
            params: Query parameters.
            json_data: JSON request body.
        """
        key = self._generate_key(method, endpoint, params, json_data)
        
        with self.lock:
            # Evict oldest items if cache is full
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
                del self.cache[oldest_key]
            
            self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            A dictionary with cache statistics.
        """
        with self.lock:
            current_time = time.time()
            total_items = len(self.cache)
            expired_items = sum(1 for _, timestamp in self.cache.values() 
                               if current_time - timestamp > self.ttl)
            valid_items = total_items - expired_items
            
            return {
                "total_items": total_items,
                "valid_items": valid_items,
                "expired_items": expired_items,
                "max_size": self.max_size,
                "ttl": self.ttl,
                "utilization": total_items / self.max_size if self.max_size > 0 else 0,
            }

