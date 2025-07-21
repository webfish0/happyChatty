#!/usr/bin/env python3
"""
Demo script for real-time speech sentiment analysis.
Runs the pipeline for a short duration to demonstrate functionality.
"""

import asyncio
import logging
import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from audio_capture import AsyncAudioCapture
from transcription_engine import AsyncTranscriptionEngine
from utterance_segmenter import AsyncUtteranceSegmenter
from sentiment_analyzer import SentimentAnalyzer
from event_emitter import event_emitter, EventFormatter
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoRunner:
    """Demo runner for speech sentiment analysis."""
    
    def __init__(self, duration=15, debug=False):
        self.duration = duration
        self.events = []
        self.debug = debug
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
    async def run_demo(self):
        """Run the demo for specified duration."""
        logger.info(f"Starting {self.duration}s demo...")
        
        # Initialize components
        audio_capture = AsyncAudioCapture()
        
        # Load Hugging Face token from environment
        import os
        huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        if not huggingface_token:
            logger.warning("HUGGINGFACE_TOKEN not found in environment")
            logger.info("Using basic speech recognition without diarization")
            from transcription_engine import BasicTranscriptionEngine
            transcription_engine = BasicTranscriptionEngine()
        else:
            transcription_engine = AsyncTranscriptionEngine(huggingface_token=huggingface_token)
            
        utterance_segmenter = AsyncUtteranceSegmenter()
        sentiment_analyzer = SentimentAnalyzer()
        
        # Add console callback
        event_emitter.add_callback(self._console_callback)
        
        try:
            # Start audio capture
            await audio_capture.start_recording()
            logger.info("Audio capture started. Speak into your microphone...")
            
            # Record start time
            start_time = asyncio.get_event_loop().time()
            
            # Processing loop
            chunk_count = 0
            async for audio_chunk in audio_capture.get_audio_chunks():
                if asyncio.get_event_loop().time() - start_time > self.duration:
                    break
                    
                chunk_count += 1
                if audio_chunk is not None and len(audio_chunk) > 0:
                    # Log audio level
                    level = audio_capture.get_audio_level(audio_chunk)
                    if self.debug or chunk_count % 10 == 0:  # Log every 10th chunk
                        logger.info(f"Audio chunk #{chunk_count}: {len(audio_chunk)} bytes, level: {level:.3f}")
                    
                    # Skip processing if audio level is too low
                    if level < 0.01:
                        if self.debug:
                            logger.debug("Skipping low-level audio")
                        continue
                    
                    # Process transcription
                    segments = await transcription_engine.transcribe_audio(audio_chunk)
                    
                    if segments:
                        logger.info(f"Transcription found: {len(segments)} segments")
                        # Segment into utterances
                        utterances = await utterance_segmenter.process_segments_async(segments)
                        
                        # Analyze sentiment for each utterance
                        for utterance in utterances:
                            await self._process_utterance(utterance, sentiment_analyzer)
                    else:
                        if self.debug:
                            logger.debug("No transcription segments found")
                else:
                    logger.warning(f"Empty audio chunk #{chunk_count}")
                
                await asyncio.sleep(0.01)
                
        except KeyboardInterrupt:
            logger.info("Demo interrupted by user")
        except Exception as e:
            logger.error(f"Demo error: {e}")
        finally:
            await audio_capture.stop_recording()
            logger.info("Demo completed")
            
            # Save results
            if self.events:
                self.save_results()
    
    async def _process_utterance(self, utterance, analyzer):
        """Process a single utterance."""
        try:
            sentiment_scores = await analyzer.analyze_utterance(
                utterance.text, 
                utterance.speaker
            )
            
            # Create event
            from event_emitter import AnalysisEvent
            event = AnalysisEvent.from_utterance(utterance, sentiment_scores)
            
            # Emit event
            await event_emitter.emit_event(event)
            
            # Store for demo
            self.events.append({
                'timestamp': event.timestamp,
                'speaker': event.speaker,
                'utterance': event.utterance,
                'sentiment': event.sentiment_scores
            })
            
        except Exception as e:
            logger.error(f"Error processing utterance: {e}")
    
    def _console_callback(self, event):
        """Console callback for real-time display."""
        formatted = EventFormatter.format_console(event)
        print(formatted)
    
    def save_results(self, filename="demo_results.json"):
        """Save demo results."""
        with open(filename, 'w') as f:
            json.dump(self.events, f, indent=2, default=str)
        logger.info(f"Demo results saved to {filename}")

async def main():
    """Main demo function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time speech sentiment analysis demo")
    parser.add_argument("--duration", type=int, default=15, help="Demo duration in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode")
    
    args = parser.parse_args()
    
    if args.test_mode:
        # Create test audio for validation
        test_audio = np.random.randint(-1000, 1000, size=16000, dtype=np.int16).tobytes()
        
        # Test audio capture
        capture = AsyncAudioCapture()
        level = capture.get_audio_level(test_audio)
        print(f"Test audio level: {level:.3f}")
        
        # Test transcription with mock data
        from transcription_engine import AsyncTranscriptionEngine
        import os
        huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        if huggingface_token:
            engine = AsyncTranscriptionEngine(huggingface_token=huggingface_token)
            segments = await engine.transcribe_audio(test_audio)
            print(f"Test transcription segments: {len(segments) if segments else 0}")
        else:
            print("Skipping transcription test (no HuggingFace token)")
        
        return
    
    demo = DemoRunner(duration=args.duration, debug=args.debug)
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())