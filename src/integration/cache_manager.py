"""
Cache Manager Implementation

Provides caching capabilities for API responses to improve performance.
"""

import time
import json
import logging
from typing import Any, Optional, Dict
from dataclasses import dataclass
from threading import Lock

from ..interfaces.codegen_integration import ICacheManager

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL support"""
    value: Any
    created_at: float
    ttl: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl


class CacheManager(ICacheManager):
    """
    In-memory cache manager with TTL support.
    
    Provides caching for API responses to reduce redundant requests
    and improve performance.
    """
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """Initialize cache manager"""
        self.default_ttl = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        
        logger.debug(f"Initialized cache manager with TTL={ttl_seconds}s, max_size={max_size}")
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _enforce_size_limit(self) -> None:
        """Enforce maximum cache size by removing oldest entries"""
        if len(self._cache) <= self.max_size:
            return
        
        # Sort by creation time and remove oldest entries
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].created_at
        )
        
        entries_to_remove = len(self._cache) - self.max_size
        for i in range(entries_to_remove):
            key = sorted_entries[i][0]
            del self._cache[key]
        
        logger.debug(f"Removed {entries_to_remove} entries to enforce size limit")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value by key"""
        with self._lock:
            self._cleanup_expired()
            
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value with optional TTL"""
        with self._lock:
            # Use provided TTL or default
            effective_ttl = ttl if ttl is not None else self.default_ttl
            
            # Create cache entry
            entry = CacheEntry(
                value=value,
                created_at=time.time(),
                ttl=effective_ttl
            )
            
            self._cache[key] = entry
            
            # Cleanup and enforce limits
            self._cleanup_expired()
            self._enforce_size_limit()
            
            logger.debug(f"Cached value for key: {key} (TTL: {effective_ttl}s)")
    
    def delete(self, key: str) -> None:
        """Delete cached value"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache entry for key: {key}")
    
    def clear(self) -> None:
        """Clear all cached values"""
        with self._lock:
            entry_count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared {entry_count} cache entries")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        with self._lock:
            self._cleanup_expired()
            
            entry = self._cache.get(key)
            if entry is None:
                return False
            
            if entry.is_expired():
                del self._cache[key]
                return False
            
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            self._cleanup_expired()
            
            total_entries = len(self._cache)
            expired_count = sum(1 for entry in self._cache.values() if entry.is_expired())
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_count,
                "max_size": self.max_size,
                "default_ttl": self.default_ttl,
                "memory_usage_estimate": self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of cache (rough approximation)"""
        try:
            # Rough estimation based on JSON serialization
            total_size = 0
            for key, entry in self._cache.items():
                key_size = len(key.encode('utf-8'))
                try:
                    value_size = len(json.dumps(entry.value).encode('utf-8'))
                except (TypeError, ValueError):
                    # Fallback for non-serializable objects
                    value_size = len(str(entry.value).encode('utf-8'))
                
                total_size += key_size + value_size + 64  # 64 bytes overhead estimate
            
            return total_size
        except Exception:
            return -1  # Unable to estimate
    
    def cleanup(self) -> int:
        """Manual cleanup of expired entries, returns count of removed entries"""
        with self._lock:
            initial_count = len(self._cache)
            self._cleanup_expired()
            removed_count = initial_count - len(self._cache)
            
            if removed_count > 0:
                logger.info(f"Manual cleanup removed {removed_count} expired entries")
            
            return removed_count

