#!/usr/bin/env python3
"""
Real-time Speech Sentiment Analysis System
Main application orchestrator that coordinates all components.
"""

import asyncio
import logging
import signal
import sys
import argparse
from pathlib import Path
import json
import os

from audio_capture import AsyncAudioCapture
from transcription_engine import AsyncTranscriptionEngine
from utterance_segmenter import AsyncUtteranceSegmenter
from sentiment_analyzer import SentimentAnalyzer, SentimentCache
from event_emitter import event_emitter, EventFormatter
from config import config
from performance_profiler import PerformanceProfiler, ComponentProfiler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('speech_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

class SpeechAnalysisOrchestrator:
    """Main orchestrator for real-time speech sentiment analysis."""
    
    def __init__(self):
        self.audio_capture = AsyncAudioCapture()
        self.performance_profiler = PerformanceProfiler()
        
        # Load Hugging Face token from environment
        huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        if huggingface_token:
            self.transcription_engine = AsyncTranscriptionEngine(huggingface_token=huggingface_token)
        else:
            logger.warning("HUGGINGFACE_TOKEN not found - using basic transcription")
            from transcription_engine import BasicTranscriptionEngine
            self.transcription_engine = BasicTranscriptionEngine()
            
        self.utterance_segmenter = AsyncUtteranceSegmenter()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.sentiment_cache = SentimentCache()
        
        self.is_running = False
        self.processing_task = None
        
    async def start(self, 
                   websocket_host: str = "localhost",
                   websocket_port: int = 8765,
                   output_file: str = None,
                   device_index: int = None):
        """Start the complete speech analysis pipeline."""
        
        logger.info("Starting Speech Analysis Orchestrator...")
        
        # Start WebSocket server
        await event_emitter.start_websocket_server(websocket_host, websocket_port)
        
        # Start file output if specified
        if output_file:
            await event_emitter.start_file_output(output_file)
        
        # Add console callback
        event_emitter.add_callback(self._console_callback)
        
        # Start audio capture
        await self.audio_capture.start_recording())
        
        # Start processing loop
        self.is_running = True
        self.processing_task = asyncio.create_task(self._processing_loop())
        
        logger.info("Speech Analysis Orchestrator started successfully")
        logger.info(f"WebSocket server: ws://{websocket_host}:{websocket_port}")
        logger.info("Press Ctrl+C to stop")
        
    async def stop(self):
        """Stop the speech analysis pipeline."""
        logger.info("Stopping Speech Analysis Orchestrator...")
        
        self.is_running = False
        
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Stop audio capture
        await self.audio_capture.stop_recording()
        
        # Close file output
        await event_emitter.close_file()
        
        # Close WebSocket server
        await event_emitter.close_websocket_server()
        
        logger.info("Speech Analysis Orchestrator stopped")
    
    async def _processing_loop(self):
        """Main processing loop for real-time analysis."""
        logger.info("Starting processing loop...")
        
        try:
            # Collect audio chunks for batch processing
            audio_buffer = bytearray()
            buffer_duration = 3.0  # Process every 3 seconds
            chunk_size = 1024
            target_buffer_size = int(16000 * 2 * buffer_duration)  # 16kHz, 16-bit, 3 seconds
            
            async for audio_chunk in self.audio_capture.get_audio_chunks():
                if not self.is_running:
                    break
                    
                if audio_chunk and len(audio_chunk) > 0:
                    audio_buffer.extend(audio_chunk)
                    
                    # Process when we have enough audio
                    if len(audio_buffer) >= target_buffer_size:
                        with ComponentProfiler("pipeline", "_processing_loop", {"buffer_size": len(audio_buffer)}):
                            # Process transcription and diarization
                            if hasattr(self.transcription_engine, 'process_audio_chunk_async'):
                                segments = await self.transcription_engine.process_audio_chunk_async(bytes(audio_buffer))
                            else:
                                segments = await self.transcription_engine.transcribe_audio(bytes(audio_buffer))
                            
                            if segments:
                                # Segment into utterances
                                utterances = await self.utterance_segmenter.process_segments_async(segments)
                                
                                # Analyze sentiment for each utterance
                                for utterance in utterances:
                                    await self._process_utterance(utterance)
                            
                            # Clear buffer after processing
                            audio_buffer.clear()
                
        except Exception as e:
            logger.error(f"Error in processing loop: {e}", exc_info=True)
            raise
    
    async def _process_utterance(self, utterance):
        """Process a single utterance for sentiment analysis."""
        try:
            # Check cache first
            cached_scores = self.sentiment_cache.get(utterance.text, utterance.speaker)
            if cached_scores:
                sentiment_scores = cached_scores
                logger.debug("Using cached sentiment scores")
            else:
                # Analyze sentiment
                with ComponentProfiler("sentiment", "analyze_sentiment", {"text_length": len(utterance.text)}):
                    sentiment_scores = await self.sentiment_analyzer.analyze_utterance(
                        utterance.text,
                        utterance.speaker
                    )
                
                # Cache the result
                self.sentiment_cache.set(utterance.text, utterance.speaker, sentiment_scores)
            
            # Get performance metrics
            performance_metrics = PerformanceProfiler.get_instance().get_metrics()
            
            # Create and emit event
            from event_emitter import AnalysisEvent
            event = AnalysisEvent.from_utterance(utterance, sentiment_scores, performance_metrics)
            await event_emitter.emit_event(event)
            
        except Exception as e:
            logger.error(f"Error processing utterance: {e}", exc_info=True)
    
    def _console_callback(self, event):
        """Callback for console output."""
        formatted = EventFormatter.format_console(event)
        print(formatted)
    
    def get_status(self) -> dict:
        """Get current system status."""
        return {
            "is_running": self.is_running,
            "event_stats": event_emitter.get_event_stats(),
            "cache_size": self.sentiment_cache.size()
        }

async def list_audio_devices():
    """List available audio input devices."""
    capture = AsyncAudioCapture()
    devices = capture.list_devices()
    
    print("\nAvailable audio input devices:")
    print("-" * 50)
    for device in devices:
        print(f"Index {device['index']}: {device['name']} ({device['channels']} channels, {device['sample_rate']} Hz)")
    print("-" * 50)

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Real-time Speech Sentiment Analysis")
    parser.add_argument("--host", default="localhost", help="WebSocket host")
    parser.add_argument("--port", type=int, default=8765, help="WebSocket port")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--device", type=int, help="Audio device index")
    parser.add_argument("--list-devices", action="store_true", help="List audio devices")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--dashboard", action="store_true", help="Start conversation dashboard")
    parser.add_argument("--dashboard-port", type=int, default=8080, help="Dashboard port")
    parser.add_argument("--performance-dashboard", action="store_true", help="Start performance monitoring dashboard")
    
    args = parser.parse_args()
    
    if args.list_devices:
        await list_audio_devices()
        return
    
    # Load custom config if provided
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            custom_config = json.load(f)
            # Update config with custom values
            # This would need proper config merging logic
    
    # Check for required environment variables
    if not config.sentiment.openrouter_api_key:
        logger.warning("OPENROUTER_API_KEY not set - using mock sentiment analysis")
    
    if not os.getenv("HUGGINGFACE_TOKEN"):
        logger.warning("HUGGINGFACE_TOKEN not set - diarization may not work")
    
    orchestrator = SpeechAnalysisOrchestrator()
    
    # Start performance dashboard if requested
    dashboard_task = None
    performance_dashboard_task = None
    if args.dashboard or args.performance_dashboard:
        from performance_dashboard import PerformanceDashboard
        dashboard = PerformanceDashboard(port=args.dashboard_port)
        dashboard_task = asyncio.create_task(dashboard.start())
        logger.info(f"Conversation dashboard started on http://localhost:{args.dashboard_port}")
        logger.info(f"Performance dashboard available at http://localhost:{args.dashboard_port}/performance")
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(orchestrator.stop())
        if dashboard_task:
            dashboard_task.cancel()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await orchestrator.start(
            websocket_host=args.host,
            websocket_port=args.port,
            output_file=args.output,
            device_index=args.device
        )
        
        # Keep running until interrupted
        while orchestrator.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        await orchestrator.stop()
        if dashboard_task:
            try:
                await dashboard.stop()
            except Exception as e:
                logger.error(f"Error stopping dashboard: {e}")

if __name__ == "__main__":
    asyncio.run(main())