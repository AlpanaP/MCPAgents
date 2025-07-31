"""
Monitoring and Metrics System for Business License Navigator.

This module provides comprehensive monitoring capabilities:
- Performance metrics tracking
- Error monitoring and alerting
- Usage analytics
- Health checks
- Resource monitoring
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import psutil
import json


@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a component."""
    response_time_ms: float = 0.0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    success_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


class MetricsCollector:
    """Collects and stores metrics data."""
    
    def __init__(self, max_history: int = 1000):
        """Initialize the metrics collector."""
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric data point."""
        metric_point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            tags=tags or {}
        )
        self.metrics[metric_name].append(metric_point)
    
    def get_metric_history(self, metric_name: str, minutes: int = 60) -> List[MetricPoint]:
        """Get metric history for the last N minutes."""
        if metric_name not in self.metrics:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            point for point in self.metrics[metric_name]
            if point.timestamp >= cutoff_time
        ]
    
    def get_average_metric(self, metric_name: str, minutes: int = 60) -> float:
        """Get average value for a metric over the last N minutes."""
        history = self.get_metric_history(metric_name, minutes)
        if not history:
            return 0.0
        
        return sum(point.value for point in history) / len(history)
    
    def get_metric_summary(self, metric_name: str, minutes: int = 60) -> Dict[str, float]:
        """Get summary statistics for a metric."""
        history = self.get_metric_history(metric_name, minutes)
        if not history:
            return {"min": 0.0, "max": 0.0, "avg": 0.0, "count": 0}
        
        values = [point.value for point in history]
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values)
        }


class PerformanceMonitor:
    """Monitors performance of various components."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics_collector = MetricsCollector()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=1000)
    
    def record_request(self, response_time_ms: float, success: bool = True):
        """Record a request with its response time."""
        self.request_count += 1
        if not success:
            self.error_count += 1
        
        self.response_times.append(response_time_ms)
        self.metrics_collector.record_metric("response_time_ms", response_time_ms)
        self.metrics_collector.record_metric("requests_total", 1)
        
        if not success:
            self.metrics_collector.record_metric("errors_total", 1)
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        current_time = time.time()
        uptime_seconds = current_time - self.start_time
        
        # Calculate requests per second
        requests_per_second = self.request_count / uptime_seconds if uptime_seconds > 0 else 0
        
        # Calculate error rate
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0
        success_rate = 1 - error_rate
        
        # Calculate average response time
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        # Get system metrics
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
        cpu_usage = psutil.cpu_percent()
        
        return PerformanceMetrics(
            response_time_ms=avg_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            success_rate=success_rate,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        metrics = self.get_performance_metrics()
        
        # Define thresholds
        thresholds = {
            "response_time_ms": 5000,
            "error_rate": 0.05,
            "memory_usage_percent": 80,
            "cpu_usage_percent": 80
        }
        
        # Check health
        health_checks = {
            "response_time": metrics.response_time_ms <= thresholds["response_time_ms"],
            "error_rate": metrics.error_rate <= thresholds["error_rate"],
            "memory_usage": (metrics.memory_usage_mb / psutil.virtual_memory().total * 100) <= thresholds["memory_usage_percent"],
            "cpu_usage": metrics.cpu_usage_percent <= thresholds["cpu_usage_percent"]
        }
        
        overall_healthy = all(health_checks.values())
        
        return {
            "healthy": overall_healthy,
            "checks": health_checks,
            "metrics": {
                "response_time_ms": metrics.response_time_ms,
                "requests_per_second": metrics.requests_per_second,
                "error_rate": metrics.error_rate,
                "success_rate": metrics.success_rate,
                "memory_usage_mb": metrics.memory_usage_mb,
                "cpu_usage_percent": metrics.cpu_usage_percent,
                "uptime_seconds": time.time() - self.start_time
            }
        }


class ErrorMonitor:
    """Monitors and tracks errors."""
    
    def __init__(self, max_errors: int = 1000):
        """Initialize the error monitor."""
        self.max_errors = max_errors
        self.errors = deque(maxlen=max_errors)
        self.error_counts = defaultdict(int)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Record an error."""
        error_entry = {
            "timestamp": datetime.now(),
            "type": error_type,
            "message": error_message,
            "context": context or {}
        }
        
        self.errors.append(error_entry)
        self.error_counts[error_type] += 1
        
        self.logger.error(f"Error recorded: {error_type} - {error_message}")
    
    def get_error_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get error summary for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_errors = [
            error for error in self.errors
            if error["timestamp"] >= cutoff_time
        ]
        
        error_types = defaultdict(int)
        for error in recent_errors:
            error_types[error["type"]] += 1
        
        return {
            "total_errors": len(recent_errors),
            "error_types": dict(error_types),
            "recent_errors": recent_errors[-10:]  # Last 10 errors
        }
    
    def get_error_rate(self, minutes: int = 60) -> float:
        """Get error rate for the last N minutes."""
        summary = self.get_error_summary(minutes)
        return summary["total_errors"] / (minutes * 60) if minutes > 0 else 0


class UsageAnalytics:
    """Tracks usage analytics."""
    
    def __init__(self):
        """Initialize usage analytics."""
        self.usage_data = defaultdict(lambda: defaultdict(int))
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def record_usage(self, feature: str, state: str = None, business_type: str = None):
        """Record usage of a feature."""
        self.usage_data[feature]["total"] += 1
        if state:
            self.usage_data[feature][f"state_{state}"] += 1
        if business_type:
            self.usage_data[feature][f"business_{business_type}"] += 1
    
    def get_usage_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get usage summary."""
        return {
            "features": dict(self.usage_data),
            "total_usage": sum(data["total"] for data in self.usage_data.values()),
            "most_used_features": sorted(
                self.usage_data.items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )[:5]
        }


class MonitoringSystem:
    """Main monitoring system that coordinates all monitoring components."""
    
    def __init__(self):
        """Initialize the monitoring system."""
        self.performance_monitor = PerformanceMonitor()
        self.error_monitor = ErrorMonitor()
        self.usage_analytics = UsageAnalytics()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background monitoring thread."""
        def monitor_loop():
            while True:
                try:
                    # Record system metrics
                    memory_usage = psutil.virtual_memory().used / (1024 * 1024)
                    cpu_usage = psutil.cpu_percent()
                    
                    self.performance_monitor.metrics_collector.record_metric(
                        "system_memory_mb", memory_usage
                    )
                    self.performance_monitor.metrics_collector.record_metric(
                        "system_cpu_percent", cpu_usage
                    )
                    
                    time.sleep(60)  # Update every minute
                except Exception as e:
                    self.logger.error(f"Error in background monitoring: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def record_request(self, response_time_ms: float, success: bool = True, 
                      feature: str = None, state: str = None, business_type: str = None):
        """Record a request with full context."""
        self.performance_monitor.record_request(response_time_ms, success)
        
        if feature:
            self.usage_analytics.record_usage(feature, state, business_type)
    
    def record_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Record an error."""
        self.error_monitor.record_error(error_type, error_message, context)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        performance_health = self.performance_monitor.get_health_status()
        error_summary = self.error_monitor.get_error_summary(60)
        
        return {
            "overall_healthy": performance_health["healthy"],
            "performance": performance_health,
            "errors": error_summary,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metrics_dashboard(self) -> Dict[str, Any]:
        """Get metrics dashboard data."""
        return {
            "performance": self.performance_monitor.get_performance_metrics().__dict__,
            "errors": self.error_monitor.get_error_summary(60),
            "usage": self.usage_analytics.get_usage_summary(),
            "system": {
                "memory_mb": psutil.virtual_memory().used / (1024 * 1024),
                "cpu_percent": psutil.cpu_percent(),
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file."""
        try:
            dashboard_data = self.get_metrics_dashboard()
            with open(filepath, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            self.logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")


# Global monitoring system instance
monitoring_system = MonitoringSystem() 