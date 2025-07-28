#!/usr/bin/env python3
"""
Test script for conversation dashboard functionality
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from event_emitter import event_emitter, AnalysisEvent
from sentiment_analyzer import SentimentScores

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_dashboard_events():
    """Test sending events to the dashboard."""
    logger.info("Starting dashboard test...")
    
    # Start WebSocket server
    await event_emitter.start_websocket_server("localhost", 8765)
    logger.info("WebSocket server started on ws://localhost:8765")
    
    # Create sample sentiment scores
    sample_scores = {
        "Happy": 0.8,
        "Content": 0.6,
        "Enthusiastic": 0.4,
        "Sad": 0.1,
        "Angry": 0.05
    }
    
    # Send a series of test events
    speakers = ["SPEAKER_01", "SPEAKER_02"]
    sample_texts = [
        "Hello there! How are you doing today?",
        "I'm doing great, thanks for asking!",
        "That's wonderful to hear!",
        "I'm so happy we could meet up.",
        "This conversation is really enjoyable."
    ]
    
    try:
        for i in range(10):
            speaker = speakers[i % len(speakers)]
            text = sample_texts[i % len(sample_texts)]
            
            # Create analysis event
            event = AnalysisEvent(
                timestamp=datetime.now().isoformat() + 'Z',
                speaker=speaker,
                text=text,
                scores=sample_scores,
                duration=2.5,
                confidence=0.95,
                performance_metrics={
                    "average_latency": 150,
                    "components": {
                        "audio": {"average_time": 10},
                        "transcription": {"average_time": 80},
                        "sentiment": {"average_time": 60}
                    }
                }
            )
            
            # Emit event
            await event_emitter.emit_event(event)
            logger.info(f"Sent event {i+1}: {speaker} - {text[:30]}...")
            
            # Wait a bit between events
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Error during dashboard test: {e}")
        raise
    finally:
        # Clean up
        await event_emitter.close_websocket_server()
        logger.info("Test completed and WebSocket server closed")

if __name__ == "__main__":
    asyncio.run(test_dashboard_events())