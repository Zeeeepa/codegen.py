"""
Metrics utilities for the Codegen API client.

This module contains classes for tracking API client metrics.
"""

import time
import uuid
from datetime import datetime
from threading import Lock
from typing import Dict, List, Any, Optional

from codegen.models.responses import RequestMetrics, ClientStats


class MetricsTracker:
    """Tracks metrics for API client usage."""
    
    def __init__(self, max_recent_requests: int = 50):
        """Initialize the metrics tracker.
        
        Args:
            max_recent_requests: Maximum number of recent requests to track.
        """
        self.start_time = time.time()
        self.total_requests = 0
        self.total_errors = 0
        self.total_cache_hits = 0
        self.total_duration = 0.0
        self.status_code_distribution: Dict[int, int] = {}
        self.recent_requests: List[RequestMetrics] = []
        self.max_recent_requests = max_recent_requests
        self.lock = Lock()
    
    def record_request(self, method: str, endpoint: str, duration: float, 
                      status_code: int, request_id: Optional[str] = None, 
                      cached: bool = False) -> None:
        """Record metrics for an API request.
        
        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint.
            duration: Request duration in seconds.
            status_code: HTTP status code.
            request_id: Unique request ID.
            cached: Whether the response was from cache.
        """
        with self.lock:
            self.total_requests += 1
            
            if cached:
                self.total_cache_hits += 1
            
            if status_code >= 400:
                self.total_errors += 1
            
            self.total_duration += duration
            
            # Update status code distribution
            if status_code in self.status_code_distribution:
                self.status_code_distribution[status_code] += 1
            else:
                self.status_code_distribution[status_code] = 1
            
            # Add to recent requests
            metrics = RequestMetrics(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_seconds=duration,
                timestamp=datetime.now(),
                request_id=request_id or str(uuid.uuid4()),
                cached=cached,
            )
            
            self.recent_requests.append(metrics)
            
            # Trim recent requests if needed
            if len(self.recent_requests) > self.max_recent_requests:
                self.recent_requests = self.recent_requests[-self.max_recent_requests:]
    
    def get_stats(self) -> ClientStats:
        """Get current client statistics.
        
        Returns:
            A ClientStats object with current metrics.
        """
        with self.lock:
            uptime = time.time() - self.start_time
            
            # Calculate derived metrics
            error_rate = self.total_errors / self.total_requests if self.total_requests > 0 else 0
            avg_response_time = self.total_duration / self.total_requests if self.total_requests > 0 else 0
            cache_hit_rate = self.total_cache_hits / self.total_requests if self.total_requests > 0 else 0
            
            # Calculate requests per minute
            if uptime >= 60:
                requests_per_minute = self.total_requests / (uptime / 60)
            else:
                # If uptime is less than a minute, extrapolate
                requests_per_minute = self.total_requests * (60 / max(uptime, 1))
            
            return ClientStats(
                uptime_seconds=uptime,
                total_requests=self.total_requests,
                total_errors=self.total_errors,
                error_rate=error_rate,
                requests_per_minute=requests_per_minute,
                average_response_time=avg_response_time,
                cache_hit_rate=cache_hit_rate,
                status_code_distribution=self.status_code_distribution.copy(),
                recent_requests=self.recent_requests.copy(),
            )
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self.lock:
            self.start_time = time.time()
            self.total_requests = 0
            self.total_errors = 0
            self.total_cache_hits = 0
            self.total_duration = 0.0
            self.status_code_distribution.clear()
            self.recent_requests.clear()

