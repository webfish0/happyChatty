#!/usr/bin/env python3
"""
Performance Monitoring Dashboard for Real-time Speech Sentiment Analysis
Provides Chrome DevTools-style timeline visualization of system performance metrics.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import websockets
import aiohttp
from aiohttp import web
import threading
import webbrowser
from pathlib import Path
import aiofiles

from performance_profiler import PerformanceProfiler

logger = logging.getLogger(__name__)

class PerformanceDashboard:
    """Real-time performance monitoring dashboard with Chrome DevTools-style timeline."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.websocket_clients = set()
        self.is_running = False
        
        # Setup routes
        self.app.router.add_get('/', self._handle_conversation_dashboard)
        self.app.router.add_get('/performance', self._handle_index)
        self.app.router.add_get('/ws', self._handle_websocket)
        self.app.router.add_static('/static', Path(__file__).parent / 'static')
        
        # Performance data storage
        self.timeline_events = []
        self.max_history = 1000
        
    async def start(self):
        """Start the performance dashboard."""
        logger.info(f"Starting performance dashboard on http://{self.host}:{self.port}")
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.is_running = True
        
        # Start metrics collection
        asyncio.create_task(self._collect_metrics())
        
        # Open browser
        webbrowser.open(f"http://{self.host}:{self.port}")
        
    async def stop(self):
        """Stop the performance dashboard."""
        self.is_running = False
        
        # Close all websocket connections
        clients = list(self.websocket_clients)
        for ws in clients:
            try:
                await ws.close()
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")
        self.websocket_clients.clear()
        
    async def _handle_index(self, request):
        """Serve the main dashboard HTML."""
        html_content = self._get_dashboard_html()
        return web.Response(text=html_content, content_type='text/html')
    
    async def _handle_conversation_dashboard(self, request):
        """Serve the conversation sentiment dashboard."""
        # Serve the index.html file from static directory
        static_path = Path(__file__).parent / 'static' / 'index.html'
        if static_path.exists():
            async with aiofiles.open(static_path, 'r') as f:
                content = await f.read()
            return web.Response(text=content, content_type='text/html')
        else:
            # Fallback to simple redirect
            raise web.HTTPFound('/static/index.html')
    
    async def _handle_websocket(self, request):
        """Handle websocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_clients.add(ws)
        
        try:
            # Send initial data
            await ws.send_json({
                'type': 'initial',
                'data': self.timeline_events[-100:] if self.timeline_events else []
            })
            
            # Keep connection alive
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            self.websocket_clients.discard(ws)
        
        return ws
    
    async def _collect_metrics(self):
        """Collect and broadcast performance metrics."""
        while self.is_running:
            try:
                # Get current metrics
                metrics = PerformanceProfiler.get_instance().get_metrics()
                
                # Create timeline event
                timeline_event = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'performance',
                    'data': metrics
                }
                
                # Store in history
                self.timeline_events.append(timeline_event)
                if len(self.timeline_events) > self.max_history:
                    self.timeline_events.pop(0)
                
                # Broadcast to clients
                await self._broadcast_metrics(timeline_event)
                
                # Wait before next collection
                await asyncio.sleep(0.1)  # Faster updates for real-time feel
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(1)
    
    async def _broadcast_metrics(self, timeline_event: Dict[str, Any]):
        """Broadcast metrics to all connected clients."""
        if not self.websocket_clients:
            return
            
        message = {
            'type': 'timeline',
            'data': timeline_event
        }
        
        # Send to all clients
        disconnected = []
        for ws in self.websocket_clients:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.append(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.websocket_clients.discard(ws)
    
    def _get_dashboard_html(self) -> str:
        """Generate the dashboard HTML with Chrome DevTools-style timeline."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Speech Analysis Performance Timeline</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            font-size: 12px;
        }
        .header {
            background: #1a1a1a;
            color: white;
            padding: 10px 20px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .container {
            max-width: 100%;
            margin: 0;
            padding: 0;
        }
        .timeline-container {
            background: white;
            margin: 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            overflow: hidden;
        }
        .timeline-header {
            background: #f8f9fa;
            padding: 10px 15px;
            border-bottom: 1px solid #dee2e6;
            font-weight: 600;
            color: #495057;
        }
        .timeline-content {
            position: relative;
            height: 400px;
            overflow-y: auto;
            background: #fafafa;
        }
        .timeline-item {
            display: flex;
            border-bottom: 1px solid #eee;
            min-height: 40px;
            align-items: center;
            padding: 0 15px;
        }
        .timeline-item:hover {
            background: #f0f0f0;
        }
        .timeline-label {
            width: 120px;
            font-weight: 600;
            color: #333;
            font-size: 11px;
            flex-shrink: 0;
        }
        .timeline-bar-container {
            flex: 1;
            height: 20px;
            background: #e9ecef;
            border-radius: 2px;
            position: relative;
            margin: 0 10px;
        }
        .timeline-bar {
            height: 100%;
            border-radius: 2px;
            position: absolute;
            left: 0;
            top: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 10px;
            font-weight: bold;
            transition: width 0.3s ease;
        }
        .audio-bar { background: #007bff; }
        .transcription-bar { background: #28a745; }
        .sentiment-bar { background: #ffc107; }
        .events-bar { background: #dc3545; }
        
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 20px;
            background: white;
            margin: 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .stat-card {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }
        .stat-label {
            font-size: 12px;
            color: #6c757d;
            margin-top: 5px;
        }
        
        .legend {
            display: flex;
            gap: 20px;
            padding: 10px 15px;
            background: white;
            margin: 0 20px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            align-items: center;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
        }
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }
        
        .connection-status {
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 11px;
        }
        .connected {
            background: #28a745;
            color: white;
        }
        .disconnected {
            background: #dc3545;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Speech Analysis Performance Timeline</h1>
            <div id="connection-status" class="connection-status disconnected">Disconnected</div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color audio-bar"></div>
                <span>Audio Capture</span>
            </div>
            <div class="legend-item">
                <div class="legend-color transcription-bar"></div>
                <span>Transcription</span>
            </div>
            <div class="legend-item">
                <div class="legend-color sentiment-bar"></div>
                <span>Sentiment Analysis</span>
            </div>
            <div class="legend-item">
                <div class="legend-color events-bar"></div>
                <span>Event Emission</span>
            </div>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-value" id="total-events">0</div>
                <div class="stat-label">Total Events</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-latency">0ms</div>
                <div class="stat-label">Average Total Latency</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="last-processed">-</div>
                <div class="stat-label">Last Processed</div>
            </div>
        </div>
        
        <div class="timeline-container">
            <div class="timeline-header">Real-time Processing Timeline</div>
            <div class="timeline-content" id="timeline-content">
                <div style="text-align: center; padding: 50px; color: #666;">
                    Waiting for data...
                </div>
            </div>
        </div>
    </div>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        const connectionStatus = document.getElementById('connection-status');
        const timelineContent = document.getElementById('timeline-content');
        
        let eventCounter = 0;
        
        ws.onopen = function() {
            connectionStatus.textContent = 'Connected';
            connectionStatus.className = 'connection-status connected';
        };
        
        ws.onclose = function() {
            connectionStatus.textContent = 'Disconnected';
            connectionStatus.className = 'connection-status disconnected';
        };
        
        ws.onmessage = function(event) {
            const message = JSON.parse(event.data);
            
            if (message.type === 'timeline') {
                updateTimeline(message.data);
            } else if (message.type === 'initial') {
                message.data.forEach(updateTimeline);
            }
        };
        
        function updateTimeline(timelineEvent) {
            const data = timelineEvent.data;
            const timestamp = new Date(timelineEvent.timestamp);
            
            // Update summary stats
            document.getElementById('total-events').textContent = data.total_events || 0;
            document.getElementById('avg-latency').textContent = Math.round(data.average_latency || 0) + 'ms';
            document.getElementById('last-processed').textContent = timestamp.toLocaleTimeString();
            
            // Create timeline item
            const timelineItem = document.createElement('div');
            timelineItem.className = 'timeline-item';
            
            const components = data.components || {};
            const maxTime = Math.max(
                components.audio?.average_time || 0,
                components.transcription?.average_time || 0,
                components.sentiment?.average_time || 0,
                components.events?.average_time || 0,
                100 // Default max 100ms
            );
            
            const scale = 100 / maxTime; // Scale to percentage
            
            timelineItem.innerHTML = `
                <div class="timeline-label">${timestamp.toLocaleTimeString()}</div>
                <div class="timeline-bar-container">
                    ${createBar('audio', components.audio?.average_time || 0, scale, 'Audio')}
                    ${createBar('transcription', components.transcription?.average_time || 0, scale, 'Transcription')}
                    ${createBar('sentiment', components.sentiment?.average_time || 0, scale, 'Sentiment')}
                    ${createBar('events', components.events?.average_time || 0, scale, 'Events')}
                </div>
            `;
            
            // Add to timeline
            if (timelineContent.children.length === 1 && 
                timelineContent.children[0].textContent.includes('Waiting for data')) {
                timelineContent.innerHTML = '';
            }
            
            timelineContent.insertBefore(timelineItem, timelineContent.firstChild);
            
            // Keep only last 50 items
            while (timelineContent.children.length > 50) {
                timelineContent.removeChild(timelineContent.lastChild);
            }
        }
        
        function createBar(type, time, scale, label) {
            if (time === 0) return '';
            const width = Math.min(time * scale, 100);
            const left = getBarPosition(type);
            return `
                <div class="timeline-bar ${type}-bar" 
                     style="width: ${width}%; left: ${left}%;"
                     title="${label}: ${Math.round(time)}ms">
                    ${Math.round(time)}ms
                </div>
            `;
        }
        
        function getBarPosition(type) {
            const positions = {
                'audio': 0,
                'transcription': 25,
                'sentiment': 50,
                'events': 75
            };
            return positions[type] || 0;
        }
    </script>
</body>
</html>
        """

async def start_dashboard(host: str = "localhost", port: int = 8080):
    """Start the performance dashboard as a standalone service."""
    dashboard = PerformanceDashboard(host, port)
    await dashboard.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await dashboard.stop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_dashboard())