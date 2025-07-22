#!/usr/bin/env python3
"""
Test script to verify performance profiling and dashboard functionality.
"""

import asyncio
import time
import random
from performance_profiler import PerformanceProfiler, ComponentProfiler
from performance_dashboard import PerformanceDashboard

async def simulate_audio_capture():
    """Simulate audio capture operations."""
    with ComponentProfiler("audio_capture", "capture_chunk", {"chunk_size": 1024}):
        await asyncio.sleep(random.uniform(0.001, 0.005))  # 1-5ms

async def simulate_transcription():
    """Simulate transcription operations."""
    with ComponentProfiler("transcription", "transcribe_audio", {"audio_length": 1000}):
        await asyncio.sleep(random.uniform(0.05, 0.2))  # 50-200ms

async def simulate_sentiment():
    """Simulate sentiment analysis operations."""
    with ComponentProfiler("sentiment", "analyze_utterance", {"text_length": 100}):
        await asyncio.sleep(random.uniform(0.01, 0.05))  # 10-50ms

async def simulate_events():
    """Simulate event emission operations."""
    with ComponentProfiler("events", "emit_event", {"event_count": 1}):
        await asyncio.sleep(random.uniform(0.001, 0.01))  # 1-10ms

async def run_simulation():
    """Run performance simulation."""
    profiler = PerformanceProfiler.get_instance()
    dashboard = PerformanceDashboard()
    
    print("Starting performance simulation...")
    print("Starting dashboard server...")
    
    # Start dashboard
    await dashboard.start()
    
    # Run simulation for 30 seconds
    start_time = time.time()
    iteration = 0
    
    while time.time() - start_time < 30:
        iteration += 1
        print(f"Iteration {iteration}")
        
        # Simulate pipeline operations
        await simulate_audio_capture()
        await simulate_transcription()
        await simulate_sentiment()
        await simulate_events()
        
        # Print current stats
        stats = profiler.get_all_stats()
        print("\nCurrent stats:")
        for component, data in stats.items():
            print(f"  {component}: avg={data.get('avg_duration_ms', 0):.2f}ms, "
                  f"ops={data.get('total_operations', 0)}")
        
        await asyncio.sleep(1)
    
    print("\nFinal performance summary:")
    stats = profiler.get_all_stats()
    for component, data in stats.items():
        print(f"{component}:")
        print(f"  Average: {data.get('avg_duration_ms', 0):.2f}ms")
        print(f"  Operations: {data.get('total_operations', 0)}")
        print(f"  Min: {data.get('min_duration_ms', 0):.2f}ms")
        print(f"  Max: {data.get('max_duration_ms', 0):.2f}ms")
    
    # Export metrics
    profiler.export_metrics("performance_test.json")
    print("Metrics exported to performance_test.json")
    
    await dashboard.stop()

if __name__ == "__main__":
    asyncio.run(run_simulation())