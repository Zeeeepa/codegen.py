"""
Metrics collection utilities
"""

import time
import logging
from datetime import datetime
from dataclasses import dataclass
from threading import Lock
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    method: str
    endpoint: str
    status_code: int
    duration_seconds: float
    timestamp: datetime
    request_id: str
    cached: bool = False


@dataclass
class ClientStats:
    """Comprehensive client statistics"""
    uptime_seconds: float
    total_requests: int
    total_errors: int
    error_rate: float
    requests_per_minute: float
    average_response_time: float
    cache_hit_rate: float
    status_code_distribution: Dict[int, int]
    recent_requests: List[RequestMetrics]


class MetricsCollector:
    """Advanced metrics collection and analysis"""
    
    def __init__(self):
        self.requests: List[RequestMetrics] = []
        self.start_time = datetime.now()
        self._lock = Lock()
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        duration: float,
        status_code: int,
        request_id: str,
        cached: bool = False,
    ):
        """Record a request with comprehensive metrics"""
        with self._lock:
            metric = RequestMetrics(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                timestamp=datetime.now(),
                request_id=request_id,
                cached=cached,
            )
            self.requests.append(metric)
            
            # Keep only recent requests (last 1000)
            if len(self.requests) > 1000:
                self.requests = self.requests[-1000:]
    
    def get_stats(self) -> ClientStats:
        """Get comprehensive client statistics"""
        with self._lock:
            if not self.requests:
                return ClientStats(
                    uptime_seconds=0,
                    total_requests=0,
                    total_errors=0,
                    error_rate=0,
                    requests_per_minute=0,
                    average_response_time=0,
                    cache_hit_rate=0,
                    status_code_distribution={},
                    recent_requests=[],
                )
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            total_requests = len(self.requests)
            error_requests = [r for r in self.requests if r.status_code >= 400]
            cached_requests = [r for r in self.requests if r.cached]
            
            avg_response_time = (
                sum(r.duration_seconds for r in self.requests) / total_requests
            )
            error_rate = (
                len(error_requests) / total_requests if total_requests > 0 else 0
            )
            cache_hit_rate = (
                len(cached_requests) / total_requests if total_requests > 0 else 0
            )
            requests_per_minute = total_requests / (uptime / 60) if uptime > 0 else 0
            
            # Status code distribution
            status_codes = {}
            for request in self.requests:
                status_codes[request.status_code] = (
                    status_codes.get(request.status_code, 0) + 1
                )
            
            return ClientStats(
                uptime_seconds=uptime,
                total_requests=total_requests,
                total_errors=len(error_requests),
                error_rate=error_rate,
                requests_per_minute=requests_per_minute,
                average_response_time=avg_response_time,
                cache_hit_rate=cache_hit_rate,
                status_code_distribution=status_codes,
                recent_requests=self.requests[-10:],
            )
    
    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self.requests.clear()
            self.start_time = datetime.now()

