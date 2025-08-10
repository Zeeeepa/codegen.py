"""
Caching utilities
"""

import time
import logging
from threading import Lock
from typing import Optional, Any, Dict

logger = logging.getLogger(__name__)


class CacheManager:
    """Advanced in-memory cache with TTL support and statistics"""
    
    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # Check if expired
            if time.time() - self._timestamps[key] > self.ttl_seconds:
                del self._cache[key]
                del self._timestamps[key]
                del self._access_counts[key]
                self._misses += 1
                return None
            
            self._hits += 1
            self._access_counts[key] = self._access_counts.get(key, 0) + 1
            return self._cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache with TTL"""
        with self._lock:
            # Evict oldest if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                if self._timestamps:  # Check if timestamps dict is not empty
                    oldest_key = min(self._timestamps, key=self._timestamps.get)
                    del self._cache[oldest_key]
                    del self._timestamps[oldest_key]
                    if oldest_key in self._access_counts:
                        del self._access_counts[oldest_key]
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._access_counts[key] = self._access_counts.get(key, 0)
    
    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._access_counts.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) * 100 if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate_percentage": hit_rate,
                "ttl_seconds": self.ttl_seconds,
            }

