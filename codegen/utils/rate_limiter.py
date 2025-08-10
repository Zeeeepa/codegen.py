"""
Rate limiting utilities
"""

import time
import logging
from threading import Lock
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class RateLimiter:
    """Thread-safe rate limiter with sliding window"""
    
    def __init__(self, requests_per_period: int, period_seconds: int):
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.requests: List[float] = []
        self.lock = Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            # Remove old requests
            self.requests = [
                req_time
                for req_time in self.requests
                if now - req_time < self.period_seconds
            ]
            
            if len(self.requests) >= self.requests_per_period:
                sleep_time = self.period_seconds - (now - self.requests[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                    time.sleep(sleep_time)
            
            self.requests.append(now)
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current rate limit usage"""
        with self.lock:
            now = time.time()
            recent_requests = [
                req_time
                for req_time in self.requests
                if now - req_time < self.period_seconds
            ]
            return {
                "current_requests": len(recent_requests),
                "max_requests": self.requests_per_period,
                "period_seconds": self.period_seconds,
                "usage_percentage": (len(recent_requests) / self.requests_per_period) * 100,
            }

