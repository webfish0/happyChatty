import asyncio
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, asdict
import websockets
import aiofiles
from pathlib import Path

from utterance_segmenter import Utterance
from sentiment_analyzer import SentimentScores
from performance_profiler import ComponentProfiler

logger = logging.getLogger(__name__)

@dataclass
class AnalysisEvent:
    """Structured event containing complete analysis results."""
    timestamp: str
    speaker: str
    text: str
    scores: Dict[str, float]
    duration: float
    confidence: float
    performance_metrics: Dict[str, Any] = None
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_utterance(cls, utterance: Utterance, sentiment_scores: SentimentScores, performance_metrics: Dict[str, Any] = None) -> 'AnalysisEvent':
        """Create event from utterance and sentiment scores."""
        return cls(
            timestamp=utterance.start_time.isoformat() + 'Z',
            speaker=utterance.speaker,
            text=utterance.text,
            scores=sentiment_scores.to_dict(),
            duration=utterance.duration,
            confidence=utterance.confidence,
            performance_metrics=performance_metrics
        )

class EventEmitter:
    """Emits structured JSON events to multiple destinations."""
    
    def __init__(self):
        self.websocket_clients = set()
        self.file_output = None
        self.callbacks = []
        self.event_history = []
        self.max_history = 1000
        
    def add_callback(self, callback: Callable[[AnalysisEvent], None]):
        """Add callback function for real-time events."""
        self.callbacks.append(callback)
    
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server for real-time event streaming."""
        logger.info(f"Starting WebSocket server on {host}:{port}")
        
        async def handle_client(websocket, path):
            self.websocket_clients.add(websocket)
            try:
                # Send recent history to new client
                for event in self.event_history[-10:]:
                    await websocket.send(event.to_json())
                
                await websocket.wait_closed()
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.websocket_clients.discard(websocket)
        
        start_server = websockets.serve(handle_client, host, port)
        await start_server
        logger.info(f"WebSocket server started on ws://{host}:{port}")
    
    async def start_file_output(self, filepath: str, append: bool = True):
        """Start writing events to file."""
        self.file_output = Path(filepath)
        
        # Create directory if it doesn't exist
        self.file_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Write header if new file
        if not append or not self.file_output.exists():
            async with aiofiles.open(self.file_output, 'w') as f:
                await f.write('{"events":[\n')
        
        logger.info(f"Started writing events to {self.file_output}")
    
    async def emit_event(self, event: AnalysisEvent):
        """Emit a single analysis event to all destinations."""
        with ComponentProfiler("events", "emit_event", {"speaker": event.speaker, "text_length": len(event.text)}):
            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Send to WebSocket clients
            await self._broadcast_to_websockets(event)
            
            # Write to file
            await self._write_to_file(event)
            
            # Call registered callbacks
            await self._call_callbacks(event)
            
            logger.info(f"Emitted event: {event.speaker} - {event.text[:50]}...")
    
    async def _broadcast_to_websockets(self, event: AnalysisEvent):
        """Broadcast event to all connected WebSocket clients."""
        if not self.websocket_clients:
            return
            
        disconnected_clients = []
        
        for websocket in self.websocket_clients:
            try:
                await websocket.send(event.to_json())
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(websocket)
            except Exception as e:
                logger.error(f"Error sending to WebSocket client: {e}")
                disconnected_clients.append(websocket)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.discard(client)
    
    async def _write_to_file(self, event: AnalysisEvent):
        """Write event to file."""
        if not self.file_output:
            return
            
        try:
            async with aiofiles.open(self.file_output, 'a') as f:
                # Write comma separator if not first event
                if self.file_output.stat().st_size > 20:  # More than just header
                    await f.write(',\n')
                
                await f.write(event.to_json())
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
    
    async def _call_callbacks(self, event: AnalysisEvent):
        """Call all registered callbacks."""
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    async def close_file(self):
        """Close file output and finalize JSON."""
        if self.file_output and self.file_output.exists():
            try:
                async with aiofiles.open(self.file_output, 'a') as f:
                    await f.write('\n]}')
                logger.info("Closed file output")
            except Exception as e:
                logger.error(f"Error closing file: {e}")
    
    async def close_websocket_server(self):
        """Close all WebSocket connections."""
        if self.websocket_clients:
            # Close all client connections
            close_tasks = []
            for websocket in self.websocket_clients:
                close_tasks.append(websocket.close())
            
            if close_tasks:
                await asyncio.gather(*close_tasks, return_exceptions=True)
            
            self.websocket_clients.clear()
            logger.info("Closed WebSocket connections")
    
    def get_recent_events(self, count: int = 10) -> List[AnalysisEvent]:
        """Get recent events from history."""
        return self.event_history[-count:] if self.event_history else []
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get statistics about emitted events."""
        if not self.event_history:
            return {"total_events": 0}
        
        speakers = {}
        for event in self.event_history:
            speakers[event.speaker] = speakers.get(event.speaker, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "unique_speakers": len(speakers),
            "speaker_counts": speakers,
            "websocket_clients": len(self.websocket_clients),
            "file_output": str(self.file_output) if self.file_output else None
        }

class EventFormatter:
    """Utility class for formatting events in different ways."""
    
    @staticmethod
    def format_console(event: AnalysisEvent) -> str:
        """Format event for console output."""
        top_emotions = sorted(event.scores.items(), key=lambda x: x[1], reverse=True)[:3]
        top_str = ", ".join([f"{k}:{v:.2f}" for k, v in top_emotions])
        
        return f"[{event.timestamp}] {event.speaker}: {event.text[:60]}... | {top_str}"
    
    @staticmethod
    def format_summary(event: AnalysisEvent) -> str:
        """Format event as brief summary."""
        dominant_emotion = max(event.scores.items(), key=lambda x: x[1])
        return f"{event.speaker}: {dominant_emotion[0]} ({dominant_emotion[1]:.1%})"
    
    @staticmethod
    def format_detailed(event: AnalysisEvent) -> Dict[str, Any]:
        """Format event with additional computed metrics."""
        scores = event.scores
        
        # Calculate emotion categories
        positive_emotions = [
            'Happy', 'Joyful', 'Content', 'Enthusiastic', 'Helpful', 
            'Kind', 'Compassionate', 'Polite', 'Grateful', 'Sweet', 'Wholesome'
        ]
        
        negative_emotions = [
            'Sad', 'Angry', 'Frustrated', 'Disappointed', 'Anxious', 
            'Rude', 'Ungrateful', 'Cruel', 'Hostile', 'Sleazy', 'Insulting', 'Threatening'
        ]
        
        complex_emotions = [
            'Mischievous', 'Curious', 'Confused', 'Surprised', 
            'Sarcastic', 'Ironic', 'Teasing'
        ]
        
        positive_score = sum(scores.get(emotion, 0) for emotion in positive_emotions)
        negative_score = sum(scores.get(emotion, 0) for emotion in negative_emotions)
        complex_score = sum(scores.get(emotion, 0) for emotion in complex_emotions)
        
        # Normalize by number of emotions in each category
        positive_score /= len(positive_emotions)
        negative_score /= len(negative_emotions)
        complex_score /= len(complex_emotions)
        
        return {
            "event": asdict(event),
            "summary": {
                "positive_score": positive_score,
                "negative_score": negative_score,
                "complex_score": complex_score,
                "dominant_emotion": max(scores.items(), key=lambda x: x[1]),
                "emotion_count": sum(1 for v in scores.values() if v > 0.1)
            }
        }

# Global event emitter instance
event_emitter = EventEmitter()