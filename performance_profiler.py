"""
Performance profiling utilities for real-time speech analysis system.
Provides timing decorators and metrics collection for each component.
"""

import time
import functools
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    component_name: str
    operation_name: str
    duration_ms: float
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None

class PerformanceProfiler:
    """Centralized performance profiling for all system components."""
    
    def __init__(self):
        self.metrics: list[PerformanceMetrics] = []
        self.start_times: Dict[str, float] = {}
        
    def start_timing(self, component: str, operation: str) -> str:
        """Start timing an operation."""
        key = f"{component}:{operation}:{time.time()}"
        self.start_times[key] = time.time()
        return key
        
    def end_timing(self, key: str, metadata: Optional[Dict[str, Any]] = None) -> PerformanceMetrics:
        """End timing and record metrics."""
        if key not in self.start_times:
            raise ValueError(f"Timing key {key} not found")
            
        start_time = self.start_times.pop(key)
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        component, operation, _ = key.split(":", 2)
        
        metrics = PerformanceMetrics(
            component_name=component,
            operation_name=operation,
            duration_ms=duration_ms,
            timestamp=end_time,
            metadata=metadata
        )
        
        self.metrics.append(metrics)
        return metrics
        
    def get_component_stats(self, component_name: str) -> Dict[str, Any]:
        """Get statistics for a specific component."""
        component_metrics = [m for m in self.metrics if m.component_name == component_name]
        
        if not component_metrics:
            return {
                "component": component_name,
                "total_operations": 0,
                "avg_duration_ms": 0.0,
                "min_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "total_duration_ms": 0.0,
                "operations_per_second": 0.0,
                "last_operation_time": 0.0
            }
            
        durations = [m.duration_ms for m in component_metrics]
        last_operation = max(m.timestamp for m in component_metrics)
        
        return {
            "component": component_name,
            "total_operations": len(component_metrics),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "total_duration_ms": sum(durations),
            "operations_per_second": 1000 / (sum(durations) / len(durations)) if durations else 0,
            "last_operation_time": last_operation
        }
        
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all components."""
        components = set(m.component_name for m in self.metrics)
        return {comp: self.get_component_stats(comp) for comp in components}
        
    def export_metrics(self, filename: str):
        """Export all metrics to JSON file."""
        with open(filename, 'w') as f:
            json.dump([asdict(m) for m in self.metrics], f, indent=2)
            
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()
        self.start_times.clear()

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics for dashboard display."""
        stats = self.get_all_stats()
        
        # Calculate overall metrics
        total_events = sum(s.get('total_operations', 0) for s in stats.values())
        avg_latency = sum(s.get('avg_duration_ms', 0) for s in stats.values()) / len(stats) if stats else 0
        
        # Map component names to dashboard categories
        component_mapping = {
            'audio_capture': 'audio',
            'transcription': 'transcription',
            'sentiment': 'sentiment',
            'sentiment_analysis': 'sentiment',
            'events': 'events',
            'event_emission': 'events',
            'utterance_segmentation': 'transcription'
        }
        
        # Group stats by dashboard categories
        grouped_stats = {}
        for component_name, component_stats in stats.items():
            dashboard_name = component_mapping.get(component_name, component_name)
            if dashboard_name not in grouped_stats:
                grouped_stats[dashboard_name] = {
                    'total_operations': 0,
                    'total_duration_ms': 0.0,
                    'average_time': 0.0,
                    'min_duration_ms': float('inf'),
                    'max_duration_ms': 0.0
                }
            
            grouped_stats[dashboard_name]['total_operations'] += component_stats.get('total_operations', 0)
            grouped_stats[dashboard_name]['total_duration_ms'] += component_stats.get('total_duration_ms', 0.0)
            
            # Update min/max
            if component_stats.get('min_duration_ms', float('inf')) < grouped_stats[dashboard_name]['min_duration_ms']:
                grouped_stats[dashboard_name]['min_duration_ms'] = component_stats.get('min_duration_ms', float('inf'))
            if component_stats.get('max_duration_ms', 0) > grouped_stats[dashboard_name]['max_duration_ms']:
                grouped_stats[dashboard_name]['max_duration_ms'] = component_stats.get('max_duration_ms', 0)
        
        # Calculate averages for each group
        for category, data in grouped_stats.items():
            if data['total_operations'] > 0:
                data['average_time'] = data['total_duration_ms'] / data['total_operations']
            else:
                data['average_time'] = 0.0
        
        return {
            'total_events': total_events,
            'average_latency': avg_latency,
            'components': grouped_stats,
            'timestamp': time.time()
        }

    @classmethod
    def get_instance(cls):
        """Get the global profiler instance."""
        return profiler

# Global profiler instance
profiler = PerformanceProfiler()

def timing_decorator(component_name: str):
    """Decorator to automatically time function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = profiler.start_timing(component_name, func.__name__)
            try:
                result = func(*args, **kwargs)
                metadata = {"args_length": len(args), "kwargs_keys": list(kwargs.keys())}
                profiler.end_timing(key, metadata)
                return result
            except Exception as e:
                profiler.end_timing(key, {"error": str(e), "error_type": type(e).__name__})
                raise
        return wrapper
    return decorator

class ComponentProfiler:
    """Context manager for profiling specific operations."""
    
    def __init__(self, component_name: str, operation_name: str, metadata: Optional[Dict[str, Any]] = None):
        self.component_name = component_name
        self.operation_name = operation_name
        self.metadata = metadata
        self.key = None
        
    def __enter__(self):
        self.key = profiler.start_timing(self.component_name, self.operation_name)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            error_metadata = {"error": str(exc_val), "error_type": exc_type.__name__}
            if self.metadata:
                error_metadata.update(self.metadata)
            profiler.end_timing(self.key, error_metadata)
        else:
            profiler.end_timing(self.key, self.metadata)

# Convenience functions for common profiling patterns
def profile_audio_capture(func):
    """Decorator for audio capture operations."""
    return timing_decorator("audio_capture")(func)

def profile_transcription(func):
    """Decorator for transcription operations."""
    return timing_decorator("transcription")(func)

def profile_sentiment_analysis(func):
    """Decorator for sentiment analysis operations."""
    return timing_decorator("sentiment_analysis")(func)

def profile_event_emission(func):
    """Decorator for event emission operations."""
    return timing_decorator("event_emission")(func)

def profile_utterance_segmentation(func):
    """Decorator for utterance segmentation operations."""
    return timing_decorator("utterance_segmentation")(func)

# Performance monitoring dashboard
class PerformanceDashboard:
    """Real-time performance monitoring dashboard."""
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.running = False
        
    def start_monitoring(self):
        """Start real-time monitoring."""
        self.running = True
        import threading
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.running = False
        
    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.running:
            stats = profiler.get_all_stats()
            logger.info("=== Performance Stats ===")
            for component, stats_data in stats.items():
                logger.info(f"{component}: avg={stats_data.get('avg_duration_ms', 0):.2f}ms, "
                          f"ops/sec={stats_data.get('operations_per_second', 0):.2f}")
            time.sleep(self.update_interval)
            
    def print_summary(self):
        """Print current performance summary."""
        stats = profiler.get_all_stats()
        print("\n=== Performance Summary ===")
        for component, data in stats.items():
            print(f"\n{component.upper()}:")
            print(f"  Total operations: {data.get('total_operations', 0)}")
            print(f"  Average duration: {data.get('avg_duration_ms', 0):.2f}ms")
            print(f"  Min/Max duration: {data.get('min_duration_ms', 0):.2f}ms / {data.get('max_duration_ms', 0):.2f}ms")
            print(f"  Operations/sec: {data.get('operations_per_second', 0):.2f}")