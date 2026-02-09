"""
Observability & Metrics
=======================
Lightweight metrics collection for monitoring system health.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time
from collections import defaultdict

from app.config import settings


@dataclass
class MetricsCollector:
    """
    In-memory metrics collector for MVP.
    
    In production, this would integrate with Prometheus, DataDog, etc.
    """
    
    request_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    request_durations: Dict[str, list] = field(default_factory=lambda: defaultdict(list))
    error_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    active_requests: int = 0
    
    # Detection metrics
    alerts_created: int = 0
    alerts_resolved: int = 0
    detection_scores: list = field(default_factory=list)
    
    # System metrics
    start_time: datetime = field(default_factory=datetime.now)
    
    def track_request_start(self, method: str, path: str) -> None:
        """Track request start."""
        self.active_requests += 1
        key = f"{method}:{path}"
        self.request_counts[key] += 1
    
    def track_request_end(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
    ) -> None:
        """Track request completion."""
        self.active_requests = max(0, self.active_requests - 1)
        
        key = f"{method}:{path}"
        
        # Keep last 100 durations per endpoint
        if len(self.request_durations[key]) >= 100:
            self.request_durations[key].pop(0)
        self.request_durations[key].append(duration)
        
        # Track errors
        if status_code >= 400:
            error_key = f"{key}:{status_code}"
            self.error_counts[error_key] += 1
    
    def track_request_error(
        self,
        method: str,
        path: str,
        error_type: str,
        duration: float,
    ) -> None:
        """Track request error."""
        self.active_requests = max(0, self.active_requests - 1)
        
        error_key = f"{method}:{path}:{error_type}"
        self.error_counts[error_key] += 1
    
    def track_alert_created(self, severity: str) -> None:
        """Track alert creation."""
        self.alerts_created += 1
    
    def track_alert_resolved(self, decision: str) -> None:
        """Track alert resolution."""
        self.alerts_resolved += 1
    
    def track_detection_score(self, score: float) -> None:
        """Track detection score for distribution analysis."""
        # Keep last 1000 scores
        if len(self.detection_scores) >= 1000:
            self.detection_scores.pop(0)
        self.detection_scores.append(score)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate average latencies
        avg_latencies = {}
        for key, durations in self.request_durations.items():
            if durations:
                avg_latencies[key] = {
                    "avg_ms": round(sum(durations) / len(durations) * 1000, 2),
                    "min_ms": round(min(durations) * 1000, 2),
                    "max_ms": round(max(durations) * 1000, 2),
                    "count": len(durations),
                }
        
        # Calculate score distribution
        score_distribution = {}
        if self.detection_scores:
            scores = sorted(self.detection_scores)
            score_distribution = {
                "min": round(min(scores), 2),
                "max": round(max(scores), 2),
                "avg": round(sum(scores) / len(scores), 2),
                "p50": round(scores[len(scores) // 2], 2),
                "p95": round(scores[int(len(scores) * 0.95)], 2) if len(scores) >= 20 else None,
            }
        
        return {
            "uptime_seconds": round(uptime, 2),
            "active_requests": self.active_requests,
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "alerts_created": self.alerts_created,
            "alerts_resolved": self.alerts_resolved,
            "latencies": avg_latencies,
            "score_distribution": score_distribution,
            "top_endpoints": sorted(
                self.request_counts.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10],
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.request_counts.clear()
        self.request_durations.clear()
        self.error_counts.clear()
        self.active_requests = 0
        self.alerts_created = 0
        self.alerts_resolved = 0
        self.detection_scores.clear()
        self.start_time = datetime.now()


# Global metrics instance
metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector."""
    return metrics


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, name: Optional[str] = None):
        self.name = name
        self.start_time: float = 0
        self.duration: float = 0
    
    def __enter__(self) -> "Timer":
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.duration = time.perf_counter() - self.start_time
    
    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return self.duration * 1000
